"""
Phase 12: Demographic Fairness & Bias Audit Tests.
Verifies Disparate Impact (80% four-fifths rule), Demographic Parity Ratio,
Equal Opportunity Difference across protected classes, and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.governance.fairness_engine import FairnessAuditEngine

client = TestClient(app)


def test_fairness_engine_audit_report():
    """Verify fairness evaluation across Sex, Age, and Income populations."""
    report = FairnessAuditEngine.audit_fairness(force_recompute=False)
    assert report.overall_fairness_status in ["COMPLIANT", "FAIRNESS_WARNING", "NON_COMPLIANT", "AUDIT_REVIEW_FLAGGED"]
    assert len(report.attributes_evaluated) >= 2
    dp_map = {k.upper(): v for k, v in report.demographic_parity.items()}
    eo_map = {k.upper(): v for k, v in report.equal_opportunity.items()}
    assert "SEX" in dp_map
    assert "AGE" in dp_map

    # Sex demographic parity
    dp_sex = dp_map["SEX"]
    assert dp_sex.attribute == "SEX"
    assert dp_sex.baseline_group == "Male"
    assert dp_sex.comparison_group == "Female"
    assert dp_sex.disparity_ratio > 0.0
    assert isinstance(dp_sex.compliant_with_80_pct_rule, bool)

    # Sex equal opportunity
    eo_sex = eo_map["SEX"]
    assert eo_sex.attribute == "SEX"
    assert eo_sex.tpr_difference >= 0.0
    assert isinstance(eo_sex.within_tolerance, bool)


def test_fairness_engine_subgroup_positive_rates():
    """Verify positive prediction rates across subgroups are computed."""
    report = FairnessAuditEngine.audit_fairness(force_recompute=False)
    sp_map = {k.upper(): v for k, v in report.subgroup_positive_rates.items()}
    assert "SEX" in sp_map
    assert "AGE" in sp_map
    sex_rates = sp_map["SEX"]
    assert "Male" in sex_rates
    assert "Female" in sex_rates


def test_api_fairness_report_endpoint():
    """GET /api/v1/fairness/report returns fairness audit metrics."""
    resp = client.get("/api/v1/fairness/report")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_fairness_status" in data
    assert "demographic_parity" in data
    assert "equal_opportunity" in data
    dp_keys = [k.upper() for k in data["demographic_parity"].keys()]
    assert "SEX" in dp_keys
