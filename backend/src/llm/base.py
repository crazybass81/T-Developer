"""LLM 기본 클래스 및 인터페이스"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """모델 설정"""
    name: str
    provider: str
    max_tokens: int
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop_sequences: List[str]

@dataclass
class ModelResponse:
    """모델 응답"""
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
        """비용 추정"""
        pass

class ModelProviderFactory:
    """모델 프로바이더 팩토리"""
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        """프로바이더 등록"""
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
    def is_registered(cls, name: str) -> bool:
        """프로바이더 등록 여부 확인"""
        return name in cls._providers
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """등록된 프로바이더 목록"""
        return list(cls._providers.keys())