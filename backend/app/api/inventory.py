from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.schemas.inventory import InventoryResponse, InventoryCreate, InventoryUpdate
from app.services.inventory import inventory_service

router = APIRouter()

@router.get("/", response_model=List[InventoryResponse])
def get_inventory(
    db: Session = Depends(deps.get_db),
    warehouse_id: int = None,
    resource_id: int = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve inventory across warehouses.
    """
    return inventory_service.get_inventory(db, warehouse_id, resource_id, skip, limit)

@router.post("/", response_model=InventoryResponse)
def create_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_in: InventoryCreate
) -> Any:
    """
    Create a new inventory record.
    """
    inventory, error = inventory_service.create_inventory(db, inventory_in)
    if error:
        status_code = 400 if "already exists" in error else 404
        raise HTTPException(status_code=status_code, detail=error)
    return inventory

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    *,
    db: Session = Depends(deps.get_db),
    inventory_id: int,
    inventory_in: InventoryUpdate
) -> Any:
    """
    Update inventory quantity (e.g., after a delivery or depletion).
    """
    inventory, error = inventory_service.update_inventory(db, inventory_id, inventory_in)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return inventory
