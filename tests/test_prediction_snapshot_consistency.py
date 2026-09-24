"""
Automated Integration Test: Prediction Snapshot Consistency
Verifies that the AssessmentPredictionSnapshot provides an immutable, single source of truth:
- Dashboard health score, category, and risk counts match the snapshot exactly.
- Reasoning module explanations and evidence catalog match the snapshot exactly.
- Zero recomputation divergence between Dashboard and Reasoning.
"""

import pytest
import uuid
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.reporting.service import ReportingService
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.core.persistence import PersistenceRepository, initialize_database

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    initialize_database()

def test_assessment_snapshot_dashboard_reasoning_consistency():
    """Verify that Dashboard and Reasoning are in 100% mathematical and logical agreement with the Snapshot."""
    asmt_id = uuid.uuid4()
    payload = {
        "user_id": str(uuid.uuid4()),
        "age": 28,
        "gender": "FEMALE",
        "dietary_pattern": "OMNIVORE",
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
            "daily_fruit_vegetable_servings": 5,
            "dietary_restrictions": []
        },
        "lifestyle": {
            "sunlight_exposure_min_per_day": 45,
            "sleep_hours_per_night": 8.0,
            "stress_level": 2,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "physical_activity_level": "MODERATE"
        },
        "biomarkers": {
            "serum_ferritin": 60.0,
            "serum_b12": 650.0,
            "serum_folate": 16.0,
            "serum_calcium": 9.5,
            "serum_magnesium": 2.2,
            "serum_potassium": 4.5,
            "serum_zinc": 95.0,
            "serum_selenium": 125.0
        },
        "symptoms": {}
    }

    # 1. Screen patient and generate authoritative snapshot
    snapshot = PredictionService.predict_assessment(
        assessment_payload=payload,
        assessment_id=asmt_id,
        compute_explainability=True
    )

    assert "health_score" in snapshot
    assert "risk_counts" in snapshot
    assert "explanations" in snapshot
    assert "evidence_catalog" in snapshot

    snap_high = snapshot["risk_counts"]["HIGH"]
    snap_mod = snapshot["risk_counts"]["MODERATE"]
    snap_low = snapshot["risk_counts"]["LOW"]

    # 2. Query Dashboard
    dashboard = ReportingService.get_dashboard(asmt_id)
    assert dashboard.overall_health_score == snapshot["health_score"]
    assert dashboard.health_score_category.value == snapshot["category"]
    assert dashboard.nutrient_risk_distribution["HIGH"] == snap_high
    assert dashboard.nutrient_risk_distribution["MODERATE"] == snap_mod
    assert dashboard.nutrient_risk_distribution["LOW"] == snap_low
    assert dashboard.overall_risk_classification == snapshot["overall_risk"]

    # 3. Query Explainability
    explanation_resp = ExplainabilityService.explain_clinical_prediction(
        assessment_payload=payload,
        prediction_id=asmt_id
    )
    assert len(explanation_resp.explanations) == 9
    assert explanation_resp.overall_risk_tier == snapshot["overall_risk"]

    # Verify that each explanation matches the snapshot's risk tier
    exp_map = {e.target: e for e in explanation_resp.explanations}
    for target_pred in snapshot["predictions"]:
        t_id = target_pred["target"]
        assert t_id in exp_map
        exp_tier = exp_map[t_id].risk_tier.value if hasattr(exp_map[t_id].risk_tier, 'value') else str(exp_map[t_id].risk_tier)
        assert exp_tier == target_pred["risk_tier"]

    # 4. Query Dynamic Evidence Catalog
    evidence_catalog = ExplainabilityService.get_dynamic_evidence_base(assessment_id=str(asmt_id))
    for target_id, entry in evidence_catalog.items():
        matched_pred = next((p for p in snapshot["predictions"] if p["target"] == target_id), None)
        assert matched_pred is not None
        assert entry["risk_tier"] == matched_pred["risk_tier"]
        if matched_pred["risk_tier"] == "HIGH":
            assert "Tier 1 — High Priority Repletion" in entry["clinical_priority"]
        elif matched_pred["risk_tier"] == "MODERATE":
            assert "Tier 2 — Moderate Clinical Guidance" in entry["clinical_priority"]
        else:
            assert "Tier 3 — Routine Monitoring" in entry["clinical_priority"]


def test_deficient_patient_snapshot_consistency():
    """Test a deficient patient profile: elevated deficiency, capped score, Tier 1 priority."""
    asmt_id = uuid.uuid4()
    payload = {
        "user_id": str(uuid.uuid4()),
        "age": 35,
        "gender": "FEMALE",
        "dietary_pattern": "VEGAN",
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "daily_fruit_vegetable_servings": 1,
            "dietary_restrictions": ["vegan"]
        },
        "lifestyle": {
            "sunlight_exposure_min_per_day": 5,
            "sleep_hours_per_night": 4.5,
            "stress_level": 9,
            "smoking_status": "DAILY",
            "alcohol_consumption": "DAILY",
            "physical_activity_level": "SEDENTARY"
        },
        "biomarkers": {
            "serum_ferritin": 6.0,  # Critical ferritin -> Iron deficiency
            "hemoglobin": 9.2,      # Anemia
            "serum_b12": 110.0,     # Critical B12
            "serum_folate": 3.0,
            "serum_calcium": 8.0,
            "serum_magnesium": 1.4,
            "serum_potassium": 3.2
        },
        "symptoms": {
            "severe_fatigue": 9,
            "dizziness_lightheadedness": 8,
            "brittle_nails": 7,
            "pale_skin": 8,
            "hair_loss": 6
        }
    }

    # 1. Screen patient and generate authoritative snapshot
    snapshot = PredictionService.predict_assessment(
        assessment_payload=payload,
        assessment_id=asmt_id,
        compute_explainability=True
    )

    high_count = snapshot["risk_counts"]["HIGH"]
    assert high_count >= 1, "At least one target must be HIGH risk given critical biomarkers"

    # Health score must be capped (<= 68 for 1+ high risk, <= 48 for 2+ high risk)
    assert snapshot["health_score"] <= 68
    assert snapshot["category"] in ["MODERATE_RISK", "HIGH_RISK", "CRITICAL"]

    # 2. Query Dashboard
    dashboard = ReportingService.get_dashboard(asmt_id)
    assert dashboard.overall_health_score == snapshot["health_score"]
    assert dashboard.health_score_category.value == snapshot["category"]
    assert dashboard.nutrient_risk_distribution["HIGH"] == high_count
    assert dashboard.overall_risk_classification == "HIGH"

    # 3. Query Explainability
    explanation_resp = ExplainabilityService.explain_clinical_prediction(
        assessment_payload=payload,
        prediction_id=asmt_id
    )
    high_explanations = [
        e for e in explanation_resp.explanations
        if (e.risk_tier.value if hasattr(e.risk_tier, 'value') else str(e.risk_tier)) == "HIGH"
    ]
    assert len(high_explanations) == high_count

    # 4. Query Dynamic Evidence Catalog
    evidence_catalog = ExplainabilityService.get_dynamic_evidence_base(assessment_id=str(asmt_id))
    for exp in high_explanations:
        entry = evidence_catalog[exp.target]
        assert entry["risk_tier"] == "HIGH"
        assert "Tier 1 — High Priority Repletion" in entry["clinical_priority"]
