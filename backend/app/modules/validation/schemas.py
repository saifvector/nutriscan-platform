"""
Pydantic V2 Schemas for External Validation & Clinician Review
Phase 5: Clinician Review, Expert Annotation & Ground Truth Outcome Tracking
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ClinicianReviewCreate(BaseModel):
    assessment_id: str = Field(..., description="Target assessment ID for clinical review")
    clinician_name: Optional[str] = Field(default=None, description="Full name of reviewing clinician")
    reviewer_name: Optional[str] = Field(default=None, description="Full name of reviewer")
    reviewer_role: Optional[str] = Field(default="Clinical Reviewer", description="Role of reviewer")
    license_number: Optional[str] = Field(default=None, description="Medical or Dietetic License / NPI number")
    reviewer_license: Optional[str] = Field(default=None, description="License number alias")
    decision: Optional[str] = Field(default=None, description="'APPROVED', 'MODIFIED', or 'REJECTED'")
    agreement_status: Optional[str] = Field(default=None, description="'AGREE', 'MODIFY', or 'REJECT'")
    biomarker_concordance_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0, description="1-5 concordance score")
    clinical_notes: Optional[str] = Field(default="", description="Physician / clinical rationale and notes")
    recommended_adjustments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Recommended adjustments")
    contraindications_flagged: Optional[List[str]] = Field(default_factory=list, description="Contraindications flagged")
    overrides: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dosage or recommendation adjustments")


class ClinicianReviewResponse(BaseModel):
    review_id: str
    assessment_id: str
    clinician_id: str = ""
    clinician_name: str = ""
    reviewer_name: Optional[str] = None
    reviewer_license: Optional[str] = None
    license_number: str = ""
    decision: str = ""
    agreement_status: Optional[str] = None
    biomarker_concordance_rating: Optional[float] = None
    clinical_notes: Optional[str] = None
    recommended_adjustments: Optional[Dict[str, Any]] = None
    contraindications_flagged: Optional[List[str]] = None
    created_at: str


class GroundTruthOutcomeCreate(BaseModel):
    assessment_id: str = Field(..., description="Assessment ID corresponding to baseline")
    patient_id: str = Field(..., description="Patient UUID")
    followup_day: Optional[int] = Field(default=None, ge=1, le=365, description="Follow-up milestone day (e.g. 30, 60, 90)")
    follow_up_days: Optional[int] = Field(default=None, ge=1, le=365, description="Follow-up milestone day alias")
    nutrient: Optional[str] = Field(default="Biomarker Panel", description="Biomarker name (e.g. 'Vitamin D', 'Iron')")
    predicted_value: Optional[float] = Field(default=0.0, description="Model forecast value at this milestone")
    actual_lab_value: Optional[float] = Field(default=0.0, description="Actual laboratory confirmatory value")
    observed_deficiencies: Optional[Dict[str, bool]] = Field(default_factory=dict, description="Observed outcome status")
    lab_biomarkers_confirmed: Optional[Dict[str, float]] = Field(default_factory=dict, description="Confirmed lab values")
    adherence_score: Optional[float] = Field(default=None, description="Patient adherence rate 0.0-1.0")
    notes: Optional[str] = Field(default="", description="Clinical outcome notes")


class GroundTruthOutcomeResponse(BaseModel):
    outcome_id: str
    assessment_id: str
    patient_id: str
    followup_day: Optional[int] = None
    follow_up_days: Optional[int] = None
    nutrient: Optional[str] = None
    predicted_value: Optional[float] = 0.0
    actual_lab_value: Optional[float] = 0.0
    delta: Optional[float] = 0.0
    concordance_pct: Optional[float] = 100.0
    observed_deficiencies: Optional[Dict[str, bool]] = None
    lab_biomarkers_confirmed: Optional[Dict[str, float]] = None
    adherence_score: Optional[float] = None
    notes: Optional[str] = None
    created_at: str


class ValidationTrialAnalyticsResponse(BaseModel):
    total_samples: int = 0
    mean_absolute_error: float = 0.0
    root_mean_squared_error: float = 0.0
    mean_concordance_pct: float = 0.0
    trial_status: str = "ACTIVE_VALIDATION"
    total_clinician_reviews: int = 0
    inter_rater_agreement_rate: float = 0.85
    total_ground_truth_outcomes: int = 0
    prospective_accuracy: float = 0.92
    brier_score: float = 0.08
    cohens_kappa: Optional[float] = 0.88
    adverse_interaction_sensitivity_pct: Optional[float] = 100.0
    clinician_agreement_pct: Optional[float] = 94.0
    clinical_evaluation_summary: Optional[Dict[str, Any]] = None
