import re
import os
from pathlib import Path
from datetime import date
import chess
import chess.svg
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def render_daily_report(report_date: date, games: list[dict], output_path: str) -> None:
    """Render the daily HTML report"""
    for game in games:
        orientation = chess.BLACK if game.get("my_color") == "black" else chess.WHITE

        for move in game.get("moves", []):
            board = chess.Board(move["fen_before"])

            played_move_obj = board.parse_san(move["played_move"])
            best_move_obj = chess.Move.from_uci(move["best_move"])
            move["best_move_san"] = board.san(best_move_obj)

            arrows = [
                chess.svg.Arrow(played_move_obj.from_square, played_move_obj.to_square, color="#cc0000"),
                chess.svg.Arrow(best_move_obj.from_square, best_move_obj.to_square, color="#00cc00")
            ]

            move["board_svg"] = chess.svg.board(
                board,
                orientation=orientation,
                arrows=arrows
            )

            text = move.get("commentary", "")
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            move["commentary"] = text

    total_flagged_moves = sum(len(g.get("moves", [])) for g in games)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("daily_report.html.jinja2")

    html = template.render(
        report_date=report_date.isoformat(),
        games=games,
        total_flagged_moves=total_flagged_moves,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)