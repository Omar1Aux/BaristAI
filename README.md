# ☕ BaristAI

BaristAI is a Flask + JavaScript dashboard for process-aware espresso-machine monitoring. It is designed for a university Project Day demo: historical machine processes can be replayed through Server-Sent Events (SSE), and live readings can enter the backend through MQTT or the `/api/live/reading` endpoint.

## What the project does

- Treats `process_id` as the unique identifier for one machine process.
- Does **not** assume every process is a coffee shot.
- Uses `segment_id` to identify the machine state:

| segment_id | Meaning |
| --- | --- |
| 1 | Brewing |
| 2 | Flushing |
| 3 | Steam |
| 4 | Heating |
| 5 | Idle |

- Calculates extraction time from the **brewing segment only** (`segment_id == 1`), not from the full process duration.
- Shows pressure, temperature, extraction time, and display-only flow rate.
- Provides rule-based extraction quality feedback. The model/score is **not a human taste prediction**.

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

## Main files

```text
app.py                  Flask routes, SSE streams, live reading endpoint
core/data_engine.py      Dataset loading, process/segment helpers, rule-based scoring
dashboard.html           Dashboard markup
dashboard.js             Dashboard controls, charts, SSE clients
style.css                Dashboard styling
mqtt_listener.py         Optional MQTT-to-Flask bridge
csv_streamer.py          Optional MQTT historical-data publisher
requirements.txt         Python dependencies
```

## Historical simulation

The **Simulate Live** button opens an SSE connection to:

```http
GET /api/process/<process_id>/stream
```

The Flask backend streams one historical row at a time. The dashboard plots the process while extraction time follows only the brewing window.

## Real live mode

The **Real Live** button listens to:

```http
GET /api/live/stream
```

Live readings can be posted directly:

```http
POST /api/live/reading
Content-Type: application/json

{
  "process_id": 101,
  "segment_id": 1,
  "temp": 93.5,
  "pressure": 9.2,
  "time": 27,
  "flowRate": 1.8,
  "totalVolume": 36
}
```

Or forwarded from MQTT by running:

```bash
python mqtt_listener.py
```

Supported environment variables:

```env
MQTT_ENABLED=true
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=espresso/data
MQTT_USERNAME=
MQTT_PASSWORD=
BACKEND_READING_URL=http://127.0.0.1:5000/api/live/reading
BARISTAI_DATA_FILE=data/rancilio-portafilter-dataset.parquet
```

## Feedback rules

Rule-based scoring uses only brewing-segment metrics:

- Temperature target: 90–96 °C
- Pressure target: 8.5–10.5 bar
- Brewing extraction time target: 25–30 seconds

`flowRate` is displayed to the user but is not used for scoring.
