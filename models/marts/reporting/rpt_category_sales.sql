-- Units and revenue per product category and month (completed orders only).
select
    cast(date_trunc('month', order_date) as date)   as order_month,
    category,
    count(distinct order_id)                        as orders,
    sum(quantity)                                   as units,
    sum(revenue)                                    as revenue
from {{ ref('fct_order_items') }}
where is_completed
group by 1, 2
order by 1, 2
