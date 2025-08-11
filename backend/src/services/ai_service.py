"""
Unified AI Service
Provides abstraction layer for multiple AI providers
"""
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import time

from src.config.ai_config import ai_config

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from AI"""
        pass
    
    @abstractmethod
    async def analyze(self, text: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze text for specific purpose"""
        pass

class BedrockProvider(AIProvider):
    """AWS Bedrock provider"""
    
    def __init__(self):
        try:
            import boto3
            self.client = boto3.client('bedrock-runtime', region_name=ai_config.bedrock_region)
            self.available = True
        except Exception as e:
            logger.warning(f"Bedrock not available: {e}")
            self.available = False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Bedrock"""
        if not self.available:
            return ""
        
        try:
            # Prepare request for Claude on Bedrock
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get("max_tokens", ai_config.bedrock_max_tokens if hasattr(ai_config, 'bedrock_max_tokens') else 4000),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": kwargs.get("temperature", 0.7)
            })
            
            # Call Bedrock
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=ai_config.bedrock_model_id,
                    body=body,
                    contentType='application/json',
                    accept='application/json'
                )
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body.get('content', [{}])[0].get('text', '')
            
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            return ""
    
    async def analyze(self, text: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze using Bedrock"""
        prompt = f"""Analyze the following text for {analysis_type}:

Text: {text}

Provide a structured JSON response with the analysis results."""
        
        response = await self.generate(prompt, **kwargs)
        
        try:
            # Try to parse as JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                return {"analysis": response, "type": analysis_type}
        except:
            return {"analysis": response, "type": analysis_type}

class OpenAIProvider(AIProvider):
    """OpenAI provider"""
    
    def __init__(self):
        self.available = False
        if ai_config.openai_api_key:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=ai_config.openai_api_key)
                self.available = True
            except ImportError:
                logger.warning("OpenAI library not installed")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate using OpenAI"""
        if not self.available:
            return ""
        
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", ai_config.openai_model),
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for software development."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", ai_config.openai_temperature),
                max_tokens=kwargs.get("max_tokens", ai_config.openai_max_tokens)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return ""
    
    async def analyze(self, text: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        prompt = f"""Analyze the following text for {analysis_type}:

Text: {text}

Provide a structured JSON response with the analysis results."""
        
        response = await self.generate(prompt, **kwargs)
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"analysis": response, "type": analysis_type}
        except:
            return {"analysis": response, "type": analysis_type}

class AnthropicProvider(AIProvider):
    """Anthropic provider"""
    
    def __init__(self):
        self.available = False
        if ai_config.anthropic_api_key:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=ai_config.anthropic_api_key)
                self.available = True
            except ImportError:
                logger.warning("Anthropic library not installed")
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Anthropic"""
        if not self.available:
            return ""
        
        try:
            response = await self.client.messages.create(
                model=kwargs.get("model", ai_config.anthropic_model),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get("max_tokens", ai_config.anthropic_max_tokens),
                temperature=kwargs.get("temperature", ai_config.anthropic_temperature)
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return ""
    
    async def analyze(self, text: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze using Anthropic"""
        prompt = f"""Analyze the following text for {analysis_type}:

Text: {text}

Provide a structured JSON response with the analysis results."""
        
        response = await self.generate(prompt, **kwargs)
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"analysis": response, "type": analysis_type}
        except:
            return {"analysis": response, "type": analysis_type}

class MockProvider(AIProvider):
    """Mock provider for testing"""
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response"""
        return f"Mock response for: {prompt[:50]}..."
    
    async def analyze(self, text: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Mock analysis"""
        return {
            "type": analysis_type,
            "text_length": len(text),
            "mock": True,
            "analysis": f"Mock analysis of type {analysis_type}"
        }

class AIService:
    """Unified AI service with provider management"""
    
    def __init__(self):
        self.providers = {}
        self.cache = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize available providers"""
        
        # Initialize Bedrock
        bedrock = BedrockProvider()
        if bedrock.available:
            self.providers["bedrock"] = bedrock
            logger.info("Bedrock provider initialized")
        
        # Initialize OpenAI
        openai = OpenAIProvider()
        if openai.available:
            self.providers["openai"] = openai
            logger.info("OpenAI provider initialized")
        
        # Initialize Anthropic
        anthropic = AnthropicProvider()
        if anthropic.available:
            self.providers["anthropic"] = anthropic
            logger.info("Anthropic provider initialized")
        
        # Always have mock as fallback
        self.providers["mock"] = MockProvider()
        
        # Validate configuration
        if not ai_config.validate():
            logger.warning("AI configuration validation failed, using mock provider")
            ai_config.preferred_provider = "mock"
    
    def get_provider(self, provider_name: Optional[str] = None) -> AIProvider:
        """Get AI provider instance"""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        # Try preferred provider
        if ai_config.preferred_provider in self.providers:
            return self.providers[ai_config.preferred_provider]
        
        # Try fallback provider
        if ai_config.fallback_provider and ai_config.fallback_provider in self.providers:
            return self.providers[ai_config.fallback_provider]
        
        # Return any available provider
        for name, provider in self.providers.items():
            if name != "mock":
                return provider
        
        # Last resort: mock provider
        return self.providers["mock"]
    
    async def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate response using AI provider"""
        
        # Check cache if enabled
        if ai_config.enable_caching:
            cache_key = f"gen_{hash(prompt)}_{provider or ai_config.preferred_provider}"
            if cache_key in self.cache:
                cached_time, cached_response = self.cache[cache_key]
                if time.time() - cached_time < ai_config.cache_ttl:
                    logger.debug("Using cached AI response")
                    return cached_response
        
        # Get provider and generate
        ai_provider = self.get_provider(provider)
        response = await ai_provider.generate(prompt, **kwargs)
        
        # Cache response
        if ai_config.enable_caching and response:
            self.cache[cache_key] = (time.time(), response)
        
        return response
    
    async def analyze(self, text: str, analysis_type: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Analyze text using AI provider"""
        
        # Check cache if enabled
        if ai_config.enable_caching:
            cache_key = f"ana_{hash(text)}_{analysis_type}_{provider or ai_config.preferred_provider}"
            if cache_key in self.cache:
                cached_time, cached_response = self.cache[cache_key]
                if time.time() - cached_time < ai_config.cache_ttl:
                    logger.debug("Using cached AI analysis")
                    return cached_response
        
        # Get provider and analyze
        ai_provider = self.get_provider(provider)
        response = await ai_provider.analyze(text, analysis_type, **kwargs)
        
        # Cache response
        if ai_config.enable_caching and response:
            self.cache[cache_key] = (time.time(), response)
        
        return response
    
    async def analyze_code_requirements(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for code requirements"""
        prompt = f"""Analyze the following user input for a software project:

"{user_input}"

Extract and return a JSON object with:
- project_type: web_app, mobile_app, api, cli, library, etc.
- main_features: list of key features requested
- technologies: suggested technologies/frameworks
- complexity: simple, medium, complex
- estimated_files: approximate number of files needed
- requirements: list of functional requirements
- constraints: any mentioned constraints or preferences
"""
        
        result = await self.analyze(user_input, "requirements")
        return result
    
    async def generate_code(self, specification: Dict[str, Any]) -> str:
        """Generate code based on specification"""
        prompt = f"""Generate production-ready code based on this specification:

Project: {specification.get('project_name', 'Unknown')}
Type: {specification.get('project_type', 'web_app')}
Framework: {specification.get('framework', 'react')}
Features: {specification.get('features', [])}
Requirements: {specification.get('requirements', [])}

Generate complete, working code with proper structure, error handling, and best practices.
Focus on the main application file first."""
        
        return await self.generate(prompt)
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("AI service cache cleared")

# Global AI service instance
ai_service = AIService()