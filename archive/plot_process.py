import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_parquet("cleaned_rancilio_data.parquet")


process_id = int(input("Enter process_id: "))

# Filter
process_df = df[df["process_id"] == process_id]

if process_df.empty:
    print("No data found for this process_id.")
else:
    print(f"Rows found: {len(process_df)}")

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle(f"Espresso Extraction — Process ID: {process_id}", fontsize=14)

    sensors = [
        ("temp", "Temperature (°C)", "tomato"),
        ("pressure", "Pressure (bar)", "steelblue"),
        ("flowRate", "Flow Rate (mL/s)", "seagreen"),
    ]

    for ax, (column, label, color) in zip(axes, sensors):
        ax.plot(process_df["timestamp"], process_df[column], color=color, label=label)
        ax.set_xlabel("Timestamp")
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.legend()
        ax.grid(True)
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.show()