"""
Unit Tests for Phase 2 Machine Learning Foundation
"""

import pytest
import numpy as np
import pandas as pd

from backend.app.ml.constants import (
    TARGET_NUTRIENTS,
    RiskCategory,
    OverallSeverity
)
from backend.app.ml.dataset_generator import NutritionalDatasetGenerator
from backend.app.ml.feature_engineering import ClinicalFeaturePipeline
from backend.app.ml.models import (
    LogisticRegressionNutrientModel,
    RandomForestNutrientModel
)
from backend.app.ml.nutrient_interactions import NutrientInteractionEngine
from backend.app.ml.risk_scorer import NutritionalRiskScorer
from backend.app.ml.explainability import ClinicalExplainabilityEngine
from backend.app.ml.inference_engine import NutritionalInferenceEngine


@pytest.fixture
def sample_dataset():
    generator = NutritionalDatasetGenerator(seed=123)
    return generator.generate_dataframe(n_samples=250)


def test_dataset_generator(sample_dataset):
    assert len(sample_dataset) == 250
    # Check all target columns present
    for nut in TARGET_NUTRIENTS:
        assert f"target_{nut}" in sample_dataset.columns
        assert f"prob_{nut}" in sample_dataset.columns
        # Check targets are 0, 1, or 2
        unique_targets = sample_dataset[f"target_{nut}"].unique()
        assert set(unique_targets).issubset({0, 1, 2})


def test_feature_pipeline_fit_transform(sample_dataset):
    target_cols = [f"target_{nut}" for nut in TARGET_NUTRIENTS]
    feature_cols = [c for c in sample_dataset.columns if not c.startswith("target_") and not c.startswith("prob_")]
    
    X_raw = sample_dataset[feature_cols]
    
    pipeline = ClinicalFeaturePipeline(scaler_type="robust")
    pipeline.fit(X_raw)
    assert pipeline.is_fitted
    assert len(pipeline.feature_names_) > 25

    X_transformed = pipeline.transform(X_raw)
    assert X_transformed.shape[0] == 250
    assert X_transformed.shape[1] == len(pipeline.feature_names_)
    # Check no NaN values after transformation
    assert not X_transformed.isna().any().any()


def test_bmi_calculation():
    pipeline = ClinicalFeaturePipeline()
    test_df = pd.DataFrame([{
        "age": 30, "gender": "MALE", "height_cm": 180.0, "weight_kg": 81.0,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 3, "water_intake_liters": 2.0,
        "daily_fruit_vegetable_servings": 3, "activity_level": "SEDENTARY",
        "sleep_hours_per_night": 7.0, "sunlight_exposure_min_per_day": 20,
        "stress_level": 5, "smoking_status": "NEVER", "alcohol_consumption": "NONE"
    }])
    pipeline.fit(test_df)
    transformed = pipeline.transform(test_df)
    assert "bmi" in transformed.columns
    # 81 / (1.8^2) = 25.0
    assert abs(pipeline.medians_.get("weight_kg", 81.0) / ((pipeline.medians_.get("height_cm", 180.0)/100)**2) - 25.0) < 0.1


def test_nutrient_interactions():
    engine = NutrientInteractionEngine()
    
    # Co-deficiency in Vitamin D and Calcium
    mock_risks = {
        "Vitamin D": {"risk_level": "High Risk", "probability": 0.85},
        "Calcium": {"risk_level": "High Risk", "probability": 0.80},
        "Iron": {"risk_level": "Low Risk", "probability": 0.15}
    }
    
    analysis = engine.analyze_interactions(mock_risks)
    assert analysis["total_active_interactions"] >= 1
    assert analysis["overall_compounding_multiplier"] > 1.0
    
    active_pair = analysis["interactions"][0]["nutrients"]
    assert "Vitamin D" in active_pair and "Calcium" in active_pair


def test_risk_scorer():
    scorer = NutritionalRiskScorer()
    
    # Probability distribution [p_low, p_mod, p_high]
    probs = np.array([0.1, 0.3, 0.6])
    score = scorer.calculate_individual_score(probs, predicted_class=2)
    # (0.3 * 50) + (0.6 * 100) = 15 + 60 = 75.0
    assert score == 75.0

    # Overall risk aggregation
    sample_evals = [
        {"nutrient": "Vitamin B12", "score": 85.0, "risk_level": "High Risk"},
        {"nutrient": "Iron", "score": 80.0, "risk_level": "High Risk"},
        {"nutrient": "Vitamin C", "score": 20.0, "risk_level": "Low Risk"}
    ]
    
    overall = scorer.calculate_overall_risk(sample_evals, interaction_multiplier=1.2)
    assert overall["overall_risk_score"] > 50.0
    assert overall["overall_severity"] in [OverallSeverity.HIGH.value, OverallSeverity.CRITICAL.value]
    assert len(overall["priority_ranking"]) == 3
    assert overall["priority_ranking"][0]["priority_rank"] == 1


def test_end_to_end_inference(sample_dataset):
    target_cols = [f"target_{nut}" for nut in TARGET_NUTRIENTS]
    feature_cols = [c for c in sample_dataset.columns if not c.startswith("target_") and not c.startswith("prob_")]

    pipeline = ClinicalFeaturePipeline()
    pipeline.fit(sample_dataset[feature_cols])

    X_train = pipeline.transform(sample_dataset[feature_cols])
    y_train = sample_dataset[target_cols]

    # Train baseline Logistic Regression
    model = LogisticRegressionNutrientModel(max_iter=200)
    model.fit(X_train, y_train)

    inference_engine = NutritionalInferenceEngine(model=model, pipeline=pipeline)
    
    sample_patient = {
        "age": 28, "gender": "FEMALE", "height_cm": 162.0, "weight_kg": 52.0,
        "dietary_pattern": "VEGAN", "meals_per_day": 3, "water_intake_liters": 2.2,
        "daily_fruit_vegetable_servings": 4, "food_restrictions": ["meat_free"],
        "activity_level": "MODERATELY_ACTIVE", "sleep_hours_per_night": 7.0,
        "sunlight_exposure_min_per_day": 10, "stress_level": 6,
        "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "has_digestive_disorder": False, "has_chronic_disease": False,
        "has_prior_deficiency": False, "takes_multivitamin": False,
        "takes_vitamin_d": False, "takes_iron": False, "takes_b12": False,
        "takes_calcium": False, "takes_magnesium": False, "takes_zinc": False,
        "supplement_duration_months": 0,
        "symptoms": {"fatigue": 7, "pale_skin": 6, "hair_loss": 5}
    }

    result = inference_engine.screen_patient(sample_patient, compute_explainability=True)
    assert "overall_summary" in result
    assert "nutrient_evaluations" in result
    assert len(result["nutrient_evaluations"]) == 18
    assert "overall_risk_score" in result["overall_summary"]
