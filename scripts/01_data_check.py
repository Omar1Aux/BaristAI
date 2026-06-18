import pandas as pd

DATA_PATH = "data/segmented_rancilio_data.parquet"

df = pd.read_parquet(DATA_PATH)

print("\n===== BASIC INFO =====")
print(df.info())

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== FIRST ROWS =====")
print(df.head())

print("\n===== MISSING VALUES =====")
print(df.isna().sum())

print("\n===== NUMERIC SUMMARY =====")
print(df.describe())

print("\n===== PROCESS COUNT =====")
print("Number of processes:", df["process_id"].nunique())

print("\n===== ROWS PER PROCESS =====")
print(df.groupby("process_id").size().describe())

print("\n===== TEMP RANGE =====")
print(df["temp"].min(), df["temp"].max())

print("\n===== PRESSURE RANGE =====")
print(df["pressure"].min(), df["pressure"].max())

print("\n===== FLOW RATE RANGE =====")
if "flowRate" in df.columns:
    print(df["flowRate"].min(), df["flowRate"].max())
else:
    print("No flowRate column found")