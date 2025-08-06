# backend/src/agents/nl_input/integration_tests.py
import pytest
import asyncio
from typing import Dict, Any, List
import time

class TestNLInputAgentIntegration:
    """완성된 NL Input Agent 통합 테스트"""

    @pytest.fixture
    async def nl_agent_system(self):
        """통합된 NL Agent 시스템"""
        from requirement_clarification import RequirementClarificationSystem
        from template_learner import ProjectTemplateLearner
        from multilingual_processor import MultilingualNLProcessor
        from intent_analyzer import IntentAnalyzer
        from requirement_prioritizer import RequirementPrioritizer

        system = {
            'clarification': RequirementClarificationSystem(),
            'template_learner': ProjectTemplateLearner(),
            'multilingual': MultilingualNLProcessor(),
            'intent_analyzer': IntentAnalyzer(),
            'prioritizer': RequirementPrioritizer()
        }
        
        return system

    @pytest.fixture
    def test_scenarios(self):
        """다양한 테스트 시나리오"""
        return [
            {
                "name": "E-commerce Platform",
                "description": "Build a modern e-commerce platform with user authentication, product catalog, shopping cart, and payment processing. Should handle 10,000 concurrent users.",
                "language": "en",
                "expected_intent": "build_new",
                "expected_goals": ["performance", "security"],
                "expected_complexity": "complex"
            },
            {
                "name": "Korean Mobile App",
                "description": "모바일 앱을 개발해주세요. 사용자 인증과 실시간 채팅 기능이 필요합니다.",
                "language": "ko",
                "expected_intent": "build_new",
                "expected_goals": ["security"],
                "expected_complexity": "medium"
            },
            {
                "name": "Legacy Migration",
                "description": "Migrate our legacy PHP application to modern Node.js with microservices architecture. Must maintain existing functionality.",
                "language": "en",
                "expected_intent": "migrate_existing",
                "expected_goals": ["modernization"],
                "expected_complexity": "very_complex"
            }
        ]

    @pytest.mark.asyncio
    async def test_end_to_end_processing(self, nl_agent_system, test_scenarios):
        """종단간 처리 테스트 - 완성된 구현"""
        
        for scenario in test_scenarios:
            print(f"\n=== Testing: {scenario['name']} ===")
            
            # 1. 다국어 처리
            if scenario['language'] != 'en':
                requirements, metadata = await nl_agent_system['multilingual'].process_multilingual_input(
                    scenario['description']
                )
                processed_description = requirements['description']
            else:
                processed_description = scenario['description']
                metadata = {'original_language': 'en'}

            # 2. 의도 분석
            intent_result = await nl_agent_system['intent_analyzer'].analyze_user_intent(
                processed_description
            )
            
            # 검증: 의도 분석
            assert intent_result.primary.value == scenario['expected_intent']
            assert intent_result.confidence > 0.5
            
            # 3. 요구사항 구조화
            structured_requirements = {
                'description': processed_description,
                'intent': intent_result.primary.value,
                'business_goals': [goal.type for goal in intent_result.business_goals],
                'technical_goals': [goal.type for goal in intent_result.technical_goals],
                'constraints': intent_result.constraints
            }

            # 4. 모호성 식별 및 명확화
            ambiguities = await nl_agent_system['clarification'].identify_ambiguities(
                structured_requirements
            )
            
            if ambiguities:
                questions = await nl_agent_system['clarification'].generate_clarification_questions(
                    ambiguities
                )
                
                # 시뮬레이션된 사용자 응답
                mock_responses = self._generate_mock_responses(questions)
                
                refined_requirements = await nl_agent_system['clarification'].process_user_responses(
                    questions, mock_responses
                )
                
                structured_requirements.update(refined_requirements)

            # 5. 요구사항 우선순위 결정
            requirement_list = self._convert_to_requirement_list(structured_requirements)
            
            prioritized = await nl_agent_system['prioritizer'].prioritize_requirements(
                requirement_list,
                {'sprint_capacity': 20, 'strategic_goals': ['user_experience', 'performance']}
            )

            # 검증: 우선순위 결정
            assert len(prioritized) > 0
            assert all(req.priority_score > 0 for req in prioritized)
            assert prioritized[0].priority_score >= prioritized[-1].priority_score  # 정렬 확인

            print(f"✅ {scenario['name']} processed successfully")
            print(f"   Intent: {intent_result.primary.value} (confidence: {intent_result.confidence:.2f})")
            print(f"   Goals: {len(intent_result.business_goals)} business, {len(intent_result.technical_goals)} technical")
            print(f"   Requirements: {len(prioritized)} prioritized")

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, nl_agent_system):
        """성능 벤치마크 테스트 - 완성된 구현"""
        
        test_descriptions = [
            "Simple todo app",
            "Complex e-commerce platform with microservices, real-time analytics, and AI recommendations",
            "Enterprise CRM system with advanced reporting and integration capabilities"
        ]

        performance_results = []

        for description in test_descriptions:
            start_time = time.time()
            
            # 전체 파이프라인 실행
            intent_result = await nl_agent_system['intent_analyzer'].analyze_user_intent(description)
            
            structured_requirements = {
                'description': description,
                'intent': intent_result.primary.value,
                'business_goals': [goal.type for goal in intent_result.business_goals],
                'technical_goals': [goal.type for goal in intent_result.technical_goals]
            }
            
            requirement_list = self._convert_to_requirement_list(structured_requirements)
            prioritized = await nl_agent_system['prioritizer'].prioritize_requirements(
                requirement_list, {'sprint_capacity': 20}
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            performance_results.append({
                'description_length': len(description),
                'processing_time': processing_time,
                'requirements_generated': len(prioritized)
            })

        # 성능 검증
        avg_time = sum(r['processing_time'] for r in performance_results) / len(performance_results)
        max_time = max(r['processing_time'] for r in performance_results)

        print(f"\n=== Performance Results ===")
        print(f"Average processing time: {avg_time:.3f}s")
        print(f"Maximum processing time: {max_time:.3f}s")

        # 성능 기준 검증
        assert avg_time < 2.0, f"Average processing time {avg_time:.3f}s exceeds 2.0s limit"
        assert max_time < 5.0, f"Maximum processing time {max_time:.3f}s exceeds 5.0s limit"

    @pytest.mark.asyncio
    async def test_template_learning_integration(self, nl_agent_system):
        """템플릿 학습 통합 테스트"""
        
        # 성공 프로젝트 데이터
        successful_projects = [
            {
                'description': 'E-commerce platform with React and Node.js',
                'requirements': ['user_auth', 'product_catalog', 'payment'],
                'tech_stack': ['React', 'Node.js', 'MongoDB'],
                'complexity_score': 0.7,
                'success_rate': 0.9
            },
            {
                'description': 'Online marketplace with Vue and Python',
                'requirements': ['user_auth', 'product_catalog', 'reviews'],
                'tech_stack': ['Vue', 'Python', 'PostgreSQL'],
                'complexity_score': 0.8,
                'success_rate': 0.85
            },
            {
                'description': 'Shopping website with Angular and Java',
                'requirements': ['user_auth', 'product_catalog', 'inventory'],
                'tech_stack': ['Angular', 'Java', 'MySQL'],
                'complexity_score': 0.75,
                'success_rate': 0.88
            }
        ]

        # 템플릿 학습
        templates = await nl_agent_system['template_learner'].learn_from_successful_projects(
            successful_projects
        )

        # 검증
        assert len(templates) > 0, "No templates were learned"
        
        # 템플릿 제안 테스트
        test_description = "Build an e-commerce website"
        suggested_template = await nl_agent_system['template_learner'].suggest_template(
            test_description
        )

        if suggested_template:
            assert suggested_template.success_rate > 0
            assert len(suggested_template.common_requirements) > 0
            print(f"✅ Template suggested: {suggested_template.name}")
            print(f"   Success rate: {suggested_template.success_rate:.2f}")
            print(f"   Common requirements: {suggested_template.common_requirements[:3]}")

    def _generate_mock_responses(self, questions: List) -> Dict[str, Any]:
        """모의 사용자 응답 생성"""
        responses = {}
        
        for question in questions:
            if question.options:
                # 첫 번째 옵션 선택
                responses[question.id] = question.options[0]
            else:
                # 기본 응답
                responses[question.id] = "Standard requirement"
        
        return responses

    def _convert_to_requirement_list(self, structured_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """구조화된 요구사항을 리스트로 변환"""
        requirements = []
        
        # 비즈니스 목표를 요구사항으로 변환
        for i, goal in enumerate(structured_requirements.get('business_goals', [])):
            requirements.append({
                'id': f'business_{i}',
                'description': f'Business goal: {goal}',
                'type': 'business',
                'business_priority': 'high',
                'complexity': 'medium',
                'user_impact': 'high'
            })
        
        # 기술적 목표를 요구사항으로 변환
        for i, goal in enumerate(structured_requirements.get('technical_goals', [])):
            requirements.append({
                'id': f'technical_{i}',
                'description': f'Technical goal: {goal}',
                'type': 'technical',
                'business_priority': 'medium',
                'complexity': 'complex',
                'technical_risk': 'medium'
            })
        
        # 기본 요구사항 추가
        if not requirements:
            requirements.append({
                'id': 'default_1',
                'description': structured_requirements.get('description', 'Default requirement'),
                'type': 'functional',
                'business_priority': 'medium',
                'complexity': 'medium',
                'user_impact': 'medium'
            })
        
        return requirements

# 실행 스크립트
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])