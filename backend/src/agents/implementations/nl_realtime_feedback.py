from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
from .nl_input_agent import NLInputAgent

@dataclass
class FeedbackEvent:
    id: str
    type: str  # 'clarification', 'correction', 'addition'
    content: str
    timestamp: datetime
    processed: bool = False

class RealtimeFeedbackProcessor:
    """실시간 피드백 처리기"""
    
    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.feedback_queue: List[FeedbackEvent] = []
        self.processing_lock = False
        self.active_sessions: Dict[str, Dict] = {}

    async def handle_realtime_feedback(self, session_id: str, websocket) -> None:
        """WebSocket을 통한 실시간 피드백 처리"""
        
        self.active_sessions[session_id] = {
            'websocket': websocket,
            'last_activity': datetime.utcnow(),
            'requirements': None
        }
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    feedback = FeedbackEvent(
                        id=data.get('id', str(datetime.utcnow().timestamp())),
                        type=data.get('type', 'clarification'),
                        content=data.get('content', ''),
                        timestamp=datetime.utcnow()
                    )
                    
                    # 피드백 큐에 추가
                    self.feedback_queue.append(feedback)
                    
                    # 즉시 확인 응답
                    await websocket.send(json.dumps({
                        'type': 'feedback_received',
                        'id': feedback.id,
                        'status': 'queued'
                    }))
                    
                    # 피드백 처리
                    if not self.processing_lock:
                        await self.process_feedback_queue(session_id)
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                    
        finally:
            # 세션 정리
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

    async def process_feedback_queue(self, session_id: str) -> None:
        """피드백 큐 처리"""
        
        self.processing_lock = True
        
        try:
            while self.feedback_queue:
                feedback = self.feedback_queue.pop(0)
                
                try:
                    # 피드백 유형별 처리
                    result = None
                    if feedback.type == 'clarification':
                        result = await self.process_clarification(session_id, feedback)
                    elif feedback.type == 'correction':
                        result = await self.process_correction(session_id, feedback)
                    elif feedback.type == 'addition':
                        result = await self.process_addition(session_id, feedback)
                    
                    # 처리 결과 전송
                    if session_id in self.active_sessions:
                        websocket = self.active_sessions[session_id]['websocket']
                        await websocket.send(json.dumps({
                            'type': 'feedback_processed',
                            'feedback_id': feedback.id,
                            'result': result,
                            'updated_requirements': await self.get_current_requirements(session_id)
                        }))
                        
                    feedback.processed = True
                    
                except Exception as e:
                    # 오류 응답 전송
                    if session_id in self.active_sessions:
                        websocket = self.active_sessions[session_id]['websocket']
                        await websocket.send(json.dumps({
                            'type': 'feedback_error',
                            'feedback_id': feedback.id,
                            'error': str(e)
                        }))
                        
        finally:
            self.processing_lock = False

    async def process_clarification(self, session_id: str, feedback: FeedbackEvent) -> Dict[str, Any]:
        """명확화 응답 처리"""
        
        session_data = self.active_sessions.get(session_id, {})
        current_requirements = session_data.get('requirements')
        
        if not current_requirements:
            return {'type': 'error', 'message': 'No current requirements found'}
        
        # 명확화 내용을 기존 요구사항에 통합
        enhanced_description = f"{current_requirements.get('description', '')} {feedback.content}"
        
        # NL Agent로 재처리
        updated_requirements = await self.nl_agent.process_description(enhanced_description)
        
        # 세션 업데이트
        self.active_sessions[session_id]['requirements'] = updated_requirements.__dict__
        
        return {
            'type': 'requirements_refined',
            'changes': self.diff_requirements(current_requirements, updated_requirements.__dict__)
        }

    async def process_correction(self, session_id: str, feedback: FeedbackEvent) -> Dict[str, Any]:
        """수정 사항 처리"""
        
        session_data = self.active_sessions.get(session_id, {})
        current_requirements = session_data.get('requirements')
        
        if not current_requirements:
            return {'type': 'error', 'message': 'No current requirements found'}
        
        # 수정 사항 파싱 및 적용
        corrections = self.parse_corrections(feedback.content)
        updated_requirements = self.apply_corrections(current_requirements, corrections)
        
        # 세션 업데이트
        self.active_sessions[session_id]['requirements'] = updated_requirements
        
        return {
            'type': 'requirements_corrected',
            'corrections_applied': corrections,
            'changes': self.diff_requirements(current_requirements, updated_requirements)
        }

    async def process_addition(self, session_id: str, feedback: FeedbackEvent) -> Dict[str, Any]:
        """추가 사항 처리"""
        
        session_data = self.active_sessions.get(session_id, {})
        current_requirements = session_data.get('requirements')
        
        if not current_requirements:
            return {'type': 'error', 'message': 'No current requirements found'}
        
        # 추가 요구사항 처리
        additional_requirements = await self.nl_agent.process_description(feedback.content)
        
        # 기존 요구사항과 병합
        merged_requirements = self.merge_requirements(
            current_requirements,
            additional_requirements.__dict__
        )
        
        # 세션 업데이트
        self.active_sessions[session_id]['requirements'] = merged_requirements
        
        return {
            'type': 'requirements_extended',
            'additions': additional_requirements.__dict__,
            'changes': self.diff_requirements(current_requirements, merged_requirements)
        }

    def parse_corrections(self, content: str) -> List[Dict[str, Any]]:
        """수정 사항 파싱"""
        
        corrections = []
        
        # 간단한 패턴 매칭 (실제로는 더 정교한 NLP 필요)
        if 'change' in content.lower() or '변경' in content:
            corrections.append({
                'type': 'modification',
                'content': content
            })
        elif 'remove' in content.lower() or '제거' in content:
            corrections.append({
                'type': 'removal',
                'content': content
            })
        
        return corrections

    def apply_corrections(
        self,
        requirements: Dict[str, Any],
        corrections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """수정 사항 적용"""
        
        updated = requirements.copy()
        
        for correction in corrections:
            if correction['type'] == 'modification':
                # 간단한 수정 로직
                updated['description'] += f" (Modified: {correction['content']})"
            elif correction['type'] == 'removal':
                # 제거 로직
                updated['description'] += f" (Removed: {correction['content']})"
        
        return updated

    def merge_requirements(
        self,
        base: Dict[str, Any],
        additional: Dict[str, Any]
    ) -> Dict[str, Any]:
        """요구사항 병합"""
        
        merged = base.copy()
        
        # 기술 요구사항 병합
        if 'technical_requirements' in additional:
            merged['technical_requirements'] = list(set(
                merged.get('technical_requirements', []) +
                additional['technical_requirements']
            ))
        
        # 비기능 요구사항 병합
        if 'non_functional_requirements' in additional:
            merged['non_functional_requirements'] = list(set(
                merged.get('non_functional_requirements', []) +
                additional['non_functional_requirements']
            ))
        
        # 기술 선호도 병합
        if 'technology_preferences' in additional:
            merged_prefs = merged.get('technology_preferences', {})
            for key, value in additional['technology_preferences'].items():
                if key in merged_prefs:
                    merged_prefs[key] = list(set(merged_prefs[key] + value))
                else:
                    merged_prefs[key] = value
            merged['technology_preferences'] = merged_prefs
        
        return merged

    def diff_requirements(
        self,
        old: Dict[str, Any],
        new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """요구사항 변경 사항 계산"""
        
        changes = {
            'added': {},
            'modified': {},
            'removed': {}
        }
        
        # 간단한 diff 구현
        for key in new:
            if key not in old:
                changes['added'][key] = new[key]
            elif old[key] != new[key]:
                changes['modified'][key] = {
                    'old': old[key],
                    'new': new[key]
                }
        
        for key in old:
            if key not in new:
                changes['removed'][key] = old[key]
        
        return changes

    async def get_current_requirements(self, session_id: str) -> Optional[Dict[str, Any]]:
        """현재 요구사항 조회"""
        
        session_data = self.active_sessions.get(session_id)
        return session_data.get('requirements') if session_data else None