import pandas as pd

df = pd.read_parquet("rancilio-portafilter-dataset.parquet")
original_rows = len(df)

df[["pressure", "flowRate", "totalVolume"]] = df[
    ["pressure", "flowRate", "totalVolume"]
].fillna(0)

valid = (
    df["temp"].between(0, 140) &
    df["pressure"].between(0, 15) &
    (df["flowRate"] >= 0)
)

df = df[valid]

df.to_parquet("cleaned_rancilio_data.parquet", index=False)

print(f"Original rows : {original_rows:,}")
print(f"Cleaned rows  : {len(df):,}")
print(f"Removed rows  : {original_rows - len(df):,}")
print("Saved as cleaned_rancilio_data.parquet")