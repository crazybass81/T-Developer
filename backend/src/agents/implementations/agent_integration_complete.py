# Complete Integration of Tasks 4.1-4.5
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass

# Import all implemented components
from .nl_multimodal_processor import MultimodalInputProcessor
from .nl_realtime_feedback import RealtimeFeedbackProcessor
from .ui_framework_analyzer import UIFrameworkAnalyzer
from .parsing_agent_advanced import AdvancedParsingAgent
from .component_decision_mcdm import MultiCriteriaDecisionSystem
from .matching_rate_calculator import AdvancedMatchingRateCalculator

@dataclass
class CompleteAgentWorkflow:
    """완전한 에이전트 워크플로우 결과"""
    nl_analysis: Dict[str, Any]
    ui_recommendation: Dict[str, Any]
    code_analysis: Dict[str, Any]
    component_decisions: Dict[str, Any]
    matching_results: Dict[str, Any]
    integration_plan: Dict[str, Any]

class IntegratedAgentSystem:
    """Tasks 4.1-4.5 통합 에이전트 시스템"""

    def __init__(self):
        # 개별 에이전트 초기화
        self.nl_agent = self._create_nl_agent()
        self.ui_analyzer = UIFrameworkAnalyzer()
        self.parsing_agent = AdvancedParsingAgent()
        self.decision_system = MultiCriteriaDecisionSystem()
        self.matching_calculator = AdvancedMatchingRateCalculator()
        
        # 통합 컴포넌트
        self.multimodal_processor = MultimodalInputProcessor(self.nl_agent)
        self.feedback_processor = RealtimeFeedbackProcessor(self.nl_agent)

    def _create_nl_agent(self) -> Agent:
        """NL Input Agent 생성"""
        return Agent(
            name="Integrated-NL-Agent",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Senior requirements analyst with multimodal capabilities",
            instructions=[
                "Process natural language requirements with multimodal support",
                "Handle real-time feedback and clarifications",
                "Extract comprehensive project specifications",
                "Coordinate with other specialized agents"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-integrated-conversations"
            ),
            temperature=0.3
        )

    async def process_complete_workflow(
        self,
        project_input: Dict[str, Any],
        session_id: str
    ) -> CompleteAgentWorkflow:
        """완전한 에이전트 워크플로우 실행"""

        # Phase 1: Natural Language Processing (Task 4.1)
        nl_analysis = await self._process_nl_input(project_input, session_id)
        
        # Phase 2: UI Framework Analysis (Task 4.2)
        ui_recommendation = await self._analyze_ui_requirements(nl_analysis)
        
        # Phase 3: Code Parsing (Task 4.3) - if existing code provided
        code_analysis = None
        if project_input.get('existing_codebase'):
            code_analysis = await self._parse_existing_code(project_input['existing_codebase'])
        
        # Phase 4: Component Decision Making (Task 4.4)
        component_decisions = await self._make_component_decisions(
            nl_analysis, ui_recommendation, code_analysis
        )
        
        # Phase 5: Matching Rate Calculation (Task 4.5)
        matching_results = await self._calculate_matching_rates(
            nl_analysis, component_decisions
        )
        
        # Phase 6: Integration Planning
        integration_plan = await self._create_integration_plan(
            nl_analysis, ui_recommendation, component_decisions, matching_results
        )

        return CompleteAgentWorkflow(
            nl_analysis=nl_analysis,
            ui_recommendation=ui_recommendation,
            code_analysis=code_analysis,
            component_decisions=component_decisions,
            matching_results=matching_results,
            integration_plan=integration_plan
        )

    async def _process_nl_input(
        self,
        project_input: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """자연어 입력 처리 (Task 4.1)"""

        # 멀티모달 입력 처리
        if project_input.get('multimodal_inputs'):
            processed_input = await self.multimodal_processor.process_multimodal_input(
                project_input['multimodal_inputs']
            )
        else:
            processed_input = await self.nl_agent.process_description(
                project_input.get('description', ''),
                context=project_input.get('context')
            )

        # 실시간 피드백 설정
        if project_input.get('enable_realtime_feedback'):
            await self.feedback_processor.setup_session(session_id)

        return {
            'requirements': processed_input,
            'session_id': session_id,
            'processing_metadata': {
                'multimodal_used': bool(project_input.get('multimodal_inputs')),
                'realtime_enabled': bool(project_input.get('enable_realtime_feedback')),
                'confidence_score': processed_input.get('confidence', 0.8)
            }
        }

    async def _analyze_ui_requirements(
        self,
        nl_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """UI 요구사항 분석 (Task 4.2)"""

        requirements = nl_analysis['requirements']
        
        # 프로젝트 규모 추정
        project_scale = self._estimate_project_scale(requirements)
        
        # 프레임워크 적합성 분석
        framework_analysis = await self.ui_analyzer.analyze_framework_fit(
            requirements=requirements,
            project_scale=project_scale
        )

        # 최적 프레임워크 선택
        best_framework = max(
            framework_analysis.items(),
            key=lambda x: x[1]['scores']['final']
        )

        return {
            'recommended_framework': best_framework[0],
            'framework_analysis': framework_analysis,
            'project_scale': project_scale,
            'ui_architecture': await self._design_ui_architecture(
                best_framework[0], requirements
            )
        }

    async def _parse_existing_code(
        self,
        codebase_location: str
    ) -> Dict[str, Any]:
        """기존 코드 파싱 (Task 4.3)"""

        analysis = await self.parsing_agent.parse_codebase(codebase_location)
        
        return {
            'codebase_analysis': analysis,
            'reusable_components': analysis.reusable_modules,
            'refactoring_suggestions': analysis.suggestions,
            'integration_points': await self._identify_integration_points(analysis)
        }

    async def _make_component_decisions(
        self,
        nl_analysis: Dict[str, Any],
        ui_recommendation: Dict[str, Any],
        code_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """컴포넌트 의사결정 (Task 4.4)"""

        # 의사결정 대안 구성
        alternatives = await self._build_component_alternatives(
            nl_analysis, ui_recommendation, code_analysis
        )
        
        # 기준 가중치 설정
        criteria_weights = await self._determine_criteria_weights(nl_analysis)
        
        # MCDM 의사결정 실행
        decision_result = await self.decision_system.make_decision(
            alternatives=alternatives,
            criteria_weights=criteria_weights,
            method='topsis'
        )

        return {
            'selected_components': decision_result['ranking'][:5],  # 상위 5개
            'decision_analysis': decision_result,
            'alternatives_considered': alternatives,
            'decision_rationale': await self._generate_decision_rationale(decision_result)
        }

    async def _calculate_matching_rates(
        self,
        nl_analysis: Dict[str, Any],
        component_decisions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """매칭률 계산 (Task 4.5)"""

        requirements = nl_analysis['requirements']
        selected_components = component_decisions['selected_components']
        
        # 매칭률 계산
        matching_results = await self.matching_calculator.calculate_matching_rates(
            requirements=[requirements],
            components=selected_components
        )

        return {
            'matching_matrix': matching_results.matrix,
            'overall_coverage': matching_results.overall_coverage,
            'gap_analysis': matching_results.gap_analysis,
            'optimization_suggestions': matching_results.recommendations
        }

    async def _create_integration_plan(
        self,
        nl_analysis: Dict[str, Any],
        ui_recommendation: Dict[str, Any],
        component_decisions: Dict[str, Any],
        matching_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 계획 생성"""

        integration_prompt = f"""
        다음 분석 결과를 바탕으로 통합 구현 계획을 수립해주세요:

        1. 요구사항: {nl_analysis['requirements']}
        2. UI 프레임워크: {ui_recommendation['recommended_framework']}
        3. 선택된 컴포넌트: {component_decisions['selected_components']}
        4. 매칭 커버리지: {matching_results['overall_coverage']}

        다음을 포함한 상세 계획을 제공해주세요:
        - 구현 단계별 로드맵
        - 기술적 위험 요소
        - 성능 최적화 방안
        - 테스트 전략
        """

        integration_analysis = await self.nl_agent.arun(integration_prompt)

        return {
            'implementation_roadmap': await self._parse_roadmap(integration_analysis),
            'risk_assessment': await self._assess_integration_risks(
                component_decisions, matching_results
            ),
            'performance_optimization': await self._plan_performance_optimization(
                ui_recommendation, component_decisions
            ),
            'testing_strategy': await self._design_testing_strategy(
                nl_analysis, component_decisions
            )
        }

    # Helper methods
    def _estimate_project_scale(self, requirements: Dict[str, Any]) -> 'ProjectScale':
        """프로젝트 규모 추정"""
        from .ui_framework_analyzer import ProjectScale
        
        # 간단한 휴리스틱 기반 추정
        complexity_indicators = len(requirements.get('technical_requirements', []))
        
        if complexity_indicators > 10:
            return ProjectScale(
                current_users=1000,
                expected_users_2years=100000,
                feature_complexity='high',
                team_size=8,
                development_timeline='12_months'
            )
        elif complexity_indicators > 5:
            return ProjectScale(
                current_users=100,
                expected_users_2years=10000,
                feature_complexity='medium',
                team_size=4,
                development_timeline='6_months'
            )
        else:
            return ProjectScale(
                current_users=10,
                expected_users_2years=1000,
                feature_complexity='low',
                team_size=2,
                development_timeline='3_months'
            )

    async def _design_ui_architecture(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """UI 아키텍처 설계"""
        
        architecture_patterns = {
            'react': 'Component-based with hooks',
            'vue': 'MVVM with composition API',
            'angular': 'MVC with services',
            'nextjs': 'SSR with API routes'
        }
        
        return {
            'pattern': architecture_patterns.get(framework, 'Component-based'),
            'state_management': self._recommend_state_management(framework),
            'routing_strategy': self._recommend_routing(framework),
            'styling_approach': self._recommend_styling(framework, requirements)
        }

    def _recommend_state_management(self, framework: str) -> str:
        """상태 관리 라이브러리 추천"""
        recommendations = {
            'react': 'Redux Toolkit + RTK Query',
            'vue': 'Pinia',
            'angular': 'NgRx',
            'nextjs': 'Zustand'
        }
        return recommendations.get(framework, 'Context API')

    async def handle_realtime_feedback(
        self,
        session_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실시간 피드백 처리"""
        
        return await self.feedback_processor._process_single_feedback(
            session_id, feedback
        )

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """세션 상태 조회"""
        
        return {
            'session_id': session_id,
            'active': session_id in self.feedback_processor.active_sessions,
            'queue_size': self.feedback_processor.feedback_queue.qsize(),
            'processing': self.feedback_processor.processing_lock
        }