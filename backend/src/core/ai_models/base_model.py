"""
Base AI Model Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
from dataclasses import dataclass


@dataclass
class ModelResponse:
    """AI 모델 응답"""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str
    metadata: Dict[str, Any] = None


class BaseAIModel(ABC):
    """AI 모델 기본 인터페이스"""
    
    def __init__(self, api_key: str = None):
        """
        초기화
        
        Args:
            api_key: API 키
        """
        self.api_key = api_key
        self.model_name = ""
        self.max_retries = 3
        self.timeout = 30
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def analyze(self,
                     prompt: str,
                     temperature: float = 0.3,
                     **kwargs) -> str:
        """
        분석 작업
        
        Args:
            prompt: 분석 프롬프트
            temperature: 온도 (낮을수록 일관성 있음)
            
        Returns:
            분석 결과
        """
        pass
    
    @abstractmethod
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
        pass
    
    async def retry_with_backoff(self, func, *args, **kwargs):
        """지수 백오프로 재시도"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    def validate_response(self, response: str) -> bool:
        """응답 유효성 검증"""
        if not response or len(response.strip()) == 0:
            return False
        return True
    
    def format_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """프롬프트 포맷팅"""
        if context:
            for key, value in context.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt