import requests
import json
from datetime import datetime, timezone, timedelta


def _fetch_month_games(username: str, year: int, month: int) -> list[dict]:
    """Fetch one month of rated, standard-chess games from Chess.com"""
    headers = {"User-Agent": "chess-analytics-project (personal use)"}

    url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return []  # no games that month

    response.raise_for_status()

    data = response.json()
    return [
        game for game in data.get("games", [])
        if game.get("rated") and game.get("rules") == "chess"
    ]


def fetch_chesscom_games_historical(username: str, output_path: str, years_back: int) -> int:
    """Fetch full game history and write it to a local NDJSON file"""
    today = datetime.now()
    count = 0

    with open(output_path, "w", encoding="utf-8") as f:
        for year in range(today.year - years_back, today.year + 1):
            for month in range(1, 13):
                if year == today.year and month > today.month:
                    break

                games = _fetch_month_games(username, year, month)
                for game in games:
                    row = {"raw_json": json.dumps(game)}
                    f.write(json.dumps(row) + "\n")
                    count += 1
                    if count % 1000 == 0:
                        print(count)

    return count


def fetch_chesscom_games_daily(username: str, boundary: datetime, boundary_end: datetime) -> list[dict]:
    """Fetch games played within (boundary, boundary_end]"""
    months_to_check = {(boundary.year, boundary.month), (boundary_end.year, boundary_end.month)}

    prev_month_date = boundary.replace(day=1) - timedelta(days=1)
    months_to_check.add((prev_month_date.year, prev_month_date.month))

    all_games = []
    for year, month in months_to_check:
        all_games.extend(_fetch_month_games(username, year, month))

    return [
        game for game in all_games
        if boundary < datetime.fromtimestamp(game["end_time"], tz=timezone.utc) <= boundary_end
    ]
