-- How many visits reach each step: visit -> cart -> checkout -> purchase.
select
    cast(date_trunc('month', session_date) as date)         as session_month,
    count(*)                                                as sessions,
    count(*) filter (where reached_cart)                    as sessions_with_cart,
    count(*) filter (where reached_checkout)                as sessions_with_checkout,
    count(*) filter (where purchased)                       as sessions_with_purchase,
    round(count(*) filter (where reached_cart) / count(*), 4)       as cart_rate,
    round(count(*) filter (where purchased) / count(*), 4)          as conversion_rate
from {{ ref('fct_sessions') }}
group by 1
order by 1
