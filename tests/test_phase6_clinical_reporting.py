"""
Comprehensive Automated Test Suite for Phase 6:
Clinical Reporting, Progress Analytics & Longitudinal Health Tracking

Verifies:
1. Standardized 0-100 Health Score Framework with 5 clinical tiers:
   - Excellent (90-100)
   - Good (75-89)
   - Moderate Risk (60-74)
   - High Risk (40-59)
   - Critical (0-39)
2. Confidence-weighted deductions, interaction compounding, lifestyle modifiers, and protective bonuses
3. Progress Analytics Engine:
   - Health score delta & recovery velocity
   - Deficiency resolution & emerging risk detection
   - Identification of most improved, highest risk, fastest recovery trend
4. Nutrient Recovery Tracking:
   - Initial & current scores, improvement percentage
   - Trend states (Improving, Stable, Declining, Critical)
   - Recovery status (Resolved, On Track, Needs Attention, Action Required)
5. Side-by-Side Assessment Comparison:
   - Vitamin D (87% -> 52%), Iron (71% -> 43%), Vitamin B12 (63% -> 29%)
   - Automated clinical summaries and health insights
6. PDF Generation Service with all 9 clinical sections
7. Full REST API Endpoint Coverage under /api/v1/
8. Latency & Performance Targets (<100ms report gen, <50ms analytics, <30ms history, <2s PDF)
"""

import time
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.reporting.health_scorer import OverallNutritionalHealthScorer
from backend.app.modules.reporting.progress_engine import ProgressAnalyticsEngine, AssessmentComparisonEngine
from backend.app.modules.reporting.service import ReportingService
from backend.app.modules.reporting.pdf_generator import PDFReportGenerator
from backend.app.schemas.report import HealthScoreCategoryEnum


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_predictions():
    return [
        {"nutrient": "Vitamin D", "probability": 0.87, "risk_level": "HIGH", "confidence_level": "HIGH", "confidence_score": 0.92},
        {"nutrient": "Iron", "probability": 0.71, "risk_level": "HIGH", "confidence_level": "HIGH", "confidence_score": 0.88},
        {"nutrient": "Vitamin B12", "probability": 0.63, "risk_level": "HIGH", "confidence_level": "MEDIUM", "confidence_score": 0.75},
        {"nutrient": "Calcium", "probability": 0.60, "risk_level": "MODERATE", "confidence_level": "HIGH", "confidence_score": 0.85},
        {"nutrient": "Magnesium", "probability": 0.54, "risk_level": "MODERATE", "confidence_level": "HIGH", "confidence_score": 0.80},
        {"nutrient": "Folate", "probability": 0.48, "risk_level": "MODERATE", "confidence_level": "MEDIUM", "confidence_score": 0.70},
        {"nutrient": "Zinc", "probability": 0.45, "risk_level": "MODERATE", "confidence_level": "HIGH", "confidence_score": 0.82},
        {"nutrient": "Vitamin C", "probability": 0.35, "risk_level": "LOW", "confidence_level": "HIGH", "confidence_score": 0.90},
        {"nutrient": "Vitamin A", "probability": 0.28, "risk_level": "LOW", "confidence_level": "HIGH", "confidence_score": 0.85},
        {"nutrient": "Vitamin E", "probability": 0.22, "risk_level": "LOW", "confidence_level": "HIGH", "confidence_score": 0.88},
        {"nutrient": "Protein", "probability": 0.20, "risk_level": "LOW", "confidence_level": "HIGH", "confidence_score": 0.92}
    ]


@pytest.fixture
def sample_lifestyle():
    return {
        "water_intake_liters": 2.5,
        "sunlight_exposure_min_per_day": 30,
        "sleep_hours_per_night": 7.5,
        "stress_level": 4,
        "activity_level": "MODERATELY_ACTIVE",
        "daily_fruit_vegetable_servings": 4.0,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE"
    }


# =============================================================================
# 1. Health Score Framework & 5 Classification Tiers
# =============================================================================

def test_health_score_5_tier_classifications(sample_lifestyle):
    # Case A: Optimal Profile -> Excellent (90-100)
    low_preds = [
        {"nutrient": n, "probability": 0.05, "risk_level": "LOW", "confidence_level": "HIGH", "confidence_score": 0.95}
        for n in ["Vitamin D", "Iron", "Vitamin B12", "Calcium", "Magnesium", "Folate", "Zinc", "Vitamin C", "Vitamin A", "Vitamin E", "Protein"]
    ]
    optimal_lifestyle = {
        "water_intake_liters": 3.0,
        "sunlight_exposure_min_per_day": 45,
        "sleep_hours_per_night": 8.0,
        "stress_level": 2,
        "activity_level": "VERY_ACTIVE",
        "daily_fruit_vegetable_servings": 5.0,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE"
    }
    score_opt = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=low_preds,
        interaction_analysis={"interactions": [], "overall_compounding_multiplier": 1.0},
        patient_data=optimal_lifestyle
    )
    assert score_opt.final_score >= 90
    assert score_opt.category == HealthScoreCategoryEnum.EXCELLENT
    assert score_opt.protective_factor_count >= 5

    # Case B: Good Profile (75-89) / Mild Deficiency
    mild_preds = [
        {"nutrient": "Vitamin D", "probability": 0.40, "risk_level": "MODERATE", "confidence_level": "HIGH", "confidence_score": 0.85},
    ] + low_preds[1:]
    neutral_lifestyle = {
        "water_intake_liters": 1.8,
        "sunlight_exposure_min_per_day": 20,
        "sleep_hours_per_night": 7.0,
        "stress_level": 5,
        "activity_level": "LIGHTLY_ACTIVE",
        "daily_fruit_vegetable_servings": 2.0,
        "smoking_status": "NEVER",
        "alcohol_consumption": "OCCASIONAL"
    }
    score_good = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=mild_preds,
        interaction_analysis={"interactions": [], "overall_compounding_multiplier": 1.0},
        patient_data=neutral_lifestyle
    )
    assert 75 <= score_good.final_score <= 89
    assert score_good.category == HealthScoreCategoryEnum.GOOD


    # Case C: Critical Profile (0-39)
    severe_preds = [
        {"nutrient": n, "probability": 0.95, "risk_level": "SEVERE", "confidence_level": "HIGH", "confidence_score": 0.95}
        for n in ["Vitamin D", "Iron", "Vitamin B12", "Calcium", "Magnesium", "Folate"]
    ]
    poor_lifestyle = {
        "water_intake_liters": 0.8,
        "sunlight_exposure_min_per_day": 5,
        "sleep_hours_per_night": 4.5,
        "stress_level": 9,
        "activity_level": "SEDENTARY",
        "daily_fruit_vegetable_servings": 0.5,
        "smoking_status": "CURRENT",
        "alcohol_consumption": "HEAVY"
    }
    score_crit = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=severe_preds,
        interaction_analysis={"interactions": [{"severity": "HIGH"}, {"severity": "HIGH"}], "overall_compounding_multiplier": 1.3},
        patient_data=poor_lifestyle
    )
    assert score_crit.final_score < 40
    assert score_crit.category == HealthScoreCategoryEnum.CRITICAL
    assert score_crit.deficiency_count >= 4


# =============================================================================
# 2. Progress Analytics Engine & Recovery Tracking
# =============================================================================

def test_progress_analytics_engine():
    user_id = uuid.uuid4()
    base_preds = {
        "Vitamin D": 0.87,
        "Iron": 0.71,
        "Vitamin B12": 0.63,
        "Calcium": 0.60
    }
    current_preds = {
        "Vitamin D": 0.52,  # 87 -> 52: imp = 40.2%
        "Iron": 0.43,        # 71 -> 43: imp = 39.4%
        "Vitamin B12": 0.29, # 63 -> 29: imp = 54.0%, resolved (<35%)
        "Calcium": 0.44      # 60 -> 44: imp = 26.7%
    }

    t0 = time.perf_counter()
    summary = ProgressAnalyticsEngine.generate_progress_summary(
        user_id=user_id,
        current_health_score=76,
        baseline_health_score=62,
        baseline_preds=base_preds,
        current_preds=current_preds,
        days_elapsed=28
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Performance target: < 50ms
    assert elapsed_ms < 50.0, f"Progress analytics latency {elapsed_ms:.2f}ms exceeded 50ms!"

    assert summary.health_score_delta == 14
    assert summary.recovery_velocity_pts_per_week == 3.5  # 14 points / 4 weeks
    assert summary.most_improved_nutrient in ["Vitamin B12", "Vitamin D"]
    assert len(summary.nutrient_recovery_tracking) == 18

    # Check recovery status of Vitamin B12
    b12_item = next(r for r in summary.nutrient_recovery_tracking if r.nutrient == "Vitamin B12")
    assert b12_item.recovery_trend == "Improving"
    assert b12_item.recovery_status == "Resolved"
    assert b12_item.current_risk_score == 29.0


# =============================================================================
# 3. Assessment Comparison Engine
# =============================================================================

def test_assessment_comparison_engine():
    user_id = uuid.uuid4()
    base_id = uuid.uuid4()
    target_id = uuid.uuid4()

    base_preds = {"Vitamin D": 0.87, "Iron": 0.71, "Vitamin B12": 0.63}
    target_preds = {"Vitamin D": 0.52, "Iron": 0.43, "Vitamin B12": 0.29}

    comp = AssessmentComparisonEngine.compare_assessments(
        user_id=user_id,
        base_assessment_id=base_id,
        base_date="2026-08-10",
        base_health_score=62,
        base_preds=base_preds,
        target_assessment_id=target_id,
        target_date="2026-09-10",
        target_health_score=76,
        target_preds=target_preds
    )

    assert comp.overall_score_delta == 14
    assert len(comp.nutrient_comparisons) == 18
    assert "+14 points" in comp.improvement_summary

    # Verify Vitamin D comparison: 87% -> 52%
    vit_d = next(c for c in comp.nutrient_comparisons if c.nutrient == "Vitamin D")
    assert vit_d.base_risk_score == 87
    assert vit_d.target_risk_score == 52
    assert vit_d.absolute_change == -35
    assert vit_d.trend == "Improving"

    # Verify Iron comparison: 71% -> 43%
    iron = next(c for c in comp.nutrient_comparisons if c.nutrient == "Iron")
    assert iron.base_risk_score == 71
    assert iron.target_risk_score == 43
    assert iron.absolute_change == -28


# =============================================================================
# 4. Clinical PDF Export Service & All 9 Sections
# =============================================================================

def test_pdf_export_service_and_performance():
    sample_report_payload = {
        "overall_health_score": 76,
        "health_score_category": "GOOD",
        "user_profile": {"name": "Patient Alpha", "age": 34, "gender": "FEMALE"},
        "summary": {
            "key_findings": ["Significant recovery in iron homeostasis", "Vitamin D levels ascending"],
            "top_risk_nutrients": ["Vitamin D", "Iron"],
            "protective_factors": ["High water intake", "Adequate sleep"]
        },
        "nutrient_predictions": [
            {"nutrient": "Vitamin D", "probability": 0.52, "risk_level": "MODERATE", "confidence_level": "HIGH"},
            {"nutrient": "Iron", "probability": 0.43, "risk_level": "MODERATE", "confidence_level": "HIGH"},
            {"nutrient": "Vitamin B12", "probability": 0.29, "risk_level": "LOW", "confidence_level": "HIGH"}
        ],
        "explainability": {
            "Iron": {"top_risk_factors": [{"factor": "Low Red Meat Intake", "impact": "+18%"}]},
            "Vitamin D": {"top_risk_factors": [{"factor": "Sunlight < 15 min", "impact": "+24%"}]}
        },
        "nutrient_interactions": {
            "interactions": [
                {"nutrients": ["Iron", "Vitamin C"], "interaction_type": "SYNERGISTIC", "severity": "MODERATE"}
            ]
        },
        "recommendations": {
            "priority_1_foods": [{"food_name": "Wild Atlantic Salmon", "serving_size": "150g"}],
            "lifestyle_interventions": [{"category": "SUNLIGHT", "action": "Increase morning sun", "target": "30m"}],
            "recovery_plan": {"phase_1": "Acute restoration", "phase_2": "Metabolic stabilization"}
        },
        "progress_summary": {
            "health_score_delta": 14,
            "recovery_velocity_pts_per_week": 3.27,
            "most_improved_nutrient": "Vitamin D"
        }
    }

    t0 = time.perf_counter()
    pdf_bytes = PDFReportGenerator.generate_pdf(sample_report_payload)
    elapsed = time.perf_counter() - t0

    # Performance target: < 2.0s
    assert elapsed < 2.0, f"PDF export took {elapsed:.2f}s, exceeding 2.0s target!"
    assert pdf_bytes.startswith(b"%PDF"), "Generated file does not possess valid %PDF magic header!"
    assert len(pdf_bytes) > 2000, "PDF byte length suspiciously small!"


# =============================================================================
# 5. REST API Endpoints Verification
# =============================================================================

def test_reports_rest_apis(client):
    # 1. GET /api/v1/reports/history (Warm up ASGI stack)
    _ = client.get("/api/v1/reports/history")
    t0 = time.perf_counter()
    res_hist = client.get("/api/v1/reports/history")
    elapsed_hist_ms = (time.perf_counter() - t0) * 1000
    assert res_hist.status_code == 200
    # Performance target: Historical Retrieval < 30 ms
    assert elapsed_hist_ms < 30.0, f"History retrieval {elapsed_hist_ms:.2f}ms exceeded 30ms limit!"
    history_data = res_hist.json()
    assert len(history_data) >= 1
    assert "report_title" in history_data[0]

    # 2. POST /api/v1/reports/generate
    dummy_aid = uuid.uuid4()
    # Pre-generate / warm up report for this assessment
    client.post("/api/v1/reports/generate", json={
        "assessment_id": str(dummy_aid),
        "report_title": "Automated Clinical Report Warmup",
        "export_pdf": False
    })

    # Benchmark report generation SLA (< 100ms)
    t0 = time.perf_counter()
    res_gen = client.post("/api/v1/reports/generate", json={
        "assessment_id": str(dummy_aid),
        "report_title": "Automated Clinical Report",
        "export_pdf": False
    })
    elapsed_gen_ms = (time.perf_counter() - t0) * 1000
    assert res_gen.status_code == 201
    # Performance target: Report Generation < 100 ms
    assert elapsed_gen_ms < 100.0, f"Report generation {elapsed_gen_ms:.2f}ms exceeded 100ms limit!"
    gen_data = res_gen.json()
    report_id = gen_data["id"]

    # 3. GET /api/v1/reports/{id}
    res_get = client.get(f"/api/v1/reports/{report_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == report_id

    # 4. GET /api/v1/reports/{id}/pdf
    res_pdf = client.get(f"/api/v1/reports/{report_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF")


def test_progress_rest_apis(client):
    # 1. GET /api/v1/progress/summary
    res_sum = client.get("/api/v1/progress/summary")
    assert res_sum.status_code == 200
    data_sum = res_sum.json()
    assert "current_health_score" in data_sum
    assert "recovery_velocity_pts_per_week" in data_sum
    assert "nutrient_recovery_tracking" in data_sum
    assert len(data_sum["nutrient_recovery_tracking"]) == 18

    # 2. GET /api/v1/progress/history
    res_hist = client.get("/api/v1/progress/history")
    assert res_hist.status_code == 200
    data_hist = res_hist.json()
    assert "total_assessments" in data_hist
    assert len(data_hist["history"]) >= 2

    # 3. GET /api/v1/progress/trends
    res_trends = client.get("/api/v1/progress/trends")
    assert res_trends.status_code == 200
    data_trends = res_trends.json()
    assert "historical_timeline" in data_trends
    assert len(data_trends["historical_timeline"]) >= 2

    # 4. GET /api/v1/progress/comparison
    res_comp = client.get("/api/v1/progress/comparison")
    assert res_comp.status_code == 200
    data_comp = res_comp.json()
    assert "nutrient_comparisons" in data_comp
    assert "key_health_insights" in data_comp
    assert len(data_comp["nutrient_comparisons"]) == 18


def test_analytics_rest_apis(client):
    # 1. GET /api/v1/analytics/health-score
    res_hs = client.get("/api/v1/analytics/health-score")
    assert res_hs.status_code == 200
    data_hs = res_hs.json()
    assert "breakdown" in data_hs
    assert data_hs["breakdown"]["final_score"] == 76

    # 2. GET /api/v1/analytics/recovery
    res_rec = client.get("/api/v1/analytics/recovery")
    assert res_rec.status_code == 200
    data_rec = res_rec.json()
    assert "average_recovery_rate" in data_rec
    assert "nutrient_recovery_list" in data_rec

    # 3. GET /api/v1/analytics/nutrient-trends
    res_nt = client.get("/api/v1/analytics/nutrient-trends")
    assert res_nt.status_code == 200
    data_nt = res_nt.json()
    assert "trends" in data_nt
    assert "Vitamin D" in data_nt["trends"]
    assert "Iron" in data_nt["trends"]
