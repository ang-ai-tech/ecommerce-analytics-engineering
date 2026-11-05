with source as (
    select * from {{ source('shop', 'web_events') }}
)

select
    cast(event_id as integer)                   as event_id,
    session_id,
    cast(nullif(customer_id, '') as integer)    as customer_id,
    event_type,
    cast(event_at as timestamp)                 as event_at,
    cast(nullif(order_id, '') as integer)       as order_id
from source
