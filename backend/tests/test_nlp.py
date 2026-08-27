import pytest
from app.intelligence.nlp.extractor import nlp_extractor

def test_nlp_extraction():
    # Test using the exact prompt example
    test_text = "Government hospital in Zone 4 is running low on insulin. Around 200 patients are affected."
    
    result = nlp_extractor.analyze_text(test_text)
    
    assert result["location"] == "Zone 4"
    assert result["resource"].lower() == "insulin"
    assert result["urgency"] == "CRITICAL" # because 'running low'
    assert result["affected_population"] == 200
    assert result["event_type"] == "MEDICAL_SHORTAGE"

def test_food_extraction():
    test_text = "People in Sector 12 desperately need food. 50 families are starving."
    result = nlp_extractor.analyze_text(test_text)
    
    assert result["location"] == "Sector 12"
    assert result["resource"].lower() in ["food", "rice packs", "food grains", "emergency relief supplies"]
    assert result["affected_population"] == 50
    assert result["event_type"] == "FOOD_SHORTAGE"
    assert result["urgency"] in ["CRITICAL", "WARNING"]

