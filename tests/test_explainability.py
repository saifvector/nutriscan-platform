"""
Comprehensive Automated Test Suite: Phase 4 Explainability & Risk Factor Analysis
Tests:
- SHAP feature attributions, directionality, and percentage normalization
- Positive vs. Protective factor separation
- Clinical reasoning narrative generation (Patient-facing & Clinician-facing)
- 5-Category risk factor extraction (Dietary, Lifestyle, Symptom, Medical, Supplement)
- Server-side SVG waterfall chart generation
- FastAPI Explainability REST endpoints and latency compliance (< 500 ms SLA)
"""

import pytest
import uuid
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml import (
    NutritionalInferenceEngine,
    ClinicalExplainabilityEngine,
    ClinicalReasoningEngine,
    DashboardVisualizer,
    TARGET_NUTRIENTS,
    NUTRIENT_CODES
)
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.explainability.service import ExplainabilityService

client = TestClient(app)


@pytest.fixture(scope="module")
def clinical_screening_payload():
    return {
        "age": 32,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 62.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 3,
            "water_intake_liters": 2.2,
            "daily_fruit_vegetable_servings": 1,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": ["dairy-free", "meat-free"]
        },
        "lifestyle_factors": {
            "activity_level": "SEDENTARY",
            "sleep_hours_per_night": 6.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 10,
            "stress_level": 8
        },
        "symptoms": {
            "fatigue": 9,
            "hair_loss": 7,
            "muscle_cramps": 6,
            "bone_pain": 3
        },
        "medical_history": [{"condition_name": "Celiac Disease", "is_active": True, "impacts_absorption": True}],
        "supplement_usage": []
    }


def test_clinical_reasoning_synthesis():
    """Verify narrative synthesis, clinician notes, and ICD-10 mappings."""
    pos_factors = [
        {"factor_name": "Insufficient Direct Sunlight Exposure (< 20 min/day)", "impact_score": 0.45},
        {"factor_name": "Dairy-Free Dietary Restriction", "impact_score": 0.35},
        {"factor_name": "Elevated Fatigue", "impact_score": 0.28}
    ]
    prot_factors = [
        {"factor_name": "Daily Produce Intake", "impact_score": -0.15}
    ]

    reasoning = ClinicalReasoningEngine.synthesize_narrative(
        nutrient_name="Vitamin D",
        risk_level="HIGH",
        probability=0.88,
        positive_factors=pos_factors,
        protective_factors=prot_factors
    )

    assert reasoning["nutrient"] == "Vitamin D"
    assert reasoning["risk_level"] == "HIGH"
    assert len(reasoning["primary_contributors"]) >= 2
    assert "Insufficient Direct Sunlight Exposure" in reasoning["narrative_explanation"]
    assert "protective" in reasoning["protective_summary"].lower()
    assert "E55.9" in str(reasoning["icd10_considerations"])
    assert "Serum 25-hydroxyvitamin D" in reasoning["clinical_notes"]


def test_categorized_risk_factors_extraction(clinical_screening_payload):
    """Verify accurate extraction into all 5 clinical categories + physiological."""
    categories = ClinicalReasoningEngine.extract_categorized_risk_factors(
        unscaled_features=clinical_screening_payload,
        nutrient_predictions=[{"nutrient": "Vitamin D", "risk_level": "HIGH"}]
    )

    assert "dietary_factors" in categories
    assert "lifestyle_factors" in categories
    assert "symptom_factors" in categories
    assert "medical_factors" in categories
    assert "supplement_factors" in categories
    assert "physiological_factors" in categories

    # Verify vegan diet captured in dietary
    diet_names = [f["factor_name"] for f in categories["dietary_factors"]]
    assert any("Vegan" in name for name in diet_names)

    # Verify low sunlight captured in lifestyle
    life_names = [f["factor_name"] for f in categories["lifestyle_factors"]]
    assert any("Sunlight" in name for name in life_names)

    # Verify celiac captured in medical
    med_names = [f["factor_name"] for f in categories["medical_factors"]]
    assert any("Malabsorption" in name or "Celiac" in name for name in med_names)

    # Verify absence of supplementation captured
    supp_names = [f["factor_name"] for f in categories["supplement_factors"]]
    assert any("Absence" in name for name in supp_names)


def test_svg_waterfall_generation():
    """Verify SVG waterfall plot rendering produces valid responsive markup."""
    steps = [
        {"factor_name": "Low Sunlight", "delta": 0.35},
        {"factor_name": "Vegan Diet", "delta": 0.20},
        {"factor_name": "Active Exercise", "delta": -0.10}
    ]
    svg = DashboardVisualizer.generate_waterfall_svg(
        nutrient_name="Vitamin D",
        base_value=0.25,
        final_value=0.70,
        steps=steps
    )

    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "Vitamin D" in svg
    assert "Baseline E[f(x)]" in svg
    assert "Low Sunlight" in svg


def test_local_shap_attribution_and_percentages(clinical_screening_payload):
    """Verify SHAP attributions, contribution percentage normalization, and positive/protective split."""
    engine = PredictionService.get_engine()
    X_df, unscaled_dict = engine.pipeline.transform_single(clinical_screening_payload)
    feature_names = engine.pipeline.feature_names_
    scaled_row = X_df.values[0]

    vit_d_model = engine.model.models_.get("Vitamin D")
    explanation = engine.explainability_engine.explain_nutrient_prediction(
        nutrient_name="Vitamin D",
        feature_names=feature_names,
        unscaled_features=unscaled_dict,
        scaled_feature_row=scaled_row,
        model_subestimator=vit_d_model,
        top_k=6,
        use_shap=True
    )

    assert "top_positive_factors" in explanation
    assert "top_protective_factors" in explanation
    assert "all_contributions" in explanation
    assert "waterfall_plot" in explanation

    # Check that positive factors have non-negative impact and protective have non-positive
    for f in explanation["top_positive_factors"]:
        assert f["impact_score"] >= 0
        assert f["direction"] == "RISK_INCREASING"

    for f in explanation["top_protective_factors"]:
        assert f["impact_score"] <= 0
        assert f["direction"] == "PROTECTIVE"

    # Check contribution percentage sum is reasonably bounded
    percentages = [f["contribution_percentage"] for f in explanation["all_contributions"]]
    assert len(percentages) > 0
    assert sum(percentages) <= 105.0  # Sum of top subsets <= 100% (or equal to 100% across all)


def test_global_feature_importance():
    """Verify global feature importance computation across all nutrients."""
    resp = ExplainabilityService.get_global_importance()
    assert resp.model_name is not None
    assert len(resp.top_global_drivers) >= 5
    first_driver = resp.top_global_drivers[0]
    assert first_driver.mean_absolute_shap > 0
    assert first_driver.relative_importance_percentage > 0


def test_fastapi_explainability_endpoint(clinical_screening_payload):
    """Verify POST /predict registers assessment and GET /explainability returns rich report."""
    # Step 1: Predict
    predict_res = client.post("/api/v1/predict", json=clinical_screening_payload)
    assert predict_res.status_code == 200
    pred_data = predict_res.json()
    assessment_id = pred_data.get("assessment_id")
    assert assessment_id is not None

    # Step 2: Get Explainability
    start = time.perf_counter()
    explain_res = client.get(f"/api/v1/predictions/{assessment_id}/explainability")
    latency = (time.perf_counter() - start) * 1000

    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert explain_data["overall_risk"] in ["LOW", "MODERATE", "HIGH"]
    assert len(explain_data["nutrients_explained"]) >= 10
    assert latency < 500, f"Explainability latency ({latency} ms) exceeded 500 ms SLA"

    # Inspect first explained nutrient
    first_nut = explain_data["nutrients_explained"][0]
    assert "nutrient" in first_nut
    assert "top_positive_factors" in first_nut
    assert "waterfall_plot" in first_nut
    assert "clinical_reasoning" in first_nut
    assert len(first_nut["clinical_reasoning"]["primary_contributors"]) > 0


def test_fastapi_risk_factors_endpoint(clinical_screening_payload):
    """Verify GET /api/v1/predictions/{id}/risk-factors partitions factors across all 5 categories."""
    predict_res = client.post("/api/v1/predict", json=clinical_screening_payload)
    assessment_id = predict_res.json()["assessment_id"]

    rf_res = client.get(f"/api/v1/predictions/{assessment_id}/risk-factors")
    assert rf_res.status_code == 200
    rf_data = rf_res.json()

    assert rf_data["total_risk_factors_identified"] > 0
    assert len(rf_data["dietary_factors"]) > 0
    assert len(rf_data["lifestyle_factors"]) > 0
    assert len(rf_data["symptom_factors"]) > 0
    assert len(rf_data["medical_factors"]) > 0


def test_fastapi_single_nutrient_and_svg_endpoint(clinical_screening_payload):
    """Verify drill-down for a single nutrient and standalone SVG chart endpoint."""
    predict_res = client.post("/api/v1/predict", json=clinical_screening_payload)
    assessment_id = predict_res.json()["assessment_id"]

    # 1. Single nutrient drill down
    drill_res = client.get(f"/api/v1/predictions/{assessment_id}/explainability/VITAMIN_D")
    assert drill_res.status_code == 200
    drill_data = drill_res.json()
    assert drill_data["nutrient_code"] == "VITAMIN_D"
    assert len(drill_data["top_positive_factors"]) > 0

    # 2. SVG waterfall visualization
    svg_res = client.get(f"/api/v1/predictions/{assessment_id}/visualizations/waterfall/VITAMIN_D?format=svg")
    assert svg_res.status_code == 200
    assert "image/svg+xml" in svg_res.headers.get("content-type", "")
    assert "<svg" in svg_res.text
    assert "</svg>" in svg_res.text

    # 3. JSON recharts contract
    json_res = client.get(f"/api/v1/predictions/{assessment_id}/visualizations/waterfall/VITAMIN_D?format=json")
    assert json_res.status_code == 200
    json_data = json_res.json()
    assert json_data["format"] == "recharts_json"
    assert len(json_data["chart_data"]) > 0
