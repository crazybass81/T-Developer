"""
Permission System
역할 기반 접근 제어 (RBAC)
"""

from typing import List, Set
from functools import wraps
from fastapi import Depends, HTTPException, status
from .models import User, UserRole, Permission
from .auth_middleware import get_current_active_user

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.ADMIN_ACCESS,
        Permission.ADMIN_MANAGE,
        Permission.BILLING_VIEW,
        Permission.BILLING_MANAGE,
        Permission.API_UNLIMITED,
        Permission.API_PREMIUM,
    },
    UserRole.ADMIN: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.ADMIN_ACCESS,
        Permission.BILLING_VIEW,
        Permission.API_PREMIUM,
    },
    UserRole.DEVELOPER: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.USER_READ,
        Permission.API_PREMIUM,
    },
    UserRole.USER: {
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.USER_READ,
    },
    UserRole.GUEST: {
        Permission.PROJECT_READ,
    },
}


def get_user_permissions(user: User) -> Set[Permission]:
    """사용자의 모든 권한 가져오기"""
    permissions = set(user.permissions)

    # Add role-based permissions
    for role in user.roles:
        if role in ROLE_PERMISSIONS:
            permissions.update(ROLE_PERMISSIONS[role])

    return permissions


def has_permission(user: User, permission: Permission) -> bool:
    """사용자가 특정 권한을 가지고 있는지 확인"""
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


def has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """사용자가 권한 중 하나라도 가지고 있는지 확인"""
    user_permissions = get_user_permissions(user)
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(user: User, permissions: List[Permission]) -> bool:
    """사용자가 모든 권한을 가지고 있는지 확인"""
    user_permissions = get_user_permissions(user)
    return all(perm in user_permissions for perm in permissions)


class RequirePermissions:
    """권한 요구 의존성"""

    def __init__(self, permissions: List[Permission], require_all: bool = True):
        self.permissions = permissions
        self.require_all = require_all

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if self.require_all:
            has_perms = has_all_permissions(user, self.permissions)
        else:
            has_perms = has_any_permission(user, self.permissions)

        if not has_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        return user


def require_permissions(*permissions: Permission, require_all: bool = True):
    """권한 요구 데코레이터"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs
            user = kwargs.get("current_user") or kwargs.get("user")

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if require_all:
                has_perms = has_all_permissions(user, list(permissions))
            else:
                has_perms = has_any_permission(user, list(permissions))

            if not has_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class RoleChecker:
    """역할 확인 의존성"""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if not any(role in self.allowed_roles for role in user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Role not authorized"
            )
        return user


# Convenience dependencies
require_admin = RoleChecker([UserRole.ADMIN, UserRole.SUPER_ADMIN])
require_developer = RoleChecker(
    [UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPER_ADMIN]
)
require_project_create = RequirePermissions([Permission.PROJECT_CREATE])
require_project_delete = RequirePermissions([Permission.PROJECT_DELETE])
require_user_manage = RequirePermissions(
    [Permission.USER_CREATE, Permission.USER_UPDATE, Permission.USER_DELETE],
    require_all=False,
)
