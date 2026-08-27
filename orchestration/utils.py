from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from config import TIMEZONE, DAILY_BOUNDARY_HOUR


def get_daily_boundary() -> tuple[datetime, datetime]:
    """Return the (start, end) UTC boundary from yesterday's
    DAILY_BOUNDARY_HOUR to today's one"""
    local_tz = ZoneInfo(TIMEZONE)
    now_local = datetime.now(local_tz)
    end_local = now_local.replace(
        hour=DAILY_BOUNDARY_HOUR, minute=0, second=0, microsecond=0
    )
    start_local = end_local - timedelta(days=1)
    return start_local.astimezone(ZoneInfo("UTC")), end_local.astimezone(ZoneInfo("UTC"))