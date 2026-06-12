import pandas as pd

# Load cleaned data
df = pd.read_parquet("cleaned_rancilio_data.parquet")

feedback_results = []

for process_id in df["process_id"].unique():

    process = df[df["process_id"] == process_id]

    max_temp = process["temp"].max()
    min_temp = process["temp"].min()
    avg_temp = process["temp"].mean()

    max_pressure = process["pressure"].max()
    avg_pressure = process["pressure"].mean()

    max_flow = process["flowRate"].max()
    avg_flow = process["flowRate"].mean()

    total_volume = process["totalVolume"].max()

    feedback = []

    # Temperature feedback
    if max_temp > 96:
        feedback.append("Temperature too high")
    elif avg_temp < 85:
        feedback.append("Temperature too low")
    else:
        feedback.append("Temperature looks stable")

    # Pressure feedback
    if max_pressure > 10:
        feedback.append("Pressure too high")
    elif max_pressure < 7:
        feedback.append("Pressure too low")
    else:
        feedback.append("Pressure looks good")

    # Flow feedback
    if max_flow > 10:
        feedback.append("Flow rate too high")
    elif max_flow < 3:
        feedback.append("Flow rate too low")
    else:
        feedback.append("Flow rate looks okay")

    feedback_results.append({
        "process_id": process_id,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "avg_temp": avg_temp,
        "max_pressure": max_pressure,
        "avg_pressure": avg_pressure,
        "max_flowRate": max_flow,
        "avg_flowRate": avg_flow,
        "total_volume": total_volume,
        "feedback": " | ".join(feedback)
    })

feedback_df = pd.DataFrame(feedback_results)

feedback_df.to_parquet("process_feedback.parquet", index=False)

print("Feedback file created successfully!")
print(feedback_df.head())