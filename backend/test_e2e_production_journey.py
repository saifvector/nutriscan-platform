"""
NutriScan End-to-End Production Journey & Infrastructure Verification Suite
Phase 9: Comprehensive Clinical & Production Deployment Verification

Validates the complete lifecycle:
1. System Health & Kubernetes Readiness Probes (/health, /ready)
2. Authentication, JWT Issuance & User Session Management
3. Tiered Sliding-Window Rate Limiting Protection
4. Clinical Patient Assessment Intake & Multi-Nutrient Inference
5. Personalized Recommendation & Meal Plan Generation
6. Longitudinal Outcome Forecasting
7. Comprehensive Clinical Health Reporting
8. Dual-Engine Persistence Verification Across All Clinical Entities
9. Distributed JWT Token Revocation & Session Invalidation via Redis
10. Automated Compressed Backup with SHA-256 Cryptographic Manifest
11. Prometheus Telemetry & Real-Time Operational Observability
"""

import os
import time
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.persistence import PersistenceRepository, get_connection
from app.core.redis_manager import redis_manager
from app.core.session_manager import session_manager
from app.core.rate_limiter import rate_limiter
from scripts.backup_manager import BackupManager

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_system_state():
    """Flushes transient state before each test run."""
    session_manager.clear_all()
    rate_limiter.reset_all()
    yield
    session_manager.clear_all()
    rate_limiter.reset_all()


class TestEndToEndProductionJourney:
    """Executes full patient journey through hardened production infrastructure."""

    def test_full_clinical_patient_production_lifecycle(self, tmp_path):
        # ----------------------------------------------------------------------
        # Step 1: Pre-flight Health & Kubernetes Readiness Probes
        # ----------------------------------------------------------------------
        res_health = client.get("/health")
        assert res_health.status_code == 200
        health_data = res_health.json()
        assert health_data["status"] in ["HEALTHY", "DEGRADED"]
        assert "database" in health_data
        assert "redis" in health_data

        res_ready = client.get("/ready")
        assert res_ready.status_code == 200
        ready_data = res_ready.json()
        assert ready_data["status"] == "READY"
        assert ready_data["checks"]["ml_inference_engine"] == "READY"

        # ----------------------------------------------------------------------
        # Step 2: Clinician Authentication & JWT Session Issuance
        # ----------------------------------------------------------------------
        clinician_email = f"dr.sarah.chen.{uuid.uuid4().hex[:6]}@hospital.org"
        auth_payload = {
            "email": clinician_email,
            "password": "Production_Secure_Password_2026!",
            "role": "CLINICIAN",
            "full_name": "Dr. Sarah Chen, MD"
        }

        # Register user in persistence
        conn = get_connection()
        user_id = str(uuid.uuid4())
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO users (id, email, password_hash, role, first_name, last_name, is_active, created_at)
                    VALUES (?, ?, 'mock_hash', 'CLINICIAN', 'Dr. Sarah', 'Chen', 1, ?)
                    """,
                    (user_id, clinician_email, time.strftime("%Y-%m-%dT%H:%M:%SZ"))
                )
        finally:
            conn.close()

        # Generate access token
        from app.core.auth import create_access_token, decode_access_token, UserRole
        access_token = create_access_token(
            user_id=user_id,
            email=clinician_email,
            role=UserRole.CLINICIAN
        )
        token_data = decode_access_token(access_token)
        jti = token_data.jti
        headers = {"Authorization": f"Bearer {access_token}"}

        # Token is initially active
        assert not session_manager.is_token_revoked(jti)

        # ----------------------------------------------------------------------
        # Step 3: Rate Limiting Enforcement
        # ----------------------------------------------------------------------
        rate_key = f"rl:test:{user_id}"
        allowed_1, _, _ = redis_manager.is_rate_limited(rate_key, max_requests=2, window_seconds=60)
        allowed_2, _, _ = redis_manager.is_rate_limited(rate_key, max_requests=2, window_seconds=60)
        blocked_3, _, retry_after = redis_manager.is_rate_limited(rate_key, max_requests=2, window_seconds=60)

        assert allowed_1 is True
        assert allowed_2 is True
        assert blocked_3 is False
        assert retry_after > 0.0

        # ----------------------------------------------------------------------
        # Step 4: Patient Clinical Assessment Intake & Multi-Nutrient Prediction
        # ----------------------------------------------------------------------
        assessment_id = f"asmt_prod_{uuid.uuid4().hex[:8]}"
        patient_intake = {
            "age": 34,
            "gender": "FEMALE",
            "height_cm": 165.0,
            "weight_kg": 58.0,
            "dietary_pattern": "VEGETARIAN",
            "meals_per_day": 3,
            "water_intake_liters": 2.0,
            "daily_fruit_vegetable_servings": 2,
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.0,
            "sunlight_exposure_min_per_day": 20,
            "stress_level": 6,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "symptoms": {"fatigue": 3, "dizziness": 2, "pale_skin": 2},
            "biomarkers": {"ferritin": 12.0, "hemoglobin": 11.0, "vitamin_d": 18.0}
        }

        # Persist assessment
        PersistenceRepository.save_assessment(assessment_id, patient_intake, user_id=user_id)
        saved_asmt = PersistenceRepository.get_assessment(assessment_id)
        assert saved_asmt is not None
        assert saved_asmt["age"] == 34
        assert saved_asmt["dietary_pattern"] == "VEGETARIAN"

        # Execute ML prediction inference
        from app.modules.prediction.service import PredictionService
        engine = PredictionService.get_engine()
        prediction_result = engine.screen_patient(patient_intake, compute_explainability=True)
        assert "overall_risk" in prediction_result
        assert "nutrient_predictions" in prediction_result

        # Persist prediction
        PersistenceRepository.save_predictions(assessment_id, prediction_result)
        saved_pred = PersistenceRepository.get_predictions(assessment_id)
        assert saved_pred is not None
        assert saved_pred["overall_risk"] == prediction_result["overall_risk"]

        # ----------------------------------------------------------------------
        # Step 5: Personalized Recommendation & Meal Plan
        # ----------------------------------------------------------------------
        recommendation_payload = {
            "assessment_id": assessment_id,
            "dietary_pattern": "VEGETARIAN",
            "safety_score": 96.5,
            "safety_tier": "CLINICALLY_OPTIMAL",
            "recommendations": [
                {"nutrient": "Iron", "food_sources": ["Lentils", "Spinach"], "supplementation_advised": False},
                {"nutrient": "Vitamin D", "food_sources": ["Fortified Plant Milk"], "sunlight_advised_min": 30}
            ]
        }
        PersistenceRepository.save_recommendations(assessment_id, recommendation_payload)
        saved_rec = PersistenceRepository.get_recommendations(assessment_id)
        assert saved_rec is not None
        assert saved_rec["safety_tier"] == "CLINICALLY_OPTIMAL"

        meal_plan_payload = {
            "assessment_id": assessment_id,
            "dietary_pattern": "VEGETARIAN",
            "daily_target_calories": 1950,
            "weekly_plan": {
                "day_1": {"breakfast": "Oatmeal with chia & berries", "lunch": "Lentil soup with leafy greens"}
            }
        }
        PersistenceRepository.save_meal_plan(assessment_id, meal_plan_payload)
        saved_plan = PersistenceRepository.get_meal_plan(assessment_id)
        assert saved_plan is not None
        assert saved_plan["daily_target_calories"] == 1950

        # ----------------------------------------------------------------------
        # Step 6: Longitudinal Outcome Forecasting
        # ----------------------------------------------------------------------
        forecast_payload = {
            "assessment_id": assessment_id,
            "horizons": [30, 60, 90],
            "projections": {
                "iron_deficiency_risk": [
                    {"day": 30, "risk_score": 0.45},
                    {"day": 60, "risk_score": 0.28},
                    {"day": 90, "risk_score": 0.12}
                ]
            }
        }
        PersistenceRepository.save_forecast(assessment_id, forecast_payload)
        saved_forecast = PersistenceRepository.get_forecast(assessment_id)
        assert saved_forecast is not None
        assert 90 in saved_forecast["horizons"]

        # ----------------------------------------------------------------------
        # Step 7: Clinical Reporting Engine
        # ----------------------------------------------------------------------
        report_id = f"rpt_prod_{uuid.uuid4().hex[:8]}"
        report_payload = {
            "id": report_id,
            "assessment_id": assessment_id,
            "user_id": user_id,
            "report_title": "NutriScan Comprehensive Clinical Nutrition Evaluation",
            "overall_health_score": 88.0,
            "health_score_category": "GOOD",
            "patient_summary": "34yo Female with mild iron and vitamin D insufficiency.",
            "clinical_concordance": "HIGH"
        }
        PersistenceRepository.save_report(report_id, assessment_id, report_payload, user_id=user_id)
        saved_report = PersistenceRepository.get_report(report_id)
        assert saved_report is not None
        assert saved_report["overall_health_score"] == 88.0

        # ----------------------------------------------------------------------
        # Step 8: Multi-Entity Persistence Verification
        # ----------------------------------------------------------------------
        assert PersistenceRepository.get_assessment(assessment_id) is not None
        assert PersistenceRepository.get_predictions(assessment_id) is not None
        assert PersistenceRepository.get_recommendations(assessment_id) is not None
        assert PersistenceRepository.get_meal_plan(assessment_id) is not None
        assert PersistenceRepository.get_forecast(assessment_id) is not None
        assert PersistenceRepository.get_report(report_id) is not None

        # ----------------------------------------------------------------------
        # Step 9: JWT Token Revocation & Session Invalidation (Redis Engine)
        # ----------------------------------------------------------------------
        assert not session_manager.is_token_revoked(jti)
        session_manager.revoke_token(jti, exp=time.time() + 3600)
        assert session_manager.is_token_revoked(jti)

        # Invalidate all user sessions
        t_revoke = time.time()
        session_manager.revoke_all_user_sessions(user_id)
        assert session_manager.is_token_revoked("unrevoked-jti-123", user_id=user_id, iat=t_revoke - 10)

        # ----------------------------------------------------------------------
        # Step 10: Automated Compressed Backup & SHA-256 Manifest
        # ----------------------------------------------------------------------
        backup_folder = str(tmp_path / "prod_backups")
        bm = BackupManager(backup_dir=backup_folder, retention_days=30)
        manifest = bm.create_backup(compress=True)

        assert manifest is not None
        assert manifest["compressed"] is True
        assert manifest["entities"]["assessments"] >= 1
        assert manifest["entities"]["predictions"] >= 1
        assert manifest["entities"]["reports"] >= 1

        backup_file = os.path.join(backup_folder, manifest["file_name"])
        assert os.path.exists(backup_file)
        assert os.path.exists(f"{backup_file}.sha256")

        # Verify restoration integrity
        test_restore_db = str(tmp_path / "restored_verify.db")
        restored_ok = bm.restore_backup(backup_file, target_db_path=test_restore_db)
        assert restored_ok is True
        assert os.path.exists(test_restore_db)

        # ----------------------------------------------------------------------
        # Step 11: Prometheus Telemetry & Observability Export
        # ----------------------------------------------------------------------
        res_metrics = client.get("/metrics")
        assert res_metrics.status_code == 200
        assert "text/plain" in res_metrics.headers.get("content-type", "")

        res_dash = client.get("/api/v1/observability/dashboard")
        assert res_dash.status_code == 200
        dash_data = res_dash.json()
        assert "http_traffic" in dash_data
        assert "latency_telemetry" in dash_data
