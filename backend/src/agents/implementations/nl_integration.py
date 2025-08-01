from typing import Dict, Any, List, Optional
import asyncio
from .nl_input_agent import NLInputAgent, ProjectRequirements
from .nl_input_multimodal import MultimodalInputProcessor
from .requirement_clarification import RequirementClarificationSystem, ClarificationQuestion

class NLInputAgentIntegration:
    """NL Input Agent 통합 시스템"""
    
    def __init__(self):
        self.nl_agent = NLInputAgent()
        self.multimodal_processor = MultimodalInputProcessor(self.nl_agent)
        self.clarification_system = RequirementClarificationSystem()
        
    async def process_complete_request(
        self,
        inputs: List[Any],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """완전한 요청 처리 파이프라인"""
        
        try:
            # 1. 멀티모달 입력 처리
            if len(inputs) > 1 or not isinstance(inputs[0], str):
                requirements = await self.multimodal_processor.process_multimodal_input(inputs)
            else:
                requirements = await self.nl_agent.process_description(inputs[0], user_context)
            
            # 2. 모호성 검사 및 명확화
            ambiguities = await self.clarification_system.identify_ambiguities(requirements)
            
            result = {
                'requirements': requirements.__dict__,
                'processing_status': 'completed',
                'confidence_score': self._calculate_confidence(requirements),
                'ambiguities': len(ambiguities),
                'clarification_needed': len(ambiguities) > 0
            }
            
            # 3. 명확화 질문 생성 (필요시)
            if ambiguities:
                questions = await self.clarification_system.generate_clarification_questions(ambiguities)
                result['clarification_questions'] = [q.__dict__ for q in questions]
                result['processing_status'] = 'needs_clarification'
            
            return result
            
        except Exception as e:
            return {
                'processing_status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__
            }
    
    async def process_clarification_response(
        self,
        original_requirements: Dict[str, Any],
        responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """명확화 응답 처리"""
        
        try:
            # 원본 요구사항 복원
            requirements = ProjectRequirements(**original_requirements)
            
            # 질문 재생성 (응답 처리를 위해)
            ambiguities = await self.clarification_system.identify_ambiguities(requirements)
            questions = await self.clarification_system.generate_clarification_questions(ambiguities)
            
            # 응답 처리
            refined = await self.clarification_system.process_user_responses(questions, responses)
            
            # 요구사항 업데이트
            updated_requirements = self._merge_requirements(requirements, refined.data)
            
            return {
                'requirements': updated_requirements.__dict__,
                'processing_status': 'completed',
                'confidence_score': self._calculate_confidence(updated_requirements),
                'clarification_applied': True
            }
            
        except Exception as e:
            return {
                'processing_status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__
            }
    
    def _calculate_confidence(self, requirements: ProjectRequirements) -> float:
        """신뢰도 점수 계산"""
        score = 0.0
        
        # 프로젝트 타입 명확성
        if requirements.project_type and requirements.project_type != 'general':
            score += 0.2
            
        # 기술 요구사항 완성도
        if len(requirements.technical_requirements) >= 3:
            score += 0.3
        elif len(requirements.technical_requirements) >= 1:
            score += 0.15
            
        # 기술 스택 명시도
        if requirements.technology_preferences:
            score += 0.2
            
        # 비기능 요구사항
        if requirements.non_functional_requirements:
            score += 0.15
            
        # 설명 상세도
        if len(requirements.description) > 50:
            score += 0.15
            
        return min(score, 1.0)
    
    def _merge_requirements(
        self,
        original: ProjectRequirements,
        updates: Dict[str, Any]
    ) -> ProjectRequirements:
        """요구사항 병합"""
        
        # 기존 데이터를 딕셔너리로 변환
        merged_data = original.__dict__.copy()
        
        # 업데이트 적용
        for key, value in updates.items():
            if key == 'frontend_framework':
                if 'technology_preferences' not in merged_data:
                    merged_data['technology_preferences'] = {}
                merged_data['technology_preferences']['frontend'] = [value]
            elif key == 'backend_framework':
                if 'technology_preferences' not in merged_data:
                    merged_data['technology_preferences'] = {}
                merged_data['technology_preferences']['backend'] = [value]
            elif key == 'expected_users':
                merged_data['non_functional_requirements'].append(f"Expected users: {value}")
            elif key == 'authentication_method':
                merged_data['technical_requirements'].append(f"Authentication: {value}")
        
        return ProjectRequirements(**merged_data)