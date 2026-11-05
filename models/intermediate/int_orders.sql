-- Real customer orders only (QA test orders removed), with their totals.
with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

order_totals as (
    select
        order_id,
        count(*)        as number_of_lines,
        sum(quantity)   as number_of_units,
        sum(amount)     as order_amount
    from {{ ref('stg_order_items') }}
    group by order_id
)

select
    orders.*,
    order_totals.number_of_lines,
    order_totals.number_of_units,
    order_totals.order_amount
from orders
inner join customers
    on orders.customer_id = customers.customer_id
left join order_totals
    on orders.order_id = order_totals.order_id
where not customers.is_test_account
