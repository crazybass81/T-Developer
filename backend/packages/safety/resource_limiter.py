"""Resource Limiter implementation.

시스템 리소스 사용을 제한하고 모니터링하는 Resource Limiter입니다.
"""

from __future__ import annotations

import asyncio
import os
import psutil
import time
import logging
from typing import Any, Callable, Optional, TypeVar
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ResourceLimit:
    """리소스 제한 설정."""
    
    max_memory_mb: float = 500.0  # 최대 메모리 사용량 (MB)
    max_cpu_percent: float = 80.0  # 최대 CPU 사용률 (%)
    max_file_handles: int = 100  # 최대 파일 핸들 수
    max_execution_time: float = 300.0  # 최대 실행 시간 (초)
    max_concurrent_tasks: int = 10  # 최대 동시 실행 태스크 수
    check_interval: float = 0.5  # 리소스 체크 간격 (초)


@dataclass
class ResourceStats:
    """리소스 사용 통계."""
    
    total_tasks_executed: int = 0
    total_violations: int = 0
    memory_violations: int = 0
    cpu_violations: int = 0
    time_violations: int = 0
    concurrent_violations: int = 0
    file_violations: int = 0


class ResourceLimiter:
    """리소스 사용 제한 및 모니터링.
    
    시스템 리소스 사용을 모니터링하고 제한을 초과하지 않도록 합니다.
    """
    
    def __init__(self, limits: Optional[ResourceLimit] = None):
        """Resource Limiter 초기화.
        
        Args:
            limits: 리소스 제한 설정
        """
        self.limits = limits or ResourceLimit()
        self.stats = ResourceStats()
        self._current_tasks = 0
        self._lock = asyncio.Lock()
        self._process = psutil.Process(os.getpid())
        
        logger.info(
            f"ResourceLimiter initialized - "
            f"Memory: {self.limits.max_memory_mb}MB, "
            f"CPU: {self.limits.max_cpu_percent}%, "
            f"Tasks: {self.limits.max_concurrent_tasks}"
        )
    
    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """리소스 제한 하에서 함수 실행.
        
        Args:
            func: 실행할 함수
            *args: 위치 인자
            **kwargs: 키워드 인자
            
        Returns:
            함수 실행 결과
            
        Raises:
            ResourceExceededError: 리소스 제한 초과 시
        """
        # 동시 실행 태스크 수 체크
        async with self._lock:
            if self._current_tasks >= self.limits.max_concurrent_tasks:
                self.stats.concurrent_violations += 1
                self.stats.total_violations += 1
                raise ResourceExceededError(
                    f"Concurrent tasks limit exceeded: {self._current_tasks} >= {self.limits.max_concurrent_tasks}"
                )
            self._current_tasks += 1
        
        try:
            # 실행 전 리소스 체크
            await self._check_resources()
            
            # 함수 실행 (타임아웃 포함)
            if asyncio.iscoroutinefunction(func):
                task = asyncio.create_task(func(*args, **kwargs))
            else:
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(None, func, *args, **kwargs)
            
            # 리소스 모니터링과 함께 실행
            result = await self._execute_with_monitoring(task)
            
            self.stats.total_tasks_executed += 1
            return result
            
        finally:
            # 태스크 카운터 감소
            async with self._lock:
                self._current_tasks -= 1
    
    async def _execute_with_monitoring(self, task: asyncio.Task) -> Any:
        """리소스 모니터링과 함께 태스크 실행.
        
        Args:
            task: 실행할 태스크
            
        Returns:
            태스크 실행 결과
            
        Raises:
            ResourceExceededError: 리소스 제한 초과 시
        """
        start_time = time.time()
        monitor_task = asyncio.create_task(self._monitor_resources(start_time))
        
        try:
            # 태스크와 모니터 동시 실행
            done, pending = await asyncio.wait(
                [task, monitor_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 먼저 완료된 태스크 확인
            if task in done:
                # 태스크가 정상 완료됨
                monitor_task.cancel()
                return await task
            else:
                # 모니터가 먼저 완료됨 (리소스 위반)
                task.cancel()
                await monitor_task  # 예외를 발생시킴
                
        except asyncio.CancelledError:
            # 태스크 취소됨
            if not task.done():
                task.cancel()
            if not monitor_task.done():
                monitor_task.cancel()
            raise
    
    async def _monitor_resources(self, start_time: float) -> None:
        """리소스 사용 모니터링.
        
        Args:
            start_time: 시작 시간
            
        Raises:
            ResourceExceededError: 리소스 제한 초과 시
        """
        while True:
            # 실행 시간 체크
            elapsed = time.time() - start_time
            if elapsed > self.limits.max_execution_time:
                self.stats.time_violations += 1
                self.stats.total_violations += 1
                raise ResourceExceededError(
                    f"Execution time exceeded: {elapsed:.1f}s > {self.limits.max_execution_time}s"
                )
            
            # 리소스 체크
            await self._check_resources()
            
            # 체크 간격만큼 대기
            await asyncio.sleep(self.limits.check_interval)
    
    async def _check_resources(self) -> None:
        """현재 리소스 사용량 체크.
        
        Raises:
            ResourceExceededError: 리소스 제한 초과 시
        """
        # 메모리 체크
        memory_mb = self._get_memory_usage()
        if memory_mb > self.limits.max_memory_mb:
            self.stats.memory_violations += 1
            self.stats.total_violations += 1
            raise ResourceExceededError(
                f"Memory limit exceeded: {memory_mb:.1f}MB > {self.limits.max_memory_mb}MB"
            )
        
        # CPU 체크
        cpu_percent = self._get_cpu_usage()
        if cpu_percent > self.limits.max_cpu_percent:
            self.stats.cpu_violations += 1
            self.stats.total_violations += 1
            raise ResourceExceededError(
                f"CPU limit exceeded: {cpu_percent:.1f}% > {self.limits.max_cpu_percent}%"
            )
        
        # 파일 핸들 체크
        open_files = self._get_open_files_count()
        if open_files > self.limits.max_file_handles:
            self.stats.file_violations += 1
            self.stats.total_violations += 1
            raise ResourceExceededError(
                f"File handles limit exceeded: {open_files} > {self.limits.max_file_handles}"
            )
    
    def _get_memory_usage(self) -> float:
        """현재 메모리 사용량 조회 (MB).
        
        Returns:
            메모리 사용량 (MB)
        """
        try:
            memory_info = self._process.memory_info()
            return memory_info.rss / (1024 * 1024)  # bytes to MB
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """현재 CPU 사용률 조회 (%).
        
        Returns:
            CPU 사용률 (%)
        """
        try:
            return self._process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def _get_open_files_count(self) -> int:
        """열린 파일 수 조회.
        
        Returns:
            열린 파일 수
        """
        try:
            return len(self._process.open_files())
        except Exception as e:
            logger.warning(f"Failed to get open files count: {e}")
            return 0
    
    def get_current_resources(self) -> dict:
        """현재 리소스 사용 상태 조회.
        
        Returns:
            리소스 사용 상태 딕셔너리
        """
        return {
            "memory_mb": self._get_memory_usage(),
            "cpu_percent": self._get_cpu_usage(),
            "open_files": self._get_open_files_count(),
            "current_tasks": self._current_tasks
        }
    
    def get_stats(self) -> dict:
        """통계 정보 조회.
        
        Returns:
            통계 정보 딕셔너리
        """
        current = self.get_current_resources()
        return {
            "current_tasks": self._current_tasks,
            "total_tasks_executed": self.stats.total_tasks_executed,
            "total_violations": self.stats.total_violations,
            "memory_violations": self.stats.memory_violations,
            "cpu_violations": self.stats.cpu_violations,
            "time_violations": self.stats.time_violations,
            "concurrent_violations": self.stats.concurrent_violations,
            "file_violations": self.stats.file_violations,
            "memory_usage_mb": current["memory_mb"],
            "cpu_usage_percent": current["cpu_percent"],
            "open_files": current["open_files"]
        }
    
    def update_limits(self, new_limits: ResourceLimit) -> None:
        """리소스 제한 업데이트.
        
        Args:
            new_limits: 새로운 리소스 제한
        """
        self.limits = new_limits
        logger.info(
            f"ResourceLimiter limits updated - "
            f"Memory: {self.limits.max_memory_mb}MB, "
            f"CPU: {self.limits.max_cpu_percent}%, "
            f"Tasks: {self.limits.max_concurrent_tasks}"
        )


class ResourceExceededError(Exception):
    """리소스 제한 초과 시 발생하는 예외."""
    pass