"""
Authentication Models
사용자 및 권한 모델
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """사용자 역할"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """세부 권한"""

    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    ADMIN_MANAGE = "admin:manage"

    # Billing permissions
    BILLING_VIEW = "billing:view"
    BILLING_MANAGE = "billing:manage"

    # API permissions
    API_UNLIMITED = "api:unlimited"
    API_PREMIUM = "api:premium"


class User(BaseModel):
    """사용자 모델"""

    id: str
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.USER])
    permissions: List[Permission] = Field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    # Enterprise fields
    organization_id: Optional[str] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None

    # Subscription info
    subscription_tier: Optional[str] = "free"
    api_quota: int = 100  # Daily API calls
    storage_quota: int = 1024  # MB

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """사용자 생성 요청"""

    email: EmailStr
    password: str = Field(..., min_length=8)
    username: Optional[str] = None
    full_name: Optional[str] = None
    organization_id: Optional[str] = None


class UserLogin(BaseModel):
    """로그인 요청"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """토큰 응답"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """비밀번호 재설정 확인"""

    token: str
    new_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """사용자 정보 업데이트"""

    username: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""

    current_password: str
    new_password: str = Field(..., min_length=8)
