import json

class RulesEngine:
    def __init__(self, rules_file: str):
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)
            
    def evaluate(self, damages: list) -> list:
        """
        Implement declarative rules.
        """
        flags = []
        for damage in damages:
            # Example RULE_01
            if damage['class'] == 'water_damage' and damage['lower_boundary_z'] <= 0.20:
                flags.append({
                    "flag_id": "FLAG_01",
                    "rule_id": "RULE_01",
                    "triggering_damage_id": damage['damage_id'],
                    "surface_id": damage['surface_id'],
                    "description": "Concealed baseboard & wall cavity moisture",
                    "severity": "critical"
                })
            # Example RULE_02
            if damage['class'] == 'mold' and damage['area_m2'] >= 1.0:
                flags.append({
                    "flag_id": "FLAG_02",
                    "rule_id": "RULE_02",
                    "triggering_damage_id": damage['damage_id'],
                    "surface_id": damage['surface_id'],
                    "description": "Concealed sub-surface structural fungal colonization",
                    "severity": "critical"
                })
        return flags
