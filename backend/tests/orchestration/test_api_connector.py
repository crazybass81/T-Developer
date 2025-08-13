"""Tests for API Connector"""
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.orchestration.api_connector import APIConnector, APIRequest, APIResponse


class TestAPIConnector:
    def test_connector_initialization(self):
        """Test API connector initialization"""
        connector = APIConnector("http://test.com")
        assert connector.base_url == "http://test.com"
        assert connector.session is None
        assert len(connector.circuit_breaker) == 0
        assert len(connector.rate_limits) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test connector as context manager"""
        async with APIConnector() as connector:
            assert connector.session is not None
        # Session should be closed after exiting context

    def test_circuit_breaker_closed(self):
        """Test circuit breaker in closed state"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Initially should be closed
        assert connector._is_circuit_open(agent_key) == False

    def test_circuit_breaker_opens(self):
        """Test circuit breaker opens after failures"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Record multiple failures
        for _ in range(5):
            connector._record_failure(agent_key)

        # Circuit should be open
        assert connector._is_circuit_open(agent_key) == True

    def test_circuit_breaker_half_open(self):
        """Test circuit breaker half-open state"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Open circuit
        connector.circuit_breaker[agent_key] = {
            "failures": 5,
            "last_failure": 0,  # Long time ago
            "state": "open",
        }

        # Should transition to half-open
        is_open = connector._is_circuit_open(agent_key)
        assert is_open == False
        assert connector.circuit_breaker[agent_key]["state"] == "half_open"

    def test_rate_limiting(self):
        """Test rate limiting"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Should allow initial requests
        assert connector._check_rate_limit(agent_key) == True

        # Consume all tokens
        connector.rate_limits[agent_key]["tokens"] = 0

        # Should deny request
        assert connector._check_rate_limit(agent_key) == False

    def test_rate_limit_refill(self):
        """Test rate limit token refill"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Initialize and consume tokens
        connector._check_rate_limit(agent_key)
        connector.rate_limits[agent_key]["tokens"] = 0
        connector.rate_limits[agent_key]["last_refill"] -= 10  # 10 seconds ago

        # Should refill tokens
        assert connector._check_rate_limit(agent_key) == True
        assert connector.rate_limits[agent_key]["tokens"] > 0

    @pytest.mark.asyncio
    async def test_call_agent_circuit_open(self):
        """Test call fails when circuit is open"""
        connector = APIConnector()

        # Open circuit
        agent_key = "test_agent:endpoint"
        connector.circuit_breaker[agent_key] = {
            "failures": 5,
            "last_failure": float("inf"),  # Recent
            "state": "open",
        }

        request = APIRequest("test_agent", "endpoint", "POST", {})
        response = await connector.call_agent(request)

        assert response.status == 503
        assert response.error == "Circuit breaker open"

    @pytest.mark.asyncio
    async def test_call_agent_rate_limited(self):
        """Test call fails when rate limited"""
        connector = APIConnector()

        # Exhaust rate limit
        agent_key = "test_agent:endpoint"
        connector.rate_limits[agent_key] = {
            "tokens": 0,
            "max_tokens": 100,
            "refill_rate": 0,
            "last_refill": time.time(),  # Current time, not infinity
        }

        request = APIRequest("test_agent", "endpoint", "POST", {})
        response = await connector.call_agent(request)

        assert response.status == 429
        assert response.error == "Rate limit exceeded"

    @pytest.mark.asyncio
    async def test_execute_request_success(self):
        """Test successful request execution"""
        connector = APIConnector()

        # Create a proper mock session
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.request = MagicMock(return_value=mock_context)

        connector.session = mock_session

        request = APIRequest("test_agent", "endpoint", "POST", {"data": "test"})
        response = await connector._execute_request(request)

        assert response.status == 200
        assert response.data == {"result": "success"}
        assert response.latency_ms > 0

    @pytest.mark.asyncio
    async def test_execute_request_timeout(self):
        """Test request timeout handling"""
        connector = APIConnector()

        with patch("aiohttp.ClientSession.request", side_effect=asyncio.TimeoutError):
            request = APIRequest("test_agent", "endpoint", "POST", {}, timeout=1)

            with pytest.raises(Exception, match="Request timeout"):
                await connector._execute_request(request)

    @pytest.mark.asyncio
    async def test_batch_call(self):
        """Test batch API calls"""
        connector = APIConnector()

        # Mock successful responses
        with patch.object(connector, "call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = APIResponse(200, {"result": "ok"})

            requests = [
                APIRequest("agent1", "endpoint1", "POST", {}),
                APIRequest("agent2", "endpoint2", "GET", {}),
            ]

            responses = await connector.batch_call(requests)

            assert len(responses) == 2
            assert all(r.status == 200 for r in responses)
            assert mock_call.call_count == 2

    def test_record_metrics(self):
        """Test metric recording"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Record success
        connector._record_success(agent_key)
        assert len(connector.metrics[agent_key]) == 1
        assert connector.metrics[agent_key][0]["success"] == True

        # Record failure
        connector._record_failure(agent_key)
        assert len(connector.metrics[agent_key]) == 2
        assert connector.metrics[agent_key][1]["success"] == False

    def test_get_metrics(self):
        """Test metric retrieval"""
        connector = APIConnector()
        agent_key = "test_agent:endpoint"

        # Record some metrics
        connector._record_success(agent_key)
        connector._record_success(agent_key)
        connector._record_failure(agent_key)

        metrics = connector.get_metrics(agent_key)

        assert metrics["agent_key"] == agent_key
        assert metrics["total_calls"] == 3
        assert metrics["success_rate"] == pytest.approx(66.67, 0.1)

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test agent health check"""
        connector = APIConnector()

        with patch.object(connector, "call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = APIResponse(200, {"status": "healthy"})

            is_healthy = await connector.health_check("test_agent")

            assert is_healthy == True
            mock_call.assert_called_once()
