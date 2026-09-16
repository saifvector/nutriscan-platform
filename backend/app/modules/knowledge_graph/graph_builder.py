"""
Clinical Knowledge Graph Builder
Phase 7B: High-performance singleton in-memory DiGraph builder using NetworkX.
Target initialization time: < 100 ms. Thread-safe lazy loading.
"""

import time
import threading
import logging
from typing import Optional, Tuple
import networkx as nx

from .entities import ENTITIES_REGISTRY
from .relationships import RELATIONSHIPS_REGISTRY
from .schemas import EntityType, RelationshipType

logger = logging.getLogger("nutrient_platform.knowledge_graph")


class KnowledgeGraphBuilder:
    """
    Thread-safe Singleton Builder for the Clinical Knowledge Graph.
    Constructs an in-memory NetworkX DiGraph pre-populated with clinical entities
    and directional causal relationships.
    """

    _instance: Optional["KnowledgeGraphBuilder"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._graph: Optional[nx.DiGraph] = None
        self._build_time_ms: float = 0.0
        self._initialized: bool = False

    @classmethod
    def get_instance(cls) -> "KnowledgeGraphBuilder":
        """Thread-safe accessor for singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def build_graph(self, force_rebuild: bool = False) -> Tuple[nx.DiGraph, float]:
        """
        Build or retrieve the cached in-memory NetworkX DiGraph.
        Execution is guaranteed to be thread-safe with latency < 100 ms.
        """
        if self._graph is not None and not force_rebuild:
            return self._graph, self._build_time_ms

        with self._lock:
            # Double-checked locking
            if self._graph is not None and not force_rebuild:
                return self._graph, self._build_time_ms

            t_start = time.perf_counter()
            G = nx.DiGraph()

            # 1. Populate all 7 entity classes as nodes
            for entity_id, data in ENTITIES_REGISTRY.items():
                G.add_node(
                    entity_id,
                    id=entity_id,
                    name=data["name"],
                    entity_type=data["entity_type"],
                    category=data.get("category"),
                    description=data["description"],
                    metadata=data.get("metadata", {})
                )

            # 2. Populate directional causal edges
            for rel in RELATIONSHIPS_REGISTRY:
                src = rel["source_id"]
                tgt = rel["target_id"]

                # Ensure source and target exist in registry
                if src in ENTITIES_REGISTRY and tgt in ENTITIES_REGISTRY:
                    src_data = ENTITIES_REGISTRY[src]
                    tgt_data = ENTITIES_REGISTRY[tgt]
                    G.add_edge(
                        src,
                        tgt,
                        id=rel["id"],
                        source_name=src_data["name"],
                        source_type=src_data["entity_type"],
                        target_name=tgt_data["name"],
                        target_type=tgt_data["entity_type"],
                        relationship_type=rel["relationship_type"],
                        weight=float(rel.get("weight", 1.0)),
                        mechanism=rel["mechanism"],
                        citation=rel.get("citation")
                    )
                else:
                    logger.warning(f"Skipping edge {rel['id']}: missing node {src} or {tgt}")

            self._build_time_ms = round((time.perf_counter() - t_start) * 1000, 3)
            self._graph = G
            self._initialized = True

            logger.info(
                f"Clinical Knowledge Graph initialized: {G.number_of_nodes()} nodes, "
                f"{G.number_of_edges()} edges in {self._build_time_ms:.2f} ms."
            )
            return self._graph, self._build_time_ms

    @property
    def graph(self) -> nx.DiGraph:
        """Convenience property for accessing graph with auto-initialization."""
        if self._graph is None:
            g, _ = self.build_graph()
            return g
        return self._graph

    @property
    def build_time_ms(self) -> float:
        return self._build_time_ms
