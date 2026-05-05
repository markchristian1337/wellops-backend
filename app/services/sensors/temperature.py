from sqlalchemy import func
from app.models.sensors.temperature import Temperature
from app.schemas.sensors.temperature import TemperatureCreate, SensorSummaryOut
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from pandas import DataFrame
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Row


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
            func.max(Temperature.recorded_at).label("max_recorded_at"),
        )
        .group_by(Temperature.sensor_id)
        .subquery()
    )
    q = db.query(Temperature).join(
        subq,
        (Temperature.sensor_id == subq.c.sensor_id)
        & (Temperature.recorded_at == subq.c.max_recorded_at),
    )
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    return q.all()


def fetch_history(
    db: Session, sensor_id: Optional[str] = None, limit: Optional[int] = 100
) -> list[Temperature]:
    q = db.query(Temperature)
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    q = q.order_by(Temperature.recorded_at.desc()).limit(limit)
    return q.all()


def fetch_range(
    db: Session, from_dt: datetime, to_dt: datetime, sensor_id: Optional[str] = None
) -> list[Temperature]:
    q = (
        db.query(Temperature)
        .filter(Temperature.recorded_at >= from_dt)
        .filter(Temperature.recorded_at <= to_dt)
    )
    if sensor_id is not None:
        q = q.filter(Temperature.sensor_id == sensor_id)
    q = q.order_by(Temperature.recorded_at.desc())
    return q.all()


def fetch_summary(
    db: Session, sensor_id: str, count: Optional[int] = 100
) -> SensorSummaryOut:
    data = fetch_history(db, sensor_id, count)
    df = DataFrame([{"sensor_id": r.sensor_id, "value": r.value} for r in data])
    if df.empty:
        raise HTTPException(
            status_code=404, detail=f"No readings found for sensor {sensor_id}"
        )
    stats = df["value"].agg(["mean", "std", "min", "max"])
    mean_val = round(float(stats["mean"]), 4)
    std_val = round(float(stats["std"]), 4)
    min_val = round(float(stats["min"]), 4)
    max_val = round(float(stats["max"]), 4)
    now = datetime.now(timezone.utc)
    summary = SensorSummaryOut(
        sensor_id=sensor_id,
        mean=mean_val,
        std=std_val,
        min=min_val,
        max=max_val,
        count=count or 100,
        calculated_at=now,
    )
    # print(df)
    return summary


def fetch_last_n_per_sensor(db: Session, n: Optional[int] = 100) -> list:
    sql = text("""
        SELECT * FROM temperature_readings
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY sensor_id 
                           ORDER BY recorded_at DESC
                       ) as rn
                FROM temperature_readings
            ) ranked
            WHERE rn <= :n
        )
        ORDER BY sensor_id, recorded_at DESC
    """)
    result = db.execute(sql, {"n": n})
    return list(result.fetchall())


def fetch_summaries(db: Session, count: Optional[int] = 100) -> list[SensorSummaryOut]:
    data = fetch_last_n_per_sensor(db, n=count)
    df = DataFrame([{"sensor_id": r.sensor_id, "value": r.value} for r in data])
    if df.empty:
        return []
    now = datetime.now(timezone.utc)
    stats = df.groupby("sensor_id")["value"].agg(["mean", "std", "min", "max", "count"])
    print(stats)
    stats = stats.reset_index()
    records = stats.to_dict("records")
    summaries = [
        SensorSummaryOut(
            sensor_id=r["sensor_id"],
            mean=round(float(r["mean"]), 4),
            std=round(float(r["std"]), 4),
            min=round(float(r["min"]), 4),
            max=round(float(r["max"]), 4),
            count=int(r["count"]),
            calculated_at=now,
        )
        for r in records
    ]
    return summaries
