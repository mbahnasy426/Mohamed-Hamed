"""Run all six rounds + the homework from the portfolio repository root.

Usage:
    uv run python Module06a/run_module6a.py

Measured results are saved to Module06a/results.txt and metrics.json.
The 6–8 sentence memo is regenerated from real values only after success.
"""
from __future__ import annotations
import json
import platform
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'results.txt'
METRICS = HERE / 'metrics.json'
M5 = ROOT / 'Module05' / 'normalize.db'
log = []


def say(msg=''):
    print(msg, flush=True)
    log.append(str(msg))


def run(script, args=()):
    cmd = [sys.executable, str(HERE / script), *args]
    say(f'\n$ python Module06a/{script} ' + ' '.join(args))
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.stdout.strip():
        say(result.stdout.rstrip())
    if result.stderr.strip():
        say(result.stderr.rstrip())
    say(f'exit status: {result.returncode}')
    if result.returncode:
        OUT.write_text('\n'.join(log) + '\n', encoding='utf-8')
        raise SystemExit(f'{script} failed — see Module06a/results.txt')
    return result


def make_memo():
    m = json.loads(METRICS.read_text(encoding='utf-8'))
    race, boundary, c = m['race'], m['boundary'], m['compression']
    d, a = race['dashboard'], race['monthly']
    text = f'''# Module 06a — Decision memo to Lea Winter and Yasmin Kaya

**Subject: Move the historical month-end report to Parquet + DuckDB**

Lea and Yasmin, I recommend keeping the live job-entry and single-row operational transactions in SQLite while storing an analytical copy of `report_history` in Parquet for DuckDB to scan.  The SQLite dashboard query had a measured five-run median of **{d['sqlite_ms']:.3f} ms**, compared with **{d['duckdb_ms']:.3f} ms** in DuckDB ({d['sqlite_over_duckdb']:.2f}× SQLite/DuckDB).  The monthly report had medians of **{a['sqlite_ms']:.3f} ms** and **{a['duckdb_ms']:.3f} ms**, respectively ({a['sqlite_over_duckdb']:.2f}×); both engines returned the same groups and amounts after correcting their different `strftime` argument order.  The analytical Snappy file occupies **{c['snappy_bytes']/1e6:.2f} MB**, while zstd uses **{c['zstd_bytes']/1e6:.2f} MB**, and both contain 2,000,000 rows with the same price totals.  I would refresh the copy at the end of each shift (or nightly after ingest is complete) using `refresh.py --check`, publish the new file only after a count/total check, and monitor the last successful refresh timestamp.  A stale copy means a newly completed job can be missing from management's totals even when the query returns quickly, so failed refreshes need an alert and the report should clearly display an as-of time.  I would **not** move the live single-row insert/lookup workload: our 1,000-statement measurements were SQLite **{boundary['sqlite_insert_ms']:.3f}/{boundary['sqlite_lookup_ms']:.3f} ms** versus DuckDB **{boundary['duckdb_insert_ms']:.3f}/{boundary['duckdb_lookup_ms']:.3f} ms** (inserts/lookups).  This is a reproducible local test, not proof of the production 40-minute workload; these timings and decisions should be revalidated on Kortmann's actual hardware and datasets.

**Caveat:** matching row count and sum detects many incomplete copies, but does not prove row-by-row equality. Two different datasets can share those two checksums; a key-level audit or stronger integrity check is needed for a high-stakes financial report.

Evidence: [results.txt](results.txt), [metrics.json](metrics.json), [duckdb-notes.md](duckdb-notes.md).
'''
    (HERE / 'memo.md').write_text(text, encoding='utf-8')
    say('\nRound 6 | memo written: Module06a/memo.md (from measured values)')


def main():
    say('Module 6a — original instructor six rounds and homework')
    say(f'Environment: {platform.platform()} | Python {sys.version.split()[0]} | SQLite {sqlite3.sqlite_version}')
    say(f'Run UTC: {datetime.now(timezone.utc).isoformat(timespec="seconds")}')
    try:
        import duckdb
        say(f'DuckDB {duckdb.__version__}')
    except ImportError:
        raise SystemExit('DuckDB not installed. From repo root run: uv sync (or: python -m pip install duckdb)')
    if not M5.exists():
        script = ROOT / 'Module05' / 'run_module5.py'
        if not script.is_file():
            raise SystemExit('Need Module05/run_module5.py from your original portfolio')
        say('Module05/normalize.db missing; rebuilding with original Module 05 script...')
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
        say(result.stdout[-1000:] if result.stdout else result.stderr[-1000:])
        if result.returncode or not M5.exists():
            raise SystemExit('Could not regenerate Module05/normalize.db')

    # Remove previous metrics, so a failed partial run cannot appear complete.
    METRICS.unlink(missing_ok=True)
    run('prepare.py')                 # 1 Build
    run('to_parquet.py')              # 2 Convert
    run('race.py')                    # 3 Race
    run('plan.py')                    # 4 Plan
    run('boundary.py')                # 5 Boundary
    run('compress.py')                # Core homework
    run('refresh.py', ('--check',))    # Intense homework pass one
    run('refresh.py', ('--check',))    # Intense homework pass two
    make_memo()                       # 6 Decide
    say('\nAll six rounds and both homework tracks completed by this script.')
    say('Pod discussion / in-class demonstration: not claimed as completed.')
    OUT.write_text('\n'.join(log) + '\n', encoding='utf-8')
    say('Evidence saved: Module06a/results.txt and Module06a/metrics.json')


if __name__ == '__main__':
    main()
