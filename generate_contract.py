import json
import os
import uuid
import datetime

# Mock CAD Extractor Output (In real pipeline, this comes from process_ply.py)
# We use deterministic mock values simulating our Point Cloud output
ROOMS_DATA = [
    {
        "room_id": "single_room",
        "label": "Living Room",
        "ceiling_height_m": 2.45,
        "floor_area_m2": 15.5,
        "walls": [
            {"wall_id": "w1", "start_point": [0,0], "end_point": [4,0], "length_m": 4.0},
            {"wall_id": "w2", "start_point": [4,0], "end_point": [4,3.875], "length_m": 3.875},
            {"wall_id": "w3", "start_point": [4,3.875], "end_point": [0,3.875], "length_m": 4.0},
            {"wall_id": "w4", "start_point": [0,3.875], "end_point": [0,0], "length_m": 3.875}
        ],
        "openings": [],
        "simulated_damage": [
            {"id": "dmg_1", "surface_id": "w1", "class": "water_damage", "metric_extent_m2": 2.0, "lower_boundary_z": 0.15, "confidence": 0.92},
            {"id": "dmg_2", "surface_id": "w2", "class": "mold", "metric_extent_m2": 1.2, "lower_boundary_z": 1.0, "confidence": 0.88}
        ]
    }
]

def evaluate_rules(damage, rules):
    flags = []
    # Simplified rule evaluator
    for rule in rules:
        cond = rule['condition']
        if "water_damage" in cond and damage['class'] == 'water_damage':
            if "lower_boundary_z <= 0.20" in cond and damage.get('lower_boundary_z', 1.0) <= 0.20:
                flags.append(rule)
        elif "mold" in cond and damage['class'] == 'mold':
            if "area_m2 >= 1.0" in cond and damage.get('metric_extent_m2', 0) >= 1.0:
                flags.append(rule)
    return flags

def generate_contract():
    print("Loading rules and pricing database...")
    with open("configs/rules.json", "r") as f:
        rules = json.load(f)
    with open("configs/pricing_db.json", "r") as f:
        pricing = json.load(f)

    print("Generating schema-compliant JSON contract...")
    contract = {
        "capture_metadata": {
            "tier": "lidar",
            "device_model": "iPhone_Pro",
            "processing_time_seconds": 12.5,
            "drift_correction_enabled": True
        },
        "property_footprint": {
            "total_floor_area_m2": sum(r["floor_area_m2"] for r in ROOMS_DATA),
            "confidence_interval": {"lower": -0.05, "upper": 0.05, "confidence_level": 0.95}
        },
        "rooms": [],
        "adjacency_graph": [],
        "concealed_damage_flags": [],
        "scope_line_items": []
    }

    for r_data in ROOMS_DATA:
        room = {
            "room_id": r_data["room_id"],
            "label": r_data["label"],
            "ceiling_height_m": {"value": r_data["ceiling_height_m"], "ci": {"lower": -0.015, "upper": 0.015, "confidence_level": 0.95}},
            "floor_area_m2": {"value": r_data["floor_area_m2"], "ci": {"lower": -0.2, "upper": 0.2, "confidence_level": 0.95}},
            "walls": r_data["walls"],
            "openings": r_data["openings"],
            "damage_regions": []
        }

        for dmg in r_data["simulated_damage"]:
            # Add damage to room
            room["damage_regions"].append({
                "damage_id": dmg["id"],
                "surface_id": dmg["surface_id"],
                "damage_class": dmg["class"],
                "metric_extent_m2": {"value": dmg["metric_extent_m2"], "ci": {"lower": -0.1, "upper": 0.1, "confidence_level": 0.90}},
                "confidence": dmg["confidence"]
            })

            # Check rules
            triggered_rules = evaluate_rules(dmg, rules)
            for rule in triggered_rules:
                contract["concealed_damage_flags"].append({
                    "flag_id": f"FLAG_{uuid.uuid4().hex[:6]}",
                    "rule_id": rule["id"],
                    "triggering_damage_id": dmg["id"],
                    "surface_id": dmg["surface_id"],
                    "description": rule["description"],
                    "severity": rule["severity"]
                })

            # Scope Line Items based on pricing DB
            if dmg["class"] == "water_damage":
                contract["scope_line_items"].append({
                    "line_item_id": f"LINE_{uuid.uuid4().hex[:6]}",
                    "surface_id": dmg["surface_id"],
                    "xactimate_code": "WTR MIST",
                    "description": "Tear out wet drywall, cleanup",
                    "quantity": dmg["metric_extent_m2"],
                    "unit": "SF",
                    "estimated_cost_usd": round(dmg["metric_extent_m2"] * pricing["WTR MIST"], 2)
                })

        contract["rooms"].append(room)

    output_path = "final_contract.json"
    with open(output_path, "w") as f:
        json.dump(contract, f, indent=4)
        
    print(f"Contract generation complete! Saved to {output_path}")

if __name__ == "__main__":
    generate_contract()
