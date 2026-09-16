"""
Recommendation Module Initialization
Phase 5: Personalized Nutrition Recommendation Engine
"""

from .knowledge_base import FOOD_KNOWLEDGE_BASE
from .engine import PersonalizedRecommendationEngine
from .service import RecommendationService
from .router import router as recommendation_router

__all__ = [
    "FOOD_KNOWLEDGE_BASE",
    "PersonalizedRecommendationEngine",
    "RecommendationService",
    "recommendation_router"
]
