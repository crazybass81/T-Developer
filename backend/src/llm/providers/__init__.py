"""LLM 프로바이더 모듈"""

from ..base import ModelProviderFactory
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .bedrock_provider import BedrockProvider
from .huggingface_provider import HuggingFaceProvider
from .cohere_provider import CohereProvider


# 25+ 프로바이더 등록
def register_all_providers():
    """모든 프로바이더를 팩토리에 등록"""

    # 주요 프로바이더
    ModelProviderFactory.register("openai", OpenAIProvider)
    ModelProviderFactory.register("anthropic", AnthropicProvider)
    ModelProviderFactory.register("bedrock", BedrockProvider)
    ModelProviderFactory.register("huggingface", HuggingFaceProvider)
    ModelProviderFactory.register("cohere", CohereProvider)

    # 추가 프로바이더들 (구현 예정)
    provider_list = [
        "ai21",
        "google",
        "aleph_alpha",
        "together",
        "replicate",
        "palm",
        "bard",
        "claude",
        "llama",
        "mistral",
        "falcon",
        "vicuna",
        "alpaca",
        "gpt4all",
        "dolly",
        "stablelm",
        "bloom",
        "opt",
        "galactica",
        "codegen",
        "codex",
        "davinci",
        "curie",
        "babbage",
        "ada",
    ]

    # 각 프로바이더에 대한 기본 구현체 등록 (실제로는 개별 구현 필요)
    for provider in provider_list:
        if not ModelProviderFactory.is_registered(provider):
            # 기본 구현체로 등록 (실제 환경에서는 각각 구현)
            ModelProviderFactory.register(provider, OpenAIProvider)


# 자동 등록
register_all_providers()

__all__ = [
    "OpenAIProvider",
    "AnthropicProvider",
    "BedrockProvider",
    "HuggingFaceProvider",
    "CohereProvider",
    "register_all_providers",
]
