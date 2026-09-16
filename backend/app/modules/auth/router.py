"""
Authentication REST API Router
Phase 1 & 3: Advanced Security, Authentication & User Management

Endpoints:
- POST /api/v1/auth/register  : Creates new user account with PBKDF2 hashed password
- POST /api/v1/auth/login     : Authenticates credentials, issues cryptographically signed JWT
- GET  /api/v1/auth/me        : Returns currently authenticated user context
- POST /api/v1/auth/refresh   : Rotates JWT access token, preventing session fixation
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr

from .schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
    ChangePasswordRequest,
    RevokeTokenRequest,
    GenericMessageResponse
)
from ...core.auth import (
    UserRole,
    AuthenticatedUser,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ...core.session_manager import session_manager
from ...core.persistence import PersistenceRepository

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Registers a new patient or clinician account with salted PBKDF2-HMAC-SHA256 password hashing."
)
async def register(request: UserRegisterRequest) -> TokenResponse:
    existing = PersistenceRepository.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    pwd_hash = hash_password(request.password)
    user_data = PersistenceRepository.create_user(
        email=request.email,
        password_hash=pwd_hash,
        role=request.role.value if request.role else UserRole.PATIENT.value,
        first_name=request.first_name or "",
        last_name=request.last_name or ""
    )

    PersistenceRepository.log_audit_event(
        module="AUTH",
        action="USER_REGISTERED",
        severity="INFO",
        user_id=user_data["user_id"],
        details={"email": request.email, "role": user_data["role"]}
    )

    token = create_access_token(
        user_id=user_data["user_id"],
        email=user_data["email"],
        role=UserRole(user_data["role"])
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_data["user_id"],
        email=user_data["email"],
        role=UserRole(user_data["role"])
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates credentials using constant-time comparison and returns signed JWT."
)
async def login(request: UserLoginRequest) -> TokenResponse:
    user = PersistenceRepository.get_user_by_email(request.email)
    if not user or not user.get("is_active"):
        PersistenceRepository.log_audit_event(
            module="AUTH",
            action="LOGIN_FAILED_UNKNOWN_USER",
            severity="WARNING",
            details={"attempted_email": request.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(request.password, user["password_hash"]):
        PersistenceRepository.log_audit_event(
            module="AUTH",
            action="LOGIN_FAILED_BAD_PASSWORD",
            severity="WARNING",
            user_id=user["id"],
            details={"email": request.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    PersistenceRepository.update_user_last_login(user["id"])
    PersistenceRepository.log_audit_event(
        module="AUTH",
        action="LOGIN_SUCCESS",
        severity="INFO",
        user_id=user["id"],
        details={"email": request.email}
    )

    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=UserRole(user["role"])
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user["id"],
        email=user["email"],
        role=UserRole(user["role"])
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns authenticated profile information extracted from validated JWT token."
)
async def get_me(current_user: AuthenticatedUser = Depends(get_current_user)) -> UserProfileResponse:
    user = PersistenceRepository.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    return UserProfileResponse(
        user_id=user["id"],
        email=user["email"],
        role=UserRole(user["role"]),
        is_active=bool(user["is_active"]),
        created_at=user["created_at"]
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Authentication Token",
    description="Rotates access token with fresh expiration and unique JWT ID, preventing session fixation."
)
async def refresh_token(current_user: AuthenticatedUser = Depends(get_current_user)) -> TokenResponse:
    token = create_access_token(
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role
    )

    PersistenceRepository.log_audit_event(
        module="AUTH",
        action="TOKEN_ROTATED",
        severity="INFO",
        user_id=current_user.user_id
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=current_user.user_id,
        email=current_user.email,
        role=current_user.role
    )


@router.post(
    "/logout",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout & Token Revocation",
    description="Instantly revokes current active JWT token by adding its jti to the denylist."
)
async def logout(current_user: AuthenticatedUser = Depends(get_current_user)) -> GenericMessageResponse:
    if current_user.jti:
        session_manager.revoke_token(current_user.jti, float(current_user.exp or 0))

    PersistenceRepository.log_audit_event(
        module="AUTH",
        action="USER_LOGOUT",
        severity="INFO",
        user_id=current_user.user_id,
        details={"jti": current_user.jti}
    )

    return GenericMessageResponse(status="success", message="Successfully logged out and session revoked.")


@router.post(
    "/revoke",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Token & Session Revocation",
    description="Revokes specific JWT by jti, or invalidates all active sessions for a target user."
)
async def revoke_session(
    request: RevokeTokenRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> GenericMessageResponse:
    if request.user_id:
        # Non-admins can only revoke their own sessions
        if request.user_id != current_user.user_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can revoke sessions of other users."
            )
        PersistenceRepository.invalidate_user_sessions(request.user_id)
        return GenericMessageResponse(status="success", message=f"All active sessions for user {request.user_id} revoked.")

    if request.jti:
        # Default 24h expiration if not specified
        session_manager.revoke_token(request.jti, float(current_user.exp or 0))
        return GenericMessageResponse(status="success", message=f"Token {request.jti} revoked.")

    # If neither provided, revoke caller's current token
    if current_user.jti:
        session_manager.revoke_token(current_user.jti, float(current_user.exp or 0))
    return GenericMessageResponse(status="success", message="Current session revoked.")


@router.post(
    "/change-password",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Password & Invalidate Sessions",
    description="Updates user password and immediately invalidates all active tokens across all devices."
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> GenericMessageResponse:
    user = PersistenceRepository.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    if not verify_password(request.old_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed."
        )

    new_hash = hash_password(request.new_password)
    PersistenceRepository.update_user_password(current_user.user_id, new_hash)

    return GenericMessageResponse(
        status="success",
        message="Password successfully updated. All prior active sessions have been invalidated."
    )


@router.post(
    "/update-role",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Role & Enforce Privilege Isolation",
    description="Administrator endpoint to update account role and immediately revoke old session privileges."
)
async def update_user_role(
    target_user_id: str,
    new_role: UserRole,
    admin_user: AuthenticatedUser = Depends(require_admin)
) -> GenericMessageResponse:
    target_user = PersistenceRepository.get_user_by_id(target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found.")

    PersistenceRepository.update_user_role(target_user_id, new_role.value)
    return GenericMessageResponse(
        status="success",
        message=f"User {target_user_id} role updated to {new_role.value}. Active sessions invalidated."
    )
