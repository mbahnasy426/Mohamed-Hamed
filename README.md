# Module 04 — Data Integrity, Constraints & Edge Triggers

**Adam Salman · HSBI Databases Portfolio**

This module follows the [instructor's Module 4](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/04-integrity-constraints-and-triggers.md) and uses the **same machine/sensor example** as [Mohamed Nassar's Module04](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio/tree/main/Module04). The scripts here are independently runnable; results are measured rather than copied from another student.

## What is in this folder?

| File | Purpose |
| --- | --- |
| [setup.sql](setup.sql) | STRICT sensor/reading schema, foreign key, constraints, and generated `energy_j` |
| [triggers.sql](triggers.sql) | `AFTER INSERT` vibration alarm and `AFTER UPDATE` change audit |
| [readings.csv](readings.csv) | Ten reproducible sample readings |
| [ingest.py](ingest.py) | Parameterized `executemany()` UPSERT CSV loader |
| [run_module4.py](run_module4.py) | One-command verification of Tasks A, 1–4 and optional Task 5 |
| [results.txt](results.txt) | Actual example run output from the stated execution environment |
| [integrity-notes.md](integrity-notes.md) | Concepts, unexpected cases, pod-study and security comparison |
| [ref04.md](../Reflections/ref04.md) | Reflection draft with honest completion status |

## Run it in VS Code

Open the root of **Adam.Salman-Portfolio** in VS Code, then use its terminal:

```powershell
git pull --ff-only origin main
uv run python Module04/run_module4.py
```

Or, if Python 3.14 is installed and SQLite is at least 3.37:

```powershell
python Module04/run_module4.py
```

The runner deletes and **recreates only** `Module04/edge.db`, runs assertions, and saves a fresh `Module04/results.txt`. Do not run it against a production database. The generated database file is intentionally ignored by Git. To ingest the CSV again without rebuilding:

```powershell
uv run python Module04/ingest.py
```

### Evidence by task

**Task A — acceptance test:** A weak SQLite table accepts out-of-range temperatures, free-text values and invalid metric labels. A `STRICT` table with `CHECK` and `NOT NULL` refuses them. The test also proves that `CHECK` alone accepts `NULL`, and `STRICT` can coerce `'20'` into a valid REAL.

**Task 1 — constraints:** A valid reading is inserted (`41.5`, `interval_s=1`), so the generated column yields **`energy_j=41.5`**. Rejected SQL statements and their exact exception messages appear in [results.txt](results.txt): temperature `9000`, value `'hot'`, non-existent sensor `99`, duplicate `cnc-01/temp_c`, interval `0`, and NULL value. The connection with `PRAGMA foreign_keys=OFF` demonstrates that a foreign key declaration alone is not enough.

**Task 2 — replay-safe ingestion:** A unique index on `(sensor_id, ts)` defines the natural key. `UPSERT` updates the initial reading from `41.5` to `41.7` instead of duplicating it. The Python CSV loader uses bound parameters and runs twice: **11 rows after run 1, 11 after run 2**, with **zero duplicate keys** (1 original row + 10 CSV timestamps).

```sql
CREATE UNIQUE INDEX ux_reading_sensor_ts ON reading(sensor_id, ts);
INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (1, '2026-03-01 08:00:00', 41.7, 1)
ON CONFLICT(sensor_id, ts) DO UPDATE
SET value = excluded.value, interval_s = excluded.interval_s;
```

**Task 3 — triggers:** A new `vib_rms` value of `2.7` creates a row in `alarm`; changing the reading to `1.4` creates an `audit` row with old/new values. The audit trigger skips no-op updates, so replaying exactly the same value does not generate an extra audit record. The runner benchmarks **10,000 readings**, with/without the alarm trigger, using three runs each and reporting the medians. Benchmarks are **environment-dependent**: use your own `results.txt` to present measurements from your laptop.

**Task 4 — access control:** `machine_health` gives report readers a limited projection: machine, metric, peak and sample count. A connection opened with `mode=ro` can `SELECT`, but a `DELETE` fails. The runner attempts `chmod 444`, tests a normal connection, and restores file permissions in a `finally` block. On Windows, Unix `chmod` semantics do **not** map exactly to NTFS permissions; an administrator or privileged process may also bypass POSIX file restrictions. **A view is not, by itself, an authorization boundary.**

**Task 5 — optional extension:** Demonstrates an `INSTEAD OF INSERT` trigger on a simple view, forwarding a view insert to its base table without changing the Module04 sample.

## What remains manual?

**Pod Task B** (sharing observations with another pod) is a real discussion and cannot be completed by a script. Record it in [integrity-notes.md](integrity-notes.md) after it happens. Also run the command above in your local VS Code and keep the generated output; the committed example [results.txt](results.txt) was verified in a separate execution environment, **not** on Adam's computer.

[Main portfolio](../README.md) · [Reflection 04](../Reflections/ref04.md)
