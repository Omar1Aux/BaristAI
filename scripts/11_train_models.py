import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


DATA_PATH = "data/ai_training_dataset.parquet"
MODEL_OUTPUT = "quality_model.pkl"

df = pd.read_parquet(DATA_PATH)

feature_columns = [
    "duration",
    "volume_delta",
    "temp_avg",
    "temp_min",
    "temp_max",
    "temp_std",
    "pressure_avg",
    "pressure_min",
    "pressure_max",
    "pressure_std",
    "flow_avg",
    "flow_min",
    "flow_max",
    "flow_std",
    "preinfusion",
    "preinfusionpause",
    "setPoint",
]

X = df[feature_columns]
y = df["quality_label"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
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

    "Gradient Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

results = []

best_model = None
best_model_name = None
best_f1 = -1

labels = list(range(len(label_encoder.classes_)))

for name, model in models.items():
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
    recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
    f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)

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
    print()
    print(classification_report(
        y_test,
        predictions,
        labels=labels,
        target_names=label_encoder.classes_,
        zero_division=0
    ))

    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

results_df = pd.DataFrame(results)
results_df.to_csv("data/model_comparison.csv", index=False)

joblib.dump({
    "model": best_model,
    "model_name": best_model_name,
    "label_encoder": label_encoder,
    "feature_columns": feature_columns
}, MODEL_OUTPUT)

print("\n==============================")
print("Best Model:", best_model_name)
print("Best F1-score:", round(best_f1, 3))
print("Saved model to:", MODEL_OUTPUT)
print("Saved comparison to: data/model_comparison.csv")