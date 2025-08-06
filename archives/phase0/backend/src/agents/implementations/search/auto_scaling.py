# backend/src/agents/implementations/search/auto_scaling.py
from typing import Dict, List, Any, Optional
import asyncio
import time
from dataclasses import dataclass
from collections import deque
import numpy as np

@dataclass
class ScalingMetrics:
    cpu_usage: float
    memory_usage: float
    query_rate: float
    response_time: float
    error_rate: float
    queue_depth: int

@dataclass
class ScalingDecision:
    action: str  # scale_up, scale_down, maintain
    target_instances: int
    confidence: float
    reasoning: str

class AutoScalingManager:
    """자동 스케일링 관리자"""

    def __init__(self):
        self.metrics_history = deque(maxlen=100)
        self.scaling_cooldown = 300  # 5분
        self.last_scaling_time = 0
        
        # 스케일링 임계값
        self.scale_up_thresholds = {
            'cpu_usage': 0.7,
            'memory_usage': 0.8,
            'response_time': 200,  # ms
            'error_rate': 0.05
        }
        
        self.scale_down_thresholds = {
            'cpu_usage': 0.3,
            'memory_usage': 0.4,
            'response_time': 50,  # ms
            'error_rate': 0.01
        }

    async def evaluate_scaling(
        self,
        current_metrics: ScalingMetrics,
        current_instances: int
    ) -> ScalingDecision:
        """스케일링 평가"""

        # 메트릭 히스토리에 추가
        self.metrics_history.append(current_metrics)

        # 쿨다운 체크
        if time.time() - self.last_scaling_time < self.scaling_cooldown:
            return ScalingDecision(
                action="maintain",
                target_instances=current_instances,
                confidence=1.0,
                reasoning="Scaling cooldown active"
            )

        # 트렌드 분석
        trend_analysis = self._analyze_trends()

        # 스케일링 결정
        decision = self._make_scaling_decision(
            current_metrics,
            current_instances,
            trend_analysis
        )

        return decision

    def _analyze_trends(self) -> Dict[str, float]:
        """메트릭 트렌드 분석"""

        if len(self.metrics_history) < 10:
            return {'trend': 0.0, 'volatility': 0.0}

        recent_metrics = list(self.metrics_history)[-10:]
        
        # CPU 사용률 트렌드
        cpu_values = [m.cpu_usage for m in recent_metrics]
        cpu_trend = np.polyfit(range(len(cpu_values)), cpu_values, 1)[0]

        # 응답 시간 트렌드
        response_values = [m.response_time for m in recent_metrics]
        response_trend = np.polyfit(range(len(response_values)), response_values, 1)[0]

        # 쿼리율 트렌드
        query_values = [m.query_rate for m in recent_metrics]
        query_trend = np.polyfit(range(len(query_values)), query_values, 1)[0]

        # 변동성 계산
        volatility = np.std([m.cpu_usage for m in recent_metrics])

        return {
            'cpu_trend': cpu_trend,
            'response_trend': response_trend,
            'query_trend': query_trend,
            'volatility': volatility
        }

    def _make_scaling_decision(
        self,
        metrics: ScalingMetrics,
        current_instances: int,
        trends: Dict[str, float]
    ) -> ScalingDecision:
        """스케일링 결정"""

        scale_up_score = 0
        scale_down_score = 0

        # 스케일 업 조건 체크
        if metrics.cpu_usage > self.scale_up_thresholds['cpu_usage']:
            scale_up_score += 2
        if metrics.memory_usage > self.scale_up_thresholds['memory_usage']:
            scale_up_score += 2
        if metrics.response_time > self.scale_up_thresholds['response_time']:
            scale_up_score += 3
        if metrics.error_rate > self.scale_up_thresholds['error_rate']:
            scale_up_score += 3

        # 트렌드 고려
        if trends['cpu_trend'] > 0.05:  # 증가 트렌드
            scale_up_score += 1
        if trends['response_trend'] > 10:  # 응답시간 증가
            scale_up_score += 2

        # 스케일 다운 조건 체크
        if metrics.cpu_usage < self.scale_down_thresholds['cpu_usage']:
            scale_down_score += 1
        if metrics.memory_usage < self.scale_down_thresholds['memory_usage']:
            scale_down_score += 1
        if metrics.response_time < self.scale_down_thresholds['response_time']:
            scale_down_score += 1

        # 결정
        if scale_up_score >= 4:
            target_instances = min(current_instances * 2, 20)  # 최대 20개
            return ScalingDecision(
                action="scale_up",
                target_instances=target_instances,
                confidence=min(1.0, scale_up_score / 10),
                reasoning=f"High load detected (score: {scale_up_score})"
            )
        elif scale_down_score >= 3 and current_instances > 1:
            target_instances = max(current_instances // 2, 1)  # 최소 1개
            return ScalingDecision(
                action="scale_down",
                target_instances=target_instances,
                confidence=min(1.0, scale_down_score / 5),
                reasoning=f"Low load detected (score: {scale_down_score})"
            )
        else:
            return ScalingDecision(
                action="maintain",
                target_instances=current_instances,
                confidence=0.8,
                reasoning="Metrics within normal range"
            )

class LoadBalancer:
    """로드 밸런서"""

    def __init__(self):
        self.instances = {}
        self.health_checker = HealthChecker()
        self.routing_algorithm = "weighted_round_robin"

    async def distribute_load(
        self,
        request: Dict[str, Any],
        available_instances: List[str]
    ) -> str:
        """로드 분산"""

        # 헬스 체크
        healthy_instances = await self.health_checker.get_healthy_instances(
            available_instances
        )

        if not healthy_instances:
            raise Exception("No healthy instances available")

        # 라우팅 알고리즘에 따라 인스턴스 선택
        if self.routing_algorithm == "round_robin":
            return self._round_robin_select(healthy_instances)
        elif self.routing_algorithm == "weighted_round_robin":
            return self._weighted_round_robin_select(healthy_instances)
        elif self.routing_algorithm == "least_connections":
            return self._least_connections_select(healthy_instances)
        else:
            return healthy_instances[0]

    def _weighted_round_robin_select(
        self,
        instances: List[str]
    ) -> str:
        """가중 라운드 로빈 선택"""

        # 인스턴스별 가중치 계산 (CPU 사용률 역수)
        weights = {}
        for instance in instances:
            cpu_usage = self.instances.get(instance, {}).get('cpu_usage', 0.5)
            weights[instance] = 1.0 / (cpu_usage + 0.1)  # 0으로 나누기 방지

        # 가중치 기반 선택
        total_weight = sum(weights.values())
        import random
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for instance, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return instance
        
        return instances[0]  # 폴백

class HealthChecker:
    """헬스 체커"""

    def __init__(self):
        self.health_cache = {}
        self.cache_ttl = 30  # 30초

    async def get_healthy_instances(
        self,
        instances: List[str]
    ) -> List[str]:
        """건강한 인스턴스 목록 반환"""

        healthy = []
        
        for instance in instances:
            if await self.is_healthy(instance):
                healthy.append(instance)

        return healthy

    async def is_healthy(self, instance: str) -> bool:
        """인스턴스 헬스 체크"""

        # 캐시 확인
        if instance in self.health_cache:
            cached_time, is_healthy = self.health_cache[instance]
            if time.time() - cached_time < self.cache_ttl:
                return is_healthy

        # 실제 헬스 체크
        try:
            # HTTP 헬스 체크 시뮬레이션
            health_status = await self._perform_health_check(instance)
            
            # 캐시 업데이트
            self.health_cache[instance] = (time.time(), health_status)
            
            return health_status
        except Exception:
            self.health_cache[instance] = (time.time(), False)
            return False

    async def _perform_health_check(self, instance: str) -> bool:
        """실제 헬스 체크 수행"""
        
        # 실제 구현에서는 HTTP 요청을 보냄
        # 여기서는 시뮬레이션
        import random
        await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
        return random.random() > 0.1  # 90% 확률로 건강

class CircuitBreaker:
    """서킷 브레이커"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        """서킷 브레이커를 통한 함수 호출"""

        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e