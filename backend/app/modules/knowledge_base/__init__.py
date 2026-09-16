"""
Clinical Knowledge Base Module
Phase 7A: Nutrient Expansion & Clinical Knowledge Base Enhancement
"""

from .schemas import ClinicalNutrientProfile, NutrientListResponse, DietaryIntakeRef, EvidenceCitations
from .registry import CLINICAL_NUTRIENT_REGISTRY, ClinicalKnowledgeBaseService
from .router import router as knowledge_base_router

__all__ = [
    "ClinicalNutrientProfile",
    "NutrientListResponse",
    "DietaryIntakeRef",
    "EvidenceCitations",
    "CLINICAL_NUTRIENT_REGISTRY",
    "ClinicalKnowledgeBaseService",
    "knowledge_base_router"
]
