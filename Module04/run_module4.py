"""Rebuild and verify Module 04, then save genuine local evidence in results.txt.

Command (from repository root): uv run python Module04/run_module4.py
Requires SQLite >=3.37 for STRICT tables.
"""
from __future__ import annotations

import os
import platform
import sqlite3
import stat
import statistics
import time
from pathlib import Path

from ingest import ingest, UPSERT_SQL

HERE = Path(__file__).resolve().parent
DB = HERE / "edge.db"
RESULTS = HERE / "results.txt"
report: list[str] = []


def log(message: object = "") -> None:
    line = str(message)
    print(line)
    report.append(line)


def section(title: str) -> None:
    log("\n" + "=" * 68 + "\n" + title + "\n" + "=" * 68)


def connect(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    return conn


def check_rejection(conn: sqlite3.Connection, label: str, sql: str, fragment: str) -> None:
    try:
        conn.execute(sql)
    except sqlite3.IntegrityError as error:
        assert fragment.lower() in str(error).lower(), (label, error)
        log(f"REJECTED | {label} | {type(error).__name__}: {error}")
    except sqlite3.Error as error:
        assert fragment.lower() in str(error).lower(), (label, error)
        log(f"REJECTED | {label} | {type(error).__name__}: {error}")
    else:
        raise AssertionError(f"Unexpectedly accepted: {label}")


def study_test() -> None:
    section("TASK A: unconstrained versus constrained table")
    with sqlite3.connect(":memory:") as conn:
        conn.execute("CREATE TABLE raw(sensor_id INTEGER, metric TEXT, value REAL)")
        bad = [(1, "temp_c", 9000), (1, "temp_c", "hot"), (2, "bogus", -500),
               ("abc", "temp_c", 20), (None, None, None), (1, "Temp_C", 20)]
        conn.executemany("INSERT INTO raw VALUES (?,?,?)", bad)
        log(f"Unconstrained table accepted {conn.execute('SELECT COUNT(*) FROM raw').fetchone()[0]} suspicious rows.")
        for row in conn.execute("SELECT sensor_id, typeof(sensor_id), metric, value, typeof(value) FROM raw"):
            log(f"  stored: {row}")
        conn.execute("""CREATE TABLE guarded(
          id INTEGER PRIMARY KEY, sensor_id INTEGER NOT NULL,
          metric TEXT NOT NULL CHECK(metric IN ('temp_c','vib_rms','spindle_load')),
          value REAL CHECK(value BETWEEN -273.15 AND 5000)
        ) STRICT""")
        tests = [
            ("9000 degrees", "1,'temp_c',9000", "CHECK constraint failed"),
            ("text hot", "1,'temp_c','hot'", "cannot store TEXT"),
            ("unknown metric", "2,'bogus',-500", "CHECK constraint failed"),
            ("text sensor id", "'abc','temp_c',20", "cannot store TEXT"),
            ("missing sensor id", "NULL,'temp_c',20", "NOT NULL constraint failed"),
            ("case-sensitive metric", "1,'Temp_C',20", "CHECK constraint failed"),
        ]
        for label, values, error in tests:
            check_rejection(conn, label, f"INSERT INTO guarded(sensor_id,metric,value) VALUES ({values})", error)
        conn.execute("INSERT INTO guarded(sensor_id,metric,value) VALUES (1,'temp_c',NULL)")
        conn.execute("INSERT INTO guarded(sensor_id,metric,value) VALUES (1,'temp_c','20')")
        conn.execute("INSERT INTO guarded(sensor_id,metric,value) VALUES (1,'temp_c',4999)")
        log("Accepted NULL through CHECK (no NOT NULL on guarded.value), text '20' coerced to 20.0, and plausible 4999.")
        for row in conn.execute("SELECT sensor_id,metric,value,typeof(value) FROM guarded"):
            log(f"  accepted: {row}")


def benchmark(with_alarm: bool) -> tuple[float, int]:
    samples: list[float] = []
    alarm_count = 0
    readings = [(2, f"2026-03-02 {i // 3600:02}:{(i // 60) % 60:02}:{i % 60:02}",
                 1.0 + (i % 15) / 10, 1) for i in range(10000)]
    for _ in range(3):
        with connect(":memory:") as mem:
            mem.executescript((HERE / "setup.sql").read_text(encoding="utf-8"))
            mem.execute("INSERT INTO sensor VALUES (2,'cnc-01','vib_rms','mm/s')")
            mem.executescript((HERE / "triggers.sql").read_text(encoding="utf-8"))
            if not with_alarm:
                mem.execute("DROP TRIGGER trg_vib_alarm")
            t0 = time.perf_counter()
            with mem:
                mem.executemany("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (?,?,?,?)", readings)
            samples.append((time.perf_counter() - t0) * 1000)
            alarm_count = mem.execute("SELECT COUNT(*) FROM alarm").fetchone()[0]
    log(f"{'With' if with_alarm else 'Without'} alarm trigger: 3 runs (ms) "
        + ", ".join(f"{x:.1f}" for x in samples)
        + f"; median {statistics.median(samples):.1f} ms; alarms {alarm_count}")
    return statistics.median(samples), alarm_count


def main() -> None:
    section("RUN CONTEXT")
    log(f"Python: {platform.python_version()}; SQLite: {sqlite3.sqlite_version}; OS: {platform.system()}")
    log("Generated on this execution environment; timings are machine-dependent.")
    if tuple(map(int, sqlite3.sqlite_version.split('.'))) < (3, 37, 0):
        raise RuntimeError("SQLite 3.37+ required for STRICT tables")
    study_test()

    section("SETUP AND TASK 1: constraints and generated column")
    if DB.exists():
        os.chmod(DB, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        DB.unlink()
    conn = connect(DB)
    try:
        conn.executescript((HERE / "setup.sql").read_text(encoding="utf-8"))
        conn.execute("INSERT INTO sensor VALUES (1,'cnc-01','temp_c','degC'), (2,'cnc-01','vib_rms','mm/s')")
        conn.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:00',41.5,1)")
        tests = [
            ("domain: 9000", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:01',9000,1)", "CHECK constraint failed"),
            ("STRICT: hot", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:02','hot',1)", "cannot store TEXT"),
            ("foreign key: sensor 99", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (99,'2026-03-01 08:00:03',40,1)", "FOREIGN KEY constraint failed"),
            ("UNIQUE: duplicate cnc-01/temp_c", "INSERT INTO sensor VALUES (3,'cnc-01','temp_c','degC')", "UNIQUE constraint failed"),
            ("CHECK: interval 0", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:04',40,0)", "CHECK constraint failed"),
            ("NOT NULL: value", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:05',NULL,1)", "NOT NULL constraint failed"),
        ]
        for label, sql, error in tests:
            check_rejection(conn, label, sql, error)
        row = conn.execute("SELECT value,interval_s,energy_j FROM reading").fetchone()
        assert row == (41.5, 1, 41.5)
        log(f"Generated energy_j: {row[0]} * {row[1]} = {row[2]}")
        conn.commit()
        with sqlite3.connect(DB) as unsafe:
            unsafe.execute("PRAGMA foreign_keys = OFF")
            unsafe.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (99,'2026-03-01 08:00:03',40,1)")
            log("With foreign_keys=OFF, orphan reading is accepted (then rolled back).")
            unsafe.rollback()
        assert conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0] == 1

        section("TASK 2: UPSERT and double CSV replay")
        conn.execute("CREATE UNIQUE INDEX ux_reading_sensor_ts ON reading(sensor_id,ts)")
        conn.execute(UPSERT_SQL, (1, "2026-03-01 08:00:00", 41.7, 1))
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM reading WHERE sensor_id=1 AND ts='2026-03-01 08:00:00'").fetchone()[0] == 1
        log("Corrected original value 41.5 -> 41.7; natural-key row count remains 1.")
        for i in (1, 2):
            processed, count = ingest(HERE / "readings.csv", DB)
            assert processed == 10 and count == 11
            log(f"CSV run {i}: processed {processed}; total readings {count}.")
        assert conn.execute("SELECT COUNT(*) FROM (SELECT 1 FROM reading GROUP BY sensor_id,ts HAVING COUNT(*) > 1)").fetchone()[0] == 0
        log("Duplicate natural keys: 0")

        section("TASK 3: triggers and timing")
        conn.executescript((HERE / "triggers.sql").read_text(encoding="utf-8"))
        conn.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (2,'2026-03-01 09:00:00',2.7,1)")
        alarm = conn.execute("SELECT sensor_id,ts,value,reason FROM alarm").fetchone()
        assert alarm == (2, "2026-03-01 09:00:00", 2.7, "vibration over 2.0 mm/s")
        log(f"Alarm fired: {alarm}")
        conn.execute("UPDATE reading SET value=1.4 WHERE sensor_id=2")
        audit = conn.execute("SELECT reading_id,old_value,new_value FROM audit").fetchone()
        assert audit[1:] == (2.7, 1.4)
        log(f"Audit fired: {audit}")
        conn.execute("UPDATE reading SET value=1.4 WHERE sensor_id=2")
        assert conn.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 1
        log("No-op update caused no extra audit row.")
        conn.commit()
        without, n1 = benchmark(False)
        with_trigger, n2 = benchmark(True)
        assert n1 == 0 and n2 == 2664
        log(f"Median trigger overhead on this environment: {with_trigger-without:.1f} ms / 10000 rows ({with_trigger/without:.2f}x).")

        section("TASK 4: view and read-only access")
        conn.execute("""CREATE VIEW machine_health AS
            SELECT s.machine_id, s.metric, MAX(r.value) AS peak, COUNT(*) AS n
            FROM sensor s JOIN reading r USING(sensor_id)
            GROUP BY s.machine_id, s.metric""")
        conn.commit()
        for row in conn.execute("SELECT machine_id,metric,peak,n FROM machine_health ORDER BY metric"):
            log(f"machine_health: {row}")
        assert conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0] == 12
    finally:
        conn.close()

    previous_mode = stat.S_IMODE(DB.stat().st_mode)
    try:
        os.chmod(DB, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        log("chmod 444 equivalent: " + stat.filemode(DB.stat().st_mode))
        ro = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
        try:
            log(f"mode=ro SELECT COUNT(*): {ro.execute('SELECT COUNT(*) FROM reading').fetchone()[0]}")
            check_rejection(ro, "mode=ro DELETE", "DELETE FROM reading", "readonly")
        finally:
            ro.close()
        try:
            with sqlite3.connect(DB) as usual:
                usual.execute("DELETE FROM reading")
                log("Ordinary connection could write despite chmod 444 (privileged/OS-dependent); rolled back.")
                usual.rollback()
        except sqlite3.OperationalError as error:
            log(f"Ordinary connection with chmod 444 rejected write: {error}")
    finally:
        os.chmod(DB, previous_mode)
        log("Restored original file permissions.")

    section("OPTIONAL TASK 5: INSTEAD OF trigger on a view")
    with connect(":memory:") as extra:
        extra.executescript("""
        CREATE TABLE toy(id INTEGER PRIMARY KEY, value REAL NOT NULL) STRICT;
        CREATE VIEW toy_input AS SELECT id,value FROM toy;
        CREATE TRIGGER toy_view_insert INSTEAD OF INSERT ON toy_input BEGIN
          INSERT INTO toy(id,value) VALUES (NEW.id,NEW.value);
        END;""")
        extra.execute("INSERT INTO toy_input(id,value) VALUES (7,2.5)")
        assert extra.execute("SELECT id,value FROM toy").fetchone() == (7, 2.5)
        log("INSTEAD OF INSERT view trigger forwarded (7, 2.5) into its base table.")

    section("RESULT")
    log("PASS: constraints, UPSERT replay, alarms, audit, read-only mode, and view trigger.")
    RESULTS.write_text("\n".join(report) + "\n", encoding="utf-8")
    log(f"Saved {RESULTS}")


if __name__ == "__main__":
    main()
