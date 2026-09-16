"""
Phase 12: Clinical Validation Framework Tests.
Verifies holdout cohort performance and cross-demographic subgroup validity across 9 champion models.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.governance.validation_engine import ClinicalValidationEngine
from backend.app.schemas.phase12_governance import SubgroupCategory

client = TestClient(app)


def test_validation_engine_cohort_summary():
    """Verify holdout cohort performance metrics across all 9 champion models."""
    summary = ClinicalValidationEngine.get_cohort_summary(force_recompute=False)
    assert summary.total_holdout_samples > 0
    assert summary.evaluated_targets_count >= 8
    assert summary.overall_macro_auroc > 0.60
    assert summary.overall_macro_ece < 0.25

    for target in summary.targets:
        assert target.sample_size > 0
        assert target.prevalence_pct >= 0.0
        assert target.auroc >= 0.50
        assert target.auprc >= 0.0
        assert 0.0 <= target.sensitivity <= 1.0
        assert 0.0 <= target.specificity <= 1.0
        assert target.ece < 0.50
        assert target.brier_score < 0.30


def test_validation_demographic_breakdown_sex():
    """Verify stratified performance for Male vs Female subgroups."""
    breakdown = ClinicalValidationEngine.get_demographic_breakdown(SubgroupCategory.SEX)
    assert breakdown.stratification == SubgroupCategory.SEX
    assert len(breakdown.subgroups) >= 2

    group_names = [s.subgroup_value for s in breakdown.subgroups]
    assert "Male" in group_names
    assert "Female" in group_names

    for sub in breakdown.subgroups:
        assert sub.sample_size > 50
        assert len(sub.targets) >= 8
        for t in sub.targets:
            assert t.auroc >= 0.50
            assert t.ece < 0.50


def test_validation_demographic_breakdown_age():
    """Verify stratified performance across Age categories."""
    breakdown = ClinicalValidationEngine.get_demographic_breakdown(SubgroupCategory.AGE)
    assert breakdown.stratification == SubgroupCategory.AGE
    assert len(breakdown.subgroups) >= 2

    for sub in breakdown.subgroups:
        assert sub.sample_size > 0
        assert len(sub.targets) >= 8


def test_validation_demographic_breakdown_income():
    """Verify stratified performance across Income Poverty Ratio (PIR) categories."""
    breakdown = ClinicalValidationEngine.get_demographic_breakdown(SubgroupCategory.INCOME_PIR)
    assert breakdown.stratification == SubgroupCategory.INCOME_PIR
    assert len(breakdown.subgroups) >= 2


def test_api_cohort_summary_endpoint():
    """GET /api/v1/validation/cohort-summary returns diagnostic metrics."""
    resp = client.get("/api/v1/validation/cohort-summary")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_holdout_samples" in data
    assert "evaluated_targets_count" in data
    assert "overall_macro_auroc" in data
    assert "targets" in data
    assert len(data["targets"]) >= 8


def test_api_demographic_breakdown_endpoint():
    """GET /api/v1/validation/demographic-breakdown?stratification=SEX returns stratified report."""
    resp = client.get("/api/v1/validation/demographic-breakdown?stratification=SEX")
    assert resp.status_code == 200
    data = resp.json()

    assert data["stratification"] == "SEX"
    assert len(data["subgroups"]) >= 2
    assert "targets" in data["subgroups"][0]
