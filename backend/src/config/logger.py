"""
로깅 설정 모듈
프로덕션 레벨 로깅 with CloudWatch 통합
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class CloudWatchFormatter(logging.Formatter):
    """CloudWatch 호환 JSON 포맷터"""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 추가 컨텍스트가 있으면 포함
        if hasattr(record, "context"):
            log_obj["context"] = record.context

        # 에러인 경우 스택 트레이스 포함
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class Logger:
    """통합 로거 설정"""

    _instance: Optional["Logger"] = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.setup_root_logger()

    def setup_root_logger(self):
        """루트 로거 설정"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)

        # 환경에 따라 포맷 선택
        import os

        if os.getenv("ENVIRONMENT") == "production":
            console_handler.setFormatter(CloudWatchFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )

        root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """이름별 로거 가져오기"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        return self._loggers[name]

    def set_level(self, level: str):
        """로그 레벨 설정"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)

    def add_context(self, logger: logging.Logger, context: Dict[str, Any]):
        """로거에 컨텍스트 추가"""

        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs["extra"] = {"context": self.extra}
                return msg, kwargs

        return ContextAdapter(logger, context)


# 싱글톤 인스턴스
logger_manager = Logger()


def get_logger(name: str) -> logging.Logger:
    """간편한 로거 생성 함수"""
    return logger_manager.get_logger(name)
