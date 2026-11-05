-- One row per product in an order, for product and category analysis.
with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('int_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
)

select
    items.order_item_id,
    items.order_id,
    orders.customer_id,
    orders.order_date,
    items.product_id,
    products.category,
    items.quantity,
    items.unit_price,
    items.amount,
    orders.status = 'completed'                                         as is_completed,
    case when orders.status = 'completed' then items.amount else 0 end  as revenue
from items
-- inner join: lines of test orders disappear together with their orders
inner join orders
    on items.order_id = orders.order_id
left join products
    on items.product_id = products.product_id
