import pandas as pd

df = pd.read_parquet("data/segmented_rancilio_data.parquet")

rows = []

for process_id, g in df.groupby("process_id"):
    volume_delta = g["totalVolume"].max() - g["totalVolume"].min()

    rows.append({
        "process_id": process_id,
        "rows": len(g),
        "phase": ",".join(g["phase"].unique()),
        "temp_avg": g["temp"].mean(),
        "temp_max": g["temp"].max(),
        "pressure_avg": g["pressure"].mean(),
        "pressure_max": g["pressure"].max(),
        "flow_avg": g["flowRate"].mean(),
        "flow_max": g["flowRate"].max(),
        "volume_delta": volume_delta,
    })

summary = pd.DataFrame(rows)

clean = summary[
    (summary["phase"].str.contains("Brewing", na=False)) &
    (summary["rows"] >= 100) &
    (summary["rows"] <= 400) &
    (summary["pressure_max"] >= 5) &
    (summary["flow_max"] >= 100) &
    (summary["volume_delta"] >= 20) &
    (summary["volume_delta"] <= 250)
].copy()

rejected = summary[~summary["process_id"].isin(clean["process_id"])].copy()

clean.to_csv("data/clean_shot_ids_v2.csv", index=False)
rejected.to_csv("data/rejected_processes_v2.csv", index=False)

print("Total processes:", len(summary))
print("Clean shots:", len(clean))
print("Rejected:", len(rejected))

print("\nClean shot IDs:")
print(clean["process_id"].tolist())

print("\nRejected suspicious:")
print(
    rejected.sort_values("volume_delta", ascending=False)[
        ["process_id", "rows", "pressure_max", "flow_max", "volume_delta", "phase"]
    ].head(15)
)