from sqlalchemy import func
from app.models.sensors.temperature import Temperature
from app.schemas.sensors.temperature import TemperatureCreate
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

def create_reading(temperature_in, db):
    # sensor = db.query(sensor).filter(sensor.id == temperature_in.sensor_id).first()
    # if sensor is None:
    #     raise HTTPException(status_code=404, detail="sensor_id not found")

    now = datetime.now(timezone.utc)
    raw = temperature_in.model_dump_json()
    temperature = Temperature(**temperature_in.model_dump(mode="json"))

    temperature.raw_payload = raw

    db.add(temperature)
    db.commit()
    db.refresh(temperature)

    return temperature

def fetch_latest(db: Session, sensor_id: Optional[str] = None) -> list[Temperature]:
    subq = (
        db.query(
            Temperature.sensor_id,
            func.max(Temperature.recorded_at).label("max_recorded_at")
        )
        .group_by(Temperature.sensor_id)
        .subquery()
    )
    q = db.query(Temperature).join(
        subq,
        (Temperature.sensor_id == subq.c.sensor_id) &
        (Temperature.recorded_at == subq.c.max_recorded_at)
    )
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    return q.all()
    
def fetch_history(db: Session, sensor_id: Optional[str] = None, limit: Optional[int] = 100) -> list[Temperature]:
    q = db.query(Temperature)
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    q = q.order_by(Temperature.recorded_at.desc()).limit(limit)
    return q.all()

def fetch_range(db: Session, from_dt: datetime, to_dt: datetime, sensor_id: Optional[str] = None) -> list[Temperature]:
    q = db.query(Temperature).filter(Temperature.recorded_at >= from_dt).filter(Temperature.recorded_at <= to_dt)
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    q = q.order_by(Temperature.recorded_at.desc())
    return q.all()