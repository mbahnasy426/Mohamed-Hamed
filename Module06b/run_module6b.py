"""Run Module 6b's reproducible local evidence, saving results.txt on success.

Run from repository root: uv run python Module06b/run_module6b.py
The shared PostgreSQL Task 1 still requires classroom access.
"""
import platform
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
lines = [
    "Module 06b — locally reproduced evidence (not the user's own computer)",
    f"Python {sys.version.split()[0]} | SQLite {sqlite3.sqlite_version} | OS {platform.platform()}",
    "Engine timings depend on OS, storage, caching and Python/shelve backend.",
]
for filename in ("json_bench.py", "local_boundary.py", "kv_compare.py"):
    command = [sys.executable, str(HERE / filename)]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    lines += ["", f"$ python Module06b/{filename}", run.stdout.rstrip()]
    if run.returncode:
        if run.stderr:
            lines.append(run.stderr.rstrip())
        raise RuntimeError(f"{filename} failed; results.txt not overwritten")

output = "\n".join(lines) + "\n"
(HERE / "results.txt").write_text(output, encoding="utf-8")
print(output, end="")
print("Saved Module06b/results.txt")
