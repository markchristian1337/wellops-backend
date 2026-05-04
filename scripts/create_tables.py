from app.core.db import Base, engine

# Import models so they register with Base.metadata
from app.models.well import Well  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.sensors.temperature import Temperature  # noqa: F401


Base.metadata.create_all(bind=engine)