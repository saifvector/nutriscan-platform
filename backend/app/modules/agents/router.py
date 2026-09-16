"""
Multi-Agent Clinical Intelligence API Router
Exposes enterprise endpoints for:
- /api/v1/agents/roster
- /api/v1/agents/consult
- /api/v1/agents/debate
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    AgentProfile,
    MultiAgentConsultationResponse,
    DebateTurn,
    AgentDebateRequest
)
from .service import MultiAgentService

router = APIRouter(prefix="/agents", tags=["Multi-Agent Clinical Intelligence"])


@router.get("/roster", response_model=List[AgentProfile])
async def get_agent_roster():
    """Retrieves metadata, specialty domains, and credentials for all 7 clinical specialist agents."""
    return MultiAgentService.get_agent_roster()


@router.post("/consult", response_model=MultiAgentConsultationResponse)
async def conduct_multi_agent_consultation(payload: Dict[str, Any]):
    """
    Executes an interdisciplinary clinical consultation across 6 specialist agents
    and the Consensus Coordinator, returning individual perspectives, debate transcript,
    inter-agent agreement matrix, and consensus protocol.
    """
    try:
        return MultiAgentService.consult(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent consultation error: {str(e)}"
        )


@router.post("/debate", response_model=List[DebateTurn])
async def conduct_targeted_debate(request: AgentDebateRequest, payload: Dict[str, Any]):
    """
    Simulates a targeted multi-turn clinical debate between specific specialist agents
    on a designated topic.
    """
    try:
        return MultiAgentService.run_debate(request, payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Targeted agent debate error: {str(e)}"
        )
