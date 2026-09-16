"""
Pydantic V2 Schemas for Phase 9: Outcome Learning & Adaptive Nutrition Intelligence
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# 1. Adherence Intelligence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class AdherenceLogRequest(BaseModel):
    assessment_id: str = "demo"
    log_date: Optional[str] = None  # YYYY-MM-DD
    meal_adherence_pct: float = Field(..., ge=0.0, le=100.0)
    supplement_adherence_pct: float = Field(..., ge=0.0, le=100.0)
    lifestyle_adherence_pct: float = Field(..., ge=0.0, le=100.0)
    hydration_liters: float = Field(2.5, ge=0.0)
    sunlight_minutes: int = Field(20, ge=0)
    sleep_hours: float = Field(8.0, ge=0.0)
    exercise_minutes: int = Field(30, ge=0)
    missed_items: Optional[List[str]] = Field(default_factory=list)
    logged_items: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None


class AdherenceLogItem(BaseModel):
    id: str
    assessment_id: str
    log_date: str
    daily_adherence_score: float
    adherence_tier: str  # EXCELLENT, GOOD, MODERATE, POOR
    meal_adherence_pct: float
    supplement_adherence_pct: float
    lifestyle_adherence_pct: float
    hydration_liters: float
    sunlight_minutes: int
    sleep_hours: float
    exercise_minutes: int
    missed_items: List[str]
    recovery_impact_estimate: str


class AdherenceSummaryResponse(BaseModel):
    assessment_id: str
    daily_adherence_score: float
    weekly_adherence_score: float
    monthly_adherence_score: float
    overall_adherence_tier: str
    compliance_breakdown: Dict[str, float]
    missed_interventions: List[str]
    adherence_trend_analysis: str
    recovery_impact_estimation: str
    recent_logs: List[AdherenceLogItem]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Outcome Tracking Schemas (Symptoms, Biometrics, Labs)
# ─────────────────────────────────────────────────────────────────────────────

class SymptomLogRequest(BaseModel):
    assessment_id: str = "demo"
    recorded_date: Optional[str] = None
    symptoms: Dict[str, float] = Field(..., description="Map of symptom name to severity 0-10")
    notes: Optional[str] = None


class SymptomProgressItem(BaseModel):
    symptom_name: str
    baseline_severity: float
    current_severity: float
    delta_change: float
    percentage_improvement: float
    status: str  # IMPROVING, STABLE, DECLINING, RESOLVED
    weekly_recovery_velocity: float
    forecast_days_to_resolution: Optional[int]


class SymptomTimelineResponse(BaseModel):
    assessment_id: str
    overall_symptom_score: float
    symptom_recovery_score: float  # 0-100 where 100 is completely resolved
    symptoms_tracked_count: int
    improving_count: int
    resolved_count: int
    symptom_progress: List[SymptomProgressItem]
    clinical_summary: str
    historical_curve_points: List[Dict[str, Any]]


class LabLogRequest(BaseModel):
    assessment_id: str = "demo"
    test_date: Optional[str] = None
    lab_provider: Optional[str] = "Certified Diagnostic Laboratory"
    biomarkers: Dict[str, float] = Field(..., description="Tested biomarker levels (e.g. ferritin, vit D)")
    clinical_interpretation: Optional[str] = None


class BiomarkerComparisonItem(BaseModel):
    biomarker_name: str
    unit: str
    baseline_value: float
    current_value: float
    optimal_range: str
    delta_value: float
    percentage_change: float
    status: str  # DEFICIENT, SUBOPTIMAL, NORMAL, OPTIMAL
    clinical_significance: str


class LabTrackingResponse(BaseModel):
    assessment_id: str
    test_date: str
    biomarkers: List[BiomarkerComparisonItem]
    overall_lab_adequacy_score: float
    clinical_interpretation: str


class RecoveryStatusResponse(BaseModel):
    assessment_id: str
    baseline_health_score: float
    current_health_score: float
    health_score_delta: float
    recovery_velocity_pts_per_week: float
    recovery_status: str  # RAPID_RECOVERY, STEADY_RECOVERY, PLATEAU, REGRESSION
    days_in_protocol: int
    projected_full_recovery_date: str
    overall_improvement_percentage: float
    clinical_progress_summary: str


# ─────────────────────────────────────────────────────────────────────────────
# 3. Recommendation Effectiveness Schemas
# ─────────────────────────────────────────────────────────────────────────────

class InterventionEffectivenessItem(BaseModel):
    intervention_id: str
    intervention_type: str  # FOOD, SUPPLEMENT, LIFESTYLE
    name: str
    target_deficiency: str
    effectiveness_score: float = Field(..., description="Scale 0-100")
    clinical_impact_score: float = Field(..., description="Scale 0-100")
    recovery_contribution_score: float = Field(..., description="Scale 0-100")
    adherence_rate: float
    response_rate: str
    classification: str  # ACCELERATOR, EFFECTIVE, NEUTRAL, BOTTLENECK


class EffectivenessResponse(BaseModel):
    assessment_id: str
    overall_effectiveness_score: float
    top_effective_foods: List[InterventionEffectivenessItem]
    top_effective_supplements: List[InterventionEffectivenessItem]
    top_effective_lifestyle: List[InterventionEffectivenessItem]
    recovery_accelerators: List[InterventionEffectivenessItem]
    recovery_bottlenecks: List[InterventionEffectivenessItem]
    intervention_response_summary: str


# ─────────────────────────────────────────────────────────────────────────────
# 4. Adaptive Recommendation Schemas
# ─────────────────────────────────────────────────────────────────────────────

class AdaptiveRecommendationItem(BaseModel):
    adaptation_id: str
    scenario_category: str  # SCENARIO_A_FOOD_AVOIDANCE, SCENARIO_B_SUNLIGHT_FAILURE, SCENARIO_C_SUPPLEMENT_RESISTANCE, GENERAL_ADAPTATION
    trigger_reason: str
    original_guidance: str
    adapted_guidance: str
    alternative_interventions: List[str]
    adaptation_logic: str
    expected_recovery_acceleration: str
    is_active: bool


class AdaptivePlanResponse(BaseModel):
    assessment_id: str
    has_active_adaptations: bool
    adaptation_event_count: int
    active_adaptations: List[AdaptiveRecommendationItem]
    updated_recovery_plan: Dict[str, Any]
    adaptation_audit_log: List[Dict[str, Any]]


class GenerateAdaptationRequest(BaseModel):
    assessment_id: str = "demo"
    force_scenario: Optional[str] = None  # FISH_AVOIDANCE, SUNLIGHT_FAILURE, SUPPLEMENT_RESISTANCE
    user_feedback_notes: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# 5. Prediction Accuracy Validation Schemas
# ─────────────────────────────────────────────────────────────────────────────

class MilestoneAccuracyItem(BaseModel):
    milestone_day: int  # 30, 60, 90
    predicted_health_score: float
    actual_health_score: float
    absolute_error: float
    accuracy_percentage: float
    within_confidence_band: bool


class PredictionAccuracyResponse(BaseModel):
    assessment_id: str
    overall_prediction_accuracy_pct: float
    projection_mean_absolute_error: float
    confidence_calibration_score: float
    model_reliability_score: float  # Scale 0-100
    calibration_status: str  # HIGHLY_CALIBRATED, WELL_CALIBRATED, DRIFT_DETECTED
    milestone_evaluations: List[MilestoneAccuracyItem]
    clinical_model_report: str


# ─────────────────────────────────────────────────────────────────────────────
# 6. Relapse & Risk Monitoring Schemas
# ─────────────────────────────────────────────────────────────────────────────

class EarlyWarningFlagItem(BaseModel):
    flag_id: str
    flag_type: str  # PLATEAU_DETECTED, DECLINING_ADHERENCE, RELAPSE_RISK, EMERGING_DEFICIENCY, LIFESTYLE_DETERIORATION
    severity_level: str  # LOW, MODERATE, HIGH, CRITICAL
    headline: str
    clinical_description: str
    recommended_corrective_action: str


class RelapseRiskResponse(BaseModel):
    assessment_id: str
    relapse_probability_score: float  # 0.0 to 1.0
    overall_risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    early_warning_flags: List[EarlyWarningFlagItem]
    intervention_alerts: List[str]
    surveillance_summary: str


# ─────────────────────────────────────────────────────────────────────────────
# 7. Clinical Learning Dataset Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LearningCohortItem(BaseModel):
    cohort_id: str
    cohort_name: str
    sample_size: int
    target_deficiency: str
    average_recovery_velocity: float
    top_effective_intervention: str
    retraining_eligibility: str


class LearningDatasetResponse(BaseModel):
    total_longitudinal_records: int
    structured_outcome_datasets_count: int
    recovery_cohorts: List[LearningCohortItem]
    intervention_effectiveness_cohorts: List[Dict[str, Any]]
    dataset_version: str
    ready_for_model_retraining: bool
