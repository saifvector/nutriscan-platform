"""
FastAPI Multi-Nutrient Prediction Router
Phase 3: Multi-Nutrient Prediction Engine Development

Endpoints:
- POST /api/v1/predict: Run real-time screening prediction on incoming screening payload
- POST /api/v1/predict/batch: Vectorized batch prediction for multiple patient profiles
- GET  /api/v1/predictions/{id}: Retrieve prediction results by ID
- GET  /api/v1/predictions/rules/interactions: Active biochemical interaction catalog
- GET  /api/v1/predictions/models/benchmark: Performance metrics & benchmark reports
"""

import os
import json
from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, Depends, status, Path

from .service import PredictionService
from ...schemas.prediction import (
    MultiNutrientPredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    NutrientPredictionItem,
    OverallDeficiencySummary
)
from ...schemas.clinical_prediction import (
    ClinicalPredictionResponse,
    ClinicalBatchPredictionRequest,
    ClinicalBatchPredictionResponse,
    ModelRegistryResponse,
    ClinicalInferenceHealthResponse
)
from ...schemas.assessment import HealthAssessmentCreate
from ...ml.constants import NUTRIENT_INTERACTIONS
from ...core.auth import get_current_user_optional, require_admin, verify_resource_ownership, AuthenticatedUser, UserRole

router = APIRouter(prefix="", tags=["Multi-Nutrient Prediction Engine"])


@router.post(
    "/predict",
    response_model=Any,
    status_code=status.HTTP_200_OK,
    summary="Screen Patient & Predict Clinical Deficiencies (Authoritative Single Source of Truth)",
    description="Simultaneously evaluates 9 calibrated NHANES clinical targets via ClinicalRiskEngine, generates AssessmentPredictionSnapshot, and persists single source of truth."
)
async def predict_deficiencies(
    payload: HealthAssessmentCreate,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    """
    Accepts full 10-field clinical assessment questionnaire and executes XGBoost multi-target inference.
    """
    try:
        raw_dict = payload.model_dump()
        if current_user and "user_id" not in raw_dict:
            raw_dict["user_id"] = current_user.user_id
        result = PredictionService.predict_assessment(
            assessment_payload=raw_dict,
            compute_explainability=True
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Prediction engine execution failed: {str(e)}"
        )


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Vectorized Batch Nutrient Screening",
    description="Executes high-throughput batch inference for population-scale screenings."
)
async def predict_batch_deficiencies(batch_request: BatchPredictionRequest):
    """
    Processes a list of patient assessment records in a single optimized pass.
    """
    try:
        batch_output = PredictionService.predict_batch(
            assessments=batch_request.assessments,
            compute_explainability=False
        )
        return batch_output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch prediction failed: {str(e)}"
        )


# ==============================================================================
# PHASE 10C PRODUCTION CLINICAL RISK INFERENCE ENDPOINTS
# ==============================================================================

@router.post(
    "/predictions/predict",
    response_model=ClinicalPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Phase 10C Production Clinical Deficiency Risk Prediction",
    description="Executes calibrated inference across all 9 verified Phase 10B champion models with Platt probability calibration, risk tiering, and SHAP explainability."
)
async def predict_clinical_deficiencies(payload: Dict[str, Any]):
    """
    Accepts patient assessment payload and generates calibrated risk probabilities
    for all 9 clinical targets: Iron, Iron Deficiency Anemia, Vitamin D Deficiency,
    Vitamin D Insufficiency, Folate, Magnesium, Selenium, Potassium, and Calcium.
    """
    try:
        return PredictionService.predict_clinical(assessment_payload=payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Clinical prediction execution failed: {str(e)}"
        )


@router.post(
    "/predictions/batch",
    response_model=ClinicalBatchPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Phase 10C Production Batch Clinical Screening",
    description="Vectorized high-throughput batch inference across multiple patient records."
)
async def predict_clinical_batch(batch_request: ClinicalBatchPredictionRequest):
    """
    Processes a list of patient assessment records in high-throughput batch mode.
    """
    try:
        return PredictionService.predict_clinical_batch(assessments=batch_request.assessments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clinical batch prediction failed: {str(e)}"
        )


@router.get(
    "/predictions/models",
    response_model=ModelRegistryResponse,
    summary="Phase 10C Production Clinical Model Registry Catalog",
    description="Returns metadata, version tracking, validation metrics, and model cards for all 9 Phase 10B champion models."
)
async def get_clinical_models():
    """
    Exposes the active Model Registry catalog, versions, holdout test metrics,
    and audited optimal decision thresholds.
    """
    try:
        registry = PredictionService.get_model_registry()
        return registry.get_metadata_catalog()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch model registry: {str(e)}"
        )


@router.get(
    "/predictions/health",
    response_model=ClinicalInferenceHealthResponse,
    summary="Phase 10C Production Clinical Inference Engine Health (Lightweight)",
    description="Evaluates engine readiness and active champion models without running heavy inference."
)
async def get_clinical_health():
    """
    Lightweight health check evaluating registered models and calibrators (<10ms).
    """
    engine = PredictionService.get_clinical_engine()
    is_healthy = engine.registry.is_healthy()
    return ClinicalInferenceHealthResponse(
        status="HEALTHY" if is_healthy else "DEGRADED",
        service="Phase 10C Production Clinical Risk Engine",
        model_suite_version=engine.registry.VERSION,
        engine_warmed=True,
        registered_models_count=len(engine.registry.get_all_models()),
        benchmark_latency_ms=0.5,
        all_calibrators_loaded=is_healthy,
        memory_status="NOMINAL"
    )


@router.get(
    "/predictions/health/deep",
    response_model=ClinicalInferenceHealthResponse,
    summary="Phase 10C Production Clinical Inference Engine Deep Health & Benchmark",
    description="Executes a live benchmark inference pass across active champion models."
)
async def get_clinical_health_deep():
    """
    Deep health evaluation running a live benchmark inference pass.
    """
    import time
    start = time.perf_counter()
    engine = PredictionService.get_clinical_engine()
    dummy = {"age": 30, "gender": "FEMALE", "height_cm": 165, "weight_kg": 60}
    res = engine.predict_patient(dummy)
    bench_lat = round((time.perf_counter() - start) * 1000.0, 2)
    is_healthy = engine.registry.is_healthy()
    return ClinicalInferenceHealthResponse(
        status="HEALTHY" if is_healthy else "DEGRADED",
        service="Phase 10C Production Clinical Risk Engine",
        model_suite_version=engine.registry.VERSION,
        engine_warmed=True,
        registered_models_count=len(engine.registry.get_all_models()),
        benchmark_latency_ms=bench_lat,
        all_calibrators_loaded=is_healthy,
        memory_status="NOMINAL"
    )


# ==============================================================================
# LEGACY & PARAMETERIZED ENDPOINTS
# ==============================================================================

@router.get(
    "/predictions/rules/interactions",
    summary="List Biochemical Nutrient Interaction Rules",
    description="Returns the clinical rules catalog of nutrient synergies, antagonisms, and dependencies."
)
async def get_interaction_rules():
    formatted_rules = []
    for r in NUTRIENT_INTERACTIONS:
        formatted_rules.append({
            "nutrient_pair": list(r["pair"]),
            "interaction_type": r["type"],
            "description": r["description"],
            "compounding_multiplier": r["synergy_multiplier"],
            "clinical_action": r["clinical_action"]
        })
    return {
        "total_rules": len(formatted_rules),
        "interaction_catalog": formatted_rules
    }


@router.get(
    "/prediction/benchmarks",
    summary="Retrieve Multi-Target Model Benchmark Report",
    description="Returns pre-computed evaluation metrics, ROC-AUC, sensitivity, and calibration curves across all 11 target models."
)
async def get_model_benchmarks():
    """
    Retrieves production model performance benchmarks compiled during validation.
    """
    artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml_artifacts"))
    report_path = os.path.join(artifacts_dir, "benchmark_report.json")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)
        return {"status": "success", "benchmarks": data}
    return {"status": "pending", "message": "Benchmark report not yet compiled."}


@router.get(
    "/predictions/{prediction_id}",
    summary="Retrieve Prediction Record by ID",
    description="Fetches a previously computed prediction record, confidence scores, and SHAP drivers."
)
@router.get(
    "/predict/{prediction_id}",
    summary="Retrieve Prediction Record by ID (Alias)",
    include_in_schema=False
)
async def get_prediction_by_id(
    prediction_id: str = Path(..., min_length=1, max_length=64, description="Unique identifier of prediction record or assessment"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    """
    Retrieves stored predictions from SQLite persistence layer. Returns 404 if not found.
    """
    from ...core.persistence import PersistenceRepository
    record = PersistenceRepository.get_prediction(str(prediction_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction record for ID '{prediction_id}' not found."
        )

    # Insecure Direct Object Reference (IDOR) protection
    if current_user:
        owner_id = PersistenceRepository.get_assessment_owner(str(prediction_id))
        if owner_id:
            verify_resource_ownership(
                current_user=current_user,
                resource_user_id=owner_id,
                resource_id=str(prediction_id),
                resource_type="prediction"
            )

    return record


@router.post(
    "/pipeline/run-full-journey/{assessment_id}",
    summary="Execute Complete End-to-End Clinical Journey",
    description="Cascades from assessment -> predictions -> copilot -> recommendations -> meal plan -> forecast -> report, persisting all artifacts to SQLite."
)
async def run_full_journey(
    assessment_id: uuid.UUID = Path(..., description="Unique UUID of assessment"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        from ...core.persistence import PersistenceRepository
        if current_user:
            owner_id = PersistenceRepository.get_assessment_owner(str(assessment_id))
            if owner_id:
                verify_resource_ownership(
                    current_user=current_user,
                    resource_user_id=owner_id,
                    resource_id=str(assessment_id),
                    resource_type="assessment"
                )

        from ...core.workflow_orchestrator import ClinicalWorkflowOrchestrator
        result = ClinicalWorkflowOrchestrator.execute_full_journey(str(assessment_id))
        return {"status": "success", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical workflow orchestration failed: {str(e)}"
        )


@router.post(
    "/pipeline/reconcile-coverage",
    summary="Reconcile Database Coverage for Orphaned Assessments",
    description="Backfills missing meal plans, forecasts, and reports for existing assessments in SQLite database. Restricted to ADMIN role."
)
async def reconcile_coverage(
    max_records: int = 50,
    current_user: AuthenticatedUser = Depends(require_admin)
):
    try:
        from ...core.workflow_orchestrator import ClinicalWorkflowOrchestrator
        result = ClinicalWorkflowOrchestrator.reconcile_database_coverage(max_records=max_records)
        return {"status": "success", "reconciliation": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reconciliation failed: {str(e)}"
        )

