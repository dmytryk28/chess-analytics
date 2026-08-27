{% macro day_of_week_monday_first(date_or_timestamp_column) %}
    mod(extract(dayofweek from {{ date_or_timestamp_column }}) + 5, 7) + 1
{% endmacro %}