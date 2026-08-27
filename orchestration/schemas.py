from google.cloud.bigquery import SchemaField

MOVE_ANALYSIS_SCHEMA = [
    SchemaField("game_id", "STRING", mode="REQUIRED"),
    SchemaField("move_number", "INT64", mode="REQUIRED"),
    SchemaField("played_move", "STRING", mode="REQUIRED"),
    SchemaField("best_move", "STRING", mode="NULLABLE"),
    SchemaField("win_pct_loss", "FLOAT64", mode="REQUIRED"),
    SchemaField("centipawn_loss", "INT64", mode="REQUIRED"),
    SchemaField("fen_before", "STRING", mode="REQUIRED"),
    SchemaField("commentary", "STRING", mode="REQUIRED")
]