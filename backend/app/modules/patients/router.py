"""
Patient Records & Clinical History API Router
Exposes endpoints for patient roster search, baseline retrieval, and longitudinal clinical history timelines.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
from .service import PatientService
from ...core.auth import get_current_user_optional, AuthenticatedUser

router = APIRouter(prefix="/patients", tags=["Patient Records & Clinical History"])


@router.get(
    "",
    summary="Search & List Patient Records",
    description="Retrieve all patients with assessment counts, latest assessment date, latest risk score, and active deficiency burden."
)
async def list_patients(
    search: Optional[str] = Query(None, description="Filter patients by name or ID"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Record pagination offset"),
):
    try:
        return PatientService.search_patients(query=search, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query patient records: {str(e)}"
        )


@router.get(
    "/{patient_id}",
    summary="Get Patient Baseline Profile",
    description="Retrieve patient demographic baseline, dietary habits, and baseline clinical history."
)
async def get_patient(
    patient_id: str = Path(..., description="Unique patient identifier or name")
):
    patient = PatientService.get_patient(patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with identifier '{patient_id}' was not found in records."
        )
    return patient


@router.get(
    "/{patient_id}/timeline",
    summary="Get Longitudinal Patient Timeline",
    description="Retrieve chronological assessment dates, risk scores, deficiency history, treatment history, and trajectory progress trends."
)
async def get_patient_timeline(
    patient_id: str = Path(..., description="Unique patient identifier or name")
):
    timeline = PatientService.get_patient_timeline(patient_id=patient_id)
    if not timeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No clinical history or records found for patient '{patient_id}'."
        )
    return timeline


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create or Update Patient Record",
    description="Explicitly register or update a patient baseline record."
)
async def upsert_patient_record(payload: Dict[str, Any]):
    try:
        patient_id = PatientService.upsert_patient(patient_data=payload)
        return {"success": True, "patient_id": patient_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to persist patient record: {str(e)}"
        )


@router.delete(
    "/delete-all",
    status_code=status.HTTP_200_OK,
    summary="Delete All Patients & Clinical History",
    description="Permanently and transactionally deletes ALL patients, assessments, predictions, reports, and clinical records."
)
@router.delete(
    "/all",
    status_code=status.HTTP_200_OK,
    summary="Delete All Patients & Clinical History (Alias)",
    description="Permanently and transactionally deletes ALL patients, assessments, predictions, reports, and clinical records."
)
async def delete_all_patients(
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        user_identifier = current_user.email if current_user else "clinician_admin"
        res = PatientService.delete_all_patients(deleted_by=user_identifier)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all patient records: {str(e)}"
        )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Patient Record & Cascade History",
    description="Permanently and transactionally deletes patient record, all associated assessments, predictions, reports, meal plans, forecasts, outcomes, and explainability caches."
)
async def delete_patient_record(
    patient_id: str = Path(..., description="Unique patient identifier or name to permanently delete"),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        user_identifier = current_user.email if current_user else "clinician_user"
        res = PatientService.delete_patient(patient_id=patient_id, deleted_by=user_identifier)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with identifier '{patient_id}' was not found in records."
            )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete patient record: {str(e)}"
        )
