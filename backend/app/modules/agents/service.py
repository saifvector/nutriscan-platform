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
        """Executes a full 7-agent consultation and produces consensus protocol."""
        return ConsensusCoordinatorAgent.run_consultation(patient_payload)

    @classmethod
    def run_debate(cls, request: AgentDebateRequest, patient_payload: Dict[str, Any]) -> List[DebateTurn]:
        """Generates dynamic debate turns between requested agents on a clinical topic."""
        full_consult = ConsensusCoordinatorAgent.run_consultation(patient_payload)
        filtered_turns = [
            turn for turn in full_consult.debate_transcript
            if any(agent_key in turn.speaker_id for agent_key in request.agent_ids) or "coordinator" in turn.speaker_id
        ]
        return filtered_turns[:request.max_turns]
