"""
SlackNotifierFactory - Slack 알림 모듈 팩토리

로컬 또는 Lambda 기반 Slack 알림 모듈을 생성하는 팩토리 클래스입니다.
"""
import os
import logging
from typing import Union

from config import settings
from slack.notifier import SlackNotifier
from slack.lambda_notifier import LambdaSlackNotifier

# 로깅 설정
logger = logging.getLogger(__name__)

class SlackNotifierFactory:
    """
    Slack 알림 모듈 팩토리
    
    로컬 또는 Lambda 기반 Slack 알림 모듈을 생성하는 팩토리 클래스입니다.
    """
    
    @staticmethod
    def create_notifier() -> Union[SlackNotifier, LambdaSlackNotifier]:
        """
        Slack 알림 모듈 생성
        
        Returns:
            SlackNotifier 또는 LambdaSlackNotifier 인스턴스
        """
        # 환경 변수에서 설정 확인
        use_lambda = os.environ.get("USE_LAMBDA_NOTIFIER", "").lower() in ["true", "1", "yes"]
        
        # Lambda 사용 여부에 따라 적절한 구현체 반환
        if use_lambda:
            logger.info("Using Lambda-based Slack notifier")
            return LambdaSlackNotifier()
        else:
            logger.info("Using local Slack notifier")
            return SlackNotifier()