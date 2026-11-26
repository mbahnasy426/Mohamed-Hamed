"""Module 6b key-value homework: shelve vs SQLite, with comparable 20k keys.

Run from repository root: uv run python Module06b/kv_compare.py
Times are machine-specific and transactions differ: shelve writes one key at a time;
SQLite uses one batched transaction. Do not interpret as intrinsic engine speed.
"""
import dbm
import shelve
import sqlite3
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 20_000
for pattern in ("sessions", "sessions.*"):
    for path in HERE.glob(pattern):
        if path.is_file():
            path.unlink()

with shelve.open(str(HERE / "sessions"), flag="n") as db:
    t0 = time.perf_counter()
    for i in range(N):
        db[f"session-{i}"] = f"user-{i % 100}:filter=city:{i % 4}"
    shelve_set = time.perf_counter() - t0
    t0 = time.perf_counter()
    for i in range(N):
        assert db[f"session-{i}"] == f"user-{i % 100}:filter=city:{i % 4}"
    shelve_get = time.perf_counter() - t0
backend = dbm.whichdb(str(HERE / "sessions"))

with sqlite3.connect(HERE / "sessions.db") as con:
    con.execute("CREATE TABLE session(k TEXT PRIMARY KEY, v TEXT NOT NULL) WITHOUT ROWID")
    t0 = time.perf_counter()
    con.executemany("INSERT INTO session(k, v) VALUES (?, ?)", (
        (f"session-{i}", f"user-{i % 100}:filter=city:{i % 4}") for i in range(N)
    ))
    con.commit()
    sqlite_set = time.perf_counter() - t0
    t0 = time.perf_counter()
    for i in range(N):
        assert con.execute("SELECT v FROM session WHERE k = ?", (f"session-{i}",)).fetchone()[0] == f"user-{i % 100}:filter=city:{i % 4}"
    sqlite_get = time.perf_counter() - t0
    t0 = time.perf_counter()
    grouped = con.execute("""SELECT substr(v, instr(v, 'city:')) AS city_filter,
                                  COUNT(*) AS sessions,
                                  COUNT(DISTINCT substr(v, 1, instr(v, ':')-1)) AS users
                           FROM session GROUP BY city_filter ORDER BY city_filter""").fetchall()
    sqlite_group_ms = (time.perf_counter() - t0) * 1000

assert grouped == [(f"city:{i}", 5000, 25) for i in range(4)]
t0 = time.perf_counter()
counts = {}
with shelve.open(str(HERE / "sessions"), flag="r") as db:
    for value in db.values():
        city_filter = value.split("filter=", 1)[1]
        counts[city_filter] = counts.get(city_filter, 0) + 1
shelve_scan_ms = (time.perf_counter() - t0) * 1000
assert counts == {f"city:{i}": 5000 for i in range(4)}

print(f"sessions: {N}; shelve backend: {backend}")
print(f"shelve set={shelve_set:.3f}s get={shelve_get:.3f}s")
print(f"SQLite set={sqlite_set:.3f}s get={sqlite_get:.3f}s")
print(f"SQLite GROUP BY per city: {grouped}; {sqlite_group_ms:.1f}ms")
print(f"shelve full Python scan: {dict(sorted(counts.items()))}; {shelve_scan_ms:.1f}ms")
print("PASS: 20,000 matching keys and four groups; timings are host-specific")
