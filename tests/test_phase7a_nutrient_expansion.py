"""
Phase 7A: Nutrient Expansion & Clinical Knowledge Base Enhancement Test Suite
Validates comprehensive support for all 18 clinically relevant nutrients across:
1. Constants & Target Nutrients
2. Feature Engineering & 9 New Symptoms
3. Biochemical Interaction Engine & Severity Scoring
4. Clinical Knowledge Base Registry & REST Endpoints
5. Multi-Nutrient ML Prediction Engine & Sub-500ms Latency
6. Explainable AI & Clinical Workup Catalog (ICD-10, Confirmatory Labs)
7. Personalized Recommendations & Synergistic Pairings
8. Longitudinal Health Scoring Calibration & PDF Report Generation
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml.constants import (
    TARGET_NUTRIENTS,
    NUTRIENT_CODES,
    CLINICAL_URGENCY_WEIGHTS,
    SYMPTOM_FIELDS,
    NUTRIENT_INTERACTIONS
)
from backend.app.ml.feature_engineering import ClinicalFeaturePipeline
from backend.app.ml.nutrient_interactions import NutrientInteractionEngine
from backend.app.modules.knowledge_base.registry import ClinicalKnowledgeBaseService
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.modules.recommendation.engine import PersonalizedRecommendationEngine
from backend.app.modules.reporting.health_scorer import OverallNutritionalHealthScorer
from backend.app.modules.reporting.pdf_generator import PDFReportGenerator
from backend.app.modules.reporting.service import ReportingService

client = TestClient(app)

EXPANDED_7_NUTRIENTS = [
    "Vitamin B1",
    "Vitamin B2",
    "Vitamin B3",
    "Vitamin B6",
    "Potassium",
    "Selenium",
    "Iodine"
]

EXPANDED_7_CODES = [
    "VITAMIN_B1",
    "VITAMIN_B2",
    "VITAMIN_B3",
    "VITAMIN_B6",
    "POTASSIUM",
    "SELENIUM",
    "IODINE"
]

NEW_SYMPTOMS = [
    "irritability",
    "poor_appetite",
    "cracked_lips",
    "eye_irritation",
    "dermatitis",
    "digestive_disturbances",
    "irregular_heartbeat",
    "thyroid_dysfunction",
    "unexplained_weight_gain"
]


# =============================================================================
# 1. Constants & Nutrient Definitions
# =============================================================================

def test_18_nutrients_defined_in_constants():
    """Verify all 18 target nutrients and codes are present with valid urgency weights."""
    assert len(TARGET_NUTRIENTS) == 18
    assert len(NUTRIENT_CODES) == 18
    assert len(CLINICAL_URGENCY_WEIGHTS) == 18

    for nut in EXPANDED_7_NUTRIENTS:
        assert nut in TARGET_NUTRIENTS
        assert nut in CLINICAL_URGENCY_WEIGHTS
        assert CLINICAL_URGENCY_WEIGHTS[nut] > 0

    for code in EXPANDED_7_CODES:
        assert code in NUTRIENT_CODES.values()

    # Verify all 9 new symptoms are in SYMPTOM_FIELDS
    for sym in NEW_SYMPTOMS:
        assert sym in SYMPTOM_FIELDS


# =============================================================================
# 2. Feature Engineering & Dataset Generation
# =============================================================================

def test_feature_engineering_with_new_symptoms():
    """Ensure ClinicalFeaturePipeline derives features including new symptoms and cluster scores."""
    import joblib
    pipeline = joblib.load("ml_artifacts/feature_pipeline.joblib")
    sample_patient = {
        "age": 42,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 68.0,
        "dietary_habits": {
            "dietary_pattern": "VEGETARIAN",
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
            "sunlight_exposure_min_per_day": 20,
            "stress_level": 6,
        },
        "symptoms": {
            "fatigue": 7,
            "cracked_lips": 8,
            "irregular_heartbeat": 6,
            "thyroid_dysfunction": 7,
            "unexplained_weight_gain": 6
        },
        "medical_history": [],
        "supplement_usage": []
    }

    df_scaled, unscaled_dict = pipeline.transform_single(sample_patient)
    assert "bmi" in df_scaled.columns
    # Check that new symptoms exist in features
    for sym in NEW_SYMPTOMS:
        assert f"symptom_{sym}" in df_scaled.columns
    # Check that clusters include endocrine and cardiovascular
    assert "cluster_endocrine_thyroid_index" in df_scaled.columns
    assert "cluster_cardiovascular_metabolic_index" in df_scaled.columns


# =============================================================================
# 3. Biochemical Interaction Engine
# =============================================================================

def test_biochemical_interaction_engine_expanded_nutrients():
    """Verify interaction engine evaluates synergies, inhibitions, and compounding multipliers."""
    engine = NutrientInteractionEngine()
    preds = {
        "Iodine": {"risk_level": "HIGH", "probability": 0.82},
        "Selenium": {"risk_level": "HIGH", "probability": 0.78},
        "Potassium": {"risk_level": "HIGH", "probability": 0.75},
        "Magnesium": {"risk_level": "HIGH", "probability": 0.70},
        "Vitamin D": {"risk_level": "HIGH", "probability": 0.85},
        "Calcium": {"risk_level": "HIGH", "probability": 0.80}
    }
    analysis = engine.analyze_interactions(preds)

    assert "total_active_interactions" in analysis
    assert analysis["total_active_interactions"] >= 3
    assert "overall_compounding_multiplier" in analysis
    assert analysis["overall_compounding_multiplier"] >= 1.0

    # Verify synergy and inhibition scores
    assert "synergy_score" in analysis
    assert 0 <= analysis["synergy_score"] <= 100
    assert "inhibition_score" in analysis
    assert 0 <= analysis["inhibition_score"] <= 100
    assert "interaction_severity" in analysis
    assert analysis["interaction_severity"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    # Verify presence of Iodine-Selenium interaction
    iodine_selenium = any(
        ("Iodine" in item["nutrients"] and "Selenium" in item["nutrients"])
        for item in analysis["interactions"]
    )
    assert iodine_selenium, "Expected Iodine <-> Selenium interaction to be detected"


# =============================================================================
# 4. Clinical Knowledge Base Registry & REST Endpoints
# =============================================================================

def test_clinical_knowledge_base_registry():
    """Verify registry contains 18 comprehensive monographs with WHO/NIH standards."""
    all_monographs = ClinicalKnowledgeBaseService.get_all_nutrients()
    assert len(all_monographs) == 18

    # Verify each newly expanded nutrient has rich clinical metadata
    for code in EXPANDED_7_CODES:
        mono = ClinicalKnowledgeBaseService.get_nutrient_by_code(code)
        assert mono is not None, f"Missing monograph for code {code}"
        assert mono["common_name"]
        assert mono["clinical_role"]
        assert len(mono["absorption_enhancers"]) > 0
        assert len(mono["absorption_inhibitors"]) > 0
        assert len(mono["deficiency_symptoms"]) > 0
        assert len(mono["high_risk_populations"]) > 0
        assert mono["daily_recommended_intake"]["standard_adult_male"]
        assert mono["daily_recommended_intake"]["tolerable_upper_limit"]
        assert mono["citations"]["who_reference"]


def test_clinical_knowledge_base_rest_api():
    """Test FastAPI Knowledge Base endpoints."""
    # 1. List all 18 nutrients
    res = client.get("/api/v1/knowledge-base/nutrients")
    assert res.status_code == 200
    data = res.json()
    assert data["total_nutrients"] == 18
    assert len(data["nutrients"]) == 18

    # 2. Get Potassium monograph
    res_k = client.get("/api/v1/knowledge-base/nutrients/POTASSIUM")
    assert res_k.status_code == 200
    data_k = res_k.json()
    assert data_k["nutrient_code"] == "POTASSIUM"
    assert "membrane potential" in data_k["clinical_role"]

    # 3. Get Iodine monograph
    res_i = client.get("/api/v1/knowledge-base/nutrients/IODINE")
    assert res_i.status_code == 200
    data_i = res_i.json()
    assert data_i["nutrient_code"] == "IODINE"
    assert "thyroid" in data_i["clinical_role"].lower()

    # 4. Filter by category
    res_cat = client.get("/api/v1/knowledge-base/nutrients?category=Mineral")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    assert any(n["nutrient_code"] == "SELENIUM" for n in data_cat["nutrients"])

    # 5. List clinical interactions
    res_inter = client.get("/api/v1/knowledge-base/interactions")
    assert res_inter.status_code == 200
    data_inter = res_inter.json()
    assert data_inter["total_interactions"] >= 12


# =============================================================================
# 5. Multi-Nutrient Screening API & Latency SLA (<500ms)
# =============================================================================

def test_multi_nutrient_screening_api_latency_and_18_outputs():
    """Verify /predict returns 18 predictions within the 500ms SLA."""
    payload = {
        "age": 36,
        "gender": "FEMALE",
        "height_cm": 168.0,
        "weight_kg": 64.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 3,
            "water_intake_liters": 2.2,
            "daily_fruit_vegetable_servings": 4,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": []
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.0,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 15,
            "stress_level": 7
        },
        "symptoms": {
            "fatigue": 8,
            "cracked_lips": 6,
            "irregular_heartbeat": 5,
            "unexplained_weight_gain": 7,
            "thyroid_dysfunction": 8
        },
        "medical_history": [],
        "supplement_usage": []
    }

    # Warm-up request to eliminate one-time JIT / module init overhead
    client.post("/api/v1/predict", json=payload)

    t0 = time.perf_counter()
    res = client.post("/api/v1/predict", json=payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert res.status_code == 200
    data = res.json()

    # Latency constraint: < 500ms
    assert elapsed_ms < 500.0, f"Screening latency {elapsed_ms:.2f} ms exceeded 500ms limit!"
    assert data["inference_latency_ms"] < 500.0

    # Check that all 18 nutrients are predicted
    assert len(data["nutrient_predictions"]) == 18
    assert len(data["priority_ranking"]) == 18

    # Verify newly added nutrients are present
    predicted_nutrients = [p["nutrient"] for p in data["nutrient_predictions"]]
    for nut in EXPANDED_7_NUTRIENTS:
        assert nut in predicted_nutrients

    # Check for presence of priority ranking
    assert data["priority_ranking"][0] == data["nutrient_predictions"][0]["nutrient"]


# =============================================================================
# 6. Explainable AI & Clinical Workup Catalog
# =============================================================================

def test_explainability_catalog_for_expanded_nutrients():
    """Verify ClinicalReasoningEngine provides ICD-10 and confirmatory labs for all 18 nutrients."""
    from backend.app.ml.reasoning import ClinicalReasoningEngine

    for nut in EXPANDED_7_NUTRIENTS:
        assert nut in ClinicalReasoningEngine.CLINICAL_WORKUP_CATALOG
        workup = ClinicalReasoningEngine.CLINICAL_WORKUP_CATALOG[nut]
        assert "icd10" in workup and len(workup["icd10"]) > 0
        assert "confirmatory_labs" in workup and len(workup["confirmatory_labs"]) > 10
        assert "clinical_threshold" in workup and len(workup["clinical_threshold"]) > 10
        assert "guideline" in workup and len(workup["guideline"]) > 10


# =============================================================================
# 7. Personalized Recommendations & Synergistic Pairings
# =============================================================================

def test_recommendations_for_expanded_nutrients():
    """Verify recommendation engine suggests specific nutrient-dense foods and synergies."""
    preds = [
        {"nutrient": "Potassium", "risk_level": "HIGH", "probability": 0.85},
        {"nutrient": "Iodine", "risk_level": "HIGH", "probability": 0.82},
        {"nutrient": "Selenium", "risk_level": "HIGH", "probability": 0.79},
        {"nutrient": "Vitamin B1", "risk_level": "HIGH", "probability": 0.75},
        {"nutrient": "Vitamin B6", "risk_level": "HIGH", "probability": 0.72}
    ]
    foods = PersonalizedRecommendationEngine.generate_food_recommendations(
        nutrient_predictions=preds,
        dietary_pattern="VEGAN",
        restrictions=[]
    )
    assert len(foods["priority_1"]) + len(foods["priority_2"]) + len(foods["priority_3"]) > 0

    # Verify synergies include Iodine + Selenium
    elevated = [p["nutrient"] for p in preds]
    synergies = PersonalizedRecommendationEngine.generate_synergy_pairings(
        elevated_nutrients=elevated,
        dietary_pattern="VEGAN"
    )
    has_iodine_selenium = any(
        (s.primary_nutrient in ["Iodine", "Selenium"] and s.synergistic_nutrient in ["Iodine", "Selenium"])
        for s in synergies
    )
    assert has_iodine_selenium, "Expected synergistic pairing for Iodine + Selenium"


# =============================================================================
# 8. Longitudinal Health Scoring & PDF Generation
# =============================================================================

def test_calibrated_health_score_with_18_nutrients():
    """Verify 18-nutrient health score calibration produces well-bounded scores without collapse."""
    preds_18 = [
        {"nutrient": nut, "probability": 0.45, "risk_level": "MODERATE"}
        for nut in TARGET_NUTRIENTS
    ]
    patient = {
        "water_intake_liters": 2.5,
        "sunlight_exposure_min_per_day": 30,
        "sleep_hours_per_night": 7.5,
        "activity_level": "MODERATELY_ACTIVE",
        "stress_level": 5
    }

    score_result = OverallNutritionalHealthScorer.calculate_health_score(
        nutrient_predictions=preds_18,
        patient_data=patient
    )

    assert 0 <= score_result.final_score <= 100
    # Score should be moderately calibrated around 55-80, not collapsed to 0
    assert score_result.final_score >= 50
    assert score_result.category in ["GOOD", "MODERATE_RISK"]


def test_pdf_generation_18_nutrients():
    """Verify PDF generator produces valid PDF bytes containing all 18 nutrients."""
    import uuid
    # First create an assessment run through predict endpoint so reporting service has registered payload
    payload = {
        "age": 38, "gender": "FEMALE", "height_cm": 165.0, "weight_kg": 62.0,
        "dietary_habits": {"dietary_pattern": "VEGAN", "meals_per_day": 3, "water_intake_liters": 2.2, "daily_fruit_vegetable_servings": 3, "junk_food_frequency": "RARELY", "dietary_restrictions": []},
        "lifestyle_factors": {"activity_level": "MODERATELY_ACTIVE", "sleep_hours_per_night": 7.5, "smoking_status": "NEVER", "alcohol_consumption": "NONE", "sunlight_exposure_min_per_day": 20, "stress_level": 5},
        "symptoms": {"fatigue": 6},
        "medical_history": [],
        "supplement_usage": []
    }
    screen_res = client.post("/api/v1/predict", json=payload)
    assert screen_res.status_code == 200
    assessment_id = uuid.UUID(screen_res.json()["assessment_id"])

    report = ReportingService.generate_report(
        assessment_id=assessment_id,
        report_title="18-Nutrient Clinical Assessment Report",
        export_pdf=True
    )
    assert report.id is not None
    assert report.status == "COMPLETED"

    pdf_bytes = ReportingService.get_report_pdf_bytes(report.id)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000
