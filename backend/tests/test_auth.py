"""
Authentication Tests
JWT 및 인증 시스템 테스트
"""

import pytest
from datetime import datetime, timedelta
from src.auth.jwt_handler import JWTHandler, create_access_token, verify_token
from src.auth.models import User, UserRole, Permission
from src.auth.permissions import has_permission, has_all_permissions


class TestJWTHandler:
    """JWT Handler 테스트"""

    def test_create_access_token(self):
        """Access token 생성 테스트"""
        handler = JWTHandler()

        token = handler.create_access_token(
            user_id="test-user-id",
            email="test@example.com",
            roles=["user"],
            permissions=["project:read"],
        )

        assert token is not None
        assert isinstance(token, str)
        assert token.count(".") == 2  # JWT format: header.payload.signature

    def test_verify_valid_token(self):
        """유효한 토큰 검증 테스트"""
        handler = JWTHandler()

        token = handler.create_access_token(
            user_id="test-user-id", email="test@example.com"
        )

        payload = handler.verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_verify_expired_token(self):
        """만료된 토큰 검증 테스트"""
        handler = JWTHandler()
        handler.access_token_expire = -1  # Set to expire immediately

        token = handler.create_access_token(
            user_id="test-user-id", email="test@example.com"
        )

        with pytest.raises(ValueError, match="Token has expired"):
            handler.verify_token(token, token_type="access")

    def test_verify_invalid_token(self):
        """잘못된 토큰 검증 테스트"""
        handler = JWTHandler()

        with pytest.raises(ValueError, match="Invalid token"):
            handler.verify_token("invalid.token.here", token_type="access")

    def test_refresh_token_creation(self):
        """Refresh token 생성 테스트"""
        handler = JWTHandler()

        token = handler.create_refresh_token(
            user_id="test-user-id", email="test@example.com"
        )

        payload = handler.verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload["type"] == "refresh"
        assert payload["sub"] == "test-user-id"

    def test_token_revocation(self, mock_redis):
        """토큰 취소 테스트"""
        handler = JWTHandler()
        handler.redis_client = mock_redis

        token = handler.create_access_token(
            user_id="test-user-id", email="test@example.com"
        )

        result = handler.revoke_token(token)
        assert result is True

    def test_refresh_access_token(self):
        """Access token 갱신 테스트"""
        handler = JWTHandler()

        refresh_token = handler.create_refresh_token(
            user_id="test-user-id", email="test@example.com"
        )

        new_access_token = handler.refresh_access_token(refresh_token)

        assert new_access_token is not None
        payload = handler.verify_token(new_access_token, token_type="access")
        assert payload["sub"] == "test-user-id"


class TestPermissions:
    """권한 시스템 테스트"""

    def test_user_permissions(self):
        """사용자 권한 확인 테스트"""
        user = User(
            id="test-id",
            email="test@example.com",
            roles=[UserRole.USER],
            permissions=[],
            is_active=True,
        )

        # User role should have PROJECT_READ permission
        assert has_permission(user, Permission.PROJECT_READ)
        assert has_permission(user, Permission.PROJECT_CREATE)

        # User role should not have admin permissions
        assert not has_permission(user, Permission.ADMIN_ACCESS)
        assert not has_permission(user, Permission.USER_DELETE)

    def test_admin_permissions(self):
        """관리자 권한 확인 테스트"""
        admin = User(
            id="admin-id",
            email="admin@example.com",
            roles=[UserRole.ADMIN],
            permissions=[],
            is_active=True,
        )

        # Admin should have most permissions
        assert has_permission(admin, Permission.PROJECT_CREATE)
        assert has_permission(admin, Permission.USER_CREATE)
        assert has_permission(admin, Permission.ADMIN_ACCESS)

        # Admin should not have SUPER_ADMIN only permissions
        assert not has_permission(admin, Permission.ADMIN_MANAGE)

    def test_super_admin_permissions(self):
        """슈퍼 관리자 권한 확인 테스트"""
        super_admin = User(
            id="super-id",
            email="super@example.com",
            roles=[UserRole.SUPER_ADMIN],
            permissions=[],
            is_active=True,
        )

        # Super admin should have all permissions
        assert has_permission(super_admin, Permission.ADMIN_MANAGE)
        assert has_permission(super_admin, Permission.BILLING_MANAGE)
        assert has_permission(super_admin, Permission.API_UNLIMITED)

    def test_custom_permissions(self):
        """커스텀 권한 테스트"""
        user = User(
            id="custom-id",
            email="custom@example.com",
            roles=[UserRole.USER],
            permissions=[Permission.BILLING_VIEW, Permission.API_PREMIUM],
            is_active=True,
        )

        # Should have custom permissions in addition to role permissions
        assert has_permission(user, Permission.PROJECT_READ)  # From role
        assert has_permission(user, Permission.BILLING_VIEW)  # Custom
        assert has_permission(user, Permission.API_PREMIUM)  # Custom

    def test_has_all_permissions(self):
        """모든 권한 보유 확인 테스트"""
        user = User(
            id="test-id",
            email="test@example.com",
            roles=[UserRole.DEVELOPER],
            permissions=[],
            is_active=True,
        )

        # Should have all these permissions
        assert has_all_permissions(
            user, [Permission.PROJECT_CREATE, Permission.PROJECT_READ]
        )

        # Should not have all these permissions
        assert not has_all_permissions(
            user, [Permission.PROJECT_CREATE, Permission.ADMIN_ACCESS]
        )
