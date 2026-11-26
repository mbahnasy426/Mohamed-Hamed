# Module 06a — The Analytical Engine (DuckDB)

**Portfolio:** Adam Salman · HSBI Databases · reproducible independent lab.

Official instructions: [Module 6a, DuckDB Analytical Engine](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06a-duckdb-analytical-engine.md). The six-round structure and filenames match the professor's studio and the [Task Pod's Module06a](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module06a). This is **Module 6a**, not Module 6b (the later polyglot persistence session).

## Learning goals — what each piece proves

| Learning goal | Evidence in this folder |
|---|---|
| 1. Move a SQLite table reproducibly to Parquet | `prepare.py`, `to_parquet.py`, matching row counts and sums |
| 2. Compare same aggregates honestly | `race.py`: equal answers, warm-up, five interleaved median runs, min–max spread |
| 3. Interpret analytical execution plans | `plan.py`: DuckDB `EXPLAIN ANALYZE` alongside SQLite `EXPLAIN QUERY PLAN` |
| 4. Say when DuckDB is the **wrong** engine | `boundary.py`: 1,000 row-by-row inserts, indexed lookups and a batch variant |
| 5. Design a refreshing analytical copy | `refresh.py --check`, the updated `memo.md` and `duckdb-notes.md` |

## Run everything

From the **existing `Adam.Salman-Portfolio` repository root** (the directory containing `Module05/` and `pyproject.toml`):

```powershell
uv sync
uv run python Module06a/run_module6a.py
```

If `Module05/normalize.db` has been removed, the runner first regenerates it with your `Module05/run_module5.py` if available. You can also do this explicitly:

```powershell
uv run python Module05/run_module5.py
```

The runner does not delete the Module 05 database; `prepare.py` only rebuilds Module 6a's own `history.db`. Expect the history to contain **2,000,000** rows, expanded from 200,000 original rows by shifting dates 0–9 times by 91 days.

The results from **your own computer** are written to `Module06a/results.txt` and `Module06a/metrics.json`; after success the memo is filled with actual measured timing values. Only then should you present your own timings as evidence.

## The professor's six rounds

| Round | Script | Output and check |
|---|---|---|
| 1 · Build | `prepare.py` | `history.db`, `report_jobpart.csv`; exactly 2 million SQLite rows |
| 2 · Convert | `to_parquet.py` | `report_history.parquet`; equal count and sum of `part_price` |
| 3 · Race | `race.py` | Equal result sets; SQLite vs DuckDB medians for dashboard/monthly; indexed one-day query |
| 4 · Plan | `plan.py` | DuckDB operator and row-count evidence; SQLite scan/index plan |
| 5 · Boundary | `boundary.py` | 1,000 SQLite and DuckDB single-row insert + lookup timings; DuckDB batch inserts |
| 6 · Decide | runner generates `memo.md` | 6–8-sentence recommendation to Lea Winter and Yasmin Kaya, using measured values |

**Core homework:** `compress.py` compares Snappy and zstd Parquet copies and verifies equal rows/price totals. **Intense-track homework:** the runner calls `refresh.py --check` twice to prove the refresh is repeatable, refusing to publish mismatched counts/sums.

## Optional portfolio navigation update

After copying the files, run `uv run python Module06a/update_portfolio_readme.py` to add the Module 06a links to your existing root `README.md`. This is idempotent and does not alter Modules 01–05.

## Important correctness details

- SQLite uses `strftime('%Y-%m', done_on)`, but DuckDB uses `strftime(done_on, '%Y-%m')`. The official sample reuses a DuckDB expression in SQLite; that accidentally returns NULL month groups. Our `race.py` fixes this and **refuses to benchmark if the outputs differ**.
- Timings vary by device, cache, DuckDB version, operating system and background load; median + range and exact answer checks prevent misleading claims.
- `SUM(part_price)` and row count are basic checks, **not** a cryptographic fingerprint of each row. A stronger production reconciliation should compare keys/partitions and report freshness.
- Do **not** commit generated `.db`, `.csv`, `.parquet`, `__pycache__` or virtual environments. The existing portfolio `.gitignore` already excludes them.
- `results.txt`, `metrics.json`, `memo.md`, the scripts, and `duckdb-notes.md` are small evidence files that **can** be committed after a successful run.

## Explain it in three sentences

1. SQLite is the operational system: it handles small, frequent transactions well.
2. DuckDB can scan and group two million historical rows efficiently from columnar, compressed Parquet, without locking the operational SQLite writer for a long report.
3. Keep a timed, checked refresh to prevent reporting stale history; do not pretend DuckDB is best for every workload.

**Reflection:** [Reflections/ref06a.md](../Reflections/ref06a.md). **Reference teammate:** [Nassar Module06a scripts](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module06a).

### Limits and attendance

These scripts are independent reproducible exercises. Running them does **not** establish completion of the professor's nearest-pod discussions or an in-person check-in. Record those separately when they actually happen.
