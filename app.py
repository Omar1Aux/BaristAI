from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json
import time
from pathlib import Path

from core.data_engine import (
    get_process_ids,
    get_process,
    get_process_summary,
    get_timeseries,
    evaluate_process,
)

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent

latest_live_data = None
live_history = []


def dashboard_payload(row, evaluation):
    return {
        "process_id": row.get("process_id"),
        "process_type": row.get("segment_label", "Unknown"),
        "segment_id": row.get("segment_id"),
        "segment_label": row.get("segment_label", "Unknown"),
        "elapsed_seconds": row.get("elapsed_seconds", 0),
        "temperature": {
            "current": round(row.get("temperature", 0), 2)
        },
        "pressure": {
            "current": round(row.get("pressure", 0), 2)
        },
        "extractionTime": {
            "current": round(row.get("elapsed_seconds", 0), 2),
            "unit": "s"
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
    evaluation = evaluate_process(process_id)

    if not rows:
        return jsonify({"error": "Process not found"}), 404

    def generate():
        global latest_live_data, live_history

        for row in rows:
            payload = dashboard_payload(row, evaluation)

            latest_live_data = payload
            live_history.append(payload)
            live_history = live_history[-100:]

            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )


@app.route("/api/live/reading", methods=["POST"])
def api_live_reading():
    global latest_live_data, live_history

    data = request.json or {}

    row = {
        "process_id": int(data.get("process_id", 0)),
        "segment_id": int(data.get("segment_id", 1)),
        "segment_label": data.get("segment_label", "Live"),
        "elapsed_seconds": float(data.get("elapsed_seconds", data.get("time", 0))),
        "temperature": float(data.get("temp", data.get("temperature", 0))),
        "pressure": float(data.get("pressure", 0)),
        "flowRate": float(data.get("flowRate", 0)),
        "totalVolume": float(data.get("totalVolume", 0)),
    }

    evaluation = {
        "quality_score": float(data.get("quality_score", 0)),
        "quality_label": data.get("quality_label", "Live reading"),
        "feedback": data.get("feedback", ["Live data received."])
    }

    latest_live_data = dashboard_payload(row, evaluation)
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

            time.sleep(1)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
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
    evaluation = evaluate_process(process_id)

    if not rows:
        return jsonify({"error": "Process not found"}), 404

    row = rows[0]
    return jsonify(dashboard_payload(row, evaluation))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)