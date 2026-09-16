"""
Clinical Knowledge Graph REST API Router
Phase 7B: Endpoints mounted under /api/v1/knowledge-graph.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from .service import KnowledgeGraphService
from .schemas import (
    GraphEntityResponse,
    GraphRelationshipResponse,
    ShortestPathResponse,
    NutrientInfluenceResponse,
    NutrientNetworkSubgraphResponse,
    CentralityAnalysisResponse,
    SystemImpactResponse,
    GraphStatsResponse,
    EntityType,
    RelationshipType
)

router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Clinical Knowledge Graph & Causal Intelligence"]
)


@router.get(
    "/stats",
    response_model=GraphStatsResponse,
    summary="Get Knowledge Graph Topology Statistics",
    description="Returns node count, edge count, distributions by category, and initialization timing."
)
def get_graph_stats():
    service = KnowledgeGraphService.get_service()
    return service.get_stats()


@router.get(
    "/entities",
    response_model=List[GraphEntityResponse],
    summary="List Clinical Entities",
    description="Retrieve entities filtered by entity class (Nutrient, Symptom, Food, Lifestyle, Condition, Lab, System) or keyword search."
)
def list_entities(
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type class"),
    search: Optional[str] = Query(None, description="Case-insensitive text search across names and descriptions")
):
    service = KnowledgeGraphService.get_service()
    return service.list_entities(entity_type=entity_type, search_query=search)


@router.get(
    "/entities/{entity_id}",
    response_model=GraphEntityResponse,
    summary="Get Single Entity Details",
    description="Retrieve detailed clinical metadata, category, and properties for a specific entity ID."
)
def get_entity_details(entity_id: str):
    service = KnowledgeGraphService.get_service()
    entity = service.get_entity(entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in knowledge graph."
        )
    return entity


@router.get(
    "/relationships",
    response_model=List[GraphRelationshipResponse],
    summary="List Clinical Relationships",
    description="Filter directional causal edges by origin node, target node, or relationship predicate."
)
def list_relationships(
    source_id: Optional[str] = Query(None, description="Filter by source node ID"),
    target_id: Optional[str] = Query(None, description="Filter by target node ID"),
    relationship_type: Optional[RelationshipType] = Query(None, alias="type", description="Filter by relationship type predicate")
):
    service = KnowledgeGraphService.get_service()
    return service.list_relationships(
        source_id=source_id,
        target_id=target_id,
        relationship_type=relationship_type
    )


@router.get(
    "/nutrients/{nutrient_id}/network",
    response_model=NutrientNetworkSubgraphResponse,
    summary="Get Nutrient Ego Network Subgraph",
    description="Extracts the complete 1-hop neighborhood surrounding a nutrient, categorized into Symptoms, Foods, Lifestyle Drivers, Lab Tests, and Systems."
)
def get_nutrient_network(nutrient_id: str):
    service = KnowledgeGraphService.get_service()
    subgraph = service.get_nutrient_network(nutrient_id)
    if not subgraph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nutrient '{nutrient_id}' not found in knowledge graph."
        )
    return subgraph


@router.get(
    "/nutrients/{nutrient_id}/influence",
    response_model=NutrientInfluenceResponse,
    summary="Get Nutrient Causal Influence Radius",
    description="Traverses downstream causal links up to N hops, quantifying affected symptoms, biological systems, and effective influence weight."
)
def get_nutrient_influence(
    nutrient_id: str,
    max_hops: int = Query(2, ge=1, le=4, description="Maximum causal hop depth")
):
    service = KnowledgeGraphService.get_service()
    return service.get_nutrient_influence(nutrient_id, max_hops=max_hops)


@router.get(
    "/path",
    response_model=ShortestPathResponse,
    summary="Find Shortest Causal Pathway",
    description="Calculates the shortest biological trajectory between two entities with hop-by-hop biochemical mechanisms and literature citations."
)
def get_shortest_path(
    source: str = Query(..., description="Source entity ID (e.g. LIFESTYLE_LOW_SUN)"),
    target: str = Query(..., description="Target entity ID (e.g. SYMPTOM_BONE_PAIN)")
):
    service = KnowledgeGraphService.get_service()
    return service.get_shortest_path(source_id=source, target_id=target)


@router.get(
    "/centrality",
    response_model=CentralityAnalysisResponse,
    summary="Get Centrality Analytics & Influence Rankings",
    description="Calculates degree centrality, betweenness centrality, influence scores, and dependency scores, ranking top influential nutrients."
)
def get_centrality():
    service = KnowledgeGraphService.get_service()
    return service.get_centrality_rankings()


@router.get(
    "/systems/{system_id}",
    response_model=SystemImpactResponse,
    summary="Get Biological System Impact Breakdown",
    description="Calculates nutrient contribution percentages, physiological mechanisms, and associated deficiency symptoms for a body system."
)
def get_system_impact(system_id: str):
    service = KnowledgeGraphService.get_service()
    impact = service.get_system_impact(system_id)
    if not impact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Biological system '{system_id}' not found in knowledge graph."
        )
    return impact
