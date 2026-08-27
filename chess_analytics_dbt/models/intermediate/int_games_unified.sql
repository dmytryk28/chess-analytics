{{ config(materialized='table') }}

select
    game_id,
    platform,
    played_at,
    time_control_category,
    time_control_initial_seconds,
    time_control_increment_seconds,
    eco,
    opening_name,
    white_username,
    black_username,
    white_rating,
    black_rating,
    white_result,
    black_result,
    pgn
from {{ ref('stg_lichess_games') }}

union all

select
    game_id,
    platform,
    played_at,
    time_control_category,
    time_control_initial_seconds,
    time_control_increment_seconds,
    eco,
    cast(null as string) as opening_name,
    white_username,
    black_username,
    white_rating,
    black_rating,
    white_result,
    black_result,
    pgn
from {{ ref('stg_chesscom_games') }}