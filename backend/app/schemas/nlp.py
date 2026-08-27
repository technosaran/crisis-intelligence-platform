from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    source: str = "VOLUNTEER"
    raw_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CrisisSignalSchema(BaseModel):
    location: Optional[str]
    resource: Optional[str]
    urgency: str
    affected_population: Optional[int]
    event_type: str
    confidence: float

class AnalyzeResponse(BaseModel):
    report_id: int
    signal: CrisisSignalSchema
    
    model_config = {"from_attributes": True}
