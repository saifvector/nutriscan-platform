"""
Phase 10C Clinical Prediction Schemas & Data Transfer Objects (DTOs).
Provides structured definitions for:
- Clinical Risk Tiers (LOW, MODERATE, HIGH)
- Single and Multi-Nutrient Clinical Predictions
- Batch Screening Requests and Responses
- Model Registry Metadata and Model Cards
- System Health and Audit Logs
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
from datetime import datetime


class ClinicalRiskTier(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class ConfidenceTier(str, Enum):
    HIGH_CONFIDENCE = "High Confidence"
    MEDIUM_CONFIDENCE = "Medium Confidence"
    LOW_CONFIDENCE = "Low Confidence"


class ClinicalPredictorShap(BaseModel):
    feature_name: str = Field(..., description="Canonical predictor name")
    feature_label: str = Field(..., description="Human-readable clinical feature label")
    feature_value: Optional[Any] = Field(default=None, description="Observed or imputed input value")
    importance_weight: float = Field(..., description="Mean absolute SHAP / importance attribution")

    @field_validator("feature_value", mode="before")
    @classmethod
    def convert_numpy_feature_value(cls, v):
        if hasattr(v, "item"):
            return v.item()
        return v


class ClinicalTargetPrediction(BaseModel):
    """Prediction output for a single clinical deficiency target."""
    target: str = Field(..., description="Target identifier, e.g. target_iron_deficiency")
    target_name: str = Field(..., description="Clinical target name, e.g. Iron Deficiency")
    champion_algorithm: str = Field(..., description="Selected Phase 10B champion algorithm")
    raw_probability: float = Field(..., ge=0.0, le=1.0, description="Raw uncalibrated classifier score")
    calibrated_probability: float = Field(..., ge=0.0, le=1.0, description="Platt-scaled empirical probability")
    risk_tier: ClinicalRiskTier = Field(..., description="Clinical risk tier: LOW, MODERATE, or HIGH")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Mathematical certainty score [0.0 - 1.0]")
    confidence_tier: ConfidenceTier = Field(..., description="High, Medium, or Low Confidence")
    optimal_threshold: float = Field(..., description="Audited Phase 10B optimal decision cutoff")
    priority_rank: int = Field(..., ge=1, le=9, description="Triage priority rank (1 = highest urgency)")
    top_predictors: List[ClinicalPredictorShap] = Field(default_factory=list, description="Top SHAP feature drivers")


class ClinicalAuditLog(BaseModel):
    """Audit record for clinical compliance and observability."""
    prediction_id: uuid.UUID = Field(..., description="Unique prediction session UUID")
    timestamp: datetime = Field(..., description="UTC timestamp of inference execution")
    model_suite_version: str = Field(..., description="Clinical model suite version")
    feature_completeness_pct: float = Field(..., ge=0.0, le=100.0, description="Observed input completeness percentage")
    total_features_evaluated: int = Field(default=105, description="Total features in NHANES model vector")
    observed_features_count: int = Field(..., description="Number of non-default features supplied")
    active_champion_models: List[str] = Field(..., description="List of champion model algorithms used")
    inference_latency_ms: float = Field(..., description="Measured inference latency in milliseconds")


class ClinicalPredictionResponse(BaseModel):
    """Complete response payload for a single patient clinical screening."""
    prediction_id: uuid.UUID = Field(..., description="Unique assessment prediction identifier")
    timestamp: datetime = Field(..., description="Inference execution timestamp (UTC)")
    model_suite_version: str = Field(default="v10.3.0-prod", description="Version of active clinical model suite")
    overall_risk_tier: ClinicalRiskTier = Field(..., description="Highest detected risk tier across all targets")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="Aggregated 0-100 clinical risk score")
    total_deficiencies_detected: int = Field(..., description="Count of targets flagged as HIGH or MODERATE risk")
    priority_ranking: List[str] = Field(..., description="Target names ordered by clinical priority")
    predictions: List[ClinicalTargetPrediction] = Field(..., description="Detailed predictions across all 9 targets")
    audit_log: ClinicalAuditLog = Field(..., description="Audit metadata and feature completeness trace")
    inference_latency_ms: float = Field(..., description="End-to-end execution latency in milliseconds")


class ClinicalBatchPredictionRequest(BaseModel):
    """Batch screening request supporting multiple patient profiles."""
    assessments: List[Dict[str, Any]] = Field(..., min_length=1, description="List of patient assessment payloads")


class ClinicalBatchPredictionResponse(BaseModel):
    """High-throughput batch screening response."""
    total_records: int = Field(..., description="Total patient records evaluated")
    batch_latency_ms: float = Field(..., description="Total batch execution latency in milliseconds")
    average_latency_per_record_ms: float = Field(..., description="Average per-patient execution latency")
    results: List[ClinicalPredictionResponse] = Field(..., description="List of individual clinical prediction responses")


class ModelCardSummary(BaseModel):
    """Standardized metadata summary for a single champion model."""
    target: str
    target_name: str
    champion_algorithm: str
    optimal_threshold: float
    holdout_roc_auc: float
    holdout_pr_auc: float
    holdout_sensitivity: float
    holdout_specificity: float
    holdout_f1: float
    calibrated_brier_score: float
    calibrated_ece: float
    num_features: int
    model_file: str


class ModelRegistryResponse(BaseModel):
    """Catalog of all active Phase 10B champion models in production."""
    status: str = Field(default="READY")
    model_suite_version: str = Field(default="v10.3.0-prod")
    total_registered_models: int = Field(default=9)
    registry_path: str
    last_reloaded: datetime
    models: List[ModelCardSummary]


class ClinicalInferenceHealthResponse(BaseModel):
    """Readiness and latency health status of the clinical inference engine."""
    status: str = Field(..., description="'HEALTHY' or 'DEGRADED'")
    service: str = Field(default="Phase 10C Production Clinical Risk Engine")
    model_suite_version: str = Field(default="v10.3.0-prod")
    engine_warmed: bool = Field(default=True)
    registered_models_count: int = Field(default=9)
    benchmark_latency_ms: float = Field(..., description="Live benchmark latency for a single inference pass")
    all_calibrators_loaded: bool = Field(default=True)
    memory_status: str = Field(default="NOMINAL")
