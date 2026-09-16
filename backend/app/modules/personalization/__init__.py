"""
Phase 13: Real-World Clinical Intelligence, Personalization & Continuous Learning
Package initialization.
"""

from .schemas import (
    OptimizationRequest,
    OptimizationResponse,
    PrecisionFoodQuery,
    PrecisionFoodItem,
    PrecisionFoodResponse,
    MealPlanGenerateRequest,
    DailyMealPlan,
    WeeklyMealPlan,
    GroceryListResponse,
    OutcomeForecastRequest,
    OutcomeForecastItem,
    OutcomeForecastResponse,
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse,
    InterventionComparisonRequest,
    InterventionComparisonResponse,
    UnifiedInterventionItem
)
from .service import PersonalizationService

__all__ = [
    "OptimizationRequest",
    "OptimizationResponse",
    "PrecisionFoodQuery",
    "PrecisionFoodItem",
    "PrecisionFoodResponse",
    "MealPlanGenerateRequest",
    "DailyMealPlan",
    "WeeklyMealPlan",
    "GroceryListResponse",
    "OutcomeForecastRequest",
    "OutcomeForecastItem",
    "OutcomeForecastResponse",
    "RecommendationFeedbackRequest",
    "RecommendationFeedbackResponse",
    "InterventionComparisonRequest",
    "InterventionComparisonResponse",
    "UnifiedInterventionItem",
    "PersonalizationService"
]
