from pydantic import BaseModel
from typing import List, Optional

class LocationDemand(BaseModel):
    location_id: int
    location_name: str
    demand: float
    priority_score: float

class AllocationOptimizeRequest(BaseModel):
    resource_id: int
    total_available_supply: float
    demands: List[LocationDemand]
    fairness_ratio: float = 0.20

class LocationAllocation(BaseModel):
    location_id: int
    location_name: str
    priority_score: Optional[float] = None
    allocated_amount: float
    unmet_demand: float
    fulfilled_percentage: float

class AllocationOptimizeResponse(BaseModel):
    resource_id: int
    total_allocated: float
    total_unmet_demand: float
    allocations: List[LocationAllocation]
