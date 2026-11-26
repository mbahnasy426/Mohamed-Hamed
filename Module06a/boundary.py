"""Round 5: measure OLTP-style single-row inserts and primary-key lookups."""
from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
METRICS = HERE / 'metrics.json'
N = 1000
ROWS = [(i, f'k{i}', i * 1.5) for i in range(N)]


def ms(fn):
    start = time.perf_counter()
    fn()
    return round((time.perf_counter() - start) * 1000, 3)


def measure_sqlite():
    con = sqlite3.connect(':memory:')
    con.execute('CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v REAL)')
    # Real single-row statements, not an executemany call disguised as a loop.
    def insert():
        for row in ROWS:
            con.execute('INSERT INTO s VALUES (?, ?, ?)', row)
        con.commit()
    ins = ms(insert)
    def lookup():
        for i in range(N):
            assert con.execute('SELECT v FROM s WHERE id = ?', (i,)).fetchone() == (i*1.5,)
    look = ms(lookup)
    con.close()
    return ins, look


def measure_duckdb():
    con = duckdb.connect()
    con.execute('CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v DOUBLE)')
    def insert():
        for row in ROWS:
            con.execute('INSERT INTO s VALUES (?, ?, ?)', row)
    ins = ms(insert)
    def lookup():
        for i in range(N):
            assert con.execute('SELECT v FROM s WHERE id = ?', (i,)).fetchone() == (i*1.5,)
    look = ms(lookup)
    con.execute('CREATE TABLE batch(id INTEGER PRIMARY KEY, k TEXT, v DOUBLE)')
    batch = ms(lambda: con.executemany('INSERT INTO batch VALUES (?, ?, ?)', ROWS))
    assert con.execute('SELECT COUNT(*) FROM batch').fetchone()[0] == N
    con.close()
    return ins, look, batch


def main():
    si, sl = measure_sqlite()
    di, dl, batch = measure_duckdb()
    results = {'n': N, 'sqlite_insert_ms': si, 'sqlite_lookup_ms': sl,
               'duckdb_insert_ms': di, 'duckdb_lookup_ms': dl,
               'duckdb_executemany_insert_ms': batch}
    print(f'Round 5 | {N:,} inserts: SQLite {si} ms | DuckDB {di} ms')
    print(f'Round 5 | {N:,} primary-key lookups: SQLite {sl} ms | DuckDB {dl} ms')
    print(f'Round 5 | {N:,} DuckDB inserts via executemany: {batch} ms')
    old = json.loads(METRICS.read_text(encoding='utf-8')) if METRICS.exists() else {}
    old['boundary'] = results
    METRICS.write_text(json.dumps(old, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
