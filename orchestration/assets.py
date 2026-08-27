from dagster import asset, RetryPolicy, AssetExecutionContext
from extractors.chesscom_client import fetch_chesscom_games_daily
from extractors.bigquery_loader import run_query, load_rows_to_bigquery
from analysis.stockfish_runner import analyze_game
from analysis.gemini_summarizer import summarize_mistake
from orchestration.resources import BigQueryResource
from dagster_dbt import dbt_assets, DbtCliResource
from orchestration.dbt_assets import dbt_project
from orchestration.utils import get_daily_boundary
from analysis.render_report import render_daily_report
from config import CHESSCOM_USERNAME, GCP_PROJECT_ID, DATA_DIR, TIMEZONE
from orchestration.schemas import MOVE_ANALYSIS_SCHEMA
from telegram_bot.notifier import send_text_message, send_document
import chess
from typing import Optional
from zoneinfo import ZoneInfo


@asset(retry_policy=RetryPolicy(max_retries=1, delay=60), group_name="extraction")
def raw_chesscom_games_daily(context: AssetExecutionContext, bigquery: BigQueryResource) -> None:
    """Fetch games played within (boundary, boundary_end]"""
    boundary_utc, boundary_end_utc = get_daily_boundary()
    context.log.info(f"Fetching Chess.com games in ({boundary_utc.isoformat()}, {boundary_end_utc.isoformat()}]")

    games = fetch_chesscom_games_daily(CHESSCOM_USERNAME, boundary=boundary_utc, boundary_end=boundary_end_utc)
    context.log.info(f"Fetched {len(games)} games")

    if games:
        rows_loaded = bigquery.load_games(games, dataset="raw", table="raw_chesscom_games")
        context.add_output_metadata({"games_loaded": rows_loaded})
    else:
        context.add_output_metadata({"games_loaded": 0})


@dbt_assets(manifest=dbt_project.manifest_path)
def chess_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """Every dbt model (staging -> intermediate -> fct_games) becomes an individually
    trackable node in the Dagster asset graph"""
    yield from dbt.cli(["build"], context=context).stream()


@asset(deps=[chess_dbt_assets], group_name="analysis")
def stockfish_analysis(context: AssetExecutionContext) -> list[dict]:
    """Analyze yesterday's games with Stockfish. Return flagged moves in
    memory"""
    boundary_utc, boundary_end_utc = get_daily_boundary()

    sql = f"""
        select game_id, pgn, my_result, my_color
        from `{GCP_PROJECT_ID}.intermediate.int_games_enriched`
        where played_at > timestamp('{boundary_utc.isoformat()}')
          and played_at <= timestamp('{boundary_end_utc.isoformat()}')
    """

    games = run_query(sql)
    context.log.info(f"Found {len(games)} games to analyze")

    all_flagged_moves = []
    for game in games:
        deep = game["my_result"] != "win"
        flagged = analyze_game(
            pgn_text=game["pgn"],
            game_id=game["game_id"],
            color=game["my_color"],
            deep=deep
        )
        all_flagged_moves.extend(flagged)

    context.add_output_metadata({"games_analyzed": len(games), "moves_flagged": len(all_flagged_moves)})
    return all_flagged_moves


@asset(deps=[stockfish_analysis], group_name="analysis")
def gemini_summaries(context: AssetExecutionContext, stockfish_analysis: list[dict]) -> None:
    """Generate an explanation for each mistake flagged by Stockfish today,
    merge it with the move data, and write a row per mistake to BigQuery"""
    if not stockfish_analysis:
        context.log.info("No flagged moves. Skip Gemini")
        return
    context.log.info(f"Summarizing {len(stockfish_analysis)} flagged moves")

    complete_rows = []
    for move in stockfish_analysis:
        board = chess.Board(move["fen_before"])
        played_move_obj = board.parse_san(move["played_move"])
        best_move_obj = chess.Move.from_uci(move["best_move"])

        commentary = summarize_mistake(
            fen_before=move["fen_before"],
            played_move_san=move["played_move"],
            played_move_uci=played_move_obj.uci(),
            best_move_san=board.san(best_move_obj),
            best_move_uci=move["best_move"],
            win_pct_loss=move["win_pct_loss"]
        )
        complete_rows.append({**move, "commentary": commentary})

    rows_loaded = load_rows_to_bigquery(
        complete_rows, schema=MOVE_ANALYSIS_SCHEMA, dataset="analysis", table="move_analysis"
    )
    context.add_output_metadata({"rows_written": rows_loaded})


@asset(deps=[gemini_summaries], group_name="reporting")
def daily_html_report(context: AssetExecutionContext) -> Optional[str]:
    """Assemble Stockfish + Gemini results into a single HTML report,
    grouped by game. Return the local file path"""
    boundary_utc, boundary_end_utc = get_daily_boundary()

    sql = f"""
        select
            g.game_id,
            g.opponent_username,
            g.my_result,
            g.my_color,
            m.move_number,
            m.played_move,
            m.best_move,
            m.win_pct_loss,
            m.fen_before,
            m.commentary
        from `{GCP_PROJECT_ID}.intermediate.int_games_enriched` g
        join `{GCP_PROJECT_ID}.analysis.move_analysis` m
            on g.game_id = m.game_id
        where g.played_at > timestamp('{boundary_utc.isoformat()}')
          and g.played_at <= timestamp('{boundary_end_utc.isoformat()}')
        order by g.game_id, m.move_number
    """

    rows = run_query(sql)

    if not rows:
        context.log.info("No flagged moves today, skip report generation")
        return None

    games_by_id: dict[str, dict] = {}
    for row in rows:
        game_id = row["game_id"]
        if game_id not in games_by_id:
            games_by_id[game_id] = {
                "opponent_username": row["opponent_username"],
                "my_result": row["my_result"],
                "my_color": row["my_color"],
                "moves": []
            }
        games_by_id[game_id]["moves"].append({
            "move_number": row["move_number"],
            "played_move": row["played_move"],
            "best_move": row["best_move"],
            "win_pct_loss": row["win_pct_loss"],
            "fen_before": row["fen_before"],
            "commentary": row["commentary"]
        })

    report_date = boundary_utc.date()
    output_path = str(DATA_DIR / f"report_{report_date.isoformat()}.html")

    render_daily_report(report_date=report_date, games=list(games_by_id.values()), output_path=output_path)

    context.log.info(f"Report written to {output_path}")
    context.add_output_metadata({"report_path": output_path, "games_included": len(games_by_id)})

    return output_path


@asset(deps=[daily_html_report], group_name="reporting")
def telegram_digest(context: AssetExecutionContext, daily_html_report: Optional[str]) -> None:
    """Send a short text digest followed by the full HTML report as a document"""
    boundary_utc, boundary_end_utc = get_daily_boundary()

    local_tz = ZoneInfo(TIMEZONE)
    start_str = boundary_utc.astimezone(local_tz).strftime("%d.%m.%Y %H:%M")
    end_str = boundary_end_utc.astimezone(local_tz).strftime("%d.%m.%Y %H:%M")

    sql_stats = f"""
        select
            count(*) as games_played,
            countif(my_result = 'win') as wins,
            countif(my_result = 'loss') as losses,
            countif(my_result = 'draw') as draws
        from `{GCP_PROJECT_ID}.marts.fct_games`
        where played_at > timestamp('{boundary_utc.isoformat()}')
          and played_at <= timestamp('{boundary_end_utc.isoformat()}')
    """
    stats = run_query(sql_stats)[0]

    if stats["games_played"] == 0:
        message = f"No games played in period {start_str} - {end_str}"
        send_text_message(message)
        context.log.info("Message sent (no games)")
        return

    sql_mistakes = f"""
        select count(*) as cnt
        from `{GCP_PROJECT_ID}.analysis.move_analysis` m
        join `{GCP_PROJECT_ID}.marts.fct_games` g on m.game_id = g.game_id
        where g.played_at > timestamp('{boundary_utc.isoformat()}')
          and g.played_at <= timestamp('{boundary_end_utc.isoformat()}')
    """
    mistakes_count = run_query(sql_mistakes)[0]["cnt"]

    digest_text = (
        f"♟️ Chess digest {start_str} - {end_str}\n"
        f"Games: {stats['games_played']} (W {stats['wins']} / D {stats['draws']} / L {stats['losses']})\n"
        f"Mistakes flagged: {mistakes_count}"
    )

    if daily_html_report:
        send_document(daily_html_report, caption=digest_text)
        context.log.info("Telegram digest sent with report document")
    else:
        context.log.info("No report generated (0 mistakes). Sending text only.")
        send_text_message(digest_text)