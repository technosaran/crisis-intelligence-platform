from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    warehouse_id: int
    resource_id: int
    quantity: float
    reserved_quantity: float = 0.0
    minimum_threshold: float = 0.0

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[float] = None
    reserved_quantity: Optional[float] = None
    minimum_threshold: Optional[float] = None

class InventoryResponse(InventoryBase):
    id: int
    updated_at: datetime
    
    # We could also include nested Resource/Warehouse info here if desired
    
    model_config = {"from_attributes": True}
