from typing import Any, Dict, List, Optional

from .model_provider_abstract import ModelConfig, ModelProvider, ModelProviderFactory
from .providers.bedrock_provider import BedrockProvider
from .providers.openai_provider import OpenAIProvider


class ModelManager:
    """LLM 모델 관리자"""

    def __init__(self):
        self.providers: Dict[str, ModelProvider] = {}
        self.default_configs = self._load_default_configs()
        self._register_providers()

    def _register_providers(self):
        """프로바이더 등록"""
        ModelProviderFactory.register("openai", OpenAIProvider)
        ModelProviderFactory.register("bedrock", BedrockProvider)

    def _load_default_configs(self) -> Dict[str, ModelConfig]:
        """기본 모델 설정 로드"""
        return {
            "gpt-4": ModelConfig(
                name="gpt-4",
                provider="openai",
                max_tokens=4096,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop_sequences=[],
            ),
            "claude-3-sonnet": ModelConfig(
                name="anthropic.claude-3-sonnet-20240229-v1:0",
                provider="bedrock",
                max_tokens=4096,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop_sequences=[],
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                max_tokens=4096,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop_sequences=[],
            ),
        }

    async def get_provider(self, model_name: str) -> ModelProvider:
        """모델 프로바이더 가져오기"""
        if model_name not in self.providers:
            if model_name not in self.default_configs:
                raise ValueError(f"Unknown model: {model_name}")

            config = self.default_configs[model_name]
            provider = ModelProviderFactory.create(config.provider, config)
            await provider.initialize()
            self.providers[model_name] = provider

        return self.providers[model_name]

    async def generate(
        self, model_name: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ):
        """텍스트 생성"""
        provider = await self.get_provider(model_name)
        return await provider.generate(prompt, options)

    async def stream_generate(
        self, model_name: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ):
        """스트리밍 텍스트 생성"""
        provider = await self.get_provider(model_name)
        async for chunk in provider.stream_generate(prompt, options):
            yield chunk

    def list_models(self) -> List[str]:
        """사용 가능한 모델 목록"""
        return list(self.default_configs.keys())

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """모델 정보 조회"""
        if model_name not in self.default_configs:
            raise ValueError(f"Unknown model: {model_name}")

        config = self.default_configs[model_name]
        return {
            "name": config.name,
            "provider": config.provider,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
