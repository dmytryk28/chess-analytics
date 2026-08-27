from google.cloud import bigquery
from google.oauth2 import service_account
import json
import io

from config import GCP_PROJECT_ID, GCP_SA_KEY_PATH

RAW_JSON_SCHEMA = [bigquery.SchemaField("raw_json", "STRING", mode="REQUIRED")]


def _get_bigquery_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(GCP_SA_KEY_PATH)
    return bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)


def _load_ndjson_file(file_obj, schema: list, dataset: str, table: str) -> int:
    """Core loader: append NDJSON object to a BigQuery table with the given schema"""
    client = _get_bigquery_client()
    table_id = f"{GCP_PROJECT_ID}.{dataset}.{table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_file(file_obj, destination=table_id, job_config=job_config)
    job.result()

    print(f"Loaded {job.output_rows} rows into {table_id}")
    return job.output_rows


def run_query(sql: str) -> list[dict]:
    """Run a SQL query against BigQuery and return rows as dicts"""
    client = _get_bigquery_client()
    return [dict(row) for row in client.query(sql).result()]


def load_file_to_bigquery(local_path: str, dataset: str, table: str) -> None:
    """Upload a local file to BigQuery"""
    with open(local_path, "rb") as f:
        _load_ndjson_file(f, schema=RAW_JSON_SCHEMA, dataset=dataset, table=table)


def load_games_to_bigquery(games: list[dict], dataset: str, table: str) -> int:
    """Upload a list of raw game dicts to BigQuery"""
    if not games:
        return 0

    rows = [{"raw_json": json.dumps(game)} for game in games]
    ndjson_data = "\n".join(json.dumps(row) for row in rows)
    return _load_ndjson_file(io.StringIO(ndjson_data), schema=RAW_JSON_SCHEMA, dataset=dataset, table=table)


def load_rows_to_bigquery(rows: list[dict], schema: list, dataset: str, table: str) -> int:
    """Upload typed rows to BigQuery with an explicit schema"""
    if not rows:
        return 0

    ndjson_data = "\n".join(json.dumps(row, default=str) for row in rows)
    return _load_ndjson_file(io.StringIO(ndjson_data), schema=schema, dataset=dataset, table=table)
