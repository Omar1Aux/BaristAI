import pandas as pd

df = pd.read_parquet("process_metrics.parquet")

scores = []

for index, row in df.iterrows():

    process_id = row["process_id"] if "process_id" in df.columns else index

    score = 0
    notes = []

    # Temperature score: 30 points
    if 88 <= row["temp_avg"] <= 96:
        score += 30
        notes.append("Temperature good")
    elif 85 <= row["temp_avg"] < 88 or 96 < row["temp_avg"] <= 100:
        score += 15
        notes.append("Temperature acceptable")
    else:
        notes.append("Temperature outside ideal range")

    # Pressure score: 30 points
    if 8 <= row["pressure_avg"] <= 10:
        score += 30
        notes.append("Pressure good")
    elif 6 <= row["pressure_avg"] < 8 or 10 < row["pressure_avg"] <= 12:
        score += 15
        notes.append("Pressure acceptable")
    else:
        notes.append("Pressure outside ideal range")

    # Duration score: 20 points
    if 25 <= row["duration_seconds"] <= 30:
        score += 20
        notes.append("Extraction duration good")
    elif 20 <= row["duration_seconds"] < 25 or 30 < row["duration_seconds"] <= 35:
        score += 10
        notes.append("Extraction duration acceptable")
    else:
        notes.append("Extraction duration outside ideal range")

    # Flow stability score: 20 points
    # Lower std means more stable relative flow behavior
    if row["flow_std"] <= row["flow_avg"] * 0.5:
        score += 20
        notes.append("Flow stable")
    elif row["flow_std"] <= row["flow_avg"]:
        score += 10
        notes.append("Flow moderately stable")
    else:
        notes.append("Flow unstable")

    if score >= 80:
        quality = "Excellent extraction"
    elif score >= 60:
        quality = "Acceptable extraction"
    else:
        quality = "Poor extraction"

    scores.append({
        "process_id": process_id,
        "quality_score": score,
        "quality_label": quality,
        "quality_notes": " | ".join(notes)
    })

score_df = pd.DataFrame(scores)

score_df.to_parquet("process_quality_scores.parquet", index=False)

print("process_quality_scores.parquet created successfully!")
print(score_df.head())