# Task 7 — LLM-assisted SQL profiling

## Prompt given to ChatGPT

> Here is my SQLite table: `readings(ts TEXT, machine TEXT, temp_c REAL, vib_rms REAL, spindle_load REAL)`. Write a query that returns, for each machine, the average spindle load for readings taken overnight (after 18:00), ordered by average load descending.

## AI-generated SQL

```sql
SELECT machine, ROUND(AVG(spindle_load), 2) AS avg_spindle_load
FROM readings
WHERE time(ts) > '18:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC;
```

## Execution results (recorded from a real run)

Executed using `uv run python module-01/query_telemetry.py` against the local `telemetry.db` containing 172,800 readings. The recorded output in [query-results.txt](query-results.txt) was:

| Machine | Average spindle load |
| --- | ---: |
| cnc-03 | 60.43 |
| cnc-01 | 60.37 |
| cnc-02 | 60.36 |

**Recorded execution time:** 27.656 ms (one run; timing may vary).

The output has one row per machine, and the average spindle loads are sorted in descending order.

## EXPLAIN QUERY PLAN (recorded)

```text
(7, 0, 216, 'SCAN readings')
(12, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')
(52, 0, 0, 'USE TEMP B-TREE FOR ORDER BY')
```

SQLite scanned the `readings` table and used temporary B-trees for grouping and sorting. This explains how the query was processed; the plan is not by itself proof that the query's interpretation of “overnight” is correct.

## Challenge and verification

The AI-generated SQL executed successfully and returned one average per machine in descending order. I compared its output with the saved execution results and inspected `EXPLAIN QUERY PLAN`. However, the prompt's word **overnight** is ambiguous: `time(ts) > '18:00:00'` includes only readings after 18:00 and before midnight, and excludes exactly 18:00 and all after-midnight readings. Therefore, the SQL does **not** cover a complete 18:00–06:00 night shift.

If the intended shift is 18:00–06:00, an appropriate time filter would be:

```sql
WHERE time(ts) >= '18:00:00' OR time(ts) < '06:00:00'
```

This proposed correction has **not** been rerun or timed in the saved evidence, so I do not claim new results for it. The lesson is to test AI-generated SQL, inspect the actual output and query plan, and check whether the query matches the question's intended meaning.
