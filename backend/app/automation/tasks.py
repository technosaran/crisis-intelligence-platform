from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import requests
import asyncio

from app.models.core_models import Location, Resource, Inventory, DemandForecast, CrisisSignal, Alert, Decision, Warehouse
from app.intelligence.scoring.decision import decision_engine
from app.core.config import settings
from app.api.websockets import manager

def broadcast_sync(message: dict):
    """Safely broadcast a message via WebSocket from sync context."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(message))
    except RuntimeError:
        # No running loop - create a new one (rare case)
        try:
            asyncio.run(manager.broadcast(message))
        except Exception as e:
            print(f"WebSocket broadcast failed: {e}")

async def simulate_truck_gps(convoy_id: str, coordinates: list):
    """Simulates real-time GPS telemetry for a dispatched convoy over WebSockets."""
    print(f"[TELEMETRY] Starting live GPS tracking for convoy {convoy_id}")
    for i in range(len(coordinates) - 1):
        start_coord = coordinates[i]
        end_coord = coordinates[i+1]
        
        # Break each path segment into 5 micro-steps for smooth movement
        steps = 5
        for step in range(1, steps + 1):
            fraction = step / steps
            current_lat = start_coord[0] + (end_coord[0] - start_coord[0]) * fraction
            current_lng = start_coord[1] + (end_coord[1] - start_coord[1]) * fraction
            
            await manager.broadcast({
                "event_type": "TRUCK_GPS",
                "data": {
                    "convoy_id": convoy_id,
                    "lat": current_lat,
                    "lng": current_lng,
                    "progress_percent": round(((i * steps + step) / ((len(coordinates)-1) * steps)) * 100)
                }
            })
            await asyncio.sleep(0.5)  # Update every 500ms
            
    await manager.broadcast({
        "event_type": "CONVOY_ARRIVED",
        "data": {"convoy_id": convoy_id}
    })
    print(f"[TELEMETRY] Convoy {convoy_id} arrived at destination.")

class AutomationEngine:
    def __init__(self):
        pass

    def run_cycle(self, db: Session) -> dict:
        """
        Runs a background check across all active zones.
        Generates Alerts and Decisions automatically based on thresholds.
        """
        locations = db.query(Location).all()
        resources = db.query(Resource).all()
        
        alerts_generated = 0
        decisions_made = 0

        for loc in locations:
            # Get latest NLP signal for this location
            signal = db.query(CrisisSignal).filter(
                func.lower(CrisisSignal.location) == loc.name.lower()
            ).order_by(CrisisSignal.id.desc()).first()
            
            nlp_urg = signal.urgency if signal else "WATCH"
            
            for res in resources:
                # 1. Check Inventory — scoped to warehouses at this location
                total_stock = db.query(func.sum(Inventory.quantity)).join(Warehouse).filter(
                    Warehouse.location_id == loc.id,
                    Inventory.resource_id == res.id
                ).scalar() or 0.0

                # 2. Check Forecast (Latest 7 days)
                forecasts = db.query(DemandForecast).filter(
                    DemandForecast.location_id == loc.id,
                    DemandForecast.resource_id == res.id
                ).order_by(DemandForecast.forecast_timestamp.asc()).limit(7).all()
                
                daily_demands = [f.predicted_demand for f in forecasts]
                total_predicted_demand = sum(daily_demands) if forecasts else 0.0
                
                # Shortage Prediction
                from app.intelligence.shortage.predictor import shortage_predictor
                shortage_res = shortage_predictor.calculate_shortage(float(total_stock), daily_demands)
                shortage_prob = shortage_res["shortage_probability"]
                shortage_status = shortage_res["status"]

                # 3. Decision Synthesis
                state = {
                    "location_id": loc.id,
                    "resource_id": res.id,
                    "shortage_status": shortage_status,
                    "shortage_probability": shortage_prob,
                    "current_warehouse_stock": float(total_stock),
                    "predicted_demand": float(total_predicted_demand),
                    "nlp_urgency": nlp_urg
                }
                
                decision_result = decision_engine.evaluate_state(state)
                
                # 4. Generate Alert if thresholds met
                if decision_result["decision_type"] in ["REPLENISH", "ALLOCATE", "DISPATCH"]:
                    severity = "CRITICAL" if decision_result["decision_type"] == "REPLENISH" else "WARNING"
                    message = f"System generated {decision_result['decision_type']} directive: {decision_result['explanation']}"
                    
                    # Create Alert
                    alert = Alert(
                        type="AUTOMATED_DECISION",
                        severity=severity,
                        message=message,
                        location=loc.name,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(alert)
                    alerts_generated += 1
                    
                    # Broadcast Alert via WebSockets
                    broadcast_sync({
                        "event_type": "NEW_ALERT",
                        "data": {
                            "type": "AUTOMATED_DECISION",
                            "severity": severity,
                            "message": message,
                            "location": loc.name,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    })
                    
                    # Create Decision Record
                    dec_record = Decision(
                        decision_type=decision_result["decision_type"],
                        input_state=state,
                        recommendation={"action": decision_result["decision_type"], "resource_id": res.id},
                        confidence=decision_result["confidence"],
                        explanation=decision_result["explanation"],
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(dec_record)
                    decisions_made += 1
                    
                    # 5. Dispatch Webhook to N8N Orchestrator
                    if settings.WEBHOOK_URL:
                        payload = {
                            "event": "AUTOMATED_CRISIS_DECISION",
                            "location": loc.name,
                            "resource_id": res.id,
                            "decision": decision_result["decision_type"],
                            "severity": severity,
                            "explanation": decision_result["explanation"],
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                        try:
                            requests.post(settings.WEBHOOK_URL, json=payload, timeout=5)
                        except Exception as e:
                            print(f"Failed to dispatch N8N webhook: {e}")

        db.commit()
        
        return {
            "status": "success",
            "alerts_generated": alerts_generated,
            "decisions_made": decisions_made
        }

automation_engine = AutomationEngine()
