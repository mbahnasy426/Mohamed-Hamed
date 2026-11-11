"""Run all locally reproducible Module 3 tasks and save results.txt.

From the repository root: uv run python Module03/run_module3.py
The warehouse database is intentionally rebuilt on every run.
"""
import sqlite3
import sys
from pathlib import Path

from bench import DASHBOARD, plan, run_benchmark
from injection_demo import demonstrate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATABASE = HERE / "warehouse.db"
LOG = HERE / "results.txt"


def main() -> None:
    log_lines = []

    def say(message=""):
        line = str(message)
        print(line)
        log_lines.append(line)

    say("MODULE 03 - SQL VERIFICATION AND PROFILING")
    say("Python: " + sys.version.split()[0])
    say("SQLite: " + sqlite3.sqlite_version)
    say("Source: HSBI Module 03 warehouse example; measurements are local to this execution.")
    say("")

    if DATABASE.exists():
        DATABASE.unlink()
    conn = sqlite3.connect(DATABASE)
    try:
        conn.executescript((HERE / "setup.sql").read_text(encoding="utf-8"))
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("customer", "product", "orders", "order_line")
        }
        assert counts == {
            "customer": 2000, "product": 500, "orders": 60000, "order_line": 240000
        }, counts
        say("SETUP: " + str(counts))
        say("PASS: exact row counts")
        say("")

        say("TASK A - PLAN SAFARI (on a temporary copy of Module02 setup)")
        legacy = sqlite3.connect(":memory:")
        try:
            legacy.executescript((ROOT / "Module02" / "setup.sql").read_text(encoding="utf-8"))
            queries = [
                ("technician equals Beier",
                 "SELECT * FROM maint_job WHERE technician = 'Beier'"),
                ("machine equals cnc-02",
                 "SELECT * FROM machine WHERE machine_name = 'cnc-02'"),
                ("leading wildcard LIKE",
                 "SELECT * FROM maint_job WHERE technician LIKE '%ei%'"),
            ]
            say("Predictions: SCAN, SCAN, SCAN (no supporting indexes yet)")
            for label, query in queries:
                say(f"Before | {label}: " + " | ".join(plan(legacy, query)))
            legacy.execute("CREATE INDEX ix_job_tech ON maint_job(technician)")
            for label, query in queries:
                say(f"After  | {label}: " + " | ".join(plan(legacy, query)))
            for label, query in [
                ("function lower()", "SELECT * FROM maint_job WHERE lower(technician)='beier'"),
                ("prefix LIKE 'Bei%'", "SELECT * FROM maint_job WHERE technician LIKE 'Bei%'"),
            ]:
                say(f"Negative/curiosity | {label}: " + " | ".join(plan(legacy, query)))
            assert any("ix_job_tech" in p for p in plan(legacy, queries[0][1]))
            say("PASS: technician exact match uses index; original Module02 database untouched")
        finally:
            legacy.close()
        say("")

        say("TASK B - ALGEBRA")
        say("SELECT * FROM maint_job WHERE technician='Beier'")
        say("Algebra: sigma[technician='Beier'](maint_job); SELECT * means no projection needed.")
        say("")

        say("TASK 1 - AI-ASSISTED DASHBOARD QUERY")
        ai_query = (HERE / "llm_query.sql").read_text(encoding="utf-8")
        ai_query = "\n".join(line for line in ai_query.splitlines()
                             if not line.lstrip().startswith("--")).strip().rstrip(";")
        reference = conn.execute(DASHBOARD).fetchall()
        actual = conn.execute(ai_query).fetchall()
        assert actual == reference, "AI SQL differs from course reference"
        say("PASS: AI SQL matches reference rows exactly.")
        for row in actual:
            say("  " + str(row))
        say("Predicted: likely full scan of order_line, PK lookups, temp B-trees.")
        say("Actual plan: " + " | ".join(plan(conn, ai_query)))
        conn.execute("SAVEPOINT no_orders_city")
        try:
            conn.execute("INSERT INTO customer VALUES (3001, 'New customer', 'NoOrders')")
            empty_city_present = any(row[0] == "NoOrders" for row in conn.execute(ai_query))
            assert not empty_city_present
            say("Edge case VERIFIED: an inner join omits a city with no orders.")
        finally:
            conn.execute("ROLLBACK TO no_orders_city")
            conn.execute("RELEASE no_orders_city")
        say("")

        say("TASK 2 - INDEX BENCHMARK")
        run_benchmark(conn, say)
        say("")

        say("TASK 3 - SQL INJECTION")
        say(demonstrate())
        say("")

        say("TASK 4 - RELATIONAL ALGEBRA")
        say("sigma[2025<=ordered_on<2026](customer JOIN orders JOIN order_line JOIN product)")
        say("then gamma[city; COUNT(DISTINCT customer_id), SUM(qty*price)]")
        say("ORDER BY revenue DESC is a SQL sort, not a classic relational-algebra operator.")
        say("")

        say("TASK 5 - OPTIONAL STRETCH: 3 equivalent late-order reports")
        reports = (HERE / "stretcher_queries.sql").read_text(encoding="utf-8")
        # Strip SQL-only comments before splitting into the three statements.
        reports = "\n".join(line for line in reports.splitlines() if not line.strip().startswith("--"))
        statements = [q.strip() for q in reports.split(";") if q.strip()]
        statements = [s.strip() for s in statements if s.strip()]
        assert len(statements) == 3, len(statements)
        conn.execute("CREATE INDEX IF NOT EXISTS ix_orders_customer_status ON orders(customer_id, status)")
        results = [conn.execute(sql).fetchall() for sql in statements]
        assert results[0] == results[1] == results[2], "Stretcher query results differ"
        for index, sql in enumerate(statements, start=1):
            say(f"Version {index}: {len(results[index-1])} rows; plan: " +
                " | ".join(plan(conn, sql)))
        say("PASS: GROUP BY, correlated subquery, and window function agree.")
        say("")

        say("TASK C / PEER EXCHANGE: NOT VERIFIED. Do this with a neighboring pod.")
        say("The generated warehouse.db is ignored by Git; the text evidence is committed.")
    finally:
        conn.close()
        LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        print(f"Saved: {LOG}")


if __name__ == "__main__":
    main()
