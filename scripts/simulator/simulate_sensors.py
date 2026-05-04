import time, random, pika, json, os
from datetime import datetime, timezone

SENSORS = [
    {"sensor_id": "SENSOR-001", "location": "Tank A"},
    {"sensor_id": "SENSOR-002", "location": "Tank B"},
    {"sensor_id": "SENSOR-003", "location": "Wellhead 3"},
    {"sensor_id": "SENSOR-004", "location": "Compressor Station"},
]

BASE_TEMPS = {s["sensor_id"]: random.uniform(85, 105) for s in SENSORS}

QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "sensor.readings")

rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")

if not rabbitmq_user or not rabbitmq_pass:
    raise ValueError("RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS must be set")

# create a pika BlockingConnection
credentials = pika.PlainCredentials(
    username=rabbitmq_user,
    password=rabbitmq_pass
)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq-service"),
        credentials=credentials
        )
)
# open a channel
channel = connection.channel()

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
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2  # makes message persistent — survives RabbitMQ restart
                )
            )
            print(f"[OK] {sensor['sensor_id']} → {value}°F")
        except Exception as e:
            
            print(f"[ERROR] {sensor['sensor_id']}: {e}")

    time.sleep(5)