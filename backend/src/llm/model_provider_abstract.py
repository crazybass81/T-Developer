from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum

@dataclass
class ModelConfig:
    name: str
    provider: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = None

    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []

@dataclass
class ModelResponse:
    text: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any]

class ModelProvider(ABC):
    """모든 LLM 프로바이더의 추상 기본 클래스"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        
    @abstractmethod
    async def initialize(self) -> None:
        """프로바이더 초기화"""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        """텍스트 생성"""
        pass
    
    @abstractmethod
    async def stream_generate(
        self, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """스트리밍 텍스트 생성"""
        pass
    
    @abstractmethod
    async def embed(
        self, 
        texts: List[str]
    ) -> List[List[float]]:
        """텍스트 임베딩 생성"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """토큰 수 추정"""
        pass
    
    @abstractmethod
    def get_cost_estimate(
        self, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """비용 추정 (USD)"""
        pass

class ModelProviderFactory:
    """모델 프로바이더 팩토리"""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        """프로바이더 등록"""
        if not issubclass(provider_class, ModelProvider):
            raise TypeError(f"{provider_class} must be a subclass of ModelProvider")
        cls._providers[name] = provider_class
    
    @classmethod
    def create(
        cls, 
        provider_name: str, 
        config: ModelConfig
    ) -> ModelProvider:
        """프로바이더 인스턴스 생성"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """등록된 프로바이더 목록 반환"""
        return list(cls._providers.keys())