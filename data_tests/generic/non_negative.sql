{% test non_negative(model, column_name) %}
-- Fails for every row where the value is below zero.
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
