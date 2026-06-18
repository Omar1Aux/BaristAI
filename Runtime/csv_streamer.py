import time
import json
import pandas as pd
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "espresso/data"

DATA_FILE = "data/clean_brew_windows.parquet"
PROCESS_ID = 15
DELAY_SECONDS = 1


def main():
    df = pd.read_parquet(DATA_FILE)

    process_data = df[df["process_id"] == PROCESS_ID].reset_index(drop=True)

    if process_data.empty:
        print(f"No data found for process_id {PROCESS_ID}")
        return

    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    print("CSV/Parquet streamer started")
    print(f"Streaming process_id {PROCESS_ID}")
    print(f"Rows: {len(process_data)}")
    print("Press CTRL + C to stop")

    try:
        for index, row in process_data.iterrows():
            payload = {
                "temp": round(float(row["temp"]), 2),
                "pressure": round(float(row["pressure"]), 2),
                "time": round(index * 0.5, 1)
            }

            client.publish(TOPIC, json.dumps(payload))
            print("Published:", payload)

            time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\nStreamer stopped")

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()