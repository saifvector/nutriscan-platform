"""
Unit and Integration Tests for Phase 10B Clinical Model Training & Validation.

Tests cover:
1. Training configuration integrity and audited scale_pos_weight mapping.
2. Probability calibration (PlattCalibrator), ECE, and Brier score evaluation.
3. Dataset loading and zero target leakage into predictors.
4. Threshold optimization behavior under class imbalance.
5. Verification of Phase 10B saved model artifacts and deliverable reports.
"""

import os
import pytest
import numpy as np
import pandas as pd
import joblib

from backend.app.modules.training.config import (
    TARGETS,
    TARGET_DISPLAY_NAMES,
    AUDITED_SCALE_POS_WEIGHTS,
    CV_SPLITS,
    RANDOM_STATE,
    MODELS_DIR,
    REPORTS_DIR,
    PARQUET_DATA_PATH
)
from backend.app.modules.training.calibration import (
    PlattCalibrator,
    compute_ece,
    evaluate_calibration
)
from backend.app.modules.training.pipeline import ClinicalModelTrainingPipeline


def test_config_integrity():
    """Verify all 9 clinical targets are configured with weights and display names."""
    assert len(TARGETS) == 9
    assert len(TARGET_DISPLAY_NAMES) == 9
    assert len(AUDITED_SCALE_POS_WEIGHTS) == 9

    expected_targets = [
        'target_iron_deficiency',
        'target_iron_deficiency_anemia',
        'target_vitamin_d_deficiency',
        'target_vitamin_d_insufficiency',
        'target_folate_deficiency',
        'target_magnesium_deficiency',
        'target_selenium_deficiency',
        'target_potassium_deficiency',
        'target_calcium_deficiency'
    ]
    for target in expected_targets:
        assert target in TARGETS
        assert target in TARGET_DISPLAY_NAMES
        assert target in AUDITED_SCALE_POS_WEIGHTS
        assert AUDITED_SCALE_POS_WEIGHTS[target] > 0


def test_platt_calibrator():
    """Verify PlattCalibrator fits correctly and outputs monotonic probabilities."""
    calibrator = PlattCalibrator(random_state=42)
    np.random.seed(42)
    raw_probs = np.random.uniform(0.1, 0.9, 100)
    y_true = (raw_probs > 0.5).astype(int)

    calibrator.fit(raw_probs, y_true)
    cal_probs = calibrator.predict_proba(raw_probs)

    assert len(cal_probs) == 100
    assert np.all(cal_probs >= 0.0)
    assert np.all(cal_probs <= 1.0)

    # Monotonicity test
    test_inputs = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    test_outputs = calibrator.predict_proba(test_inputs)
    assert np.all(np.diff(test_outputs) >= 0)


def test_calibration_metrics():
    """Verify ECE and calibration evaluation metrics."""
    y_true = np.array([0, 0, 0, 1, 1, 1, 0, 1])
    raw_probs = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 0.4, 0.6])
    cal_probs = raw_probs.copy()

    ece = compute_ece(y_true, raw_probs, n_bins=5)
    assert 0.0 <= ece <= 1.0

    eval_res = evaluate_calibration(y_true, raw_probs, cal_probs, n_bins=5)
    assert 'brier_score_raw' in eval_res
    assert 'brier_score_calibrated' in eval_res
    assert 'ece_raw' in eval_res
    assert 'ece_calibrated' in eval_res
    assert eval_res['brier_score_raw'] >= 0.0


def test_dataset_loading_and_zero_leakage():
    """Verify that dataset loads 11,933 records and approved features contain zero lab target leaks."""
    pipeline = ClinicalModelTrainingPipeline(data_path=PARQUET_DATA_PATH)
    pipeline.load_data()

    assert pipeline.df is not None
    assert len(pipeline.df) == 11933
    assert len(pipeline.features) == 105

    # Target leakage verification
    lab_prefixes = ['LBX', 'LBD', 'URX', 'URD']
    for f in pipeline.features:
        assert not any(f.upper().startswith(p) for p in lab_prefixes), f"Leaked lab feature found: {f}"
        assert not f.startswith('target_'), f"Leaked target label found: {f}"
        assert f not in TARGETS, f"Direct target found in feature list: {f}"


def test_threshold_optimization():
    """Verify threshold optimization returns an actionable cutoff between 0.10 and 0.90."""
    pipeline = ClinicalModelTrainingPipeline(data_path=PARQUET_DATA_PATH)
    y_val = np.array([0, 0, 0, 0, 0, 1, 1, 0, 1, 0])
    probs = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.65, 0.7, 0.3, 0.85, 0.12])

    thresh = pipeline.optimize_threshold(y_val, probs)
    assert 0.10 <= thresh <= 0.90


def test_phase10b_deliverables_existence():
    """Verify all 5 required Phase 10B deliverable reports exist and contain required sections."""
    deliverables = [
        "phase10b_training_report.md",
        "phase10b_model_comparison.csv",
        "phase10b_feature_importance.csv",
        "phase10b_calibration_report.md",
        "phase10b_model_cards.md"
    ]

    for fname in deliverables:
        # Check both reports/ directory and root
        rep_path = os.path.join(REPORTS_DIR, fname)
        root_path = fname
        assert os.path.exists(rep_path) or os.path.exists(root_path), f"Missing deliverable: {fname}"

    # Verify comparison CSV contents
    comp_path = os.path.join(REPORTS_DIR, "phase10b_model_comparison.csv")
    if os.path.exists(comp_path):
        df_comp = pd.read_csv(comp_path)
        assert len(df_comp) == 36  # 9 targets x 4 algorithms
        assert 'test_roc_auc' in df_comp.columns
        assert 'test_pr_auc' in df_comp.columns
        assert 'test_f1' in df_comp.columns

    # Verify feature importance CSV contents
    feat_path = os.path.join(REPORTS_DIR, "phase10b_feature_importance.csv")
    if os.path.exists(feat_path):
        df_feat = pd.read_csv(feat_path)
        assert len(df_feat) > 0
        assert 'mean_abs_shap' in df_feat.columns

    # Verify best model files exist in models/
    for target in TARGETS:
        best_path = os.path.join(MODELS_DIR, f"best_{target}.joblib")
        assert os.path.exists(best_path), f"Missing champion model: {best_path}"
        saved_obj = joblib.load(best_path)
        assert 'model' in saved_obj
        assert 'calibrator' in saved_obj
        assert 'optimal_threshold' in saved_obj
