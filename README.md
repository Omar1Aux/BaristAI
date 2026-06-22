# ☕ BaristAI

## Process-Aware Espresso Monitoring Platform

BaristAI is a process-aware espresso monitoring system that transforms raw espresso machine sensor data into meaningful insights, visual analytics, and actionable extraction feedback.

The project combines:

* Data Engineering
* Process Analysis
* Machine Learning
* Server-Side Streaming
* Dashboard Visualization
* MQTT / IoT Integration

---

# 📸 Dashboard Preview

> Add a screenshot of the final dashboard here.

```text
BaristAI Dashboard
├── Temperature Monitoring
├── Pressure Monitoring
├── Extraction Time Analysis
├── Process Classification
├── Rule-Based Feedback
├── Historical Streaming
└── MQTT Live Monitoring
```

---

# 🎯 Project Goal

Espresso machines generate thousands of sensor readings during operation.

These readings contain valuable information about:

* Temperature
* Pressure
* Flow
* Volume
* Machine State

However, raw sensor data is difficult to interpret.

BaristAI converts raw machine telemetry into a process-aware monitoring platform capable of:

* Understanding machine processes
* Detecting brewing windows
* Evaluating extraction quality
* Providing recommendations
* Supporting future real-time deployment

---

# 🚀 Key Features

## Process-Aware Monitoring

Unlike traditional approaches, BaristAI does not assume that every process is a coffee extraction.

A machine process can be:

* Brewing
* Heating
* Flushing
* Steam
* Idle

Each process is identified using:

```text
process_id
```

---

## Segment-Based Analysis

Each process contains one or more machine segments.

Segment definitions:

| Segment ID | Meaning  |
| ---------- | -------- |
| 1          | Brewing  |
| 2          | Flushing |
| 3          | Steam    |
| 4          | Heating  |
| 5          | Idle     |

This allows BaristAI to understand machine behavior and extract the actual brewing phase.

---

## Accurate Brew Window Detection

BaristAI separates:

```text
Process Duration
```

from

```text
Brew Duration
```

Instead of measuring the entire process, the system extracts the actual brewing window using:

```python
segment_id == 1
```

This produces more realistic extraction metrics.

---

# 📊 Dataset

The project uses historical espresso machine data stored in Parquet format.

Main information includes:

* process_id
* segment_id
* timestamp
* temperature
* pressure
* totalVolume
* flowRate
* machine settings

---

# 🧹 Data Engineering Pipeline

The raw dataset passes through multiple preprocessing stages.

```text
Raw Data
    ↓
Data Validation
    ↓
Process Summary
    ↓
Filtering
    ↓
Brew Window Extraction
    ↓
Feature Engineering
    ↓
Machine Learning Dataset
```

---

# 📂 Data Processing Scripts

| Script                           | Purpose               |
| -------------------------------- | --------------------- |
| 01_data_check.py                 | Dataset inspection    |
| 02_process_summary.py            | Process statistics    |
| 03_plot_all_processes.py         | Process visualization |
| 06_filter_clean_shots.py         | Process filtering     |
| 07_filter_clean_shots_v2.py      | Improved filtering    |
| 08_extract_clean_brew_windows.py | Brew extraction       |
| 09_build_ai_features.py          | Feature engineering   |
| train_process_aware_model.py     | Model training        |

---

# 🏗️ System Architecture

## Historical Data Flow

```text
Parquet Dataset
        ↓
Data Engine
        ↓
Flask Backend
        ↓
SSE Streaming
        ↓
Dashboard
```

---

## Live Data Flow

```text
ESP32
        ↓
MQTT Broker
        ↓
MQTT Listener
        ↓
Flask Backend
        ↓
Live Stream
        ↓
Dashboard
```

---

# 🌐 Server-Side Streaming

Historical processes are streamed from the backend using:

```text
Server-Sent Events (SSE)
```

The server sends one reading at a time to simulate a real espresso process.

API:

```http
GET /api/process/<process_id>/stream
```

---

# 🔌 MQTT Integration

BaristAI is designed for future real-time deployment.

Supported environment variables:

```env
MQTT_ENABLED=true
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=espresso/data
MQTT_USERNAME=
MQTT_PASSWORD=
```

---

# 🤖 Machine Learning

## Important Note

The current model does **not** predict coffee taste.

Human sensory labels are not available.

Instead, the model learns:

```text
Rule-Derived Extraction Quality
```

based on engineering targets.

---

## Features

The model uses:

* Average Temperature
* Temperature Std
* Average Pressure
* Pressure Std
* Brew Duration
* Volume Delta
* Preinfusion Settings
* Machine Setpoints

---

## Models Evaluated

| Model               | Purpose     |
| ------------------- | ----------- |
| Logistic Regression | Baseline    |
| Random Forest       | Ensemble    |
| Gradient Boosting   | Final Model |

Selected model:

```text
Gradient Boosting
```

Stored as:

```text
quality_model.pkl
```

---

# 📋 Rule-Based Feedback

Target ranges:

| Metric          | Target       |
| --------------- | ------------ |
| Temperature     | 90–96 °C     |
| Pressure        | 8.5–10.5 bar |
| Extraction Time | 25–30 sec    |

---

## Example Recommendations

### Pressure Too High

```text
Grind coarser
Reduce puck resistance
```

### Pressure Too Low

```text
Grind finer
Increase resistance
```

### Temperature Too Low

```text
Allow more warm-up time
Check stability
```

### Temperature Too High

```text
Cooling flush
Reduce overheating
```

### Extraction Too Short

```text
Increase resistance
Increase dose
```

### Extraction Too Long

```text
Reduce resistance
Reduce dose
```

---

# 📈 Dashboard Components

The dashboard includes:

* Process Selector
* Simulate Live Mode
* Real Live Mode
* Temperature Card
* Pressure Card
* Extraction Time Card
* Feedback Panel
* Status Panel
* Dual-Axis Extraction Chart
* Segment-Aware Visualization

---

# 🛠️ Technology Stack

## Backend

* Python
* Flask
* Flask-CORS

## Data Engineering

* Pandas
* PyArrow

## Machine Learning

* Scikit-Learn
* Joblib

## Communication

* MQTT
* Server-Sent Events

## Frontend

* HTML
* CSS
* JavaScript
* Chart.js

---

# 📡 API Endpoints

## Process APIs

```http
GET /api/process_ids
```

```http
GET /api/process/<process_id>/summary
```

```http
GET /api/process/<process_id>/timeseries
```

```http
GET /api/process/<process_id>/stream
```

---

## Live APIs

```http
POST /api/live/reading
```

```http
GET /api/live/stream
```

```http
GET /api/live/status
```

```http
POST /api/live/reset
```

---

# ▶️ Installation

Clone the repository:

```bash
git clone https://github.com/Omar1Aux/BaristAI.git
cd BaristAI
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run

Start backend:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🔮 Future Work

* Real ESP32 deployment
* Cloud storage
* Human taste labels
* Taste prediction models
* Mobile dashboard
* Predictive maintenance
* Multi-machine monitoring

---

# 👨‍💻 Team

BaristAI was developed as a Data Analytics & AI project focused on combining:

* Data Engineering
* Machine Learning
* IoT Architecture
* Interactive Dashboard Design

---

# ⭐ BaristAI

**Process-aware Monitoring • Rule-Based Feedback • Server-Side Streaming • MQTT Ready**
