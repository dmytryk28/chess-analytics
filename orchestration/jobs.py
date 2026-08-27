from dagster import define_asset_job, AssetSelection
from dagster_dbt import build_dbt_asset_selection

from orchestration.assets import (
    raw_chesscom_games_daily,
    chess_dbt_assets,
    stockfish_analysis,
    gemini_summaries,
    daily_html_report,
    telegram_digest
)

python_assets = AssetSelection.assets(
    raw_chesscom_games_daily,
    stockfish_analysis,
    gemini_summaries,
    daily_html_report,
    telegram_digest
)

dbt_subset = build_dbt_asset_selection(
    [chess_dbt_assets],
    dbt_select="+fct_games"
)

daily_incremental_job = define_asset_job(
    name="daily_incremental_job",
    selection=python_assets | dbt_subset
)