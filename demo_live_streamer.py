import argparse
import time
from pathlib import Path

import pandas as pd
import requests


def main():
    parser = argparse.ArgumentParser(description="BaristAI demo live streamer")
    parser.add_argument("--file", default="demo_shots.csv", help="CSV file path")
    parser.add_argument("--process-id", type=int, default=101, help="Demo process_id to stream")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between readings in seconds")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/live/reading", help="Flask live reading endpoint")
    parser.add_argument("--reset-url", default="http://127.0.0.1:5000/api/live/reset", help="Flask reset endpoint")
    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.exists():
        csv_path = Path(__file__).resolve().parent / args.file

    df = pd.read_csv(csv_path)
    df = df[df["process_id"] == args.process_id].copy()

    if df.empty:
        available = sorted(pd.read_csv(csv_path)["process_id"].unique().tolist())
        raise SystemExit(f"No rows found for process_id={args.process_id}. Available: {available}")

    df = df.sort_values("time")

    print(f"Resetting live buffer: {args.reset_url}")
    try:
        requests.post(args.reset_url, timeout=3)
    except Exception as exc:
        print("Warning: could not reset live buffer:", exc)

    print(f"Streaming process_id={args.process_id}")
    print(f"Rows: {len(df)}")
    print(f"POST endpoint: {args.url}")
    print("Press CTRL + C to stop.\n")

    for _, row in df.iterrows():
        payload = {
            "process_id": int(row["process_id"]),
            "segment_id": int(row["segment_id"]),
            "temp": float(row["temp"]),
            "pressure": float(row["pressure"]),
            "flowRate": float(row.get("flowRate", 0)),
            "totalVolume": float(row.get("totalVolume", 0)),
            "time": float(row["time"]),
            "preinfusion": float(row.get("preinfusion", 0)),
            "preinfusionpause": float(row.get("preinfusionpause", 0)),
            "setPoint": float(row.get("setPoint", 93)),
            "quality_label": "Live reading",
            "feedback": ["Live demo data received."]
        }

        response = requests.post(args.url, json=payload, timeout=5)
        print(f"Sent t={payload['time']:>5.1f}s | temp={payload['temp']:>5.1f} | pressure={payload['pressure']:>5.2f} | segment={payload['segment_id']} | status={response.status_code}")
        time.sleep(args.delay)

    print("\nDemo stream finished.")


if __name__ == "__main__":
    main()
