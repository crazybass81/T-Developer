"""AWS Agent Squad 기반 NewBuilderOrchestrator.

새로운 프로젝트를 SeedProduct로 생성하는 오케스트레이터입니다.
AWS Agent Squad 프레임워크와 Bedrock AgentCore 런타임을 사용합니다.

SeedProduct란:
- 일반적인 MVP와 다르게 진화의 씨앗이 되는 최소단위 프로젝트
- Evolution Loop를 통해 점진적으로 성장할 수 있는 기반 구조
- 확장과 변경이 용이한 아키텍처

주요 기능:
1. 첫 루프 차별화 - 현재 상태 분석 건너뛰기, 갭 분석은 우선순위 결정용
2. Evolution Loop - 2번째 루프부터 갭이 0이 될 때까지 반복
3. AI-Driven 워크플로우 - AI가 실행 순서 결정
4. 모든 문서 공유 - 모든 에이전트가 모든 문서 참조
5. 페르소나 시스템 - 각 에이전트의 고유한 성격
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import shutil

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
class SeedProductConfig:
    """SeedProduct 생성 설정."""
    
    # 기본 설정
    name: str
    type: str  # api, web, cli, library, microservice
    language: str  # python, javascript, go, rust, java
    framework: Optional[str] = None  # fastapi, express, gin, actix, spring
    
    # 진화 설정
    evolution_ready: bool = True  # Evolution Loop 준비 상태
    extensibility_level: str = "high"  # low, medium, high
    modularity: bool = True
    
    # 아키텍처 패턴
    architecture_pattern: str = "clean"  # clean, hexagonal, layered, mvc
    enable_plugins: bool = True
    enable_hooks: bool = True


@dataclass
class AWSNewBuilderConfig:
    """AWS 기반 NewBuilder 설정.
    
    AWS Agent Squad 프레임워크를 사용하는
    NewBuilderOrchestrator의 설정입니다.
    """
    
    # 프로젝트 설정
    project_name: str
    output_dir: str = "/tmp/newbuild_output"
    seed_config: Optional[SeedProductConfig] = None
    
    # Evolution Loop 설정
    enable_evolution_loop: bool = True
    max_evolution_iterations: int = 10
    convergence_threshold: float = 0.95
    gap_tolerance: float = 0.01
    
    # 첫 루프 설정
    skip_current_state_first_loop: bool = True  # 첫 루프에서 현재 상태 분석 건너뛰기
    use_gap_for_priority: bool = True  # 첫 루프에서 갭 분석을 우선순위 결정용으로 사용
    
    # AI 드리븐 설정
    ai_driven_workflow: bool = True
    ai_decision_threshold: float = 0.8
    
    # AWS Bedrock 설정
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens: int = 4096
    temperature: float = 0.8  # 창의성을 위해 약간 높게
    
    # 실행 설정
    max_parallel_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    
    # 문서 설정
    share_all_documents: bool = True
    save_documents: bool = True
    
    # 페르소나 설정
    enable_personas: bool = True


class AWSNewBuilderOrchestrator:
    """AWS Agent Squad 기반 NewBuilderOrchestrator.
    
    창조 아키텍트(Creation Architect)로서 새로운 시스템을 창조합니다.
    SeedProduct를 생성하고 Evolution Loop를 통해 성장시킵니다.
    """
    
    def __init__(self, config: AWSNewBuilderConfig):
        """오케스트레이터 초기화.
        
        Args:
            config: NewBuilder 설정
        """
        self.config = config
        self.is_first_loop = True
        self.current_iteration = 0
        
        # 페르소나 설정
        self.persona = get_persona("NewBuildOrchestrator") if config.enable_personas else None
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
            name="NewBuilderSquad",
            strategy=ExecutionStrategy.AI_DRIVEN,  # 첫 루프는 AI-Driven
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
        
        # 프로젝트 경로
        self.project_path = None
        
        logger.info("🚀 AWS NewBuilderOrchestrator 초기화 완료")
    
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
        
        self.agents_initialized = True
        logger.info("✅ 모든 에이전트 초기화 완료")
    
    async def create_seed_product(self, requirements: str) -> Dict[str, Any]:
        """SeedProduct 생성 및 Evolution Loop 실행.
        
        첫 루프는 특별한 방식으로 실행되고,
        2번째 루프부터는 일반 Evolution Loop를 실행합니다.
        
        Args:
            requirements: 프로젝트 요구사항
            
        Returns:
            생성 결과
        """
        # 에이전트 초기화
        await self.initialize()
        
        logger.info("🌱 SeedProduct 생성 시작")
        logger.info(f"📋 요구사항: {requirements}")
        
        # 출력 디렉토리 생성
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 프로젝트 경로 설정
        self.project_path = output_path / self.config.project_name
        self.project_path.mkdir(exist_ok=True)
        
        # 전체 결과 저장
        all_results = {
            'project_name': self.config.project_name,
            'project_path': str(self.project_path),
            'requirements': requirements,
            'iterations': []
        }
        
        # 첫 번째 루프 (SeedProduct 생성)
        logger.info("\n🔄 첫 번째 루프 - SeedProduct 생성")
        first_loop_result = await self._execute_first_loop(requirements)
        all_results['iterations'].append(first_loop_result)
        
        # Evolution Loop (2번째 루프부터)
        if self.config.enable_evolution_loop:
            self.is_first_loop = False
            self.squad.config.strategy = ExecutionStrategy.EVOLUTION_LOOP
            
            logger.info("\n🔄 Evolution Loop 시작 (2번째 루프부터)")
            
            # Evolution Loop 실행
            evolution_task = {
                'type': 'evolution',
                'description': f"SeedProduct를 요구사항에 맞게 진화",
                'project_path': str(self.project_path),
                'input_data': {
                    'requirements': requirements,
                    'seed_product': first_loop_result,
                    'project_path': str(self.project_path)
                },
                'requires_ai': True
            }
            
            evolution_result = await self.squad.execute_squad(evolution_task)
            all_results['evolution'] = evolution_result
            all_results['converged'] = evolution_result.get('converged', False)
            all_results['final_gap_score'] = evolution_result.get('final_gap_score', 1.0)
        
        # 문서 저장
        if self.config.save_documents:
            await self._save_documents(all_results)
        
        # 최종 보고
        if all_results.get('converged', False):
            logger.info(f"✅ SeedProduct 생성 및 진화 완료! (최종 갭: {all_results['final_gap_score']:.2%})")
        else:
            logger.info(f"🌱 SeedProduct 생성 완료 (Evolution Loop: {self.config.enable_evolution_loop})")
        
        return all_results
    
    async def _execute_first_loop(self, requirements: str) -> Dict[str, Any]:
        """첫 번째 루프 실행.
        
        현재 상태 분석을 건너뛰고, 갭 분석은 우선순위 결정용으로 사용합니다.
        
        Args:
            requirements: 요구사항
            
        Returns:
            첫 루프 결과
        """
        result = {'loop': 1, 'type': 'seed_creation'}
        
        # 1. 요구사항 분석
        logger.info("1️⃣ 요구사항 분석")
        req_task = {
            'type': 'requirement_analysis',
            'description': requirements,
            'input_data': {'requirements': requirements},
            'requires_ai': True
        }
        
        if 'RequirementAnalyzer' in self.squad.agents:
            req_result = await self.runtime.execute_agent(
                'RequirementAnalyzer',
                self.squad.agents['RequirementAnalyzer'],
                req_task
            )
            result['requirements'] = req_result
        
        # 2. 외부 리서치
        logger.info("2️⃣ 외부 리서치")
        research_task = {
            'type': 'research',
            'description': f"SeedProduct 생성을 위한 리서치",
            'input_data': {
                'requirements': requirements,
                'seed_config': self.config.seed_config.__dict__ if self.config.seed_config else {}
            },
            'requires_ai': True
        }
        
        if 'ExternalResearcher' in self.squad.agents:
            research_result = await self.runtime.execute_agent(
                'ExternalResearcher',
                self.squad.agents['ExternalResearcher'],
                research_task
            )
            result['research'] = research_result
        
        # 3. 갭 분석 (우선순위 결정용)
        logger.info("3️⃣ 갭 분석 (우선순위 결정)")
        gap_task = {
            'type': 'priority_analysis',
            'description': "구현 우선순위 결정",
            'input_data': {
                'requirements': result.get('requirements', {}),
                'research': result.get('research', {})
            },
            'requires_ai': True,
            'prompt': f"""
요구사항과 리서치를 바탕으로 SeedProduct 구현 우선순위를 결정하세요.

요구사항: {requirements}

다음을 포함하여 분석하세요:
1. 핵심 기능 (반드시 포함되어야 할 최소 기능)
2. 확장 가능성을 위한 기반 구조
3. Evolution Loop를 위한 준비 사항
4. 구현 순서와 우선순위
"""
        }
        
        if 'GapAnalyzer' in self.squad.agents:
            gap_result = await self.runtime.execute_agent(
                'GapAnalyzer',
                self.squad.agents['GapAnalyzer'],
                gap_task
            )
            result['priorities'] = gap_result
        
        # 4. 시스템 아키텍처 설계
        logger.info("4️⃣ 시스템 아키텍처 설계")
        arch_task = {
            'type': 'architecture_design',
            'description': "SeedProduct 아키텍처 설계",
            'input_data': {
                'requirements': result.get('requirements', {}),
                'priorities': result.get('priorities', {}),
                'seed_config': self.config.seed_config.__dict__ if self.config.seed_config else {}
            },
            'requires_ai': True
        }
        
        if 'SystemArchitect' in self.squad.agents:
            arch_result = await self.runtime.execute_agent(
                'SystemArchitect',
                self.squad.agents['SystemArchitect'],
                arch_task
            )
            result['architecture'] = arch_result
        
        # 5. 오케스트레이터 설계
        logger.info("5️⃣ 오케스트레이터 설계")
        orch_task = {
            'type': 'orchestrator_design',
            'description': "SeedProduct 오케스트레이션 설계",
            'input_data': {
                'architecture': result.get('architecture', {}),
                'priorities': result.get('priorities', {})
            },
            'requires_ai': True
        }
        
        if 'OrchestratorDesigner' in self.squad.agents:
            orch_result = await self.runtime.execute_agent(
                'OrchestratorDesigner',
                self.squad.agents['OrchestratorDesigner'],
                orch_task
            )
            result['orchestration'] = orch_result
        
        # 6. 계획 수립
        logger.info("6️⃣ 구현 계획 수립")
        plan_task = {
            'type': 'planning',
            'description': "SeedProduct 구현 계획",
            'input_data': {
                'architecture': result.get('architecture', {}),
                'orchestration': result.get('orchestration', {}),
                'priorities': result.get('priorities', {})
            },
            'requires_ai': True
        }
        
        if 'PlannerAgent' in self.squad.agents:
            plan_result = await self.runtime.execute_agent(
                'PlannerAgent',
                self.squad.agents['PlannerAgent'],
                plan_task
            )
            result['plan'] = plan_result
        
        # 7. 세부 태스크 생성
        logger.info("7️⃣ 세부 태스크 생성")
        task_create = {
            'type': 'task_creation',
            'description': "SeedProduct 구현 태스크",
            'input_data': {
                'plan': result.get('plan', {}),
                'architecture': result.get('architecture', {})
            },
            'requires_ai': True
        }
        
        if 'TaskCreatorAgent' in self.squad.agents:
            task_result = await self.runtime.execute_agent(
                'TaskCreatorAgent',
                self.squad.agents['TaskCreatorAgent'],
                task_create
            )
            result['tasks'] = task_result
        
        # 8. 코드 생성
        logger.info("8️⃣ SeedProduct 코드 생성")
        code_task = {
            'type': 'code_generation',
            'description': "SeedProduct 코드 생성",
            'project_path': str(self.project_path),
            'input_data': {
                'tasks': result.get('tasks', {}),
                'architecture': result.get('architecture', {}),
                'project_path': str(self.project_path)
            },
            'requires_ai': True
        }
        
        if 'CodeGenerator' in self.squad.agents:
            code_result = await self.runtime.execute_agent(
                'CodeGenerator',
                self.squad.agents['CodeGenerator'],
                code_task
            )
            result['code'] = code_result
            
            # 실제 파일 생성
            await self._create_project_files(code_result)
        
        # 9. 테스트 생성 및 실행
        logger.info("9️⃣ 테스트 생성 및 실행")
        test_task = {
            'type': 'testing',
            'description': "SeedProduct 테스트",
            'project_path': str(self.project_path),
            'input_data': {
                'code': result.get('code', {}),
                'project_path': str(self.project_path)
            },
            'requires_ai': True
        }
        
        if 'TestAgent' in self.squad.agents:
            test_result = await self.runtime.execute_agent(
                'TestAgent',
                self.squad.agents['TestAgent'],
                test_task
            )
            result['tests'] = test_result
        
        result['success'] = True
        result['project_created'] = True
        result['project_path'] = str(self.project_path)
        
        logger.info("✅ 첫 번째 루프 완료 - SeedProduct 생성 성공")
        
        return result
    
    async def _create_project_files(self, code_result: Dict[str, Any]):
        """프로젝트 파일 생성.
        
        Args:
            code_result: 코드 생성 결과
        """
        # 기본 프로젝트 구조 생성
        project_structure = {
            'src': {},
            'tests': {},
            'docs': {},
            'config': {}
        }
        
        for dir_name in project_structure:
            dir_path = self.project_path / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # README 생성
        readme_content = f"""# {self.config.project_name}

## 개요
이 프로젝트는 T-Developer의 NewBuilderOrchestrator에 의해 생성된 SeedProduct입니다.
Evolution Loop를 통해 점진적으로 발전할 수 있도록 설계되었습니다.

## 특징
- 🌱 SeedProduct 아키텍처
- 🔄 Evolution Loop 지원
- 🎭 페르소나 기반 에이전트
- 🤖 AI-Driven Development

## 구조
```
{self.config.project_name}/
├── src/           # 소스 코드
├── tests/         # 테스트 코드
├── docs/          # 문서
└── config/        # 설정 파일
```

## 생성 정보
- 생성일: {datetime.now().isoformat()}
- 오케스트레이터: NewBuilderOrchestrator (창조 아키텍트)
- 프레임워크: AWS Agent Squad
- 런타임: Bedrock AgentCore
"""
        
        readme_path = self.project_path / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
        
        # 기본 설정 파일 생성
        if self.config.seed_config:
            import json
            config_path = self.project_path / "config" / "seed_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.seed_config.__dict__, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 프로젝트 파일 생성: {self.project_path}")
    
    async def _save_documents(self, result: Dict[str, Any]):
        """문서 저장.
        
        Args:
            result: 실행 결과
        """
        docs_path = self.project_path / "docs"
        docs_path.mkdir(exist_ok=True)
        
        # 전체 보고서 저장
        report_path = docs_path / f"creation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 생성 보고서 저장: {report_path}")
        
        # 개별 문서 저장
        documents_path = docs_path / "agent_documents"
        documents_path.mkdir(exist_ok=True)
        
        all_docs = self.document_context.get_all_documents()
        for agent_name, doc in all_docs.items():
            doc_path = documents_path / f"{agent_name}.json"
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📂 에이전트 문서 저장: {documents_path}")
    
    def get_project_path(self) -> Optional[Path]:
        """생성된 프로젝트 경로 반환.
        
        Returns:
            프로젝트 경로
        """
        return self.project_path
    
    def get_shared_documents(self) -> Dict[str, Any]:
        """공유 문서 반환.
        
        Returns:
            모든 에이전트가 공유하는 문서
        """
        return self.document_context.get_all_documents()