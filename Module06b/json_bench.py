"""Module 6b, Task 2: JSON validation, expansion and expression-index proof.

Run from the repository root: uv run python Module06b/json_bench.py
Generated database is ignored by Git.
"""
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
with sqlite3.connect(HERE / "polyglot.db") as con:
    con.executescript("""
        DROP TABLE IF EXISTS device;
        CREATE TABLE device (
            device_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            meta TEXT NOT NULL CHECK (json_valid(meta))
        ) STRICT;
    """)
    rows = [
        ("cnc-01", '{"vendor":"Siemens","firmware":"4.2","calibrated":"2026-01-10"}'),
        ("cnc-02", '{"vendor":"Fanuc","firmware":"3.9"}'),
        ("molder-07", '{"vendor":"Arburg","firmware":"8.1","nozzle_mm":2.5}'),
    ]
    for i in range(4, 1001):
        rows.append((f"device-{i:04d}", json.dumps({
            "vendor": ("Siemens", "Fanuc", "Arburg")[i % 3],
            "firmware": f"{i % 5}.{i % 10}",
        })))
    con.executemany("INSERT INTO device(name, meta) VALUES (?, ?)", rows)
    count = con.execute("SELECT COUNT(*) FROM device").fetchone()[0]
    assert count == 1000
    print(f"device rows: {count}")
    print("json_extract vendors (first five):", con.execute(
        "SELECT name, json_extract(meta, '$.vendor') FROM device ORDER BY device_id LIMIT 5"
    ).fetchall())
    print("->> firmware (first three):", con.execute(
        "SELECT name, meta ->> '$.firmware' FROM device ORDER BY device_id LIMIT 3"
    ).fetchall())
    print("json_each for cnc-01:", con.execute(
        "SELECT j.key, j.value FROM device AS d, json_each(d.meta) AS j "
        "WHERE d.name = 'cnc-01' ORDER BY j.key"
    ).fetchall())

    try:
        con.execute("INSERT INTO device(name, meta) VALUES (?, ?)",
                    ("bad-json", "{vendor: Siemens"))
    except sqlite3.IntegrityError:
        print("invalid JSON: REJECTED by CHECK (json_valid(meta))")
    else:
        raise AssertionError("Broken JSON was accepted")

    con.execute("INSERT INTO device(name, meta) VALUES (?, ?)", (
        "cnc-04", '{"vendor":"Siemens","firmware":"4.3","spindle_rpm_max":12000}'
    ))
    assert con.execute("SELECT json_extract(meta, '$.spindle_rpm_max') FROM device "
                       "WHERE name = 'cnc-04'").fetchone()[0] == 12000
    print("new JSON field: cnc-04 spindle_rpm_max=12000; older rows return NULL")

    indexed = "json_extract(meta, '$.vendor') = 'Fanuc'"
    shorthand = "meta ->> 'vendor' = 'Fanuc'"
    con.execute("CREATE INDEX ix_device_vendor ON device(json_extract(meta, '$.vendor'))")
    for label, predicate in [("indexed json_extract", indexed),
                             ("different ->> expression", shorthand)]:
        plan = con.execute(f"EXPLAIN QUERY PLAN SELECT name FROM device WHERE {predicate}").fetchall()
        matched = con.execute(f"SELECT COUNT(*) FROM device WHERE {predicate}").fetchone()[0]
        description = " | ".join(row[3] for row in plan)
        print(f"{label}: count={matched}; plan={description}")
        assert matched > 0
        if label.startswith("indexed"):
            assert "USING INDEX ix_device_vendor" in description
        else:
            assert "SCAN device" in description
    print("PASS: JSON validation, new field and contrasting query plans")
