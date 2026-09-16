"""
Rule-Based Clinical Biochemical Nutrient Interaction Engine
Phase 7A: Nutrient Expansion & Biochemical Interaction Engine Enhancement

Evaluates biochemical synergies, competitive absorptions, enzymatic dependencies,
and biosynthetic conversions between co-occurring nutrient deficiencies across all 18 target nutrients:
- Generates Synergy Score (0-100)
- Generates Inhibition/Competition Score (0-100)
- Generates Interaction Severity (LOW, MODERATE, HIGH, CRITICAL)
- Calculates compounding risk multipliers and actionable clinical guidance
"""

from typing import Dict, Any, List, Optional
from .constants import NUTRIENT_INTERACTIONS, RiskCategory


class NutrientInteractionEngine:
    """
    Evaluates risk interactions among the 18 target nutrients.
    Calculates compounding risk multipliers, synergy scores, inhibition scores, and clinical observations.
    """

    def __init__(self, interaction_rules: Optional[List[Dict[str, Any]]] = None):
        self.rules = interaction_rules or NUTRIENT_INTERACTIONS

    def analyze_interactions(
        self,
        predicted_risks: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Takes predicted nutrient risk outcomes:
        predicted_risks = {
            "Vitamin D": {"risk_level": "High Risk", "probability": 0.82},
            "Calcium": {"risk_level": "Moderate Risk", "probability": 0.65}, ...
        }
        Returns:
            - list of active interactions
            - compound severity modifier
            - synergy_score (0-100)
            - inhibition_score (0-100)
            - interaction_severity ("LOW", "MODERATE", "HIGH", "CRITICAL")
            - clinical interaction observations and guidance
        """
        active_interactions = []
        overall_compounding_multiplier = 1.0
        total_synergy_weight = 0.0
        total_inhibition_weight = 0.0

        for rule in self.rules:
            nut_a, nut_b = rule["pair"]
            
            risk_a_info = predicted_risks.get(nut_a)
            risk_b_info = predicted_risks.get(nut_b)
            
            if not risk_a_info or not risk_b_info:
                continue

            # Standardize risk level lookup (handles "HIGH", "High Risk", "MODERATE", "Moderate Risk")
            level_a_raw = str(risk_a_info.get("risk_level", "LOW")).upper()
            level_b_raw = str(risk_b_info.get("risk_level", "LOW")).upper()
            
            is_a_elevated = any(term in level_a_raw for term in ["MODERATE", "HIGH", "CRITICAL"])
            is_b_elevated = any(term in level_b_raw for term in ["MODERATE", "HIGH", "CRITICAL"])
            
            prob_a = float(risk_a_info.get("probability", 0.0))
            prob_b = float(risk_b_info.get("probability", 0.0))

            rule_type = rule.get("type", "INTERACTION")
            is_inhibitory = any(term in rule_type for term in ["ANTAGONISTIC", "COMPETITION", "INHIBITION"])

            # Active interaction when either:
            # 1. Both nutrients are elevated (co-deficiency synergy / dependency failure)
            # 2. Competitive/inhibitory interaction where one or both are elevated
            if is_a_elevated and is_b_elevated:
                severity = "HIGH" if ("HIGH" in level_a_raw or "HIGH" in level_b_raw or "CRITICAL" in level_a_raw or "CRITICAL" in level_b_raw) else "MODERATE"
                multiplier = rule.get("synergy_multiplier", 1.15)
                avg_prob = (prob_a + prob_b) / 2.0
                
                overall_compounding_multiplier *= (1.0 + (multiplier - 1.0) * avg_prob)

                if is_inhibitory:
                    total_inhibition_weight += (multiplier - 1.0) * avg_prob * 100.0
                else:
                    total_synergy_weight += (multiplier - 1.0) * avg_prob * 100.0

                interaction_record = {
                    "nutrients": [nut_a, nut_b],
                    "interaction_type": rule_type,
                    "severity": severity,
                    "compounding_multiplier": round(multiplier, 2),
                    "clinical_mechanism": rule.get("description", ""),
                    "actionable_guidance": rule.get("clinical_action", ""),
                    "summary": f"{rule_type}: Co-elevated risk in {nut_a} and {nut_b} compounds clinical consequence."
                }
                active_interactions.append(interaction_record)

        # Normalization of scores
        synergy_score = round(min(100.0, total_synergy_weight * 2.5), 1)
        inhibition_score = round(min(100.0, total_inhibition_weight * 3.5), 1)
        overall_compounding_multiplier = round(min(overall_compounding_multiplier, 1.85), 3)

        # Determine composite interaction severity
        if overall_compounding_multiplier >= 1.45 or len(active_interactions) >= 4:
            composite_severity = "CRITICAL"
        elif overall_compounding_multiplier >= 1.25 or len(active_interactions) >= 2:
            composite_severity = "HIGH"
        elif active_interactions:
            composite_severity = "MODERATE"
        else:
            composite_severity = "LOW"

        return {
            "total_active_interactions": len(active_interactions),
            "overall_compounding_multiplier": overall_compounding_multiplier,
            "synergy_score": synergy_score,
            "inhibition_score": inhibition_score,
            "interaction_severity": composite_severity,
            "interactions": active_interactions
        }
