"""
Prediction Schemas & Data Transfer Objects (DTOs)
Phase 3: Multi-Nutrient Prediction Engine Development
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class ConfidenceLevelEnum(str, Enum):
    HIGH_CONFIDENCE = "High Confidence"
    MEDIUM_CONFIDENCE = "Medium Confidence"
    LOW_CONFIDENCE = "Low Confidence"


class RiskFactorDetail(BaseModel):
    feature_name: str
    factor_name: str
    category: str
    raw_value: Any
    impact_score: float
    impact_magnitude: str
    direction: str
    clinical_explanation: str
    evidence_reference: Optional[str] = None


class NutrientPredictionItem(BaseModel):
    """
    Standardized per-nutrient prediction item matching target contract.
    Target schema:
    {
      "nutrient": "Vitamin D",
      "risk_level": "HIGH",
      "deficiency_probability": 0.87,
      "confidence": 0.92,
      "score": 85.0,
      "probability_distribution": {
        "low": 0.05,
        "moderate": 0.15,
        "high": 0.80
      }
    }
    """
    nutrient: str = Field(..., description="Nutrient name, e.g., 'Vitamin D', 'Iron', 'Vitamin B12'")
    nutrient_code: Optional[str] = Field(default=None, description="Canonical code, e.g. 'VITAMIN_D', 'IRON'")
    risk_level: str = Field(..., description="'LOW', 'MODERATE', or 'HIGH'")
    deficiency_probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated deficiency probability: P(MODERATE) + P(HIGH)")
    probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated deficiency probability (alias)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Mathematical model certainty / confidence score")
    confidence_level: Optional[str] = Field(default="High Confidence", description="'High Confidence', 'Medium Confidence', 'Low Confidence'")
    priority_rank: Optional[int] = Field(default=None, description="Triage priority rank (1 = highest urgency)")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Continuous risk score 0.0 - 100.0")
    confidence_interval: Optional[Dict[str, float]] = Field(default=None, description="Low/high confidence interval")
    probability_distribution: Union[Dict[str, float], List[float]] = Field(
        default_factory=lambda: {"low": 0.0, "moderate": 0.0, "high": 0.0},
        description="Probability distribution: {'low': float, 'moderate': float, 'high': float}"
    )
    risk_factors: Optional[List[RiskFactorDetail]] = Field(default_factory=list, description="Top SHAP driving factors")


class NutrientInteractionItem(BaseModel):
    nutrients: List[str]
    interaction_type: str
    severity: str
    compounding_multiplier: float
    clinical_mechanism: str
    actionable_guidance: str
    summary: str


class OverallDeficiencySummary(BaseModel):
    overall_risk: str = Field(..., description="'LOW', 'MODERATE', or 'HIGH'")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    overall_severity: str = Field(..., description="'LOW', 'MODERATE', 'HIGH', 'CRITICAL'")
    high_risk_count: int
    moderate_risk_count: int
    compounding_interaction_multiplier: float


class MultiNutrientPredictionResponse(BaseModel):
    """
    Standardized Multi-Nutrient Prediction API Response.
    """
    assessment_id: Optional[uuid.UUID] = None
    overall_risk: str = Field(..., description="'LOW', 'MODERATE', or 'HIGH'")
    overall_risk_score: float
    overall_severity: Optional[str] = None
    inference_latency_ms: float = Field(..., description="Inference execution time in milliseconds (< 500 ms)")
    nutrient_predictions: List[NutrientPredictionItem]
    predictions: Optional[List[NutrientPredictionItem]] = None
    priority_ranking: List[str] = Field(..., description="Nutrient names ordered by priority 1 to 11")
    nutrient_interactions: Optional[List[NutrientInteractionItem]] = Field(default_factory=list)
    screening_metadata: Optional[Dict[str, Any]] = None


class BatchPredictionRequest(BaseModel):
    assessments: List[Dict[str, Any]] = Field(..., description="List of patient screening input payloads")


class BatchPredictionResponse(BaseModel):
    total_records: int
    batch_latency_ms: float
    results: List[MultiNutrientPredictionResponse]
