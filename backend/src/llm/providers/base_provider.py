from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Optional


@dataclass
class ModelResponse:
    text: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any]


@dataclass
class ModelConfig:
    name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[list] = None


class ModelProvider(ABC):
    def __init__(self, config: ModelConfig):
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        pass

    @abstractmethod
    async def stream_generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        pass


class ModelProviderFactory:
    _providers = {}

    @classmethod
    def register(cls, name: str, provider_class):
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, name: str, config: ModelConfig) -> ModelProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name](config)
