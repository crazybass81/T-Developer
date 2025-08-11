"""
AI Provider Configuration
Manages OpenAI, Anthropic, and AWS Bedrock settings
Integrated with AWS Secrets Manager and Parameter Store
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

# Import AWS Secrets Manager (this will load credentials on import)
try:
    from src.config.aws_secrets import aws_secrets
    AWS_SECRETS_AVAILABLE = True
except ImportError:
    AWS_SECRETS_AVAILABLE = False
    aws_secrets = None

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """AI Provider configuration"""
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4000
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 4000
    
    # AWS Bedrock Configuration
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_region: str = "us-east-1"
    
    # Provider selection
    preferred_provider: str = "bedrock"  # "openai", "anthropic", "bedrock"
    fallback_provider: Optional[str] = "openai"
    
    # Rate limiting
    requests_per_minute: int = 60
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load configuration from environment variables"""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
            
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            anthropic_temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
            anthropic_max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000")),
            
            bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"),
            bedrock_region=os.getenv("AWS_REGION", "us-east-1"),
            
            preferred_provider=os.getenv("AI_PROVIDER", "bedrock"),
            fallback_provider=os.getenv("AI_FALLBACK_PROVIDER", "openai"),
            
            requests_per_minute=int(os.getenv("AI_RATE_LIMIT", "60")),
            enable_caching=os.getenv("AI_ENABLE_CACHE", "true").lower() == "true",
            cache_ttl=int(os.getenv("AI_CACHE_TTL", "3600"))
        )
    
    def get_available_providers(self) -> list:
        """Get list of available AI providers"""
        providers = []
        
        if self.openai_api_key:
            providers.append("openai")
        
        if self.anthropic_api_key:
            providers.append("anthropic")
        
        # Bedrock uses IAM role, always available on AWS
        try:
            import boto3
            providers.append("bedrock")
        except ImportError:
            pass
        
        return providers
    
    def validate(self) -> bool:
        """Validate configuration"""
        available = self.get_available_providers()
        
        if not available:
            logger.warning("No AI providers configured")
            return False
        
        if self.preferred_provider not in available:
            logger.warning(f"Preferred provider {self.preferred_provider} not available")
            if self.fallback_provider and self.fallback_provider in available:
                logger.info(f"Using fallback provider: {self.fallback_provider}")
                self.preferred_provider = self.fallback_provider
            else:
                self.preferred_provider = available[0]
                logger.info(f"Using available provider: {self.preferred_provider}")
        
        return True

# Global configuration instance
ai_config = AIConfig.from_env()