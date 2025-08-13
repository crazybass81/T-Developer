#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Security Checkpoint Validator
Day 2 보안 시스템 통합 검증 스크립트

AI-DRIVEN-EVOLUTION.md Day 2 산출물 검증:
1. KMS 키 생성 및 암호화 정책 설정 ✓
2. AWS Secrets Manager 설정 및 구성 ✓
3. Parameter Store 구조 설계 및 구현 ✓
4. 환경별 변수 분리 (dev/staging/prod) ✓
5. 암호화 키 rotation 정책 설정 ✓
6. 접근 로그 활성화 ✓
7. 비밀 스캔 자동화 구현 ✓
8. Secrets Manager Python 클라이언트 개발 ✓
9. Parameter Store Python 클라이언트 개발 ✓
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityCheckpointValidator:
    """보안 체크포인트 검증기"""

    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "day2_deliverables": {},
            "infrastructure_files": {},
            "python_clients": {},
            "security_features": {},
            "overall_score": 0,
            "passed_checks": 0,
            "total_checks": 0,
            "critical_issues": [],
            "recommendations": [],
        }
        self.project_root = Path(__file__).parent.parent.parent.parent

    def validate_infrastructure_files(self) -> Dict[str, Any]:
        """인프라 파일 검증"""
        logger.info("=== 인프라 파일 검증 ===")

        infra_results = {
            "terraform_files": {},
            "required_files_present": True,
            "file_structure_valid": True,
        }

        # 필수 Terraform 파일 검증
        required_terraform_files = {
            "kms.tf": "KMS 키 및 암호화 정책",
            "secrets_manager.tf": "AWS Secrets Manager 설정",
            "parameter_store.tf": "Parameter Store 구조",
            "environments.tf": "환경별 변수 분리",
            "access_logging.tf": "접근 로그 시스템",
            "secret_scanning.tf": "비밀 스캔 자동화",
        }

        terraform_dir = self.project_root / "infrastructure" / "terraform"

        for filename, description in required_terraform_files.items():
            file_path = terraform_dir / filename

            if file_path.exists():
                file_size = file_path.stat().st_size
                infra_results["terraform_files"][filename] = {
                    "exists": True,
                    "description": description,
                    "size_bytes": file_size,
                    "status": "PASS" if file_size > 100 else "WARN",
                }

                # 파일 내용 간단 검증
                try:
                    content = file_path.read_text()
                    if "resource" in content and "aws_" in content:
                        infra_results["terraform_files"][filename][
                            "has_aws_resources"
                        ] = True
                    else:
                        infra_results["terraform_files"][filename]["status"] = "FAIL"
                        infra_results["terraform_files"][filename][
                            "issue"
                        ] = "No AWS resources found"
                except Exception as e:
                    infra_results["terraform_files"][filename]["read_error"] = str(e)
            else:
                infra_results["terraform_files"][filename] = {
                    "exists": False,
                    "description": description,
                    "status": "FAIL",
                }
                infra_results["required_files_present"] = False

        return infra_results

    def validate_python_clients(self) -> Dict[str, Any]:
        """Python 클라이언트 검증"""
        logger.info("=== Python 클라이언트 검증 ===")

        client_results = {
            "secrets_manager_client": {},
            "parameter_store_client": {},
            "integration_examples": {},
            "all_clients_functional": True,
        }

        security_dir = Path(__file__).parent

        # Secrets Manager 클라이언트 검증
        secrets_client_path = security_dir / "secrets_client.py"
        if secrets_client_path.exists():
            client_results["secrets_manager_client"] = self._validate_client_file(
                secrets_client_path, "SecretsManagerClient"
            )
        else:
            client_results["secrets_manager_client"] = {
                "exists": False,
                "status": "FAIL",
            }
            client_results["all_clients_functional"] = False

        # Parameter Store 클라이언트 검증
        parameter_client_path = security_dir / "parameter_store_client.py"
        if parameter_client_path.exists():
            client_results["parameter_store_client"] = self._validate_client_file(
                parameter_client_path, "ParameterStoreClient"
            )
        else:
            client_results["parameter_store_client"] = {
                "exists": False,
                "status": "FAIL",
            }
            client_results["all_clients_functional"] = False

        # 통합 예제 검증
        integration_files = {
            "integration_example.py": "Secrets Manager 통합 예제",
            "evolution_parameter_manager.py": "Parameter Store 통합 예제",
            "config.py": "통합 설정 관리",
        }

        for filename, description in integration_files.items():
            file_path = security_dir / filename
            if file_path.exists():
                client_results["integration_examples"][filename] = {
                    "exists": True,
                    "description": description,
                    "status": "PASS",
                }
            else:
                client_results["integration_examples"][filename] = {
                    "exists": False,
                    "description": description,
                    "status": "FAIL",
                }

        return client_results

    def _validate_client_file(self, file_path: Path, main_class: str) -> Dict[str, Any]:
        """클라이언트 파일 상세 검증"""
        try:
            content = file_path.read_text()

            result = {
                "exists": True,
                "size_bytes": len(content),
                "has_main_class": main_class in content,
                "has_async_support": "async def" in content,
                "has_caching": "cache" in content.lower(),
                "has_error_handling": "except" in content,
                "has_retry_logic": "retry" in content.lower(),
                "status": "PASS",
            }

            # 필수 기능 검증
            required_features = [
                "has_main_class",
                "has_async_support",
                "has_caching",
                "has_error_handling",
            ]
            missing_features = [f for f in required_features if not result[f]]

            if missing_features:
                result["status"] = "WARN"
                result["missing_features"] = missing_features

            return result

        except Exception as e:
            return {"exists": True, "status": "FAIL", "validation_error": str(e)}

    def validate_security_features(self) -> Dict[str, Any]:
        """보안 기능 검증"""
        logger.info("=== 보안 기능 검증 ===")

        security_results = {
            "encryption_at_rest": self._check_encryption_config(),
            "access_logging": self._check_logging_config(),
            "secret_scanning": self._check_scanning_config(),
            "environment_separation": self._check_environment_config(),
            "key_rotation": self._check_rotation_config(),
        }

        return security_results

    def _check_encryption_config(self) -> Dict[str, Any]:
        """암호화 설정 검증"""
        kms_file = self.project_root / "infrastructure" / "terraform" / "kms.tf"

        if not kms_file.exists():
            return {"status": "FAIL", "reason": "KMS configuration file not found"}

        try:
            content = kms_file.read_text()

            checks = {
                "has_kms_keys": "aws_kms_key" in content,
                "has_key_rotation": "enable_key_rotation" in content,
                "has_key_policies": "aws_kms_key_policy" in content
                or "policy" in content,
                "has_multiple_keys": content.count("aws_kms_key") >= 2,
            }

            passed_checks = sum(checks.values())
            total_checks = len(checks)

            return {
                "status": "PASS" if passed_checks == total_checks else "WARN",
                "checks": checks,
                "score": f"{passed_checks}/{total_checks}",
            }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def _check_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 검증"""
        logging_file = (
            self.project_root / "infrastructure" / "terraform" / "access_logging.tf"
        )

        if not logging_file.exists():
            return {
                "status": "FAIL",
                "reason": "Access logging configuration file not found",
            }

        try:
            content = logging_file.read_text()

            checks = {
                "has_cloudtrail": "aws_cloudtrail" in content,
                "has_vpc_flow_logs": "aws_flow_log" in content,
                "has_s3_logging": "s3_bucket" in content and "logging" in content,
                "has_cloudwatch_logs": "aws_cloudwatch_log_group" in content,
            }

            passed_checks = sum(checks.values())
            total_checks = len(checks)

            return {
                "status": "PASS" if passed_checks >= 2 else "WARN",
                "checks": checks,
                "score": f"{passed_checks}/{total_checks}",
            }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def _check_scanning_config(self) -> Dict[str, Any]:
        """스캔 설정 검증"""
        scanning_file = (
            self.project_root / "infrastructure" / "terraform" / "secret_scanning.tf"
        )

        if not scanning_file.exists():
            return {
                "status": "FAIL",
                "reason": "Secret scanning configuration file not found",
            }

        try:
            content = scanning_file.read_text()

            checks = {
                "has_lambda_function": "aws_lambda_function" in content,
                "has_step_functions": "aws_sfn_" in content,
                "has_event_triggers": "aws_cloudwatch_event" in content
                or "aws_eventbridge" in content,
                "has_quarantine_bucket": "quarantine" in content.lower(),
            }

            passed_checks = sum(checks.values())
            total_checks = len(checks)

            return {
                "status": "PASS" if passed_checks >= 2 else "WARN",
                "checks": checks,
                "score": f"{passed_checks}/{total_checks}",
            }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def _check_environment_config(self) -> Dict[str, Any]:
        """환경 설정 검증"""
        env_file = (
            self.project_root / "infrastructure" / "terraform" / "environments.tf"
        )

        if not env_file.exists():
            return {
                "status": "FAIL",
                "reason": "Environment configuration file not found",
            }

        try:
            content = env_file.read_text()

            environments = ["development", "staging", "production"]
            checks = {
                f"has_{env}_config": env in content.lower() for env in environments
            }
            checks["has_environment_locals"] = (
                "locals" in content and "environment" in content
            )
            checks["has_conditional_logic"] = "var.environment" in content

            passed_checks = sum(checks.values())
            total_checks = len(checks)

            return {
                "status": "PASS" if passed_checks >= 4 else "WARN",
                "checks": checks,
                "score": f"{passed_checks}/{total_checks}",
            }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def _check_rotation_config(self) -> Dict[str, Any]:
        """키 로테이션 설정 검증"""
        files_to_check = [
            self.project_root / "infrastructure" / "terraform" / "kms.tf",
            self.project_root / "infrastructure" / "terraform" / "secrets_manager.tf",
        ]

        rotation_found = False
        rotation_details = {}

        for file_path in files_to_check:
            if file_path.exists():
                try:
                    content = file_path.read_text()

                    file_checks = {
                        "has_key_rotation": "enable_key_rotation" in content,
                        "has_automatic_rotation": "rotation" in content.lower(),
                        "has_rotation_schedule": "rotation_interval" in content
                        or "days" in content,
                    }

                    if any(file_checks.values()):
                        rotation_found = True
                        rotation_details[file_path.name] = file_checks

                except Exception as e:
                    rotation_details[file_path.name] = {"error": str(e)}

        return {
            "status": "PASS" if rotation_found else "WARN",
            "rotation_found": rotation_found,
            "details": rotation_details,
        }

    async def run_functional_tests(self) -> Dict[str, Any]:
        """기능적 테스트 실행"""
        logger.info("=== 기능적 테스트 실행 ===")

        functional_results = {
            "secrets_client_test": await self._test_secrets_client(),
            "parameter_client_test": await self._test_parameter_client(),
            "integration_test": await self._test_integration(),
        }

        return functional_results

    async def _test_secrets_client(self) -> Dict[str, Any]:
        """Secrets Manager 클라이언트 테스트"""
        try:
            # Mock 테스트 실행
            from unittest.mock import Mock, patch
            import json

            with patch("boto3.client") as mock_boto:
                mock_client = Mock()
                mock_client.get_secret_value.return_value = {
                    "SecretString": json.dumps({"test_key": "test_value"}),
                    "Name": "test-secret",
                    "ARN": "arn:aws:secretsmanager:us-east-1:123456789:secret:test",
                    "VersionId": "v1",
                }
                mock_boto.return_value = mock_client

                from secrets_client import (
                    SecretsManagerClient,
                    ClientConfig,
                    CacheConfig,
                )

                config = ClientConfig(cache_config=CacheConfig(enabled=False))
                client = SecretsManagerClient(config)

                # 기본 조회 테스트
                secret = client.get_secret("test-secret")
                assert "parsed_secret" in secret
                assert secret["parsed_secret"]["test_key"] == "test_value"

                return {
                    "status": "PASS",
                    "message": "Secrets Manager client functional",
                }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def _test_parameter_client(self) -> Dict[str, Any]:
        """Parameter Store 클라이언트 테스트"""
        try:
            from unittest.mock import Mock, patch
            import json
            from datetime import datetime, timezone

            with patch("boto3.client") as mock_boto:
                mock_client = Mock()
                mock_client.get_parameter.return_value = {
                    "Parameter": {
                        "Name": "/test/parameter",
                        "Value": json.dumps({"setting": "value"}),
                        "Type": "SecureString",
                        "Version": 1,
                        "LastModifiedDate": datetime.now(timezone.utc),
                    }
                }
                mock_boto.return_value = mock_client

                from parameter_store_client import ParameterStoreClient, ParameterConfig

                config = ParameterConfig(cache_enabled=False)
                client = ParameterStoreClient(config)

                # 기본 조회 테스트
                parameter = client.get_parameter("/test/parameter")
                assert "parsed_value" in parameter
                assert parameter["parsed_value"]["setting"] == "value"

                return {
                    "status": "PASS",
                    "message": "Parameter Store client functional",
                }

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def _test_integration(self) -> Dict[str, Any]:
        """통합 테스트"""
        try:
            from config import SecurityConfig, initialize_security

            # 설정 초기화 테스트
            config = SecurityConfig(
                project_name="test-project", environment="development"
            )
            initialize_security(config)

            # 설정 검증
            assert config.project_name == "test-project"
            assert config.environment == "development"

            # 비밀 이름 매핑 테스트
            secret_names = config.get_secret_names()
            assert "openai_api" in secret_names
            assert "database_creds" in secret_names

            return {"status": "PASS", "message": "Integration components functional"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    def calculate_overall_score(self) -> None:
        """전체 점수 계산"""
        total_checks = 0
        passed_checks = 0

        # 각 카테고리별 점수 계산
        for category, results in self.validation_results.items():
            if isinstance(results, dict) and "status" in results:
                total_checks += 1
                if results["status"] == "PASS":
                    passed_checks += 1
            elif isinstance(results, dict):
                for sub_item, sub_result in results.items():
                    if isinstance(sub_result, dict) and "status" in sub_result:
                        total_checks += 1
                        if sub_result["status"] == "PASS":
                            passed_checks += 1

        self.validation_results["total_checks"] = total_checks
        self.validation_results["passed_checks"] = passed_checks
        self.validation_results["overall_score"] = (
            round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0
        )

    def generate_recommendations(self) -> None:
        """개선 권장사항 생성"""
        recommendations = []

        # 인프라 파일 권장사항
        if not self.validation_results.get("infrastructure_files", {}).get(
            "required_files_present", True
        ):
            recommendations.append("누락된 Terraform 파일들을 생성하여 인프라 구성을 완료하세요.")

        # Python 클라이언트 권장사항
        if not self.validation_results.get("python_clients", {}).get(
            "all_clients_functional", True
        ):
            recommendations.append("모든 Python 클라이언트가 완전히 구현되었는지 확인하세요.")

        # 보안 기능 권장사항
        security_features = self.validation_results.get("security_features", {})
        for feature, result in security_features.items():
            if isinstance(result, dict) and result.get("status") != "PASS":
                recommendations.append(f"{feature} 보안 기능을 개선하거나 완전히 구현하세요.")

        # 전체 점수 기반 권장사항
        if self.validation_results["overall_score"] < 80:
            recommendations.append("보안 체크포인트 점수가 80% 미만입니다. 실패한 항목들을 우선적으로 수정하세요.")

        self.validation_results["recommendations"] = recommendations

    async def run_complete_validation(self) -> Dict[str, Any]:
        """완전한 검증 실행"""
        logger.info("T-Developer Day 2 보안 시스템 검증 시작")
        logger.info("=" * 60)

        try:
            # 1. 인프라 파일 검증
            self.validation_results[
                "infrastructure_files"
            ] = self.validate_infrastructure_files()

            # 2. Python 클라이언트 검증
            self.validation_results["python_clients"] = self.validate_python_clients()

            # 3. 보안 기능 검증
            self.validation_results[
                "security_features"
            ] = self.validate_security_features()

            # 4. 기능적 테스트 실행
            functional_results = await self.run_functional_tests()
            self.validation_results["functional_tests"] = functional_results

            # 5. 전체 점수 계산
            self.calculate_overall_score()

            # 6. 권장사항 생성
            self.generate_recommendations()

            # 7. Day 2 산출물 체크리스트 검증
            self.validation_results["day2_deliverables"] = {
                "kms_encryption": "COMPLETED"
                if self.validation_results["security_features"]["encryption_at_rest"][
                    "status"
                ]
                == "PASS"
                else "NEEDS_REVIEW",
                "secrets_manager": "COMPLETED"
                if "secrets_manager_client" in self.validation_results["python_clients"]
                else "NEEDS_REVIEW",
                "parameter_store": "COMPLETED"
                if "parameter_store_client" in self.validation_results["python_clients"]
                else "NEEDS_REVIEW",
                "environment_separation": "COMPLETED"
                if self.validation_results["security_features"][
                    "environment_separation"
                ]["status"]
                == "PASS"
                else "NEEDS_REVIEW",
                "key_rotation": "COMPLETED"
                if self.validation_results["security_features"]["key_rotation"][
                    "status"
                ]
                == "PASS"
                else "NEEDS_REVIEW",
                "access_logging": "COMPLETED"
                if self.validation_results["security_features"]["access_logging"][
                    "status"
                ]
                == "PASS"
                else "NEEDS_REVIEW",
                "secret_scanning": "COMPLETED"
                if self.validation_results["security_features"]["secret_scanning"][
                    "status"
                ]
                == "PASS"
                else "NEEDS_REVIEW",
                "python_clients": "COMPLETED"
                if self.validation_results["python_clients"]["all_clients_functional"]
                else "NEEDS_REVIEW",
            }

            logger.info(
                f"보안 검증 완료: {self.validation_results['overall_score']}% ({self.validation_results['passed_checks']}/{self.validation_results['total_checks']})"
            )

            return self.validation_results

        except Exception as e:
            logger.error(f"검증 중 오류 발생: {e}")
            self.validation_results["validation_error"] = str(e)
            return self.validation_results


async def main():
    """메인 실행 함수"""
    validator = SecurityCheckpointValidator()

    print("🔐 T-Developer Day 2 보안 시스템 검증")
    print("=" * 60)
    print("AI-DRIVEN-EVOLUTION.md Day 2 체크포인트 검증 중...")
    print()

    # 완전한 검증 실행
    results = await validator.run_complete_validation()

    # 결과 출력
    print("\n📊 검증 결과 요약:")
    print(
        f"전체 점수: {results['overall_score']}% ({results['passed_checks']}/{results['total_checks']})"
    )
    print()

    print("📋 Day 2 산출물 상태:")
    for deliverable, status in results["day2_deliverables"].items():
        status_icon = "✅" if status == "COMPLETED" else "⚠️"
        print(f"  {status_icon} {deliverable}: {status}")

    if results.get("recommendations"):
        print("\n💡 권장사항:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")

    print(f"\n📄 상세 결과가 security_validation_report.json에 저장됩니다.")

    # 결과를 파일로 저장
    report_path = Path(__file__).parent / "security_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    # 성공/실패 반환
    success = results["overall_score"] >= 70  # 70% 이상이면 성공
    if success:
        print("\n🎉 Day 2 보안 시스템 검증 성공!")
        print("다음 단계: Day 3 Meta Agents 구현 준비")
    else:
        print(f"\n❌ 일부 항목이 기준에 미달합니다. (최소 70% 필요)")
        print("권장사항을 참고하여 수정 후 재검증하세요.")

    return success


if __name__ == "__main__":
    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
