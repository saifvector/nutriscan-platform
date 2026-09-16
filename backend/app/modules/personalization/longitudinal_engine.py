"""
Longitudinal Personalization & Continuous Learning Engine
Phase 13: Real-World Clinical Intelligence & Personalization

Analyzes longitudinal patient data:
- Detects successful interventions (symptom reduction, biomarker movement, high compliance)
- Detects failed / abandoned interventions (drop-off, GI distress, low tolerance)
- Identifies user-specific response patterns
- Updates dynamic efficacy multipliers and tolerance penalties.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime


class LongitudinalPersonalizationEngine:
    """
    Maintains and updates continuous learning profiles for personalized recommendation adaptation.
    """

    # In-memory storage for rapid session execution
    _profiles: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_or_create_profile(cls, user_id: str) -> Dict[str, Any]:
        if user_id not in cls._profiles:
            cls._profiles[user_id] = {
                "user_id": user_id,
                "successful_interventions": [],
                "failed_interventions": [],
                "tolerance_penalties": {},     # item_name -> penalty multiplier (e.g. 0.3 for disliked)
                "efficacy_multipliers": {},    # nutrient -> biological responsiveness (e.g. 1.25 for rapid responder)
                "adherence_history": [],
                "overall_responsiveness_score": 82.0,
                "last_adapted_at": datetime.utcnow().isoformat()
            }
        return cls._profiles[user_id]

    @classmethod
    def process_intervention_outcome(
        cls,
        user_id: str,
        intervention_id: str,
        nutrient: str,
        adherence_rate: float,
        symptom_delta: float, # Negative means symptom improvement
        reported_side_effects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates real-world intervention outcome and updates longitudinal learning weights.
        """
        profile = cls.get_or_create_profile(user_id)
        side_effects = reported_side_effects or []

        # Success criteria: Adherence >= 75% AND (symptom_delta <= -2.0 OR no side effects)
        is_success = (adherence_rate >= 75.0) and (symptom_delta <= -1.5) and (len(side_effects) == 0)
        is_failure = (adherence_rate < 40.0) or (len(side_effects) > 0)

        if is_success:
            if intervention_id not in profile["successful_interventions"]:
                profile["successful_interventions"].append(intervention_id)
            # Boost nutrient efficacy multiplier
            curr_mult = profile["efficacy_multipliers"].get(nutrient, 1.0)
            profile["efficacy_multipliers"][nutrient] = round(min(1.5, curr_mult + 0.10), 2)
            profile["overall_responsiveness_score"] = round(min(98.0, profile["overall_responsiveness_score"] + 2.5), 1)
            outcome_status = "SUCCESSFUL_INTERVENTION"
        elif is_failure:
            if intervention_id not in profile["failed_interventions"]:
                profile["failed_interventions"].append(intervention_id)
            # Apply tolerance penalty for item/category
            profile["tolerance_penalties"][intervention_id] = 0.40
            profile["overall_responsiveness_score"] = round(max(50.0, profile["overall_responsiveness_score"] - 2.0), 1)
            outcome_status = "FAILED_OR_ABANDONED"
        else:
            outcome_status = "MODERATE_RESPONSE"

        profile["last_adapted_at"] = datetime.utcnow().isoformat()
        return {
            "user_id": user_id,
            "intervention_id": intervention_id,
            "outcome_status": outcome_status,
            "adapted_profile": profile
        }

    @classmethod
    def apply_longitudinal_adjustments(
        cls,
        user_id: str,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Applies learned user-specific tolerance penalties and efficacy multipliers to candidate recommendations.
        """
        if user_id not in cls._profiles:
            return candidates

        prof = cls._profiles[user_id]
        penalties = prof.get("tolerance_penalties", {})
        multipliers = prof.get("efficacy_multipliers", {})

        adjusted = []
        for cand in candidates:
            c = dict(cand)
            c_id = c.get("id") or c.get("food_name") or ""

            # Check tolerance penalty
            if c_id in penalties:
                penalty = penalties[c_id]
                c["unified_score"] = round(c.get("unified_score", 80.0) * penalty, 1)
                c["adherence"] = round(c.get("adherence", 80.0) * penalty, 1)

            # Check nutrient responsiveness multiplier
            nuts = c.get("nutrients", [])
            for n in nuts:
                if n in multipliers:
                    c["velocity"] = round(c.get("velocity", 75.0) * multipliers[n], 1)

            adjusted.append(c)

        return adjusted
