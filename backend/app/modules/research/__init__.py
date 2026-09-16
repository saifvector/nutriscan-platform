"""
Research Intelligence Module
"""

from .schemas import (
    EvidenceItem,
    GuidelineComparison,
    ContradictionAlert,
    ResearchEvidenceReport,
    EvidenceQueryRequest
)
from .service import ResearchService
from .router import router

__all__ = [
    "EvidenceItem",
    "GuidelineComparison",
    "ContradictionAlert",
    "ResearchEvidenceReport",
    "EvidenceQueryRequest",
    "ResearchService",
    "router"
]
