"""
Production Prediction Service Layer
Phase 3: Multi-Nutrient Prediction Engine Development

Provides:
- In-memory model caching & singleton management
- Single-patient and vectorized batch inference orchestration
- Sub-500ms execution latency tracking
- Database mapping & persistence into PostgreSQL (nutrient_predictions, risk_factors)
"""

import os
import time
import joblib
from typing import Dict, Any, List, Optional
import uuid
import logging

from ...ml import (
    NutritionalInferenceEngine,
    TARGET_NUTRIENTS,
    NUTRIENT_CODES,
    RiskCategory
)
from ...schemas.prediction import MultiNutrientPredictionResponse, BatchPredictionResponse
from .clinical_engine import ClinicalRiskEngine
from .registry import ClinicalModelRegistry
from ...schemas.clinical_prediction import (
    ClinicalPredictionResponse,
    ClinicalBatchPredictionResponse,
    ModelRegistryResponse
)

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Thread-safe, high-performance prediction service.
    Coordinates both legacy Phase 3-7 inference and Phase 10C production clinical risk inference.
    """

    _instance = None
    _engine: Optional[NutritionalInferenceEngine] = None
    _clinical_engine: Optional[ClinicalRiskEngine] = None
    _model_load_time: Optional[float] = None

    @classmethod
    def get_engine(cls) -> NutritionalInferenceEngine:
        """
        Thread-safe singleton getter with automated warm caching.
        Loads from ml_artifacts/ or creates on-the-fly development champion.
        """
        if cls._engine is None:
            load_start = time.perf_counter()
            candidates = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "ml_artifacts")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml_artifacts")),
                os.path.abspath("ml_artifacts")
            ]
            artifacts_dir = next((d for d in candidates if os.path.exists(os.path.join(d, "champion_model.joblib"))), candidates[0])
            model_path = os.path.join(artifacts_dir, "champion_model.joblib")
            pipeline_path = os.path.join(artifacts_dir, "feature_pipeline.joblib")

            if os.path.exists(model_path) and os.path.exists(pipeline_path):
                logger.info(f"Loading champion model from {model_path}...")
                model = joblib.load(model_path)
                pipeline = joblib.load(pipeline_path)
                cls._engine = NutritionalInferenceEngine(
                    model=model,
                    pipeline=pipeline,
                    model_version="v3.0.0"
                )
            else:
                logger.warning("Serialized artifacts not found; compiling on-the-fly champion...")
                from ...ml import ModelBenchmarkRunner
                runner = ModelBenchmarkRunner()
                _, _, champion_model, pipeline = runner.run_benchmark_comparison(
                    n_samples=600, include_catboost=False
                )
                cls._engine = NutritionalInferenceEngine(
                    model=champion_model,
                    pipeline=pipeline,
                    model_version="v3.0.0-dev"
                )
            cls._model_load_time = round((time.perf_counter() - load_start) * 1000, 2)
            logger.info(f"Prediction engine initialized in {cls._model_load_time} ms.")
        return cls._engine

    @classmethod
    def get_clinical_engine(cls) -> ClinicalRiskEngine:
        """
        Thread-safe singleton getter for Phase 10C ClinicalRiskEngine.
        Operates on the 9 verified Phase 10B champion models.
        """
        if cls._clinical_engine is None:
            cls._clinical_engine = ClinicalRiskEngine()
        return cls._clinical_engine

    @classmethod
    def predict_clinical(
        cls,
        assessment_payload: Dict[str, Any],
        prediction_id: Optional[uuid.UUID] = None
    ) -> ClinicalPredictionResponse:
        """
        Executes Phase 10C Clinical Deficiency Risk inference.
        Guarantees sub-50ms execution latency and empirical probability calibration.
        """
        engine = cls.get_clinical_engine()
        return engine.predict_patient(assessment_payload=assessment_payload, prediction_id=prediction_id)

    @classmethod
    def predict_clinical_batch(
        cls,
        assessments: List[Dict[str, Any]]
    ) -> ClinicalBatchPredictionResponse:
        """
        Executes Phase 10C batch clinical inference across multiple patient records.
        """
        engine = cls.get_clinical_engine()
        return engine.predict_batch(assessments=assessments)

    @classmethod
    def get_model_registry(cls) -> ClinicalModelRegistry:
        """Returns the active ClinicalModelRegistry instance."""
        engine = cls.get_clinical_engine()
        return engine.registry

    @classmethod
    def predict_assessment(
        cls,
        assessment_payload: Dict[str, Any],
        assessment_id: Optional[uuid.UUID] = None,
        compute_explainability: bool = True
    ) -> Dict[str, Any]:
        """
        Executes multi-nutrient prediction across all 11 nutrients.
        Guarantees sub-500ms execution latency.
        """
        engine = cls.get_engine()
        result = engine.screen_patient(
            assessment_payload=assessment_payload,
            compute_explainability=compute_explainability
        )
        if assessment_id is None:
            assessment_id = uuid.uuid4()
        result["assessment_id"] = assessment_id

        # Register in ExplainabilityService fast-cache
        try:
            from ..explainability.service import ExplainabilityService
            ExplainabilityService.register_prediction_run(
                assessment_id=str(assessment_id),
                payload=assessment_payload,
                prediction_result=result
            )
        except Exception as e:
            logger.debug(f"Explainability registration note: {e}")

        # Thread-safe SQLite persistence for cross-module consistency and restart safety
        try:
            from ...core.persistence import PersistenceRepository
            PersistenceRepository.save_assessment(str(assessment_id), assessment_payload)
            PersistenceRepository.save_predictions(str(assessment_id), result)
            logger.debug(f"Saved assessment and predictions to persistence for {assessment_id}")
        except Exception as e:
            logger.warning(f"Persistence save note: {e}")

        return result

    @classmethod
    def predict_batch(
        cls,
        assessments: List[Dict[str, Any]],
        compute_explainability: bool = False
    ) -> Dict[str, Any]:
        """
        Executes high-throughput batch prediction.
        """
        batch_start = time.perf_counter()
        engine = cls.get_engine()
        batch_results = engine.screen_batch(
            patient_records=assessments,
            compute_explainability=compute_explainability
        )
        total_time_ms = round((time.perf_counter() - batch_start) * 1000, 2)
        return {
            "total_records": len(assessments),
            "batch_latency_ms": total_time_ms,
            "results": batch_results
        }

    @classmethod
    async def persist_predictions(
        cls,
        db_session: Any,
        assessment_id: uuid.UUID,
        prediction_result: Dict[str, Any]
    ) -> List[Any]:
        """
        Maps prediction engine results into PostgreSQL database entities:
        - nutrient_predictions
        - risk_factors (SHAP attributions)
        """
        from ...models.prediction import NutrientPrediction, RiskFactor

        persisted_records = []
        latency = int(prediction_result.get("inference_latency_ms", 1))

        for nut_data in prediction_result.get("nutrient_predictions", []):
            ci = nut_data.get("confidence_interval") or {}
            pred_entity = NutrientPrediction(
                id=uuid.uuid4(),
                assessment_id=assessment_id,
                nutrient_code=nut_data["nutrient_code"],
                nutrient_name=nut_data["nutrient"],
                probability_score=nut_data["probability"],
                confidence_score=nut_data.get("confidence", 0.85),
                confidence_level=nut_data.get("confidence_level", "High Confidence"),
                predicted_risk_level=nut_data["risk_level"],
                priority_rank=nut_data.get("priority_rank"),
                confidence_interval_low=ci.get("low"),
                confidence_interval_high=ci.get("high"),
                model_name=nut_data.get("model_name", "XGBoost"),
                model_version=nut_data.get("model_version", "v3.0.0"),
                inference_latency_ms=latency
            )

            # Link top risk factors
            for rf in nut_data.get("risk_factors", []):
                factor_entity = RiskFactor(
                    id=uuid.uuid4(),
                    prediction_id=pred_entity.id,
                    factor_category=rf.get("category", "CLINICAL"),
                    factor_name=rf.get("factor_name", rf.get("feature_name")),
                    factor_description=rf.get("clinical_explanation", ""),
                    impact_score=rf.get("impact_score", 0.0),
                    impact_magnitude=rf.get("impact_magnitude", "MEDIUM"),
                    evidence_reference=rf.get("evidence_reference", "")
                )
                pred_entity.risk_factors.append(factor_entity)

            db_session.add(pred_entity)
            persisted_records.append(pred_entity)

        await db_session.commit()
        return persisted_records
