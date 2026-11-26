# Module 06b — Polyglot Persistence & the Decision

**Adam Salman · HSBI Databases portfolio.** This module follows my [Module 06a](../Module06a/README.md) work and the professor's [official Module 6b studio](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06b-polyglot-persistence.md). The [Module 7 project brief](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/07-final-project-studio.md) asks us to bring a project ticket from Module 6b.

## Five learning goals and evidence

| Goal | What I can demonstrate |
|---|---|
| JSON in SQLite | `json_bench.py` stores 1,000 device documents, validates JSON, expands it with `json_each`, and proves two contrasting query plans |
| Key-value access | `kv_compare.py` benchmarks 20,000 keys in both `shelve` and an indexed SQLite table |
| ACID, BASE and CAP | `engine-notes.md` explains these terms against Module 4 transactions, Module 6a's refreshing copy, and the local/server boundary |
| Evidence-based engine choice | The decision record below is in `engine-notes.md`; it explicitly distinguishes my existing measurements, fresh test-environment results and instructor references |
| Server trade-offs | `local_boundary.py` is the permitted SQLite two-writer fallback; real PostgreSQL classroom observations remain pending |

## Reproduce the experiments

From the **repository root**:

```powershell
uv sync
uv run python Module06b/run_module6b.py
```

Or run `json_bench.py`, `local_boundary.py` and `kv_compare.py` separately. Each is repeatable and creates only local, Git-ignored database files. The runner writes [results.txt](results.txt) **only when all three scripts finish successfully**. Results currently checked in were produced on a separate Linux/Python 3.13.5 environment, **not my own computer**; I need to rerun on my device before reporting my own timings.

## Task 1 — Boundary: local versus server

**Completed in the instructor's shared pgweb classroom server:** logged into PostgreSQL `pod15`, queried `machine`, verified a machine row at Bielefeld, and ran increment updates from two browsers. A later read of machine 1 showed `parts_produced=3` (three successful increments over the attempts). The instructor then stopped PostgreSQL: queries failed until the service was restarted; after restart queries worked again.

**My three observations:** Shared access across browsers became easier; remote login/service management became harder; server downtime prevented all remote database queries. The exact PostgreSQL writer lock/wait behavior **was not observed**; quick committed updates are not proof of blocking. The separate `local_boundary.py` SQLite fallback demonstrates locking locally. See [engine notes](engine-notes.md#task-1--shared-postgresql-server-classroom-observation).

## Task 2 — Shape

**JSON:** The official 1,000-device sample is stored in a `STRICT` SQLite table with `CHECK(json_valid(meta))`. Broken JSON fails; adding `spindle_rpm_max` to one record needs no schema migration. The two identical vendor filters return **334 rows** each; the indexed `json_extract(meta, '$.vendor')` query uses **`SEARCH device USING INDEX ix_device_vendor`**, whereas `meta ->> 'vendor'` shows **`SCAN device`**. This is because the expression must match the expression index, not merely return the same answer.

**Key-value:** The test-environment run of 20,000 sessions recorded `shelve` set/get **3.957/0.100 s** and SQLite set/get **0.027/0.095 s**. The SQLite set path uses **one batch transaction**; `shelve` performed per-key writes and used the `dbm.sqlite3` backend. These are not controlled intrinsic engine comparisons. SQLite can answer aggregate questions with `GROUP BY` (four filters of 5,000 sessions / 25 users); `shelve` must scan keys in Python. For this workload I would choose a SQLite key-value table.

## Task 3 — Decision and defence

The one-page [engine decision record](engine-notes.md#one-page-engine-decision-record) provides one row each for ingest, month-end report, changing vendor metadata, dashboard sessions and optional network users. It answers the **one-engine** question and lists the **defence questions**. A real exchange with another Task Pod and any resulting revision must be recorded after it occurs, not invented.

## Homework and navigation

- [Runnable local evidence](results.txt) and [engine notes / decision record](engine-notes.md).
- [Project ticket for Module 7](project-ticket.md): person, decision, first query, data source.
- [Reflection 06b](../Reflections/ref06b.md), explicitly listing remaining classroom work.
- [Nassar's Module 06b](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module06b) was used for pod structure and comparison. [Hamed's portfolio](https://github.com/mbahnasy426/Mohamed-Hamed) has no Module 06b directory at the time of this preparation. All claimed execution output here belongs to this test environment, not a teammate.

**Status:** JSON experiment, local concurrency fallback, key-value homework, decision draft, project ticket, reflection: prepared and locally tested where applicable. Shared PostgreSQL connection, writes and outage/recovery **observed**; PostgreSQL transaction lock/wait, own-device timings, Module 06a own-device historical-report benchmark, and real pod defence: **still to do**.
