

# Module 2 — Data Contracts & Reading Legacy Schemas

| Learning goal | Evidence |
|---|---|
| Reconstruct entities, keys, relationships and cardinality | [ER audit with Mermaid diagram](er-audit.md) |
| Distinguish 1:1, 1:n and m:n and draw examples | [Four ER sketches and SQL proof](er-examples.md) |
| Find defects using real queries, not guesses | [SQL for five defects](defect-queries.sql) and [recorded results](er-audit.md) |
| Explain natural vs surrogate keys | [ER audit — key choices](er-audit.md) |
| Implement a code-first data contract | [Pydantic + SQLAlchemy contract](contract.py) |
| Describe the missing business requirements | [Business rules](er-audit.md) |
| Record sources, verification and learning | [Study log](study-log.md) and [Reflection 02](../Reflections/ref02.md) |

## Learning Goals

- Learn how to understand an existing database and create ER and EER diagrams.
- Understand the difference between entities, attributes, relationships, primary keys, and foreign keys.
- Learn about the different relationships, such as one-to-one, one-to-many, and many-to-many.
- Learn how to find problems in databases, like duplicated data, missing foreign keys, and incorrect relationships.
- Understand the difference between natural keys and surrogate keys.
- Learn how Pydantic and SQLAlchemy can help us create rules to keep database information correct.
- Understand why business rules are important in a database.

## What I Learned

In this module, I learned more about how databases are structured and how tables are connected to each other. I also understood that a database can have problems even if it is working.

One important thing I learned was how primary keys and foreign keys help connect tables. I also learned about ER diagrams and the different types of relationships.

## Studio Lab — Auditing the Legacy Maintenance Schema

In this lab, we focused on understanding a maintenance database and finding problems in its structure.

### Task 1 — Understanding the Database Structure

I learned how to identify entities, attributes, primary keys, and foreign keys in a database.

I also understood how ER diagrams show the relationships between different tables.

### Task 2 — Finding Problems in the Database

I learned that a database can contain different problems, such as:

- Missing foreign keys.
- Duplicated information.
- Records connected to something that does not exist.
- Incorrect relationships between tables.

I also understood that we should use SQL queries to check these problems instead of just guessing.

### Task 3 — Data Contracts

I learned that we can use different rules to make sure the information stored in a database is correct.

**In the database (SQLAlchemy):**

- Primary keys help identify records.
- Foreign keys connect tables.
- UNIQUE prevents duplicated values in columns that should be unique.
- NOT NULL means a value cannot be missing.

**In the model (Pydantic):**

- We can check that the information follows certain rules before saving it.
- For example, a machine serial number should start with "SN-".
- We can also check that a date is valid.

**Why we use both:**

I understood that the model helps us find mistakes before saving the information, while the database has rules to protect the data.

### Task 4 — Understanding Relationships and Keys

I learned the difference between:

- **Entity:** Something we store information about, like a machine.


## Reflection 2
[Reflection 2](/Reflections/ref02.md)

## Task ...

...

If the module is longer than 1 week, you might have several reflections within it. If not, delete this and the following.

## Reflection 3
[Reflection 3](/Reflections/ref03.md)


