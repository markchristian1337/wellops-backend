import time, requests, random
from datetime import datetime, timezone

SENSORS = [
    {"sensor_id": "SENSOR-001", "location": "Tank A"},
    {"sensor_id": "SENSOR-002", "location": "Tank B"},
    {"sensor_id": "SENSOR-003", "location": "Wellhead 3"},
    {"sensor_id": "SENSOR-004", "location": "Compressor Station"},
    # {"sensor_id": "SENSOR-005", "location": "Houston"},
    # {"sensor_id": "SENSOR-006", "location": "Anchorage"},
    # {"sensor_id": "SENSOR-007", "location": "Costa Rica"},
    # {"sensor_id": "SENSOR-008", "location": "Mexico"},
]

BASE_TEMPS = {s["sensor_id"]: random.uniform(85, 105) for s in SENSORS}

while True:
    for sensor in SENSORS:
        drift = random.uniform(-1.5, 1.5)
        BASE_TEMPS[sensor["sensor_id"]] += drift * 0.3
        value = round(BASE_TEMPS[sensor["sensor_id"]] + random.uniform(-1, 1), 2)
        
        data = { 
            **sensor,
            'value': value,
            'unit': 'F',
            'recorded_at': datetime.now(timezone.utc).isoformat()
        }

        try:
            response = requests.post(
                "http://localhost:8000/api/sensors/temperatures",
                json=data
            )
            response.raise_for_status()
            print(f"[OK] {sensor['sensor_id']} → {value}°F")
        except Exception as e:
            
            print(f"[ERROR] {sensor['sensor_id']}: {e}")

    time.sleep(5)