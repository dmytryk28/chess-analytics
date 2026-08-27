{{ config(materialized='table') }}

select
    game_id,
    platform,
    played_at,
    played_date,
    eco,
    time_control_initial_seconds,
    time_control_increment_seconds,
    my_color,
    opponent_username,
    my_rating,
    opponent_rating,
    rating_diff,
    my_result
from {{ ref('int_games_enriched') }}