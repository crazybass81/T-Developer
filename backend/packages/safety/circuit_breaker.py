"""Circuit Breaker pattern implementation.

연쇄 실패를 방지하고 시스템을 보호하는 Circuit Breaker 패턴 구현입니다.
"""

from __future__ import annotations

import asyncio
import time
import logging
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit Breaker 상태."""
    
    CLOSED = "closed"  # 정상 작동 (요청 통과)
    OPEN = "open"      # 차단 (요청 거부)
    HALF_OPEN = "half_open"  # 테스트 중 (일부 요청만 통과)


@dataclass
class CircuitBreakerConfig:
    """Circuit Breaker 설정."""
    
    failure_threshold: int = 5  # 실패 임계값
    recovery_timeout: float = 60.0  # 복구 대기 시간 (초)
    success_threshold: int = 2  # HALF_OPEN에서 CLOSED로 전환하기 위한 성공 횟수
    half_open_max_calls: int = 3  # HALF_OPEN 상태에서 허용할 최대 호출 수
    error_rate_threshold: float = 0.5  # 에러율 임계값 (0.0 ~ 1.0)
    window_size: int = 10  # 에러율 계산을 위한 윈도우 크기


@dataclass
class CircuitBreakerStats:
    """Circuit Breaker 통계."""
    
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    recent_calls: list = field(default_factory=list)  # 최근 호출 결과 (True/False)


class CircuitBreaker:
    """Circuit Breaker 구현.
    
    연쇄 실패를 방지하고 시스템을 보호합니다.
    
    상태 전환:
    - CLOSED → OPEN: 실패가 임계값을 초과하면
    - OPEN → HALF_OPEN: 복구 시간이 지나면
    - HALF_OPEN → CLOSED: 테스트 성공하면
    - HALF_OPEN → OPEN: 테스트 실패하면
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """Circuit Breaker 초기화.
        
        Args:
            name: Circuit Breaker 이름
            config: 설정 (없으면 기본값 사용)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        self._half_open_calls = 0
        
        logger.info(f"CircuitBreaker '{name}' initialized (state: {self.state.value})")
    
    async def call(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """Circuit Breaker를 통해 함수 호출.
        
        Args:
            func: 호출할 함수
            *args: 위치 인자
            **kwargs: 키워드 인자
            
        Returns:
            함수 실행 결과
            
        Raises:
            CircuitBreakerOpenError: Circuit이 OPEN 상태일 때
            원본 함수의 예외: 함수 실행 중 발생한 예외
        """
        async with self._lock:
            # 상태 확인 및 자동 전환
            self._check_state_transition()
            
            # OPEN 상태: 요청 거부
            if self.state == CircuitState.OPEN:
                logger.warning(f"CircuitBreaker '{self.name}' is OPEN - rejecting call")
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN"
                )
            
            # HALF_OPEN 상태: 제한적 허용
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    logger.warning(
                        f"CircuitBreaker '{self.name}' HALF_OPEN limit reached"
                    )
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' HALF_OPEN limit reached"
                    )
                self._half_open_calls += 1
        
        # 함수 실행
        try:
            # 비동기 함수 처리
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # 동기 함수를 비동기로 실행
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            
            # 성공 기록
            await self._record_success()
            return result
            
        except Exception as e:
            # 실패 기록
            await self._record_failure()
            raise e
    
    async def _record_success(self) -> None:
        """성공 기록."""
        async with self._lock:
            self.stats.total_calls += 1
            self.stats.successful_calls += 1
            self.stats.consecutive_successes += 1
            self.stats.consecutive_failures = 0
            self.stats.last_success_time = time.time()
            
            # 최근 호출 기록
            self.stats.recent_calls.append(True)
            if len(self.stats.recent_calls) > self.config.window_size:
                self.stats.recent_calls.pop(0)
            
            # HALF_OPEN → CLOSED 전환 확인
            if self.state == CircuitState.HALF_OPEN:
                if self.stats.consecutive_successes >= self.config.success_threshold:
                    logger.info(
                        f"CircuitBreaker '{self.name}': HALF_OPEN → CLOSED"
                    )
                    self.state = CircuitState.CLOSED
                    self._half_open_calls = 0
                    self.stats.consecutive_failures = 0
                # HALF_OPEN에서 max_calls에 도달했는데 아직 CLOSED로 전환 안 됨
                elif self._half_open_calls >= self.config.half_open_max_calls:
                    # 최대 호출 수에 도달했지만 success_threshold를 못 채웠으면 OPEN으로
                    logger.warning(
                        f"CircuitBreaker '{self.name}': HALF_OPEN → OPEN (max calls reached)"
                    )
                    self.state = CircuitState.OPEN
                    self._half_open_calls = 0
    
    async def _record_failure(self) -> None:
        """실패 기록."""
        async with self._lock:
            self.stats.total_calls += 1
            self.stats.failed_calls += 1
            self.stats.consecutive_failures += 1
            self.stats.consecutive_successes = 0
            self.stats.last_failure_time = time.time()
            
            # 최근 호출 기록
            self.stats.recent_calls.append(False)
            if len(self.stats.recent_calls) > self.config.window_size:
                self.stats.recent_calls.pop(0)
            
            # CLOSED/HALF_OPEN → OPEN 전환 확인
            if self._should_open_circuit():
                logger.warning(
                    f"CircuitBreaker '{self.name}': {self.state.value} → OPEN "
                    f"(failures: {self.stats.consecutive_failures})"
                )
                self.state = CircuitState.OPEN
                self._half_open_calls = 0
            # HALF_OPEN에서는 첫 실패에도 바로 OPEN으로
            elif self.state == CircuitState.HALF_OPEN:
                logger.warning(
                    f"CircuitBreaker '{self.name}': HALF_OPEN → OPEN (failure in half-open)"
                )
                self.state = CircuitState.OPEN
                self._half_open_calls = 0
    
    def _should_open_circuit(self) -> bool:
        """Circuit을 OPEN 상태로 전환해야 하는지 확인.
        
        Returns:
            True면 OPEN으로 전환
        """
        # 연속 실패 횟수 확인
        if self.stats.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # 에러율 확인
        if len(self.stats.recent_calls) >= self.config.window_size:
            error_rate = self.stats.recent_calls.count(False) / len(self.stats.recent_calls)
            if error_rate >= self.config.error_rate_threshold:
                return True
        
        return False
    
    def _check_state_transition(self) -> None:
        """상태 자동 전환 확인."""
        if self.state == CircuitState.OPEN:
            # 복구 시간이 지났는지 확인
            if self.stats.last_failure_time:
                elapsed = time.time() - self.stats.last_failure_time
                if elapsed >= self.config.recovery_timeout:
                    logger.info(
                        f"CircuitBreaker '{self.name}': OPEN → HALF_OPEN "
                        f"(recovery timeout reached)"
                    )
                    self.state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self.stats.consecutive_failures = 0
                    self.stats.consecutive_successes = 0
    
    def get_state(self) -> CircuitState:
        """현재 상태 반환.
        
        Returns:
            현재 Circuit Breaker 상태
        """
        return self.state
    
    def get_stats(self) -> dict:
        """통계 정보 반환.
        
        Returns:
            통계 정보 딕셔너리
        """
        error_rate = 0.0
        if self.stats.recent_calls:
            error_rate = self.stats.recent_calls.count(False) / len(self.stats.recent_calls)
        
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.stats.total_calls,
            "successful_calls": self.stats.successful_calls,
            "failed_calls": self.stats.failed_calls,
            "consecutive_failures": self.stats.consecutive_failures,
            "consecutive_successes": self.stats.consecutive_successes,
            "error_rate": error_rate,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time
        }
    
    async def reset(self) -> None:
        """Circuit Breaker 상태 초기화."""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.stats = CircuitBreakerStats()
            self._half_open_calls = 0
            logger.info(f"CircuitBreaker '{self.name}' reset to CLOSED")
    
    async def manual_open(self) -> None:
        """수동으로 Circuit을 OPEN 상태로 전환."""
        async with self._lock:
            self.state = CircuitState.OPEN
            self.stats.last_failure_time = time.time()
            logger.warning(f"CircuitBreaker '{self.name}' manually opened")
    
    async def manual_close(self) -> None:
        """수동으로 Circuit을 CLOSED 상태로 전환."""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.stats.consecutive_failures = 0
            self._half_open_calls = 0
            logger.info(f"CircuitBreaker '{self.name}' manually closed")


class CircuitBreakerOpenError(Exception):
    """Circuit Breaker가 OPEN 상태일 때 발생하는 예외."""
    pass