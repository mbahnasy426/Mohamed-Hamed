-- Module 02: corrected relational schema (design proposal)
-- Enable FK enforcement in every SQLite connection.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS machine (
 machine_id INTEGER PRIMARY KEY,
 serial_no VARCHAR NOT NULL UNIQUE,
 site VARCHAR NOT NULL,
 installed DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS part (
 part_no VARCHAR PRIMARY KEY,
 description VARCHAR NOT NULL,
 unit_price NUMERIC(9,2) NOT NULL CHECK (unit_price >= 0)
);
CREATE TABLE IF NOT EXISTS maint_job (
 job_id INTEGER PRIMARY KEY,
 machine_id INTEGER NOT NULL REFERENCES machine(machine_id),
 technician VARCHAR NOT NULL,
 done_on DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS job_part (
 job_id INTEGER NOT NULL REFERENCES maint_job(job_id),
 part_no VARCHAR NOT NULL REFERENCES part(part_no),
 PRIMARY KEY (job_id,part_no)
);
-- The SQLAlchemy contract.py emits a close transitional schema;
-- this hand-authored SQL adds CHECK(unit_price >= 0) explicitly.
