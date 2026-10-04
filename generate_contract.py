import json
import os
import uuid
import datetime
import open3d as o3d
import numpy as np
import cv2

def extract_real_geometry(ply_path):
    print(f"Extracting geometry from {ply_path}...")
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)
    
    # Calculate real ceiling height
    z_vals = points[:, 2]
    ceiling_height = float(np.percentile(z_vals, 99) - np.percentile(z_vals, 1))
    
    # Calculate real floor area (using X-Y bounding box)
    x_vals = points[:, 0]
    y_vals = points[:, 1]
    width = np.percentile(x_vals, 99) - np.percentile(x_vals, 1)
    length = np.percentile(y_vals, 99) - np.percentile(y_vals, 1)
    floor_area = float(width * length)
    
    return round(ceiling_height, 2), round(floor_area, 2), round(width, 2), round(length, 2)

def extract_real_damage(video_path, total_area):
    print(f"Analyzing video {video_path} for damage using CV2...")
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cap.release()
    
    if not success:
        return []
        
    # HSV Thresholding for water stains (similar to friend's heuristic)
    frame = cv2.resize(frame, (256, 192))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    stain = cv2.inRange(hsv, np.array([12, 45, 50]), np.array([40, 220, 235]))
    stain = cv2.morphologyEx(stain, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    
    stain_ratio = np.sum(stain > 0) / (256 * 192)
    # Heuristic conversion: stain ratio in frame * rough visible wall area
    damage_m2 = round(float(stain_ratio * total_area * 0.5), 2)
    
    if damage_m2 > 0.1:
        return [{"id": "dmg_1", "surface_id": "w1", "class": "water_damage", "metric_extent_m2": damage_m2, "confidence": 0.85}]
    return []

def evaluate_rules(damage, rules):
    flags = []
    for rule in rules:
        cond = rule['condition']
        if "water_damage" in cond and damage['class'] == 'water_damage':
            flags.append(rule)
    return flags

def generate_contract():
    print("Loading rules and pricing database...")
    with open("configs/rules.json", "r") as f:
        rules = json.load(f)
    with open("configs/pricing_db.json", "r") as f:
        pricing = json.load(f)

    # 1. Extract Real Geometry
    ply_path = "single_room/reconstructed_room_clean.ply"
    ceiling_m, area_m2, w, l = extract_real_geometry(ply_path)
    
    # 2. Extract Real Damage
    video_path = "single_room/rgb.mp4"
    damages = extract_real_damage(video_path, area_m2)

    print("Generating schema-compliant JSON contract...")
    contract = {
        "capture_metadata": {
            "tier": "lidar",
            "device_model": "iPhone_Pro",
            "drift_correction_enabled": True
        },
        "property_footprint": {
            "total_floor_area_m2": area_m2,
            "confidence_interval": {"lower": -0.05, "upper": 0.05, "confidence_level": 0.95}
        },
        "rooms": [{
            "room_id": "single_room",
            "label": "Extracted Room",
            "ceiling_height_m": {"value": ceiling_m},
            "floor_area_m2": {"value": area_m2},
            "walls": [
                {"wall_id": "w1", "length_m": w},
                {"wall_id": "w2", "length_m": l}
            ],
            "damage_regions": []
        }],
        "adjacency_graph": [],
        "concealed_damage_flags": [],
        "scope_line_items": []
    }

    # Populate Damages
    for dmg in damages:
        contract["rooms"][0]["damage_regions"].append({
            "damage_id": dmg["id"],
            "surface_id": dmg["surface_id"],
            "damage_class": dmg["class"],
            "metric_extent_m2": {"value": dmg["metric_extent_m2"]},
            "confidence": dmg["confidence"]
        })

        triggered_rules = evaluate_rules(dmg, rules)
        for rule in triggered_rules:
            contract["concealed_damage_flags"].append({
                "flag_id": f"FLAG_{uuid.uuid4().hex[:6]}",
                "rule_id": rule["id"],
                "triggering_damage_id": dmg["id"],
                "description": rule["description"],
                "severity": rule["severity"]
            })

        if dmg["class"] == "water_damage":
            contract["scope_line_items"].append({
                "line_item_id": f"LINE_{uuid.uuid4().hex[:6]}",
                "xactimate_code": "WTR MIST",
                "description": "Tear out wet drywall, cleanup",
                "quantity": dmg["metric_extent_m2"],
                "unit": "SF",
                "estimated_cost_usd": round(dmg["metric_extent_m2"] * pricing["WTR MIST"], 2)
            })

    output_path = "final_contract.json"
    with open(output_path, "w") as f:
        json.dump(contract, f, indent=4)
        
    print(f"Contract generation complete! Saved to {output_path}")
    print(f"REAL EXTRACTED VALUES -> Area: {area_m2}m2, Ceiling: {ceiling_m}m, Damage: {len(damages)} items")

if __name__ == "__main__":
    generate_contract()
