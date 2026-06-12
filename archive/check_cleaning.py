import pandas as pd

df = pd.read_parquet("cleaned_rancilio_data.parquet")

print("Rows:", len(df))
print("Processes:", df["process_id"].nunique())

print("\nMissing values:")
print(df[["temp", "pressure", "flowRate", "totalVolume"]].isna().sum())

print("\nInvalid values:")
print("Invalid temp:", ((df["temp"] < 0) | (df["temp"] > 140)).sum())
print("Invalid pressure:", ((df["pressure"] < 0) | (df["pressure"] > 15)).sum())
print("Invalid flowRate:", (df["flowRate"] < 0).sum())

print("\nStats:")
print(df[["temp", "pressure", "flowRate", "totalVolume"]].describe())