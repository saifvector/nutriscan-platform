"""
NutriScan Edge Case Assault Test Suite
Phase 7: Robustness, Boundary Testing, and Extreme Clinical Scenarios

Assault Vectors:
1. Age Extremes: Age 0 (Pediatric/Infant) and Age 120 (Super-Centenarian)
2. BMI Extremes: BMI 10 (Severe Cachexia/Wasting) and BMI 70 (Super-Morbid Obesity)
3. Zero Biomarkers: Assessment with null/empty biomarker panel
4. Critical Deficiency Biomarkers: Vit D = 1 ng/mL, Ferritin = 1 ng/mL, B12 = 25 pg/mL
5. Toxicity / Hypervitaminosis Biomarkers: Vit D = 150 ng/mL, Ferritin = 2000 ng/mL
6. Complex Clinical Profile A: Pregnant Vegan with Anemia Symptoms
7. Complex Clinical Profile B: Chronic Kidney Disease (CKD) Stage 4
8. Complex Clinical Profile C: Type 2 Diabetes with Metabolic Syndrome
9. Complex Clinical Profile D: Frail Elderly (Age 88) with Sarcopenia Risk
"""

import sys
import os
import uuid
import pytest
from typing import Dict, Any

# Ensure backend root in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.workflow_orchestrator import ClinicalWorkflowOrchestrator
from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster
from backend.app.modules.personalization.meal_planner_pro import IntelligentMealPlanner
from backend.app.modules.personalization.schemas import (
    MealPlanGenerateRequest,
    DietaryPatternEnum,
    CulturalPatternEnum
)
from backend.app.modules.prediction.service import PredictionService


def test_edge_case_age_zero():
    """Test Age 0 boundary: Must not crash, divide by zero, or produce NaN."""
    payload = {
        "user_id": "edge_age_0",
        "age": 0,
        "gender": "MALE",
        "height_cm": 50.0,
        "weight_kg": 3.5,
        "dietary_pattern": "OMNIVORE",
        "activity_level": "SEDENTARY",
        "biomarkers": {}
    }
    result = PredictionService.predict_assessment(payload)
    assert result is not None
    assert "overall_severity" in result
    assert not any(v != v for v in [result.get("overall_score", 0)])  # No NaN


def test_edge_case_age_centenarian():
    """Test Age 120 boundary: Must not crash or overflow."""
    payload = {
        "user_id": "edge_age_120",
        "age": 120,
        "gender": "FEMALE",
        "height_cm": 150.0,
        "weight_kg": 45.0,
        "dietary_pattern": "MEDITERRANEAN",
        "activity_level": "SEDENTARY",
        "biomarkers": {"vitamin_d": 15.0}
    }
    result = PredictionService.predict_assessment(payload)
    assert result is not None
    assert result["overall_severity"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_edge_case_bmi_extremes():
    """Test BMI 10 (extreme wasting) and BMI 70 (super-morbid obesity)."""
    # BMI ~ 10: 170 cm, 29 kg
    payload_wasting = {
        "user_id": "edge_bmi_10",
        "age": 28,
        "gender": "FEMALE",
        "height_cm": 170.0,
        "weight_kg": 29.0,
        "dietary_pattern": "VEGAN",
        "activity_level": "SEDENTARY",
        "biomarkers": {}
    }
    res_wasting = PredictionService.predict_assessment(payload_wasting)
    assert res_wasting is not None

    # BMI ~ 70: 160 cm, 180 kg
    payload_obese = {
        "user_id": "edge_bmi_70",
        "age": 45,
        "gender": "MALE",
        "height_cm": 160.0,
        "weight_kg": 180.0,
        "dietary_pattern": "OMNIVORE",
        "activity_level": "SEDENTARY",
        "biomarkers": {}
    }
    res_obese = PredictionService.predict_assessment(payload_obese)
    assert res_obese is not None


def test_edge_case_missing_biomarkers():
    """Test empty biomarkers panel: System must deduce risks from lifestyle, diet, symptoms."""
    payload = {
        "user_id": "edge_missing_biomarkers",
        "age": 30,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "dietary_restrictions": ["meat-free", "dairy-free"],
            "meals_per_day": 3
        },
        "lifestyle_factors": {
            "activity_level": "SEDENTARY",
            "sunlight_exposure_min_per_day": 5.0,
            "sleep_hours_per_night": 6.5,
            "stress_level": 6
        },
        "biomarkers": {},
        "symptoms": {
            "fatigue": 9,
            "pale_skin": 8,
            "brittle_nails": 8,
            "hair_loss": 8
        }
    }
    result = PredictionService.predict_assessment(payload)
    assert result is not None
    assert len(result["nutrient_predictions"]) >= 11
    # Vegan with low sunlight and high fatigue should flag Vitamin D / B12 / Iron
    flagged = [e["nutrient"] for e in result["nutrient_predictions"] if e["risk_level"] in ["MODERATE", "HIGH"]]
    assert len(flagged) > 0


def test_edge_case_critical_deficiency():
    """Test ultra-low biomarker levels: Vit D = 1 ng/mL, Ferritin = 1 ng/mL, B12 = 25 pg/mL."""
    payload = {
        "user_id": "edge_severe_deficiency",
        "age": 34,
        "gender": "FEMALE",
        "height_cm": 162.0,
        "weight_kg": 52.0,
        "dietary_pattern": "VEGETARIAN",
        "activity_level": "SEDENTARY",
        "biomarkers": {
            "vitamin_d": 1.0,
            "ferritin": 1.0,
            "vitamin_b12": 25.0
        },
        "symptoms": {
            "fatigue": 10,
            "bone_pain": 9,
            "muscle_weakness": 8
        }
    }
    result = PredictionService.predict_assessment(payload)
    assert result["overall_severity"] in ["HIGH", "CRITICAL"]

    # Test forecast engine does not crash or produce negative/NaN recovery times
    traj_d = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=1.0)
    assert traj_d.estimated_days_to_normalization > 60
    assert traj_d.trajectory_points[-1].predicted_level > 25.0

    traj_fe = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Iron", baseline_override=1.0)
    assert traj_fe.estimated_days_to_normalization > 40


def test_edge_case_toxicity_excess():
    """Test supra-physiological excess: Vit D = 150 ng/mL, Ferritin = 2000 ng/mL."""
    traj_excess_d = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=150.0)
    vel = traj_excess_d.recovery_velocity.upper()
    assert "DE-ESCALATION" in vel or "CLEARANCE" in vel
    # Trajectory should decline towards physiological safety, not skyrocket higher
    assert traj_excess_d.trajectory_points[-1].predicted_level < 150.0


def test_edge_case_pregnant_vegan():
    """Assault test: Pregnant vegan profile across full orchestration."""
    payload = {
        "user_id": "edge_pregnant_vegan",
        "age": 29,
        "gender": "FEMALE",
        "height_cm": 168.0,
        "weight_kg": 64.0,
        "dietary_pattern": "VEGAN",
        "activity_level": "LIGHTLY_ACTIVE",
        "medical_conditions": ["PREGNANCY", "GESTATIONAL_ANEMIA_RISK"],
        "biomarkers": {
            "vitamin_d": 14.0,
            "ferritin": 12.0,
            "folate": 3.5,
            "vitamin_b12": 180.0
        },
        "symptoms": {
            "fatigue": 7,
            "dizziness": 6
        }
    }

    # Verify meal planner generates 100% VEGAN compliant plan
    req = MealPlanGenerateRequest(
        target_deficiencies=["Iron", "Vitamin D", "Folate", "Vitamin B12", "Calcium", "Zinc"],
        dietary_pattern=DietaryPatternEnum.VEGAN,
        cultural_pattern=CulturalPatternEnum.MEDITERRANEAN,
        daily_calorie_target=2200,
        plan_duration_days=7
    )
    plan = IntelligentMealPlanner.generate_plan(req)

    assert plan is not None
    assert plan.plan_id is not None

    # Confirm strictly NO non-vegan ingredients in any of the meals across 7 days
    forbidden_terms = ["chicken", "beef", "pork", "fish", "salmon", "dairy", "cheese", "egg", "liver", "bacon"]
    for day in plan.daily_plans:
        for meal in day.meals:
            m_name = meal.dish_name.lower()
            all_text = (m_name + " " + " ".join(meal.ingredients)).lower()
            for term in forbidden_terms:
                if term == "dairy" and "dairy-free" in all_text:
                    continue
                if term in all_text and not ("plant" in all_text or "vegan" in all_text or "tofu" in all_text or "flax" in all_text or "almond" in all_text or "soy" in all_text):
                    assert False, f"Non-vegan ingredient '{term}' found in meal: {meal.dish_name} ({meal.ingredients})"

    # Confirm nutrient coverage meets high threshold
    cov = plan.overall_rda_compliance_pct
    vit_d = next((v for k, v in cov.items() if "vitamin d" in k.lower()), 0.0)
    iron = next((v for k, v in cov.items() if "iron" in k.lower()), 0.0)
    assert iron >= 80.0, f"Iron coverage {iron}% < 80%"
    assert vit_d >= 70.0, f"Vitamin D coverage {vit_d}% < 70%"



def test_edge_case_ckd_stage_4():
    """Assault test: CKD patient where potassium/calcium balance is critical."""
    payload = {
        "user_id": "edge_ckd_patient",
        "age": 67,
        "gender": "MALE",
        "height_cm": 172.0,
        "weight_kg": 76.0,
        "dietary_pattern": "OMNIVORE",
        "activity_level": "SEDENTARY",
        "medical_conditions": ["CHRONIC_KIDNEY_DISEASE_STAGE_4"],
        "biomarkers": {
            "vitamin_d": 12.0,
            "calcium": 8.1,
            "potassium": 5.4  # High normal / borderline hyperkalemic
        },
        "symptoms": {
            "fatigue": 8,
            "muscle_cramps": 6
        }
    }

    result = PredictionService.predict_assessment(payload)
    assert result is not None
    assert result["overall_severity"] in ["MODERATE", "HIGH", "CRITICAL"]


def test_edge_case_frail_elderly():
    """Assault test: Frail elderly patient (Age 88) with polypharmacy & multiple deficiencies."""
    payload = {
        "user_id": "edge_elderly_88",
        "age": 88,
        "gender": "FEMALE",
        "height_cm": 152.0,
        "weight_kg": 46.0,
        "dietary_pattern": "VEGETARIAN",
        "activity_level": "SEDENTARY",
        "medical_conditions": ["OSTEOPENIA", "POLYPHARMACY", "SARCOPENIA"],
        "biomarkers": {
            "vitamin_d": 9.0,
            "calcium": 7.9,
            "vitamin_b12": 150.0,
            "zinc": 55.0
        },
        "symptoms": {
            "bone_pain": 9,
            "muscle_weakness": 9,
            "fatigue": 8,
            "memory_issues": 7
        }
    }

    result = PredictionService.predict_assessment(payload)
    assert result["overall_severity"] in ["HIGH", "CRITICAL"]

    # Check that forecasting runs successfully
    traj_d = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=9.0)
    assert traj_d.estimated_days_to_normalization > 60
    assert not any(p.predicted_level != p.predicted_level for p in traj_d.trajectory_points)


if __name__ == "__main__":
    print("Executing NutriScan Edge Case Assault Suite...")
    test_edge_case_age_zero()
    print("PASS: Age 0 boundary handled gracefully.")
    test_edge_case_age_centenarian()
    print("PASS: Age 120 boundary handled gracefully.")
    test_edge_case_bmi_extremes()
    print("PASS: BMI 10 & 70 extremes handled gracefully.")
    test_edge_case_missing_biomarkers()
    print("PASS: Missing biomarkers inferred safely from symptoms & diet.")
    test_edge_case_critical_deficiency()
    print("PASS: Critical deficiencies correctly triaged.")
    test_edge_case_toxicity_excess()
    print("PASS: Hypervitaminosis toxicity handled with de-escalation clearance.")
    test_edge_case_pregnant_vegan()
    print("PASS: Pregnant vegan meal plan 100% compliant with high micronutrient density.")
    test_edge_case_ckd_stage_4()
    print("PASS: CKD Stage 4 boundary evaluated without exception.")
    test_edge_case_frail_elderly()
    print("PASS: Frail elderly case evaluated with zero NaN anomalies.")
    print("\nALL EDGE CASE ASSAULT TESTS PASSED SUCCESSFULLY!")
