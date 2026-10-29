-- Task 6
SELECT machine, COUNT(*) AS n FROM readings GROUP BY machine;
SELECT machine, MAX(vib_rms) AS peak_vib FROM readings GROUP BY machine;
SELECT COUNT(*) AS alarms FROM readings WHERE vib_rms > 2.0;

-- Task 7: readings after 18:00 on each date
SELECT machine, ROUND(AVG(spindle_load), 2) AS avg_spindle_load
FROM readings
WHERE time(ts) > '18:00:00'
GROUP BY machine
ORDER BY avg_spindle_load DESC;
