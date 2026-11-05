# ADR 0002 — Raw data kept as text, cleaned once in staging

**Status:** accepted

## Context
The raw exports contain duplicates, inconsistent spellings and test data. If every report fixes these problems on its own, the fixes differ and the numbers stop matching, which is the problem this project is meant to solve.

## Decision
- The `raw` layer shows the files exactly as received, every column as text.
- Each raw table has exactly one **staging** model, the only place where values are cast, cleaned, deduplicated and standardised. Staging models do not join tables.
- Business rules that combine tables (such as removing test orders) are applied once in the **intermediate** layer.
- Marts read only from staging and intermediate models, never from raw.

## Consequences
- When a rule changes, for example a new spelling of a status, it is changed in one model and every report follows.
- A bad value in the raw file (text where a number is expected) fails in staging, early and with a clear error, instead of producing a wrong number in a report.
- There is one more layer of models to maintain; staging models are views, so they cost no storage.
