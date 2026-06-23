from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json
import time
from pathlib import Path

from core.data_engine import (
    get_process_ids,
    get_process_summary,
    get_timeseries,
    evaluate_live_reading as evaluate_current_reading,
)

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

latest_live_data = None
live_history = []


def dashboard_payload(row, evaluation, use_evaluation_metrics=False):
    temperature_current = row.get("temperature", 0)
    pressure_current = row.get("pressure", 0)
    extraction_current = row.get("brew_elapsed_seconds", 0)

    if use_evaluation_metrics:
        temperature_current = evaluation.get("temperature_avg", temperature_current)
        pressure_current = evaluation.get("pressure_avg", pressure_current)
        extraction_current = evaluation.get("brew_duration", extraction_current)

    return {
        "process_id": row.get("process_id"),
        "process_type": row.get("process_type", row.get("segment_label", "Live")),
        "segment_id": row.get("segment_id"),
        "segment_label": row.get("segment_label", "Unknown"),
        "elapsed_seconds": row.get("elapsed_seconds", 0),
        "temperature": {
            "current": round(temperature_current, 2)
        },
        "pressure": {
            "current": round(pressure_current, 2)
        },
        "extractionTime": {
            "current": round(extraction_current, 2),
            "unit": "s",
            "source": "brewing segment only"
        },
        "flowRate": {
            "current": round(row.get("flowRate", 0), 2),
            "unit": "ml/s",
            "display_only": True
        },
        "reading": {
            "temperature": round(row.get("temperature", 0), 2),
            "pressure": round(row.get("pressure", 0), 2)
        },
        "prediction": {
            "quality_score": evaluation.get("quality_score", 0),
            "quality_label": evaluation.get("quality_label", "Unknown"),
            "feedback": evaluation.get("feedback", [])
        }
    }


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


@app.route("/processes")
def legacy_processes():
    return jsonify({"process_ids": get_process_ids()})


@app.route("/api/process_ids")
def api_process_ids():
    return jsonify({"process_ids": get_process_ids()})


@app.route("/api/process/<int:process_id>/summary")
def api_process_summary(process_id):
    summary = get_process_summary(process_id)

    if summary is None:
        return jsonify({"error": "Process not found"}), 404

    return jsonify(summary)


@app.route("/api/process/<int:process_id>/timeseries")
def api_process_timeseries(process_id):
    rows = get_timeseries(process_id)

    if not rows:
        return jsonify({"error": "Process not found"}), 404

    return jsonify(rows)


@app.route("/api/process/<int:process_id>/stream")
def api_process_stream(process_id):
    rows = get_timeseries(process_id)
    summary = get_process_summary(process_id)
    if not rows:
        return jsonify({"error": "Process not found"}), 404

    process_type = summary.get("process_type", "Unknown") if summary else "Unknown"
    process_evaluation = evaluate_process(process_id)
    use_process_evaluation = process_type == "Brewing process"

    def generate():
        global latest_live_data, live_history

        for row in rows:
            row["process_type"] = process_type
            evaluation = process_evaluation if use_process_evaluation else evaluate_current_reading(row)
            payload = dashboard_payload(row, evaluation)

            latest_live_data = payload
            live_history.append(payload)
            live_history = live_history[-100:]

            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/live/reading", methods=["POST"])
def api_live_reading():
    global latest_live_data, live_history

    data = request.json or {}

    segment_id = int(data.get("segment_id", 1))

    segment_labels = {
        1: "Brewing",
        2: "Flushing",
        3: "Steam",
        4: "Heating",
        5: "Idle"
    }

    row = {
        "process_id": int(data.get("process_id", 0)),
        "segment_id": segment_id,
        "segment_label": segment_labels.get(segment_id, "Live"),
        "process_type": "Live",
        "elapsed_seconds": float(data.get("elapsed_seconds", data.get("time", 0))),
        "temperature": float(data.get("temp", data.get("temperature", 0))),
        "pressure": float(data.get("pressure", 0)),
        "flowRate": float(data.get("flowRate", 0)),
        "totalVolume": float(data.get("totalVolume", 0)),
    }

    row["brew_elapsed_seconds"] = row["elapsed_seconds"] if row["segment_id"] == 1 else 0
    evaluation = evaluate_current_reading(row)

    latest_live_data = dashboard_payload(row, evaluation)
    app.logger.info(
        "Stored live reading process_id=%s segment_id=%s temp=%.2f pressure=%.2f elapsed=%.2f",
        row["process_id"], row["segment_id"], row["temperature"], row["pressure"], row["elapsed_seconds"]
    )
    live_history.append(latest_live_data)
    live_history = live_history[-100:]

    return jsonify({"status": "ok", "latest": latest_live_data})


@app.route("/api/live/status")
def api_live_status():
    return jsonify({
        "has_live_data": latest_live_data is not None,
        "latest": latest_live_data,
        "history_size": len(live_history)
    })


@app.route("/api/live/reset", methods=["POST"])
def api_live_reset():
    global latest_live_data, live_history

    latest_live_data = None
    live_history = []

    return jsonify({"status": "reset"})


@app.route("/api/live/stream")
def api_live_stream():
    def generate():
        last_payload = None

        while True:
            if latest_live_data is not None and latest_live_data != last_payload:
                last_payload = latest_live_data
                yield f"data: {json.dumps(latest_live_data)}\n\n"
            else:
                yield ": waiting for live data\n\n"

            time.sleep(1)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/influx/live")
def legacy_live():
    if latest_live_data is None:
        return jsonify({"error": "No live data yet"}), 404

    return jsonify(latest_live_data)


@app.route("/history")
def legacy_history():
    return jsonify(live_history[-30:])


@app.route("/live/predict/<int:process_id>")
def legacy_live_predict(process_id):
    rows = get_timeseries(process_id)
    if not rows:
        return jsonify({"error": "Process not found"}), 404

    row = rows[0]
    return jsonify(dashboard_payload(row, evaluate_current_reading(row)))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)