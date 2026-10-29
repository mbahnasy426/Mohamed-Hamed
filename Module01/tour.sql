PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE reading (
    id INTEGER PRIMARY KEY,
    machine TEXT,
    vibration REAL
);
INSERT INTO reading VALUES(1,'Machine_A',2.5),
  (2,'Machine_B',3.8),
  (3,'Machine_A',4.2);
COMMIT;
