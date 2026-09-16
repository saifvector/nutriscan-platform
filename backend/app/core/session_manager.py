"""
NutriScan Session Security & Token Revocation Manager
Phase 1: JWT Revocation & Session Security

Provides:
- Redis-backed token denylist with automated thread-safe in-memory TTL fallback
- jti (JWT ID) revocation tracking with automatic expiration cleanup
- User-level session invalidation on password change, role modification, or forced logout
- Multi-session tracking and instant token revocation
"""

import time
import logging
import threading
from typing import Optional, Dict, Set
from datetime import datetime, timezone

logger = logging.getLogger("nutrient_platform.session_manager")


class SessionSecurityManager:
    """
    Manages token revocation lists and session validity across NutriScan.
    Supports Redis distributed denylist if configured; seamlessly falls back
    to a synchronized in-memory TTL denylist.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SessionSecurityManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, redis_url: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        from .redis_manager import redis_manager
        self._redis_mgr = redis_manager

    def revoke_token(self, jti: str, exp: float) -> None:
        """
        Revokes a specific JWT by its unique jti claim until its expiration time.
        """
        self._redis_mgr.revoke_jti(jti, exp)

    def is_token_revoked(self, jti: str, user_id: Optional[str] = None, iat: Optional[float] = None) -> bool:
        """
        Checks if a token's jti is revoked, or if all sessions for the user were invalidated
        after the token's issued-at (iat) timestamp.
        """
        # 1. Check if specific JTI is revoked
        if self._redis_mgr.is_jti_revoked(jti):
            return True

        # 2. Check if user's sessions have been invalidated globally
        if user_id and iat:
            if self._redis_mgr.is_user_session_revoked(str(user_id), float(iat)):
                return True

        return False

    def revoke_all_user_sessions(self, user_id: str) -> None:
        """
        Invalidates all currently active sessions for a specific user ID.
        Any token issued before current timestamp is rendered invalid.
        """
        self._redis_mgr.invalidate_user_sessions(str(user_id))

    def clear_all(self) -> None:
        """Testing utility to flush denylist state."""
        with self._redis_mgr._memory_lock:
            self._redis_mgr._memory_denylist.clear()
            self._redis_mgr._memory_user_revocations.clear()
        if self._redis_mgr._is_connected and self._redis_mgr._client:
            try:
                keys = self._redis_mgr._client.keys("revoked_jti:*") + self._redis_mgr._client.keys("user_revoked_at:*")
                if keys:
                    self._redis_mgr._client.delete(*keys)
            except Exception:
                pass


# Global session security manager
session_manager = SessionSecurityManager()
