"""Tests for A2A (Agent-to-Agent) Broker - External agent integration.

Phase 4: A2A External Integration [Days 14-16]
P4-T1: A2A Broker Setup
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from packages.a2a.broker import (
    A2ABroker,
    AgentCapability,
    AgentRegistry,
    AgentRequest,
    AgentResponse,
    AuditLogger,
    AuthManager,
    BrokerConfig,
    BrokerStatus,
    PolicyEngine,
    RateLimiter,
)


class TestBrokerConfig:
    """Test A2A broker configuration."""

    def test_default_config(self):
        """Test default broker configuration."""
        config = BrokerConfig()

        assert config.port == 8080
        assert config.max_connections == 100
        assert config.timeout_seconds == 30
        assert config.enable_mtls is True
        assert config.enable_audit is True
        assert config.rate_limit_per_minute == 60

    def test_custom_config(self):
        """Test custom broker configuration."""
        config = BrokerConfig(port=9090, max_connections=50, enable_mtls=False)

        assert config.port == 9090
        assert config.max_connections == 50
        assert config.enable_mtls is False


class TestAgentCapability:
    """Test agent capability definitions."""

    def test_capability_creation(self):
        """Test creating agent capability."""
        capability = AgentCapability(
            name="security_scan",
            version="1.0.0",
            description="Performs security vulnerability scanning",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            tags=["security", "scanning"],
        )

        assert capability.name == "security_scan"
        assert capability.version == "1.0.0"
        assert "security" in capability.tags

    def test_capability_matching(self):
        """Test capability matching logic."""
        capability = AgentCapability(name="test_generation", tags=["testing", "automation"])

        assert capability.matches(["testing"]) is True
        assert capability.matches(["deployment"]) is False
        assert capability.matches(["testing", "automation"]) is True


class TestAgentRegistry:
    """Test agent registry functionality."""

    @pytest.fixture
    def registry(self):
        """Create agent registry."""
        return AgentRegistry()

    def test_register_agent(self, registry):
        """Test registering an external agent."""
        agent_id = registry.register(
            agent_id="security-scanner-v1",
            endpoint="https://security.example.com/api",
            capabilities=[
                AgentCapability(name="scan_vulnerabilities"),
                AgentCapability(name="check_compliance"),
            ],
        )

        assert agent_id == "security-scanner-v1"
        assert registry.is_registered("security-scanner-v1") is True

    def test_discover_agents(self, registry):
        """Test discovering agents by capability."""
        # Register test agents
        registry.register(
            agent_id="test-gen-1",
            endpoint="https://test1.example.com",
            capabilities=[AgentCapability(name="generate_tests", tags=["testing"])],
        )

        registry.register(
            agent_id="security-1",
            endpoint="https://sec1.example.com",
            capabilities=[AgentCapability(name="scan", tags=["security"])],
        )

        # Discover by tag
        test_agents = registry.discover(tags=["testing"])
        assert len(test_agents) == 1
        assert test_agents[0]["agent_id"] == "test-gen-1"

        security_agents = registry.discover(tags=["security"])
        assert len(security_agents) == 1
        assert security_agents[0]["agent_id"] == "security-1"

    def test_unregister_agent(self, registry):
        """Test unregistering an agent."""
        registry.register(
            agent_id="temp-agent", endpoint="https://temp.example.com", capabilities=[]
        )

        assert registry.is_registered("temp-agent") is True

        registry.unregister("temp-agent")
        assert registry.is_registered("temp-agent") is False


class TestPolicyEngine:
    """Test policy engine for capability control."""

    @pytest.fixture
    def engine(self):
        """Create policy engine."""
        return PolicyEngine()

    @pytest.mark.asyncio
    async def test_load_policy(self, engine, tmp_path):
        """Test loading policy configuration."""
        policy_file = tmp_path / "a2a-policy.yaml"
        policy_file.write_text(
            """
whitelist:
  capabilities:
    - security_scan
    - test_generation
    - code_review
  agents:
    - security-scanner-*
    - test-gen-*
blacklist:
  capabilities:
    - dangerous_operation
  agents:
    - malicious-*
rate_limits:
  default: 60
  by_capability:
    security_scan: 10
    test_generation: 30
"""
        )

        await engine.load_policy(policy_file)

        assert engine.is_capability_allowed("security_scan") is True
        assert engine.is_capability_allowed("dangerous_operation") is False
        assert engine.is_agent_allowed("security-scanner-v1") is True
        assert engine.is_agent_allowed("malicious-bot") is False

    @pytest.mark.asyncio
    async def test_validate_request(self, engine):
        """Test request validation against policy."""
        # Setup policy
        engine.whitelist_capabilities = {"test_generation", "security_scan"}
        engine.blacklist_agents = {"malicious-*"}

        # Valid request
        valid_request = AgentRequest(
            agent_id="test-gen-1", capability="test_generation", payload={}
        )
        assert await engine.validate_request(valid_request) is True

        # Invalid capability
        invalid_request = AgentRequest(
            agent_id="test-gen-1", capability="dangerous_operation", payload={}
        )
        assert await engine.validate_request(invalid_request) is False


class TestAuthManager:
    """Test authentication and authorization."""

    @pytest.fixture
    def auth_manager(self):
        """Create auth manager."""
        return AuthManager()

    @pytest.mark.asyncio
    async def test_mtls_setup(self, auth_manager, tmp_path):
        """Test mTLS configuration."""
        cert_file = tmp_path / "cert.pem"
        key_file = tmp_path / "key.pem"
        ca_file = tmp_path / "ca.pem"

        # Create dummy cert files
        cert_file.write_text("CERT")
        key_file.write_text("KEY")
        ca_file.write_text("CA")

        result = await auth_manager.setup_mtls(
            cert_path=cert_file, key_path=key_file, ca_path=ca_file
        )

        assert result is True
        assert auth_manager.is_mtls_enabled() is True

    @pytest.mark.asyncio
    async def test_authenticate_agent(self, auth_manager):
        """Test agent authentication."""
        # Register agent credentials
        await auth_manager.register_agent(agent_id="trusted-agent", api_key="secret-key-123")

        # Valid authentication
        assert (
            await auth_manager.authenticate(agent_id="trusted-agent", api_key="secret-key-123")
            is True
        )

        # Invalid authentication
        assert (
            await auth_manager.authenticate(agent_id="trusted-agent", api_key="wrong-key") is False
        )

        # Unknown agent
        assert await auth_manager.authenticate(agent_id="unknown-agent", api_key="any-key") is False


class TestRateLimiter:
    """Test rate limiting functionality."""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter."""
        return RateLimiter()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, limiter):
        """Test rate limit enforcement."""
        # Configure limits
        limiter.set_limit("test-agent", requests_per_minute=10)

        # Should allow first 10 requests
        for i in range(10):
            assert await limiter.check_rate_limit("test-agent") is True
            await limiter.record_request("test-agent")

        # 11th request should be blocked
        assert await limiter.check_rate_limit("test-agent") is False

    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, limiter):
        """Test rate limit window reset."""
        limiter.set_limit("test-agent", requests_per_minute=5)

        # Use up limit
        for i in range(5):
            await limiter.record_request("test-agent")

        assert await limiter.check_rate_limit("test-agent") is False

        # Simulate time passing (mock)
        with patch("time.time", return_value=limiter._windows["test-agent"] + 61):
            assert await limiter.check_rate_limit("test-agent") is True


class TestAuditLogger:
    """Test audit logging functionality."""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create audit logger."""
        return AuditLogger(log_dir=tmp_path)

    @pytest.mark.asyncio
    async def test_log_request(self, logger, tmp_path):
        """Test logging agent requests."""
        request = AgentRequest(
            agent_id="test-agent", capability="test_generation", payload={"code": "test.py"}
        )

        response = AgentResponse(success=True, data={"tests_generated": 5})

        await logger.log_request(request, response)

        # Check log file exists
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) > 0

        # Verify log content
        log_content = log_files[0].read_text()
        assert "test-agent" in log_content
        assert "test_generation" in log_content
        assert "success" in log_content

    @pytest.mark.asyncio
    async def test_query_audit_log(self, logger):
        """Test querying audit logs."""
        # Log some requests
        for i in range(5):
            request = AgentRequest(agent_id=f"agent-{i}", capability="test", payload={})
            response = AgentResponse(success=True)
            await logger.log_request(request, response)

        # Query logs
        logs = await logger.query(
            start_time=datetime.now() - timedelta(hours=1), agent_id="agent-2"
        )

        assert len(logs) == 1
        assert logs[0]["agent_id"] == "agent-2"


class TestA2ABroker:
    """Test main A2A broker orchestration."""

    @pytest.fixture
    def broker(self):
        """Create A2A broker instance."""
        config = BrokerConfig()
        return A2ABroker(config)

    @pytest.mark.asyncio
    async def test_broker_startup(self, broker):
        """Test broker startup sequence."""
        with patch.object(broker, "_start_server", new_callable=AsyncMock):
            await broker.start()

            assert broker.status == BrokerStatus.RUNNING
            assert broker.health_check() is True

    @pytest.mark.asyncio
    async def test_handle_agent_request(self, broker):
        """Test handling agent request end-to-end."""
        # Register agent
        broker.registry.register(
            agent_id="test-gen",
            endpoint="https://test.example.com",
            capabilities=[AgentCapability(name="generate_tests")],
        )

        # Mock external agent call
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={"tests": ["test1", "test2"]})
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response

            request = AgentRequest(
                agent_id="test-gen", capability="generate_tests", payload={"file": "main.py"}
            )

            response = await broker.handle_request(request)

            assert response.success is True
            assert "tests" in response.data
            assert len(response.data["tests"]) == 2

    @pytest.mark.asyncio
    async def test_broker_shutdown(self, broker):
        """Test broker graceful shutdown."""
        await broker.start()
        await broker.shutdown()

        assert broker.status == BrokerStatus.STOPPED
        assert broker.health_check() is False

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, broker):
        """Test handling concurrent agent requests."""
        # Register multiple agents
        for i in range(3):
            broker.registry.register(
                agent_id=f"agent-{i}",
                endpoint=f"https://agent{i}.example.com",
                capabilities=[AgentCapability(name=f"capability_{i}")],
            )

        # Create concurrent requests
        requests = [
            AgentRequest(agent_id=f"agent-{i}", capability=f"capability_{i}", payload={})
            for i in range(3)
        ]

        # Mock responses
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={"result": "ok"})
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response

            # Execute concurrently
            responses = await asyncio.gather(*[broker.handle_request(req) for req in requests])

            assert len(responses) == 3
            assert all(r.success for r in responses)
