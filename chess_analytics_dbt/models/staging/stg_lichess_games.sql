{{ config(materialized='table') }}

select
    JSON_EXTRACT_SCALAR(raw_json, '$.id') as game_id,
    'lichess' as platform,
    TIMESTAMP_MILLIS(CAST(JSON_EXTRACT_SCALAR(raw_json, '$.createdAt') AS INT64)) as played_at,
    JSON_EXTRACT_SCALAR(raw_json, '$.speed') as time_control_category,

    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.clock.initial') AS INT64) as time_control_initial_seconds,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.clock.increment') AS INT64) as time_control_increment_seconds,

    JSON_EXTRACT_SCALAR(raw_json, '$.opening.eco') as eco,
    JSON_EXTRACT_SCALAR(raw_json, '$.opening.name') as opening_name,

    JSON_EXTRACT_SCALAR(raw_json, '$.players.white.user.name') as white_username,
    JSON_EXTRACT_SCALAR(raw_json, '$.players.black.user.name') as black_username,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.players.white.rating') AS INT64) as white_rating,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.players.black.rating') AS INT64) as black_rating,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.players.white.ratingDiff') AS INT64) as white_rating_diff,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.players.black.ratingDiff') AS INT64) as black_rating_diff,

    JSON_EXTRACT_SCALAR(raw_json, '$.winner') as winner_raw,

    CASE
        WHEN JSON_EXTRACT_SCALAR(raw_json, '$.winner') = 'white' THEN 'win'
        WHEN JSON_EXTRACT_SCALAR(raw_json, '$.winner') = 'black' THEN 'loss'
        ELSE 'draw'
    END as white_result,
    CASE
        WHEN JSON_EXTRACT_SCALAR(raw_json, '$.winner') = 'black' THEN 'win'
        WHEN JSON_EXTRACT_SCALAR(raw_json, '$.winner') = 'white' THEN 'loss'
        ELSE 'draw'
    END as black_result,

    JSON_EXTRACT_SCALAR(raw_json, '$.status') as game_status,
    JSON_EXTRACT_SCALAR(raw_json, '$.variant') as variant,
    JSON_EXTRACT_SCALAR(raw_json, '$.pgn') as pgn

from {{ source('raw', 'raw_lichess_games') }}