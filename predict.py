import joblib
import pandas as pd

saved = joblib.load("quality_model.pkl")

model = saved["model"]
label_encoder = saved["label_encoder"]
feature_columns = saved["feature_columns"]


LABEL_SCORE = {
    "Good extraction": 90,
    "Warning extraction": 55,
    "Poor extraction": 25,
}


def predict_quality(data):
    df = pd.DataFrame([data])

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    X = df[feature_columns]

    pred_encoded = model.predict(X)[0]
    pred_label = label_encoder.inverse_transform([pred_encoded])[0]

    confidence = 0
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[0]
        confidence = round(float(probabilities.max() * 100), 2)

    return {
        "quality_score": LABEL_SCORE.get(pred_label, 0),
        "quality_label": pred_label,
        "model_confidence": confidence,
        "note": "Rule-derived model, not human taste prediction."
    }