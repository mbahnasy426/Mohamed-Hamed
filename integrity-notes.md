# Module 04 — Integrity notes

## Why integrity needs layers

| Layer | Question | Database protection | Tested example |
| --- | --- | --- | --- |
| Entity | Can rows be identified uniquely and completely? | `PRIMARY KEY`, `NOT NULL`, `UNIQUE` | The second `cnc-01`/`temp_c` sensor is rejected |
| Referential | Does the referenced sensor exist? | `FOREIGN KEY` + `PRAGMA foreign_keys=ON` on every connection | Sensor `99` is rejected |
| Domain / semantic | Do values and events make sense? | `CHECK`, `STRICT`, generated columns, triggers | `9000` and `'hot'` are rejected, vibration alerts are created |

A `CHECK` cannot generally verify another table's data in SQLite; a foreign key or trigger is needed for cross-table rules. A generated `energy_j` value is calculated consistently by SQLite as `value * interval_s`. It is a course demonstration, **not** proof that the telemetry value measures energy for every metric.

## Task A: break a database

- A normal (non-STRICT) table stored `9000`, `'hot'`, unknown metric `bogus`, a text sensor ID, a NULL record and `Temp_C`.
- With a constrained `STRICT` table, inserting those values separately raised errors showing which rule was violated. See the exact real exceptions in [results.txt](results.txt).
- `CHECK(value BETWEEN -273.15 AND 5000)` **accepts NULL** because SQL's unknown comparison does not fail a `CHECK`. To forbid NULL, use `NOT NULL` too.
- `STRICT` **accepts `'20'` in a REAL column** if SQLite can convert it without loss. `'hot'` cannot be converted.
- A reasonable-looking but wrong measurement such as `4999` passes the range check. Logical plausibility is not the same as truth.

## Tasks 1 and 2: constraint and UPSERT takeaways

1. `PRAGMA foreign_keys=ON` is a **connection-level setting**. A deliberately unsafe connection with it turned off accepted a sensor-99 orphan, then rolled the experiment back.
2. `UNIQUE(machine_id, metric)` blocks duplicate sensor definitions. A separate `UNIQUE(sensor_id, ts)` natural key prevents replay duplication in `reading`.
3. `ON CONFLICT(sensor_id, ts) DO UPDATE` corrected `41.5` to `41.7`. CSV ingestion uses `executemany` with `?` placeholders, so fields are passed as data rather than injected into SQL text.
4. Running the same 10-row CSV twice kept **11 total readings**, not 21.

## Task 3: alarms, audit, cost

- `trg_vib_alarm` runs **AFTER INSERT** when the sensor's metric is `vib_rms` and `NEW.value > 2.0`.
- `trg_reading_audit` records `OLD.value` and `NEW.value` **only when they differ**. The alarm was produced by 2.7, and the update to 1.4 produced an audit row.
- The timing script measures three separate batches of **10,000 readings** with and without the alarm trigger. It uses identical sample data and reports medians; figures depend on CPU, Python and SQLite versions. The alarm variant emits **2,664 alarm rows** by design. Look at [results.txt](results.txt) for actual values.
- AFTER is a sensible default for a derived alarm because the base reading has been inserted successfully. `BEFORE` is useful for validation and `RAISE(ABORT, ...)`; both BEFORE and AFTER triggers can reject a transaction, but writes in AFTER triggers are rolled back with it.

## Task 4: security without a server

```sh
# POSIX example; performed by the reproducible Python script where supported
chmod 444 Module04/edge.db
sqlite3 'file:Module04/edge.db?mode=ro' 'SELECT COUNT(*) FROM reading;'
sqlite3 'file:Module04/edge.db?mode=ro' 'DELETE FROM reading;'
chmod 644 Module04/edge.db
```

`machine_health` reports only `machine_id`, `metric`, `peak` and count `n`; it does not grant permission. `mode=ro` genuinely denies writes for the SQLite connection. The operating system's file permissions protect the database from other processes that do not have write rights. `chmod` alone is not a dependable per-user security model on Windows; use NTFS ACLs for equivalent file restrictions.

**PostgreSQL comparison (4 sentences).** PostgreSQL has authenticated users and database roles, so a server administrator can grant `SELECT` on a view and withhold writes to underlying tables. SQLite has no built-in `GRANT` or role management, and it depends on file access plus connection-level modes. This can be appropriate for a single local edge gateway when the device and its filesystem are controlled. It is not suitable as the only isolation for an untrusted multi-tenant web application, where users must have separate rights enforced by a server-side access model.

## Optional Task 5

I tested an `INSTEAD OF INSERT` trigger on an in-memory view; insertion into the view wrote `(7, 2.5)` into its base table. This differs from an ordinary `AFTER INSERT` trigger, which runs after a row has already been inserted into a real table.

## Pod study Task B: status

**Not yet verified.** A genuine discussion with another pod has not been recorded here. Suggested topic to compare: why NULL passes `CHECK` and why `'20'` passes STRICT. Add names, date and real feedback only after the exchange happens.

## References

- [SQLite foreign keys](https://sqlite.org/foreignkeys.html)
- [SQLite STRICT](https://sqlite.org/stricttables.html)
- [SQLite generated columns](https://sqlite.org/gencol.html)
- [SQLite UPSERT](https://sqlite.org/lang_upsert.html)
- [SQLite triggers](https://sqlite.org/lang_createtrigger.html)
