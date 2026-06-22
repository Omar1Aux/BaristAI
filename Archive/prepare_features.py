import pandas as pd

df = pd.read_parquet("cleaned_rancilio_data.parquet")

features = df.groupby("process_id").agg(

    avg_temp=("temp", "mean"),
    max_temp=("temp", "max"),

    avg_pressure=("pressure", "mean"),
    max_pressure=("pressure", "max"),

    avg_flowRate=("flowRate", "mean"),
    max_flowRate=("flowRate", "max"),

    total_volume=("totalVolume", "max"),

    avg_heater_power=("HeaterPower", "mean")

).reset_index()

features.to_parquet("process_features.parquet", index=False)

print(features.head())

print("\nNumber of processes:", len(features))