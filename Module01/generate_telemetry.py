"""Generate reproducible machine telemetry for Module 01."""
import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
machines = ["cnc-01", "cnc-02", "cnc-03"]
start = datetime(2026, 1, 5, 6, 0, 0)
days = 2
step = 3
points = days * 24 * 60 * 60 // step

out = Path(__file__).with_name("telemetry.csv")
with out.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ts", "machine", "temp_c", "vib_rms", "spindle_load"])
    for i in range(points):
        timestamp = (start + timedelta(seconds=i * step)).isoformat(sep=" ")
        for machine in machines:
            temperature = 42 + 3 * math.sin(i / 500.0) + random.gauss(0, 0.6)
            vibration = 1.2 + 0.4 * math.sin(i / 90.0) + random.gauss(0, 0.08)
            load = 60 + 15 * math.sin(i / 300.0) + random.gauss(0, 3)
            if machine == "cnc-02":
                vibration += 0.9 * (i / points)
            if random.random() < 0.0008:
                vibration += random.uniform(0.4, 0.9)
            writer.writerow([timestamp, machine, f"{temperature:.2f}", f"{vibration:.3f}", f"{load:.1f}"])
print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {points * len(machines)} rows)")
