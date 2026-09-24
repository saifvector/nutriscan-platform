"""
Patient Records Service
Handles patient lookup, demographics, and longitudinal timeline aggregation.
"""

import logging
from typing import Dict, Any, List, Optional
from ...core.persistence import PersistenceRepository

logger = logging.getLogger(__name__)


class PatientService:
    @staticmethod
    def search_patients(query: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Search patients by name or ID with aggregate screening counts and latest risk scores."""
        return PersistenceRepository.search_patients(query=query, limit=limit, offset=offset)

    @staticmethod
    def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full patient demographic and baseline clinical data."""
        return PersistenceRepository.get_patient(patient_id=patient_id)

    @staticmethod
    def get_patient_timeline(patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete longitudinal timeline for a patient including:
        - Chronological assessment history
        - Risk score progression
        - Nutrient deficiency flags and probabilities
        - Interventions and dietary treatment history
        - Longitudinal progress trends and trajectory
        """
        return PersistenceRepository.get_patient_timeline(patient_id=patient_id)

    @staticmethod
    def upsert_patient(patient_data: Dict[str, Any]) -> str:
        """Create or update patient profile."""
        return PersistenceRepository.upsert_patient(patient_data=patient_data)

    @staticmethod
    def delete_patient(patient_id: str, deleted_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Permanently delete patient and all associated assessments, predictions,
        recommendations, meal plans, reports, outcomes, and explainability caches.
        """
        return PersistenceRepository.delete_patient(patient_id=patient_id, deleted_by=deleted_by)

    @staticmethod
    def delete_all_patients(deleted_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Permanently delete ALL patients, assessments, predictions, reports,
        and all associated clinical records across all relational tables.
        """
        return PersistenceRepository.delete_all_patients(deleted_by=deleted_by)

