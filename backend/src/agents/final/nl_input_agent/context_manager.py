from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import boto3
from dataclasses import dataclass

@dataclass
class ConversationContext:
    session_id: str
    user_id: str
    current_messages: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    common_requirements: List[str]
    technology_stack_history: List[tuple]

class ConversationContextManager:
    """NL Input Agent를 위한 대화 컨텍스트 관리"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('t-dev-conversations')
        self.max_history_length = 50
        self.context_ttl = timedelta(hours=24)

    async def get_conversation_context(
        self,
        session_id: str,
        user_id: str
    ) -> ConversationContext:
        """세션별 대화 컨텍스트 조회"""

        # 현재 세션 컨텍스트
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            current_context = response.get('Item', {})
        except Exception:
            current_context = {}

        # 사용자의 이전 프로젝트 컨텍스트
        try:
            response = self.table.query(
                IndexName='user_id_index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id},
                Limit=5,
                ScanIndexForward=False
            )
            user_history = response.get('Items', [])
        except Exception:
            user_history = []

        # 관련 프로젝트 패턴 분석
        patterns = await self._analyze_user_patterns(user_history)

        return ConversationContext(
            session_id=session_id,
            user_id=user_id,
            current_messages=current_context.get('messages', []),
            user_preferences=patterns.get('preferences', {}),
            common_requirements=patterns.get('common_requirements', []),
            technology_stack_history=patterns.get('tech_stacks', [])
        )

    async def update_context(
        self,
        session_id: str,
        message: Dict[str, Any],
        extracted_info: Optional[Dict[str, Any]] = None
    ):
        """대화 컨텍스트 업데이트"""

        context = await self.get_conversation_context(session_id, message["user_id"])

        # 메시지 추가
        context.current_messages.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": message["role"],
            "content": message["content"],
            "extracted_info": extracted_info
        })

        # 히스토리 크기 관리
        if len(context.current_messages) > self.max_history_length:
            # 오래된 메시지 요약
            summary = await self._summarize_old_messages(
                context.current_messages[:10]
            )
            context.current_messages = [summary] + context.current_messages[10:]

        # 저장
        ttl = int((datetime.utcnow() + self.context_ttl).timestamp())
        
        self.table.put_item(
            Item={
                "session_id": session_id,
                "user_id": message["user_id"],
                "messages": context.current_messages,
                "last_updated": datetime.utcnow().isoformat(),
                "ttl": ttl
            }
        )

    async def _analyze_user_patterns(
        self,
        user_history: List[Dict]
    ) -> Dict[str, Any]:
        """사용자의 프로젝트 패턴 분석"""

        patterns = {
            "preferences": {},
            "common_requirements": [],
            "tech_stacks": []
        }

        if not user_history:
            return patterns

        # 기술 스택 빈도 분석
        tech_stack_frequency = {}
        for project in user_history:
            extracted_info = project.get('messages', [{}])[-1].get('extracted_info', {})
            tech_stack = extracted_info.get('tech_stack', [])
            
            for tech in tech_stack:
                tech_stack_frequency[tech] = tech_stack_frequency.get(tech, 0) + 1

        # 상위 3개 기술 스택
        patterns["tech_stacks"] = sorted(
            tech_stack_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # 공통 요구사항 패턴
        requirement_frequency = {}
        for project in user_history:
            extracted_info = project.get('messages', [{}])[-1].get('extracted_info', {})
            requirements = extracted_info.get('requirements', [])
            
            for req in requirements:
                req_key = self._normalize_requirement(req)
                requirement_frequency[req_key] = requirement_frequency.get(req_key, 0) + 1

        # 2번 이상 나타난 요구사항
        patterns["common_requirements"] = [
            req for req, count in requirement_frequency.items()
            if count >= 2
        ]

        return patterns

    def _normalize_requirement(self, requirement: str) -> str:
        """요구사항 정규화"""
        # 간단한 정규화 (소문자, 공백 제거)
        return requirement.lower().strip()

    async def _summarize_old_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """오래된 메시지 요약"""
        
        # 간단한 요약 구현
        content_summary = f"Previous conversation summary: {len(messages)} messages exchanged"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "role": "system",
            "content": content_summary,
            "is_summary": True
        }