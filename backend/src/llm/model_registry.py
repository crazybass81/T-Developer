from typing import Dict, List, Optional
from dataclasses import dataclass
from .model_provider_abstract import ModelConfig, ModelProvider, ModelProviderFactory


@dataclass
class ModelInfo:
    """모델 정보"""

    name: str
    provider: str
    description: str
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool = True
    supports_embedding: bool = False


class ModelRegistry:
    """모델 레지스트리 - 사용 가능한 모델들을 관리"""

    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._initialize_default_models()

    def _initialize_default_models(self):
        """기본 모델들 등록"""
        default_models = [
            # OpenAI Models
            ModelInfo(
                "gpt-4",
                "openai",
                "GPT-4 - Most capable model",
                8192,
                0.03,
                0.06,
                True,
                False,
            ),
            ModelInfo(
                "gpt-4-turbo",
                "openai",
                "GPT-4 Turbo - Faster and cheaper",
                128000,
                0.01,
                0.03,
                True,
                False,
            ),
            ModelInfo(
                "gpt-3.5-turbo",
                "openai",
                "GPT-3.5 Turbo - Fast and efficient",
                4096,
                0.0015,
                0.002,
                True,
                False,
            ),
            # Anthropic Models
            ModelInfo(
                "claude-3-opus",
                "anthropic",
                "Claude 3 Opus - Most capable",
                200000,
                0.015,
                0.075,
                True,
                False,
            ),
            ModelInfo(
                "claude-3-sonnet",
                "anthropic",
                "Claude 3 Sonnet - Balanced",
                200000,
                0.003,
                0.015,
                True,
                False,
            ),
            ModelInfo(
                "claude-3-haiku",
                "anthropic",
                "Claude 3 Haiku - Fast",
                200000,
                0.00025,
                0.00125,
                True,
                False,
            ),
            # AWS Bedrock Models
            ModelInfo(
                "amazon.titan-text-express-v1",
                "bedrock",
                "Amazon Titan Text Express",
                8000,
                0.0008,
                0.0016,
                False,
                True,
            ),
            ModelInfo(
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "bedrock",
                "Claude 3 Sonnet on Bedrock",
                200000,
                0.003,
                0.015,
                True,
                False,
            ),
            ModelInfo(
                "meta.llama2-70b-chat-v1",
                "bedrock",
                "Llama 2 70B Chat",
                4096,
                0.00195,
                0.00256,
                False,
                False,
            ),
        ]

        for model in default_models:
            self.register_model(model)

    def register_model(self, model_info: ModelInfo) -> None:
        """모델 등록"""
        self.models[model_info.name] = model_info

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """모델 정보 조회"""
        return self.models.get(model_name)

    def list_models(self, provider: Optional[str] = None) -> List[ModelInfo]:
        """모델 목록 조회"""
        if provider:
            return [
                model for model in self.models.values() if model.provider == provider
            ]
        return list(self.models.values())

    def create_provider(self, model_name: str, **config_overrides) -> ModelProvider:
        """모델 프로바이더 생성"""
        model_info = self.get_model_info(model_name)
        if not model_info:
            raise ValueError(f"Unknown model: {model_name}")

        config = ModelConfig(
            name=model_info.name,
            provider=model_info.provider,
            max_tokens=model_info.max_tokens,
            **config_overrides,
        )

        return ModelProviderFactory.create(model_info.provider, config)


# 전역 모델 레지스트리 인스턴스
model_registry = ModelRegistry()
