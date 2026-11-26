# Module 06a — Lab notes and discussion prep

## Story / problem

The operational SQLite database from Module 5 has a denormalized `report_jobpart` table for fast dashboard reads. Lea Winter now needs monthly and weekly reports across two years. Heavy analytics running against the active database may make operational work wait. This lab tests a **separate analytical copy** in DuckDB + Parquet and measures the trade-off with SQLite.

## Learning goal 1 — reproducible SQLite → Parquet

### Round 1: Build

- Source: `Module05/normalize.db`, table `report_jobpart`, 200,000 rows.
- Ten copies, offset by `k * 91` days where `k = 0..9`.
- Expected SQLite history row count: **10 × 200,000 = 2,000,000**. The source Module 05 data is untouched.
- The source CSV is only the 200,000 original rows; DuckDB expands these rows again during Parquet export so the two sides have the **same distribution and date shifts**.

**What if we shift by 90 instead of 91 days?** Ten copies still produce 2 million rows, but the shifted quarter boundaries are one day closer together. As months have varying lengths, `+1 month` does not mean `+30` or `+31 days` consistently.

### Round 2: Convert

- DuckDB reads the CSV with `read_csv_auto`, repeats each source row with `range(0, 10)`, and exports `report_history.parquet`.
- Validate both **row count and `ROUND(SUM(part_price),2)`** against SQLite.
- Why columnar is efficient: a query requesting four out of seven columns reads the relevant column chunks, which often compress repeated values well.
- The data checks are necessary but not sufficient: distinct rows can have equal counts and price sums. In production, compare business keys and partition-level hashes, plus fresh timestamps.

## Learning goal 2 — evidence-led engine comparison

### Round 3: Race

Run the **same two questions** against both engines: dashboard aggregate and monthly revenue/parts counts.

**Fair experiment:** warm up each engine once, run five interleaved measurements (reversing start order), report median and min–max range, and check the result groups are identical before comparing time. The output for your actual computer appears in `results.txt` and `metrics.json` after running `run_module6a.py`.

**SQL dialect trap:**

```sql
-- SQLite:
strftime('%Y-%m', done_on)
-- DuckDB:
strftime(done_on, '%Y-%m')
```

If the SQLite parameters are in the wrong order, every month can appear as NULL and timing becomes an unfair comparison. A matching business result matters more than an impressive speedup ratio.

**What would make SQLite win?** An indexed, selective point lookup (e.g. one `done_on` day) can avoid scanning the whole history. DuckDB remains attractive for full-data aggregates.

## Learning goal 3 — explain the plan

### Round 4: Plan

- `EXPLAIN QUERY PLAN` in SQLite is a **predicted** access path; look for `SCAN report_history` and possible `USE TEMP B-TREE FOR GROUP BY`.
- DuckDB `EXPLAIN ANALYZE` **runs** the query and reports row counts and operator times. Look for `TABLE_SCAN`/`READ_PARQUET`, four projected columns (`machine_id`, `site`, `technician`, `part_price`), a scan processing roughly two million rows, and `HASH_GROUP_BY` above it.
- Dominant work is scanning/aggregating the 2 million input rows, not reading the small number of final grouped results.
- `SELECT *` changes column projections; the row count alone does not tell us the number of bytes read.

## Learning goal 4 — find where DuckDB loses

### Round 5: Boundary

Measure 1,000 individual `INSERT` statements and 1,000 primary-key lookups in **both** in-memory engines. Measure a separate DuckDB `executemany` batch for comparison. These operations are OLTP-like: lots of small requests with per-statement overhead. The analytic scan is OLAP-like: large groups processed in bulk. **A columnar engine is not automatically the fastest choice for operational row-at-a-time writes.**

Avoid quoting the professor's demo times as your own measurements; use `results.txt` only after executing the scripts.

## Learning goal 5 — move the report without losing trust

### Round 6: Decide

Use `memo.md` (generated from real results by the runner) to recommend:

- **Keep in SQLite:** active job updates, operational transactions, key-based lookups.
- **Move to Parquet + DuckDB:** historical monthly/reporting scan and repeated aggregates.
- **Refresh:** generate a fresh file at shift end or nightly; validate it before replacing the published copy; record an as-of timestamp and alert if the refresh fails.
- **Staleness:** a fast but stale report can silently omit a shift's data. A `--check` comparing counts and totals catches many problems but cannot detect every incorrect value.

### Core homework and optional intense track

- `compress.py` writes zstd, compares byte sizes with the Snappy file, and checks matching data totals.
- `refresh.py --check` copies all 2 million rows from SQLite, builds a new Parquet, compares counts and checksums, and replaces the old Parquet **only on success**. Run it twice; counts and checksum should be identical even if compression-level byte layout changes.

## Pod discussion questions — to ask when in class

1. Why precisely 2 million history rows, and why 91 days?
2. How can a wrong monthly query show a fake speedup?
3. Which DuckDB plan operator reads millions of rows? Which fields were projected?
4. When does the indexed SQLite point query win? What is its query plan?
5. What part of the refresh detects a missing day? What failure could pass the count/total check?
6. If the copy is one day old, should controlling see a warning, yesterday's snapshot, or no report?

**Evidence status:** Code and explanations are prepared. Benchmark values and the completed memo are generated only by executing the runner; no in-class pod discussion is claimed here.
