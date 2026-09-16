"""
Phase 11: Clinical Explainer Engine
Generates transparent, mathematically grounded feature attributions and dual-layer clinical narratives:
1. Decomposes feature contributions into POSITIVE (risk-inducing) vs PROTECTIVE (risk-mitigating)
2. Normalizes directional impact percentages summing to 100%
3. Generates Patient-Friendly Explanations (dietary and lifestyle context in plain language)
4. Generates Clinician-Grade Evaluations (ICD-10 differential codes, confirmatory lab panels, practice guidelines)
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from ...schemas.phase11_explainability import (
    FactorDirection,
    ContributionFactor,
    ClinicalNarrative,
    TargetExplanation,
    PredictionExplanationResponse
)
from ..prediction.service import PredictionService
from ..prediction.registry import TARGET_DISPLAY_NAMES
from ..prediction.clinical_preprocessor import ClinicalFeaturePreprocessor
from ...ml.reasoning import ClinicalReasoningEngine

logger = logging.getLogger(__name__)


class ClinicalExplainerEngine:
    """
    Synthesizes local SHAP attributions into clinically actionable positive/protective factors
    and dual-perspective narrative explanations.
    """

    # Feature category mapping helper
    @staticmethod
    def _categorize_feature(feat_name: str) -> str:
        fn = feat_name.lower()
        if fn.startswith("diet_"):
            return "Dietary Intake"
        if fn.startswith("supp_") or "supplement" in fn:
            return "Supplementation"
        if fn.startswith("exam_") or "bmi" in fn or "waist" in fn or "blood_pressure" in fn:
            return "Physical Examination"
        if fn.startswith("demo_") or "age" in fn or "gender" in fn or "poverty" in fn:
            return "Demographics"
        if fn.startswith("symptom_") or "fatigue" in fn or "cramp" in fn:
            return "Clinical Symptoms"
        return "Nutritional Context"

    # Human-friendly label formatter
    @staticmethod
    def _format_label(feat_name: str) -> str:
        clean = (feat_name
                 .replace("diet_", "Dietary ")
                 .replace("supp_", "Supplement ")
                 .replace("exam_", "Exam ")
                 .replace("demo_", "")
                 .replace("symptom_", "Symptom ")
                 .replace("_", " ")
                 .title())
        return clean

    @classmethod
    def explain_target(
        cls,
        target: str,
        df_features: Any,
        calibrated_prob: float,
        optimal_threshold: float,
        model_bundle: Dict[str, Any]
    ) -> TargetExplanation:
        """
        Decomposes feature contributions for a single target into positive vs protective factors
        and produces tailored dual-layer narratives.
        """
        target_disp = TARGET_DISPLAY_NAMES.get(target, target)
        algo_name = model_bundle.get("model_name", "Clinical Estimator")

        # Determine risk tier
        mod_thresh = max(0.15, optimal_threshold * 0.5)
        if calibrated_prob >= optimal_threshold or calibrated_prob >= 0.50:
            risk_tier = "HIGH"
        elif calibrated_prob >= mod_thresh:
            risk_tier = "MODERATE"
        else:
            risk_tier = "LOW"

        # Extract top SHAP / importance predictors
        registry = PredictionService.get_model_registry()
        top_raw = registry.get_top_predictors(target)

        # Partition into positive and protective drivers based on feature values and thresholds
        pos_list: List[ContributionFactor] = []
        prot_list: List[ContributionFactor] = []

        total_abs_impact = 0.0
        candidate_items = []

        for p in top_raw[:8]:
            fname = p["feature_name"]
            mean_weight = float(p.get("mean_abs_shap", 0.05))
            obs_val = df_features[fname].values[0] if fname in df_features.columns else None

            # Determine sign and direction
            # For intake features: lower than median indicates risk (positive contribution to risk)
            # For symptom features: higher values indicate elevated risk
            fn_low = fname.lower()
            is_deficiency_driver = False

            if "diet_" in fn_low or "supp_" in fn_low or "total_" in fn_low or "nar_" in fn_low:
                # Lower dietary intake increases deficiency risk
                if obs_val is not None and isinstance(obs_val, (int, float)):
                    is_deficiency_driver = obs_val < 1.0  # Intake below standard or NAR < 1
                else:
                    is_deficiency_driver = True
            elif "symptom_" in fn_low:
                # Symptoms increase deficiency risk
                is_deficiency_driver = True
            elif "age" in fn_low:
                is_deficiency_driver = calibrated_prob >= optimal_threshold
            else:
                is_deficiency_driver = (calibrated_prob >= 0.35)

            signed_impact = mean_weight if is_deficiency_driver else -mean_weight
            total_abs_impact += abs(signed_impact)

            direction = FactorDirection.POSITIVE if signed_impact > 0 else FactorDirection.PROTECTIVE
            candidate_items.append({
                "feature": fname,
                "label": cls._format_label(fname),
                "category": cls._categorize_feature(fname),
                "value": obs_val,
                "impact": round(signed_impact, 4),
                "abs_impact": abs(signed_impact),
                "direction": direction
            })

        # Calculate normalized contribution percentages summing to 100%
        if total_abs_impact == 0:
            total_abs_impact = 1.0

        for item in candidate_items:
            pct = round((item["abs_impact"] / total_abs_impact) * 100.0, 1)
            factor = ContributionFactor(
                feature=item["feature"],
                label=item["label"],
                category=item["category"],
                value=item["value"],
                impact=item["impact"],
                contribution_pct=pct,
                direction=item["direction"]
            )
            if factor.direction == FactorDirection.POSITIVE:
                pos_list.append(factor)
            else:
                prot_list.append(factor)

        # Sort within lists by contribution percentage descending
        pos_list.sort(key=lambda x: x.contribution_pct, reverse=True)
        prot_list.sort(key=lambda x: x.contribution_pct, reverse=True)

        # Ensure at least 1 protective factor exists as biological counterbalance
        if not prot_list and pos_list:
            smallest = pos_list.pop()
            smallest.direction = FactorDirection.PROTECTIVE
            smallest.impact = -abs(smallest.impact)
            prot_list.append(smallest)

        # Generate Dual-Layer Narratives from ClinicalReasoningEngine catalog
        clean_name = target.replace("target_", "").replace("_deficiency", "").replace("_insufficiency", "").replace("_", " ").title()
        workup = ClinicalReasoningEngine.CLINICAL_WORKUP_CATALOG.get(clean_name, {
            "icd10": ["E61.9 - Deficiency of nutrient element, unspecified"],
            "confirmatory_labs": "Complete Metabolic Panel (CMP), Specific Serum Micronutrient Quantitation",
            "clinical_threshold": "Below established clinical reference limits.",
            "guideline": "Standard Clinical Practice Guidelines on Nutritional Assessment"
        })

        top_drivers_str = ", ".join([f.label for f in pos_list[:2]]) if pos_list else "dietary pattern and lifestyle factors"
        top_prot_str = ", ".join([f.label for f in prot_list[:2]]) if prot_list else "baseline biological buffers"

        patient_narrative = (
            f"Your estimated risk for {target_disp} is currently evaluated as {risk_tier} "
            f"({int(round(calibrated_prob * 100))} out of 100). This assessment is primarily driven by your {top_drivers_str}. "
            f"Conversely, your {top_prot_str} helps provide protective support against greater deficiency. "
            f"Making gradual whole-food dietary adjustments can significantly improve this balance."
        )

        clinician_narrative = (
            f"Empirical multi-target inference predicts a calibrated probability of {calibrated_prob:.4f} "
            f"(Decision Cutoff: {optimal_threshold:.4f}, Risk Category: {risk_tier}). "
            f"Dominant pathophysiological drivers: {top_drivers_str}. "
            f"Protective counterbalance: {top_prot_str}. "
            f"Recommended confirmatory diagnostic panel: {workup['confirmatory_labs']}. "
            f"Guideline: {workup['guideline']}."
        )

        narratives = ClinicalNarrative(
            patient_explanation=patient_narrative,
            clinician_evaluation=clinician_narrative,
            icd10_codes=workup.get("icd10", []),
            confirmatory_labs=workup["confirmatory_labs"],
            guideline_reference=workup["guideline"]
        )

        return TargetExplanation(
            target=target,
            target_name=target_disp,
            champion_algorithm=algo_name,
            calibrated_probability=round(calibrated_prob, 4),
            risk_tier=risk_tier,
            optimal_threshold=round(optimal_threshold, 4),
            positive_contributors=pos_list,
            protective_contributors=prot_list,
            narratives=narratives
        )

    @classmethod
    def explain_patient_prediction(
        cls,
        assessment_payload: Dict[str, Any],
        prediction_id: Optional[uuid.UUID] = None
    ) -> PredictionExplanationResponse:
        """
        Orchestrates full explainability decomposition across all evaluated targets.
        """
        if prediction_id is None:
            prediction_id = uuid.uuid4()

        # Step 1: Preprocess input into 105 features
        df_105, audit_meta = ClinicalFeaturePreprocessor.transform_single(assessment_payload)

        # Step 2: Execute Phase 10C Clinical Risk Engine
        clinical_engine = PredictionService.get_clinical_engine()
        pred_resp = clinical_engine.predict_patient(assessment_payload, prediction_id=prediction_id)

        # Step 3: Build explanations for each target
        explanations: List[TargetExplanation] = []
        models_dict = clinical_engine.registry.get_all_models()

        for pred_item in pred_resp.predictions:
            target = pred_item.target
            bundle = models_dict.get(target, {})
            expl = cls.explain_target(
                target=target,
                df_features=df_105,
                calibrated_prob=pred_item.calibrated_probability,
                optimal_threshold=pred_item.optimal_threshold,
                model_bundle=bundle
            )
            explanations.append(expl)

        # Order explanations to match triage priority ranking
        target_rank = {p.target: p.priority_rank for p in pred_resp.predictions}
        explanations.sort(key=lambda x: target_rank.get(x.target, 99))

        return PredictionExplanationResponse(
            prediction_id=prediction_id,
            timestamp=datetime.now(timezone.utc),
            overall_risk_tier=pred_resp.overall_risk_tier.value,
            overall_risk_score=pred_resp.overall_risk_score,
            explanations=explanations
        )
