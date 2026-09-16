"""
Clinical Trial Simulation API Router
Exposes enterprise endpoints for:
- /api/v1/trials/simulate
- /api/v1/trials/power-analysis
"""

from fastapi import APIRouter, HTTPException, status
from .schemas import (
    TrialSimulationRequest,
    ClinicalTrialSimulationResult,
    StatisticalPowerAnalysis
)
from .service import TrialService

router = APIRouter(prefix="/trials", tags=["Clinical Trial Simulation Framework"])


@router.post("/simulate", response_model=ClinicalTrialSimulationResult)
async def simulate_clinical_trial(request: TrialSimulationRequest):
    """
    Executes an in-silico randomized controlled trial comparing Placebo/Control,
    Standard Care, and NutriScan Precision Intervention arms across multi-week
    biomarker trajectories with adherence decay modeling.
    """
    try:
        return TrialService.simulate_trial(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trial simulation error: {str(e)}"
        )


@router.post("/power-analysis", response_model=StatisticalPowerAnalysis)
async def perform_statistical_power_analysis(
    target_nutrient: str = "Vitamin D",
    sample_size_per_arm: int = 100,
    mean_control: float = 24.5,
    mean_intervention: float = 36.4,
    pooled_std: float = 5.0
):
    """
    Calculates statistical power (1 - beta), Cohen's d effect size,
    and minimal required sample size for clinical superiority.
    """
    try:
        return TrialService.analyze_power(
            target_nutrient=target_nutrient,
            sample_size_per_arm=sample_size_per_arm,
            mean_control=mean_control,
            mean_intervention=mean_intervention,
            pooled_std=pooled_std
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statistical power analysis error: {str(e)}"
        )
