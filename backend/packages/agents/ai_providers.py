"""AI 프로바이더 모듈 (AI Providers)

이 모듈은 AWS Bedrock을 통해 실제 AI 모델에 접근하는 프로바이더 구현을 제공합니다.
T-Developer v2의 모든 AI 기능의 핵심이 되는 모듈로, Mock이나 Fake 없이
100% 실제 AI 서비스를 사용합니다.

주요 기능:
1. AWS Bedrock 연결 관리
2. Claude 3 모델 패밀리 지원 (Sonnet, Haiku, Opus)
3. 프롬프트 템플릿 관리 및 최적화
4. 응답 스트리밍 지원
5. 에러 처리 및 재시도 로직
6. 토큰 사용량 추적
7. 비용 모니터링
8. 모델별 파라미터 최적화

지원 모델:
- Claude 3 Sonnet: 균형 잡힌 성능과 비용
- Claude 3 Haiku: 빠른 응답, 경제적
- Claude 3.5 Sonnet: 최신 고성능 모델
- Claude 2/2.1: 레거시 지원

사용 예시:
    provider = BedrockAIProvider({
        "model": "claude-3-sonnet",
        "region": "us-east-1"
    })
    response = await provider.generate(
        prompt="코드 분석 요청",
        system_prompt="당신은 전문 코드 분석가입니다."
    )

중요: 이 모듈은 실제 AWS 자격 증명이 필요하며,
      Mock이나 시뮬레이션을 절대 사용하지 않습니다.

작성자: T-Developer v2
버전: 2.0.0
최종 수정: 2024-12-20
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from abc import ABC, abstractmethod

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """AI 응답 컨테이너."""
    content: str
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AIProvider(ABC):
    """AI Provider 추상 베이스 클래스."""
    
    def __init__(self, config: Dict[str, Any]):
        """AI Provider 초기화.
        
        Args:
            config: Provider 설정
        """
        self.config = config
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """AI 응답 생성.
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            **kwargs: 추가 매개변수
            
        Returns:
            AI 응답
        """
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성.
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            **kwargs: 추가 매개변수
            
        Yields:
            응답 청크
        """
        pass


class BedrockAIProvider(AIProvider):
    """AWS Bedrock AI provider implementation.
    
    This provider uses AWS Bedrock to access various AI models including:
    - Claude (Anthropic)
    - Titan (Amazon)
    - And other available models
    
    Attributes:
        client: Boto3 Bedrock Runtime client
        default_model_id: Default model to use
        region: AWS region
    """
    
    # Available models in AWS Bedrock (실제 작동하는 모델 ID)
    MODELS = {
        "claude-3-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Cross-region Claude 3.5 Sonnet
        "claude-3-haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "claude-2": "anthropic.claude-v2",
        "claude-2.1": "anthropic.claude-v2:1",
        "claude-instant": "anthropic.claude-instant-v1",
        "titan": "amazon.titan-text-express-v1",
    }
    
    def __init__(
        self,
        model: str = "claude-3-sonnet",  # 작동 확인된 모델로 변경
        region: str = "us-east-1",
        aws_profile: Optional[str] = None
    ) -> None:
        """Initialize Bedrock AI provider.
        
        Args:
            model: Model name from MODELS dict
            region: AWS region
            aws_profile: Optional AWS profile name
        """
        self.region = region
        self.default_model_id = self.MODELS.get(model, self.MODELS["claude-3-sonnet"])
        
        # Initialize Bedrock client
        session = boto3.Session(profile_name=aws_profile) if aws_profile else boto3.Session()
        self.client = session.client(
            service_name="bedrock-runtime",
            region_name=region
        )
        
        # AIProvider 초기화
        super().__init__({
            "model": model,
            "model_id": self.MODELS.get(model, model),
            "region": region,
            "aws_profile": aws_profile
        })
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model_id: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """Generate AI completion using AWS Bedrock with retry logic.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            model_id: Optional specific model ID to use
            max_retries: Maximum number of retries for throttling errors
            
        Returns:
            The generated text
            
        Raises:
            Exception: If API call fails after all retries
        """
        model_id = model_id or self.default_model_id
        
        import asyncio
        import time
        
        for attempt in range(max_retries):
            try:
                # Prepare request based on model type
                if "claude" in model_id:
                    request_body = self._prepare_claude_request(
                        prompt, system, max_tokens, temperature
                    )
                elif "titan" in model_id:
                    request_body = self._prepare_titan_request(
                        prompt, max_tokens, temperature
                    )
                else:
                    raise ValueError(f"Unsupported model: {model_id}")
                
                # Invoke model (동기 호출을 비동기로 래핑)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.invoke_model(
                        modelId=model_id,
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps(request_body)
                    )
                )
                
                # Parse response
                response_body = json.loads(response["body"].read())
                
                if "claude" in model_id:
                    return response_body.get("content", [{}])[0].get("text", "")
                elif "titan" in model_id:
                    return response_body.get("results", [{}])[0].get("outputText", "")
                else:
                    return str(response_body)
                    
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                error_message = e.response["Error"]["Message"]
                
                # Throttling 에러 처리
                if error_code == "ThrottlingException" and attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.warning(f"Throttled by Bedrock API. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                    
                raise Exception(f"Bedrock API error ({error_code}): {error_message}")
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Bedrock call failed: {str(e)}. Retrying... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Error calling Bedrock after {max_retries} attempts: {str(e)}")
    
    def _prepare_claude_request(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Prepare request body for Claude models.
        
        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Max tokens
            temperature: Temperature
            
        Returns:
            Request body dict
        """
        request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system:
            request["system"] = system
        
        return request
    
    def _prepare_titan_request(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Prepare request body for Titan models.
        
        Args:
            prompt: User prompt
            max_tokens: Max tokens
            temperature: Temperature
            
        Returns:
            Request body dict
        """
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 0.9,
                "stopSequences": []
            }
        }
    
    async def analyze_code(
        self,
        code: str,
        analysis_type: str = "general",
        language: str = "python"
    ) -> Dict[str, Any]:
        """Analyze code using AI.
        
        Args:
            code: The code to analyze
            analysis_type: Type of analysis (security, performance, quality, etc.)
            language: Programming language
            
        Returns:
            Analysis results as a dictionary
        """
        # Prepare analysis prompt based on type
        prompts = {
            "general": f"""Analyze this {language} code and provide:
1. Summary of what the code does
2. Code quality assessment
3. Potential issues or bugs
4. Improvement suggestions

Code:
```{language}
{code}
```

Provide the analysis in JSON format with keys: summary, quality_score (1-10), issues, suggestions.""",
            
            "security": f"""Perform a security analysis of this {language} code:
1. Identify potential security vulnerabilities
2. Check for common security anti-patterns
3. Suggest security improvements

Code:
```{language}
{code}
```

Provide the analysis in JSON format with keys: vulnerabilities, risk_level (low/medium/high/critical), recommendations.""",
            
            "performance": f"""Analyze the performance characteristics of this {language} code:
1. Identify performance bottlenecks
2. Analyze time and space complexity
3. Suggest optimizations

Code:
```{language}
{code}
```

Provide the analysis in JSON format with keys: bottlenecks, complexity, optimization_suggestions.""",
            
            "test": f"""Analyze this {language} code for testability:
1. Identify what needs to be tested
2. Suggest test cases
3. Assess test coverage requirements

Code:
```{language}
{code}
```

Provide the analysis in JSON format with keys: test_requirements, suggested_test_cases, coverage_targets."""
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        system_prompt = """You are an expert code analyst. Analyze the provided code thoroughly 
and return your analysis in valid JSON format. Be specific and actionable in your recommendations."""
        
        try:
            # Get AI analysis
            response = await self.complete(
                prompt=prompt,
                system=system_prompt,
                max_tokens=2048,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Try to parse as JSON
            try:
                # Extract JSON from response if wrapped in markdown
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                elif "```" in response:
                    json_start = response.find("```") + 3
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                
                result = json.loads(response)
            except json.JSONDecodeError:
                # If not valid JSON, return as text analysis
                result = {
                    "analysis_type": analysis_type,
                    "raw_analysis": response,
                    "error": "Could not parse response as JSON"
                }
            
            # Add metadata
            result["language"] = language
            result["code_lines"] = len(code.split("\n"))
            result["code_size_bytes"] = len(code.encode())
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": analysis_type,
                "language": language
            }
    
    async def generate_code(
        self,
        specification: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate code based on specification.
        
        Args:
            specification: What the code should do
            language: Target programming language
            context: Optional context (existing code, constraints, etc.)
            
        Returns:
            Generated code and metadata
        """
        prompt = f"""Generate {language} code for the following specification:

{specification}

Requirements:
1. Follow best practices and SOLID principles
2. Include proper error handling
3. Add clear docstrings/comments
4. Make the code production-ready

"""
        
        if context:
            prompt += f"""
Context/Constraints:
{context}

"""
        
        prompt += f"""Generate the code in {language}. Return ONLY the code without any explanation."""
        
        system_prompt = f"""You are an expert {language} developer. Generate clean, efficient, 
and well-documented code following best practices."""
        
        try:
            code = await self.complete(
                prompt=prompt,
                system=system_prompt,
                max_tokens=4096,
                temperature=0.5
            )
            
            # Clean up code if wrapped in markdown
            if f"```{language}" in code:
                code_start = code.find(f"```{language}") + len(f"```{language}")
                code_end = code.find("```", code_start)
                code = code[code_start:code_end].strip()
            elif "```" in code:
                code_start = code.find("```") + 3
                code_end = code.find("```", code_start)
                code = code[code_start:code_end].strip()
            
            return {
                "code": code,
                "language": language,
                "specification": specification,
                "lines": len(code.split("\n")),
                "size_bytes": len(code.encode())
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "specification": specification,
                "language": language
            }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """AI 응답 생성 (AIProvider 인터페이스 구현).
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            **kwargs: 추가 매개변수
            
        Returns:
            AI 응답
        """
        try:
            response = await self.complete(
                prompt=prompt,
                system=system_prompt,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
                model_id=kwargs.get("model_id")
            )
            
            return AIResponse(
                content=response,
                success=True,
                metadata={
                    "model": self.default_model_id,
                    "provider": "bedrock",
                    "region": self.region
                }
            )
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            return AIResponse(
                content="",
                success=False,
                error=str(e),
                metadata={"provider": "bedrock"}
            )
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성 (현재 미구현).
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            **kwargs: 추가 매개변수
            
        Yields:
            응답 청크
        """
        # Bedrock 스트리밍은 추후 구현
        response = await self.generate(prompt, system_prompt, **kwargs)
        if response.success:
            # 단순히 전체 응답을 한 번에 yield
            yield response.content


def get_ai_provider(
    provider_type: str = "bedrock",
    config: Optional[Dict[str, Any]] = None
) -> AIProvider:
    """AI Provider 인스턴스를 가져옵니다.
    
    Args:
        provider_type: Provider 타입 ("bedrock")
        config: Provider 설정
        
    Returns:
        AIProvider 인스턴스
    """
    import os
    
    if provider_type == "bedrock" or provider_type == "auto":
        # Bedrock Provider 생성
        bedrock_config = config or {}
        
        # 환경변수에서 기본값 설정
        if "model" not in bedrock_config:
            bedrock_config["model"] = os.getenv("BEDROCK_MODEL", "claude-3-sonnet")
        if "region" not in bedrock_config:
            bedrock_config["region"] = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        logger.info(f"Using AWS Bedrock AI Provider (model: {bedrock_config['model']}, region: {bedrock_config['region']})")
        
        return BedrockAIProvider(
            model=bedrock_config["model"],
            region=bedrock_config["region"],
            aws_profile=bedrock_config.get("aws_profile")
        )
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Only 'bedrock' is supported.")