"""
Phase 12: Model Drift Detection Engine Tests.
Verifies Population Stability Index (PSI), Kolmogorov-Smirnov (KS-test), and production drift endpoints.
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.governance.drift_engine import ModelDriftEngine
from backend.app.schemas.phase12_governance import DriftStatus

client = TestClient(app)


def test_drift_engine_psi_computation():
    """Verify PSI calculation logic between identical vs drifted distributions."""
    np.random.seed(42)
    baseline = np.random.normal(50, 10, 1000)
    current_identical = np.random.normal(50, 10, 1000)
    current_drifted = np.random.normal(85, 10, 1000)

    # Identical should have very low PSI (< 0.10)
    psi_stable = ModelDriftEngine.calculate_psi(baseline, current_identical, num_bins=10)
    assert psi_stable < 0.10

    # Significantly drifted should have high PSI (> 0.20)
    psi_drifted = ModelDriftEngine.calculate_psi(baseline, current_drifted, num_bins=10)
    assert psi_drifted > 0.25


def test_drift_engine_ks_test():
    """Verify two-sample Kolmogorov-Smirnov test."""
    np.random.seed(42)
    s1 = np.random.normal(0, 1, 500)
    s2 = np.random.normal(0, 1, 500)
    s3 = np.random.normal(3, 1, 500)

    ks_stat_null, p_val_null = ModelDriftEngine.calculate_ks(s1, s2)
    assert p_val_null > 0.05  # Fail to reject null hypothesis (same distribution)

    ks_stat_alt, p_val_alt = ModelDriftEngine.calculate_ks(s1, s3)
    assert p_val_alt < 0.01  # Reject null hypothesis (distinct distributions)


def test_drift_engine_status_classification():
    """Verify DriftStatus enum mapping according to regulatory thresholds."""
    assert ModelDriftEngine.get_drift_status(0.04) == DriftStatus.STABLE
    assert ModelDriftEngine.get_drift_status(0.099) == DriftStatus.STABLE
    assert ModelDriftEngine.get_drift_status(0.15) == DriftStatus.MODERATE_SHIFT
    assert ModelDriftEngine.get_drift_status(0.25) == DriftStatus.SIGNIFICANT_DRIFT


def test_drift_engine_summary_report():
    """Verify drift summary generation across features and targets."""
    summary = ModelDriftEngine.get_drift_summary()
    assert summary.features_evaluated > 0
    assert summary.max_feature_psi >= 0.0
    assert summary.overall_drift_status in [DriftStatus.STABLE, DriftStatus.MODERATE_SHIFT, DriftStatus.SIGNIFICANT_DRIFT]
    assert len(summary.drift_breakdown) > 0


def test_api_drift_endpoint():
    """GET /api/v1/monitoring/drift returns production drift metrics."""
    resp = client.get("/api/v1/monitoring/drift")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_drift_status" in data
    assert "drift_breakdown" in data
    assert "prediction_drift" in data
    assert data["features_evaluated"] > 0
