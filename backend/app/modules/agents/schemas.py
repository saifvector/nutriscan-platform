"""
Multi-Agent Clinical Reasoning Schemas
Pydantic contracts for:
- Agent Profiles & Roster
- Specialist Clinical Perspectives
- Debate Turns & Dynamic Discussion
- Agreement Matrix & Conflict Detection
- Multi-Agent Consensus Protocol & Transcript
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentProfile(BaseModel):
    agent_id: str
    name: str
    role: str
    specialty_domain: str
    avatar_color: str
    core_principles: List[str] = Field(default_factory=list)
    active: bool = True


class SpecialistPerspective(BaseModel):
    agent_id: str
    agent_name: str
    specialty: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    primary_assessment: str
    key_findings: List[str] = Field(default_factory=list)
    recommended_interventions: List[str] = Field(default_factory=list)
    priority_level: str = "HIGH"  # CRITICAL, HIGH, MODERATE, LOW
    scientific_rationale: str
    concerns_or_objections: List[str] = Field(default_factory=list)


class DebateTurn(BaseModel):
    turn_id: int
    speaker_id: str
    speaker_name: str
    speaker_role: str
    addressed_to: str
    message: str
    tone: str = "COLLABORATIVE"  # COLLABORATIVE, CHALLENGING, CAUTIONARY, SYNTHESIZING
    referenced_data_point: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentAgreementScore(BaseModel):
    agent_a: str
    agent_b: str
    agreement_percentage: float = Field(ge=0.0, le=100.0)
    concordant_points: List[str] = Field(default_factory=list)
    divergent_points: List[str] = Field(default_factory=list)


class ConsensusProtocol(BaseModel):
    consultation_id: str
    patient_id: str
    patient_name: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    consensus_status: str = "UNANIMOUS_CONSENSUS"  # UNANIMOUS_CONSENSUS, SUPERMAJORITY_RATIFIED, MAJORITY_CONSENSUS, DIVERGENT_DELIBERATION
    overall_confidence: float = Field(ge=0.0, le=1.0)
    agreement_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    supporting_agent_count: int = Field(default=5, ge=0)
    total_agent_count: int = Field(default=5, ge=1)
    participating_agents: List[str]
    unified_action_plan: List[Dict[str, Any]]
    dissenting_views: List[Dict[str, str]] = Field(default_factory=list)
    reconciled_tradeoffs: List[Dict[str, str]] = Field(default_factory=list)
    monitoring_and_safeguards: List[str] = Field(default_factory=list)
    transcript_summary: str


class MultiAgentConsultationResponse(BaseModel):
    consultation_id: str
    patient_id: str
    perspectives: List[SpecialistPerspective]
    debate_transcript: List[DebateTurn]
    agreement_matrix: List[AgentAgreementScore]
    consensus_protocol: ConsensusProtocol


class AgentDebateRequest(BaseModel):
    patient_id: str
    agent_ids: List[str] = Field(default_factory=lambda: ["nutrition", "supplement", "safety"])
    clinical_topic: str = "Acute vs Chronic Repletion Strategy"
    max_turns: int = 4
