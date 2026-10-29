-- Run after: sqlite3 Module02/legacy.db ".read Module02/setup.sql"
-- 1: orphan maintenance jobs
SELECT m.job_id, m.machine_name FROM maint_job m
LEFT JOIN machine x ON m.machine_name = x.machine_name WHERE x.machine_name IS NULL;
-- 2: duplicate natural keys
SELECT part_no, COUNT(*) AS copies FROM part GROUP BY part_no HAVING COUNT(*) > 1;
-- 3: text comparison can return wrong prices, depending on lexicographic ordering
SELECT part_no, unit_price FROM part WHERE unit_price < '15';
-- Observe the difference with a numeric CAST
SELECT part_no, unit_price FROM part WHERE CAST(unit_price AS REAL) < 15;
-- 4: invalid installed date
SELECT machine_name, installed FROM machine
WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
-- 5: incorrect join with comma-separated part numbers
SELECT j.job_id, p.description FROM maint_job j JOIN part p ON p.part_no=j.parts_used;
-- cardinality: counts per job; NULL means no part listed
SELECT job_id,parts_used,
LENGTH(parts_used)-LENGTH(REPLACE(parts_used,',',''))+1 AS n_parts FROM maint_job;
-- job counts for machines
SELECT machine_name, COUNT(*) FROM maint_job GROUP BY machine_name;
