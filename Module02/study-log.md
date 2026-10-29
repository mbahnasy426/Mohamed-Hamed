# Module 02 — Study log: ER models and legacy schemas

## Resources and what they taught me

| Source | Main idea to understand |
|---|---|
| [Course Module 2](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/02-data-contracts-and-legacy-schemas.md) | Understand the meaning behind a legacy database |
| [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html) | Enable `PRAGMA foreign_keys=ON` so links are enforced |
| [Mermaid ER diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html) | Show entities, attributes and cardinality graphically |
| [Pydantic](https://docs.pydantic.dev/latest/) | Validate input in Python |
| [SQLAlchemy](https://docs.sqlalchemy.org/) | Declare tables and constraints in Python |

## Concepts I looked up

- **Entity:** an independent thing, e.g. Machine, Part, Technician.
- **Attribute:** a fact about an entity, e.g. serial number.
- **Relationship:** how entities connect, e.g. one machine has many jobs.
- **Cardinality:** 1:1, 1:n, or m:n.
- **Natural key:** meaningful unique value like `part_no`.
- **Surrogate key:** generated ID with no business meaning, e.g. `machine_id`.
- **Orphan:** a job references a missing machine.
- **1NF:** do not store comma-separated lists in one database column.
- **Data contract:** rules written as code, checked by the application and database.

## Four drawn ER examples

See [er-examples.md](er-examples.md) for four Mermaid diagrams (1:1 nameplate, 1:n sensors, m:n work orders/parts, and maintenance jobs) and a `CREATE TABLE` / `COUNT` demonstration.

## Two useful reference sketches

1. **Machine → Sensor (1:n)** in [our ER examples](er-examples.md): illustrates why the FK goes on the many-side table.
2. **WorkOrder ↔ Part via OrderPart (m:n)** in [our ER examples](er-examples.md): illustrates why a junction table avoids comma-separated parts.

These are our own explanatory Mermaid sketches, not externally discovered screenshots.

## LLM-assisted Q&A and verification

**Prompt:** "From this schema, identify the intended entities and cardinalities. Could any maintenance jobs reference machines that do not exist?"

**Draft answer to verify:** Machine has many MaintenanceJobs; Technician has many jobs; jobs and parts are many-to-many. Missing FK allows orphan jobs.

**Verification:** [defect-queries.sql](defect-queries.sql) returns `(3, cnc-05)` as an orphan; job 1 stores two part numbers. The diagram alone does not prove these defects — the queries do.

**Prompt:** "Why is `parts_used='P-1001,P-1002'` a problem?"

**Draft answer to verify:** One column contains multiple values, breaking 1NF and making normal joins unreliable.

**Verification:** The naive join in the defect queries excludes job 1, even though it has valid part numbers.

These prompts and summaries document the reasoning used to audit the dataset; they are not presented as an archived transcript from another model.

## Remarkable findings / counterexamples

- Query results can look believable even when wrong: the text price filter excludes `9.90` from values less than `15`.
- `P-1003` is duplicated; a join duplicates job 2.
- Job 1 completely disappears from a join because its two part numbers were stored as one string.

## Agreed learning (pod discussion) — not yet documented

To complete this activity honestly, discuss the ER sketches and queries with the Task Pod and neighboring Pod. Record 3–5 points actually agreed upon, any disagreement, and the selected diagram posted in Discord. **No peer discussion or Discord post is claimed here.**

## Next steps

Confirm the diagrams with classmates, demonstrate the SQLite query results, and check the corrected database schema.
