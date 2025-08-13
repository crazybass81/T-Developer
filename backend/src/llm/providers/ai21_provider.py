import os
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from .base_provider import ModelProvider, ModelResponse


class AI21Provider(ModelProvider):
    """AI21 Labs 모델 프로바이더"""

    async def initialize(self) -> None:
        self.api_key = os.getenv("AI21_API_KEY")
        self.base_url = "https://api.ai21.com/studio/v1"
        self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_key}"})

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        payload = {
            "prompt": prompt,
            "maxTokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "topP": self.config.top_p,
            "stopSequences": self.config.stop_sequences,
        }

        response = await self.client.post(
            f"{self.base_url}/{self.config.name}/complete", json=payload
        )

        result = response.json()
        completion = result["completions"][0]

        return ModelResponse(
            text=completion["data"]["text"],
            tokens_used=result["prompt"]["tokens"] + completion["data"]["tokens"],
            finish_reason=completion["finishReason"]["reason"],
            metadata={"model": self.config.name},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        # AI21 doesn't support streaming, fallback to regular generation
        result = await self.generate(prompt, options)
        yield result.text

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # AI21 doesn't provide embeddings, use placeholder
        return [[0.0] * 768 for _ in texts]

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # AI21 pricing
        return (input_tokens * 0.000025) + (output_tokens * 0.000025)
