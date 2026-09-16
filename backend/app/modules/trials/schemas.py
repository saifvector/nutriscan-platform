"""
Clinical Trial Simulation Framework Schemas
Pydantic contracts for:
- Synthetic Patient Cohorts
- In-Silico Randomized Controlled Trial Design
- Longitudinal Intervention Arms (Control, Standard, Precision NutriScan)
- Adherence Decay Modeling
- Statistical Power & Sample Size Estimation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SyntheticPatient(BaseModel):
    subject_id: str
    age: int
    gender: str
    bmi: float
    dietary_pattern: str
    baseline_biomarker_value: float  # e.g., 25-OH D in ng/mL or Ferritin in ng/mL
    baseline_deficiency_probability: float
    assigned_arm: str  # CONTROL_PLACEBO, STANDARD_CARE, NUTRISCAN_PRECISION


class TrialArmTrajectory(BaseModel):
    arm_name: str
    arm_description: str
    sample_size: int
    adherence_rate_pct: float
    trajectory_weeks: List[int]  # [0, 4, 8, 12, 16, 24]
    mean_biomarker_trajectory: List[float]
    confidence_lower_95: List[float]
    confidence_upper_95: List[float]
    normalization_rate_pct: float  # Percentage of subjects reaching sufficiency


class StatisticalPowerAnalysis(BaseModel):
    target_nutrient: str
    sample_size_per_arm: int
    alpha_significance: float = 0.05
    effect_size_cohens_d: float
    calculated_statistical_power: float = Field(ge=0.0, le=1.0)
    p_value: float
    recommended_min_sample_size: int
    clinical_superiority_confirmed: bool


class ClinicalTrialSimulationResult(BaseModel):
    simulation_id: str
    target_nutrient: str
    total_subjects: int
    trial_duration_weeks: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    trial_arms: List[TrialArmTrajectory]
    power_analysis: StatisticalPowerAnalysis
    executive_conclusion: str


class TrialSimulationRequest(BaseModel):
    target_nutrient: str = "Vitamin D"
    cohort_size: int = Field(default=300, ge=30, le=5000)
    trial_duration_weeks: int = Field(default=12, ge=4, le=24)
    adherence_decay_factor: float = Field(default=0.85, ge=0.5, le=1.0)
