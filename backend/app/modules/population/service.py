"""
Population Health Analytics Service Facade
Provides centralized querying for cohorts, geographic prevalence, and population risk stratification.
"""

from typing import List, Dict, Any
from .schemas import (
    CohortFilterRequest,
    CohortSummary,
    PrevalenceDataPoint,
    GeographicRegionData,
    RiskStratificationDistribution
)
from .cohort_engine import CohortDiscoveryEngine
from .prevalence_mapper import PrevalenceMapperEngine
from .stratification_engine import RiskStratificationEngine


class PopulationService:
    """Service facade for Population Health Analytics."""

    @classmethod
    def discover_cohort(cls, request: CohortFilterRequest) -> CohortSummary:
        return CohortDiscoveryEngine.discover_cohort(request)

    @classmethod
    def get_prevalence_data(cls) -> List[PrevalenceDataPoint]:
        return PrevalenceMapperEngine.get_national_prevalence()

    @classmethod
    def get_geographic_regions(cls) -> List[GeographicRegionData]:
        return PrevalenceMapperEngine.get_geographic_regions()

    @classmethod
    def get_risk_stratification(cls) -> RiskStratificationDistribution:
        return RiskStratificationEngine.get_stratification()
