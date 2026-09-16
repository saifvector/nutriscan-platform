"""
Population Health Analytics Schemas
Pydantic contracts for:
- Cohort Discovery & Demographic Filters
- Micronutrient Deficiency Prevalence Mapping
- Geographic & Socioeconomic Trend Analysis
- Population Risk Stratification Tiers
- Clinical Outcome Benchmarking
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CohortFilterRequest(BaseModel):
    min_age: Optional[int] = 18
    max_age: Optional[int] = 80
    gender: Optional[str] = "ALL"  # ALL, FEMALE, MALE
    dietary_pattern: Optional[str] = "ALL"  # ALL, OMNIVORE, VEGETARIAN, VEGAN, KETO, MEDITERRANEAN
    min_income_pir: Optional[float] = None
    max_income_pir: Optional[float] = None
    symptom_filter: Optional[str] = None
    geographic_region: Optional[str] = "ALL"


class CohortSummary(BaseModel):
    cohort_id: str
    cohort_name: str
    sample_size: int
    matching_percentage: float
    mean_age: float
    female_percentage: float
    mean_bmi: float
    top_deficiency_risks: List[Dict[str, Any]]
    average_vulnerability_score: float = Field(ge=0.0, le=100.0)


class PrevalenceDataPoint(BaseModel):
    nutrient: str
    national_prevalence_pct: float
    high_risk_subgroup_pct: float
    primary_vulnerable_demographic: str
    socioeconomic_gradient_p_val: float
    regional_variance_index: float


class GeographicRegionData(BaseModel):
    region_id: str
    region_name: str
    population_size: int
    overall_vulnerability_index: float
    highest_deficiency_nutrient: str
    highest_deficiency_prevalence_pct: float
    sunlight_insolation_kwh: float
    poverty_ratio_pct: float


class RiskStratificationDistribution(BaseModel):
    critical_risk_pct: float
    high_risk_pct: float
    moderate_risk_pct: float
    low_risk_pct: float
    population_total: int
    demographic_disparities: List[Dict[str, Any]]
    projected_annual_avoidable_morbidity_usd: float
