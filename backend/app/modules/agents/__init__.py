"""
Multi-Agent Clinical Intelligence Module
"""

from .schemas import (
    AgentProfile,
    SpecialistPerspective,
    DebateTurn,
    AgentAgreementScore,
    ConsensusProtocol,
    MultiAgentConsultationResponse,
    AgentDebateRequest
)
from .service import MultiAgentService
from .router import router

__all__ = [
    "AgentProfile",
    "SpecialistPerspective",
    "DebateTurn",
    "AgentAgreementScore",
    "ConsensusProtocol",
    "MultiAgentConsultationResponse",
    "AgentDebateRequest",
    "MultiAgentService",
    "router"
]
