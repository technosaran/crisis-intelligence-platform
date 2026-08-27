import pytest
from app.optimization.allocation.optimizer import allocation_optimizer

def test_allocation_optimization():
    # 10,000 supply, 21,000 demand.
    total_supply = 10000.0
    
    demands = [
        {"location_id": 1, "location_name": "Zone A", "demand": 7000, "priority_score": 95.0},
        {"location_id": 2, "location_name": "Zone B", "demand": 9000, "priority_score": 60.0},
        {"location_id": 3, "location_name": "Zone C", "demand": 5000, "priority_score": 20.0}
    ]
    
    result = allocation_optimizer.optimize_allocation(total_supply, demands)
    
    assert result["status"] == "success"
    assert result["total_allocated"] == 10000.0
    assert result["total_unmet_demand"] == 11000.0
    
    allocations = result["allocations"]
    assert len(allocations) == 3
    
    # Extract allocations by name
    alloc_map = {a["location_name"]: a["allocated_amount"] for a in allocations}
    
    # Zone A has the highest priority and demands 7000. It should get all 7000.
    assert alloc_map["Zone A"] == 7000.0
    
    # Leftover is 3000. Zone B is second highest priority. It demands 9000. It gets 3000.
    assert alloc_map["Zone B"] == 3000.0
    
    # Zone C gets 0.
    assert alloc_map["Zone C"] == 0.0
