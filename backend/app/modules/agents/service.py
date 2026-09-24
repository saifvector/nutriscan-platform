"""
Multi-Agent Clinical Intelligence Service Facade
Provides centralized access to agent rosters, consultations, and multi-turn clinical debates.
"""

from typing import Dict, Any, List
from .schemas import (
    AgentProfile,
    MultiAgentConsultationResponse,
    DebateTurn,
    AgentDebateRequest
)
from .specialists import (
    NutritionSpecialistAgent,
    SupplementSpecialistAgent,
    LaboratoryInterpretationAgent,
    ClinicalSafetyAgent,
    DifferentialDiagnosisAgent,
    OutcomeOptimizationAgent
)
from .consensus_coordinator import ConsensusCoordinatorAgent


class MultiAgentService:
    """Service facade for the Multi-Agent Clinical Reasoning System."""

    @classmethod
    def get_agent_roster(cls) -> List[AgentProfile]:
        """Returns the full roster of the 7 autonomous clinical reasoning agents."""
        return [
            NutritionSpecialistAgent.profile,
            SupplementSpecialistAgent.profile,
            LaboratoryInterpretationAgent.profile,
            ClinicalSafetyAgent.profile,
            DifferentialDiagnosisAgent.profile,
            OutcomeOptimizationAgent.profile,
            ConsensusCoordinatorAgent.profile
        ]

    @classmethod
    def consult(cls, patient_payload: Dict[str, Any]) -> MultiAgentConsultationResponse:
        """Executes assessment-driven multi-specialist consultation and produces consensus protocol."""
        target_id = patient_payload.get("assessment_id") or patient_payload.get("patient_id")
        persisted_payload = None
        persisted_pred = None

        if target_id:
            try:
                from ...core.persistence import PersistenceRepository
                persisted_payload = PersistenceRepository.get_assessment(str(target_id))
                persisted_pred = PersistenceRepository.get_predictions(str(target_id))
                if not persisted_payload:
                    patient_rec = PersistenceRepository.get_patient(str(target_id))
                    if patient_rec and patient_rec.get("latest_assessment_id"):
                        persisted_payload = PersistenceRepository.get_assessment(patient_rec["latest_assessment_id"])
                        persisted_pred = PersistenceRepository.get_predictions(patient_rec["latest_assessment_id"])
            except Exception:
                pass

        # Also check fast-cache if not found
        if not persisted_payload and target_id:
            try:
                from ..explainability.service import ExplainabilityService
                persisted_payload = ExplainabilityService._active_payload_cache.get(str(target_id))
                persisted_pred = ExplainabilityService._active_predictions_cache.get(str(target_id))
            except Exception:
                pass

        effective_payload = dict(persisted_payload) if persisted_payload else dict(patient_payload)
        # Merge payload items (e.g. patient_id, symptoms)
        for k, v in patient_payload.items():
            if v is not None and (k not in effective_payload or not effective_payload[k]):
                effective_payload[k] = v

        return ConsensusCoordinatorAgent.run_consultation(effective_payload, persisted_pred)

    @classmethod
    def run_debate(cls, request: AgentDebateRequest, patient_payload: Dict[str, Any]) -> List[DebateTurn]:
        """Generates dynamic debate turns between requested agents on a clinical topic."""
        full_consult = ConsensusCoordinatorAgent.run_consultation(patient_payload)
        filtered_turns = [
            turn for turn in full_consult.debate_transcript
            if any(agent_key in turn.speaker_id for agent_key in request.agent_ids) or "coordinator" in turn.speaker_id
        ]
        return filtered_turns[:request.max_turns]
