{% macro normalize_chess_result(result_column) %}
    case
        when {{ result_column }} = 'win' then 'win'
        when {{ result_column }} in ('checkmated', 'resigned', 'timeout', 'abandoned') then 'loss'
        when {{ result_column }} in ('agreed', 'repetition', 'stalemate', 'insufficient', '50move', 'timevsinsufficient') then 'draw'
        else null
    end
{% endmacro %}