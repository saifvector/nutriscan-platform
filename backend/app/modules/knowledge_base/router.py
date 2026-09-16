"""
Clinical Knowledge Base Router
Phase 7A: Nutrient Expansion & Clinical Knowledge Base Enhancement
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
import logging

from .schemas import ClinicalNutrientProfile, NutrientListResponse
from .registry import ClinicalKnowledgeBaseService, CLINICAL_NUTRIENT_REGISTRY
from ...ml.constants import NUTRIENT_INTERACTIONS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/knowledge-base",
    tags=["Clinical Knowledge Base"]
)


@router.get(
    "/interactions",
    summary="Get All Known Biochemical Nutrient Interactions",
    description="Returns full catalog of synergistic, antagonistic, and dependency interactions across monitored nutrients."
)
def list_interactions():
    return {
        "total_interactions": len(NUTRIENT_INTERACTIONS),
        "interactions": NUTRIENT_INTERACTIONS
    }


@router.get(
    "/nutrients",
    response_model=NutrientListResponse,
    summary="Get All 18 Monitored Nutrient Profiles",
    description="Returns full clinical monographs for all 18 nutrients with RDA, UL, WHO/NIH references, and symptoms."
)
def list_all_nutrients(
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'Water-Soluble Vitamin')")
):
    all_nutrients = ClinicalKnowledgeBaseService.get_all_nutrients()
    if category:
        all_nutrients = [n for n in all_nutrients if category.lower() in n.get("category", "").lower()]
    return {
        "total_nutrients": len(all_nutrients),
        "nutrients": all_nutrients
    }


@router.get(
    "/nutrients/{code}",
    response_model=ClinicalNutrientProfile,
    summary="Get Detailed Monograph for a Specific Nutrient",
    description="Lookup clinical profile by canonical code (e.g. 'VITAMIN_B1', 'POTASSIUM', 'IODINE', 'SELENIUM')."
)
def get_nutrient_detail(
    code: str = Path(..., description="Canonical nutrient code, e.g. 'VITAMIN_B1', 'POTASSIUM', 'IODINE'")
):
    profile = ClinicalKnowledgeBaseService.get_nutrient_by_code(code)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Nutrient '{code}' not found in the Clinical Knowledge Base. Monitored codes: {list(CLINICAL_NUTRIENT_REGISTRY.keys())}"
        )
    return profile
