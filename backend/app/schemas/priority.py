from pydantic import BaseModel
from typing import List, Dict

class PriorityScoreBreakdown(BaseModel):
    medical_urgency: float
    population_affected: float
    shortage_probability: float
    vulnerability: float
    accessibility_risk: float

class LocationPriority(BaseModel):
    location_id: int
    location_name: str
    priority_score: float
    breakdown: PriorityScoreBreakdown

class PriorityRankingResponse(BaseModel):
    crisis_id: int
    resource_id: int
    rankings: List[LocationPriority]
