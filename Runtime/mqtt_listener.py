import json
import paho.mqtt.client as mqtt
from influx_writer import write_espresso_data

BROKER = "localhost"
TOPIC = "espresso/data"
LATEST_FILE = "Runtime/latest_mqtt_data.json"


def fix_bad_json(payload):
    payload = payload.strip().replace("{", "").replace("}", "")
    data = {}

    for part in payload.split(","):
        key, value = part.split(":")
        key = key.strip().replace('"', "")
        value = value.strip().replace('"', "")
        data[key] = float(value)

    return data


def calculate_quality(temp, pressure, time):
    score = 100

    if temp < 90 or temp > 96:
        score -= 25

    if pressure < 9 or pressure > 10:
        score -= 35

    if time < 25 or time > 30:
        score -= 25

    score = max(0, score)

    if score >= 70:
        label = "Good extraction"
    elif score >= 40:
        label = "Extraction warning"
    else:
        label = "Poor extraction"

    return score, label


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("Received:", payload)

        try:
            data = json.loads(payload)
        except:
            data = fix_bad_json(payload)

        temp = float(data["temp"])
        pressure = float(data["pressure"])
        extraction_time = float(data["time"])

        quality_score, quality_label = calculate_quality(
            temp,
            pressure,
            extraction_time
        )

        latest_data = {
            "process_id": 1,
            "temperature": {
                "current": temp
            },
            "pressure": {
                "current": pressure
            },
            "extractionTime": {
                "current": extraction_time,
                "unit": "s"
            },
            "prediction": {
                "quality_score": quality_score,
                "quality_label": quality_label
            }
        }

        with open(LATEST_FILE, "w") as file:
            json.dump(latest_data, file)

        write_espresso_data(
            process_id=1,
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