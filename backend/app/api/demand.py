from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.schemas.demand import DemandResponse, DemandCreate
from app.services.demand import demand_service

router = APIRouter()

@router.get("/", response_model=List[DemandResponse])
def get_demand_records(
    db: Session = Depends(deps.get_db),
    location_id: int = None,
    resource_id: int = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve historical demand records.
    """
    return demand_service.get_demand_records(db, location_id, resource_id, skip, limit)

@router.post("/", response_model=DemandResponse)
def create_demand_record(
    *,
    db: Session = Depends(deps.get_db),
    demand_in: DemandCreate
) -> Any:
    """
    Log a new demand record from a location.
    """
    demand, error = demand_service.create_demand_record(db, demand_in)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return demand
