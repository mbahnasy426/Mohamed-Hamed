# Task 4 — SQL to relational algebra

## Simple plan-safari example

SQL: `SELECT * FROM maint_job WHERE technician = 'Beier'`

Relational algebra: **σ[technician = 'Beier'](maint_job)**.

There is no explicit π (projection) because `SELECT *` keeps all columns.

## City revenue dashboard

The source tables are customer **C**, orders **O**, order_line **L**, and product **P**.

1. Join records by keys: **C ⋈[C.customer_id=O.customer_id] O ⋈[O.order_id=L.order_id] L ⋈[L.product_id=P.product_id] P**.
2. Filter 2025: **σ[ordered_on ≥ '2025-01-01' ∧ ordered_on < '2026-01-01']**.
3. Group by city: **γ[city; COUNT(DISTINCT customer_id), SUM(qty × price)]**.
4. Return city, distinct customers and revenue; the aggregation already projects these values.
5. `ORDER BY revenue DESC` sorts the result, but ordering is not an operator in classical relational algebra.

The query plan may reorder the joins for performance without changing the answer.

## Optional Task 5 — group, subquery, window

The three solutions are in [stretcher_queries.sql](stretcher_queries.sql). The [runner](run_module3.py) compares their full ordered result sets and records their plans. The correlated version can be slower without an index on `orders(customer_id, status)`; the runner adds that separate index only **after** the Task 2 benchmark.

Sources: [course Module 03](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/03-llm-assisted-sql-and-query-profiling.md) and [relational algebra](https://en.wikipedia.org/wiki/Relational_algebra).
