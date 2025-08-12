"""
Claude AI Model Integration
"""

import os
import json
from typing import Dict, Any, Optional, List
import asyncio
from .base_model import BaseAIModel, ModelResponse


class Claude3Opus(BaseAIModel):
    """Claude 3 Opus 모델 통합"""
    
    def __init__(self, api_key: str = None):
        """
        초기화
        
        Args:
            api_key: Anthropic API 키
        """
        super().__init__(api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.model_name = "claude-3-opus-20240229"
        self.max_context = 200000  # 200K tokens
        
        # Mock 모드 확인
        self.mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
        
        if not self.mock_mode and self.api_key:
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                print("anthropic 패키지가 설치되지 않았습니다. Mock 모드로 실행합니다.")
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
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Claude API 오류: {e}")
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
        # 분석 작업은 더 긴 응답이 필요할 수 있음
        return await self.complete(prompt, temperature, max_tokens=2000)
    
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
            # Anthropic 형식으로 변환
            formatted_messages = []
            for msg in messages:
                role = msg.get('role', 'user')
                if role == 'system':
                    # Claude는 system 메시지를 user 메시지로 처리
                    formatted_messages.append({
                        "role": "user",
                        "content": f"System: {msg['content']}"
                    })
                else:
                    formatted_messages.append({
                        "role": role,
                        "content": msg['content']
                    })
            
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                temperature=temperature,
                messages=formatted_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Claude Chat API 오류: {e}")
            return self._mock_chat(messages, temperature)
    
    def _mock_complete(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Mock 완성 응답"""
        # 프롬프트 기반 지능적 응답 생성
        if "analyze" in prompt.lower() or "identify" in prompt.lower():
            return json.dumps({
                "capabilities": [
                    "Natural language processing",
                    "Pattern recognition",
                    "Data analysis",
                    "Code generation"
                ],
                "io_patterns": {
                    "input": ["text", "structured_data"],
                    "output": ["analysis", "recommendations"]
                },
                "dependencies": ["core_libraries"],
                "performance": {
                    "latency": 150,
                    "memory": 100,
                    "cpu_intensity": "medium"
                },
                "use_cases": [
                    "Automated analysis",
                    "Pattern detection",
                    "Insight generation"
                ],
                "quality_metrics": {
                    "accuracy": 0.92,
                    "reliability": 0.95
                }
            }, indent=2)
        
        return f"Mock Claude response for: {prompt[:100]}..."
    
    def _mock_chat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Mock 대화 응답"""
        last_message = messages[-1]['content'] if messages else ""
        return f"Mock Claude chat response to: {last_message[:100]}..."
    
    async def count_tokens(self, text: str) -> int:
        """토큰 수 계산"""
        # 간단한 추정 (실제로는 tokenizer 사용 필요)
        return len(text) // 4
    
    def is_available(self) -> bool:
        """모델 사용 가능 여부"""
        return bool(self.api_key) or self.mock_mode