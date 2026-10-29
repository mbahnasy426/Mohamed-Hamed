# Embedded vs client/server databases — Module 1

## The trade-off

| | Embedded (SQLite) | Client/server (PostgreSQL/MySQL) |
| --- | --- | --- |
| Execution | Inside the application process | Independent server process |
| Setup | No separate database server | Server setup and connection credentials |
| Offline use | Local database file works offline | Client normally needs access to a running server |
| Concurrency | Many readers; one writer at a time | More suited to concurrent network clients |
| Typical scenario | One-machine CNC telemetry dashboard | Shared multi-user system |

For the three-machine telemetry exercise, embedded SQLite avoids running a dedicated DB server. Whether that is *faster* should be established by a fair measurement, not assumed.

## Observed SQLite workload

The saved [query-results.txt](query-results.txt) records a local SQLite database of **172,800 rows** and **10,526,720 bytes**, with real query times and an `EXPLAIN QUERY PLAN`. For example, a recorded run of the average-spindle-load query took **27.656 ms** on the original machine, with a full `SCAN readings`. This is one run, not a reliable benchmark or a comparison with a server.

## What is not yet proven

There is **no measured client/server baseline** here. To compare fairly, import the same rows into a local or network PostgreSQL instance; run equivalent queries at least three times on both systems; record median elapsed time, hardware, network setup and query plans. Do not describe an untested server result as evidence.

## Reproduce and verify

1. Run [generate_telemetry.py](generate_telemetry.py), [load_telemetry.py](load_telemetry.py) and [query_telemetry.py](query_telemetry.py).
2. Inspect [query-results.txt](query-results.txt) as the previously saved output.
3. Use [parameter-demo.py](parameter-demo.py) to see a bound parameter in a read query.
4. Add a genuine server comparison only after running it.

## Would the cloud cost money?

Running a cloud database would normally add hosting, operations and possibly network costs, paid by the company operating the CNC dashboard. **No actual cloud invoice or price comparison was measured** in this exercise. For one local dashboard and a weekly report, SQLite avoids the need to maintain a separate database server.
