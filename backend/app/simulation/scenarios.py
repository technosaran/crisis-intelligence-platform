# Multi-Hazard Crisis Scenario Catalog for Simulation Sandbox

SCENARIOS = {
    "CHENNAI_FLOOD": {
        "id": "CHENNAI_FLOOD",
        "title": "Chennai Urban Flash Floods",
        "type": "Flood",
        "severity": "CRITICAL",
        "description": "Massive monsoon depression causing urban inundation of low-lying sectors. Water contamination and critical shortage of Insulin and potable water across northern wards.",
        "multipliers": {
            "Medical": 3.8,
            "Food": 2.2,
            "Shelter": 3.5,
            "Water": 4.5
        },
        "road_closure_probability": 0.45,
        "default_affected_population": 320000,
        "default_duration_days": 7
    },
    "EARTHQUAKE_MAG_7": {
        "id": "EARTHQUAKE_MAG_7",
        "title": "Major Seismic Event (Magnitude 7.2)",
        "type": "Earthquake",
        "severity": "CRITICAL",
        "description": "Severe structural collapse and infrastructure destruction. Massive surge in First Aid Kits, trauma supplies, emergency tents, and arterial bridge shutdowns.",
        "multipliers": {
            "Medical": 5.2,
            "Food": 2.5,
            "Shelter": 6.0,
            "Water": 3.0
        },
        "road_closure_probability": 0.65,
        "default_affected_population": 480000,
        "default_duration_days": 10
    },
    "CYCLONE_ODISHA": {
        "id": "CYCLONE_ODISHA",
        "title": "Super Cyclone Storm Surge",
        "type": "Cyclone",
        "severity": "CRITICAL",
        "description": "Category 5 storm surge displacing coastal settlements. Total grid failure requiring autonomous distribution of food rations, potable water, and emergency power.",
        "multipliers": {
            "Medical": 3.0,
            "Food": 4.2,
            "Shelter": 4.8,
            "Water": 5.0
        },
        "road_closure_probability": 0.50,
        "default_affected_population": 400000,
        "default_duration_days": 8
    },
    "EPIDEMIC_OUTBREAK": {
        "id": "EPIDEMIC_OUTBREAK",
        "title": "Viral Epidemic Resurgence",
        "type": "Epidemic",
        "severity": "HIGH",
        "description": "Exponential outbreak of airborne viral contagion. Extreme demand spike for oxygen, specialized medication, PPE, and localized quarantine zone containment.",
        "multipliers": {
            "Medical": 6.5,
            "Food": 1.5,
            "Shelter": 1.8,
            "Water": 1.8
        },
        "road_closure_probability": 0.15,
        "default_affected_population": 250000,
        "default_duration_days": 14
    }
}

