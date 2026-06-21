from pathlib import Path
import sys
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.data_engine import get_process_ids, get_brew_window, get_brew_duration

MODEL_ROOT = BASE_DIR / "quality_model.pkl"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_MODELS = MODEL_DIR / "quality_model.pkl"

OUTPUT_DATA = BASE_DIR / "data" / "ai_training_process_aware.csv"
COMPARISON_FILE = BASE_DIR / "data" / "model_comparison_process_aware.csv"


FEATURE_COLUMNS = [
    "brew_duration",
    "temp_avg",
    "temp_min",
    "temp_max",
    "temp_std",
    "pressure_avg",
    "pressure_min",
    "pressure_max",
    "pressure_std",
    "volume_delta",
    "preinfusion",
    "preinfusionpause",
    "setPoint",
]


def safe_value(df, column, default=0):
    if column not in df.columns or df.empty:
        return default
    value = df[column].iloc[0]
    return 0 if pd.isna(value) else float(value)


def create_features(process_id):
    brew = get_brew_window(process_id)

    if brew.empty or len(brew) < 5:
        return None

    brew_duration = get_brew_duration(process_id)
    volume_delta = 0

    if "totalVolume" in brew.columns:
        volume_delta = float(brew["totalVolume"].max() - brew["totalVolume"].min())

    return {
        "process_id": process_id,
        "brew_duration": brew_duration,

        "temp_avg": float(brew["temp"].mean()) if "temp" in brew.columns else 0,
        "temp_min": float(brew["temp"].min()) if "temp" in brew.columns else 0,
        "temp_max": float(brew["temp"].max()) if "temp" in brew.columns else 0,
        "temp_std": float(brew["temp"].std()) if "temp" in brew.columns else 0,

        "pressure_avg": float(brew["pressure"].mean()) if "pressure" in brew.columns else 0,
        "pressure_min": float(brew["pressure"].min()) if "pressure" in brew.columns else 0,
        "pressure_max": float(brew["pressure"].max()) if "pressure" in brew.columns else 0,
        "pressure_std": float(brew["pressure"].std()) if "pressure" in brew.columns else 0,

        "volume_delta": volume_delta,

        "preinfusion": safe_value(brew, "preinfusion"),
        "preinfusionpause": safe_value(brew, "preinfusionpause"),
        "setPoint": safe_value(brew, "setPoint", 90),
    }


def calculate_quality_score(row):
    score = 100

    # Temperature target
    if row["temp_avg"] < 90:
        score -= 25
    elif row["temp_avg"] > 96:
        score -= 25

    # Pressure target
    if row["pressure_avg"] < 8.5:
        score -= 30
    elif row["pressure_avg"] > 10.5:
        score -= 30

    # Brew duration target
    if row["brew_duration"] < 25:
        score -= 20
    elif row["brew_duration"] > 30:
        score -= 20

    # Stability
    if row["pressure_std"] > 3:
        score -= 10

    return max(0, min(100, score))


def quality_label(score):
    if score >= 75:
        return "Good extraction"
    elif score >= 45:
        return "Warning extraction"
    else:
        return "Poor extraction"


rows = []

for process_id in get_process_ids():
    features = create_features(process_id)
    if features is not None:
        rows.append(features)

df = pd.DataFrame(rows)

df["quality_score_rule"] = df.apply(calculate_quality_score, axis=1)
df["quality_label"] = df["quality_score_rule"].apply(quality_label)

df.to_csv(OUTPUT_DATA, index=False)

print("Training dataset created")
print("Rows:", len(df))
print("\nLabel distribution:")
print(df["quality_label"].value_counts())

X = df[FEATURE_COLUMNS]
y = df["quality_label"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

stratify_value = y_encoded if df["quality_label"].value_counts().min() >= 2 else None

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=stratify_value
)

models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=5000, class_weight="balanced"))
    ]),
    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    ),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42)
}

results = []
best_model = None
best_name = None
best_f1 = -1

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    accuracy = accuracy_score(y_test, preds)
    precision = precision_score(y_test, preds, average="weighted", zero_division=0)
    recall = recall_score(y_test, preds, average="weighted", zero_division=0)
    f1 = f1_score(y_test, preds, average="weighted", zero_division=0)

    results.append({
        "model": name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    })

    print("\n==============================")
    print(name)
    print("==============================")
    print("Accuracy :", round(accuracy, 3))
    print("Precision:", round(precision, 3))
    print("Recall   :", round(recall, 3))
    print("F1-score :", round(f1, 3))

    print(classification_report(
        y_test,
        preds,
        labels=list(range(len(label_encoder.classes_))),
        target_names=label_encoder.classes_,
        zero_division=0
    ))

    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_name = name

pd.DataFrame(results).to_csv(COMPARISON_FILE, index=False)

saved_object = {
    "model": best_model,
    "model_name": best_name,
    "label_encoder": label_encoder,
    "feature_columns": FEATURE_COLUMNS,
    "note": "Rule-derived labels, not human taste labels."
}

joblib.dump(saved_object, MODEL_ROOT)
joblib.dump(saved_object, MODEL_MODELS)

print("\n==============================")
print("Best Model:", best_name)
print("Best F1-score:", round(best_f1, 3))
print("Saved:", MODEL_ROOT)
print("Saved:", MODEL_MODELS)