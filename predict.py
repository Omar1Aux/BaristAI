import joblib
import pandas as pd

saved = joblib.load("quality_model.pkl")

model = saved["model"]
label_encoder = saved["label_encoder"]
feature_columns = saved["feature_columns"]


LABEL_SCORE = {
    "Poor extraction": 25,
    "Warning extraction": 55,
    "Extraction warning": 55,
    "Good extraction": 90,
    "Excellent extraction": 95
}


def predict_quality(data):
    df = pd.DataFrame([data])

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    X = df[feature_columns]

    prediction_encoded = model.predict(X)[0]
    prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

    probabilities = model.predict_proba(X)[0]
    model_confidence = round(float(probabilities.max() * 100), 2)

    quality_score = LABEL_SCORE.get(prediction_label, model_confidence)

    return {
        "quality_score": quality_score,
        "quality_label": prediction_label,
        "model_confidence": model_confidence
    }