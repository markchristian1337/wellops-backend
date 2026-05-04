from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.core.db import Base


class Temperature(Base):
    __tablename__ = "temperature_readings"

    id = Column(Integer, primary_key=True, index=True)

    sensor_id = Column(String(50), nullable=False, index=True)

    value = Column(Float, nullable=False)

    unit = Column(String(2), nullable=False)

    recorded_at = Column(DateTime, nullable=False)

    ingested_at = Column(DateTime, server_default=func.now())   # db sets time as source of truth, not in application layer - would be inconsistent

    location = Column(String(100), nullable=True)   # location table can be added later, then location_id here

    raw_payload = Column(String, nullable=False)

    avg_value = Column(Float, nullable=False)

