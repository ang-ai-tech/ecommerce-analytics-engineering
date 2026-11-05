# Data quality issues and how they are handled

The generator puts these issues in the raw data on purpose, like the ones found in real exports.

| Issue in the raw data | Example | Where it is fixed | Test that proves it |
|---|---|---|---|
| Customers exported twice (old and new version) | customer 42 appears with two `updated_at` values | `stg_customers`: keep the newest row per customer (`qualify row_number() ... = 1`) | `unique` on `stg_customers.customer_id` |
| E-mails with capital letters or spaces | `"  user00042@example.com "`, `USER00042@EXAMPLE.COM` | `stg_customers`: `lower(trim(email))` | — |
| One status written in many ways | `completed`, `Completed`, `COMPLETE`, `Canceled` | `stg_orders`: a `case` maps every spelling to one value | `accepted_values` on `status` + unit test `test_order_status_spellings_are_unified` |
| Test orders from the QA team | e-mails ending in `@qa.example.com` | `stg_customers` flags them, `int_orders` removes them | `assert_no_test_accounts_in_marts` |
| Everything is text in the export | `"24.90"`, `"2026-03-01 10:15:00"` | staging casts every column to its type | model contracts on `fct_orders` and `dim_customers` |
| Product prices change over time | Kitchen and Lighting are 8% more expensive from 2026 | revenue uses the price on the **order line**, not today's product price | `assert_revenue_matches_order_items` |
| Two systems must agree | shop orders vs web purchase events | `fct_sessions` keeps the order of each purchase visit | `assert_every_order_has_a_purchase_visit` + `relationships` test |
| Late-arriving web events | an event arrives a day after it happened | `fct_web_events` re-reads the last 3 days on each incremental run | `unique` on `event_id` |

## Row counts (seed 42, full period)

| Table | Raw rows | After cleaning |
|---|---|---|
| customers | 3,102 | 3,010 in `stg_customers` (duplicate versions removed); 3,000 in `dim_customers` (10 test accounts removed) |
| orders | 3,928 | 3,908 in `fct_orders` (20 test orders removed) |
