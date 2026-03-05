from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.db import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False, index=True)

    severity = Column(String, nullable=False)

    message = Column(String, nullable=False)

    status = Column(String, nullable=False, index=True)

    ack_by = Column(String)
    ack_at = Column(DateTime)

    close_by = Column(String)
    close_at = Column(DateTime)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)