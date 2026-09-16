"""
NutriScan Centralized Redis & In-Memory Fallback Engine.
Phase 2: Redis Integration for Distributed Token Denylisting, Rate Limiting,
API Response Caching, and Temporary Workflow State.

Features:
- Thread-safe Redis connection pooling with automatic reconnection
- Graceful degradation to synchronized in-memory TTL maps when Redis is unavailable
- Real-time health checking and latency tracking
- Distributed sliding-window rate limiting
- API query/inference result caching with TTL
- Workflow orchestrator interim state preservation
"""

import time
import json
import logging
import threading
from typing import Optional, Dict, Any, Tuple, List

from .config import settings

logger = logging.getLogger("nutrient_platform.redis")


class RedisManager:
    """
    Singleton manager for Redis distributed operations with robust in-memory fallback.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RedisManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, redis_url: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._memory_lock = threading.RLock()
        self._redis_url = redis_url or settings.REDIS_URL
        self._client = None
        self._is_connected = False
        self._last_connect_attempt = 0.0
        self._reconnect_backoff_sec = 5.0

        # In-memory fallbacks (key -> (value, expiry_timestamp))
        self._memory_cache: Dict[str, Tuple[Any, float]] = {}
        self._memory_denylist: Dict[str, float] = {}  # jti -> exp_timestamp
        self._memory_user_revocations: Dict[str, float] = {}  # user_id -> valid_after
        self._memory_rate_limits: Dict[str, List[float]] = {}  # key -> list of float timestamps
        self._memory_workflows: Dict[str, Tuple[Dict[str, Any], float]] = {}

        self._connect()

    def _connect(self) -> bool:
        """Attempts connection to Redis with pool."""
        self._last_connect_attempt = time.time()
        if not self._redis_url:
            logger.info("No REDIS_URL configured; running in synchronized in-memory mode.")
            self._is_connected = False
            return False

        try:
            import redis
            pool = redis.ConnectionPool.from_url(
                self._redis_url,
                max_connections=20,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0
            )
            client = redis.Redis(connection_pool=pool)
            client.ping()
            self._client = client
            self._is_connected = True
            logger.info(f"Connected to Redis at {self._redis_url} successfully.")
            return True
        except Exception as e:
            logger.warning(f"Redis connection notice ({e}); utilizing thread-safe in-memory fallback.")
            self._client = None
            self._is_connected = False
            return False

    def check_health(self) -> Dict[str, Any]:
        """Returns health telemetry for Redis and in-memory fallback stores."""
        if not self._is_connected:
            # Check if backoff window has elapsed to attempt reconnect
            if time.time() - self._last_connect_attempt > self._reconnect_backoff_sec:
                self._connect()

        if self._is_connected and self._client:
            try:
                t0 = time.perf_counter()
                self._client.ping()
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                return {
                    "status": "HEALTHY",
                    "connected": True,
                    "engine": "Redis Distributed",
                    "latency_ms": latency_ms,
                    "active_keys_cached": len(self._memory_cache)
                }
            except Exception as e:
                self._is_connected = False
                logger.warning(f"Redis health probe failed: {e}; falling back to memory.")

        return {
            "status": "HEALTHY",
            "connected": False,
            "engine": "In-Memory Synchronized Fallback",
            "active_cache_keys": len(self._memory_cache),
            "revoked_tokens_in_memory": len(self._memory_denylist)
        }

    # --------------------------------------------------------------------------
    # 1. Token Denylisting & JWT Revocation
    # --------------------------------------------------------------------------
    def revoke_jti(self, jti: str, exp_timestamp: float) -> None:
        """Adds a JWT ID (jti) to the revocation denylist until its expiration."""
        now = time.time()
        ttl = max(1, int(exp_timestamp - now)) if exp_timestamp else 86400

        if self._is_connected and self._client:
            try:
                self._client.setex(f"revoked_jti:{jti}", ttl, "1")
                return
            except Exception as e:
                logger.error(f"Redis error revoking jti {jti}: {e}; using memory.")

        with self._memory_lock:
            self._memory_denylist[jti] = float(exp_timestamp)
            self._cleanup_denylist()

    def is_jti_revoked(self, jti: str) -> bool:
        """Checks if a jti has been explicitly revoked."""
        if self._is_connected and self._client:
            try:
                return bool(self._client.exists(f"revoked_jti:{jti}"))
            except Exception as e:
                logger.error(f"Redis error checking jti {jti}: {e}; checking memory.")

        with self._memory_lock:
            if jti in self._memory_denylist:
                if self._memory_denylist[jti] > time.time():
                    return True
                else:
                    del self._memory_denylist[jti]
            return False

    def invalidate_user_sessions(self, user_id: str, timestamp: Optional[float] = None) -> None:
        """Invalidates all sessions for a user issued before the specified timestamp."""
        ts = timestamp or time.time()
        ttl = 86400 * 7  # 7 days

        if self._is_connected and self._client:
            try:
                self._client.setex(f"user_revoked_at:{user_id}", ttl, str(ts))
                return
            except Exception as e:
                logger.error(f"Redis error invalidating user {user_id}: {e}; using memory.")

        with self._memory_lock:
            self._memory_user_revocations[user_id] = float(ts)

    def is_user_session_revoked(self, user_id: str, iat: float) -> bool:
        """Checks if a user session token was issued prior to user-level invalidation."""
        if self._is_connected and self._client:
            try:
                val = self._client.get(f"user_revoked_at:{user_id}")
                if val and iat < float(val):
                    return True
            except Exception as e:
                logger.error(f"Redis error checking user invalidation {user_id}: {e}; checking memory.")

        with self._memory_lock:
            min_valid = self._memory_user_revocations.get(user_id)
            if min_valid and iat < min_valid:
                return True
        return False

    def _cleanup_denylist(self):
        now = time.time()
        expired = [k for k, exp in self._memory_denylist.items() if exp <= now]
        for k in expired:
            del self._memory_denylist[k]

    # --------------------------------------------------------------------------
    # 2. Sliding-Window Rate Limiter
    # --------------------------------------------------------------------------
    def is_rate_limited(self, key: str, max_requests: int, window_seconds: float) -> Tuple[bool, int, float]:
        """
        Sliding-window log rate limiter.
        Returns: (is_allowed, current_count, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds

        if self._is_connected and self._client:
            try:
                redis_key = f"ratelimit:{key}"
                pipe = self._client.pipeline()
                pipe.zremrangebyscore(redis_key, "-inf", window_start)
                pipe.zcard(redis_key)
                pipe.zadd(redis_key, {str(now): now})
                pipe.expire(redis_key, int(window_seconds) + 5)
                results = pipe.execute()

                current_count = results[1]
                if current_count >= max_requests:
                    # Fetch earliest timestamp to compute retry_after
                    earliest = self._client.zrange(redis_key, 0, 0, withscores=True)
                    earliest_ts = earliest[0][1] if earliest else window_start
                    retry_after = max(1.0, round(window_seconds - (now - earliest_ts), 1))
                    return False, current_count, retry_after
                return True, current_count + 1, 0.0
            except Exception as e:
                logger.error(f"Redis error during rate limiting for {key}: {e}; using memory.")

        # In-memory sliding window
        with self._memory_lock:
            timestamps = self._memory_rate_limits.get(key, [])
            valid_ts = [t for t in timestamps if t > window_start]
            if len(valid_ts) >= max_requests:
                earliest = valid_ts[0]
                retry_after = max(1.0, round(window_seconds - (now - earliest), 1))
                self._memory_rate_limits[key] = valid_ts
                return False, len(valid_ts), retry_after

            valid_ts.append(now)
            self._memory_rate_limits[key] = valid_ts
            return True, len(valid_ts), 0.0

    def reset_rate_limits(self):
        """Clears rate limits for test suites."""
        with self._memory_lock:
            self._memory_rate_limits.clear()
        if self._is_connected and self._client:
            try:
                keys = self._client.keys("ratelimit:*")
                if keys:
                    self._client.delete(*keys)
            except Exception:
                pass

    # --------------------------------------------------------------------------
    # 3. API Response Caching
    # --------------------------------------------------------------------------
    def get_cache(self, key: str) -> Optional[Any]:
        """Retrieves cached JSON payload by key."""
        if self._is_connected and self._client:
            try:
                data = self._client.get(f"cache:{key}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis cache get error for {key}: {e}")

        with self._memory_lock:
            item = self._memory_cache.get(key)
            if item:
                val, exp = item
                if exp > time.time():
                    return val
                else:
                    del self._memory_cache[key]
        return None

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Caches JSON-serializable value with TTL (default 5 minutes)."""
        now = time.time()
        exp = now + ttl_seconds

        if self._is_connected and self._client:
            try:
                payload = json.dumps(value, default=str)
                self._client.setex(f"cache:{key}", ttl_seconds, payload)
                return
            except Exception as e:
                logger.error(f"Redis cache set error for {key}: {e}")

        with self._memory_lock:
            self._memory_cache[key] = (value, exp)

    def delete_cache(self, key: str) -> None:
        """Invalidates a cache entry."""
        if self._is_connected and self._client:
            try:
                self._client.delete(f"cache:{key}")
            except Exception:
                pass
        with self._memory_lock:
            self._memory_cache.pop(key, None)

    # --------------------------------------------------------------------------
    # 4. Temporary Workflow State
    # --------------------------------------------------------------------------
    def set_workflow_state(self, session_id: str, state_dict: Dict[str, Any], ttl_seconds: int = 1800) -> None:
        """Saves interim multi-step assessment workflow state (default 30 mins)."""
        exp = time.time() + ttl_seconds
        if self._is_connected and self._client:
            try:
                self._client.setex(f"workflow:{session_id}", ttl_seconds, json.dumps(state_dict, default=str))
                return
            except Exception as e:
                logger.error(f"Redis workflow state set error: {e}")

        with self._memory_lock:
            self._memory_workflows[session_id] = (state_dict, exp)

    def get_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves interim workflow state."""
        if self._is_connected and self._client:
            try:
                data = self._client.get(f"workflow:{session_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis workflow state get error: {e}")

        with self._memory_lock:
            item = self._memory_workflows.get(session_id)
            if item:
                val, exp = item
                if exp > time.time():
                    return val
                else:
                    del self._memory_workflows[session_id]
        return None

    def delete_workflow_state(self, session_id: str) -> None:
        if self._is_connected and self._client:
            try:
                self._client.delete(f"workflow:{session_id}")
            except Exception:
                pass
        with self._memory_lock:
            self._memory_workflows.pop(session_id, None)


# Global singleton manager
redis_manager = RedisManager()
