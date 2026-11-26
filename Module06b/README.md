# Module 06b — Polyglot Persistence & the Decision

**Mohamed Hamed — HSBI Databases Portfolio**

## Introduction

In this module, the main idea was to learn about different types of databases and understand when we should use each one. It is also connected to what we studied in Module 06a.

## Learning Goals

- Understand the difference between SQLite and PostgreSQL.
- Learn how JSON works in SQLite.
- Understand how key-value storage works.
- Learn about ACID, BASE and CAP.
- Understand how to choose the right database for a project.

## Task 1 — Local vs. Server Databases

In this task, the main goal was to understand the difference between a local database and a server-based database.

SQLite is easier to use because we do not need to connect to a server. PostgreSQL allows multiple users to access the same database, but it requires a server and a connection.

One disadvantage of PostgreSQL is that if the server stops working, the users cannot access the database.

The `local_boundary.py` file demonstrates what happens when two connections try to write to the same SQLite database.

## Task 2 — JSON and Key-Value Storage

### JSON in SQLite

In this part, the experiment uses 1,000 device records to understand how JSON can be stored in SQLite.

The main functions are:

- `json_valid()` — checks if the JSON is valid.
- `json_extract()` — gets specific information from JSON.
- `json_each()` — goes through the elements inside JSON.

One thing I found interesting is that we can add new information to JSON without changing the whole database structure.

Another important point is that two queries can give the same result but have different execution plans. Using the correct index can make the query more efficient.

### Key-Value Storage

In this part, we compare SQLite and Python Shelve using 20,000 records.

The reference results are:

| Database | Write time | Read time |
|---|---:|---:|
| Shelve | 3.957 s | 0.100 s |
| SQLite | 0.027 s | 0.095 s |

These results are from the reference experiment. I still need to run the experiment on my own laptop.

I would prefer SQLite because we can store the data and also use SQL to filter and group the information.

## Task 3 — Database Decision

For this task, the main goal was to understand which database is better depending on what we want to do.

| Application | Database choice |
|---|---|
| Collecting sensor data | SQLite |
| Monthly reports | SQLite |
| Device metadata | SQLite with JSON |
| Dashboard sessions | SQLite key-value storage |
| Multiple network users | PostgreSQL |

If I had to choose one database for a small local project, I would choose SQLite because it is easier to work with and does not require a server.

However, if many users need to access and update the database at the same time, I would choose PostgreSQL.

## Important Concepts

- **ACID:** Makes sure that database transactions are reliable.
- **BASE:** Focuses on availability and allows data to become consistent over time.
- **CAP:** Explains the limitations between consistency and availability when there is a network problem in a distributed system.

## How to Run the Experiments

```powershell
uv sync
uv run python Module06b/run_module6b.py
```

## Module Files

- [json_bench.py](json_bench.py)
- [kv_compare.py](kv_compare.py)
- [local_boundary.py](local_boundary.py)
- [engine-notes.md](engine-notes.md)
- [results.txt](results.txt)
- [run_module6b.py](run_module6b.py)
- [project-ticket.md](project-ticket.md)

## My Takeaway

The most important thing in this module is understanding that not every database is suitable for every project. Before choosing a database, we need to understand the requirements of the project and what we want to achieve.

I also found it interesting that SQLite can work with different types of data, including relational data, JSON and key-value data.

This module also helps me prepare for my final project in Module 7.

## References

- [Official Module 06b](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06b-polyglot-persistence.md)
- [Module 06a](../Module06a/README.md)
- Adam Salman — Task Pod reference.
- Mohamed Nassar — Task Pod reference.

## Remaining Work

- Run the experiments on my own laptop.
- Verify PostgreSQL concurrency behaviour.
- Complete the database decision discussion with the Task Pod.
