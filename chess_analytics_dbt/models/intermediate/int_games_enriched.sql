{{ config(materialized='table') }}

with base as (
    select
        *,
        case
            when platform = 'lichess' and white_username = '{{ var("lichess_username") }}' then 'white'
            when platform = 'lichess' and black_username = '{{ var("lichess_username") }}' then 'black'
            when platform = 'chesscom' and white_username = '{{ var("chesscom_username") }}' then 'white'
            when platform = 'chesscom' and black_username = '{{ var("chesscom_username") }}' then 'black'
        end as my_color
    from {{ ref('int_games_unified') }}
)

select
    game_id,
    platform,
    played_at,
    time_control_category,
    time_control_initial_seconds,
    time_control_increment_seconds,
    eco,
    opening_name,
    pgn,

    my_color,
    case when my_color = 'white' then black_username else white_username end as opponent_username,
    case when my_color = 'white' then white_rating else black_rating end as my_rating,
    case when my_color = 'white' then black_rating else white_rating end as opponent_rating,
    case when my_color = 'white' then white_rating - black_rating else black_rating - white_rating end as rating_diff,
    case when my_color = 'white' then white_result else black_result end as my_result,

    date(played_at, '{{ var("timezone") }}') as played_date

from base