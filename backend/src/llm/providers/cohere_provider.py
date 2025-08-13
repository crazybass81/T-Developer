import cohere
import os
from typing import AsyncIterator, Dict, Any, Optional, List
from ..base import ModelProvider, ModelResponse


class CohereProvider(ModelProvider):
    """Cohere 모델 프로바이더"""

    async def initialize(self) -> None:
        self.client = cohere.AsyncClient(api_key=os.getenv("COHERE_API_KEY"))

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        response = await self.client.generate(
            model=self.config.name,
            prompt=prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            p=self.config.top_p,
            stop_sequences=self.config.stop_sequences,
        )

        generation = response.generations[0]
        return ModelResponse(
            text=generation.text,
            tokens_used=response.meta.billed_units.input_tokens
            + response.meta.billed_units.output_tokens,
            finish_reason=generation.finish_reason,
            metadata={"model": self.config.name},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        stream = await self.client.generate_stream(
            model=self.config.name,
            prompt=prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        async for token in stream:
            if token.event_type == "text-generation":
                yield token.text

    async def embed(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embed(texts=texts, model="embed-english-v3.0")
        return response.embeddings

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # Cohere 비용 (Command 모델 기준)
        return (input_tokens * 0.000015) + (output_tokens * 0.000015)
