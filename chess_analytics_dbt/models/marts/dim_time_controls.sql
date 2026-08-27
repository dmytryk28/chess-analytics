{{ config(materialized='table') }}

select distinct
    time_control_category,
    time_control_initial_seconds
from {{ ref('int_games_enriched') }}
where time_control_initial_seconds is not null