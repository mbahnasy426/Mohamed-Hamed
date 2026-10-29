"""Load the generated CSV into an embedded SQLite database."""
import csv
import sqlite3
from pathlib import Path

folder = Path(__file__).parent
csv_path = folder / "telemetry.csv"
db_path = folder / "telemetry.db"

with sqlite3.connect(db_path) as connection:
    connection.executescript("""
        DROP TABLE IF EXISTS readings;
        CREATE TABLE readings (
            ts TEXT NOT NULL,
            machine TEXT NOT NULL,
            temp_c REAL NOT NULL,
            vib_rms REAL NOT NULL,
            spindle_load REAL NOT NULL
        );
    """)
    with csv_path.open(newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        connection.executemany(
            "INSERT INTO readings VALUES (?, ?, ?, ?, ?)", reader
        )
    connection.commit()
    total = connection.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    print(f"loaded {total} rows into {db_path}")
