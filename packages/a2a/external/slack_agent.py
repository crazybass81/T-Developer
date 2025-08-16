"""Slack integration agent for messaging and communication.

Phase 4: A2A External Integration
P4-T3: External Agent Implementations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from ..protocols import A2AMessage, AgentInfo, CapabilityInfo, ResponseStatus


@dataclass
class SlackConfig:
    """Slack agent configuration.

    Attributes:
        bot_token: Slack bot token
        timeout_seconds: Request timeout
        rate_limit_tier1: Tier 1 rate limit per minute
        rate_limit_tier2: Tier 2 rate limit per minute
    """

    bot_token: str
    timeout_seconds: int = 30
    rate_limit_tier1: int = 100
    rate_limit_tier2: int = 20


class SlackAgent:
    """Slack integration agent for messaging and communication."""

    AGENT_ID = "slack-agent"
    AGENT_NAME = "Slack Communication Agent"
    VERSION = "1.0.0"

    def __init__(self, config: SlackConfig):
        """Initialize Slack agent."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://slack.com/api"

        self.agent_info = self._load_agent_info()

    def _load_agent_info(self) -> AgentInfo:
        """Load agent information."""
        capabilities = [
            CapabilityInfo(
                name="send_message",
                version="1.0.0",
                description="Send a message to a Slack channel or user",
                tags=["message", "send", "slack"],
            ),
            CapabilityInfo(
                name="create_channel",
                version="1.0.0",
                description="Create a new channel",
                tags=["channel", "create", "slack"],
            ),
            CapabilityInfo(
                name="upload_file",
                version="1.0.0",
                description="Upload a file to Slack",
                tags=["file", "upload", "slack"],
            ),
            CapabilityInfo(
                name="get_user_info",
                version="1.0.0",
                description="Get user information",
                tags=["user", "info", "slack"],
            ),
        ]

        return AgentInfo(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            agent_type="external",
            version=self.VERSION,
            description="Agent for Slack messaging and communication",
            capabilities=capabilities,
        )

    async def start(self) -> None:
        """Start the Slack agent."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            headers = {
                "Authorization": f"Bearer {self.config.bot_token}",
                "Content-Type": "application/json",
                "User-Agent": f"T-Developer-{self.AGENT_NAME}/{self.VERSION}",
            }

            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)

        self.logger.info("Slack agent started")

    async def stop(self) -> None:
        """Stop the Slack agent."""
        if self.session:
            await self.session.close()
            self.session = None

        self.logger.info("Slack agent stopped")

    async def handle_request(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming A2A request."""
        try:
            capability = message.payload.capability
            action = message.payload.action or capability
            parameters = message.payload.parameters

            if action == "send_message":
                result = await self.send_message(parameters)
            elif action == "create_channel":
                result = await self.create_channel(parameters)
            elif action == "upload_file":
                result = await self.upload_file(parameters)
            elif action == "get_user_info":
                result = await self.get_user_info(parameters)
            else:
                return message.create_response(
                    status=ResponseStatus.NOT_FOUND, error=f"Unknown action: {action}"
                )

            return message.create_response(status=ResponseStatus.SUCCESS, data=result)

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return message.create_response(status=ResponseStatus.ERROR, error=str(e))

    async def send_message(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send a message to a Slack channel or user."""
        required_fields = ["channel", "text"]
        self._validate_parameters(params, required_fields)

        message_data = {"channel": params["channel"], "text": params["text"]}

        # Add optional parameters
        for field in ["blocks", "attachments", "thread_ts", "username", "icon_emoji", "icon_url"]:
            if params.get(field):
                message_data[field] = params[field]

        url = f"{self.base_url}/chat.postMessage"

        async with self.session.post(url, json=message_data) as response:
            result = await response.json()
            if result.get("ok"):
                return {
                    "ok": True,
                    "channel": result["channel"],
                    "ts": result["ts"],
                    "message": result["message"],
                }
            else:
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")

    async def create_channel(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new channel."""
        required_fields = ["name"]
        self._validate_parameters(params, required_fields)

        channel_data = {"name": params["name"], "is_private": params.get("is_private", False)}

        if params.get("user_ids"):
            channel_data["user_ids"] = params["user_ids"]

        url = f"{self.base_url}/conversations.create"

        async with self.session.post(url, json=channel_data) as response:
            result = await response.json()
            if result.get("ok"):
                return result
            else:
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")

    async def upload_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Upload a file to Slack."""
        required_fields = ["channels"]
        self._validate_parameters(params, required_fields)

        file_data = {"channels": params["channels"]}

        # Add optional parameters
        for field in ["content", "filename", "filetype", "initial_comment", "title", "thread_ts"]:
            if params.get(field):
                file_data[field] = params[field]

        url = f"{self.base_url}/files.upload"

        async with self.session.post(url, json=file_data) as response:
            result = await response.json()
            if result.get("ok"):
                return result
            else:
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")

    async def get_user_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get user information."""
        required_fields = ["user"]
        self._validate_parameters(params, required_fields)

        url = f"{self.base_url}/users.info"
        query_params = {
            "user": params["user"],
            "include_locale": params.get("include_locale", False),
        }

        async with self.session.get(url, params=query_params) as response:
            result = await response.json()
            if result.get("ok"):
                return result
            else:
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")

    async def health_check(self) -> bool:
        """Check Slack API health."""
        try:
            url = f"{self.base_url}/api.test"
            async with self.session.get(url) as response:
                result = await response.json()
                return result.get("ok", False)
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def _validate_parameters(self, params: dict[str, Any], required_fields: list[str]) -> None:
        """Validate request parameters."""
        missing_fields = [field for field in required_fields if field not in params]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

    def get_agent_info(self) -> AgentInfo:
        """Get agent information."""
        return self.agent_info
