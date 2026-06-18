from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import subprocess
import csv
from io import StringIO

from predict import predict_quality
from live_predict import live_prediction
from influx_writer import write_espresso_data

app = Flask(__name__)
CORS(app)

INFLUX_PATH = r"C:\BaristAI\influxdb3-core-3.9.3-windows_amd64\influxdb3.exe"
DATABASE = "baristai"
MEASUREMENT = "espresso"
HISTORY_LIMIT = 30

segmented_data = pd.read_parquet("data/segmented_rancilio_data.parquet")
metrics = pd.read_parquet("data/process_metrics.parquet").reset_index()
quality = pd.read_parquet("data/process_quality_scores.parquet").reset_index()
feedback = pd.read_parquet("data/process_feedback.parquet").reset_index()

live_counter = {}


def query_influx(sql):
    command = [
        INFLUX_PATH,
        "query",
        "--database",
        DATABASE,
        "--format",
        "csv",
        sql
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)

    reader = csv.DictReader(StringIO(result.stdout))
    return list(reader)


def format_influx_row(row):
    return {
        "time": row.get("time"),
        "process_id": int(float(row.get("process_id", 1))),
        "temperature": {
            "current": round(float(row.get("temperature", 0)), 2)
        },
        "pressure": {
            "current": round(float(row.get("pressure", 0)), 2)
        },
        "extractionTime": {
            "current": round(float(row.get("extraction_time", 0)), 2),
            "unit": "s"
        },
        "prediction": {
            "quality_score": round(float(row.get("quality_score", 0)), 2),
            "quality_label": quality_label_from_score(
                float(row.get("quality_score", 0))
            )
        }
    }


def quality_label_from_score(score):
    if score >= 70:
        return "Good extraction"
    if score >= 40:
        return "Extraction warning"
    return "Poor extraction"


@app.route("/")
def home():
    return send_from_directory(".", "dashboard.html")


@app.route("/dashboard.js")
def dashboard_js():
    return send_from_directory(".", "dashboard.js")


@app.route("/style.css")
def style_css():
    return send_from_directory(".", "style.css")


@app.route("/coffee-bg.png")
def coffee_bg():
    return send_from_directory(".", "coffee-bg.png")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    result = predict_quality(data)
    return jsonify(result)


@app.route("/influx/live")
def influx_live():
    try:
        sql = f"""
        SELECT time, process_id, temperature, pressure, extraction_time, quality_score
        FROM {MEASUREMENT}
        ORDER BY time DESC
        LIMIT 1
        """

        rows = query_influx(sql)

        if not rows:
            return jsonify({"error": "No InfluxDB data found"}), 404

        return jsonify(format_influx_row(rows[0]))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history")
def history():
    try:
        sql = f"""
        SELECT time, process_id, temperature, pressure, extraction_time, quality_score
        FROM {MEASUREMENT}
        ORDER BY time DESC
        LIMIT {HISTORY_LIMIT}
        """

        rows = query_influx(sql)
        rows.reverse()

        return jsonify([format_influx_row(row) for row in rows])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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