{{ config(materialized='table') }}

select
    extract(hour from played_at at time zone '{{ var("timezone") }}') as hour_of_day,
    {{ day_of_week_monday_first("played_at at time zone '" ~ var("timezone") ~ "'") }} as day_of_week,
    count(*) as games_played,
    countif(my_result = 'win') as wins,
    round(100.0 * countif(my_result = 'win') / count(*), 1) as winrate_pct
from {{ ref('fct_games') }}
group by 1, 2
order by 2, 1