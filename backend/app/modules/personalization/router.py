"""
FastAPI REST Router for Phase 13: Personalization & Continuous Learning
Mounts:
- /api/v1/personalization/*
- /api/v1/recommendations/*
- /api/v1/meal-plans/*
- /api/v1/forecasting/*
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends

from .schemas import (
    OptimizationRequest,
    OptimizationResponse,
    PrecisionFoodQuery,
    PrecisionFoodResponse,
    MealPlanGenerateRequest,
    WeeklyMealPlan,
    GroceryListResponse,
    OutcomeForecastRequest,
    OutcomeForecastResponse,
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse,
    InterventionComparisonRequest,
    InterventionComparisonResponse,
    DietaryPatternEnum,
    CulturalPatternEnum,
    BudgetTierEnum
)
from .service import PersonalizationService
from ...core.auth import (
    AuthenticatedUser,
    get_current_user_optional,
    verify_resource_ownership
)
from ...core.persistence import PersistenceRepository

router = APIRouter(tags=["Phase 13: Personalization, Meal Planning & Forecasting"])


# ==============================================================================
# 1. PERSONALIZATION ENDPOINTS (/personalization/*)
# ==============================================================================

@router.post(
    "/personalization/strategy",
    response_model=OptimizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Individualized Nutrition Optimization Strategy",
    description="Synthesizes deficiency risks, lab biomarkers, medical conditions, budget tier, and cultural food patterns."
)
async def generate_personalization_strategy(request: OptimizationRequest):
    try:
        return PersonalizationService.generate_strategy(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Optimization strategy generation failed: {str(e)}"
        )


@router.get(
    "/personalization/strategy",
    response_model=OptimizationResponse,
    summary="Get Default or Parametric Nutrition Strategy",
    description="Convenience GET endpoint returning strategy for specified target deficiencies."
)
async def get_personalization_strategy(
    deficiencies: str = Query(default="Iron,Vitamin D,Folate", description="Comma-separated target deficiencies"),
    diet: str = Query(default="OMNIVORE", description="Dietary pattern"),
    culture: str = Query(default="MEDITERRANEAN", description="Cultural food pattern"),
    budget: str = Query(default="MODERATE", description="Budget tier: LOW, MODERATE, PREMIUM")
):
    try:
        defs_list = [d.strip() for d in deficiencies.split(",") if d.strip()]
        req = OptimizationRequest(
            target_deficiencies=defs_list,
            dietary_pattern=DietaryPatternEnum(diet.upper()) if hasattr(DietaryPatternEnum, diet.upper()) else DietaryPatternEnum.OMNIVORE,
            cultural_pattern=CulturalPatternEnum(culture.upper()) if hasattr(CulturalPatternEnum, culture.upper()) else CulturalPatternEnum.MEDITERRANEAN,
            budget_tier=BudgetTierEnum(budget.upper()) if hasattr(BudgetTierEnum, budget.upper()) else BudgetTierEnum.MODERATE
        )
        return PersonalizationService.generate_strategy(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/personalization/compare",
    response_model=InterventionComparisonResponse,
    summary="Compare Nutrition Intervention Archetypes",
    description="Side-by-side comparison of whole-food only, food + targeted supplement, and lifestyle adaptation."
)
async def compare_interventions(request: InterventionComparisonRequest):
    try:
        return PersonalizationService.compare_interventions(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/personalization/feedback",
    response_model=RecommendationFeedbackResponse,
    summary="Submit Patient Recommendation Feedback",
    description="Logs palatability, ease of prep, and side effects; updates dynamic longitudinal weights."
)
async def submit_feedback(request: RecommendationFeedbackRequest):
    try:
        return PersonalizationService.submit_feedback(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==============================================================================
# 2. PRECISION RECOMMENDATIONS ENDPOINTS (/recommendations/*)
# ==============================================================================

@router.post(
    "/recommendations/precision-foods",
    response_model=PrecisionFoodResponse,
    summary="Query USDA Precision Food Recommendations",
    description="Retrieves foods from USDA FoodData Central foundation data optimized for multiple simultaneous deficiencies."
)
async def query_precision_foods(query: PrecisionFoodQuery):
    try:
        return PersonalizationService.query_precision_foods(query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/recommendations/precision-foods",
    response_model=PrecisionFoodResponse,
    summary="Quick Query Precision Foods via GET",
    description="Convenience GET endpoint filtering USDA precision foods by deficiency comma-separated list."
)
async def get_precision_foods(
    deficiencies: str = Query(default="Iron,Vitamin D", description="Comma-separated deficiencies"),
    diet: str = Query(default="OMNIVORE"),
    culture: str = Query(default="MEDITERRANEAN"),
    limit: int = Query(default=10, ge=1, le=50)
):
    try:
        defs_list = [d.strip() for d in deficiencies.split(",") if d.strip()]
        q = PrecisionFoodQuery(
            target_deficiencies=defs_list,
            dietary_pattern=DietaryPatternEnum(diet.upper()) if hasattr(DietaryPatternEnum, diet.upper()) else DietaryPatternEnum.OMNIVORE,
            cultural_pattern=CulturalPatternEnum(culture.upper()) if hasattr(CulturalPatternEnum, culture.upper()) else CulturalPatternEnum.MEDITERRANEAN,
            limit=limit
        )
        return PersonalizationService.query_precision_foods(q)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==============================================================================
# 3. INTELLIGENT MEAL PLANS ENDPOINTS (/meal-plans/*)
# ==============================================================================

@router.post(
    "/meal-plans/weekly",
    response_model=WeeklyMealPlan,
    summary="Generate Intelligent Multi-Day Meal Plan",
    description="Generates daily/weekly schedule with 100%+ RDA nutrient coverage, budget constraints, and grocery list."
)
async def generate_weekly_meal_plan(
    request: MealPlanGenerateRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        if current_user and request.assessment_id:
            owner = PersistenceRepository.get_assessment_owner(str(request.assessment_id))
            if owner:
                verify_resource_ownership(owner, current_user, "Meal Plan Assessment")
        return PersonalizationService.generate_meal_plan(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/meal-plans/daily",
    summary="Generate Daily Meal Plan",
    description="Quick GET endpoint generating a single day's breakfast, lunch, dinner, and snack schedule."
)
async def get_daily_meal_plan(
    deficiencies: str = Query(default="Iron,Vitamin D,Folate"),
    culture: str = Query(default="MEDITERRANEAN"),
    diet: str = Query(default="OMNIVORE")
):
    try:
        defs_list = [d.strip() for d in deficiencies.split(",") if d.strip()]
        req = MealPlanGenerateRequest(
            target_deficiencies=defs_list,
            cultural_pattern=CulturalPatternEnum(culture.upper()) if hasattr(CulturalPatternEnum, culture.upper()) else CulturalPatternEnum.MEDITERRANEAN,
            dietary_pattern=DietaryPatternEnum(diet.upper()) if hasattr(DietaryPatternEnum, diet.upper()) else DietaryPatternEnum.OMNIVORE,
            plan_duration_days=1
        )
        plan = PersonalizationService.generate_meal_plan(req)
        return plan.daily_plans[0] if plan.daily_plans else {}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/meal-plans/grocery-list",
    response_model=GroceryListResponse,
    summary="Generate Smart Aisle-Categorized Grocery List",
    description="Consolidates ingredients from a meal plan into shopping department categories with pricing."
)
async def generate_grocery_list(request: MealPlanGenerateRequest):
    try:
        return PersonalizationService.generate_grocery_list(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==============================================================================
# 4. OUTCOME FORECASTING ENDPOINTS (/forecasting/*)
# ==============================================================================

@router.post(
    "/forecasting/outcomes",
    response_model=OutcomeForecastResponse,
    summary="Forecast 30, 60, and 90-Day Clinical Outcomes",
    description="Calculates biological replenishment trajectories with 95% confidence intervals and normalization probabilities."
)
async def forecast_clinical_outcomes(
    request: OutcomeForecastRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        if current_user and request.assessment_id:
            owner = PersistenceRepository.get_assessment_owner(str(request.assessment_id))
            if owner:
                verify_resource_ownership(owner, current_user, "Forecast Assessment")
        return PersonalizationService.forecast_outcomes(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/forecasting/outcomes",
    response_model=OutcomeForecastResponse,
    summary="Quick Outcome Forecast via GET",
    description="Generates replenishment forecasts for specified comma-separated nutrients."
)
async def get_clinical_forecast(
    nutrients: str = Query(default="Iron,Vitamin D,Folate", description="Comma-separated nutrients"),
    adherence: float = Query(default=85.0, ge=20.0, le=100.0)
):
    try:
        nuts_list = [n.strip() for n in nutrients.split(",") if n.strip()]
        req = OutcomeForecastRequest(
            target_nutrients=nuts_list,
            adherence_assumption_pct=adherence
        )
        return PersonalizationService.forecast_outcomes(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
