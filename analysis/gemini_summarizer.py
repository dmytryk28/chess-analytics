import time
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"

PROMPT_TEMPLATE = """You are a chess coach reviewing a single move from one of my games.

Position before my move (FEN): {fen_before}
I played: {played_move_san} ({played_move_uci})
The engine's recommended move was: {best_move_san} ({best_move_uci})
This move cost me approximately {win_pct_loss}% win probability.

In 2-3 plain-English sentences, explain what went wrong with my move and what I should
have considered instead. A diagram of the position will be shown alongside your
explanation, so feel free to reference squares and pieces directly (e.g. "the knight on
f3" or "moving the rook to d5") — the reader can see the board while reading your
explanation."""

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 15


def summarize_mistake(
    fen_before: str,
    played_move_san: str,
    played_move_uci: str,
    best_move_san: str,
    best_move_uci: str,
    win_pct_loss: float
) -> str:
    prompt = PROMPT_TEMPLATE.format(
        fen_before=fen_before,
        played_move_san=played_move_san,
        played_move_uci=played_move_uci,
        best_move_san=best_move_san,
        best_move_uci=best_move_uci,
        win_pct_loss=win_pct_loss
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            return str(response.text).strip()
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    raise last_error