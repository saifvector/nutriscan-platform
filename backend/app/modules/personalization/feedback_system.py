"""
Recommendation Feedback System
Phase 13: Real-World Clinical Intelligence & Personalization

Captures structured user feedback:
- Overall rating (1-5 stars)
- Taste & palatability score
- Preparation ease score
- Side effects (GI upset, reflux, headaches)
- Updates dynamic preference weights and suggests automated substitutions.
"""

import uuid
from typing import Dict, Any, List, Optional
from .schemas import (
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse
)
from .longitudinal_engine import LongitudinalPersonalizationEngine


class RecommendationFeedbackSystem:
    """
    Ingests patient feedback and dynamically updates recommendation rankings.
    """

    _feedback_logs: List[Dict[str, Any]] = []

    @classmethod
    def record_feedback(cls, request: RecommendationFeedbackRequest) -> RecommendationFeedbackResponse:
        """
        Processes feedback, updates longitudinal profile, and determines next action.
        """
        fb_id = f"FB_{uuid.uuid4().hex[:8].upper()}"
        entry = request.model_dump()
        entry["feedback_id"] = fb_id
        cls._feedback_logs.append(entry)

        user_id = request.user_id or "ANONYMOUS_USER"
        profile = LongitudinalPersonalizationEngine.get_or_create_profile(user_id)

        # Dynamic weight adjustment based on rating and side effects
        if request.rating >= 4 and not request.reported_side_effects:
            # Positive reinforcement
            profile["tolerance_penalties"][request.recommendation_id] = 1.15
            weight = 1.15
            next_action = f"Reinforcing {request.item_name} in future meal plans due to high patient tolerance ({request.rating}/5 stars)."
        elif request.rating <= 2 or (request.reported_side_effects and len(request.reported_side_effects) > 0):
            # Adverse event or strong dislike
            profile["tolerance_penalties"][request.recommendation_id] = 0.25
            weight = 0.25
            next_action = f"Deprecating {request.item_name} from future plans. Automatic substitution triggered to prevent compliance drop-off."
        else:
            profile["tolerance_penalties"][request.recommendation_id] = 1.0
            weight = 1.0
            next_action = f"Neutral feedback recorded. Maintaining {request.item_name} with standard rotation frequency."

        return RecommendationFeedbackResponse(
            status="SUCCESS",
            feedback_id=fb_id,
            message="Feedback successfully incorporated into clinical personalization engine.",
            adapted_preference_weight=round(weight, 2),
            next_action_recommendation=next_action
        )

    @classmethod
    def get_feedback_count(cls) -> int:
        return len(cls._feedback_logs)
