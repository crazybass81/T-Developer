import httpx
import os
from typing import AsyncIterator, Dict, Any, Optional, List
from ..base import ModelProvider, ModelResponse

class HuggingFaceProvider(ModelProvider):
    """HuggingFace 모델 프로바이더"""
    
    async def initialize(self) -> None:
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"},
            timeout=30.0
        )
        self.base_url = "https://api-inference.huggingface.co/models"
    
    async def generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "do_sample": True
            }
        }
        
        response = await self.client.post(
            f"{self.base_url}/{self.config.name}",
            json=payload
        )
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '')
            # Remove input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return ModelResponse(
                text=generated_text,
                tokens_used=len(generated_text.split()),  # Rough estimate
                finish_reason='stop',
                metadata={'model': self.config.name}
            )
        
        raise Exception(f"Unexpected response: {result}")
    
    async def stream_generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        # HuggingFace doesn't support streaming by default
        result = await self.generate(prompt, options)
        yield result.text
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = await self.client.post(
                f"{self.base_url}/sentence-transformers/all-MiniLM-L6-v2",
                json={"inputs": text}
            )
            embeddings.append(response.json())
        return embeddings
    
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())
    
    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        # HuggingFace Inference API는 무료 또는 매우 저렴
        return 0.0