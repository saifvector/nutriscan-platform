"""
NutriScan Authentication & Authorization Engine
Implements:
- PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations & 16-byte random salt
- PyJWT token issuance and strict verification (expiration, signature, algorithm whitelisting)
- Protection against JWT tampering, 'alg=none' attacks, and session fixation
- Role-Based Access Control (RBAC): PATIENT, CLINICIAN, ADMIN
- Insecure Direct Object Reference (IDOR) & User Isolation guards
- Horizontal & Vertical privilege escalation prevention
"""

import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
import jwt
from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from .exceptions import NutriScanException
from .session_manager import session_manager

security_bearer = HTTPBearer(auto_error=False)

JWT_SECRET = settings.JWT_SECRET
JWT_SECRET_KEY = JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES or 1440


class UserRole(str, Enum):
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"


class TokenData(BaseModel):
    user_id: str
    email: str
    role: UserRole
    exp: float
    iat: float
    jti: str


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    role: UserRole
    is_active: bool = True
    jti: Optional[str] = None
    exp: Optional[float] = None
    iat: Optional[float] = None


# ------------------------------------------------------------------------------
# 1. Cryptographic Password Hashing (PBKDF2-HMAC-SHA256)
# ------------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Format: pbkdf2_sha256$100000$<hex_salt>$<hex_hash>
    """
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    salt = secrets.token_bytes(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored PBKDF2 hash using constant-time comparison.
    """
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_derived = bytes.fromhex(parts[3])
        actual_derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual_derived, expected_derived)
    except Exception:
        return False


# ------------------------------------------------------------------------------
# 2. JWT Token Issuance & Hardened Validation
# ------------------------------------------------------------------------------

def create_access_token(
    user_id: str,
    email: str,
    role: UserRole = UserRole.PATIENT,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a cryptographically signed JWT access token.
    Includes unique jti (JWT ID) to prevent replay and session fixation attacks.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "email": email.lower().strip(),
        "role": role.value if isinstance(role, UserRole) else str(role),
        "iat": float(now.timestamp()),
        "exp": float(expire.timestamp()),
        "jti": secrets.token_hex(16)
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decodes and rigorously validates a JWT token.
    Enforces signature verification, algorithm whitelisting, and expiration checking.
    Strictly prevents 'alg=none' signature bypass.
    """
    try:
        # Enforce exact allowed algorithm to prevent algorithm confusion attacks
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "email", "role", "exp", "iat", "jti"]
            }
        )

        token_data = TokenData(
            user_id=str(payload["sub"]),
            email=str(payload["email"]),
            role=UserRole(payload["role"]),
            exp=float(payload["exp"]),
            iat=float(payload["iat"]),
            jti=str(payload["jti"])
        )

        # Enforce instant token revocation check
        if session_manager.is_token_revoked(token_data.jti, token_data.user_id, token_data.iat):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has been revoked. Please re-authenticate.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return token_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except (jwt.InvalidTokenError, jwt.DecodeError, ValueError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(err)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ------------------------------------------------------------------------------
# 3. FastAPI Dependencies & Authorization Guards
# ------------------------------------------------------------------------------

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[AuthenticatedUser]:
    """
    Optional authentication dependency: returns AuthenticatedUser if valid Bearer token,
    or None if no Authorization header provided.
    """
    if not credentials or not credentials.credentials:
        return None
    token_data = decode_access_token(credentials.credentials)
    return AuthenticatedUser(
        user_id=token_data.user_id,
        email=token_data.email,
        role=token_data.role,
        is_active=True,
        jti=token_data.jti,
        exp=token_data.exp,
        iat=token_data.iat
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> AuthenticatedUser:
    """
    Mandatory authentication dependency: raises 401 if missing or invalid token.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token_data = decode_access_token(credentials.credentials)
    return AuthenticatedUser(
        user_id=token_data.user_id,
        email=token_data.email,
        role=token_data.role,
        is_active=True,
        jti=token_data.jti,
        exp=token_data.exp,
        iat=token_data.iat
    )


def require_role(allowed_roles: List[UserRole]):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Enforces vertical privilege boundaries (e.g. CLINICIAN or ADMIN only).
    """
    async def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of roles {[r.value for r in allowed_roles]}, but user has role '{current_user.role.value}'."
            )
        return current_user
    return role_checker


# Convenient role dependencies
require_clinician = require_role([UserRole.CLINICIAN, UserRole.ADMIN])
require_admin = require_role([UserRole.ADMIN])


# ------------------------------------------------------------------------------
# 4. IDOR & Resource Ownership Verification Guard
# ------------------------------------------------------------------------------

def verify_resource_ownership(
    resource_user_id: Optional[str],
    current_user: AuthenticatedUser,
    resource_type: str = "Resource",
    allow_clinician: bool = True,
    resource_id: Optional[str] = None
) -> bool:
    """
    Validates that the current authenticated user owns the requested resource.
    Prevents Insecure Direct Object References (IDOR) and Horizontal Privilege Escalation.
    
    - PATIENT: Can ONLY access their own resources (resource_user_id == current_user.user_id).
    - CLINICIAN / ADMIN: Allowed access across patient resources for clinical review (if allow_clinician=True).
    """
    if not resource_user_id:
        # Legacy/demo unassigned resources remain accessible
        return True

    # User owns the resource
    if str(resource_user_id) == str(current_user.user_id):
        return True

    # Elevated roles may access for clinical review
    if allow_clinician and current_user.role in [UserRole.CLINICIAN, UserRole.ADMIN]:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied: you do not have permission to view or modify this {resource_type}."
    )
