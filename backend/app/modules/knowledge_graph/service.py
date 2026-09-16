"""
Clinical Knowledge Graph Service
Phase 7B: Business orchestration layer interfacing between FastAPI router and graph algorithms.
"""

from typing import List, Optional
from .graph_engine import KnowledgeGraphEngine
from .graph_queries import KnowledgeGraphQueries
from .centrality import CentralityAnalyzer
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


class KnowledgeGraphService:
    """
    Singleton service exposing all clinical knowledge graph capabilities.
    """

    _instance: Optional["KnowledgeGraphService"] = None

    def __init__(self) -> None:
        self.engine = KnowledgeGraphEngine()
        self.queries = KnowledgeGraphQueries(self.engine)
        self.analyzer = CentralityAnalyzer(self.engine)

    @classmethod
    def get_service(cls) -> "KnowledgeGraphService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_stats(self) -> GraphStatsResponse:
        return self.engine.get_stats()

    def get_entity(self, entity_id: str) -> Optional[GraphEntityResponse]:
        return self.engine.get_node(entity_id)

    def list_entities(
        self,
        entity_type: Optional[EntityType] = None,
        search_query: Optional[str] = None
    ) -> List[GraphEntityResponse]:
        return self.engine.list_entities(entity_type=entity_type, search_query=search_query)

    def list_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[GraphRelationshipResponse]:
        return self.engine.list_relationships(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type
        )

    def get_nutrient_network(self, nutrient_id: str) -> Optional[NutrientNetworkSubgraphResponse]:
        return self.queries.get_nutrient_subgraph(nutrient_id)

    def get_nutrient_influence(self, nutrient_id: str, max_hops: int = 2) -> NutrientInfluenceResponse:
        return self.queries.get_influence_radius(nutrient_id, max_hops=max_hops)

    def get_shortest_path(self, source_id: str, target_id: str) -> ShortestPathResponse:
        return self.queries.get_shortest_path(source_id=source_id, target_id=target_id)

    def get_centrality_rankings(self) -> CentralityAnalysisResponse:
        return self.analyzer.analyze_centrality()

    def get_system_impact(self, system_id: str) -> Optional[SystemImpactResponse]:
        return self.analyzer.analyze_system_impact(system_id)
