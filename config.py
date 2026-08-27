import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")
DATA_DIR = PROJECT_ROOT / "data"

GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
GCP_SA_KEY_PATH = str(PROJECT_ROOT / os.environ["GCP_SA_KEY_PATH"])
LICHESS_USERNAME = os.environ["LICHESS_USERNAME"]
CHESSCOM_USERNAME = os.environ["CHESSCOM_USERNAME"]
TIMEZONE = os.environ["TIMEZONE"]
DAILY_BOUNDARY_HOUR = int(os.environ["DAILY_BOUNDARY_HOUR"])
STOCKFISH_PATH = os.environ["STOCKFISH_PATH"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
