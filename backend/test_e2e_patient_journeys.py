"""
End-to-End Clinical Patient Journeys Benchmark
Phase 5: End-to-End Workflow Validation

Executes complete clinical journeys across 5 standardized patient profiles:
- Patient A: Vegetarian female with Vitamin D deficiency
- Patient B: Iron deficiency anemia (heavy menses)
- Patient C: Vitamin B12 deficiency vegan (5-year vegan)
- Patient D: Multiple deficiencies (Iron, Vitamin D, Calcium, Folate)
- Patient E: Healthy normal control

Validates full cascade consistency across:
Assessment -> Prediction -> Copilot -> Recommendations -> Meal Plan -> Forecast -> Report
"""

import sys
import uuid
from pathlib import Path
from typing import Dict, Any

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.core.workflow_orchestrator import ClinicalWorkflowOrchestrator
from backend.app.core.persistence import PersistenceRepository


PATIENTS = [
    {
        "id_code": "PATIENT_A",
        "name": "Patient A: Vegetarian Female with Vitamin D Deficiency",
        "profile": {
            "age": 28,
            "gender": "FEMALE",
            "dietary_habits": {
                "dietary_pattern": "VEGETARIAN",
                "meals_per_day": 3,
                "dietary_restrictions": ["meat-free", "fish-free"]
            },
            "lifestyle_factors": {
                "sunlight_exposure_min_per_day": 8,
                "sleep_hours_per_night": 6.5,
                "activity_level": "SEDENTARY",
                "stress_level": 6
            },
            "symptoms": {"fatigue": 8, "muscle_weakness": 6},
            "biomarkers": {"serum_25ohd": 11.5},
            "medical_history": []
        },
        "expected_top_nutrient": "Vitamin D",
        "expected_diet": "VEGETARIAN",
        "must_not_contain_foods": ["salmon", "beef", "chicken", "meat", "pork", "fish"]
    },
    {
        "id_code": "PATIENT_B",
        "name": "Patient B: Iron Deficiency Anemia",
        "profile": {
            "age": 34,
            "gender": "FEMALE",
            "dietary_habits": {
                "dietary_pattern": "OMNIVORE",
                "meals_per_day": 3,
                "dietary_restrictions": []
            },
            "lifestyle_factors": {
                "sunlight_exposure_min_per_day": 20,
                "sleep_hours_per_night": 7.0,
                "activity_level": "MODERATE",
                "stress_level": 5
            },
            "symptoms": {"fatigue": 9, "pale_skin": 8, "dizziness": 7, "cold_hands": 7},
            "biomarkers": {"serum_ferritin": 7.5, "hemoglobin": 10.1},
            "medical_history": ["menorrhagia"]
        },
        "expected_top_nutrient": "Iron",
        "expected_diet": "OMNIVORE",
        "must_not_contain_foods": []
    },
    {
        "id_code": "PATIENT_C",
        "name": "Patient C: Vitamin B12 Deficiency Strict Vegan",
        "profile": {
            "age": 31,
            "gender": "MALE",
            "dietary_habits": {
                "dietary_pattern": "VEGAN",
                "meals_per_day": 3,
                "dietary_restrictions": ["meat-free", "dairy-free", "egg-free"]
            },
            "lifestyle_factors": {
                "sunlight_exposure_min_per_day": 30,
                "sleep_hours_per_night": 7.5,
                "activity_level": "ACTIVE",
                "stress_level": 4
            },
            "symptoms": {"paresthesia": 7, "brain_fog": 6, "fatigue": 6},
            "biomarkers": {"serum_b12": 135.0},
            "medical_history": ["long_term_vegan_5_years"]
        },
        "expected_top_nutrient": "Vitamin B12",
        "expected_diet": "VEGAN",
        "must_not_contain_foods": ["meat", "fish", "dairy", "egg", "cheese", "salmon", "beef", "chicken", "whey", "paneer"]
    },
    {
        "id_code": "PATIENT_D",
        "name": "Patient D: Multiple Deficiencies Complex",
        "profile": {
            "age": 42,
            "gender": "FEMALE",
            "dietary_habits": {
                "dietary_pattern": "VEGETARIAN",
                "meals_per_day": 2,
                "dietary_restrictions": ["dairy-free", "meat-free"]
            },
            "lifestyle_factors": {
                "sunlight_exposure_min_per_day": 10,
                "sleep_hours_per_night": 5.5,
                "activity_level": "SEDENTARY",
                "stress_level": 8
            },
            "symptoms": {"fatigue": 9, "hair_loss": 8, "muscle_cramps": 8, "brittle_nails": 7},
            "biomarkers": {
                "serum_25ohd": 10.5,
                "serum_ferritin": 8.5,
                "serum_calcium": 8.2,
                "rbc_folate": 170.0
            },
            "medical_history": ["malabsorption_syndrome"]
        },
        "expected_top_nutrient": "Multiple",
        "expected_diet": "VEGETARIAN",
        "must_not_contain_foods": ["meat", "salmon", "beef", "chicken", "pork", "fish"]
    },
    {
        "id_code": "PATIENT_E",
        "name": "Patient E: Healthy Normal Control",
        "profile": {
            "age": 26,
            "gender": "MALE",
            "dietary_habits": {
                "dietary_pattern": "OMNIVORE",
                "meals_per_day": 3,
                "water_intake_liters": 2.8,
                "dietary_restrictions": []
            },
            "lifestyle_factors": {
                "sunlight_exposure_min_per_day": 40,
                "sleep_hours_per_night": 8.0,
                "activity_level": "ACTIVE",
                "stress_level": 2
            },
            "symptoms": {},
            "biomarkers": {
                "serum_25ohd": 42.0,
                "serum_ferritin": 78.0,
                "serum_b12": 580.0,
                "serum_calcium": 9.5
            },
            "medical_history": []
        },
        "expected_top_nutrient": "None",
        "expected_diet": "OMNIVORE",
        "must_not_contain_foods": []
    }
]


def run_e2e_patient_journeys():
    print("================================================================================")
    print("      PHASE 5: END-TO-END PATIENT JOURNEYS (PATIENTS A TO E)                    ")
    print("================================================================================")

    for p_spec in PATIENTS:
        p_id = str(uuid.uuid4())
        name = p_spec["name"]
        profile = p_spec["profile"]
        expected_nutrient = p_spec["expected_top_nutrient"]
        must_not = p_spec["must_not_contain_foods"]

        print(f"\n>>> Running Journey for: {name} (ID: {p_id[:8]}) <<<")

        # 1. Execute Full Journey through Orchestrator
        journey_res = ClinicalWorkflowOrchestrator.execute_full_journey(
            assessment_id=p_id,
            intake_payload=profile,
            force_regenerate=True
        )

        assert journey_res["status"] == "COMPLETED"
        assert len(journey_res["artifacts_generated"]) >= 5

        # 2. Inspect Predictions
        pred = PersistenceRepository.get_predictions(p_id)
        assert pred is not None, f"{name}: Predictions missing from persistence!"
        high_mod_nutrients = [
            item["nutrient"] for item in pred.get("nutrient_predictions", [])
            if item.get("risk_level") in ["HIGH", "MODERATE"]
        ]
        print(f"  [1. Prediction] Flagged Elevated Targets: {high_mod_nutrients}")

        if expected_nutrient == "None":
            assert len(high_mod_nutrients) == 0, f"Healthy control had unexpected high flags: {high_mod_nutrients}"
        elif expected_nutrient == "Multiple":
            assert len(high_mod_nutrients) >= 2, f"Multi-deficiency patient flagged < 2 targets: {high_mod_nutrients}"
        else:
            assert any(expected_nutrient.lower() in n.lower() for n in high_mod_nutrients), \
                f"Expected target '{expected_nutrient}' was not flagged! Found: {high_mod_nutrients}"

        # 3. Inspect Recommendations
        recs = PersistenceRepository.get_recommendations(p_id)
        assert recs is not None, f"{name}: Recommendations missing from persistence!"
        p1_foods = [f["food_name"] if isinstance(f, dict) else f.food_name for f in recs.get("priority_1_foods", [])]
        supps = [s.get("item_name") for s in recs.get("supplement_recommendations", [])]
        print(f"  [2. Recommendations] Priority Foods: {p1_foods[:3]} | Supps: {supps[:2]}")

        # Verify dietary safety
        all_rec_foods = [str(f).lower() for f in p1_foods]
        for bad_food in must_not:
            for food_str in all_rec_foods:
                assert bad_food not in food_str, f"Dietary violation: '{bad_food}' found in {food_str} for {name}!"

        # 4. Inspect Meal Plan
        plan = PersistenceRepository.get_meal_plan(p_id)
        assert plan is not None, f"{name}: Meal plan missing from persistence!"
        comp = plan.get("overall_rda_compliance_pct", {})
        print(f"  [3. Meal Plan] Vit D: {comp.get('Vitamin D', 0)}% | Ca: {comp.get('Calcium', 0)}% | Zn: {comp.get('Zinc', 0)}% | Fe: {comp.get('Iron', 0)}%")
        
        # Verify coverage targets
        assert comp.get("Vitamin D", 0) >= 70.0, f"Vit D {comp.get('Vitamin D')}% < 70%"
        assert comp.get("Calcium", 0) >= 80.0, f"Calcium {comp.get('Calcium')}% < 80%"
        assert comp.get("Zinc", 0) >= 80.0, f"Zinc {comp.get('Zinc')}% < 80%"
        assert comp.get("Iron", 0) >= 80.0, f"Iron {comp.get('Iron')}% < 80%"

        # 5. Inspect Forecast
        forecast = PersistenceRepository.get_forecast(p_id)
        assert forecast is not None, f"{name}: Forecast missing from persistence!"
        forecast_items = forecast.get("forecasts", [])
        assert len(forecast_items) > 0
        top_fc = forecast_items[0]
        print(f"  [4. Forecast] Top: {top_fc.get('nutrient')} | Velocity: {top_fc.get('recovery_velocity')} | Days: {top_fc.get('estimated_days_to_normalization')}")

        # 6. Inspect Report
        report = PersistenceRepository.get_report(p_id)
        assert report is not None, f"{name}: Report missing from persistence!"
        print(f"  [5. Clinical Report] Title: '{report.get('report_title')}' | Status: {report.get('status')} | Score: {report.get('overall_health_score')}")

        print(f"  -> SUCCESS: All 5 stages completely consistent for {p_spec['id_code']}!")

    print("\n================================================================================")
    print("SUCCESS: ALL 5 PATIENT JOURNEYS VALIDATED WITH ZERO DEFECTS!")
    print("================================================================================")


def test_e2e_patient_journeys():
    """Pytest test case executing the 5 clinical patient journeys."""
    run_e2e_patient_journeys()


if __name__ == "__main__":
    run_e2e_patient_journeys()
