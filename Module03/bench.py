"""Repeatable index benchmark for the Module 3 warehouse dataset.

Use one SQLite connection, warm queries before timing, and compare median times.
The execution plans are the main evidence; timings depend on the computer.
"""
import sqlite3
import statistics
import time

DASHBOARD = """
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers,
       SUM(ol.qty * p.price) AS revenue
FROM customer AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN order_line AS ol ON ol.order_id = o.order_id
JOIN product AS p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-01-01' AND o.ordered_on < '2026-01-01'
GROUP BY c.city ORDER BY revenue DESC
"""
DAY = """
SELECT o.order_id, o.ordered_on, c.name
FROM orders AS o JOIN customer AS c ON c.customer_id = o.customer_id
WHERE o.ordered_on = '2026-02-14'
"""


def plan(conn: sqlite3.Connection, query: str) -> list[str]:
    return [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + query)]


def measure(conn: sqlite3.Connection, query: str, repeats: int = 3,
            batch: int = 1) -> tuple[float, list[float]]:
    conn.execute(query).fetchall()  # warm-up; measured samples use same connection
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        for __ in range(batch):
            conn.execute(query).fetchall()
        samples.append((time.perf_counter() - start) * 1000 / batch)
    return statistics.median(samples), samples


def run_benchmark(conn: sqlite3.Connection, say) -> None:
    for name in ("ix_orders_ordered_on", "ix_orderline_order", "ix_orderline_product"):
        conn.execute("DROP INDEX IF EXISTS " + name)
    reference = conn.execute(DASHBOARD).fetchall()
    steps = [
        ("No added index", None),
        ("+ ix_orders_ordered_on", "CREATE INDEX ix_orders_ordered_on ON orders(ordered_on)"),
        ("+ ix_orderline_order", "CREATE INDEX ix_orderline_order ON order_line(order_id)"),
        ("+ ix_orderline_product", "CREATE INDEX ix_orderline_product ON order_line(product_id)"),
    ]
    summary = []
    for label, sql in steps:
        if sql:
            conn.execute(sql)
        result = conn.execute(DASHBOARD).fetchall()
        assert result == reference, "Index changed the result unexpectedly"
        dashboard_ms, samples = measure(conn, DASHBOARD, repeats=3)
        day_ms, _ = measure(conn, DAY, repeats=3, batch=200)
        summary.append((label, dashboard_ms, day_ms))
        say(f"Step: {label}")
        say(f"  Dashboard median: {dashboard_ms:.3f} ms; 3 runs: {[round(s, 3) for s in samples]}")
        say(f"  Single-day median: {day_ms:.3f} ms (3 batches of 200)")
        say("  Dashboard plan: " + " | ".join(plan(conn, DASHBOARD)))
        say("  Single-day plan: " + " | ".join(plan(conn, DAY)))
        say("")

    say("Index benchmark summary (ms; median of 3)")
    say("Step                         Dashboard    Single day")
    for label, dashboard_ms, day_ms in summary:
        say(f"{label:28} {dashboard_ms:10.3f} {day_ms:13.3f}")

    function_day = DAY.replace(
        "o.ordered_on = '2026-02-14'",
        "date(o.ordered_on) = '2026-02-14'"
    )
    product_lookup = "SELECT COUNT(*) FROM order_line WHERE product_id = 42"
    say("Negative test (date() wraps column): " + " | ".join(plan(conn, function_day)))
    say("Product index used for selective filter: " +
        " | ".join(plan(conn, product_lookup)))
    assert any("ix_orders_ordered_on" in line for line in plan(conn, DAY))
    assert not any("ix_orders_ordered_on" in line for line in plan(conn, function_day))
    assert any("ix_orderline_product" in line for line in plan(conn, product_lookup))
    say("PASS: index use / non-use assertions verified")
