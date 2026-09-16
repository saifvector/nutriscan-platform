"""
Clinical Copilot & Clinician Review API Router
Exposes enterprise endpoints for:
- Patient Intelligence Dossier
- Narrative Clinical Assessment
- EMR SOAP Note Generation
- Differential Diagnostic Reasoning
- Severity-Gated Follow-Up Scheduling
- Clinician Sign-Off & Audit Logging
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    UnifiedPatientDossier,
    ClinicalAssessmentReport,
    SOAPNoteResponse,
    DifferentialDiagnosticReport,
    ClinicianReviewRequest,
    ClinicianReviewRecord,
    FollowUpSchedulePlan
)
from .service import ClinicalCopilotService

router = APIRouter(tags=["Clinical Copilot"])


@router.post("/copilot/patient-intelligence", response_model=UnifiedPatientDossier)
async def get_patient_intelligence(payload: Dict[str, Any]):
    """
    Aggregates predictions, biomarkers, symptoms, outcomes, meal plans, foods,
    supplements, risk scores, explainability, and safety findings into a single patient dossier.
    """
    try:
        return ClinicalCopilotService.get_patient_dossier(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling patient intelligence dossier: {str(e)}"
        )


@router.post("/copilot/clinical-assessment", response_model=ClinicalAssessmentReport)
async def generate_clinical_assessment(payload: Dict[str, Any]):
    """
    Generates a comprehensive 7-part clinical assessment report:
    Executive Summary, Clinical Findings, Deficiency Risk Summary, Contributing Factors,
    Recommended Actions, Monitoring Plan, and Follow-Up Recommendations.
    """
    try:
        return ClinicalCopilotService.generate_assessment(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating clinical assessment: {str(e)}"
        )


@router.post("/copilot/soap-note", response_model=SOAPNoteResponse)
async def generate_soap_note(payload: Dict[str, Any]):
    """
    Generates structured SOAP (Subjective, Objective, Assessment, Plan) note
    with 1-click clipboard text formatted for Epic, Cerner, and Meditech EMR systems.
    """
    try:
        return ClinicalCopilotService.generate_soap_note(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating SOAP note: {str(e)}"
        )


@router.post("/copilot/differential-reasoning", response_model=DifferentialDiagnosticReport)
async def get_differential_reasoning(payload: Dict[str, Any]):
    """
    Evaluates competing clinical etiologies, model confidence levels,
    uncertainty bounds (95% CI), and gold-standard confirmatory testing.
    """
    try:
        return ClinicalCopilotService.analyze_differential(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing differential diagnosis: {str(e)}"
        )


@router.post("/copilot/follow-up-schedule", response_model=FollowUpSchedulePlan)
async def get_follow_up_schedule(payload: Dict[str, Any]):
    """
    Generates severity-gated 30-day, 60-day, and 90-day follow-up schedules
    with re-testing lab triggers and escalation checkpoints.
    """
    try:
        return ClinicalCopilotService.schedule_followup(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling follow-up plan: {str(e)}"
        )


# --- Clinician Review Workflow Endpoints ---

@router.post("/clinical-review/action", response_model=ClinicianReviewRecord, tags=["Clinician Review Workflow"])
async def submit_clinician_review(request: ClinicianReviewRequest):
    """
    Records clinician decision (APPROVE, REJECT, MODIFY, ESCALATE)
    with cryptographic SHA-256 tamper-evident audit logging.
    """
    try:
        return ClinicalCopilotService.submit_review(request)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording clinician review: {str(e)}"
        )


@router.get("/clinical-review/history/{patient_id}", response_model=List[ClinicianReviewRecord], tags=["Clinician Review Workflow"])
async def get_patient_review_history(patient_id: str):
    """Retrieves all clinician sign-offs and reviews logged for a specific patient."""
    return ClinicalCopilotService.get_reviews_for_patient(patient_id)


@router.get("/clinical-review/all", response_model=List[ClinicianReviewRecord], tags=["Clinician Review Workflow"])
async def get_all_clinical_reviews():
    """Retrieves global registry of all logged clinician reviews."""
    return ClinicalCopilotService.get_all_reviews()
