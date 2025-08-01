# Task 4.1.4: Real-time Feedback Processing
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

class RealtimeFeedbackProcessor:
    """실시간 피드백 처리 시스템"""

    def __init__(self, nl_agent):
        self.nl_agent = nl_agent
        self.feedback_queue = asyncio.Queue()
        self.processing_lock = False
        self.active_sessions = {}

    async def handle_realtime_feedback(self, session_id: str, websocket) -> None:
        """WebSocket을 통한 실시간 피드백 처리"""
        
        self.active_sessions[session_id] = websocket
        
        try:
            async for message in websocket:
                feedback = json.loads(message)
                await self.feedback_queue.put({
                    'session_id': session_id,
                    'feedback': feedback,
                    'timestamp': datetime.utcnow()
                })
                
                # 즉시 확인 응답
                await websocket.send(json.dumps({
                    'type': 'feedback_received',
                    'id': feedback.get('id'),
                    'status': 'queued'
                }))
                
                if not self.processing_lock:
                    await self.process_feedback_queue()
                    
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        finally:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

    async def process_feedback_queue(self):
        """피드백 큐 처리"""
        self.processing_lock = True
        
        try:
            while not self.feedback_queue.empty():
                item = await self.feedback_queue.get()
                session_id = item['session_id']
                feedback = item['feedback']
                
                result = await self._process_single_feedback(session_id, feedback)
                
                if session_id in self.active_sessions:
                    websocket = self.active_sessions[session_id]
                    await websocket.send(json.dumps({
                        'type': 'feedback_processed',
                        'result': result,
                        'updated_requirements': await self._get_current_requirements(session_id)
                    }))
        finally:
            self.processing_lock = False

    async def _process_single_feedback(self, session_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """단일 피드백 처리"""
        
        feedback_type = feedback.get('type')
        content = feedback.get('content')
        
        if feedback_type == 'clarification':
            return await self._process_clarification(session_id, content)
        elif feedback_type == 'correction':
            return await self._process_correction(session_id, content)
        elif feedback_type == 'addition':
            return await self._process_addition(session_id, content)
        
        return {'status': 'unknown_feedback_type'}

    async def _process_clarification(self, session_id: str, content: str) -> Dict[str, Any]:
        """명확화 응답 처리"""
        context = await self._get_session_context(session_id)
        
        refined_prompt = f"""
        사용자가 다음과 같이 명확화했습니다: {content}
        
        기존 요구사항을 업데이트하고 개선된 분석을 제공해주세요.
        """
        
        updated_analysis = await self.nl_agent.agent.arun(refined_prompt)
        
        return {
            'type': 'requirements_refined',
            'analysis': updated_analysis,
            'changes': ['clarification_applied']
        }

    async def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """세션 컨텍스트 조회"""
        # 실제 구현에서는 세션 저장소에서 조회
        return {'session_id': session_id, 'requirements': {}}

    async def _get_current_requirements(self, session_id: str) -> Dict[str, Any]:
        """현재 요구사항 조회"""
        return {'requirements': 'updated_requirements'}