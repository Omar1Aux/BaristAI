from pathlib import Path
import os
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = Path(os.getenv(
    "BARISTAI_DATA_FILE",
    BASE_DIR / "data" / "rancilio-portafilter-dataset.parquet"
))

if not DATA_FILE.exists():
    fallback = BASE_DIR / "data" / "segmented_rancilio_data.parquet"
    if fallback.exists():
        DATA_FILE = fallback

SEGMENT_LABELS = {
    1: "Brewing",
    2: "Flushing",
    3: "Steam",
    4: "Heating",
    5: "Idle",
}

SEGMENT_COLORS = {
    1: "#8fd19e",
    2: "#9ecff0",
    3: "#b7a3e3",
    4: "#f2d37b",
    5: "#cfcfcf",
}

TARGETS = {
    "temp_min": 90,
    "temp_max": 96,
    "pressure_min": 8.5,
    "pressure_max": 10.5,
    "brew_min": 25,
    "brew_max": 30,
}


def _safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def segment_label(segment_id):
    try:
        return SEGMENT_LABELS.get(int(segment_id), "Other")
    except Exception:
        return "Other"


def load_dataset():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}. "
            "Set BARISTAI_DATA_FILE to a valid parquet file."
        )

    df = pd.read_parquet(DATA_FILE).copy()

    df.columns = [str(c).strip() for c in df.columns]

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df["process_id"] = pd.to_numeric(df["process_id"], errors="coerce").astype("Int64")
    df["segment_id"] = pd.to_numeric(df.get("segment_id", 0), errors="coerce").astype("Int64")

    df = df.dropna(subset=["process_id", "timestamp"])
    df["process_id"] = df["process_id"].astype(int)
    df["segment_id"] = df["segment_id"].fillna(0).astype(int)

    return df.sort_values(["process_id", "timestamp"], kind="stable").reset_index(drop=True)


DF = load_dataset()


def get_process_ids():
    return sorted(DF["process_id"].unique().tolist())


def get_process(process_id):
    process_df = DF[DF["process_id"] == int(process_id)].copy()
    process_df = process_df.sort_values("timestamp", kind="stable").reset_index(drop=True)

    if process_df.empty:
        return process_df

    start_time = process_df["timestamp"].iloc[0]
    process_df["elapsed_seconds"] = (process_df["timestamp"] - start_time).dt.total_seconds()

    # Brewing elapsed seconds:
    # - 0 before brewing
    # - counts from brew start during brewing
    # - keeps last brew value after brewing ends
    process_df["brew_elapsed_seconds"] = 0.0
    brew_mask = process_df["segment_id"] == 1

    if brew_mask.any():
        brew_start = process_df.loc[brew_mask, "timestamp"].iloc[0]
        brew_elapsed = (process_df.loc[brew_mask, "timestamp"] - brew_start).dt.total_seconds()
        process_df.loc[brew_mask, "brew_elapsed_seconds"] = brew_elapsed

        # Carry last brew elapsed forward after brewing ends.
        process_df["brew_elapsed_seconds"] = (
            process_df["brew_elapsed_seconds"]
            .where(process_df["brew_elapsed_seconds"] > 0)
            .ffill()
            .fillna(0)
            .astype(float)
        )

        first_brew_index = process_df.index[brew_mask][0]
        process_df.loc[:first_brew_index - 1, "brew_elapsed_seconds"] = 0.0

    return process_df


def get_process_type(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return "Unknown"

    # Important: if a process contains brewing at all, it is a Brewing process.
    # Do not classify it by dominant segment, because heating/idle can be longer.
    if (process_df["segment_id"] == 1).any():
        return "Brewing process"

    counts = process_df["segment_id"].value_counts()
    if counts.empty:
        return "Other"

    dominant_segment = int(counts.idxmax())
    return f"{segment_label(dominant_segment)} process"


def get_brew_window(process_id):
    process_df = get_process(process_id)

    if process_df.empty:
        return process_df

    return process_df[process_df["segment_id"] == 1].copy().reset_index(drop=True)


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

    segment_series = process_df["segment_id"].ffill().bfill()
    run_numbers = segment_series.ne(segment_series.shift()).fillna(True).cumsum()

    temp_df = process_df.copy()
    temp_df["_run"] = run_numbers

    segments = []
    for _, segment_df in temp_df.groupby("_run", sort=True):
        segment_id = int(segment_df["segment_id"].iloc[0])
        segments.append({
            "segment_id": segment_id,
            "label": segment_label(segment_id),
            "color": SEGMENT_COLORS.get(segment_id, "#999999"),
            "start": float(segment_df["elapsed_seconds"].iloc[0]),
            "end": float(segment_df["elapsed_seconds"].iloc[-1]),
        })

    return segments


def score_brew_metrics(temp_value, pressure_value, brew_duration):
    score = 100
    feedback = []

    if temp_value < TARGETS["temp_min"]:
        score -= 25
        feedback.append("Temperature is low. Allow more warm-up time or check temperature stability.")
    elif temp_value > TARGETS["temp_max"]:
        score -= 25
        feedback.append("Temperature is high. Consider a cooling flush or reduce overheating.")

    if pressure_value < TARGETS["pressure_min"]:
        score -= 30
        feedback.append("Pressure is low. Grind finer or increase puck resistance.")
    elif pressure_value > TARGETS["pressure_max"]:
        score -= 30
        feedback.append("Pressure is high. Grind coarser or reduce puck resistance.")

    if brew_duration < TARGETS["brew_min"]:
        score -= 20
        feedback.append("Extraction is too short. Grind finer or increase dose.")
    elif brew_duration > TARGETS["brew_max"]:
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
        "temperature_avg": round(temp_value, 2),
        "pressure_avg": round(pressure_value, 2),
        "brew_duration": round(brew_duration, 2),
        "note": "Rule-derived extraction quality, not human taste prediction.",
    }


def evaluate_process(process_id):
    brew_df = get_brew_window(process_id)

    if brew_df.empty:
        return {
            "quality_score": 0,
            "quality_label": "Invalid / Other",
            "feedback": ["No brewing segment found."],
            "brew_duration": 0,
            "note": "Rule-derived extraction quality, not human taste prediction.",
        }

    temp_avg = _safe_float(brew_df["temp"].mean()) if "temp" in brew_df.columns else 0
    pressure_avg = _safe_float(brew_df["pressure"].mean()) if "pressure" in brew_df.columns else 0
    brew_duration = get_brew_duration(process_id)

    return score_brew_metrics(temp_avg, pressure_avg, brew_duration)


def evaluate_live_reading(row):
    segment_id = int(row.get("segment_id", 1))

    # For Real Live, without full process context, score only brewing readings.
    if segment_id != 1:
        label = segment_label(segment_id)
        return {
            "quality_score": 0,
            "quality_label": f"{label} / Not a coffee shot",
            "feedback": [f"{label} segment detected. Extraction quality is only scored during brewing."],
            "brew_duration": 0,
            "note": "Rule-derived extraction quality, not human taste prediction.",
        }

    temp = _safe_float(row.get("temperature"))
    pressure = _safe_float(row.get("pressure"))
    brew_elapsed = _safe_float(row.get("brew_elapsed_seconds", row.get("elapsed_seconds", 0)))

    return score_brew_metrics(temp, pressure, brew_elapsed)


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
            "elapsed_seconds": _safe_float(row.get("elapsed_seconds")),
            "brew_elapsed_seconds": _safe_float(row.get("brew_elapsed_seconds", 0)),
            "segment_id": int(row["segment_id"]),
            "segment_label": segment_label(int(row["segment_id"])),
            "temperature": _safe_float(row.get("temp")),
            "pressure": _safe_float(row.get("pressure")),
            "flowRate": _safe_float(row.get("flowRate")),
            "totalVolume": _safe_float(row.get("totalVolume")),
        })

    return rows
