# PROJECT_BRIEF_2
## Atomic: ATOMIC_PYTHON_CORE_TABULAR | Phase: JUNIOR_CORE

## Capabilities Targeted
1. **3.1.1 — HTTP ingestion** (timeout, retries, non-2xx handling)
2. **3.1.6 — Grouped aggregations**, curated output tables
3. **3.1.7 — Ingestion contract** (required cols, dtypes, missingness, schema report)
4. **3.1.8 — Parquet output + safe-write** (temp → rename)
5. **3.1.9 — Logging module** (log levels, module loggers, no print)
6. **3.1.11 — Unit tests** (pytest, normal + edge case per function)

## Baseline Requirements
These capabilities are already Strong and must be present as hygiene — they are not evaluation targets.

- **3.1.3 — PEP 8 / readability**: consistent naming, type hints, idiomatic constructs
- **3.1.4 — DataFrame transformations**: vectorized operations, no row-level loops
- **3.1.5 — Joins/merges, key handling**: correct key alignment, duplicate/null key awareness
- **3.1.10 — Post-transform validation**: row counts, required columns, key uniqueness checks (carry forward and extend — post-transform checks were adequate but incomplete in PROJECT_1)

## Business Context

A fintech analytics team tracks currency exchange rates for a basket of currencies against a base currency. Each morning, the team needs a fresh summary of recent rate movements to flag currencies that have drifted significantly. Two data sources feed this process:

1. **A public REST API** providing current and recent daily exchange rates (e.g., exchangerate.host, frankfurter.app, or any open exchange rate API that returns JSON with date-keyed rates).
2. **A local CSV file** containing historical reference rates — a baseline snapshot the team maintains, including columns the API does not provide (e.g., internal currency-group classification, regional tags).

The team wants a single pipeline that merges both sources, computes summary statistics per currency over a configurable lookback window, and writes the result as a stable Parquet file that downstream dashboards consume. The pipeline runs daily; it must not corrupt the output if the API is temporarily down, and it must be safe to rerun without manual cleanup.

## Objective

Build a Python pipeline (script/module, not notebook) that ingests exchange rate data from a REST API and a local CSV file, validates both against an explicit ingestion contract, merges them on currency code, computes grouped aggregation summaries per currency, validates the output, and writes the result as Parquet using a safe-write pattern. All operational output uses structured logging.

## Deliverables
- [ ] **Ingestion module**: fetches exchange rate data from an HTTP API endpoint with timeout, bounded retries with backoff, and explicit non-2xx handling. Also reads the local CSV reference file. Both sources are validated against a declared ingestion contract immediately after loading.
- [ ] **Schema report**: produced post-ingestion for each source — columns, dtypes, row count, missing-value counts. Used to fail fast or apply documented adaptation when inputs violate expectations.
- [ ] **Transformation module**: merges API data with CSV reference data on currency code. Computes grouped aggregations per currency over the lookback window: at minimum mean rate, min, max, and a spread/volatility measure. Produces a curated output table with predictable, stable schema (explicit column names, types, sort order).
- [ ] **Parquet output**: writes the curated summary table as Parquet (pyarrow) with stable schema — no accidental index columns, explicit column ordering. Uses safe-write pattern (write to temp file → atomic rename). CSV may be produced as an additional output but is not the primary format.
- [ ] **Validation checks**: post-transform validation on the output — row counts, required columns present, key uniqueness/non-null on currency code. Fail fast with clear, actionable error messages on check failure.
- [ ] **Documentation**: design decisions and trade-offs in the learner's own words. Must cover: ingestion contract rationale (why these dtypes, why this missingness policy), merge strategy, aggregation choices, safe-write reasoning. Formatting cleanup via Gemini is acceptable; content must be defensible under evaluation questioning.
- [ ] **AI interaction log**: what was asked, what was taken from the answer. Submitted with deliverables.
- [ ] **Unit tests**: pytest tests for at least one core transformation/aggregation function. Each test covers a normal case and at least one edge case (e.g., single currency, all-null rates, duplicate keys). Uses fixture DataFrames, not live API calls.

## Technical Requirements

**HTTP ingestion (3.1.1):**
- At least one data source is an HTTP API endpoint returning JSON
- Every request has an explicit timeout
- Transient failures (network errors, 5xx) are retried with bounded retries and backoff
- Non-2xx responses are handled explicitly — no silent failures
- Failed requests are logged with sufficient detail to diagnose

**Ingestion contract (3.1.7):**
- Required vs optional columns declared for each source
- Dtype expectations declared (which columns must be numeric, which are strings, date format)
- Missingness/sentinel policy documented (what happens when a rate is null, when a currency is missing)
- Schema report produced immediately post-ingestion for each source
- Contract violations trigger fail-fast or explicitly documented adaptation — no silent acceptance

**Grouped aggregations (3.1.6):**
- At least one groupby aggregation producing summary statistics per currency
- Output table has predictable schema: stable column names, explicit types, sorted
- Aggregation results are deterministic across reruns with the same input

**Parquet + safe-write (3.1.8):**
- Primary output is Parquet via pyarrow
- No accidental index columns in the Parquet file
- Column ordering is explicit
- Write uses temp file → atomic rename pattern
- Rerun does not require manual cleanup of partial files

**Logging (3.1.9):**
- All informational and error output uses the Python `logging` module
- Module-level loggers (not root logger only)
- Appropriate log levels (DEBUG/INFO/WARNING/ERROR used meaningfully)
- No `print()` statements, no `sys.stderr.write()`, no `typer.secho()` for operational output

**Unit tests (3.1.11):**
- At least one pytest unit test for a core transformation or aggregation function
- Uses fixture DataFrames (not live data)
- Covers at least one normal case and one edge case
- Tests are independently runnable (`pytest` from repo root)

**Post-transform validation (3.1.10 — baseline, extended):**
- At least one validation check runs after transformation and before output write
- Checks include: row count > 0, required columns present, currency key is unique and non-null
- Failures produce clear, actionable error messages

**Idempotency:**
- Rerunning the pipeline with the same inputs produces the same output without manual cleanup

## Constraints
- **Allowed tools**: Python 3.10+, pandas, pyarrow, requests (or httpx/urllib3), pytest, any standard library module
- **Forbidden tools**: Spark, Polars, Dask, notebook environments, ORM frameworks
- **AI usage**: Gemini permitted for concept clarification and pandas/pyarrow command lookup. Whole implementation blocks (functions, modules) must not come from AI. Documentation skeleton must be learner's own words; formatting/prose cleanup via Gemini is acceptable.

## Success Criteria

Mapped to atomic done criteria (3.2):

1. **Working end-to-end pipeline** as script/module (not notebook) that ingests from one local file source and one HTTP API endpoint, transforms, validates, and writes Parquet
2. **Code organized** into functions/modules with clear separation of concerns (ingest / transform / validate / output)
3. **HTTP ingestion** includes timeout, bounded retries, explicit non-2xx handling, and logged failures
4. **Ingestion contract** is explicit and documented: required columns, dtype expectations, missingness policy
5. **Schema report** is produced post-ingestion and used to trigger fail-fast or documented adaptation
6. **Parquet output** has stable schema, written via safe-write pattern (temp → rename)
7. **All logging** is via `logging` module — no print statements in final code
8. **At least one validation check** runs post-transform and produces a clear error on failure
9. **At least one pytest unit test** covers a core transformation function with normal case + edge case
10. **PEP 8 compliant**, structured for readability and reuse
11. **Idempotent**: reruns produce the same output without manual cleanup
