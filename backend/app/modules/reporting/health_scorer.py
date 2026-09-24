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
        Computes composite clinical health score based on:
        1. Multi-nutrient predicted risk severities
        2. Direct clinical biomarker derangement penalties
        3. Direct symptom burden and severity deductions
        4. Biochemical nutrient interaction compounding
        5. Behavioral and lifestyle risk factors
        Enforces strict clinical stratification ceilings:
        - Healthy: > 90
        - Mild Deficiency: 70 - 90
        - Moderate Deficiency: 50 - 70
        - Severe Deficiency: < 50
        - Critical Deficiency: < 30
        """
        baseline_score = 100.0
        patient_data = patient_data or {}
        interaction_analysis = interaction_analysis or {}

        # -------------------------------------------------------------
        # 1. Nutrient Risk Deductions (Direct Clinical Impact)
        # -------------------------------------------------------------
        high_risk_count = 0
        moderate_risk_count = 0
        raw_nutrient_pts = 0.0

        for pred in nutrient_predictions:
            if hasattr(pred, "model_dump"):
                pred_dict = pred.model_dump()
            elif isinstance(pred, dict):
                pred_dict = pred
            else:
                pred_dict = getattr(pred, "__dict__", {})

            level = str(pred_dict.get("risk_tier", pred_dict.get("risk_level", "LOW"))).upper()
            prob = float(pred_dict.get("calibrated_probability", pred_dict.get("probability", pred_dict.get("deficiency_probability", 0.0))))
            if "SEVERE" in level or "HIGH" in level:
                high_risk_count += 1
                raw_nutrient_pts += 15.0 * max(prob, 0.70)
            elif "MODERATE" in level:
                moderate_risk_count += 1
                raw_nutrient_pts += 6.0 * max(prob, 0.45)

        total_deficiencies = high_risk_count + moderate_risk_count
        # Multi-deficiency compounding penalty: each deficiency beyond 2 adds 5.0 pts
        if total_deficiencies >= 3:
            raw_nutrient_pts += (total_deficiencies - 2) * 5.0

        # -------------------------------------------------------------
        # 2. Direct Clinical Biomarker Derangement Penalty
        # -------------------------------------------------------------
        biomarkers = patient_data.get("biomarkers", {})
        if not isinstance(biomarkers, dict):
            biomarkers = {}

        norm_bio = {}
        for k, v in biomarkers.items():
            k_clean = str(k).lower().strip().replace("-", "_").replace(" ", "_")
            if v is not None:
                try:
                    norm_bio[k_clean] = float(v)
                except (ValueError, TypeError):
                    pass

        # Canonical aliases
        if "vitamin_d" in norm_bio and "serum_25ohd" not in norm_bio: norm_bio["serum_25ohd"] = norm_bio["vitamin_d"]
        if "ferritin" in norm_bio and "serum_ferritin" not in norm_bio: norm_bio["serum_ferritin"] = norm_bio["ferritin"]
        if "iron" in norm_bio and "serum_ferritin" not in norm_bio: norm_bio["serum_ferritin"] = norm_bio["iron"]
        if "vitamin_b12" in norm_bio and "serum_b12" not in norm_bio: norm_bio["serum_b12"] = norm_bio["vitamin_b12"]
        if "b12" in norm_bio and "serum_b12" not in norm_bio: norm_bio["serum_b12"] = norm_bio["b12"]
        if "calcium" in norm_bio and "serum_calcium" not in norm_bio: norm_bio["serum_calcium"] = norm_bio["calcium"]
        if "folate" in norm_bio and "rbc_folate" not in norm_bio: norm_bio["rbc_folate"] = norm_bio["folate"]
        if "magnesium" in norm_bio and "serum_magnesium" not in norm_bio: norm_bio["serum_magnesium"] = norm_bio["magnesium"]
        if "potassium" in norm_bio and "serum_potassium" not in norm_bio: norm_bio["serum_potassium"] = norm_bio["potassium"]

        critical_biomarkers_count = 0
        deficient_biomarkers_count = 0
        biomarker_penalty = 0.0

        # Vit D
        if "serum_25ohd" in norm_bio:
            v = norm_bio["serum_25ohd"]
            if v < 10.0:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 20.0:
                deficient_biomarkers_count += 1
                biomarker_penalty += 9.0

        # Ferritin
        if "serum_ferritin" in norm_bio:
            v = norm_bio["serum_ferritin"]
            if v < 10.0:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 15.0:
                deficient_biomarkers_count += 1
                biomarker_penalty += 9.0

        # B12
        if "serum_b12" in norm_bio:
            v = norm_bio["serum_b12"]
            if v < 150.0:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 200.0:
                deficient_biomarkers_count += 1
                biomarker_penalty += 9.0

        # Calcium
        if "serum_calcium" in norm_bio:
            v = norm_bio["serum_calcium"]
            if v < 8.5:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 8.8:
                deficient_biomarkers_count += 1
                biomarker_penalty += 9.0

        # Folate
        if "rbc_folate" in norm_bio:
            v = norm_bio["rbc_folate"]
            if v < 250.0:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 400.0:
                deficient_biomarkers_count += 1
                biomarker_penalty += 8.0

        # Potassium
        if "serum_potassium" in norm_bio:
            v = norm_bio["serum_potassium"]
            if v < 3.5:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 3.8:
                deficient_biomarkers_count += 1
                biomarker_penalty += 8.0

        # Magnesium
        if "serum_magnesium" in norm_bio:
            v = norm_bio["serum_magnesium"]
            if v < 1.6:
                critical_biomarkers_count += 1
                biomarker_penalty += 18.0
            elif v < 1.9:
                deficient_biomarkers_count += 1
                biomarker_penalty += 8.0

        # -------------------------------------------------------------
        # 3. Direct Symptom Burden and Severity Penalty
        # -------------------------------------------------------------
        symptoms = patient_data.get("symptoms", {})
        if not isinstance(symptoms, dict):
            symptoms = {}

        sym_vals = []
        for k, v in symptoms.items():
            try:
                sym_vals.append(float(v))
            except (ValueError, TypeError):
                pass
        
        # Check flat symptoms if present
        for k in ["fatigue", "bone_pain", "muscle_weakness", "hair_loss", "brain_fog", "pale_skin", "cold_intolerance", "muscle_cramps", "tingling_numbness"]:
            if f"symptom_{k}" in patient_data:
                try:
                    sym_vals.append(float(patient_data[f"symptom_{k}"]))
                except (ValueError, TypeError):
                    pass

        total_burden = sum(sym_vals)
        max_symptom = max(sym_vals) if sym_vals else 0.0
        severe_symptoms_count = sum(1 for v in sym_vals if v >= 7.0)

        symptom_penalty = 0.0
        if total_burden >= 35.0 or severe_symptoms_count >= 3 or max_symptom >= 8.5:
            symptom_penalty = min(28.0, 16.0 + total_burden * 0.3)
        elif total_burden >= 20.0 or severe_symptoms_count >= 2 or max_symptom >= 7.0:
            symptom_penalty = min(20.0, 10.0 + total_burden * 0.25)
        elif total_burden >= 10.0 or severe_symptoms_count >= 1:
            symptom_penalty = min(12.0, 5.0 + total_burden * 0.2)
        elif total_burden > 0:
            symptom_penalty = min(6.0, total_burden * 0.4)

        total_nutrient_deduction = round(raw_nutrient_pts + biomarker_penalty + symptom_penalty, 1)

        # -------------------------------------------------------------
        # 4. Nutrient Interaction Compounding Penalty (up to 15 points)
        # -------------------------------------------------------------
        active_interactions = interaction_analysis.get("interactions", [])
        interaction_penalty = 0.0
        for item in active_interactions:
            sev = str(item.get("severity", "MODERATE")).upper()
            if "HIGH" in sev or "SEVERE" in sev:
                interaction_penalty += 4.5
            else:
                interaction_penalty += 2.5

        multiplier = float(interaction_analysis.get("overall_compounding_multiplier", 1.0))
        if multiplier > 1.1:
            interaction_penalty += (multiplier - 1.0) * 10.0

        interaction_penalty = min(15.0, round(interaction_penalty, 1))

        # -------------------------------------------------------------
        # 5. Controlled Lifestyle Adjustment (-45.0 to +5.0 points)
        # -------------------------------------------------------------
        positive_bonus = 0.0
        hazard_deductions = 0.0
        protective_factor_count = 0
        severe_lifestyle_hazard_count = 0

        diet_info = patient_data.get("dietary_habits", {})
        if not isinstance(diet_info, dict): diet_info = {}
        life_info = patient_data.get("lifestyle_factors", {})
        if not isinstance(life_info, dict): life_info = {}

        # Water intake
        water = float(patient_data.get("water_intake_liters", diet_info.get("water_intake_liters", 2.0)))
        if water >= 2.5:
            positive_bonus += 1.5
            protective_factor_count += 1
        elif water < 1.2:
            hazard_deductions -= 3.0

        # Sunlight exposure
        sunlight = float(patient_data.get("sunlight_exposure_min_per_day", life_info.get("sunlight_exposure_min_per_day", 25)))
        if sunlight >= 30:
            positive_bonus += 1.5
            protective_factor_count += 1
        elif sunlight < 15:
            hazard_deductions -= 3.5

        # Sleep duration
        sleep = float(patient_data.get("sleep_hours_per_night", life_info.get("sleep_hours_per_night", 7.0)))
        if 7.0 <= sleep <= 9.0:
            positive_bonus += 1.5
            protective_factor_count += 1
        elif sleep < 5.0:
            hazard_deductions -= 8.0
            severe_lifestyle_hazard_count += 1
        elif sleep < 6.0 or sleep > 10.0:
            hazard_deductions -= 3.5

        # Stress level
        stress = float(patient_data.get("stress_level", life_info.get("stress_level", 5)))
        if stress <= 3:
            positive_bonus += 1.5
            protective_factor_count += 1
        elif stress >= 8:
            hazard_deductions -= 8.0
            severe_lifestyle_hazard_count += 1
        elif stress >= 7:
            hazard_deductions -= 4.0

        # Physical activity
        activity = str(patient_data.get("activity_level", life_info.get("activity_level", "MODERATE"))).upper()
        if "VERY" in activity or "HIGH" in activity:
            positive_bonus += 1.0
            protective_factor_count += 1
        elif "SEDENTARY" in activity:
            hazard_deductions -= 2.0

        # Produce
        produce = float(patient_data.get("daily_fruit_vegetable_servings", diet_info.get("daily_fruit_vegetable_servings", 3)))
        if produce >= 4.0:
            positive_bonus += 1.5
            protective_factor_count += 1
        elif produce <= 1.0:
            hazard_deductions -= 6.0
            severe_lifestyle_hazard_count += 1

        # Tobacco / Alcohol
        smoking = str(patient_data.get("smoking_status", life_info.get("smoking_status", "NEVER"))).upper()
        if any(k in smoking for k in ["DAILY", "CURRENT", "REGULAR", "HEAVY", "YES"]):
            hazard_deductions -= 10.0
            severe_lifestyle_hazard_count += 1
        elif "FORMER" in smoking:
            hazard_deductions -= 2.0
        elif "NEVER" in smoking:
            protective_factor_count += 1

        alcohol = str(patient_data.get("alcohol_consumption", life_info.get("alcohol_consumption", "NONE"))).upper()
        if any(k in alcohol for k in ["DAILY", "HEAVY", "FREQUENT"]):
            hazard_deductions -= 10.0
            severe_lifestyle_hazard_count += 1
        elif "MODERATE" in alcohol:
            hazard_deductions -= 3.0
        elif "NONE" in alcohol:
            protective_factor_count += 1

        # Compounding multiplier if 3+ severe lifestyle hazards co-occur
        if severe_lifestyle_hazard_count >= 3:
            hazard_deductions = hazard_deductions * 1.25

        hazard_deductions = max(-45.0, round(hazard_deductions, 1))

        # Hard Clinical Gate: If high deficiencies, critical biomarkers, severe lifestyle hazard,
        # or non-trivial symptoms exist, NO positive lifestyle bonus is permitted
        if high_risk_count > 0 or critical_biomarkers_count > 0 or severe_lifestyle_hazard_count > 0 or total_burden >= 10.0:
            positive_bonus = 0.0
        else:
            positive_bonus = min(5.0, round(positive_bonus, 1))

        lifestyle_modifier = round(hazard_deductions + positive_bonus, 1)
        lifestyle_modifier = max(-45.0, min(5.0, lifestyle_modifier))

        # -------------------------------------------------------------
        # 6. Composite Score & Strict Clinical Stratification Ceilings
        # -------------------------------------------------------------
        raw_score = baseline_score - total_nutrient_deduction - interaction_penalty + lifestyle_modifier

        # Mandatory Clinical Ceilings enforcing Phase 11 Acceptance Criteria
        if high_risk_count >= 3 or critical_biomarkers_count >= 2:
            # Critical Deficiency: Must be < 30
            final_score = min(28, int(raw_score))
        elif high_risk_count >= 2 or critical_biomarkers_count >= 1:
            # Severe Deficiency: Must be < 50
            final_score = min(48, int(raw_score))
        elif high_risk_count >= 1 or moderate_risk_count >= 2:
            # Moderate Deficiency: Must be capped at 68
            final_score = min(68, int(raw_score))
        elif moderate_risk_count >= 1:
            # Mild Deficiency: Must be capped at 88
            final_score = min(88, int(raw_score))
        elif total_burden >= 15.0 or severe_lifestyle_hazard_count >= 2:
            # Symptomatic or severe lifestyle degradation: Capped at 85, no artificial floor!
            final_score = min(85, int(raw_score))
        else:
            # Truly Healthy: Can reach up to 100
            final_score = min(100, int(raw_score))

        final_score = int(max(5, min(100, final_score)))

        # Standardized Category Tiering
        if final_score >= 90:
            category = HealthScoreCategoryEnum.EXCELLENT
            interpretation = (
                "Excellent nutritional status (90–100). Biomarker indicators and physiological habits show robust "
                "micronutrient resilience with minimal risk of acute or subclinical deficiencies."
            )
        elif final_score >= 70:
            category = HealthScoreCategoryEnum.GOOD
            interpretation = (
                "Mild isolated nutritional vulnerability (70–89). Subclinical depletion detected; targeted dietary "
                "adjustments and lifestyle optimization will reinforce physiological balance."
            )
        elif final_score >= 50:
            category = HealthScoreCategoryEnum.MODERATE_RISK
            interpretation = (
                "Moderate nutritional vulnerability detected (50–69). Multiple micronutrients show elevated depletion risk, "
                "exacerbated by clinical symptoms or biochemical interactions. Actionable dietary recovery recommended."
            )
        elif final_score >= 30:
            category = HealthScoreCategoryEnum.HIGH_RISK
            interpretation = (
                "Severe nutritional risk (< 50). Elevated deficiency probabilities identified across essential micronutrients. "
                "Prioritized clinical recovery roadmap and targeted nutritional interventions advised."
            )
        else:
            category = HealthScoreCategoryEnum.CRITICAL
            interpretation = (
                "Critical nutritional deficiency state (< 30). Severe single or multiple co-occurring deficiencies detected "
                "with compounding biochemical risks. Immediate clinical consultation and confirmatory lab workup recommended."
            )

        return HealthScoreBreakdown(
            baseline_score=baseline_score,
            nutrient_risk_deduction=total_nutrient_deduction,
            interaction_penalty=interaction_penalty,
            lifestyle_modifier=lifestyle_modifier,
            confidence_adjustment=0.0,
            deficiency_count=total_deficiencies,
            protective_factor_count=protective_factor_count,
            final_score=final_score,
            category=category,
            interpretation=interpretation
        )

