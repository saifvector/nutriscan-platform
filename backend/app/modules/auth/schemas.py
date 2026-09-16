"""
Pydantic V2 Schemas for Authentication & User Account Management
"""

from typing import Optional
from pydantic import BaseModel, Field
from ...core.auth import UserRole


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Unique user email address", min_length=3, max_length=255)
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: Optional[str] = Field(default="", description="First name")
    last_name: Optional[str] = Field(default="", description="Last name")
    role: Optional[UserRole] = Field(default=UserRole.PATIENT, description="Account role: PATIENT, CLINICIAN, or ADMIN")


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address", min_length=3, max_length=255)
    password: str = Field(..., description="Account password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    role: UserRole


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    role: UserRole
    is_active: bool
    created_at: str


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="Current account password")
    new_password: str = Field(..., min_length=8, description="New account password (minimum 8 characters)")


class RevokeTokenRequest(BaseModel):
    jti: Optional[str] = Field(default=None, description="Specific JWT ID to invalidate")
    user_id: Optional[str] = Field(default=None, description="User ID to invalidate all active sessions for")


class GenericMessageResponse(BaseModel):
    status: str = "success"
    message: str
