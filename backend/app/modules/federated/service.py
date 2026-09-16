"""
Federated Learning Service Facade
Centralizes status reporting, node registration, model update submission, and secure aggregation.
"""

from typing import Dict, Any, List
from .schemas import (
    FederatedNode,
    ModelUpdatePayload,
    AggregationRoundResult,
    FederatedNetworkStatus
)
from .coordinator import FederatedCoordinator


class FederatedService:
    """Service facade for Federated Learning Infrastructure."""

    @classmethod
    def get_network_status(cls) -> FederatedNetworkStatus:
        return FederatedCoordinator.get_status()

    @classmethod
    def register_clinical_node(cls, node: FederatedNode) -> FederatedNode:
        return FederatedCoordinator.register_node(node)

    @classmethod
    def submit_node_update(cls, payload: ModelUpdatePayload) -> Dict[str, Any]:
        return FederatedCoordinator.submit_update(payload)

    @classmethod
    def trigger_secure_aggregation(cls) -> AggregationRoundResult:
        return FederatedCoordinator.trigger_aggregation()
