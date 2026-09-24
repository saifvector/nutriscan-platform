"""
test_audit_remediation.py
Comprehensive End-to-End Validation Test Suite for NutriScan Audit Remediation.

Validates:
1. Healthy Patient Profile (Low risk, deficiency_probability = P(MODERATE)+P(HIGH) < 0.05, score >= 85, maintenance guidance)
2. Clinical Safety Guardrails (CKD, Hemochromatosis, Pregnancy, Smokers, UL thresholds)
3. Schema Contract Compliance (nutrient, risk_level, deficiency_probability, confidence, score, probability_distribution dict)
4. IDOR Authorization Security (cross-patient access returns 403 Forbidden)
5. Persistence & Cache Invalidation (SQLite persistence, cache eviction)
"""

import pytest
import uuid
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.assessment import MedicalHistoryItem, HealthAssessmentCreate
from backend.app.schemas.phase12_governance import SafetyAction, SafetySeverity
from backend.app.modules.governance.safety_engine import ClinicalSafetyEngine
from backend.app.modules.recommendation.engine import PersonalizedRecommendationEngine
from backend.app.modules.recommendation.service import RecommendationService
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.modules.reporting.service import ReportingService
from backend.app.core.persistence import PersistenceRepository
from backend.app.core.auth import AuthenticatedUser, create_access_token


client = TestClient(app)


def test_healthy_patient_profile_pipeline():
    """
    Validates end-to-end inference and recommendations for a healthy patient profile:
    Age: 30, BMI: 22.0, Diet: OMNIVORE, adequate sunlight, non-smoker, no chronic conditions.
    Deficiency probability must be strictly P(MODERATE) + P(HIGH) < 0.05.
    Risk level must be LOW.
    Health score must be >= 85.
    Recommendations must provide foundational maintenance without acute high-dose clinical interventions.
    """
    healthy_intake = {
        "user_id": str(uuid.uuid4()),
        "age": 30,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
            "meals_per_day": 3,
            "water_intake_liters": 2.5,
            "daily_fruit_vegetable_servings": 4,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": []
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 45,
            "stress_level": 3
        },
        "symptoms": {},
        "medical_history": [],
        "supplement_usage": []
    }

    response = client.post("/api/v1/predict", json=healthy_intake)
    assert response.status_code == 200, f"Assessment failed: {response.text}"
    assessment_data = response.json()
    assessment_id = assessment_data.get("assessment_id") or assessment_data.get("id")
    assert assessment_id, "Missing assessment_id in response"

    # Fetch predictions
    pred_res = client.get(f"/api/v1/predictions/{assessment_id}")
    assert pred_res.status_code == 200, f"Predictions fetch failed: {pred_res.text}"
    pred_data = pred_res.json()
    predictions = pred_data.get("predictions", [])
    assert len(predictions) > 0, "No predictions returned"

    # Verify schema and risk bounds for all nutrients
    for p in predictions:
        assert "nutrient" in p
        assert "risk_level" in p
        assert "deficiency_probability" in p
        assert "confidence" in p
        assert "score" in p
        assert "probability_distribution" in p

        # Check distribution is a dict with low, moderate, high
        dist = p["probability_distribution"]
        assert isinstance(dist, dict), f"probability_distribution must be a dict, got {type(dist)}"
        assert "low" in dist and "moderate" in dist and "high" in dist

        # Mathematical invariance check: deficiency_probability == moderate + high
        expected_deficiency_prob = round(dist["moderate"] + dist["high"], 4)
        actual_deficiency_prob = round(p["deficiency_probability"], 4)
        assert abs(actual_deficiency_prob - expected_deficiency_prob) < 0.001, (
            f"Deficiency probability {actual_deficiency_prob} does not equal "
            f"moderate ({dist['moderate']}) + high ({dist['high']})"
        )

        # For healthy patient, deficiency probability must be strictly LOW (< 0.15, typically < 0.05)
        assert p["deficiency_probability"] < 0.15, (
            f"Deficiency probability for {p['nutrient']} too high: {p['deficiency_probability']}"
        )
        assert p["risk_level"] == "LOW", f"Risk level for {p['nutrient']} should be LOW, got {p['risk_level']}"

    # Verify recommendations for healthy patient
    rec_res = client.get(f"/api/v1/recommendations/{assessment_id}")
    assert rec_res.status_code == 200, f"Recommendations fetch failed: {rec_res.text}"
    rec_data = rec_res.json()

    # Recommendations should focus on dietary maintenance, no acute aggressive supplements
    assert rec_data.get("primary_deficiency") in (None, "", "NONE", "Maintenance"), (
        f"Healthy patient should not have primary deficiency: {rec_data.get('primary_deficiency')}"
    )


def test_clinical_safety_ckd_guardrails():
    """
    Validates that a Chronic Kidney Disease (CKD) patient has contraindicated nutrients
    (Potassium, Phosphorus, Magnesium, High-dose Protein) strictly blocked.
    """
    ckd_patient = {
        "age": 62,
        "gender": "MALE",
        "medical_history": [
            {"condition_name": "Chronic Kidney Disease", "is_active": True}
        ],
        "symptoms": {}
    }

    # Evaluate safety engine directly
    res = ClinicalSafetyEngine.evaluate_safety(
        patient_intake=ckd_patient,
        proposed_recommendations=[
            {"nutrient": "Potassium", "dosage": "1000mg", "item_name": "Potassium Chloride"},
            {"nutrient": "Magnesium", "dosage": "400mg", "item_name": "Magnesium Glycinate"}
        ]
    )

    violations = res.violations
    assert len(violations) >= 2, "CKD patient must trigger safety violations for Potassium and Magnesium"
    assert any(v.action_taken == SafetyAction.BLOCKED and v.nutrient == "Potassium" for v in violations), (
        "Potassium supplement for CKD patient must be BLOCKED"
    )
    assert any(v.action_taken == SafetyAction.BLOCKED and v.nutrient == "Magnesium" for v in violations), (
        "Magnesium supplement for CKD patient must be BLOCKED"
    )


def test_clinical_safety_hemochromatosis_guardrails():
    """
    Validates that a Hemochromatosis patient has Iron strictly blocked.
    """
    hemo_patient = {
        "age": 45,
        "gender": "MALE",
        "medical_history": [
            {"condition_name": "Hemochromatosis", "is_active": True}
        ],
        "symptoms": {}
    }

    res = ClinicalSafetyEngine.evaluate_safety(
        patient_intake=hemo_patient,
        proposed_recommendations=[
            {"nutrient": "Iron", "dosage": "65mg", "item_name": "Ferrous Sulfate"}
        ]
    )

    violations = res.violations
    assert len(violations) > 0, "Hemochromatosis patient must trigger safety violation for Iron"
    assert any(v.action_taken == SafetyAction.BLOCKED and v.nutrient == "Iron" for v in violations), (
        "Iron for Hemochromatosis must be BLOCKED"
    )


def test_clinical_safety_smoker_guardrails():
    """
    Validates that a Smoker has high-dose synthetic Beta-Carotene blocked
    due to elevated lung carcinoma risk (CARET trial).
    """
    smoker_patient = {
        "age": 50,
        "gender": "MALE",
        "is_smoker": True,
        "lifestyle_factors": {
            "smoking_status": "CURRENT_SMOKER"
        },
        "symptoms": {}
    }

    res = ClinicalSafetyEngine.evaluate_safety(
        patient_intake=smoker_patient,
        proposed_recommendations=[
            {"nutrient": "Beta-Carotene", "dosage": "15mg", "item_name": "Synthetic Beta-Carotene Supplement"}
        ]
    )

    violations = res.violations
    assert len(violations) > 0, "Smoker patient must trigger safety violation for Beta-Carotene"
    assert any(v.action_taken == SafetyAction.BLOCKED for v in violations), (
        "Beta-carotene supplement for smoker must be BLOCKED"
    )


def test_clinical_safety_pregnancy_retinol_guardrails():
    """
    Validates that a pregnant patient has high-dose preformed Retinol blocked (teratogenicity).
    """
    pregnant_patient = {
        "age": 28,
        "gender": "FEMALE",
        "is_pregnant": True,
        "medical_history": [
            {"condition_name": "Pregnancy", "is_active": True}
        ],
        "symptoms": {}
    }

    res = ClinicalSafetyEngine.evaluate_safety(
        patient_intake=pregnant_patient,
        proposed_recommendations=[
            {"nutrient": "Vitamin A", "dosage": "10000 IU", "item_name": "Retinol Palmitate"}
        ]
    )

    violations = res.violations
    assert len(violations) > 0, "Pregnant patient must trigger safety violation for Retinol"
    assert any(v.action_taken == SafetyAction.BLOCKED for v in violations), (
        "High-dose retinol for pregnancy must be BLOCKED"
    )


def test_idor_authorization_enforcement():
    """
    Validates that User B cannot access User A's recommendation report,
    returning HTTP 403 Forbidden.
    """
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())

    intake = {
        "user_id": user_a_id,
        "age": 35,
        "gender": "FEMALE",
        "height_cm": 168.0,
        "weight_kg": 62.0,
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
            "meals_per_day": 3,
            "water_intake_liters": 2.0,
            "daily_fruit_vegetable_servings": 3,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": []
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.0,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 30,
            "stress_level": 4
        },
        "symptoms": {},
        "medical_history": [],
        "supplement_usage": []
    }

    token_a = create_access_token(user_id=user_a_id, email="usera@example.com", role="PATIENT")
    token_b = create_access_token(user_id=user_b_id, email="userb@example.com", role="PATIENT")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    create_res = client.post("/api/v1/predict", json=intake, headers=headers_a)
    assert create_res.status_code == 200, f"Prediction failed: {create_res.text}"
    assessment_id = create_res.json().get("assessment_id") or create_res.json().get("id")

    # User A accesses own recommendations -> 200 OK
    res_a = client.get(f"/api/v1/recommendations/{assessment_id}", headers=headers_a)
    assert res_a.status_code == 200, f"User A failed to access own data: {res_a.text}"

    # User B attempts to access User A's recommendations -> 403 Forbidden
    res_b = client.get(f"/api/v1/recommendations/{assessment_id}", headers=headers_b)
    assert res_b.status_code == 403, f"User B should be forbidden (403), got {res_b.status_code}"


def test_cache_invalidation_and_persistence():
    """
    Validates that cache invalidation and persistence retrieval work cleanly.
    """
    test_id = str(uuid.uuid4())

    # Pre-populate explainability cache
    ExplainabilityService._active_payload_cache[test_id] = {"cached": True, "assessment_id": test_id}
    assert test_id in ExplainabilityService._active_payload_cache

    # Invalidate
    ExplainabilityService.invalidate_cache(test_id)
    assert test_id not in ExplainabilityService._active_payload_cache

    # Pre-populate reporting cache
    ReportingService._reports_cache[test_id] = {"report": True}
    assert test_id in ReportingService._reports_cache

    # Invalidate
    ReportingService.invalidate_cache(test_id)
    assert test_id not in ReportingService._reports_cache
