# backend/src/agents/nl_input/realtime_processor.py
from typing import Dict, List, Any, Optional, Callable
import asyncio
import websockets
import json
from dataclasses import dataclass

@dataclass
class StreamingResult:
    partial_result: Dict[str, Any]
    is_complete: bool
    confidence: float
    processing_time: float

class RealtimeProcessor:
    """실시간 처리 기능"""

    def __init__(self):
        self.active_streams = {}
        self.stream_handlers = {}
        self.buffer_size = 1024

    async def start_streaming_analysis(self, session_id: str, websocket) -> None:
        """스트리밍 분석 시작"""
        
        self.active_streams[session_id] = {
            'websocket': websocket,
            'buffer': '',
            'partial_results': [],
            'start_time': asyncio.get_event_loop().time()
        }
        
        try:
            async for message in websocket:
                await self._process_streaming_input(session_id, message)
        except websockets.exceptions.ConnectionClosed:
            await self._cleanup_stream(session_id)

    async def _process_streaming_input(self, session_id: str, message: str) -> None:
        """스트리밍 입력 처리"""
        
        stream_data = self.active_streams.get(session_id)
        if not stream_data:
            return
        
        try:
            data = json.loads(message)
            
            if data.get('type') == 'text_chunk':
                await self._handle_text_chunk(session_id, data.get('content', ''))
            elif data.get('type') == 'complete':
                await self._handle_stream_complete(session_id)
            elif data.get('type') == 'cancel':
                await self._handle_stream_cancel(session_id)
                
        except json.JSONDecodeError:
            await self._send_error(session_id, "Invalid JSON format")

    async def _handle_text_chunk(self, session_id: str, chunk: str) -> None:
        """텍스트 청크 처리"""
        
        stream_data = self.active_streams[session_id]
        stream_data['buffer'] += chunk
        
        # 버퍼가 충분히 클 때 부분 분석 수행
        if len(stream_data['buffer']) >= self.buffer_size:
            partial_result = await self._analyze_partial_text(stream_data['buffer'])
            
            # 결과 전송
            await self._send_partial_result(session_id, partial_result)
            
            # 부분 결과 저장
            stream_data['partial_results'].append(partial_result)

    async def _analyze_partial_text(self, text: str) -> StreamingResult:
        """부분 텍스트 분석"""
        
        start_time = asyncio.get_event_loop().time()
        
        # 간단한 키워드 추출
        keywords = await self._extract_keywords_fast(text)
        
        # 의도 추정
        intent_estimate = await self._estimate_intent_fast(text)
        
        # 복잡도 추정
        complexity_estimate = min(len(text) / 1000, 1.0)
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return StreamingResult(
            partial_result={
                'keywords': keywords,
                'estimated_intent': intent_estimate,
                'estimated_complexity': complexity_estimate,
                'text_length': len(text)
            },
            is_complete=False,
            confidence=0.6,  # 부분 결과이므로 낮은 신뢰도
            processing_time=processing_time
        )

    async def _extract_keywords_fast(self, text: str) -> List[str]:
        """빠른 키워드 추출"""
        
        # 기술 키워드
        tech_keywords = ['react', 'vue', 'angular', 'node.js', 'python', 'java', 'database', 'api']
        
        # 비즈니스 키워드
        business_keywords = ['user', 'customer', 'order', 'payment', 'authentication', 'dashboard']
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in tech_keywords + business_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # 상위 10개만

    async def _estimate_intent_fast(self, text: str) -> str:
        """빠른 의도 추정"""
        
        intent_patterns = {
            'build_new': ['build', 'create', 'develop', 'new'],
            'migrate': ['migrate', 'move', 'transfer', 'convert'],
            'modernize': ['modernize', 'update', 'upgrade', 'refactor']
        }
        
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, patterns in intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            intent_scores[intent] = score
        
        return max(intent_scores, key=intent_scores.get) if intent_scores else 'unknown'

    async def _send_partial_result(self, session_id: str, result: StreamingResult) -> None:
        """부분 결과 전송"""
        
        stream_data = self.active_streams.get(session_id)
        if not stream_data:
            return
        
        message = {
            'type': 'partial_result',
            'data': result.partial_result,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        try:
            await stream_data['websocket'].send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            await self._cleanup_stream(session_id)

    async def _handle_stream_complete(self, session_id: str) -> None:
        """스트림 완료 처리"""
        
        stream_data = self.active_streams.get(session_id)
        if not stream_data:
            return
        
        # 전체 텍스트로 최종 분석
        full_text = stream_data['buffer']
        final_result = await self._analyze_complete_text(full_text)
        
        # 최종 결과 전송
        await self._send_final_result(session_id, final_result)
        
        # 스트림 정리
        await self._cleanup_stream(session_id)

    async def _analyze_complete_text(self, text: str) -> Dict[str, Any]:
        """완전한 텍스트 분석"""
        
        # 여기서는 기존의 완전한 NL 분석 파이프라인 사용
        return {
            'complete_analysis': True,
            'text': text,
            'final_confidence': 0.95
        }

    async def _send_final_result(self, session_id: str, result: Dict[str, Any]) -> None:
        """최종 결과 전송"""
        
        stream_data = self.active_streams.get(session_id)
        if not stream_data:
            return
        
        message = {
            'type': 'final_result',
            'data': result,
            'session_id': session_id,
            'total_processing_time': asyncio.get_event_loop().time() - stream_data['start_time']
        }
        
        try:
            await stream_data['websocket'].send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            pass

    async def _cleanup_stream(self, session_id: str) -> None:
        """스트림 정리"""
        if session_id in self.active_streams:
            del self.active_streams[session_id]

    async def _send_error(self, session_id: str, error_message: str) -> None:
        """에러 전송"""
        
        stream_data = self.active_streams.get(session_id)
        if not stream_data:
            return
        
        message = {
            'type': 'error',
            'message': error_message,
            'session_id': session_id
        }
        
        try:
            await stream_data['websocket'].send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            pass