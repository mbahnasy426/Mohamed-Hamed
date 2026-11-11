# Module 03 — LLM-Assisted SQL & Query Profiling

This module follows the [HSBI course instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md), uses the **same warehouse schema and dataset** as [Mohamed Nassar's work](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module03), and is consistent with [Mohamed Hamed's Module 3 reflection](https://github.com/mbahnasy426/Mohamed-Hamed/blob/main/Reflections/ref03.md). Scripts and explanations are maintained in this portfolio; numerical timings should be measured on each machine.

## Learning-goal evidence

| Goal | My evidence |
| --- | --- |
| Advanced DQL: joins, groups, subqueries and windows | [AI-assisted query](llm_query.sql), [optional rewrites](stretcher_queries.sql) |
| Explain SCAN, SEARCH, COVERING, and temp B-trees | [Recorded query plans](results.txt), [study notes](sql-notes.md) |
| Measure index effects with medians and negative tests | [Benchmark code](bench.py), [results](results.txt) |
| Check AI-generated SQL for accuracy, performance and edge cases | [Runner assertions](run_module3.py), [correctness notes](sql-notes.md) |
| Demonstrate SQL injection and the safe fix | [Injection demonstration](injection_demo.py), [results](results.txt) |
| Translate SQL into relational algebra | [Algebra notes](algebra.md) |

## Completed in the reproducible scripts

- **Pod study Task A:** predict and inspect scans/searches on the Module02 sample, with and without an index.
- **Task B:** write the algebra translation and compare to SQL.
- **Task 1:** run the AI-assisted city report, compare its entire result to the provided reference, examine a real query plan, and prove the no-orders edge case.
- **Task 2:** measure dashboard and single-day lookup at four indexing stages. Three runs per stage, medians, and batched small query. Save the actual plans.
- **Task 3:** show a malicious name string returning 2,000 customers in an intentionally unsafe query and zero with a bound parameter; demonstrate apostrophe crash.
- **Task 4:** translate the query into σ, π, ⋈ and γ.
- **Optional Task 5:** run and compare aggregation, correlated subquery, and window function versions of a late-orders report.

**Not done by a script:** Task C (talking to a neighboring pod), real in-class discussion/curiosity swap, or any Discord post. Add honest evidence only when it happens.

## How to run in VS Code (PowerShell)

From your portfolio repository root:

```powershell
git pull --ff-only origin main
uv run python Module03/run_module3.py
uv run python Module03/injection_demo.py
```

The runner rebuilds `Module03/warehouse.db` from [setup.sql](setup.sql), verifies 2,000 customers / 500 products / 60,000 orders / 240,000 order lines, then saves the real plans and timings to `Module03/results.txt`. If you want only SQL setup, run:

```powershell
sqlite3 Module03/warehouse.db ".read Module03/setup.sql"
```

`warehouse.db` is ignored by Git. The committed `results.txt` records an **independent verification of the same queries** in an execution environment, **not a direct log from this runner or a benchmark observed on the student's Windows machine**. Running the runner on your PC overwrites the file with its direct local evidence. Run the command on your own machine before presenting times to the professor; timings and some query plans may vary by SQLite version.

## To explain it to the professor

"I used an AI-assisted SQL query to calculate customer counts and revenue by city. I compared its results with the course query and inspected EXPLAIN QUERY PLAN. I benchmarked several indexes, including a negative example where an index was not used. I demonstrated why SQL input must use bound parameters, then translated a query into relational algebra."

## Pod compatibility

- [Adam Salman](https://github.com/adamhsalman-droid/Adam.Salman-Portfolio): reproducible Module 3 scripts, checking and documentation.
- [Mohamed Nassar](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module03): warehouse benchmark and injection demo; same dataset and principles.
- [Mohamed Hamed](https://github.com/mbahnasy426/Mohamed-Hamed/blob/main/Reflections/ref03.md): learning notes on relational algebra, SCAN vs SEARCH, and AI checking.

[Main portfolio](../README.md) · [Reflection 03](../Reflections/ref03.md) · [Study notes](sql-notes.md).
