"""AWS Agent Squad 기반 UpgradeOrchestrator.

기존 프로젝트를 업그레이드/디버깅/리팩터링하는 오케스트레이터입니다.
AWS Agent Squad 프레임워크와 Bedrock AgentCore 런타임을 사용합니다.

주요 기능:
1. Evolution Loop - 갭이 0이 될 때까지 반복
2. AI-Driven 워크플로우 - AI가 실행 순서 결정
3. 모든 문서 공유 - 모든 에이전트가 모든 문서 참조
4. 페르소나 시스템 - 각 에이전트의 고유한 성격
5. 100% Real AI - Mock/Fake 없음
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# AWS Agent Squad 프레임워크
from ..aws_agent_squad.core import (
    AgentRuntime,
    RuntimeConfig,
    SquadOrchestrator,
    SquadConfig
)
from ..aws_agent_squad.core.squad_orchestrator import ExecutionStrategy

# 에이전트
from ..agents import (
    RequirementAnalyzer,
    StaticAnalyzer,
    CodeAnalysisAgent,
    BehaviorAnalyzer,
    ImpactAnalyzer,
    QualityGate,
    ExternalResearcher,
    GapAnalyzer,
    SystemArchitect,
    OrchestratorDesigner,
    PlannerAgent,
    TaskCreatorAgent,
    CodeGenerator,
    TestAgent
)

# 페르소나
from ..agents.personas import get_persona

# 문서 컨텍스트
from ..memory.document_context import SharedDocumentContext

logger = logging.getLogger(__name__)


@dataclass
class AWSUpgradeConfig:
    """AWS 기반 업그레이드 설정.
    
    AWS Agent Squad 프레임워크를 사용하는
    UpgradeOrchestrator의 설정입니다.
    """
    
    # 프로젝트 설정
    project_path: str
    output_dir: str = "/tmp/upgrade_output"
    
    # Evolution Loop 설정
    enable_evolution_loop: bool = True
    max_evolution_iterations: int = 10
    convergence_threshold: float = 0.95
    gap_tolerance: float = 0.01
    
    # AI 드리븐 설정
    ai_driven_workflow: bool = True
    ai_decision_threshold: float = 0.8
    
    # AWS Bedrock 설정
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # 실행 설정
    max_parallel_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    
    # 문서 설정
    share_all_documents: bool = True
    save_documents: bool = True
    
    # 페르소나 설정
    enable_personas: bool = True


class AWSUpgradeOrchestrator:
    """AWS Agent Squad 기반 UpgradeOrchestrator.
    
    진화 마에스트로(Evolution Maestro)로서 시스템을 점진적으로 개선합니다.
    갭이 0이 될 때까지 Evolution Loop를 실행합니다.
    """
    
    def __init__(self, config: AWSUpgradeConfig):
        """오케스트레이터 초기화.
        
        Args:
            config: 업그레이드 설정
        """
        self.config = config
        
        # 페르소나 설정
        self.persona = get_persona("UpgradeOrchestrator") if config.enable_personas else None
        if self.persona:
            logger.info(f"🎭 페르소나 활성화: {self.persona.name} - '{self.persona.catchphrase}'")
        
        # AWS Agent Squad 런타임 초기화
        runtime_config = RuntimeConfig(
            region=config.aws_region,
            model_id=config.bedrock_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            max_parallel_agents=config.max_parallel_agents,
            timeout_seconds=config.timeout_seconds,
            retry_count=config.retry_count,
            max_evolution_iterations=config.max_evolution_iterations,
            convergence_threshold=config.convergence_threshold,
            gap_tolerance=config.gap_tolerance
        )
        self.runtime = AgentRuntime(runtime_config)
        
        # Squad Orchestrator 초기화
        squad_config = SquadConfig(
            name="UpgradeSquad",
            strategy=ExecutionStrategy.EVOLUTION_LOOP if config.enable_evolution_loop else ExecutionStrategy.AI_DRIVEN,
            enable_evolution_loop=config.enable_evolution_loop,
            convergence_threshold=config.convergence_threshold,
            max_iterations=config.max_evolution_iterations,
            enable_ai_orchestration=config.ai_driven_workflow,
            share_all_documents=config.share_all_documents
        )
        self.squad = SquadOrchestrator(self.runtime, squad_config)
        
        # 문서 컨텍스트
        self.document_context = SharedDocumentContext()
        
        # 에이전트 초기화는 나중에
        self.agents_initialized = False
        
        logger.info("🚀 AWS UpgradeOrchestrator 초기화 완료")
    
    async def initialize(self):
        """에이전트 초기화 및 등록.
        
        모든 에이전트를 생성하고 Squad에 등록합니다.
        각 에이전트에 페르소나를 부여합니다.
        """
        if self.agents_initialized:
            return
        
        logger.info("🔧 에이전트 초기화 시작...")
        
        # 에이전트 생성 및 등록
        agents_config = [
            ("RequirementAnalyzer", RequirementAnalyzer),
            ("StaticAnalyzer", StaticAnalyzer),
            ("CodeAnalysisAgent", CodeAnalysisAgent),
            ("BehaviorAnalyzer", BehaviorAnalyzer),
            ("ImpactAnalyzer", ImpactAnalyzer),
            ("QualityGate", QualityGate),
            ("ExternalResearcher", ExternalResearcher),
            ("GapAnalyzer", GapAnalyzer),
            ("SystemArchitect", SystemArchitect),
            ("OrchestratorDesigner", OrchestratorDesigner),
            ("PlannerAgent", PlannerAgent),
            ("TaskCreatorAgent", TaskCreatorAgent),
            ("CodeGenerator", CodeGenerator),
            ("TestAgent", TestAgent)
        ]
        
        for agent_name, agent_class in agents_config:
            try:
                # 에이전트 인스턴스 생성
                agent_instance = agent_class(
                    memory_hub=None,  # AWS Runtime이 메모리 관리
                    document_context=self.document_context
                )
                
                # 에이전트 실행 함수 생성
                async def agent_execute(task, context, agent=agent_instance):
                    """에이전트 실행 래퍼."""
                    # AWS Agent Squad 태스크를 기존 에이전트 태스크로 변환
                    from ..agents.base import AgentTask
                    agent_task = AgentTask(
                        type=task.get('type', 'default'),
                        description=task.get('description', ''),
                        input_data=task.get('input_data', {}),
                        config=task.get('config', {})
                    )
                    
                    # 에이전트 실행
                    result = await agent.execute(agent_task)
                    
                    # 결과를 문서 컨텍스트에 추가
                    if context.get('share_all_documents', True):
                        self.document_context.add_document(
                            agent_name,
                            result.output_data,
                            document_type=task.get('type', 'default')
                        )
                    
                    return result.output_data
                
                # 페르소나 가져오기
                persona = None
                if self.config.enable_personas:
                    persona_obj = get_persona(agent_name)
                    if persona_obj:
                        persona = {
                            'name': persona_obj.name,
                            'role': persona_obj.role,
                            'personality_traits': [t.value for t in persona_obj.personality_traits],
                            'expertise': persona_obj.expertise,
                            'communication_style': persona_obj.communication_style,
                            'core_values': persona_obj.core_values,
                            'catchphrase': persona_obj.catchphrase
                        }
                
                # Squad에 에이전트 등록
                self.squad.register_agent(agent_name, agent_execute, persona)
                
            except Exception as e:
                logger.error(f"❌ {agent_name} 초기화 실패: {str(e)}")
        
        # 기본 실행 순서 설정
        self.squad.set_execution_order([
            "RequirementAnalyzer",
            "StaticAnalyzer",
            "CodeAnalysisAgent",
            "BehaviorAnalyzer",
            "ImpactAnalyzer",
            "QualityGate",
            "ExternalResearcher",
            "GapAnalyzer",
            "SystemArchitect",
            "OrchestratorDesigner",
            "PlannerAgent",
            "TaskCreatorAgent",
            "CodeGenerator",
            "TestAgent"
        ])
        
        self.agents_initialized = True
        logger.info("✅ 모든 에이전트 초기화 완료")
    
    async def execute_evolution_loop(self, requirements: str) -> Dict[str, Any]:
        """Evolution Loop 실행.
        
        갭이 0이 될 때까지 시스템을 진화시킵니다.
        
        Args:
            requirements: 요구사항
            
        Returns:
            진화 결과
        """
        # 에이전트 초기화
        await self.initialize()
        
        logger.info("🔄 Evolution Loop 실행 시작")
        logger.info(f"📋 요구사항: {requirements}")
        
        # 초기 작업 생성
        initial_task = {
            'type': 'upgrade',
            'description': requirements,
            'project_path': self.config.project_path,
            'output_dir': self.config.output_dir,
            'input_data': {
                'requirements': requirements,
                'project_path': self.config.project_path
            },
            'config': {
                'enable_evolution': self.config.enable_evolution_loop,
                'share_documents': self.config.share_all_documents
            },
            'requires_ai': True,
            'prompt': f"""
프로젝트 업그레이드 요구사항:
{requirements}

프로젝트 경로: {self.config.project_path}

이 요구사항을 분석하고 업그레이드 계획을 수립하세요.
"""
        }
        
        # Squad 실행
        result = await self.squad.execute_squad(initial_task)
        
        # 결과 처리
        final_result = {
            'success': result.get('converged', False),
            'iterations': result.get('total_iterations', 0),
            'final_gap_score': result.get('final_gap_score', 1.0),
            'evolution_history': result.get('iterations', []),
            'final_documents': self.document_context.get_all_documents(),
            'execution_metrics': result.get('execution_metrics', {})
        }
        
        # 문서 저장
        if self.config.save_documents:
            await self._save_documents(final_result)
        
        # 최종 보고
        if final_result['success']:
            logger.info(f"✅ Evolution Loop 성공! (반복: {final_result['iterations']}, 최종 갭: {final_result['final_gap_score']:.2%})")
        else:
            logger.warning(f"⚠️ Evolution Loop 미완료 (반복: {final_result['iterations']}, 최종 갭: {final_result['final_gap_score']:.2%})")
        
        return final_result
    
    async def execute_ai_driven(self, requirements: str) -> Dict[str, Any]:
        """AI 드리븐 실행.
        
        AI가 에이전트 실행 순서를 결정합니다.
        
        Args:
            requirements: 요구사항
            
        Returns:
            실행 결과
        """
        # 에이전트 초기화
        await self.initialize()
        
        # Squad 전략 변경
        self.squad.config.strategy = ExecutionStrategy.AI_DRIVEN
        
        logger.info("🤖 AI-Driven 실행 시작")
        
        # 초기 작업 생성
        initial_task = {
            'type': 'upgrade',
            'description': requirements,
            'project_path': self.config.project_path,
            'input_data': {
                'requirements': requirements,
                'project_path': self.config.project_path
            },
            'requires_ai': True
        }
        
        # Squad 실행
        result = await self.squad.execute_squad(initial_task)
        
        return {
            'success': True,
            'executions': result.get('executions', []),
            'final_documents': self.document_context.get_all_documents(),
            'execution_metrics': result.get('execution_metrics', {})
        }
    
    async def _save_documents(self, result: Dict[str, Any]):
        """문서 저장.
        
        Args:
            result: 실행 결과
        """
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 전체 보고서 저장
        report_path = output_path / f"upgrade_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 보고서 저장: {report_path}")
        
        # 개별 문서 저장
        docs_path = output_path / "documents"
        docs_path.mkdir(exist_ok=True)
        
        for agent_name, doc in result.get('final_documents', {}).items():
            doc_path = docs_path / f"{agent_name}.json"
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📂 문서 저장: {docs_path}")
    
    def get_gap_score(self) -> float:
        """현재 갭 스코어 반환.
        
        Returns:
            갭 스코어
        """
        return self.squad.get_gap_score()
    
    def get_iteration_count(self) -> int:
        """현재 반복 횟수 반환.
        
        Returns:
            반복 횟수
        """
        return self.squad.get_iteration_count()
    
    def get_shared_documents(self) -> Dict[str, Any]:
        """공유 문서 반환.
        
        Returns:
            모든 에이전트가 공유하는 문서
        """
        return self.document_context.get_all_documents()