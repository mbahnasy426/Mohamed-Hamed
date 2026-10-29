"""Show a bound parameter on an existing local telemetry SQLite database.

Run after generate_telemetry.py and load_telemetry.py.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("telemetry.db")
if not DB.exists():
    raise SystemExit("Missing telemetry.db: run generate_telemetry.py and load_telemetry.py first.")

machine = "cnc-02"  # Example input supplied separately from the SQL statement
sql = "SELECT machine, COUNT(*) FROM readings WHERE machine = ? GROUP BY machine"

with sqlite3.connect(DB) as conn:
    rows = conn.execute(sql, (machine,)).fetchall()

print("SQL:", sql)
print("Parameter:", machine)
print("Results:", rows)
assert len(rows) == 1 and rows[0][0] == machine, "Unexpected machine result"
