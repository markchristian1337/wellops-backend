from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.models.alert import Alert
from app.models.well import Well
from app.schemas.alert import AlertOut, AlertCreate, AlertUpdate, AlertStatus

from datetime import datetime, timezone


router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=List[AlertOut])
def list_alerts(status: Optional[AlertStatus] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    # basic guardrails (prevents people asking for 1 million rows)
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")
    q = db.query(Alert)
    if status is not None:
        q = q.filter(Alert.status == status.value)

    alerts = (
        q.order_by(Alert.id.desc())
         .offset(offset)
         .limit(limit)
         .all()
    )
    return alerts

@router.post("", response_model=AlertOut, status_code=201)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == alert_in.well_id).first()
    if well is None:
        raise HTTPException(status_code=404, detail="well_id not found")

    now = datetime.now(timezone.utc)

    alert = Alert(**alert_in.model_dump(mode="json"))
    alert.status = "open"
    alert.created_at = now
    alert.updated_at = now

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# @router.put("/{alert_id}", response_model=AlertOut, status_code=201)
# def update_alert(alert_update: AlertUpdate, db: Session = Depends(get_db)):
    
#     alert = Alert(**alert_update.model_dump())
    
#     db.add(alert)
#     db.commit()
#     db.refresh(alert)
    
#     return alert