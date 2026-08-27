{{ config(materialized='table') }}

select
    JSON_EXTRACT_SCALAR(raw_json, '$.uuid') as game_id,
    'chesscom' as platform,
    TIMESTAMP_SECONDS(CAST(JSON_EXTRACT_SCALAR(raw_json, '$.end_time') AS INT64)) as played_at,
    JSON_EXTRACT_SCALAR(raw_json, '$.time_class') as time_control_category,

    JSON_EXTRACT_SCALAR(raw_json, '$.time_control') as time_control_raw,

    CAST(REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(raw_json, '$.time_control'), r'^(\d+)') AS INT64)
        as time_control_initial_seconds,
    IFNULL(CAST(REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(raw_json, '$.time_control'), r'\+(\d+)$') AS INT64), 0)
        as time_control_increment_seconds,

    -- Chess.com's "eco" field is a URL, not a code,
    -- the real ECO code is only inside the PGN's ECO tag
    JSON_EXTRACT_SCALAR(raw_json, '$.eco') as eco_url,
    REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(raw_json, '$.pgn'), r'\[ECO "(\w\d+)"\]') as eco,

    JSON_EXTRACT_SCALAR(raw_json, '$.white.username') as white_username,
    JSON_EXTRACT_SCALAR(raw_json, '$.black.username') as black_username,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.white.rating') AS INT64) as white_rating,
    CAST(JSON_EXTRACT_SCALAR(raw_json, '$.black.rating') AS INT64) as black_rating,

    JSON_EXTRACT_SCALAR(raw_json, '$.white.result') as white_result_raw,
    JSON_EXTRACT_SCALAR(raw_json, '$.black.result') as black_result_raw,

    {{ normalize_chess_result("JSON_EXTRACT_SCALAR(raw_json, '$.white.result')") }} as white_result,
    {{ normalize_chess_result("JSON_EXTRACT_SCALAR(raw_json, '$.black.result')") }} as black_result,

    JSON_EXTRACT_SCALAR(raw_json, '$.rules') as variant,
    JSON_EXTRACT_SCALAR(raw_json, '$.pgn') as pgn

from {{ source('raw', 'raw_chesscom_games') }}