"""
NutriScan Enterprise Domain Models & Persistence Architecture Specification
Phase 8: Architecture Consolidation & Authoritative Persistence Mapping

ARCHITECTURE DIRECTIVE:
1. RUNTIME PERSISTENCE ENGINE:
   The authoritative runtime persistence engine for active assessment sessions, multi-nutrient
   predictions, SHAP explanations, recommendations, meal plans, outcome tracking, and audit
   logging is `PersistenceRepository` (app.core.persistence.PersistenceRepository).
   It guarantees thread-safety (SQLite WAL mode & connection pooling), crash-resilience,
   and deterministic sub-millisecond retrieval without session locking hazards.

2. ENTERPRISE DOMAIN SCHEMAS:
   The SQLAlchemy declarative models defined below represent the canonical relational domain
   schemas for multi-tenant schema migrations, Alembic tracking, and external PostgreSQL warehousing.
"""

from ..core.persistence import PersistenceRepository

from .user import Base, User, UserProfile
from .assessment import HealthAssessment
from .prediction import NutrientPrediction, RiskFactor
from .recommendation import FoodRecommendation
from .report import GeneratedReport
from .progress import AssessmentHistory, HealthScoreRecord, ProgressMetric
from .outcomes import (
    AdherenceLog,
    SymptomJournal,
    LabResult,
    OutcomeMetric,
    AdaptiveRecommendation,
    PredictionValidation
)
from .governance import (
    ClinicalAuditRecord,
    ClinicalSafetyEvent,
    ModelDriftSnapshot,
    ValidationBenchmark,
    MonitoringAlert
)

__all__ = [
    # Authoritative Runtime Persistence
    "PersistenceRepository",
    # Domain Models & Relational Schemas
    "Base",
    "User",
    "UserProfile",
    "HealthAssessment",
    "NutrientPrediction",
    "RiskFactor",
    "FoodRecommendation",
    "GeneratedReport",
    "AssessmentHistory",
    "HealthScoreRecord",
    "ProgressMetric",
    "AdherenceLog",
    "SymptomJournal",
    "LabResult",
    "OutcomeMetric",
    "AdaptiveRecommendation",
    "PredictionValidation",
    "ClinicalAuditRecord",
    "ClinicalSafetyEvent",
    "ModelDriftSnapshot",
    "ValidationBenchmark",
    "MonitoringAlert",
]
