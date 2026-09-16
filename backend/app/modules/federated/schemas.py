"""
Federated Learning Infrastructure Schemas
Pydantic contracts for:
- Federated Hospital / Institute Nodes
- Privacy-Preserving Model Parameter Updates
- Differential Privacy Budget (Epsilon, Delta)
- Secure Aggregation (FedAvg) Round State
- Site-Specific Institutional Adaptation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FederatedNode(BaseModel):
    node_id: str
    node_name: str
    institution_type: str  # ACADEMIC_MEDICAL_CENTER, REGIONAL_HEALTH_SYSTEM, COMMUNITY_CLINIC, OUTPATIENT_CONSORTIUM
    geographic_region: str
    patient_cohort_size: int
    connectivity_status: str = "ONLINE"  # ONLINE, TRAINING, OFFLINE, DEGRADED
    last_sync_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    cumulative_epsilon_spent: float = Field(default=0.45, ge=0.0)


class ModelUpdatePayload(BaseModel):
    node_id: str
    round_id: int
    sample_size: int = Field(gt=0)
    gradient_norm: float = Field(ge=0.0)
    clipped_l2_norm: float = Field(default=1.0)
    weights: Dict[str, float]  # Named parameter weights or delta
    epsilon: float = Field(default=0.5, gt=0.0)
    delta: float = Field(default=1e-5, gt=0.0)
    checksum_sha256: Optional[str] = None


class AggregationRoundResult(BaseModel):
    round_id: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    participating_nodes_count: int
    total_samples_aggregated: int
    global_model_version: str
    differential_privacy_guarantee: Dict[str, float]  # {"epsilon": 0.5, "delta": 1e-5}
    convergence_metric_loss: float
    aggregated_weights_sample: Dict[str, float]
    site_adaptation_summary: List[Dict[str, Any]]


class FederatedNetworkStatus(BaseModel):
    current_round: int
    global_model_version: str
    active_nodes_count: int
    total_network_samples: int
    privacy_budget_limit: float = 5.0
    average_epsilon_spent: float
    secure_aggregation_protocol: str = "SecAgg+ / FedAvg with Calibrated Gaussian DP"
    registered_nodes: List[FederatedNode]
    recent_round_history: List[AggregationRoundResult]
