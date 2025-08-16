"""A2A handshake protocol for agent connection establishment.

Phase 4: A2A External Integration
P4-T2: A2A Protocol Implementation
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .message_types import (
    A2AMessage,
    AgentInfo,
    MessageType,
    create_error_message,
    create_handshake_message,
)


class HandshakeState(Enum):
    """Handshake connection states."""

    DISCONNECTED = "disconnected"
    INITIATING = "initiating"
    CHALLENGE_SENT = "challenge_sent"
    CHALLENGE_RECEIVED = "challenge_received"
    AUTHENTICATING = "authenticating"
    CONNECTED = "connected"
    FAILED = "failed"
    TIMEOUT = "timeout"


class HandshakeError(Exception):
    """Exception for handshake errors."""

    pass


@dataclass
class HandshakeConfig:
    """Handshake configuration.

    Attributes:
        timeout_seconds: Handshake timeout
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries
        require_auth: Whether authentication is required
        supported_protocols: Supported protocol versions
        challenge_required: Whether challenge-response is required
    """

    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: int = 5
    require_auth: bool = True
    supported_protocols: list[str] = field(default_factory=lambda: ["1.0"])
    challenge_required: bool = False


@dataclass
class HandshakeChallenge:
    """Challenge for authentication.

    Attributes:
        challenge_id: Unique challenge identifier
        challenge_type: Type of challenge
        challenge_data: Challenge data
        timestamp: Challenge creation time
        expires_at: Challenge expiration time
    """

    challenge_id: str
    challenge_type: str
    challenge_data: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300)

    def is_expired(self) -> bool:
        """Check if challenge has expired."""
        return time.time() > self.expires_at


@dataclass
class HandshakeContext:
    """Context for handshake session.

    Attributes:
        session_id: Unique session identifier
        local_agent: Local agent information
        remote_agent: Remote agent information
        state: Current handshake state
        started_at: Handshake start time
        config: Handshake configuration
        challenge: Current challenge
        auth_token: Authentication token
        retry_count: Number of retries attempted
        error_message: Last error message
    """

    session_id: str
    local_agent: AgentInfo
    remote_agent: Optional[AgentInfo] = None
    state: HandshakeState = HandshakeState.DISCONNECTED
    started_at: float = field(default_factory=time.time)
    config: HandshakeConfig = field(default_factory=HandshakeConfig)
    challenge: Optional[HandshakeChallenge] = None
    auth_token: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if handshake has timed out."""
        return time.time() - self.started_at > self.config.timeout_seconds

    def can_retry(self) -> bool:
        """Check if handshake can be retried."""
        return self.retry_count < self.config.max_retries


class AuthenticationProvider:
    """Base class for authentication providers."""

    async def create_challenge(self, agent_id: str) -> HandshakeChallenge:
        """Create authentication challenge.

        Args:
            agent_id: Agent identifier

        Returns:
            Authentication challenge
        """
        raise NotImplementedError

    async def verify_response(
        self, challenge: HandshakeChallenge, response: dict[str, Any]
    ) -> bool:
        """Verify challenge response.

        Args:
            challenge: Original challenge
            response: Response to verify

        Returns:
            True if response is valid
        """
        raise NotImplementedError

    async def generate_token(self, agent_id: str) -> str:
        """Generate authentication token.

        Args:
            agent_id: Agent identifier

        Returns:
            Authentication token
        """
        raise NotImplementedError


class SimpleTokenAuthProvider(AuthenticationProvider):
    """Simple token-based authentication provider."""

    def __init__(self, shared_secret: str):
        """Initialize with shared secret.

        Args:
            shared_secret: Shared secret for token generation
        """
        self.shared_secret = shared_secret

    async def create_challenge(self, agent_id: str) -> HandshakeChallenge:
        """Create simple token challenge."""
        import uuid

        challenge_id = str(uuid.uuid4())
        nonce = str(uuid.uuid4())

        return HandshakeChallenge(
            challenge_id=challenge_id,
            challenge_type="token",
            challenge_data={"nonce": nonce, "algorithm": "sha256"},
        )

    async def verify_response(
        self, challenge: HandshakeChallenge, response: dict[str, Any]
    ) -> bool:
        """Verify token response."""
        import hashlib

        expected_hash = hashlib.sha256(
            f"{challenge.challenge_data['nonce']}{self.shared_secret}".encode()
        ).hexdigest()

        return response.get("token_hash") == expected_hash

    async def generate_token(self, agent_id: str) -> str:
        """Generate simple authentication token."""
        import hashlib
        import time

        timestamp = str(int(time.time()))
        token_data = f"{agent_id}:{timestamp}:{self.shared_secret}"
        return hashlib.sha256(token_data.encode()).hexdigest()


class HandshakeManager:
    """Manages A2A handshake protocol."""

    def __init__(
        self,
        local_agent: AgentInfo,
        config: Optional[HandshakeConfig] = None,
        auth_provider: Optional[AuthenticationProvider] = None,
    ):
        """Initialize handshake manager.

        Args:
            local_agent: Local agent information
            config: Handshake configuration
            auth_provider: Authentication provider
        """
        self.local_agent = local_agent
        self.config = config or HandshakeConfig()
        self.auth_provider = auth_provider
        self.logger = logging.getLogger(self.__class__.__name__)

        # Active handshake sessions
        self.sessions: dict[str, HandshakeContext] = {}

        # Callbacks
        self.on_handshake_complete: Optional[Callable[[str, AgentInfo], None]] = None
        self.on_handshake_failed: Optional[Callable[[str, str], None]] = None

    async def initiate_handshake(
        self, remote_agent_id: str, transport: Callable[[A2AMessage], None]
    ) -> str:
        """Initiate handshake with remote agent.

        Args:
            remote_agent_id: Remote agent identifier
            transport: Transport function for sending messages

        Returns:
            Session ID for tracking handshake

        Raises:
            HandshakeError: If handshake cannot be initiated
        """
        import uuid

        session_id = str(uuid.uuid4())

        # Create handshake context
        context = HandshakeContext(
            session_id=session_id, local_agent=self.local_agent, config=self.config
        )

        self.sessions[session_id] = context

        try:
            # Create handshake message
            handshake_msg = create_handshake_message(
                sender_id=self.local_agent.agent_id, agent_info=self.local_agent
            )

            # Add session ID to metadata
            handshake_msg.payload.metadata["session_id"] = session_id
            handshake_msg.header.receiver_id = remote_agent_id

            # Update state
            context.state = HandshakeState.INITIATING

            # Send handshake message
            await transport(handshake_msg)

            self.logger.info(f"Initiated handshake with {remote_agent_id} (session: {session_id})")

            # Start timeout task
            asyncio.create_task(self._handle_timeout(session_id))

            return session_id

        except Exception as e:
            # Clean up on error
            if session_id in self.sessions:
                del self.sessions[session_id]
            raise HandshakeError(f"Failed to initiate handshake: {e}")

    async def handle_handshake_message(
        self, message: A2AMessage, transport: Callable[[A2AMessage], None]
    ) -> Optional[str]:
        """Handle incoming handshake message.

        Args:
            message: Incoming handshake message
            transport: Transport function for sending responses

        Returns:
            Session ID if handshake completed successfully
        """
        session_id = message.payload.metadata.get("session_id")

        try:
            if message.header.message_type == MessageType.HANDSHAKE:
                return await self._handle_handshake_request(message, transport)
            elif message.header.message_type == MessageType.RESPONSE:
                return await self._handle_handshake_response(message, transport)
            else:
                self.logger.warning(
                    f"Unexpected message type in handshake: {message.header.message_type}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error handling handshake message: {e}")

            if session_id:
                await self._fail_handshake(session_id, str(e))

            return None

    async def _handle_handshake_request(
        self, message: A2AMessage, transport: Callable[[A2AMessage], None]
    ) -> Optional[str]:
        """Handle incoming handshake request."""
        try:
            # Extract agent info
            remote_agent = AgentInfo.from_dict(message.payload.data)
            session_id = message.payload.metadata.get("session_id")

            if not session_id:
                import uuid

                session_id = str(uuid.uuid4())

            # Create or update session
            if session_id not in self.sessions:
                context = HandshakeContext(
                    session_id=session_id, local_agent=self.local_agent, config=self.config
                )
                self.sessions[session_id] = context
            else:
                context = self.sessions[session_id]

            context.remote_agent = remote_agent
            context.state = HandshakeState.CHALLENGE_RECEIVED

            # Check protocol compatibility
            if not self._is_protocol_compatible(message.header.version):
                await self._fail_handshake(
                    session_id, f"Incompatible protocol version: {message.header.version}"
                )
                return None

            # Create response
            if self.config.require_auth and self.auth_provider:
                # Send challenge
                challenge = await self.auth_provider.create_challenge(remote_agent.agent_id)
                context.challenge = challenge
                context.state = HandshakeState.CHALLENGE_SENT

                response = message.create_response(
                    status="challenge",
                    data={
                        "agent_info": self.local_agent.to_dict(),
                        "challenge": {
                            "challenge_id": challenge.challenge_id,
                            "challenge_type": challenge.challenge_type,
                            "challenge_data": challenge.challenge_data,
                        },
                    },
                )
            else:
                # No authentication required
                context.state = HandshakeState.CONNECTED
                response = message.create_response(
                    status="success", data={"agent_info": self.local_agent.to_dict()}
                )

                # Complete handshake
                await self._complete_handshake(session_id)

            # Send response
            response.payload.metadata["session_id"] = session_id
            await transport(response)

            return session_id if context.state == HandshakeState.CONNECTED else None

        except Exception as e:
            self.logger.error(f"Error handling handshake request: {e}")
            await self._send_error_response(message, str(e), transport)
            return None

    async def _handle_handshake_response(
        self, message: A2AMessage, transport: Callable[[A2AMessage], None]
    ) -> Optional[str]:
        """Handle handshake response."""
        session_id = message.payload.metadata.get("session_id")

        if not session_id or session_id not in self.sessions:
            self.logger.warning("Received handshake response for unknown session")
            return None

        context = self.sessions[session_id]

        try:
            response_data = message.payload.data
            status = response_data.get("status")

            if status == "success":
                # Extract remote agent info
                agent_data = response_data.get("agent_info")
                if agent_data:
                    context.remote_agent = AgentInfo.from_dict(agent_data)

                # Complete handshake
                context.state = HandshakeState.CONNECTED
                await self._complete_handshake(session_id)
                return session_id

            elif status == "challenge":
                # Handle authentication challenge
                if not self.auth_provider:
                    await self._fail_handshake(
                        session_id, "Authentication required but no provider configured"
                    )
                    return None

                challenge_data = response_data.get("challenge")
                if not challenge_data:
                    await self._fail_handshake(session_id, "Invalid challenge response")
                    return None

                # Create challenge response
                challenge = HandshakeChallenge(
                    challenge_id=challenge_data["challenge_id"],
                    challenge_type=challenge_data["challenge_type"],
                    challenge_data=challenge_data["challenge_data"],
                )

                # Generate response (simplified)
                if challenge.challenge_type == "token":
                    import hashlib

                    nonce = challenge.challenge_data.get("nonce", "")
                    # This should use proper shared secret
                    token_hash = hashlib.sha256(f"{nonce}shared_secret".encode()).hexdigest()

                    auth_response = A2AMessage(header=message.header, payload=message.payload)
                    auth_response.header.sender_id = self.local_agent.agent_id
                    auth_response.header.receiver_id = message.header.sender_id
                    auth_response.payload.data = {
                        "challenge_id": challenge.challenge_id,
                        "token_hash": token_hash,
                    }
                    auth_response.payload.metadata["session_id"] = session_id

                    context.state = HandshakeState.AUTHENTICATING
                    await transport(auth_response)

                return None

            else:
                # Handle error response
                error_msg = response_data.get("error", "Unknown error")
                await self._fail_handshake(session_id, error_msg)
                return None

        except Exception as e:
            self.logger.error(f"Error handling handshake response: {e}")
            await self._fail_handshake(session_id, str(e))
            return None

    def _is_protocol_compatible(self, version: str) -> bool:
        """Check if protocol version is compatible."""
        return version in self.config.supported_protocols

    async def _complete_handshake(self, session_id: str) -> None:
        """Complete handshake successfully."""
        if session_id not in self.sessions:
            return

        context = self.sessions[session_id]

        if context.remote_agent:
            self.logger.info(
                f"Handshake completed successfully with {context.remote_agent.agent_id} "
                f"(session: {session_id})"
            )

            # Call completion callback
            if self.on_handshake_complete:
                await self._safe_callback(
                    self.on_handshake_complete, context.remote_agent.agent_id, context.remote_agent
                )

        # Clean up session
        del self.sessions[session_id]

    async def _fail_handshake(self, session_id: str, error_message: str) -> None:
        """Fail handshake with error."""
        if session_id not in self.sessions:
            return

        context = self.sessions[session_id]
        context.state = HandshakeState.FAILED
        context.error_message = error_message

        self.logger.warning(f"Handshake failed (session: {session_id}): {error_message}")

        # Call failure callback
        if self.on_handshake_failed:
            remote_id = context.remote_agent.agent_id if context.remote_agent else "unknown"
            await self._safe_callback(self.on_handshake_failed, remote_id, error_message)

        # Clean up session
        del self.sessions[session_id]

    async def _handle_timeout(self, session_id: str) -> None:
        """Handle handshake timeout."""
        await asyncio.sleep(self.config.timeout_seconds)

        if session_id in self.sessions:
            context = self.sessions[session_id]
            if context.state not in [HandshakeState.CONNECTED, HandshakeState.FAILED]:
                await self._fail_handshake(session_id, "Handshake timeout")

    async def _send_error_response(
        self, message: A2AMessage, error: str, transport: Callable[[A2AMessage], None]
    ) -> None:
        """Send error response."""
        error_msg = create_error_message(
            sender_id=self.local_agent.agent_id,
            error_code="HANDSHAKE_ERROR",
            error_message=error,
            correlation_id=message.header.message_id,
        )

        await transport(error_msg)

    async def _safe_callback(self, callback: Callable, *args) -> None:
        """Safely call callback function."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            self.logger.error(f"Callback error: {e}")

    def get_session_status(self, session_id: str) -> Optional[HandshakeState]:
        """Get handshake session status."""
        if session_id in self.sessions:
            return self.sessions[session_id].state
        return None

    def cleanup_expired_sessions(self) -> None:
        """Clean up expired handshake sessions."""
        expired_sessions = [
            session_id for session_id, context in self.sessions.items() if context.is_expired()
        ]

        for session_id in expired_sessions:
            self.logger.warning(f"Cleaning up expired handshake session: {session_id}")
            del self.sessions[session_id]
