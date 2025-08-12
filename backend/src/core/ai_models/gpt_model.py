"""
GPT-4 AI Model Integration
"""

import os
import json
from typing import Dict, Any, Optional, List
import asyncio
from .base_model import BaseAIModel, ModelResponse


class GPT4Turbo(BaseAIModel):
    """GPT-4 Turbo 모델 통합"""
    
    def __init__(self, api_key: str = None):
        """
        초기화
        
        Args:
            api_key: OpenAI API 키
        """
        super().__init__(api_key or os.getenv('OPENAI_API_KEY'))
        self.model_name = "gpt-4-turbo-preview"
        self.max_context = 128000  # 128K tokens
        
        # Mock 모드 확인
        self.mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        
        if not self.mock_mode and self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                print("openai 패키지가 설치되지 않았습니다. Mock 모드로 실행합니다.")
                self.mock_mode = True
                self.client = None
        else:
            self.client = None
    
    async def complete(self, 
                      prompt: str,
                      temperature: float = 0.7,
                      max_tokens: int = 1000,
                      **kwargs) -> str:
        """
        텍스트 완성
        
        Args:
            prompt: 프롬프트
            temperature: 온도 (0-1)
            max_tokens: 최대 토큰 수
            
        Returns:
            생성된 텍스트
        """
        if self.mock_mode or not self.client:
            return self._mock_complete(prompt, temperature, max_tokens)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes code and provides structured responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=kwargs.get('response_format', {"type": "text"})
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API 오류: {e}")
            return self._mock_complete(prompt, temperature, max_tokens)
    
    async def analyze(self,
                     prompt: str,
                     temperature: float = 0.3,
                     **kwargs) -> str:
        """
        분석 작업 (더 낮은 temperature로 일관성 있는 분석)
        
        Args:
            prompt: 분석 프롬프트
            temperature: 온도 (낮을수록 일관성 있음)
            
        Returns:
            분석 결과
        """
        # JSON 모드로 구조화된 응답 요청
        kwargs['response_format'] = {"type": "json_object"}
        return await self.complete(prompt, temperature, max_tokens=2000, **kwargs)
    
    async def chat(self,
                  messages: List[Dict[str, str]],
                  temperature: float = 0.7,
                  **kwargs) -> str:
        """
        대화형 완성
        
        Args:
            messages: 대화 메시지 리스트
            temperature: 온도
            
        Returns:
            응답 메시지
        """
        if self.mock_mode or not self.client:
            return self._mock_chat(messages, temperature)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI Chat API 오류: {e}")
            return self._mock_chat(messages, temperature)
    
    def _mock_complete(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Mock 완성 응답"""
        # 프롬프트 기반 지능적 응답 생성
        if "validate" in prompt.lower() or "enhance" in prompt.lower():
            return json.dumps({
                "capabilities": [
                    "Natural language processing",
                    "Pattern recognition",
                    "Data analysis",
                    "Code generation",
                    "Error handling",
                    "Async operations"
                ],
                "improvements": [
                    "Add comprehensive error handling",
                    "Implement caching mechanism",
                    "Optimize performance bottlenecks",
                    "Add input validation"
                ],
                "confidence_ratings": {
                    "Natural language processing": 0.95,
                    "Pattern recognition": 0.88,
                    "Data analysis": 0.92,
                    "Code generation": 0.90
                },
                "additional_insights": [
                    "Strong architecture design",
                    "Good separation of concerns",
                    "Scalable implementation"
                ],
                "warnings": []
            }, indent=2)
        
        return f"Mock GPT-4 response for: {prompt[:100]}..."
    
    def _mock_chat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Mock 대화 응답"""
        last_message = messages[-1]['content'] if messages else ""
        return f"Mock GPT-4 chat response to: {last_message[:100]}..."
    
    async def generate_code(self, 
                          specification: str,
                          language: str = "python",
                          **kwargs) -> str:
        """
        코드 생성 특화 메서드
        
        Args:
            specification: 코드 명세
            language: 프로그래밍 언어
            
        Returns:
            생성된 코드
        """
        prompt = f"""
        Generate {language} code for the following specification:
        {specification}
        
        Requirements:
        - Production-ready code
        - Include error handling
        - Add type hints (if applicable)
        - Include docstrings
        - Follow best practices
        
        Return only the code without explanations.
        """
        
        return await self.complete(prompt, temperature=0.3, max_tokens=3000)
    
    async def review_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        코드 리뷰
        
        Args:
            code: 리뷰할 코드
            
        Returns:
            리뷰 결과
        """
        prompt = f"""
        Review the following code and provide analysis in JSON format:
        
        ```
        {code}
        ```
        
        Analyze:
        1. Code quality (1-10)
        2. Security issues
        3. Performance concerns
        4. Best practice violations
        5. Improvement suggestions
        
        Return as JSON.
        """
        
        response = await self.analyze(prompt, temperature=0.2)
        
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to parse response", "raw": response}
    
    async def count_tokens(self, text: str) -> int:
        """토큰 수 계산"""
        # 간단한 추정 (실제로는 tiktoken 사용 필요)
        return len(text) // 4
    
    def is_available(self) -> bool:
        """모델 사용 가능 여부"""
        return bool(self.api_key) or self.mock_mode