"""Resource Limiter 테스트.

TDD 방식으로 Resource Limiter의 모든 기능을 테스트합니다.
"""

import asyncio
import pytest
import psutil
import time
from unittest.mock import Mock, patch

from backend.packages.safety.resource_limiter import (
    ResourceLimiter,
    ResourceLimit,
    ResourceExceededError
)


class TestResourceLimiter:
    """Resource Limiter 테스트."""
    
    @pytest.fixture
    def resource_limits(self):
        """테스트용 리소스 제한."""
        return ResourceLimit(
            max_memory_mb=100,  # 100MB
            max_cpu_percent=50,  # 50%
            max_file_handles=10,  # 10개 파일
            max_execution_time=5.0,  # 5초
            max_concurrent_tasks=3  # 동시 3개
        )
    
    @pytest.fixture
    def resource_limiter(self, resource_limits):
        """테스트용 Resource Limiter."""
        return ResourceLimiter(limits=resource_limits)
    
    @pytest.mark.asyncio
    async def test_initial_state(self, resource_limiter):
        """초기 상태 확인."""
        stats = resource_limiter.get_stats()
        assert stats["current_tasks"] == 0
        assert stats["total_tasks_executed"] == 0
        assert stats["total_violations"] == 0
    
    @pytest.mark.asyncio
    async def test_successful_execution_within_limits(self, resource_limiter):
        """제한 내에서 성공적인 실행."""
        async def simple_task():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await resource_limiter.execute(simple_task)
        assert result == "success"
        
        stats = resource_limiter.get_stats()
        assert stats["total_tasks_executed"] == 1
        assert stats["total_violations"] == 0
    
    @pytest.mark.asyncio
    async def test_memory_limit_check(self, resource_limiter):
        """메모리 제한 확인."""
        async def memory_heavy_task():
            # 메모리를 많이 사용하는 작업 시뮬레이션
            data = bytearray(200 * 1024 * 1024)  # 200MB
            await asyncio.sleep(0.1)
            return len(data)
        
        # 메모리 제한 초과로 실패해야 함
        with patch.object(resource_limiter, '_get_memory_usage', return_value=150):
            with pytest.raises(ResourceExceededError) as exc_info:
                await resource_limiter.execute(memory_heavy_task)
            assert "memory" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_cpu_limit_check(self, resource_limiter):
        """CPU 제한 확인."""
        async def cpu_intensive_task():
            # CPU 집약적 작업 시뮬레이션
            start = time.time()
            while time.time() - start < 0.5:
                _ = sum(i**2 for i in range(1000))
            return "done"
        
        # CPU 사용률 모킹
        with patch.object(resource_limiter, '_get_cpu_usage', return_value=75):
            with pytest.raises(ResourceExceededError) as exc_info:
                await resource_limiter.execute(cpu_intensive_task)
            assert "cpu" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_execution_time_limit(self, resource_limiter):
        """실행 시간 제한."""
        async def long_running_task():
            await asyncio.sleep(10)  # 10초 (제한: 5초)
            return "should not reach here"
        
        with pytest.raises(ResourceExceededError) as exc_info:
            await resource_limiter.execute(long_running_task)
        assert "execution time" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_tasks_limit(self, resource_limiter):
        """동시 실행 태스크 수 제한."""
        async def task(task_id):
            await asyncio.sleep(0.5)
            return task_id
        
        # 4개 태스크 동시 실행 (제한: 3개)
        tasks = [
            asyncio.create_task(resource_limiter.execute(task, i))
            for i in range(4)
        ]
        
        # 하나는 실패해야 함
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # ResourceExceededError가 최소 1개 있어야 함
        errors = [r for r in results if isinstance(r, ResourceExceededError)]
        assert len(errors) >= 1
        assert "concurrent" in str(errors[0]).lower()
    
    @pytest.mark.asyncio
    async def test_file_handles_limit(self, resource_limiter):
        """파일 핸들 수 제한."""
        async def file_opening_task():
            files = []
            for i in range(15):  # 15개 파일 열기 (제한: 10개)
                files.append(open(f"/tmp/test_{i}.txt", "w"))
            return len(files)
        
        with patch.object(resource_limiter, '_get_open_files_count', return_value=12):
            with pytest.raises(ResourceExceededError) as exc_info:
                await resource_limiter.execute(file_opening_task)
            assert "file" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_check_resources_before_execution(self, resource_limiter):
        """실행 전 리소스 체크."""
        # 이미 리소스가 부족한 상황 시뮬레이션
        with patch.object(resource_limiter, '_get_memory_usage', return_value=95):
            async def task():
                return "should not execute"
            
            # 실행 전 체크에서 실패
            with pytest.raises(ResourceExceededError):
                await resource_limiter.execute(task)
    
    @pytest.mark.asyncio
    async def test_cleanup_after_failure(self, resource_limiter):
        """실패 후 정리."""
        async def failing_task():
            raise ValueError("Task failed")
        
        # 태스크 실패
        with pytest.raises(ValueError):
            await resource_limiter.execute(failing_task)
        
        # 현재 실행 중인 태스크 수는 0이어야 함
        stats = resource_limiter.get_stats()
        assert stats["current_tasks"] == 0
    
    @pytest.mark.asyncio
    async def test_get_stats(self, resource_limiter):
        """통계 정보 확인."""
        async def task():
            return "success"
        
        # 몇 개 태스크 실행
        await resource_limiter.execute(task)
        await resource_limiter.execute(task)
        
        # 메모리 제한 위반 시뮬레이션
        with patch.object(resource_limiter, '_get_memory_usage', return_value=150):
            try:
                await resource_limiter.execute(task)
            except ResourceExceededError:
                pass
        
        stats = resource_limiter.get_stats()
        assert stats["total_tasks_executed"] == 2
        assert stats["total_violations"] == 1
        assert stats["current_tasks"] == 0
        assert "memory_usage_mb" in stats
        assert "cpu_usage_percent" in stats
    
    @pytest.mark.asyncio
    async def test_update_limits(self, resource_limiter):
        """제한 값 업데이트."""
        new_limits = ResourceLimit(
            max_memory_mb=200,
            max_cpu_percent=75,
            max_execution_time=10.0
        )
        
        resource_limiter.update_limits(new_limits)
        
        # 새 제한으로 작동하는지 확인
        async def task():
            return "success"
        
        # 이전에는 실패했을 메모리 사용도 이제 성공
        with patch.object(resource_limiter, '_get_memory_usage', return_value=150):
            result = await resource_limiter.execute(task)
            assert result == "success"
    
    @pytest.mark.asyncio
    async def test_resource_monitoring(self, resource_limiter):
        """리소스 모니터링."""
        # 현재 리소스 상태 확인
        resources = resource_limiter.get_current_resources()
        
        assert "memory_mb" in resources
        assert "cpu_percent" in resources
        assert "open_files" in resources
        assert resources["memory_mb"] >= 0
        assert 0 <= resources["cpu_percent"] <= 100
        assert resources["open_files"] >= 0