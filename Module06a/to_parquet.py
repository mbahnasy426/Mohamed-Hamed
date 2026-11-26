"""Round 2: convert the original 200k CSV into a 2M-row Parquet copy."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
CSV = HERE / 'report_jobpart.csv'
PARQUET = HERE / 'report_history.parquet'
HISTORY = HERE / 'history.db'


def sql_path(p: Path) -> str:
    return "'" + p.as_posix().replace("'", "''") + "'"


def main():
    if not CSV.is_file() or not HISTORY.is_file():
        raise SystemExit('First run: uv run python Module06a/prepare.py')
    con = duckdb.connect()
    # Project rows explicitly to keep column types identical to history.db.
    con.execute(f'''
        COPY (
          SELECT CAST(r.job_id AS BIGINT) + k * 1000000 AS job_id,
                 r.machine_id, r.site, r.technician, r.part_no,
                 CAST(r.part_price AS DOUBLE) AS part_price,
                 CAST(r.done_on AS DATE) + CAST(k * 91 AS INTEGER) AS done_on
          FROM read_csv_auto({sql_path(CSV)}, header = true) AS r
          CROSS JOIN range(0, 10) AS t(k)
        ) TO {sql_path(PARQUET)} (FORMAT PARQUET, COMPRESSION SNAPPY)
    ''')
    pq_rows, pq_sum = con.execute(f'''
        SELECT COUNT(*), ROUND(SUM(part_price), 2)
        FROM read_parquet({sql_path(PARQUET)})
    ''').fetchone()
    with sqlite3.connect(HISTORY) as sq:
        sq_rows, sq_sum = sq.execute('''
            SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM report_history
        ''').fetchone()
    print(f'Round 2 | SQLite rows: {sq_rows:,} | Parquet rows: {pq_rows:,}')
    print(f'Round 2 | SQLite SUM: {sq_sum} | Parquet SUM: {pq_sum}')
    print(f'Round 2 | Parquet size bytes: {PARQUET.stat().st_size:,}')
    if (sq_rows, sq_sum) != (pq_rows, pq_sum):
        raise SystemExit('ERROR: datasets differ — do not benchmark!')
    print('Round 2 | verified: matching row counts and price totals')


if __name__ == '__main__':
    main()
