"""
Clinical Trial Simulation Service Facade
Centralizes in-silico randomized trial simulation and statistical power analysis.
"""

from typing import List
from .schemas import (
    TrialSimulationRequest,
    ClinicalTrialSimulationResult,
    StatisticalPowerAnalysis
)
from .simulation_engine import TrialSimulationEngine
from .power_calculator import PowerCalculatorEngine


class TrialService:
    """Service facade for the Clinical Trial Simulation Framework."""

    @classmethod
    def simulate_trial(cls, request: TrialSimulationRequest) -> ClinicalTrialSimulationResult:
        return TrialSimulationEngine.run_simulation(request)

    @classmethod
    def analyze_power(
        cls,
        target_nutrient: str = "Vitamin D",
        sample_size_per_arm: int = 100,
        mean_control: float = 24.5,
        mean_intervention: float = 36.4,
        pooled_std: float = 5.0
    ) -> StatisticalPowerAnalysis:
        return PowerCalculatorEngine.calculate_power(
            target_nutrient=target_nutrient,
            sample_size_per_arm=sample_size_per_arm,
            mean_control=mean_control,
            mean_intervention=mean_intervention,
            pooled_std=pooled_std
        )
