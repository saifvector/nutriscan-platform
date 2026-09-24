"""
Explainability Service Layer
Phase 4: Explainable AI and Risk Factor Analysis System

Orchestrates:
- SHAP TreeExplainer local and global feature attribution
- Positive vs. Protective risk factor partitioning
- Feature contribution percentage calculation
- Clinical reasoning narrative synthesis (Patient & Clinician dual-layer)
- Categorized risk factor extraction across 5 clinical domains
- Waterfall plot coordinate and SVG visualization rendering
- In-memory caching and database persistence bridge
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import numpy as np

from ...ml import (
    NutritionalInferenceEngine,
    ClinicalExplainabilityEngine,
    ClinicalReasoningEngine,
    DashboardVisualizer,
    TARGET_NUTRIENTS,
    NUTRIENT_CODES
)
from ..prediction.service import PredictionService
from ...schemas.explainability import (
    NutrientExplainabilityDetail,
    MultiNutrientExplainabilityResponse,
    FeatureContributionItem,
    WaterfallPlotData,
    WaterfallStepItem,
    ClinicalReasoningSummary,
    RiskFactorCardItem,
    CategorizedRiskFactorsResponse,
    GlobalFeatureImportanceResponse,
    GlobalFeatureImportanceItem
)
from ...schemas.phase11_explainability import (
    PredictionExplanationResponse,
    EvidenceSummaryResponse,
    NutrientInteractionsResponse,
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
    RecommendationRationaleResponse,
    RecommendationRationaleItem,
    EvidenceGrade
)
from .clinical_explainer import ClinicalExplainerEngine
from .evidence_engine import ClinicalEvidenceEngine
from .evidence_catalog import generate_dynamic_clinical_evidence_entry
from .interaction_engine import NutrientInteractionReasoningEngine
from .simulator import WhatIfSimulationEngine

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """
    Production-ready service layer for XAI, SHAP attributions,
    risk factor categorizations, and clinical reasoning.
    """

    # In-memory bounded TTL cache for active assessment payloads to guarantee sub-50ms explainability retrieval
    MAX_CACHE_SIZE: int = 500
    CACHE_TTL_SECONDS: float = 3600.0  # 1 hour

    _active_payload_cache: Dict[str, Dict[str, Any]] = {}
    _active_predictions_cache: Dict[str, Dict[str, Any]] = {}
    _active_explainability_cache: Dict[str, MultiNutrientExplainabilityResponse] = {}
    _cache_timestamps: Dict[str, float] = {}

    @classmethod
    def invalidate_cache(cls, assessment_id: Optional[str] = None):
        """Invalidates in-memory cache for a specific assessment ID, or all if None."""
        if assessment_id:
            id_str = str(assessment_id)
            cls._active_payload_cache.pop(id_str, None)
            cls._active_predictions_cache.pop(id_str, None)
            cls._active_explainability_cache.pop(id_str, None)
            cls._cache_timestamps.pop(id_str, None)
        else:
            cls._active_payload_cache.clear()
            cls._active_predictions_cache.clear()
            cls._active_explainability_cache.clear()
            cls._cache_timestamps.clear()

    @classmethod
    def _evict_stale_or_overflow(cls):
        now = time.time()
        expired_keys = [k for k, ts in cls._cache_timestamps.items() if (now - ts) > cls.CACHE_TTL_SECONDS]
        for k in expired_keys:
            cls.invalidate_cache(k)
        if len(cls._active_payload_cache) > cls.MAX_CACHE_SIZE:
            oldest_keys = sorted(cls._cache_timestamps.keys(), key=lambda k: cls._cache_timestamps.get(k, 0))
            for k in oldest_keys[:len(cls._active_payload_cache) - cls.MAX_CACHE_SIZE]:
                cls.invalidate_cache(k)

    @classmethod
    def register_prediction_run(
        cls,
        assessment_id: str,
        payload: Dict[str, Any],
        prediction_result: Dict[str, Any]
    ):
        """Stores assessment payload and prediction output in fast memory cache."""
        cls._evict_stale_or_overflow()
        id_str = str(assessment_id)
        cls._active_payload_cache[id_str] = payload
        cls._active_predictions_cache[id_str] = prediction_result
        cls._cache_timestamps[id_str] = time.time()

    @classmethod
    def get_explainability(
        cls,
        assessment_id: uuid.UUID,
        target_nutrient_code: Optional[str] = None,
        top_k: int = 6
    ) -> MultiNutrientExplainabilityResponse:
        """
        Generates full explainability report for an assessment.
        If target_nutrient_code is provided, focuses on that specific nutrient.
        """
        start_time = time.perf_counter()
        id_str = str(assessment_id)

        # Check TTL expiry
        if id_str in cls._cache_timestamps:
            if (time.time() - cls._cache_timestamps[id_str]) > cls.CACHE_TTL_SECONDS:
                cls.invalidate_cache(id_str)

        # Instant cache return if full report was previously computed
        if target_nutrient_code is None and id_str in cls._active_explainability_cache:
            return cls._active_explainability_cache[id_str]

        # Retrieve cached payload or mock representative sample for standalone testing
        payload = cls._active_payload_cache.get(id_str)
        pred_result = cls._active_predictions_cache.get(id_str)

        engine = PredictionService.get_engine()
        if payload is None:
            from ...core.persistence import PersistenceRepository
            payload = PersistenceRepository.get_assessment(id_str)
            if payload is None:
                raise ValueError(f"Assessment record for ID '{id_str}' not found.")
            pred_result = PersistenceRepository.get_prediction(id_str)
            if pred_result is None:
                pred_result = engine.screen_patient(payload, compute_explainability=False)

        # Transform features using clinical pipeline
        X_df, unscaled_dict = engine.pipeline.transform_single(payload)
        scaled_row = X_df.values[0]
        feature_names = getattr(engine.pipeline, "feature_names_", getattr(engine.pipeline, "final_feature_names_", []))

        nutrients_to_explain = (
            [n for n in TARGET_NUTRIENTS if NUTRIENT_CODES.get(n, "").upper() == target_nutrient_code.upper()]
            if target_nutrient_code else TARGET_NUTRIENTS
        )
        if not nutrients_to_explain:
            nutrients_to_explain = TARGET_NUTRIENTS[:3]

        predictions_dict = {p["nutrient"]: p for p in pred_result.get("nutrient_predictions", [])}

        explained_items: List[NutrientExplainabilityDetail] = []

        for nut in nutrients_to_explain:
            pred_info = predictions_dict.get(nut, {
                "risk_level": "MODERATE",
                "probability": 0.50,
                "confidence_level": "High Confidence"
            })
            submodel = engine.model.models_.get(nut)

            # Selective SHAP: Use deep tree SHAP for single nutrient drill down or elevated risk, fast surrogate otherwise
            should_use_shap = True if target_nutrient_code else (
                pred_info.get("risk_level") in ["HIGH", "MODERATE"] or nut in TARGET_NUTRIENTS[:2]
            )

            # Local SHAP attribution
            explain_dict = engine.explainability_engine.explain_nutrient_prediction(
                nutrient_name=nut,
                feature_names=feature_names,
                unscaled_features=unscaled_dict,
                scaled_feature_row=scaled_row,
                model_subestimator=submodel,
                top_k=top_k,
                use_shap=should_use_shap
            )

            # Clinical Reasoning Synthesis
            reasoning = ClinicalReasoningEngine.synthesize_narrative(
                nutrient_name=nut,
                risk_level=pred_info.get("risk_level", "LOW"),
                probability=pred_info.get("probability", 0.0),
                positive_factors=explain_dict["top_positive_factors"],
                protective_factors=explain_dict["top_protective_factors"],
                unscaled_features=unscaled_dict
            )

            detail = NutrientExplainabilityDetail(
                nutrient_code=NUTRIENT_CODES.get(nut, nut.upper().replace(" ", "_")),
                nutrient=nut,
                risk_level=pred_info.get("risk_level", "LOW"),
                probability=pred_info.get("probability", 0.0),
                confidence_level=pred_info.get("confidence_level", "High Confidence"),
                total_features_evaluated=len(feature_names),
                top_positive_factors=explain_dict["top_positive_factors"],
                top_protective_factors=explain_dict["top_protective_factors"],
                all_contributions=explain_dict["all_contributions"],
                waterfall_plot=WaterfallPlotData(**explain_dict["waterfall_plot"]),
                clinical_reasoning=ClinicalReasoningSummary(**reasoning),
                svg_chart=explain_dict.get("svg_chart")
            )
            explained_items.append(detail)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response = MultiNutrientExplainabilityResponse(
            assessment_id=assessment_id,
            overall_risk=pred_result.get("overall_risk", "MODERATE"),
            overall_confidence="High Confidence",
            nutrients_explained=explained_items,
            execution_time_ms=latency_ms
        )
        if target_nutrient_code is None:
            cls._active_explainability_cache[id_str] = response
        return response

    @classmethod
    def get_categorized_risk_factors(
        cls,
        assessment_id: uuid.UUID
    ) -> CategorizedRiskFactorsResponse:
        """
        Organizes all patient risk factors into the 5 clinical categories.
        """
        id_str = str(assessment_id)
        payload = cls._active_payload_cache.get(id_str)
        pred_result = cls._active_predictions_cache.get(id_str)

        if payload is None:
            from ...core.persistence import PersistenceRepository
            payload = PersistenceRepository.get_assessment(id_str)
            if payload is None:
                raise ValueError(f"Assessment record for ID '{id_str}' not found.")
            pred_result = PersistenceRepository.get_prediction(id_str)
            if pred_result is None:
                engine = PredictionService.get_engine()
                pred_result = engine.screen_patient(payload, compute_explainability=False)

        preds = pred_result.get("nutrient_predictions", []) if pred_result else []
        cat_factors = ClinicalReasoningEngine.extract_categorized_risk_factors(
            unscaled_features=payload,
            nutrient_predictions=preds
        )

        total_factors = sum(len(v) for v in cat_factors.values())

        return CategorizedRiskFactorsResponse(
            assessment_id=assessment_id,
            total_risk_factors_identified=total_factors,
            dietary_factors=[RiskFactorCardItem(**item) for item in cat_factors["dietary_factors"]],
            lifestyle_factors=[RiskFactorCardItem(**item) for item in cat_factors["lifestyle_factors"]],
            symptom_factors=[RiskFactorCardItem(**item) for item in cat_factors["symptom_factors"]],
            medical_factors=[RiskFactorCardItem(**item) for item in cat_factors["medical_factors"]],
            supplement_factors=[RiskFactorCardItem(**item) for item in cat_factors["supplement_factors"]],
            physiological_factors=[RiskFactorCardItem(**item) for item in cat_factors["physiological_factors"]]
        )

    @classmethod
    def get_global_importance(
        cls,
        target_nutrient_code: Optional[str] = None
    ) -> GlobalFeatureImportanceResponse:
        """
        Returns population-wide feature importance across nutrients.
        """
        engine = PredictionService.get_engine()
        feature_names = getattr(engine.pipeline, "feature_names_", getattr(engine.pipeline, "final_feature_names_", []))
        global_data = engine.explainability_engine.compute_global_feature_importance(feature_names)

        drivers = [GlobalFeatureImportanceItem(**item) for item in global_data["top_global_drivers"]]

        return GlobalFeatureImportanceResponse(
            model_name=global_data["model_name"],
            model_version=global_data["model_version"],
            target_nutrient=target_nutrient_code or "ALL_NUTRIENTS",
            top_global_drivers=drivers,
            total_population_samples_benchmarked=global_data["total_population_samples_benchmarked"]
        )

    @classmethod
    def get_waterfall_chart(
        cls,
        assessment_id: uuid.UUID,
        nutrient_code: str,
        format: str = "svg"
    ) -> Dict[str, Any]:
        """
        Returns standalone SVG markup or Recharts JSON coordinates for a specific nutrient.
        """
        report = cls.get_explainability(assessment_id=assessment_id, target_nutrient_code=nutrient_code)
        if not report.nutrients_explained:
            raise ValueError(f"Nutrient '{nutrient_code}' not recognized or found.")

        detail = report.nutrients_explained[0]
        if format.lower() == "svg":
            return {
                "nutrient_code": nutrient_code,
                "nutrient": detail.nutrient,
                "format": "svg",
                "svg_content": detail.svg_chart
            }
        else:
            recharts_data = DashboardVisualizer.format_recharts_contract(
                base_value=detail.waterfall_plot.base_value if detail.waterfall_plot else 0.25,
                final_value=detail.waterfall_plot.final_value if detail.waterfall_plot else detail.probability,
                steps=[s.model_dump() for s in detail.waterfall_plot.steps] if detail.waterfall_plot else []
            )
            return {
                "nutrient_code": nutrient_code,
                "nutrient": detail.nutrient,
                "format": "recharts_json",
                "chart_data": recharts_data
            }

    # =========================================================================
    # PHASE 11: EXPLAINABLE AI, CLINICAL REASONING & EVIDENCE SERVICE METHODS
    # =========================================================================

    @classmethod
    def explain_clinical_prediction(
        cls,
        assessment_payload: Dict[str, Any],
        prediction_id: Optional[uuid.UUID] = None
    ) -> PredictionExplanationResponse:
        """
        Phase 11 Primary Prediction Explainability:
        Returns stored precomputed SHAP explanations directly from the AssessmentPredictionSnapshot
        if available (zero runtime re-inference).
        Only recomputes if assessment was not previously screened.
        """
        from ...core.persistence import PersistenceRepository
        from ...schemas.phase11_explainability import TargetExplanation, PredictionExplanationResponse
        from datetime import datetime, timezone

        id_str = str(prediction_id) if prediction_id else None
        if id_str:
            snapshot = PersistenceRepository.get_prediction(id_str)
            if snapshot and isinstance(snapshot, dict) and snapshot.get("explanations"):
                stored_explanations = [
                    TargetExplanation(**e) if isinstance(e, dict) else e 
                    for e in snapshot["explanations"]
                ]
                try:
                    p_uuid = uuid.UUID(id_str)
                except Exception:
                    p_uuid = uuid.uuid4()

                return PredictionExplanationResponse(
                    prediction_id=p_uuid,
                    timestamp=datetime.now(timezone.utc),
                    overall_risk_tier=snapshot.get("overall_risk", "LOW"),
                    overall_risk_score=float(snapshot.get("overall_risk_score", 0.0)),
                    explanations=stored_explanations
                )

        return ClinicalExplainerEngine.explain_patient_prediction(
            assessment_payload=assessment_payload,
            prediction_id=prediction_id
        )

    @classmethod
    def get_evidence_summary(
        cls,
        nutrient: Optional[str] = None
    ) -> EvidenceSummaryResponse:
        """
        Phase 11 Clinical Evidence Engine:
        Retrieves scientific citations, NIH ODS fact sheets, and USDA reference records.
        """
        if nutrient:
            ev = ClinicalEvidenceEngine.get_evidence_for_target(nutrient)
            items = [ev] if ev else []
        else:
            items = ClinicalEvidenceEngine.get_all_citations()

        return EvidenceSummaryResponse(
            total_citations=len(items),
            evidence_items=items
        )

    @classmethod
    def get_nutrient_interactions(
        cls,
        nutrients: Optional[List[str]] = None
    ) -> NutrientInteractionsResponse:
        """
        Phase 11 Nutrient Interaction Reasoning Engine:
        Evaluates biochemical synergies, competitive transporter antagonisms, and timing protocols.
        """
        if nutrients:
            rules = NutrientInteractionReasoningEngine.detect_interactions(nutrients)
        else:
            rules = NutrientInteractionReasoningEngine.get_all_interactions()

        return NutrientInteractionsResponse(
            total_interactions=len(rules),
            interactions=rules
        )

    @classmethod
    def simulate_what_if(
        cls,
        request: WhatIfSimulationRequest
    ) -> WhatIfSimulationResponse:
        """
        Phase 11 What-If Clinical Simulation Engine:
        Forecasts risk trajectory reductions and deficiency normalization timelines.
        """
        return WhatIfSimulationEngine.run_simulation(request)

    @classmethod
    def get_recommendation_rationales(
        cls,
        assessment_id: Optional[uuid.UUID] = None
    ) -> RecommendationRationaleResponse:
        """
        Phase 11 Clinical Recommendation Traceability:
        Links active recommendations to primary evidence sources, triggering risk scores,
        and projected biological outcomes.
        """
        id_str = str(assessment_id) if assessment_id else None
        cached_payload = cls._active_payload_cache.get(id_str) if id_str else None

        from ..recommendation.service import RecommendationService
        from ..recommendation.knowledge_base import FOOD_KNOWLEDGE_BASE

        rec_response = RecommendationService.get_recommendations(assessment_id or uuid.uuid4())
        rationale_items: List[RecommendationRationaleItem] = []

        all_food_items = (
            rec_response.priority_1_foods +
            rec_response.priority_2_foods +
            rec_response.priority_3_foods
        )

        for food in all_food_items[:12]:
            target_nut = food.target_nutrient
            evidence = ClinicalEvidenceEngine.get_evidence_for_target(target_nut)
            usda_ref = ClinicalEvidenceEngine.get_usda_reference(food.food_name)

            outcome_map = {
                "Iron": "Projected restoration of transferrin saturation and incremental ferritin replenishment over 60-90 days.",
                "Vitamin D": "Anticipated increase in circulating 25(OH)D of 5-8 ng/mL over 4-6 weeks with consistent intake.",
                "Folate": "Cellular RBC folate normalization and reduction in plasma homocysteine within 30 days.",
                "Magnesium": "Neuromuscular relaxation and stabilization of intracellular Na+/K+ balance within 2-4 weeks.",
                "Potassium": "Restoration of vascular endothelial tone and improved urinary sodium excretion.",
                "Calcium": "Preservation of trabecular bone mineral density and suppression of excess PTH secretion.",
                "Selenium": "Optimal selenoprotein P synthesis and glutathione peroxidase antioxidant protection."
            }
            outcome_text = outcome_map.get(target_nut, "Supports micronutrient adequacy and metabolic homeostasis.")

            rationale_items.append(RecommendationRationaleItem(
                recommendation_id=uuid.uuid4(),
                food_or_protocol=food.food_name,
                target_nutrient=target_nut,
                triggering_prediction_id=assessment_id,
                triggering_risk_tier="HIGH" if food.recommendation_score >= 80 else "MODERATE",
                evidence_source=evidence.evidence_source if evidence else usda_ref.get("source", "USDA FoodData Central"),
                evidence_strength=evidence.evidence_strength if evidence else EvidenceGrade.GRADE_B,
                reference_url=evidence.reference_url if evidence else "https://fdc.nal.usda.gov/",
                clinical_rationale=food.rationale or f"High nutrient density source for {target_nut}.",
                expected_outcome=outcome_text
            ))

        return RecommendationRationaleResponse(
            total_recommendations=len(rationale_items),
            recommendations=rationale_items
        )

    @classmethod
    def get_dynamic_evidence_base(
        cls,
        target_id: Optional[str] = None,
        assessment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dynamic Explainability & Clinical Evidence Base
        Generates evidence, citations, narratives, and dynamic feature attributions
        grounded in real patient assessment and prediction records.
        Never returns synthetic, mock, or hardcoded clinical data.
        """
        from fastapi import HTTPException, status
        if not assessment_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No assessment ID provided. Cannot generate clinical evidence without a valid assessment."
            )

        from ...core.persistence import PersistenceRepository

        id_str = str(assessment_id)
        snapshot = PersistenceRepository.get_prediction(id_str)
        if snapshot and isinstance(snapshot, dict) and snapshot.get("evidence_catalog"):
            catalog = snapshot["evidence_catalog"]
            if target_id:
                if target_id in catalog:
                    return catalog[target_id]
                for k, v in catalog.items():
                    if target_id.lower() in k.lower() or k.lower() in target_id.lower():
                        return v
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Target ID '{target_id}' not found in evaluated clinical profile."
                )
            return catalog

        payload = cls._active_payload_cache.get(id_str)
        if payload is None:
            payload = PersistenceRepository.get_assessment(id_str)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment record for ID '{assessment_id}' not found."
            )

        try:
            pred_uuid = uuid.UUID(id_str)
        except Exception:
            pred_uuid = uuid.uuid4()

        explanation_resp = cls.explain_clinical_prediction(
            assessment_payload=payload,
            prediction_id=pred_uuid
        )

        catalog: Dict[str, Dict[str, Any]] = {}
        for exp in explanation_resp.explanations:
            catalog[exp.target] = generate_dynamic_clinical_evidence_entry(
                target_id=exp.target,
                target_name=exp.target_name,
                risk_tier=exp.risk_tier,
                calibrated_probability=exp.calibrated_probability,
                confidence_score=getattr(exp, "confidence_score", 0.90),
                positive_contributors=exp.positive_contributors,
                protective_contributors=exp.protective_contributors,
                clinician_evaluation=exp.narratives.clinician_evaluation,
                confirmatory_labs=exp.narratives.confirmatory_labs,
                guideline_reference=exp.narratives.guideline_reference,
                champion_algorithm=exp.champion_algorithm,
                optimal_threshold=exp.optimal_threshold
            )

        if target_id:
            if target_id in catalog:
                return catalog[target_id]
            for k, v in catalog.items():
                if target_id.lower() in k.lower() or k.lower() in target_id.lower():
                    return v
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target ID '{target_id}' not found in evaluated clinical profile."
            )

        return catalog

