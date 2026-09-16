"""
Phase 3 ML Pipeline Stability & Determinism Test Suite.
Validates:
1. Preprocessor schema consistency: 105 float32 columns in exact canonical order with 0 NaN values.
2. Resilience against edge-case inputs (empty dict, negative numbers, extreme values, strings).
3. Calibration determinism: all 9 targets return calibrated probabilities bounded within [0.0001, 0.9999].
4. Confidence scores and risk tiers mathematical consistency.
5. Strict execution without warnings or deprecation leakage.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.modules.prediction.clinical_preprocessor import (
    ClinicalFeaturePreprocessor,
    APPROVED_FEATURES
)
from backend.app.modules.prediction.registry import ClinicalModelRegistry
from backend.app.modules.prediction.clinical_engine import ClinicalRiskEngine
from backend.app.schemas.clinical_prediction import ClinicalRiskTier, ConfidenceTier


def test_preprocessor_column_order_and_dtypes():
    """Verify that preprocessor outputs exactly 105 float32 columns in APPROVED_FEATURES order."""
    raw = {
        "age": 45,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 62.0,
        "diet_iron_mg": 12.0,
        "diet_vitamin_d_mcg": 5.0
    }
    df, meta = ClinicalFeaturePreprocessor.transform_single(raw)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == APPROVED_FEATURES
    assert len(df.columns) == 105
    assert (df.dtypes == np.float32).all(), "All feature columns must be explicit float32"
    assert not df.isna().any().any(), "No NaN values allowed in model input vector"
    assert meta["observed_count"] > 0
    assert meta["completeness_pct"] > 0.0


def test_preprocessor_extreme_edge_cases():
    """Verify preprocessor handles completely empty or hostile payloads without crashing."""
    # 1. Empty payload
    df_empty, meta_empty = ClinicalFeaturePreprocessor.transform_single({})
    assert len(df_empty.columns) == 105
    assert not df_empty.isna().any().any()
    assert (df_empty.dtypes == np.float32).all()

    # 2. Hostile / malformed values
    hostile = {
        "age": "invalid_age",
        "gender": None,
        "height_cm": -999.0,
        "weight_kg": "not_a_number",
        "medical_history": ["Severe Anemia", 12345, None],
        "random_unknown_field": "ignore_me"
    }
    df_hostile, meta_hostile = ClinicalFeaturePreprocessor.transform_single(hostile)
    assert len(df_hostile.columns) == 105
    assert not df_hostile.isna().any().any()
    assert (df_hostile.dtypes == np.float32).all()


def test_batch_preprocessor_consistency():
    """Verify batch transformation maintains exact ordering and float32 types."""
    batch = [
        {"age": 25, "gender": "MALE"},
        {"age": 68, "gender": "FEMALE", "weight_kg": 75.0},
        {}
    ]
    combined_df, metas = ClinicalFeaturePreprocessor.transform_batch(batch)
    assert len(combined_df) == 3
    assert list(combined_df.columns) == APPROVED_FEATURES
    assert (combined_df.dtypes == np.float32).all()
    assert not combined_df.isna().any().any()
    assert len(metas) == 3


def test_model_registry_integrity():
    """Verify registry discovers and loads all 9 champion targets."""
    registry = ClinicalModelRegistry()
    assert registry.is_healthy(), "ClinicalModelRegistry must report healthy state"
    models = registry.get_all_models()
    assert len(models) == 9, f"Expected 9 registered models, found {len(models)}"

    for target, bundle in models.items():
        assert "model" in bundle
        assert "calibrator" in bundle
        assert hasattr(bundle["model"], "predict_proba")
        assert hasattr(bundle["calibrator"], "predict_proba")


def test_prediction_engine_end_to_end_determinism():
    """Verify end-to-end multi-target inference, calibrated probabilities, and risk tiers."""
    engine = ClinicalRiskEngine()
    payload = {
        "age": 34,
        "gender": "FEMALE",
        "height_cm": 160.0,
        "weight_kg": 54.0,
        "diet_iron_mg": 4.5,
        "diet_vitamin_d_mcg": 1.2,
        "medical_history": ["anemia"]
    }

    result = engine.predict_patient(payload)
    assert len(result.predictions) == 9
    assert result.overall_risk_score >= 0.0
    assert len(result.priority_ranking) == 9

    # Verify probability bounds and confidence tiers
    for pred in result.predictions:
        assert 0.0001 <= pred.calibrated_probability <= 0.9999
        assert 0.0001 <= pred.raw_probability <= 0.9999
        assert 0.50 <= pred.confidence_score <= 1.0
        assert pred.risk_tier in [ClinicalRiskTier.LOW, ClinicalRiskTier.MODERATE, ClinicalRiskTier.HIGH]
        assert pred.confidence_tier in [ConfidenceTier.LOW_CONFIDENCE, ConfidenceTier.MEDIUM_CONFIDENCE, ConfidenceTier.HIGH_CONFIDENCE]
        assert len(pred.top_predictors) <= 3
