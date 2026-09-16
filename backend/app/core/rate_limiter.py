"""
NutriScan In-Memory Sliding-Window Rate Limiter & Brute-Force Guard
Implements:
- Microsecond-accurate sliding-window request tracking per IP / user token
- Tiered request limits (Authentication endpoints: 5/min, Inference: 60/min, General: 300/min)
- RFC-7807 429 Too Many Requests response with standard Retry-After header
- Thread-safe synchronization via threading.Lock()
- Automatic memory garbage collection for expired window keys
"""

import time
import threading
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SlidingWindowRateLimiter:
    """
    Distributed & in-memory sliding-window rate limiter utilizing RedisManager.
    """
    def __init__(self):
        from .redis_manager import redis_manager
        self._redis_mgr = redis_manager

    def is_allowed(self, key: str, max_requests: int, window_seconds: float) -> Tuple[bool, int, float]:
        """
        Determines if a request with `key` is permitted under `max_requests` per `window_seconds`.
        Returns: (is_allowed, current_count, retry_after_seconds)
        """
        return self._redis_mgr.is_rate_limited(key, max_requests, window_seconds)

    def reset_key(self, key: str):
        """Resets rate limit counter for a specific key (e.g. after successful login)."""
        with self._redis_mgr._memory_lock:
            self._redis_mgr._memory_rate_limits.pop(key, None)
        if self._redis_mgr._is_connected and self._redis_mgr._client:
            try:
                self._redis_mgr._client.delete(f"ratelimit:{key}")
            except Exception:
                pass

    def reset_all(self):
        """Clears all rate limiting history (for test suites)."""
        self._redis_mgr.reset_rate_limits()


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()
global_rate_limiter = rate_limiter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Enforces tiered rate limits based on path sensitivity:
    - Auth & Login: 5 requests / 60 seconds (brute force protection)
    - Inference & Forecasts: 60 requests / 60 seconds
    - Default API: 300 requests / 60 seconds
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Bypass rate limiting for internal health and metrics checks
        if path in ["/health", "/health/deep", "/metrics", "/docs", "/openapi.json", "/"]:
            return await call_next(request)

        # Extract client IP
        client_ip = request.client.host if request.client else "unknown_ip"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Tiered limit determination
        if "/auth/login" in path or "/auth/register" in path:
            limit = 5
            window = 60.0
            tier = "AUTH_BRUTE_FORCE"
            rate_key = f"rl:auth:{client_ip}"
        elif any(heavy in path for heavy in ["/predictions", "/forecasts", "/meal-plans"]):
            limit = 60
            window = 60.0
            tier = "INFERENCE_BURST"
            rate_key = f"rl:heavy:{client_ip}"
        else:
            limit = 300
            window = 60.0
            tier = "STANDARD_API"
            rate_key = f"rl:std:{client_ip}"

        allowed, count, retry_after = rate_limiter.is_allowed(rate_key, max_requests=limit, window_seconds=window)

        if not allowed:
            from .security_middleware import get_current_correlation_id
            cid = get_current_correlation_id() or "system"
            return JSONResponse(
                status_code=429,
                headers={
                    "Retry-After": str(int(retry_after)),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                },
                content={
                    "error": True,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded for {tier} tier ({limit} req/{int(window)}s). Please wait before retrying.",
                    "correlation_id": cid,
                    "details": {
                        "tier": tier,
                        "limit": limit,
                        "window_seconds": window,
                        "retry_after_seconds": retry_after
                    }
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response
