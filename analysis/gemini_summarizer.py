import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import json
from typing import List, Dict

client = genai.Client(api_key=GEMINI_API_KEY)

MODELS = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]

PROMPT_TEMPLATE = """You are a chess coach reviewing mistakes from my games. 
Analyze the following list of moves provided in JSON format. Each item contains the board position (FEN), my played move, the engine's recommended best move, and the win probability loss.

For each move, write 2-3 plain-English sentences explaining what went wrong with my move and what I should have considered instead. 
A diagram of the position will be shown alongside each of your explanations, so do not describe the whole board. Instead, feel free to reference squares and pieces directly (e.g. "the knight on f3" or "moving the rook to d5").

Mistakes to analyze:
{moves_json}"""

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 15


def summarize_mistakes_batch(moves: List[Dict]) -> List[Dict]:
    if not moves:
        return []

    moves_for_prompt = []
    for i, move in enumerate(moves):
        moves_for_prompt.append({
            "move_id": i,
            "fen_before": move["fen_before"],
            "played_move": f"{move['played_move_san']} ({move['played_move_uci']})",
            "best_move": f"{move['best_move_san']} ({move['best_move_uci']})",
            "win_pct_loss": move["win_pct_loss"]
        })

    prompt = PROMPT_TEMPLATE.format(moves_json=json.dumps(moves_for_prompt, indent=2))

    response_schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "move_id": types.Schema(type=types.Type.INTEGER),
                "commentary": types.Schema(type=types.Type.STRING)
            },
            required=["move_id", "commentary"]
        )
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema,
                    ),
                )
                results = json.loads(response.text)
                commentaries = {item["move_id"]: item["commentary"] for item in results}
                for i, move in enumerate(moves):
                    move["commentary"] = commentaries.get(i, "Analysis failed for this move")
                return moves

            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)

        print(f"Model {model_name} failed after {MAX_RETRIES} attempts. Switching to next model...")

    raise Exception(f"All models failed. Last error: {last_error}")