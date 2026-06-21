from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "rancilio-portafilter-dataset.parquet"

if not DATA_FILE.exists():
    DATA_FILE = BASE_DIR / "data" / "segmented_rancilio_data.parquet"

SEGMENT_LABELS = {
    1: "Brewing",
    2: "Flushing",
    3: "Steam",
    4: "Heating",
    5: "Idle",
}

SEGMENT_COLORS = {
    1: "#d95f02",
    2: "#1b9e77",
    3: "#7570b3",
    4: "#e6ab02",
    5: "#666666",
}


def load_dataset():
    df = pd.read_parquet(DATA_FILE).copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df["process_id"] = pd.to_numeric(df["process_id"], errors="coerce").astype("Int64")
    df["segment_id"] = pd.to_numeric(df["segment_id"], errors="coerce").astype("Int64")

    df = df.dropna(subset=["process_id", "timestamp"])
    df["process_id"] = df["process_id"].astype(int)
    df["segment_id"] = df["segment_id"].fillna(0).astype(int)

    df = df.sort_values(["process_id", "timestamp"], kind="stable").reset_index(drop=True)
    return df


DF = load_dataset()


def get_process_ids():
    return sorted(DF["process_id"].unique().tolist())


def get_process(process_id):
    process_df = DF[DF["process_id"] == int(process_id)].copy()
    process_df = process_df.sort_values("timestamp", kind="stable").reset_index(drop=True)

    if process_df.empty:
        return process_df

    start_time = process_df["timestamp"].iloc[0]
    process_df["elapsed_seconds"] = (
        process_df["timestamp"] - start_time
    ).dt.total_seconds()

    return process_df


def get_process_type(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return "Unknown"

    counts = process_df["segment_id"].value_counts()

    if counts.empty:
        return "Other"

    dominant_segment = int(counts.idxmax())
    return SEGMENT_LABELS.get(dominant_segment, "Other")


def get_brew_window(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return process_df

    brew_df = process_df[process_df["segment_id"] == 1].copy()

    if brew_df.empty:
        return brew_df

    start_time = brew_df["timestamp"].iloc[0]
    brew_df["brew_elapsed_seconds"] = (
        brew_df["timestamp"] - start_time
    ).dt.total_seconds()

    return brew_df.reset_index(drop=True)


def get_process_duration(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return 0

    return round(
        (process_df["timestamp"].iloc[-1] - process_df["timestamp"].iloc[0]).total_seconds(),
        2
    )


def get_brew_duration(process_id):
    brew_df = get_brew_window(process_id)

    if brew_df.empty:
        return 0

    return round(
        (brew_df["timestamp"].iloc[-1] - brew_df["timestamp"].iloc[0]).total_seconds(),
        2
    )


def get_segments(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return []

    segments = []
    segment_series = process_df["segment_id"].ffill().bfill()
    run_numbers = segment_series.ne(segment_series.shift()).fillna(True).cumsum()

    temp_df = process_df.copy()
    temp_df["_run"] = run_numbers

    for _, segment_df in temp_df.groupby("_run", sort=True):
        segment_id = int(segment_df["segment_id"].iloc[0])

        segments.append({
            "segment_id": segment_id,
            "label": SEGMENT_LABELS.get(segment_id, "Other"),
            "color": SEGMENT_COLORS.get(segment_id, "#999999"),
            "start": float(segment_df["elapsed_seconds"].iloc[0]),
            "end": float(segment_df["elapsed_seconds"].iloc[-1]),
        })

    return segments


def evaluate_process(process_id):
    brew_df = get_brew_window(process_id)

    if brew_df.empty:
        return {
            "quality_score": 0,
            "quality_label": "Invalid / Other",
            "feedback": ["No brewing segment found."]
        }

    temp_avg = float(brew_df["temp"].mean()) if "temp" in brew_df.columns else 0
    pressure_avg = float(brew_df["pressure"].mean()) if "pressure" in brew_df.columns else 0
    brew_duration = get_brew_duration(process_id)

    score = 100
    feedback = []

    if temp_avg < 90:
        score -= 25
        feedback.append("Temperature is low. Allow more warm-up time or check temperature stability.")
    elif temp_avg > 96:
        score -= 25
        feedback.append("Temperature is high. Consider a cooling flush or reduce overheating.")

    if pressure_avg < 8.5:
        score -= 30
        feedback.append("Pressure is low. Grind finer or increase puck resistance.")
    elif pressure_avg > 10.5:
        score -= 30
        feedback.append("Pressure is high. Grind coarser or reduce puck resistance.")

    if brew_duration < 25:
        score -= 20
        feedback.append("Extraction is too short. Grind finer or increase dose.")
    elif brew_duration > 30:
        score -= 20
        feedback.append("Extraction is too long. Grind coarser or reduce dose.")

    score = max(0, min(100, score))

    if score >= 75:
        label = "Good extraction"
    elif score >= 45:
        label = "Warning extraction"
    else:
        label = "Poor extraction"

    if not feedback:
        feedback.append("Extraction looks stable.")

    return {
        "quality_score": round(score, 2),
        "quality_label": label,
        "feedback": feedback,
        "temperature_avg": round(temp_avg, 2),
        "pressure_avg": round(pressure_avg, 2),
        "brew_duration": round(brew_duration, 2),
    }


def get_process_summary(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return None

    evaluation = evaluate_process(process_id)

    return {
        "process_id": int(process_id),
        "process_type": get_process_type(process_id),
        "rows": int(len(process_df)),
        "process_duration": get_process_duration(process_id),
        "brew_duration": get_brew_duration(process_id),
        "segments": get_segments(process_id),
        "evaluation": evaluation,
    }


def get_timeseries(process_id):
    process_df = get_process(process_id)

    rows = []

    for _, row in process_df.iterrows():
        rows.append({
            "process_id": int(row["process_id"]),
            "elapsed_seconds": float(row["elapsed_seconds"]),
            "segment_id": int(row["segment_id"]),
            "segment_label": SEGMENT_LABELS.get(int(row["segment_id"]), "Other"),
            "temperature": float(row["temp"]) if "temp" in row and pd.notna(row["temp"]) else 0,
            "pressure": float(row["pressure"]) if "pressure" in row and pd.notna(row["pressure"]) else 0,
            "flowRate": float(row["flowRate"]) if "flowRate" in row and pd.notna(row["flowRate"]) else 0,
            "totalVolume": float(row["totalVolume"]) if "totalVolume" in row and pd.notna(row["totalVolume"]) else 0,
        })

    return rows