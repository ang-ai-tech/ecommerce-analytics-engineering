# ADR 0001 — DuckDB as the warehouse

**Status:** accepted

## Context
The project must be easy to run for anyone who opens the repository, including CI, with no cloud account, password or database server. The focus is on the modelling and testing work, not on the infrastructure (which is covered by the Financial Data Platform project with PostgreSQL and Airflow).

## Decision
Use **DuckDB**, an analytical database stored in one file, with the `dbt-duckdb` adapter.

## Consequences
- `pip install` is the only setup step; a full `dbt build` takes a few seconds.
- DuckDB reads CSV files directly, so no separate loading script is needed.
- The models use standard SQL plus a few DuckDB conveniences (`qualify`, `filter`, `date_diff`) that also exist in Snowflake, BigQuery or Databricks with small changes. Moving to a cloud warehouse means changing `profiles.yml` and the raw sources, not the business logic.
- DuckDB allows one writer at a time: the dashboard opens the file read-only and closes the connection after each query, so `dbt build` can run while the dashboard is open.
