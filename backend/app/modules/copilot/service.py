"""
Clinical Copilot Service Facade
Central unified orchestrator connecting all Phase 14 Copilot capabilities:
- Patient Intelligence Dossier
- 7-Part Clinical Assessment
- SOAP Note Generator
- Differential Diagnostic Reasoning
- Clinician Review & Decision Workflow
- Follow-Up Scheduling
"""

from typing import Dict, Any, List
from .schemas import (
    UnifiedPatientDossier,
    ClinicalAssessmentReport,
    SOAPNoteResponse,
    DifferentialDiagnosticReport,
    ClinicianReviewRequest,
    ClinicianReviewRecord,
    FollowUpSchedulePlan
)
from .dossier_engine import DossierEngine
from .assessment_generator import AssessmentGenerator
from .soap_generator import SOAPNoteGenerator
from .differential_engine import DifferentialEngine
from .review_engine import ReviewEngine
from .followup_engine import FollowUpEngine
from ...core.metrics import metrics


class ClinicalCopilotService:
    """High-level facade for clinical copilot capabilities."""

    @classmethod
    def _resolve_patient_data(cls, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(patient_data or {})
        if "patient_data" in data and isinstance(data["patient_data"], dict):
            inner = dict(data["patient_data"])
            data.pop("patient_data")
            inner.update(data)
            data = inner
        asmnt_id = data.get("assessment_id") or data.get("patient_id") or data.get("id")
        from ...core.persistence import PersistenceRepository
        persisted = None
        if asmnt_id:
            persisted = PersistenceRepository.get_assessment(str(asmnt_id))

        if persisted:
            merged = dict(persisted)
            merged.update(data)
            # Ensure name fields are preserved from persisted if not provided in incoming data
            resolved_name = (
                data.get("name")
                or data.get("patient_name")
                or data.get("full_name")
                or data.get("patientName")
                or data.get("display_name")
                or persisted.get("patient_name")
                or persisted.get("name")
                or persisted.get("full_name")
            )
            if resolved_name and not str(resolved_name).startswith("Patient ("):
                merged["name"] = str(resolved_name).strip()
                merged["patient_name"] = str(resolved_name).strip()
                merged["full_name"] = str(resolved_name).strip()
            return merged
        else:
            if not data.get("age") and not data.get("dietary_pattern"):
                if asmnt_id:
                    raise ValueError(f"Patient assessment record for ID '{asmnt_id}' not found.")
                else:
                    raise ValueError("Missing clinical intake data. A valid assessment payload or existing assessment_id is required.")
        return data

    @classmethod
    def get_patient_dossier(cls, patient_data: Dict[str, Any]) -> UnifiedPatientDossier:
        resolved = cls._resolve_patient_data(patient_data)
        try:
            metrics.record_copilot_op(op_type="patient_dossier", status="success")
        except Exception:
            pass
        return DossierEngine.compile_dossier(resolved)

    @classmethod
    def generate_assessment(cls, patient_data: Dict[str, Any]) -> ClinicalAssessmentReport:
        resolved = cls._resolve_patient_data(patient_data)
        dossier = DossierEngine.compile_dossier(resolved)
        try:
            metrics.record_copilot_op(op_type="assessment_generation", status="success")
        except Exception:
            pass
        return AssessmentGenerator.generate_assessment(dossier)

    generate_clinical_assessment = generate_assessment

    @classmethod
    def generate_soap_note(cls, patient_data: Dict[str, Any]) -> SOAPNoteResponse:
        resolved = cls._resolve_patient_data(patient_data)
        dossier = DossierEngine.compile_dossier(resolved)
        try:
            metrics.record_copilot_op(op_type="soap_generation", status="success")
        except Exception:
            pass
        return SOAPNoteGenerator.generate_soap_note(dossier)

    @classmethod
    def analyze_differential(cls, patient_data: Dict[str, Any]) -> DifferentialDiagnosticReport:
        resolved = cls._resolve_patient_data(patient_data)
        dossier = DossierEngine.compile_dossier(resolved)
        try:
            metrics.record_copilot_op(op_type="differential_analysis", status="success")
        except Exception:
            pass
        return DifferentialEngine.analyze_differential(dossier)

    @classmethod
    def schedule_followup(cls, patient_data: Dict[str, Any]) -> FollowUpSchedulePlan:
        resolved = cls._resolve_patient_data(patient_data)
        dossier = DossierEngine.compile_dossier(resolved)
        try:
            metrics.record_copilot_op(op_type="followup_scheduling", status="success")
        except Exception:
            pass
        return FollowUpEngine.schedule_followups(dossier)

    @classmethod
    def submit_review(cls, request: ClinicianReviewRequest) -> ClinicianReviewRecord:
        return ReviewEngine.process_review(request)

    @classmethod
    def get_reviews_for_patient(cls, patient_id: str) -> List[ClinicianReviewRecord]:
        return ReviewEngine.get_patient_audit_history(patient_id)

    @classmethod
    def get_all_reviews(cls) -> List[ClinicianReviewRecord]:
        return ReviewEngine.get_all_reviews()


CopilotService = ClinicalCopilotService
