"""기존 UpgradeOrchestrator 호환성 레이어.

이 파일은 기존 코드와의 호환성을 유지하면서
AWS Agent Squad 기반 새 구현을 사용하도록 합니다.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# AWS 버전 import
from .aws_upgrade_orchestrator import (
    AWSUpgradeOrchestrator,
    AWSUpgradeConfig
)

logger = logging.getLogger(__name__)


# 기존 클래스명 유지 (호환성)
class UpgradeConfig(AWSUpgradeConfig):
    """기존 UpgradeConfig 호환성 클래스."""
    
    def __init__(self, **kwargs):
        # 기존 파라미터를 AWS 파라미터로 매핑
        aws_kwargs = {
            'project_path': kwargs.get('project_path', ''),
            'output_dir': kwargs.get('output_dir', '/tmp/upgrade_output'),
            'enable_evolution_loop': kwargs.get('enable_evolution_loop', True),
            'max_evolution_iterations': kwargs.get('max_evolution_iterations', 10),
            'convergence_threshold': kwargs.get('convergence_threshold', 0.95),
            'ai_driven_workflow': kwargs.get('ai_driven_workflow', True),
            'enable_personas': kwargs.get('enable_personas', True)
        }
        super().__init__(**aws_kwargs)


class UpgradeReport:
    """기존 UpgradeReport 호환성 클래스."""
    
    def __init__(self, result: Dict[str, Any]):
        self.success = result.get('success', False)
        self.iterations = result.get('iterations', 0)
        self.final_gap_score = result.get('final_gap_score', 1.0)
        self.documents = result.get('final_documents', {})
        self.raw_result = result


class UpgradeOrchestrator:
    """기존 UpgradeOrchestrator 호환성 클래스.
    
    내부적으로 AWS Agent Squad 버전을 사용합니다.
    """
    
    def __init__(self, config: UpgradeConfig):
        """오케스트레이터 초기화."""
        logger.info("🔄 호환성 레이어를 통해 AWS UpgradeOrchestrator 사용")
        
        # AWS 버전 생성
        self.aws_orchestrator = AWSUpgradeOrchestrator(config)
        self.config = config
        
        # 호환성을 위한 속성
        self.memory_hub = None
        self.document_context = self.aws_orchestrator.document_context
        self.persona = self.aws_orchestrator.persona
        
        # 에이전트 속성 (호환성)
        self.requirement_analyzer = None
        self.external_researcher = None
        self.gap_analyzer = None
        self.system_architect = None
        self.orchestrator_designer = None
        self.planner_agent = None
        self.task_creator_agent = None
        self.code_generator = None
        self.quality_gate = None
    
    async def initialize(self):
        """에이전트 초기화."""
        await self.aws_orchestrator.initialize()
        
        # 호환성을 위한 에이전트 참조 설정
        if self.aws_orchestrator.agents_initialized:
            # AWS Squad의 에이전트를 참조
            logger.info("✅ 호환성 레이어 초기화 완료")
    
    async def execute_evolution_loop(self, requirements: str) -> UpgradeReport:
        """Evolution Loop 실행 (호환성 메서드)."""
        result = await self.aws_orchestrator.execute_evolution_loop(requirements)
        return UpgradeReport(result)
    
    async def execute(self, requirements: str) -> UpgradeReport:
        """실행 (호환성 메서드)."""
        if self.config.enable_evolution_loop:
            return await self.execute_evolution_loop(requirements)
        else:
            result = await self.aws_orchestrator.execute_ai_driven(requirements)
            return UpgradeReport(result)
    
    async def analyze_current_state(self, project_path: str) -> Dict[str, Any]:
        """현재 상태 분석 (호환성 메서드)."""
        # AWS 버전은 Evolution Loop 내에서 처리
        return {
            'project_path': project_path,
            'status': 'analyzed',
            'message': 'AWS Agent Squad 버전에서 자동 처리됨'
        }
    
    async def analyze_gap(self, current_state: Dict, requirements: str) -> Dict[str, Any]:
        """갭 분석 (호환성 메서드)."""
        return {
            'gap_score': self.aws_orchestrator.get_gap_score(),
            'iteration': self.aws_orchestrator.get_iteration_count()
        }
    
    def get_shared_documents(self) -> Dict[str, Any]:
        """공유 문서 반환."""
        return self.aws_orchestrator.get_shared_documents()