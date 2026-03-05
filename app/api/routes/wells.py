from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db
from app.models.well import Well
from app.schemas.well import WellOut, WellCreate


router = APIRouter(prefix="/wells", tags=["wells"])

@router.get("", response_model=List[WellOut])
def list_wells(db: Session = Depends(get_db)):
    wells = db.query(Well).order_by(Well.id).all()
    return wells

@router.post("", response_model=WellOut, status_code=201)
def create_well(well_in: WellCreate, db: Session = Depends(get_db)):
    # Friendly conflict check (DB unique constraint is still the final guard)
    existing = (
        db.query(Well)
        .filter(Well.api_number == well_in.api_number)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="api_number already exists")
    
    # Convert validated input schema -> ORM model
    well = Well(**well_in.model_dump())
    
    db.add(well)
    db.commit()
    db.refresh(well)    # populate generated fields like id
    
    return well

