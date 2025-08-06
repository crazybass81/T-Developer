"""
T-Developer MVP - Requirement Clarification System

요구사항 명확화 및 질문 생성 시스템
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class ClarificationQuestion:
    id: str
    category: str
    question: str
    options: Optional[List[str]] = None
    required: bool = False
    impact: str = "medium"  # high, medium, low

@dataclass
class Ambiguity:
    type: str
    field: str
    severity: str
    description: str

class RequirementClarificationSystem:
    """요구사항 명확화 시스템"""

    def __init__(self):
        self.question_generator = QuestionGenerator()

    async def identify_ambiguities(
        self,
        requirements: 'ProjectRequirements'
    ) -> List[Ambiguity]:
        """모호한 요구사항 식별"""
        ambiguities = []

        # 1. 기술 스택 모호성 검사
        if not requirements.technology_preferences.get('frontend'):
            ambiguities.append(Ambiguity(
                type="missing_tech_choice",
                field="frontend_framework",
                severity="high",
                description="프론트엔드 프레임워크가 명시되지 않음"
            ))

        # 2. 규모 및 성능 요구사항 검사
        if not any("사용자" in req for req in requirements.non_functional_requirements):
            ambiguities.append(Ambiguity(
                type="missing_scale_info",
                field="expected_user_count",
                severity="medium",
                description="예상 사용자 수가 명시되지 않음"
            ))

        # 3. 보안 요구사항 검사
        if not self._has_security_requirements(requirements):
            ambiguities.append(Ambiguity(
                type="missing_security_info",
                field="authentication_method",
                severity="high",
                description="보안 및 인증 요구사항이 불명확함"
            ))

        # 4. 배포 환경 검사
        if not any("배포" in req or "호스팅" in req for req in requirements.technical_requirements):
            ambiguities.append(Ambiguity(
                type="missing_deployment_info",
                field="deployment_environment",
                severity="medium",
                description="배포 환경이 명시되지 않음"
            ))

        return ambiguities

    async def generate_clarification_questions(
        self,
        ambiguities: List[Ambiguity]
    ) -> List[ClarificationQuestion]:
        """명확화 질문 생성"""
        questions = []

        for ambiguity in ambiguities:
            question = await self.question_generator.generate(ambiguity)
            questions.append(question)

        # 우선순위 정렬
        return sorted(questions, key=lambda q: self._get_priority_score(q), reverse=True)

    async def process_user_responses(
        self,
        questions: List[ClarificationQuestion],
        responses: Dict[str, Any]
    ) -> 'RefinedRequirements':
        """사용자 응답 처리"""
        refined_requirements = RefinedRequirements()

        for question in questions:
            response = responses.get(question.id)
            if response:
                await self._apply_response(refined_requirements, question, response)

        return refined_requirements

    def _has_security_requirements(self, requirements: 'ProjectRequirements') -> bool:
        """보안 요구사항 존재 여부 확인"""
        security_keywords = ['보안', '인증', '로그인', '권한', 'security', 'auth']
        
        all_text = ' '.join([
            requirements.description,
            ' '.join(requirements.technical_requirements),
            ' '.join(requirements.non_functional_requirements)
        ]).lower()
        
        return any(keyword in all_text for keyword in security_keywords)

    def _get_priority_score(self, question: ClarificationQuestion) -> int:
        """질문 우선순위 점수 계산"""
        impact_scores = {"high": 3, "medium": 2, "low": 1}
        base_score = impact_scores.get(question.impact, 1)
        
        if question.required:
            base_score += 2
            
        return base_score

    async def _apply_response(
        self,
        refined_requirements: 'RefinedRequirements',
        question: ClarificationQuestion,
        response: Any
    ):
        """응답을 요구사항에 적용"""
        if question.category == "technology":
            refined_requirements.add_technology_preference(
                question.field,
                response
            )
        elif question.category == "performance":
            refined_requirements.add_performance_requirement(
                question.field,
                response
            )
        elif question.category == "security":
            refined_requirements.add_security_requirement(
                question.field,
                response
            )

class QuestionGenerator:
    """질문 생성기"""

    def __init__(self):
        self.question_templates = {
            "missing_tech_choice": {
                "frontend_framework": {
                    "question": "어떤 프론트엔드 프레임워크를 사용하시겠습니까?",
                    "options": ["React", "Vue.js", "Angular", "Next.js", "기타"],
                    "impact": "high"
                },
                "backend_framework": {
                    "question": "어떤 백엔드 프레임워크를 선호하시나요?",
                    "options": ["Node.js", "Python Django", "Spring Boot", "기타"],
                    "impact": "high"
                }
            },
            "missing_scale_info": {
                "expected_user_count": {
                    "question": "예상 동시 사용자 수는 얼마나 되나요?",
                    "options": ["100명 미만", "100-1000명", "1000-10000명", "10000명 이상"],
                    "impact": "medium"
                }
            },
            "missing_security_info": {
                "authentication_method": {
                    "question": "어떤 인증 방식을 사용하시겠습니까?",
                    "options": ["이메일/비밀번호", "소셜 로그인", "OAuth 2.0", "기타"],
                    "impact": "high"
                }
            },
            "missing_deployment_info": {
                "deployment_environment": {
                    "question": "어떤 환경에 배포하시겠습니까?",
                    "options": ["AWS", "Google Cloud", "Azure", "온프레미스", "기타"],
                    "impact": "medium"
                }
            }
        }

    async def generate(self, ambiguity: Ambiguity) -> ClarificationQuestion:
        """모호성에 대한 질문 생성"""
        
        template = self.question_templates.get(ambiguity.type, {}).get(ambiguity.field)
        
        if template:
            return ClarificationQuestion(
                id=f"{ambiguity.type}_{ambiguity.field}",
                category=ambiguity.type.split('_')[1] if '_' in ambiguity.type else "general",
                question=template["question"],
                options=template.get("options"),
                required=ambiguity.severity == "high",
                impact=template.get("impact", "medium")
            )
        else:
            # 기본 질문 생성
            return ClarificationQuestion(
                id=f"generic_{ambiguity.field}",
                category="general",
                question=f"{ambiguity.field}에 대해 더 자세히 설명해 주세요.",
                required=ambiguity.severity == "high",
                impact=ambiguity.severity
            )

class RefinedRequirements:
    """정제된 요구사항"""

    def __init__(self):
        self.technology_preferences = {}
        self.performance_requirements = {}
        self.security_requirements = {}
        self.deployment_requirements = {}

    def add_technology_preference(self, field: str, value: Any):
        """기술 선호사항 추가"""
        self.technology_preferences[field] = value

    def add_performance_requirement(self, field: str, value: Any):
        """성능 요구사항 추가"""
        self.performance_requirements[field] = value

    def add_security_requirement(self, field: str, value: Any):
        """보안 요구사항 추가"""
        self.security_requirements[field] = value

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "technology_preferences": self.technology_preferences,
            "performance_requirements": self.performance_requirements,
            "security_requirements": self.security_requirements,
            "deployment_requirements": self.deployment_requirements
        }