import os
import json
import requests
import paho.mqtt.client as mqtt

MQTT_ENABLED = os.getenv("MQTT_ENABLED", "true").lower() == "true"
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "espresso/data")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

BACKEND_READING_URL = os.getenv(
    "BACKEND_READING_URL",
    "http://127.0.0.1:5000/api/live/reading"
)

if not MQTT_ENABLED:
    print("MQTT is disabled. Set MQTT_ENABLED=true to enable.")
    raise SystemExit(0)


def safe_float(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def normalize_payload(data):
    return {
        "process_id": int(data.get("process_id", 0)),
        "segment_id": int(data.get("segment_id", 1)),
        "temp": safe_float(data.get("temp", data.get("temperature", 0))),
        "pressure": safe_float(data.get("pressure", 0)),
        "flowRate": safe_float(data.get("flowRate", 0)),
        "totalVolume": safe_float(data.get("totalVolume", 0)),
        "time": safe_float(data.get("time", data.get("elapsed_seconds", 0)))
    }


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with code:", rc)
    print("Subscribed topic:", MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        raw = msg.payload.decode("utf-8")
        print("MQTT received:", raw)

        data = json.loads(raw)
        payload = normalize_payload(data)

        response = requests.post(
            BACKEND_READING_URL,
            json=payload,
            timeout=3
        )

        print("Backend response:", response.status_code)

    except Exception as e:
        print("MQTT listener error:", e)


client = mqtt.Client()

if MQTT_USERNAME:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("MQTT listener started")
print("Broker:", MQTT_BROKER)
print("Port:", MQTT_PORT)
print("Topic:", MQTT_TOPIC)

client.loop_forever()