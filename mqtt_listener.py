import json
import pandas as pd
import paho.mqtt.client as mqtt

from live_predict import live_prediction
from influx_writer import write_espresso_data

BROKER = "localhost"
TOPIC = "espresso/data"
LATEST_FILE = "Runtime/latest_mqtt_data.json"

live_buffers = {}


def fix_bad_json(payload):
    payload = payload.strip().replace("{", "").replace("}", "")
    data = {}

    for part in payload.split(","):
        key, value = part.split(":")
        key = key.strip().replace('"', "")
        value = value.strip().replace('"', "")
        data[key] = float(value)

    return data


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("Received:", payload)

        try:
            data = json.loads(payload)
        except Exception:
            data = fix_bad_json(payload)

        process_id = int(data.get("process_id", 1))
        temp = float(data["temp"])
        pressure = float(data["pressure"])
        extraction_time = float(data["time"])

        row = {
            "process_id": process_id,
            "temp": temp,
            "pressure": pressure,
            "flowRate": float(data.get("flowRate", 0)),
            "totalVolume": float(data.get("totalVolume", 0)),
            "preinfusion": float(data.get("preinfusion", 0)),
            "preinfusionpause": float(data.get("preinfusionpause", 0)),
            "setPoint": float(data.get("setPoint", 90))
        }

        if process_id not in live_buffers:
            live_buffers[process_id] = []

        live_buffers[process_id].append(row)

        timeseries_df = pd.DataFrame(live_buffers[process_id])
        prediction = live_prediction(timeseries_df)

        quality_score = float(prediction["quality_score"])
        quality_label = prediction["quality_label"]
        model_confidence = float(prediction.get("model_confidence", quality_score))

        latest_data = {
            "process_id": process_id,
            "temperature": {
                "current": round(temp, 2)
            },
            "pressure": {
                "current": round(pressure, 2)
            },
            "extractionTime": {
                "current": extraction_time,
                "unit": "s"
            },
            "prediction": {
                "quality_score": round(quality_score, 2),
                "quality_label": quality_label,
                "model_confidence": round(model_confidence, 2)
            }
        }

        with open(LATEST_FILE, "w") as file:
            json.dump(latest_data, file)

        write_espresso_data(
            process_id=process_id,
            temperature=temp,
            pressure=pressure,
            extraction_time=extraction_time,
            quality_score=quality_score
        )

        print("Written to InfluxDB:", latest_data)

    except Exception as e:
        print("Error:", e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.loop_forever()