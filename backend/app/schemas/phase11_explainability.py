"""
Phase 11: Explainable AI, Clinical Reasoning & Evidence Engine Schemas
Data Transfer Objects (DTOs) for:
- Prediction Explainability & SHAP Attribution (Positive vs Protective Partitioning)
- Dual-Layer Clinical Reasoning Narratives (Patient & Clinician Perspectives)
- Clinical Evidence & Source Traceability (NIH ODS, USDA FDC, NHANES, NIH DSID)
- Nutrient Interaction Reasoning & Biochemical Mechanisms
- What-If Clinical Risk Simulation & Trajectory Forecasting
- Recommendation Rationale & Evidence Linking
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class FactorDirection(str, Enum):
    POSITIVE = "POSITIVE"     # Risk-elevating factor
    PROTECTIVE = "PROTECTIVE" # Risk-reducing / protective factor


class EvidenceGrade(str, Enum):
    GRADE_A = "Grade A"  # Meta-analyses, Cochrane, RCTs, National Academy of Medicine DRIs
    GRADE_B = "Grade B"  # Prospective cohort studies (NHANES, Nurses' Health Study)
    GRADE_C = "Grade C"  # Observational, clinical consensus, mechanistic studies


class InteractionType(str, Enum):
    SYNERGISTIC_ABSORPTION = "SYNERGISTIC_ABSORPTION"
    ANTAGONISTIC_COMPETITION = "ANTAGONISTIC_COMPETITION"
    ENZYMATIC_DEPENDENCY = "ENZYMATIC_DEPENDENCY"
    METABOLIC_INTERDEPENDENCE = "METABOLIC_INTERDEPENDENCE"
    ELECTROLYTE_HOMEOSTASIS = "ELECTROLYTE_HOMEOSTASIS"


class ContributionFactor(BaseModel):
    """Individual feature attribution item with contribution metrics."""
    feature: str = Field(..., description="Canonical feature name in 105-variable NHANES matrix")
    label: str = Field(..., description="Human-readable feature description")
    category: str = Field(..., description="Dietary, Lifestyle, Examination, Demographic, or Symptom")
    value: Optional[Any] = Field(default=None, description="Observed or imputed patient value")
    impact: float = Field(..., description="Signed directional SHAP attribution value")
    contribution_pct: float = Field(..., ge=0.0, le=100.0, description="Normalized attribution percentage of total variance")
    direction: FactorDirection = Field(..., description="POSITIVE (elevates risk) or PROTECTIVE (mitigates risk)")


class ClinicalNarrative(BaseModel):
    """Dual-layer narrative explanation tailored to patient and clinician audiences."""
    patient_explanation: str = Field(..., description="Clear, plain-English summary avoiding medical jargon")
    clinician_evaluation: str = Field(..., description="Physician-grade pathophysiological analysis with biomarker correlations")
    icd10_codes: List[str] = Field(default_factory=list, description="Relevant ICD-10 differential diagnosis codes")
    confirmatory_labs: str = Field(..., description="Recommended venous blood test panel to confirm status")
    guideline_reference: str = Field(..., description="Primary clinical society practice guideline")


class TargetExplanation(BaseModel):
    """Comprehensive explainability breakdown for a single deficiency target."""
    target: str = Field(..., description="Deficiency target key, e.g. target_iron_deficiency")
    target_name: str = Field(..., description="Clinical target name, e.g. Iron Deficiency")
    champion_algorithm: str = Field(..., description="Production champion model algorithm")
    calibrated_probability: float = Field(..., ge=0.0, le=1.0, description="Platt-scaled empirical risk probability")
    risk_tier: str = Field(..., description="LOW, MODERATE, or HIGH")
    optimal_threshold: float = Field(..., description="Calibrated clinical decision cutoff")
    positive_contributors: List[ContributionFactor] = Field(default_factory=list, description="Top factors elevating risk")
    protective_contributors: List[ContributionFactor] = Field(default_factory=list, description="Top factors providing protection")
    narratives: ClinicalNarrative = Field(..., description="Dual-perspective clinical narrative")


class PredictionExplanationResponse(BaseModel):
    """Full explainability response for a screening session across all flagged and evaluated targets."""
    prediction_id: uuid.UUID = Field(..., description="Assessment / prediction session UUID")
    timestamp: datetime = Field(..., description="UTC timestamp of analysis")
    overall_risk_tier: str = Field(..., description="Overall highest risk tier")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="0-100 composite risk score")
    explanations: List[TargetExplanation] = Field(..., description="Detailed explanations per target")


class EvidenceItem(BaseModel):
    """Validated scientific citation linking clinical recommendations to primary research."""
    nutrient: str = Field(..., description="Target nutrient or deficiency name")
    evidence_title: str = Field(..., description="Study or guideline title")
    evidence_source: str = Field(..., description="NIH ODS, USDA FoodData Central, NHANES, or NIH DSID")
    evidence_strength: EvidenceGrade = Field(..., description="Grade A, Grade B, or Grade C")
    reference_url: str = Field(..., description="Direct link to source database or PubMed")
    pmid_or_fdc_id: Optional[str] = Field(default=None, description="PubMed ID or USDA FoodData Central ID")
    study_type: str = Field(..., description="RCT, Systematic Review, Epidemiological Cohort, or DRI Guideline")
    key_findings: str = Field(..., description="Concise clinical takeaways and biochemical summary")
    recommended_daily_intake: str = Field(..., description="Sex/age appropriate clinical reference intake")
    tolerable_upper_limit: Optional[str] = Field(default=None, description="Tolerable Upper Intake Level (UL) toxicity boundary")


class EvidenceSummaryResponse(BaseModel):
    """Catalog of primary scientific citations and evidence bases."""
    total_citations: int = Field(..., description="Total evidence records compiled")
    evidence_items: List[EvidenceItem] = Field(..., description="List of evidence citations")


class NutrientInteractionItem(BaseModel):
    """Biochemical nutrient-nutrient or nutrient-food interaction."""
    nutrient_a: str = Field(..., description="Primary nutrient")
    nutrient_b: str = Field(..., description="Interacting nutrient or substance")
    interaction_type: InteractionType = Field(..., description="Mechanistic classification")
    description: str = Field(..., description="Pathophysiological interaction summary")
    biochemical_mechanism: str = Field(..., description="Molecular / transporter mechanism details")
    synergy_multiplier: float = Field(default=1.0, description="Risk modulation multiplier")
    clinical_action: str = Field(..., description="Physician and dietitian actionable advice")
    timing_advice: str = Field(..., description="Practical meal and supplement scheduling guidance")


class NutrientInteractionsResponse(BaseModel):
    """Complete catalog of active biochemical interactions."""
    total_interactions: int = Field(..., description="Count of interaction rules")
    interactions: List[NutrientInteractionItem] = Field(..., description="Interaction catalog")


class WhatIfSimulationRequest(BaseModel):
    """Input payload for simulating prospective nutritional or lifestyle interventions."""
    base_assessment: Dict[str, Any] = Field(..., description="Current baseline patient assessment payload")
    dietary_modifications: Optional[Dict[str, float]] = Field(
        default=None,
        description="Hypothetical changes in daily dietary intake, e.g. {'diet_iron_mg': 22.0, 'daily_fruit_vegetable_servings': 4}"
    )
    supplement_additions: Optional[Dict[str, float]] = Field(
        default=None,
        description="Hypothetical supplemental additions, e.g. {'supp_vitamin_d_mcg': 50.0, 'supp_iron_mg': 18.0}"
    )
    lifestyle_modifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Hypothetical lifestyle updates, e.g. {'sunlight_exposure_min_per_day': 30, 'sleep_hours_per_night': 8.0, 'stress_level': 4}"
    )


class TargetSimulationComparison(BaseModel):
    """Before vs. after comparison for a single clinical target."""
    target: str = Field(..., description="Target identifier")
    target_name: str = Field(..., description="Clinical target name")
    baseline_probability: float = Field(..., description="Calibrated probability before intervention")
    simulated_probability: float = Field(..., description="Calibrated probability after intervention")
    probability_delta: float = Field(..., description="Simulated minus baseline probability")
    baseline_tier: str = Field(..., description="Baseline risk tier (LOW, MODERATE, HIGH)")
    simulated_tier: str = Field(..., description="Simulated risk tier after intervention")
    tier_improved: bool = Field(..., description="True if risk tier decreased in severity")


class WhatIfSimulationResponse(BaseModel):
    """Response payload detailing the projected impact of simulated interventions."""
    baseline_risk_score: float = Field(..., description="Baseline overall risk score (0-100)")
    simulated_risk_score: float = Field(..., description="Projected overall risk score (0-100)")
    risk_score_delta: float = Field(..., description="Simulated minus baseline score (negative = improvement)")
    deficiencies_resolved_count: int = Field(..., description="Number of targets transitioning from HIGH/MODERATE to LOW")
    target_comparisons: List[TargetSimulationComparison] = Field(..., description="Per-target delta comparisons")
    projected_timeline: str = Field(..., description="Estimated timeframe to achieve biological normalization")
    summary_narrative: str = Field(..., description="Clinical synthesis of projected benefits")


class RecommendationRationaleItem(BaseModel):
    """Traceable clinical rationale linking an intervention to prediction and evidence."""
    recommendation_id: uuid.UUID = Field(..., description="Unique recommendation ID")
    food_or_protocol: str = Field(..., description="Food item or lifestyle protocol name")
    target_nutrient: str = Field(..., description="Addressed deficiency or nutrient")
    triggering_prediction_id: Optional[uuid.UUID] = Field(default=None, description="Linked assessment UUID")
    triggering_risk_tier: str = Field(..., description="Patient risk tier that triggered this item")
    evidence_source: str = Field(..., description="Primary citation authority (e.g. USDA / NIH ODS)")
    evidence_strength: EvidenceGrade = Field(..., description="Grade A, B, or C")
    reference_url: str = Field(..., description="Direct citation link")
    clinical_rationale: str = Field(..., description="Why this item was selected")
    expected_outcome: str = Field(..., description="Anticipated physiological or biomarker improvement")


class RecommendationRationaleResponse(BaseModel):
    """Complete traceable rationale package for all active recommendations."""
    total_recommendations: int = Field(..., description="Total items evaluated")
    recommendations: List[RecommendationRationaleItem] = Field(..., description="Traceable recommendation list")
