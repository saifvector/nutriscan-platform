"""
Clinical Knowledge Base Schemas
Phase 7A: Nutrient Expansion & Clinical Knowledge Base Enhancement
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DietaryIntakeRef(BaseModel):
    standard_adult_male: str = Field(..., description="RDA or AI for adult males")
    standard_adult_female: str = Field(..., description="RDA or AI for adult females")
    pregnancy_lactation: Optional[str] = Field(None, description="RDA/AI during pregnancy or lactation")
    tolerable_upper_limit: Optional[str] = Field(None, description="Tolerable Upper Intake Level (UL)")


class EvidenceCitations(BaseModel):
    who_reference: str = Field(..., description="World Health Organization guideline or technical monograph")
    nih_reference: str = Field(..., description="NIH Office of Dietary Supplements Fact Sheet reference")
    additional_guidelines: Optional[List[str]] = Field(default_factory=list, description="EFSA, Endocrine Society, or IOM guidelines")


class ClinicalNutrientProfile(BaseModel):
    nutrient_code: str = Field(..., description="Canonical nutrient code, e.g. VITAMIN_B1")
    common_name: str = Field(..., description="Common display name, e.g. Vitamin B1 (Thiamine)")
    category: str = Field(..., description="'Water-Soluble Vitamin', 'Fat-Soluble Vitamin', 'Macromineral', 'Trace Mineral', 'Macronutrient'")
    active_vitamers: List[str] = Field(..., description="Active biochemical vitamers or physiological forms")
    clinical_role: str = Field(..., description="Primary biological role and physiological pathway involvement")
    daily_recommended_intake: DietaryIntakeRef
    toxicity_limits: str = Field(..., description="Upper limit / hypervitaminosis or toxicity clinical consequences")
    deficiency_symptoms: List[str] = Field(..., description="Manifestation symptoms of deficiency")
    high_risk_populations: List[str] = Field(..., description="Demographic and clinical cohorts at elevated vulnerability")
    key_dietary_sources: List[str] = Field(..., description="Whole food sources with high nutrient density")
    absorption_enhancers: List[str] = Field(..., description="Nutrient and dietary factors that improve bioavailability")
    absorption_inhibitors: List[str] = Field(..., description="Antinutrients, pharmaceutical agents, or dietary inhibitors")
    citations: EvidenceCitations


class NutrientListResponse(BaseModel):
    total_nutrients: int = Field(..., description="Total monitored nutrients (18)")
    nutrients: List[ClinicalNutrientProfile]
