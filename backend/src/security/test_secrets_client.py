#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Secrets Manager Client Tests
Secrets Manager 클라이언트의 기능을 검증하는 테스트

실제 AWS 연결 테스트 및 Mock 테스트 포함
"""

import asyncio
import json
import logging
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SecurityConfig, initialize_security
from secrets_client import SecretsManagerClient, ClientConfig, CacheConfig
from integration_example import EvolutionSystemIntegration

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockSecretsManagerClient:
    """테스트용 Mock Secrets Manager Client"""

    def __init__(self):
        self.secrets = {
            "t-developer/evolution/openai-api-key": {
                "SecretString": json.dumps(
                    {
                        "api_key": "sk-test-openai-key-12345",
                        "model": "gpt-4",
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    }
                ),
                "Name": "t-developer/evolution/openai-api-key",
                "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
                "VersionId": "v1",
                "CreatedDate": datetime.utcnow(),
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/test",
            },
            "t-developer/evolution/anthropic-api-key": {
                "SecretString": json.dumps(
                    {
                        "api_key": "sk-ant-test-key-12345",
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 4096,
                        "temperature": 0.7,
                    }
                ),
                "Name": "t-developer/evolution/anthropic-api-key",
                "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
                "VersionId": "v1",
                "CreatedDate": datetime.utcnow(),
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/test",
            },
            "t-developer/database/credentials": {
                "SecretString": json.dumps(
                    {
                        "engine": "postgres",
                        "host": "test-db-host",
                        "port": 5432,
                        "dbname": "t_developer_test",
                        "username": "test_user",
                        "password": "test_password_123",
                    }
                ),
                "Name": "t-developer/database/credentials",
                "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
                "VersionId": "v1",
                "CreatedDate": datetime.utcnow(),
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/test",
            },
            "t-developer/agents/communication-key": {
                "SecretString": json.dumps(
                    {
                        "symmetric_key": "test-symmetric-key-12345",
                        "algorithm": "AES-256-GCM",
                        "key_derivation": "PBKDF2",
                        "iterations": 100000,
                    }
                ),
                "Name": "t-developer/agents/communication-key",
                "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test",
                "VersionId": "v1",
                "CreatedDate": datetime.utcnow(),
                "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/test",
            },
        }

    def get_secret_value(self, **kwargs):
        """Mock get_secret_value"""
        secret_id = kwargs.get("SecretId")
        if secret_id in self.secrets:
            return self.secrets[secret_id]
        else:
            from botocore.exceptions import ClientError

            raise ClientError(
                {"Error": {"Code": "ResourceNotFoundException"}}, "GetSecretValue"
            )

    def list_secrets(self, **kwargs):
        """Mock list_secrets"""
        filters = kwargs.get("Filters", [])
        secrets_list = []

        for name, secret in self.secrets.items():
            # 필터링 적용
            if filters:
                name_filter = next((f for f in filters if f["Key"] == "name"), None)
                if name_filter:
                    if not any(
                        name.startswith(value) for value in name_filter["Values"]
                    ):
                        continue

            secrets_list.append(
                {
                    "Name": name,
                    "ARN": secret["ARN"],
                    "Description": f"Test secret for {name}",
                    "KmsKeyId": secret.get("KmsKeyId"),
                    "RotationEnabled": False,
                    "LastChangedDate": secret["CreatedDate"],
                    "Tags": [],
                }
            )

        return {"SecretList": secrets_list}


def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n=== 기본 기능 테스트 ===")

    # Mock 클라이언트 패치
    with patch("boto3.client") as mock_boto:
        mock_client = MockSecretsManagerClient()
        mock_boto.return_value = mock_client

        # 클라이언트 설정
        config = ClientConfig(cache_config=CacheConfig(enabled=False))  # 테스트에서는 캐시 비활성화

        client = SecretsManagerClient(config)

        # OpenAI API 키 테스트
        try:
            openai_secret = client.get_secret("t-developer/evolution/openai-api-key")
            assert "parsed_secret" in openai_secret
            assert (
                openai_secret["parsed_secret"]["api_key"] == "sk-test-openai-key-12345"
            )
            print("✓ OpenAI 비밀 조회 성공")
        except Exception as e:
            print(f"✗ OpenAI 비밀 조회 실패: {e}")

        # 비밀 JSON 값 추출 테스트
        try:
            api_key = client.get_secret_value(
                "t-developer/evolution/openai-api-key", "api_key"
            )
            assert api_key == "sk-test-openai-key-12345"
            print("✓ 비밀 값 추출 성공")
        except Exception as e:
            print(f"✗ 비밀 값 추출 실패: {e}")

        # 존재하지 않는 비밀 테스트
        try:
            client.get_secret("nonexistent-secret")
            print("✗ 존재하지 않는 비밀 테스트 실패 - 예외가 발생해야 함")
        except Exception:
            print("✓ 존재하지 않는 비밀 예외 처리 성공")

        # 비밀 목록 조회 테스트
        try:
            secrets_list = client.list_secrets("t-developer/")
            assert len(secrets_list) > 0
            print(f"✓ 비밀 목록 조회 성공 ({len(secrets_list)}개)")
        except Exception as e:
            print(f"✗ 비밀 목록 조회 실패: {e}")


def test_cache_functionality():
    """캐시 기능 테스트"""
    print("\n=== 캐시 기능 테스트 ===")

    with patch("boto3.client") as mock_boto:
        mock_client = MockSecretsManagerClient()
        mock_boto.return_value = mock_client

        # 캐시 활성화 설정
        config = ClientConfig(
            cache_config=CacheConfig(enabled=True, ttl_seconds=60, max_size=10)
        )

        client = SecretsManagerClient(config)

        # 첫 번째 호출 (AWS에서 가져옴)
        secret1 = client.get_secret("t-developer/evolution/openai-api-key")

        # 두 번째 호출 (캐시에서 가져옴)
        secret2 = client.get_secret("t-developer/evolution/openai-api-key")

        assert (
            secret1["parsed_secret"]["api_key"] == secret2["parsed_secret"]["api_key"]
        )
        print("✓ 캐시 기능 동작 확인")

        # 캐시 무효화 테스트
        client.invalidate_cache("t-developer/evolution/openai-api-key")
        secret3 = client.get_secret("t-developer/evolution/openai-api-key")

        assert secret3["parsed_secret"]["api_key"] == "sk-test-openai-key-12345"
        print("✓ 캐시 무효화 기능 확인")


async def test_async_functionality():
    """비동기 기능 테스트"""
    print("\n=== 비동기 기능 테스트 ===")

    with patch("boto3.client") as mock_boto:
        mock_client = MockSecretsManagerClient()
        mock_boto.return_value = mock_client

        config = ClientConfig(cache_config=CacheConfig(enabled=False))
        client = SecretsManagerClient(config)

        # 비동기 비밀 조회
        try:
            openai_secret = await client.get_secret_async(
                "t-developer/evolution/openai-api-key"
            )
            assert "parsed_secret" in openai_secret
            print("✓ 비동기 비밀 조회 성공")
        except Exception as e:
            print(f"✗ 비동기 비밀 조회 실패: {e}")

        # 배치 조회 테스트
        try:
            secret_names = [
                "t-developer/evolution/openai-api-key",
                "t-developer/evolution/anthropic-api-key",
                "t-developer/database/credentials",
            ]

            batch_results = client.batch_get_secrets(secret_names)
            assert len(batch_results) == 3
            assert all(result is not None for result in batch_results.values())
            print("✓ 배치 비밀 조회 성공")
        except Exception as e:
            print(f"✗ 배치 비밀 조회 실패: {e}")


def test_integration():
    """통합 테스트"""
    print("\n=== 통합 테스트 ===")

    with patch("boto3.client") as mock_boto:
        mock_client = MockSecretsManagerClient()
        mock_boto.return_value = mock_client

        try:
            # 보안 설정 초기화
            config = SecurityConfig(
                project_name="t-developer",
                environment="development",
                secrets_cache_enabled=False,
            )
            initialize_security(config)

            # Evolution System Integration 테스트
            integration = EvolutionSystemIntegration()

            # API 인증정보 테스트
            engine_secrets = integration.engine_secrets

            # 동기 방식으로 테스트 (간단히)
            client = engine_secrets.secrets_client

            # OpenAI 설정 테스트
            openai_config = client.get_secret_json(
                "t-developer/evolution/openai-api-key"
            )
            assert openai_config["api_key"] == "sk-test-openai-key-12345"
            print("✓ OpenAI 통합 테스트 성공")

            # 데이터베이스 설정 테스트
            db_config = client.get_secret_json("t-developer/database/credentials")
            assert db_config["host"] == "test-db-host"
            print("✓ 데이터베이스 통합 테스트 성공")

            # Agent 통신 키 테스트
            agent_config = client.get_secret_json(
                "t-developer/agents/communication-key"
            )
            assert agent_config["symmetric_key"] == "test-symmetric-key-12345"
            print("✓ Agent 통신 키 통합 테스트 성공")

        except Exception as e:
            print(f"✗ 통합 테스트 실패: {e}")


async def test_real_aws_connection():
    """실제 AWS 연결 테스트 (선택적)"""
    print("\n=== 실제 AWS 연결 테스트 ===")

    # 환경변수 확인
    if not os.getenv("TEST_REAL_AWS", "").lower() == "true":
        print("실제 AWS 테스트 건너뛰기 (TEST_REAL_AWS=true 설정시 실행)")
        return

    try:
        config = ClientConfig(cache_config=CacheConfig(enabled=False))
        client = SecretsManagerClient(config)

        # 실제 비밀 목록 조회 시도
        secrets_list = client.list_secrets("t-developer/")
        print(f"✓ 실제 AWS 연결 성공 - {len(secrets_list)}개 비밀 발견")

        # 각 비밀의 기본 정보만 출력 (보안상)
        for secret in secrets_list:
            print(
                f"  - {secret['name']}: {secret.get('description', 'No description')}"
            )

    except Exception as e:
        print(f"✗ 실제 AWS 연결 실패: {e}")
        print("AWS 자격증명과 권한을 확인하세요.")


def test_error_handling():
    """오류 처리 테스트"""
    print("\n=== 오류 처리 테스트 ===")

    with patch("boto3.client") as mock_boto:
        # 오류를 발생시키는 Mock 클라이언트
        mock_client = Mock()

        from botocore.exceptions import ClientError

        mock_client.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "GetSecretValue"
        )

        mock_boto.return_value = mock_client

        config = ClientConfig(cache_config=CacheConfig(enabled=False))
        client = SecretsManagerClient(config)

        # AccessDeniedException 테스트
        try:
            client.get_secret("test-secret")
            print("✗ AccessDeniedException 테스트 실패")
        except Exception as e:
            if "Access denied" in str(e):
                print("✓ AccessDeniedException 처리 성공")
            else:
                print(f"✗ 예상과 다른 예외: {e}")


async def run_all_tests():
    """모든 테스트 실행"""
    print("T-Developer Secrets Manager Client 테스트 시작")
    print("=" * 60)

    try:
        # 기본 기능 테스트
        test_basic_functionality()

        # 캐시 기능 테스트
        test_cache_functionality()

        # 비동기 기능 테스트
        await test_async_functionality()

        # 통합 테스트
        test_integration()

        # 오류 처리 테스트
        test_error_handling()

        # 실제 AWS 연결 테스트 (선택적)
        await test_real_aws_connection()

        print("\n" + "=" * 60)
        print("✓ 모든 테스트 완료!")

    except Exception as e:
        print(f"\n✗ 테스트 실행 중 오류 발생: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
