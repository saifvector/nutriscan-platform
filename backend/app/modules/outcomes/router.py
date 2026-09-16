"""
Outcome Learning & Adaptive Nutrition REST API Router
Phase 9: Outcome Learning & Adaptive Nutrition Intelligence

Endpoints:
- GET  /api/v1/outcomes/adherence
- GET  /api/v1/outcomes/adherence/{assessment_id}
- GET  /api/v1/outcomes/symptoms
- GET  /api/v1/outcomes/symptoms/{assessment_id}
- GET  /api/v1/outcomes/labs
- GET  /api/v1/outcomes/labs/{assessment_id}
- GET  /api/v1/outcomes/recovery
- GET  /api/v1/outcomes/recovery/{assessment_id}
- GET  /api/v1/outcomes/effectiveness
- GET  /api/v1/outcomes/effectiveness/{assessment_id}
- GET  /api/v1/outcomes/risk-monitoring
- GET  /api/v1/outcomes/risk-monitoring/{assessment_id}
- GET  /api/v1/outcomes/prediction-accuracy
- GET  /api/v1/outcomes/accuracy/{assessment_id}
- GET  /api/v1/outcomes/prediction-accuracy/{assessment_id}
- GET  /api/v1/outcomes/adaptive-plans
- GET  /api/v1/outcomes/adaptive/{assessment_id}
- POST /api/v1/outcomes/log-adherence / POST /api/v1/outcomes/adherence
- POST /api/v1/outcomes/log-symptoms / POST /api/v1/outcomes/symptoms
- POST /api/v1/outcomes/log-labs / POST /api/v1/outcomes/labs
- POST /api/v1/outcomes/generate-adaptation / POST /api/v1/outcomes/adaptive/generate
"""

from typing import Optional, List
from fastapi import APIRouter, Query, Path

from .schemas import (
    AdherenceLogRequest,
    AdherenceLogItem,
    AdherenceSummaryResponse,
    SymptomLogRequest,
    SymptomTimelineResponse,
    LabLogRequest,
    LabTrackingResponse,
    RecoveryStatusResponse,
    EffectivenessResponse,
    AdaptivePlanResponse,
    GenerateAdaptationRequest,
    PredictionAccuracyResponse,
    RelapseRiskResponse,
    LearningDatasetResponse
)
from .service import OutcomeIntelligenceService

router = APIRouter(prefix="/outcomes", tags=["Outcome Learning & Adaptive Intelligence"])


# ─── Adherence Intelligence ────────────────────────────────────────────────────────
@router.get(
    "/adherence",
    response_model=AdherenceSummaryResponse,
    summary="Adherence Intelligence Summary",
    description="Retrieves daily, weekly, and monthly adherence indices, category breakdown, missed items, and recovery impact."
)
async def get_adherence(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_adherence_summary(assessment_id=assessment_id or "demo")


@router.get(
    "/adherence/{assessment_id}",
    response_model=AdherenceSummaryResponse,
    summary="Adherence Intelligence by Assessment ID"
)
async def get_adherence_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_adherence_summary(assessment_id=assessment_id)


# ─── Symptom Timeline ──────────────────────────────────────────────────────────────
@router.get(
    "/symptoms",
    response_model=SymptomTimelineResponse,
    summary="Longitudinal Symptom Timeline",
    description="Tracks 9 core symptoms (0-10 severity), weekly progression velocity, and days-to-resolution forecast."
)
async def get_symptoms(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_symptom_timeline(assessment_id=assessment_id or "demo")


@router.get(
    "/symptoms/{assessment_id}",
    response_model=SymptomTimelineResponse,
    summary="Longitudinal Symptom Timeline by Assessment ID"
)
async def get_symptoms_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_symptom_timeline(assessment_id=assessment_id)


# ─── Laboratory Biomarkers ────────────────────────────────────────────────────────
@router.get(
    "/labs",
    response_model=LabTrackingResponse,
    summary="Follow-up Laboratory Biomarkers"
)
async def get_labs(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_labs(assessment_id=assessment_id or "demo")


@router.get(
    "/labs/{assessment_id}",
    response_model=LabTrackingResponse,
    summary="Follow-up Laboratory Biomarkers by Assessment ID"
)
async def get_labs_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_labs(assessment_id=assessment_id)


# ─── Clinical Recovery Status ──────────────────────────────────────────────────────
@router.get(
    "/recovery",
    response_model=RecoveryStatusResponse,
    summary="Clinical Recovery Status",
    description="Calculates baseline vs. current health score delta, recovery velocity (pts/week), and recovery status."
)
async def get_recovery(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_recovery_status(assessment_id=assessment_id or "demo")


@router.get(
    "/recovery/{assessment_id}",
    response_model=RecoveryStatusResponse,
    summary="Clinical Recovery Status by Assessment ID"
)
async def get_recovery_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_recovery_status(assessment_id=assessment_id)


# ─── Recommendation Effectiveness ──────────────────────────────────────────────────
@router.get(
    "/effectiveness",
    response_model=EffectivenessResponse,
    summary="Recommendation Effectiveness",
    description="Ranks top performing foods, supplements, and lifestyle interventions; highlights recovery accelerators vs bottlenecks."
)
async def get_effectiveness(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_effectiveness(assessment_id=assessment_id or "demo")


@router.get(
    "/effectiveness/{assessment_id}",
    response_model=EffectivenessResponse,
    summary="Recommendation Effectiveness by Assessment ID"
)
async def get_effectiveness_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_effectiveness(assessment_id=assessment_id)


# ─── Relapse & Risk Monitoring ─────────────────────────────────────────────────────
@router.get(
    "/risk-monitoring",
    response_model=RelapseRiskResponse,
    summary="Relapse & Risk Monitoring",
    description="Continuous surveillance for recovery plateaus, declining adherence, and nutrient relapse risk."
)
async def get_risk_monitoring(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_risk_monitoring(assessment_id=assessment_id or "demo")


@router.get(
    "/risk-monitoring/{assessment_id}",
    response_model=RelapseRiskResponse,
    summary="Relapse & Risk Monitoring by Assessment ID"
)
async def get_risk_monitoring_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_risk_monitoring(assessment_id=assessment_id)


# ─── Prediction Accuracy Validation ────────────────────────────────────────────────
@router.get(
    "/prediction-accuracy",
    response_model=PredictionAccuracyResponse,
    summary="Prediction Accuracy Validation",
    description="Validates predicted recovery trajectory vs. actual observed recovery (accuracy %, MAE, calibration)."
)
async def get_prediction_accuracy(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_prediction_accuracy(assessment_id=assessment_id or "demo")


@router.get(
    "/accuracy/{assessment_id}",
    response_model=PredictionAccuracyResponse,
    summary="Prediction Accuracy Validation by Assessment ID"
)
async def get_accuracy_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_prediction_accuracy(assessment_id=assessment_id)


@router.get(
    "/prediction-accuracy/{assessment_id}",
    response_model=PredictionAccuracyResponse,
    summary="Prediction Accuracy Validation by Assessment ID"
)
async def get_prediction_accuracy_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    return OutcomeIntelligenceService.get_prediction_accuracy(assessment_id=assessment_id)


# ─── Adaptive Recommendation Engine ────────────────────────────────────────────────
@router.get(
    "/adaptive-plans",
    response_model=AdaptivePlanResponse,
    summary="Active Adaptive Plans",
    description="Retrieves active dynamic adaptations, alternatives (fish avoidance, sunlight failure, supplement fatigue), and audit log."
)
async def get_adaptive_plans(
    assessment_id: Optional[str] = Query("demo", description="Assessment ID")
):
    return OutcomeIntelligenceService.get_adaptive_plans(assessment_id=assessment_id or "demo")


@router.get(
    "/adaptive/{assessment_id}",
    response_model=List[AdaptivePlanResponse],
    summary="Adaptive Plans by Assessment ID"
)
async def get_adaptive_by_id(
    assessment_id: str = Path(..., description="Assessment ID")
):
    plan = OutcomeIntelligenceService.get_adaptive_plans(assessment_id=assessment_id)
    return [plan]


# ─── Logging & Mutation Endpoints ──────────────────────────────────────────────────
@router.post(
    "/log-adherence",
    response_model=AdherenceLogItem,
    summary="Log Daily Adherence",
    description="Records compliance across meals, supplements, hydration, sunlight, sleep, and exercise."
)
async def log_adherence(request: AdherenceLogRequest):
    return OutcomeIntelligenceService.log_adherence(request)


@router.post("/adherence", response_model=AdherenceSummaryResponse, summary="Log Adherence & Return Summary")
async def post_adherence(request: AdherenceLogRequest):
    OutcomeIntelligenceService.log_adherence(request)
    return OutcomeIntelligenceService.get_adherence_summary(request.assessment_id)


@router.post(
    "/log-symptoms",
    response_model=SymptomTimelineResponse,
    summary="Log Symptom Journal",
    description="Records symptom severity ratings on a 0-10 clinical scale and updates progression velocity."
)
async def log_symptoms(request: SymptomLogRequest):
    return OutcomeIntelligenceService.log_symptoms(request)


@router.post("/symptoms", response_model=SymptomTimelineResponse, summary="Log Symptoms & Return Timeline")
async def post_symptoms(request: SymptomLogRequest):
    return OutcomeIntelligenceService.log_symptoms(request)


@router.post(
    "/log-labs",
    response_model=LabTrackingResponse,
    summary="Log Follow-Up Laboratory Values",
    description="Records follow-up biomarker panels (Ferritin, CBC, 25(OH)D, B12, Folate, etc.)."
)
async def log_labs(request: LabLogRequest):
    return OutcomeIntelligenceService.log_labs(request)


@router.post("/labs", response_model=LabTrackingResponse, summary="Log Labs & Return Tracking")
async def post_labs(request: LabLogRequest):
    return OutcomeIntelligenceService.log_labs(request)


@router.post(
    "/generate-adaptation",
    response_model=AdaptivePlanResponse,
    summary="Trigger Adaptive Recommendation Analysis",
    description="Evaluates adherence telemetry or explicit feedback to formulate dynamic alternative protocols."
)
async def generate_adaptation(request: GenerateAdaptationRequest):
    return OutcomeIntelligenceService.generate_adaptation(request)


@router.post(
    "/adaptive/generate",
    response_model=AdaptivePlanResponse,
    summary="Generate Adaptation Alias"
)
async def generate_adaptation_alias(request: GenerateAdaptationRequest):
    return OutcomeIntelligenceService.generate_adaptation(request)


# ─── Clinical Learning Dataset Builder ─────────────────────────────────────────────
@router.get(
    "/learning-dataset",
    response_model=LearningDatasetResponse,
    summary="Clinical Learning Dataset Summary",
    description="Aggregates structured longitudinal outcomes and training cohorts for offline model retraining."
)
async def get_learning_dataset():
    return OutcomeIntelligenceService.get_learning_dataset()
