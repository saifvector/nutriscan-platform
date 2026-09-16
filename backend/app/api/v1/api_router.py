"""
Centralized API Router for Version 1
Aggregates authentication, assessment, prediction, recommendations, and reports.
"""

from fastapi import APIRouter
from ...modules.prediction.router import router as prediction_router
from ...modules.explainability.router import router as explainability_router
from ...modules.recommendation.router import router as recommendation_router
from ...modules.reporting.router import router as reporting_router
from ...modules.knowledge_base.router import router as knowledge_base_router
from ...modules.knowledge_graph.router import router as knowledge_graph_router
from ...modules.intelligence.router import router as intelligence_router
from ...modules.outcomes.router import router as outcomes_router
from ...modules.governance.router import router as governance_router
from ...modules.personalization.router import router as personalization_router
from ...modules.copilot.router import router as copilot_router
from ...modules.agents.router import router as agents_router
from ...modules.research.router import router as research_router
from ...modules.population.router import router as population_router
from ...modules.federated.router import router as federated_router
from ...modules.trials.router import router as trials_router
from ...modules.auth.router import router as auth_router
from ...modules.validation.router import router as validation_router

api_router = APIRouter()

# Include auth, validation, prediction, explainability, copilot, personalization, etc.
api_router.include_router(auth_router)
api_router.include_router(validation_router)
api_router.include_router(prediction_router)
api_router.include_router(explainability_router)
api_router.include_router(copilot_router)
api_router.include_router(agents_router)
api_router.include_router(research_router)
api_router.include_router(population_router)
api_router.include_router(federated_router)
api_router.include_router(trials_router)
api_router.include_router(personalization_router)
api_router.include_router(recommendation_router)
api_router.include_router(reporting_router)
api_router.include_router(knowledge_base_router)
api_router.include_router(knowledge_graph_router)
api_router.include_router(intelligence_router)
api_router.include_router(outcomes_router)
api_router.include_router(governance_router)

