import pytest
from app.intelligence.scoring.priority import priority_engine

def test_priority_ranking():
    # Zone A: Highly vulnerable, massive population, critical NLP reports
    zone_a = {
        "location_id": 1,
        "location_name": "Zone A",
        "medical_urgency_raw": "CRITICAL",  # 1.0
        "population": 250000,               # 1.0 normalized
        "shortage_probability": 0.95,       # 0.95
        "vulnerability_score": 0.9,         # 0.9
        "accessibility_risk": 0.8           # 0.8
    }
    
    # Zone B: Safe, smaller population
    zone_b = {
        "location_id": 2,
        "location_name": "Zone B",
        "medical_urgency_raw": "SAFE",      # 0.2
        "population": 50000,                # 0.2 normalized
        "shortage_probability": 0.1,        # 0.1
        "vulnerability_score": 0.2,         # 0.2
        "accessibility_risk": 0.1           # 0.1
    }
    
    rankings = priority_engine.calculate_priority_rankings([zone_a, zone_b])
    
    assert len(rankings) == 2
    assert rankings[0]["location_name"] == "Zone A"
    assert rankings[1]["location_name"] == "Zone B"
    
    # Zone A score should be significantly higher and in Tier 1
    assert rankings[0]["priority_score"] >= 75.0
    assert rankings[0]["tier"] == "TIER_1_CRITICAL"
    assert rankings[0]["priority_score"] > rankings[1]["priority_score"]

    # Ensure breakdown is exported properly
    breakdown = rankings[0]["breakdown"]
    assert breakdown["medical_urgency"] == 100.0
    assert breakdown["shortage_probability"] == 95.0

