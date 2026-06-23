"""Optional InfluxDB writer for BaristAI.

InfluxDB is not required for the dashboard, Simulate Live, or MQTT Real Live.
This file only preserves the optional old Influx write path.

If InfluxDB does not start, the most common causes are:
1. Another InfluxDB process is already using the port.
2. The local influxdb_data folder is corrupted.
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INFLUX_PATH = BASE_DIR / "influxdb3-core-3.9.3-windows_amd64" / "influxdb3.exe"

INFLUX_PATH = os.getenv("INFLUX_PATH", str(DEFAULT_INFLUX_PATH))
INFLUX_DATABASE = os.getenv("INFLUX_DATABASE", "baristai")


def write_espresso_data(process_id, temperature, pressure, extraction_time, quality_score):
    line = (
        f"espresso,process_id={int(process_id)} "
        f"temperature={float(temperature)},"
        f"pressure={float(pressure)},"
        f"extraction_time={float(extraction_time)},"
        f"quality_score={float(quality_score)}"
    )

    command = [
        INFLUX_PATH,
        "write",
        "--database",
        INFLUX_DATABASE,
        line,
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print("Influx write failed:")
        print(result.stderr)

    return result
