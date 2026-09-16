"""
Micronutrient Prevalence & Geographic Mapping Engine
Maps macro-level national prevalence, demographic disparity gradients,
and geographic vulnerability indices.
"""

from typing import List, Dict, Any
from .schemas import PrevalenceDataPoint, GeographicRegionData


NATIONAL_PREVALENCE_DATABASE: List[Dict[str, Any]] = [
    {
        "nutrient": "Vitamin D",
        "national_prevalence_pct": 41.6,
        "high_risk_subgroup_pct": 68.2,
        "primary_vulnerable_demographic": "Higher latitudes (>40 N), dark pigmentation, sedentary indoor workers",
        "socioeconomic_gradient_p_val": 0.001,
        "regional_variance_index": 1.45
    },
    {
        "nutrient": "Iron",
        "national_prevalence_pct": 18.5,
        "high_risk_subgroup_pct": 34.8,
        "primary_vulnerable_demographic": "Premenopausal females, pregnant women, plant-based diets",
        "socioeconomic_gradient_p_val": 0.0004,
        "regional_variance_index": 1.28
    },
    {
        "nutrient": "Magnesium",
        "national_prevalence_pct": 52.4,
        "high_risk_subgroup_pct": 69.1,
        "primary_vulnerable_demographic": "High processed-food consumers, type 2 diabetics, chronic alcohol intake",
        "socioeconomic_gradient_p_val": 0.0001,
        "regional_variance_index": 1.15
    },
    {
        "nutrient": "Vitamin B12",
        "national_prevalence_pct": 14.8,
        "high_risk_subgroup_pct": 42.0,
        "primary_vulnerable_demographic": "Adults >60y (atrophic gastritis), metformin/PPI users, strict vegans",
        "socioeconomic_gradient_p_val": 0.021,
        "regional_variance_index": 1.12
    },
    {
        "nutrient": "Zinc",
        "national_prevalence_pct": 22.7,
        "high_risk_subgroup_pct": 38.5,
        "primary_vulnerable_demographic": "Elderly populations, high grain phytate diets, vegetarian cohorts",
        "socioeconomic_gradient_p_val": 0.005,
        "regional_variance_index": 1.18
    },
    {
        "nutrient": "Folate (B9)",
        "national_prevalence_pct": 8.4,
        "high_risk_subgroup_pct": 21.0,
        "primary_vulnerable_demographic": "Women of childbearing age, low green vegetable intake",
        "socioeconomic_gradient_p_val": 0.0002,
        "regional_variance_index": 1.32
    }
]

GEOGRAPHIC_REGIONS_DATABASE: List[Dict[str, Any]] = [
    {
        "region_id": "REG-NE",
        "region_name": "Northeast & Mid-Atlantic",
        "population_size": 57000000,
        "overall_vulnerability_index": 62.4,
        "highest_deficiency_nutrient": "Vitamin D",
        "highest_deficiency_prevalence_pct": 54.2,
        "sunlight_insolation_kwh": 3.8,
        "poverty_ratio_pct": 11.8
    },
    {
        "region_id": "REG-MW",
        "region_name": "Upper Midwest & Great Lakes",
        "population_size": 68000000,
        "overall_vulnerability_index": 68.1,
        "highest_deficiency_nutrient": "Vitamin D",
        "highest_deficiency_prevalence_pct": 58.7,
        "sunlight_insolation_kwh": 3.5,
        "poverty_ratio_pct": 12.4
    },
    {
        "region_id": "REG-SE",
        "region_name": "Southeast & Gulf Coast",
        "population_size": 95000000,
        "overall_vulnerability_index": 64.8,
        "highest_deficiency_nutrient": "Magnesium",
        "highest_deficiency_prevalence_pct": 59.4,
        "sunlight_insolation_kwh": 5.2,
        "poverty_ratio_pct": 16.5
    },
    {
        "region_id": "REG-SW",
        "region_name": "Southwest & Sunbelt",
        "population_size": 42000000,
        "overall_vulnerability_index": 44.2,
        "highest_deficiency_nutrient": "Iron",
        "highest_deficiency_prevalence_pct": 22.1,
        "sunlight_insolation_kwh": 6.4,
        "poverty_ratio_pct": 13.9
    },
    {
        "region_id": "REG-PNW",
        "region_name": "Pacific Northwest",
        "population_size": 15000000,
        "overall_vulnerability_index": 67.5,
        "highest_deficiency_nutrient": "Vitamin D",
        "highest_deficiency_prevalence_pct": 61.3,
        "sunlight_insolation_kwh": 3.4,
        "poverty_ratio_pct": 10.5
    }
]


class PrevalenceMapperEngine:
    """Engine responsible for macro-prevalence and regional geographic statistics."""

    @classmethod
    def get_national_prevalence(cls) -> List[PrevalenceDataPoint]:
        return [PrevalenceDataPoint(**p) for p in NATIONAL_PREVALENCE_DATABASE]

    @classmethod
    def get_geographic_regions(cls) -> List[GeographicRegionData]:
        return [GeographicRegionData(**r) for r in GEOGRAPHIC_REGIONS_DATABASE]
