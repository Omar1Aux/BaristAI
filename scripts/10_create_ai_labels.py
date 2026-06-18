import pandas as pd

INPUT_PATH = "data/ai_features.parquet"
OUTPUT_PATH = "data/ai_training_dataset.parquet"

df = pd.read_parquet(INPUT_PATH)


def calculate_quality_score(row):
    score = 100

    # Temperature target
    if row["temp_avg"] < 88:
        score -= 20
    elif row["temp_avg"] > 96:
        score -= 20

    # Pressure target
    if row["pressure_avg"] < 4:
        score -= 25
    elif row["pressure_avg"] > 10:
        score -= 20

    # Duration target
    if row["duration"] < 25:
        score -= 20
    elif row["duration"] > 120:
        score -= 15

    # Flow stability
    if row["flow_std"] > 180:
        score -= 15

    # Pressure stability
    if row["pressure_std"] > 3:
        score -= 10

    return max(0, min(100, score))


def quality_label(score):
    if score >= 70:
        return "Good extraction"
    elif score >= 40:
        return "Warning extraction"
    else:
        return "Poor extraction"


df["quality_score"] = df.apply(calculate_quality_score, axis=1)
df["quality_label"] = df["quality_score"].apply(quality_label)

df.to_parquet(OUTPUT_PATH, index=False)
df.to_csv("data/ai_training_dataset.csv", index=False)

print("AI training dataset created")
print("Rows:", len(df))
print("\nLabel distribution:")
print(df["quality_label"].value_counts())

print("\nSample:")
print(df[["process_id", "quality_score", "quality_label"]].head(15))