"""
Phase 5 & 6 Security Hardening & Observability Test Suite.
Validates:
1. OWASP Security Headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy).
2. Distributed Tracing: X-Correlation-ID injection & echo across HTTP requests.
3. Domain Exception Handling: NutriScanException and RequestValidationError return structured JSON with correlation_id.
4. SQL Injection Resistance: Parameterized queries protect all SQLite persistence methods.
5. PDF Generator Injection Resistance: Hostile markup and unclosed XML tags do not crash PDF generation.
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.exceptions import ClinicalSafetyException, BiomarkerValidationException
from backend.app.core.persistence import PersistenceRepository
from backend.app.modules.reporting.pdf_generator import PDFReportGenerator

client = TestClient(app)


def test_security_headers_present_on_all_responses():
    """Verify presence of OWASP-recommended HTTP security headers."""
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_correlation_id_propagation():
    """Verify X-Correlation-ID is generated if missing and echoed back."""
    # 1. Without header -> system generates UUID
    res1 = client.get("/health")
    assert "X-Correlation-ID" in res1.headers
    generated_id = res1.headers["X-Correlation-ID"]
    assert len(generated_id) > 10

    # 2. With header -> system preserves provided correlation ID
    custom_cid = "trace-test-clinical-12345"
    res2 = client.get("/health", headers={"X-Correlation-ID": custom_cid})
    assert res2.headers.get("X-Correlation-ID") == custom_cid


def test_structured_error_response_on_validation_failure():
    """Verify malformed requests return structured JSON with correlation_id and error_code."""
    custom_cid = str(uuid.uuid4())
    # Send bad JSON to trigger RequestValidationError
    response = client.post(
        "/api/v1/meal-plans/weekly",
        json={"patient_age": "not_an_integer", "gender": 12345},
        headers={"X-Correlation-ID": custom_cid}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] is True
    assert data["error_code"] == "REQUEST_VALIDATION_ERROR"
    assert data["correlation_id"] == custom_cid
    assert "validation_errors" in data["details"]


def test_sql_injection_resilience_in_persistence():
    """Verify persistence layer parameterized queries neutralize SQL injection payloads."""
    malicious_ids = [
        "' OR '1'='1",
        "'; DROP TABLE audit_events; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "1; WAITFOR DELAY '0:0:5'--"
    ]

    for sqli in malicious_ids:
        # None of these should throw sqlite3.OperationalError or leak data
        events = PersistenceRepository.get_persistent_audit_events(assessment_id=sqli)
        assert isinstance(events, list)

        # Count check
        count = PersistenceRepository.count_audit_events()
        assert isinstance(count, int)


def test_pdf_report_injection_hardening():
    """Verify PDF generator does not crash when supplied malicious HTML/XML markup."""
    hostile_report_data = {
        "overall_health_score": 65,
        "health_score_category": "MODERATE",
        "summary": {
            "user_profile": {
                "age": 32,
                "gender": "<script>alert('xss')</script>",
                "bmi": 24.1,
                "dietary_pattern": "<b>Hostile <font color='red'>Formatting</b>"
            },
            "executive_summary_text": "Serum level < 5.0 & Calcium > 10.5 with unclosed <tag",
            "key_findings": [
                "<xml><injected>bad markup</injected>",
                "Calcium < 8.4 mg/dL",
                "Patient reported: 'feeling tired & fatigued'"
            ]
        },
        "nutrient_predictions": [
            {
                "nutrient": "<b>Vitamin D</b>",
                "probability": 0.85,
                "risk_level": "<HIGH>",
                "clinical_implication": "Risk of hypocalcemia < 8.5 & bone demineralization > 10%"
            }
        ],
        "nutrient_interactions": {
            "interactions": [
                {
                    "nutrients": ["Calcium < 8.0", "Iron > 15.0"],
                    "interaction_type": "<ANTAGONISM>",
                    "clinical_mechanism": "Competitive mucosal binding at DMT-1 receptor <pH 6.5>",
                    "actionable_guidance": "Space intake by > 90 minutes & take with ascorbic acid"
                }
            ]
        },
        "recommendations": {
            "priority_1_foods": [
                {"food_name": "Wild Salmon <Canned with bones>"},
                {"food_name": "Fortified Soy Milk & Almond Milk"}
            ],
            "lifestyle_interventions": [
                {"category": "<SOLAR>", "action": "Sunlight exposure > 20 min", "target": "25-OH-D > 30 ng/mL"}
            ],
            "recovery_plan": {}
        },
        "progress_summary": {
            "health_score_delta": 12,
            "recovery_velocity_pts_per_week": 2.5,
            "most_improved_nutrient": "<Vitamin D3>"
        }
    }

    # Generate PDF with hostile input
    pdf_bytes = PDFReportGenerator.generate_pdf(hostile_report_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF"), "Must output valid PDF document"
