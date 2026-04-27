from app.core.db import SessionLocal
from app.models.well import Well
from app.models.alert import Alert
from app.models.sensors.temperature import Temperature
from datetime import datetime, timezone, timedelta
import random

db = SessionLocal()

wells = [
    Well(name="Well A", api_number="42-383-00001", basin="Permian", status="producing", lat=31.9686, lon=-99.9018),
    Well(name="Well B", api_number="42-383-00002", basin="Eagle Ford", status="producing", lat=28.7041, lon=-97.3684),
    Well(name="Well C", api_number="42-383-00003", basin="Bakken", status="shut_in", lat=47.5515, lon=-102.8779),
]
db.add_all(wells)
db.commit()
for w in wells:
    db.refresh(w)

alert_severities = ["low", "medium", "high", "critical"]
statuses = ["open", "ack", "closed"]

alerts = []
for i in range(30):
    well = random.choice(wells)
    alerts.append(Alert(
        well_id=well.id,
        severity=random.choice(alert_severities),
        message=f"Alert detected on {well.name}",
        status=random.choice(statuses),
        created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72)),
        updated_at=datetime.now(timezone.utc),
    ))
db.add_all(alerts)
db.commit()

sensors = [
    {"sensor_id": "SENSOR-001", "location": "Tank A"},
    {"sensor_id": "SENSOR-002", "location": "Tank B"},
    {"sensor_id": "SENSOR-003", "location": "Wellhead 3"},
    {"sensor_id": "SENSOR-004", "location": "Compressor Station"},
]

now = datetime.now(timezone.utc)
readings = []
for sensor in sensors:
    base_temp = random.uniform(85, 110)
    for i in range(30):
        recorded_at = now - timedelta(minutes=30 - i)
        value = round(base_temp + random.uniform(-2, 2), 2)
        readings.append(Temperature(
            sensor_id=sensor["sensor_id"],
            location=sensor["location"],
            value=value,
            unit="F",
            recorded_at=recorded_at,
            ingested_at=recorded_at,
            raw_payload="seeded",
        ))

db.add_all(readings)
db.commit()
db.close()
print("Seeded successfully")