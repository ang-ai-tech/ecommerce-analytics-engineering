{{
    config(
        materialized='incremental',
        unique_key='event_id',
        on_schema_change='fail'
    )
}}

-- The biggest table, so it is loaded incrementally: each run adds only new events.
select *
from {{ ref('stg_web_events') }}

{% if is_incremental() %}
-- Re-read the last few days too, in case some events arrived late.
-- unique_key replaces rows that are already there, so nothing is duplicated.
where event_at > (
    select max(event_at) - interval {{ var('events_lookback_days') }} day
    from {{ this }}
)
{% endif %}
