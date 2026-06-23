import os
import json
import time
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = os.getenv(
    "DATA_FILE",
    str(BASE_DIR / "data" / "rancilio-portafilter-dataset.parquet")
)

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "espresso/data")

PROCESS_ID = int(os.getenv("PROCESS_ID", "15"))
DELAY_SECONDS = float(os.getenv("DELAY_SECONDS", "1"))


def load_data():
    df = pd.read_parquet(DATA_FILE).copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df["process_id"] = pd.to_numeric(df["process_id"], errors="coerce").astype("Int64")
    df["segment_id"] = pd.to_numeric(df.get("segment_id", 0), errors="coerce").astype("Int64")

    df = df.dropna(subset=["process_id", "timestamp"])
    df["process_id"] = df["process_id"].astype(int)
    df["segment_id"] = df["segment_id"].fillna(0).astype(int)

    df = df.sort_values(["process_id", "timestamp"]).reset_index(drop=True)
    return df


def main():
    df = load_data()

    process_df = df[df["process_id"] == PROCESS_ID].copy().reset_index(drop=True)

    if process_df.empty:
        print(f"No data found for process_id {PROCESS_ID}")
        print("Available process IDs:", sorted(df["process_id"].unique().tolist())[:50])
        return

    start_time = process_df["timestamp"].iloc[0]
    process_df["elapsed_seconds"] = (
        process_df["timestamp"] - start_time
    ).dt.total_seconds()

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    print("CSV streamer started")
    print("Data:", DATA_FILE)
    print("Process:", PROCESS_ID)
    print("Broker:", MQTT_BROKER)
    print("Topic:", MQTT_TOPIC)
    print("Rows:", len(process_df))
    print("Delay:", DELAY_SECONDS, "seconds")
    print("Press CTRL + C to stop")

    try:
        for _, row in process_df.iterrows():
            payload = {
                "process_id": int(row["process_id"]),
                "segment_id": int(row["segment_id"]),
                "temp": round(float(row.get("temp", 0)), 2),
                "pressure": round(float(row.get("pressure", 0)), 2),
                "flowRate": round(float(row.get("flowRate", 0)), 2),
                "totalVolume": round(float(row.get("totalVolume", 0)), 2),
                "time": round(float(row["elapsed_seconds"]), 2),
            }

            result = client.publish(MQTT_TOPIC, json.dumps(payload))
            result.wait_for_publish(timeout=3)
            print("Published:", payload)

            time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\nStreamer stopped.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
