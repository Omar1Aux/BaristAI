import joblib
import pandas as pd

# Load trained model
model = joblib.load("quality_model.pkl")

features = [
    "temp_avg",
    "temp_max",
    "temp_std",
    "pressure_avg",
    "pressure_max",
    "pressure_std",
    "flow_avg",
    "flow_max",
    "flow_std",
    "duration_seconds",
    "total_volume"
]

def predict_quality(data):

    df = pd.DataFrame([data])

    prediction = model.predict(df[features])[0]

    if prediction >= 80:
        label = "Excellent extraction"
    elif prediction >= 60:
        label = "Good extraction"
    elif prediction >= 40:
        label = "Average extraction"
    else:
        label = "Poor extraction"

    return {
        "quality_score": round(float(prediction),2),
        "quality_label": label
    }