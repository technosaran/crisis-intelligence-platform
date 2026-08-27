from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
import json
from datetime import datetime

from app.api import deps
from app.models.core_models import Decision
from app.schemas.decision import DecisionInputState, DecisionResponse
from app.intelligence.scoring.decision import decision_engine
from app.core.config import settings
import httpx

router = APIRouter()

@router.post("/evaluate", response_model=DecisionResponse)
def evaluate_and_decide(
    request: DecisionInputState,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Evaluates the current crisis state and generates an actionable decision.
    """
    state_dict = request.model_dump()
    
    # 1. Synthesize Decision
    result = decision_engine.evaluate_state(state_dict)
    
    # 2. Save Decision Trace for Explainability
    decision_record = Decision(
        decision_type=result["decision_type"],
        input_state=result["input_state"],
        recommendation={"action": result["decision_type"], "target_location": request.location_id},
        confidence=result["confidence"],
        explanation=result["explanation"],
        timestamp=datetime.utcnow()
    )
    
    db.add(decision_record)
    db.commit()
    db.refresh(decision_record)
    
    # 3. Telegram Alerting
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        text = f"{result['decision_type']} DIRECTIVE - {result['explanation']}"
        try:
            httpx.post(url, json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text})
        except Exception as e:
            print(f"[TELEGRAM ALERT FAILED] {e}")
    else:
        print(f"[TELEGRAM MOCK] Would have sent alert: {result['decision_type']} DIRECTIVE - {result['explanation']}")
    
    return DecisionResponse(
        decision_type=result["decision_type"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        input_state=result["input_state"]
    )

@router.get("/", response_model=List[DecisionResponse])
def get_decisions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve past AI decisions for audit and explainability.
    """
    decisions = db.query(Decision).order_by(Decision.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Map to schema
    return [
        DecisionResponse(
            decision_type=d.decision_type,
            confidence=d.confidence,
            explanation=d.explanation,
            input_state=d.input_state
        ) for d in decisions
    ]
