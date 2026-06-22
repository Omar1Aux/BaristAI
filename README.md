# BaristAI

**BaristAI** is a process-aware espresso monitoring dashboard.

It analyzes espresso machine process data using `process_id` and `segment_id`, streams historical readings from the Flask backend, provides rule-based extraction feedback, and is prepared for future real-time integration using MQTT and ESP32 devices.

---

## Project Idea

The goal of BaristAI is to transform raw espresso machine sensor data into useful visual feedback.

Instead of treating every process as a coffee shot, BaristAI understands that one `process_id` represents one machine process, which may be:

- Brewing
- Flushing
- Steam
- Heating
- Idle
- Invalid / Other

This makes the project process-aware and closer to real espresso machine behavior.

---

## Key Features

- Process-aware dashboard
- Uses `process_id` as the main identifier
- Uses `segment_id` to understand process phases
- Calculates real brew/extraction duration from the brewing segment
- Server-side streaming using Server-Sent Events
- Historical process simulation from backend
- MQTT-ready live data pipeline
- Rule-based espresso feedback
- Rule-derived machine learning model
- Temperature, pressure, and extraction time monitoring
- Segment-colored pressure and temperature chart
- Clean Flask backend and vanilla HTML/CSS/JavaScript frontend

---

## Process and Segment Meaning

Each `process_id` is a unique machine process.

Not every process is a coffee extraction.

`segment_id` meaning:

| segment_id | Meaning |
|---|---|
| 1 | Brewing |
| 2 | Flushing |
| 3 | Steam |
| 4 | Heating |
| 5 | Idle |

The dashboard visualizes one process at a time and colors the chart based on these segments.

---

## Data Source

The main dataset is stored as a Parquet file inside the `data/` folder.

The backend reads the dataset through:

```text
core/data_engine.py