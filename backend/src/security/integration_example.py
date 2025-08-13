#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Secrets Manager Integration Example
실제 Evolution System에서 Secrets Manager 클라이언트를 사용하는 예제

이 파일은 다음을 보여줍니다:
1. Evolution Engine에서 API 키 사용
2. Database 연결 정보 관리
3. Agent 간 통신 암호화 키 관리
4. 비동기 처리 패턴
5. 오류 처리 및 폴백 전략
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

try:
    from .secrets_client import SecretsManagerClient, get_client, get_secret_value
    from .config import get_config, initialize_security
except ImportError:
    from secrets_client import SecretsManagerClient, get_client, get_secret_value
    from config import get_config, initialize_security

# 로깅 설정
logger = logging.getLogger(__name__)


class EvolutionEngineSecrets:
    """Evolution Engine용 비밀 관리"""

    def __init__(self):
        self.config = get_config()
        self.secrets_client = get_client(self.config.to_secrets_client_config())
        self._api_keys_cache = {}

    async def get_openai_config(self) -> Dict[str, Any]:
        """OpenAI API 설정 가져오기"""
        try:
            secret_name = self.config.get_secret_names()["openai_api"]
            openai_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in openai_secret:
                return openai_secret["parsed_secret"]

            logger.warning("OpenAI secret not in expected JSON format")
            return {}

        except Exception as e:
            logger.error(f"Failed to get OpenAI config: {e}")
            return self._get_fallback_openai_config()

    async def get_anthropic_config(self) -> Dict[str, Any]:
        """Anthropic API 설정 가져오기"""
        try:
            secret_name = self.config.get_secret_names()["anthropic_api"]
            anthropic_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in anthropic_secret:
                return anthropic_secret["parsed_secret"]

            logger.warning("Anthropic secret not in expected JSON format")
            return {}

        except Exception as e:
            logger.error(f"Failed to get Anthropic config: {e}")
            return self._get_fallback_anthropic_config()

    def _get_fallback_openai_config(self) -> Dict[str, Any]:
        """OpenAI 폴백 설정 (환경변수 등)"""
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return {
                "api_key": api_key,
                "model": "gpt-4",
                "max_tokens": 4096,
                "temperature": 0.7,
            }
        return {}

    def _get_fallback_anthropic_config(self) -> Dict[str, Any]:
        """Anthropic 폴백 설정"""
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return {
                "api_key": api_key,
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4096,
                "temperature": 0.7,
            }
        return {}


class DatabaseConnectionManager:
    """데이터베이스 연결 관리"""

    def __init__(self):
        self.config = get_config()
        self.secrets_client = get_client(self.config.to_secrets_client_config())
        self._connection_string = None

    async def get_database_config(self) -> Dict[str, Any]:
        """데이터베이스 연결 설정"""
        try:
            secret_name = self.config.get_secret_names()["database_creds"]
            db_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in db_secret:
                return db_secret["parsed_secret"]

            logger.warning("Database secret not in expected JSON format")
            return {}

        except Exception as e:
            logger.error(f"Failed to get database config: {e}")
            return self._get_fallback_db_config()

    async def get_connection_string(self) -> str:
        """데이터베이스 연결 문자열 생성"""
        if self._connection_string:
            return self._connection_string

        db_config = await self.get_database_config()
        if not db_config:
            raise ConnectionError("Database configuration not available")

        # PostgreSQL 연결 문자열 구성
        self._connection_string = (
            f"postgresql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        )

        return self._connection_string

    def _get_fallback_db_config(self) -> Dict[str, Any]:
        """데이터베이스 폴백 설정"""
        import os

        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "t_developer_evolution"),
            "username": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASS", "password"),
        }

    def invalidate_connection(self):
        """연결 정보 무효화 (재연결 강제)"""
        self._connection_string = None
        secret_name = self.config.get_secret_names()["database_creds"]
        self.secrets_client.invalidate_cache(secret_name)


class AgentCommunicationSecurity:
    """Agent 간 통신 보안"""

    def __init__(self):
        self.config = get_config()
        self.secrets_client = get_client(self.config.to_secrets_client_config())
        self._encryption_key = None

    async def get_communication_key(self) -> Dict[str, Any]:
        """Agent 통신 암호화 키"""
        try:
            secret_name = self.config.get_secret_names()["agent_comm_key"]
            comm_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in comm_secret:
                return comm_secret["parsed_secret"]

            logger.warning("Agent communication secret not in expected JSON format")
            return {}

        except Exception as e:
            logger.error(f"Failed to get agent communication key: {e}")
            return self._generate_fallback_key()

    async def encrypt_message(self, message: str, recipient_agent_id: str) -> str:
        """메시지 암호화"""
        from cryptography.fernet import Fernet

        comm_config = await self.get_communication_key()
        symmetric_key = comm_config.get("symmetric_key", "").encode()

        if not symmetric_key:
            raise ValueError("No encryption key available")

        # Base64 키 생성 (Fernet 요구사항)
        import base64
        import hashlib

        key = base64.urlsafe_b64encode(hashlib.sha256(symmetric_key).digest())

        fernet = Fernet(key)
        encrypted_message = fernet.encrypt(message.encode())

        return base64.b64encode(encrypted_message).decode()

    async def decrypt_message(
        self, encrypted_message: str, sender_agent_id: str
    ) -> str:
        """메시지 복호화"""
        from cryptography.fernet import Fernet

        comm_config = await self.get_communication_key()
        symmetric_key = comm_config.get("symmetric_key", "").encode()

        if not symmetric_key:
            raise ValueError("No decryption key available")

        import base64
        import hashlib

        key = base64.urlsafe_b64encode(hashlib.sha256(symmetric_key).digest())

        fernet = Fernet(key)
        encrypted_data = base64.b64decode(encrypted_message.encode())
        decrypted_message = fernet.decrypt(encrypted_data)

        return decrypted_message.decode()

    def _generate_fallback_key(self) -> Dict[str, Any]:
        """폴백 암호화 키 생성"""
        import os
        import secrets

        # 환경변수에서 키 시도
        fallback_key = os.getenv("AGENT_COMM_KEY")
        if not fallback_key:
            # 임시 키 생성 (경고와 함께)
            fallback_key = secrets.token_urlsafe(32)
            logger.warning(
                "Using temporary agent communication key - not suitable for production"
            )

        return {
            "symmetric_key": fallback_key,
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2",
            "iterations": 100000,
        }


class SafetySystemSecurity:
    """Safety System 보안"""

    def __init__(self):
        self.config = get_config()
        self.secrets_client = get_client(self.config.to_secrets_client_config())

    async def get_emergency_stop_token(self) -> str:
        """긴급 정지 토큰"""
        try:
            secret_name = self.config.get_secret_names()["safety_secret"]
            safety_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in safety_secret:
                return safety_secret["parsed_secret"].get("emergency_stop_token", "")

            logger.warning("Safety secret not in expected JSON format")
            return ""

        except Exception as e:
            logger.error(f"Failed to get emergency stop token: {e}")
            return ""

    async def verify_safety_override_key(self, provided_key: str) -> bool:
        """안전 오버라이드 키 검증"""
        try:
            secret_name = self.config.get_secret_names()["safety_secret"]
            safety_secret = await self.secrets_client.get_secret_async(secret_name)

            if "parsed_secret" in safety_secret:
                stored_key = safety_secret["parsed_secret"].get(
                    "safety_override_key", ""
                )
                return provided_key == stored_key

            return False

        except Exception as e:
            logger.error(f"Failed to verify safety override key: {e}")
            return False


class EvolutionSystemIntegration:
    """Evolution System 통합 클래스"""

    def __init__(self):
        self.engine_secrets = EvolutionEngineSecrets()
        self.db_manager = DatabaseConnectionManager()
        self.agent_security = AgentCommunicationSecurity()
        self.safety_security = SafetySystemSecurity()

    async def initialize_system(self) -> Dict[str, Any]:
        """시스템 초기화 - 모든 필수 비밀 확인"""
        logger.info("Initializing T-Developer Evolution System...")

        initialization_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
            "errors": [],
            "warnings": [],
            "configs_loaded": [],
        }

        # OpenAI 설정 확인
        try:
            openai_config = await self.engine_secrets.get_openai_config()
            if openai_config:
                initialization_results["configs_loaded"].append("openai")
            else:
                initialization_results["warnings"].append(
                    "OpenAI configuration not available"
                )
        except Exception as e:
            initialization_results["errors"].append(f"OpenAI config error: {e}")

        # Anthropic 설정 확인
        try:
            anthropic_config = await self.engine_secrets.get_anthropic_config()
            if anthropic_config:
                initialization_results["configs_loaded"].append("anthropic")
            else:
                initialization_results["warnings"].append(
                    "Anthropic configuration not available"
                )
        except Exception as e:
            initialization_results["errors"].append(f"Anthropic config error: {e}")

        # 데이터베이스 설정 확인
        try:
            db_config = await self.db_manager.get_database_config()
            if db_config:
                initialization_results["configs_loaded"].append("database")
            else:
                initialization_results["errors"].append(
                    "Database configuration not available"
                )
        except Exception as e:
            initialization_results["errors"].append(f"Database config error: {e}")

        # Agent 통신 보안 확인
        try:
            agent_comm_key = await self.agent_security.get_communication_key()
            if agent_comm_key:
                initialization_results["configs_loaded"].append("agent_communication")
            else:
                initialization_results["errors"].append(
                    "Agent communication key not available"
                )
        except Exception as e:
            initialization_results["errors"].append(f"Agent communication error: {e}")

        # 시스템 성공 여부 결정
        if initialization_results["errors"]:
            initialization_results["success"] = False
            logger.error(
                f"System initialization failed: {initialization_results['errors']}"
            )
        else:
            logger.info(
                f"System initialized successfully. Loaded configs: {initialization_results['configs_loaded']}"
            )

        return initialization_results

    async def test_all_integrations(self) -> Dict[str, Any]:
        """모든 통합 테스트"""
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "overall_success": True,
        }

        # OpenAI 테스트
        try:
            openai_config = await self.engine_secrets.get_openai_config()
            test_results["tests"]["openai"] = {
                "success": bool(openai_config),
                "has_api_key": "api_key" in openai_config,
            }
        except Exception as e:
            test_results["tests"]["openai"] = {"success": False, "error": str(e)}
            test_results["overall_success"] = False

        # Agent 암호화 테스트
        try:
            test_message = "Test message for encryption"
            encrypted = await self.agent_security.encrypt_message(
                test_message, "test-agent"
            )
            decrypted = await self.agent_security.decrypt_message(
                encrypted, "test-agent"
            )

            test_results["tests"]["agent_encryption"] = {
                "success": decrypted == test_message,
                "roundtrip_success": True,
            }
        except Exception as e:
            test_results["tests"]["agent_encryption"] = {
                "success": False,
                "error": str(e),
            }
            test_results["overall_success"] = False

        # 안전 시스템 테스트
        try:
            emergency_token = await self.safety_security.get_emergency_stop_token()
            test_results["tests"]["safety_system"] = {
                "success": bool(emergency_token),
                "has_emergency_token": len(emergency_token) > 0,
            }
        except Exception as e:
            test_results["tests"]["safety_system"] = {"success": False, "error": str(e)}
            test_results["overall_success"] = False

        return test_results


# 편의 함수들
async def quick_setup() -> EvolutionSystemIntegration:
    """빠른 설정 및 초기화"""
    initialize_security()
    integration = EvolutionSystemIntegration()
    await integration.initialize_system()
    return integration


async def health_check() -> Dict[str, Any]:
    """시스템 상태 확인"""
    integration = EvolutionSystemIntegration()
    return await integration.test_all_integrations()


# 실행 예제
async def main():
    """메인 실행 함수"""
    logging.basicConfig(level=logging.INFO)

    try:
        # 시스템 초기화
        integration = await quick_setup()

        # 상태 확인
        health_status = await health_check()
        print("Health Check Results:")
        print(json.dumps(health_status, indent=2, default=str))

        # OpenAI API 키 테스트
        openai_config = await integration.engine_secrets.get_openai_config()
        if openai_config:
            print(f"OpenAI Model: {openai_config.get('model', 'Not specified')}")

        # 데이터베이스 연결 문자열 테스트
        try:
            conn_string = await integration.db_manager.get_connection_string()
            print(f"Database connection available: {bool(conn_string)}")
        except Exception as e:
            print(f"Database connection error: {e}")

        print("Integration test completed successfully!")

    except Exception as e:
        print(f"Integration test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
