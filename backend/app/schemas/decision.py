from pydantic import BaseModel
from typing import Optional, Dict, Any

class DecisionInputState(BaseModel):
    location_id: int
    resource_id: Optional[int] = 1
    shortage_status: str  # CRITICAL, WARNING, WATCH, SAFE
    shortage_probability: float
    current_warehouse_stock: float
    predicted_demand: float
    nlp_urgency: str = "WATCH"  # CRITICAL, WARNING, etc.


class DecisionResponse(BaseModel):
    decision_type: str  # REPLENISH, ALLOCATE, DISPATCH, REROUTE, WAIT
    confidence: float
    explanation: str
    input_state: Dict[str, Any]
    
class DecisionRecordSchema(DecisionResponse):
    id: int
    timestamp: str
    
    model_config = {"from_attributes": True}
