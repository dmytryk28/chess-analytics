import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_text_message(text: str) -> None:
    """Send a short plain-text message"""
    response = requests.post(
        f"{API_BASE}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )
    response.raise_for_status()


def send_document(file_path: str, caption: str = "") -> None:
    """Send a file as a document attachment"""
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/sendDocument",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
            files={"document": f}
        )
    response.raise_for_status()