"""
Clinical Knowledge Graph Queries
Phase 7B: Graph traversal algorithms (Neighbors, Shortest Path, Influence Radius, Explorer).
"""

from typing import List, Dict, Any, Optional
import networkx as nx

from .graph_engine import KnowledgeGraphEngine
from .schemas import (
    GraphEntityResponse,
    GraphRelationshipResponse,
    ShortestPathResponse,
    PathHop,
    InfluenceRadiusNode,
    NutrientInfluenceResponse,
    NutrientNetworkSubgraphResponse,
    SubgraphCounts,
    EntityType,
    RelationshipType
)


class KnowledgeGraphQueries:
    """
    Core graph querying and causal traversal engine.
    """

    def __init__(self, engine: Optional[KnowledgeGraphEngine] = None) -> None:
        self.engine = engine or KnowledgeGraphEngine()

    @property
    def graph(self) -> nx.DiGraph:
        return self.engine.graph

    def normalize_node_id(self, node_id: str) -> Optional[str]:
        """Resolve full node ID from input string (handling short codes or exact IDs)."""
        g = self.graph
        if g.has_node(node_id):
            return node_id
        # Check case-insensitive exact match
        for n in g.nodes:
            if n.lower() == node_id.lower():
                return n
        # Check suffix or contains
        candidates = [n for n in g.nodes if n.endswith(node_id) or node_id.lower() in n.lower()]
        return candidates[0] if candidates else None

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "both",
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> List[GraphRelationshipResponse]:
        """
        Retrieve 1-hop connected edges and neighbor nodes.
        direction: 'both' | 'outgoing' | 'incoming'
        """
        g = self.graph
        nid = self.normalize_node_id(node_id)
        if not nid:
            return []

        results: List[GraphRelationshipResponse] = []

        # Outgoing edges
        if direction in ("both", "outgoing"):
            for _, v, d in g.out_edges(nid, data=True):
                if relationship_types and d.get("relationship_type") not in relationship_types:
                    continue
                results.append(
                    GraphRelationshipResponse(
                        id=d["id"],
                        source_id=nid,
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

        # Incoming edges
        if direction in ("both", "incoming"):
            for u, _, d in g.in_edges(nid, data=True):
                if relationship_types and d.get("relationship_type") not in relationship_types:
                    continue
                results.append(
                    GraphRelationshipResponse(
                        id=d["id"],
                        source_id=u,
                        source_name=d["source_name"],
                        source_type=d["source_type"],
                        target_id=nid,
                        target_name=d["target_name"],
                        target_type=d["target_type"],
                        relationship_type=d["relationship_type"],
                        weight=d.get("weight", 1.0),
                        mechanism=d["mechanism"],
                        citation=d.get("citation")
                    )
                )

        return results

    def get_shortest_path(self, source_id: str, target_id: str) -> ShortestPathResponse:
        """
        Find shortest causal path between two entities.
        Prioritizes directed reachability; falls back to undirected traversal if direct edge is reversed.
        """
        g = self.graph
        src = self.normalize_node_id(source_id)
        tgt = self.normalize_node_id(target_id)

        if not src or not tgt:
            return ShortestPathResponse(
                source_id=source_id,
                source_name=source_id,
                target_id=target_id,
                target_name=target_id,
                path_length=0,
                exists=False,
                hops=[],
                node_sequence=[],
                clinical_summary=f"Entity '{source_id if not src else target_id}' could not be located in knowledge graph."
            )

        src_name = g.nodes[src]["name"]
        tgt_name = g.nodes[tgt]["name"]

        # 1. Attempt directed path
        path_nodes: List[str] = []
        is_directed = True
        try:
            path_nodes = nx.shortest_path(g, source=src, target=tgt)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # 2. Attempt undirected path
            try:
                undirected_g = g.to_undirected()
                path_nodes = nx.shortest_path(undirected_g, source=src, target=tgt)
                is_directed = False
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                path_nodes = []

        if not path_nodes or len(path_nodes) < 2:
            return ShortestPathResponse(
                source_id=src,
                source_name=src_name,
                target_id=tgt,
                target_name=tgt_name,
                path_length=0,
                exists=False,
                hops=[],
                node_sequence=[src] if path_nodes else [],
                clinical_summary=f"No clinical connection established between {src_name} and {tgt_name}."
            )

        # Build step-by-step hops
        hops: List[PathHop] = []
        summary_lines: List[str] = []

        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]

            # Check edge in forward direction, else reverse
            if g.has_edge(u, v):
                edge_data = g.edges[u, v]
                step_u, step_v = u, v
            else:
                edge_data = g.edges[v, u]
                step_u, step_v = v, u

            hop = PathHop(
                step=i + 1,
                source_id=step_u,
                source_name=g.nodes[step_u]["name"],
                source_type=g.nodes[step_u]["entity_type"],
                target_id=step_v,
                target_name=g.nodes[step_v]["name"],
                target_type=g.nodes[step_v]["entity_type"],
                relationship_type=edge_data["relationship_type"],
                mechanism=edge_data["mechanism"],
                citation=edge_data.get("citation")
            )
            hops.append(hop)
            summary_lines.append(f"{hop.source_name} --({hop.relationship_type})--> {hop.target_name}")

        narrative = " ➔ ".join(g.nodes[n]["name"] for n in path_nodes)
        clinical_summary = f"Causal Pathway: {narrative}. " + " | ".join(
            f"Step {h.step}: {h.mechanism}" for h in hops
        )

        return ShortestPathResponse(
            source_id=src,
            source_name=src_name,
            target_id=tgt,
            target_name=tgt_name,
            path_length=len(hops),
            exists=True,
            hops=hops,
            node_sequence=path_nodes,
            clinical_summary=clinical_summary
        )

    def get_influence_radius(self, node_id: str, max_hops: int = 2) -> NutrientInfluenceResponse:
        """
        Compute all downstream reachable entities up to max_hops from the target node.
        Attenuates weight based on chain length.
        """
        g = self.graph
        nid = self.normalize_node_id(node_id)
        if not nid:
            return NutrientInfluenceResponse(
                nutrient_id=node_id,
                nutrient_name=node_id,
                max_hops=max_hops,
                total_downstream_entities=0,
                influence_score=0.0,
                affected_symptoms=[],
                affected_systems=[],
                downstream_nodes=[]
            )

        node_name = g.nodes[nid]["name"]

        # BFS downstream traversal up to max_hops
        visited: Dict[str, Dict[str, Any]] = {}
        queue: List[tuple] = [(nid, 0, 1.0, [])]  # (current_node, current_hop, current_weight, path_rels)

        while queue:
            curr, hops, weight, path = queue.pop(0)
            if hops >= max_hops:
                continue

            for _, target, data in g.out_edges(curr, data=True):
                edge_weight = float(data.get("weight", 1.0))
                effective_weight = weight * edge_weight
                rel_type = data.get("relationship_type", "ASSOCIATED_WITH")
                new_path = path + [rel_type]

                if target not in visited or visited[target]["effective_weight"] < effective_weight:
                    visited[target] = {
                        "hop_distance": hops + 1,
                        "effective_weight": round(effective_weight, 3),
                        "relationship_path": new_path
                    }
                    queue.append((target, hops + 1, effective_weight, new_path))

        downstream_nodes: List[InfluenceRadiusNode] = []
        affected_symptoms: List[str] = []
        affected_systems: List[str] = []
        total_influence = 0.0

        for target_id, info in visited.items():
            t_data = g.nodes[target_id]
            t_name = t_data["name"]
            t_type = t_data["entity_type"]

            downstream_nodes.append(
                InfluenceRadiusNode(
                    node_id=target_id,
                    name=t_name,
                    entity_type=t_type,
                    hop_distance=info["hop_distance"],
                    relationship_path=info["relationship_path"],
                    effective_weight=info["effective_weight"]
                )
            )

            total_influence += info["effective_weight"]
            if t_type == EntityType.SYMPTOM and t_name not in affected_symptoms:
                affected_symptoms.append(t_name)
            elif t_type == EntityType.BIOLOGICAL_SYSTEM and t_name not in affected_systems:
                affected_systems.append(t_name)

        downstream_nodes.sort(key=lambda x: (x.hop_distance, -x.effective_weight))

        return NutrientInfluenceResponse(
            nutrient_id=nid,
            nutrient_name=node_name,
            max_hops=max_hops,
            total_downstream_entities=len(downstream_nodes),
            influence_score=round(total_influence, 2),
            affected_symptoms=affected_symptoms,
            affected_systems=affected_systems,
            downstream_nodes=downstream_nodes
        )

    def get_nutrient_subgraph(self, nutrient_id: str) -> Optional[NutrientNetworkSubgraphResponse]:
        """
        Extract the complete 1-hop ego network surrounding a specific nutrient,
        categorizing connected entities into Symptoms, Foods, Lifestyle Drivers, Lab Tests, and Systems.
        """
        g = self.graph
        nid = self.normalize_node_id(nutrient_id)
        if not nid:
            return None

        center_data = g.nodes[nid]
        nodes_map: Dict[str, GraphEntityResponse] = {
            nid: GraphEntityResponse(
                id=nid,
                name=center_data["name"],
                entity_type=center_data["entity_type"],
                category=center_data.get("category"),
                description=center_data["description"],
                metadata=center_data.get("metadata", {})
            )
        }

        edges_list: List[GraphRelationshipResponse] = []
        categorized: Dict[str, List[GraphEntityResponse]] = {
            "symptoms": [],
            "foods": [],
            "lifestyle_factors": [],
            "medical_conditions": [],
            "lab_tests": [],
            "biological_systems": [],
            "nutrients": []
        }

        # Outgoing edges
        for _, v, d in g.out_edges(nid, data=True):
            v_data = g.nodes[v]
            if v not in nodes_map:
                node_resp = GraphEntityResponse(
                    id=v,
                    name=v_data["name"],
                    entity_type=v_data["entity_type"],
                    category=v_data.get("category"),
                    description=v_data["description"],
                    metadata=v_data.get("metadata", {})
                )
                nodes_map[v] = node_resp
                self._add_to_categorized(categorized, node_resp)

            edges_list.append(
                GraphRelationshipResponse(
                    id=d["id"],
                    source_id=nid,
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

        # Incoming edges
        for u, _, d in g.in_edges(nid, data=True):
            u_data = g.nodes[u]
            if u not in nodes_map:
                node_resp = GraphEntityResponse(
                    id=u,
                    name=u_data["name"],
                    entity_type=u_data["entity_type"],
                    category=u_data.get("category"),
                    description=u_data["description"],
                    metadata=u_data.get("metadata", {})
                )
                nodes_map[u] = node_resp
                self._add_to_categorized(categorized, node_resp)

            edges_list.append(
                GraphRelationshipResponse(
                    id=d["id"],
                    source_id=u,
                    source_name=d["source_name"],
                    source_type=d["source_type"],
                    target_id=nid,
                    target_name=d["target_name"],
                    target_type=d["target_type"],
                    relationship_type=d["relationship_type"],
                    weight=d.get("weight", 1.0),
                    mechanism=d["mechanism"],
                    citation=d.get("citation")
                )
            )

        counts = SubgraphCounts(
            nutrients=len(categorized["nutrients"]),
            symptoms=len(categorized["symptoms"]),
            foods=len(categorized["foods"]),
            lifestyle_factors=len(categorized["lifestyle_factors"]),
            medical_conditions=len(categorized["medical_conditions"]),
            lab_tests=len(categorized["lab_tests"]),
            biological_systems=len(categorized["biological_systems"])
        )

        return NutrientNetworkSubgraphResponse(
            center_nutrient_id=nid,
            center_nutrient_name=center_data["name"],
            nodes=list(nodes_map.values()),
            edges=edges_list,
            summary_counts=counts,
            categorized_explorer=categorized
        )

    def _add_to_categorized(self, categorized: Dict[str, List[GraphEntityResponse]], node: GraphEntityResponse) -> None:
        etype = node.entity_type
        if etype == EntityType.SYMPTOM:
            categorized["symptoms"].append(node)
        elif etype == EntityType.FOOD:
            categorized["foods"].append(node)
        elif etype == EntityType.LIFESTYLE_FACTOR:
            categorized["lifestyle_factors"].append(node)
        elif etype == EntityType.MEDICAL_CONDITION:
            categorized["medical_conditions"].append(node)
        elif etype == EntityType.LAB_TEST:
            categorized["lab_tests"].append(node)
        elif etype == EntityType.BIOLOGICAL_SYSTEM:
            categorized["biological_systems"].append(node)
        elif etype == EntityType.NUTRIENT:
            categorized["nutrients"].append(node)
