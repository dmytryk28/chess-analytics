from pathlib import Path
from dagster_dbt import DbtCliResource, DbtProject

DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent / "chess_analytics_dbt"

dbt_project = DbtProject(project_dir=str(DBT_PROJECT_DIR))
dbt_resource = DbtCliResource(project_dir=dbt_project)