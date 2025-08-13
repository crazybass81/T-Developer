"""
AWS Configuration Manager
AWS Secrets Manager와 Parameter Store를 통한 환경변수 관리
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError


class AWSConfigManager:
    """AWS Secrets Manager와 Parameter Store 통합 관리"""

    def __init__(self, environment: str = None):
        """
        초기화

        Args:
            environment: 환경 (development, staging, production)
        """
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # AWS 클라이언트 초기화
        self.secrets_client = boto3.client("secretsmanager", region_name=self.region)
        self.ssm_client = boto3.client("ssm", region_name=self.region)

        # 캐시 설정 (5분간 유지)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)

        # 프리픽스 설정
        self.param_prefix = f"/t-developer/{self.environment}/"
        self.secret_prefix = f"t-developer/{self.environment}/"

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        AWS Secrets Manager에서 시크릿 조회

        Args:
            secret_name: 시크릿 이름

        Returns:
            시크릿 값
        """
        cache_key = f"secret:{secret_name}"

        # 캐시 확인
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                return cached_data

        try:
            # 전체 경로 구성
            full_secret_name = f"{self.secret_prefix}{secret_name}"

            # Secrets Manager에서 조회
            response = self.secrets_client.get_secret_value(SecretId=full_secret_name)

            # JSON 파싱
            if "SecretString" in response:
                secret_data = json.loads(response["SecretString"])
            else:
                # Binary secret
                secret_data = response["SecretBinary"]

            # 캐시 저장
            self._cache[cache_key] = (secret_data, datetime.now())

            return secret_data

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"Secret not found: {full_secret_name}")
                return {}
            else:
                raise e

    @lru_cache(maxsize=128)
    def get_parameter(self, param_name: str, decrypt: bool = True) -> str:
        """
        AWS Parameter Store에서 파라미터 조회

        Args:
            param_name: 파라미터 이름
            decrypt: 암호화된 파라미터 복호화 여부

        Returns:
            파라미터 값
        """
        cache_key = f"param:{param_name}"

        # 캐시 확인
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                return cached_data

        try:
            # 전체 경로 구성
            full_param_name = f"{self.param_prefix}{param_name}"

            # Parameter Store에서 조회
            response = self.ssm_client.get_parameter(Name=full_param_name, WithDecryption=decrypt)

            value = response["Parameter"]["Value"]

            # 캐시 저장
            self._cache[cache_key] = (value, datetime.now())

            return value

        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                print(f"Parameter not found: {full_param_name}")
                return ""
            else:
                raise e

    def get_parameters_by_path(self, path: str = "") -> Dict[str, str]:
        """
        경로별 파라미터 일괄 조회

        Args:
            path: 파라미터 경로

        Returns:
            파라미터 딕셔너리
        """
        try:
            full_path = f"{self.param_prefix}{path}" if path else self.param_prefix

            paginator = self.ssm_client.get_paginator("get_parameters_by_path")
            page_iterator = paginator.paginate(Path=full_path, Recursive=True, WithDecryption=True)

            parameters = {}
            for page in page_iterator:
                for param in page["Parameters"]:
                    # 프리픽스 제거한 키 이름
                    key = param["Name"].replace(self.param_prefix, "")
                    parameters[key] = param["Value"]

            return parameters

        except ClientError as e:
            print(f"Error fetching parameters by path: {e}")
            return {}

    def get_ai_api_keys(self) -> Dict[str, str]:
        """
        AI 모델 API 키 조회

        Returns:
            API 키 딕셔너리
        """
        api_keys = {}

        # Secrets Manager에서 민감한 API 키 조회
        secret_mappings = {
            "OPENAI_API_KEY": "openai-api-key",
            "ANTHROPIC_API_KEY": "anthropic-api-key",
            "AWS_BEDROCK_ACCESS_KEY": "bedrock-access-key",
        }

        for env_var, secret_name in secret_mappings.items():
            secret = self.get_secret(secret_name)
            if secret and isinstance(secret, dict):
                # 시크릿이 딕셔너리인 경우 'key' 필드 조회
                api_keys[env_var] = secret.get("key", "")
            elif secret:
                api_keys[env_var] = secret

        return api_keys

    def get_framework_config(self) -> Dict[str, Any]:
        """
        프레임워크 설정 조회

        Returns:
            프레임워크 설정
        """
        config = {}

        # Parameter Store에서 일반 설정 조회
        param_mappings = {
            "api_url": "API_URL",
            "timeout": "TIMEOUT",
            "max_retries": "MAX_RETRIES",
            "log_level": "LOG_LEVEL",
        }

        for param_name, env_var in param_mappings.items():
            value = self.get_parameter(param_name)
            if value:
                config[env_var] = value

        return config

    async def get_secret_async(self, secret_name: str) -> Dict[str, Any]:
        """비동기 시크릿 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_secret, secret_name)

    async def get_parameter_async(self, param_name: str) -> str:
        """비동기 파라미터 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_parameter, param_name)

    def put_parameter(
        self, param_name: str, value: str, description: str = "", secure: bool = False
    ) -> bool:
        """
        Parameter Store에 파라미터 저장

        Args:
            param_name: 파라미터 이름
            value: 파라미터 값
            description: 설명
            secure: 암호화 여부

        Returns:
            성공 여부
        """
        try:
            full_param_name = f"{self.param_prefix}{param_name}"

            self.ssm_client.put_parameter(
                Name=full_param_name,
                Value=value,
                Description=description,
                Type="SecureString" if secure else "String",
                Overwrite=True,
            )

            # 캐시 무효화
            cache_key = f"param:{param_name}"
            if cache_key in self._cache:
                del self._cache[cache_key]

            return True

        except ClientError as e:
            print(f"Error putting parameter: {e}")
            return False

    def put_secret(
        self, secret_name: str, secret_value: Dict[str, Any], description: str = ""
    ) -> bool:
        """
        Secrets Manager에 시크릿 저장

        Args:
            secret_name: 시크릿 이름
            secret_value: 시크릿 값 (딕셔너리)
            description: 설명

        Returns:
            성공 여부
        """
        try:
            full_secret_name = f"{self.secret_prefix}{secret_name}"

            # 시크릿이 존재하는지 확인
            try:
                self.secrets_client.describe_secret(SecretId=full_secret_name)
                # 존재하면 업데이트
                self.secrets_client.put_secret_value(
                    SecretId=full_secret_name, SecretString=json.dumps(secret_value)
                )
            except ClientError:
                # 존재하지 않으면 생성
                self.secrets_client.create_secret(
                    Name=full_secret_name,
                    Description=description,
                    SecretString=json.dumps(secret_value),
                )

            # 캐시 무효화
            cache_key = f"secret:{secret_name}"
            if cache_key in self._cache:
                del self._cache[cache_key]

            return True

        except ClientError as e:
            print(f"Error putting secret: {e}")
            return False

    def initialize_environment(self):
        """환경변수를 AWS에서 로드하여 설정"""
        print(f"Loading configuration for environment: {self.environment}")

        # AI API 키 로드
        api_keys = self.get_ai_api_keys()
        for key, value in api_keys.items():
            if value:
                os.environ[key] = value
                print(f"✓ Loaded {key} from Secrets Manager")

        # 프레임워크 설정 로드
        config = self.get_framework_config()
        for key, value in config.items():
            if value:
                os.environ[key] = str(value)
                print(f"✓ Loaded {key} from Parameter Store")

        print("Configuration loaded successfully")


# 싱글톤 인스턴스
_config_manager = None


def get_config_manager() -> AWSConfigManager:
    """싱글톤 ConfigManager 반환"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AWSConfigManager()
    return _config_manager


# 사용 예시
if __name__ == "__main__":
    # 설정 매니저 초기화
    config_mgr = get_config_manager()

    # 환경변수 초기화
    config_mgr.initialize_environment()

    # 개별 조회 예시
    openai_key = config_mgr.get_secret("openai-api-key")
    api_url = config_mgr.get_parameter("api_url")

    print(f"OpenAI Key exists: {bool(openai_key)}")
    print(f"API URL: {api_url}")
