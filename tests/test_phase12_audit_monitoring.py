"""
Phase 12: Production Monitoring & Clinical Audit Trail Tests.
Verifies telemetry tracking, p50/p95/p99 latency calculation, alert lifecycles,
audit record logging, CSV stream export, PDF certificate rendering, and API endpoints.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.governance.monitoring_service import ProductionMonitoringService
from backend.app.modules.governance.alert_engine import AlertingEngine, GovernanceAlertEngine
from backend.app.modules.governance.audit_service import ClinicalAuditService
from backend.app.schemas.phase12_governance import AlertType, AlertSeverity

client = TestClient(app)


def test_monitoring_telemetry_recording():
    """Verify inference telemetry updates request counts, latency percentiles, and risk distributions."""
    ProductionMonitoringService.record_inference(latency_ms=18.5, safety_tier="LOW", blocked=False)
    ProductionMonitoringService.record_inference(latency_ms=32.0, safety_tier="MODERATE", blocked=False)
    ProductionMonitoringService.record_inference(latency_ms=45.2, safety_tier="CRITICAL", blocked=True)

    telemetry = ProductionMonitoringService.get_telemetry_summary()
    assert telemetry.total_requests >= 3
    assert telemetry.blocked_requests >= 1
    assert telemetry.latency_p50_ms > 0.0
    assert telemetry.latency_p95_ms >= telemetry.latency_p50_ms
    assert telemetry.risk_tier_counts["LOW"] >= 1


def test_alert_engine_emit_and_acknowledge():
    """Verify alert creation, active queue filtering, and acknowledgment."""
    alert = AlertingEngine.emit_alert(
        alert_type=AlertType.DRIFT_ALERT,
        severity=AlertSeverity.WARNING,
        title="Elevated Calcium Drift",
        message="Calcium deficiency model output distribution shifted PSI=0.14."
    )
    assert alert.alert_id is not None
    assert alert.is_acknowledged is False

    active_alerts = AlertingEngine.get_active_alerts()
    found = any(a.alert_id == alert.alert_id for a in active_alerts)
    assert found is True

    # Acknowledge alert
    ack_alert = AlertingEngine.acknowledge_alert(alert.alert_id, acknowledged_by="Dr. Auditor")
    assert ack_alert is not None
    assert ack_alert.is_acknowledged is True
    assert ack_alert.acknowledged_by == "Dr. Auditor"


def test_audit_service_record_and_list():
    """Verify audit record persistence and querying."""
    rec = ClinicalAuditService.record_audit_event(
        assessment_id=uuid.uuid4(),
        patient_intake_hash="abc123hash",
        predicted_deficiencies=["Vitamin D Deficiency", "Iron Deficiency"],
        safety_score=85.0,
        safety_risk_tier="MODERATE",
        is_blocked=False,
        explanation_available=True,
        execution_latency_ms=24.5
    )
    assert rec.audit_id is not None

    records = ClinicalAuditService.list_records(limit=10)
    assert len(records) >= 1


def test_audit_service_csv_stream():
    """Verify streaming CSV generation format."""
    csv_lines = ClinicalAuditService.generate_csv_stream()
    assert len(csv_lines) >= 1
    header = csv_lines[0]
    assert "audit_id" in header
    assert "safety_score" in header


def test_audit_service_pdf_certificate_generation():
    """Verify ReportLab PDF certificate generation returns valid PDF bytes."""
    pdf_bytes = ClinicalAuditService.generate_pdf_certificate(
        assessment_id="TEST-CERT-001",
        patient_info={"Age": 48, "Gender": "Female"},
        deficiencies=["Vitamin D Deficiency", "Folate Deficiency"],
        safety_score=92.0,
        safety_tier="LOW",
        governance_notes="Model validated against NHANES 2017-2020 cycle. Calibration certified."
    )
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_api_monitoring_metrics_endpoint():
    """GET /api/v1/monitoring/metrics returns telemetry stats."""
    resp = client.get("/api/v1/monitoring/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_screenings_evaluated" in data
    assert "latency_percentiles" in data
    assert "overall_risk_distribution" in data


def test_api_alerts_endpoints():
    """GET /api/v1/monitoring/alerts and POST acknowledgment."""
    resp = client.get("/api/v1/monitoring/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data

    if data["alerts"]:
        target_alert = data["alerts"][0]
        ack_resp = client.post(
            f"/api/v1/monitoring/alerts/{target_alert['alert_id']}/acknowledge",
            json={"acknowledged_by": "Auditor Lead"}
        )
        assert ack_resp.status_code == 200
        assert ack_resp.json()["is_acknowledged"] is True


def test_api_audit_logs_endpoint():
    """GET /api/v1/audit/logs returns audit event logs."""
    resp = client.get("/api/v1/audit/logs?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "records" in data
    assert len(data["records"]) >= 1


def test_api_audit_csv_export_endpoint():
    """GET /api/v1/audit/export/csv returns downloadable CSV stream."""
    resp = client.get("/api/v1/audit/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "audit_id" in resp.text


def test_api_audit_pdf_certificate_endpoint():
    """GET /api/v1/audit/export/pdf/{audit_id} returns application/pdf."""
    # First get an audit record ID
    logs_resp = client.get("/api/v1/audit/logs?limit=1")
    audit_id = logs_resp.json()["records"][0]["audit_id"]

    resp = client.get(f"/api/v1/audit/export/pdf/{audit_id}")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "application/pdf"
    assert resp.content.startswith(b"%PDF")
