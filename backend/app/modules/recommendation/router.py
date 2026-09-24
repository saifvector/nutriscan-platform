"""
FastAPI Personalized Nutrition Recommendation Router
Phase 5: Personalized Nutrition Recommendation Engine

Endpoints:
- GET /api/v1/recommendations/{assessment_id}: Complete personalized nutritional recommendation strategy
- GET /api/v1/recommendations/{assessment_id}/foods: Filtered and ranked foods (Priority 1, 2, 3)
- GET /api/v1/recommendations/{assessment_id}/lifestyle: Targeted lifestyle, hydration, sleep, and activity protocols
- GET /api/v1/recommendations/{assessment_id}/recovery-plan: Phased 7-Day, 14-Day, and 30-Day recovery roadmap
"""

from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Path, Depends

from .service import RecommendationService
from ...schemas.recommendation import (
    PersonalizedRecommendationsResponse,
    FoodRecommendationsResponse,
    LifestyleRecommendationsResponse,
    RecoveryPlanResponse
)
from ...core.auth import get_current_user_optional, verify_resource_ownership, AuthenticatedUser
from ...core.persistence import PersistenceRepository

router = APIRouter(prefix="/recommendations", tags=["Personalized Nutrition Recommendations"])


def _check_recommendation_ownership(assessment_id: Optional[str], current_user: Optional[AuthenticatedUser]):
    if current_user and assessment_id:
        owner_id = PersistenceRepository.get_assessment_owner(str(assessment_id))
        if owner_id:
            verify_resource_ownership(
                current_user=current_user,
                resource_user_id=owner_id,
                resource_id=str(assessment_id),
                resource_type="recommendation"
            )


@router.get(
    "",
    response_model=PersonalizedRecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Personalized Nutrition Recommendations via Query Param",
    description="Generates dietary guidance, synergistic pairings, and safety evaluation for given assessment_id query param."
)
async def get_personalized_recommendations_query(
    assessment_id: Optional[str] = None,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        _check_recommendation_ownership(assessment_id, current_user)
        return RecommendationService.get_recommendations(assessment_id=assessment_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalized recommendation generation failed: {str(e)}"
        )


@router.get(
    "/{assessment_id}",
    response_model=PersonalizedRecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Full Personalized Nutrition Recommendations",
    description="Generates end-to-end dietary guidance, synergistic food pairings, lifestyle interventions, recovery milestones, and recommendation scores."
)
async def get_personalized_recommendations(
    assessment_id: str = Path(..., min_length=1, max_length=64, description="Unique assessment ID"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        _check_recommendation_ownership(assessment_id, current_user)
        return RecommendationService.get_recommendations(assessment_id=assessment_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalized recommendation generation failed: {str(e)}"
        )


@router.get(
    "/{assessment_id}/foods",
    response_model=FoodRecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ranked Food Recommendations by Priority Tier",
    description="Returns diet-compatible foods partitioned into Priority 1 (Powerhouse Staples), Priority 2 (Core Supportive), and Priority 3 (Rotation)."
)
async def get_food_recommendations(
    assessment_id: str = Path(..., min_length=1, max_length=64, description="Unique assessment ID"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        _check_recommendation_ownership(assessment_id, current_user)
        return RecommendationService.get_food_recommendations(assessment_id=assessment_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Food recommendations retrieval failed: {str(e)}"
        )


@router.get(
    "/{assessment_id}/lifestyle",
    response_model=LifestyleRecommendationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Practical Lifestyle Interventions",
    description="Returns targeted protocols for sunlight exposure, hydration, mechanical activity, circadian sleep, and stress reduction."
)
async def get_lifestyle_recommendations(
    assessment_id: str = Path(..., min_length=1, max_length=64, description="Unique assessment ID"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        _check_recommendation_ownership(assessment_id, current_user)
        return RecommendationService.get_lifestyle_recommendations(assessment_id=assessment_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lifestyle recommendations retrieval failed: {str(e)}"
        )


@router.get(
    "/{assessment_id}/recovery-plan",
    response_model=RecoveryPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 7-Day, 14-Day, and 30-Day Nutrient Recovery Plan",
    description="Returns phased milestone roadmap with specific daily dietary strategies, checklists, and habit consolidation targets."
)
async def get_recovery_plan(
    assessment_id: str = Path(..., min_length=1, max_length=64, description="Unique assessment ID"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        _check_recommendation_ownership(assessment_id, current_user)
        return RecommendationService.get_recovery_plan(assessment_id=assessment_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recovery plan retrieval failed: {str(e)}"
        )
