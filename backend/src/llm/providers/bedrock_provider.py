import boto3
import json
import os
from typing import AsyncIterator, Dict, Any, Optional, List
from ..base import ModelProvider, ModelResponse


class BedrockProvider(ModelProvider):
    """AWS Bedrock 프로바이더"""

    async def initialize(self) -> None:
        self.client = boto3.client(
            "bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1")
        )

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        body = json.dumps(
            {
                "prompt": prompt,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            }
        )

        response = self.client.invoke_model(
            modelId=self.config.name,
            body=body,
            accept="application/json",
            contentType="application/json",
        )

        result = json.loads(response["body"].read())

        return ModelResponse(
            text=result.get("completion", result.get("generated_text", "")),
            tokens_used=result.get("token_count", 0),
            finish_reason=result.get("stop_reason", "stop"),
            metadata={"model_id": self.config.name},
        )

    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        # Bedrock streaming implementation
        body = json.dumps(
            {
                "prompt": prompt,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
        )

        response = self.client.invoke_model_with_response_stream(
            modelId=self.config.name, body=body
        )

        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if "completion" in chunk:
                yield chunk["completion"]

    async def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            body = json.dumps({"inputText": text})
            response = self.client.invoke_model(
                modelId="amazon.titan-embed-text-v1", body=body
            )
            result = json.loads(response["body"].read())
            embeddings.append(result["embedding"])
        return embeddings

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # Bedrock 모델별 비용 (Claude 기준)
        return (input_tokens * 0.000008) + (output_tokens * 0.000024)
