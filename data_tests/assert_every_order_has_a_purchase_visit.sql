-- Two different systems (shop orders and web tracking) must agree:
-- every order of a real customer has exactly one visit that ends with a purchase.
select
    fct_orders.order_id,
    count(fct_sessions.session_id) as purchase_visits
from {{ ref('fct_orders') }} as fct_orders
left join {{ ref('fct_sessions') }} as fct_sessions
    on fct_orders.order_id = fct_sessions.order_id
group by fct_orders.order_id
having count(fct_sessions.session_id) <> 1
