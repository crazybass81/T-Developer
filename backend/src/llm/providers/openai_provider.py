import openai
import os
from typing import AsyncIterator, Dict, Any, Optional, List
from ..base import ModelProvider, ModelResponse


class OpenAIProvider(ModelProvider):
    """OpenAI 모델 프로바이더"""

    async def initialize(self) -> None:
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        options = options or {}

        response = await self.client.chat.completions.create(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=options.get("max_tokens", self.config.max_tokens),
            temperature=options.get("temperature", self.config.temperature),
            top_p=options.get("top_p", self.config.top_p),
            frequency_penalty=options.get(
                "frequency_penalty", self.config.frequency_penalty
            ),
            presence_penalty=options.get(
                "presence_penalty", self.config.presence_penalty
            ),
            stop=options.get("stop", self.config.stop_sequences),
        )

        choice = response.choices[0]
        return ModelResponse(
            text=choice.message.content,
            tokens_used=response.usage.total_tokens,
            finish_reason=choice.finish_reason,
            metadata={"model": response.model, "created": response.created},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        options = options or {}

        stream = await self.client.chat.completions.create(
            model=self.config.name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **options
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002", input=texts
        )
        return [data.embedding for data in response.data]

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4  # 대략적 추정

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # GPT-4 기준 비용
        return (input_tokens * 0.00003) + (output_tokens * 0.00006)
