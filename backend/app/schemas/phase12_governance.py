"""
Phase 12: Clinical Validation, Safety Governance & Production Monitoring Schemas.
Codifies Pydantic DTOs for:
- Clinical Demographic Validation & Performance Benchmarks
- Real-Time Feature & Model Drift Telemetry (PSI, KS 2-Sample)
- Clinical Safety Guardrails & Upper Tolerable Limit Governance
- Bias & Fairness Auditing (Demographic Parity & Equal Opportunity)
- Production Monitoring & Real-Time Performance Rollups
- Clinical Audit Trail & Signed Decision Snapshots
"""

import uuid
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class SafetySeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


SafetyRiskTier = SafetySeverity


class SafetyAction(str, Enum):
    FLAGGED = "FLAGGED"
    QUARANTINED = "QUARANTINED"
    BLOCKED = "BLOCKED"
    OVERRIDDEN = "OVERRIDDEN"


class DriftStatus(str, Enum):
    STABLE = "STABLE"
    MODERATE_SHIFT = "MODERATE_SHIFT"
    SIGNIFICANT_DRIFT = "SIGNIFICANT_DRIFT"


class DriftCategory(str, Enum):
    FEATURE = "FEATURE"
    POPULATION = "POPULATION"
    PREDICTION = "PREDICTION"
    NUTRIENT_INTAKE = "NUTRIENT_INTAKE"


class MetricType(str, Enum):
    PSI = "PSI"
    KS_2SAMPLE = "KS_2SAMPLE"
    WASSERSTEIN = "WASSERSTEIN"


class SubgroupCategory(str, Enum):
    AGE = "AGE"
    SEX = "SEX"
    RACE_ETHNICITY = "RACE_ETHNICITY"
    INCOME_PIR = "INCOME_PIR"


ProtectedAttribute = SubgroupCategory


class AlertType(str, Enum):
    DRIFT_ALERT = "DRIFT_ALERT"
    CALIBRATION_DEGRADATION = "CALIBRATION_DEGRADATION"
    SAFETY_VIOLATION = "SAFETY_VIOLATION"
    PREDICTION_FAILURE = "PREDICTION_FAILURE"
    DATA_QUALITY = "DATA_QUALITY"
    FAIRNESS_DISPARITY = "FAIRNESS_DISPARITY"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# A. CLINICAL VALIDATION SCHEMAS
# ---------------------------------------------------------------------------

class ValidationTargetMetrics(BaseModel):
    """Diagnostic performance metrics for a single clinical target model."""
    target: str = Field(..., description="Target machine learning identifier")
    target_name: str = Field(..., description="Display title of the deficiency")
    algorithm: str = Field(..., description="Champion algorithm used")
    sample_size: int = Field(..., description="Evaluation sample size")
    prevalence_pct: float = Field(..., description="Empirical ground-truth prevalence percentage")
    auroc: float = Field(..., ge=0.0, le=1.0, description="Area Under the Receiver Operating Characteristic Curve")
    auprc: float = Field(..., ge=0.0, le=1.0, description="Area Under the Precision-Recall Curve")
    sensitivity: float = Field(..., ge=0.0, le=1.0, description="True Positive Rate (Recall)")
    specificity: float = Field(..., ge=0.0, le=1.0, description="True Negative Rate")
    ppv: float = Field(..., ge=0.0, le=1.0, description="Positive Predictive Value (Precision)")
    npv: float = Field(..., ge=0.0, le=1.0, description="Negative Predictive Value")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="Harmonic mean of precision and recall")
    ece: float = Field(..., ge=0.0, description="Expected Calibration Error")
    brier_score: float = Field(..., ge=0.0, description="Mean squared probability error")


class SubgroupValidationReport(BaseModel):
    """Stratified validation metrics for a specific demographic subgroup."""
    subgroup_category: SubgroupCategory
    subgroup_value: str
    sample_size: int
    targets: List[ValidationTargetMetrics]


class CohortValidationSummaryResponse(BaseModel):
    """Aggregated holdout cohort validation summary across all 9 models."""
    total_holdout_samples: int
    evaluated_targets_count: int
    overall_macro_auroc: float
    overall_macro_ece: float
    targets: List[ValidationTargetMetrics]


class DemographicBreakdownResponse(BaseModel):
    """Cross-demographic validation reports across Age, Sex, Race, and Income."""
    stratification: SubgroupCategory
    subgroups: List[SubgroupValidationReport]


# ---------------------------------------------------------------------------
# B. MODEL DRIFT DETECTION SCHEMAS
# ---------------------------------------------------------------------------

class FeatureDriftItem(BaseModel):
    """Drift telemetry for a single input feature or nutrient."""
    feature_name: str
    category: DriftCategory
    psi: float = Field(..., description="Population Stability Index")
    ks_statistic: Optional[float] = Field(default=None, description="KS two-sample maximum divergence")
    ks_p_value: Optional[float] = Field(default=None, description="KS two-sample p-value")
    status: DriftStatus
    alert_triggered: bool


class TargetPredictionDrift(BaseModel):
    """Drift telemetry for calibrated prediction probability distribution."""
    target: str
    target_name: str
    psi: float
    status: DriftStatus


class DriftReportResponse(BaseModel):
    """Complete population stability and statistical drift analysis."""
    timestamp: datetime
    reference_sample_size: int
    evaluated_window_size: int
    overall_drift_status: DriftStatus
    max_feature_psi: float
    features_evaluated: int
    drift_breakdown: List[FeatureDriftItem]
    prediction_drift: List[TargetPredictionDrift]


# ---------------------------------------------------------------------------
# C. CLINICAL SAFETY ENGINE SCHEMAS
# ---------------------------------------------------------------------------

class SafetyViolation(BaseModel):
    """Granular clinical guardrail violation record."""
    severity: SafetySeverity
    rule_id: str
    rule_name: str
    nutrient: Optional[str] = None
    violating_value: Optional[float] = None
    threshold_value: Optional[float] = None
    clinical_rationale: str
    action_taken: SafetyAction

    @property
    def details(self) -> str:
        return self.clinical_rationale


class SafetyEvaluationRequest(BaseModel):
    """Payload for assessing safety of an assessment and proposed interventions."""
    assessment: Dict[str, Any] = Field(..., description="Patient clinical and demographic profile")
    predictions: List[Dict[str, Any]] = Field(default_factory=list, description="Calibrated target predictions")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Proposed food or supplement interventions")


class SafetyEvaluationResponse(BaseModel):
    """Comprehensive safety evaluation report and quantitative clearance."""
    safety_score: float = Field(..., ge=0.0, le=100.0, description="0-100 Clinical Safety Score")
    safety_tier: SafetySeverity
    is_safe_for_dispatch: bool
    violations_count: int
    violations: List[SafetyViolation]
    mitigation_instructions: str

    @property
    def is_blocked(self) -> bool:
        return not self.is_safe_for_dispatch

    @property
    def risk_tier(self) -> SafetySeverity:
        return self.safety_tier


# ---------------------------------------------------------------------------
# D. BIAS & FAIRNESS SCHEMAS
# ---------------------------------------------------------------------------

class DemographicParityResult(BaseModel):
    """Assessment of equal acceptance rate across demographic groups."""
    attribute: str
    baseline_group: str
    comparison_group: str
    baseline_positive_rate: float
    comparison_positive_rate: float
    disparity_ratio: float
    compliant_with_80_pct_rule: bool


class EqualOpportunityResult(BaseModel):
    """Assessment of equal True Positive Rate across demographic groups."""
    attribute: str
    baseline_group: str
    comparison_group: str
    baseline_tpr: float
    comparison_tpr: float
    tpr_difference: float
    within_tolerance: bool


class FairnessReportResponse(BaseModel):
    """Multi-attribute algorithmic fairness and parity audit report."""
    timestamp: datetime
    overall_fairness_status: str
    attributes_evaluated: List[str]
    demographic_parity: Dict[str, DemographicParityResult]
    equal_opportunity: Dict[str, EqualOpportunityResult]
    subgroup_positive_rates: Dict[str, Dict[str, float]]


# ---------------------------------------------------------------------------
# E. PRODUCTION MONITORING & ALERTING SCHEMAS
# ---------------------------------------------------------------------------

class LatencyPercentiles(BaseModel):
    p50_ms: float
    p95_ms: float
    p99_ms: float


class MonitoringMetricsResponse(BaseModel):
    """Real-time production operations and inference telemetry."""
    timestamp: datetime
    total_screenings_evaluated: int
    requests_per_minute: float
    average_latency_ms: float
    latency_percentiles: LatencyPercentiles
    error_rate_pct: float
    overall_risk_distribution: Dict[str, float]
    active_safety_violations_count: int
    calibration_status: str
    drift_status: DriftStatus


class AlertItem(BaseModel):
    """Automated system alert record."""
    alert_id: uuid.UUID
    timestamp: datetime
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    @property
    def id(self) -> uuid.UUID:
        return self.alert_id


class AlertsListResponse(BaseModel):
    """Collection of active and historic monitoring alerts."""
    total_alerts: int
    unacknowledged_count: int
    alerts: List[AlertItem]


class AcknowledgeAlertRequest(BaseModel):
    """Payload for resolving or acknowledging an alert."""
    acknowledged_by: str


# ---------------------------------------------------------------------------
# F. CLINICAL AUDIT TRAIL SCHEMAS
# ---------------------------------------------------------------------------

class AuditRecordItem(BaseModel):
    """Immutable audit record for a single clinical screening transaction."""
    audit_id: uuid.UUID
    prediction_id: uuid.UUID
    assessment_id: Optional[uuid.UUID] = None
    timestamp: datetime
    model_suite_version: str
    feature_completeness_pct: float
    total_features_evaluated: int
    observed_features_count: int
    overall_risk_tier: str
    overall_risk_score: float
    safety_score: float
    safety_tier: SafetySeverity
    predictions: List[Dict[str, Any]]
    top_predictors: List[Dict[str, Any]]
    recommendation_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    safety_flags: List[Dict[str, Any]] = Field(default_factory=list)
    inference_latency_ms: float


class AuditLogsResponse(BaseModel):
    """Paginated collection of clinical audit logs."""
    total_records: int
    limit: int
    offset: int
    records: List[AuditRecordItem]
