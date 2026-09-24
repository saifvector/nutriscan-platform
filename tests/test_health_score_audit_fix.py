"""
Unit and Integration Validation Suite for Health Score Audit Fix
Verifies:
1. Field mapping synchronization: current_score, health_score, breakdown.final_score
2. Parameterized /analytics/health-score?assessment_id=... loads real assessment data
3. Consistent health scores across:
   - GET /api/v1/analytics/health-score
   - GET /api/v1/dashboard/{assessment_id}
   - POST /api/v1/reports/generate
   - GET /api/v1/reports/{report_id}/pdf
4. Empty-state handling for non-existent assessment_id
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.modules.reporting.service import ReportingService
from backend.app.modules.reporting.health_scorer import OverallNutritionalHealthScorer
from backend.app.core.persistence import PersistenceRepository


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_assessment():
    aid = f"ASM-AUDIT-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "user_id": str(uuid.uuid4()),
        "age": 28,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "dietary_pattern": "OMNIVORE",
        "meals_per_day": 3,
        "water_intake_liters": 2.5,
        "daily_fruit_vegetable_servings": 4,
        "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 8.0,
        "sunlight_exposure_min_per_day": 35,
        "stress_level": 3,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE",
        "symptoms": {}
    }
    engine = PredictionService.get_engine()
    preds = engine.screen_patient(payload, compute_explainability=True)
    ExplainabilityService.register_prediction_run(aid, payload, preds)
    PersistenceRepository.save_assessment(aid, payload)
    PersistenceRepository.save_predictions(aid, preds)
    return aid, payload, preds


def test_unparameterized_health_score(client):
    """Verifies unparameterized /analytics/health-score returns 200 with baseline scores."""
    res = client.get("/api/v1/analytics/health-score")
    assert res.status_code == 200
    data = res.json()
    assert data["current_score"] == 76
    assert data["health_score"] == 76
    assert data["category"] == "GOOD"
    assert data["breakdown"]["final_score"] == 76


def test_nonexistent_assessment_health_score(client):
    """Verifies that querying a non-existent assessment returns clean empty state with has_assessment=False."""
    res = client.get("/api/v1/analytics/health-score?assessment_id=ASM-NONEXISTENT-99999")
    assert res.status_code == 200
    data = res.json()
    assert data["has_assessment"] is False
    assert data["hasAssessment"] is False
    assert data["current_score"] == 0
    assert data["health_score"] == 0
    assert data["category"] == "UNKNOWN"
    assert data["breakdown"]["final_score"] == 0


def test_real_assessment_health_score_consistency(client, registered_assessment):
    """Verifies that the analytics health score matches the dashboard and reports for the same assessment."""
    aid, payload, preds = registered_assessment

    # 1. Query /analytics/health-score with assessment_id
    res_hs = client.get(f"/api/v1/analytics/health-score?assessment_id={aid}")
    assert res_hs.status_code == 200
    hs_data = res_hs.json()

    assert hs_data["has_assessment"] is True
    assert hs_data["hasAssessment"] is True
    assert hs_data["current_score"] > 0
    assert hs_data["health_score"] == hs_data["current_score"]
    assert hs_data["breakdown"]["final_score"] == hs_data["current_score"]
    assert hs_data["category"] in ["EXCELLENT", "GOOD", "MODERATE_RISK", "HIGH_RISK", "CRITICAL"]

    computed_score = hs_data["current_score"]

    # 2. Query Dashboard
    dash = ReportingService.get_dashboard(uuid.uuid5(uuid.NAMESPACE_DNS, aid))
    assert dash.overall_health_score == computed_score
    assert dash.health_score_category.value == hs_data["category"]
    assert dash.score_breakdown.final_score == computed_score

    # 3. Generate Report
    res_rep = client.post("/api/v1/reports/generate", json={
        "assessment_id": aid,
        "report_title": "Consistency Verification Report",
        "export_pdf": True
    })
    assert res_rep.status_code in [200, 201]
    rep_data = res_rep.json()
    assert rep_data["overall_health_score"] == computed_score
    assert rep_data["health_score_category"] == hs_data["category"]

    # 4. Fetch PDF
    rep_id = rep_data["id"]
    res_pdf = client.get(f"/api/v1/reports/{rep_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.content.startswith(b"%PDF")
