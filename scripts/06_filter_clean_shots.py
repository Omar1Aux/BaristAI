import pandas as pd

DATA_PATH = "data/process_summary.csv"

summary = pd.read_csv(DATA_PATH)

clean = summary[
    (summary["phases"].str.contains("Brewing", na=False)) &
    (summary["rows"] >= 100) &
    (summary["rows"] <= 400) &
    (summary["pressure_max"] >= 5) &
    (summary["flow_max"] >= 100) &
    (summary["total_volume_max"] >= 100) &
    (summary["total_volume_max"] <= 900)
].copy()

rejected = summary[~summary["process_id"].isin(clean["process_id"])].copy()

clean.to_csv("data/clean_shot_ids.csv", index=False)
rejected.to_csv("data/rejected_processes.csv", index=False)

print("Total processes:", len(summary))
print("Clean shots:", len(clean))
print("Rejected:", len(rejected))

print("\nClean shot IDs:")
print(clean["process_id"].tolist())

print("\nTop rejected by rows:")
print(rejected.sort_values("rows", ascending=False)[["process_id", "rows", "pressure_max", "flow_max", "total_volume_max", "phases"]].head(15))