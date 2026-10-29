# Module 01 — Introduction and Local-First Foundations

## Learning goals

By the end of this module, I should be able to:

1. Explain the CBL/PBL approach, portfolio assessment, and evolving course requirements.
2. Set up a personal GitHub portfolio with an appropriate `.gitignore`.
3. Reproduce the course Python environment with `uv`, SQLite, DuckDB, and Datasette.
4. Measure and explain how an embedded database differs from a client/server database.
5. Load real telemetry rows into SQLite and use bound parameters in Python.
6. Run and verify an AI-generated SQL query rather than trusting it immediately.

My goal is to understand the basics of databases and practise using them through small exercises.

## Course and portfolio links

- [Module 01 instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/01-introduction-and-local-first.md)
- [Course syllabus](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/syllabus.md)
- [My portfolio home](../README.md)
- [SQL Island notes](sql-island.md)
- [AI query verification](task-07-ai-verification.md)

## Task Pod

Our Task Pod has three members:

- Adam Salman — [Portfolio](https://github.com/adamhsalman-droid/Adam.Salman-Portfolio)
- Mohamed Alsayed — [Portfolio](https://github.com/mbahnasy426/Mohamed-Hamed)
- Mohamed Nassar — [Portfolio](https://github.com/nassarrrrr/M.Nassar-HSBI-Database-Portofolio)

## Contributions

- **Mohamed Nassar (Tasks 1–4):** Set up the GitHub portfolio, configured the Python environment, and completed the SQLite shell exercises.
- **Mohamed Alsayed (Task 5):** Completed the SQL Island exercises, practiced SQL commands, and documented the learning experience.
- **Adam Salman (Tasks 6–7):** Generated and analyzed telemetry data using Python and SQLite, and verified AI-generated SQL queries.

**Teamwork:** All three members discussed the assignments, reviewed the results, and supported each other throughout the project.


## Evidence status (updated October 2026)

- [x] **Portfolio / Task Pod:** own repository, links to podmates, descriptions of contributions.
- [x] **Python environment:** saved `uv-check-output.txt`, `pyproject.toml`, `uv.lock` and `uv-check.py`.
- [x] **SQLite shell / SQL Island:** saved shell tour, SQL samples and SQL Island screenshot. [SQL Island notes](sql-island.md).
- [x] **Telemetry:** reproducible generator, loader, query script, and saved results (172,800 readings).
- [x] **AI verification:** recorded query, actual plan, and documented limitation of the AI's interpretation of *overnight*. [Verification note](task-07-ai-verification.md).
- [x] **Reflection:** [completed logbook](../Reflections/ref01.md).
- [x] **Bound parameters:** `load_telemetry.py` uses `executemany` with placeholders; [parameter-demo.py](parameter-demo.py) illustrates a parameterized `SELECT`.
- [ ] **Live peer gate:** make and show a new commit from your own laptop; independently test the Markdown links.
- [ ] **Instructor access:** confirm collaborator permissions in GitHub Settings.
- [ ] **Embedded vs server:** SQLite measurements are saved, but an equivalent client/server measurement has not been run. [Comparison and honest evidence status](local-first-comparison.md).

This is evidence of work saved in the portfolio, not a claim that each step was independently rerun in this review.

## Reproducing Tasks 3, 6 and 7

From the **root of this repository** (after installing `uv`):

```sh
uv python install 3.14
uv init --name databases-portfolio
uv add duckdb datasette sqlite-utils pydantic sqlalchemy
uv run uv-check.py
uv run python module-01/generate_telemetry.py
uv run python module-01/load_telemetry.py
uv run python module-01/query_telemetry.py
```

Use `uv init` only if a `pyproject.toml` does not already exist. The `.db`, CSV, virtual environment, and secrets stay out of the repository. Commit the generated lockfile and save **genuine** output after running the commands.

Task 4 uses the real `sqlite3` terminal. The included `tour.sql` is an illustrative starting script, not evidence that a shell session has taken place.
