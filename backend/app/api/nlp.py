from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from pydantic import BaseModel

from app.api import deps
from app.models.core_models import CrisisReport, CrisisSignal
from app.schemas.nlp import AnalyzeRequest, AnalyzeResponse, CrisisSignalSchema
from app.intelligence.nlp.extractor import nlp_extractor
from app.automation.tasks import broadcast_sync

router = APIRouter()

class SOSRequest(BaseModel):
    sender_name: str
    location: str
    message: str


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_crisis_report(
    request: AnalyzeRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Ingest a raw text report, extract intelligence, and save signals.
    """
    if not request.raw_text or len(request.raw_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # 1. Save Raw Report
    report = CrisisReport(
        source=request.source,
        raw_text=request.raw_text,
        latitude=request.latitude,
        longitude=request.longitude,
        processed_status="PROCESSED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # 2. Extract Signals
    extracted_data = nlp_extractor.analyze_text(request.raw_text)

    # 3. Save Signal
    signal = CrisisSignal(
        report_id=report.id,
        location=extracted_data["location"],
        resource=extracted_data["resource"],
        urgency=extracted_data["urgency"],
        affected_population=extracted_data["affected_population"],
        event_type=extracted_data["event_type"],
        confidence=extracted_data["confidence"]
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)

    # 4. Format Response
    return AnalyzeResponse(
        report_id=report.id,
        signal=CrisisSignalSchema(
            location=signal.location,
            resource=signal.resource,
            urgency=signal.urgency,
            affected_population=signal.affected_population,
            event_type=signal.event_type,
            confidence=signal.confidence
        )
    )

@router.get("/signals", response_model=list[CrisisSignalSchema])
def get_signals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve processed crisis signals.
    """
    signals = db.query(CrisisSignal).offset(skip).limit(limit).all()
    return signals

@router.post("/sos-submit")
def submit_sos(
    request: SOSRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    # Extract intelligence
    extracted_data = nlp_extractor.analyze_text(request.message)
    
    # Broadcast to WebSockets
    broadcast_message = {
        "event_type": "NEW_SOS",
        "data": {
            "sender": request.sender_name,
            "reported_location": request.location,
            "message": request.message,
            "nlp_analysis": extracted_data
        }
    }
    broadcast_sync(broadcast_message)
    
    return {"status": "success", "message": "SOS received and broadcasted"}
