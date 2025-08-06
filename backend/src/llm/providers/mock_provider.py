import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from ..model_provider_abstract import ModelProvider, ModelResponse

class MockProvider(ModelProvider):
    """테스트용 Mock 프로바이더"""
    
    async def initialize(self) -> None:
        """Mock 프로바이더 초기화"""
        self.client = "mock_client"
    
    async def generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        """Mock 텍스트 생성"""
        await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션
        
        response_text = f"Mock response for: {prompt[:50]}..."
        tokens_used = len(prompt.split()) + len(response_text.split())
        
        return ModelResponse(
            text=response_text,
            tokens_used=tokens_used,
            finish_reason="stop",
            metadata={
                "model": self.config.name,
                "provider": "mock",
                "temperature": self.config.temperature
            }
        )
    
    async def stream_generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Mock 스트리밍 생성"""
        words = ["Mock", "streaming", "response", "for", "your", "prompt"]
        
        for word in words:
            await asyncio.sleep(0.05)
            yield f"{word} "
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Mock 임베딩 생성"""
        embeddings = []
        for text in texts:
            embedding = [float(hash(text + str(i)) % 100) / 100 for i in range(384)]
            embeddings.append(embedding)
        return embeddings
    
    def estimate_tokens(self, text: str) -> int:
        """토큰 수 추정"""
        return len(text.split())
    
    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        """비용 추정"""
        return (input_tokens * 0.001 + output_tokens * 0.002) / 1000