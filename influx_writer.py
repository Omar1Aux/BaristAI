import subprocess

INFLUX_PATH = r"C:\BaristAI\influxdb3-core-3.9.3-windows_amd64\influxdb3.exe"
DATABASE = "baristai"


def write_espresso_data(process_id, temperature, pressure, extraction_time, quality_score):
    line = (
        f"espresso,process_id={process_id} "
        f"temperature={temperature},"
        f"pressure={pressure},"
        f"extraction_time={extraction_time},"
        f"quality_score={quality_score}"
    )

    command = [
        INFLUX_PATH,
        "write",
        "--database",
        DATABASE,
        line
    ]

    subprocess.run(command, capture_output=True, text=True)