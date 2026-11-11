"""Module 05: reproducible rounds 1–5; retain normalize.db for Module 06a.

Run from the portfolio root: uv run python Module05/run_module5.py
Rebuild only intentionally: uv run python Module05/run_module5.py --rebuild
"""
from __future__ import annotations

import argparse
from pathlib import Path
import platform
import sqlite3
import statistics
import time

HERE = Path(__file__).resolve().parent
DB = HERE / "normalize.db"
SETUP = HERE / "setup.sql"

NORMALIZED = """
SELECT m.machine_id, m.site, j.technician, SUM(p.part_price) AS cost
FROM job j
JOIN machine m ON m.machine_id = j.machine_id
JOIN job_part jp ON jp.job_id = j.job_id
JOIN part p ON p.part_no = jp.part_no
WHERE j.done_on >= date('2026-03-01')
GROUP BY m.machine_id, j.technician
"""
REPORT = """
SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_jobpart
WHERE done_on >= date('2026-03-01')
GROUP BY machine_id, technician
"""


def timed_ms(con: sqlite3.Connection, sql: str) -> float:
    start = time.perf_counter()
    con.execute(sql).fetchall()
    return (time.perf_counter() - start) * 1000


def median_race(con: sqlite3.Connection, a: str, b: str, n: int = 5) -> tuple[float, float]:
    # Untimed warm-ups, then alternate A/B so cache order is less biased.
    con.execute(a).fetchall()
    con.execute(b).fetchall()
    aa, bb = [], []
    for i in range(n):
        if i % 2:
            bb.append(timed_ms(con, b))
            aa.append(timed_ms(con, a))
        else:
            aa.append(timed_ms(con, a))
            bb.append(timed_ms(con, b))
    return statistics.median(aa), statistics.median(bb)


def anomalies() -> list[str]:
    con = sqlite3.connect(":memory:")
    con.executescript("""
    CREATE TABLE flat5(job_id INTEGER, machine_id TEXT, site TEXT,
                       technician TEXT, part_no TEXT, part_price REAL);
    INSERT INTO flat5 VALUES
      (1,'cnc-01','Gütersloh','tech-0','P-0001',6.00),
      (1,'cnc-01','Gütersloh','tech-0','P-0002',7.00),
      (2,'cnc-02','Gütersloh','tech-1','P-0001',6.00),
      (2,'cnc-02','Gütersloh','tech-1','P-0003',8.50),
      (3,'cnc-01','Gütersloh','tech-0','P-0003',8.50);
    """)
    con.execute("UPDATE flat5 SET site='Bielefeld' WHERE machine_id='cnc-01' AND part_no='P-0001'")
    inconsistent = con.execute("SELECT DISTINCT site FROM flat5 WHERE machine_id='cnc-01'").fetchall()
    # An unused part cannot be represented without a fake job or NULL job fields.
    con.execute("INSERT INTO flat5 VALUES (NULL,NULL,NULL,NULL,'P-0999',99.00)")
    fake = con.execute("SELECT job_id FROM flat5 WHERE part_no='P-0999'").fetchone()[0] is None
    # Remove the only job holding P-0002; its price disappears too.
    con.execute("DELETE FROM flat5 WHERE part_no='P-0002'")
    lost = con.execute("SELECT COUNT(*) FROM flat5 WHERE part_no='P-0002'").fetchone()[0] == 0
    con.close()
    assert len(inconsistent) == 2 and fake and lost
    return ["Update anomaly: one partial edit makes cnc-01 sites disagree: " + str([x[0] for x in inconsistent]),
            "Insert anomaly: P-0999 requires a fake/NULL job row in flat5",
            "Delete anomaly: deleting P-0002's last job row loses its part price"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Delete and recreate normalize.db (destructive)")
    args = parser.parse_args()
    if args.rebuild and DB.exists():
        DB.unlink()
    first_build = not DB.exists()
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys=ON")
    if first_build:
        con.executescript(SETUP.read_text(encoding="utf-8"))
        con.commit()
    required = {"flat_jobpart", "machine", "part", "job", "job_part", "report_jobpart"}
    existing = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not required <= existing:
        raise SystemExit("Existing normalize.db has an incomplete schema; back it up, then run --rebuild")
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("flat_jobpart", "machine", "part", "job", "job_part", "report_jobpart")}
    assert counts == {"flat_jobpart": 200000, "machine": 50, "part": 10,
                      "job": 20000, "job_part": 200000, "report_jobpart": 200000}, counts
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []

    def canon(rows: list[tuple]) -> list[tuple]:
        return sorted((r[0], r[1], r[2], round(r[3], 4)) for r in rows)

    assert canon(con.execute(NORMALIZED).fetchall()) == canon(con.execute(REPORT).fetchall())
    n_ms, r_ms = median_race(con, NORMALIZED, REPORT)
    nplan = [r[-1] for r in con.execute("EXPLAIN QUERY PLAN " + NORMALIZED)]
    rplan = [r[-1] for r in con.execute("EXPLAIN QUERY PLAN " + REPORT)]

    # Price a site update, without leaving the DB changed for the next module.
    touched_normalized = con.execute("SELECT COUNT(*) FROM machine WHERE machine_id='cnc-02'").fetchone()[0]
    touched_report = con.execute("SELECT COUNT(*) FROM report_jobpart WHERE machine_id='cnc-02'").fetchone()[0]
    con.execute("SAVEPOINT site_test")
    t0 = time.perf_counter()
    con.execute("UPDATE machine SET site='Bielefeld' WHERE machine_id='cnc-02'")
    upd_normalized_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    con.execute("UPDATE report_jobpart SET site='Bielefeld' WHERE machine_id='cnc-02'")
    upd_report_ms = (time.perf_counter() - t0) * 1000
    con.execute("ROLLBACK TO site_test")
    con.execute("RELEASE site_test")
    assert touched_normalized == 1 and touched_report == 4000

    storage = {}
    try:
        storage["normalized_tables"] = con.execute(
            "SELECT COALESCE(SUM(pgsize),0) FROM dbstat WHERE name IN ('job','job_part','part','machine')"
        ).fetchone()[0]
        storage["report_table"] = con.execute(
            "SELECT COALESCE(SUM(pgsize),0) FROM dbstat WHERE name='report_jobpart'"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        storage = {"normalized_tables": None, "report_table": None}

    # Test the index caution in Round 5, and restore the original schema.
    con.execute("DROP INDEX IF EXISTS ix_report_machine")
    without_index = statistics.median(timed_ms(con, REPORT) for _ in range(5))
    noindex_plan = [r[-1] for r in con.execute("EXPLAIN QUERY PLAN " + REPORT + "\n-- index_dropped") ]
    con.execute("CREATE INDEX ix_report_machine ON report_jobpart(machine_id)")
    con.commit()

    lines = ["Module 05 — measured evidence (automatically generated)",
             "Host: " + platform.platform(), "SQLite: " + sqlite3.sqlite_version,
             "Database: Module05/normalize.db (retained locally; ignored by Git)",
             "Build: " + ("created from setup.sql" if first_build else "reused existing database"),
             "", "Round 2 — anomalies", *anomalies(),
             "", "Round 3 — row counts", *[f"{key}: {val:,}" for key, val in counts.items()],
             "Foreign key check: passed", "Normalized/report aggregate results: identical",
             "", "Round 4 — alternating warm-cache medians (5 runs each)",
             f"Normalized four-table join: {n_ms:.3f} ms",
             f"Denormalized report table: {r_ms:.3f} ms",
             f"Ratio normalized/report: {n_ms/r_ms:.2f}x (above 1 means report is faster)",
             "Normalized EXPLAIN QUERY PLAN:", *["  " + x for x in nplan],
             "Report EXPLAIN QUERY PLAN:", *["  " + x for x in rplan],
             "", "Round 5 — site change cnc-02 (changes rolled back)",
             f"Normalized rows touched: {touched_normalized} ({upd_normalized_ms:.3f} ms)",
             f"Report rows touched: {touched_report:,} ({upd_report_ms:.3f} ms)",
             f"3NF base tables storage: {storage['normalized_tables']} bytes",
             f"Report base table storage: {storage['report_table']} bytes",
             f"Report query without ix_report_machine: {without_index:.3f} ms (5-run median)",
             "Report plan without index:", *["  " + x for x in noindex_plan],
             "", "Note: DB indexes, other objects, and free pages are excluded from table-only dbstat figures.",
             "Note: timings are specific to this host; rerun on your machine.",
             "Round 6 memo: Module05/memo.md",
             "Round 7 curiosity notes: Module05/normalization-notes.md",
             "No real pod gate/Discord discussion is claimed."]
    text = "\n".join(lines) + "\n"
    (HERE / "results.txt").write_text(text, encoding="utf-8")
    print(text)
    con.close()


if __name__ == "__main__":
    main()
