-- Of the customers who first bought in a month (the cohort),
-- how many bought again 1, 2, 3... months later?
with cohorts as (
    select customer_id, cohort_month
    from {{ ref('dim_customers') }}
    where cohort_month is not null
),

cohort_sizes as (
    select cohort_month, count(*) as cohort_customers
    from cohorts
    group by cohort_month
),

purchase_months as (
    select distinct
        customer_id,
        cast(date_trunc('month', order_date) as date) as order_month
    from {{ ref('fct_orders') }}
    where is_completed
),

activity as (
    select
        cohorts.cohort_month,
        date_diff('month', cohorts.cohort_month, purchase_months.order_month)
            as months_since_first_purchase,
        count(distinct purchase_months.customer_id) as active_customers
    from purchase_months
    inner join cohorts
        on purchase_months.customer_id = cohorts.customer_id
    group by 1, 2
)

select
    activity.cohort_month,
    activity.months_since_first_purchase,
    cohort_sizes.cohort_customers,
    activity.active_customers,
    round(activity.active_customers / cohort_sizes.cohort_customers, 4) as retention_rate
from activity
inner join cohort_sizes
    on activity.cohort_month = cohort_sizes.cohort_month
order by 1, 2
