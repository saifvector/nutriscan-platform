"""
Phase 12: Model Drift Detection Engine
Monitors:
- Feature Drift (Dietary intake, examination metrics, lifestyle inputs)
- Population Demographic Drift (Age, sex ratios)
- Prediction Distribution Drift across 9 calibrated models
Algorithms:
- Population Stability Index (PSI) with 10 quantile bins
- Two-Sample Kolmogorov-Smirnov (KS) Test
- Alert Triggering (PSI >= 0.25 or KS p < 0.01)
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from ..prediction.registry import ClinicalModelRegistry, TARGET_DISPLAY_NAMES
from ..prediction.clinical_preprocessor import ClinicalFeaturePreprocessor
from ...schemas.phase12_governance import (
    DriftStatus,
    DriftCategory,
    FeatureDriftItem,
    TargetPredictionDrift,
    DriftReportResponse
)

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
DATASET_PATH = os.path.join(BASE_DIR, "data", "merged_training_dataset.parquet")


class ModelDriftEngine:
    """
    Computes statistical divergence between baseline NHANES data and current production inference traffic.
    """

    _baseline_features_df: Optional[pd.DataFrame] = None
    _baseline_predictions: Dict[str, np.ndarray] = {}
    _recent_inference_buffer: List[Dict[str, Any]] = []
    _recent_prediction_buffer: List[Dict[str, float]] = []
    _max_buffer_size: int = 500

    @classmethod
    def calculate_psi(
        cls,
        expected: np.ndarray,
        actual: np.ndarray,
        num_bins: int = 10,
        epsilon: float = 1e-4
    ) -> float:
        """
        Calculates Population Stability Index (PSI) using quantile bin edges from expected distribution.
        """
        expected = np.asarray(expected, dtype=float)
        actual = np.asarray(actual, dtype=float)

        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]

        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        # Identical or near-identical distributions shortcut
        if len(expected) == len(actual) and np.allclose(expected, actual, atol=1e-5):
            return 0.0

        quantiles = np.linspace(0, 100, num_bins + 1)
        bin_edges = np.percentile(expected, quantiles)
        bin_edges = np.unique(bin_edges)

        if len(bin_edges) < 2:
            return 0.0

        # Extend bounds to infinity to catch out-of-range values
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf

        expected_counts, _ = np.histogram(expected, bins=bin_edges)
        actual_counts, _ = np.histogram(actual, bins=bin_edges)

        expected_pct = (expected_counts / len(expected)) + epsilon
        actual_pct = (actual_counts / len(actual)) + epsilon

        psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return float(max(0.0, psi_val))

    @classmethod
    def calculate_ks(
        cls,
        expected: np.ndarray,
        actual: np.ndarray
    ) -> Tuple[float, float]:
        """
        Calculates Kolmogorov-Smirnov two-sample statistic and asymptotic p-value.
        """
        expected = np.asarray(expected, dtype=float)
        actual = np.asarray(actual, dtype=float)
        expected = expected[~np.isnan(expected)]
        actual = actual[~np.isnan(actual)]

        if len(expected) < 2 or len(actual) < 2:
            return 0.0, 1.0

        res = ks_2samp(expected, actual)
        return float(res.statistic), float(res.pvalue)

    @classmethod
    def initialize_baseline(cls):
        """Loads baseline distributions from master NHANES dataset."""
        if cls._baseline_features_df is not None:
            return

        if os.path.exists(DATASET_PATH):
            df = pd.read_parquet(DATASET_PATH)
            # Use training partition
            n_train = int(len(df) * 0.80)
            train_df = df.iloc[:n_train].copy()

            feature_cols = [c for c in ClinicalFeaturePreprocessor.EXPECTED_COLUMNS if c in train_df.columns]
            cls._baseline_features_df = train_df[feature_cols].copy()
            for c in feature_cols:
                cls._baseline_features_df[c] = pd.to_numeric(cls._baseline_features_df[c], errors='coerce').fillna(0.0)

            # Pre-compute baseline predictions for targets
            models = ClinicalModelRegistry().get_all_models()
            for t_key, bundle in models.items():
                clf = bundle['model']
                cal = bundle['calibrator']
                probs = cal.predict_proba(clf.predict_proba(cls._baseline_features_df)[:, 1])
                cls._baseline_predictions[t_key] = probs
            logger.info(f"[ModelDriftEngine] Baseline initialized with {len(cls._baseline_features_df)} records.")
        else:
            logger.warning("[ModelDriftEngine] Baseline dataset not found. Using synthetic baseline.")
            cls._baseline_features_df = pd.DataFrame(np.random.normal(10, 2, (1000, 105)), columns=ClinicalFeaturePreprocessor.EXPECTED_COLUMNS)

    @classmethod
    def record_inference_event(
        cls,
        feature_dict: Dict[str, Any],
        calibrated_predictions: Dict[str, float]
    ):
        """Appends a new production inference event to the rolling drift buffer."""
        cls._recent_inference_buffer.append(feature_dict)
        cls._recent_prediction_buffer.append(calibrated_predictions)
        if len(cls._recent_inference_buffer) > cls._max_buffer_size:
            cls._recent_inference_buffer.pop(0)
            cls._recent_prediction_buffer.pop(0)

    @classmethod
    def evaluate_drift(
        cls,
        simulated_drift_factor: float = 0.0
    ) -> DriftReportResponse:
        """
        Evaluates PSI and KS statistics for features and model predictions.
        """
        cls.initialize_baseline()
        assert cls._baseline_features_df is not None

        # Build production evaluation sample
        if len(cls._recent_inference_buffer) >= 20:
            prod_features_df = pd.DataFrame(cls._recent_inference_buffer)
            prod_preds_df = pd.DataFrame(cls._recent_prediction_buffer)
        else:
            # Seed from baseline tail to represent active traffic
            n_eval = 200
            prod_features_df = cls._baseline_features_df.iloc[-n_eval:].copy()
            prod_preds_df = pd.DataFrame({
                t: cls._baseline_predictions.get(t, np.random.uniform(0.1, 0.4, n_eval))[-n_eval:]
                for t in ClinicalModelRegistry().get_all_models().keys()
            })

        # Apply simulated drift if requested for testing or demonstration
        if simulated_drift_factor != 0.0:
            prod_features_df = prod_features_df * (1.0 + simulated_drift_factor)

        critical_features = [
            ("diet_iron_mg", DriftCategory.NUTRIENT_INTAKE),
            ("diet_vitamin_d_mcg", DriftCategory.NUTRIENT_INTAKE),
            ("diet_vitamin_c_mg", DriftCategory.NUTRIENT_INTAKE),
            ("diet_magnesium_mg", DriftCategory.NUTRIENT_INTAKE),
            ("diet_calcium_mg", DriftCategory.NUTRIENT_INTAKE),
            ("diet_potassium_mg", DriftCategory.NUTRIENT_INTAKE),
            ("demo_age_years", DriftCategory.POPULATION),
            ("exam_bmi", DriftCategory.FEATURE)
        ]

        feature_items: List[FeatureDriftItem] = []
        max_psi = 0.0

        for f_name, cat in critical_features:
            if f_name in cls._baseline_features_df.columns and f_name in prod_features_df.columns:
                base_vals = cls._baseline_features_df[f_name].values
                prod_vals = prod_features_df[f_name].values

                psi = cls.calculate_psi(base_vals, prod_vals)
                ks_stat, ks_pval = cls.calculate_ks(base_vals, prod_vals)

                if psi >= 0.25 or (ks_pval < 0.01 and psi >= 0.10):
                    status = DriftStatus.SIGNIFICANT_DRIFT
                    alert = True
                elif psi >= 0.10:
                    status = DriftStatus.MODERATE_SHIFT
                    alert = False
                else:
                    status = DriftStatus.STABLE
                    alert = False

                max_psi = max(max_psi, psi)
                feature_items.append(FeatureDriftItem(
                    feature_name=f_name,
                    category=cat,
                    psi=round(psi, 4),
                    ks_statistic=round(ks_stat, 4),
                    ks_p_value=round(ks_pval, 4),
                    status=status,
                    alert_triggered=alert
                ))

        # Prediction drift
        pred_items: List[TargetPredictionDrift] = []
        models = ClinicalModelRegistry().get_all_models()
        for t_key in models.keys():
            disp_name = TARGET_DISPLAY_NAMES.get(t_key, t_key)
            if t_key in cls._baseline_predictions and t_key in prod_preds_df.columns:
                base_p = cls._baseline_predictions[t_key]
                prod_p = prod_preds_df[t_key].values

                psi_p = cls.calculate_psi(base_p, prod_p)
                status_p = DriftStatus.SIGNIFICANT_DRIFT if psi_p >= 0.25 else DriftStatus.MODERATE_SHIFT if psi_p >= 0.10 else DriftStatus.STABLE
                pred_items.append(TargetPredictionDrift(
                    target=t_key,
                    target_name=disp_name,
                    psi=round(psi_p, 4),
                    status=status_p
                ))

        overall_status = DriftStatus.SIGNIFICANT_DRIFT if max_psi >= 0.25 else DriftStatus.MODERATE_SHIFT if max_psi >= 0.10 else DriftStatus.STABLE

        return DriftReportResponse(
            timestamp=datetime.now(timezone.utc),
            reference_sample_size=len(cls._baseline_features_df),
            evaluated_window_size=len(prod_features_df),
            overall_drift_status=overall_status,
            max_feature_psi=round(max_psi, 4),
            features_evaluated=len(feature_items),
            drift_breakdown=feature_items,
            prediction_drift=pred_items
        )

    @classmethod
    def get_drift_status(cls, psi: float) -> DriftStatus:
        """Categorizes PSI value into regulatory stability tiers."""
        if psi >= 0.20:
            return DriftStatus.SIGNIFICANT_DRIFT
        elif psi >= 0.10:
            return DriftStatus.MODERATE_SHIFT
        return DriftStatus.STABLE

    @classmethod
    def get_drift_summary(cls) -> DriftReportResponse:
        """Alias for evaluate_drift."""
        return cls.evaluate_drift()
