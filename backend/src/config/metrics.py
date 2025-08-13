"""
메트릭 수집 및 모니터링
CloudWatch 메트릭 통합
"""

import time
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
import os
from contextlib import contextmanager


class MetricsCollector:
    """CloudWatch 메트릭 수집기"""

    def __init__(self):
        self.use_cloudwatch = os.getenv("USE_CLOUDWATCH", "false").lower() == "true"
        self.namespace = os.getenv("METRICS_NAMESPACE", "TDeveloper/Backend")
        self.environment = os.getenv("ENVIRONMENT", "development")

        if self.use_cloudwatch:
            try:
                self.cloudwatch = boto3.client(
                    "cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1")
                )
            except Exception as e:
                print(f"CloudWatch 초기화 실패: {e}")
                self.use_cloudwatch = False

        # 로컬 메트릭 버퍼
        self.metrics_buffer: List[Dict[str, Any]] = []

    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
    ):
        """메트릭 전송"""
        metric_data = {
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Timestamp": datetime.utcnow(),
            "Dimensions": self._format_dimensions(dimensions),
        }

        if self.use_cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace, MetricData=[metric_data]
                )
            except Exception as e:
                print(f"메트릭 전송 실패: {e}")
                self.metrics_buffer.append(metric_data)
        else:
            # 로컬 환경에서는 버퍼에 저장
            self.metrics_buffer.append(metric_data)

    def _format_dimensions(
        self, dimensions: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """차원 포맷팅"""
        formatted = [{"Name": "Environment", "Value": self.environment}]

        if dimensions:
            for key, value in dimensions.items():
                formatted.append({"Name": key, "Value": str(value)})

        return formatted

    @contextmanager
    def timer(self, metric_name: str, dimensions: Optional[Dict[str, str]] = None):
        """실행 시간 측정 컨텍스트 매니저"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000  # milliseconds
            self.put_metric(
                metric_name=f"{metric_name}_duration",
                value=duration,
                unit="Milliseconds",
                dimensions=dimensions,
            )

    def count(
        self,
        metric_name: str,
        value: int = 1,
        dimensions: Optional[Dict[str, str]] = None,
    ):
        """카운트 메트릭"""
        self.put_metric(
            metric_name=metric_name, value=value, unit="Count", dimensions=dimensions
        )

    def gauge(
        self,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]] = None,
    ):
        """게이지 메트릭"""
        self.put_metric(
            metric_name=metric_name, value=value, unit="None", dimensions=dimensions
        )

    def flush_buffer(self):
        """버퍼된 메트릭 전송"""
        if self.metrics_buffer and self.use_cloudwatch:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=self.metrics_buffer[:20],  # CloudWatch 제한
                )
                self.metrics_buffer = self.metrics_buffer[20:]
            except Exception as e:
                print(f"버퍼 플러시 실패: {e}")


# 전역 메트릭 수집기
metrics = MetricsCollector()


def track_execution_time(metric_name: str):
    """실행 시간 추적 데코레이터"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with metrics.timer(metric_name, {"function": func.__name__}):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def track_error_rate(metric_name: str):
    """에러율 추적 데코레이터"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metrics.count(
                    f"{metric_name}_success", dimensions={"function": func.__name__}
                )
                return result
            except Exception as e:
                metrics.count(
                    f"{metric_name}_error",
                    dimensions={"function": func.__name__, "error": type(e).__name__},
                )
                raise

        return wrapper

    return decorator
