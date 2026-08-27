import pytest
from app.intelligence.scoring.priority import priority_engine
from app.optimization.allocation.optimizer import allocation_optimizer
from app.intelligence.scoring.decision import decision_engine

def test_full_pipeline_flow():
    # 1. Simulate Shortage Condition (Phase 8 output)
    state = {
        "location_id": 1,
        "resource_id": 1,
        "shortage_status": "CRITICAL",
        "shortage_probability": 0.99,
        "current_warehouse_stock": 5000,
        "predicted_demand": 8000,
        "nlp_urgency": "CRITICAL"
    }

    # 2. Decision Engine processes the state (Phase 13)
    decision = decision_engine.evaluate_state(state)
    
    # Since stock (5000) < demand (8000) but > 0, it should trigger ALLOCATE
    assert decision["decision_type"] == "ALLOCATE"
    
    # 3. Trigger Priority Engine (Phase 9)
    locs_data = [
        {"location_id": 1, "location_name": "Zone A", "medical_urgency_raw": "CRITICAL", "population": 100000, "shortage_probability": 0.99, "vulnerability_score": 0.9, "accessibility_risk": 0.5},
        {"location_id": 2, "location_name": "Zone B", "medical_urgency_raw": "WATCH", "population": 50000, "shortage_probability": 0.5, "vulnerability_score": 0.3, "accessibility_risk": 0.1}
    ]
    rankings = priority_engine.calculate_priority_rankings(locs_data)
    
    assert rankings[0]["location_name"] == "Zone A"
    
    # 4. Trigger Allocation Optimizer (Phase 10)
    demands = [
        {"location_id": 1, "location_name": "Zone A", "demand": 8000, "priority_score": rankings[0]["priority_score"]},
        {"location_id": 2, "location_name": "Zone B", "demand": 2000, "priority_score": rankings[1]["priority_score"]}
    ]
    
    alloc_res = allocation_optimizer.optimize_allocation(total_supply=5000.0, demands=demands)
    
    assert alloc_res["status"] == "success"
    alloc_map = {a["location_name"]: a["allocated_amount"] for a in alloc_res["allocations"]}
    
    # Zone A demands 8000. Total supply is 5000. It has higher priority, so it gets all 5000.
    assert alloc_map["Zone A"] == 5000.0
    assert alloc_map["Zone B"] == 0.0

    # Pipeline successful.
