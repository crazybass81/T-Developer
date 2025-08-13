"""
API Key Management System
엔터프라이즈 API 키 관리
"""

import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from pydantic import BaseModel


class APIKey(BaseModel):
    """API 키 모델"""

    id: str
    key_hash: str  # Store hash, not plain key
    name: str
    user_id: str
    organization_id: Optional[str] = None

    # Permissions
    scopes: List[str] = []
    rate_limit: int = 1000  # requests per hour

    # Metadata
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0

    # Status
    is_active: bool = True
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None

    # IP restrictions
    allowed_ips: List[str] = []
    allowed_domains: List[str] = []

    # Usage limits
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    total_limit: Optional[int] = None


class APIKeyManager:
    """API 키 생성 및 관리"""

    KEY_PREFIX = "tdv_"  # T-Developer API key prefix
    KEY_LENGTH = 32

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(
            host="localhost", port=6379, db=3, decode_responses=True
        )

    def generate_api_key(
        self,
        user_id: str,
        name: str,
        scopes: List[str] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: int = 1000,
        allowed_ips: List[str] = None,
        allowed_domains: List[str] = None,
        organization_id: Optional[str] = None,
    ) -> tuple[str, APIKey]:
        """새 API 키 생성"""

        # Generate secure random key
        raw_key = secrets.token_urlsafe(self.KEY_LENGTH)
        api_key = f"{self.KEY_PREFIX}{raw_key}"

        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Create key ID
        key_id = hashlib.md5(f"{user_id}:{name}:{datetime.now().isoformat()}".encode()).hexdigest()

        # Calculate expiry
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        # Create APIKey object
        api_key_obj = APIKey(
            id=key_id,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            organization_id=organization_id,
            scopes=scopes or [],
            rate_limit=rate_limit,
            created_at=datetime.now(),
            expires_at=expires_at,
            allowed_ips=allowed_ips or [],
            allowed_domains=allowed_domains or [],
            is_active=True,
        )

        # Store in Redis
        self._store_api_key(api_key_obj)

        # Also store hash -> key_id mapping for fast lookup
        self.redis_client.set(
            f"api_key_hash:{key_hash}",
            key_id,
            ex=expires_in_days * 86400 if expires_in_days else None,
        )

        # Return both plain key (only time it's available) and object
        return api_key, api_key_obj

    def validate_api_key(
        self,
        api_key: str,
        required_scopes: List[str] = None,
        client_ip: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Optional[APIKey]:
        """API 키 검증"""

        # Check format
        if not api_key.startswith(self.KEY_PREFIX):
            return None

        # Hash the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Look up key ID
        key_id = self.redis_client.get(f"api_key_hash:{key_hash}")
        if not key_id:
            return None

        # Get key object
        api_key_obj = self._get_api_key(key_id)
        if not api_key_obj:
            return None

        # Check if active
        if not api_key_obj.is_active or api_key_obj.is_revoked:
            return None

        # Check expiry
        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.now():
            return None

        # Check IP restrictions
        if api_key_obj.allowed_ips and client_ip:
            if client_ip not in api_key_obj.allowed_ips:
                return None

        # Check domain restrictions
        if api_key_obj.allowed_domains and domain:
            if not any(domain.endswith(allowed) for allowed in api_key_obj.allowed_domains):
                return None

        # Check required scopes
        if required_scopes:
            if not all(scope in api_key_obj.scopes for scope in required_scopes):
                return None

        # Check usage limits
        if not self._check_usage_limits(api_key_obj):
            return None

        # Update usage stats
        self._update_usage_stats(api_key_obj)

        return api_key_obj

    def revoke_api_key(self, key_id: str, reason: str = "Manual revocation") -> bool:
        """API 키 취소"""

        api_key_obj = self._get_api_key(key_id)
        if not api_key_obj:
            return False

        api_key_obj.is_revoked = True
        api_key_obj.revoked_at = datetime.now()
        api_key_obj.revoked_reason = reason

        self._store_api_key(api_key_obj)

        # Remove hash mapping
        self.redis_client.delete(f"api_key_hash:{api_key_obj.key_hash}")

        return True

    def list_user_api_keys(self, user_id: str, include_revoked: bool = False) -> List[APIKey]:
        """사용자의 모든 API 키 조회"""

        pattern = f"api_key:*"
        keys = self.redis_client.keys(pattern)

        user_keys = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                api_key_obj = APIKey(**json.loads(data))
                if api_key_obj.user_id == user_id:
                    if include_revoked or not api_key_obj.is_revoked:
                        user_keys.append(api_key_obj)

        return user_keys

    def rotate_api_key(
        self, key_id: str, expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """API 키 교체 (기존 키 취소 후 새 키 발급)"""

        # Get existing key
        old_key = self._get_api_key(key_id)
        if not old_key:
            raise ValueError("API key not found")

        # Revoke old key
        self.revoke_api_key(key_id, "Key rotation")

        # Generate new key with same settings
        return self.generate_api_key(
            user_id=old_key.user_id,
            name=f"{old_key.name} (rotated)",
            scopes=old_key.scopes,
            expires_in_days=expires_in_days,
            rate_limit=old_key.rate_limit,
            allowed_ips=old_key.allowed_ips,
            allowed_domains=old_key.allowed_domains,
            organization_id=old_key.organization_id,
        )

    def _store_api_key(self, api_key: APIKey):
        """Redis에 API 키 저장"""
        key = f"api_key:{api_key.id}"
        value = api_key.json()

        if api_key.expires_at:
            ttl = int((api_key.expires_at - datetime.now()).total_seconds())
            if ttl > 0:
                self.redis_client.setex(key, ttl, value)
        else:
            self.redis_client.set(key, value)

    def _get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Redis에서 API 키 조회"""
        data = self.redis_client.get(f"api_key:{key_id}")
        if data:
            return APIKey(**json.loads(data))
        return None

    def _check_usage_limits(self, api_key: APIKey) -> bool:
        """사용량 제한 확인"""

        # Check total limit
        if api_key.total_limit and api_key.usage_count >= api_key.total_limit:
            return False

        # Check daily limit
        if api_key.daily_limit:
            daily_key = f"api_usage:daily:{api_key.id}:{datetime.now().date()}"
            daily_count = int(self.redis_client.get(daily_key) or 0)
            if daily_count >= api_key.daily_limit:
                return False

        # Check monthly limit
        if api_key.monthly_limit:
            monthly_key = f"api_usage:monthly:{api_key.id}:{datetime.now().strftime('%Y-%m')}"
            monthly_count = int(self.redis_client.get(monthly_key) or 0)
            if monthly_count >= api_key.monthly_limit:
                return False

        return True

    def _update_usage_stats(self, api_key: APIKey):
        """사용 통계 업데이트"""

        # Update last used
        api_key.last_used_at = datetime.now()
        api_key.usage_count += 1
        self._store_api_key(api_key)

        # Update daily counter
        if api_key.daily_limit:
            daily_key = f"api_usage:daily:{api_key.id}:{datetime.now().date()}"
            self.redis_client.incr(daily_key)
            self.redis_client.expire(daily_key, 86400)  # Expire after 24 hours

        # Update monthly counter
        if api_key.monthly_limit:
            monthly_key = f"api_usage:monthly:{api_key.id}:{datetime.now().strftime('%Y-%m')}"
            self.redis_client.incr(monthly_key)
            self.redis_client.expire(monthly_key, 2592000)  # Expire after 30 days


# FastAPI Dependencies
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: Optional[str] = Depends(api_key_header),
    api_key_query: Optional[str] = Depends(api_key_query),
    request: Request = None,
) -> Optional[APIKey]:
    """API 키 추출 및 검증"""

    # Get API key from header or query
    api_key = api_key_header or api_key_query

    if not api_key:
        return None

    # Get client info
    client_ip = request.client.host if request else None
    domain = request.headers.get("Origin") or request.headers.get("Referer") if request else None

    # Validate key
    manager = APIKeyManager()
    api_key_obj = manager.validate_api_key(api_key, client_ip=client_ip, domain=domain)

    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )

    return api_key_obj


def require_api_key_scopes(*scopes: str):
    """API 키 스코프 요구 데코레이터"""

    async def dependency(api_key: APIKey = Depends(get_api_key)):
        if not api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

        if not all(scope in api_key.scopes for scope in scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient API key permissions",
            )

        return api_key

    return dependency
