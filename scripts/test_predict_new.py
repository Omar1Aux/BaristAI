from predict import predict_quality

test_data = {
    "duration": 60,
    "volume_delta": 120,
    "temp_avg": 92,
    "temp_min": 89,
    "temp_max": 95,
    "temp_std": 1.5,
    "pressure_avg": 8.5,
    "pressure_min": 4,
    "pressure_max": 10,
    "pressure_std": 1.2,
    "flow_avg": 150,
    "flow_min": 20,
    "flow_max": 220,
    "flow_std": 50,
    "preinfusion": 5,
    "preinfusionpause": 5,
    "setPoint": 90
}

result = predict_quality(test_data)

print(result)