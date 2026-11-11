"""CSV -> SQLite ingestion with replay-safe UPSERT.

Run from the repository root: uv run python Module04/ingest.py [csv] [db]
First run Module04/run_module4.py to create a seeded edge.db.
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPSERT_SQL = """
INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (?, ?, ?, ?)
ON CONFLICT(sensor_id, ts) DO UPDATE SET
    value = excluded.value,
    interval_s = excluded.interval_s
"""


def ingest(csv_path: Path, db_path: Path) -> tuple[int, int]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = [
            (int(row["sensor_id"]), row["ts"], float(row["value"]), int(row["interval_s"]))
            for row in csv.DictReader(handle)
        ]
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_reading_sensor_ts ON reading(sensor_id, ts)")
        with conn:
            conn.executemany(UPSERT_SQL, rows)
        total = conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
    return len(rows), total


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "readings.csv"
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "edge.db"
    inserted, total = ingest(source, target)
    print(f"Processed {inserted} CSV rows; reading table contains {total} rows.")
