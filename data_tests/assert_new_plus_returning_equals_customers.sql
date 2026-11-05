-- Every customer who buys in a month is either new (first purchase) or returning.
select order_month, customers, new_customers, returning_customers
from {{ ref('rpt_monthly_sales') }}
where new_customers + returning_customers <> customers
