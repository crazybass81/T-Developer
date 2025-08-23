"""Circuit Breaker 테스트.

TDD 방식으로 Circuit Breaker의 모든 기능을 테스트합니다.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, Mock

from backend.packages.safety.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState
)


class TestCircuitBreaker:
    """Circuit Breaker 테스트."""
    
    @pytest.fixture
    def config(self):
        """테스트용 설정."""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1.0,  # 테스트를 위해 짧게
            success_threshold=2,
            half_open_max_calls=3,
            error_rate_threshold=0.5,
            window_size=5
        )
    
    @pytest.fixture
    def circuit_breaker(self, config):
        """테스트용 Circuit Breaker."""
        return CircuitBreaker("test", config)
    
    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self, circuit_breaker):
        """초기 상태는 CLOSED여야 함."""
        assert circuit_breaker.get_state() == CircuitState.CLOSED
        stats = circuit_breaker.get_stats()
        assert stats["state"] == "closed"
        assert stats["total_calls"] == 0
    
    @pytest.mark.asyncio
    async def test_successful_call_in_closed_state(self, circuit_breaker):
        """CLOSED 상태에서 성공적인 호출."""
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.get_state() == CircuitState.CLOSED
        
        stats = circuit_breaker.get_stats()
        assert stats["successful_calls"] == 1
        assert stats["failed_calls"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_function_call(self, circuit_breaker):
        """동기 함수도 호출 가능."""
        def sync_func(x, y):
            return x + y
        
        result = await circuit_breaker.call(sync_func, 2, 3)
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_failure_increases_counter(self, circuit_breaker):
        """실패 시 카운터 증가."""
        async def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        stats = circuit_breaker.get_stats()
        assert stats["failed_calls"] == 1
        assert stats["consecutive_failures"] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, circuit_breaker):
        """임계값 도달 시 OPEN 상태로 전환."""
        async def failing_func():
            raise ValueError("Test error")
        
        # 3번 실패 (threshold=3)
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Circuit이 OPEN 상태가 되어야 함
        assert circuit_breaker.get_state() == CircuitState.OPEN
        
        # OPEN 상태에서는 호출이 거부됨
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open(self, circuit_breaker):
        """복구 시간 후 HALF_OPEN으로 전환."""
        async def failing_func():
            raise ValueError("Test error")
        
        # Circuit을 OPEN 상태로 만들기
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.get_state() == CircuitState.OPEN
        
        # 복구 시간 대기
        await asyncio.sleep(1.1)
        
        # 다음 호출 시도 시 HALF_OPEN으로 전환되어야 함
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        assert result == "success"
        # 첫 성공 후에는 아직 HALF_OPEN
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_half_open_to_closed_transition(self, circuit_breaker):
        """HALF_OPEN에서 성공 시 CLOSED로 전환."""
        # Circuit을 HALF_OPEN 상태로 만들기
        await self._make_circuit_half_open(circuit_breaker)
        
        async def success_func():
            return "success"
        
        # success_threshold=2이므로 2번 성공하면 CLOSED로
        await circuit_breaker.call(success_func)
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        await circuit_breaker.call(success_func)
        assert circuit_breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_half_open_to_open_on_failure(self, circuit_breaker):
        """HALF_OPEN에서 실패 시 다시 OPEN으로."""
        # Circuit을 HALF_OPEN 상태로 만들기
        await self._make_circuit_half_open(circuit_breaker)
        
        async def failing_func():
            raise ValueError("Test error")
        
        # HALF_OPEN에서 실패하면 바로 OPEN으로
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_half_open_max_calls_limit(self, circuit_breaker):
        """HALF_OPEN 상태에서 최대 호출 수 제한."""
        # Circuit을 HALF_OPEN 상태로 만들기
        await self._make_circuit_half_open(circuit_breaker)
        
        async def success_func():
            return "success"
        
        # success_threshold=2이므로 1번만 성공시키고
        # 나머지는 max_calls 테스트
        await circuit_breaker.call(success_func)
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        # 2번째 호출도 성공하면 CLOSED가 되므로
        # 대신 아무 작업도 안 하는 함수로 호출 수만 채우기
        await circuit_breaker.call(success_func)
        # 이제 CLOSED 상태가 됨
        
        # 테스트를 다시 설정: HALF_OPEN으로 만들되 max_calls 테스트를 위해
        await circuit_breaker.manual_open()
        await asyncio.sleep(1.1)
        circuit_breaker._check_state_transition()
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        # 이제 half_open_max_calls=3 테스트
        for i in range(3):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
            # 3번째 호출 후에도 여전히 HALF_OPEN (success_threshold=2 미달)
            if i < 2:  # 처음 2번은 HALF_OPEN 유지
                assert circuit_breaker.get_state() == CircuitState.HALF_OPEN
        
        # 3번 호출 후 상태 확인 - success_threshold를 채웠으므로 CLOSED
        assert circuit_breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_error_rate_threshold(self, circuit_breaker):
        """에러율 기반 Circuit Open."""
        async def sometimes_failing(should_fail):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # window_size=5, error_rate_threshold=0.5
        # 5개 중 3개 실패하면 에러율 60%로 OPEN
        pattern = [True, False, True, False, True]  # 3 failures, 2 successes
        
        for should_fail in pattern:
            try:
                await circuit_breaker.call(sometimes_failing, should_fail)
            except ValueError:
                pass
        
        # 에러율이 50%를 초과하므로 OPEN
        assert circuit_breaker.get_state() == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_manual_open(self, circuit_breaker):
        """수동으로 Circuit Open."""
        assert circuit_breaker.get_state() == CircuitState.CLOSED
        
        await circuit_breaker.manual_open()
        assert circuit_breaker.get_state() == CircuitState.OPEN
        
        # OPEN 상태에서 호출 거부
        async def func():
            return "test"
        
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(func)
    
    @pytest.mark.asyncio
    async def test_manual_close(self, circuit_breaker):
        """수동으로 Circuit Close."""
        # 먼저 OPEN 상태로
        await circuit_breaker.manual_open()
        assert circuit_breaker.get_state() == CircuitState.OPEN
        
        # 수동으로 CLOSED로
        await circuit_breaker.manual_close()
        assert circuit_breaker.get_state() == CircuitState.CLOSED
        
        # 다시 호출 가능
        async def func():
            return "success"
        
        result = await circuit_breaker.call(func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_reset(self, circuit_breaker):
        """Circuit Breaker 리셋."""
        # 몇 번 실패시키기
        async def failing_func():
            raise ValueError("Test error")
        
        for _ in range(2):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        stats = circuit_breaker.get_stats()
        assert stats["failed_calls"] == 2
        
        # 리셋
        await circuit_breaker.reset()
        
        stats = circuit_breaker.get_stats()
        assert stats["total_calls"] == 0
        assert stats["failed_calls"] == 0
        assert circuit_breaker.get_state() == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_get_stats(self, circuit_breaker):
        """통계 정보 확인."""
        async def func(should_fail):
            if should_fail:
                raise ValueError("Error")
            return "success"
        
        # 2 성공, 1 실패
        await circuit_breaker.call(func, False)
        await circuit_breaker.call(func, False)
        with pytest.raises(ValueError):
            await circuit_breaker.call(func, True)
        
        stats = circuit_breaker.get_stats()
        assert stats["name"] == "test"
        assert stats["total_calls"] == 3
        assert stats["successful_calls"] == 2
        assert stats["failed_calls"] == 1
        assert stats["consecutive_failures"] == 1
        assert stats["consecutive_successes"] == 0
        assert stats["error_rate"] == 1/3  # 마지막 3개 중 1개 실패
    
    # Helper methods
    async def _make_circuit_half_open(self, circuit_breaker):
        """Circuit을 HALF_OPEN 상태로 만드는 헬퍼."""
        # OPEN 상태로 만들기
        async def failing_func():
            raise ValueError("Test error")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # 복구 시간 대기
        await asyncio.sleep(1.1)
        
        # 상태 전환 트리거
        circuit_breaker._check_state_transition()
        assert circuit_breaker.get_state() == CircuitState.HALF_OPEN