from pydantic import BaseModel
from typing import List, Dict, Optional

class SimulationStartRequest(BaseModel):
    scenario_name: str  # e.g., "CHENNAI_FLOOD"
    affected_zones: List[int]  # List of location IDs
    population_affected: int
    duration_days: int = 7

class SimulationEventRequest(BaseModel):
    event_type: str  # e.g., "ROAD_CLOSURE", "DEMAND_SPIKE"
    payload: Dict[str, float | int | str]

class SimulationResponse(BaseModel):
    status: str
    message: str
    crisis_id: Optional[int] = None
