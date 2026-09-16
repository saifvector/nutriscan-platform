"""
Population Health Analytics API Router
Exposes enterprise endpoints for:
- /api/v1/population/cohorts
- /api/v1/population/prevalence
- /api/v1/population/regions
- /api/v1/population/stratification
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    CohortFilterRequest,
    CohortSummary,
    PrevalenceDataPoint,
    GeographicRegionData,
    RiskStratificationDistribution
)
from .service import PopulationService

router = APIRouter(prefix="/population", tags=["Population Health Analytics"])


@router.post("/cohorts", response_model=CohortSummary)
async def discover_population_cohort(request: CohortFilterRequest):
    """
    Filters synthetic national cohorts by Age, Sex, Diet, and Poverty Income Ratio (PIR),
    returning cohort size, demographic averages, and collective vulnerability scores.
    """
    try:
        return PopulationService.discover_cohort(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cohort discovery error: {str(e)}"
        )


@router.get("/prevalence", response_model=List[PrevalenceDataPoint])
async def get_national_micronutrient_prevalence():
    """
    Retrieves macro-level epidemiological prevalence rates across key micronutrients,
    including high-risk subgroup rates and socioeconomic disparity gradients.
    """
    try:
        return PopulationService.get_prevalence_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prevalence data retrieval error: {str(e)}"
        )


@router.get("/regions", response_model=List[GeographicRegionData])
async def get_regional_deficiency_mapping():
    """
    Retrieves geographic regional statistics, sunlight insolation ratings,
    and regional top deficiency prevalence indices.
    """
    try:
        return PopulationService.get_geographic_regions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Regional mapping retrieval error: {str(e)}"
        )


@router.get("/stratification", response_model=RiskStratificationDistribution)
async def get_population_risk_stratification():
    """
    Returns population-wide risk stratification tiers (Critical, High, Moderate, Low),
    subgroup disparity ratios, and avoidable morbidity burden projections.
    """
    try:
        return PopulationService.get_risk_stratification()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk stratification retrieval error: {str(e)}"
        )
