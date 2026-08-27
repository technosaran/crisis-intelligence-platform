import re
from typing import Dict, Any, List
import difflib

class CrisisNLPExtractor:
    """
    Advanced NLP Information Extraction Engine for Emergency Transmissions.
    Extracts Geospatial entities, Urgency Sentiment, Resource Demands, Casualty Metrics.
    Uses Fuzzy string matching to overcome Web Speech API transcription errors.
    """
    def __init__(self):
        # Expanded dictionaries covering English, Tamil, Hindi transliterations
        self.resources_map = {
            # Medical
            "insulin": ("Insulin", "MEDICAL_SHORTAGE"),
            "oxygen": ("Oxygen Cylinders", "MEDICAL_SHORTAGE"),
            "blood": ("Blood Bags", "MEDICAL_SHORTAGE"),
            "medicine": ("Emergency Medicine", "MEDICAL_SHORTAGE"),
            "marunthu": ("Emergency Medicine", "MEDICAL_SHORTAGE"),
            "dawa": ("Emergency Medicine", "MEDICAL_SHORTAGE"),
            "first aid": ("First Aid Kits", "MEDICAL_SHORTAGE"),
            "bandages": ("First Aid Kits", "MEDICAL_SHORTAGE"),
            "kits": ("First Aid Kits", "MEDICAL_SHORTAGE"),
            "antibiotics": ("Antibiotics", "MEDICAL_SHORTAGE"),
            "defibrillator": ("Medical Defibrillators", "MEDICAL_SHORTAGE"),
            "cpr": ("Medical Defibrillators", "MEDICAL_SHORTAGE"),
            
            # Food
            "food": ("Rice Packs", "FOOD_SHORTAGE"),
            "rice": ("Rice Packs", "FOOD_SHORTAGE"),
            "rations": ("MRE Rations", "FOOD_SHORTAGE"),
            "meals": ("Prepared Meals", "FOOD_SHORTAGE"),
            "unavu": ("Prepared Meals", "FOOD_SHORTAGE"),
            "saapadu": ("Prepared Meals", "FOOD_SHORTAGE"),
            "khana": ("Prepared Meals", "FOOD_SHORTAGE"),
            "grain": ("Food Grains", "FOOD_SHORTAGE"),
            "bhook": ("Prepared Meals", "FOOD_SHORTAGE"), # hunger

            # Water
            "water": ("Drinking Water", "WATER_SHORTAGE"),
            "drinking water": ("Drinking Water", "WATER_SHORTAGE"),
            "potable water": ("Drinking Water", "WATER_SHORTAGE"),
            "thanneer": ("Drinking Water", "WATER_SHORTAGE"),
            "thanner": ("Drinking Water", "WATER_SHORTAGE"),
            "thanni": ("Drinking Water", "WATER_SHORTAGE"),
            "pani": ("Drinking Water", "WATER_SHORTAGE"),
            "purification": ("Water Purification Tabs", "WATER_SHORTAGE"),
            
            # Shelter
            "tents": ("Emergency Tents", "SHELTER_SHORTAGE"),
            "blankets": ("Thermal Blankets", "SHELTER_SHORTAGE"),
            "shelter": ("Emergency Tents", "SHELTER_SHORTAGE"),
            "beds": ("Camp Cots", "SHELTER_SHORTAGE"),
            "tarps": ("Tarpaulins", "SHELTER_SHORTAGE"),
            "kudisai": ("Emergency Tents", "SHELTER_SHORTAGE"),
            "thangum idam": ("Emergency Tents", "SHELTER_SHORTAGE")
        }

        self.urgency_keywords = {
            "critical": 0.95, "dying": 0.98, "immediate": 0.90, "emergency": 0.92,
            "severe": 0.88, "sos": 0.99, "aabathu": 0.97, "udane": 0.95,
            "khatra": 0.94, "running low": 0.85, "stranded": 0.82, "trapped": 0.95,
            "collapse": 0.90, "drowning": 0.96, "apaya": 0.93, "bachao": 0.98,
            "kaapaathunga": 0.98, "help": 0.90
        }
        
        self.warning_keywords = {
            "shortage": 0.70, "need": 0.65, "thevai": 0.75, "zaroorat": 0.70,
            "decreasing": 0.60, "running out soon": 0.75, "requesting": 0.60,
            "limited": 0.55, "require": 0.65, "koraiyuthu": 0.60
        }

        self.hazard_keywords = {
            "flood": "URBAN_FLOODING", "flooded": "URBAN_FLOODING", "vellam": "URBAN_FLOODING",
            "water level": "URBAN_FLOODING", "bridge washed": "INFRASTRUCTURE_COLLAPSE",
            "collapsed": "STRUCTURAL_COLLAPSE", "landslide": "LANDSLIDE_BLOCKAGE",
            "fire": "FIRE_HAZARD", "contaminated": "WATER_CONTAMINATION",
            "cyclone": "CYCLONE_STORM_SURGE", "puyal": "CYCLONE_STORM_SURGE",
            "earthquake": "SEISMIC_DAMAGE", "nilanadukkam": "SEISMIC_DAMAGE",
            "bhookamp": "SEISMIC_DAMAGE"
        }

    def _fuzzy_match(self, text_words: List[str], target: str, threshold: float = 0.8) -> bool:
        """Simulates transformer/fuzzy matching to handle speech-to-text misspellings"""
        for word in text_words:
            if difflib.SequenceMatcher(None, word, target).ratio() >= threshold:
                return True
        return False

    def analyze_text(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        
        # 1. Fuzzy Extraction of Resources & Event Type
        resource_found = None
        event_type = "GENERAL_CRISIS"
        detected_resources = set()
        
        for kw, (res_name, ev_type) in self.resources_map.items():
            if kw in text_lower or (len(kw) > 4 and self._fuzzy_match(words, kw, 0.85)):
                if not resource_found:
                    resource_found = res_name
                    event_type = ev_type
                detected_resources.add(res_name)

        # 2. Extract Hazard Classification
        hazard_type = "GENERAL_EMERGENCY"
        for kw, haz in self.hazard_keywords.items():
            if kw in text_lower or (len(kw) > 4 and self._fuzzy_match(words, kw, 0.85)):
                hazard_type = haz
                break

        # 3. Extract Urgency Sentiment
        max_urgency_score = 0.40 # Base Watch level
        urgency = "WATCH"
        
        for kw, score in self.urgency_keywords.items():
            if kw in text_lower or (len(kw) > 4 and self._fuzzy_match(words, kw, 0.85)):
                max_urgency_score = max(max_urgency_score, score)
                urgency = "CRITICAL"
                
        if urgency != "CRITICAL":
            for kw, score in self.warning_keywords.items():
                if kw in text_lower or (len(kw) > 4 and self._fuzzy_match(words, kw, 0.85)):
                    max_urgency_score = max(max_urgency_score, score)
                    urgency = "WARNING"

        # 4. Contextual Population Extraction
        affected_population = None
        pop_match = re.search(r'(\d+[\d,]*)\s*(patients|people|affected|civilians|families|individuals|victims|casualties|stranded|refugees|kudumbangal|log)', text_lower)
        if pop_match:
            raw_num = pop_match.group(1).replace(",", "")
            affected_population = int(raw_num)

        # 5. Extract Quantity Requested
        quantity_requested = None
        qty_match = re.search(r'(\d+[\d,]*)\s*(kits|vials|packs|liters|boxes|units|bottles|doses)', text_lower)
        if qty_match:
            quantity_requested = int(qty_match.group(1).replace(",", ""))

        # 6. Advanced NER Location Extraction
        location = None
        loc_match = re.search(r'(zone\s+[a-z0-9]+|sector\s+[a-z0-9]+|ward\s+[a-z0-9]+|district\s+[a-z0-9]+|depot\s+[a-z0-9]+)', text_lower)
        if loc_match:
            location = loc_match.group(1).title()
        else:
            if "central" in text_lower or "madhya" in text_lower:
                location = "Zone B (Central)"
            elif "north" in text_lower or "vadakku" in text_lower:
                location = "Zone A (North)"
            elif "south" in text_lower or "therku" in text_lower:
                location = "Zone C (South)"
            elif "east" in text_lower or "kizhakku" in text_lower:
                location = "Zone E (East)"
            elif "west" in text_lower or "merku" in text_lower:
                location = "Zone D (West)"

        confidence = round(min(0.98, max_urgency_score * 0.9 + (0.1 if location else 0.0) + (0.08 if affected_population else 0.0)), 2)

        return {
            "location": location,
            "resource": resource_found or "Emergency Relief Supplies",
            "detected_resources": list(detected_resources),
            "urgency": urgency,
            "urgency_score": round(max_urgency_score, 2),
            "affected_population": affected_population,
            "quantity_requested": quantity_requested,
            "event_type": event_type,
            "hazard_type": hazard_type,
            "confidence": confidence
        }

nlp_extractor = CrisisNLPExtractor()

