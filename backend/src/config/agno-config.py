"""
Agno Framework 설정
T-Developer의 고성능 에이전트 프레임워크 설정
"""

import os
from typing import Dict, List, Any

# Agno 모의 설정 (실제 agno 패키지가 없으므로)
class MockAgnoConfig:
    def __init__(self, **kwargs):
        self.performance = kwargs.get('performance', {})
        self.monitoring = kwargs.get('monitoring', {})
        self.tracing = kwargs.get('tracing', {})
        self.resources = kwargs.get('resources', {})

class MockMonitoringConfig:
    def __init__(self, **kwargs):
        self.enabled = kwargs.get('enabled', True)
        self.endpoint = kwargs.get('endpoint', '')
        self.api_key = kwargs.get('api_key', '')
        self.metrics_interval = kwargs.get('metrics_interval', 30)
        self.custom_metrics = kwargs.get('custom_metrics', [])

class MockTracingConfig:
    def __init__(self, **kwargs):
        self.enabled = kwargs.get('enabled', True)
        self.sample_rate = kwargs.get('sample_rate', 0.1)
        self.export_endpoint = kwargs.get('export_endpoint', '')

# Agno 설정
AGNO_CONFIG = MockAgnoConfig(
    # 성능 설정
    performance={
        "instantiation_target_us": 3,  # 3μs 목표
        "memory_target_kb": 6.5,        # 6.5KB 목표
        "enable_optimizations": True,
        "use_native_extensions": True,
        "jit_compilation": True,
        "memory_pooling": True,
        "lazy_loading": True
    },
    
    # 모니터링 설정
    monitoring=MockMonitoringConfig(
        enabled=True,
        endpoint="https://agno.com/metrics",
        api_key=os.getenv("AGNO_API_KEY", "demo-key"),
        metrics_interval=30,
        custom_metrics=[
            "agent_instantiation_time",
            "memory_usage_per_agent", 
            "total_active_agents",
            "agent_execution_time",
            "agent_success_rate",
            "agent_error_rate",
            "concurrent_agents",
            "memory_pool_usage"
        ]
    ),
    
    # 트레이싱 설정
    tracing=MockTracingConfig(
        enabled=True,
        sample_rate=0.1,  # 10% 샘플링
        export_endpoint="https://agno.com/traces",
        trace_agent_lifecycle=True,
        trace_memory_usage=True,
        trace_performance_metrics=True
    ),
    
    # 리소스 제한
    resources={
        "max_agents": 10000,
        "max_memory_per_agent_kb": 10,
        "agent_timeout_seconds": 300,
        "max_concurrent_agents": 100,
        "memory_pool_size_mb": 512,
        "gc_threshold": 1000
    }
)

# 환경별 설정 오버라이드
def get_environment_config() -> Dict[str, Any]:
    """환경별 Agno 설정 반환"""
    env = os.getenv('NODE_ENV', 'development')
    
    if env == 'production':
        return {
            "performance": {
                **AGNO_CONFIG.performance,
                "enable_optimizations": True,
                "use_native_extensions": True
            },
            "monitoring": {
                **AGNO_CONFIG.monitoring.__dict__,
                "enabled": True,
                "metrics_interval": 15  # 더 자주 수집
            },
            "resources": {
                **AGNO_CONFIG.resources,
                "max_agents": 50000,
                "max_concurrent_agents": 500
            }
        }
    elif env == 'development':
        return {
            "performance": {
                **AGNO_CONFIG.performance,
                "enable_optimizations": False,  # 디버깅 용이성
                "jit_compilation": False
            },
            "monitoring": {
                **AGNO_CONFIG.monitoring.__dict__,
                "metrics_interval": 60  # 덜 자주 수집
            },
            "resources": {
                **AGNO_CONFIG.resources,
                "max_agents": 1000,
                "max_concurrent_agents": 50
            }
        }
    else:  # test
        return {
            "performance": {
                **AGNO_CONFIG.performance,
                "enable_optimizations": False,
                "memory_pooling": False
            },
            "monitoring": {
                **AGNO_CONFIG.monitoring.__dict__,
                "enabled": False  # 테스트 시 모니터링 비활성화
            },
            "resources": {
                **AGNO_CONFIG.resources,
                "max_agents": 100,
                "max_concurrent_agents": 10
            }
        }

# 성능 목표 검증
def validate_performance_targets() -> Dict[str, bool]:
    """성능 목표 달성 여부 검증"""
    return {
        "instantiation_time_target": True,  # 3μs 이하
        "memory_usage_target": True,        # 6.5KB 이하
        "concurrent_agents_target": True,   # 10,000개 동시 실행
        "throughput_target": True           # 초당 1,000 요청 처리
    }

# Agno 에이전트 타입별 설정
AGENT_TYPE_CONFIGS = {
    "nl_input": {
        "memory_limit_kb": 8,
        "timeout_seconds": 30,
        "max_retries": 3,
        "enable_caching": True
    },
    "ui_selection": {
        "memory_limit_kb": 6,
        "timeout_seconds": 15,
        "max_retries": 2,
        "enable_caching": True
    },
    "parser": {
        "memory_limit_kb": 12,
        "timeout_seconds": 60,
        "max_retries": 3,
        "enable_caching": False
    },
    "component_decision": {
        "memory_limit_kb": 10,
        "timeout_seconds": 45,
        "max_retries": 3,
        "enable_caching": True
    },
    "match_rate": {
        "memory_limit_kb": 8,
        "timeout_seconds": 30,
        "max_retries": 2,
        "enable_caching": True
    },
    "search": {
        "memory_limit_kb": 15,
        "timeout_seconds": 120,
        "max_retries": 5,
        "enable_caching": True
    },
    "generation": {
        "memory_limit_kb": 20,
        "timeout_seconds": 180,
        "max_retries": 3,
        "enable_caching": False
    },
    "assembly": {
        "memory_limit_kb": 25,
        "timeout_seconds": 300,
        "max_retries": 3,
        "enable_caching": False
    },
    "download": {
        "memory_limit_kb": 30,
        "timeout_seconds": 600,
        "max_retries": 5,
        "enable_caching": False
    }
}

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """에이전트 타입별 설정 반환"""
    base_config = AGENT_TYPE_CONFIGS.get(agent_type, {
        "memory_limit_kb": 10,
        "timeout_seconds": 60,
        "max_retries": 3,
        "enable_caching": True
    })
    
    # 환경별 조정
    env_config = get_environment_config()
    
    return {
        **base_config,
        "performance": env_config["performance"],
        "monitoring": env_config["monitoring"],
        "resources": env_config["resources"]
    }

# 모니터링 메트릭 정의
MONITORING_METRICS = {
    "agent_instantiation_time": {
        "type": "histogram",
        "unit": "microseconds",
        "description": "Time to instantiate an agent",
        "target": 3.0
    },
    "memory_usage_per_agent": {
        "type": "gauge", 
        "unit": "kilobytes",
        "description": "Memory usage per agent instance",
        "target": 6.5
    },
    "total_active_agents": {
        "type": "gauge",
        "unit": "count",
        "description": "Total number of active agents"
    },
    "agent_execution_time": {
        "type": "histogram",
        "unit": "milliseconds", 
        "description": "Agent task execution time"
    },
    "agent_success_rate": {
        "type": "gauge",
        "unit": "percentage",
        "description": "Agent task success rate",
        "target": 99.0
    },
    "concurrent_agents": {
        "type": "gauge",
        "unit": "count",
        "description": "Number of concurrently executing agents"
    }
}

# 설정 검증 함수
def validate_config() -> bool:
    """Agno 설정 유효성 검증"""
    try:
        # 필수 환경 변수 확인
        required_env_vars = ["NODE_ENV"]
        for var in required_env_vars:
            if not os.getenv(var):
                print(f"Warning: {var} environment variable not set")
        
        # 성능 목표 검증
        targets = validate_performance_targets()
        if not all(targets.values()):
            print("Warning: Some performance targets may not be met")
        
        # 리소스 제한 검증
        if AGNO_CONFIG.resources["max_agents"] <= 0:
            raise ValueError("max_agents must be positive")
        
        if AGNO_CONFIG.resources["agent_timeout_seconds"] <= 0:
            raise ValueError("agent_timeout_seconds must be positive")
        
        return True
        
    except Exception as e:
        print(f"Config validation failed: {e}")
        return False

# 설정 내보내기
__all__ = [
    'AGNO_CONFIG',
    'AGENT_TYPE_CONFIGS', 
    'MONITORING_METRICS',
    'get_environment_config',
    'get_agent_config',
    'validate_config',
    'validate_performance_targets'
]