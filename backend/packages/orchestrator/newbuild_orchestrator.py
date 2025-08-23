"""기존 NewBuildOrchestrator 호환성 레이어.

이 파일은 기존 코드와의 호환성을 유지하면서
AWS Agent Squad 기반 새 구현을 사용하도록 합니다.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# AWS 버전 import
from .aws_newbuilder_orchestrator import (
    AWSNewBuilderOrchestrator,
    AWSNewBuilderConfig,
    SeedProductConfig
)

logger = logging.getLogger(__name__)


# 기존 클래스명 유지 (호환성)
class NewBuildConfig(AWSNewBuilderConfig):
    """기존 NewBuildConfig 호환성 클래스."""
    
    def __init__(self, **kwargs):
        # SeedProduct 설정 생성
        seed_config = None
        if 'project_type' in kwargs:
            seed_config = SeedProductConfig(
                name=kwargs.get('project_name', 'new-project'),
                type=kwargs.get('project_type', 'api'),
                language=kwargs.get('language', 'python'),
                framework=kwargs.get('framework', None),
                architecture_pattern=kwargs.get('architecture_pattern', 'clean')
            )
        
        # 기존 파라미터를 AWS 파라미터로 매핑
        aws_kwargs = {
            'project_name': kwargs.get('project_name', 'new-project'),
            'output_dir': kwargs.get('output_dir', '/tmp/newbuild_output'),
            'seed_config': seed_config,
            'enable_evolution_loop': kwargs.get('enable_evolution_loop', True),
            'max_evolution_iterations': kwargs.get('max_evolution_iterations', 10),
            'convergence_threshold': kwargs.get('convergence_threshold', 0.95),
            'skip_current_state_first_loop': True,
            'use_gap_for_priority': True,
            'ai_driven_workflow': kwargs.get('ai_driven_workflow', True),
            'enable_personas': kwargs.get('enable_personas', True)
        }
        super().__init__(**aws_kwargs)


class NewBuildReport:
    """기존 NewBuildReport 호환성 클래스."""
    
    def __init__(self, result: Dict[str, Any]):
        self.success = result.get('success', False) or result.get('project_created', False)
        self.project_path = result.get('project_path', '')
        self.iterations = result.get('iterations', [])
        self.converged = result.get('converged', False)
        self.final_gap_score = result.get('final_gap_score', 1.0)
        self.documents = result.get('final_documents', {})
        self.raw_result = result


class NewBuildOrchestrator:
    """기존 NewBuildOrchestrator 호환성 클래스.
    
    내부적으로 AWS Agent Squad 버전을 사용합니다.
    """
    
    def __init__(self, config: NewBuildConfig):
        """오케스트레이터 초기화."""
        logger.info("🔄 호환성 레이어를 통해 AWS NewBuilderOrchestrator 사용")
        
        # AWS 버전 생성
        self.aws_orchestrator = AWSNewBuilderOrchestrator(config)
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
        self.test_agent = None
    
    async def initialize(self):
        """에이전트 초기화."""
        await self.aws_orchestrator.initialize()
        
        # 호환성을 위한 에이전트 참조 설정
        if self.aws_orchestrator.agents_initialized:
            logger.info("✅ 호환성 레이어 초기화 완료")
    
    async def build(self, requirements: str) -> NewBuildReport:
        """프로젝트 빌드 (호환성 메서드)."""
        result = await self.aws_orchestrator.create_seed_product(requirements)
        return NewBuildReport(result)
    
    async def create_seed_product(self, requirements: str) -> NewBuildReport:
        """SeedProduct 생성 (호환성 메서드)."""
        result = await self.aws_orchestrator.create_seed_product(requirements)
        return NewBuildReport(result)
    
    async def execute_first_loop(self, requirements: str) -> Dict[str, Any]:
        """첫 번째 루프 실행 (호환성 메서드)."""
        # AWS 버전의 첫 루프 로직이 create_seed_product에 포함됨
        result = await self.aws_orchestrator.create_seed_product(requirements)
        if result.get('iterations'):
            return result['iterations'][0]  # 첫 번째 반복 결과 반환
        return result
    
    def get_project_path(self) -> Optional[Path]:
        """프로젝트 경로 반환."""
        return self.aws_orchestrator.get_project_path()
    
    def get_shared_documents(self) -> Dict[str, Any]:
        """공유 문서 반환."""
        return self.aws_orchestrator.get_shared_documents()