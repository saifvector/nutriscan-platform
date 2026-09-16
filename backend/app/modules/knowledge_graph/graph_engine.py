"""
Clinical Knowledge Graph Engine
Phase 7B: Graph operations, node indexing, subgraph extraction, and statistics.
"""

from typing import Dict, Any, List, Optional
import networkx as nx

from .graph_builder import KnowledgeGraphBuilder
from .schemas import (
    GraphEntityResponse,
    GraphRelationshipResponse,
    EntityType,
    RelationshipType,
    GraphStatsResponse
)


class KnowledgeGraphEngine:
    """
    High-level engine providing query, filtering, and conversion primitives
    over the in-memory NetworkX DiGraph.
    """

    def __init__(self) -> None:
        self.builder = KnowledgeGraphBuilder.get_instance()

    @property
    def graph(self) -> nx.DiGraph:
        return self.builder.graph

    def get_stats(self) -> GraphStatsResponse:
        """Returns topology statistics and entity distributions."""
        g = self.graph
        entity_counts: Dict[str, int] = {}
        for _, data in g.nodes(data=True):
            etype_obj = data.get("entity_type")
            etype = etype_obj.value if hasattr(etype_obj, "value") else str(etype_obj or "UNKNOWN")
            entity_counts[etype] = entity_counts.get(etype, 0) + 1

        rel_counts: Dict[str, int] = {}
        for _, _, data in g.edges(data=True):
            rtype_obj = data.get("relationship_type")
            rtype = rtype_obj.value if hasattr(rtype_obj, "value") else str(rtype_obj or "UNKNOWN")
            rel_counts[rtype] = rel_counts.get(rtype, 0) + 1

        return GraphStatsResponse(
            total_nodes=g.number_of_nodes(),
            total_edges=g.number_of_edges(),
            entity_type_counts=entity_counts,
            relationship_type_counts=rel_counts,
            is_cached=True,
            build_latency_ms=self.builder.build_time_ms
        )

    def get_node(self, node_id: str) -> Optional[GraphEntityResponse]:
        """Fetch single node by ID with Pydantic serialization."""
        g = self.graph
        if not g.has_node(node_id):
            # Try prefix match if user passed plain identifier (e.g., 'VITAMIN_D' instead of 'NUTRIENT_VITAMIN_D')
            candidates = [n for n in g.nodes if n.endswith(node_id) or n.lower() == node_id.lower()]
            if candidates:
                node_id = candidates[0]
            else:
                return None

        d = g.nodes[node_id]
        return GraphEntityResponse(
            id=node_id,
            name=d["name"],
            entity_type=d["entity_type"],
            category=d.get("category"),
            description=d["description"],
            metadata=d.get("metadata", {})
        )

    def list_entities(
        self,
        entity_type: Optional[EntityType] = None,
        search_query: Optional[str] = None
    ) -> List[GraphEntityResponse]:
        """List and filter entities by type and/or search query."""
        g = self.graph
        results: List[GraphEntityResponse] = []
        q = search_query.lower() if search_query else None

        for n, d in g.nodes(data=True):
            if entity_type and d.get("entity_type") != entity_type:
                continue
            if q and (q not in d.get("name", "").lower() and q not in d.get("description", "").lower() and q not in n.lower()):
                continue

            results.append(
                GraphEntityResponse(
                    id=n,
                    name=d["name"],
                    entity_type=d["entity_type"],
                    category=d.get("category"),
                    description=d["description"],
                    metadata=d.get("metadata", {})
                )
            )
        return sorted(results, key=lambda x: (x.entity_type, x.name))

    def list_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[GraphRelationshipResponse]:
        """List and filter relationships by source, target, or relationship type."""
        g = self.graph
        results: List[GraphRelationshipResponse] = []

        for u, v, d in g.edges(data=True):
            if source_id and u != source_id and not u.endswith(source_id):
                continue
            if target_id and v != target_id and not v.endswith(target_id):
                continue
            if relationship_type and d.get("relationship_type") != relationship_type:
                continue

            results.append(
                GraphRelationshipResponse(
                    id=d["id"],
                    source_id=u,
                    source_name=d["source_name"],
                    source_type=d["source_type"],
                    target_id=v,
                    target_name=d["target_name"],
                    target_type=d["target_type"],
                    relationship_type=d["relationship_type"],
                    weight=d.get("weight", 1.0),
                    mechanism=d["mechanism"],
                    citation=d.get("citation")
                )
            )
        return sorted(results, key=lambda x: (x.source_type, x.relationship_type))
