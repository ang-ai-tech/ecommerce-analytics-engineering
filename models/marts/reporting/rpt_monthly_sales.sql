-- Monthly KPIs. Only completed orders count as sales.
with orders as (
    select
        fct_orders.*,
        cast(date_trunc('month', fct_orders.order_date) as date) as order_month,
        dim_customers.cohort_month
    from {{ ref('fct_orders') }} as fct_orders
    inner join {{ ref('dim_customers') }} as dim_customers
        on fct_orders.customer_id = dim_customers.customer_id
)

select
    order_month,
    count(*) filter (where is_completed)                                    as orders,
    count(distinct customer_id) filter (where is_completed)                 as customers,
    -- new + returning = customers
    count(distinct customer_id) filter (where is_completed and cohort_month = order_month)
                                                                            as new_customers,
    count(distinct customer_id) filter (where is_completed and cohort_month < order_month)
                                                                            as returning_customers,
    sum(revenue)                                                            as revenue,
    round(sum(revenue) / nullif(count(*) filter (where is_completed), 0), 2)
                                                                            as average_order_value,
    count(*) filter (where not is_completed)                                as cancelled_or_refunded_orders
from orders
group by order_month
order by order_month
