"""
T-Developer MVP - Unified Agent System

Agent Squad + Agno Framework 통합 시스템
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from ..orchestration.agent_squad_core import AgentSquadOrchestrator, AgentTask
from ..agno.agno_integration import AgnoFrameworkManager, AgnoAgent

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    active_agents: int
    system_uptime_s: float

class UnifiedAgentSystem:
    """통합 에이전트 시스템"""
    
    def __init__(self):
        self.orchestrator = AgentSquadOrchestrator()
        self.agno_manager = AgnoFrameworkManager()
        self.system_start_time = datetime.utcnow()
        self.metrics = SystemMetrics(0, 0, 0, 0.0, 0, 0.0)
        
        # 9개 핵심 에이전트 타입
        self.core_agent_types = [
            'nl_input',
            'ui_selection', 
            'parser',
            'component_decision',
            'match_rate',
            'search',
            'generation',
            'assembly',
            'download'
        ]
        
    async def initialize(self):
        """시스템 초기화"""
        logger.info("Initializing Unified Agent System...")
        
        # 핵심 에이전트들 등록
        for agent_type in self.core_agent_types:
            await self._register_core_agent(agent_type)
        
        logger.info(f"Initialized {len(self.core_agent_types)} core agents")
        
    async def _register_core_agent(self, agent_type: str):
        """핵심 에이전트 등록"""
        config = {
            'type': agent_type,
            'version': '1.0.0',
            'capabilities': self._get_agent_capabilities(agent_type)
        }
        
        # Agno 에이전트 생성
        agno_agent = await self.agno_manager.create_agent(agent_type, config)
        
        # Agent Squad에 등록
        await self.orchestrator.register_agent(agent_type, agno_agent)
        
    def _get_agent_capabilities(self, agent_type: str) -> List[str]:
        """에이전트별 능력 정의"""
        capabilities_map = {
            'nl_input': ['natural_language_processing', 'requirement_extraction'],
            'ui_selection': ['framework_analysis', 'ui_recommendation'],
            'parser': ['requirement_parsing', 'structure_analysis'],
            'component_decision': ['component_evaluation', 'decision_making'],
            'match_rate': ['compatibility_analysis', 'scoring'],
            'search': ['component_search', 'ranking'],
            'generation': ['code_generation', 'template_processing'],
            'assembly': ['service_integration', 'deployment_packaging'],
            'download': ['artifact_creation', 'delivery_management']
        }
        return capabilities_map.get(agent_type, [])
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """요청 처리"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.metrics.total_requests += 1
            
            # 요청 타입에 따른 워크플로우 결정
            workflow = self._create_workflow(request)
            
            # 워크플로우 실행
            results = await self.orchestrator.execute_workflow(workflow)
            
            # 성공 메트릭 업데이트
            self.metrics.successful_requests += 1
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self._update_response_time(execution_time)
            
            return {
                'status': 'success',
                'results': results,
                'execution_time_ms': execution_time,
                'workflow_steps': len(workflow)
            }
            
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Request processing failed: {str(e)}")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time_ms': (asyncio.get_event_loop().time() - start_time) * 1000
            }
    
    def _create_workflow(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """요청에 따른 워크플로우 생성"""
        request_type = request.get('type', 'full_development')
        
        if request_type == 'full_development':
            return [
                {
                    'agent_type': 'nl_input',
                    'input_data': {'description': request.get('description', '')},
                    'parallel': False
                },
                {
                    'agent_type': 'ui_selection',
                    'input_data': {'requirements': '${nl_input.result}'},
                    'parallel': False
                },
                {
                    'agent_type': 'parser',
                    'input_data': {'requirements': '${nl_input.result}'},
                    'parallel': False
                },
                {
                    'agents': [
                        {
                            'type': 'component_decision',
                            'input': {'parsed_requirements': '${parser.result}'}
                        },
                        {
                            'type': 'search',
                            'input': {'requirements': '${parser.result}'}
                        }
                    ],
                    'parallel': True
                },
                {
                    'agent_type': 'match_rate',
                    'input_data': {
                        'requirements': '${parser.result}',
                        'components': '${search.result}'
                    },
                    'parallel': False
                },
                {
                    'agent_type': 'generation',
                    'input_data': {
                        'components': '${match_rate.result}',
                        'ui_framework': '${ui_selection.result}'
                    },
                    'parallel': False
                },
                {
                    'agent_type': 'assembly',
                    'input_data': {'generated_code': '${generation.result}'},
                    'parallel': False
                },
                {
                    'agent_type': 'download',
                    'input_data': {'assembled_project': '${assembly.result}'},
                    'parallel': False
                }
            ]
        
        # 기본 워크플로우
        return [
            {
                'agent_type': request.get('agent_type', 'nl_input'),
                'input_data': request.get('input_data', {}),
                'parallel': False
            }
        ]
    
    def _update_response_time(self, execution_time_ms: float):
        """평균 응답 시간 업데이트"""
        if self.metrics.successful_requests == 1:
            self.metrics.avg_response_time_ms = execution_time_ms
        else:
            # 이동 평균 계산
            alpha = 0.1  # 가중치
            self.metrics.avg_response_time_ms = (
                alpha * execution_time_ms + 
                (1 - alpha) * self.metrics.avg_response_time_ms
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        uptime = (datetime.utcnow() - self.system_start_time).total_seconds()
        self.metrics.system_uptime_s = uptime
        
        orchestrator_status = self.orchestrator.get_status()
        agno_metrics = self.agno_manager.get_performance_metrics()
        
        return {
            'system_metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'success_rate': (
                    self.metrics.successful_requests / max(self.metrics.total_requests, 1)
                ),
                'avg_response_time_ms': self.metrics.avg_response_time_ms,
                'uptime_s': uptime
            },
            'orchestrator': orchestrator_status,
            'agno_framework': agno_metrics,
            'core_agents': self.core_agent_types
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        try:
            # 간단한 테스트 요청
            test_request = {
                'type': 'health_check',
                'agent_type': 'nl_input',
                'input_data': {'test': True}
            }
            
            result = await self.process_request(test_request)
            
            return {
                'status': 'healthy',
                'test_result': result['status'] == 'success',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }