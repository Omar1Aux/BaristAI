import pandas as pd

segmented_data = pd.read_parquet("segmented_rancilio_data.parquet")

print(segmented_data.columns)
print(segmented_data.head())