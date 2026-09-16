"""
API Contract & Schema Regression Test Suite for NutriScan Platform.
Phase 6: OpenAPI 3.1 Validation, Consumer Contracts, and Backward Compatibility.

Validates:
1. OpenAPI specification schema completeness & path validation
2. Schema regression testing for core Pydantic request/response models
3. Consumer-driven contract (CDC) verification across:
   - Authentication contracts (TokenResponse, UserRegisterRequest)
   - Clinical Prediction contracts (HealthAssessmentCreate, MultiNutrientPredictionResponse)
   - Observability and Health contracts
4. Backward compatibility & schema evolutionary stability
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.schemas import TokenResponse, UserRegisterRequest, UserLoginRequest
from app.schemas.assessment import (
    HealthAssessmentCreate,
    GenderEnum,
    DietPatternEnum,
    DietaryHabits,
    LifestyleFactors,
    ActivityLevelEnum
)
from app.schemas.prediction import (
    MultiNutrientPredictionResponse,
    NutrientPredictionItem,
    OverallDeficiencySummary
)


from app.core.rate_limiter import rate_limiter


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_rate_limits():
    rate_limiter.reset_all()


@pytest.fixture(scope="module")
def openapi_schema():
    """Fetches the generated OpenAPI schema specification from the FastAPI application."""
    return app.openapi()


class TestOpenAPISchemaContract:
    """Validates structure, metadata, and specification compliance of the OpenAPI schema."""

    def test_openapi_version_and_metadata(self, openapi_schema):
        assert "openapi" in openapi_schema
        assert openapi_schema["openapi"].startswith("3.")
        info = openapi_schema.get("info", {})
        assert "title" in info
        assert "version" in info
        assert "Nutrient" in info["title"] or "NutriScan" in info["title"]

    def test_all_core_clinical_endpoints_registered_in_schema(self, openapi_schema):
        paths = openapi_schema.get("paths", {})
        expected_endpoints = [
            "/health",
            "/metrics",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/me",
            "/api/v1/predict",
            "/api/v1/recommendations",
            "/api/v1/reports"
        ]
        for ep in expected_endpoints:
            matching = [p for p in paths.keys() if p.startswith(ep)]
            assert len(matching) > 0, f"Expected endpoint route '{ep}' not registered in OpenAPI schema"

    def test_endpoints_declare_explicit_responses(self, openapi_schema):
        paths = openapi_schema.get("paths", {})
        for path, operations in paths.items():
            for method, op_data in operations.items():
                if method.lower() in ["get", "post", "put", "delete"]:
                    assert "responses" in op_data, f"Operation {method.upper()} {path} missing 'responses' declaration"
                    status_codes = list(op_data["responses"].keys())
                    has_success = any(sc.startswith("2") or sc == "default" for sc in status_codes)
                    assert has_success, f"Operation {method.upper()} {path} must document a success or default response"


class TestSchemaRegressionAndModelContracts:
    """Validates structural contracts of Pydantic models to guarantee zero breaking schema regressions."""

    def test_token_response_contract_fields(self):
        fields = TokenResponse.model_fields
        required_fields = ["access_token", "token_type", "user_id", "email", "role"]
        for rf in required_fields:
            assert rf in fields, f"TokenResponse contract broken: missing field '{rf}'"

    def test_user_register_request_contract_fields(self):
        fields = UserRegisterRequest.model_fields
        required_fields = ["email", "password", "role"]
        for rf in required_fields:
            assert rf in fields, f"UserRegisterRequest contract broken: missing field '{rf}'"

    def test_health_assessment_create_contract_fields(self):
        fields = HealthAssessmentCreate.model_fields
        required_fields = ["age", "gender", "height_cm", "weight_kg", "dietary_habits", "lifestyle_factors", "symptoms"]
        for rf in required_fields:
            assert rf in fields, f"HealthAssessmentCreate contract broken: missing field '{rf}'"

    def test_screening_response_contract_fields(self):
        fields = MultiNutrientPredictionResponse.model_fields
        required_fields = ["assessment_id", "overall_risk", "overall_risk_score", "nutrient_predictions", "priority_ranking"]
        for rf in required_fields:
            assert rf in fields, f"MultiNutrientPredictionResponse contract broken: missing field '{rf}'"

    def test_nutrient_prediction_item_contract_fields(self):
        fields = NutrientPredictionItem.model_fields
        required_fields = ["nutrient", "nutrient_code", "risk_level", "probability", "confidence"]
        for rf in required_fields:
            assert rf in fields, f"NutrientPredictionItem contract broken: missing field '{rf}'"


class TestConsumerDrivenContractVerification:
    """Simulates consumer requests and validates responses match consumer expectations."""

    def test_auth_login_consumer_contract(self, client):
        # Register a unique test user
        email = f"cdc_consumer_{uuid.uuid4().hex[:8]}@nutriscan.test"
        pwd = "CdcPassword123!"
        reg_res = client.post("/api/v1/auth/register", json={
            "email": email,
            "password": pwd,
            "first_name": "Consumer",
            "last_name": "Tester",
            "role": "PATIENT"
        })
        assert reg_res.status_code == 201

        # Login and verify contract
        login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200
        data = login_res.json()

        # Contract assertions
        assert isinstance(data["access_token"], str) and len(data["access_token"]) > 20
        assert data["token_type"] == "bearer"
        assert data["email"] == email
        assert data["role"] == "PATIENT"
        assert isinstance(data["expires_in"], int) and data["expires_in"] > 0

    def test_health_check_consumer_contract(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert data["status"] in ["HEALTHY", "DEGRADED"]
        assert "version" in data
        assert "database" in data
        assert "persistence_ready" in data

    def test_observability_dashboard_consumer_contract(self, client):
        res = client.get("/api/v1/observability/dashboard")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "http_traffic" in data
        assert "latency_telemetry" in data
        assert "alerts" in data
        assert "persistence" in data


class TestBackwardCompatibilityAndExtensibility:
    """Verifies that future schema additions will not break existing consumers."""

    def test_prediction_request_supports_extra_symptoms(self):
        """Validates that HealthAssessmentCreate accepts additional symptoms without schema breakdown."""
        payload = {
            "age": 45,
            "gender": GenderEnum.MALE,
            "height_cm": 178.0,
            "weight_kg": 80.0,
            "dietary_habits": DietaryHabits(
                dietary_pattern=DietPatternEnum.OMNIVORE,
                meals_per_day=3,
                water_intake_liters=2.5,
                daily_fruit_vegetable_servings=3
            ),
            "lifestyle_factors": LifestyleFactors(
                activity_level=ActivityLevelEnum.MODERATELY_ACTIVE,
                sleep_hours_per_night=7.5,
                smoking_status="NEVER",
                alcohol_consumption="NONE",
                sunlight_exposure_min_per_day=30,
                stress_level=4
            ),
            "symptoms": {
                "fatigue": 2,
                "muscle_weakness": 1,
                "future_experimental_symptom": 3  # Forward-compatible flexible mapping
            }
        }
        model = HealthAssessmentCreate(**payload)
        assert model.age == 45
        assert model.gender.value == "MALE"
        assert "future_experimental_symptom" in model.symptoms
        assert model.symptoms["future_experimental_symptom"] == 3
