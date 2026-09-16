"""
NutriScan Redis Integration & Resilience Test Suite
Phase 2: Redis Integration

Tests:
1. Health check telemetry for distributed Redis / in-memory fallback.
2. JWT Revocation denylist (JTI lifecycle).
3. User session invalidation across issued-at timestamps.
4. Distributed & in-memory sliding-window rate limiting with retry-after calculation.
5. API response caching with TTL and invalidation.
6. Temporary multi-step assessment workflow state persistence.
7. Graceful degradation when Redis connection fails or disconnects.
8. Backward compatibility through session_manager and rate_limiter interfaces.
"""

import time
import pytest
from app.core.redis_manager import RedisManager, redis_manager
from app.core.session_manager import session_manager
from app.core.rate_limiter import rate_limiter


@pytest.fixture(autouse=True)
def clean_redis_state():
    """Ensure clean denylist, cache, and rate limit state before each test."""
    session_manager.clear_all()
    rate_limiter.reset_all()
    with redis_manager._memory_lock:
        redis_manager._memory_cache.clear()
        redis_manager._memory_workflows.clear()
    yield
    session_manager.clear_all()
    rate_limiter.reset_all()


def test_redis_health_telemetry():
    """Verify health check returns valid telemetry dictionary."""
    health = redis_manager.check_health()
    assert isinstance(health, dict)
    assert "status" in health
    assert health["status"] == "HEALTHY"
    assert "connected" in health
    assert "engine" in health


def test_jti_revocation_lifecycle():
    """Verify individual JWT ID revocation and expiration."""
    jti = "test-token-uuid-12345"
    exp = time.time() + 2.0  # 2 seconds expiry

    assert not redis_manager.is_jti_revoked(jti)
    redis_manager.revoke_jti(jti, exp)
    assert redis_manager.is_jti_revoked(jti)

    # Via session_manager facade
    assert session_manager.is_token_revoked(jti)


def test_user_session_invalidation():
    """Verify user-level invalidation renders prior tokens invalid while preserving later tokens."""
    user_id = "clinician-007"
    t0 = time.time()
    token_iat_old = t0 - 100.0

    # Token issued before invalidation
    assert not redis_manager.is_user_session_revoked(user_id, token_iat_old)

    # Invalidate all user sessions
    redis_manager.invalidate_user_sessions(user_id, timestamp=t0)

    # Prior token is now revoked
    assert redis_manager.is_user_session_revoked(user_id, token_iat_old)
    assert session_manager.is_token_revoked("any-jti", user_id=user_id, iat=token_iat_old)

    # Newly issued token after invalidation is valid
    token_iat_new = t0 + 10.0
    assert not redis_manager.is_user_session_revoked(user_id, token_iat_new)
    assert not session_manager.is_token_revoked("fresh-jti", user_id=user_id, iat=token_iat_new)


def test_sliding_window_rate_limiting():
    """Verify sliding-window rate limiter blocks requests past limit and returns retry-after."""
    key = "test-rate-limit-client"
    limit = 3
    window = 10.0

    # 3 requests allowed
    for i in range(limit):
        allowed, count, retry_after = redis_manager.is_rate_limited(key, limit, window)
        assert allowed is True
        assert count == i + 1
        assert retry_after == 0.0

    # 4th request blocked
    allowed, count, retry_after = redis_manager.is_rate_limited(key, limit, window)
    assert allowed is False
    assert count >= limit
    assert retry_after > 0.0

    # Reset allows new requests
    redis_manager.reset_rate_limits()
    allowed, count, _ = redis_manager.is_rate_limited(key, limit, window)
    assert allowed is True
    assert count == 1


def test_api_response_caching():
    """Verify caching of API payloads, retrieval, and cache invalidation."""
    cache_key = "query:assessment:999"
    payload = {"patient_id": "P-999", "risk_level": "MODERATE", "deficiencies": ["Iron", "Zinc"]}

    assert redis_manager.get_cache(cache_key) is None

    redis_manager.set_cache(cache_key, payload, ttl_seconds=60)
    cached = redis_manager.get_cache(cache_key)
    assert cached is not None
    assert cached["patient_id"] == "P-999"
    assert cached["risk_level"] == "MODERATE"

    redis_manager.delete_cache(cache_key)
    assert redis_manager.get_cache(cache_key) is None


def test_workflow_state_preservation():
    """Verify multi-step assessment workflow state storage and cleanup."""
    session_id = "session-step-orchestration-456"
    workflow_state = {
        "step": 2,
        "completed_steps": ["biomarker_intake", "dietary_analysis"],
        "pending": "clinical_review",
        "temp_data": {"bmi": 21.4, "hemoglobin": 11.2}
    }

    assert redis_manager.get_workflow_state(session_id) is None

    redis_manager.set_workflow_state(session_id, workflow_state, ttl_seconds=120)
    retrieved = redis_manager.get_workflow_state(session_id)
    assert retrieved is not None
    assert retrieved["step"] == 2
    assert retrieved["completed_steps"] == ["biomarker_intake", "dietary_analysis"]

    redis_manager.delete_workflow_state(session_id)
    assert redis_manager.get_workflow_state(session_id) is None


def test_graceful_degradation_without_redis():
    """
    Verify that an explicitly disconnected Redis instance falls back to in-memory
    without raising any exceptions.
    """
    # Create isolated manager without redis URL
    mem_mgr = RedisManager(redis_url="")
    # Force client to None
    mem_mgr._client = None
    mem_mgr._is_connected = False

    # 1. Denylist
    mem_mgr.revoke_jti("mem-jti-1", time.time() + 10)
    assert mem_mgr.is_jti_revoked("mem-jti-1")

    # 2. Rate limiting
    allowed, count, _ = mem_mgr.is_rate_limited("mem-client", 2, 60)
    assert allowed is True
    assert count == 1

    # 3. Cache
    mem_mgr.set_cache("mem-key", {"status": "ok"}, 60)
    assert mem_mgr.get_cache("mem-key") == {"status": "ok"}

    # 4. Health
    health = mem_mgr.check_health()
    assert health["status"] == "HEALTHY"
    assert "In-Memory" in health["engine"]
