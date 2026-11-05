# ADR 0003 — Testing at four levels

**Status:** accepted

## Context
A report is only useful if people trust it. Mistakes can come from the data (a duplicate key), from the logic (a wrong `case`), from a change in a model (a renamed column), or from two systems that disagree.

## Decision
Each kind of mistake gets its own kind of test, and `dbt build` runs them all: a model's tests run right after the model is built, and a failure stops the models that depend on it.

| Level | Checks | Example |
|---|---|---|
| **Generic data tests** | Properties of a column on the real data | `unique`, `not_null`, `accepted_values`, `relationships`, custom `non_negative` |
| **Singular data tests** | A business rule across tables, as a query that must return no rows | revenue from orders = revenue from order lines |
| **Unit tests** | The logic of one model on small hand-written inputs, independent of the real data | every status spelling maps to the right status |
| **Model contracts** | The names and types of the columns of a model | `fct_orders.revenue` must stay `decimal(12, 2)` |

## Consequences
- Data tests catch problems in the data; unit tests catch problems in the code, even for cases that are not in today's data (such as an unknown status).
- Contracts make `fct_orders` and `dim_customers` safe to use from the dashboard and other tools: a change that breaks their shape fails the build instead of the report.
- Python `pytest` covers only the data generator; the models are tested with dbt.
