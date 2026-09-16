"""
Clinical Knowledge Graph Centrality & Influence Analysis
Phase 7B: Graph analytics, degree/betweenness centrality, influence & dependency scores, and rankings.
"""

from typing import List, Dict, Any, Optional
import networkx as nx

from .graph_engine import KnowledgeGraphEngine
from .schemas import (
    NutrientCentralityItem,
    CentralityAnalysisResponse,
    SystemImpactResponse,
    SystemContributionItem,
    EntityType
)


class CentralityAnalyzer:
    """
    Computes graph topological metrics and clinical influence rankings.
    """

    def __init__(self, engine: Optional[KnowledgeGraphEngine] = None) -> None:
        self.engine = engine or KnowledgeGraphEngine()

    @property
    def graph(self) -> nx.DiGraph:
        return self.engine.graph

    def analyze_centrality(self) -> CentralityAnalysisResponse:
        """
        Compute degree centrality, betweenness centrality, influence scores,
        and dependency scores for all nutrients in the graph.
        """
        g = self.graph
        total_nodes = g.number_of_nodes()
        total_edges = g.number_of_edges()
        density = round(nx.density(g), 4)

        # Standard NetworkX centrality metrics
        deg_centrality = nx.degree_centrality(g)
        between_centrality = nx.betweenness_centrality(g, normalized=True)

        items: List[NutrientCentralityItem] = []

        # Filter to NUTRIENT entities only
        nutrient_nodes = [
            n for n, d in g.nodes(data=True) if d.get("entity_type") == EntityType.NUTRIENT
        ]

        for nid in nutrient_nodes:
            d = g.nodes[nid]
            in_deg = g.in_degree(nid)
            out_deg = g.out_degree(nid)
            tot_deg = in_deg + out_deg

            # Influence Score: weighted downstream out-degree + direct system impacts
            weighted_out = sum(
                float(edge_data.get("weight", 1.0))
                for _, _, edge_data in g.out_edges(nid, data=True)
            )
            # Add betweenness factor
            inf_score = round(weighted_out * 1.5 + (between_centrality.get(nid, 0.0) * 20.0), 2)

            # Dependency Score: upstream incoming edges (requires, contributes_to, inhibits)
            weighted_in = sum(
                float(edge_data.get("weight", 1.0))
                for _, _, edge_data in g.in_edges(nid, data=True)
            )
            dep_score = round(weighted_in * 1.2 + (in_deg * 0.5), 2)

            items.append(
                NutrientCentralityItem(
                    nutrient_id=nid,
                    nutrient_name=d["name"],
                    degree_centrality=round(deg_centrality.get(nid, 0.0), 4),
                    in_degree=in_deg,
                    out_degree=out_deg,
                    total_degree=tot_deg,
                    betweenness_centrality=round(between_centrality.get(nid, 0.0), 4),
                    influence_score=inf_score,
                    dependency_score=dep_score,
                    rank=0  # assigned below
                )
            )

        # Rank nutrients by composite influence score (descending)
        items.sort(key=lambda x: (-x.influence_score, -x.betweenness_centrality, -x.total_degree))
        for idx, item in enumerate(items):
            item.rank = idx + 1

        top_influential = items[:5]

        return CentralityAnalysisResponse(
            total_nodes=total_nodes,
            total_edges=total_edges,
            density=density,
            top_influential_nutrients=top_influential,
            all_nutrients_centrality=items
        )

    def analyze_system_impact(self, system_id: str) -> Optional[SystemImpactResponse]:
        """
        Analyze a specific biological system: connected nutrients, contribution weights,
        associated symptoms, and physiological mechanisms.
        """
        g = self.graph
        # Normalize system identifier
        target_sys = None
        for n, d in g.nodes(data=True):
            if d.get("entity_type") == EntityType.BIOLOGICAL_SYSTEM:
                if n == system_id or n.endswith(system_id) or system_id.lower() in d.get("name", "").lower():
                    target_sys = n
                    break

        if not target_sys:
            return None

        sys_data = g.nodes[target_sys]
        sys_name = sys_data["name"]

        # Find all nutrients impacting or required by this system
        connected_nutrients: List[Dict[str, Any]] = []
        mechanisms: List[str] = []

        # Incoming edges to the system (e.g. Nutrient --IMPACTS--> System)
        for u, _, edge_data in g.in_edges(target_sys, data=True):
            u_data = g.nodes[u]
            if u_data.get("entity_type") == EntityType.NUTRIENT:
                w = float(edge_data.get("weight", 1.0))
                mech = edge_data.get("mechanism", "")
                connected_nutrients.append({
                    "id": u,
                    "name": u_data["name"],
                    "weight": w,
                    "role": mech[:80] + ("..." if len(mech) > 80 else "")
                })
                if mech and mech not in mechanisms:
                    mechanisms.append(mech)

        # Outgoing edges from system (if any)
        for _, v, edge_data in g.out_edges(target_sys, data=True):
            v_data = g.nodes[v]
            if v_data.get("entity_type") == EntityType.NUTRIENT:
                w = float(edge_data.get("weight", 1.0))
                mech = edge_data.get("mechanism", "")
                connected_nutrients.append({
                    "id": v,
                    "name": v_data["name"],
                    "weight": w,
                    "role": mech[:80] + ("..." if len(mech) > 80 else "")
                })
                if mech and mech not in mechanisms:
                    mechanisms.append(mech)

        # Calculate normalized contribution percentages
        total_weight = sum(item["weight"] for item in connected_nutrients) or 1.0
        contributions: List[SystemContributionItem] = []
        for item in connected_nutrients:
            pct = round((item["weight"] / total_weight) * 100.0, 1)
            contributions.append(
                SystemContributionItem(
                    nutrient_id=item["id"],
                    nutrient_name=item["name"],
                    contribution_percentage=pct,
                    role=item["role"]
                )
            )

        contributions.sort(key=lambda x: -x.contribution_percentage)

        # Find associated symptoms connected to these nutrients
        symptoms_set = set()
        for item in connected_nutrients:
            nid = item["id"]
            for _, v, d in g.out_edges(nid, data=True):
                if g.nodes[v].get("entity_type") == EntityType.SYMPTOM:
                    symptoms_set.add(g.nodes[v]["name"])

        return SystemImpactResponse(
            system_id=target_sys,
            system_name=sys_name,
            description=sys_data["description"],
            total_connected_nutrients=len(contributions),
            total_associated_symptoms=len(symptoms_set),
            key_nutrients=contributions,
            associated_symptoms=sorted(list(symptoms_set)),
            physiological_mechanisms=mechanisms[:4]
        )
