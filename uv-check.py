"""Verify the versions in the course's uv-managed environment."""
import sys
import platform
import sqlite3
from importlib.metadata import PackageNotFoundError, version

print("uv-managed Python:", sys.executable)
print("python            ", platform.python_version())
print("sqlite (stdlib)   ", sqlite3.sqlite_version)
for package in ("duckdb", "datasette", "sqlite-utils", "pydantic", "sqlalchemy"):
    try:
        print(f"{package:18s}", version(package))
    except PackageNotFoundError:
        print(f"{package:18s}", "NOT INSTALLED")
