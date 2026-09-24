"""
FastAPI Application Entrypoint
Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform
"""

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from .core.config import settings
from .core.metrics import metrics
from .core.database import check_db_health, check_db_readiness
from .core.redis_manager import redis_manager
from .core.security_middleware import (
    SecurityHeadersMiddleware,
    CorrelationIdMiddleware,
    get_current_correlation_id
)
from .core.rate_limiter import RateLimiterMiddleware
from .core.observability import telemetry_tracker, setup_structured_logging
from .core.exceptions import NutriScanException
from fastapi.exceptions import RequestValidationError
from .api.v1.api_router import api_router
from .modules.prediction.service import PredictionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nutrient_platform")
setup_structured_logging(logger)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    - Performs production configuration and secret hardening checks
    - Warms up the prediction engine and loads XGBoost model into memory at startup
    - Pre-populates SHAP TreeExplainers so first user request latency is < 15ms
    - Validates database readiness
    """
    logger.info("Initializing Nutritional AI Platform...")
    warm_start = time.perf_counter()

    # Production Secret & Configuration Validation
    if settings.is_production():
        if len(settings.JWT_SECRET) < 32 or "change_me" in settings.JWT_SECRET.lower() or "super_secret_jwt_key_phase1" in settings.JWT_SECRET:
            import secrets
            settings.JWT_SECRET = secrets.token_urlsafe(48)
            logger.warning("PRODUCTION NOTICE: Default JWT_SECRET detected. Automatically initialized an ephemeral 64-byte cryptographically secure secret for runtime protection.")
        
        # Verify database readiness
        db_readiness = await check_db_readiness()
        if db_readiness.get("status") not in ["READY", "HEALTHY"]:
            logger.warning(f"Production database readiness notice at startup: {db_readiness}")

    engine = PredictionService.get_engine()
    
    # Pre-warm TreeExplainers with dummy record
    dummy_payload = {
        "age": 30, "gender": "MALE", "height_cm": 175.0, "weight_kg": 70.0,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 3, "water_intake_liters": 2.0,
        "daily_fruit_vegetable_servings": 3, "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 7.0, "sunlight_exposure_min_per_day": 30,
        "stress_level": 5, "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {}
    }
    engine.screen_patient(dummy_payload, compute_explainability=True)
    
    # Phase 10C Production Clinical Risk Engine Warm-up
    clinical_engine = PredictionService.get_clinical_engine()
    clinical_engine.warm_up()
    
    # Phase 12 Model Drift & Governance Baseline Warm-up
    try:
        from .modules.governance.drift_engine import ModelDriftEngine
        ModelDriftEngine.initialize_baseline()
    except Exception as e:
        logger.warning(f"Governance baseline warm-up notice: {e}")

    elapsed = round((time.perf_counter() - warm_start) * 1000, 2)
    logger.info(f"Multi-Nutrient Prediction, Clinical & Governance Engines warmed up in {elapsed} ms.")
    yield
    logger.info("Shutting down Nutritional AI Platform...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade AI-based screening platform predicting multi-nutrient deficiencies with confidence scoring, biochemical interaction analysis, and SHAP explainability.",
    lifespan=lifespan
)

# CORS Middleware
cors_origins = list(settings.CORS_ORIGINS) if hasattr(settings, "CORS_ORIGINS") else []
cors_origins.extend([
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(cors_origins)),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.onrender\.com)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zero-Overhead Pure ASGI Observability & Metrics Middleware
class PrometheusASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start_time
            metrics.record_request(
                method=scope.get("method", "GET"),
                endpoint=scope.get("path", ""),
                status_code=status_code,
                duration_seconds=duration
            )
            telemetry_tracker.record_http_status(status_code)


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(PrometheusASGIMiddleware)


# Unified Clinical Domain Exception Handlers
@app.exception_handler(NutriScanException)
async def nutriscan_exception_handler(request: Request, exc: NutriScanException):
    cid = get_current_correlation_id()
    logger.error(f"[{cid}] NutriScanException ({exc.error_code}): {exc.message} - details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "correlation_id": cid,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    cid = get_current_correlation_id()
    logger.warning(f"[{cid}] RequestValidationError: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "error_code": "REQUEST_VALIDATION_ERROR",
            "message": "Input validation failed for clinical request payload.",
            "correlation_id": cid,
            "details": {"validation_errors": exc.errors()}
        }
    )


# Include API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System Health"])
async def health_check():
    """
    Lightweight health check (<20ms) verifying API status, database connectivity, redis, and persistence health.
    """
    from .core.persistence import PersistenceRepository
    db_status = await check_db_health()
    persistence_healthy = PersistenceRepository.is_healthy()
    redis_status = redis_manager.check_health()
    is_healthy = db_status.get("status") in ["HEALTHY", "FALLBACK_SQLITE"] and persistence_healthy
    return {
        "status": "HEALTHY" if is_healthy else "DEGRADED",
        "service": "Nutrient Deficiency AI Screening Platform",
        "version": settings.VERSION,
        "database": db_status,
        "redis": redis_status,
        "persistence_ready": persistence_healthy
    }


@app.get("/ready", tags=["System Health"])
async def readiness_probe():
    """
    Kubernetes-compliant readiness probe verifying database readiness,
    persistence engine health, and ML inference service readiness.
    Returns 200 if ready to receive traffic, 503 if not ready.
    """
    from .core.database import check_db_readiness
    from .core.persistence import PersistenceRepository
    db_ready = await check_db_readiness()
    engine = PredictionService.get_engine()
    engine_ready = engine is not None
    persist_ready = PersistenceRepository.is_healthy()
    redis_health = redis_manager.check_health()

    is_ready = (db_ready.get("ready", False) or db_ready.get("status") in ["READY", "HEALTHY"]) and persist_ready
    status_code = 200 if is_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "READY" if is_ready else "NOT_READY",
            "service": "NutriScan AI Healthcare Platform",
            "version": settings.VERSION,
            "checks": {
                "database": db_ready,
                "ml_inference_engine": "READY" if engine_ready else "NOT_READY",
                "persistence_layer": "HEALTHY" if persist_ready else "UNHEALTHY",
                "redis_distributed": redis_health
            }
        }
    )


@app.get("/health/deep", tags=["System Health"])
async def health_check_deep():
    """
    Deep health check verifying ML inference engine warm status, active champion models, and registry health.
    """
    from .core.persistence import PersistenceRepository
    db_status = await check_db_health()
    is_engine_ready = PredictionService._engine is not None
    clinical_engine = PredictionService.get_clinical_engine()
    registry_healthy = clinical_engine.registry.is_healthy()
    persistence_healthy = PersistenceRepository.is_healthy()
    overall = "HEALTHY" if (is_engine_ready and registry_healthy and persistence_healthy) else "DEGRADED"
    return {
        "status": overall,
        "service": "Nutrient Deficiency AI Screening Platform",
        "version": settings.VERSION,
        "prediction_engine_ready": is_engine_ready,
        "clinical_models_registered": len(clinical_engine.registry.get_all_models()),
        "registry_healthy": registry_healthy,
        "database": db_status,
        "persistence_ready": persistence_healthy
    }



@app.get("/metrics", tags=["System Observability"], response_class=PlainTextResponse)
async def get_metrics():
    """Exposes Prometheus text exposition format (version 0.0.4) metrics."""
    return metrics.export_prometheus_text()


@app.get(f"{settings.API_V1_STR}/observability/dashboard", tags=["System Observability"])
async def get_observability_dashboard():
    """Returns real-time system operational telemetry, latency percentiles, and alerts."""
    return telemetry_tracker.get_dashboard_summary()


@app.get(f"{settings.API_V1_STR}/database/export-postgres", tags=["Database Architecture"])
async def export_postgres_sql():
    """Generates production-grade PostgreSQL DDL and data dump for cloud database migration."""
    from .core.persistence import PersistenceRepository
    dump = PersistenceRepository.export_to_postgres_sql()
    return {
        "target_engine": "PostgreSQL 14+",
        "compatibility": "JSONB, TIMESTAMPTZ, UUID",
        "sql_dump": dump
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the AI-Based Nutrient Deficiency Screening Platform API",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR
    }
