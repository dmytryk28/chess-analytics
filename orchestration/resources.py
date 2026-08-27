from dagster import ConfigurableResource

from extractors.bigquery_loader import load_games_to_bigquery


class BigQueryResource(ConfigurableResource):
    """Dagster wrapper around the bigquery_loader function"""

    def load_games(self, games: list[dict], dataset: str, table: str) -> int:
        return load_games_to_bigquery(games, dataset, table)