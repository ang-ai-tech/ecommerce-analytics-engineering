-- Revenue must be the same whether it is summed from orders or from order lines.
-- Returns a row (= the test fails) if the two totals differ by more than one cent.
with from_orders as (
    select sum(revenue) as revenue from {{ ref('fct_orders') }}
),

from_items as (
    select sum(revenue) as revenue from {{ ref('fct_order_items') }}
)

select
    from_orders.revenue as revenue_from_orders,
    from_items.revenue  as revenue_from_items
from from_orders
cross join from_items
where abs(from_orders.revenue - from_items.revenue) > 0.01
