"""Round 1: expand the Module 05 report into 10 quarters (2 million rows)."""
from __future__ import annotations
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'Module05' / 'normalize.db'
HISTORY = HERE / 'history.db'
CSV = HERE / 'report_jobpart.csv'
QUARTERS = 10
EXPECTED_SOURCE_ROWS = 200_000
COLUMNS = ('job_id', 'machine_id', 'site', 'technician', 'part_no', 'part_price', 'done_on')


def main():
    if not SOURCE.is_file():
        raise SystemExit('Missing Module05/normalize.db; first run: uv run python Module05/run_module5.py')
    with sqlite3.connect(SOURCE) as source:
        try:
            count = source.execute('SELECT COUNT(*) FROM report_jobpart').fetchone()[0]
        except sqlite3.OperationalError as exc:
            raise SystemExit(f'Module 05 is incomplete: {exc}') from exc
        if count != EXPECTED_SOURCE_ROWS:
            raise SystemExit(f'Module 05 needs {EXPECTED_SOURCE_ROWS:,} rows; found {count:,}')
        with CSV.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            writer.writerows(source.execute('SELECT ' + ', '.join(COLUMNS) + ' FROM report_jobpart'))

    # Deliberate rebuild, never changes the original Module05 database.
    HISTORY.unlink(missing_ok=True)
    with sqlite3.connect(HISTORY) as db:
        db.execute('ATTACH DATABASE ? AS m5', (str(SOURCE),))
        db.execute('''CREATE TABLE report_history (
            job_id INTEGER, machine_id TEXT, site TEXT, technician TEXT,
            part_no TEXT, part_price REAL, done_on TEXT)''')
        db.execute('''WITH RECURSIVE quarters(k) AS (
            SELECT 0 UNION ALL SELECT k + 1 FROM quarters WHERE k < ?
        )
        INSERT INTO report_history
        SELECT r.job_id + k * 1000000, r.machine_id, r.site, r.technician,
               r.part_no, r.part_price,
               date(r.done_on, '+' || (k * 91) || ' days')
        FROM m5.report_jobpart AS r CROSS JOIN quarters''', (QUARTERS - 1,))
        db.commit()
        rows, checksum = db.execute('SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM report_history').fetchone()
        assert rows == count * QUARTERS, (rows, count)
    print(f'Round 1 | source rows: {count:,}')
    print(f'Round 1 | history rows: {rows:,} | expected: 2,000,000')
    print(f'Round 1 | history checksum SUM(part_price): {checksum}')
    print(f'Round 1 | history.db bytes: {HISTORY.stat().st_size:,}')
    print(f'Round 1 | source CSV bytes: {CSV.stat().st_size:,}')


if __name__ == '__main__':
    main()
