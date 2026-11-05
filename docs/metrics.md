# Metric definitions

One definition per metric, used by every report. All amounts are in euro and include VAT.

| Metric | Definition | Table |
|---|---|---|
| **Revenue** | Sum of `quantity × unit price paid` over the lines of **completed** orders. Cancelled and refunded orders count as 0. | `fct_orders.revenue`, `rpt_monthly_sales.revenue` |
| **Orders** | Number of completed orders. | `rpt_monthly_sales.orders` |
| **Average order value (AOV)** | Revenue ÷ orders. | `rpt_monthly_sales.average_order_value` |
| **Customers (in a month)** | Distinct customers with at least one completed order in the month. | `rpt_monthly_sales.customers` |
| **New customer** | A customer whose first completed order is in that month. | `rpt_monthly_sales.new_customers` |
| **Returning customer** | A customer who buys in the month and had already bought in an earlier month. New + returning = customers. | `rpt_monthly_sales.returning_customers` |
| **Customer type** | `no purchase` (0 completed orders), `one-time` (1), `repeat` (2 or more). | `dim_customers.customer_type` |
| **Repeat customer rate** | Repeat customers ÷ customers with at least one purchase. | dashboard |
| **Cohort** | All customers whose first completed order is in the same month. | `dim_customers.cohort_month` |
| **Retention rate** | For a cohort and a number N: customers of the cohort who buy in month N after the first purchase ÷ customers in the cohort. Month 0 is always 100%. | `rpt_cohort_retention.retention_rate` |
| **Session (visit)** | A group of events from one visit to the website or app. | `fct_sessions` |
| **Cart rate** | Visits with at least one "add to cart" ÷ all visits. | `rpt_funnel_monthly.cart_rate` |
| **Conversion rate** | Visits ending with a purchase ÷ all visits. | `rpt_funnel_monthly.conversion_rate` |

## Example

A customer first buys in March 2026 and buys again in May 2026.

- They are a **new customer** in March and a **returning customer** in May.
- Their **cohort** is March 2026.
- In the March cohort they count as active in month 0 (March) and month 2 (May), not in month 1 (April).
- Their **customer type** is `repeat`.
