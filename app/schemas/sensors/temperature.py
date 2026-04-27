from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TemperatureCreate(BaseModel):

    sensor_id: str

    value: float

    unit: str

    location: Optional[str] = None

    recorded_at: datetime


class TemperatureOut(BaseModel):

    id: int

    sensor_id: str

    value: float

    unit: str

    recorded_at: datetime

    ingested_at: datetime

    location: Optional[str] = None

    raw_payload: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


