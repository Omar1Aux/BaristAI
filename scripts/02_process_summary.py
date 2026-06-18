import pandas as pd

DATA_PATH = "data/segmented_rancilio_data.parquet"

df = pd.read_parquet(DATA_PATH)

summary = []

for process_id, group in df.groupby("process_id"):
    summary.append({
        "process_id": process_id,
        "rows": len(group),
        "start_time": group["timestamp"].min(),
        "end_time": group["timestamp"].max(),
        "duration_seconds": (group["timestamp"].max() - group["timestamp"].min()).total_seconds(),
        "temp_min": group["temp"].min(),
        "temp_avg": group["temp"].mean(),
        "temp_max": group["temp"].max(),
        "pressure_min": group["pressure"].min(),
        "pressure_avg": group["pressure"].mean(),
        "pressure_max": group["pressure"].max(),
        "flow_min": group["flowRate"].min(),
        "flow_avg": group["flowRate"].mean(),
        "flow_max": group["flowRate"].max(),
        "total_volume_max": group["totalVolume"].max(),
        "phases": ", ".join(group["phase"].unique())
    })

summary_df = pd.DataFrame(summary)

summary_df.to_csv("data/process_summary.csv", index=False)

print(summary_df.sort_values("rows", ascending=False).head(10))
print("\nSaved to data/process_summary.csv")