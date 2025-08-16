"""Tests for A2A protocol implementation.

Phase 4: A2A External Integration - Test Suite
"""

import asyncio

import pytest

from packages.a2a.protocols import (
    A2AMessage,
    A2AProtocol,
    AgentInfo,
    CapabilityInfo,
    MessageFilter,
    MessageHeader,
    MessagePayload,
    MessageRouter,
    MessageType,
    MessageValidationError,
    MessageValidator,
    RateLimitConfig,
    RateLimiter,
    ResponseStatus,
    create_request_message,
)


@pytest.fixture
def sample_agent_info():
    """Create sample agent info for testing."""
    capabilities = [
        CapabilityInfo(
            name="test_capability", version="1.0.0", description="Test capability", tags=["test"]
        )
    ]

    return AgentInfo(agent_id="test-agent", agent_name="Test Agent", capabilities=capabilities)


@pytest.fixture
def sample_message():
    """Create sample A2A message for testing."""
    header = MessageHeader(
        message_type=MessageType.REQUEST, sender_id="sender-agent", receiver_id="receiver-agent"
    )

    payload = MessagePayload(
        capability="test_capability", action="test_action", parameters={"param1": "value1"}
    )

    return A2AMessage(header=header, payload=payload)


class TestMessageValidator:
    """Test message validation."""

    def test_valid_message(self, sample_message: A2AMessage):
        """Test validation of valid message."""
        # Should not raise exception
        MessageValidator.validate_message(sample_message)

    def test_invalid_message_no_sender(self, sample_message: A2AMessage):
        """Test validation with missing sender."""
        sample_message.header.sender_id = ""

        with pytest.raises(MessageValidationError):
            MessageValidator.validate_message(sample_message)

    def test_invalid_message_no_id(self, sample_message: A2AMessage):
        """Test validation with missing message ID."""
        sample_message.header.message_id = ""

        with pytest.raises(MessageValidationError):
            MessageValidator.validate_message(sample_message)

    def test_invalid_protocol_version(self, sample_message: A2AMessage):
        """Test validation with invalid protocol version."""
        sample_message.header.version = "2.0"  # Unsupported version

        with pytest.raises(MessageValidationError):
            MessageValidator.validate_message(sample_message)

    def test_expired_message(self, sample_message: A2AMessage):
        """Test validation of expired message."""
        import time

        sample_message.header.timestamp = time.time() - 400  # Expired
        sample_message.header.ttl_seconds = 300

        with pytest.raises(MessageValidationError):
            MessageValidator.validate_message(sample_message)


class TestRateLimiter:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_within_bounds(self):
        """Test rate limiting within bounds."""
        config = RateLimitConfig(requests_per_minute=5, window_size=60)
        limiter = RateLimiter(config)

        # Make requests within limit
        for i in range(5):
            allowed = await limiter.check_rate_limit("test-agent")
            assert allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limiting when exceeded."""
        config = RateLimitConfig(requests_per_minute=2, window_size=60)
        limiter = RateLimiter(config)

        # Make requests up to limit
        assert await limiter.check_rate_limit("test-agent") is True
        assert await limiter.check_rate_limit("test-agent") is True

        # Next request should be denied
        assert await limiter.check_rate_limit("test-agent") is False

    @pytest.mark.asyncio
    async def test_rate_limit_window_reset(self):
        """Test rate limit window reset."""
        config = RateLimitConfig(requests_per_minute=2, window_size=1)  # 1 second window
        limiter = RateLimiter(config)

        # Exhaust limit
        assert await limiter.check_rate_limit("test-agent") is True
        assert await limiter.check_rate_limit("test-agent") is True
        assert await limiter.check_rate_limit("test-agent") is False

        # Wait for window reset
        await asyncio.sleep(1.1)

        # Should be allowed again
        assert await limiter.check_rate_limit("test-agent") is True


class TestMessageRouter:
    """Test message routing."""

    @pytest.fixture
    def router(self):
        """Create message router for testing."""
        return MessageRouter()

    @pytest.mark.asyncio
    async def test_handler_registration(self, router: MessageRouter):
        """Test handler registration."""
        handler_called = False

        async def test_handler(message: A2AMessage) -> None:
            nonlocal handler_called
            handler_called = True

        router.register_handler(MessageType.REQUEST, test_handler)

        # Create test message
        message = A2AMessage(
            header=MessageHeader(message_type=MessageType.REQUEST, sender_id="test"),
            payload=MessagePayload(),
        )

        await router.route_message(message)
        assert handler_called is True

    @pytest.mark.asyncio
    async def test_capability_handler(self, router: MessageRouter):
        """Test capability-specific handler."""
        response_data = {"result": "success"}

        async def capability_handler(message: A2AMessage) -> A2AMessage:
            return message.create_response(status=ResponseStatus.SUCCESS, data=response_data)

        router.register_capability_handler("test_capability", capability_handler)

        # Create request message
        message = A2AMessage(
            header=MessageHeader(
                message_type=MessageType.REQUEST,
                sender_id="test-sender",
                receiver_id="test-receiver",
            ),
            payload=MessagePayload(capability="test_capability"),
        )

        response = await router.route_message(message)
        assert response is not None
        assert response.payload.data["result"] == "success"

    @pytest.mark.asyncio
    async def test_message_filter(self, router: MessageRouter):
        """Test message filtering."""
        handler_called = False

        async def test_handler(message: A2AMessage) -> None:
            nonlocal handler_called
            handler_called = True

        router.register_handler(MessageType.REQUEST, test_handler)

        # Add filter that blocks messages from specific sender
        message_filter = MessageFilter(sender_ids={"allowed-sender"})
        router.add_filter(message_filter)

        # Create message from blocked sender
        blocked_message = A2AMessage(
            header=MessageHeader(message_type=MessageType.REQUEST, sender_id="blocked-sender"),
            payload=MessagePayload(),
        )

        await router.route_message(blocked_message)
        assert handler_called is False

        # Create message from allowed sender
        allowed_message = A2AMessage(
            header=MessageHeader(message_type=MessageType.REQUEST, sender_id="allowed-sender"),
            payload=MessagePayload(),
        )

        await router.route_message(allowed_message)
        assert handler_called is True


class TestA2AProtocol:
    """Test A2A protocol functionality."""

    @pytest.fixture
    def protocol(self, sample_agent_info: AgentInfo):
        """Create A2A protocol for testing."""
        return A2AProtocol(agent_id="test-agent", agent_info=sample_agent_info)

    @pytest.mark.asyncio
    async def test_message_processing(self, protocol: A2AProtocol, sample_message: A2AMessage):
        """Test message processing."""
        response = await protocol.process_message(sample_message)
        assert response is None  # No specific handler for test capability

    @pytest.mark.asyncio
    async def test_handshake_handling(self, protocol: A2AProtocol, sample_agent_info: AgentInfo):
        """Test handshake message handling."""
        # Create handshake message
        handshake_msg = A2AMessage(
            header=MessageHeader(message_type=MessageType.HANDSHAKE, sender_id="remote-agent"),
            payload=MessagePayload(data=sample_agent_info.to_dict()),
        )

        response = await protocol.process_message(handshake_msg)
        assert response is not None
        assert response.header.message_type == MessageType.RESPONSE
        assert response.payload.data["status"] == ResponseStatus.SUCCESS.value

    @pytest.mark.asyncio
    async def test_capability_discovery(self, protocol: A2AProtocol):
        """Test capability discovery handling."""
        # Create capability discovery message
        discovery_msg = A2AMessage(
            header=MessageHeader(
                message_type=MessageType.CAPABILITY_DISCOVERY, sender_id="remote-agent"
            ),
            payload=MessagePayload(
                data={"query_tags": ["test"], "query_capabilities": ["test_capability"]}
            ),
        )

        response = await protocol.process_message(discovery_msg)
        assert response is not None
        assert response.payload.data["status"] == ResponseStatus.SUCCESS.value
        assert "matching_capabilities" in response.payload.data

    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, protocol: A2AProtocol, sample_message: A2AMessage):
        """Test rate limit enforcement."""
        # Configure very low rate limit
        protocol.rate_limiter.config.requests_per_minute = 1
        protocol.rate_limiter.config.window_size = 60

        # First message should succeed
        response1 = await protocol.process_message(sample_message)

        # Second message should be rate limited
        with pytest.raises(Exception):  # Should raise RateLimitError
            await protocol.process_message(sample_message)

    @pytest.mark.asyncio
    async def test_capability_handler_registration(self, protocol: A2AProtocol):
        """Test capability handler registration."""
        response_data = {"processed": True}

        async def test_capability_handler(message: A2AMessage) -> A2AMessage:
            return message.create_response(status=ResponseStatus.SUCCESS, data=response_data)

        protocol.register_capability_handler("test_capability", test_capability_handler)

        # Create request for the capability
        request_msg = A2AMessage(
            header=MessageHeader(
                message_type=MessageType.REQUEST, sender_id="test-sender", receiver_id="test-agent"
            ),
            payload=MessagePayload(capability="test_capability"),
        )

        response = await protocol.process_message(request_msg)
        assert response is not None
        assert response.payload.data["processed"] is True

    @pytest.mark.asyncio
    async def test_heartbeat_management(self, protocol: A2AProtocol):
        """Test heartbeat functionality."""
        # Start heartbeat
        await protocol.start_heartbeat()
        assert protocol.heartbeat_task is not None
        assert not protocol.heartbeat_task.done()

        # Stop heartbeat
        await protocol.stop_heartbeat()
        assert protocol.heartbeat_task.done()


class TestMessageTypes:
    """Test message type functionality."""

    def test_message_serialization(self, sample_message: A2AMessage):
        """Test message serialization to dictionary."""
        message_dict = sample_message.to_dict()

        assert "header" in message_dict
        assert "payload" in message_dict
        assert message_dict["header"]["sender_id"] == "sender-agent"
        assert message_dict["payload"]["capability"] == "test_capability"

    def test_message_deserialization(self, sample_message: A2AMessage):
        """Test message deserialization from dictionary."""
        message_dict = sample_message.to_dict()
        reconstructed = A2AMessage.from_dict(message_dict)

        assert reconstructed.header.sender_id == sample_message.header.sender_id
        assert reconstructed.payload.capability == sample_message.payload.capability

    def test_response_creation(self, sample_message: A2AMessage):
        """Test response message creation."""
        response = sample_message.create_response(
            status=ResponseStatus.SUCCESS, data={"result": "test"}
        )

        assert response.header.message_type == MessageType.RESPONSE
        assert response.header.sender_id == sample_message.header.receiver_id
        assert response.header.receiver_id == sample_message.header.sender_id
        assert response.header.correlation_id == sample_message.header.message_id

    def test_message_expiration(self):
        """Test message expiration checking."""
        import time

        # Create expired message
        header = MessageHeader(
            timestamp=time.time() - 400, ttl_seconds=300  # 400 seconds ago  # 5 minute TTL
        )

        assert header.is_expired() is True

        # Create non-expired message
        header = MessageHeader(
            timestamp=time.time() - 100, ttl_seconds=300  # 100 seconds ago  # 5 minute TTL
        )

        assert header.is_expired() is False


@pytest.mark.asyncio
async def test_protocol_integration():
    """Test full protocol integration scenario."""
    # Create two protocol instances
    agent1_info = AgentInfo(
        agent_id="agent-1",
        agent_name="Agent 1",
        capabilities=[CapabilityInfo(name="echo", description="Echo service", tags=["utility"])],
    )

    agent2_info = AgentInfo(
        agent_id="agent-2",
        agent_name="Agent 2",
        capabilities=[
            CapabilityInfo(name="reverse", description="Reverse service", tags=["utility"])
        ],
    )

    protocol1 = A2AProtocol("agent-1", agent1_info)
    protocol2 = A2AProtocol("agent-2", agent2_info)

    # Register echo capability handler on agent 1
    async def echo_handler(message: A2AMessage) -> A2AMessage:
        text = message.payload.parameters.get("text", "")
        return message.create_response(status=ResponseStatus.SUCCESS, data={"echo": text})

    protocol1.register_capability_handler("echo", echo_handler)

    # Create request from agent 2 to agent 1
    request = create_request_message(
        sender_id="agent-2",
        receiver_id="agent-1",
        capability="echo",
        action="echo",
        parameters={"text": "Hello, World!"},
    )

    # Process request on agent 1
    response = await protocol1.process_message(request)

    # Verify response
    assert response is not None
    assert response.payload.data["result"]["echo"] == "Hello, World!"
    assert response.header.correlation_id == request.header.message_id
