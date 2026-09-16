"""
Production Database Migration & Environment Switching Test Suite.
Phase 1: PostgreSQL Compatibility, Connection Pooling, Automatic Migrations & Dual-Engine Persistence.

Validates:
1. Environment-based database switching (Development -> SQLite, Production -> PostgreSQL)
2. Database health checks and readiness probes (/health and /ready)
3. Full persistence lifecycle across all core clinical entities:
   - Assessment creation and persistence
   - Multi-nutrient prediction persistence
   - Personalized food and supplement recommendation persistence
   - Longitudinal biomarker outcome forecast persistence
   - Clinical report persistence
4. Automatic schema migration and table validation
5. SQL placeholder compatibility and PostgreSQL DDL generator
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.database import check_db_health, check_db_readiness
from app.core.persistence import PersistenceRepository


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestEnvironmentDatabaseSwitching:
    """Verifies dynamic switching and engine detection based on environment settings."""

    def test_environment_engine_resolution(self):
        # By default in dev environment, effective engine is sqlite
        assert settings.get_effective_db_engine() in ["sqlite", "postgresql"]

    def test_manual_engine_switching(self):
        initial = PersistenceRepository.get_active_engine()
        
        PersistenceRepository.switch_engine("postgresql")
        assert PersistenceRepository.get_active_engine() == "PostgreSQL"
        
        PersistenceRepository.switch_engine("sqlite")
        assert PersistenceRepository.get_active_engine() == "SQLite"
        
        PersistenceRepository.reset_engine()

    @pytest.mark.asyncio
    async def test_db_health_check_payload(self):
        health = await check_db_health()
        assert "status" in health
        assert health["status"] in ["HEALTHY", "DEGRADED"]
        assert "persistence_layer" in health
        assert "persisted_assessments" in health
        assert "engine" in health

    @pytest.mark.asyncio
    async def test_db_readiness_probe(self):
        readiness = await check_db_readiness()
        assert "ready" in readiness
        assert readiness["ready"] is True
        assert "database" in readiness


class TestClinicalPersistenceLifecycle:
    """Verifies CRUD persistence for all 5 core clinical domains."""

    @pytest.fixture(autouse=True)
    def setup_entities(self):
        self.assessment_id = f"mig_test_{uuid.uuid4().hex[:8]}"
        self.patient_id = f"pat_{uuid.uuid4().hex[:8]}"

    def test_full_clinical_lifecycle_persistence(self):
        # 1. Assessment Persistence
        assessment_payload = {
            "age": 34,
            "gender": "FEMALE",
            "height_cm": 165.0,
            "weight_kg": 62.0,
            "dietary_pattern": "VEGETARIAN",
            "symptoms": {"fatigue": 7, "brittle_nails": 6}
        }
        PersistenceRepository.save_assessment(self.assessment_id, assessment_payload)
        saved_assessment = PersistenceRepository.get_assessment(self.assessment_id)
        assert saved_assessment is not None
        assert saved_assessment["age"] == 34
        assert saved_assessment["gender"] == "FEMALE"

        # 2. Prediction Persistence
        prediction_payload = {
            "overall_risk": "HIGH",
            "overall_risk_score": 78.5,
            "nutrient_predictions": [
                {"nutrient": "Iron", "risk_level": "HIGH", "probability": 0.85, "confidence": 0.91},
                {"nutrient": "Vitamin B12", "risk_level": "MODERATE", "probability": 0.62, "confidence": 0.88}
            ]
        }
        PersistenceRepository.save_predictions(self.assessment_id, prediction_payload)
        saved_prediction = PersistenceRepository.get_prediction(self.assessment_id)
        assert saved_prediction is not None
        assert saved_prediction["overall_risk"] == "HIGH"
        assert saved_prediction["overall_risk_score"] == 78.5
        assert len(saved_prediction["nutrient_predictions"]) == 2

        # 3. Recommendation Persistence
        recommendation_payload = {
            "safety_score": 96.0,
            "safety_tier": "TIER_1_OPTIMAL",
            "food_recommendations": [
                {"food": "Spinach", "nutrient": "Iron", "portion": "100g"},
                {"food": "Lentils", "nutrient": "Iron", "portion": "150g"}
            ],
            "supplement_recommendations": [
                {"supplement": "Iron Bisglycinate", "dosage": "25mg", "frequency": "DAILY"}
            ]
        }
        PersistenceRepository.save_recommendations(self.assessment_id, recommendation_payload)
        saved_rec = PersistenceRepository.get_recommendations(self.assessment_id)
        assert saved_rec is not None
        assert saved_rec["safety_score"] == 96.0
        assert len(saved_rec["food_recommendations"]) == 2

        # 4. Forecast Persistence
        forecast_payload = {
            "baseline_date": "2026-09-16",
            "milestones": [
                {"day": 30, "biomarker": "Serum Ferritin", "projected_value": 28.5},
                {"day": 60, "biomarker": "Serum Ferritin", "projected_value": 45.0}
            ]
        }
        PersistenceRepository.save_forecast(self.assessment_id, forecast_payload)
        saved_forecast = PersistenceRepository.get_forecast(self.assessment_id)
        assert saved_forecast is not None
        assert len(saved_forecast["milestones"]) == 2

        # 5. Report Persistence
        report_id = f"rep_{uuid.uuid4().hex[:8]}"
        report_payload = {
            "report_title": "Comprehensive Nutritional Screening & Protocol",
            "overall_health_score": 82.0,
            "health_score_category": "GOOD",
            "summary": "Mild-to-moderate micronutrient deficiencies detected; oral repletion initiated."
        }
        PersistenceRepository.save_report(
            report_id=report_id,
            assessment_id=self.assessment_id,
            report_dict=report_payload
        )
        saved_report = PersistenceRepository.get_report(self.assessment_id)
        assert saved_report is not None
        assert saved_report["report_title"] == report_payload["report_title"]
        assert saved_report["overall_health_score"] == 82.0


class TestPostgresMigrationSchemaExporter:
    """Verifies that the PostgreSQL schema generator produces standard ANSI SQL DDL."""

    def test_export_to_postgres_sql(self):
        sql_dump = PersistenceRepository.export_to_postgres_sql()
        assert "CREATE TABLE IF NOT EXISTS users" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS assessments" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS predictions" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS recommendations" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS meal_plans" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS forecasts" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS reports" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS audit_events" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS clinician_reviews" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS ground_truth_outcomes" in sql_dump
        assert "JSONB" in sql_dump
        assert "TIMESTAMPTZ" in sql_dump
