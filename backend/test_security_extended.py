"""
Comprehensive Extended Security Test Suite for NutriScan Platform.
Phase 2 Hardening:
- Cross-Site Scripting (XSS) Prevention & HTML Entity Neutralization
- Cross-Site Request Forgery (CSRF) & Origin Defense
- Server-Side Request Forgery (SSRF) Defense against Private/Metadata IPs
- Path Traversal Defense against Directory Escaping & Null Bytes
- File Upload Abuse & Executable Extension Prevention
- Secret Exposure Scrubbing & Credential Leakage Prevention
- API Fuzzing & Malformed Payload Handling
- HTTP Header Injection & Open Redirect Defense
- JWT Revocation Lifecycle (Logout, Password Change, Invalidation)
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security_guard import SecurityGuard
from app.core.session_manager import session_manager
from app.core.persistence import PersistenceRepository
from app.core.auth import create_access_token, decode_access_token


@pytest.fixture(scope="module")
def client():
    """Provides a FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


class TestXSSMitigation:
    """Validates XSS injection defenses and HTML entity escaping."""

    def test_script_tag_neutralization(self):
        malicious = "<script>alert('XSS-ATTACK');</script>Hello Clinician"
        sanitized = SecurityGuard.sanitize_xss(malicious)
        assert "<script>" not in sanitized
        assert "alert('XSS-ATTACK');" not in sanitized
        assert "Hello Clinician" in sanitized

    def test_event_handler_neutralization(self):
        malicious = '<img src=x onerror="alert(1)">'
        sanitized = SecurityGuard.sanitize_xss(malicious)
        assert "onerror=" not in sanitized
        assert "blocked-handler=" in sanitized

    def test_javascript_protocol_neutralization(self):
        malicious = '<a href="javascript:alert(document.cookie)">Click</a>'
        sanitized = SecurityGuard.sanitize_xss(malicious)
        assert "javascript:" not in sanitized
        assert "blocked-scheme:" in sanitized

    def test_api_responses_serve_json_not_html(self, client):
        """Ensures API responses enforce application/json MIME to prevent browser HTML interpretation."""
        response = client.get("/health")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type


class TestSSRFMitigation:
    """Validates defenses against Server-Side Request Forgery."""

    def test_blocks_localhost_and_loopback(self):
        for url in ["http://localhost:8080/admin", "http://127.0.0.1:5432", "http://[::1]/internal"]:
            is_safe, reason = SecurityGuard.is_ssrf_safe_url(url)
            assert not is_safe, f"Expected {url} to be blocked, reason: {reason}"

    def test_blocks_cloud_metadata_endpoints(self):
        metadata_urls = [
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://169.254.169.254/metadata/v1"
        ]
        for url in metadata_urls:
            is_safe, reason = SecurityGuard.is_ssrf_safe_url(url)
            assert not is_safe, f"Metadata service {url} must be blocked"

    def test_blocks_disallowed_schemes(self):
        schemes = [
            "file:///etc/passwd",
            "gopher://127.0.0.1:6379/_flushall",
            "ftp://anonymous@ftp.example.com/test",
            "data:text/html,<script>alert(1)</script>"
        ]
        for s in schemes:
            is_safe, reason = SecurityGuard.is_ssrf_safe_url(s)
            assert not is_safe, f"Scheme {s} must be blocked"


class TestPathTraversalMitigation:
    """Validates defenses against path traversal and arbitrary file reads."""

    def test_blocks_parent_directory_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dangerous_paths = [
                "../../etc/passwd",
                "..\\..\\windows\\system32\\cmd.exe",
                "folder/../../../secret.key",
                "/etc/shadow",
                "\\windows\\win.ini"
            ]
            for p in dangerous_paths:
                is_safe, _ = SecurityGuard.sanitize_file_path(tmpdir, p)
                assert not is_safe, f"Path traversal '{p}' must be rejected"

    def test_blocks_null_byte_in_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            null_byte_path = "report.pdf\x00.exe"
            is_safe, reason = SecurityGuard.sanitize_file_path(tmpdir, null_byte_path)
            assert not is_safe
            assert "Null byte" in reason

    def test_allows_valid_subpath(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = "reports/patient_123.pdf"
            is_safe, resolved = SecurityGuard.sanitize_file_path(tmpdir, valid_path)
            assert is_safe
            assert tmpdir in resolved


class TestFileUploadAbuse:
    """Validates defenses against malicious file uploads."""

    def test_rejects_executable_extensions(self):
        disallowed = ["malware.exe", "script.sh", "exploit.bat", "webshell.php", "backdoor.py"]
        for fname in disallowed:
            is_valid, reason = SecurityGuard.validate_file_upload(fname, b"content")
            assert not is_valid
            assert "disallowed" in reason.lower()

    def test_rejects_oversized_payloads(self):
        fname = "massive_data.csv"
        oversized_blob = b"A" * 1500
        is_valid, reason = SecurityGuard.validate_file_upload(fname, oversized_blob, max_size_bytes=1000)
        assert not is_valid
        assert "exceeds maximum allowed size" in reason

    def test_allows_permitted_clinical_extensions(self):
        allowed = ["lab_results.pdf", "biomarkers.csv", "profile.json", "scan.png"]
        for fname in allowed:
            is_valid, _ = SecurityGuard.validate_file_upload(fname, b"VALID_SAMPLE_CONTENT")
            assert is_valid


class TestSecretExposureMitigation:
    """Validates that sensitive secrets and credentials are scrubbed."""

    def test_scrubs_bearer_tokens(self):
        log_msg = "User authenticated with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.xyz"
        scrubbed = SecurityGuard.scrub_sensitive_secrets(log_msg)
        assert "eyJhbGci" not in scrubbed
        assert "[REDACTED_SECRET]" in scrubbed

    def test_scrubs_passwords_and_connection_strings(self):
        log_msg = "Failed to connect to postgresql://nutrient_admin:p@ssw0rd123@localhost:5432/db"
        scrubbed = SecurityGuard.scrub_sensitive_secrets(log_msg)
        assert "p@ssw0rd123" not in scrubbed
        assert "[REDACTED_SECRET]" in scrubbed


class TestAPIFuzzingAndMalformedPayloads:
    """Tests API resilience against malformed inputs and fuzzing patterns."""

    def test_null_byte_in_json_handled_safely(self, client):
        payload = {
            "age": 30,
            "gender": "MALE\x00_INJECTION",
            "dietary_pattern": "VEGETARIAN"
        }
        # FastAPI / Pydantic validation handles null bytes cleanly without 500 crash
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code in [400, 422]

    def test_negative_age_rejected_by_pydantic_schema(self, client):
        payload = {
            "age": -15,
            "gender": "FEMALE",
            "height_cm": 160.0,
            "weight_kg": 55.0
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data.get("error") is True


class TestHeaderManipulationAndOpenRedirect:
    """Validates HTTP header protection and Open Redirect defense."""

    def test_header_injection_carriage_return_rejected(self):
        malicious_header = "clinical-session-1\r\nSet-Cookie: session=hacked"
        is_safe, _ = SecurityGuard.validate_header_value(malicious_header)
        assert not is_safe

    def test_open_redirect_rejects_external_hosts(self):
        malicious_redirects = [
            "https://evil-phishing.com/login",
            "http://attacker.com/steal-token",
            "//attacker.com/bypass"
        ]
        for url in malicious_redirects:
            is_safe, _ = SecurityGuard.validate_redirect_url(url)
            assert not is_safe

    def test_open_redirect_allows_safe_relative_paths(self):
        safe_redirects = ["/dashboard", "/login?success=1", "/clinician/review"]
        for url in safe_redirects:
            is_safe, resolved = SecurityGuard.validate_redirect_url(url)
            assert is_safe
            assert resolved == url


class TestJWTRevocationLifecycle:
    """Validates end-to-end JWT revocation, logout, and credential invalidation."""

    def test_explicit_token_revocation(self):
        from app.core.auth import UserRole
        from fastapi import HTTPException
        token = create_access_token(user_id="test_revocation_user", email="rev@test.org", role=UserRole.PATIENT)
        decoded = decode_access_token(token)
        assert decoded is not None
        jti = decoded.jti
        assert jti is not None

        # Verify token is active
        assert not session_manager.is_token_revoked(jti, "test_revocation_user", decoded.iat)

        # Revoke the token
        session_manager.revoke_token(jti, decoded.exp)
        assert session_manager.is_token_revoked(jti, "test_revocation_user", decoded.iat)

        # Verification through decode_access_token should raise HTTPException(401)
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    def test_logout_endpoint_revokes_calling_token(self, client):
        # Register and log in a dedicated user with unique email
        import uuid
        test_email = f"logout_{uuid.uuid4().hex[:8]}@nutriscan.test"
        reg_payload = {
            "email": test_email,
            "password": "SecurePassword123!",
            "first_name": "Revocation",
            "last_name": "Tester",
            "role": "PATIENT"
        }
        reg_res = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201
        
        login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # Call /auth/me with valid token
        me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200

        # Perform logout
        logout_res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "success"

        # Re-attempt /auth/me with the logged out token - MUST fail with 401
        me_after_logout = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_after_logout.status_code == 401
        assert "Bearer" in me_after_logout.headers.get("www-authenticate", "")

    def test_password_change_invalidates_all_active_sessions(self, client):
        import uuid
        test_email = f"pwd_reset_{uuid.uuid4().hex[:8]}@nutriscan.test"
        old_pwd = "OldPassword123!"
        new_pwd = "NewSecurePassword456!"

        reg_res = client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": old_pwd,
            "first_name": "Pwd",
            "last_name": "Tester",
            "role": "PATIENT"
        })
        assert reg_res.status_code == 201

        login_res = client.post("/api/v1/auth/login", json={"email": test_email, "password": old_pwd})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # Change password
        change_res = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"old_password": old_pwd, "new_password": new_pwd}
        )
        assert change_res.status_code == 200

        # Old token is now invalid due to session invalidation
        post_change_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert post_change_res.status_code == 401

        # Login with new password succeeds and gets new valid token
        new_login = client.post("/api/v1/auth/login", json={"email": test_email, "password": new_pwd})
        assert new_login.status_code == 200
        new_token = new_login.json()["access_token"]
        assert new_token != token

        # New token works
        me_new = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        assert me_new.status_code == 200
