import json

class ScopingService:
    def __init__(self, pricing_db_path: str):
        with open(pricing_db_path, 'r') as f:
            self.pricing_db = json.load(f)
            
    def generate_scope(self, damages: list, flags: list) -> list:
        """
        Map detected damage and concealed flags to construction line items.
        """
        line_items = []
        for i, flag in enumerate(flags):
            if flag['rule_id'] == 'RULE_01':
                line_items.append({
                    "line_item_id": f"LI_{i}_0",
                    "surface_id": flag['surface_id'],
                    "xactimate_code": "DRY LF",
                    "description": "Tear out wet baseboard",
                    "quantity": 3.0, # Mock LF
                    "unit": "LF",
                    "estimated_cost_usd": 3.0 * self.pricing_db.get("DRY LF", 2.50)
                })
                line_items.append({
                    "line_item_id": f"LI_{i}_1",
                    "surface_id": flag['surface_id'],
                    "xactimate_code": "DRY SF",
                    "description": "Remove drywall up to 24 inches",
                    "quantity": 3.0 * 0.61, # SF = width * 0.61m
                    "unit": "SF",
                    "estimated_cost_usd": (3.0 * 0.61) * self.pricing_db.get("DRY SF", 1.50)
                })
                
        for i, damage in enumerate(damages):
            if damage['class'] in ['mold', 'water_damage']:
                line_items.append({
                    "line_item_id": f"LI_DMG_{i}",
                    "surface_id": damage['surface_id'],
                    "xactimate_code": "WTR MIST",
                    "description": "Apply anti-microbial agent",
                    "quantity": damage['area_m2'] * 10.764, # m2 to sq ft
                    "unit": "SF",
                    "estimated_cost_usd": (damage['area_m2'] * 10.764) * self.pricing_db.get("WTR MIST", 0.35)
                })
        return line_items
