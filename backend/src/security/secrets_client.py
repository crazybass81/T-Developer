#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Secrets Manager Python Client
AWS Secrets Manager와의 안전하고 효율적인 통신을 위한 클라이언트

Features:
- 자동 캐싱 및 TTL 관리
- 연결 풀링 및 재시도 로직
- 보안 로깅 및 감사 추적
- 환경별 설정 관리
- 비동기 지원
- 자동 키 회전 감지
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache, wraps
from threading import Lock, RLock
from typing import Any, Dict, List, Optional, Tuple, Union

import boto3
import redis
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

# 환경 설정
PROJECT_NAME = os.environ.get("PROJECT_NAME", "t-developer")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# 로깅 설정
logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """비밀 메타데이터"""

    name: str
    version: str
    created_date: datetime
    last_accessed: datetime
    ttl_expires: datetime
    kms_key_id: Optional[str] = None
    rotation_enabled: bool = False
    tags: Dict[str, str] = None


@dataclass
class CacheConfig:
    """캐시 설정"""

    enabled: bool = True
    ttl_seconds: int = 300  # 5분
    max_size: int = 100
    redis_url: Optional[str] = None
    encryption_key: Optional[str] = None


@dataclass
class ClientConfig:
    """클라이언트 설정"""

    region: str = AWS_REGION
    retry_attempts: int = 3
    retry_backoff: float = 1.0
    timeout_seconds: int = 30
    cache_config: CacheConfig = None
    thread_pool_workers: int = 10
    audit_logging: bool = True
    encryption_in_transit: bool = True


class SecretsManagerError(Exception):
    """Secrets Manager 관련 오류"""

    pass


class SecretNotFoundError(SecretsManagerError):
    """비밀을 찾을 수 없음"""

    pass


class AccessDeniedError(SecretsManagerError):
    """접근 거부됨"""

    pass


class SecretExpiredError(SecretsManagerError):
    """비밀이 만료됨"""

    pass


class AuditLogger:
    """보안 감사 로깅"""

    def __init__(self, audit_enabled: bool = True):
        self.enabled = audit_enabled
        self.logger = logging.getLogger(f"{__name__}.audit")

    def log_access(
        self,
        secret_name: str,
        operation: str,
        success: bool,
        user_agent: str = None,
        source_ip: str = None,
        **kwargs,
    ):
        """비밀 접근 로깅"""
        if not self.enabled:
            return

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "secret_name": self._mask_secret_name(secret_name),
            "success": success,
            "environment": ENVIRONMENT,
            "project": PROJECT_NAME,
            "user_agent": user_agent,
            "source_ip": source_ip,
            **kwargs,
        }

        log_level = logging.INFO if success else logging.WARNING
        self.logger.log(log_level, f"SECRET_ACCESS: {json.dumps(audit_entry)}")

    def _mask_secret_name(self, secret_name: str) -> str:
        """비밀 이름 마스킹 (보안을 위해)"""
        if "/" in secret_name:
            parts = secret_name.split("/")
            # 마지막 부분만 마스킹
            parts[-1] = f"{parts[-1][:3]}***{parts[-1][-3:]}" if len(parts[-1]) > 6 else "***"
            return "/".join(parts)
        return f"{secret_name[:3]}***{secret_name[-3:]}" if len(secret_name) > 6 else "***"


class SecretCache:
    """비밀 캐싱 시스템"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._local_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_lock = RLock()
        self._redis_client = None

        if config.redis_url:
            try:
                self._redis_client = redis.from_url(config.redis_url)
                self._redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to local cache: {e}")

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if not self.config.enabled:
            return None

        # Redis 시도
        if self._redis_client:
            try:
                cached_data = self._redis_client.get(self._hash_key(key))
                if cached_data:
                    data = json.loads(cached_data.decode())
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    if expires_at > datetime.utcnow():
                        return data["value"]
                    else:
                        self._redis_client.delete(self._hash_key(key))
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        # 로컬 캐시 확인
        with self._cache_lock:
            if key in self._local_cache:
                value, expires_at = self._local_cache[key]
                if expires_at > datetime.utcnow():
                    return value
                else:
                    del self._local_cache[key]

        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        if not self.config.enabled:
            return

        ttl = ttl_seconds or self.config.ttl_seconds
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        # Redis 저장
        if self._redis_client:
            try:
                cache_data = {"value": value, "expires_at": expires_at.isoformat()}
                self._redis_client.setex(self._hash_key(key), ttl, json.dumps(cache_data))
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        # 로컬 캐시 저장
        with self._cache_lock:
            # 캐시 크기 제한
            if len(self._local_cache) >= self.config.max_size:
                # 가장 오래된 항목 제거 (LRU 방식)
                oldest_key = min(self._local_cache.keys(), key=lambda k: self._local_cache[k][1])
                del self._local_cache[oldest_key]

            self._local_cache[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        """캐시에서 값 제거"""
        if self._redis_client:
            try:
                self._redis_client.delete(self._hash_key(key))
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        with self._cache_lock:
            self._local_cache.pop(key, None)

    def clear(self) -> None:
        """모든 캐시 데이터 제거"""
        if self._redis_client:
            try:
                # 프로젝트별 키만 삭제
                pattern = f"{PROJECT_NAME}:secrets:*"
                keys = self._redis_client.keys(pattern)
                if keys:
                    self._redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

        with self._cache_lock:
            self._local_cache.clear()

    def _hash_key(self, key: str) -> str:
        """키 해싱 (Redis 키 네임스페이스)"""
        return f"{PROJECT_NAME}:secrets:{hashlib.md5(key.encode()).hexdigest()}"


def retry_on_exception(max_retries: int = 3, backoff_factor: float = 1.0):
    """재시도 데코레이터"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ClientError, NoCredentialsError) as e:
                    last_exception = e
                    if attempt == max_retries:
                        break

                    # 재시도할 수 없는 오류들
                    error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
                    if error_code in [
                        "ResourceNotFoundException",
                        "AccessDeniedException",
                    ]:
                        break

                    # 백오프 대기
                    wait_time = backoff_factor * (2**attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)

            raise last_exception

        return wrapper

    return decorator


class SecretsManagerClient:
    """T-Developer Secrets Manager 클라이언트"""

    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        if self.config.cache_config is None:
            self.config.cache_config = CacheConfig()

        # AWS 클라이언트 설정
        boto_config = Config(
            region_name=self.config.region,
            retries={"max_attempts": self.config.retry_attempts},
            connect_timeout=self.config.timeout_seconds,
            read_timeout=self.config.timeout_seconds,
            max_pool_connections=50,
        )

        self._client = boto3.client("secretsmanager", config=boto_config)
        self._cache = SecretCache(self.config.cache_config)
        self._audit_logger = AuditLogger(self.config.audit_logging)
        self._executor = ThreadPoolExecutor(max_workers=self.config.thread_pool_workers)
        self._metadata_cache: Dict[str, SecretMetadata] = {}
        self._metadata_lock = Lock()

    @retry_on_exception(max_retries=3)
    def get_secret(
        self,
        secret_name: str,
        version_id: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """비밀 조회 (메인 메서드)"""
        start_time = time.time()
        cache_key = f"{secret_name}:{version_id or 'AWSCURRENT'}"

        try:
            # 캐시 확인 (강제 새로고침이 아닌 경우)
            if not force_refresh:
                cached_value = self._cache.get(cache_key)
                if cached_value:
                    self._audit_logger.log_access(
                        secret_name,
                        "get_secret",
                        True,
                        source="cache",
                        response_time_ms=round((time.time() - start_time) * 1000),
                    )
                    return cached_value

            # AWS에서 비밀 조회
            kwargs = {"SecretId": secret_name}
            if version_id:
                kwargs["VersionId"] = version_id

            response = self._client.get_secret_value(**kwargs)

            # 응답 처리
            secret_data = {
                "name": response["Name"],
                "arn": response["ARN"],
                "version_id": response["VersionId"],
                "created_date": response["CreatedDate"].isoformat(),
                "secret_string": response.get("SecretString"),
                "secret_binary": response.get("SecretBinary"),
                "kms_key_id": response.get("KmsKeyId"),
                "version_stages": response.get("VersionStages", []),
            }

            # JSON 파싱 시도
            if secret_data["secret_string"]:
                try:
                    secret_data["parsed_secret"] = json.loads(secret_data["secret_string"])
                except json.JSONDecodeError:
                    # JSON이 아닌 경우 그대로 유지
                    pass

            # 캐시에 저장
            self._cache.set(cache_key, secret_data)

            # 메타데이터 업데이트
            self._update_metadata(secret_name, response)

            # 감사 로그
            self._audit_logger.log_access(
                secret_name,
                "get_secret",
                True,
                source="aws",
                response_time_ms=round((time.time() - start_time) * 1000),
                version_id=version_id,
            )

            return secret_data

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            # 특정 에러 처리
            if error_code == "ResourceNotFoundException":
                self._audit_logger.log_access(secret_name, "get_secret", False, error="not_found")
                raise SecretNotFoundError(f"Secret not found: {secret_name}")
            elif error_code == "AccessDeniedException":
                self._audit_logger.log_access(
                    secret_name, "get_secret", False, error="access_denied"
                )
                raise AccessDeniedError(f"Access denied to secret: {secret_name}")
            else:
                self._audit_logger.log_access(secret_name, "get_secret", False, error=error_code)
                raise SecretsManagerError(f"Error retrieving secret: {e}")

    def get_secret_string(self, secret_name: str, version_id: Optional[str] = None) -> str:
        """비밀 문자열만 반환"""
        secret_data = self.get_secret(secret_name, version_id)
        return secret_data.get("secret_string", "")

    def get_secret_json(self, secret_name: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        """JSON 형태의 비밀 반환"""
        secret_data = self.get_secret(secret_name, version_id)
        if "parsed_secret" in secret_data:
            return secret_data["parsed_secret"]

        # JSON 파싱 재시도
        secret_string = secret_data.get("secret_string", "")
        if secret_string:
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError:
                raise SecretsManagerError(f"Secret is not valid JSON: {secret_name}")

        raise SecretsManagerError(f"No secret string found: {secret_name}")

    def get_secret_value(
        self,
        secret_name: str,
        key: str,
        default: Any = None,
        version_id: Optional[str] = None,
    ) -> Any:
        """JSON 비밀에서 특정 키 값 추출"""
        try:
            secret_json = self.get_secret_json(secret_name, version_id)
            return secret_json.get(key, default)
        except (SecretsManagerError, KeyError):
            return default

    def batch_get_secrets(self, secret_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """다중 비밀 배치 조회"""
        if not secret_names:
            return {}

        # 병렬 처리로 성능 향상
        futures = {}
        for secret_name in secret_names:
            future = self._executor.submit(self.get_secret, secret_name)
            futures[secret_name] = future

        results = {}
        for secret_name, future in futures.items():
            try:
                results[secret_name] = future.result(timeout=self.config.timeout_seconds)
            except Exception as e:
                logger.warning(f"Failed to get secret {secret_name}: {e}")
                results[secret_name] = None

        return results

    async def get_secret_async(
        self, secret_name: str, version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """비동기 비밀 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.get_secret, secret_name, version_id)

    @retry_on_exception(max_retries=2)
    def list_secrets(self, name_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """비밀 목록 조회"""
        try:
            kwargs = {}
            if name_prefix:
                kwargs["Filters"] = [{"Key": "name", "Values": [name_prefix]}]

            response = self._client.list_secrets(**kwargs)

            secrets = []
            for secret in response["SecretList"]:
                secrets.append(
                    {
                        "name": secret["Name"],
                        "arn": secret["ARN"],
                        "description": secret.get("Description", ""),
                        "kms_key_id": secret.get("KmsKeyId"),
                        "rotation_enabled": secret.get("RotationEnabled", False),
                        "last_changed_date": secret.get("LastChangedDate", "").isoformat()
                        if secret.get("LastChangedDate")
                        else None,
                        "tags": secret.get("Tags", []),
                    }
                )

            return secrets

        except ClientError as e:
            raise SecretsManagerError(f"Error listing secrets: {e}")

    def get_t_developer_secrets(self) -> Dict[str, Dict[str, Any]]:
        """T-Developer 프로젝트의 모든 비밀 조회"""
        prefix = f"{PROJECT_NAME}/"
        secrets_list = self.list_secrets(name_prefix=prefix)

        secret_names = [s["name"] for s in secrets_list]
        return self.batch_get_secrets(secret_names)

    def get_api_credentials(self) -> Dict[str, Dict[str, Any]]:
        """API 인증정보 조회 (OpenAI, Anthropic 등)"""
        api_secrets = {}

        # OpenAI API Key
        try:
            openai_secret = self.get_secret_json(f"{PROJECT_NAME}/evolution/openai-api-key")
            api_secrets["openai"] = openai_secret
        except SecretsManagerError:
            logger.warning("OpenAI API key not found")

        # Anthropic API Key
        try:
            anthropic_secret = self.get_secret_json(f"{PROJECT_NAME}/evolution/anthropic-api-key")
            api_secrets["anthropic"] = anthropic_secret
        except SecretsManagerError:
            logger.warning("Anthropic API key not found")

        return api_secrets

    def get_database_credentials(self) -> Dict[str, Any]:
        """데이터베이스 인증정보 조회"""
        try:
            return self.get_secret_json(f"{PROJECT_NAME}/database/credentials")
        except SecretsManagerError:
            logger.warning("Database credentials not found")
            return {}

    def get_system_secrets(self) -> Dict[str, Any]:
        """시스템 비밀 조회 (마스터 키, JWT 등)"""
        try:
            return self.get_secret_json(f"{PROJECT_NAME}/evolution/master-secret")
        except SecretsManagerError:
            logger.warning("System secrets not found")
            return {}

    def invalidate_cache(self, secret_name: Optional[str] = None) -> None:
        """캐시 무효화"""
        if secret_name:
            # 특정 비밀의 모든 버전 캐시 제거
            keys_to_remove = [
                key for key in self._cache._local_cache.keys() if key.startswith(f"{secret_name}:")
            ]
            for key in keys_to_remove:
                self._cache.delete(key)
        else:
            # 모든 캐시 제거
            self._cache.clear()

    def refresh_secret(self, secret_name: str) -> Dict[str, Any]:
        """비밀 강제 새로고침"""
        self.invalidate_cache(secret_name)
        return self.get_secret(secret_name, force_refresh=True)

    def _update_metadata(self, secret_name: str, response: Dict[str, Any]) -> None:
        """메타데이터 업데이트"""
        with self._metadata_lock:
            self._metadata_cache[secret_name] = SecretMetadata(
                name=response["Name"],
                version=response["VersionId"],
                created_date=response["CreatedDate"],
                last_accessed=datetime.utcnow(),
                ttl_expires=datetime.utcnow()
                + timedelta(seconds=self.config.cache_config.ttl_seconds),
                kms_key_id=response.get("KmsKeyId"),
                rotation_enabled=False,  # 별도 API 호출 필요
                tags={},
            )

    def get_metadata(self, secret_name: str) -> Optional[SecretMetadata]:
        """비밀 메타데이터 조회"""
        with self._metadata_lock:
            return self._metadata_cache.get(secret_name)

    def close(self) -> None:
        """리소스 정리"""
        self._executor.shutdown(wait=True)
        if hasattr(self._cache, "_redis_client") and self._cache._redis_client:
            self._cache._redis_client.close()


# 글로벌 클라이언트 인스턴스 (싱글톤 패턴)
_global_client: Optional[SecretsManagerClient] = None
_client_lock = Lock()


def get_client(config: Optional[ClientConfig] = None) -> SecretsManagerClient:
    """글로벌 Secrets Manager 클라이언트 가져오기"""
    global _global_client

    with _client_lock:
        if _global_client is None:
            _global_client = SecretsManagerClient(config)
        return _global_client


# 편의 함수들
def get_secret(secret_name: str, version_id: Optional[str] = None) -> Dict[str, Any]:
    """간편한 비밀 조회"""
    return get_client().get_secret(secret_name, version_id)


def get_secret_value(secret_name: str, key: str, default: Any = None) -> Any:
    """간편한 비밀 값 조회"""
    return get_client().get_secret_value(secret_name, key, default)


def get_api_key(service: str) -> Optional[str]:
    """API 키 간편 조회"""
    credentials = get_client().get_api_credentials()
    service_creds = credentials.get(service.lower(), {})
    return service_creds.get("api_key")


# 테스트용 함수
if __name__ == "__main__":
    # 간단한 테스트
    logging.basicConfig(level=logging.INFO)

    try:
        client = SecretsManagerClient()

        # 테스트 비밀 목록 조회
        secrets = client.list_secrets(name_prefix=PROJECT_NAME)
        print(f"Found {len(secrets)} secrets")

        # API 인증정보 테스트
        api_creds = client.get_api_credentials()
        print(f"API credentials available: {list(api_creds.keys())}")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if "client" in locals():
            client.close()
