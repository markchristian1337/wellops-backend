from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# Enums lock down allowed string values at the API boundary.
# This prevents invalid values like severity="urgent" or status="done".
class AlertSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertStatus(str, Enum):
    open = "open"
    ack = "ack"
    closed = "closed"


class AlertOut(BaseModel):
    """
    Response schema (what the API returns).
    Includes all fields the UI may need to display.
    Fields that are not always present (ack/close info) are optional.
    """

    id: int
    well_id: int

    # Use enums instead of plain str to constrain values.
    severity: AlertSeverity
    message: str
    status: AlertStatus

    # Optional fields: these are None until the alert is ack/closed.
    ack_by: str | None = None
    ack_at: datetime | None = None

    close_by: str | None = None
    close_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None  # fixed typo: updatedd_at -> updated_at

    # Allows returning SQLAlchemy model instances directly from routes.
    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    """
    Create schema (POST /alerts request body).
    Client provides only what they are allowed to control at creation.
    Status/timestamps are server-owned and must NOT be included here.
    """

    well_id: int = Field(..., gt=0)
    severity: AlertSeverity
    message: str = Field(..., min_length=1, max_length=500)


class AlertUpdate(BaseModel):
    """
    Update schema (PATCH /alerts/{id} request body).
    'id' is NOT included because it comes from the URL path.
    This schema represents a lifecycle transition request.
    Business rules (enforced in the route):
      - open -> ack requires ack_by and server sets ack_at
      - ack -> closed requires close_by and server sets close_at
    """

    status: AlertStatus

    ack_by: str | None = Field(default=None, min_length=1, max_length=100)
    close_by: str | None = Field(default=None, min_length=1, max_length=100)