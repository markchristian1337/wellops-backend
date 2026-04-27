from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.sensors.temperature import TemperatureOut, TemperatureCreate
from app.services.sensors.temperature import create_reading, fetch_latest, fetch_history, fetch_range
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/sensors/temperatures", tags=["sensors/temperatures"])

@router.post("", response_model=TemperatureOut, status_code=201)
def post_reading(temperature_in: TemperatureCreate, db: Session = Depends(get_db)):
    return create_reading(temperature_in, db)

@router.get("/latest", response_model=List[TemperatureOut], status_code=200)
def get_latest(sensor_id: Optional[str] = None, db: Session = Depends(get_db)):
    return fetch_latest(db, sensor_id)

@router.get("/history", response_model=List[TemperatureOut], status_code=200)
def get_history(sensor_id: Optional[str] = None, limit: Optional[int] = 100, db: Session = Depends(get_db)):
    return fetch_history(db, sensor_id, limit)

@router.get("/range", response_model=List[TemperatureOut], status_code=200)
def get_range(from_dt: datetime, to_dt: datetime, sensor_id: Optional[str] = None, db: Session = Depends(get_db)):
    return fetch_range(db, from_dt, to_dt, sensor_id)
