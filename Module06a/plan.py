"""Round 4: show measured DuckDB operators and SQLite's access prediction."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
PARQUET = HERE / 'report_history.parquet'
HISTORY = HERE / 'history.db'


def main():
    if not PARQUET.exists() or not HISTORY.exists():
        raise SystemExit('Run prepare.py and to_parquet.py first.')
    path = "'" + PARQUET.as_posix().replace("'", "''") + "'"
    sql = '''SELECT machine_id, site, technician, SUM(part_price) AS cost
             FROM read_parquet(''' + path + ''') GROUP BY machine_id, site, technician'''
    with duckdb.connect() as dk:
        details = dk.execute('EXPLAIN ANALYZE ' + sql).fetchall()[0][1]
    print('Round 4 | DuckDB measured EXPLAIN ANALYZE:')
    print(details)
    with sqlite3.connect(HISTORY) as sq:
        print('Round 4 | SQLite predictive EXPLAIN QUERY PLAN:')
        for row in sq.execute('''EXPLAIN QUERY PLAN
            SELECT machine_id, site, technician, SUM(part_price)
            FROM report_history GROUP BY machine_id, site, technician'''):
            print(row[3])
    print('Round 4 | interpretation: look for READ_PARQUET/TABLE_SCAN of 2,000,000 rows,')
    print('Round 4 | only four projected columns and the grouping operator above the scan.')


if __name__ == '__main__':
    main()
