"""NewBuild Orchestrator - 새 프로젝트를 처음부터 빌드하는 오케스트레이터

이 오케스트레이터는 자연어 요구사항으로부터 완전히 새로운 프로젝트를 생성합니다.
Evolution Loop를 통해 생성된 프로젝트를 지속적으로 개선합니다.

주요 특징:
1. Evolution Loop 지원 - 생성 후 반복적 개선
2. 첫 번째 루프에서는 현재상태 분석 제외 (새 프로젝트이므로)
3. 갭분석을 우선순위 결정용으로 활용
4. 두 번째 루프부터는 UpgradeOrchestrator와 동일한 프로세스

첫 번째 루프 실행 순서:
1. RequirementAnalyzer - 요구사항 분석/문서화
2. ExternalResearcher - 베스트 프랙티스 조사
3. GapAnalyzer - 우선순위 결정 (목표 상태 정의)
4. SystemArchitect - 아키텍처 설계
5. OrchestratorDesigner - 구현 설계
6. PlannerAgent - Phase 계획
7. TaskCreatorAgent - 세부 태스크
8. ProjectInitializer - 프로젝트 구조 생성
9. CodeGenerator - 초기 코드 생성
10. 테스트 실행

두 번째 루프부터 (Evolution Loop):
1. 현재상태 분석 (병렬) - Static, Code, Behavior, Impact, Quality
2. ExternalResearcher - 추가 리서치
3. GapAnalyzer - 갭 분석
4. SystemArchitect - 아키텍처 진화
5. OrchestratorDesigner - 구현 개선
6. PlannerAgent - 개선 계획
7. TaskCreatorAgent - 개선 태스크
8. CodeGenerator - 코드 개선
9. 테스트 실행
10. 갭 확인 → 반복 또는 종료
"""

from __future__ import annotations

import asyncio
import logging
import json
import os
import shutil
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from backend.packages.agents.base import AgentTask, AgentResult, TaskStatus
from backend.packages.agents.ai_providers import BedrockAIProvider
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.system_architect import SystemArchitect
from backend.packages.agents.orchestrator_designer import OrchestratorDesigner
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.code_generator import CodeGenerator
from backend.packages.agents.quality_gate import QualityGate
# Evolution Loop를 위한 추가 에이전트
from backend.packages.agents.static_analyzer import StaticAnalyzer
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.gap_analyzer import GapAnalyzer
from backend.packages.agents.behavior_analyzer import BehaviorAnalyzer
from backend.packages.agents.impact_analyzer import ImpactAnalyzer
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType
from backend.packages.safety import CircuitBreaker, CircuitBreakerConfig, ResourceLimiter, ResourceLimit

# Agno 통합
from backend.packages.agno import AgnoManager
from backend.packages.agno.spec import AgentSpec as AgnoSpec
from backend.packages.agno.generator import CodeGenerator as AgnoCodeGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class NewBuildConfig:
    """새 프로젝트 빌드 설정"""
    
    project_name: str  # 프로젝트 이름
    output_dir: str = "/tmp/t-developer/new-projects"  # 프로젝트 생성 경로
    project_type: str = "web"  # web, api, cli, library, mobile
    language: str = "python"  # python, javascript, typescript, java, go
    framework: Optional[str] = None  # flask, django, react, vue, spring
    
    # 프로젝트 설정
    include_tests: bool = True  # 테스트 코드 생성
    include_docs: bool = True  # 문서 생성
    include_ci_cd: bool = True  # CI/CD 파이프라인 생성
    include_docker: bool = True  # Docker 설정 생성
    include_kubernetes: bool = False  # K8s 매니페스트 생성
    
    # AI 설정
    ai_driven_design: bool = True  # AI 기반 설계
    auto_generate_all: bool = True  # 모든 코드 자동 생성
    use_best_practices: bool = True  # 베스트 프랙티스 적용
    
    # Evolution Loop 설정
    enable_evolution_loop: bool = True  # Evolution Loop 활성화
    max_evolution_iterations: int = 5  # 최대 반복 횟수
    evolution_convergence_threshold: float = 0.90  # 수렴 임계값 (갭 해소율)
    auto_improve_code: bool = True  # 코드 자동 개선
    
    # 리소스 제한
    max_execution_time: int = 1800  # 30분
    max_files: int = 100  # 최대 생성 파일 수
    max_code_lines: int = 10000  # 최대 코드 라인 수


@dataclass
class ProjectStructure:
    """프로젝트 구조 정의"""
    
    root_dir: Path
    src_dir: Path
    test_dir: Path
    docs_dir: Path
    config_dir: Path
    
    # 파일 목록
    files_to_create: List[Dict[str, Any]] = field(default_factory=list)
    directories_to_create: List[Path] = field(default_factory=list)
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    project_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NewBuildReport:
    """새 프로젝트 빌드 보고서"""
    
    timestamp: str
    project_name: str
    output_path: str
    
    # 단계별 결과
    requirement_analysis: Optional[Dict[str, Any]] = None
    external_research: Optional[Dict[str, Any]] = None
    architecture_design: Optional[Dict[str, Any]] = None
    orchestrator_design: Optional[Dict[str, Any]] = None
    development_plan: Optional[Dict[str, Any]] = None
    detailed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    
    # 생성 결과
    project_structure: Optional[ProjectStructure] = None
    files_created: List[str] = field(default_factory=list)
    code_generated: Dict[str, Any] = field(default_factory=dict)
    tests_generated: Dict[str, Any] = field(default_factory=dict)
    documentation_generated: Dict[str, Any] = field(default_factory=dict)
    
    # 품질 메트릭
    quality_metrics: Optional[Dict[str, Any]] = None
    test_coverage: float = 0.0
    code_complexity: float = 0.0
    
    # 실행 메타데이터
    success: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    total_execution_time: float = 0.0
    
    # Evolution Loop 메타데이터
    evolution_iterations: int = 0  # Evolution Loop 반복 횟수
    gap_analysis: Optional[Dict[str, Any]] = None  # 갭 분석 결과
    current_state_analysis: Optional[Dict[str, Any]] = None  # 현재 상태 분석
    gaps_remaining: List[Dict[str, Any]] = field(default_factory=list)  # 남은 갭
    convergence_rate: float = 0.0  # 수렴률
    
    # 다음 단계
    next_steps: List[str] = field(default_factory=list)
    deployment_instructions: Optional[str] = None


class NewBuildOrchestrator:
    """새 프로젝트 빌드 오케스트레이터
    
    자연어 요구사항으로부터 완전히 새로운 프로젝트를 생성합니다.
    AI 드리븐 방식으로 최적의 아키텍처와 구현을 자동 생성합니다.
    """
    
    def __init__(self, config: NewBuildConfig):
        """초기화
        
        Args:
            config: 새 프로젝트 빌드 설정
        """
        self.config = config
        self.memory_hub = None
        
        # SharedDocumentContext 추가 - 모든 에이전트가 문서 공유
        self.document_context = None
        
        # 에이전트 초기화 (필요시 생성)
        self.requirement_analyzer = None
        self.external_researcher = None
        self.system_architect = None
        self.orchestrator_designer = None
        self.planner_agent = None
        self.task_creator_agent = None
        self.code_generator = None
        self.quality_gate = None
        
        # Evolution Loop를 위한 추가 에이전트
        self.gap_analyzer = None
        self.static_analyzer = None
        self.code_analyzer = None
        self.behavior_analyzer = None
        self.impact_analyzer = None
        
        # Agno 통합
        self.agno_manager = None
        self.agno_code_generator = None
        
        # AI Provider - 100% REAL AI
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # 페르소나 설정 - 창조 아키텍트
        from backend.packages.agents.personas import get_persona
        self.persona = get_persona("NewBuildOrchestrator")
        if self.persona:
            logger.info(f"🎭 페르소나 활성화: {self.persona.name} - '{self.persona.catchphrase}'")
        
        # 안전 메커니즘
        self.circuit_breaker = CircuitBreaker(
            name="NewBuildOrchestrator",
            config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                half_open_max_calls=2
            )
        )
        
        self.resource_limiter = ResourceLimiter(
            limits=ResourceLimit(
                max_memory_mb=2000,
                max_cpu_percent=80,
                max_execution_time=config.max_execution_time,
                max_concurrent_tasks=10
            )
        )
    
    async def initialize(self) -> None:
        """컴포넌트 초기화"""
        logger.info("Initializing NewBuild Orchestrator...")
        
        # Memory Hub 초기화
        self.memory_hub = MemoryHub()
        await self.memory_hub.initialize()
        
        # SharedDocumentContext 초기화
        from backend.packages.memory.document_context import SharedDocumentContext
        self.document_context = SharedDocumentContext()
        logger.info("SharedDocumentContext initialized for document sharing")
        
        # 에이전트 초기화 (document_context 전달)
        self.requirement_analyzer = RequirementAnalyzer(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.external_researcher = ExternalResearcher(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.system_architect = SystemArchitect(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.orchestrator_designer = OrchestratorDesigner(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.planner_agent = PlannerAgent(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.task_creator_agent = TaskCreatorAgent(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.code_generator = CodeGenerator(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.quality_gate = QualityGate(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        
        # Evolution Loop 에이전트 초기화
        self.gap_analyzer = GapAnalyzer(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.static_analyzer = StaticAnalyzer(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.code_analyzer = CodeAnalysisAgent(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.behavior_analyzer = BehaviorAnalyzer(
            memory_hub=self.memory_hub,
            document_context=self.document_context
        )
        self.impact_analyzer = ImpactAnalyzer(
            memory_hub=self.memory_hub,
            static_analyzer=self.static_analyzer,
            document_context=self.document_context
        )
        
        # Agno 초기화 (자동 에이전트 생성용)
        if self.config.auto_generate_all:
            logger.info("Initializing Agno for auto-generation...")
            from backend.packages.agents.registry import AgentRegistry
            
            registry = AgentRegistry()
            self.agno_manager = AgnoManager(
                memory_hub=self.memory_hub,
                registry=registry
            )
            self.agno_code_generator = AgnoCodeGenerator(
                memory_hub=self.memory_hub
            )
        
        logger.info("NewBuild Orchestrator initialized successfully")
    
    async def build(self, requirements: str) -> NewBuildReport:
        """새 프로젝트 빌드 실행 (Evolution Loop 지원)
        
        첫 번째 루프에서는 현재상태 분석 없이 프로젝트를 생성하고,
        두 번째 루프부터는 UpgradeOrchestrator와 동일한 프로세스로 개선합니다.
        
        Args:
            requirements: 자연어 프로젝트 요구사항
            
        Returns:
            NewBuildReport: 빌드 보고서
        """
        logger.info(f"🚀 Starting new project build: {self.config.project_name}")
        logger.info(f"Evolution Loop enabled: {self.config.enable_evolution_loop}")
        start_time = datetime.now()
        
        # 보고서 초기화
        report = NewBuildReport(
            timestamp=start_time.isoformat(),
            project_name=self.config.project_name,
            output_path=str(Path(self.config.output_dir) / self.config.project_name)
        )
        
        # Evolution Loop 설정
        evolution_iteration = 0
        max_iterations = self.config.max_evolution_iterations if self.config.enable_evolution_loop else 1
        project_structure = None  # 첫 번째 루프에서 생성될 프로젝트 구조
        
        try:
            # 요구사항 분석은 한 번만 수행
            logger.info("📋 Phase 1: Analyzing requirements...")
            requirement_result = await self._analyze_requirements(requirements)
            report.requirement_analysis = requirement_result
            
            # Evolution Loop 시작
            while evolution_iteration < max_iterations:
                evolution_iteration += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 Evolution Loop Iteration {evolution_iteration}/{max_iterations}")
                logger.info(f"{'='*80}\n")
                
                # 새 루프 시작 - SharedDocumentContext 초기화
                if self.document_context:
                    self.document_context.start_new_loop()
                    # 요구사항 분석 결과를 첫 문서로 추가
                    if requirement_result:
                        self.document_context.add_document(
                            "RequirementAnalyzer",
                            requirement_result,
                            document_type="analysis"
                        )
                
                if evolution_iteration == 1:
                    # ========== 첫 번째 루프: 초기 프로젝트 생성 ==========
                    logger.info("🎯 First iteration: Creating new project from scratch")
                    
                    # Phase 2: 외부 리서치
                    logger.info("🔍 Phase 2: Researching best practices...")
                    research_result = await self._research_best_practices(requirement_result)
                    report.external_research = research_result
                    if self.document_context and research_result:
                        self.document_context.add_document(
                            "ExternalResearcher",
                            research_result,
                            document_type="research"
                        )
                    
                    # Phase 3: 갭분석 (우선순위 결정용)
                    logger.info("📊 Phase 3: Determining priorities with gap analysis...")
                    gap_result = await self._analyze_priorities(
                        requirement_result,
                        research_result
                    )
                    report.gap_analysis = gap_result
                    if self.document_context and gap_result:
                        self.document_context.add_document(
                            "GapAnalyzer",
                            gap_result,
                            document_type="analysis"
                        )
                    
                    # Phase 4: 시스템 아키텍처 설계
                    logger.info("🏗️ Phase 4: Designing system architecture...")
                    architecture = await self._design_architecture(
                        requirement_result,
                        research_result
                    )
                    report.architecture_design = architecture
                    if self.document_context and architecture:
                        self.document_context.add_document(
                            "SystemArchitect",
                            architecture,
                            document_type="design"
                        )
                    
                    # Phase 5: 구현 상세 설계
                    logger.info("📐 Phase 5: Designing implementation details...")
                    implementation_design = await self._design_implementation(
                        architecture,
                        requirement_result
                    )
                    report.orchestrator_design = implementation_design
                    if self.document_context and implementation_design:
                        self.document_context.add_document(
                            "OrchestratorDesigner",
                            implementation_design,
                            document_type="design"
                        )
                    
                    # Phase 6: 개발 계획 수립
                    logger.info("📅 Phase 6: Creating development plan...")
                    dev_plan = await self._create_development_plan(
                        architecture,
                        implementation_design
                    )
                    report.development_plan = dev_plan
                    if self.document_context and dev_plan:
                        self.document_context.add_document(
                            "PlannerAgent",
                            dev_plan,
                            document_type="plan"
                        )
                    
                    # Phase 7: 세부 태스크 생성
                    logger.info("✅ Phase 7: Creating detailed tasks...")
                    tasks = await self._create_detailed_tasks(dev_plan)
                    report.detailed_tasks = tasks
                    if self.document_context and tasks:
                        self.document_context.add_document(
                            "TaskCreatorAgent",
                            tasks,
                            document_type="tasks"
                        )
                    
                    # Phase 8: 프로젝트 구조 생성
                    logger.info("📁 Phase 8: Creating project structure...")
                    project_structure = await self._create_project_structure(
                        architecture,
                        implementation_design
                    )
                    report.project_structure = project_structure
                    
                    # Phase 9: 초기 코드 생성
                    logger.info("💻 Phase 9: Generating initial code...")
                    code_result = await self._generate_code(
                        tasks,
                        project_structure,
                        architecture
                    )
                    report.code_generated = code_result
                    report.files_created = list(code_result.get("files", {}).keys())
                    
                    # Phase 10: 테스트 생성
                    if self.config.include_tests:
                        logger.info("🧪 Phase 10: Generating tests...")
                        test_result = await self._generate_tests(
                            code_result,
                            architecture
                        )
                        report.tests_generated = test_result
                    
                else:
                    # ========== 두 번째 루프부터: UpgradeOrchestrator와 동일한 프로세스 ==========
                    logger.info(f"🔧 Iteration {evolution_iteration}: Improving existing project")
                    
                    # Phase 1: 현재 상태 분석 (병렬 실행)
                    logger.info(f"Phase 1 (Iteration {evolution_iteration}): Analyzing current state...")
                    current_state_results = await self._execute_current_state_analysis(
                        project_structure.root_dir if project_structure else report.output_path
                    )
                    report.current_state_analysis = current_state_results
                    
                    # Phase 2: 추가 외부 리서치
                    logger.info(f"Phase 2 (Iteration {evolution_iteration}): Additional research...")
                    additional_research = await self._research_improvements(
                        requirement_result,
                        current_state_results
                    )
                    
                    # Phase 3: 갭 분석
                    logger.info(f"Phase 3 (Iteration {evolution_iteration}): Analyzing gaps...")
                    gap_result = await self._execute_gap_analysis(
                        requirement_result,
                        current_state_results,
                        report.external_research
                    )
                    report.gap_analysis = gap_result
                    
                    # 갭 체크 - Evolution Loop 종료 조건
                    gaps = gap_result.get('gaps', []) if gap_result else []
                    gap_score = gap_result.get('gap_score', 0) if gap_result else 0
                    report.gaps_remaining = gaps
                    report.convergence_rate = gap_score
                    
                    # 갭이 해소되었거나 수렴 임계값에 도달한 경우
                    if not gaps or gap_score >= self.config.evolution_convergence_threshold:
                        logger.info(f"✅ All gaps resolved or convergence reached (score: {gap_score:.2%})")
                        break
                    
                    logger.info(f"📊 Remaining gaps: {len(gaps)}, Gap score: {gap_score:.2%}")
                    
                    # Phase 4: 아키텍처 진화
                    logger.info(f"Phase 4 (Iteration {evolution_iteration}): Evolving architecture...")
                    architecture = await self._evolve_architecture(
                        report.architecture_design,
                        gap_result
                    )
                    report.architecture_design = architecture
                    
                    # Phase 5: 구현 개선
                    logger.info(f"Phase 5 (Iteration {evolution_iteration}): Improving implementation...")
                    implementation_design = await self._improve_implementation(
                        architecture,
                        gap_result
                    )
                    report.orchestrator_design = implementation_design
                    
                    # Phase 6: 개선 계획
                    logger.info(f"Phase 6 (Iteration {evolution_iteration}): Creating improvement plan...")
                    improvement_plan = await self._create_improvement_plan(
                        architecture,
                        gap_result
                    )
                    report.development_plan = improvement_plan
                    
                    # Phase 7: 개선 태스크
                    logger.info(f"Phase 7 (Iteration {evolution_iteration}): Creating improvement tasks...")
                    improvement_tasks = await self._create_improvement_tasks(
                        improvement_plan
                    )
                    report.detailed_tasks.extend(improvement_tasks)
                    
                    # Phase 8: 코드 개선
                    if self.config.auto_improve_code:
                        logger.info(f"Phase 8 (Iteration {evolution_iteration}): Improving code...")
                        code_improvements = await self._improve_code(
                            improvement_tasks,
                            project_structure,
                            architecture
                        )
                        # 기존 코드에 개선사항 병합
                        report.code_generated.update(code_improvements)
                
                # Evolution Loop이 비활성화된 경우 첫 반복 후 종료
                if not self.config.enable_evolution_loop:
                    logger.info("Evolution Loop disabled, stopping after first iteration")
                    break
            
            # Evolution Loop 완료
            report.evolution_iterations = evolution_iteration
            
            if self.config.enable_evolution_loop:
                logger.info(f"\n{'='*80}")
                logger.info(f"🧬 Evolution Loop completed after {evolution_iteration} iterations")
                logger.info(f"{'='*80}\n")
            
            # 최종 문서 생성
            if self.config.include_docs:
                logger.info("📚 Final Phase: Generating documentation...")
                docs_result = await self._generate_documentation(
                    report.architecture_design,
                    report.code_generated
                )
                report.documentation_generated = docs_result
            
            # 최종 품질 검증
            logger.info("✔️ Final Phase: Quality validation...")
            quality_result = await self._validate_quality(project_structure)
            report.quality_metrics = quality_result
            
            # 보고서 완성
            report.success = True
            report.next_steps = self._generate_next_steps(report)
            report.deployment_instructions = self._generate_deployment_instructions(report)
            
            # 모든 보고서를 MD 파일로 저장
            await self._save_all_reports(report)
            
            logger.info(f"✅ Project build completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            report.success = False
            report.errors.append(str(e))
            
        finally:
            end_time = datetime.now()
            report.total_execution_time = (end_time - start_time).total_seconds()
            logger.info(f"⏱️ Total execution time: {report.total_execution_time:.2f}s")
        
        return report
    
    async def _analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """요구사항 분석"""
        task = AgentTask(
            task_id="analyze_requirements",
            intent="analyze",
            inputs={"text": requirements}
        )
        
        result = await self.requirement_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _research_best_practices(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """베스트 프랙티스 리서치"""
        # 프로젝트 타입과 기술 스택에 맞는 베스트 프랙티스 조사
        research_query = f"""
        Best practices for {self.config.project_type} project using {self.config.language}
        {f'with {self.config.framework}' if self.config.framework else ''}
        Requirements: {json.dumps(requirements, indent=2)[:500]}
        """
        
        task = AgentTask(
            task_id="research_best_practices",
            intent="research",
            inputs={
                "query": research_query,
                "sources": ["github", "documentation", "tutorials"]
            }
        )
        
        result = await self.external_researcher.execute(task)
        return result.data if result.success else {}
    
    async def _design_architecture(
        self,
        requirements: Dict[str, Any],
        research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시스템 아키텍처 설계"""
        # 새 프로젝트이므로 current_architecture는 None
        design = await self.system_architect.design_architecture(
            requirements=requirements,
            gap_report={},  # 새 프로젝트이므로 갭 없음
            current_architecture=None,
            constraints={
                "project_type": self.config.project_type,
                "language": self.config.language,
                "framework": self.config.framework,
                "best_practices": research
            }
        )
        
        return design.dict()
    
    async def _design_implementation(
        self,
        architecture: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """구현 상세 설계"""
        design_doc = await self.orchestrator_designer.design_orchestrator(
            architecture_design=architecture,
            requirements=requirements,
            constraints={
                "project_type": self.config.project_type,
                "max_files": self.config.max_files
            }
        )
        
        return design_doc.dict()
    
    async def _create_development_plan(
        self,
        architecture: Dict[str, Any],
        implementation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개발 계획 수립"""
        task = AgentTask(
            task_id="create_dev_plan",
            intent="plan",
            inputs={
                "architecture": architecture,
                "implementation": implementation,
                "project_type": self.config.project_type
            }
        )
        
        result = await self.planner_agent.execute(task)
        return result.data if result.success else {}
    
    async def _create_detailed_tasks(
        self,
        dev_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """세부 태스크 생성"""
        task = AgentTask(
            task_id="create_tasks",
            intent="create_tasks",
            inputs={
                "plan": dev_plan,
                "task_duration": "5-20 minutes"
            }
        )
        
        result = await self.task_creator_agent.execute(task)
        return result.data.get("tasks", []) if result.success else []
    
    async def _create_project_structure(
        self,
        architecture: Dict[str, Any],
        implementation: Dict[str, Any]
    ) -> ProjectStructure:
        """프로젝트 구조 생성"""
        project_root = Path(self.config.output_dir) / self.config.project_name
        
        # 기본 디렉토리 구조
        structure = ProjectStructure(
            root_dir=project_root,
            src_dir=project_root / "src",
            test_dir=project_root / "tests",
            docs_dir=project_root / "docs",
            config_dir=project_root / "config"
        )
        
        # 디렉토리 생성
        directories = [
            structure.root_dir,
            structure.src_dir,
            structure.test_dir,
            structure.docs_dir,
            structure.config_dir,
            project_root / "scripts",
            project_root / ".github" / "workflows"  # CI/CD
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            structure.directories_to_create.append(directory)
        
        # 기본 파일 목록
        structure.files_to_create = [
            {"path": project_root / "README.md", "type": "documentation"},
            {"path": project_root / ".gitignore", "type": "config"},
            {"path": project_root / "requirements.txt", "type": "config"},
            {"path": project_root / "setup.py", "type": "config"},
            {"path": project_root / "Dockerfile", "type": "config"},
            {"path": project_root / ".env.example", "type": "config"},
        ]
        
        # CI/CD 파일
        if self.config.include_ci_cd:
            structure.files_to_create.append({
                "path": project_root / ".github" / "workflows" / "ci.yml",
                "type": "ci_cd"
            })
        
        # 프로젝트 메타데이터
        structure.project_metadata = {
            "name": self.config.project_name,
            "type": self.config.project_type,
            "language": self.config.language,
            "framework": self.config.framework,
            "created_at": datetime.now().isoformat(),
            "architecture": architecture,
            "implementation": implementation
        }
        
        return structure
    
    async def _generate_code(
        self,
        tasks: List[Dict[str, Any]],
        structure: ProjectStructure,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """코드 생성"""
        code_files = {}
        
        # AI를 통한 코드 생성
        for task in tasks[:self.config.max_files]:  # 파일 수 제한
            if task.get("type") == "code_generation":
                file_path = task.get("file_path")
                if file_path:
                    # AI에게 코드 생성 요청
                    prompt = f"""
                    Generate code for: {task.get('description')}
                    File: {file_path}
                    Language: {self.config.language}
                    Framework: {self.config.framework}
                    Architecture: {json.dumps(architecture, indent=2)[:1000]}
                    
                    Generate production-ready, well-commented code following best practices.
                    """
                    
                    code = await self.ai_provider.complete(prompt)
                    code_files[file_path] = code
                    
                    # 실제 파일 생성
                    full_path = structure.root_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(code)
        
        return {
            "files": code_files,
            "total_files": len(code_files),
            "total_lines": sum(len(code.split('\n')) for code in code_files.values())
        }
    
    async def _generate_tests(
        self,
        code_result: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """테스트 코드 생성"""
        test_files = {}
        
        for file_path, code in code_result.get("files", {}).items():
            if "test" not in file_path:  # 테스트 파일이 아닌 경우만
                test_path = f"tests/test_{Path(file_path).stem}.py"
                
                # AI에게 테스트 생성 요청
                prompt = f"""
                Generate comprehensive unit tests for this code:
                
                {code[:2000]}
                
                Use pytest framework, include edge cases, and aim for 80%+ coverage.
                """
                
                test_code = await self.ai_provider.complete(prompt)
                test_files[test_path] = test_code
        
        return {
            "files": test_files,
            "total_tests": len(test_files)
        }
    
    async def _generate_documentation(
        self,
        architecture: Dict[str, Any],
        code_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """문서 생성"""
        docs = {}
        
        # README.md 생성
        readme_content = f"""# {self.config.project_name}

## Overview
{architecture.get('rationale', 'Project description')}

## Architecture
{json.dumps(architecture.get('agents', []), indent=2)}

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
# Example usage
```

## Development
- Language: {self.config.language}
- Framework: {self.config.framework or 'None'}
- Project Type: {self.config.project_type}

## Testing
```bash
pytest tests/
```

## License
MIT

---
Generated by T-Developer NewBuildOrchestrator
"""
        
        docs["README.md"] = readme_content
        
        # API 문서 생성 (API 프로젝트인 경우)
        if self.config.project_type == "api":
            docs["API.md"] = "# API Documentation\n\n[Generated API docs]"
        
        return docs
    
    async def _validate_quality(
        self,
        structure: ProjectStructure
    ) -> Dict[str, Any]:
        """품질 검증"""
        # 간단한 품질 체크 (실제로는 QualityGate 에이전트 사용)
        return {
            "files_created": len(structure.files_to_create),
            "directories_created": len(structure.directories_to_create),
            "test_coverage": 0.0,  # 실제 테스트 실행 후 업데이트
            "code_complexity": 5.0,  # 기본값
            "quality_score": 85.0
        }
    
    def _generate_next_steps(self, report: NewBuildReport) -> List[str]:
        """다음 단계 생성"""
        steps = []
        
        if report.success:
            steps.append(f"Navigate to project: cd {report.output_path}")
            steps.append("Install dependencies: pip install -r requirements.txt")
            
            if self.config.include_tests:
                steps.append("Run tests: pytest tests/")
            
            if self.config.project_type == "web":
                steps.append("Start development server: python app.py")
            elif self.config.project_type == "api":
                steps.append("Start API server: uvicorn main:app --reload")
            
            if self.config.include_docker:
                steps.append("Build Docker image: docker build -t {project_name} .")
                steps.append("Run with Docker: docker run -p 8000:8000 {project_name}")
        else:
            steps.append("Review errors and retry with adjusted requirements")
        
        return steps
    
    def _generate_deployment_instructions(self, report: NewBuildReport) -> str:
        """배포 지침 생성"""
        if not report.success:
            return "Project build failed. Fix errors before deployment."
        
        instructions = f"""
# Deployment Instructions for {self.config.project_name}

## Local Development
1. cd {report.output_path}
2. pip install -r requirements.txt
3. python app.py

## Docker Deployment
1. docker build -t {self.config.project_name} .
2. docker run -d -p 8000:8000 {self.config.project_name}

## Cloud Deployment
### AWS
- Use Elastic Beanstalk or ECS
- Configure environment variables
- Set up RDS for database

### Heroku
- heroku create {self.config.project_name}
- git push heroku main
- heroku config:set ENV_VAR=value

## CI/CD Pipeline
GitHub Actions workflow is configured in .github/workflows/ci.yml
"""
        
        return instructions
    
    # ========== Evolution Loop를 위한 추가 메서드들 ==========
    
    async def _analyze_priorities(
        self,
        requirements: Dict[str, Any],
        research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """첫 번째 루프에서 갭분석을 통한 우선순위 결정"""
        # 목표 상태 정의 및 우선순위 결정
        task = AgentTask(
            task_id="analyze_priorities",
            intent="prioritize",
            inputs={
                "requirements": requirements,
                "research": research,
                "mode": "new_project"
            }
        )
        
        result = await self.gap_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _execute_current_state_analysis(
        self,
        project_path: Any
    ) -> Dict[str, Any]:
        """현재 상태 분석 (병렬 실행)"""
        from pathlib import Path
        project_path = Path(project_path) if not isinstance(project_path, Path) else project_path
        
        # 병렬로 실행할 분석 태스크들
        tasks = []
        
        # StaticAnalyzer
        static_task = AgentTask(
            task_id="static_analysis",
            intent="analyze",
            inputs={"path": str(project_path), "recursive": True}
        )
        tasks.append(('static', self.static_analyzer.execute(static_task)))
        
        # CodeAnalysisAgent
        code_task = AgentTask(
            task_id="code_analysis",
            intent="analyze",
            inputs={
                "file_path": str(project_path),
                "analysis_type": "general",
                "safe_mode": True
            }
        )
        tasks.append(('code', self.code_analyzer.execute(code_task)))
        
        # QualityGate
        quality_task = AgentTask(
            task_id="quality_check",
            intent="check",
            inputs={"project_path": str(project_path)}
        )
        tasks.append(('quality', self.quality_gate.execute(quality_task)))
        
        # 병렬 실행
        results = {}
        for name, task_coro in tasks:
            try:
                result = await task_coro
                results[name] = result.data if result.success else {}
            except Exception as e:
                logger.error(f"Error in {name} analysis: {e}")
                results[name] = {}
        
        return results
    
    async def _research_improvements(
        self,
        requirements: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개선을 위한 추가 리서치"""
        research_query = f"""
        Based on current state analysis, research improvements for:
        Requirements: {json.dumps(requirements, indent=2)[:500]}
        Current Issues: {json.dumps(current_state.get('quality', {}), indent=2)[:500]}
        """
        
        task = AgentTask(
            task_id="research_improvements",
            intent="research",
            inputs={"query": research_query}
        )
        
        result = await self.external_researcher.execute(task)
        return result.data if result.success else {}
    
    async def _execute_gap_analysis(
        self,
        requirements: Dict[str, Any],
        current_state: Dict[str, Any],
        research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """갭 분석 실행"""
        task = AgentTask(
            task_id="gap_analysis",
            intent="analyze_gaps",
            inputs={
                "requirements": requirements,
                "current_state": current_state,
                "research": research
            }
        )
        
        result = await self.gap_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _evolve_architecture(
        self,
        current_architecture: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """아키텍처 진화"""
        evolved = await self.system_architect.evolve_architecture(
            current_architecture=current_architecture,
            new_requirements=gap_analysis.get("improvement_requirements", {}),
            performance_metrics=gap_analysis.get("performance_metrics", {})
        )
        return evolved.dict()
    
    async def _improve_implementation(
        self,
        architecture: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """구현 개선"""
        # 기존 구현 설계를 개선
        design_doc = await self.orchestrator_designer.design_orchestrator(
            architecture_design=architecture,
            requirements=gap_analysis.get("improvement_requirements", {}),
            constraints={"mode": "improvement"}
        )
        return design_doc.dict()
    
    async def _create_improvement_plan(
        self,
        architecture: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개선 계획 수립"""
        task = AgentTask(
            task_id="improvement_plan",
            intent="plan",
            inputs={
                "architecture": architecture,
                "gaps": gap_analysis.get("gaps", []),
                "mode": "improvement"
            }
        )
        
        result = await self.planner_agent.execute(task)
        return result.data if result.success else {}
    
    async def _create_improvement_tasks(
        self,
        improvement_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """개선 태스크 생성"""
        task = AgentTask(
            task_id="improvement_tasks",
            intent="create_tasks",
            inputs={
                "plan": improvement_plan,
                "task_duration": "5-20 minutes",
                "mode": "improvement"
            }
        )
        
        result = await self.task_creator_agent.execute(task)
        return result.data.get("tasks", []) if result.success else []
    
    async def _improve_code(
        self,
        tasks: List[Dict[str, Any]],
        structure: ProjectStructure,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """코드 개선"""
        improvements = {}
        
        for task in tasks[:10]:  # 제한된 수의 개선만 수행
            if task.get("type") == "code_improvement":
                file_path = task.get("file_path")
                if file_path:
                    # 기존 코드 읽기
                    full_path = structure.root_dir / file_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8') as f:
                            existing_code = f.read()
                        
                        # AI를 통한 코드 개선
                        prompt = f"""
                        Improve this code based on the task:
                        Task: {task.get('description')}
                        Current Code:
                        {existing_code[:2000]}
                        
                        Generate improved code with better performance, readability, and maintainability.
                        """
                        
                        improved_code = await self.ai_provider.complete(prompt)
                        improvements[file_path] = improved_code
                        
                        # 파일 업데이트
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(improved_code)
        
        return {
            "improved_files": list(improvements.keys()),
            "total_improvements": len(improvements)
        }
    
    async def _save_all_reports(self, report: NewBuildReport) -> None:
        """모든 보고서를 MD 파일로 저장"""
        output_dir = Path(report.output_path) / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 메인 보고서
        main_report_path = output_dir / "build_report.md"
        with open(main_report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Build Report for {report.project_name}\n\n")
            f.write(f"- **Timestamp**: {report.timestamp}\n")
            f.write(f"- **Success**: {report.success}\n")
            f.write(f"- **Execution Time**: {report.total_execution_time:.2f}s\n")
            f.write(f"- **Files Created**: {len(report.files_created)}\n\n")
            
            if report.next_steps:
                f.write("## Next Steps\n")
                for step in report.next_steps:
                    f.write(f"- {step}\n")
                f.write("\n")
            
            if report.deployment_instructions:
                f.write("## Deployment Instructions\n")
                f.write(report.deployment_instructions)
        
        logger.info(f"📝 Reports saved to {output_dir}")


async def main():
    """테스트용 메인 함수"""
    config = NewBuildConfig(
        project_name="my-awesome-api",
        project_type="api",
        language="python",
        framework="fastapi",
        include_tests=True,
        include_docs=True,
        include_docker=True
    )
    
    orchestrator = NewBuildOrchestrator(config)
    await orchestrator.initialize()
    
    requirements = """
    Create a RESTful API for a task management system with:
    - User authentication
    - CRUD operations for tasks
    - Task assignment and status tracking
    - Due date reminders
    - REST API with OpenAPI documentation
    """
    
    report = await orchestrator.build(requirements)
    
    if report.success:
        print(f"✅ Project created successfully at: {report.output_path}")
        print("\nNext steps:")
        for step in report.next_steps:
            print(f"  - {step}")
    else:
        print(f"❌ Build failed: {report.errors}")


if __name__ == "__main__":
    asyncio.run(main())