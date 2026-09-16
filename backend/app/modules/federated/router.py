"""
Federated Learning API Router
Exposes enterprise endpoints for:
- /api/v1/federated/status
- /api/v1/federated/register-node
- /api/v1/federated/submit-update
- /api/v1/federated/aggregate
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    FederatedNode,
    ModelUpdatePayload,
    AggregationRoundResult,
    FederatedNetworkStatus
)
from .service import FederatedService

router = APIRouter(prefix="/federated", tags=["Federated Learning Infrastructure"])


@router.get("/status", response_model=FederatedNetworkStatus)
async def get_federated_status():
    """
    Returns global network topology, current federated round, active nodes,
    privacy budget expenditures (epsilon, delta), and recent aggregation history.
    """
    try:
        return FederatedService.get_network_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Federated status retrieval error: {str(e)}"
        )


@router.post("/register-node", response_model=FederatedNode)
async def register_node(node: FederatedNode):
    """Registers a hospital, clinic, or research institution as a federated training node."""
    try:
        return FederatedService.register_clinical_node(node)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Node registration error: {str(e)}"
        )


@router.post("/submit-update", response_model=Dict[str, Any])
async def submit_model_update(payload: ModelUpdatePayload):
    """
    Submits a locally clipped, differentially private parameter update from a clinical node.
    """
    try:
        return FederatedService.submit_node_update(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model update submission error: {str(e)}"
        )


@router.post("/aggregate", response_model=AggregationRoundResult)
async def trigger_federated_aggregation():
    """
    Executes secure weighted FedAvg aggregation across participating institutional nodes,
    advances the global model round, and generates site-specific adaptation summaries.
    """
    try:
        return FederatedService.trigger_secure_aggregation()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Secure aggregation error: {str(e)}"
        )
