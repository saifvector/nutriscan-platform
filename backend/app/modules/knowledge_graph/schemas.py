"""
Pydantic V2 Schemas for Clinical Knowledge Graph
Phase 7B: Graph modeling and causal inference contracts
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    NUTRIENT = "NUTRIENT"
    SYMPTOM = "SYMPTOM"
    FOOD = "FOOD"
    LIFESTYLE_FACTOR = "LIFESTYLE_FACTOR"
    MEDICAL_CONDITION = "MEDICAL_CONDITION"
    LAB_TEST = "LAB_TEST"
    BIOLOGICAL_SYSTEM = "BIOLOGICAL_SYSTEM"


class RelationshipType(str, Enum):
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    IMPACTS = "IMPACTS"
    REQUIRES = "REQUIRES"
    INHIBITS = "INHIBITS"
    ENHANCES = "ENHANCES"
    CONFIRMS = "CONFIRMS"
    AFFECTS = "AFFECTS"
    SUPPORTS = "SUPPORTS"


class GraphEntityResponse(BaseModel):
    id: str = Field(..., description="Unique entity identifier (e.g. NUTRIENT_VITAMIN_D)")
    name: str = Field(..., description="Human-readable entity name")
    entity_type: EntityType = Field(..., description="Category class of entity")
    category: Optional[str] = Field(None, description="Subcategory or classification")
    description: str = Field(..., description="Clinical description or physiological definition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom properties, tags, metrics")


class GraphRelationshipResponse(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    source_id: str = Field(..., description="Origin node identifier")
    source_name: str = Field(..., description="Origin node label")
    source_type: EntityType = Field(..., description="Origin node entity type")
    target_id: str = Field(..., description="Destination node identifier")
    target_name: str = Field(..., description="Destination node label")
    target_type: EntityType = Field(..., description="Destination node entity type")
    relationship_type: RelationshipType = Field(..., description="Directional relationship predicate")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="Evidence certainty and physiological magnitude")
    mechanism: str = Field(..., description="Biochemical/physiological explanatory mechanism")
    citation: Optional[str] = Field(None, description="Clinical practice reference (WHO, NIH, Lancet, etc.)")


class PathHop(BaseModel):
    step: int
    source_id: str
    source_name: str
    source_type: EntityType
    target_id: str
    target_name: str
    target_type: EntityType
    relationship_type: RelationshipType
    mechanism: str
    citation: Optional[str] = None


class ShortestPathResponse(BaseModel):
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    path_length: int
    exists: bool
    hops: List[PathHop] = Field(default_factory=list)
    node_sequence: List[str] = Field(default_factory=list)
    clinical_summary: str = Field(..., description="Narrative synthesis of causal trajectory")


class InfluenceRadiusNode(BaseModel):
    node_id: str
    name: str
    entity_type: EntityType
    hop_distance: int
    relationship_path: List[str]
    effective_weight: float


class NutrientInfluenceResponse(BaseModel):
    nutrient_id: str
    nutrient_name: str
    max_hops: int
    total_downstream_entities: int
    influence_score: float
    affected_symptoms: List[str]
    affected_systems: List[str]
    downstream_nodes: List[InfluenceRadiusNode]


class SubgraphCounts(BaseModel):
    nutrients: int = 0
    symptoms: int = 0
    foods: int = 0
    lifestyle_factors: int = 0
    medical_conditions: int = 0
    lab_tests: int = 0
    biological_systems: int = 0


class NutrientNetworkSubgraphResponse(BaseModel):
    center_nutrient_id: str
    center_nutrient_name: str
    nodes: List[GraphEntityResponse]
    edges: List[GraphRelationshipResponse]
    summary_counts: SubgraphCounts
    categorized_explorer: Dict[str, List[GraphEntityResponse]]


class NutrientCentralityItem(BaseModel):
    nutrient_id: str
    nutrient_name: str
    degree_centrality: float
    in_degree: int
    out_degree: int
    total_degree: int
    betweenness_centrality: float
    influence_score: float
    dependency_score: float
    rank: int


class CentralityAnalysisResponse(BaseModel):
    total_nodes: int
    total_edges: int
    density: float
    top_influential_nutrients: List[NutrientCentralityItem]
    all_nutrients_centrality: List[NutrientCentralityItem]


class SystemContributionItem(BaseModel):
    nutrient_id: str
    nutrient_name: str
    contribution_percentage: float
    role: str


class SystemImpactResponse(BaseModel):
    system_id: str
    system_name: str
    description: str
    total_connected_nutrients: int
    total_associated_symptoms: int
    key_nutrients: List[SystemContributionItem]
    associated_symptoms: List[str]
    physiological_mechanisms: List[str]


class GraphStatsResponse(BaseModel):
    total_nodes: int
    total_edges: int
    entity_type_counts: Dict[str, int]
    relationship_type_counts: Dict[str, int]
    is_cached: bool
    build_latency_ms: float
