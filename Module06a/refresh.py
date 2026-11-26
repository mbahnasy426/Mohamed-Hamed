"""Homework (intense): idempotent Parquet refresh from SQLite, with --check."""
from __future__ import annotations
import argparse
import csv
import os
import sqlite3
import time
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
HISTORY = HERE / 'history.db'
PARQUET = HERE / 'report_history.parquet'
TMP_CSV = HERE / '_refresh_source.csv'
TMP_PARQUET = HERE / '_refresh_new.parquet'
FIELDS = ('job_id', 'machine_id', 'site', 'technician', 'part_no', 'part_price', 'done_on')


def sql_path(p: Path):
    return "'" + p.as_posix().replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='Compare source and copy before replacing the old file')
    args = ap.parse_args()
    if not HISTORY.is_file():
        raise SystemExit('Missing history.db: run prepare.py')
    start = time.perf_counter()
    con = sqlite3.connect(HISTORY)
    try:
        src_rows, src_sum = con.execute(
            'SELECT COUNT(*), ROUND(SUM(part_price),2) FROM report_history').fetchone()
        with TMP_CSV.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
            writer.writerows(con.execute('SELECT ' + ','.join(FIELDS) + ' FROM report_history'))
        # Write new copy separately. Do not risk corrupting a previous good report.
        TMP_PARQUET.unlink(missing_ok=True)
        with duckdb.connect() as dk:
            dk.execute(f'''
                COPY (SELECT CAST(job_id AS BIGINT) AS job_id,
                             machine_id, site, technician, part_no,
                             CAST(part_price AS DOUBLE) AS part_price,
                             CAST(done_on AS DATE) AS done_on
                      FROM read_csv_auto({sql_path(TMP_CSV)}, header=true))
                TO {sql_path(TMP_PARQUET)} (FORMAT PARQUET, COMPRESSION SNAPPY)
            ''')
            copy_rows, copy_sum = dk.execute(f'''
                SELECT COUNT(*), ROUND(SUM(part_price),2)
                FROM read_parquet({sql_path(TMP_PARQUET)})''').fetchone()
        if args.check:
            print(f'check | SQLite rows={src_rows}, sum={src_sum} | Parquet rows={copy_rows}, sum={copy_sum}')
            if (src_rows, src_sum) != (copy_rows, copy_sum):
                raise SystemExit('CHECK FAILED: retained previous Parquet file; exit status 1')
            print('check | OK')
        # A safe refresh should never publish an obviously incomplete export.
        if (src_rows, src_sum) != (copy_rows, copy_sum):
            raise SystemExit('Mismatch: old Parquet retained')
        os.replace(TMP_PARQUET, PARQUET)
        elapsed = (time.perf_counter() - start) * 1000
        print(f'rows={copy_rows} checksum={copy_sum} parquet_bytes={PARQUET.stat().st_size} elapsed_ms={elapsed:.1f}')
    finally:
        con.close()
        TMP_CSV.unlink(missing_ok=True)
        TMP_PARQUET.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
