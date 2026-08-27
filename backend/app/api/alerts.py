from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, List

from app.api import deps
from app.models.core_models import Alert
from app.schemas.alert import AlertResponse
from app.automation.tasks import automation_engine

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve automated alerts.
    """
    return db.query(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/run_cycle")
def trigger_automation_cycle(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Manually trigger the automation cycle (for testing/diagnostics).
    In production, this would run on a scheduler.
    """
    # For demonstration, run synchronously to return stats, 
    # but could be pushed to background_tasks
    result = automation_engine.run_cycle(db)
    return result
