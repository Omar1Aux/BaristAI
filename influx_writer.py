import subprocess
from datetime import datetime

INFLUX_PATH = r"C:\BaristAI\influxdb3-core-3.9.3-windows_amd64\influxdb3.exe"
DATABASE = "baristai"


def write_espresso_data(process_id, temperature, pressure, flow_rate, quality_score):
    line = (
        f'espresso,process_id={process_id} '
        f'temperature={temperature},'
        f'pressure={pressure},'
        f'flowRate={flow_rate},'
        f'quality_score={quality_score}'
    )

    command = [
        INFLUX_PATH,
        "write",
        "--database",
        DATABASE,
        line
    ]

    subprocess.run(command, capture_output=True, text=True)