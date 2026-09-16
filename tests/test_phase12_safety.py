"""
Phase 12: Clinical Safety Governance Engine Tests.
Verifies NIH Tolerable Upper Limit (UL) guardrails, pathological contraindications, drug interactions,
safety scoring, automated intervention blocking, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.governance.safety_engine import ClinicalSafetyEngine
from backend.app.schemas.phase12_governance import SafetySeverity, SafetyRiskTier

client = TestClient(app)


def test_safety_engine_clean_recommendation():
    """Verify safe recommendations pass with 100 score and LOW risk tier."""
    patient = {
        "age": 35,
        "gender": "Female",
        "conditions": [],
        "medications": []
    }
    recs = [
        {"nutrient": "Vitamin D", "dosage": 25.0, "unit": "mcg"},
        {"nutrient": "Magnesium", "dosage": 200.0, "unit": "mg"}
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert eval_result.safety_score == 100.0
    assert eval_result.safety_tier == SafetySeverity.LOW
    assert eval_result.is_safe_for_dispatch is True
    assert eval_result.is_blocked is False
    assert len(eval_result.violations) == 0


def test_safety_engine_nih_tolerable_upper_limit():
    """Verify exceeding NIH UL triggers safety violation and score penalty."""
    patient = {"age": 45, "gender": "Male"}
    recs = [
        {"nutrient": "Vitamin D", "dosage": 150.0, "unit": "mcg"}  # UL is 100 mcg
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert eval_result.safety_score < 100.0
    assert len(eval_result.violations) >= 1
    ul_violation = next(v for v in eval_result.violations if "UL_EXCEEDED" in v.rule_id)
    assert ul_violation.severity in [SafetySeverity.HIGH, SafetySeverity.CRITICAL]


def test_safety_engine_pathological_contraindication_hemochromatosis():
    """Hemochromatosis + Iron recommendation must trigger CRITICAL block."""
    patient = {
        "age": 50,
        "gender": "Male",
        "medical_conditions": ["Hemochromatosis", "Hypertension"]
    }
    recs = [
        {"nutrient": "Iron", "dosage": 65.0, "unit": "mg"}
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert eval_result.is_safe_for_dispatch is False
    assert eval_result.is_blocked is True
    assert eval_result.safety_tier == SafetySeverity.CRITICAL
    assert eval_result.safety_score <= 50.0
    contra_violation = next(v for v in eval_result.violations if "HEMOCHROMATOSIS" in v.rule_id)
    assert contra_violation.severity == SafetySeverity.CRITICAL


def test_safety_engine_pathological_contraindication_ckd_potassium():
    """Chronic Kidney Disease + Potassium recommendation must trigger CRITICAL block."""
    patient = {
        "age": 62,
        "conditions": ["Chronic Kidney Disease (CKD)", "Stage 3"]
    }
    recs = [
        {"nutrient": "Potassium", "dosage": 1500.0, "unit": "mg"}
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert eval_result.is_safe_for_dispatch is False
    assert eval_result.is_blocked is True
    assert eval_result.safety_tier == SafetySeverity.CRITICAL


def test_safety_engine_drug_interaction_warfarin_vitamin_k():
    """Warfarin + Vitamin K recommendation must trigger severe conflict warning."""
    patient = {
        "medications": ["Warfarin (Coumadin)", "Atorvastatin"]
    }
    recs = [
        {"nutrient": "Vitamin K", "dosage": 100.0, "unit": "mcg"}
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert len(eval_result.violations) >= 1
    warfarin_vio = next(v for v in eval_result.violations if "WARFARIN" in v.rule_id)
    assert warfarin_vio.severity in [SafetySeverity.HIGH, SafetySeverity.CRITICAL]


def test_safety_engine_duplicate_compounding_detection():
    """Duplicate nutrient intake across multiple sources must trigger warning."""
    patient = {}
    recs = [
        {"nutrient": "Zinc", "dosage": 30.0, "unit": "mg"},
        {"nutrient": "Zinc", "dosage": 25.0, "unit": "mg"}
    ]
    eval_result = ClinicalSafetyEngine.evaluate_safety(patient, recs)
    assert len(eval_result.violations) >= 1
    dup_vio = next(v for v in eval_result.violations if "DUPLICATE" in v.rule_id)
    assert dup_vio is not None


def test_api_safety_evaluate_endpoint():
    """POST /api/v1/safety/evaluate returns full clinical governance evaluation."""
    payload = {
        "assessment": {
            "age": 42,
            "gender": "Female",
            "conditions": ["Hemochromatosis"]
        },
        "recommendations": [
            {"target_nutrient": "Iron", "dose_mg": 50.0}
        ]
    }
    resp = client.post("/api/v1/safety/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_safe_for_dispatch"] is False
    assert data["safety_tier"] == "CRITICAL"
    assert len(data["violations"]) >= 1
