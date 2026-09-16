"""
Research Intelligence API Router
Exposes enterprise endpoints for:
- /api/v1/research/evidence
- /api/v1/research/guidelines
- /api/v1/research/contradictions
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    ResearchEvidenceReport,
    EvidenceQueryRequest,
    GuidelineComparison,
    ContradictionAlert
)
from .service import ResearchService

router = APIRouter(prefix="/research", tags=["Research Intelligence Engine"])


@router.post("/evidence", response_model=ResearchEvidenceReport)
async def query_research_evidence(request: EvidenceQueryRequest):
    """
    Retrieves aggregated clinical evidence, computes freshness scores,
    cross-references international guidelines, and evaluates biochemical contradictions.
    """
    try:
        return ResearchService.get_evidence_report(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research evidence retrieval error: {str(e)}"
        )


@router.get("/guidelines", response_model=List[GuidelineComparison])
async def get_comparative_guidelines(nutrient: str = "Vitamin D"):
    """
    Compares recommendations and upper intake bounds from WHO, NIH ODS,
    ESPEN, and The Endocrine Society for the specified nutrient.
    """
    try:
        return ResearchService.get_guidelines_comparison(nutrient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guideline comparison error: {str(e)}"
        )


@router.get("/contradictions", response_model=List[ContradictionAlert])
async def check_clinical_contradictions(nutrient: str = "Vitamin D"):
    """
    Identifies competitive absorption conflicts, drug-nutrient contraindications,
    and adverse interaction warnings with clinical mitigation strategies.
    """
    try:
        return ResearchService.get_contradictions(nutrient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contradiction detection error: {str(e)}"
        )
