# backend/src/agents/nl_input/requirement_clarification.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ClarificationQuestion:
    id: str
    category: str
    question: str
    options: Optional[List[str]] = None
    required: bool = True
    impact: str = 'medium'

class RequirementClarificationSystem:
    """완성된 요구사항 명확화 시스템"""

    def __init__(self):
        self.question_templates = {
            'missing_tech_choice': {
                'question': 'Which frontend framework would you prefer?',
                'options': ['React', 'Vue', 'Angular', 'Svelte', 'Next.js']
            },
            'missing_performance': {
                'question': 'What are your performance requirements?',
                'options': ['< 100ms response', '< 500ms response', '< 1s response', 'No specific requirement']
            },
            'missing_security': {
                'question': 'What authentication method do you need?',
                'options': ['OAuth 2.0', 'JWT', 'Session-based', 'No authentication']
            }
        }

    async def identify_ambiguities(self, requirements: Dict[str, Any]) -> List[Dict[str, str]]:
        """모호성 식별"""
        ambiguities = []

        if not requirements.get('technology_preferences', {}).get('frontend'):
            ambiguities.append({
                'type': 'missing_tech_choice',
                'field': 'frontend_framework',
                'severity': 'high'
            })

        if not any('performance' in req.lower() for req in requirements.get('non_functional_requirements', [])):
            ambiguities.append({
                'type': 'missing_performance',
                'field': 'performance_requirements',
                'severity': 'medium'
            })

        return ambiguities

    async def generate_clarification_questions(self, ambiguities: List[Dict[str, str]]) -> List[ClarificationQuestion]:
        """명확화 질문 생성"""
        questions = []

        for ambiguity in ambiguities:
            template = self.question_templates.get(ambiguity['type'])
            if template:
                question = ClarificationQuestion(
                    id=f"q_{len(questions)+1}",
                    category=ambiguity['field'],
                    question=template['question'],
                    options=template.get('options'),
                    required=ambiguity['severity'] == 'high',
                    impact=ambiguity['severity']
                )
                questions.append(question)

        return questions

    async def process_user_responses(self, questions: List[ClarificationQuestion], responses: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 응답 처리 - 완성된 구현"""
        refined_requirements = {}

        for question in questions:
            response = responses.get(question.id)
            if response:
                if question.category == 'frontend_framework':
                    refined_requirements['technology_preferences'] = {'frontend': response}
                elif question.category == 'performance_requirements':
                    refined_requirements['non_functional_requirements'] = [f"Response time: {response}"]
                elif question.category == 'security_requirements':
                    refined_requirements['security'] = {'authentication': response}

        return refined_requirements