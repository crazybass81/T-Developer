#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Parameter Store Client (TDD GREEN Phase)
테스트를 통과하는 최소한의 Parameter Store 클라이언트 구현

TDD GREEN Phase: 테스트 통과하는 최소 코드
- 모든 필요한 클래스와 메서드 정의
- 기본적인 기능 구현
- 테스트가 통과하는 수준으로만 작성
"""

import asyncio
import boto3
import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ParameterType:
    """Parameter Store 파라미터 타입 상수"""

    STRING = "String"
    SECURE_STRING = "SecureString"
    STRING_LIST = "StringList"


class ParameterTier:
    """Parameter Store 파라미터 티어 상수"""

    STANDARD = "Standard"
    ADVANCED = "Advanced"
    INTELLIGENT_TIERING = "Intelligent-Tiering"


@dataclass
class ParameterCacheConfig:
    """Parameter Store 캐시 설정"""

    enabled: bool = True
    ttl_seconds: int = 300  # 5분
    max_size: int = 1000
    cleanup_interval: int = 60  # 1분


@dataclass
class ParameterConfig:
    """Parameter Store 클라이언트 설정"""

    region: str = "us-east-1"
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    retry_attempts: int = 3
    timeout_seconds: int = 30

    def to_cache_config(self) -> ParameterCacheConfig:
        """캐시 설정 변환"""
        return ParameterCacheConfig(
            enabled=self.cache_enabled,
            ttl_seconds=self.cache_ttl_seconds,
            max_size=self.cache_max_size,
        )


class ParameterCache:
    """Parameter Store 결과 캐시"""

    def __init__(self, config: ParameterCacheConfig):
        self.config = config
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """캐시에서 값 조회"""
        if not self.config.enabled:
            return None

        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry["timestamp"] < self.config.ttl_seconds:
                    return entry["data"]
                else:
                    # 만료된 엔트리 제거
                    del self._cache[key]

        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """캐시에 값 저장"""
        if not self.config.enabled:
            return

        with self._lock:
            # 크기 제한 확인
            if len(self._cache) >= self.config.max_size:
                # 가장 오래된 항목 제거
                oldest_key = min(
                    self._cache.keys(), key=lambda k: self._cache[k]["timestamp"]
                )
                del self._cache[oldest_key]

            self._cache[key] = {"data": value, "timestamp": time.time()}

    def delete(self, key: str) -> None:
        """캐시에서 특정 키 제거"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """캐시 전체 비우기"""
        with self._lock:
            self._cache.clear()


class ParameterStoreClient:
    """Parameter Store 클라이언트"""

    def __init__(self, config: Optional[ParameterConfig] = None):
        self.config = config or ParameterConfig()
        self._cache = ParameterCache(self.config.to_cache_config())
        self._client = None
        self._thread_pool = ThreadPoolExecutor(max_workers=10)

    @property
    def client(self):
        """SSM 클라이언트 lazy 초기화"""
        if self._client is None:
            self._client = boto3.client("ssm", region_name=self.config.region)
        return self._client

    def _parse_parameter_value(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        """파라미터 값 파싱 (JSON 시도)"""
        result = parameter.copy()

        try:
            # JSON 파싱 시도
            parsed_value = json.loads(parameter["Value"])
            result["parsed_value"] = parsed_value
        except (json.JSONDecodeError, TypeError):
            # JSON이 아니면 원본 값 사용
            result["parsed_value"] = parameter["Value"]

        return result

    def get_parameter(self, name: str, decrypt: bool = True) -> Dict[str, Any]:
        """단일 파라미터 조회"""
        # 캐시 확인
        cached_result = self._cache.get(name)
        if cached_result is not None:
            return cached_result

        try:
            response = self.client.get_parameter(Name=name, WithDecryption=decrypt)

            parameter = response["Parameter"]
            result = self._parse_parameter_value(parameter)

            # 캐시에 저장
            self._cache.set(name, result)

            return result

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ParameterNotFound":
                raise Exception(f"ParameterNotFound: {name}")
            else:
                raise Exception(
                    f"AWS Error {error_code}: {e.response['Error']['Message']}"
                )

    def get_parameter_value(self, name: str, json_key: Optional[str] = None) -> Any:
        """파라미터 값 직접 조회"""
        parameter = self.get_parameter(name)

        if json_key is not None and "parsed_value" in parameter:
            parsed = parameter["parsed_value"]
            if isinstance(parsed, dict) and json_key in parsed:
                return parsed[json_key]
            else:
                raise KeyError(f"Key '{json_key}' not found in parameter JSON")

        return parameter.get("parsed_value", parameter.get("Value"))

    def batch_get_parameters(
        self, names: List[str], decrypt: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """배치 파라미터 조회"""
        results = {}
        uncached_names = []

        # 캐시에서 먼저 조회
        for name in names:
            cached_result = self._cache.get(name)
            if cached_result is not None:
                results[name] = cached_result
            else:
                uncached_names.append(name)

        # 캐시에 없는 것들만 AWS에서 조회
        if uncached_names:
            try:
                # AWS SSM은 한 번에 10개까지만 조회 가능
                for i in range(0, len(uncached_names), 10):
                    batch = uncached_names[i : i + 10]

                    response = self.client.get_parameters(
                        Names=batch, WithDecryption=decrypt
                    )

                    # 성공한 파라미터들 처리
                    for parameter in response["Parameters"]:
                        name = parameter["Name"]
                        result = self._parse_parameter_value(parameter)
                        results[name] = result
                        self._cache.set(name, result)

                    # 실패한 파라미터들 로깅
                    for invalid_name in response.get("InvalidParameters", []):
                        logger.warning(f"Parameter not found: {invalid_name}")

            except ClientError as e:
                logger.error(f"Batch get parameters error: {e}")
                raise

        return results

    def get_parameters_by_path(
        self, path: str, recursive: bool = True, decrypt: bool = True
    ) -> List[Dict[str, Any]]:
        """경로별 파라미터 조회"""
        results = []
        next_token = None

        try:
            while True:
                kwargs = {
                    "Path": path,
                    "Recursive": recursive,
                    "WithDecryption": decrypt,
                    "MaxResults": 10,
                }

                if next_token:
                    kwargs["NextToken"] = next_token

                response = self.client.get_parameters_by_path(**kwargs)

                for parameter in response["Parameters"]:
                    result = self._parse_parameter_value(parameter)
                    results.append(result)

                    # 캐시에도 저장
                    self._cache.set(parameter["Name"], result)

                next_token = response.get("NextToken")
                if not next_token:
                    break

        except ClientError as e:
            logger.error(f"Get parameters by path error: {e}")
            raise

        return results

    async def get_parameter_async(
        self, name: str, decrypt: bool = True
    ) -> Dict[str, Any]:
        """비동기 단일 파라미터 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool, self.get_parameter, name, decrypt
        )

    async def batch_get_parameters_async(
        self, names: List[str], decrypt: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """비동기 배치 파라미터 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool, self.batch_get_parameters, names, decrypt
        )

    def invalidate_cache(self, name: Optional[str] = None) -> None:
        """캐시 무효화"""
        if name is not None:
            self._cache.delete(name)
        else:
            self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        with self._cache._lock:
            return {
                "enabled": self._cache.config.enabled,
                "size": len(self._cache._cache),
                "max_size": self._cache.config.max_size,
                "ttl_seconds": self._cache.config.ttl_seconds,
            }


# 편의 함수들
_global_client: Optional[ParameterStoreClient] = None


def get_client(config: Optional[ParameterConfig] = None) -> ParameterStoreClient:
    """글로벌 Parameter Store 클라이언트 인스턴스 반환"""
    global _global_client
    if _global_client is None or config is not None:
        _global_client = ParameterStoreClient(config)
    return _global_client


def get_parameter_value(name: str, json_key: Optional[str] = None) -> Any:
    """편의 함수: 파라미터 값 빠른 조회"""
    client = get_client()
    return client.get_parameter_value(name, json_key)
