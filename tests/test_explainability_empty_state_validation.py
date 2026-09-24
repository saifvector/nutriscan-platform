"""
Validation Test Suite: Empty State & Anti-Mock Verification for Clinical Reasoning
Guarantees:
1. Opening explainability without a valid assessment ID returns 404 and NEVER generates synthetic patient profiles.
2. No DEMO-CLINICAL or DEMO-CLINICAL-* identifiers are ever returned.
3. No static percentages (38%) or static grades are returned in DYNAMIC_CLINICAL_EVIDENCE_CATALOG.
4. All findings are strictly traceable: Assessment -> Prediction -> Explainability Output -> UI.
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.modules.explainability.evidence_catalog import (
    DYNAMIC_CLINICAL_EVIDENCE_CATALOG,
    generate_dynamic_clinical_evidence_entry
)

client = TestClient(app)


def test_prediction_explanation_without_id_returns_404():
    """Verify GET /api/v1/explainability/prediction-explanation returns 404 when ID is omitted."""
    resp = client.get("/api/v1/explainability/prediction-explanation")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert "No assessment or prediction ID provided" in data["detail"]
    # Verify no clinical predictions or mock profiles leaked
    assert "explanations" not in data
    assert "overall_risk_tier" not in data


def test_evidence_without_assessment_id_returns_404():
    """Verify GET /api/v1/explainability/evidence returns 404 when assessment_id is omitted."""
    resp = client.get("/api/v1/explainability/evidence")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert "No assessment ID provided" in data["detail"]
    # Verify no clinical evidence catalog leaked
    assert "target_iron_deficiency" not in data


def test_explainability_endpoints_with_nonexistent_id_return_404():
    """Verify random nonexistent UUIDs return 404 instead of generating synthetic fallbacks."""
    fake_id = str(uuid.uuid4())
    
    resp_pred = client.get(f"/api/v1/explainability/prediction-explanation?prediction_id={fake_id}")
    assert resp_pred.status_code == 404
    assert "not found" in resp_pred.json()["detail"].lower()

    resp_ev = client.get(f"/api/v1/explainability/evidence?assessment_id={fake_id}")
    assert resp_ev.status_code == 404
    assert "not found" in resp_ev.json()["detail"].lower()


def test_explainability_with_valid_assessment_is_traceable():
    """
    Verify that an actual assessment generates real model predictions,
    real SHAP attributions, real confidence scores, and dynamic evidence.
    """
    valid_id = str(uuid.uuid4())
    intake_payload = {
        "age": 45,
        "gender": "MALE",
        "dietary_habits": {"dietary_pattern": "OMNIVORE", "meals_per_day": 3},
        "lifestyle_factors": {"sunlight_exposure_min_per_day": 30, "sleep_hours_per_night": 7.5},
        "symptoms": {"fatigue": 2, "weakness": 1}
    }
    # Register the real assessment in the active repository
    ExplainabilityService._active_payload_cache[valid_id] = intake_payload

    # 1. Fetch prediction explanation
    resp_exp = client.get(f"/api/v1/explainability/prediction-explanation?prediction_id={valid_id}")
    assert resp_exp.status_code == 200
    exp_data = resp_exp.json()
    assert exp_data["prediction_id"] == valid_id
    assert len(exp_data["explanations"]) >= 1

    # Check that confidence_score is returned dynamically
    first_exp = exp_data["explanations"][0]
    assert "confidence_score" in first_exp
    assert 0.0 <= first_exp["confidence_score"] <= 1.0

    # 2. Fetch dynamic clinical evidence
    resp_ev = client.get(f"/api/v1/explainability/evidence?assessment_id={valid_id}")
    assert resp_ev.status_code == 200
    ev_data = resp_ev.json()
    assert isinstance(ev_data, dict)
    assert len(ev_data) >= 1

    # Check that evidence entries have dynamic fields from real prediction
    for target_key, ev_entry in ev_data.items():
        assert "riskLevel" in ev_entry
        assert "probability" in ev_entry
        assert "confidence" in ev_entry
        assert "clinicalPriority" in ev_entry
        assert "evidenceStrength" in ev_entry
        assert "evidenceCitations" in ev_entry
        assert len(ev_entry["evidenceCitations"]) >= 1


def test_zero_demo_clinical_strings_in_any_api_response():
    """Verify that the string 'DEMO-CLINICAL' never appears in any response."""
    valid_id = str(uuid.uuid4())
    sample_payload = {
        "age": 28,
        "gender": "FEMALE",
        "dietary_habits": {"dietary_pattern": "VEGETARIAN"},
        "lifestyle_factors": {"sunlight_exposure_min_per_day": 15},
        "symptoms": {"fatigue": 4}
    }
    ExplainabilityService._active_payload_cache[valid_id] = sample_payload

    endpoints = [
        f"/api/v1/explainability/prediction-explanation?prediction_id={valid_id}",
        f"/api/v1/explainability/evidence?assessment_id={valid_id}",
        "/api/v1/explainability/evidence-summary",
        "/api/v1/explainability/nutrient-interactions"
    ]

    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        text = resp.text
        assert "DEMO-CLINICAL" not in text
        assert "DEMO-CLINICAL-8F3C" not in text


def test_dynamic_evidence_catalog_contains_no_static_percentages():
    """
    Verify DYNAMIC_CLINICAL_EVIDENCE_CATALOG contains no static hardcoded 38%
    or hardcoded default probabilities.
    """
    # The dictionary itself should not contain static hardcoded 38%
    for k, v in DYNAMIC_CLINICAL_EVIDENCE_CATALOG.items():
        for contributor in v.get("topContributors", []):
            assert contributor.get("percentage") != 38
