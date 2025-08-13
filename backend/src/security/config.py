#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Security Configuration
보안 관련 설정 및 초기화

환경변수 기반 설정과 기본값 관리
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from .secrets_client import ClientConfig, CacheConfig
except ImportError:
    from secrets_client import ClientConfig, CacheConfig


@dataclass
class SecurityConfig:
    """보안 설정 통합 클래스"""

    # 환경 정보
    project_name: str = "t-developer"
    environment: str = "development"
    aws_region: str = "us-east-1"

    # Secrets Manager 설정
    secrets_cache_enabled: bool = True
    secrets_cache_ttl: int = 300  # 5분
    secrets_cache_max_size: int = 100
    secrets_retry_attempts: int = 3
    secrets_timeout: int = 30

    # Redis 설정 (선택적)
    redis_url: Optional[str] = None
    redis_enabled: bool = False

    # 감사 및 로깅
    audit_logging_enabled: bool = True
    log_level: str = "INFO"

    # 보안 강화 옵션
    strict_tls: bool = True
    certificate_validation: bool = True

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """환경변수에서 설정 로드"""
        return cls(
            project_name=os.getenv("PROJECT_NAME", "t-developer"),
            environment=os.getenv("ENVIRONMENT", "development"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            secrets_cache_enabled=os.getenv("SECRETS_CACHE_ENABLED", "true").lower()
            == "true",
            secrets_cache_ttl=int(os.getenv("SECRETS_CACHE_TTL", "300")),
            secrets_cache_max_size=int(os.getenv("SECRETS_CACHE_MAX_SIZE", "100")),
            secrets_retry_attempts=int(os.getenv("SECRETS_RETRY_ATTEMPTS", "3")),
            secrets_timeout=int(os.getenv("SECRETS_TIMEOUT", "30")),
            redis_url=os.getenv("REDIS_URL"),
            redis_enabled=os.getenv("REDIS_ENABLED", "false").lower() == "true",
            audit_logging_enabled=os.getenv("AUDIT_LOGGING_ENABLED", "true").lower()
            == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            strict_tls=os.getenv("STRICT_TLS", "true").lower() == "true",
            certificate_validation=os.getenv("CERT_VALIDATION", "true").lower()
            == "true",
        )

    def to_secrets_client_config(self) -> ClientConfig:
        """Secrets Manager 클라이언트 설정으로 변환"""
        cache_config = CacheConfig(
            enabled=self.secrets_cache_enabled,
            ttl_seconds=self.secrets_cache_ttl,
            max_size=self.secrets_cache_max_size,
            redis_url=self.redis_url if self.redis_enabled else None,
        )

        return ClientConfig(
            region=self.aws_region,
            retry_attempts=self.secrets_retry_attempts,
            timeout_seconds=self.secrets_timeout,
            cache_config=cache_config,
            audit_logging=self.audit_logging_enabled,
            encryption_in_transit=self.strict_tls,
        )

    def to_parameter_client_config(self):
        """Parameter Store 클라이언트 설정으로 변환"""
        try:
            from parameter_store_client import ParameterConfig

            return ParameterConfig(
                region=self.aws_region,
                cache_enabled=self.secrets_cache_enabled,
                cache_ttl_seconds=self.secrets_cache_ttl,
                cache_max_size=self.secrets_cache_max_size,
                retry_attempts=self.secrets_retry_attempts,
                timeout_seconds=self.secrets_timeout,
            )
        except ImportError:
            # Parameter Store 클라이언트가 없는 경우 기본값 반환
            return None

    def get_secret_names(self) -> Dict[str, str]:
        """프로젝트별 비밀 이름 매핑"""
        return {
            "openai_api": f"{self.project_name}/evolution/openai-api-key",
            "anthropic_api": f"{self.project_name}/evolution/anthropic-api-key",
            "master_secret": f"{self.project_name}/evolution/master-secret",
            "database_creds": f"{self.project_name}/database/credentials",
            "agent_comm_key": f"{self.project_name}/agents/communication-key",
            "safety_secret": f"{self.project_name}/safety/system-secret",
        }

    def validate(self) -> bool:
        """설정 유효성 검증"""
        if not self.project_name:
            raise ValueError("PROJECT_NAME is required")

        if not self.environment:
            raise ValueError("ENVIRONMENT is required")

        if self.secrets_cache_ttl < 0:
            raise ValueError("Cache TTL must be non-negative")

        if self.secrets_retry_attempts < 0:
            raise ValueError("Retry attempts must be non-negative")

        return True


# 글로벌 설정 인스턴스
_config: Optional[SecurityConfig] = None


def get_config() -> SecurityConfig:
    """글로벌 보안 설정 가져오기"""
    global _config
    if _config is None:
        _config = SecurityConfig.from_env()
        _config.validate()
    return _config


def initialize_security(config: Optional[SecurityConfig] = None) -> SecurityConfig:
    """보안 시스템 초기화"""
    global _config
    _config = config or SecurityConfig.from_env()
    _config.validate()

    # 로깅 레벨 설정
    import logging

    logging.basicConfig(level=getattr(logging, _config.log_level))

    return _config


# 환경별 프리셋
ENVIRONMENT_PRESETS = {
    "development": {
        "secrets_cache_ttl": 60,  # 1분 (개발시 빠른 변경 감지)
        "audit_logging_enabled": True,
        "log_level": "DEBUG",
        "strict_tls": False,  # 개발 환경에서는 완화
    },
    "staging": {
        "secrets_cache_ttl": 300,  # 5분
        "audit_logging_enabled": True,
        "log_level": "INFO",
        "strict_tls": True,
    },
    "production": {
        "secrets_cache_ttl": 600,  # 10분 (성능 최적화)
        "audit_logging_enabled": True,
        "log_level": "WARNING",
        "strict_tls": True,
    },
}


def get_environment_preset(environment: str) -> Dict[str, Any]:
    """환경별 프리셋 설정"""
    return ENVIRONMENT_PRESETS.get(environment, ENVIRONMENT_PRESETS["development"])
