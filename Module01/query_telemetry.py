"""Run the three required Task 6 queries and the Task 7 query, with timings."""
import sqlite3
from pathlib import Path
from time import perf_counter

database = Path(__file__).with_name("telemetry.db")
queries = [
    ("readings per machine", "SELECT machine, COUNT(*) AS n FROM readings GROUP BY machine"),
    ("peak vibration per machine", "SELECT machine, MAX(vib_rms) AS peak_vib FROM readings GROUP BY machine"),
    ("readings above alarm threshold", "SELECT COUNT(*) AS alarms FROM readings WHERE vib_rms > 2.0"),
    ("average overnight spindle load",
     """SELECT machine, ROUND(AVG(spindle_load), 2) AS avg_spindle_load
        FROM readings
        WHERE time(ts) > '18:00:00'
        GROUP BY machine
        ORDER BY avg_spindle_load DESC""")
]

with sqlite3.connect(database) as connection:
    total = connection.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    print(f"database: {database.name}, bytes: {database.stat().st_size}, rows: {total}")
    for label, query in queries:
        start = perf_counter()
        result = connection.execute(query).fetchall()
        elapsed_ms = (perf_counter() - start) * 1000
        print(f"\n{label}\nSQL: {query.strip()}\nrows: {result}\nelapsed_ms: {elapsed_ms:.3f}")
        if label == "average overnight spindle load":
            print("EXPLAIN QUERY PLAN:")
            for row in connection.execute("EXPLAIN QUERY PLAN " + query):
                print(row)
