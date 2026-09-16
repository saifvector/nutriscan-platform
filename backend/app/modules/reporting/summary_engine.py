"""
Assessment Summary Engine
Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Consolidates patient screening inputs, prediction outputs, explainability insights,
and lifestyle parameters into an executive clinical summary:
- Assessment Date & User Profile (Demographics, BMI, Dietary Pattern)
- Key Clinical Findings
- Top Risk Nutrients
- Protective Counterbalance Factors
- Critical Lifestyle Bottlenecks
- Executive Summary Narrative
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from ...schemas.report import AssessmentSummary


class AssessmentSummaryEngine:
    """
    Synthesizes structured clinical assessments and high-level summaries for patients and clinicians.
    """

    @classmethod
    def generate_summary(
        cls,
        patient_data: Dict[str, Any],
        nutrient_predictions: List[Dict[str, Any]],
        explainability_data: Optional[Dict[str, Any]] = None,
        health_score: Optional[int] = None,
        health_category: Optional[str] = None
    ) -> AssessmentSummary:
        """
        Synthesizes complete assessment summary.
        """
        now = datetime.utcnow()
        explainability_data = explainability_data or {}

        # 1. Demographics & Profile
        age = patient_data.get("age", 30)
        gender = str(patient_data.get("gender", "UNKNOWN")).upper()
        height = float(patient_data.get("height_cm", 170.0))
        weight = float(patient_data.get("weight_kg", 68.0))
        height_m = height / 100.0
        bmi = round(weight / (height_m * height_m), 1) if height_m > 0 else 22.0

        if bmi < 18.5:
            bmi_cat = "Underweight"
        elif bmi < 25.0:
            bmi_cat = "Normal Weight"
        elif bmi < 30.0:
            bmi_cat = "Overweight"
        else:
            bmi_cat = "Obese"

        diet_habits = patient_data.get("dietary_habits", {})
        if not isinstance(diet_habits, dict):
            diet_habits = {}
        dietary_pattern = str(patient_data.get("dietary_pattern", diet_habits.get("dietary_pattern", "OMNIVORE"))).upper()

        user_profile = {
            "age": age,
            "gender": gender,
            "height_cm": height,
            "weight_kg": weight,
            "bmi": bmi,
            "bmi_category": bmi_cat,
            "dietary_pattern": dietary_pattern
        }

        # 2. Top Risk Nutrients
        sorted_preds = sorted(
            nutrient_predictions,
            key=lambda x: (
                2 if str(x.get("risk_level", "")).upper() in ["HIGH", "SEVERE"] else
                (1 if str(x.get("risk_level", "")).upper() == "MODERATE" else 0),
                float(x.get("probability", 0.0))
            ),
            reverse=True
        )
        top_risk_nutrients = [
            p["nutrient"] for p in sorted_preds
            if str(p.get("risk_level", "")).upper() in ["HIGH", "SEVERE", "MODERATE"]
        ]
        if not top_risk_nutrients:
            top_risk_nutrients = [p["nutrient"] for p in sorted_preds[:2]]

        # 3. Protective Factors
        protective_factors = []
        life_info = patient_data.get("lifestyle_factors", {})
        if not isinstance(life_info, dict):
            life_info = {}

        produce = float(patient_data.get("daily_fruit_vegetable_servings", diet_habits.get("daily_fruit_vegetable_servings", 3)))
        if produce >= 3.0:
            protective_factors.append(f"Regular fresh fruit & vegetable intake ({produce:.1f} servings/day) supports antioxidant defense")

        water = float(patient_data.get("water_intake_liters", diet_info.get("water_intake_liters", 2.0) if "diet_info" in locals() else diet_habits.get("water_intake_liters", 2.0)))
        if water >= 2.0:
            protective_factors.append(f"Adequate hydration baseline ({water:.1f} L/day) aids water-soluble vitamin bioavailability")

        sleep = float(patient_data.get("sleep_hours_per_night", life_info.get("sleep_hours_per_night", 7.0)))
        if 7.0 <= sleep <= 9.0:
            protective_factors.append(f"Restorative sleep duration ({sleep:.1f} hrs/night) preserves cellular micronutrient retention")

        activity = str(patient_data.get("activity_level", life_info.get("activity_level", "MODERATE"))).upper()
        if "SEDENTARY" not in activity:
            protective_factors.append(f"Active physical exercise routine ({activity.capitalize()}) enhances musculoskeletal turnover")

        if not protective_factors:
            protective_factors.append("Consistent daily meal timing provides predictable baseline caloric intake")

        # 4. Critical Lifestyle Bottlenecks
        critical_lifestyle_factors = []
        sunlight = float(patient_data.get("sunlight_exposure_min_per_day", life_info.get("sunlight_exposure_min_per_day", 20)))
        if sunlight < 20:
            critical_lifestyle_factors.append(f"Sub-optimal sunlight exposure ({sunlight:.0f} min/day) limits dermal endogenous Vitamin D3 synthesis")

        stress = float(patient_data.get("stress_level", life_info.get("stress_level", 5)))
        if stress >= 6:
            critical_lifestyle_factors.append(f"Elevated chronic stress (level {stress:.0f}/10) accelerates renal excretion of magnesium and zinc")

        if "SEDENTARY" in activity:
            critical_lifestyle_factors.append("Sedentary lifestyle dampens bone mineral remodeling and metabolic circulation")

        smoking = str(patient_data.get("smoking_status", life_info.get("smoking_status", "NEVER"))).upper()
        if "CURRENT" in smoking or "DAILY" in smoking:
            critical_lifestyle_factors.append("Active tobacco smoking increases ascorbic acid (Vitamin C) metabolic oxidation turnover")

        if not critical_lifestyle_factors:
            critical_lifestyle_factors.append("No critical behavioral lifestyle bottlenecks detected")

        # 5. Key Clinical Findings
        score_str = f"{health_score}/100 ({health_category})" if health_score is not None else "Evaluated"
        key_findings = [
            f"Overall Nutritional Health Score stands at {score_str}.",
            f"Primary micronutrient vulnerabilities identified: {', '.join(top_risk_nutrients[:3])}.",
            f"Screening reflects a {dietary_pattern.capitalize()} dietary structure with BMI of {bmi:.1f} ({bmi_cat})."
        ]
        if len(top_risk_nutrients) >= 3:
            key_findings.append(f"Multi-nutrient co-depletion detected across {len(top_risk_nutrients)} essential vitamins and minerals.")
        else:
            key_findings.append("Micronutrient status remains relatively focused with localized opportunities for dietary optimization.")

        # 6. Executive Summary Narrative
        executive_summary_text = (
            f"Comprehensive screening conducted on {now.strftime('%B %d, %Y')} for a {age}-year-old {gender.lower()} "
            f"following a {dietary_pattern.capitalize()} dietary pattern (BMI: {bmi:.1f} - {bmi_cat}). "
            f"The assessment yields an Overall Nutritional Health Score of {score_str}. "
            f"High-priority nutritional surveillance is indicated for {', '.join(top_risk_nutrients[:3])}. "
            f"Protective habits including {protective_factors[0].lower() if protective_factors else 'baseline nutrition'} provide resilience, "
            f"while interventions targeting {critical_lifestyle_factors[0].lower() if critical_lifestyle_factors else 'lifestyle factors'} "
            f"will optimize systemic nutrient absorption and long-term vitality."
        )

        return AssessmentSummary(
            assessment_date=now,
            user_profile=user_profile,
            key_findings=key_findings,
            top_risk_nutrients=top_risk_nutrients,
            protective_factors=protective_factors,
            critical_lifestyle_factors=critical_lifestyle_factors,
            executive_summary_text=executive_summary_text
        )
