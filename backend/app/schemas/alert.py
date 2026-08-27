from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    type: str
    severity: str
    message: str
    location: Optional[str] = None

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
