"""
Test Suite: Phase 9 — Outcome Learning & Adaptive Nutrition Intelligence
Verifies all 8 core engines, database models, live REST APIs, and performance latency targets.
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.outcomes.adherence import AdherenceEngine
from backend.app.modules.outcomes.tracking import OutcomeTrackingEngine
from backend.app.modules.outcomes.effectiveness import RecommendationEffectivenessEngine
from backend.app.modules.outcomes.adaptive import AdaptiveRecommendationEngine
from backend.app.modules.outcomes.symptom_timeline import SymptomRecoveryTimelineEngine
from backend.app.modules.outcomes.prediction_accuracy import PredictionAccuracyValidationEngine
from backend.app.modules.outcomes.risk_monitoring import RelapseRiskMonitoringEngine
from backend.app.modules.outcomes.learning_dataset import ClinicalLearningDatasetBuilder
from backend.app.modules.outcomes.schemas import (
    AdherenceLogRequest,
    SymptomLogRequest,
    LabLogRequest,
    GenerateAdaptationRequest
)
from backend.app.models.outcomes import (
    AdherenceLog,
    SymptomJournal,
    LabResult,
    OutcomeMetric,
    AdaptiveRecommendation,
    PredictionValidation
)


@pytest.fixture
def client():
    return TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Adherence Intelligence Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_adherence_engine_scoring_and_classification():
    engine = AdherenceEngine()

    # Excellent compliance
    exc_score = engine.compute_daily_score(
        meal_pct=95.0,
        supp_pct=100.0,
        lifestyle_pct=90.0,
        hydration=2.8,
        sunlight=25,
        sleep=8.0,
        exercise=35
    )
    assert 90.0 <= exc_score <= 100.0
    assert engine._classify_tier(exc_score) == "EXCELLENT"

    # Moderate compliance
    mod_score = engine.compute_daily_score(
        meal_pct=65.0,
        supp_pct=70.0,
        lifestyle_pct=60.0,
        hydration=1.8,
        sunlight=10,
        sleep=6.0,
        exercise=15
    )
    assert 60.0 <= mod_score <= 74.0
    assert engine._classify_tier(mod_score) == "MODERATE"

    # Poor compliance
    poor_score = engine.compute_daily_score(
        meal_pct=40.0,
        supp_pct=30.0,
        lifestyle_pct=45.0,
        hydration=1.0,
        sunlight=5,
        sleep=5.0,
        exercise=0
    )
    assert poor_score < 60.0
    assert engine._classify_tier(poor_score) == "POOR"


def test_adherence_engine_logging_and_summary():
    engine = AdherenceEngine()
    req = AdherenceLogRequest(
        assessment_id="test_patient_1",
        meal_adherence_pct=88.0,
        supplement_adherence_pct=100.0,
        lifestyle_adherence_pct=85.0,
        hydration_liters=2.6,
        sunlight_minutes=20,
        sleep_hours=7.5,
        exercise_minutes=30,
        missed_items=["Evening snack timing"]
    )
    log_item = engine.log_adherence(req)
    assert log_item.daily_adherence_score > 85.0
    assert log_item.adherence_tier in ["GOOD", "EXCELLENT"]

    summary = engine.get_adherence_summary("test_patient_1")
    assert summary.daily_adherence_score == log_item.daily_adherence_score
    assert summary.overall_adherence_tier in ["GOOD", "EXCELLENT"]
    assert "Evening snack timing" in summary.missed_interventions


def test_adherence_calculation_latency_target():
    """Performance Target: Adherence calculations < 20 ms"""
    engine = AdherenceEngine()
    t0 = time.perf_counter()
    _ = engine.compute_daily_score(90.0, 95.0, 85.0, 2.5, 20, 8.0, 30)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 20.0, f"Adherence latency exceeded 20ms: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Outcome Tracking Engine Tests (Symptoms, Labs, Recovery)
# ─────────────────────────────────────────────────────────────────────────────

def test_symptom_tracking_and_progression():
    engine = OutcomeTrackingEngine()
    timeline = engine.get_symptom_timeline("demo")

    assert timeline.symptoms_tracked_count == 9
    assert timeline.improving_count >= 1
    assert timeline.symptom_recovery_score > 50.0
    assert len(timeline.historical_curve_points) >= 4

    # Verify fatigue progress
    fatigue = next(s for s in timeline.symptom_progress if s.symptom_name == "Fatigue")
    assert fatigue.baseline_severity == 8.5
    assert fatigue.current_severity < fatigue.baseline_severity
    assert fatigue.percentage_improvement > 0.0
    assert fatigue.status in ["IMPROVING", "RESOLVED"]


def test_lab_tracking_and_biomarkers():
    engine = OutcomeTrackingEngine()
    labs = engine.get_lab_tracking("demo")

    assert len(labs.biomarkers) >= 6
    assert labs.overall_lab_adequacy_score > 80.0

    ferritin = next(b for b in labs.biomarkers if "Ferritin" in b.biomarker_name)
    assert ferritin.baseline_value == 14.2
    assert ferritin.current_value == 38.5
    assert ferritin.delta_value > 0

    vit_d = next(b for b in labs.biomarkers if "Vitamin D" in b.biomarker_name)
    assert vit_d.current_value > vit_d.baseline_value
    assert vit_d.status in ["NORMAL", "OPTIMAL"]


def test_recovery_status_summary():
    engine = OutcomeTrackingEngine()
    status = engine.get_recovery_status("demo")

    assert status.current_health_score > status.baseline_health_score
    assert status.health_score_delta > 20.0
    assert status.recovery_velocity_pts_per_week > 0.0
    assert status.recovery_status in ["RAPID_RECOVERY", "STEADY_RECOVERY"]


def test_outcome_analysis_latency_target():
    """Performance Target: Outcome analysis < 50 ms"""
    engine = OutcomeTrackingEngine()
    t0 = time.perf_counter()
    _ = engine.get_symptom_timeline("demo")
    _ = engine.get_lab_tracking("demo")
    _ = engine.get_recovery_status("demo")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 50.0, f"Outcome analysis exceeded 50ms: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Recommendation Effectiveness Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_effectiveness_engine():
    engine = RecommendationEffectivenessEngine()
    res = engine.evaluate_effectiveness("demo")

    assert res.overall_effectiveness_score > 70.0
    assert len(res.top_effective_foods) >= 2
    assert len(res.top_effective_supplements) >= 2
    assert len(res.recovery_accelerators) >= 2
    assert len(res.recovery_bottlenecks) >= 1

    # Check that iron bisglycinate is an accelerator
    fe = next((a for a in res.recovery_accelerators if "Iron" in a.name), None)
    assert fe is not None
    assert fe.effectiveness_score >= 90.0

    # Check that unsteamed spinach is identified as a bottleneck
    spinach = next((b for b in res.recovery_bottlenecks if "Spinach" in b.name), None)
    assert spinach is not None
    assert spinach.effectiveness_score < 50.0


# ─────────────────────────────────────────────────────────────────────────────
# 4. Adaptive Recommendation Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_adaptive_recommendation_scenarios():
    engine = AdaptiveRecommendationEngine()

    # Scenario A: Fish Avoidance
    req_a = GenerateAdaptationRequest(assessment_id="demo", force_scenario="FISH_AVOIDANCE")
    plan_a = engine.generate_adaptations(req_a)
    assert plan_a.has_active_adaptations is True
    assert any(a.scenario_category == "SCENARIO_A_FOOD_AVOIDANCE" for a in plan_a.active_adaptations)
    item_a = next(a for a in plan_a.active_adaptations if a.scenario_category == "SCENARIO_A_FOOD_AVOIDANCE")
    assert any("Egg" in alt or "Yeast" in alt or "Algae" in alt for alt in item_a.alternative_interventions)

    # Scenario B: Sunlight Target Failure
    req_b = GenerateAdaptationRequest(assessment_id="demo", force_scenario="SUNLIGHT_FAILURE")
    plan_b = engine.generate_adaptations(req_b)
    item_b = next(a for a in plan_b.active_adaptations if a.scenario_category == "SCENARIO_B_SUNLIGHT_FAILURE")
    assert any("10,000 Lux" in alt or "5,000 IU" in alt for alt in item_b.alternative_interventions)

    # Scenario C: Supplement Resistance
    req_c = GenerateAdaptationRequest(assessment_id="demo", force_scenario="SUPPLEMENT_RESISTANCE")
    plan_c = engine.generate_adaptations(req_c)
    item_c = next(a for a in plan_c.active_adaptations if a.scenario_category == "SCENARIO_C_SUPPLEMENT_RESISTANCE")
    assert any("Molasses" in alt or "Epsom" in alt for alt in item_c.alternative_interventions)


def test_adaptation_generation_latency_target():
    """Performance Target: Adaptation generation < 100 ms"""
    engine = AdaptiveRecommendationEngine()
    t0 = time.perf_counter()
    _ = engine.generate_adaptations(GenerateAdaptationRequest(assessment_id="demo", force_scenario="ALL"))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 100.0, f"Adaptation latency exceeded 100ms: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Symptom Recovery Timeline Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_symptom_recovery_timeline():
    engine = SymptomRecoveryTimelineEngine()
    timeline = engine.compute_timeline("demo")

    assert timeline.symptom_recovery_score > 60.0
    assert len(timeline.symptom_progress) == 9
    assert len(timeline.historical_curve_points) == 6

    # Verify days to resolution forecast
    for p in timeline.symptom_progress:
        if p.status == "IMPROVING":
            assert p.forecast_days_to_resolution is not None and p.forecast_days_to_resolution > 0


# ─────────────────────────────────────────────────────────────────────────────
# 6. Prediction Accuracy Validation Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_prediction_accuracy_validation():
    engine = PredictionAccuracyValidationEngine()
    accuracy = engine.validate_accuracy("demo")

    assert accuracy.overall_prediction_accuracy_pct >= 95.0
    assert accuracy.projection_mean_absolute_error < 3.0
    assert accuracy.calibration_status in ["HIGHLY_CALIBRATED", "WELL_CALIBRATED"]
    assert len(accuracy.milestone_evaluations) == 3
    assert all(m.within_confidence_band for m in accuracy.milestone_evaluations)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Relapse & Risk Monitoring Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_relapse_risk_monitoring():
    engine = RelapseRiskMonitoringEngine()

    # Good compliance -> Low risk
    low_res = engine.monitor_risk(weekly_adherence=90.0, days_without_progress=2)
    assert low_res.overall_risk_level == "LOW"
    assert low_res.relapse_probability_score < 0.20

    # Critical drop -> High risk
    high_res = engine.monitor_risk(weekly_adherence=55.0, days_without_progress=15)
    assert high_res.overall_risk_level == "HIGH"
    assert high_res.relapse_probability_score >= 0.40
    assert any(f.flag_type == "DECLINING_ADHERENCE" for f in high_res.early_warning_flags)
    assert any(f.flag_type == "PLATEAU_DETECTED" for f in high_res.early_warning_flags)


def test_risk_monitoring_latency_target():
    """Performance Target: Risk monitoring < 50 ms"""
    engine = RelapseRiskMonitoringEngine()
    t0 = time.perf_counter()
    _ = engine.monitor_risk(weekly_adherence=75.0, days_without_progress=5)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 50.0, f"Risk monitoring latency exceeded 50ms: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 8. Clinical Learning Dataset Builder Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_learning_dataset_builder():
    builder = ClinicalLearningDatasetBuilder()
    data = builder.build_dataset_summary()

    assert data.total_longitudinal_records > 4000
    assert len(data.recovery_cohorts) >= 4
    assert len(data.intervention_effectiveness_cohorts) >= 2
    assert data.ready_for_model_retraining is True


# ─────────────────────────────────────────────────────────────────────────────
# 9. Database Model Integrity Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_database_models_mapping():
    # Instantiation checks
    adh = AdherenceLog(
        assessment_id="test_case",
        meal_adherence_pct=90.0,
        supplement_adherence_pct=100.0,
        lifestyle_adherence_pct=85.0,
        daily_adherence_score=91.5,
        adherence_tier="EXCELLENT",
        missed_items=[]
    )
    assert adh.daily_adherence_score == 91.5

    sym = SymptomJournal(
        assessment_id="test_case",
        symptom_scores={"Fatigue": 3.0},
        overall_symptom_score=3.0,
        symptom_recovery_score=70.0
    )
    assert sym.overall_symptom_score == 3.0

    lab = LabResult(
        assessment_id="test_case",
        biomarkers={"ferritin": 35.0}
    )
    assert lab.biomarkers["ferritin"] == 35.0

    adapt = AdaptiveRecommendation(
        assessment_id="test_case",
        trigger_reason="FISH_AVOIDANCE",
        scenario_category="SCENARIO_A",
        adaptation_rationale="Substituted pasture eggs and algae oil"
    )
    assert adapt.trigger_reason == "FISH_AVOIDANCE"


# ─────────────────────────────────────────────────────────────────────────────
# 10. Live FastAPI REST Endpoints & Latency Targets
# ─────────────────────────────────────────────────────────────────────────────

def test_api_get_adherence(client):
    res = client.get("/api/v1/outcomes/adherence?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "daily_adherence_score" in data
    assert "weekly_adherence_score" in data
    assert "compliance_breakdown" in data


def test_api_get_symptoms(client):
    res = client.get("/api/v1/outcomes/symptoms?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "symptom_recovery_score" in data
    assert len(data["symptom_progress"]) == 9


def test_api_get_recovery(client):
    res = client.get("/api/v1/outcomes/recovery?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "health_score_delta" in data
    assert "recovery_status" in data


def test_api_get_effectiveness(client):
    res = client.get("/api/v1/outcomes/effectiveness?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "top_effective_foods" in data
    assert "recovery_accelerators" in data


def test_api_get_risk_monitoring(client):
    res = client.get("/api/v1/outcomes/risk-monitoring?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "relapse_probability_score" in data
    assert "early_warning_flags" in data


def test_api_get_prediction_accuracy(client):
    res = client.get("/api/v1/outcomes/prediction-accuracy?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "overall_prediction_accuracy_pct" in data
    assert "model_reliability_score" in data


def test_api_get_adaptive_plans(client):
    res = client.get("/api/v1/outcomes/adaptive-plans?assessment_id=demo")
    assert res.status_code == 200
    data = res.json()
    assert "active_adaptations" in data
    assert "updated_recovery_plan" in data


def test_api_post_log_adherence(client):
    payload = {
        "assessment_id": "demo",
        "meal_adherence_pct": 92.0,
        "supplement_adherence_pct": 100.0,
        "lifestyle_adherence_pct": 88.0,
        "hydration_liters": 2.7,
        "sunlight_minutes": 25,
        "sleep_hours": 8.0,
        "exercise_minutes": 30
    }
    res = client.post("/api/v1/outcomes/log-adherence", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["daily_adherence_score"] > 88.0


def test_api_post_log_symptoms(client):
    payload = {
        "assessment_id": "demo",
        "symptoms": {"Fatigue": 2.5, "Brain Fog": 2.0}
    }
    res = client.post("/api/v1/outcomes/log-symptoms", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "symptom_recovery_score" in data


def test_api_post_generate_adaptation_and_latency(client):
    """Performance Target: API responses < 200 ms"""
    payload = {
        "assessment_id": "demo",
        "force_scenario": "FISH_AVOIDANCE"
    }
    t0 = time.perf_counter()
    res = client.post("/api/v1/outcomes/generate-adaptation", json=payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert res.status_code == 200
    data = res.json()
    assert data["has_active_adaptations"] is True
    assert elapsed_ms < 200.0, f"API response exceeded 200ms: {elapsed_ms:.2f}ms"
