"""
Personalization Orchestration Service
Phase 13: Real-World Clinical Intelligence & Personalization

Central service layer orchestrating:
1. Personalized Nutrition Optimization Engine
2. Precision Food Recommendation Engine
3. Intelligent Meal Planner & Smart Grocery Lists
4. Recommendation Ranking Engine (Unified Intervention Score)
5. Clinical Outcome Forecasting Engine
6. Longitudinal Continuous Learning & Feedback
7. Explainable Recommendation Reasoning
"""

import logging
from typing import Dict, Any, List, Optional
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
    InterventionComparisonResponse
)
from .optimization_engine import PersonalizationOptimizationEngine
from .precision_foods import PrecisionFoodEngine
from .meal_planner_pro import IntelligentMealPlanner
from .ranking_engine import RecommendationRankingEngine
from .forecasting_engine import ClinicalOutcomeForecaster
from .feedback_system import RecommendationFeedbackSystem
from .longitudinal_engine import LongitudinalPersonalizationEngine
from .explainable_reasoning import ExplainableRecommendationReasoning

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Unified service facade for all Phase 13 capabilities.
    """

    # 1. Optimization Strategy
    @classmethod
    def generate_strategy(cls, request: OptimizationRequest) -> OptimizationResponse:
        return PersonalizationOptimizationEngine.optimize_strategy(request)

    # 2. Precision Foods
    @classmethod
    def query_precision_foods(cls, query: PrecisionFoodQuery) -> PrecisionFoodResponse:
        return PrecisionFoodEngine.query_precision_foods(query)

    # 3. Intelligent Meal Planning
    @classmethod
    def generate_meal_plan(cls, request: MealPlanGenerateRequest) -> WeeklyMealPlan:
        plan = IntelligentMealPlanner.generate_plan(request)
        try:
            from ...core.persistence import PersistenceRepository
            asmnt_id = getattr(request, "assessment_id", None) or plan.plan_id
            PersistenceRepository.save_meal_plan(
                str(asmnt_id),
                request.dietary_pattern.value,
                plan.model_dump() if hasattr(plan, "model_dump") else plan.dict()
            )
        except Exception as e:
            logger.warning(f"Failed to persist meal plan to SQLite: {e}")
        return plan

    # 4. Smart Grocery List
    @classmethod
    def generate_grocery_list(cls, request: MealPlanGenerateRequest) -> GroceryListResponse:
        plan = cls.generate_meal_plan(request)
        return plan.grocery_list

    # 5. Outcome Forecasting
    @classmethod
    def forecast_outcomes(cls, request: OutcomeForecastRequest) -> OutcomeForecastResponse:
        forecast = ClinicalOutcomeForecaster.generate_full_forecast(request)
        try:
            from ...core.persistence import PersistenceRepository
            asmnt_id = request.assessment_id or forecast.forecast_id
            PersistenceRepository.save_forecast(
                str(asmnt_id),
                forecast.model_dump() if hasattr(forecast, "model_dump") else forecast.dict()
            )
        except Exception as e:
            logger.warning(f"Failed to persist forecast to SQLite: {e}")
        return forecast

    # 6. Recommendation Feedback
    @classmethod
    def submit_feedback(cls, request: RecommendationFeedbackRequest) -> RecommendationFeedbackResponse:
        return RecommendationFeedbackSystem.record_feedback(request)

    # 7. Intervention Comparison
    @classmethod
    def compare_interventions(cls, request: InterventionComparisonRequest) -> InterventionComparisonResponse:
        return RecommendationRankingEngine.compare_interventions(request)

    # 8. Explainable Recommendation Rationale
    @classmethod
    def get_recommendation_reasoning(
        cls,
        intervention_name: str,
        target_nutrients: List[str]
    ) -> Dict[str, Any]:
        return ExplainableRecommendationReasoning.generate_rationale(
            intervention_name=intervention_name,
            target_nutrients=target_nutrients
        )
