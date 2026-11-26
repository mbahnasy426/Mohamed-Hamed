"""SQLite fallback for Module 6b Task 1 when classroom PostgreSQL is unavailable.

This demonstrates local writer contention; it is NOT evidence of a PostgreSQL
session, network outage, instructor demo, or peer discussion.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "boundary.db"
with sqlite3.connect(DB) as setup:
    setup.executescript("""
        DROP TABLE IF EXISTS machine;
        CREATE TABLE machine(
            machine_id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            parts_produced INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO machine VALUES (1, 'guetersloh', 0);
    """)
first = sqlite3.connect(DB, timeout=0.1, isolation_level=None)
second = sqlite3.connect(DB, timeout=0.1, isolation_level=None)
try:
    first.execute("BEGIN IMMEDIATE")
    first.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
    try:
        second.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
    except sqlite3.OperationalError as exc:
        assert "locked" in str(exc).lower(), str(exc)
        print("second writer while first transaction open: database is locked")
    else:
        raise AssertionError("A concurrent writer unexpectedly succeeded")
    first.execute("COMMIT")
    second.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
    result = second.execute("SELECT parts_produced FROM machine WHERE machine_id = 1").fetchone()[0]
    assert result == 2
    print("after first writer commits, second writer retries: parts_produced=2")
    print("PASS: SQLite fallback only; shared PostgreSQL experiment still pending")
finally:
    first.close()
    second.close()
