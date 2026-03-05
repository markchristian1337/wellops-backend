from sqlalchemy import Column, Integer, String, Float
from app.core.db import Base


class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    api_number = Column(String, unique=True, nullable=False)

    basin = Column(String)

    status = Column(String)

    lat = Column(Float)

    lon = Column(Float)