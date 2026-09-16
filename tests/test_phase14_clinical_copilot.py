"""
Phase 14 Test Suite — Clinical Copilot & Enterprise Deployment Readiness
Tests:
1. Unified Patient Intelligence Dossier Aggregation
2. 7-Part Clinical Assessment Generation
3. EMR-Ready SOAP Note Synthesizer
4. Differential Diagnostic Reasoning Engine & Competing Etiologies
5. Uncertainty Bounds & Statistical Confidence
6. Clinician Review Workflow (Approve, Reject, Modify, Escalate)
7. SHA-256 Tamper-Evident Audit Logging
8. Follow-Up Scheduling Engine (30, 60, 90-day Milestones)
9. Prometheus Observability Metrics Exposition
10. Database Pool Health & Diagnostics
11. Backward Compatibility & Zero Regressions
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.copilot.service import ClinicalCopilotService
from backend.app.modules.copilot.schemas import ClinicianReviewRequest
from backend.app.core.metrics import metrics

client = TestClient(app)

SAMPLE_PATIENT_PAYLOAD = {
    "patient_id": "PT-2026-TEST-14",
    "full_name": "Eleanor Vance",
    "age": 45,
    "gender": "FEMALE",
    "height_cm": 165.0,
    "weight_kg": 60.0,
    "dietary_pattern": "VEGAN",
    "meals_per_day": 3,
    "water_intake_liters": 2.0,
    "daily_fruit_vegetable_servings": 4,
    "activity_level": "SEDENTARY",
    "sleep_hours_per_night": 6.5,
    "sunlight_exposure_min_per_day": 15,
    "stress_level": 7,
    "smoking_status": "NEVER",
    "alcohol_consumption": "NONE",
    "symptoms": {
        "fatigue": 8,
        "muscle_weakness": 6,
        "cognitive_fog": 6,
        "cold_intolerance": 7
    }
}


# ==============================================================================
# 1. Unified Patient Intelligence Dossier Tests
# ==============================================================================

def test_patient_intelligence_dossier_aggregation():
    response = client.post("/api/v1/copilot/patient-intelligence", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    # Verify 10 clinical data streams are present
    assert "dossier_id" in data
    assert data["demographics"]["full_name"] == "Eleanor Vance"
    assert data["demographics"]["dietary_pattern"] == "VEGAN"
    assert len(data["deficiencies"]) > 0
    assert len(data["biomarkers"]) >= 5
    assert len(data["symptoms"]) >= 3
    assert "baseline_health_score" in data["outcomes"]
    assert len(data["precision_foods"]) > 0
    assert len(data["supplement_plan"]) > 0
    assert 0 <= data["composite_risk_score"] <= 100
    assert len(data["top_shap_features"]) > 0
    assert len(data["safety_governance_alerts"]) > 0


def test_dossier_vegan_adaptation():
    response = client.post("/api/v1/copilot/patient-intelligence", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    alerts = " ".join(data["safety_governance_alerts"])
    assert "phytate" in alerts.lower() or "plant-based" in alerts.lower()


# ==============================================================================
# 2. 7-Part Clinical Assessment Tests
# ==============================================================================

def test_clinical_assessment_generator_7_parts():
    response = client.post("/api/v1/copilot/clinical-assessment", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    # Part 1: Executive Summary
    assert len(data["executive_summary"]) > 50
    assert "Eleanor Vance" in data["executive_summary"]

    # Part 2: Clinical Findings
    assert len(data["clinical_findings"]) >= 3

    # Part 3: Deficiency Risk Summary
    risk_summary = data["deficiency_risk_summary"]
    assert "critical_risk_count" in risk_summary
    assert "high_risk_count" in risk_summary
    assert len(risk_summary["primary_targets"]) > 0

    # Part 4: Contributing Factors
    assert len(data["contributing_factors"]) >= 2
    categories = [cf["category"] for cf in data["contributing_factors"]]
    assert "Dietary Pattern" in categories

    # Part 5: Recommended Actions (Prioritized)
    assert len(data["recommended_actions"]) >= 2
    priorities = [ra["priority"] for ra in data["recommended_actions"]]
    assert any("Tier 1" in p for p in priorities)

    # Part 6: Monitoring Plan
    assert "biomarker_targets" in data["monitoring_plan"]
    assert len(data["monitoring_plan"]["biomarker_targets"]) >= 2

    # Part 7: Follow-Up Recommendations
    assert len(data["follow_up_recommendations"]) >= 3


# ==============================================================================
# 3. EMR-Ready SOAP Note Tests
# ==============================================================================

def test_soap_note_synthesis_structure():
    response = client.post("/api/v1/copilot/soap-note", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["patient_name"] == "Eleanor Vance"
    assert "chief_complaint" in data["subjective"]
    assert "history_of_present_illness" in data["subjective"]
    assert "vitals_and_anthropometrics" in data["objective"]
    assert "primary_diagnoses" in data["assessment"]
    assert "nutrition_prescriptions" in data["plan"]
    assert "supplementation_protocol" in data["plan"]

    # Formatted EMR Markdown string
    assert "SUBJECTIVE:" in data["formatted_text"]
    assert "OBJECTIVE:" in data["formatted_text"]
    assert "ASSESSMENT:" in data["formatted_text"]
    assert "PLAN:" in data["formatted_text"]
    assert "CLINICAL SOAP NOTE" in data["formatted_text"]


# ==============================================================================
# 4. Differential Diagnostic Reasoning Tests
# ==============================================================================

def test_differential_diagnostic_reasoning():
    response = client.post("/api/v1/copilot/differential-reasoning", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    assert len(data["differential_items"]) >= 5
    for item in data["differential_items"]:
        assert "nutrient" in item
        assert 0.0 <= item["predicted_probability"] <= 1.0
        assert 0.0 <= item["confidence_score"] <= 1.0
        assert len(item["uncertainty_interval"]) == 2
        # CI consistency: lower <= upper
        assert item["uncertainty_interval"][0] <= item["uncertainty_interval"][1]
        assert len(item["competing_causes"]) > 0
        assert len(item["confirmatory_diagnostics"]) > 0


def test_differential_confirmatory_labs():
    response = client.post("/api/v1/copilot/differential-reasoning", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200
    data = response.json()

    all_labs = []
    for item in data["differential_items"]:
        for conf in item["confirmatory_diagnostics"]:
            all_labs.append(conf["test"])

    # Verify standard gold-standard markers are present across differentials
    lab_text = " ".join(all_labs)
    assert "25-Hydroxyvitamin D" in lab_text or "Ferritin" in lab_text or "Methylmalonic Acid" in lab_text


# ==============================================================================
# 5. Clinician Review Workflow Tests
# ==============================================================================

def test_clinician_review_approve():
    req = {
        "patient_id": "PT-2026-TEST-14",
        "clinician_id": "DOC-7721",
        "clinician_name": "Dr. Gregory House",
        "clinician_role": "ATTENDING_PHYSICIAN",
        "decision": "APPROVE",
        "target_category": "MICRONUTRIENT_CARE_PLAN",
        "rationale": "Patient history and biomarker levels justify immediate initiation of supplementation."
    }
    response = client.post("/api/v1/clinical-review/action", json=req)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["decision"] == "APPROVE"
    assert data["clinician_name"] == "Dr. Gregory House"
    assert len(data["audit_hash"]) == 64  # Valid SHA-256 hex string


def test_clinician_review_escalate():
    req = {
        "patient_id": "PT-2026-TEST-14",
        "clinician_id": "DOC-7721",
        "clinician_name": "Dr. Lisa Cuddy",
        "clinician_role": "CHIEF_OF_MEDICINE",
        "decision": "ESCALATE",
        "target_category": "HEMATOLOGY_INVESTIGATION",
        "rationale": "Microcytic hypochromic indices require bone marrow and gastroenterology workup.",
        "escalation_specialty": "HEMATOLOGY"
    }
    response = client.post("/api/v1/clinical-review/action", json=req)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "ESCALATE"
    assert data["escalation_specialty"] == "HEMATOLOGY"


def test_clinician_review_patient_history():
    # Fetch history for test patient
    response = client.get("/api/v1/clinical-review/history/PT-2026-TEST-14")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2
    decisions = [r["decision"] for r in history]
    assert "APPROVE" in decisions
    assert "ESCALATE" in decisions


# ==============================================================================
# 6. Follow-Up Scheduling Engine Tests
# ==============================================================================

def test_follow_up_schedule_milestones():
    response = client.post("/api/v1/copilot/follow-up-schedule", json=SAMPLE_PATIENT_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    assert len(data["milestones"]) == 3
    milestone_days = [m["milestone_days"] for m in data["milestones"]]
    assert milestone_days == [30, 60, 90]

    # Verify 60-day milestone contains lab re-testing
    m_60 = next(m for m in data["milestones"] if m["milestone_days"] == 60)
    assert len(m_60["labs_to_retest"]) >= 2
    assert len(m_60["escalation_triggers"]) >= 1


# ==============================================================================
# 7. Enterprise Observability & Deployment Tests
# ==============================================================================

def test_prometheus_metrics_endpoint():
    # Make a request to ensure counters are populated
    client.post("/api/v1/copilot/patient-intelligence", json=SAMPLE_PATIENT_PAYLOAD)
    
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    
    assert "nutriscan_http_requests_total" in content
    assert "nutriscan_http_request_duration_seconds" in content
    assert "nutriscan_copilot_operations_total" in content


def test_health_check_database_pool():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "status" in data["database"]
    assert "pool_size" in data["database"]


# ==============================================================================
# 8. Backward Compatibility Verification (Phases 1–13)
# ==============================================================================

def test_backward_compatibility_predict():
    """Verify Phase 3 / Phase 10 / Phase 12 / Phase 13 /predict continues working unchanged."""
    payload = {
        "age": 35,
        "gender": "MALE",
        "height_cm": 178.0,
        "weight_kg": 75.0,
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
            "meals_per_day": 3,
            "water_intake_liters": 2.5,
            "daily_fruit_vegetable_servings": 3,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": []
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 30,
            "stress_level": 4
        },
        "symptoms": {
            "fatigue": 4,
            "muscle_weakness": 2
        }
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "predictions" in data or "nutrient_predictions" in data
    assert "overall_risk" in data or "overall_severity" in data


def test_backward_compatibility_governance():
    """Verify Phase 12 Governance Safety Evaluation endpoint remains intact."""
    req = {
        "assessment": {
            "age": 35,
            "gender": "Male",
            "conditions": []
        },
        "recommendations": [
            {"target_nutrient": "Vitamin D", "dose_mg": 0.05}
        ]
    }
    response = client.post("/api/v1/safety/evaluate", json=req)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "safety_score" in data
    assert "safety_tier" in data
