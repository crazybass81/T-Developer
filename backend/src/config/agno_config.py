import os
from typing import Any, Dict, List


# Agno 설정 (실제 agno 패키지가 없으므로 모의 구현)
class AgnoConfig:
    def __init__(self, **kwargs):
        self.performance = kwargs.get("performance", {})
        self.monitoring = kwargs.get("monitoring", {})
        self.tracing = kwargs.get("tracing", {})
        self.resources = kwargs.get("resources", {})


class MonitoringConfig:
    def __init__(
        self,
        enabled=True,
        endpoint=None,
        api_key=None,
        metrics_interval=30,
        custom_metrics=None,
    ):
        self.enabled = enabled
        self.endpoint = endpoint
        self.api_key = api_key
        self.metrics_interval = metrics_interval
        self.custom_metrics = custom_metrics or []


class TracingConfig:
    def __init__(self, enabled=True, sample_rate=0.1, export_endpoint=None):
        self.enabled = enabled
        self.sample_rate = sample_rate
        self.export_endpoint = export_endpoint


AGNO_CONFIG = AgnoConfig(
    # 성능 설정
    performance={
        "instantiation_target_us": 3,  # 3μs 목표
        "memory_target_kb": 6.5,  # 6.5KB 목표
        "enable_optimizations": True,
        "use_native_extensions": True,
    },
    # 모니터링 설정
    monitoring=MonitoringConfig(
        enabled=True,
        endpoint="https://agno.com/metrics",
        api_key=os.getenv("AGNO_API_KEY"),
        metrics_interval=30,
        custom_metrics=[
            "agent_instantiation_time",
            "memory_usage_per_agent",
            "total_active_agents",
        ],
    ),
    # 트레이싱 설정
    tracing=TracingConfig(
        enabled=True,
        sample_rate=0.1,  # 10% 샘플링
        export_endpoint="https://agno.com/traces",
    ),
    # 리소스 제한
    resources={
        "max_agents": 10000,
        "max_memory_per_agent_kb": 10,
        "agent_timeout_seconds": 300,
    },
)
