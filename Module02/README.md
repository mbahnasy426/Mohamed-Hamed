# Module 02 — Data Contracts & Reading Legacy Schemas

**Focus:** inspect a broken maintenance database, reconstruct its intended ER model, prove defects using SQL, and describe a corrected executable contract.

## Learning goals and evidence

| Learning goal | Evidence |
|---|---|
| Reconstruct entities, keys, relationships and cardinality | [ER audit with Mermaid diagram](er-audit.md) |
| Distinguish 1:1, 1:n and m:n and draw examples | [Four ER sketches and SQL proof](er-examples.md) |
| Find defects using real queries, not guesses | [SQL for five defects](defect-queries.sql) and [recorded results](er-audit.md) |
| Explain natural vs surrogate keys | [ER audit — key choices](er-audit.md) |
| Implement a code-first data contract | [Pydantic + SQLAlchemy contract](contract.py) |
| Describe the missing business requirements | [Business rules](er-audit.md) |
| Record sources, verification and learning | [Study log](study-log.md) and [Reflection 02](../Reflections/ref02.md) |

## Reproduce the legacy database and tests

From the repository root (SQLite CLI installed):

```powershell
sqlite3 Module02/legacy.db ".read Module02/setup.sql"
sqlite3 -header -column Module02/legacy.db ".read Module02/defect-queries.sql"
uv run python Module02/contract.py
```

The `setup.sql` is rerunnable and intentionally creates an **incorrect** schema. It must not be mistaken for the repaired one. Database files (`*.db`) are ignored by Git.

## Findings to explain in the checkpoint

1. `maint_job` references missing machine `cnc-05` (orphan).
2. `P-1003` exists twice (no uniqueness).
3. `unit_price` is `TEXT`, so comparing it with `'15'` can give misleading results.
4. A machine has installed date `unknown`.
5. `parts_used` contains comma-separated values, which hides a many-to-many relationship.

## What is still to verify

- Run the SQL and the Pydantic/SQLAlchemy contract on the student's own environment; the five legacy defect results were checked using SQLite, but the committed contract is not yet accompanied by captured runtime DDL output.
- Complete a **real** neighboring-pod discussion, record the agreed learning and share a diagram on Discord. The portfolio does not claim those events occurred.
- Optional stretcher work on EER inheritance and additional Mermaid curiosities is not included.



[Course Module 2](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/02-data-contracts-and-legacy-schemas.md) · [Back to main portfolio](../README.md)
