"""
Personalized Recommendation Service Layer
Phase 5: Personalized Nutrition Recommendation Engine

Orchestrates:
- Retrieving patient assessment and prediction data from cache/database
- Generating dietary-filtered food recommendations across Priority 1, 2, 3
- Assembling biochemical nutrient synergy combinations
- Synthesizing non-dietary lifestyle protocols
- Generating 7-Day, 14-Day, and 30-Day recovery roadmaps
- Multi-dimensional scoring (Relevance, Coverage, Compatibility, Overall)
- In-memory fast caching for sub-25ms response latency
- Database mapping and persistence into PostgreSQL food_recommendations table
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .engine import PersonalizedRecommendationEngine
from ..prediction.service import PredictionService
from ..explainability.service import ExplainabilityService
from ...schemas.recommendation import (
    PersonalizedRecommendationsResponse,
    FoodRecommendationsResponse,
    LifestyleRecommendationsResponse,
    RecoveryPlanResponse,
    FoodItemDetail,
    SynergyPairingItem,
    LifestyleInterventionItem,
    RecoveryPlan,
    RecommendationScores
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    High-performance recommendation service layer.
    """

    # In-memory fast LRU-style cache for generated recommendations
    _active_recommendations_cache: Dict[str, PersonalizedRecommendationsResponse] = {}

    @classmethod
    def get_recommendations(
        cls,
        assessment_id: uuid.UUID
    ) -> PersonalizedRecommendationsResponse:
        """
        Generates or retrieves comprehensive personalized recommendation package.
        """
        id_str = str(assessment_id)

        # 1. Instant Cache Return
        if id_str in cls._active_recommendations_cache:
            return cls._active_recommendations_cache[id_str]

        # 2. Retrieve Assessment and Predictions
        from ...core.persistence import PersistenceRepository

        payload = ExplainabilityService._active_payload_cache.get(id_str)
        pred_result = ExplainabilityService._active_predictions_cache.get(id_str)

        # Check SQLite persistence if not in memory
        if payload is None or pred_result is None:
            persisted_payload = PersistenceRepository.get_assessment(id_str)
            persisted_pred = PersistenceRepository.get_predictions(id_str)
            if persisted_payload:
                payload = persisted_payload
            if persisted_pred:
                pred_result = persisted_pred

        # If payload is still None, fail with error
        if payload is None:
            if assessment_id:
                raise ValueError(f"Assessment record for ID '{id_str}' not found.")
            raise ValueError("No active assessment specified. Please provide a valid assessment ID.")

        if pred_result is None:
            engine = PredictionService.get_engine()
            pred_result = engine.screen_patient(payload, compute_explainability=True)
            if id_str:
                ExplainabilityService.register_prediction_run(id_str, payload, pred_result)

        # 3. Extract Dietary Pattern and Restrictions
        diet_habits = payload.get("dietary_habits", {})
        if isinstance(diet_habits, dict):
            dietary_pattern = diet_habits.get("dietary_pattern", payload.get("dietary_pattern", "OMNIVORE"))
            restrictions = list(diet_habits.get("dietary_restrictions", []))
        else:
            dietary_pattern = str(payload.get("dietary_pattern", "OMNIVORE"))
            restrictions = list(payload.get("dietary_restrictions", []))

        # Check boolean flags in flattened payload
        if payload.get("has_dairy_free") and "dairy-free" not in restrictions:
            restrictions.append("dairy-free")
        if payload.get("has_gluten_free") and "gluten-free" not in restrictions:
            restrictions.append("gluten-free")

        preds = pred_result.get("nutrient_predictions", [])
        elevated_nutrients = [p["nutrient"] for p in preds if p.get("risk_level") in ["HIGH", "MODERATE"]]
        
        # Phase 10C: Incorporate verified clinical deficiency predictions
        try:
            clinical_res = PredictionService.predict_clinical(payload)
            for cp in clinical_res.predictions:
                if str(cp.risk_tier) in ["HIGH", "MODERATE", "ClinicalRiskTier.HIGH", "ClinicalRiskTier.MODERATE"]:
                    nut_clean = cp.target_name.replace(" Deficiency", "").replace(" Insufficiency", "").replace(" Anemia", "").strip()
                    if nut_clean and nut_clean not in elevated_nutrients:
                        elevated_nutrients.append(nut_clean)
        except Exception as e:
            logger.debug(f"Clinical recommendation enrichment note: {e}")

        if not elevated_nutrients:
            elevated_nutrients = [p["nutrient"] for p in preds[:3]]

        # 4. Generate Core Recommendations
        ranked_foods = PersonalizedRecommendationEngine.generate_food_recommendations(
            nutrient_predictions=preds,
            dietary_pattern=dietary_pattern,
            restrictions=restrictions
        )

        priority_1 = ranked_foods["priority_1"]
        priority_2 = ranked_foods["priority_2"]
        priority_3 = ranked_foods["priority_3"]

        # Phase 12: Intercept candidate recommendations with ClinicalSafetyEngine
        try:
            from ..governance.safety_engine import ClinicalSafetyEngine
            candidate_list = [f.model_dump() if hasattr(f, "model_dump") else dict(f) for f in (priority_1 + priority_2 + priority_3)]
            safety_eval = ClinicalSafetyEngine.evaluate_safety(
                patient_intake=payload,
                proposed_recommendations=candidate_list,
                predictions=preds
            )
            blocked_nutrients = set()
            for v in safety_eval.violations:
                v_act = getattr(v, "action", None)
                if v_act == "BLOCKED" or str(v_act).endswith("BLOCKED"):
                    blocked_nutrients.add(getattr(v, "nutrient", ""))

            if blocked_nutrients:
                priority_1 = [f for f in priority_1 if f.target_nutrient not in blocked_nutrients]
                priority_2 = [f for f in priority_2 if f.target_nutrient not in blocked_nutrients]
                priority_3 = [f for f in priority_3 if f.target_nutrient not in blocked_nutrients]
                logger.info(f"Clinical Safety Engine intercepted and pruned recommendations for: {blocked_nutrients}")
        except Exception as e:
            logger.warning(f"Clinical safety evaluation note: {e}")

        # 5. Generate Biochemical Synergy Pairings
        synergies = PersonalizedRecommendationEngine.generate_synergy_pairings(
            elevated_nutrients=elevated_nutrients,
            dietary_pattern=dietary_pattern
        )

        # 6. Generate Lifestyle Interventions
        flat_patient = dict(payload)
        if isinstance(payload.get("lifestyle_factors"), dict):
            flat_patient.update(payload["lifestyle_factors"])
        lifestyle = PersonalizedRecommendationEngine.generate_lifestyle_interventions(
            nutrient_predictions=preds,
            patient_data=flat_patient
        )

        # 7. Generate Targeted Supplements within NIH Upper Tolerable Limits
        supplements = PersonalizedRecommendationEngine.generate_supplement_recommendations(
            elevated_nutrients=elevated_nutrients,
            dietary_pattern=dietary_pattern,
            patient_intake=payload
        )

        # 8. Generate Laboratory Monitoring & Re-Testing Protocol
        monitoring = PersonalizedRecommendationEngine.generate_monitoring_plan(
            elevated_nutrients=elevated_nutrients
        )

        # 9. Generate Clinician Follow-Up Schedule
        followup = PersonalizedRecommendationEngine.generate_followup_plan(
            elevated_nutrients=elevated_nutrients
        )

        # 10. Generate Phased Recovery Plan (7, 14, 30-Day)
        recovery_plan = PersonalizedRecommendationEngine.generate_recovery_plan(
            elevated_nutrients=elevated_nutrients,
            top_foods=priority_1 + priority_2,
            lifestyle_items=lifestyle
        )

        # 11. Compute Recommendation Scoring
        scores = PersonalizedRecommendationEngine.calculate_recommendation_scores(
            nutrient_predictions=preds,
            recommended_foods=priority_1 + priority_2 + priority_3,
            restrictions=restrictions
        )

        clinical_summary = (
            f"Personalized nutrition strategy compiled for {dietary_pattern.capitalize()} dietary pattern "
            f"(Restrictions: {', '.join(restrictions) if restrictions else 'None'}). "
            f"Addresses primary flagged risks: {', '.join(elevated_nutrients[:3])}. "
            f"Overall Strategy Score: {scores.overall_recommendation_score}/100."
        )

        response = PersonalizedRecommendationsResponse(
            assessment_id=assessment_id,
            generated_at=datetime.utcnow(),
            dietary_pattern_applied=dietary_pattern,
            active_restrictions=restrictions,
            target_nutrients=elevated_nutrients,
            scoring_summary=scores,
            priority_1_foods=priority_1,
            priority_2_foods=priority_2,
            priority_3_foods=priority_3,
            synergistic_pairings=synergies,
            lifestyle_interventions=lifestyle,
            supplement_recommendations=supplements,
            monitoring_recommendations=monitoring,
            followup_recommendations=followup,
            recovery_plan=recovery_plan,
            clinical_summary_note=clinical_summary
        )

        cls._active_recommendations_cache[id_str] = response

        # Thread-safe SQLite persistence for cross-module consistency and restart safety
        try:
            rec_dict = response.model_dump() if hasattr(response, "model_dump") else response.dict()
            PersistenceRepository.save_recommendations(id_str, rec_dict)
        except Exception as e:
            logger.warning(f"Persistence save note for recommendations: {e}")

        return response

    @classmethod
    def get_food_recommendations(
        cls,
        assessment_id: uuid.UUID
    ) -> FoodRecommendationsResponse:
        """
        Retrieves filtered and ranked food recommendations.
        """
        full_report = cls.get_recommendations(assessment_id)

        # Group foods by nutrient
        foods_by_nut: Dict[str, List[FoodItemDetail]] = {}
        all_foods = full_report.priority_1_foods + full_report.priority_2_foods + full_report.priority_3_foods
        for food in all_foods:
            nut = food.target_nutrient
            if nut not in foods_by_nut:
                foods_by_nut[nut] = []
            foods_by_nut[nut].append(food)

        return FoodRecommendationsResponse(
            assessment_id=assessment_id,
            dietary_pattern=full_report.dietary_pattern_applied,
            total_foods_recommended=len(all_foods),
            priority_1_foods=full_report.priority_1_foods,
            priority_2_foods=full_report.priority_2_foods,
            priority_3_foods=full_report.priority_3_foods,
            foods_by_nutrient=foods_by_nut
        )

    @classmethod
    def get_lifestyle_recommendations(
        cls,
        assessment_id: uuid.UUID
    ) -> LifestyleRecommendationsResponse:
        """
        Retrieves lifestyle interventions.
        """
        full_report = cls.get_recommendations(assessment_id)
        return LifestyleRecommendationsResponse(
            assessment_id=assessment_id,
            total_interventions=len(full_report.lifestyle_interventions),
            interventions=full_report.lifestyle_interventions
        )

    @classmethod
    def get_recovery_plan(
        cls,
        assessment_id: uuid.UUID
    ) -> RecoveryPlanResponse:
        """
        Retrieves 7-Day, 14-Day, and 30-Day nutrient recovery roadmaps.
        """
        full_report = cls.get_recommendations(assessment_id)
        return RecoveryPlanResponse(
            assessment_id=assessment_id,
            recovery_plan=full_report.recovery_plan
        )

    @classmethod
    async def persist_recommendations(
        cls,
        db_session: Any,
        prediction_id_map: Dict[str, uuid.UUID],
        recommendations: PersonalizedRecommendationsResponse
    ) -> List[Any]:
        """
        Persists generated food recommendations into PostgreSQL food_recommendations table.
        """
        from ...models.recommendation import FoodRecommendation

        persisted = []
        all_foods = (
            recommendations.priority_1_foods +
            recommendations.priority_2_foods +
            recommendations.priority_3_foods
        )

        for food in all_foods:
            pred_id = prediction_id_map.get(food.target_nutrient)
            if not pred_id:
                # If target nutrient not explicitly in map, link to first available
                pred_id = list(prediction_id_map.values())[0] if prediction_id_map else uuid.uuid4()

            rank_val = 1 if food.priority_tier.value == "PRIORITY_1" else (2 if food.priority_tier.value == "PRIORITY_2" else 3)

            entity = FoodRecommendation(
                id=uuid.uuid4(),
                prediction_id=pred_id,
                nutrient_name=food.target_nutrient,
                food_name=food.food_name,
                food_group=food.food_group,
                priority_rank=rank_val,
                recommendation_score=food.recommendation_score,
                serving_size=food.serving_size,
                nutrient_density_mg=food.nutrient_density,
                unit=food.unit,
                dietary_compatibility=", ".join(food.dietary_compatibility),
                rationale=food.rationale,
                preparation_tips=food.preparation_tips,
                contraindications=food.contraindications
            )
            db_session.add(entity)
            persisted.append(entity)

        await db_session.commit()
        return persisted
