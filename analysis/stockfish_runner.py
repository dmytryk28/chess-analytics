import math
import chess
import chess.pgn
import io as pyio
from stockfish import Stockfish

from config import STOCKFISH_PATH

WIN_PCT_LOSS_THRESHOLD = 8.0
DEEP_ANALYSIS_DEPTH = 20
SHALLOW_ANALYSIS_DEPTH = 14


def cp_to_win_pct(cp: int) -> float:
    """Convert centipawns to victory probability (from 0 to 100)"""
    clamped_cp = max(-4000, min(4000, cp))
    return 100 / (1 + math.exp(-0.00368208 * clamped_cp))


def analyze_game(pgn_text: str, game_id: str, color: str, deep: bool) -> list[dict]:
    depth = DEEP_ANALYSIS_DEPTH if deep else SHALLOW_ANALYSIS_DEPTH
    stockfish = Stockfish(path=STOCKFISH_PATH, depth=depth)

    game = chess.pgn.read_game(pyio.StringIO(pgn_text))
    if game is None:
        return []

    board = game.board()
    flagged_moves = []

    for ply_number, move in enumerate(game.mainline_moves(), start=1):
        mover_color = "white" if ply_number % 2 == 1 else "black"

        if mover_color != color:
            board.push(move)
            continue

        fen_before = board.fen()
        san_move = board.san(move)
        played_uci = move.uci()

        stockfish.set_fen_position(fen_before)
        eval_before_white = _read_eval_cp(stockfish)
        eval_before_mine = eval_before_white if color == "white" else -eval_before_white
        best_move_uci = stockfish.get_best_move()

        if best_move_uci == played_uci:
            board.push(move)
            continue

        board.push(move)
        stockfish.set_fen_position(board.fen())

        eval_after_white = _read_eval_cp(stockfish)
        eval_after_mine = eval_after_white if color == "white" else -eval_after_white

        win_pct_before = cp_to_win_pct(eval_before_mine)
        win_pct_after = cp_to_win_pct(eval_after_mine)

        wp_loss = win_pct_before - win_pct_after
        cp_loss = eval_before_mine - eval_after_mine

        if wp_loss >= WIN_PCT_LOSS_THRESHOLD:
            flagged_moves.append({
                "game_id": game_id,
                "move_number": (ply_number + 1) // 2,
                "played_move": san_move,
                "best_move": best_move_uci,
                "win_pct_loss": round(wp_loss, 1),
                "centipawn_loss": cp_loss,
                "fen_before": fen_before
            })
    return flagged_moves


def _read_eval_cp(stockfish: Stockfish) -> int:
    evaluation = stockfish.get_evaluation()
    if evaluation["type"] == "cp":
        return evaluation["value"]
    return 100000 if evaluation["value"] > 0 else -100000