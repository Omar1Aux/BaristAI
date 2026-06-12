import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# Load data
df = pd.read_parquet("process_metrics.parquet").reset_index()
quality = pd.read_parquet("process_quality_scores.parquet").reset_index()

# Merge metrics with quality score
data = df.merge(
    quality[["process_id", "quality_score"]],
    on="process_id"
)

# Features
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

X = data[features]
y = data["quality_score"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluation
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("Model trained successfully!")
print(f"MAE: {mae:.2f}")
print(f"R2 Score: {r2:.2f}")

# Save model
joblib.dump(model, "quality_model.pkl")

print("Saved model as quality_model.pkl")