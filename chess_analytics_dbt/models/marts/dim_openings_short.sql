{{ config(materialized='table') }}

with cleaned_names as (
    select
        eco,
        trim(split(opening_name, ':')[safe_offset(0)]) as base_opening_name
    from {{ ref('dim_openings') }}
)

select
    eco,
    base_opening_name as opening_name
from cleaned_names
qualify row_number() over (
    partition by eco
    order by length(base_opening_name) asc
) = 1