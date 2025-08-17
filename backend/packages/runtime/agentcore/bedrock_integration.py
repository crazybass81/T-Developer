"""AWS Bedrock integration for Claude 3 model invocation.

Phase 2: AWS Integration
P2-T1: Bedrock Integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


# Type definitions
class BedrockConfig(Protocol):
    """Type-safe Bedrock configuration."""

    region: str
    model_id: str
    max_tokens: int
    temperature: float
    top_p: float
    timeout: int
    retry_attempts: int


@dataclass
class TokenUsage:
    """Token usage tracking.

    Attributes:
        input_tokens: Number of input tokens consumed
        output_tokens: Number of output tokens generated
        total_tokens: Total tokens used
        cost_usd: Estimated cost in USD
    """

    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float


@dataclass
class BedrockResponse:
    """Response from Bedrock model invocation.

    Attributes:
        success: Whether the invocation was successful
        content: Generated text content
        token_usage: Token consumption details
        duration_ms: Response time in milliseconds
        error: Error message if unsuccessful
        metadata: Additional response metadata
    """

    success: bool
    content: str = ""
    token_usage: Optional[TokenUsage] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamChunk:
    """Streaming response chunk.

    Attributes:
        content: Text content in this chunk
        is_final: Whether this is the final chunk
        token_count: Tokens in this chunk
        metadata: Chunk metadata
    """

    content: str
    is_final: bool = False
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """Rate limiter for Bedrock API calls."""

    def __init__(self, max_requests_per_minute: int = 300):
        """Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_requests = max_requests_per_minute
        self.requests: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self._lock:
            current_time = time.time()

            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests if current_time - req_time < 60]

            # Check if we're under the limit
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = min(self.requests)
                wait_time = 60 - (current_time - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            # Record this request
            self.requests.append(current_time)


class TokenManager:
    """Token usage tracking and cost estimation."""

    # Claude 3 pricing (per 1K tokens) - adjust based on current AWS pricing
    PRICING = {
        "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
        "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
        "anthropic.claude-3-opus-20240229-v1:0": {"input": 0.015, "output": 0.075},
    }

    def __init__(self):
        """Initialize token manager."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self._lock = asyncio.Lock()

    async def record_usage(
        self, model_id: str, input_tokens: int, output_tokens: int
    ) -> TokenUsage:
        """Record token usage and calculate cost.

        Args:
            model_id: Bedrock model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Token usage details including cost
        """
        async with self._lock:
            # Calculate cost
            pricing = self.PRICING.get(model_id, {"input": 0.003, "output": 0.015})
            cost = input_tokens / 1000 * pricing["input"] + output_tokens / 1000 * pricing["output"]

            # Update totals
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost

            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost,
            )

    def get_usage_summary(self) -> dict[str, Any]:
        """Get total usage summary."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
        }


class BedrockClient:
    """AWS Bedrock client for Claude 3 model invocation."""

    DEFAULT_CONFIG = {
        "region": "us-east-1",
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 0.9,
        "timeout": 30,
        "retry_attempts": 3,
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize Bedrock client.

        Args:
            config: Client configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self._validate_config()

        # Initialize AWS client
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.config["region"],
            config=Config(
                retries={"max_attempts": self.config["retry_attempts"]},
                read_timeout=self.config["timeout"],
            ),
        )

        self.rate_limiter = RateLimiter()
        self.token_manager = TokenManager()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_config(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ["region", "model_id", "max_tokens"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required config field: {field}")

        if self.config["max_tokens"] <= 0:
            raise ValueError("max_tokens must be positive")

        if not 0 <= self.config["temperature"] <= 1:
            raise ValueError("temperature must be between 0 and 1")

        if not 0 <= self.config["top_p"] <= 1:
            raise ValueError("top_p must be between 0 and 1")

    async def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> BedrockResponse:
        """Invoke Claude 3 model with prompt.

        Args:
            prompt: Input prompt for the model
            system_prompt: Optional system prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            **kwargs: Additional model parameters

        Returns:
            Model response with content and metadata
        """
        start_time = time.time()

        try:
            # Rate limiting
            await self.rate_limiter.acquire()

            # Prepare request
            request_body = self._build_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.config["max_tokens"],
                temperature=temperature or self.config["temperature"],
                **kwargs,
            )

            # Call Bedrock
            response = await self._call_bedrock(request_body)

            # Process response
            return await self._process_response(response, start_time)

        except Exception as e:
            self.logger.error(f"Bedrock invocation failed: {e}")
            return BedrockResponse(
                success=False, error=str(e), duration_ms=int((time.time() - start_time) * 1000)
            )

    async def invoke_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Invoke Claude 3 model with streaming response.

        Args:
            prompt: Input prompt for the model
            system_prompt: Optional system prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            **kwargs: Additional model parameters

        Yields:
            Stream chunks with partial content
        """
        try:
            # Rate limiting
            await self.rate_limiter.acquire()

            # Prepare request
            request_body = self._build_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens or self.config["max_tokens"],
                temperature=temperature or self.config["temperature"],
                stream=True,
                **kwargs,
            )

            # Call Bedrock with streaming
            response = await self._call_bedrock_stream(request_body)

            # Yield chunks
            async for chunk in self._process_stream(response):
                yield chunk

        except Exception as e:
            self.logger.error(f"Bedrock streaming failed: {e}")
            yield StreamChunk(content="", is_final=True, metadata={"error": str(e)})

    def _build_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build request body for Bedrock API.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream response
            **kwargs: Additional parameters

        Returns:
            Request body dictionary
        """
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Build request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": self.config["top_p"],
            "messages": messages,
        }

        # Add any additional parameters
        request_body.update(kwargs)

        return request_body

    async def _call_bedrock(self, request_body: dict[str, Any]) -> dict[str, Any]:
        """Call Bedrock API synchronously.

        Args:
            request_body: Request body dictionary

        Returns:
            Raw API response

        Raises:
            ClientError: If API call fails
        """
        loop = asyncio.get_event_loop()

        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=self.config["model_id"],
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                ),
            )

            return json.loads(response["body"].read())

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ThrottlingException":
                # Exponential backoff for throttling
                await asyncio.sleep(2 ** self.config["retry_attempts"])
                raise
            else:
                raise

    async def _call_bedrock_stream(self, request_body: dict[str, Any]) -> Any:
        """Call Bedrock API with streaming.

        Args:
            request_body: Request body dictionary

        Returns:
            Streaming response object
        """
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: self.client.invoke_model_with_response_stream(
                modelId=self.config["model_id"],
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            ),
        )

        return response["body"]

    async def _process_response(
        self, response: dict[str, Any], start_time: float
    ) -> BedrockResponse:
        """Process synchronous response.

        Args:
            response: Raw API response
            start_time: Request start time

        Returns:
            Processed response
        """
        try:
            # Extract content
            content = response.get("content", [{}])[0].get("text", "")

            # Extract token usage
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            # Record usage
            token_usage = await self.token_manager.record_usage(
                self.config["model_id"], input_tokens, output_tokens
            )

            return BedrockResponse(
                success=True,
                content=content,
                token_usage=token_usage,
                duration_ms=int((time.time() - start_time) * 1000),
                metadata={"stop_reason": response.get("stop_reason")},
            )

        except Exception as e:
            return BedrockResponse(
                success=False,
                error=f"Response processing failed: {e}",
                duration_ms=int((time.time() - start_time) * 1000),
            )

    async def _process_stream(self, stream: Any) -> AsyncGenerator[StreamChunk, None]:
        """Process streaming response.

        Args:
            stream: Bedrock streaming response

        Yields:
            Stream chunks
        """
        try:
            for event in stream:
                if "chunk" in event:
                    chunk_data = json.loads(event["chunk"]["bytes"])

                    if chunk_data["type"] == "content_block_delta":
                        delta = chunk_data.get("delta", {})
                        content = delta.get("text", "")

                        yield StreamChunk(content=content, is_final=False)

                    elif chunk_data["type"] == "message_stop":
                        yield StreamChunk(content="", is_final=True, metadata=chunk_data)

        except Exception as e:
            self.logger.error(f"Stream processing error: {e}")
            yield StreamChunk(content="", is_final=True, metadata={"error": str(e)})

    def get_usage_summary(self) -> dict[str, Any]:
        """Get token usage summary."""
        return self.token_manager.get_usage_summary()

    async def health_check(self) -> bool:
        """Check if Bedrock service is accessible.

        Returns:
            True if service is healthy
        """
        try:
            # Simple test invocation
            response = await self.invoke(prompt="Hello", max_tokens=10)
            return response.success
        except Exception:
            return False


class BedrockService:
    """High-level service for Bedrock operations."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize Bedrock service.

        Args:
            config: Service configuration
        """
        self.client = BedrockClient(config)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_text(
        self, prompt: str, system_prompt: Optional[str] = None, stream: bool = False, **kwargs: Any
    ) -> BedrockResponse | AsyncGenerator[StreamChunk, None]:
        """Generate text using Claude 3.

        Args:
            prompt: Input prompt
            system_prompt: System prompt
            stream: Whether to stream response
            **kwargs: Additional parameters

        Returns:
            Response or stream generator
        """
        if stream:
            return self.client.invoke_stream(prompt=prompt, system_prompt=system_prompt, **kwargs)
        else:
            return await self.client.invoke(prompt=prompt, system_prompt=system_prompt, **kwargs)

    async def batch_generate(
        self,
        prompts: list[str],
        system_prompt: Optional[str] = None,
        concurrency: int = 5,
        **kwargs: Any,
    ) -> list[BedrockResponse]:
        """Generate text for multiple prompts concurrently.

        Args:
            prompts: List of input prompts
            system_prompt: System prompt
            concurrency: Maximum concurrent requests
            **kwargs: Additional parameters

        Returns:
            List of responses
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def process_prompt(prompt: str) -> BedrockResponse:
            async with semaphore:
                return await self.client.invoke(
                    prompt=prompt, system_prompt=system_prompt, **kwargs
                )

        tasks = [process_prompt(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

    async def shutdown(self) -> None:
        """Shutdown the service."""
        self.logger.info("Bedrock service shutdown complete")
