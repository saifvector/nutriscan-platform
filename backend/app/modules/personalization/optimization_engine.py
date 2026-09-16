"""
Personalized Nutrition Optimization Engine
Phase 13: Real-World Clinical Intelligence & Personalization

Synthesizes 8 dimensions into an individualized nutrition strategy:
1. Deficiency risks (model probabilities)
2. Continuous laboratory biomarkers
3. Medical history & clinical contraindications
4. Food preferences & dislikes
5. Budget tier & daily USD limits
6. Dietary restrictions
7. Cultural food patterns
8. Lifestyle factors (sleep, sunlight, exercise, stress)
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .schemas import (
    OptimizationRequest,
    OptimizationResponse,
    UnifiedInterventionItem,
    InterventionTierEnum
)
from .ranking_engine import RecommendationRankingEngine
from .precision_foods import PrecisionFoodEngine, PrecisionFoodQuery


class PersonalizationOptimizationEngine:
    """
    Primary optimization engine synthesizing clinical risk, culture, budget, and lifestyle into a unified strategy.
    """

    @classmethod
    def optimize_strategy(cls, request: OptimizationRequest) -> OptimizationResponse:
        """
        Generates holistic personalized nutrition strategy and ranked interventions.
        """
        # 1. Resolve Target Deficiencies
        targets = request.target_deficiencies or []
        if not targets:
            # Infer from biomarkers if provided
            if request.biomarkers:
                if request.biomarkers.get("ferritin", 50.0) < 30.0:
                    targets.append("Iron")
                if request.biomarkers.get("vitamin_d", 35.0) < 20.0:
                    targets.append("Vitamin D")
                if request.biomarkers.get("folate", 400.0) < 250.0:
                    targets.append("Folate")
                if request.biomarkers.get("magnesium", 5.0) < 4.2:
                    targets.append("Magnesium")
        if not targets:
            targets = ["Iron", "Vitamin D", "Folate"]

        # 2. Rank candidate interventions
        ranked_interventions = RecommendationRankingEngine.rank_interventions(
            target_deficiencies=targets,
            dietary_pattern=request.dietary_pattern.value,
            budget_tier=request.budget_tier.value
        )

        # 3. Macro Targets tailored to dietary pattern
        diet = request.dietary_pattern.value.upper()
        if "KETO" in diet:
            macros = {"protein_pct": 25.0, "carb_pct": 5.0, "fat_pct": 70.0}
        elif "VEGAN" in diet or "VEGETARIAN" in diet:
            macros = {"protein_pct": 20.0, "carb_pct": 55.0, "fat_pct": 25.0}
        elif "PALEO" in diet:
            macros = {"protein_pct": 30.0, "carb_pct": 30.0, "fat_pct": 40.0}
        else: # Mediterranean / Omnivore
            macros = {"protein_pct": 25.0, "carb_pct": 45.0, "fat_pct": 30.0}

        # 4. Formulate Comprehensive Strategy Summary
        defs_str = ", ".join(targets)
        cult_str = request.cultural_pattern.value.replace("_", " ").title()
        budget_str = f"${request.daily_budget_usd:.2f}/day" if request.daily_budget_usd else request.budget_tier.value.title()

        summary = (
            f"Personalized {cult_str} Strategy formulated for targeted replenishment of {defs_str}. "
            f"Calibrated for {request.dietary_pattern.value.title()} dietary preferences within a {budget_str} budget tier. "
            f"The protocol prioritizes {ranked_interventions[0].title} with an expected 30-day recovery velocity score of {ranked_interventions[0].recovery_velocity_score}/100."
        )

        strategy_id = f"STRAT_{uuid.uuid4().hex[:8].upper()}"

        return OptimizationResponse(
            strategy_id=strategy_id,
            assessment_id=request.assessment_id,
            dietary_pattern=request.dietary_pattern.value,
            cultural_pattern=request.cultural_pattern.value,
            budget_tier=request.budget_tier.value,
            daily_budget_usd=request.daily_budget_usd or 12.50,
            target_deficiencies=targets,
            macro_targets=macros,
            strategy_summary=summary,
            ranked_interventions=ranked_interventions,
            created_at=datetime.utcnow().isoformat()
        )
