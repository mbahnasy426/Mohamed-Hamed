# Module 06a — The Analytical Engine (DuckDB)

**Mohamed Hamed — HSBI Databases Portfolio**

## Introduction

In this module, the main idea was to learn about DuckDB and understand the difference between analytical and operational databases.

This module is connected to Module 05, where we studied normalization and denormalization. Here, we use a larger amount of data to compare SQLite and DuckDB and understand which one is better for different situations.

## Learning Goals

- Understand the difference between SQLite and DuckDB.
- Learn how to convert data from SQLite to Parquet.
- Compare the performance of both databases.
- Understand how to read and compare execution plans.
- Learn when we should and should not use DuckDB.
- Understand how to keep analytical data updated.

## Round 1 — Preparing the Data

In this part, we use the data from Module 05 and increase the number of records from 200,000 to 2,000,000.

The reason for increasing the amount of data is to see the difference in performance when working with a large database.

The `prepare.py` file creates the historical database and exports the data into a CSV file.

## Round 2 — Converting to Parquet

In this round, the main goal was to understand how Parquet works and why it is useful for analytical databases.

Parquet stores data by columns instead of rows, which makes it useful when we only need specific columns from a large amount of data.

The `to_parquet.py` file converts the data to Parquet and checks that the number of rows and the total price are the same after the conversion.

## Round 3 — Comparing SQLite and DuckDB

In this round, we compare the performance of SQLite and DuckDB by running similar queries on the same data.

The comparison includes:

- Dashboard queries.
- Monthly reports.
- Queries for a specific day.
- Aggregation queries.

An important thing in this task is to make sure that both databases return the same results before comparing their execution times.

The experiment is repeated five times, and the median execution time is used to make the comparison more reliable.

## Round 4 — Execution Plans

This part is connected to what we studied in Module 03 about query execution plans.

SQLite uses `EXPLAIN QUERY PLAN`, while DuckDB uses `EXPLAIN ANALYZE`.

These commands help us understand how the database executes a query and how much work is needed to return the results.

One important thing is that understanding the execution plan can help us understand why one query is faster than another.

## Round 5 — When Not to Use DuckDB

In this round, we compare SQLite and DuckDB when inserting 1,000 individual records and searching for specific records.

DuckDB is designed mainly for analytical queries and processing large amounts of data. However, this does not mean that it is better in every situation.

| SQLite | DuckDB |
|---|---|
| Operational databases | Analytical databases |
| Frequent small transactions | Large analytical queries |
| Individual record updates | Processing large datasets |
| Indexed lookups | Aggregations and reports |
| Row-based storage | Column-oriented processing |

I would use SQLite for collecting and updating data regularly, while I would use DuckDB for analysing historical data and creating reports.

## Round 6 — Database Decision

For this round, the main goal was to decide how we could use both databases together.

My choice would be to use SQLite as the main operational database and DuckDB for analysing the data.

Instead of running large reports directly on SQLite, we can create a Parquet copy of the data and use DuckDB to analyse it.

However, we need to refresh the analytical copy regularly to make sure that the reports are not using old information.

## Homework

### Parquet Compression

The `compress.py` file compares two compression methods:

- Snappy
- Zstandard (Zstd)

The main goal is to understand how compression can reduce the file size while keeping the same information.

### Refreshing the Data

The `refresh.py` file demonstrates how we can update the analytical copy and check that the data is correct.

This is important because the original SQLite database can change, and we need the analytical database to have updated information.

## How to Run the Experiments

From the main repository folder:

```powershell
uv sync
uv run python Module06a/run_module6a.py
```

If the Module 05 database is missing:

```powershell
uv run python Module05/run_module5.py
```

The experimental results are stored in `results.txt` and `metrics.json` after running the experiments successfully.

## Module Files

| File | Description |
|---|---|
| `prepare.py` | Prepares the historical data |
| `to_parquet.py` | Converts data to Parquet |
| `race.py` | Compares database performance |
| `plan.py` | Compares execution plans |
| `boundary.py` | Tests individual inserts and lookups |
| `compress.py` | Compares compression methods |
| `refresh.py` | Updates the analytical data |
| `memo.md` | Database recommendation |
| `duckdb-notes.md` | Module notes |
| `results.txt` | Experimental results |
| `metrics.json` | Performance measurements |
| `run_module6a.py` | Runs all the experiments |

## My Takeaway

The most important thing in this module is understanding the difference between operational and analytical databases.

Before choosing a database, we need to understand what kind of data we are working with and what we want to do with it.

I also found it interesting that we can use two different databases in the same project, where each database has its own purpose.

SQLite is more suitable for daily operations, while DuckDB is more suitable for analysing large amounts of data and creating reports.

## References

- [Official Module 06a — DuckDB Analytical Engine](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06a-duckdb-analytical-engine.md)
- [Module 05](../Module05/)
- Adam Salman — Task Pod reference.
- [Mohamed Nassar — Module 06a](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module06a)
- [Reflection 06a](../Reflections/ref06a.md)

## Remaining Work

- Verify the performance measurements on my own laptop.
- Compare and review the experimental results.
- Complete any remaining Task Pod discussions.
