"""
Phase 12: Clinical Governance, Validation & Production Monitoring REST Router.
Exposes endpoints for:
- /validation/* (Cohort validation, demographic subgroup slicing)
- /monitoring/* (Throughput, latency percentiles, drift, alert management)
- /safety/* (Safety guardrails evaluation, NIH UL limits)
- /fairness/* (Demographic parity, equal opportunity, disparate impact)
- /audit/* (Clinical audit logs, CSV export, PDF certificate generation)
"""

import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Path, Query, Response

from ...schemas.phase12_governance import (
    SubgroupCategory,
    CohortValidationSummaryResponse,
    DemographicBreakdownResponse,
    DriftReportResponse,
    SafetyEvaluationRequest,
    SafetyEvaluationResponse,
    FairnessReportResponse,
    MonitoringMetricsResponse,
    AlertsListResponse,
    AlertItem,
    AcknowledgeAlertRequest,
    AuditRecordItem,
    AuditLogsResponse,
    AlertSeverity
)
from .validation_engine import ClinicalValidationEngine
from .drift_engine import ModelDriftEngine
from .safety_engine import ClinicalSafetyEngine
from .fairness_engine import FairnessAuditEngine
from .monitoring_service import ProductionMonitoringService
from .audit_service import ClinicalAuditService
from .alert_engine import AlertingEngine

router = APIRouter(prefix="", tags=["Clinical Validation, Safety Governance & Production Monitoring"])


# ===========================================================================
# 1. CLINICAL VALIDATION ENDPOINTS
# ===========================================================================

@router.get(
    "/validation/cohort-summary",
    response_model=CohortValidationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Holdout Cohort Validation Summary",
    description="Returns diagnostic performance metrics (AUROC, AUPRC, Sensitivity, Specificity, PPV, NPV, F1, ECE, Brier) across all 9 champion models."
)
async def get_cohort_validation_summary(
    force_recompute: bool = Query(False, description="Bypass cache and recompute from raw dataset")
):
    try:
        return ClinicalValidationEngine.get_cohort_summary(force_recompute=force_recompute)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cohort validation calculation failed: {str(e)}"
        )


@router.get(
    "/validation/demographic-breakdown",
    response_model=DemographicBreakdownResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Demographic Subgroup Validation Breakdown",
    description="Stratifies holdout performance across Age, Sex, Race/Ethnicity, or Income PIR."
)
async def get_demographic_validation_breakdown(
    stratification: SubgroupCategory = Query(SubgroupCategory.SEX, description="Subgroup category: AGE, SEX, RACE_ETHNICITY, INCOME_PIR"),
    force_recompute: bool = Query(False, description="Bypass cache and recompute")
):
    try:
        return ClinicalValidationEngine.get_demographic_breakdown(stratification=stratification, force_recompute=force_recompute)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demographic validation calculation failed: {str(e)}"
        )


# ===========================================================================
# 2. PRODUCTION MONITORING & DRIFT ENDPOINTS
# ===========================================================================

@router.get(
    "/monitoring/metrics",
    response_model=MonitoringMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Production Operations & Telemetry Metrics",
    description="Aggregates requests/min, latency percentiles (p50, p95, p99), risk tier distributions, and calibration status."
)
async def get_monitoring_metrics():
    try:
        return ProductionMonitoringService.get_monitoring_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring metrics query failed: {str(e)}"
        )


@router.get(
    "/monitoring/drift",
    response_model=DriftReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Statistical Model & Feature Drift Telemetry",
    description="Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) two-sample metrics against baseline NHANES data."
)
async def get_drift_telemetry(
    simulated_drift_factor: float = Query(0.0, description="Optional synthetic factor to simulate population shift (for testing/demo)")
):
    try:
        return ModelDriftEngine.evaluate_drift(simulated_drift_factor=simulated_drift_factor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model drift calculation failed: {str(e)}"
        )


@router.get(
    "/monitoring/alerts",
    response_model=AlertsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Governance & Drift Alerts",
    description="Returns active, unacknowledged, or historical system alerts."
)
async def get_system_alerts(
    active_only: bool = Query(False, description="Filter for unacknowledged alerts only"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity: INFO, WARNING, CRITICAL"),
    limit: int = Query(50, ge=1, le=200, description="Max alerts to retrieve")
):
    try:
        return AlertingEngine.get_alerts(active_only=active_only, severity=severity, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alerts retrieval failed: {str(e)}"
        )


@router.post(
    "/monitoring/alerts/{alert_id}/acknowledge",
    response_model=AlertItem,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge System Alert",
    description="Marks a monitoring alert as reviewed and resolved by a clinician."
)
async def acknowledge_alert(
    alert_id: uuid.UUID = Path(..., description="Unique alert UUID"),
    request: AcknowledgeAlertRequest = ...
):
    alert = AlertingEngine.acknowledge_alert(alert_id=alert_id, acknowledged_by=request.acknowledged_by)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found."
        )
    return alert


# ===========================================================================
# 3. CLINICAL SAFETY ENGINE ENDPOINTS
# ===========================================================================

@router.post(
    "/safety/evaluate",
    response_model=SafetyEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Clinical Safety Guardrails & Clearance",
    description="Validates assessments and proposed recommendations against NIH Tolerable Upper Limits and pathological contraindications."
)
async def evaluate_clinical_safety(
    request: SafetyEvaluationRequest
):
    try:
        return ClinicalSafetyEngine.evaluate(request=request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical safety evaluation failed: {str(e)}"
        )


@router.get(
    "/safety/rules",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Clinical Safety Rules Catalog",
    description="Returns all codified safety guardrails, upper tolerable limits, and clinical contraindication rules."
)
async def get_safety_rules_catalog():
    try:
        return ClinicalSafetyEngine.get_all_safety_rules()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Safety rules catalog query failed: {str(e)}"
        )


# ===========================================================================
# 4. BIAS & FAIRNESS AUDITING ENDPOINTS
# ===========================================================================

@router.get(
    "/fairness/report",
    response_model=FairnessReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Algorithmic Fairness & Parity Audit Report",
    description="Audits Demographic Parity, Equal Opportunity, and Disparate Impact (80% rule) across protected classes."
)
async def get_fairness_audit_report(
    force_recompute: bool = Query(False, description="Bypass cache and recompute")
):
    try:
        return FairnessAuditEngine.audit_fairness(force_recompute=force_recompute)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fairness audit calculation failed: {str(e)}"
        )


# ===========================================================================
# 5. CLINICAL AUDIT TRAIL ENDPOINTS
# ===========================================================================

@router.get(
    "/audit/logs",
    response_model=AuditLogsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Paginated Clinical Audit Logs",
    description="Retrieves historical screening transactions with model versions, features, predictions, and safety clearance."
)
async def get_clinical_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier: LOW, MODERATE, HIGH"),
    min_safety_score: Optional[float] = Query(None, description="Filter by minimum safety score")
):
    try:
        return ClinicalAuditService.get_audit_logs(
            limit=limit,
            offset=offset,
            risk_tier=risk_tier,
            min_safety_score=min_safety_score
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit logs query failed: {str(e)}"
        )


@router.get(
    "/audit/logs/{audit_id}",
    response_model=AuditRecordItem,
    status_code=status.HTTP_200_OK,
    summary="Get Single Clinical Audit Record",
    description="Retrieves complete immutable transaction snapshot for an audit record ID."
)
async def get_clinical_audit_record(
    audit_id: uuid.UUID = Path(..., description="Unique audit record UUID")
):
    record = ClinicalAuditService.get_audit_record(audit_id=audit_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit record {audit_id} not found."
        )
    return record


@router.get(
    "/audit/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Export Clinical Audit Logs as CSV",
    description="Streams tabular CSV file containing audit logs for regulatory and compliance inspection."
)
async def export_audit_logs_csv():
    try:
        csv_data = ClinicalAuditService.export_csv()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=clinical_audit_trail.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV export failed: {str(e)}"
        )


@router.get(
    "/audit/export/pdf/{audit_id}",
    status_code=status.HTTP_200_OK,
    summary="Download Clinical Decision Certificate PDF",
    description="Generates signed, publication-quality Clinical Decision Certificate with model provenance and safety attestation."
)
async def download_audit_certificate_pdf(
    audit_id: uuid.UUID = Path(..., description="Unique audit record UUID")
):
    try:
        pdf_bytes = ClinicalAuditService.export_pdf_certificate(audit_id=audit_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=clinical_decision_certificate_{audit_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF certificate generation failed: {str(e)}"
        )
