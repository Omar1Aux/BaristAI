import pandas as pd

# Load data
df = pd.read_parquet("cleaned_rancilio_data.parquet")

# Create new column
df["phase"] = "Idle"

# Heating phase
df.loc[
    (df["pressure"] == 0) &
    (df["flowRate"] == 0) &
    (df["temp"] < 90),
    "phase"
] = "Heating"

# Brewing phase
df.loc[
    (df["pressure"] > 0) |
    (df["flowRate"] > 0),
    "phase"
] = "Brewing"

# Save
df.to_parquet("segmented_rancilio_data.parquet", index=False)

print(df[["process_id", "temp", "pressure", "flowRate", "phase"]].head(20))