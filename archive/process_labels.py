import pandas as pd

# Load metrics
df = pd.read_parquet("process_metrics.parquet")

labels = []

for index, row in df.iterrows():

    process_id = row["process_id"] if "process_id" in df.columns else index

    feedback = []
    label = "Good extraction"

    # Pressure rules
    if row["pressure_max"] > 10:
        feedback.append("Pressure too high")
        label = "Bad extraction"
    elif row["pressure_max"] < 7:
        feedback.append("Pressure too low")
        label = "Bad extraction"
    else:
        feedback.append("Pressure looks good")

    # Temperature rules
    if row["temp_avg"] < 85:
        feedback.append("Temperature too low")
        label = "Bad extraction"
    elif row["temp_max"] > 96:
        feedback.append("Temperature too high")
        label = "Bad extraction"
    else:
        feedback.append("Temperature looks stable")

    # Duration rules
    if row["duration_seconds"] < 20:
        feedback.append("Extraction too short")
        label = "Under extraction"
    elif row["duration_seconds"] > 35:
        feedback.append("Extraction too long")
        label = "Over extraction"
    else:
        feedback.append("Extraction duration looks good")

    labels.append({
        "process_id": process_id,
        "label": label,
        "feedback": " | ".join(feedback)
    })

labels_df = pd.DataFrame(labels)

labels_df.to_parquet("process_labels.parquet", index=False)

print("process_labels.parquet created successfully!")
print(labels_df.head())