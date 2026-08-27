import requests
import json
from datetime import datetime, timezone


def fetch_lichess_games(username: str, output_path: str, years_back: int) -> int:
    """Fetch the player's full rated, standard-chess game history from Lichess
    and write it to a local NDJSON file. Return the count of games"""
    now = datetime.now(timezone.utc)
    since = now.replace(year=now.year - years_back)
    since_ms = int(since.timestamp() * 1000)

    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "since": since_ms,
        "rated": "true",
        "perfType": "bullet,blitz,rapid,classical",
        "pgnInJson": "true",
        "opening": "true",
    }
    headers = {
        "Accept": "application/x-ndjson",
        "User-Agent": "chess-analytics-project (personal use)",
    }

    response = requests.get(url, params=params, headers=headers, stream=True)
    response.raise_for_status()

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for line in response.iter_lines():
            if line:
                game = json.loads(line)
                if game.get("variant") == "standard":
                    row = {"raw_json": json.dumps(game)}
                    f.write(json.dumps(row) + "\n")
                    count += 1
                    if count % 1000 == 0:
                        print(count)

    return count
