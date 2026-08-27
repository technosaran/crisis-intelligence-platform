from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DemandBase(BaseModel):
    location_id: int
    resource_id: int
    quantity: float
    source: str = "SYSTEM"

class DemandCreate(DemandBase):
    pass

class DemandResponse(DemandBase):
    id: int
    timestamp: datetime
    
    model_config = {"from_attributes": True}
