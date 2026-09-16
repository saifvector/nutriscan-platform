"""
Reporting & Dashboard REST API Router
Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Endpoints:
- POST /api/v1/reports/generate      : Compiles and persists clinical nutritional assessment report
- GET  /api/v1/reports/{id}          : Retrieves full report JSON by report UUID
- GET  /api/v1/reports/{id}/pdf      : Downloads or views vector clinical assessment PDF
- GET  /api/v1/dashboard/{assessment_id} : Returns interactive dashboard data bundle & SVGs
"""

import uuid
from typing import Optional, Any, Union
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import JSONResponse

from .service import ReportingService
from ...schemas.report import (
    DashboardResponse,
    GenerateReportRequest,
    GeneratedReportResponse,
    AssessmentHistoryResponse,
    ProgressSummaryResponse,
    ProgressTrendsResponse,
    AssessmentComparisonResponse,
    AnalyticsHealthScoreResponse,
    AnalyticsRecoveryResponse,
    AnalyticsNutrientTrendsResponse
)
from ...core.auth import get_current_user_optional, verify_resource_ownership, AuthenticatedUser, UserRole
from ...core.persistence import PersistenceRepository

router = APIRouter(tags=["Clinical Reporting & Progress Analytics"])


@router.get(
    "/reports/history",
    response_model=list[GeneratedReportResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Assessment Reports History",
    description="Retrieves ordered historical generated reports for a user."
)
async def get_reports_history(
    user_id: Optional[uuid.UUID] = None,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> list[GeneratedReportResponse]:
    try:
        # If user is a patient, enforce only viewing their own reports
        target_user = user_id
        if current_user and current_user.role == UserRole.PATIENT:
            target_user = uuid.UUID(current_user.user_id)
        return ReportingService.get_reports_history(user_id=target_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reports history: {str(e)}"
        )


@router.post(
    "/reports/generate",
    response_model=GeneratedReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Comprehensive Assessment Report",
    description="Consolidates multi-nutrient predictions, SHAP explainability, nutrient interactions, and recommendations into a persisted assessment report with optional PDF export."
)
async def generate_report(
    request: GenerateReportRequest,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> GeneratedReportResponse:
    try:
        if current_user and current_user.role == UserRole.PATIENT:
            owner_id = PersistenceRepository.get_assessment_owner(str(request.assessment_id))
            if owner_id and owner_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: You do not own this assessment."
                )

        target_user_id = uuid.UUID(current_user.user_id) if current_user else None
        report = ReportingService.generate_report(
            assessment_id=request.assessment_id,
            user_id=target_user_id,
            report_title=request.report_title or "Comprehensive Nutritional Assessment Report",
            export_pdf=request.export_pdf
        )
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile report: {str(e)}"
        )


@router.get(
    "/reports/{id}",
    response_model=GeneratedReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Assessment Report by ID",
    description="Retrieves a previously generated nutritional assessment report JSON payload."
)
async def get_report(
    id: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> GeneratedReportResponse:
    report = ReportingService.get_report_by_id(id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{id}' not found."
        )

    # Insecure Direct Object Reference (IDOR) protection
    if current_user:
        report_owner = PersistenceRepository.get_report_owner(id) or (str(report.user_id) if report.user_id else None)
        verify_resource_ownership(
            current_user=current_user,
            resource_user_id=report_owner,
            resource_id=id,
            resource_type="report"
        )

    return report


@router.get(
    "/reports/{id}/pdf",
    status_code=status.HTTP_200_OK,
    summary="Download Assessment Report as PDF",
    description="Streams a publication-grade vector PDF document for clinical assessment."
)
async def get_report_pdf(
    id: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        report = ReportingService.get_report_by_id(id)
        if report and current_user:
            report_owner = PersistenceRepository.get_report_owner(id) or (str(report.user_id) if report.user_id else None)
            verify_resource_ownership(
                current_user=current_user,
                resource_user_id=report_owner,
                resource_id=id,
                resource_type="report"
            )

        pdf_bytes = ReportingService.get_report_pdf_bytes(id)
        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF for report '{id}' could not be generated."
            )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="assessment_report_{id}.pdf"',
                "Content-Type": "application/pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK,
    summary="Get Unlinked Dashboard State",
    description="Returns clean empty state when no active assessment ID is provided."
)
async def get_dashboard_unlinked() -> Any:
    return {"hasAssessment": False, "data": None}


@router.get(
    "/dashboard/{assessment_id}",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Interactive Nutritional Health Dashboard",
    description="Returns high-level health score, risk distribution, priority rankings, active interaction alerts, recovery milestones, and 6 visualization contracts (Radar, Bar, Priority, SHAP, Interaction Graph, Timeline) with standalone SVGs."
)
async def get_dashboard(
    assessment_id: uuid.UUID,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> DashboardResponse:
    try:
        if current_user:
            owner_id = PersistenceRepository.get_assessment_owner(str(assessment_id))
            if owner_id:
                verify_resource_ownership(
                    current_user=current_user,
                    resource_user_id=owner_id,
                    resource_id=str(assessment_id),
                    resource_type="dashboard"
                )

        dashboard = ReportingService.get_dashboard(assessment_id)
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard for assessment '{assessment_id}': {str(e)}"
        )


# =============================================================================
# Progress Tracking REST APIs
# =============================================================================

@router.get(
    "/progress/summary",
    status_code=status.HTTP_200_OK,
    summary="Get Longitudinal Health Progress Summary",
    description="Calculates overall health score improvement, recovery velocity, resolved deficiencies, emerging risks, and per-nutrient recovery tracking."
)
async def get_progress_summary(
    user_id: Optional[uuid.UUID] = None,
    assessment_id: Optional[uuid.UUID] = None
) -> Any:
    if not assessment_id:
        return {"hasAssessment": False, "data": None}
    try:
        return ReportingService.get_progress_summary(user_id=user_id, assessment_id=assessment_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate progress summary: {str(e)}"
        )


@router.get(
    "/progress/history",
    response_model=AssessmentHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Longitudinal Assessment History",
    description="Returns chronological sequence of all previous health assessments with scores, versions, and risk distribution snapshots."
)
async def get_progress_history(
    user_id: Optional[uuid.UUID] = None
) -> AssessmentHistoryResponse:
    try:
        return ReportingService.get_assessment_history(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment history: {str(e)}"
        )


@router.get(
    "/progress/trends",
    response_model=ProgressTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Health Score and Nutrient Trends",
    description="Returns chronological timeline coordinates and per-nutrient risk probability trajectories."
)
async def get_progress_trends(
    user_id: Optional[uuid.UUID] = None
) -> ProgressTrendsResponse:
    try:
        return ReportingService.get_progress_trends(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve progress trends: {str(e)}"
        )


@router.get(
    "/progress/comparison",
    response_model=AssessmentComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Side-by-Side Assessment Comparison",
    description="Compares baseline and target assessments (e.g. Vitamin D 87% -> 52%) with automated clinical insights and improvement summaries."
)
async def get_progress_comparison(
    user_id: Optional[uuid.UUID] = None,
    base_id: Optional[uuid.UUID] = None,
    target_id: Optional[uuid.UUID] = None
) -> AssessmentComparisonResponse:
    try:
        return ReportingService.get_assessment_comparison(user_id=user_id, base_id=base_id, target_id=target_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute assessment comparison: {str(e)}"
        )


# =============================================================================
# Analytics REST APIs
# =============================================================================

@router.get(
    "/analytics/health-score",
    status_code=status.HTTP_200_OK,
    summary="Get Health Score Analytics",
    description="Returns detailed health score decomposition, lifestyle influence weighting, and historical progression."
)
async def get_analytics_health_score(
    user_id: Optional[uuid.UUID] = None,
    assessment_id: Optional[str] = None
) -> Any:
    if not assessment_id:
        return {"hasAssessment": False, "data": None}
    try:
        return ReportingService.get_analytics_health_score(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load health score analytics: {str(e)}"
        )


@router.get(
    "/analytics/recovery",
    status_code=status.HTTP_200_OK,
    summary="Get Nutrient Recovery Analytics",
    description="Returns average recovery rate, weekly recovery velocity, resolved deficiency count, and full recovery timeline."
)
async def get_analytics_recovery(
    user_id: Optional[uuid.UUID] = None,
    assessment_id: Optional[str] = None
) -> Any:
    if not assessment_id:
        return {"hasAssessment": False, "data": None}
    try:
        return ReportingService.get_analytics_recovery(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load recovery analytics: {str(e)}"
        )


@router.get(
    "/analytics/nutrient-trends",
    response_model=AnalyticsNutrientTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Nutrient Analytics Trends",
    description="Evaluates all monitored nutrients with reduction points, percentage gains, and trend states."
)
async def get_analytics_nutrient_trends(
    user_id: Optional[uuid.UUID] = None
) -> AnalyticsNutrientTrendsResponse:
    try:
        return ReportingService.get_analytics_nutrient_trends(user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load nutrient trend analytics: {str(e)}"
        )

