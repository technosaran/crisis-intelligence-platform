from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict, Optional
from pydantic import BaseModel

from app.api import deps
from app.schemas.allocation import AllocationOptimizeRequest, AllocationOptimizeResponse
from app.optimization.allocation.optimizer import allocation_optimizer
from app.models.core_models import DemandRecord, Inventory, Location, Warehouse
from sqlalchemy import func

router = APIRouter()

class MultiWarehouseAllocationRequest(BaseModel):
    resource_id: int
    fairness_ratio: float = 0.15

@router.post("/optimize", response_model=AllocationOptimizeResponse)
def optimize_allocation(
    request: AllocationOptimizeRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Distribute limited resources mathematically using Linear Programming with optional fairness bounds.
    """
    if not request.demands:
        raise HTTPException(status_code=400, detail="Demand list cannot be empty.")
        
    demands_dict = [d.model_dump() for d in request.demands]
    
    result = allocation_optimizer.optimize_allocation(
        request.total_available_supply, 
        demands_dict,
        fairness_ratio=request.fairness_ratio
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))
        
    return AllocationOptimizeResponse(
        resource_id=request.resource_id,
        total_allocated=result["total_allocated"],
        total_unmet_demand=result["total_unmet_demand"],
        allocations=result["allocations"]
    )

@router.post("/multi-warehouse-optimize")
def optimize_multi_warehouse(
    request: MultiWarehouseAllocationRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Multi-Warehouse to Multi-Zone Transportation LP Optimization.
    Calculates the complete dispatch matrix across all depots and emergency zones.
    """
    # 1. Fetch Warehouses and their stock for this resource
    warehouses_db = db.query(Warehouse).all()
    warehouses_data = []
    for wh in warehouses_db:
        stock = db.query(Inventory.quantity).filter(
            Inventory.warehouse_id == wh.id,
            Inventory.resource_id == request.resource_id
        ).scalar() or 0.0

        lat = wh.location.latitude if wh.location else 13.050
        lng = wh.location.longitude if wh.location else 80.245

        warehouses_data.append({
            "id": wh.id,
            "name": wh.name,
            "stock": stock,
            "lat": lat,
            "lng": lng
        })


    # 2. Fetch Locations and their aggregate demands
    locations_db = db.query(Location).all()
    demands_data = []
    for loc in locations_db:
        loc_demand = db.query(func.sum(DemandRecord.quantity)).filter(
            DemandRecord.resource_id == request.resource_id,
            DemandRecord.location_id == loc.id
        ).scalar() or 0.0

        if loc_demand > 0:
            demands_data.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "demand": loc_demand,
                "priority_score": loc.vulnerability_score * 100.0,
                "lat": loc.latitude,
                "lng": loc.longitude
            })

    if not demands_data:
        # Fallback to seeded demo demand if DB hasn't been stimulated yet
        demands_data = [
            {"location_id": 1, "location_name": "Zone A (North Hospital Depot)", "demand": 4500, "priority_score": 92.0, "lat": 13.118, "lng": 80.220},
            {"location_id": 3, "location_name": "Zone C (South Coastal Relief)", "demand": 3800, "priority_score": 85.0, "lat": 12.970, "lng": 80.215},
            {"location_id": 4, "location_name": "Zone D (West Medical Center)", "demand": 2900, "priority_score": 78.0, "lat": 13.040, "lng": 80.140},
            {"location_id": 5, "location_name": "Zone E (East Harbor Shelter)", "demand": 4100, "priority_score": 88.0, "lat": 13.090, "lng": 80.290},
        ]

    if not warehouses_data or sum(w["stock"] for w in warehouses_data) <= 0:
        warehouses_data = [
            {"id": 1, "name": "Central Logistics Depot A", "stock": 5000, "lat": 13.050, "lng": 80.245},
            {"id": 2, "name": "North Medical Supply Hub", "stock": 4000, "lat": 13.120, "lng": 80.210},
            {"id": 3, "name": "South Harbor Emergency Depot", "stock": 3500, "lat": 12.980, "lng": 80.220},
        ]

    from app.worker import optimize_allocation_task
    
    task = optimize_allocation_task.delay(warehouses_data, demands_data, request.fairness_ratio)
    
    return {"task_id": task.id, "status": "processing", "message": "Optimization task dispatched to Celery worker."}

@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)
    if task_result.ready():
        if task_result.successful():
            return {"task_id": task_id, "status": "completed", "result": task_result.result}
        else:
            return {"task_id": task_id, "status": "failed", "error": str(task_result.result)}
    return {"task_id": task_id, "status": "processing"}

@router.get("/live-state/{resource_id}")
def get_live_allocation_state(resource_id: int, db: Session = Depends(deps.get_db)):
    """Fetch real-time inventory and demand state for a resource to feed into the optimizer."""
    # 1. Total supply
    total_supply = db.query(func.sum(Inventory.quantity)).filter(Inventory.resource_id == resource_id).scalar() or 0.0
    
    # 2. Aggregated Demands
    locations = db.query(Location).all()
    demands_list = []
    
    for loc in locations:
        loc_demand = db.query(func.sum(DemandRecord.quantity)).filter(
            DemandRecord.resource_id == resource_id,
            DemandRecord.location_id == loc.id
        ).scalar() or 0.0
        
        if loc_demand > 0:
            demands_list.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "demand": loc_demand,
                "priority_score": loc.vulnerability_score * 100.0,
                "lat": loc.latitude,
                "lng": loc.longitude
            })
            
    return {
        "resource_id": resource_id,
        "total_available_supply": total_supply,
        "demands": demands_list
    }

