{{ config(materialized='table') }}

select
    eco,
    opening_name,
    count(*) as name_frequency,
from {{ ref('int_games_enriched') }}
where eco is not null and opening_name is not null
group by eco, opening_name
