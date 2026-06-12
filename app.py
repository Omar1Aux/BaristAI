from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from predict import predict_quality
from live_predict import live_prediction
from influx_writer import write_espresso_data

app = Flask(__name__)
CORS(app)

sensor_data = pd.read_parquet("cleaned_rancilio_data.parquet")
segmented_data = pd.read_parquet("segmented_rancilio_data.parquet")
metrics = pd.read_parquet("process_metrics.parquet").reset_index()
quality = pd.read_parquet("process_quality_scores.parquet").reset_index()
feedback = pd.read_parquet("process_feedback.parquet").reset_index()

live_counter = {}


@app.route("/")
def home():
    return "BaristAI Backend is running!"


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    result = predict_quality(data)
    return jsonify(result)


@app.route("/live/predict/<int:process_id>")
def live_predict_endpoint(process_id):
    process_data = segmented_data[
        segmented_data["process_id"] == process_id
    ].reset_index(drop=True)

    if process_data.empty:
        return jsonify({"error": "Process ID not found"}), 404

    index = live_counter.get(process_id, 0)

    if index >= len(process_data):
        index = 0

    current_row = process_data.iloc[index]
    current_slice = process_data.iloc[:index + 1]

    live_counter[process_id] = index + 1

    prediction = live_prediction(current_slice)

    temperature = round(float(current_row["temp"]), 2)
    pressure = round(float(current_row["pressure"]), 2)
    extraction_time = index + 1
    quality_score = round(float(prediction["quality_score"]), 2)
    quality_label = prediction["quality_label"]

    try:
        write_espresso_data(
            process_id,
            temperature,
            pressure,
            extraction_time,
            quality_score
        )
    except Exception as e:
        print("InfluxDB write error:", e)

    return jsonify({
        "process_id": process_id,

        "temperature": {
            "current": temperature,
            "avg": round(float(current_slice["temp"].mean()), 2)
        },

        "pressure": {
            "current": pressure,
            "avg": round(float(current_slice["pressure"].mean()), 2)
        },

        "extractionTime": {
            "current": extraction_time,
            "unit": "s"
        },

        "prediction": {
            "quality_score": quality_score,
            "quality_label": quality_label
        }
    })


@app.route("/processes")
def get_processes():
    return jsonify({
        "process_ids": sorted(segmented_data["process_id"].unique().tolist())
    })


@app.route("/quality/<int:process_id>")
def get_quality(process_id):
    quality_row = quality[quality["process_id"] == process_id]

    if quality_row.empty:
        return jsonify({"error": "Process ID not found"}), 404

    q = quality_row.iloc[0]

    return jsonify({
        "process_id": process_id,
        "quality_score": float(q["quality_score"]),
        "quality_label": q["quality_label"],
        "quality_notes": q["quality_notes"]
    })


if __name__ == "__main__":
    app.run(debug=True)