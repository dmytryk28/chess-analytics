from dagster import Definitions

from orchestration.assets import (
    raw_chesscom_games_daily,
    chess_dbt_assets,
    stockfish_analysis,
    gemini_summaries,
    daily_html_report,
    telegram_digest
)
from orchestration.dbt_assets import dbt_resource
from orchestration.resources import BigQueryResource
from orchestration.jobs import daily_incremental_job

defs = Definitions(
    assets=[
        raw_chesscom_games_daily,
        chess_dbt_assets,
        stockfish_analysis,
        gemini_summaries,
        daily_html_report,
        telegram_digest
    ],
    resources={
        "bigquery": BigQueryResource(),
        "dbt": dbt_resource,
    },
    jobs=[daily_incremental_job],
)