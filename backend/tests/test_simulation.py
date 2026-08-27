import pytest
from app.simulation.scenarios import SCENARIOS
from app.simulation.engine import trigger_event
from unittest.mock import MagicMock

def test_scenarios_exist():
    assert "CHENNAI_FLOOD" in SCENARIOS
    assert "EARTHQUAKE_MAG_7" in SCENARIOS
    assert SCENARIOS["CHENNAI_FLOOD"]["type"] == "Flood"
    assert SCENARIOS["CHENNAI_FLOOD"]["multipliers"]["Medical"] == 3.8

def test_engine_trigger_event_invalid_type():
    mock_db = MagicMock()
    result = trigger_event(mock_db, "UNKNOWN_EVENT", {})
    assert result["status"] == "error"
    assert "Unknown event type" in result["message"]
