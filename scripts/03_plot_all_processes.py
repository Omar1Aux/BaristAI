import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "data/segmented_rancilio_data.parquet"
OUTPUT_DIR = "process_plots"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_parquet(DATA_PATH)

for process_id, group in df.groupby("process_id"):
    group = group.reset_index(drop=True)

    plt.figure(figsize=(12, 7))

    plt.plot(group.index, group["temp"], label="Temperature")
    plt.plot(group.index, group["pressure"], label="Pressure")
    plt.plot(group.index, group["flowRate"], label="Flow Rate")

    plt.title(f"Process {process_id} | Rows: {len(group)} | Phases: {', '.join(group['phase'].unique())}")
    plt.xlabel("Time step")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    file_path = os.path.join(OUTPUT_DIR, f"process_{process_id}.png")
    plt.savefig(file_path, dpi=120, bbox_inches="tight")
    plt.close()

print(f"Done. Plots saved in: {OUTPUT_DIR}")