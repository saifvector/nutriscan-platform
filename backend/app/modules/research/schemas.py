"""
Research Intelligence Engine Schemas
Pydantic contracts for:
- Clinical Evidence Items & Citations
- Freshness & Methodological Quality Weights
- Comparative International Guidelines (WHO, NIH, ESPEN, Endocrine Society)
- Scientific Contradiction Alerts & Mitigations
- GRADE Recommendation Confidence
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EvidenceItem(BaseModel):
    evidence_id: str
    target_nutrient: str
    study_title: str
    journal: str
    publication_year: int
    study_type: str  # META_ANALYSIS, SYSTEMATIC_REVIEW, RCT, PROSPECTIVE_COHORT, OBSERVATIONAL
    sample_size: int
    doi_or_pmid: str
    key_findings: str
    effect_size_cohens_d: float
    p_value: float
    freshness_score: float = Field(ge=0.0, le=1.0)
    methodological_weight: float = Field(ge=0.0, le=1.0)
    grade_rating: str  # HIGH, MODERATE, LOW, VERY_LOW


class GuidelineComparison(BaseModel):
    nutrient_or_topic: str
    organization: str  # WHO, NIH_ODS, ESPEN, ENDOCRINE_SOCIETY, EFSA
    recommended_daily_target: str
    upper_tolerable_limit: str
    therapeutic_indication: str
    evidence_strength: str
    guideline_year: int
    concordance_with_nutriscan: str  # ALIGNED, ADAPTIVE_ENHANCEMENT, DIVERGENT


class ContradictionAlert(BaseModel):
    contradiction_id: str
    severity: str  # HIGH, MODERATE, ADVISORY
    nutrient_a: str
    nutrient_b_or_factor: str
    biochemical_mechanism: str
    potential_harm: str
    mitigation_strategy: str
    supporting_citation: str


class ResearchEvidenceReport(BaseModel):
    query_nutrient: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_confidence_score: float = Field(ge=0.0, le=1.0)
    overall_grade_rating: str
    average_freshness_score: float = Field(ge=0.0, le=1.0)
    evidence_items: List[EvidenceItem]
    guideline_comparisons: List[GuidelineComparison]
    contradiction_alerts: List[ContradictionAlert]
    executive_synthesis: str


class EvidenceQueryRequest(BaseModel):
    nutrient: str = "Vitamin D"
    include_contradictions: bool = True
    min_year: int = 2018
