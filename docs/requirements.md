# Requirements & Acceptance Criteria

## 1. Business context

A (fictional) online store sells home and office products in Italy, Germany, France, Spain and the Netherlands, through its website and its app. Data comes from two systems: the **shop system** (customers, products, orders) and the **web tracking** (visits and events).

Today each team builds its own reports in spreadsheets from the raw exports. Marketing, sales and management get different numbers for the same question, because:

- the customer export contains duplicate versions of some customers;
- order statuses are spelled in different ways;
- test orders from the QA team are counted as real sales;
- nobody checks that orders and website purchases agree.

## 2. Goal

Build one shared, tested and documented set of tables, with a clear definition for every metric, that all reports can use.

## 3. Stakeholders

| Persona | Need |
|---|---|
| Management | A monthly view of sales and growth they can trust |
| Marketing | Know if customers come back (retention) and where visitors drop off (funnel) |
| Product / category managers | Sales by product category |
| Data team | Rules written once, tested automatically, easy to change |

## 4. Scope

**In scope:** customers, products, orders, order lines, website and app events; cleaning and deduplication; monthly sales KPIs, category sales, cohort retention, purchase funnel; a dashboard.

**Out of scope (v1):** discounts and vouchers, shipping, partial refunds, currencies other than euro, marketing costs, real-time data.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR-1 | Each customer appears once, with the newest version of their data. |
| FR-2 | Each order has one status out of: completed, cancelled, refunded. |
| FR-3 | Orders from internal test accounts never appear in reporting tables. |
| FR-4 | Revenue counts completed orders only, using the price actually paid. |
| FR-5 | Monthly report: orders, customers (new and returning), revenue, average order value. |
| FR-6 | Cohort report: share of customers buying again N months after their first purchase. |
| FR-7 | Funnel report: visits reaching cart, checkout and purchase, per month. |
| FR-8 | A dashboard shows these reports. |

## 6. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | **Trust:** every build runs data tests; a failing test stops the pipeline. |
| NFR-2 | **Stability:** the columns of core tables used by reports are protected by contracts. |
| NFR-3 | **Efficiency:** the largest table (web events) is loaded incrementally. |
| NFR-4 | **Documentation:** every model and metric is described; lineage is visible in dbt docs. |
| NFR-5 | **Portability:** runs on a laptop with Python only; reproducible data (fixed seed). |

## 7. Acceptance criteria

- [x] `dbt build` passes with all data tests and unit tests green.
- [x] Revenue summed from orders equals revenue summed from order lines.
- [x] Every real order has exactly one website or app visit ending in a purchase.
- [x] No test account appears in `dim_customers`.
- [x] Running `dbt build` on partial data and then on full data gives the same result as a single full run.
- [x] CI runs lint, Python tests and two dbt builds on every push.
