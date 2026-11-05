{#-
    Runs at the start of every dbt command (on-run-start in dbt_project.yml).
    Creates one view per CSV file in the `raw` schema, so the raw files can be used
    as normal dbt sources. Every column is read as text: casting happens in staging.
-#}
{% macro create_raw_views() %}
    create schema if not exists raw;
    {% for table in ['customers', 'products', 'orders', 'order_items', 'web_events'] %}
    create or replace view raw.{{ table }} as
        select *
        from read_csv('{{ var("raw_data_path") }}/{{ table }}.csv', header = true, all_varchar = true);
    {% endfor %}
{% endmacro %}
