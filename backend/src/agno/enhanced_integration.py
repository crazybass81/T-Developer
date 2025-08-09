"""
Enhanced Agno Framework Integration
Agno 프레임워크를 실제 파이프라인에 통합
"""

import time
from typing import Any, Dict, Optional, Type
from dataclasses import dataclass
import asyncio
import logging

from src.agno.agno_agent import AgnoAgent, AgentPerformanceMetrics
from src.agno.agent_pool import AgentPool
from src.agno.framework_manager import AgnoFrameworkManager
from src.agents.base import BaseAgent

logger = logging.getLogger(__name__)


@dataclass
class AgnoConfig:
    """Agno 통합 설정"""
    enable_pooling: bool = True
    pool_size: int = 10
    enable_metrics: bool = True
    target_creation_time_us: float = 3.0  # 목표: 3μs
    target_memory_kb: float = 6.5  # 목표: 6.5KB
    enable_auto_scaling: bool = True
    min_pool_size: int = 5
    max_pool_size: int = 100


class AgnoEnhancedIntegration:
    """Agno 프레임워크 강화 통합"""
    
    def __init__(self, config: Optional[AgnoConfig] = None):
        self.config = config or AgnoConfig()
        self.manager = AgnoFrameworkManager()
        self.pools: Dict[str, AgentPool] = {}
        self.metrics: Dict[str, AgentPerformanceMetrics] = {}
        
        logger.info("Agno Enhanced Integration initialized")
    
    def create_lightweight_agent(
        self,
        agent_class: Type[BaseAgent],
        agent_type: str,
        *args,
        **kwargs
    ) -> AgnoAgent:
        """
        경량 에이전트 생성 (Agno 최적화)
        
        목표:
        - 생성 시간: < 3μs
        - 메모리 사용: < 6.5KB
        - 재사용 가능한 풀링
        """
        start_time = time.perf_counter_ns()
        
        # 풀에서 재사용 가능한 에이전트 확인
        if self.config.enable_pooling and agent_type in self.pools:
            pool = self.pools[agent_type]
            if not pool.is_empty():
                agent = pool.get()
                # 에이전트 재설정
                agent.reset()
                
                creation_time_ns = time.perf_counter_ns() - start_time
                creation_time_us = creation_time_ns / 1000
                
                logger.debug(f"Reused agent from pool in {creation_time_us:.2f}μs")
                
                if self.config.enable_metrics:
                    self._record_metrics(agent_type, creation_time_us, reused=True)
                
                return agent
        
        # 새 에이전트 생성 (Agno 최적화)
        try:
            # Agno 프레임워크를 통한 초경량 생성
            agno_agent = self.manager.create_agent(
                agent_id=f"{agent_type}_{time.time()}",
                agent_type=agent_type,
                capabilities=['lightweight', 'fast-creation'],
                metadata={'class': agent_class.__name__}
            )
            
            # 실제 에이전트 로직 래핑
            base_agent = agent_class(*args, **kwargs)
            agno_agent.base_agent = base_agent
            
            creation_time_ns = time.perf_counter_ns() - start_time
            creation_time_us = creation_time_ns / 1000
            
            # 메모리 사용량 추정 (실제로는 더 정교한 측정 필요)
            import sys
            memory_kb = sys.getsizeof(agno_agent) / 1024
            
            logger.info(
                f"Created lightweight agent in {creation_time_us:.2f}μs, "
                f"memory: {memory_kb:.2f}KB"
            )
            
            # 성능 목표 검증
            if creation_time_us > self.config.target_creation_time_us:
                logger.warning(
                    f"Agent creation time {creation_time_us:.2f}μs exceeded "
                    f"target {self.config.target_creation_time_us}μs"
                )
            
            if memory_kb > self.config.target_memory_kb:
                logger.warning(
                    f"Agent memory {memory_kb:.2f}KB exceeded "
                    f"target {self.config.target_memory_kb}KB"
                )
            
            if self.config.enable_metrics:
                self._record_metrics(agent_type, creation_time_us, memory_kb)
            
            # 풀에 추가
            if self.config.enable_pooling:
                if agent_type not in self.pools:
                    self.pools[agent_type] = AgentPool(
                        max_size=self.config.pool_size
                    )
            
            return agno_agent
            
        except Exception as e:
            logger.error(f"Failed to create lightweight agent: {e}")
            # Fallback to regular agent
            return AgnoAgent(
                agent_id=f"{agent_type}_{time.time()}",
                agent_type=agent_type
            )
    
    async def execute_parallel_subtasks(
        self,
        tasks: list,
        agent_type: str,
        max_concurrent: int = 10
    ) -> list:
        """
        Agno 에이전트를 활용한 병렬 서브태스크 실행
        
        수천 개의 작은 태스크를 초경량 에이전트로 병렬 처리
        """
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_agent(task):
            async with semaphore:
                # 초경량 에이전트 생성
                agent = self.create_lightweight_agent(
                    BaseAgent,  # 실제로는 태스크별 적절한 클래스
                    agent_type
                )
                
                try:
                    # 태스크 실행
                    result = await agent.execute_async(task)
                    return result
                finally:
                    # 에이전트 반환 (풀로)
                    if self.config.enable_pooling and agent_type in self.pools:
                        self.pools[agent_type].put(agent)
        
        # 모든 태스크 병렬 실행
        tasks_coroutines = [execute_with_agent(task) for task in tasks]
        results = await asyncio.gather(*tasks_coroutines, return_exceptions=True)
        
        # 에러 처리
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
    
    def optimize_agent_pipeline(self, agents: list) -> list:
        """
        에이전트 파이프라인 최적화
        
        - 무거운 에이전트를 경량 버전으로 교체
        - 병렬 실행 가능한 단계 식별
        - 메모리 풀링 최적화
        """
        optimized_agents = []
        
        for agent in agents:
            # 에이전트 타입에 따른 최적화
            agent_type = agent.__class__.__name__
            
            # 경량화 가능한 에이전트 판별
            if self._can_be_lightweight(agent_type):
                # Agno 경량 에이전트로 교체
                lightweight = self.create_lightweight_agent(
                    agent.__class__,
                    agent_type
                )
                optimized_agents.append(lightweight)
                logger.info(f"Optimized {agent_type} with Agno lightweight version")
            else:
                optimized_agents.append(agent)
        
        return optimized_agents
    
    def _can_be_lightweight(self, agent_type: str) -> bool:
        """에이전트가 경량화 가능한지 판별"""
        # 경량화 가능한 에이전트 타입
        lightweight_candidates = [
            'ParserAgent',  # 구문 분석은 작은 단위로 분할 가능
            'MatchRateAgent',  # 매칭 계산은 병렬화 가능
            'SearchAgent',  # 검색은 분산 가능
            'ValidationAgent',  # 검증은 독립적 실행 가능
        ]
        
        return agent_type in lightweight_candidates
    
    def _record_metrics(
        self,
        agent_type: str,
        creation_time_us: float,
        memory_kb: float = 0,
        reused: bool = False
    ):
        """성능 메트릭 기록"""
        if agent_type not in self.metrics:
            self.metrics[agent_type] = AgentPerformanceMetrics()
        
        metrics = self.metrics[agent_type]
        metrics.creation_count += 1
        metrics.total_creation_time_us += creation_time_us
        
        if reused:
            metrics.pool_hits += 1
        else:
            metrics.pool_misses += 1
        
        if memory_kb > 0:
            metrics.memory_usage_kb = memory_kb
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        report = {
            'pools': {},
            'metrics': {},
            'summary': {
                'total_agents_created': 0,
                'average_creation_time_us': 0,
                'pool_efficiency': 0
            }
        }
        
        # 풀 상태
        for agent_type, pool in self.pools.items():
            report['pools'][agent_type] = {
                'size': len(pool.agents),
                'max_size': pool.max_size
            }
        
        # 메트릭
        total_creation_time = 0
        total_agents = 0
        total_hits = 0
        total_misses = 0
        
        for agent_type, metrics in self.metrics.items():
            avg_time = (
                metrics.total_creation_time_us / metrics.creation_count
                if metrics.creation_count > 0 else 0
            )
            
            report['metrics'][agent_type] = {
                'creation_count': metrics.creation_count,
                'average_creation_time_us': avg_time,
                'memory_usage_kb': metrics.memory_usage_kb,
                'pool_hits': metrics.pool_hits,
                'pool_misses': metrics.pool_misses,
                'pool_efficiency': (
                    metrics.pool_hits / (metrics.pool_hits + metrics.pool_misses)
                    if (metrics.pool_hits + metrics.pool_misses) > 0 else 0
                )
            }
            
            total_creation_time += metrics.total_creation_time_us
            total_agents += metrics.creation_count
            total_hits += metrics.pool_hits
            total_misses += metrics.pool_misses
        
        # 요약
        if total_agents > 0:
            report['summary']['average_creation_time_us'] = (
                total_creation_time / total_agents
            )
        
        report['summary']['total_agents_created'] = total_agents
        
        if (total_hits + total_misses) > 0:
            report['summary']['pool_efficiency'] = (
                total_hits / (total_hits + total_misses)
            )
        
        return report
    
    async def auto_scale_pools(self):
        """풀 크기 자동 조정"""
        if not self.config.enable_auto_scaling:
            return
        
        for agent_type, metrics in self.metrics.items():
            if agent_type not in self.pools:
                continue
            
            pool = self.pools[agent_type]
            efficiency = (
                metrics.pool_hits / (metrics.pool_hits + metrics.pool_misses)
                if (metrics.pool_hits + metrics.pool_misses) > 0 else 0
            )
            
            # 효율이 낮으면 풀 크기 증가
            if efficiency < 0.7 and pool.max_size < self.config.max_pool_size:
                new_size = min(pool.max_size * 2, self.config.max_pool_size)
                pool.max_size = new_size
                logger.info(f"Increased pool size for {agent_type} to {new_size}")
            
            # 효율이 매우 높으면 풀 크기 감소 (리소스 절약)
            elif efficiency > 0.95 and pool.max_size > self.config.min_pool_size:
                new_size = max(pool.max_size // 2, self.config.min_pool_size)
                pool.max_size = new_size
                logger.info(f"Decreased pool size for {agent_type} to {new_size}")


# 글로벌 인스턴스
agno_integration = AgnoEnhancedIntegration()