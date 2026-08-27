{{ config(materialized='table') }}

select
    played_date as date_day,
    extract(year from played_date) as year,
    extract(month from played_date) as month,
    extract(day from played_date) as day,
    {{ day_of_week_monday_first("played_date") }} as day_of_week,
    {{ day_of_week_monday_first("played_date") }} in (6, 7) as is_weekend
from (
    select distinct played_date
    from {{ ref('int_games_enriched') }}
)