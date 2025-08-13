import os
from typing import Any, AsyncIterator, Dict, List, Optional

import google.generativeai as genai

from .base_provider import ModelProvider, ModelResponse


class GoogleProvider(ModelProvider):
    """Google Gemini 프로바이더"""

    async def initialize(self) -> None:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.config.name)

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            stop_sequences=self.config.stop_sequences,
        )

        response = await self.model.generate_content_async(
            prompt, generation_config=generation_config
        )

        return ModelResponse(
            text=response.text,
            tokens_used=response.usage_metadata.total_token_count,
            finish_reason=response.candidates[0].finish_reason.name,
            metadata={"model": self.config.name},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        response = await self.model.generate_content_async(prompt, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            result = genai.embed_content(model="models/embedding-001", content=text)
            embeddings.append(result["embedding"])
        return embeddings

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * 0.000125) + (output_tokens * 0.000375)
