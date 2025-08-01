from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .nl_input_agent import ProjectRequirements

@dataclass
class Ambiguity:
    type: str
    field: str
    severity: str
    description: str = ""

@dataclass
class ClarificationQuestion:
    id: str
    category: str
    question: str
    options: Optional[List[str]] = None
    required: bool = True
    impact: str = 'medium'

class QuestionGenerator:
    """명확화 질문 생성기"""
    
    async def generate(self, ambiguity: Ambiguity) -> ClarificationQuestion:
        """모호성에 따른 질문 생성"""
        question_templates = {
            'missing_tech_choice': {
                'frontend_framework': {
                    'question': '선호하는 프론트엔드 프레임워크가 있나요?',
                    'options': ['React', 'Vue.js', 'Angular', 'Svelte', '상관없음']
                },
                'backend_framework': {
                    'question': '백엔드 기술 스택 선호도가 있나요?',
                    'options': ['Node.js', 'Python (Django/FastAPI)', 'Java (Spring)', 'Go', '상관없음']
                }
            },
            'missing_scale_info': {
                'expected_user_count': {
                    'question': '예상 사용자 수는 얼마나 되나요?',
                    'options': ['100명 미만', '100-1,000명', '1,000-10,000명', '10,000명 이상']
                }
            },
            'missing_security_info': {
                'authentication_method': {
                    'question': '사용자 인증 방식은 어떻게 하시겠어요?',
                    'options': ['이메일/비밀번호', 'OAuth (Google, GitHub 등)', 'JWT 토큰', '별도 인증 불필요']
                }
            }
        }
        
        template = question_templates.get(ambiguity.type, {}).get(ambiguity.field, {
            'question': f'{ambiguity.field}에 대해 더 자세히 설명해주세요.',
            'options': None
        })
        
        return ClarificationQuestion(
            id=f"{ambiguity.type}_{ambiguity.field}",
            category=ambiguity.type,
            question=template['question'],
            options=template.get('options'),
            required=ambiguity.severity == 'high',
            impact=ambiguity.severity
        )

class RefinedRequirements:
    """정제된 요구사항"""
    
    def __init__(self):
        self.data = {}
        
    def update(self, field: str, value: Any):
        """요구사항 업데이트"""
        self.data[field] = value

class RequirementClarificationSystem:
    """요구사항 명확화 시스템"""
    
    def __init__(self):
        self.question_generator = QuestionGenerator()

    async def identify_ambiguities(self, requirements: ProjectRequirements) -> List[Ambiguity]:
        """모호성 식별"""
        ambiguities = []

        # 1. 기술 스택 모호성 검사
        if not requirements.technology_preferences.get('frontend'):
            ambiguities.append(Ambiguity(
                type='missing_tech_choice',
                field='frontend_framework',
                severity='high',
                description='프론트엔드 프레임워크가 명시되지 않음'
            ))

        if not requirements.technology_preferences.get('backend'):
            ambiguities.append(Ambiguity(
                type='missing_tech_choice',
                field='backend_framework',
                severity='high',
                description='백엔드 기술 스택이 명시되지 않음'
            ))

        # 2. 규모 및 성능 요구사항 검사
        has_user_info = any('user' in req.lower() or '사용자' in req 
                           for req in requirements.non_functional_requirements)
        if not has_user_info:
            ambiguities.append(Ambiguity(
                type='missing_scale_info',
                field='expected_user_count',
                severity='medium',
                description='예상 사용자 수가 명시되지 않음'
            ))

        # 3. 보안 요구사항 검사
        if not self._has_security_requirements(requirements):
            ambiguities.append(Ambiguity(
                type='missing_security_info',
                field='authentication_method',
                severity='high',
                description='인증 방식이 명시되지 않음'
            ))

        return ambiguities

    async def generate_clarification_questions(self, ambiguities: List[Ambiguity]) -> List[ClarificationQuestion]:
        """명확화 질문 생성"""
        questions = []

        for ambiguity in ambiguities:
            question = await self.question_generator.generate(ambiguity)
            questions.append(question)

        # 우선순위 정렬
        return sorted(questions, key=lambda q: {
            'high': 3, 'medium': 2, 'low': 1
        }.get(q.impact, 1), reverse=True)

    async def process_user_responses(
        self,
        questions: List[ClarificationQuestion],
        responses: Dict[str, Any]
    ) -> RefinedRequirements:
        """사용자 응답 처리"""
        refined = RefinedRequirements()

        for question in questions:
            response = responses.get(question.id)
            if response:
                await self._apply_response(refined, question, response)

        return refined

    async def _apply_response(
        self,
        refined: RefinedRequirements,
        question: ClarificationQuestion,
        response: Any
    ):
        """응답을 요구사항에 적용"""
        if question.category == 'missing_tech_choice':
            if question.id.endswith('frontend_framework'):
                refined.update('frontend_framework', response)
            elif question.id.endswith('backend_framework'):
                refined.update('backend_framework', response)
                
        elif question.category == 'missing_scale_info':
            refined.update('expected_users', response)
            
        elif question.category == 'missing_security_info':
            refined.update('authentication_method', response)

    def _has_security_requirements(self, requirements: ProjectRequirements) -> bool:
        """보안 요구사항 존재 여부 확인"""
        security_keywords = ['인증', '보안', 'auth', 'security', 'login', '로그인']
        
        all_text = ' '.join([
            requirements.description,
            *requirements.technical_requirements,
            *requirements.non_functional_requirements
        ]).lower()
        
        return any(keyword in all_text for keyword in security_keywords)