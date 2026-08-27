{{ config(materialized='table') }}

select
    d.opening_name,
    f.my_color,
    count(*) as games_played,
    countif(f.my_result = 'win') as wins,
    countif(f.my_result = 'loss') as losses,
    countif(f.my_result = 'draw') as draws,
    round(100.0 * countif(f.my_result = 'win') / count(*), 1) as winrate_pct,
    round(avg(f.rating_diff), 0) as avg_rating_diff
from {{ ref('fct_games') }} f
join {{ ref('dim_openings_short') }} d using (eco)
group by 1, 2
having count(*) >= 5