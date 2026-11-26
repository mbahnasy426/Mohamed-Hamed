"""Core homework: compare Snappy and zstd Parquet storage on equal data."""
from __future__ import annotations
import json
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'report_history.parquet'
TARGET = HERE / 'report_zstd.parquet'
METRICS = HERE / 'metrics.json'


def sql_path(p):
    return "'" + p.as_posix().replace("'", "''") + "'"


def main():
    if not SOURCE.is_file():
        raise SystemExit('Run to_parquet.py first')
    with duckdb.connect() as dk:
        dk.execute(f'''COPY (SELECT * FROM read_parquet({sql_path(SOURCE)}))
                       TO {sql_path(TARGET)} (FORMAT PARQUET, COMPRESSION ZSTD)''')
        def checksum(p):
            return dk.execute(f'''SELECT COUNT(*), ROUND(SUM(part_price),2)
                                  FROM read_parquet({sql_path(p)})''').fetchone()
        a, b = checksum(SOURCE), checksum(TARGET)
    if a != b:
        raise SystemExit('Compression caused a mismatch!')
    sizes = {'snappy_bytes': SOURCE.stat().st_size, 'zstd_bytes': TARGET.stat().st_size,
             'zstd_vs_snappy_percent': round(100*TARGET.stat().st_size/SOURCE.stat().st_size, 1)}
    print(f'Homework | snappy={sizes["snappy_bytes"]:,} bytes '
          f'| zstd={sizes["zstd_bytes"]:,} bytes '
          f'| zstd is {sizes["zstd_vs_snappy_percent"]}% of snappy')
    print(f'Homework | matching rows={a[0]:,}, sum={a[1]}')
    old = json.loads(METRICS.read_text(encoding='utf-8')) if METRICS.exists() else {}
    old['compression'] = sizes
    METRICS.write_text(json.dumps(old, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
