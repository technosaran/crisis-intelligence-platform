import pytest
from app.intelligence.scoring.decision import decision_engine

def test_decision_dispatch():
    state = {
        "shortage_status": "CRITICAL",
        "shortage_probability": 0.95,
        "current_warehouse_stock": 10000,
        "predicted_demand": 5000,
        "nlp_urgency": "CRITICAL"
    }
    
    result = decision_engine.evaluate_state(state)
    assert result["decision_type"] == "DISPATCH"
    assert "Sufficient stock available" in result["explanation"]

def test_decision_allocate():
    state = {
        "shortage_status": "CRITICAL",
        "shortage_probability": 0.95,
        "current_warehouse_stock": 2000,
        "predicted_demand": 5000,
        "nlp_urgency": "WARNING"
    }
    
    result = decision_engine.evaluate_state(state)
    assert result["decision_type"] == "ALLOCATE"
    assert "cannot fulfill total demand" in result["explanation"]

def test_decision_replenish():
    state = {
        "shortage_status": "CRITICAL",
        "shortage_probability": 0.95,
        "current_warehouse_stock": 0,
        "predicted_demand": 5000,
        "nlp_urgency": "CRITICAL"
    }
    
    result = decision_engine.evaluate_state(state)
    assert result["decision_type"] == "REPLENISH"
    assert "inventory is exactly 0" in result["explanation"]
