import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "temp_avg": 89,
    "temp_max": 97,
    "temp_std": 2.4,
    "pressure_avg": 6,
    "pressure_max": 12,
    "pressure_std": 1.5,
    "flow_avg": 180,
    "flow_max": 1500,
    "flow_std": 500,
    "duration_seconds": 30,
    "total_volume": 40
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())