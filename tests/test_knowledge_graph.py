"""
Comprehensive Automated Test Suite for Clinical Knowledge Graph
Phase 7B: Validates graph creation, relationships, shortest paths, influence radius,
centrality calculations, system impacts, and REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from backend.app.modules.knowledge_graph.graph_engine import KnowledgeGraphEngine
from backend.app.modules.knowledge_graph.graph_queries import KnowledgeGraphQueries
from backend.app.modules.knowledge_graph.centrality import CentralityAnalyzer
from backend.app.modules.knowledge_graph.service import KnowledgeGraphService
from backend.app.modules.knowledge_graph.schemas import EntityType, RelationshipType


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def builder():
    return KnowledgeGraphBuilder.get_instance()


@pytest.fixture(scope="module")
def engine():
    return KnowledgeGraphEngine()


@pytest.fixture(scope="module")
def queries(engine):
    return KnowledgeGraphQueries(engine)


@pytest.fixture(scope="module")
def analyzer(engine):
    return CentralityAnalyzer(engine)


# ═════════════════════════════════════════════════════════════════════════════
# 1. GRAPH BUILDER & INITIALIZATION TESTS
# ═════════════════════════════════════════════════════════════════════════════

def test_graph_builder_initialization_and_speed(builder):
    """Verifies that the graph initializes in < 100ms and adheres to the singleton pattern."""
    graph, latency_ms = builder.build_graph()
    assert graph is not None
    assert latency_ms < 100.0, f"Graph build time {latency_ms} ms exceeded 100 ms target."
    assert graph.number_of_nodes() >= 60
    assert graph.number_of_edges() >= 40

    # Test singleton identity
    builder2 = KnowledgeGraphBuilder.get_instance()
    assert builder is builder2
    assert builder.graph is builder2.graph


def test_all_18_nutrients_present(engine):
    """Verifies all 18 clinical target nutrients exist as nodes in the graph."""
    expected_18 = [
        "NUTRIENT_PROTEIN", "NUTRIENT_VITAMIN_A", "NUTRIENT_VITAMIN_B1", "NUTRIENT_VITAMIN_B2",
        "NUTRIENT_VITAMIN_B3", "NUTRIENT_VITAMIN_B6", "NUTRIENT_VITAMIN_B12", "NUTRIENT_FOLATE",
        "NUTRIENT_VITAMIN_C", "NUTRIENT_VITAMIN_D", "NUTRIENT_VITAMIN_E", "NUTRIENT_IRON",
        "NUTRIENT_CALCIUM", "NUTRIENT_MAGNESIUM", "NUTRIENT_ZINC", "NUTRIENT_POTASSIUM",
        "NUTRIENT_SELENIUM", "NUTRIENT_IODINE"
    ]
    for nid in expected_18:
        node = engine.get_node(nid)
        assert node is not None, f"Nutrient node {nid} missing from knowledge graph."
        assert node.entity_type == EntityType.NUTRIENT
        assert "urgency_weight" in node.metadata


def test_all_7_entity_classes_present(engine):
    """Verifies presence of nodes across all 7 required entity classes."""
    stats = engine.get_stats()
    type_counts = stats.entity_type_counts

    required_classes = [
        EntityType.NUTRIENT.value,
        EntityType.SYMPTOM.value,
        EntityType.FOOD.value,
        EntityType.LIFESTYLE_FACTOR.value,
        EntityType.MEDICAL_CONDITION.value,
        EntityType.LAB_TEST.value,
        EntityType.BIOLOGICAL_SYSTEM.value
    ]
    for req in required_classes:
        assert req in type_counts, f"Entity class {req} missing from topology stats."
        assert type_counts[req] > 0, f"Entity class {req} has 0 nodes."


def test_relationships_and_directional_weights(engine):
    """Verifies directional edges, weight range, mechanisms, and citations."""
    relationships = engine.list_relationships()
    assert len(relationships) >= 40

    edge_types = set(r.relationship_type for r in relationships)
    assert RelationshipType.CAUSES in edge_types
    assert RelationshipType.CONTRIBUTES_TO in edge_types
    assert RelationshipType.ASSOCIATED_WITH in edge_types
    assert RelationshipType.IMPACTS in edge_types
    assert RelationshipType.REQUIRES in edge_types
    assert RelationshipType.SUPPORTS in edge_types
    assert RelationshipType.CONFIRMS in edge_types

    for r in relationships:
        assert 0.0 <= r.weight <= 1.0
        assert len(r.mechanism) > 10
        assert r.source_id is not None
        assert r.target_id is not None


# ═════════════════════════════════════════════════════════════════════════════
# 2. GRAPH QUERY TESTS
# ═════════════════════════════════════════════════════════════════════════════

def test_neighbors_query(queries):
    """Tests 1-hop neighbor queries for Vitamin D."""
    neighbors = queries.get_neighbors("NUTRIENT_VITAMIN_D", direction="both")
    assert len(neighbors) > 0

    neighbor_ids = set([n.source_id for n in neighbors] + [n.target_id for n in neighbors])
    # Vitamin D should connect to Magnesium, Calcium, Bone Pain, etc.
    assert "NUTRIENT_MAGNESIUM" in neighbor_ids or "NUTRIENT_CALCIUM" in neighbor_ids
    assert "SYMPTOM_BONE_PAIN" in neighbor_ids or "LIFESTYLE_LOW_SUN" in neighbor_ids


def test_shortest_path_low_sun_to_bone_pain(queries):
    """Verifies the causal path from Low Sun Exposure to Bone Pain."""
    path_res = queries.get_shortest_path("LIFESTYLE_LOW_SUN", "SYMPTOM_BONE_PAIN")
    assert path_res.exists is True
    assert path_res.path_length >= 2
    assert "LIFESTYLE_LOW_SUN" in path_res.node_sequence
    assert "SYMPTOM_BONE_PAIN" in path_res.node_sequence
    assert "NUTRIENT_VITAMIN_D" in path_res.node_sequence
    assert len(path_res.hops) == path_res.path_length
    assert len(path_res.clinical_summary) > 20


def test_shortest_path_vegan_to_neuropathy(queries):
    """Verifies the causal path from Strict Vegan Diet to Tingling/Numbness."""
    path_res = queries.get_shortest_path("LIFESTYLE_STRICT_VEGAN", "SYMPTOM_TINGLING_NUMBNESS")
    assert path_res.exists is True
    assert "NUTRIENT_VITAMIN_B12" in path_res.node_sequence
    assert len(path_res.hops) >= 2


def test_influence_radius_downstream(queries):
    """Verifies downstream reachability computation up to 2 hops for Vitamin B12."""
    inf_res = queries.get_influence_radius("NUTRIENT_VITAMIN_B12", max_hops=2)
    assert inf_res.nutrient_name == "Vitamin B12 (Cobalamin)"
    assert inf_res.total_downstream_entities > 0
    assert inf_res.influence_score > 0
    assert "Peripheral Tingling & Paresthesia" in inf_res.affected_symptoms
    assert len(inf_res.affected_systems) > 0


def test_nutrient_ego_subgraph(queries):
    """Verifies ego network extraction and categorization."""
    subgraph = queries.get_nutrient_subgraph("NUTRIENT_IRON")
    assert subgraph is not None
    assert subgraph.center_nutrient_name == "Iron"
    assert len(subgraph.nodes) > 3
    assert len(subgraph.edges) > 3
    assert subgraph.summary_counts.symptoms > 0
    assert subgraph.summary_counts.foods > 0


# ═════════════════════════════════════════════════════════════════════════════
# 3. CENTRALITY & SYSTEM IMPACT TESTS
# ═════════════════════════════════════════════════════════════════════════════

def test_centrality_and_rankings(analyzer):
    """Verifies degree centrality, betweenness, and influence rankings."""
    res = analyzer.analyze_centrality()
    assert res.total_nodes >= 60
    assert res.total_edges >= 40
    assert len(res.all_nutrients_centrality) == 18
    assert len(res.top_influential_nutrients) == 5

    # Check top influential nutrients include major master nutrients
    top_names = [n.nutrient_name for n in res.top_influential_nutrients]
    assert any("Vitamin D" in name or "Iron" in name or "Magnesium" in name for name in top_names)

    # Validate ranks are 1 through 18
    ranks = [n.rank for n in res.all_nutrients_centrality]
    assert ranks == list(range(1, 19))


def test_system_impact_breakdown(analyzer):
    """Verifies biological system impact calculation and percentage normalization."""
    res = analyzer.analyze_system_impact("SYSTEM_IMMUNE")
    assert res is not None
    assert res.system_name == "Immune & Defense System"
    assert res.total_connected_nutrients > 0
    assert len(res.key_nutrients) > 0

    # Ensure percentage contributions sum to ~100%
    total_pct = sum(k.contribution_percentage for k in res.key_nutrients)
    assert 99.0 <= total_pct <= 101.0
    assert len(res.associated_symptoms) > 0


# ═════════════════════════════════════════════════════════════════════════════
# 4. FASTAPI REST API ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

def test_api_stats(client):
    res = client.get("/api/v1/knowledge-graph/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] >= 60
    assert data["is_cached"] is True


def test_api_entities_list(client):
    res = client.get("/api/v1/knowledge-graph/entities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 60

    # Filter by NUTRIENT
    res_nutrients = client.get("/api/v1/knowledge-graph/entities?entity_type=NUTRIENT")
    assert res_nutrients.status_code == 200
    nutrients_data = res_nutrients.json()
    assert len(nutrients_data) == 18

    # Keyword search
    res_search = client.get("/api/v1/knowledge-graph/entities?search=bone")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert len(search_data) > 0


def test_api_single_entity(client):
    res = client.get("/api/v1/knowledge-graph/entities/NUTRIENT_VITAMIN_D")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Vitamin D"
    assert data["entity_type"] == "NUTRIENT"

    res_404 = client.get("/api/v1/knowledge-graph/entities/NON_EXISTENT_ID")
    assert res_404.status_code == 404


def test_api_relationships_list(client):
    res = client.get("/api/v1/knowledge-graph/relationships")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 40

    # Filter by type
    res_causes = client.get("/api/v1/knowledge-graph/relationships?type=CAUSES")
    assert res_causes.status_code == 200
    assert len(res_causes.json()) > 0


def test_api_nutrient_network(client):
    res = client.get("/api/v1/knowledge-graph/nutrients/NUTRIENT_VITAMIN_D/network")
    assert res.status_code == 200
    data = res.json()
    assert data["center_nutrient_name"] == "Vitamin D"
    assert len(data["nodes"]) > 0
    assert "summary_counts" in data


def test_api_nutrient_influence(client):
    res = client.get("/api/v1/knowledge-graph/nutrients/NUTRIENT_VITAMIN_D/influence?max_hops=2")
    assert res.status_code == 200
    data = res.json()
    assert data["nutrient_name"] == "Vitamin D"
    assert data["total_downstream_entities"] > 0


def test_api_shortest_path(client):
    res = client.get("/api/v1/knowledge-graph/path?source=LIFESTYLE_LOW_SUN&target=SYMPTOM_BONE_PAIN")
    assert res.status_code == 200
    data = res.json()
    assert data["exists"] is True
    assert data["path_length"] >= 2
    assert len(data["hops"]) == data["path_length"]


def test_api_centrality(client):
    res = client.get("/api/v1/knowledge-graph/centrality")
    assert res.status_code == 200
    data = res.json()
    assert len(data["top_influential_nutrients"]) == 5
    assert len(data["all_nutrients_centrality"]) == 18


def test_api_system_impact(client):
    res = client.get("/api/v1/knowledge-graph/systems/SYSTEM_NEUROLOGICAL")
    assert res.status_code == 200
    data = res.json()
    assert data["system_name"] == "Neurological & Cognitive System"
    assert len(data["key_nutrients"]) > 0
