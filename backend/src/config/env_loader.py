"""
환경변수 로더
AWS Parameter Store와 Secrets Manager에서 환경변수를 로드하여
os.environ에 설정하는 유틸리티
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.aws_config import aws_config

logger = logging.getLogger(__name__)


class EnvironmentLoader:
    """
    AWS Parameter Store와 Secrets Manager에서 환경변수를 로드
    """

    # 로드할 파라미터 목록
    PARAMETERS_TO_LOAD = [
        "PORT",
        "HOST",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "API_VERSION",
        "CORS_ORIGINS",
        "MAX_WORKERS",
        "REQUEST_TIMEOUT",
        "RATE_LIMIT",
        # Database
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        # Redis
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB",
        # S3
        "S3_BUCKET",
        "S3_REGION",
        # Agent 설정
        "AGENT_TIMEOUT",
        "AGENT_RETRY_COUNT",
        "PIPELINE_MAX_RETRIES",
    ]

    # 로드할 시크릿 목록
    SECRETS_TO_LOAD = [
        "DB_PASSWORD",
        "REDIS_PASSWORD",
        "JWT_SECRET",
        "JWT_REFRESH_SECRET",
        "ENCRYPTION_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AWS_BEDROCK_API_KEY",
        "GITHUB_TOKEN",
        "SLACK_WEBHOOK_URL",
    ]

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.loaded_count = 0
        self.failed_count = 0

    def load_all(self) -> Dict[str, Any]:
        """
        모든 환경변수를 로드하고 os.environ에 설정

        Returns:
            로드된 환경변수 딕셔너리
        """
        logger.info(f"🔄 Loading environment variables for: {self.environment}")

        loaded_vars = {}

        # 1. AWS Parameter Store에서 파라미터 로드
        logger.info("📦 Loading parameters from AWS Parameter Store...")
        for param_name in self.PARAMETERS_TO_LOAD:
            value = self._load_parameter(param_name)
            if value is not None:
                loaded_vars[param_name] = value
                self.loaded_count += 1
            else:
                self.failed_count += 1

        # 2. AWS Secrets Manager에서 시크릿 로드
        logger.info("🔐 Loading secrets from AWS Secrets Manager...")
        for secret_name in self.SECRETS_TO_LOAD:
            value = self._load_secret(secret_name)
            if value is not None:
                loaded_vars[secret_name] = value
                self.loaded_count += 1
            else:
                self.failed_count += 1

        # 3. 특수 처리가 필요한 환경변수
        self._load_special_vars(loaded_vars)

        # 4. 통계 출력
        logger.info(f"✅ Environment loading complete:")
        logger.info(f"   - Loaded: {self.loaded_count} variables")
        logger.info(f"   - Failed: {self.failed_count} variables")
        logger.info(f"   - Environment: {self.environment}")

        return loaded_vars

    def _load_parameter(self, param_name: str) -> Optional[str]:
        """
        Parameter Store에서 파라미터 로드
        """
        try:
            # AWS Parameter Store에서 가져오기
            value = aws_config.get_parameter(param_name)

            if value is not None:
                # os.environ에 설정
                os.environ[param_name] = str(value)
                logger.debug(
                    f"  ✓ {param_name}: {'***' if 'PASSWORD' in param_name else value}"
                )
                return value
            else:
                # 이미 환경변수에 있는지 확인
                existing = os.getenv(param_name)
                if existing:
                    logger.debug(f"  ⚠️ {param_name}: Using existing env var")
                    return existing
                else:
                    logger.debug(f"  ✗ {param_name}: Not found")
                    return None

        except Exception as e:
            logger.error(f"  ❌ Error loading {param_name}: {e}")
            return None

    def _load_secret(self, secret_name: str) -> Optional[str]:
        """
        Secrets Manager에서 시크릿 로드
        """
        try:
            # AWS Secrets Manager에서 가져오기
            value = aws_config.get_secret(secret_name)

            if value is not None:
                # os.environ에 설정
                os.environ[secret_name] = str(value)
                logger.debug(f"  ✓ {secret_name}: ***hidden***")
                return value
            else:
                # 이미 환경변수에 있는지 확인
                existing = os.getenv(secret_name)
                if existing:
                    logger.debug(f"  ⚠️ {secret_name}: Using existing env var")
                    return existing
                else:
                    logger.debug(f"  ✗ {secret_name}: Not found")
                    return None

        except Exception as e:
            logger.error(f"  ❌ Error loading secret {secret_name}: {e}")
            return None

    def _load_special_vars(self, loaded_vars: Dict[str, Any]):
        """
        특수 처리가 필요한 환경변수 로드
        """
        # DATABASE_URL 생성
        if "DB_PASSWORD" in loaded_vars:
            db_url = aws_config.get_database_url()
            os.environ["DATABASE_URL"] = db_url
            loaded_vars["DATABASE_URL"] = db_url
            logger.debug(f"  ✓ DATABASE_URL: postgresql://...")
            self.loaded_count += 1

        # REDIS_URL 생성
        if "REDIS_HOST" in loaded_vars or "REDIS_HOST" in os.environ:
            redis_url = aws_config.get_redis_url()
            os.environ["REDIS_URL"] = redis_url
            loaded_vars["REDIS_URL"] = redis_url
            logger.debug(f"  ✓ REDIS_URL: redis://...")
            self.loaded_count += 1

        # AWS_REGION 설정
        if "AWS_REGION" not in os.environ:
            os.environ["AWS_REGION"] = aws_config.region
            loaded_vars["AWS_REGION"] = aws_config.region
            logger.debug(f"  ✓ AWS_REGION: {aws_config.region}")
            self.loaded_count += 1

    def validate_critical_vars(self) -> bool:
        """
        중요한 환경변수가 모두 설정되었는지 검증

        Returns:
            모든 중요 변수가 설정되었으면 True
        """
        critical_vars = [
            "ENVIRONMENT",
            "AWS_REGION",
        ]

        # 프로덕션에서만 필수
        if os.getenv("ENVIRONMENT") == "production":
            critical_vars.extend(
                [
                    "DB_PASSWORD",
                    "JWT_SECRET",
                    "ENCRYPTION_KEY",
                ]
            )

        missing = []
        for var in critical_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            logger.error(
                f"❌ Critical environment variables missing: {', '.join(missing)}"
            )
            return False

        logger.info("✅ All critical environment variables are set")
        return True

    def print_loaded_vars(self, loaded_vars: Dict[str, Any]):
        """
        로드된 환경변수 출력 (디버깅용)
        """
        logger.info("\n📋 Loaded Environment Variables:")
        for key, value in sorted(loaded_vars.items()):
            if any(
                sensitive in key.upper()
                for sensitive in ["PASSWORD", "SECRET", "KEY", "TOKEN"]
            ):
                logger.info(f"  {key}: ***hidden***")
            else:
                logger.info(f"  {key}: {value}")


# 싱글톤 인스턴스
env_loader = EnvironmentLoader()


def load_environment():
    """
    환경변수 로드 헬퍼 함수
    """
    try:
        # 환경변수 로드
        loaded_vars = env_loader.load_all()

        # 중요 변수 검증
        if not env_loader.validate_critical_vars():
            logger.warning("⚠️ Some critical environment variables are missing")

        # 디버그 모드에서만 출력
        if os.getenv("DEBUG", "").lower() == "true":
            env_loader.print_loaded_vars(loaded_vars)

        return loaded_vars

    except Exception as e:
        logger.error(f"❌ Failed to load environment: {e}")
        # 개발 환경에서는 계속 진행
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.warning("⚠️ Continuing with default values in development mode")
            return {}
        else:
            raise


if __name__ == "__main__":
    # 테스트 실행
    logging.basicConfig(level=logging.INFO)

    print("\n🚀 Testing Environment Loader...")
    loaded = load_environment()
    print(f"\n📊 Total loaded: {len(loaded)} variables")
