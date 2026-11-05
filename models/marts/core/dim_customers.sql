-- One row per real customer, with a summary of their purchases.
with customers as (
    select * from {{ ref('stg_customers') }}
    where not is_test_account
),

purchases as (
    select
        customer_id,
        min(ordered_at)     as first_purchase_at,
        max(ordered_at)     as last_purchase_at,
        count(*)            as completed_orders,
        sum(revenue)        as lifetime_revenue
    from {{ ref('fct_orders') }}
    where is_completed
    group by customer_id
)

select
    customers.customer_id,
    customers.email,
    customers.country_code,
    customers.created_at,
    purchases.first_purchase_at,
    purchases.last_purchase_at,
    cast(coalesce(purchases.completed_orders, 0) as integer)            as completed_orders,
    cast(coalesce(purchases.lifetime_revenue, 0) as decimal(12, 2))     as lifetime_revenue,
    -- The cohort is the month of the first purchase.
    cast(date_trunc('month', purchases.first_purchase_at) as date)      as cohort_month,
    case
        when purchases.completed_orders is null then 'no purchase'
        when purchases.completed_orders = 1 then 'one-time'
        else 'repeat'
    end                                                                 as customer_type
from customers
left join purchases
    on customers.customer_id = purchases.customer_id
