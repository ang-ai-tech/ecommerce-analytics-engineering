-- One row per order. Revenue counts completed orders only.
with orders as (
    select * from {{ ref('int_orders') }}
),

purchase_sequence as (
    -- 1 = the customer's first completed order, 2 = the second, ...
    select
        order_id,
        row_number() over (partition by customer_id order by ordered_at, order_id) as purchase_number
    from orders
    where status = 'completed'
)

select
    orders.order_id,
    orders.customer_id,
    orders.ordered_at,
    orders.order_date,
    orders.status,
    orders.channel,
    cast(orders.number_of_units as integer)                         as number_of_units,
    cast(orders.order_amount as decimal(12, 2))                     as order_amount,
    orders.status = 'completed'                                     as is_completed,
    cast(case when orders.status = 'completed' then orders.order_amount else 0 end
         as decimal(12, 2))                                         as revenue,
    cast(purchase_sequence.purchase_number as integer)              as purchase_number,
    coalesce(purchase_sequence.purchase_number = 1, false)          as is_first_purchase
from orders
left join purchase_sequence
    on orders.order_id = purchase_sequence.order_id
