from pydantic import BaseModel, ConfigDict

class WellOut(BaseModel):

    id: int

    name: str

    api_number: str

    basin: str | None

    status: str | None

    lat: float | None

    lon: float | None

    model_config = ConfigDict(from_attributes=True)


class WellCreate(BaseModel):

    name: str

    api_number: str

    basin: str | None = None

    status: str | None = None

    lat: float | None = None

    lon: float | None = None