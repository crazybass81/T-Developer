import os
from typing import Any, AsyncIterator, Dict, List, Optional

import openai

from .base_provider import ModelProvider, ModelResponse


class AzureProvider(ModelProvider):
    """Azure OpenAI 모델 프로바이더"""

    async def initialize(self) -> None:
        self.client = openai.AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        response = await self.client.chat.completions.create(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        choice = response.choices[0]
        return ModelResponse(
            text=choice.message.content,
            tokens_used=response.usage.total_tokens,
            finish_reason=choice.finish_reason,
            metadata={"model": response.model},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(model="text-embedding-ada-002", input=texts)
        return [data.embedding for data in response.data]

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * 0.00003) + (output_tokens * 0.00006)
