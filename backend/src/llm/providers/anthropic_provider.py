import os
from typing import Any, AsyncIterator, Dict, List, Optional

import anthropic

from ..base import ModelProvider, ModelResponse


class AnthropicProvider(ModelProvider):
    """Anthropic Claude 프로바이더"""

    async def initialize(self) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        response = await self.client.messages.create(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.max_tokens,
            temperature=options.get("temperature", self.config.temperature)
            if options
            else self.config.temperature,
        )

        return ModelResponse(
            text=response.content[0].text,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            metadata={"model": response.model},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        async with self.client.messages.stream(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Anthropic doesn't provide embeddings, use a fallback
        raise NotImplementedError("Anthropic doesn't provide embedding models")

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # Claude-3 기준 비용
        return (input_tokens * 0.000015) + (output_tokens * 0.000075)
