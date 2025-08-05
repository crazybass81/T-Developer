# backend/src/agents/nl_input/context_optimizer.py
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class ContextWindow:
    size: int
    overlap: int
    priority: float

class ContextOptimizer:
    """컨텍스트 관리 최적화"""

    def __init__(self):
        self.max_context_size = 8192  # tokens
        self.context_windows = []
        self.priority_calculator = PriorityCalculator()

    async def optimize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 최적화"""
        
        # 컨텍스트 크기 확인
        if self._calculate_context_size(context) <= self.max_context_size:
            return context
        
        # 우선순위 기반 압축
        optimized = await self._compress_by_priority(context)
        
        # 윈도우 기반 분할
        if self._calculate_context_size(optimized) > self.max_context_size:
            optimized = await self._split_into_windows(optimized)
        
        return optimized

    async def manage_long_term_memory(self, session_id: str, context: Dict[str, Any]) -> None:
        """장기 메모리 관리"""
        
        # 중요한 정보 추출
        important_info = await self._extract_important_info(context)
        
        # 메모리에 저장
        await self._store_in_memory(session_id, important_info)
        
        # 오래된 메모리 정리
        await self._cleanup_old_memory(session_id)

    async def retrieve_relevant_context(self, session_id: str, query: str) -> Dict[str, Any]:
        """관련 컨텍스트 검색"""
        
        # 현재 세션 컨텍스트
        current_context = await self._get_current_context(session_id)
        
        # 관련 히스토리 검색
        relevant_history = await self._search_relevant_history(session_id, query)
        
        # 컨텍스트 병합
        merged_context = await self._merge_contexts(current_context, relevant_history)
        
        return merged_context

    def _calculate_context_size(self, context: Dict[str, Any]) -> int:
        """컨텍스트 크기 계산 (토큰 수)"""
        text_content = str(context)
        return len(text_content.split()) * 1.3  # 대략적인 토큰 수

    async def _compress_by_priority(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """우선순위 기반 압축"""
        
        # 각 컨텍스트 요소의 우선순위 계산
        prioritized_items = []
        for key, value in context.items():
            priority = await self.priority_calculator.calculate(key, value)
            prioritized_items.append((key, value, priority))
        
        # 우선순위 순으로 정렬
        prioritized_items.sort(key=lambda x: x[2], reverse=True)
        
        # 크기 제한 내에서 선택
        compressed = {}
        current_size = 0
        
        for key, value, priority in prioritized_items:
            item_size = len(str(value).split()) * 1.3
            if current_size + item_size <= self.max_context_size:
                compressed[key] = value
                current_size += item_size
            else:
                break
        
        return compressed

    async def _split_into_windows(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """윈도우 기반 분할"""
        
        # 컨텍스트를 논리적 단위로 분할
        windows = []
        current_window = {}
        current_size = 0
        
        for key, value in context.items():
            item_size = len(str(value).split()) * 1.3
            
            if current_size + item_size > self.max_context_size:
                if current_window:
                    windows.append(current_window)
                current_window = {key: value}
                current_size = item_size
            else:
                current_window[key] = value
                current_size += item_size
        
        if current_window:
            windows.append(current_window)
        
        # 첫 번째 윈도우 반환 (가장 중요한 컨텍스트)
        return windows[0] if windows else {}

class PriorityCalculator:
    """우선순위 계산기"""
    
    async def calculate(self, key: str, value: Any) -> float:
        """우선순위 계산"""
        
        # 키 기반 우선순위
        key_priorities = {
            'requirements': 1.0,
            'constraints': 0.9,
            'goals': 0.8,
            'context': 0.7,
            'history': 0.5
        }
        
        base_priority = key_priorities.get(key, 0.5)
        
        # 값 기반 조정
        if isinstance(value, dict):
            base_priority *= 1.1  # 구조화된 데이터 우선
        elif isinstance(value, list) and len(value) > 0:
            base_priority *= 1.05  # 리스트 데이터
        
        return min(base_priority, 1.0)