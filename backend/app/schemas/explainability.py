"""
Pydantic V2 Schemas: Explainable AI & Risk Factor Analysis
Phase 4: Explainable AI and Risk Factor Analysis System

Contracts for:
- SHAP Feature Attributions & Contribution Percentages
- Positive Risk Drivers vs. Protective Factors
- Waterfall Plot Coordinates & SVG Visual Data
- 5-Category Risk Factor Classifications
- Clinical Reasoning Narratives (Patient-facing & Clinician notes)
- Population-Level Global Feature Importance
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime


class RiskFactorCategoryEnum(str, Enum):
    DIETARY = "DIETARY"
    LIFESTYLE = "LIFESTYLE"
    SYMPTOM = "SYMPTOM"
    MEDICAL_HISTORY = "MEDICAL_HISTORY"
    SUPPLEMENT = "SUPPLEMENT"
    PHYSIOLOGICAL = "PHYSIOLOGICAL"


class ImpactMagnitudeEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FactorDirectionEnum(str, Enum):
    RISK_INCREASING = "RISK_INCREASING"
    PROTECTIVE = "PROTECTIVE"


class FeatureContributionItem(BaseModel):
    feature_name: str = Field(..., description="Raw transformed model feature identifier")
    factor_name: str = Field(..., description="Clinically recognizable factor name")
    category: RiskFactorCategoryEnum = Field(..., description="Standardized clinical category")
    raw_value: Any = Field(..., description="Original unscaled value entered by user")
    impact_score: float = Field(..., description="Signed SHAP value / model attribution (+ increases risk, - protective)")
    impact_magnitude: ImpactMagnitudeEnum = Field(..., description="Categorical magnitude of impact")
    direction: FactorDirectionEnum = Field(..., description="Direction of risk contribution")
    contribution_percentage: float = Field(..., description="Percentage of total absolute attribution (|SHAP_i| / sum(|SHAP|))")
    clinical_explanation: str = Field(..., description="Physiological explanation of why this factor contributes to risk")
    evidence_reference: Optional[str] = Field(None, description="Medical guideline, NIH, or PubMed clinical citation")

    model_config = ConfigDict(from_attributes=True)


class WaterfallStepItem(BaseModel):
    step_index: int
    feature_name: str
    factor_name: str
    delta: float = Field(..., description="Signed shift in log-odds / margin from baseline")
    cumulative_value: float = Field(..., description="Running value after applying delta")
    direction: FactorDirectionEnum


class WaterfallPlotData(BaseModel):
    base_value: float = Field(..., description="Population expected baseline value E[f(x)]")
    final_value: float = Field(..., description="Final model prediction score f(x)")
    steps: List[WaterfallStepItem] = Field(default_factory=list)


class ClinicalReasoningSummary(BaseModel):
    nutrient: str
    risk_level: str
    primary_contributors: List[str] = Field(
        ...,
        description="Top 3-5 dominant clinical risk drivers"
    )
    narrative_explanation: str = Field(
        ...,
        description="Patient-friendly clinical synthesis explaining the root cause combination"
    )
    protective_summary: Optional[str] = Field(
        None,
        description="Recognition of protective dietary/lifestyle factors mitigating risk"
    )
    clinical_notes: str = Field(
        ...,
        description="Practitioner-oriented pathophysiological assessment with guideline references"
    )
    icd10_considerations: Optional[List[str]] = Field(
        default_factory=list,
        description="Relevant ICD-10 diagnostic codes for clinical differential workup"
    )


class NutrientExplainabilityDetail(BaseModel):
    nutrient_code: str
    nutrient: str
    risk_level: str
    probability: float
    confidence_level: str
    total_features_evaluated: int
    top_positive_factors: List[FeatureContributionItem] = Field(
        default_factory=list,
        description="Primary risk drivers that increase deficiency probability"
    )
    top_protective_factors: List[FeatureContributionItem] = Field(
        default_factory=list,
        description="Protective behaviors and factors that lower deficiency probability"
    )
    all_contributions: List[FeatureContributionItem] = Field(
        default_factory=list,
        description="Complete ranked feature attributions with contribution percentages"
    )
    waterfall_plot: Optional[WaterfallPlotData] = None
    clinical_reasoning: ClinicalReasoningSummary
    svg_chart: Optional[str] = Field(
        None,
        description="Server-rendered standalone SVG waterfall chart for direct embedding"
    )


class MultiNutrientExplainabilityResponse(BaseModel):
    assessment_id: Optional[uuid.UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_risk: str
    overall_confidence: str
    nutrients_explained: List[NutrientExplainabilityDetail] = Field(default_factory=list)
    execution_time_ms: float = Field(..., description="Latency for SHAP computation and clinical reasoning")


class RiskFactorCardItem(BaseModel):
    factor_id: str
    factor_name: str
    category: RiskFactorCategoryEnum
    severity: str = Field(..., description="CRITICAL, HIGH, MODERATE, or LOW")
    impact_score: float
    impact_magnitude: ImpactMagnitudeEnum
    direction: FactorDirectionEnum
    associated_nutrients: List[str] = Field(
        default_factory=list,
        description="Nutrients affected by this particular risk factor"
    )
    clinical_mechanism: str
    recommended_action: str
    evidence_citation: Optional[str] = None


class CategorizedRiskFactorsResponse(BaseModel):
    assessment_id: Optional[uuid.UUID] = None
    total_risk_factors_identified: int
    dietary_factors: List[RiskFactorCardItem] = Field(default_factory=list)
    lifestyle_factors: List[RiskFactorCardItem] = Field(default_factory=list)
    symptom_factors: List[RiskFactorCardItem] = Field(default_factory=list)
    medical_factors: List[RiskFactorCardItem] = Field(default_factory=list)
    supplement_factors: List[RiskFactorCardItem] = Field(default_factory=list)
    physiological_factors: List[RiskFactorCardItem] = Field(default_factory=list)


class GlobalFeatureImportanceItem(BaseModel):
    feature_name: str
    factor_name: str
    category: RiskFactorCategoryEnum
    mean_absolute_shap: float
    relative_importance_percentage: float


class GlobalFeatureImportanceResponse(BaseModel):
    model_name: str
    model_version: str
    target_nutrient: Optional[str] = "ALL_NUTRIENTS"
    top_global_drivers: List[GlobalFeatureImportanceItem] = Field(default_factory=list)
    total_population_samples_benchmarked: int
