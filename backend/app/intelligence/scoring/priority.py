from typing import List, Dict

class PriorityEngine:
    """
    Multi-Criteria Decision Analysis (MCDA / AHP) Priority Engine for Disaster Relief.
    Weights derived from Analytic Hierarchy Process (AHP) for emergency logistics:
      - Medical Urgency: 30%
      - Shortage Probability: 25%
      - Structural/Demographic Vulnerability: 20%
      - Population Affected: 15%
      - Accessibility & Logistics Risk: 10%
    """
    def __init__(self):
        self.weights = {
            "medical_urgency": 0.30,
            "shortage_probability": 0.25,
            "vulnerability": 0.20,
            "population": 0.15,
            "accessibility_risk": 0.10
        }

    def calculate_priority_rankings(
        self, 
        locations_data: List[Dict],
        custom_weights: Dict[str, float] = None
    ) -> List[Dict]:
        """
        locations_data should be a list of dicts with:
        - location_id
        - location_name
        - medical_urgency_raw (e.g. CRITICAL, WARNING, WATCH, SAFE)
        - population
        - shortage_probability (0.0 to 1.0)
        - vulnerability_score (0.0 to 1.0)
        - accessibility_risk (0.0 to 1.0)
        """
        if not locations_data:
            return []

        weights = custom_weights or self.weights
        total_w = sum(weights.values())
        norm_w = {k: v / total_w for k, v in weights.items()}

        # Find max population for normalization
        max_pop = max(loc.get("population", 1) for loc in locations_data)
        max_pop = max(max_pop, 1) # Prevent division by zero

        rankings = []
        for loc in locations_data:
            # 1. Normalize Medical Urgency
            raw_urgency = loc.get("medical_urgency_raw", "WATCH")
            urgency_map = {"CRITICAL": 1.0, "WARNING": 0.75, "WATCH": 0.45, "SAFE": 0.15}
            med_urgency = urgency_map.get(raw_urgency, 0.45)

            # 2. Normalize Population (Log-scaled or linear normalized)
            pop = loc.get("population", 0)
            pop_normalized = min(1.0, max(0.05, pop / max_pop))

            # 3. Shortage Risk
            shortage = min(1.0, max(0.05, loc.get("shortage_probability", 0.1)))

            # 4. Vulnerability
            vuln = min(1.0, max(0.05, loc.get("vulnerability_score", 0.5)))

            # 5. Accessibility Risk
            acc_risk = min(1.0, max(0.05, loc.get("accessibility_risk", 0.5)))

            # MCDA Weighted Sum Model (Normalized to 0 - 100)
            weighted_score = (
                norm_w["medical_urgency"] * med_urgency +
                norm_w["shortage_probability"] * shortage +
                norm_w["vulnerability"] * vuln +
                norm_w["population"] * pop_normalized +
                norm_w["accessibility_risk"] * acc_risk
            ) * 100.0

            scaled_score = round(weighted_score, 2)

            # Priority classification tier
            if scaled_score >= 75.0:
                tier = "TIER_1_CRITICAL"
            elif scaled_score >= 50.0:
                tier = "TIER_2_HIGH"
            elif scaled_score >= 30.0:
                tier = "TIER_3_MODERATE"
            else:
                tier = "TIER_4_LOW"

            rankings.append({
                "location_id": loc["location_id"],
                "location_name": loc["location_name"],
                "priority_score": scaled_score,
                "tier": tier,
                "breakdown": {
                    "medical_urgency": round(med_urgency * 100, 1),
                    "population_affected": round(pop_normalized * 100, 1),
                    "shortage_probability": round(shortage * 100, 1),
                    "vulnerability": round(vuln * 100, 1),
                    "accessibility_risk": round(acc_risk * 100, 1)
                }
            })

        # Sort descending by priority_score
        rankings.sort(key=lambda x: x["priority_score"], reverse=True)
        return rankings

priority_engine = PriorityEngine()

