"""
Automated Test Suite for Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Verifies:
1. Overall Nutritional Health Score (0-100) engine and 4 category classifications
2. Assessment summary synthesis and key clinical findings
3. Dashboard visualizations generation (Radar, Bar, Priority, SHAP, Interaction Graph, Recovery Timeline)
4. Vector PDF report generation engine with header validation
5. Reporting service orchestration, persistence mapping, and session caching
6. Production FastAPI endpoints:
   - POST /api/v1/reports/generate
   - GET  /api/v1/reports/{id}
   - GET  /api/v1/reports/{id}/pdf
   - GET  /api/v1/dashboard/{assessment_id}
"""

import uuid
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.reporting.health_scorer import OverallNutritionalHealthScorer
from backend.app.modules.reporting.summary_engine import AssessmentSummaryEngine
from backend.app.modules.reporting.dashboard_builder import DashboardBuilder
from backend.app.modules.reporting.pdf_generator import PDFReportGenerator
from backend.app.modules.reporting.service import ReportingService
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.modules.recommendation.service import RecommendationService
from backend.app.schemas.report import HealthScoreCategoryEnum


@pytest.fixture
def sample_patient_payload():
    return {
        "age": 34,
        "gender": "FEMALE",
        "height_cm": 168.0,
        "weight_kg": 62.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 3,
            "water_intake_liters": 2.4,
            "daily_fruit_vegetable_servings": 3,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": ["dairy-free", "meat-free"]
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 15,
            "stress_level": 6
        },
        "symptoms": {
            "fatigue": 7,
            "hair_loss": 5,
            "muscle_cramps": 4
        },
        "medical_history": [],
        "supplement_usage": []
    }


@pytest.fixture
def mock_predictions():
    return [
        {"nutrient": "Iron", "probability": 0.78, "risk_level": "HIGH", "confidence_level": "HIGH", "clinical_implication": "Hemoglobin cofactor"},
        {"nutrient": "Vitamin D", "probability": 0.72, "risk_level": "HIGH", "confidence_level": "HIGH", "clinical_implication": "Calcium homeostatic regulator"},
        {"nutrient": "Vitamin B12", "probability": 0.68, "risk_level": "HIGH", "confidence_level": "HIGH", "clinical_implication": "Neural methylation cofactor"},
        {"nutrient": "Calcium", "probability": 0.54, "risk_level": "MODERATE", "confidence_level": "HIGH", "clinical_implication": "Skeletal matrix mineral"},
        {"nutrient": "Magnesium", "probability": 0.48, "risk_level": "MODERATE", "confidence_level": "MEDIUM", "clinical_implication": "Enzymatic ATP activator"},
        {"nutrient": "Folate", "probability": 0.42, "risk_level": "MODERATE", "confidence_level": "HIGH", "clinical_implication": "DNA synthesis co-factor"},
        {"nutrient": "Zinc", "probability": 0.38, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Immune cellular signaling"},
        {"nutrient": "Vitamin C", "probability": 0.22, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Ascorbic antioxidant"},
        {"nutrient": "Vitamin A", "probability": 0.18, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Visual photopigment"},
        {"nutrient": "Vitamin E", "probability": 0.15, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Lipid membrane protection"},
        {"nutrient": "Protein", "probability": 0.12, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Structural amino acid pool"},
        {"nutrient": "Vitamin B1", "probability": 0.20, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Thiamine pyrophosphate bioenergetics"},
        {"nutrient": "Vitamin B2", "probability": 0.18, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "FMN and FAD redox cofactor"},
        {"nutrient": "Vitamin B3", "probability": 0.15, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "NAD/NADP cellular respiration"},
        {"nutrient": "Vitamin B6", "probability": 0.25, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "PLP neurotransmitter transamination"},
        {"nutrient": "Potassium", "probability": 0.45, "risk_level": "MODERATE", "confidence_level": "HIGH", "clinical_implication": "Cellular membrane resting potential"},
        {"nutrient": "Selenium", "probability": 0.22, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Glutathione peroxidase selenoproteins"},
        {"nutrient": "Iodine", "probability": 0.35, "risk_level": "LOW", "confidence_level": "HIGH", "clinical_implication": "Thyroid hormone thyroxine synthesis"}
    ]


# -----------------------------------------------------------------------------
# Test 1: Overall Nutritional Health Scorer Engine
# -----------------------------------------------------------------------------
def test_health_score_calculation_and_categories(mock_predictions, sample_patient_payload):
    # Test elevated risk payload
    interaction_analysis = {
        "total_active_interactions": 1,
        "overall_compounding_multiplier": 1.15,
        "interactions": [
            {"nutrients": ["Vitamin D", "Calcium"], "severity": "HIGH", "interaction_type": "SYNERGY"}
        ]
    }
    breakdown = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=mock_predictions,
        interaction_analysis=interaction_analysis,
        patient_data=sample_patient_payload
    )

    assert 0 <= breakdown.final_score <= 100
    assert breakdown.category in [
        HealthScoreCategoryEnum.EXCELLENT,
        HealthScoreCategoryEnum.GOOD,
        HealthScoreCategoryEnum.MODERATE_RISK,
        HealthScoreCategoryEnum.HIGH_RISK,
        HealthScoreCategoryEnum.CRITICAL
    ]
    assert breakdown.nutrient_risk_deduction > 0.0
    assert len(breakdown.interpretation) > 20

    # Test optimal healthy profile
    healthy_preds = [
        {"nutrient": p["nutrient"], "probability": 0.08, "risk_level": "LOW"}
        for p in mock_predictions
    ]
    healthy_patient = {
        "water_intake_liters": 2.8,
        "sunlight_exposure_min_per_day": 40,
        "sleep_hours_per_night": 8.0,
        "stress_level": 2,
        "activity_level": "HIGH",
        "daily_fruit_vegetable_servings": 5.0
    }
    healthy_breakdown = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=healthy_preds,
        interaction_analysis={"interactions": [], "overall_compounding_multiplier": 1.0},
        patient_data=healthy_patient
    )
    assert healthy_breakdown.final_score >= 85
    assert healthy_breakdown.category == HealthScoreCategoryEnum.EXCELLENT


# -----------------------------------------------------------------------------
# Test 2: Assessment Summary Engine
# -----------------------------------------------------------------------------
def test_assessment_summary_generation(mock_predictions, sample_patient_payload):
    summary = AssessmentSummaryEngine.generate_summary(
        patient_data=sample_patient_payload,
        nutrient_predictions=mock_predictions,
        health_score=68,
        health_category="MODERATE_RISK"
    )

    assert summary.user_profile["age"] == 34
    assert summary.user_profile["gender"] == "FEMALE"
    assert summary.user_profile["bmi"] > 0
    assert len(summary.top_risk_nutrients) >= 3
    assert "Iron" in summary.top_risk_nutrients
    assert len(summary.protective_factors) > 0
    assert len(summary.critical_lifestyle_factors) > 0
    assert len(summary.key_findings) >= 3
    assert len(summary.executive_summary_text) > 50


# -----------------------------------------------------------------------------
# Test 3: Dashboard Visualizations Bundle & SVGs
# -----------------------------------------------------------------------------
def test_dashboard_visualizations_bundle(mock_predictions):
    bundle = DashboardBuilder.build_all_visualizations(
        nutrient_predictions=mock_predictions,
        interaction_analysis={
            "interactions": [{"nutrients": ["Vitamin D", "Calcium"], "interaction_type": "SYNERGY", "severity": "HIGH"}]
        },
        explainability_data={
            "top_risk_drivers": [{"factor_name": "Low Sun", "impact_score": 0.12, "contribution_percentage": 25.0}],
            "top_protective_factors": [{"factor_name": "High Greens", "impact_score": -0.08, "contribution_percentage": 18.0}]
        },
        recovery_plan={
            "phase_7_day": {"phase_title": "Acute Replenishment", "primary_objective": "Relieve fatigue"},
            "phase_14_day": {"phase_title": "Absorption", "primary_objective": "Synergies"},
            "phase_30_day": {"phase_title": "Consolidation", "primary_objective": "Diversity"}
        }
    )

    # 1. Radar Chart
    assert bundle.radar_chart["chart_type"] == "RADAR"
    assert len(bundle.radar_chart["data"]) == 18
    assert "<svg" in bundle.radar_chart["svg"]
    assert "<polygon" in bundle.radar_chart["svg"]

    # 2. Bar Chart
    assert bundle.bar_chart["chart_type"] == "BAR_CHART"
    assert len(bundle.bar_chart["data"]) == 18
    assert "<svg" in bundle.bar_chart["svg"]

    # 3. Priority Ranking
    assert bundle.priority_ranking_chart["chart_type"] == "PRIORITY_RANKING"
    assert "<svg" in bundle.priority_ranking_chart["svg"]

    # 4. SHAP Feature Importance
    assert bundle.shap_importance_chart["chart_type"] == "SHAP_IMPORTANCE"
    assert "<svg" in bundle.shap_importance_chart["svg"]

    # 5. Interaction Graph
    assert bundle.interaction_graph["chart_type"] == "INTERACTION_GRAPH"
    assert len(bundle.interaction_graph["nodes"]) > 0
    assert len(bundle.interaction_graph["edges"]) > 0
    assert "<svg" in bundle.interaction_graph["svg"]

    # 6. Recovery Progress Timeline
    assert bundle.recovery_timeline["chart_type"] == "RECOVERY_TIMELINE"
    assert len(bundle.recovery_timeline["milestones"]) == 3
    assert "<svg" in bundle.recovery_timeline["svg"]


# -----------------------------------------------------------------------------
# Test 4: Vector PDF Report Generation Engine
# -----------------------------------------------------------------------------
def test_pdf_report_generation(mock_predictions, sample_patient_payload):
    summary = AssessmentSummaryEngine.generate_summary(
        patient_data=sample_patient_payload,
        nutrient_predictions=mock_predictions,
        health_score=72,
        health_category="GOOD"
    )

    report_payload = {
        "report_id": str(uuid.uuid4()),
        "assessment_id": str(uuid.uuid4()),
        "overall_health_score": 72,
        "health_score_category": "GOOD",
        "summary": summary.model_dump(),
        "nutrient_predictions": mock_predictions,
        "nutrient_interactions": {
            "interactions": [
                {
                    "nutrients": ["Vitamin D", "Calcium"],
                    "interaction_type": "SYNERGY",
                    "clinical_mechanism": "Calcitriol upregulates intestinal calcium transporters.",
                    "actionable_guidance": "Pair sun exposure or D3 with dietary calcium sources."
                }
            ]
        },
        "recommendations": {
            "priority_1_foods": [{"food_name": "Lentils", "food_group": "LEGUMES"}],
            "lifestyle_interventions": [{"category": "HYDRATION", "action": "Drink 2.5L water", "target": "2.5 L/day"}]
        }
    }

    pdf_bytes = PDFReportGenerator.generate_pdf(report_payload)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")

    # Also test fallback engine directly
    fallback_bytes = PDFReportGenerator._generate_fallback_pdf(report_payload)
    assert isinstance(fallback_bytes, bytes)
    assert fallback_bytes.startswith(b"%PDF-")


# -----------------------------------------------------------------------------
# Test 5: Reporting Service Orchestration & Caching
# -----------------------------------------------------------------------------
def test_reporting_service_orchestration(sample_patient_payload):
    assessment_id = uuid.uuid4()
    id_str = str(assessment_id)

    # Prime explainability cache
    engine = PredictionService.get_engine()
    pred_result = engine.screen_patient(sample_patient_payload, compute_explainability=True)
    ExplainabilityService.register_prediction_run(id_str, sample_patient_payload, pred_result)

    # 1. Generate Report
    report = ReportingService.generate_report(
        assessment_id=assessment_id,
        report_title="Automated Test Nutritional Report",
        export_pdf=True
    )

    assert report.assessment_id == assessment_id
    assert 0 <= report.overall_health_score <= 100
    assert report.status == "COMPLETED"
    assert "/api/v1/reports/" in report.pdf_file_url
    assert len(report.summary_text) > 30

    # 2. Retrieve by ID
    retrieved = ReportingService.get_report_by_id(report.id)
    assert retrieved is not None
    assert retrieved.id == report.id

    # 3. Retrieve PDF Bytes
    pdf_bytes = ReportingService.get_report_pdf_bytes(report.id)
    assert pdf_bytes.startswith(b"%PDF-")

    # 4. Get Dashboard
    dashboard = ReportingService.get_dashboard(assessment_id)
    assert dashboard.assessment_id == assessment_id
    assert dashboard.overall_health_score == report.overall_health_score
    assert len(dashboard.visualizations.radar_chart["data"]) == 18


# -----------------------------------------------------------------------------
# Test 6: FastAPI Reporting & Dashboard REST Endpoints
# -----------------------------------------------------------------------------
def test_fastapi_reporting_and_dashboard_endpoints(sample_patient_payload):
    client = TestClient(app)

    # Step 1: Execute screening to register prediction
    screen_res = client.post("/api/v1/predict", json=sample_patient_payload)
    assert screen_res.status_code == 200
    screen_data = screen_res.json()
    assessment_id = screen_data["assessment_id"]

    # Step 2: Test GET /api/v1/dashboard/{assessment_id}
    t0 = time.time()
    dash_res = client.get(f"/api/v1/dashboard/{assessment_id}")
    latency = (time.time() - t0) * 1000.0

    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "overall_health_score" in dash_data
    assert 0 <= dash_data["overall_health_score"] <= 100
    assert dash_data["health_score_category"] in ["EXCELLENT", "GOOD", "MODERATE_RISK", "HIGH_RISK"]
    assert "visualizations" in dash_data
    assert "radar_chart" in dash_data["visualizations"]
    assert "<svg" in dash_data["visualizations"]["radar_chart"]["svg"]
    assert latency < 500.0, f"Dashboard latency ({latency:.1f}ms) exceeded 500ms SLA"

    # Step 3: Test POST /api/v1/reports/generate
    gen_res = client.post("/api/v1/reports/generate", json={
        "assessment_id": assessment_id,
        "report_title": "Comprehensive Clinical Screening Report",
        "export_pdf": True
    })
    assert gen_res.status_code == 201
    gen_data = gen_res.json()
    report_id = gen_data["id"]
    assert gen_data["status"] == "COMPLETED"
    assert gen_data["overall_health_score"] == dash_data["overall_health_score"]

    # Step 4: Test GET /api/v1/reports/{id}
    rep_res = client.get(f"/api/v1/reports/{report_id}")
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert rep_data["id"] == report_id
    assert rep_data["assessment_id"] == assessment_id

    # Step 5: Test GET /api/v1/reports/{id}/pdf
    pdf_res = client.get(f"/api/v1/reports/{report_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")
    assert len(pdf_res.content) > 500
