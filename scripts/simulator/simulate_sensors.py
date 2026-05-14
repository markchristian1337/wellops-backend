import time, random, pika, json, os
from datetime import datetime, timezone

SENSORS = [
    {"sensor_id": "SENSOR-001", "location": "Tank A"},
    {"sensor_id": "SENSOR-002", "location": "Tank B"},
    {"sensor_id": "SENSOR-003", "location": "Wellhead 3"},
    {"sensor_id": "SENSOR-004", "location": "Compressor Station"},
]

BASE_TEMPS = {s["sensor_id"]: random.uniform(85, 105) for s in SENSORS}

EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE_NAME", "sensor.readings")

rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")

if not rabbitmq_user or not rabbitmq_pass:
    raise ValueError("RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS must be set")

credentials = pika.PlainCredentials(username=rabbitmq_user, password=rabbitmq_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq-service"),
        credentials=credentials,
    )
)
channel = connection.channel()

channel.exchange_declare(
    exchange=EXCHANGE_NAME,
    exchange_type="topic",
    durable=True,
)

while True:
    for sensor in SENSORS:
        drift = random.uniform(-1.5, 1.5)
        BASE_TEMPS[sensor["sensor_id"]] += drift * 0.3
        value = round(BASE_TEMPS[sensor["sensor_id"]] + random.uniform(-1, 1), 2)

        data = {
            **sensor,
            "value": value,
            "unit": "F",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

        routing_key = f"temperature.{sensor['sensor_id']}"

        try:
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            print(f"[OK] {sensor['sensor_id']} → {value}°F")
        except Exception as e:
            print(f"[ERROR] {sensor['sensor_id']}: {e}")

    time.sleep(5)
