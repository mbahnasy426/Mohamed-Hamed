"""Demonstrate a vulnerable query and the safe bound-parameter alternative.

Run only against the generated classroom database; no external data is used.
"""
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("warehouse.db")


def vulnerable(conn: sqlite3.Connection, name: str):
    # Deliberately unsafe EXAMPLE. Never copy into real applications.
    query = f"SELECT customer_id, name FROM customer WHERE name = '{name}'"
    return conn.execute(query).fetchall()


def safe(conn: sqlite3.Connection, name: str):
    return conn.execute(
        "SELECT customer_id, name FROM customer WHERE name = ?", (name,)
    ).fetchall()


def demonstrate() -> str:
    if not DATABASE.exists():
        raise SystemExit("Missing warehouse.db. Run: uv run python Module03/run_module3.py")
    with sqlite3.connect(DATABASE) as conn:
        payload = "' OR '1'='1"
        normal = vulnerable(conn, "Customer 1")
        attack = vulnerable(conn, payload)
        protected = safe(conn, payload)
        assert len(normal) == 1
        assert len(attack) == 2000, len(attack)
        assert protected == []

        details = [
            "SQL injection demonstration (classroom dataset)",
            f"Normal name lookup: {normal}",
            f"Unsafe payload: {payload!r}",
            f"Vulnerable query rows: {len(attack)} (first 3: {attack[:3]})",
            f"Bound-parameter rows: {len(protected)}",
        ]
        try:
            vulnerable(conn, "O'Brien")
            details.append("Unsafe apostrophe: unexpectedly accepted")
        except sqlite3.Error as exc:
            details.append(f"Unsafe apostrophe: SQL error: {exc}")
        apostrophe_rows = safe(conn, "O'Brien")
        details.append(f"Safe apostrophe rows: {apostrophe_rows}")
        details.append("PASS: bound parameters treat user input as data, not SQL")
        return "\n".join(details)


if __name__ == "__main__":
    print(demonstrate())
