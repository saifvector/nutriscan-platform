"""
Clinical Copilot Module
Exposes unified patient intelligence, 7-part clinical assessment, EMR SOAP note,
differential diagnostic reasoning, clinician review workflow, and follow-up scheduling.
"""

from .router import router
from .service import ClinicalCopilotService

__all__ = ["router", "ClinicalCopilotService"]
