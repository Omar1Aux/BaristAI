from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from predict import predict_quality
from live_predict import live_prediction
from influx_writer import write_espresso_data 

app = Flask(__name__)
CORS(app)

# Load parquet files
sensor_data = pd.read_parquet("cleaned_rancilio_data.parquet")

metrics = pd.read_parquet("process_metrics.parquet").reset_index()
feedback = pd.read_parquet("process_feedback.parquet").reset_index()
quality = pd.read_parquet("process_quality_scores.parquet").reset_index()

segmented_data = pd.read_parquet("segmented_rancilio_data.parquet")

@app.route("/")
def home():
    return "BaristAI Backend is running!"


@app.route("/process/<int:process_id>")
def get_process(process_id):
    metric_row = metrics[metrics["process_id"] == process_id]
    feedback_row = feedback[feedback["process_id"] == process_id]
    quality_row = quality[quality["process_id"] == process_id]

    if metric_row.empty:
        return jsonify({"error": "Process ID not found"}), 404

    m = metric_row.iloc[0]

    result = {
        "process_id": process_id,
        "metrics": {
            "temperature": {
                "min": float(m["temp_min"]),
                "max": float(m["temp_max"]),
                "avg": float(m["temp_avg"]),
                "std": float(m["temp_std"]),
                "unit": "°C"
            },
            "pressure": {
                "min": float(m["pressure_min"]),
                "max": float(m["pressure_max"]),
                "avg": float(m["pressure_avg"]),
                "std": float(m["pressure_std"]),
                "unit": "bar"
            },
            "flowRate": {
                "unit": "relative sensor value",
                "min": float(m["flow_min"]),
                "max": float(m["flow_max"]),
                "avg": float(m["flow_avg"]),
                "std": float(m["flow_std"])
            },
            "duration_seconds": float(m["duration_seconds"]),
            "total_volume": float(m["total_volume"])
        }
    }

    if not feedback_row.empty:
        result["feedback"] = feedback_row.iloc[0]["feedback"]

    if not quality_row.empty:
        q = quality_row.iloc[0]
        result["quality"] = {
            "score": float(q["quality_score"]),
            "label": q["quality_label"],
            "notes": q["quality_notes"]
        }

    return jsonify(result)


@app.route("/process/<int:process_id>/timeseries")
def get_process_timeseries(process_id):
    process = sensor_data[sensor_data["process_id"] == process_id]

    if process.empty:
        return jsonify({"error": "Process ID not found"}), 404

    data = []

    for _, row in process.iterrows():
        data.append({
            "timestamp": str(row["timestamp"]),
            "temperature": float(row["temp"]),
            "pressure": float(row["pressure"]),
            "flowRate": float(row["flowRate"])
        })

    return jsonify({
        "process_id": process_id,
        "flowRate_unit": "relative sensor value",
        "data": data
    })


@app.route("/dashboard/<int:process_id>")
def get_dashboard_data(process_id):
    metric_row = metrics[metrics["process_id"] == process_id]
    feedback_row = feedback[feedback["process_id"] == process_id]
    quality_row = quality[quality["process_id"] == process_id]
    process = sensor_data[sensor_data["process_id"] == process_id]

    if metric_row.empty:
        return jsonify({"error": "Process ID not found"}), 404

    m = metric_row.iloc[0]

    dashboard_data = {
        "process_id": process_id,

        "cards": {
            "temperature": {
                "current": float(process["temp"].iloc[-1]) if not process.empty else None,
                "max": float(m["temp_max"]),
                "avg": float(m["temp_avg"]),
                "unit": "°C"
            },
            "pressure": {
                "current": float(process["pressure"].iloc[-1]) if not process.empty else None,
                "max": float(m["pressure_max"]),
                "avg": float(m["pressure_avg"]),
                "unit": "bar"
            },
            "flowRate": {
                "current": float(process["flowRate"].iloc[-1]) if not process.empty else None,
                "max": float(m["flow_max"]),
                "avg": float(m["flow_avg"]),
                "unit": "relative sensor value"
            },
            "total_volume": {
                "value": float(m["total_volume"])
            },
            "duration": {
                "seconds": float(m["duration_seconds"])
            }
        },

        "feedback": feedback_row.iloc[0]["feedback"] if not feedback_row.empty else None,

        "quality": {
            "score": float(quality_row.iloc[0]["quality_score"]) if not quality_row.empty else None,
            "label": quality_row.iloc[0]["quality_label"] if not quality_row.empty else None,
            "notes": quality_row.iloc[0]["quality_notes"] if not quality_row.empty else None
        },

        "timeseries": [
            {
                "timestamp": str(row["timestamp"]),
                "temperature": float(row["temp"]),
                "pressure": float(row["pressure"]),
                "flowRate": float(row["flowRate"])
            }
            for _, row in process.iterrows()
        ]
    }

    return jsonify(dashboard_data)


@app.route("/processes")
def get_all_processes():
    process_ids = metrics["process_id"].tolist()

    return jsonify({
        "total_processes": len(process_ids),
        "process_ids": process_ids
    })


@app.route("/summary")
def get_summary():
    return jsonify({
        "total_processes": int(len(metrics)),
        "average_temperature": float(metrics["temp_avg"].mean()),
        "average_pressure": float(metrics["pressure_avg"].mean()),
        "average_flowRate": float(metrics["flow_avg"].mean()),
        "flowRate_unit": "relative sensor value",
        "average_quality_score": float(quality["quality_score"].mean())
    })


@app.route("/best-process")
def get_best_process():
    best_row = quality.loc[quality["quality_score"].idxmax()]
    process_id = int(best_row["process_id"])
    return get_process(process_id)


@app.route("/worst-process")
def get_worst_process():
    worst_row = quality.loc[quality["quality_score"].idxmin()]
    process_id = int(worst_row["process_id"])
    return get_process(process_id)


@app.route("/feedback/<int:process_id>")
def get_feedback(process_id):
    feedback_row = feedback[feedback["process_id"] == process_id]

    if feedback_row.empty:
        return jsonify({"error": "Process ID not found"}), 404

    return jsonify({
        "process_id": process_id,
        "feedback": feedback_row.iloc[0]["feedback"]
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
@app.route("/live/<int:process_id>")
def get_live_data(process_id):
    process = sensor_data[sensor_data["process_id"] == process_id]

    if process.empty:
        return jsonify({"error": "Process ID not found"}), 404

    latest = process.iloc[-1]

    return jsonify({
        "process_id": process_id,
        "timestamp": str(latest["timestamp"]),
        "temperature": float(latest["temp"]),
        "pressure": float(latest["pressure"]),
        "flowRate": float(latest["flowRate"]),
        "flowRate_unit": "relative sensor value"
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    result = predict_quality(data)
    return jsonify(result)


@app.route("/predict/process/<int:process_id>")
def predict_existing_process(process_id):
    metric_row = metrics[metrics["process_id"] == process_id]

    if metric_row.empty:
        return jsonify({"error": "Process ID not found"}), 404

    m = metric_row.iloc[0]

    data = {
        "temp_avg": float(m["temp_avg"]),
        "temp_max": float(m["temp_max"]),
        "temp_std": float(m["temp_std"]),
        "pressure_avg": float(m["pressure_avg"]),
        "pressure_max": float(m["pressure_max"]),
        "pressure_std": float(m["pressure_std"]),
        "flow_avg": float(m["flow_avg"]),
        "flow_max": float(m["flow_max"]),
        "flow_std": float(m["flow_std"]),
        "duration_seconds": float(m["duration_seconds"]),
        "total_volume": float(m["total_volume"])
    }

    prediction = predict_quality(data)

    return jsonify({
        "process_id": process_id,
        "prediction": prediction
    })


live_counter = {}

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

    temp = round(float(current_row["temp"]), 2)
    pressure = round(float(current_row["pressure"]), 2)
    flow_rate = round(float(current_row["flowRate"]), 2)
    quality_score = round(float(prediction["quality_score"]), 2)

    try:
        write_espresso_data(
            process_id,
            temp,
            pressure,
            flow_rate,
            quality_score
        )
    except Exception as e:
        print("InfluxDB write error:", e)

    return jsonify({
        "process_id": process_id,
        "temperature": {
            "current": temp,
            "avg": round(float(current_slice["temp"].mean()), 2)
        },
        "pressure": {
            "current": pressure,
            "avg": round(float(current_slice["pressure"].mean()), 2)
        },
        "flowRate": {
            "current": flow_rate,
            "avg": round(float(current_slice["flowRate"].mean()), 2),
            "unit": "relative sensor value"
        },
        "prediction": {
            "quality_score": quality_score,
            "quality_label": prediction["quality_label"]
        }
    })

if __name__ == "__main__":
    app.run(debug=True)