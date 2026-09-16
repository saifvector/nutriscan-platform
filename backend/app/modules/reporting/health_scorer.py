"""
Overall Nutritional Health Scorer Engine
Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Calculates a standardized clinical Nutritional Health Score (0-100):
- 85 - 100: EXCELLENT (Optimal micronutrient status & protective lifestyle)
- 70 - 84:  GOOD (Minor subclinical risks, solid baseline)
- 50 - 69:  MODERATE_RISK (Multiple elevated nutrient deficiency risks, lifestyle bottlenecks)
- 0 - 49:   HIGH_RISK (Severe single or multiple co-occurring deficiencies, urgent intervention)

Synthesizes:
1. Multi-nutrient predicted probabilities & risk severities across all 11 nutrients
2. Compound penalties from biochemical nutrient interactions
3. Net modifiers from positive/negative lifestyle & dietary habits
"""

from typing import Dict, Any, List, Optional
from ...schemas.report import HealthScoreBreakdown, HealthScoreCategoryEnum


class OverallNutritionalHealthScorer:
    """
    Computes a standardized 0-100 overall nutritional health score with clinical transparency.
    """

    @classmethod
    def calculate_health_score(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        interaction_analysis: Optional[Dict[str, Any]] = None,
        patient_data: Optional[Dict[str, Any]] = None
    ) -> HealthScoreBreakdown:
        """
        Computes composite health score:
        S = max(0, min(100, round(100 - P_nutrients - P_interactions + M_lifestyle)))
        """
        baseline_score = 100.0
        patient_data = patient_data or {}
        interaction_analysis = interaction_analysis or {}

        # -------------------------------------------------------------
        # 1. Nutrient Risk Deductions & Confidence Weighting (up to 55 points)
        # -------------------------------------------------------------
        raw_nutrient_deduction = 0.0
        deficiency_count = 0
        confidence_adjustment = 0.0

        total_evaluated = len(nutrient_predictions)
        scale_factor = 11.0 / max(total_evaluated, 11.0) if total_evaluated > 0 else 1.0

        for pred in nutrient_predictions:
            prob = float(pred.get("probability", 0.0))
            level = str(pred.get("risk_level", "LOW")).upper()
            conf_str = str(pred.get("confidence_level", "HIGH")).upper()
            conf_val = float(pred.get("confidence_score", 0.85 if "HIGH" in conf_str else (0.65 if "MED" in conf_str else 0.45)))

            # Severity-weighted point factor (scaled for total monitored nutrients)
            if "SEVERE" in level:
                base_weight = 14.0 * scale_factor
                deficiency_count += 1
            elif "HIGH" in level:
                base_weight = 10.5 * scale_factor
                deficiency_count += 1
            elif "MODERATE" in level:
                base_weight = 5.0 * scale_factor
                if prob >= 0.40:
                    deficiency_count += 1
            else:
                base_weight = 1.0 * scale_factor

            # Confidence weighting factor (0.70 to 1.0)
            confidence_factor = 1.0 if conf_val >= 0.80 else (0.85 if conf_val >= 0.60 else 0.70)
            nominal_deduction = prob * base_weight
            weighted_deduction = nominal_deduction * confidence_factor
            
            confidence_adjustment += (nominal_deduction - weighted_deduction)
            raw_nutrient_deduction += weighted_deduction

        # Multi-deficiency compounding penalty: each deficiency beyond 3 adds 1.2 pts
        if deficiency_count > 3:
            raw_nutrient_deduction += (deficiency_count - 3) * 1.2

        # Normalize nutrient risk deduction: max 55 points
        nutrient_risk_deduction = min(55.0, round(raw_nutrient_deduction, 1))
        confidence_adjustment = round(confidence_adjustment, 1)

        # -------------------------------------------------------------
        # 2. Nutrient Interaction Compounding Penalty (P_interactions, up to 15 points)
        # -------------------------------------------------------------
        active_interactions = interaction_analysis.get("interactions", [])
        interaction_penalty = 0.0
        for item in active_interactions:
            sev = str(item.get("severity", "MODERATE")).upper()
            if "HIGH" in sev or "SEVERE" in sev:
                interaction_penalty += 4.5
            else:
                interaction_penalty += 2.5

        # Also account for compounding multiplier if > 1.0
        multiplier = float(interaction_analysis.get("overall_compounding_multiplier", 1.0))
        if multiplier > 1.1:
            interaction_penalty += (multiplier - 1.0) * 10.0

        interaction_penalty = min(15.0, round(interaction_penalty, 1))

        # -------------------------------------------------------------
        # 3. Lifestyle & Protective Factors (M_lifestyle, -20 to +18 points)
        # -------------------------------------------------------------
        lifestyle_modifier = 0.0
        protective_factor_count = 0

        # Flatten nested diet/lifestyle structures if present
        diet_info = patient_data.get("dietary_habits", {})
        if not isinstance(diet_info, dict):
            diet_info = {}
        life_info = patient_data.get("lifestyle_factors", {})
        if not isinstance(life_info, dict):
            life_info = {}

        # Water intake
        water = float(patient_data.get("water_intake_liters", diet_info.get("water_intake_liters", 2.0)))
        if water >= 2.5:
            lifestyle_modifier += 3.0
            protective_factor_count += 1
        elif water < 1.2:
            lifestyle_modifier -= 4.0

        # Sunlight exposure
        sunlight = float(patient_data.get("sunlight_exposure_min_per_day", life_info.get("sunlight_exposure_min_per_day", 20)))
        if sunlight >= 30:
            lifestyle_modifier += 3.0
            protective_factor_count += 1
        elif sunlight < 15:
            lifestyle_modifier -= 4.0

        # Sleep duration
        sleep = float(patient_data.get("sleep_hours_per_night", life_info.get("sleep_hours_per_night", 7.0)))
        if 7.0 <= sleep <= 9.0:
            lifestyle_modifier += 3.0
            protective_factor_count += 1
        elif sleep < 6.0 or sleep > 10.0:
            lifestyle_modifier -= 3.5

        # Stress level (1 to 10)
        stress = float(patient_data.get("stress_level", life_info.get("stress_level", 5)))
        if stress <= 3:
            lifestyle_modifier += 2.5
            protective_factor_count += 1
        elif stress >= 7:
            lifestyle_modifier -= 4.0

        # Physical activity
        activity = str(patient_data.get("activity_level", life_info.get("activity_level", "MODERATE"))).upper()
        if "VERY" in activity or "HIGH" in activity or "ATHLETE" in activity:
            lifestyle_modifier += 3.0
            protective_factor_count += 1
        elif "SEDENTARY" in activity:
            lifestyle_modifier -= 3.0

        # Fruit/Vegetable intake
        produce = float(patient_data.get("daily_fruit_vegetable_servings", diet_info.get("daily_fruit_vegetable_servings", 3)))
        if produce >= 4.0:
            lifestyle_modifier += 3.5
            protective_factor_count += 1
        elif produce <= 1.0:
            lifestyle_modifier -= 4.5

        # Tobacco / Alcohol
        smoking = str(patient_data.get("smoking_status", life_info.get("smoking_status", "NEVER"))).upper()
        if "CURRENT" in smoking or "DAILY" in smoking:
            lifestyle_modifier -= 4.0
        elif "NEVER" in smoking:
            protective_factor_count += 1

        alcohol = str(patient_data.get("alcohol_consumption", life_info.get("alcohol_consumption", "NONE"))).upper()
        if "HEAVY" in alcohol:
            lifestyle_modifier -= 4.0
        elif "NONE" in alcohol:
            protective_factor_count += 1

        lifestyle_modifier = max(-20.0, min(18.0, round(lifestyle_modifier, 1)))

        # -------------------------------------------------------------
        # 4. Standardized 5-Tier Classification (0-100)
        # -------------------------------------------------------------
        net_score = baseline_score - nutrient_risk_deduction - interaction_penalty + lifestyle_modifier
        final_score = int(max(0, min(100, round(net_score))))

        if final_score >= 90:
            category = HealthScoreCategoryEnum.EXCELLENT
            interpretation = (
                "Excellent nutritional status (90–100). Biomarker indicators and behavioral habits show robust "
                "micronutrient resilience with minimal risk of acute or subclinical deficiencies."
            )
        elif final_score >= 75:
            category = HealthScoreCategoryEnum.GOOD
            interpretation = (
                "Good nutritional foundation (75–89). Mild isolated risk factors identified; targeted dietary adjustments "
                "and lifestyle optimization will reinforce long-term physiological homeostasis."
            )
        elif final_score >= 60:
            category = HealthScoreCategoryEnum.MODERATE_RISK
            interpretation = (
                "Moderate nutritional vulnerability detected (60–74). Multiple micronutrients show elevated depletion risk, "
                "exacerbated by lifestyle stressors or biochemical interactions. Actionable dietary recovery recommended."
            )
        elif final_score >= 40:
            category = HealthScoreCategoryEnum.HIGH_RISK
            interpretation = (
                "High nutritional risk (40–59). Elevated deficiency probabilities identified across essential micronutrients. "
                "Prioritized clinical recovery roadmap and targeted nutritional interventions advised."
            )
        else:
            category = HealthScoreCategoryEnum.CRITICAL
            interpretation = (
                "Critical nutritional deficiency state (0–39). Severe single or multiple co-occurring deficiencies detected "
                "with compounding biochemical risks. Immediate clinical consultation and confirmatory lab workup recommended."
            )

        return HealthScoreBreakdown(
            baseline_score=baseline_score,
            nutrient_risk_deduction=nutrient_risk_deduction,
            interaction_penalty=interaction_penalty,
            lifestyle_modifier=lifestyle_modifier,
            confidence_adjustment=confidence_adjustment,
            deficiency_count=deficiency_count,
            protective_factor_count=protective_factor_count,
            final_score=final_score,
            category=category,
            interpretation=interpretation
        )

