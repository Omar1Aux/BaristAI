import pandas as pd

DATA_PATH = "data/clean_brew_windows.parquet"
OUTPUT_PATH = "data/ai_features.parquet"

df = pd.read_parquet(DATA_PATH)

features = []

for process_id, g in df.groupby("process_id"):
    g = g.sort_values("shot_step")

    duration = len(g)
    volume_delta = g["totalVolume"].max() - g["totalVolume"].min()

    features.append({
        "process_id": process_id,

        "duration": duration,
        "volume_delta": volume_delta,

        "temp_avg": g["temp"].mean(),
        "temp_min": g["temp"].min(),
        "temp_max": g["temp"].max(),
        "temp_std": g["temp"].std(),

        "pressure_avg": g["pressure"].mean(),
        "pressure_min": g["pressure"].min(),
        "pressure_max": g["pressure"].max(),
        "pressure_std": g["pressure"].std(),

        "flow_avg": g["flowRate"].mean(),
        "flow_min": g["flowRate"].min(),
        "flow_max": g["flowRate"].max(),
        "flow_std": g["flowRate"].std(),

        "preinfusion": g["preinfusion"].max(),
        "preinfusionpause": g["preinfusionpause"].max(),
        "setPoint": g["setPoint"].max(),
    })

features_df = pd.DataFrame(features)

features_df.to_parquet(OUTPUT_PATH, index=False)
features_df.to_csv("data/ai_features.csv", index=False)

print("AI feature dataset created")
print("Rows:", len(features_df))
print("Columns:", features_df.columns.tolist())
print(features_df.head())