from typing import List

class ShortagePredictor:
    def __init__(self):
        pass

    def calculate_shortage(self, current_stock: float, daily_demands: List[float]) -> dict:
        remaining_stock = current_stock
        stockout_day = None
        
        total_demand = sum(daily_demands)

        # No demand means no shortage risk — return SAFE immediately
        if total_demand <= 0:
            return {
                "current_stock": current_stock,
                "predicted_demand": 0.0,
                "projected_shortage": 0.0,
                "days_until_stockout": None,
                "shortage_probability": 0.01,
                "status": "SAFE"
            }
        
        for i, demand in enumerate(daily_demands):
            if remaining_stock - demand <= 0:
                # Interpolate exact day fraction
                if demand > 0:
                    fraction = remaining_stock / demand
                else:
                    fraction = 0
                stockout_day = i + fraction
                remaining_stock = 0
                break
            remaining_stock -= demand
            
        projected_shortage = max(0.0, total_demand - current_stock)
        
        # Calculate Probability and Status
        if stockout_day is None:
            # Won't run out in the given horizon
            probability = 0.05
            status = "SAFE"
        else:
            if stockout_day <= 3.0:
                status = "CRITICAL"
                probability = 0.95 - (stockout_day * 0.05)
            elif stockout_day <= 7.0:
                status = "WARNING"
                probability = 0.80 - ((stockout_day - 3) * 0.05)
            elif stockout_day <= 14.0:
                status = "WATCH"
                probability = 0.50 - ((stockout_day - 7) * 0.04)
            else:
                status = "SAFE"
                probability = 0.10
                
        return {
            "current_stock": current_stock,
            "predicted_demand": total_demand,
            "projected_shortage": projected_shortage,
            "days_until_stockout": round(stockout_day, 1) if stockout_day is not None else None,
            "shortage_probability": min(0.99, max(0.01, round(probability, 2))),
            "status": status
        }

shortage_predictor = ShortagePredictor()
