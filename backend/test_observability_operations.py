"""
Test Observability & Operational Readiness Suite (Phase 6)
NutriScan Final Gap Closure Program

Validates:
1. Structured JSON Logging Formatting & Correlation ID Traceability
2. Latency Telemetry (p50, p95, p99) for Predictions, Forecasts, and Recommendations
3. HTTP Status Code Distribution & Real-Time Error Rate Tracking
4. Automated Production Alert Threshold Detection (p95 latency spike, 5xx error rate)
5. Production Observability Dashboard Endpoint (/api/v1/observability/dashboard)
"""

import json
import logging
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.observability import (
    JSONStructuredFormatter,
    TelemetryTracker,
    telemetry_tracker,
    setup_structured_logging
)

client = TestClient(app)


class TestStructuredLogging:
    """Validates structured JSON logging output and machine parseability."""

    def test_json_formatter_produces_valid_json_with_metadata(self):
        formatter = JSONStructuredFormatter()
        logger = logging.getLogger("test_clinical_audit")
        record = logger.makeRecord(
            name="test_clinical_audit",
            level=logging.INFO,
            fn="service.py",
            lno=42,
            msg="Clinical decision support inference completed.",
            args=(),
            exc_info=None,
            extra={"correlation_id": "cid-9921-xyz", "assessment_id": "as-7712"}
        )

        formatted_str = formatter.format(record)
        # Parse output as JSON
        log_json = json.loads(formatted_str)

        assert log_json["level"] == "INFO"
        assert log_json["logger"] == "test_clinical_audit"
        assert log_json["message"] == "Clinical decision support inference completed."
        assert "timestamp" in log_json
        assert log_json["correlation_id"] == "cid-9921-xyz"
        assert log_json["assessment_id"] == "as-7712"


class TestTelemetryTrackerAndAlerts:
    """Validates real-time telemetry, percentiles, and operational thresholds."""

    @pytest.fixture
    def fresh_tracker(self):
        return TelemetryTracker(max_history=1000)

    def test_latency_percentile_calculations(self, fresh_tracker):
        # Simulate 100 requests with known latencies: 1ms to 100ms
        for i in range(1, 101):
            fresh_tracker.record_latency("predictions", float(i))

        percentiles = fresh_tracker.get_latency_percentiles("predictions")
        assert percentiles["count"] == 100
        assert 49.0 <= percentiles["p50_ms"] <= 51.0
        assert 94.0 <= percentiles["p95_ms"] <= 96.0
        assert 98.0 <= percentiles["p99_ms"] <= 100.0

    def test_http_status_and_error_rate_calculation(self, fresh_tracker):
        # 95 successful requests, 3 client errors, 2 server errors
        for _ in range(95):
            fresh_tracker.record_http_status(200)
        for _ in range(3):
            fresh_tracker.record_http_status(404)
        for _ in range(2):
            fresh_tracker.record_http_status(500)

        metrics = fresh_tracker.get_http_metrics()
        assert metrics["total_requests"] == 100
        assert metrics["2xx_success"] == 95
        assert metrics["4xx_client_error"] == 3
        assert metrics["5xx_server_error"] == 2
        # Error rate is (3 + 2) / 100 = 5.0%
        assert metrics["error_rate_pct"] == 5.0

    def test_alert_triggered_on_high_error_rate(self, fresh_tracker):
        # Trigger high error rate (> 5.0%)
        for _ in range(80):
            fresh_tracker.record_http_status(200)
        for _ in range(20):
            fresh_tracker.record_http_status(500)

        alerts = fresh_tracker.check_alert_thresholds()
        assert len(alerts) >= 1
        high_err_alert = next((a for a in alerts if a["alert"] == "HIGH_ERROR_RATE"), None)
        assert high_err_alert is not None
        assert high_err_alert["severity"] == "CRITICAL"
        assert high_err_alert["current_value"] == 20.0

    def test_alert_triggered_on_high_p95_latency(self, fresh_tracker):
        # Trigger high p95 latency (> 500ms)
        for _ in range(100):
            fresh_tracker.record_latency("predictions", 650.0)

        alerts = fresh_tracker.check_alert_thresholds()
        latency_alert = next((a for a in alerts if a["alert"] == "HIGH_P95_LATENCY"), None)
        assert latency_alert is not None
        assert latency_alert["severity"] == "WARNING"
        assert latency_alert["current_value"] == 650.0


class TestObservabilityDashboardAPI:
    """Validates the live observability dashboard REST API endpoint."""

    def test_observability_dashboard_endpoint(self):
        # Record sample traffic
        telemetry_tracker.record_latency("predictions", 45.2)
        telemetry_tracker.record_latency("forecasts", 85.0)
        telemetry_tracker.record_latency("recommendations", 32.1)
        telemetry_tracker.record_http_status(200)

        res = client.get("/api/v1/observability/dashboard")
        assert res.status_code == 200
        dashboard = res.json()

        assert dashboard["status"] in ["OPERATIONAL", "HEALTHY", "DEGRADED"]
        assert "timestamp" in dashboard
        assert "http_traffic" in dashboard
        assert "latency_telemetry" in dashboard
        assert "predictions" in dashboard["latency_telemetry"]
        assert "forecasts" in dashboard["latency_telemetry"]
        assert "recommendations" in dashboard["latency_telemetry"]
        assert "alerts" in dashboard
        assert dashboard["persistence"]["wal_mode"] is True


class TestProductionHealthAndReadyProbes:
    """Validates /health, /ready, and /metrics endpoints for production container orchestrators."""

    def test_health_endpoint_contains_redis_and_persistence(self):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ["HEALTHY", "DEGRADED"]
        assert "database" in data
        assert "redis" in data
        assert data["redis"]["status"] == "HEALTHY"
        assert "persistence_ready" in data

    def test_ready_readiness_probe_returns_200(self):
        res = client.get("/ready")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "READY"
        assert "checks" in data
        assert data["checks"]["ml_inference_engine"] == "READY"
        assert data["checks"]["persistence_layer"] == "HEALTHY"
        assert "database" in data["checks"]
        assert "redis_distributed" in data["checks"]

    def test_prometheus_metrics_endpoint(self):
        res = client.get("/metrics")
        assert res.status_code == 200
        assert "text/plain" in res.headers.get("content-type", "")
        body = res.text
        # Prometheus format validation
        assert "# HELP" in body or "# TYPE" in body or "nutriscan" in body.lower()

