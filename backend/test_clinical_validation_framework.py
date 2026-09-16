"""
Clinical Validation Framework & Regulatory Audit Test Suite.
Phase 7: Clinical Safety, Inter-Rater Reliability & Empirical Trial Validation.

Tests:
1. Cohen's Kappa & Fleiss' Kappa inter-rater reliability calculations
2. Multi-class confusion matrix, sensitivity, specificity across deficiency tiers
3. Adverse biochemical interaction detection sensitivity (>99.0% threshold)
4. Empirical forecast accuracy (MAE, RMSE, MAPE, Concordance %)
5. Clinician review agreement & dataset evaluation
6. End-to-end API validation flow with authenticated clinician sign-offs & analytics
"""

import uuid
import warnings
import pytest

# Suppress external library warnings in test runner
warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient

from app.main import app
from app.modules.validation.clinical_evaluator import ClinicalValidationEvaluator
from app.core.auth import create_access_token, UserRole
from app.core.persistence import PersistenceRepository


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def clinician_auth_headers():
    """Generates valid JWT bearer authorization headers for a CLINICIAN role."""
    token = create_access_token(
        user_id=f"doc_{uuid.uuid4().hex[:8]}",
        email="dr.validator@nutriscan.test",
        role=UserRole.CLINICIAN
    )
    return {"Authorization": f"Bearer {token}"}


class TestInterRaterReliabilityMetrics:
    """Verifies statistical correctness of Cohen's and Fleiss' Kappa implementations."""

    def test_cohens_kappa_perfect_agreement(self):
        rater1 = ["APPROVED", "MODIFIED", "APPROVED", "REJECTED", "APPROVED"]
        rater2 = ["APPROVED", "MODIFIED", "APPROVED", "REJECTED", "APPROVED"]
        kappa = ClinicalValidationEvaluator.calculate_cohens_kappa(rater1, rater2)
        assert kappa == 1.0

    def test_cohens_kappa_partial_agreement(self):
        rater1 = ["APPROVED", "APPROVED", "MODIFIED", "APPROVED", "REJECTED",
                  "APPROVED", "MODIFIED", "APPROVED", "APPROVED", "MODIFIED"]
        rater2 = ["APPROVED", "APPROVED", "MODIFIED", "APPROVED", "MODIFIED",
                  "APPROVED", "MODIFIED", "APPROVED", "REJECTED", "MODIFIED"]
        kappa = ClinicalValidationEvaluator.calculate_cohens_kappa(rater1, rater2)
        assert 0.60 <= kappa <= 1.0, f"Expected substantial agreement, got kappa={kappa}"

    def test_cohens_kappa_chance_or_poor_agreement(self):
        rater1 = ["APPROVED", "APPROVED", "MODIFIED", "MODIFIED"]
        rater2 = ["MODIFIED", "MODIFIED", "APPROVED", "APPROVED"]
        kappa = ClinicalValidationEvaluator.calculate_cohens_kappa(rater1, rater2)
        assert kappa <= 0.0

    def test_cohens_kappa_input_validation(self):
        with pytest.raises(ValueError):
            ClinicalValidationEvaluator.calculate_cohens_kappa(["A", "B"], ["A"])

    def test_fleiss_kappa_multi_rater_consensus(self):
        matrix = [
            [3, 0, 0],
            [3, 0, 0],
            [0, 3, 0],
            [2, 1, 0],
            [0, 0, 3],
        ]
        kappa = ClinicalValidationEvaluator.calculate_fleiss_kappa(matrix)
        assert kappa >= 0.75, f"Expected substantial Fleiss kappa, got {kappa}"


class TestConfusionMatrixAndClinicalSensitivity:
    """Verifies diagnostic sensitivity, specificity, and multi-tier confusion matrix calculation."""

    def test_multi_class_confusion_matrix_metrics(self):
        y_true = [
            "LOW", "LOW", "LOW", "LOW", "LOW",
            "MODERATE", "MODERATE", "MODERATE", "MODERATE", "MODERATE",
            "HIGH", "HIGH", "HIGH", "HIGH", "HIGH",
            "HIGH", "HIGH", "HIGH", "HIGH", "HIGH"
        ]
        y_pred = [
            "LOW", "LOW", "LOW", "LOW", "MODERATE",
            "MODERATE", "MODERATE", "MODERATE", "MODERATE", "LOW",
            "HIGH", "HIGH", "HIGH", "HIGH", "HIGH",
            "HIGH", "HIGH", "HIGH", "HIGH", "MODERATE"
        ]
        results = ClinicalValidationEvaluator.calculate_confusion_matrix_and_metrics(y_true, y_pred)

        assert results["sample_size"] == 20
        assert results["overall_accuracy"] >= 0.85

        high_metrics = results["metrics_by_tier"]["HIGH"]
        assert high_metrics["sensitivity"] >= 0.90
        assert high_metrics["specificity"] >= 0.95

        assert results["macro_sensitivity"] >= 0.80
        assert results["macro_specificity"] >= 0.85


class TestAdverseInteractionSafetyThreshold:
    """Verifies adverse biochemical interaction detection meets the >99.0% regulatory safety gate."""

    def test_critical_interaction_detection_sensitivity(self):
        eval_result = ClinicalValidationEvaluator.evaluate_adverse_interaction_detection()
        assert eval_result["meets_safety_gate"] is True
        assert eval_result["sensitivity_pct"] >= 99.0
        assert eval_result["total_hazardous_pairs"] >= 5

    def test_custom_interaction_detector_integration(self):
        def mock_detector(nuts):
            return [{"interaction": "DETECTED"}]

        custom_eval = ClinicalValidationEvaluator.evaluate_adverse_interaction_detection(
            interaction_detector_fn=mock_detector
        )
        assert custom_eval["sensitivity_pct"] == 100.0
        assert custom_eval["meets_safety_gate"] is True


class TestForecastAndClinicianDatasetEvaluation:
    """Verifies longitudinal forecast error metrics and clinician sign-off dataset evaluations."""

    def test_evaluate_forecast_metrics(self):
        actual = [22.0, 35.0, 18.5, 42.0, 28.0]
        predicted = [23.5, 33.8, 19.0, 40.5, 29.2]

        metrics = ClinicalValidationEvaluator.evaluate_forecast_metrics(predicted, actual)
        assert metrics["mae"] < 2.0
        assert metrics["rmse"] < 2.5
        assert metrics["mape"] < 10.0
        assert metrics["concordance_pct"] == 100.0
        assert metrics["r_squared"] > 0.90

    def test_evaluate_clinician_reviews_dataset(self):
        reviews = [
            {"decision": "APPROVED", "biomarker_concordance_rating": 5.0},
            {"decision": "APPROVED", "biomarker_concordance_rating": 4.0},
            {"decision": "APPROVED", "biomarker_concordance_rating": 5.0},
            {"decision": "MODIFIED", "biomarker_concordance_rating": 4.0},
            {"decision": "REJECTED", "biomarker_concordance_rating": 2.0},
        ]
        res = ClinicalValidationEvaluator.evaluate_clinician_reviews_dataset(reviews)
        assert res["total_reviews"] == 5
        assert res["agreement_pct"] == 60.0
        assert res["modification_pct"] == 20.0
        assert res["rejection_pct"] == 20.0
        assert 3.5 <= res["mean_concordance_score"] <= 4.5


class TestValidationAPIEndpoints:
    """End-to-end integration tests for clinician sign-offs, ground truth lab outcomes, and trial analytics."""

    def test_submit_and_retrieve_clinician_review(self, client, clinician_auth_headers):
        assessment_id = f"assess_{uuid.uuid4().hex[:8]}"
        # Ensure parent assessment exists to satisfy foreign key constraint
        PersistenceRepository.save_assessment(
            assessment_id,
            {"age": 35, "gender": "FEMALE", "dietary_pattern": "OMNIVORE"}
        )

        payload = {
            "assessment_id": assessment_id,
            "clinician_name": "Dr. Eleanor Vance, MD",
            "license_number": "MED-884920",
            "decision": "APPROVED",
            "biomarker_concordance_rating": 5.0,
            "clinical_notes": "Clinical assessment validated. Recommendation aligns with RDA guidelines.",
            "recommended_adjustments": {"vitamin_d_target_iu": 2000}
        }
        post_res = client.post("/api/v1/validation/reviews", json=payload, headers=clinician_auth_headers)
        assert post_res.status_code == 201
        data = post_res.json()
        assert data["assessment_id"] == assessment_id
        assert data["decision"] == "APPROVED"
        assert data["license_number"] == "MED-884920"

        # Fetch reviews for assessment
        get_res = client.get(f"/api/v1/validation/reviews/{assessment_id}", headers=clinician_auth_headers)
        assert get_res.status_code == 200
        reviews = get_res.json()
        assert len(reviews) >= 1
        assert reviews[0]["assessment_id"] == assessment_id

    def test_record_and_retrieve_ground_truth_outcome(self, client, clinician_auth_headers):
        assessment_id = f"assess_{uuid.uuid4().hex[:8]}"
        patient_id = f"pat_{uuid.uuid4().hex[:8]}"
        # Ensure parent assessment exists
        PersistenceRepository.save_assessment(
            assessment_id,
            {"age": 42, "gender": "MALE", "dietary_pattern": "MEDITERRANEAN"}
        )

        outcome_payload = {
            "assessment_id": assessment_id,
            "patient_id": patient_id,
            "followup_day": 30,
            "nutrient": "Vitamin D",
            "predicted_value": 32.0,
            "actual_lab_value": 31.4,
            "observed_deficiencies": {"VITAMIN_D": False},
            "lab_biomarkers_confirmed": {"serum_25_oh_d": 31.4},
            "notes": "30-day post-supplementation serum lab verified."
        }
        post_res = client.post("/api/v1/validation/outcomes", json=outcome_payload, headers=clinician_auth_headers)
        assert post_res.status_code == 201
        out_data = post_res.json()
        assert out_data["assessment_id"] == assessment_id
        assert out_data["patient_id"] == patient_id
        assert abs(out_data["delta"]) <= 1.0

        # Retrieve outcomes
        get_res = client.get(f"/api/v1/validation/outcomes/{assessment_id}", headers=clinician_auth_headers)
        assert get_res.status_code == 200
        outcomes = get_res.json()
        assert len(outcomes) >= 1

    def test_get_validation_analytics(self, client):
        res = client.get("/api/v1/validation/analytics")
        assert res.status_code == 200
        data = res.json()
        assert "trial_status" in data
        assert "mean_concordance_pct" in data
        assert "inter_rater_agreement_rate" in data
        assert "adverse_interaction_sensitivity_pct" in data
        assert data["adverse_interaction_sensitivity_pct"] >= 99.0
        assert "clinical_evaluation_summary" in data
