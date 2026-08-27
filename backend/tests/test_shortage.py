import pytest
from app.intelligence.shortage.predictor import shortage_predictor

def test_safe_shortage():
    # 20k in stock, consuming 1k a day for 7 days
    current_stock = 20000.0
    daily_demands = [1000.0] * 7
    
    res = shortage_predictor.calculate_shortage(current_stock, daily_demands)
    assert res["status"] == "SAFE"
    assert res["projected_shortage"] == 0.0
    assert res["days_until_stockout"] is None

def test_critical_shortage():
    # 2500 in stock, demand is 1000/day
    current_stock = 2500.0
    daily_demands = [1000.0] * 7
    
    res = shortage_predictor.calculate_shortage(current_stock, daily_demands)
    # Day 0: 2500 - 1000 = 1500
    # Day 1: 1500 - 1000 = 500
    # Day 2: 500 - 1000 < 0 => stockout day = 2 + (500/1000) = 2.5
    assert res["days_until_stockout"] == 2.5
    assert res["status"] == "CRITICAL"
    assert res["projected_shortage"] == 4500.0
    assert res["shortage_probability"] > 0.8

def test_warning_shortage():
    # Stock runs out on day 5 (e.g. 5.0 ETA)
    current_stock = 5000.0
    daily_demands = [1000.0] * 7
    
    res = shortage_predictor.calculate_shortage(current_stock, daily_demands)
    assert res["days_until_stockout"] == 5.0
    assert res["status"] == "WARNING"
