"""
Test Advanced Security Suite (Phase 1 & Phase 3)
NutriScan Final Gap Closure Program

Validates:
1. JWT Signature Verification & Tampering Rejection
2. `alg=none` Attack Prevention
3. Expired Token Handling
4. Broken Authentication (Unauthenticated Requests to Protected Endpoints)
5. Vertical Privilege Escalation Rejection (PATIENT -> CLINICIAN / PATIENT -> ADMIN)
6. Horizontal Privilege Escalation / IDOR Prevention (User A cannot access User B's records)
7. Sliding-Window Rate Limiting (5 rapid login attempts trigger RFC-7807 429)
8. PBKDF2 Password Hashing & Sensitive Data Exposure Prevention (No password hash leaks)
9. Security Headers Enforcement (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
"""

import time
import uuid
from datetime import timedelta
import pytest
import jwt
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    UserRole,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)
from app.core.persistence import PersistenceRepository
from app.core.rate_limiter import global_rate_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_security_environment():
    """Reset rate limits and ensure persistence is active."""
    global_rate_limiter.reset_all()
    yield
    global_rate_limiter.reset_all()


class TestPasswordSecurity:
    """Validates PBKDF2-HMAC-SHA256 password hashing security."""

    def test_password_hashing_and_verification(self):
        password = "ClinicalSecurePassword2026!"
        hashed = hash_password(password)

        assert hashed.startswith("pbkdf2_sha256$100000$")
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword123!", hashed) is False

    def test_unique_salts_generated_per_hash(self):
        password = "IdenticalPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2, "Salts must be unique across password hashes to prevent rainbow table attacks."
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTSecurityAndTampering:
    """Validates JWT cryptography, signature verification, and attack resistance."""

    def test_valid_token_issuance_and_decoding(self):
        token = create_access_token(
            user_id="user-12345",
            email="doctor@hospital.org",
            role=UserRole.CLINICIAN,
            expires_delta=timedelta(minutes=30)
        )
        payload = decode_access_token(token)

        assert payload.user_id == "user-12345"
        assert payload.email == "doctor@hospital.org"
        assert payload.role == UserRole.CLINICIAN
        assert payload.jti
        assert payload.exp > time.time()

    def test_jwt_tampered_payload_rejected(self):
        """Modifying the payload without a valid signature must be rejected."""
        token = create_access_token(
            user_id="patient-1",
            email="patient@test.org",
            role=UserRole.PATIENT
        )
        parts = token.split(".")
        # Tamper with payload (middle part)
        tampered_token = f"{parts[0]}.eyJzdWIiOiAicGF0aWVudC0xIiwgInJvbGUiOiAiQURNSU4ifQ.{parts[2]}"

        with pytest.raises(Exception):
            decode_access_token(tampered_token)

    def test_jwt_tampered_signature_rejected(self):
        token = create_access_token(
            user_id="patient-1",
            email="patient@test.org",
            role=UserRole.PATIENT
        )
        parts = token.split(".")
        # Invalidate signature
        corrupted_signature = parts[2][:-4] + "ABCD"
        tampered_token = f"{parts[0]}.{parts[1]}.{corrupted_signature}"

        with pytest.raises(Exception):
            decode_access_token(tampered_token)

    def test_jwt_alg_none_attack_rejected(self):
        """Prevents critical CVE where alg is set to 'none' and signature is omitted."""
        header = {"alg": "none", "typ": "JWT"}
        payload = {
            "sub": "attacker-id",
            "email": "attacker@evil.com",
            "role": "ADMIN",
            "exp": time.time() + 3600,
            "iat": time.time()
        }
        import base64
        import json

        hdr_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        pay_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        alg_none_token = f"{hdr_b64}.{pay_b64}."

        with pytest.raises(Exception):
            decode_access_token(alg_none_token)

    def test_expired_token_rejected(self):
        expired_token = create_access_token(
            user_id="expired-user",
            email="expired@test.org",
            role=UserRole.PATIENT,
            expires_delta=timedelta(minutes=-10)  # Expired 10 minutes ago
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(expired_token)
        assert exc_info.value.status_code == 401


class TestAuthenticationAndUserEndpoints:
    """Validates registration, login, token refresh, and data leak protection."""

    def test_user_registration_and_login_flow(self):
        unique_email = f"test_{uuid.uuid4().hex[:8]}@nutriscan.org"
        reg_payload = {
            "email": unique_email,
            "password": "SecurePassword123!",
            "first_name": "Sarah",
            "last_name": "Mitchell",
            "role": "CLINICIAN"
        }

        # 1. Register
        reg_res = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201
        data = reg_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == unique_email
        assert data["role"] == "CLINICIAN"
        # Sensitive data check: password hash must NEVER be exposed
        assert "password" not in data
        assert "password_hash" not in data

        # 2. Login
        login_res = client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data

        # 3. Authenticated Profile Fetch
        auth_header = {"Authorization": f"Bearer {login_data['access_token']}"}
        me_res = client.get("/api/v1/auth/me", headers=auth_header)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == unique_email
        assert "password" not in me_res.json()
        assert "password_hash" not in me_res.json()

    def test_login_with_incorrect_password_fails(self):
        unique_email = f"test_{uuid.uuid4().hex[:8]}@nutriscan.org"
        client.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "CorrectPassword123!",
            "role": "PATIENT"
        })

        bad_login = client.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        assert bad_login.status_code == 401
        assert "Invalid email or password" in bad_login.json()["detail"]


class TestRoleBasedAccessControlAndPrivilegeEscalation:
    """Validates vertical privilege escalation protections."""

    def test_unauthenticated_access_to_clinician_reviews_fails(self):
        res = client.post("/api/v1/validation/reviews", json={
            "assessment_id": str(uuid.uuid4()),
            "reviewer_name": "Anonymous",
            "reviewer_role": "Doctor",
            "agreement_status": "AGREE"
        })
        assert res.status_code == 401

    def test_patient_cannot_perform_clinician_sign_off(self):
        """Vertical privilege escalation: PATIENT attempting to call CLINICIAN-only review endpoint."""
        patient_token = create_access_token(
            user_id=str(uuid.uuid4()),
            email="patient@test.org",
            role=UserRole.PATIENT
        )
        headers = {"Authorization": f"Bearer {patient_token}"}

        res = client.post("/api/v1/validation/reviews", json={
            "assessment_id": str(uuid.uuid4()),
            "reviewer_name": "Patient Fraud",
            "reviewer_role": "Doctor",
            "agreement_status": "AGREE"
        }, headers=headers)

        assert res.status_code == 403
        assert "Access forbidden: requires one of roles" in res.json()["detail"]

    def test_clinician_cannot_perform_admin_database_reconciliation(self):
        """Vertical privilege escalation: CLINICIAN attempting to call ADMIN-only endpoint."""
        clinician_token = create_access_token(
            user_id=str(uuid.uuid4()),
            email="clinician@hospital.org",
            role=UserRole.CLINICIAN
        )
        headers = {"Authorization": f"Bearer {clinician_token}"}

        res = client.post("/api/v1/pipeline/reconcile-coverage", headers=headers)
        assert res.status_code == 403
        assert "Access forbidden: requires one of roles" in res.json()["detail"]


class TestIDORAndHorizontalPrivilegeEscalation:
    """Validates Insecure Direct Object Reference (IDOR) protections across resources."""

    def test_patient_cannot_view_another_patients_meal_plan(self):
        user_a_id = str(uuid.uuid4())
        user_b_id = str(uuid.uuid4())
        as_id = str(uuid.uuid4())

        # Save assessment belonging to User A
        PersistenceRepository.save_assessment(as_id, {"user_id": user_a_id, "age": 42})

        # User B attempts to generate/access meal plan for User A's assessment
        token_user_b = create_access_token(user_id=user_b_id, email="b@test.org", role=UserRole.PATIENT)
        headers = {"Authorization": f"Bearer {token_user_b}"}

        res = client.post(
            "/api/v1/meal-plans/weekly",
            json={"assessment_id": as_id, "target_deficiencies": ["Iron"]},
            headers=headers
        )
        assert res.status_code == 403
        assert "Access denied" in res.json()["detail"]

    def test_patient_cannot_view_another_patients_report(self):
        user_a_id = str(uuid.uuid4())
        user_b_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        as_id = str(uuid.uuid4())

        # Persist assessment and report for User A
        PersistenceRepository.save_assessment(as_id, {"user_id": user_a_id, "age": 42})
        report_data = {
            "id": report_id,
            "assessment_id": as_id,
            "user_id": user_a_id,
            "report_title": "Confidential Health Report",
            "overall_health_score": 85.0,
            "health_score_category": "OPTIMAL",
            "status": "COMPLETED",
            "summary_text": "Nutritional intake indicates optimal profile.",
            "report_payload": {"test": "data"},
            "generated_at": "2026-09-16T10:00:00"
        }
        PersistenceRepository.save_report(report_id, as_id, report_data)

        # User B attempts to fetch User A's report
        token_user_b = create_access_token(user_id=user_b_id, email="userb@test.org", role=UserRole.PATIENT)
        headers = {"Authorization": f"Bearer {token_user_b}"}

        res = client.get(f"/api/v1/reports/{report_id}", headers=headers)
        assert res.status_code == 403
        assert "Access denied" in res.json()["detail"]

    def test_clinician_can_access_patient_records(self):
        """Clinicians are authorized to review patient records for care delivery."""
        patient_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        as_id = str(uuid.uuid4())

        PersistenceRepository.save_assessment(as_id, {"user_id": patient_id, "age": 55})
        report_data = {
            "id": report_id,
            "assessment_id": as_id,
            "user_id": patient_id,
            "report_title": "Patient Clinical Report",
            "overall_health_score": 72.0,
            "health_score_category": "MODERATE",
            "status": "COMPLETED",
            "summary_text": "Patient exhibits moderate deficiency risks.",
            "report_payload": {"test": "clinician_access"},
            "generated_at": "2026-09-16T10:00:00"
        }
        PersistenceRepository.save_report(report_id, as_id, report_data)

        clinician_token = create_access_token(
            user_id=str(uuid.uuid4()),
            email="dr.house@hospital.org",
            role=UserRole.CLINICIAN
        )
        headers = {"Authorization": f"Bearer {clinician_token}"}

        res = client.get(f"/api/v1/reports/{report_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["report_title"] == "Patient Clinical Report"


class TestSlidingWindowRateLimiting:
    """Validates brute-force mitigation and rate limiting."""

    def test_login_endpoint_rate_limits_after_exceeding_threshold(self):
        global_rate_limiter.reset_all()
        login_payload = {
            "email": "bruteforce@target.org",
            "password": "GuessedPassword123"
        }

        # Threshold for auth is 5 requests per 60s
        responses = []
        for _ in range(7):
            res = client.post("/api/v1/auth/login", json=login_payload)
            responses.append(res.status_code)

        # First 5 should reach the handler (even if returning 401 for bad creds)
        assert responses[:5] == [401, 401, 401, 401, 401]
        # 6th and 7th requests MUST be rate-limited with 429
        assert responses[5] == 429
        assert responses[6] == 429


class TestSecurityHeadersEnforcement:
    """Validates OWASP-compliant security headers on all responses."""

    def test_security_headers_present_on_endpoints(self):
        res = client.get("/health")
        assert res.status_code == 200

        headers = res.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert "default-src 'self'" in headers["Content-Security-Policy"]
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "X-Correlation-ID" in headers
