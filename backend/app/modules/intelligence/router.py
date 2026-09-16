"""
Nutrition Intelligence & Clinical Decision API Router
Phase 8: Nutrition Intelligence & Clinical Decision Engine

Exposes high-performance REST APIs:
- GET  /api/v1/intelligence/gaps
- GET  /api/v1/intelligence/meals
- GET  /api/v1/intelligence/substitutions
- GET  /api/v1/intelligence/supplements
- GET  /api/v1/intelligence/projections
- GET  /api/v1/intelligence/action-plan
- POST /api/v1/intelligence/generate-plan
"""

from typing import List, Optional
from fastapi import APIRouter, Query

from .schemas import (
    NutrientGapAnalysisResponse,
    MealIntelligenceResponse,
    MealPlanRequest,
    FoodSubstitutionsResponse,
    SupplementIntelligenceResponse,
    RecoveryProjectionResponse,
    ClinicalDecisionResponse,
    GenerateIntelligencePlanRequest,
    GenerateIntelligencePlanResponse
)
from .service import NutritionIntelligenceService

router = APIRouter(prefix="/intelligence", tags=["Nutrition Intelligence"])


@router.get(
    "/gaps",
    response_model=NutrientGapAnalysisResponse,
    summary="Nutrient Gap Analysis",
    description="Calculates estimated daily intake vs RDA/AI/UL reference values and evaluates adequacy percentages."
)
async def get_nutrient_gaps(
    assessment_id: Optional[str] = Query(None, description="Assessment ID (or 'demo')"),
    gender: Optional[str] = Query("FEMALE", description="Biological sex for RDA calibration (MALE / FEMALE)")
):
    return NutritionIntelligenceService.get_nutrient_gaps(assessment_id=assessment_id, gender=gender)


@router.get(
    "/meals",
    response_model=MealIntelligenceResponse,
    summary="Personalized Meal Intelligence",
    description="Generates Breakfast, Lunch, Dinner, and Snack recommendations scored by nutrient density, bioavailability, and gap efficiency."
)
async def get_meals(
    assessment_id: Optional[str] = Query(None, description="Assessment ID"),
    dietary_preference: Optional[str] = Query("OMNIVORE", description="Dietary pattern (VEGAN, VEGETARIAN, KETO, MEDITERRANEAN, etc.)"),
    budget_level: Optional[str] = Query("MODERATE", description="Budget level (BUDGET, MODERATE, PREMIUM)"),
    cuisine_preference: Optional[str] = Query("MEDITERRANEAN", description="Cuisine preference"),
    include_weekly: Optional[bool] = Query(True, description="Generate 7-day schedule with grocery list")
):
    request = MealPlanRequest(
        assessment_id=assessment_id,
        dietary_preference=dietary_preference,
        budget_level=budget_level,
        cuisine_preference=cuisine_preference,
        include_weekly=include_weekly
    )
    return NutritionIntelligenceService.get_meal_plans(request)


@router.get(
    "/substitutions",
    response_model=FoodSubstitutionsResponse,
    summary="Food Substitution Intelligence",
    description="Compares smart food swaps displaying micronutrient deltas, bioavailability shifts, and clinical tradeoffs."
)
async def get_substitutions(
    deficiencies: Optional[List[str]] = Query(None, description="Filter substitutions beneficial for specific deficiencies")
):
    return NutritionIntelligenceService.get_food_substitutions(deficiencies=deficiencies)


@router.get(
    "/supplements",
    response_model=SupplementIntelligenceResponse,
    summary="Supplement Intelligence Guidance",
    description="Provides NIH & DSID grounded supplement dosage ranges, chrono-nutrition timing, and interaction warnings."
)
async def get_supplements(
    assessment_id: Optional[str] = Query(None, description="Assessment ID"),
    deficiencies: Optional[List[str]] = Query(None, description="Specific deficiencies to target")
):
    return NutritionIntelligenceService.get_supplement_guidance(
        assessment_id=assessment_id,
        deficiencies=deficiencies
    )


@router.get(
    "/projections",
    response_model=RecoveryProjectionResponse,
    summary="Recovery Projection Simulator",
    description="Models 30-day, 60-day, and 90-day recovery trajectories, milestone checkpoints, and confidence bands."
)
async def get_projections(
    assessment_id: Optional[str] = Query(None, description="Assessment ID"),
    baseline_score: Optional[float] = Query(54.0, description="Baseline health score (0-100)"),
    deficiencies: Optional[List[str]] = Query(None, description="Detected deficiencies")
):
    return NutritionIntelligenceService.get_recovery_projections(
        assessment_id=assessment_id,
        baseline_score=baseline_score,
        deficiencies=deficiencies
    )


@router.get(
    "/action-plan",
    response_model=ClinicalDecisionResponse,
    summary="Clinical Decision Action Plan",
    description="Prioritizes interventions, fastest recovery actions, lifestyle priorities, and diagnostic laboratory tests."
)
async def get_action_plan(
    assessment_id: Optional[str] = Query(None, description="Assessment ID"),
    deficiencies: Optional[List[str]] = Query(None, description="Detected deficiencies"),
    gap_score: Optional[float] = Query(62.0, description="Nutrient gap score")
):
    return NutritionIntelligenceService.get_action_plan(
        assessment_id=assessment_id,
        deficiencies=deficiencies,
        gap_score=gap_score
    )


@router.post(
    "/generate-plan",
    response_model=GenerateIntelligencePlanResponse,
    summary="Generate Comprehensive Intelligence Plan",
    description="All-in-one generator executing gap analysis, meal schedules, substitutions, supplement guidance, recovery projections, and clinical action plan."
)
async def generate_plan(request: GenerateIntelligencePlanRequest):
    return NutritionIntelligenceService.generate_comprehensive_plan(request)
