"""
NutriScan Clinical Prediction Accuracy Recovery & Production Remediation Validation Suite
Covers Phases 1, 2, 6, 7, 8, 9, and 11.
Zero synthetic assumptions; tests runtime engine, API routes, and clinical safety gates.
"""

import sys
import os
import json
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from backend.app.main import app
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.reporting.service import ReportingService
from backend.app.modules.reporting.health_scorer import OverallNutritionalHealthScorer
from backend.app.ml.constants import TARGET_NUTRIENTS

client = TestClient(app)


def test_phase1_full_pipeline_audit():
    """
    Phase 1: Full Prediction Pipeline Audit.
    Traces a patient record through preprocessor, inference engine, risk calibration,
    biomarker override gates, health scorer, and API response.
    """
    print("\n--- PHASE 1: FULL PREDICTION PIPELINE AUDIT ---")
    intake_payload = {
        "age": 30,
        "gender": "FEMALE",
        "height_cm": 165,
        "weight_kg": 60,
        "dietary_pattern": "OMNIVORE",
        "meals_per_day": 3,
        "water_intake_liters": 2.5,
        "daily_fruit_vegetable_servings": 4,
        "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 8.0,
        "sunlight_exposure_min_per_day": 35,
        "stress_level": 2,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE",
        "symptoms": {},
        "biomarkers": {"serum_25ohd": 42.0, "serum_ferritin": 65.0}
    }

    res = PredictionService.predict_assessment(intake_payload, compute_explainability=True)
    assert "nutrient_predictions" in res
    assert len(res["nutrient_predictions"]) == 18

    for p in res["nutrient_predictions"]:
        assert "nutrient" in p
        assert "risk_level" in p
        assert "deficiency_probability" in p
        assert "probability" in p
        assert "score" in p
        assert "probability_distribution" in p
        assert isinstance(p["probability_distribution"], dict)
        assert set(p["probability_distribution"].keys()) == {"low", "moderate", "high"}

    print("Phase 1 verified: Pipeline successfully outputs 18 nutrients with valid tri-class distributions.")


def test_phase2_controlled_experiments_tests_a_b_c_d():
    """
    Phase 2: Clinical Feature Influence Verification across Tests A, B, C, D.
    Verifies that the engine actually responds to symptoms and biomarkers.
    """
    print("\n--- PHASE 2: CONTROLLED CLINICAL FEATURE INFLUENCE EXPERIMENTS ---")
    engine = PredictionService.get_engine()

    base_healthy = {
        "age": 32, "gender": "FEMALE", "height_cm": 165, "weight_kg": 62,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 3, "water_intake_liters": 2.5,
        "daily_fruit_vegetable_servings": 4, "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 8.0, "sunlight_exposure_min_per_day": 35,
        "stress_level": 2, "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {},
        "biomarkers": {}
    }

    # Test A: Healthy baseline
    res_a = engine.screen_patient(base_healthy, compute_explainability=False)
    score_a = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=res_a["nutrient_predictions"],
        interaction_analysis={"interactions": res_a.get("nutrient_interactions", [])},
        patient_data=base_healthy
    )
    assert score_a.final_score >= 90, f"Test A score should be >= 90, got {score_a.final_score}"
    assert all(p["risk_level"] == "LOW" for p in res_a["nutrient_predictions"])
    print(f"Test A (Healthy): Score = {score_a.final_score} (Expected > 90) -> PASS")

    # Test B: Severe symptoms only (fatigue, brain fog, bone pain, muscle weakness, hair loss)
    test_b = dict(base_healthy)
    test_b["symptoms"] = {
        "fatigue": 9,
        "brain_fog": 8,
        "bone_pain": 9,
        "muscle_weakness": 8,
        "hair_loss": 8
    }
    res_b = engine.screen_patient(test_b, compute_explainability=False)
    score_b = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=res_b["nutrient_predictions"],
        interaction_analysis={"interactions": res_b.get("nutrient_interactions", [])},
        patient_data=test_b
    )
    # Check that model responds to symptoms
    vit_d_b = next(p for p in res_b["nutrient_predictions"] if p["nutrient"] == "Vitamin D")
    iron_b = next(p for p in res_b["nutrient_predictions"] if p["nutrient"] == "Iron")

    assert vit_d_b["risk_level"] in ["MODERATE", "HIGH"], f"Vitamin D risk should be elevated, got {vit_d_b['risk_level']}"
    assert iron_b["risk_level"] in ["MODERATE", "HIGH"], f"Iron risk should be elevated, got {iron_b['risk_level']}"
    assert vit_d_b["probability"] >= 0.50, f"Vitamin D probability should be >= 0.50, got {vit_d_b['probability']}"
    assert score_b.final_score < score_a.final_score, "Health score must drop when severe symptoms are present"
    assert score_b.final_score <= 70, f"Test B score should be <= 70, got {score_b.final_score}"
    print(f"Test B (Symptoms Only): Score = {score_b.final_score} (Expected <= 70), Vit D = {vit_d_b['risk_level']} ({vit_d_b['probability']}), Iron = {iron_b['risk_level']} ({iron_b['probability']}) -> PASS")

    # Test C: Severe biomarkers only (Vit D = 8, Ferritin = 5, B12 = 120)
    test_c = dict(base_healthy)
    test_c["biomarkers"] = {
        "vitamin_d": 8.0,
        "ferritin": 5.0,
        "serum_b12": 120.0
    }
    res_c = engine.screen_patient(test_c, compute_explainability=False)
    score_c = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=res_c["nutrient_predictions"],
        interaction_analysis={"interactions": res_c.get("nutrient_interactions", [])},
        patient_data=test_c
    )
    vit_d_c = next(p for p in res_c["nutrient_predictions"] if p["nutrient"] == "Vitamin D")
    iron_c = next(p for p in res_c["nutrient_predictions"] if p["nutrient"] == "Iron")
    b12_c = next(p for p in res_c["nutrient_predictions"] if p["nutrient"] == "Vitamin B12")

    assert vit_d_c["risk_level"] == "HIGH", f"Vit D must be HIGH, got {vit_d_c['risk_level']}"
    assert iron_c["risk_level"] == "HIGH", f"Iron must be HIGH, got {iron_c['risk_level']}"
    assert b12_c["risk_level"] == "HIGH", f"B12 must be HIGH, got {b12_c['risk_level']}"
    assert vit_d_c["probability"] >= 0.95
    assert iron_c["probability"] >= 0.95
    assert b12_c["probability"] >= 0.95
    assert score_c.final_score < 30, f"Test C score should be < 30 with 3 critical biomarkers, got {score_c.final_score}"
    print(f"Test C (Biomarkers Only): Score = {score_c.final_score} (Expected < 30), 3 HIGH Deficiencies -> PASS")

    # Test D: Combined severe (symptoms, biomarkers, poor diet, poor sleep, zero sunlight, high stress)
    test_d = dict(test_b)
    test_d["biomarkers"] = {
        "vitamin_d": 8.0,
        "ferritin": 5.0,
        "serum_b12": 120.0,
        "calcium": 7.8
    }
    test_d["dietary_pattern"] = "VEGAN"
    test_d["daily_fruit_vegetable_servings"] = 0
    test_d["sleep_hours_per_night"] = 4.0
    test_d["sunlight_exposure_min_per_day"] = 0
    test_d["stress_level"] = 10
    test_d["smoking_status"] = "CURRENT"
    test_d["alcohol_consumption"] = "HEAVY"

    res_d = engine.screen_patient(test_d, compute_explainability=False)
    score_d = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=res_d["nutrient_predictions"],
        interaction_analysis={"interactions": res_d.get("nutrient_interactions", [])},
        patient_data=test_d
    )
    high_count_d = sum(1 for p in res_d["nutrient_predictions"] if p["risk_level"] == "HIGH")
    assert high_count_d >= 4, f"Test D should have at least 4 HIGH deficiencies, got {high_count_d}"
    assert score_d.final_score < 30, f"Test D score should be < 30, got {score_d.final_score}"
    print(f"Test D (Combined Severe): Score = {score_d.final_score} (Expected < 30), High Count = {high_count_d} -> PASS")


def test_phase7_clinical_override_rule_engine():
    """
    Phase 7: Clinical Override Rule Engine verification.
    Verifies hard safety gates execute before serialization.
    """
    print("\n--- PHASE 7: CLINICAL OVERRIDE RULE ENGINE VERIFICATION ---")
    engine = PredictionService.get_engine()

    # Rule 1: Vitamin D < 10 ng/mL -> Risk = HIGH
    p1 = engine.screen_patient({"age": 25, "biomarkers": {"serum_25ohd": 8.5}}, compute_explainability=False)
    vd = next(x for x in p1["nutrient_predictions"] if x["nutrient"] == "Vitamin D")
    assert vd["risk_level"] == "HIGH"
    assert vd["probability"] >= 0.95

    # Rule 2: Ferritin < 10 ng/mL -> Iron Risk = HIGH
    p2 = engine.screen_patient({"age": 25, "biomarkers": {"serum_ferritin": 7.0}}, compute_explainability=False)
    fe = next(x for x in p2["nutrient_predictions"] if x["nutrient"] == "Iron")
    assert fe["risk_level"] == "HIGH"
    assert fe["probability"] >= 0.95

    # Rule 3: B12 < 150 pg/mL -> B12 Risk = HIGH
    p3 = engine.screen_patient({"age": 25, "biomarkers": {"serum_b12": 110.0}}, compute_explainability=False)
    b12 = next(x for x in p3["nutrient_predictions"] if x["nutrient"] == "Vitamin B12")
    assert b12["risk_level"] == "HIGH"
    assert b12["probability"] >= 0.95

    # Rule 4: Calcium < 8.5 mg/dL -> Calcium Risk = HIGH
    p4 = engine.screen_patient({"age": 25, "biomarkers": {"serum_calcium": 7.9}}, compute_explainability=False)
    ca = next(x for x in p4["nutrient_predictions"] if x["nutrient"] == "Calcium")
    assert ca["risk_level"] == "HIGH"
    assert ca["probability"] >= 0.95

    print("Phase 7 verified: All 4 hard clinical laboratory override gates execute deterministically.")


def test_phase8_and_11_adversarial_clinical_validation():
    """
    Phase 8: Adversarial Clinical Validation across Cases 1 to 5.
    Phase 11: Mandatory Acceptance Criteria.
    - Healthy Patient: Score > 90
    - Mild Deficiency: Score 70-90
    - Moderate Deficiency: Score 50-70
    - Severe Deficiency: Score < 50
    - Critical Deficiency: Score < 30
    """
    print("\n--- PHASE 8 & 11: ADVERSARIAL CLINICAL VALIDATION ---")
    engine = PredictionService.get_engine()

    # Case 1: Healthy
    c1_intake = {
        "age": 28, "gender": "MALE", "height_cm": 178, "weight_kg": 72,
        "dietary_pattern": "MEDITERRANEAN", "meals_per_day": 3, "water_intake_liters": 2.5,
        "daily_fruit_vegetable_servings": 5, "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 8.0, "sunlight_exposure_min_per_day": 40,
        "stress_level": 2, "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {}, "biomarkers": {}
    }
    r1 = engine.screen_patient(c1_intake, compute_explainability=False)
    s1 = OverallNutritionalHealthScorer.calculate_health_score(r1["nutrient_predictions"], {}, c1_intake)
    assert s1.final_score > 90, f"Case 1 Healthy should be > 90, got {s1.final_score}"
    print(f"Case 1 (Healthy): Health Score = {s1.final_score} (Expected > 90) -> PASS")

    # Case 2: Mild Deficiency (e.g. mild Vitamin D insufficiency, sunlight 10 min, slight fatigue)
    c2_intake = {
        "age": 35, "gender": "FEMALE", "height_cm": 165, "weight_kg": 64,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 3, "water_intake_liters": 2.0,
        "daily_fruit_vegetable_servings": 3, "activity_level": "LIGHTLY_ACTIVE",
        "sleep_hours_per_night": 7.0, "sunlight_exposure_min_per_day": 10,
        "stress_level": 4, "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {"fatigue": 4},
        "biomarkers": {"serum_25ohd": 24.0} # Mild insufficiency (20-30 ng/mL)
    }
    r2 = engine.screen_patient(c2_intake, compute_explainability=False)
    s2 = OverallNutritionalHealthScorer.calculate_health_score(r2["nutrient_predictions"], {}, c2_intake)
    assert 70 <= s2.final_score <= 90, f"Case 2 Mild Deficiency should be 70-90, got {s2.final_score}"
    print(f"Case 2 (Mild Deficiency): Health Score = {s2.final_score} (Expected 70-90) -> PASS")

    # Case 3: Moderate Deficiency (e.g. 2 Moderate deficiencies: Iron & B12)
    c3_intake = {
        "age": 40, "gender": "FEMALE", "height_cm": 160, "weight_kg": 58,
        "dietary_pattern": "VEGETARIAN", "meals_per_day": 3, "water_intake_liters": 2.0,
        "daily_fruit_vegetable_servings": 3, "activity_level": "SEDENTARY",
        "sleep_hours_per_night": 6.5, "sunlight_exposure_min_per_day": 20,
        "stress_level": 6, "smoking_status": "NEVER", "alcohol_consumption": "OCCASIONAL",
        "symptoms": {"fatigue": 6, "pale_skin": 5, "brain_fog": 6},
        "biomarkers": {"serum_ferritin": 25.0, "serum_b12": 280.0} # Subclinical depletion
    }
    r3 = engine.screen_patient(c3_intake, compute_explainability=False)
    s3 = OverallNutritionalHealthScorer.calculate_health_score(r3["nutrient_predictions"], {}, c3_intake)
    assert 50 <= s3.final_score <= 70, f"Case 3 Moderate Deficiency should be 50-70, got {s3.final_score}"
    print(f"Case 3 (Moderate Deficiency): Health Score = {s3.final_score} (Expected 50-70) -> PASS")

    # Case 4: Severe Deficiency (Multiple High or 1 critical + 1 high)
    c4_intake = {
        "age": 45, "gender": "FEMALE", "height_cm": 162, "weight_kg": 55,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 2, "water_intake_liters": 1.5,
        "daily_fruit_vegetable_servings": 1, "activity_level": "SEDENTARY",
        "sleep_hours_per_night": 5.5, "sunlight_exposure_min_per_day": 10,
        "stress_level": 8, "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {"fatigue": 8, "bone_pain": 8, "muscle_weakness": 7, "pale_skin": 7},
        "biomarkers": {"serum_25ohd": 14.0, "serum_ferritin": 12.0} # Deficient Vit D and Ferritin
    }
    r4 = engine.screen_patient(c4_intake, compute_explainability=False)
    s4 = OverallNutritionalHealthScorer.calculate_health_score(r4["nutrient_predictions"], {}, c4_intake)
    assert s4.final_score < 50, f"Case 4 Severe Deficiency should be < 50, got {s4.final_score}"
    print(f"Case 4 (Severe Deficiency): Health Score = {s4.final_score} (Expected < 50) -> PASS")

    # Case 5: Critical Deficiency (Ferritin 3, Vit D 6, B12 90, severe symptoms, poor diet)
    c5_intake = {
        "age": 30, "gender": "FEMALE", "height_cm": 165, "weight_kg": 52,
        "dietary_pattern": "VEGAN", "meals_per_day": 2, "water_intake_liters": 1.2,
        "daily_fruit_vegetable_servings": 1, "activity_level": "SEDENTARY",
        "sleep_hours_per_night": 4.5, "sunlight_exposure_min_per_day": 0,
        "stress_level": 9, "smoking_status": "CURRENT", "alcohol_consumption": "HEAVY",
        "symptoms": {"fatigue": 9, "bone_pain": 9, "hair_loss": 9, "muscle_weakness": 9, "brain_fog": 8, "pale_skin": 9},
        "biomarkers": {"serum_ferritin": 3.0, "serum_25ohd": 6.0, "serum_b12": 90.0}
    }
    r5 = engine.screen_patient(c5_intake, compute_explainability=False)
    s5 = OverallNutritionalHealthScorer.calculate_health_score(r5["nutrient_predictions"], {}, c5_intake)
    assert s5.final_score < 30, f"Case 5 Critical Deficiency should be < 30, got {s5.final_score}"
    print(f"Case 5 (Critical Deficiency): Health Score = {s5.final_score} (Expected < 30) -> PASS")


def test_phase9_dashboard_integrity_api():
    """
    Phase 9: Dashboard Integrity Verification via Live REST Endpoints.
    Submits an assessment via POST /api/v1/predict, then retrieves GET /api/v1/dashboard/{id}.
    Verifies that health score, risk distribution, and predictions are transmitted verbatim.
    """
    print("\n--- PHASE 9: DASHBOARD INTEGRITY API VERIFICATION ---")
    intake = {
        "age": 30,
        "gender": "FEMALE",
        "height_cm": 165,
        "weight_kg": 60,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 2,
            "water_intake_liters": 1.5,
            "daily_fruit_vegetable_servings": 2,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": ["vegan"]
        },
        "lifestyle_factors": {
            "activity_level": "SEDENTARY",
            "sleep_hours_per_night": 6.0,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 10,
            "stress_level": 7
        },
        "symptoms": {"fatigue": 8, "brain_fog": 8, "bone_pain": 8, "tingling_numbness": 7},
        "biomarkers": {"serum_25ohd": 8.0, "serum_ferritin": 6.0, "serum_b12": 110.0}
    }

    pred_res = client.post("/api/v1/predict", json=intake)
    assert pred_res.status_code == 200, f"Prediction failed: {pred_res.text}"
    pred_data = pred_res.json()

    assessment_id = pred_data.get("assessment_id")
    assert assessment_id, "Assessment ID must be returned by prediction endpoint"

    dash_res = client.get(f"/api/v1/dashboard/{assessment_id}")
    assert dash_res.status_code == 200, f"Dashboard retrieval failed: {dash_res.text}"
    dash_data = dash_res.json()

    # Verify score integrity: critical biomarkers must yield score < 30
    assert dash_data["overall_health_score"] < 30, f"Critical patient dashboard score should be < 30, got {dash_data['overall_health_score']}"
    assert dash_data["overall_risk_classification"] == "HIGH"
    assert dash_data["nutrient_risk_distribution"]["HIGH"] >= 3

    # Verify priority ranking order
    priority = dash_data["deficiency_priority_ranking"]
    assert len(priority) > 0
    top_nutrient = priority[0]
    assert top_nutrient["tier"] == "Priority 1"
    assert top_nutrient["risk_level"] == "HIGH"

    print(f"Phase 9 verified: Dashboard API successfully preserved score {dash_data['overall_health_score']}, overall risk {dash_data['overall_risk_classification']}, and Priority 1 ranking.")


if __name__ == "__main__":
    print("Executing Clinical Accuracy Recovery Test Suite...")
    test_phase1_full_pipeline_audit()
    test_phase2_controlled_experiments_tests_a_b_c_d()
    test_phase7_clinical_override_rule_engine()
    test_phase8_and_11_adversarial_clinical_validation()
    test_phase9_dashboard_integrity_api()
    print("\nALL CLINICAL PREDICTION ACCURACY TESTS PASSED SUCCESSFULLY.")
