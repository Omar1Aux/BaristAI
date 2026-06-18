import pandas as pd

df = pd.read_parquet("data/segmented_rancilio_data.parquet")

clean_ids = pd.read_csv("data/clean_shot_ids_v2.csv")["process_id"].tolist()

clean_parts = []

BUFFER_BEFORE = 5
BUFFER_AFTER = 8
FLOW_THRESHOLD = 50

for process_id in clean_ids:
    g = df[df["process_id"] == process_id].reset_index(drop=True)

    active_idx = g.index[g["flowRate"] > FLOW_THRESHOLD].tolist()

    if not active_idx:
        continue

    start = max(min(active_idx) - BUFFER_BEFORE, 0)
    end = min(max(active_idx) + BUFFER_AFTER, len(g) - 1)

    shot = g.iloc[start:end + 1].copy()
    shot["shot_step"] = range(1, len(shot) + 1)

    clean_parts.append(shot)

clean_brew_df = pd.concat(clean_parts, ignore_index=True)

clean_brew_df.to_parquet("data/clean_brew_windows.parquet")

print("Clean processes:", len(clean_parts))
print("Rows after window extraction:", len(clean_brew_df))
print("Saved: data/clean_brew_windows.parquet")

print("\nRows per process after extraction:")
print(clean_brew_df.groupby("process_id").size().describe())