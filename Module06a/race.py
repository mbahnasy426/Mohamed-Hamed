"""Round 3: fair interleaved SQLite vs DuckDB benchmarks and answer checks."""
from __future__ import annotations
import json
import sqlite3
import statistics
import time
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
HISTORY = HERE / 'history.db'
PARQUET = HERE / 'report_history.parquet'
METRICS = HERE / 'metrics.json'
RUNS = 5  # Odd run count; first warm-up is intentionally not measured.

DASHBOARD = '''SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM {src} WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician'''
# IMPORTANT: arguments are reversed between SQLite and DuckDB!
MONTHLY_SQLITE = '''SELECT strftime('%Y-%m', done_on) AS month, machine_id,
       COUNT(*) AS jobs, SUM(part_price) AS cost
FROM report_history GROUP BY month, machine_id ORDER BY month, machine_id'''
MONTHLY_DUCK = '''SELECT strftime(done_on, '%Y-%m') AS month, machine_id,
       COUNT(*) AS jobs, SUM(part_price) AS cost
FROM {src} GROUP BY month, machine_id ORDER BY month, machine_id'''


def sql_path(p: Path) -> str:
    return "'" + p.as_posix().replace("'", "''") + "'"


def canonical(rows):
    """Compare values and groups rather than exact binary floating point."""
    return sorted(tuple(round(v, 2) if isinstance(v, float) else v for v in row) for row in rows)


def median_race(sqlite_fn, duck_fn):
    sqlite_fn(); duck_fn()  # Untimed warm-ups.
    st, dt = [], []
    for i in range(RUNS):
        # Reverse order on alternating rounds to reduce first-engine advantage.
        if i % 2:
            t = time.perf_counter(); duck_fn(); dt.append((time.perf_counter() - t) * 1000)
            t = time.perf_counter(); sqlite_fn(); st.append((time.perf_counter() - t) * 1000)
        else:
            t = time.perf_counter(); sqlite_fn(); st.append((time.perf_counter() - t) * 1000)
            t = time.perf_counter(); duck_fn(); dt.append((time.perf_counter() - t) * 1000)
    s, d = statistics.median(st), statistics.median(dt)
    return {'sqlite_ms': round(s, 3), 'duckdb_ms': round(d, 3),
            'sqlite_range_ms': [round(min(st), 3), round(max(st), 3)],
            'duckdb_range_ms': [round(min(dt), 3), round(max(dt), 3)],
            'sqlite_over_duckdb': round(s/d, 3) if d else None, 'runs': RUNS}


def main():
    if not HISTORY.exists() or not PARQUET.exists():
        raise SystemExit('Run prepare.py and to_parquet.py first.')
    sq = sqlite3.connect(HISTORY)
    dk = duckdb.connect()
    src = f'read_parquet({sql_path(PARQUET)})'
    pairs = {
        'dashboard': (DASHBOARD.format(src='report_history'), DASHBOARD.format(src=src)),
        'monthly': (MONTHLY_SQLITE, MONTHLY_DUCK.format(src=src))
    }
    measured = {}
    for name, (sql_sqlite, sql_duck) in pairs.items():
        sq_fn = lambda query=sql_sqlite: sq.execute(query).fetchall()
        dk_fn = lambda query=sql_duck: dk.execute(query).fetchall()
        a, b = sq_fn(), dk_fn()
        if canonical(a) != canonical(b):
            raise SystemExit(f'{name}: SQLite and DuckDB answers DO NOT MATCH; no timing accepted')
        m = median_race(sq_fn, dk_fn)
        measured[name] = m
        print(f'Round 3 | {name}: {len(a)} verified result groups')
        print(f'Round 3 | {name}: SQLite {m["sqlite_ms"]:.3f} ms {m["sqlite_range_ms"]} '
              f'| DuckDB {m["duckdb_ms"]:.3f} ms {m["duckdb_range_ms"]} '
              f'| speedup {m["sqlite_over_duckdb"]}x')

    # Point query: SQLite's index can make it competitive or faster.
    sql_sqlite = "SELECT COUNT(*), SUM(part_price) FROM report_history WHERE done_on = '2026-02-14'"
    sql_duck = f"SELECT COUNT(*), SUM(part_price) FROM {src} WHERE done_on = DATE '2026-02-14'"
    sq.execute('CREATE INDEX IF NOT EXISTS idx_history_done_on ON report_history(done_on)')
    try:
        qa = sq.execute(sql_sqlite).fetchall()
        qb = dk.execute(sql_duck).fetchall()
        if canonical(qa) != canonical(qb):
            raise SystemExit('Point-query answers are not identical')
        measured['indexed_day'] = median_race(lambda: sq.execute(sql_sqlite).fetchall(),
                                              lambda: dk.execute(sql_duck).fetchall())
        print('Round 3 | SQLite point-lookup plan:',
              '; '.join(r[3] for r in sq.execute('EXPLAIN QUERY PLAN ' + sql_sqlite)))
        print('Round 3 | indexed one-day SQLite vs DuckDB:', measured['indexed_day'])
    finally:
        sq.execute('DROP INDEX IF EXISTS idx_history_done_on')
        sq.commit()
        sq.close()
        dk.close()
    # Preserve independently recorded results from other rounds.
    previous = json.loads(METRICS.read_text(encoding='utf-8')) if METRICS.exists() else {}
    previous['race'] = measured
    METRICS.write_text(json.dumps(previous, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
