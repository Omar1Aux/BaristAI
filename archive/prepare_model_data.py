import pandas as pd

metrics = pd.read_parquet("process_metrics.parquet")
quality = pd.read_parquet("process_quality_scores.parquet")

dataset = metrics.merge(
    quality[["process_id", "quality_score"]],
    on="process_id"
)

dataset.to_parquet("model_dataset.parquet", index=False)

print(dataset.head())