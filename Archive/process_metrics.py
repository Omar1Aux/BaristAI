import pandas as pd

df = pd.read_parquet("cleaned_rancilio_data.parquet")

df["timestamp"] = pd.to_datetime(df["timestamp"])

metrics = df.groupby("process_id").agg(
    temp_min=("temp", "min"),
    temp_max=("temp", "max"),
    temp_avg=("temp", "mean"),
    temp_std=("temp", "std"),

    pressure_min=("pressure", "min"),
    pressure_max=("pressure", "max"),
    pressure_avg=("pressure", "mean"),
    pressure_std=("pressure", "std"),

    flow_min=("flowRate", "min"),
    flow_max=("flowRate", "max"),
    flow_avg=("flowRate", "mean"),
    flow_std=("flowRate", "std"),

    total_volume=("totalVolume", "max"),

    start_time=("timestamp", "min"),
    end_time=("timestamp", "max")
)

metrics["duration_seconds"] = (
    metrics["end_time"] - metrics["start_time"]
).dt.total_seconds()

metrics.to_parquet("process_metrics.parquet")

print("process_metrics.parquet created successfully!")
print(metrics.head())