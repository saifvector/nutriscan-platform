"""
Risk Scoring & Clinical Prioritization Framework
Phase 2: Dataset Engineering and Machine Learning Foundation

Calculates:
1. Individual Nutrient Risk Scores (0 - 100)
2. Overall Nutritional Risk Score (0 - 100) with clinical urgency weighting & interaction multipliers
3. Nutrient Priority Ranking (clinical triaging)
4. Overall Severity Classification (LOW, MODERATE, HIGH, CRITICAL)
"""

from typing import Dict, Any, List
import numpy as np
from .constants import CLINICAL_URGENCY_WEIGHTS, RiskCategory, OverallSeverity


class NutritionalRiskScorer:
    """
    Computes calibrated continuous risk scores and priority triage ranks
    for nutritional screening outcomes.
    """

    SEVERITY_THRESHOLDS = {
        OverallSeverity.LOW: (0.0, 29.9),
        OverallSeverity.MODERATE: (30.0, 64.9),
        OverallSeverity.HIGH: (65.0, 84.9),
        OverallSeverity.CRITICAL: (85.0, 100.0)
    }

    @classmethod
    def calculate_individual_score(
        cls,
        class_probs: np.ndarray,
        predicted_class: int
    ) -> float:
        """
        Derives a smooth 0-100 continuous score from the 3-class probability distribution:
        class 0 (Low): weight 0
        class 1 (Moderate): weight 50
        class 2 (High): weight 100
        """
        if len(class_probs) == 3:
            p_low, p_mod, p_high = class_probs[0], class_probs[1], class_probs[2]
            score = (p_mod * 50.0) + (p_high * 100.0)
        else:
            # Fallback if binary probability provided
            score = float(class_probs[-1] * 100.0)
            
        return round(float(np.clip(score, 0.0, 100.0)), 1)

    @classmethod
    def calculate_confidence(cls, class_probs: np.ndarray) -> tuple[float, str]:
        """
        Calculates mathematical prediction confidence and categorizes:
        - 'High Confidence' (>= 0.75)
        - 'Medium Confidence' (0.50 - 0.74)
        - 'Low Confidence' (< 0.50)
        Derived from normalized Shannon Entropy complement and top probability margin.
        """
        probs = np.clip(np.array(class_probs, dtype=float), 1e-7, 1.0)
        probs = probs / np.sum(probs)

        # 1. Entropy-based certainty (1 - H/H_max)
        num_classes = len(probs)
        if num_classes > 1:
            h_max = np.log2(num_classes)
            entropy = -np.sum(probs * np.log2(probs))
            c_entropy = max(0.0, 1.0 - (entropy / h_max))
        else:
            c_entropy = 1.0

        # 2. Probability Margin between top-1 and top-2
        sorted_probs = np.sort(probs)[::-1]
        top1 = sorted_probs[0]
        top2 = sorted_probs[1] if len(sorted_probs) > 1 else 0.0
        c_margin = top1 - top2

        # 3. Composite Confidence Score
        raw_conf = (0.5 * c_entropy) + (0.5 * c_margin)
        calibrated_conf = round(float(np.clip(max(raw_conf, top1 * 0.85), 0.0, 0.99)), 2)

        if calibrated_conf >= 0.75:
            level = "High Confidence"
        elif calibrated_conf >= 0.50:
            level = "Medium Confidence"
        else:
            level = "Low Confidence"

        return calibrated_conf, level

    @classmethod
    def calculate_overall_risk(
        cls,
        individual_evaluations: List[Dict[str, Any]],
        interaction_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Aggregates individual nutrient scores into a weighted overall score,
        applies interaction compounding, and derives severity classification.
        Ranks nutrients by: Risk Level (HIGH > MODERATE > LOW) -> Probability * Urgency Weight.
        """
        if not individual_evaluations:
            return {
                "overall_risk_score": 0.0,
                "overall_severity": OverallSeverity.LOW.value,
                "priority_ranking": []
            }

        weighted_sum = 0.0
        total_weights = 0.0
        high_risk_count = 0
        moderate_risk_count = 0

        for item in individual_evaluations:
            nut = item["nutrient"]
            score = item["score"]
            weight = CLINICAL_URGENCY_WEIGHTS.get(nut, 1.0)
            
            weighted_sum += (score * weight)
            total_weights += weight

            risk_lvl = item.get("risk_level", "").upper()
            if "HIGH" in risk_lvl:
                high_risk_count += 1
            elif "MODERATE" in risk_lvl:
                moderate_risk_count += 1

        base_overall_score = weighted_sum / max(total_weights, 1.0)
        
        # Apply biochemical interaction multiplier
        compounded_score = base_overall_score * interaction_multiplier
        final_overall_score = round(float(np.clip(compounded_score, 0.0, 100.0)), 1)

        # Classify overall severity
        if final_overall_score >= 85.0 or high_risk_count >= 3:
            severity = OverallSeverity.CRITICAL.value
            overall_risk_label = "HIGH"
        elif final_overall_score >= 65.0 or high_risk_count >= 1:
            severity = OverallSeverity.HIGH.value
            overall_risk_label = "HIGH"
        elif final_overall_score >= 30.0 or moderate_risk_count >= 2:
            severity = OverallSeverity.MODERATE.value
            overall_risk_label = "MODERATE"
        else:
            severity = OverallSeverity.LOW.value
            overall_risk_label = "LOW"

        # Multi-factor Priority ranking:
        # Tier 1: Risk Level (HIGH = 3, MODERATE = 2, LOW = 1)
        # Tier 2: Probability Score * Clinical Urgency Weight
        # Tier 3: Score
        tier_map = {
            "HIGH": 3,
            "HIGH RISK": 3,
            "MODERATE": 2,
            "MODERATE RISK": 2,
            "LOW": 1,
            "LOW RISK": 1
        }

        ranked_nutrients = sorted(
            individual_evaluations,
            key=lambda x: (
                tier_map.get(str(x.get("risk_level", "")).upper(), 1),
                x.get("probability", 0.0) * CLINICAL_URGENCY_WEIGHTS.get(x["nutrient"], 1.0),
                x.get("score", 0.0)
            ),
            reverse=True
        )

        for rank_idx, item in enumerate(ranked_nutrients, start=1):
            item["priority_rank"] = rank_idx

        return {
            "overall_risk": overall_risk_label,
            "overall_risk_score": final_overall_score,
            "overall_severity": severity,
            "high_risk_deficiencies_count": high_risk_count,
            "moderate_risk_deficiencies_count": moderate_risk_count,
            "priority_ranking": ranked_nutrients
        }
