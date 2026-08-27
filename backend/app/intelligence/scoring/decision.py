from typing import Dict, Any

class DecisionEngine:
    def __init__(self):
        pass

    def evaluate_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes crisis parameters to output an actionable decision and explanation.
        state expects: shortage_status, shortage_probability, current_warehouse_stock, predicted_demand, nlp_urgency
        """
        shortage = state.get("shortage_status", "SAFE")
        prob = state.get("shortage_probability", 0.0)
        stock = state.get("current_warehouse_stock", 0.0)
        demand = state.get("predicted_demand", 0.0)
        nlp_urg = state.get("nlp_urgency", "WATCH")

        decision = "WAIT"
        confidence = 0.5
        explanation = "Conditions are stable. No immediate action required."

        if shortage == "CRITICAL" or nlp_urg == "CRITICAL":
            if demand > 0 and stock >= demand:
                decision = "DISPATCH"
                confidence = max(0.8, prob)
                explanation = f"Shortage risk is high ({int(prob*100)}%) and NLP urgency is {nlp_urg}. Sufficient stock available ({stock} >= {demand}). Dispatch immediately."
            elif stock > 0:
                decision = "ALLOCATE"
                confidence = max(0.85, prob)
                explanation = f"Shortage is CRITICAL but warehouse stock ({stock}) cannot fulfill total demand ({demand}). Trigger optimization to allocate limited resources fairly."
            else:
                decision = "REPLENISH"
                confidence = 0.95
                explanation = f"Zone is critically short, but warehouse inventory is exactly 0. Emergency replenishment from external sources required immediately."
                
        elif shortage == "WARNING":
            if nlp_urg == "WARNING":
                decision = "ALLOCATE"
                confidence = 0.75
                explanation = "Shortage is approaching and NLP reports indicate rising concern. Pre-emptively allocate partial stock."
            else:
                decision = "WAIT"
                confidence = 0.8
                explanation = "Shortage status is WARNING, but field reports are stable. Continue monitoring."
                
        return {
            "decision_type": decision,
            "confidence": round(confidence, 2),
            "explanation": explanation,
            "input_state": state
        }

decision_engine = DecisionEngine()
