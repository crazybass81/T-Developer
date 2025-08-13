import replicate
import os
from typing import AsyncIterator, Dict, Any, Optional, List
from .base_provider import ModelProvider, ModelResponse


class ReplicateProvider(ModelProvider):
    """Replicate 모델 프로바이더"""

    async def initialize(self) -> None:
        self.client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        output = self.client.run(
            self.config.name,
            input={
                "prompt": prompt,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            },
        )

        text = "".join(output) if isinstance(output, list) else str(output)
        return ModelResponse(
            text=text,
            tokens_used=len(text.split()),
            finish_reason="stop",
            metadata={"model": self.config.name},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        for event in self.client.stream(
            self.config.name,
            input={"prompt": prompt, "max_tokens": self.config.max_tokens},
        ):
            yield str(event)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * 768 for _ in texts]

    def estimate_tokens(self, text: str) -> int:
        return len(text.split())

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens + output_tokens) * 0.00001
