"""
Outcome Intelligence & Adaptive Clinical Service
Phase 9: Outcome Learning & Adaptive Nutrition Intelligence

Central service orchestrator coordinating:
1. Adherence Intelligence Engine
2. Outcome Tracking Engine
3. Recommendation Effectiveness Engine
4. Adaptive Recommendation Engine
5. Symptom Recovery Timeline Engine
6. Prediction Accuracy Validation Engine
7. Relapse & Risk Monitoring Engine
8. Clinical Learning Dataset Builder
"""

from typing import Dict, Any, List, Optional
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
from .adherence import AdherenceEngine
from .tracking import OutcomeTrackingEngine
from .effectiveness import RecommendationEffectivenessEngine
from .adaptive import AdaptiveRecommendationEngine
from .symptom_timeline import SymptomRecoveryTimelineEngine
from .prediction_accuracy import PredictionAccuracyValidationEngine
from .risk_monitoring import RelapseRiskMonitoringEngine
from .learning_dataset import ClinicalLearningDatasetBuilder


class OutcomeIntelligenceService:
    """
    Central orchestration service for Phase 9 Outcome Learning & Adaptive loop.
    """

    _adherence_engine = AdherenceEngine()
    _tracking_engine = OutcomeTrackingEngine()
    _effectiveness_engine = RecommendationEffectivenessEngine()
    _adaptive_engine = AdaptiveRecommendationEngine()
    _timeline_engine = SymptomRecoveryTimelineEngine()
    _accuracy_engine = PredictionAccuracyValidationEngine()
    _risk_engine = RelapseRiskMonitoringEngine()
    _dataset_builder = ClinicalLearningDatasetBuilder()

    # 1. Adherence
    @classmethod
    def log_adherence(cls, request: AdherenceLogRequest) -> AdherenceLogItem:
        return cls._adherence_engine.log_adherence(request)

    @classmethod
    def get_adherence_summary(cls, assessment_id: str = "demo") -> AdherenceSummaryResponse:
        return cls._adherence_engine.get_adherence_summary(assessment_id)

    # 2. Symptoms & Tracking
    @classmethod
    def log_symptoms(cls, request: SymptomLogRequest) -> SymptomTimelineResponse:
        return cls._tracking_engine.log_symptoms(request)

    @classmethod
    def get_symptom_timeline(cls, assessment_id: str = "demo") -> SymptomTimelineResponse:
        return cls._timeline_engine.compute_timeline(assessment_id)

    # 3. Labs
    @classmethod
    def log_labs(cls, request: LabLogRequest) -> LabTrackingResponse:
        return cls._tracking_engine.log_labs(request)

    @classmethod
    def get_lab_tracking(cls, assessment_id: str = "demo") -> LabTrackingResponse:
        return cls._tracking_engine.get_lab_tracking(assessment_id)

    @classmethod
    def get_labs(cls, assessment_id: str = "demo") -> LabTrackingResponse:
        return cls._tracking_engine.get_lab_tracking(assessment_id)

    # 4. Recovery Status
    @classmethod
    def get_recovery_status(cls, assessment_id: str = "demo") -> RecoveryStatusResponse:
        return cls._tracking_engine.get_recovery_status(assessment_id)

    # 5. Effectiveness
    @classmethod
    def get_effectiveness(cls, assessment_id: str = "demo") -> EffectivenessResponse:
        return cls._effectiveness_engine.evaluate_effectiveness(assessment_id)

    # 6. Adaptive Recommendations
    @classmethod
    def generate_adaptation(cls, request: GenerateAdaptationRequest) -> AdaptivePlanResponse:
        return cls._adaptive_engine.generate_adaptations(request)

    @classmethod
    def get_adaptive_plans(cls, assessment_id: str = "demo") -> AdaptivePlanResponse:
        req = GenerateAdaptationRequest(assessment_id=assessment_id)
        return cls._adaptive_engine.generate_adaptations(req)

    # 7. Prediction Accuracy
    @classmethod
    def get_prediction_accuracy(cls, assessment_id: str = "demo") -> PredictionAccuracyResponse:
        return cls._accuracy_engine.validate_accuracy(assessment_id)

    # 8. Relapse & Risk Monitoring
    @classmethod
    def get_risk_monitoring(cls, assessment_id: str = "demo") -> RelapseRiskResponse:
        adherence_data = cls._adherence_engine.get_adherence_summary(assessment_id)
        return cls._risk_engine.monitor_risk(
            assessment_id=assessment_id,
            weekly_adherence=adherence_data.weekly_adherence_score,
            days_without_progress=4
        )

    # 9. Learning Dataset
    @classmethod
    def get_learning_dataset(cls) -> LearningDatasetResponse:
        return cls._dataset_builder.build_dataset_summary()

    # 10. Phase 10C Clinical Model Integration
    @classmethod
    def evaluate_clinical_baseline(
        cls,
        assessment_payload: Dict[str, Any],
        assessment_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Integrates Phase 10C verified clinical predictions as baseline reference
        for longitudinal outcome learning and accuracy validation.
        """
        from ..prediction.service import PredictionService
        clinical_pred = PredictionService.predict_clinical(assessment_payload)
        accuracy_report = cls.get_prediction_accuracy(assessment_id)
        return {
            "assessment_id": assessment_id,
            "clinical_prediction": clinical_pred,
            "outcome_accuracy_validation": accuracy_report,
            "status": "BASELINE_LINKED_TO_OUTCOMES"
        }

