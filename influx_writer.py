"""Optional InfluxDB writer for BaristAI live/demo readings.

The main Flask dashboard does not require InfluxDB. This module keeps the older
InfluxDB CLI path available for users who run a local `influxdb3` server.
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INFLUX_PATH = BASE_DIR / "influxdb3-core-3.9.3-windows_amd64" / "influxdb3.exe"

INFLUX_PATH = os.getenv("INFLUX_PATH", str(DEFAULT_INFLUX_PATH))
INFLUX_DATABASE = os.getenv("INFLUX_DATABASE", "baristai")


def write_espresso_data(process_id, temperature, pressure, extraction_time, quality_score):
    """Write one espresso-quality point using the InfluxDB 3 CLI.

    This function is intentionally optional: callers can use it when InfluxDB is
    running, but the dashboard/MQTT flow works without importing or calling it.
    """
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

    return subprocess.run(command, capture_output=True, text=True, check=False)
