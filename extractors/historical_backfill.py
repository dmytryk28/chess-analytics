from os import makedirs
from lichess_client import fetch_lichess_games
from extractors.chesscom_client import fetch_chesscom_games_historical
from extractors.bigquery_loader import load_file_to_bigquery
from config import LICHESS_USERNAME, CHESSCOM_USERNAME, DATA_DIR

LICHESS_DATA = "raw_lichess_games"
CHESSCOM_DATA = "raw_chesscom_games"
LICHESS_FILE = str(DATA_DIR / f"{LICHESS_DATA}.jsonl")
CHESSCOM_FILE = str(DATA_DIR / f"{CHESSCOM_DATA}.jsonl")


def main():
    makedirs(DATA_DIR, exist_ok=True)

    print("Fetching Lichess games")
    lichess_count = fetch_lichess_games(LICHESS_USERNAME, output_path=LICHESS_FILE, years_back=5)
    print(f"Saved {lichess_count} games to {LICHESS_FILE}")

    print("Fetching Chess.com games")
    chesscom_count = fetch_chesscom_games_historical(CHESSCOM_USERNAME, output_path=CHESSCOM_FILE, years_back=5)
    print(f"Saved {chesscom_count} games to {CHESSCOM_FILE}")

    print("Loading to BigQuery")
    load_file_to_bigquery(LICHESS_FILE, dataset="raw", table=LICHESS_DATA)
    load_file_to_bigquery(CHESSCOM_FILE, dataset="raw", table=CHESSCOM_DATA)


if __name__ == "__main__":
    main()