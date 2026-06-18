# BaristAI – Real-Time Espresso Analytics Dashboard

BaristAI is a real-time espresso extraction monitoring system.
It simulates live espresso machine data, streams readings through MQTT, stores process data in InfluxDB, and displays extraction metrics and AI-based feedback on a web dashboard.

## Main Features

* Real-time espresso dashboard
* MQTT-based live data streaming
* InfluxDB time-series storage
* AI-based extraction quality prediction
* Temperature, pressure, and extraction time monitoring
* Smart feedback and confidence score

## Project Pipeline

1. `csv_streamer.py` streams espresso readings from prepared data.
2. Mosquitto receives the readings on the MQTT topic.
3. `mqtt_listener.py` listens for incoming MQTT data.
4. `live_predict.py` extracts live features.
5. `predict.py` loads the trained AI model from `quality_model.pkl`.
6. `influx_writer.py` writes data into InfluxDB.
7. `app.py` provides Flask API endpoints.
8. `dashboard.html`, `dashboard.js`, and `style.css` display the dashboard.

## How to Run

Run the following files in order:

1. `start_influx.bat`
2. `start_flask.bat`
3. `start_mqtt_listener.bat`
4. `start_csv_streamer.bat`

Then open:

http://127.0.0.1:5000/

## AI Model

The AI module was trained on cleaned espresso shot data.
The workflow included:

* Data inspection
* Cleaning invalid processes
* Extracting valid brew windows
* Feature engineering
* Label creation
* Model comparison

The tested models were:

* Logistic Regression
* Random Forest
* Gradient Boosting

The final selected model is stored as:

`quality_model.pkl`

## Main Files

* `app.py` – Flask backend
* `dashboard.html` – dashboard structure
* `dashboard.js` – dashboard live updates
* `style.css` – dashboard styling
* `csv_streamer.py` – data streaming simulation
* `mqtt_listener.py` – MQTT listener
* `influx_writer.py` – InfluxDB writer
* `predict.py` – AI prediction logic
* `live_predict.py` – live feature extraction
* `quality_model.pkl` – trained AI model

## Folder Structure

* `data/` – cleaned datasets and AI training files
* `data_old/` – old or archived data files
* `scripts/` – data cleaning, feature engineering, and training scripts
* `Runtime/` – runtime files and backups
* `Archive/` – old scripts, images, and plots
* `influxdb_data/` – local InfluxDB storage

## Notes

This project is designed as a demonstration system.
The current CSV streamer simulates real machine data and can later be replaced by direct data from the real espresso machine or Prokur system.
