# Module 05 — Normalization vs. Denormalization

Based on the instructor's [seven-round studio](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/05-normalization-vs-denormalization.md). These are **independently reproduced exercises**, not a claim of attending the missed lesson.

## One-time setup and verification

Run from the root of `Adam.Salman-Portfolio`:

```powershell
uv sync
uv run python Module05/run_module5.py
```

On the first run the script builds **`Module05/normalize.db`** from `setup.sql`; later runs **reuse it**, so do not delete this DB before Module 06a. If you need a clean rebuild, first back up the DB and intentionally run `uv run python Module05/run_module5.py --rebuild`.

The script generates `results.txt` with *your own machine's* timing, checks table counts and foreign keys, compares two equivalent result sets, measures updates and storage, and tests the effect of dropping the report index. Temporary site edits are rolled back, and the report index is restored. `normalize.db` is about **36 MB** on the Linux test host; it is ignored by `.gitignore` and is **not** committed as a large binary. The setup script is the reproducible artifact that restores it when freshly cloning the repository.

## Evidence by round

| Round | Evidence |
|---|---|
| 1 · See it | [Functional dependencies + two ER sketches](normalization-notes.md) |
| 2 · Break it | Three actual SQL anomaly statements, tested in `run_module5.py` |
| 3 · Build it | [setup.sql](setup.sql), row-count and foreign-key assertions |
| 4 · Race it | Five interleaved runs each, two query plans, matching aggregates in [results.txt](results.txt) |
| 5 · Price it | Site update 1 vs 4,000 rows, `dbstat`, report index experiment |
| 6 · Decide | [Memo to Yasmin Kaya](memo.md) citing local results |
| 7 · Harvest | [Curiosity questions](normalization-notes.md) for the next actual pod exchange |

[Reflection 05](../Reflections/ref05.md) records what was done independently and what still needs an in-person discussion.

## Important for the professor's preparation email

- **Rounds 5–7:** the storage numbers, site-update row counts and memo are documented here.
- **`Module05/normalize.db`:** keep this generated local file in your portfolio folder for Module 06a. Git deliberately ignores it.
- **`uv sync`:** `duckdb` is already declared in the root `pyproject.toml`.
- **Next session:** the 2,000,000-row history / Parquet / SQLite-vs-DuckDB race is **Module 06a**, not Module 05. Do not claim it is completed here.
