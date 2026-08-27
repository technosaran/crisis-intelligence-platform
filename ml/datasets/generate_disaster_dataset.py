import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_crisis_dataset(output_path: str):
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    locations = [1, 2, 3, 4, 5]
    resources = [1, 2, 3] # e.g. 1: Insulin, 2: Water, 3: Blankets
    days = 100
    
    start_date = datetime.now() - timedelta(days=days)
    data = []
    
    for loc in locations:
        for res in resources:
            base_demand = np.random.randint(100, 500)
            
            # Create a disaster event
            disaster_start = np.random.randint(20, 80)
            disaster_duration = np.random.randint(5, 15)
            
            for day in range(days):
                current_date = start_date + timedelta(days=day)
                
                # Base trend + noise
                demand = base_demand + np.sin(day/7.0)*50 + np.random.normal(0, 20)
                
                is_disaster = 0
                if disaster_start <= day <= disaster_start + disaster_duration:
                    is_disaster = 1
                    # Surge factor
                    surge = np.random.uniform(1.5, 3.5)
                    demand = demand * surge
                
                data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day_index": day,
                    "day_of_week": current_date.weekday(),
                    "location_id": loc,
                    "resource_id": res,
                    "is_disaster_active": is_disaster,
                    "demand_quantity": max(0, int(demand))
                })
                
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic dataset at {output_path}")
    return df

if __name__ == "__main__":
    generate_crisis_dataset("crisis_demand_historical.csv")
