"""
Test External Validation & Clinical Transparency Suite (Phase 4 & Phase 5)
NutriScan Final Gap Closure Program

Validates:
1. Statutory Clinical Transparency & CDSS Metadata Model (FDA 21 CFR 820 / EU MDR non-device)
2. Clinician Review & Sign-off Workflow (Expert annotation, agreement status, adjustments)
3. Retrieval of Clinician Reviews per Assessment
4. Ground-Truth Clinical Outcome Recording (Lab follow-up verification)
5. Prospective Validation Analytics (Real-world sensitivity, specificity, inter-rater reliability)
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import create_access_token, UserRole
from app.core.persistence import PersistenceRepository
from app.modules.governance.transparency import (
    ClinicalTransparencyMetadata,
    generate_transparency_metadata
)

client = TestClient(app)


class TestClinicalTransparencyFramework:
    """Validates statutory CDSS regulatory metadata and explainability disclosures."""

    def test_transparency_metadata_generation(self):
        metadata = generate_transparency_metadata(
            calibrated_confidence_score=0.92,
            target_nutrients=["Iron", "Vitamin D", "Magnesium"],
            primary_assumptions=["Patient fasting state", "Adult physiology"]
        )

        # Regulatory & intended use affirmations
        assert metadata.is_diagnostic is False
        assert "non-device clinical decision support" in metadata.regulatory_classification.lower()
        assert "FDA 21 CFR 520" in metadata.regulatory_classification
        assert "healthcare professionals" in metadata.intended_use.lower()

        # Confidence & limitations
        assert metadata.calibrated_confidence_score == 0.92
        assert len(metadata.data_limitations) > 0
        assert "NHANES" in metadata.validation_scope
        assert metadata.primary_assumptions == ["Patient fasting state", "Adult physiology"]

    def test_transparency_metadata_serialization(self):
        metadata = generate_transparency_metadata(
            calibrated_confidence_score=0.88,
            target_nutrients=["Zinc"]
        )
        data = metadata.model_dump()
        assert data["calibrated_confidence_score"] == 0.88
        assert data["cdss_classification"] == "Class I Non-Device CDSS"
        assert "disclaimer" in data


class TestExternalValidationAndClinicianWorkflows:
    """Validates expert annotations, clinician sign-offs, and prospective trial tracking."""

    @pytest.fixture
    def clinician_auth(self):
        clinician_id = str(uuid.uuid4())
        token = create_access_token(
            user_id=clinician_id,
            email="dr.chen@nutriscan-trials.org",
            role=UserRole.CLINICIAN
        )
        return {
            "clinician_id": clinician_id,
            "headers": {"Authorization": f"Bearer {token}"}
        }

    def test_clinician_review_submission_and_retrieval(self, clinician_auth):
        as_id = str(uuid.uuid4())
        PersistenceRepository.save_assessment(as_id, {"age": 45, "gender": "FEMALE"})

        review_payload = {
            "assessment_id": as_id,
            "reviewer_name": "Dr. Sarah Chen, MD",
            "reviewer_role": "Clinical Nutritionist",
            "reviewer_license": "MED-CA-98741",
            "agreement_status": "MODIFY",
            "clinical_notes": "Patient presents with subclinical iron deficiency; recommended dosage titrated upward.",
            "recommended_adjustments": {
                "Iron": "Increase elemental iron to 65mg daily with 500mg Vitamin C for enhanced absorption."
            },
            "contraindications_flagged": ["Mild gastritis noted; avoid taking iron on empty stomach."]
        }

        # Submit review
        res = client.post("/api/v1/validation/reviews", json=review_payload, headers=clinician_auth["headers"])
        assert res.status_code == 201
        data = res.json()
        assert data["assessment_id"] == as_id
        assert data["reviewer_name"] == "Dr. Sarah Chen, MD"
        assert data["agreement_status"] == "MODIFY"
        assert "review_id" in data

        # Retrieve reviews for assessment
        get_res = client.get(f"/api/v1/validation/reviews/{as_id}", headers=clinician_auth["headers"])
        assert get_res.status_code == 200
        reviews = get_res.json()
        assert len(reviews) >= 1
        assert reviews[0]["reviewer_license"] == "MED-CA-98741"

    def test_ground_truth_outcome_recording(self, clinician_auth):
        as_id = str(uuid.uuid4())
        PersistenceRepository.save_assessment(as_id, {"age": 52, "gender": "MALE"})

        outcome_payload = {
            "assessment_id": as_id,
            "patient_id": str(uuid.uuid4()),
            "follow_up_days": 60,
            "observed_deficiencies": {
                "Iron": False,
                "Vitamin D": True
            },
            "lab_biomarkers_confirmed": {
                "serum_ferritin_ng_ml": 48.5,
                "serum_25_hydroxy_d_ng_ml": 18.2
            },
            "adherence_score": 0.85,
            "notes": "Patient achieved iron repletion; vitamin D recovery still progressing."
        }

        res = client.post("/api/v1/validation/outcomes", json=outcome_payload, headers=clinician_auth["headers"])
        assert res.status_code == 201
        data = res.json()
        assert data["assessment_id"] == as_id
        assert data["follow_up_days"] == 60
        assert data["observed_deficiencies"]["Iron"] is False
        assert data["observed_deficiencies"]["Vitamin D"] is True

        # Retrieve outcomes
        get_res = client.get(f"/api/v1/validation/outcomes/{as_id}", headers=clinician_auth["headers"])
        assert get_res.status_code == 200
        outcomes = get_res.json()
        assert len(outcomes) >= 1
        assert outcomes[0]["lab_biomarkers_confirmed"]["serum_ferritin_ng_ml"] == 48.5

    def test_prospective_validation_analytics_calculation(self, clinician_auth):
        # Insert a set of agreed and modified reviews to compute inter-rater agreement
        for i in range(5):
            as_id = str(uuid.uuid4())
            PersistenceRepository.save_assessment(as_id, {"patient_id": i})
            PersistenceRepository.save_clinician_review({
                "review_id": str(uuid.uuid4()),
                "assessment_id": as_id,
                "reviewer_id": clinician_auth["clinician_id"],
                "reviewer_name": "Dr. Validator",
                "reviewer_role": "Investigator",
                "agreement_status": "AGREE" if i % 2 == 0 else "MODIFY",
                "clinical_notes": "Trial validation annotation"
            })
            PersistenceRepository.save_ground_truth_outcome({
                "outcome_id": str(uuid.uuid4()),
                "assessment_id": as_id,
                "patient_id": f"pt_{i}",
                "follow_up_days": 30,
                "observed_deficiencies": {"Iron": True},
                "lab_biomarkers_confirmed": {"ferritin": 15.0},
                "adherence_score": 0.9
            })

        analytics_res = client.get("/api/v1/validation/analytics", headers=clinician_auth["headers"])
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()

        assert "total_clinician_reviews" in analytics
        assert analytics["total_clinician_reviews"] >= 5
        assert "inter_rater_agreement_rate" in analytics
        assert 0.0 <= analytics["inter_rater_agreement_rate"] <= 1.0
        assert "total_ground_truth_outcomes" in analytics
        assert analytics["total_ground_truth_outcomes"] >= 5
        assert "prospective_accuracy" in analytics
        assert "brier_score" in analytics
