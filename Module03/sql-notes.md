# Module 03 — Study notes and verification

## Sources first

- [HSBI course Module 03](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md): Tasks A–C, 1–4, optional 5.
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html): query-plan language.
- [Use The Index, Luke](https://use-the-index-luke.com/): indexes and selectivity.
- [OWASP prevention guide](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html): bound parameters.
- [Relational algebra](https://en.wikipedia.org/wiki/Relational_algebra): σ, π, ⋈, γ.

## What I studied

**DQL:** Queries are written `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY`. Their *logical* evaluation goes `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`. A portable counterexample is relying on a SELECT alias from the WHERE clause: aliases may not be available at that stage, although SQLite accepts some aliases as an extension.

**SCAN:** read all rows (or all index entries). **SEARCH:** use an index or primary key to narrow rows. **COVERING INDEX:** every needed column is in the index, so a separate table lookup is unnecessary. **TEMP B-TREE:** a temporary structure is needed for grouping, sorting, or DISTINCT.

**Task A — predictions:** without extra indexes, `technician = 'Beier'`, `machine_name = 'cnc-02'` and `technician LIKE '%ei%'` should all scan. An index on `maint_job(technician)` should help exact-match technician, not machine, and not leading-wildcard LIKE. Verify by running the script; SQLite versions can choose different plans.

**Task B — algebra:** `σ[technician='Beier'](maint_job)` matches the WHERE filter. My longer dashboard translation is in [algebra.md](algebra.md).

**Task 1 — AI check:** ask an LLM for city revenue in 2025 with distinct customer counts; compare its output with the course reference using an exact result assertion. Important edge case: an inner join excludes a city if it has no orders.

**Task 2 — benchmark:** use at least three runs per step, a median, and a large batch for very fast single-day lookups. Indexes are helpful only when they let SQLite skip enough work. Measure rather than assume; local results are in [results.txt](results.txt).

**Task 3 — safety:** a crafted input `' OR '1'='1` makes the vulnerable string-concatenation query return every customer. SQL parameters (`?`) send the text separately, so the input cannot become SQL. Hand-escaping apostrophes fails for numeric contexts and other cases.

**Task 4 — algebra:** JOIN corresponds to ⋈, WHERE to σ, SELECT to π, grouping to γ. Classic relational algebra does not include ORDER BY.

**Task 5 — stretcher:** compare GROUP BY, correlated subquery and window functions, and explain their different plans.

## Curiosities to share with the pod

- The optimizer may begin with the 240,000-row `order_line` table rather than `orders`. Source: Task 1 plan in results.txt.
- The dashboard may become slower after adding an index; an index is not automatically an improvement. Source: Task 2 benchmark.
- A function wrapping `ordered_on` can prevent a normal date index from being used. Source: Task 2 negative test.
- The synthetic data may show exactly 500 customers per city but different city revenue. Why? Generated modulo-based ids correlate customers and products. Source: setup.sql and dashboard output.
- `WITH RECURSIVE` generates 240,000 rows without a source number table. Source: setup.sql.
- Open question: Why does SQLite sometimes show a separate `USE TEMP B-TREE FOR count(DISTINCT)`?

## Task C — neighboring-pod discussion

**Pending actual student action:** compare SQLite versions and plan output with another pod, then swap two curiosities. Neither this file nor the reflection claims a conversation occurred. Record participants, actual points of agreement/disagreement, and date **after** it happens.

Pod references: [Mohamed Nassar](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module03) (same warehouse example and benchmark) and [Mohamed Hamed](https://github.com/mbahnasy426/Mohamed-Hamed/blob/main/Reflections/ref03.md) (relational algebra and index learning; says no peer exchange yet).
