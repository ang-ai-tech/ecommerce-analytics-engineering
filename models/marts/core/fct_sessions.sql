-- One row per visit: how far did the visitor get?
select
    session_id,
    min(event_at)                                       as session_started_at,
    cast(min(event_at) as date)                         as session_date,
    max(customer_id)                                    as customer_id,
    max(customer_id) is not null                        as is_logged_in,
    count(*) filter (where event_type = 'page_view')    as page_views,
    bool_or(event_type = 'add_to_cart')                 as reached_cart,
    bool_or(event_type = 'begin_checkout')              as reached_checkout,
    bool_or(event_type = 'purchase')                    as purchased,
    max(order_id)                                       as order_id
from {{ ref('fct_web_events') }}
group by session_id
