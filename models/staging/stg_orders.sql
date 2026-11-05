with source as (
    select * from {{ source('shop', 'orders') }}
)

select
    cast(order_id as integer)       as order_id,
    cast(customer_id as integer)    as customer_id,
    cast(ordered_at as timestamp)   as ordered_at,
    cast(ordered_at as date)        as order_date,
    -- The same status is written in different ways ("Completed", "COMPLETE", "Canceled"...).
    case lower(trim(status))
        when 'completed' then 'completed'
        when 'complete' then 'completed'
        when 'cancelled' then 'cancelled'
        when 'canceled' then 'cancelled'
        when 'refunded' then 'refunded'
        else 'unknown'
    end                             as status,
    lower(trim(channel))            as channel
from source
