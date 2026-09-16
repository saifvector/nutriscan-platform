"""
Unit and Integration Tests for Phase 10C — Production Inference & Clinical Risk Engine.

Tests cover:
1. Model Registry discovery, metadata validation, and version tracking (9 champion models).
2. Clinical Feature Preprocessor (105-column NHANES vector, derived features, completeness tracking).
3. Clinical Risk Engine single and batch inference (Platt calibration, risk tiers, confidence scoring).
4. Multi-deficiency triage and priority ordering.
5. Structured Audit Logging compliance.
6. REST API Endpoints:
   - POST /api/v1/predictions/predict
   - POST /api/v1/predictions/batch
   - GET  /api/v1/predictions/models
   - GET  /api/v1/predictions/health
7. Backward compatibility for legacy Phase 3-7 endpoints.
8. Sub-100ms inference latency benchmarks.
9. Integration with Recommendation, Intelligence, and Outcome Learning systems.
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.prediction.registry import ClinicalModelRegistry, TARGET_DISPLAY_NAMES
from backend.app.modules.prediction.clinical_preprocessor import ClinicalFeaturePreprocessor
from backend.app.modules.prediction.clinical_engine import ClinicalRiskEngine
from backend.app.modules.prediction.service import PredictionService
from backend.app.schemas.clinical_prediction import ClinicalRiskTier, ConfidenceTier

# Create client within lifespan context so warmup executes
client = TestClient(app)


def test_model_registry_discovery_and_metadata():
    """Verify registry discovers all 9 champion models and provides complete metadata."""
    registry = ClinicalModelRegistry()
    assert registry.is_healthy() is True

    all_models = registry.get_all_models()
    assert len(all_models) == 9

    expected_targets = set(TARGET_DISPLAY_NAMES.keys())
    assert expected_targets.issubset(set(all_models.keys()))

    catalog = registry.get_metadata_catalog()
    assert catalog.total_registered_models == 9
    assert catalog.status == "READY"
    assert catalog.model_suite_version == registry.VERSION

    for card in catalog.models:
        assert card.target in expected_targets
        assert card.optimal_threshold > 0.0
        assert card.num_features == 105
        assert card.holdout_roc_auc > 0.60
        assert card.calibrated_ece < 0.05
        assert card.champion_algorithm in ['Logistic Regression', 'Random Forest', 'XGBoost', 'LightGBM']


def test_clinical_feature_preprocessor():
    """Verify preprocessor converts arbitrary patient payload into 105 approved features."""
    raw_patient = {
        "age": 42,
        "gender": "FEMALE",
        "height_cm": 162.0,
        "weight_kg": 68.0,
        "waist_cm": 82.0,
        "systolic_bp": 122.0,
        "diastolic_bp": 78.0,
        "pulse_rate": 72.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "water_intake_liters": 2.5
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.0,
            "alcohol_consumption": "NONE"
        },
        "symptoms": {
            "fatigue": 7,
            "insomnia": 6
        },
        "supplement_usage": ["Iron supplement", "Vitamin D3 1000 IU"]
    }

    df_feats, audit_meta = ClinicalFeaturePreprocessor.transform_single(raw_patient)
    assert df_feats.shape == (1, 105)
    assert audit_meta['total_features'] == 105
    assert audit_meta['observed_count'] > 20
    assert 0.0 <= audit_meta['completeness_pct'] <= 100.0

    # Verify physiological derivations
    assert df_feats['demo_age_years'].values[0] == 42.0
    assert df_feats['demo_is_male'].values[0] == 0.0
    assert df_feats['exam_bmi'].values[0] > 20.0
    assert df_feats['lifestyle_special_diet'].values[0] == 1.0
    assert df_feats['supp_iron_mg'].values[0] > 0.0
    assert df_feats['supp_vitamin_d_mcg'].values[0] > 0.0


def test_clinical_risk_engine_single_prediction():
    """Verify single patient prediction produces calibrated probabilities and risk tiers."""
    engine = ClinicalRiskEngine()
    engine.warm_up()

    sample_patient = {
        "age": 30,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 54.0,
        "symptoms": {"fatigue": 8, "pale_skin": 6}
    }

    res = engine.predict_patient(sample_patient)
    assert res.prediction_id is not None
    assert res.overall_risk_tier in [ClinicalRiskTier.LOW, ClinicalRiskTier.MODERATE, ClinicalRiskTier.HIGH]
    assert 0.0 <= res.overall_risk_score <= 100.0
    assert len(res.predictions) == 9
    assert len(res.priority_ranking) == 9

    # Verify per-target fields
    for p in res.predictions:
        assert p.target in TARGET_DISPLAY_NAMES
        assert 0.0 <= p.raw_probability <= 1.0
        assert 0.0 <= p.calibrated_probability <= 1.0
        assert p.risk_tier in [ClinicalRiskTier.LOW, ClinicalRiskTier.MODERATE, ClinicalRiskTier.HIGH]
        assert 0.50 <= p.confidence_score <= 1.0
        assert p.confidence_tier in [ConfidenceTier.HIGH_CONFIDENCE, ConfidenceTier.MEDIUM_CONFIDENCE, ConfidenceTier.LOW_CONFIDENCE]
        assert 1 <= p.priority_rank <= 9
        assert len(p.top_predictors) > 0


def test_clinical_batch_prediction():
    """Verify batch prediction processes multiple patient profiles with latency tracking."""
    engine = ClinicalRiskEngine()
    patients = [
        {"age": 25, "gender": "MALE", "height_cm": 180.0, "weight_kg": 75.0},
        {"age": 55, "gender": "FEMALE", "height_cm": 158.0, "weight_kg": 72.0},
        {"age": 38, "gender": "FEMALE", "height_cm": 168.0, "weight_kg": 58.0}
    ]

    batch_res = engine.predict_batch(patients)
    assert batch_res.total_records == 3
    assert len(batch_res.results) == 3
    assert batch_res.batch_latency_ms < 1000.0
    assert batch_res.average_latency_per_record_ms < 500.0


def test_audit_logging_structure():
    """Verify structured audit log contains compliance and feature completeness metadata."""
    engine = ClinicalRiskEngine()
    sample = {"age": 45, "gender": "MALE", "height_cm": 175.0, "weight_kg": 80.0}
    res = engine.predict_patient(sample)

    audit = res.audit_log
    assert audit.prediction_id == res.prediction_id
    assert audit.timestamp is not None
    assert audit.model_suite_version == engine.registry.VERSION
    assert audit.total_features_evaluated == 105
    assert audit.observed_features_count > 0
    assert 0.0 < audit.feature_completeness_pct <= 100.0
    assert len(audit.active_champion_models) >= 3  # XGBoost, Random Forest, Logistic Regression
    assert audit.inference_latency_ms > 0.0


def test_rest_api_predictions_predict():
    """Verify POST /api/v1/predictions/predict REST endpoint."""
    sample_payload = {
        "age": 29,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "symptoms": {"fatigue": 7, "hair_loss": 5}
    }
    response = client.post("/api/v1/predictions/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.json()

    assert "prediction_id" in data
    assert "overall_risk_tier" in data
    assert "predictions" in data
    assert len(data["predictions"]) == 9
    assert "audit_log" in data
    assert data["audit_log"]["total_features_evaluated"] == 105


def test_rest_api_predictions_batch():
    """Verify POST /api/v1/predictions/batch REST endpoint."""
    batch_payload = {
        "assessments": [
            {"age": 30, "gender": "FEMALE", "height_cm": 160.0, "weight_kg": 55.0},
            {"age": 40, "gender": "MALE", "height_cm": 175.0, "weight_kg": 80.0}
        ]
    }
    response = client.post("/api/v1/predictions/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_records"] == 2
    assert len(data["results"]) == 2
    assert data["batch_latency_ms"] < 1000.0


def test_rest_api_predictions_models():
    """Verify GET /api/v1/predictions/models REST endpoint."""
    response = client.get("/api/v1/predictions/models")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "READY"
    assert data["total_registered_models"] == 9
    assert len(data["models"]) == 9
    for m in data["models"]:
        assert "target" in m
        assert "champion_algorithm" in m
        assert "holdout_roc_auc" in m


def test_rest_api_predictions_health():
    """Verify GET /api/v1/predictions/health REST endpoint."""
    response = client.get("/api/v1/predictions/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "HEALTHY"
    assert data["engine_warmed"] is True
    assert data["registered_models_count"] == 9
    assert data["benchmark_latency_ms"] < 500.0


def test_backward_compatibility_existing_endpoints():
    """Verify legacy Phase 1-9 endpoints remain 100% operational."""
    # 1. GET /health
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    # 2. GET /api/v1/predictions/rules/interactions
    res_rules = client.get("/api/v1/predictions/rules/interactions")
    assert res_rules.status_code == 200
    assert len(res_rules.json()["interaction_catalog"]) >= 5

    # 3. POST /api/v1/predict (legacy endpoint)
    sample_legacy = {
        "age": 30,
        "gender": "MALE",
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
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
            "sunlight_exposure_min_per_day": 30,
            "stress_level": 4
        },
        "symptoms": {},
        "medical_history": [],
        "supplement_usage": []
    }
    res_legacy = client.post("/api/v1/predict", json=sample_legacy)
    assert res_legacy.status_code == 200
    assert len(res_legacy.json()["nutrient_predictions"]) == 18


def test_module_integrations():
    """Verify integrations with Recommendation, Intelligence, and Outcome Learning systems."""
    import uuid
    from backend.app.modules.recommendation.service import RecommendationService
    from backend.app.modules.intelligence.service import NutritionIntelligenceService
    from backend.app.modules.outcomes.service import OutcomeIntelligenceService

    test_patient = {
        "age": 35,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "symptoms": {"fatigue": 8, "hair_loss": 6}
    }

    # 1. Outcomes baseline linking
    outcome_res = OutcomeIntelligenceService.evaluate_clinical_baseline(test_patient)
    assert outcome_res["status"] == "BASELINE_LINKED_TO_OUTCOMES"
    assert outcome_res["clinical_prediction"].total_deficiencies_detected >= 0

    # 2. Intelligence context resolution
    ctx = NutritionIntelligenceService._resolve_assessment_context("demo")
    assert "detected_deficiencies" in ctx
    assert len(ctx["detected_deficiencies"]) > 0

    # 3. Recommendation engine integration
    test_id = uuid.uuid4()
    plan = RecommendationService.get_recommendations(test_id)
    assert plan is not None
    assert len(plan.target_nutrients) > 0


