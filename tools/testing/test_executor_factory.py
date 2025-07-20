"""
TestExecutorFactory - 테스트 실행 모듈 팩토리

로컬 또는 Lambda 기반 테스트 실행 모듈을 생성하는 팩토리 클래스입니다.
"""
import os
import logging
from typing import Any

from config import settings
from agents.q_developer.agent import QDeveloperAgent
from tools.testing.lambda_test_executor import LambdaTestExecutor

# 로깅 설정
logger = logging.getLogger(__name__)

class TestExecutorFactory:
    """
    테스트 실행 모듈 팩토리
    
    로컬 또는 Lambda 기반 테스트 실행 모듈을 생성하는 팩토리 클래스입니다.
    """
    
    @staticmethod
    def create_executor() -> Any:
        """
        테스트 실행 모듈 생성
        
        Returns:
            테스트 실행 모듈 인스턴스
        """
        # 환경 변수에서 설정 확인
        use_lambda = os.environ.get("USE_LAMBDA_TEST_EXECUTOR", "").lower() in ["true", "1", "yes"]
        
        # Lambda 사용 여부에 따라 적절한 구현체 반환
        if use_lambda:
            logger.info("Using Lambda-based test executor")
            return LambdaTestExecutor()
        else:
            logger.info("Using local test executor")
            return QDeveloperAgent()