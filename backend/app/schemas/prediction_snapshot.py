"""
Assessment Prediction Snapshot Schema
Single Source of Truth across Dashboard, Reasoning, Evidence, Recommendations, Personalization, Reports, and Network.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .clinical_prediction import ClinicalTargetPrediction, ClinicalRiskTier
from .phase11_explainability import TargetExplanation, EvidenceGrade


class AssessmentPredictionSnapshot(BaseModel):
    """
    Authoritative snapshot of clinical predictions generated once per assessment.
    Guarantees logical consistency and zero runtime re-inference across all consuming modules.
    """
    assessment_id: str = Field(..., description="Unique assessment identifier")
    generated_at: str = Field(..., description="ISO 8601 generation timestamp (UTC)")
    model_suite_version: str = Field(default="v10.3.0-prod", description="Version of the clinical model suite")
    
    # 9 Verified Clinical Target Predictions
    predictions: List[ClinicalTargetPrediction] = Field(..., description="9 calibrated Phase 10B/10C target predictions")
    
    # Normalized risk counts across the 9 targets
    risk_counts: Dict[str, int] = Field(..., description="Counts of HIGH, MODERATE, and LOW risk targets")
    
    # High-level assessment metrics
    overall_risk: str = Field(..., description="Overall risk classification: HIGH, MODERATE, or LOW")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite clinical risk score [0.0 - 100.0]")
    health_score: int = Field(..., ge=0, le=100, description="Overall nutritional health score [0 - 100]")
    category: str = Field(..., description="Health category: EXCELLENT, GOOD, MODERATE_RISK, or HIGH_RISK")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Average mathematical certainty [0.0 - 1.0]")
    evidence_grade: str = Field(default="Grade A", description="Scientific evidence quality tier")
    
    # Priority triage
    highest_risk_prediction: Optional[str] = Field(None, description="Target name with highest clinical urgency, or None if all LOW")
    priority_ranking: List[str] = Field(default_factory=list, description="Ordered target names by triage urgency")
    
    # Stored pre-computed explainability & evidence (zero runtime re-inference)
    explanations: List[TargetExplanation] = Field(default_factory=list, description="Precomputed SHAP drivers and dual-layer narratives")
    evidence_catalog: Dict[str, Any] = Field(default_factory=dict, description="Precomputed scientific evidence and citation records")
    
    # Backward compatibility alias for legacy consumers expecting 'nutrient_predictions'
    nutrient_predictions: List[Dict[str, Any]] = Field(default_factory=list, description="Legacy-compatible mapped prediction array")
    audit_log: Optional[Dict[str, Any]] = Field(default=None, description="Feature completeness and latency metadata")
