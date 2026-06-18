import joblib
import pandas as pd

# Load saved objects
saved = joblib.load("quality_model.pkl")

model = saved["model"]
label_encoder = saved["label_encoder"]
feature_columns = saved["feature_columns"]


def predict_quality(data):

    df = pd.DataFrame([data])

    # Keep feature order consistent
    X = df[feature_columns]

    # Prediction
    prediction_encoded = model.predict(X)[0]
    prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

    # Confidence score
    probabilities = model.predict_proba(X)[0]
    confidence = round(float(probabilities.max() * 100), 2)

    return {
        "quality_score": confidence,
        "quality_label": prediction_label
    }