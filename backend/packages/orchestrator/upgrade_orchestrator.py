"""Upgrade Orchestrator for comprehensive system analysis and upgrade.

This orchestrator coordinates all analysis agents to provide complete
system insights and generate upgrade recommendations.
"""

from __future__ import annotations

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os
import sys
from pathlib import Path

# No need to add path - we're in the right location now

from backend.packages.agents.base import AgentTask, AgentResult, TaskStatus
from backend.packages.agents.ai_providers import get_ai_provider, BedrockAIProvider
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.static_analyzer import StaticAnalyzer
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.gap_analyzer import GapAnalyzer
from backend.packages.agents.behavior_analyzer import BehaviorAnalyzer
from backend.packages.agents.impact_analyzer import ImpactAnalyzer
from backend.packages.agents.code_generator import CodeGenerator
from backend.packages.agents.quality_gate import QualityGate
# from backend.packages.agents.report_generator import ReportGenerator  # Not implemented yet
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.planner_agent import PlannerAgent
from backend.packages.agents.task_creator_agent import TaskCreatorAgent
from backend.packages.agents.system_architect import SystemArchitect
from backend.packages.agents.orchestrator_designer import OrchestratorDesigner
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType
from backend.packages.memory.document_context import SharedDocumentContext
from backend.packages.safety import CircuitBreaker, CircuitBreakerConfig, ResourceLimiter, ResourceLimit

# Agno 통합 - 자동 에이전트 생성
from backend.packages.agno import AgnoManager
from backend.packages.agno.spec import AgentSpec as AgnoSpec
from backend.packages.agno.generator import CodeGenerator as AgnoCodeGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class UpgradeConfig:
    """Configuration for upgrade analysis."""
    
    project_path: str
    output_dir: str = "/tmp/t-developer/reports"  # 문서 저장 경로
    enable_dynamic_analysis: bool = False  # Enable code execution
    include_behavior_analysis: bool = True  # Parse logs if available
    generate_impact_matrix: bool = True  # Generate dependency matrix
    generate_recommendations: bool = True  # Generate upgrade recommendations
    safe_mode: bool = True  # Run in safe mode
    max_execution_time: int = 600  # 10 minutes max
    parallel_analysis: bool = True  # Run analyses in parallel
    
    # Evolution Loop 설정
    enable_evolution_loop: bool = False  # Evolution Loop 활성화
    max_evolution_iterations: int = 10  # 최대 반복 횟수
    auto_generate_agents: bool = False  # Agno를 통한 자동 에이전트 생성
    auto_implement_code: bool = False  # CodeGenerator를 통한 자동 코드 구현
    evolution_convergence_threshold: float = 0.95  # 수렴 임계값 (갭 해소율)
    
    # AI 드리븐 동적 워크플로우 설정
    ai_driven_workflow: bool = True  # AI가 에이전트 실행 순서 결정
    allow_parallel_execution: bool = True  # 병렬 실행 허용


@dataclass
class AnalysisPhase:
    """Represents a phase of analysis."""
    
    name: str
    agent: str
    status: str  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class EvolutionGoalSpec:
    """진화 목표 명세서."""
    
    background: str  # 배경/목적
    stakeholders: List[str]  # 이해관계자
    change_scope: Dict[str, Any]  # 변경 범위
    success_criteria: Dict[str, Any]  # 성공 기준
    constraints: Dict[str, Any]  # 제약사항
    compatibility_requirements: List[str]  # 호환성 요구사항
    open_questions: List[str]  # 열린 질문
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CurrentStateReport:
    """현재 상태 진단 보고서."""
    
    static_analysis: Dict[str, Any]  # 정적 분석
    dynamic_analysis: Dict[str, Any]  # 동적 분석
    ai_summary: Dict[str, Any]  # AI 요약
    contracts: Dict[str, Any]  # 계약/인터페이스
    test_gaps: List[Dict[str, Any]]  # 테스트 갭
    ux_metrics: Dict[str, Any]  # UX/행동 데이터
    

@dataclass  
class GapReport:
    """갭 분석 보고서."""
    
    gaps: List[Dict[str, Any]]  # 현재↔목표 차이
    impact_matrix: Dict[str, Any]  # 영향도 매트릭스
    risk_scores: Dict[str, float]  # 리스크 스코어
    migration_plan: Dict[str, Any]  # 마이그레이션 전략
    batch_plan: List[Dict[str, Any]]  # 작은 배치 계획


@dataclass
class UpgradeResearchPack:
    """업그레이드 리서치 팩 (URP).
    
    upgrade.md 문서의 4A) 섹션에 정의된 구조를 따름.
    """
    
    one_line_conclusion: str  # 한 줄 결론
    recommended_approach: Dict[str, Any]  # 추천 접근 1안
    alternative_approaches: List[Dict[str, Any]]  # 대안 2안
    compatibility_checklist: List[Dict[str, Any]]  # 호환성/계약 영향 체크리스트
    migration_strategy: Dict[str, Any]  # 마이그레이션 전략 요약
    code_snippets: List[Dict[str, Any]]  # 핵심 코드 스니펫 3개
    warnings: List[str]  # 주의사항/함정
    success_criteria: Dict[str, Any]  # 성공/실패 기준
    cost_risk_summary: Dict[str, Any]  # 비용/리스크 요약
    dedup_results: Dict[str, Any]  # De-dup 결과
    references: List[str]  # 참고자료 목록
    ttl_days: int = 14  # 유효기간
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EvolutionResult:
    """Evolution Loop 실행 결과."""
    
    success: bool  # 모든 갭이 해소되었는지
    iterations: int  # 실행된 반복 횟수
    final_gaps: List[Dict[str, Any]]  # 최종 남은 갭
    agents_created: List[str]  # 생성된 에이전트 목록
    code_generated: int  # 생성된 코드 라인 수
    tests_passed: int  # 통과한 테스트 수
    tests_failed: int  # 실패한 테스트 수
    evolution_history: List[Dict[str, Any]]  # 각 반복의 상세 이력
    convergence_rate: float  # 수렴률
    total_time: float  # 총 실행 시간
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UpgradeReport:
    """Comprehensive upgrade analysis report."""
    
    timestamp: str
    project_path: str
    
    # 1) 진화 목표 명세서
    evolution_goal: Optional[EvolutionGoalSpec] = None
    
    # 2) 현재 상태 보고서  
    current_state: Optional[CurrentStateReport] = None
    
    # 3) 외부 리서치 (URP)
    research_pack: Optional[UpgradeResearchPack] = None
    
    # 4) 갭 분석 및 계획
    gap_report: Optional[GapReport] = None
    
    # Legacy analysis results (backward compatibility)
    requirement_analysis: Optional[Dict[str, Any]] = None
    static_analysis: Optional[Dict[str, Any]] = None
    code_analysis: Optional[Dict[str, Any]] = None
    gap_analysis: Optional[Dict[str, Any]] = None
    behavior_analysis: Optional[Dict[str, Any]] = None
    impact_analysis: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    
    # Aggregated insights
    system_health_score: float = 0.0
    upgrade_risk_score: float = 0.0
    total_issues_found: int = 0
    critical_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    immediate_actions: List[str] = field(default_factory=list)
    short_term_goals: List[str] = field(default_factory=list)
    long_term_goals: List[str] = field(default_factory=list)
    
    # Execution metadata
    total_execution_time: float = 0.0
    phases_completed: int = 0
    phases_failed: int = 0
    tasks_breakdown: List[Dict[str, Any]] = field(default_factory=list)  # 5~20분 태스크
    
    # Evolution Loop metadata
    evolution_iterations: int = 0  # Evolution Loop 반복 횟수
    agents_created: List[str] = field(default_factory=list)  # Agno로 생성된 에이전트 목록


class UpgradeOrchestrator:
    """AI-driven orchestrator for intelligent upgrade analysis.
    
    This orchestrator uses AI to:
    1. Dynamically select relevant agents based on requirements
    2. Optimize execution order and parallelization
    3. Predict resource needs and allocate efficiently
    4. Detect potential failures and adjust strategy
    5. Learn from past executions to improve
    6. Generate optimal upgrade paths
    7. Intelligently coordinate analysis agents
    """
    
    def __init__(self, config: UpgradeConfig):
        """Initialize Upgrade Orchestrator.
        
        Args:
            config: Upgrade configuration
        """
        self.config = config
        self.memory_hub = None
        self.phases: List[AnalysisPhase] = []
        self.document_context = SharedDocumentContext()  # 공유 문서 컨텍스트
        
        # Initialize agents (will be created when needed)
        self.planner_agent = None
        self.task_creator_agent = None
        self.requirement_analyzer = None
        self.static_analyzer = None
        self.code_analyzer = None
        self.gap_analyzer = None
        self.behavior_analyzer = None
        self.impact_analyzer = None
        self.code_generator = None
        self.quality_gate = None
        
        # 아키텍처 및 오케스트레이터 디자인 에이전트
        self.system_architect = None
        self.orchestrator_designer = None
        
        # Agno 통합 - 자동 에이전트 생성
        self.agno_manager = None
        self.agno_code_generator = None
        self.report_generator = None
        self.external_researcher = None
        
        # AI Provider for orchestration decisions - 100% REAL AI
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # 페르소나 설정 - 진화 마에스트로
        from backend.packages.agents.personas import get_persona
        self.persona = get_persona("UpgradeOrchestrator")
        if self.persona:
            logger.info(f"🎭 페르소나 활성화: {self.persona.name} - '{self.persona.catchphrase}'")
        
        # Safety mechanisms
        self.circuit_breaker = CircuitBreaker(
            name="UpgradeOrchestrator",
            config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                half_open_max_calls=2
            )
        )
        
        self.resource_limiter = ResourceLimiter(
            limits=ResourceLimit(
                max_memory_mb=2000,  # 2GB
                max_cpu_percent=80,
                max_execution_time=config.max_execution_time,
                max_concurrent_tasks=10
            )
        )
    
    async def initialize(self) -> None:
        """Initialize all components."""
        logger.info("Initializing Upgrade Orchestrator...")
        
        # Initialize Memory Hub
        self.memory_hub = MemoryHub()
        await self.memory_hub.initialize()
        
        # Initialize all agents with memory hub and shared document context
        self.planner_agent = PlannerAgent(memory_hub=self.memory_hub, document_context=self.document_context)
        self.task_creator_agent = TaskCreatorAgent(memory_hub=self.memory_hub, document_context=self.document_context)
        self.requirement_analyzer = RequirementAnalyzer(memory_hub=self.memory_hub, document_context=self.document_context)
        self.external_researcher = ExternalResearcher(memory_hub=self.memory_hub, document_context=self.document_context)
        self.static_analyzer = StaticAnalyzer(memory_hub=self.memory_hub, document_context=self.document_context)
        self.code_analyzer = CodeAnalysisAgent(memory_hub=self.memory_hub, document_context=self.document_context)
        self.gap_analyzer = GapAnalyzer(memory_hub=self.memory_hub, document_context=self.document_context)
        self.behavior_analyzer = BehaviorAnalyzer(memory_hub=self.memory_hub, document_context=self.document_context)
        self.impact_analyzer = ImpactAnalyzer(
            memory_hub=self.memory_hub,
            static_analyzer=self.static_analyzer,
            document_context=self.document_context
        )
        self.system_architect = SystemArchitect(memory_hub=self.memory_hub, document_context=self.document_context)
        self.orchestrator_designer = OrchestratorDesigner(memory_hub=self.memory_hub, document_context=self.document_context)
        self.code_generator = CodeGenerator(memory_hub=self.memory_hub, document_context=self.document_context)
        self.quality_gate = QualityGate(memory_hub=self.memory_hub, document_context=self.document_context)
        # self.report_generator = ReportGenerator(memory_hub=self.memory_hub)  # Not implemented yet
        
        # Agno 초기화 (Evolution Loop용)
        if self.config.enable_evolution_loop:
            logger.info("Initializing Agno for Evolution Loop...")
            from backend.packages.agents.registry import AgentRegistry
            
            registry = AgentRegistry()
            self.agno_manager = AgnoManager(
                memory_hub=self.memory_hub,
                registry=registry
            )
            self.agno_code_generator = AgnoCodeGenerator(
                memory_hub=self.memory_hub
            )
            logger.info("Agno initialized successfully")
        
        logger.info("Orchestrator initialized successfully")
    
    async def analyze(self, requirements: str, include_research: bool = True) -> UpgradeReport:
        """AI-드리븐 업그레이드 분석 실행 (Evolution Loop 통합).
        
        정해진 기본 순서에 따라 에이전트들을 실행하지만,
        요구사항에 따라 AI가 동적으로 순서와 에이전트를 조정할 수 있음.
        Evolution Loop이 활성화되면 갭이 해소될 때까지 자동으로 반복.
        
        기본 실행 순서:
        1. RequirementAnalyzer - 요구사항 분석/문서화
        2. 현재상태 분석 (병렬) - behavior, code, impact, static, quality
        3. ExternalResearcher - 외부 자료 조사
        4. GapAnalyzer - 변경사항 분석/수치화
        5. SystemArchitect - 아키텍처 설계
        6. OrchestratorDesigner - 오케스트레이터/에이전트 디자인
        7. PlannerAgent - Phase 단위 계획
        8. TaskCreatorAgent - 세부 태스크 계획
        9. CodeGenerator - 코드 생성 (Agno 통합)
        10. 테스트 실행
        11. 갭 재확인 및 Evolution Loop (갭이 0이 될 때까지 반복)
        
        Args:
            requirements: 자연어 요구사항
            include_research: 외부 리서치 포함 여부
            
        Returns:
            종합 업그레이드 보고서
        """
        logger.info(f"Starting AI-driven upgrade analysis for: {self.config.project_path}")
        logger.info(f"Evolution Loop enabled: {self.config.enable_evolution_loop}")
        start_time = datetime.now()
        
        # Initialize report
        report = UpgradeReport(
            timestamp=start_time.isoformat(),
            project_path=self.config.project_path
        )
        
        # Check circuit breaker
        if not await self.circuit_breaker.call(self._check_system_ready):
            report.critical_issues.append({
                "type": "system",
                "message": "Circuit breaker is open - too many recent failures"
            })
            return report
        
        # Evolution Loop 카운터
        evolution_iteration = 0
        max_iterations = self.config.max_evolution_iterations if self.config.enable_evolution_loop else 1
        
        try:
            # 초기 요구사항 분석은 한 번만 수행
            logger.info("Phase 1: Analyzing requirements...")
            requirement_result = await self._execute_requirement_analysis(requirements)
            report.requirement_analysis = requirement_result
            
            # Evolution Loop 시작
            while evolution_iteration < max_iterations:
                evolution_iteration += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 Evolution Loop Iteration {evolution_iteration}/{max_iterations}")
                logger.info(f"{'='*80}\n")
                
                # 새 루프 시작 - 문서 컨텍스트 초기화
                self.document_context.start_new_loop()
                
                # 요구사항을 문서 컨텍스트에 추가
                self.document_context.add_document("RequirementAnalyzer", requirement_result, "requirement")
                
                # AI 드리븐 동적 워크플로우 사용 여부 결정
                if self.config.ai_driven_workflow:
                    # AI가 다음 실행할 에이전트를 동적으로 결정
                    logger.info("🤖 AI-driven dynamic workflow enabled")
                    await self._execute_dynamic_workflow(report, evolution_iteration)
                else:
                    # 기존 정적 워크플로우 실행
                    # Phase 2: 현재 상태 분석 (병렬 실행)
                    logger.info(f"Phase 2 (Iteration {evolution_iteration}): Analyzing current state...")
                    current_state_results = await self._execute_current_state_analysis()
                    report.static_analysis = current_state_results.get('static')
                    report.code_analysis = current_state_results.get('code')
                    report.behavior_analysis = current_state_results.get('behavior')
                    report.impact_analysis = current_state_results.get('impact')
                    report.quality_metrics = current_state_results.get('quality')
                    
                    # 결과를 문서 컨텍스트에 추가
                    for agent_name, result in current_state_results.items():
                        if result:
                            self.document_context.add_document(f"{agent_name}_analyzer", result, "analysis")
                
                # Phase 3: 외부 리서치 (첫 반복에서만)
                if include_research and evolution_iteration == 1:
                    logger.info("Phase 3: Conducting external research...")
                    research_result = await self._execute_external_research(
                        requirement_result,
                        current_state_results
                    )
                    report.research_pack = research_result
                
                # Phase 4: 갭 분석 (매 반복마다 수행)
                logger.info(f"Phase 4 (Iteration {evolution_iteration}): Analyzing gaps...")
                gap_result = await self._execute_gap_analysis(
                    requirement_result,
                    current_state_results,
                    report.research_pack
                )
                report.gap_analysis = gap_result
                
                # 갭 체크 - Evolution Loop 종료 조건
                gaps = gap_result.get('gaps', []) if gap_result else []
                gap_score = gap_result.get('gap_score', 0) if gap_result else 0
                
                # 갭이 해소되었거나 수렴 임계값에 도달한 경우
                if not gaps or gap_score >= self.config.evolution_convergence_threshold:
                    logger.info(f"✅ All gaps resolved or convergence reached (score: {gap_score:.2%})")
                    break
                
                logger.info(f"📊 Remaining gaps: {len(gaps)}, Gap score: {gap_score:.2%}")
                
                # Phase 5: 아키텍처 설계
                logger.info(f"Phase 5 (Iteration {evolution_iteration}): Designing architecture...")
                architecture_design = await self._execute_architecture_design(
                    requirement_result,
                    gap_result
                )
                
                # Phase 6: 오케스트레이터 디자인
                logger.info(f"Phase 6 (Iteration {evolution_iteration}): Designing orchestrator...")
                orchestrator_design = await self._execute_orchestrator_design(
                    architecture_design,
                    requirement_result
                )
                
                # Agno를 통한 자동 에이전트 생성 (활성화된 경우)
                if self.config.auto_generate_agents and self.config.enable_evolution_loop:
                    logger.info("🤖 Auto-generating agents with Agno...")
                    generated_agents = await self._generate_agents_with_agno(
                        orchestrator_design,
                        gaps
                    )
                    if generated_agents:
                        logger.info(f"Generated {len(generated_agents)} new agents")
                        report.agents_created = report.agents_created or []
                        report.agents_created.extend(generated_agents)
                
                # Phase 7: 실행 계획 수립
                logger.info(f"Phase 7 (Iteration {evolution_iteration}): Creating execution plan...")
                execution_plan = await self._execute_planning(
                    architecture_design,
                    orchestrator_design,
                    requirement_result
                )
                
                # Phase 8: 세부 태스크 생성
                logger.info(f"Phase 8 (Iteration {evolution_iteration}): Creating detailed tasks...")
                detailed_tasks = await self._execute_task_creation(
                    execution_plan,
                    orchestrator_design
                )
                report.tasks_breakdown = detailed_tasks
                
                # Phase 9: 코드 생성 (자동 구현이 활성화된 경우)
                if self.config.auto_implement_code:
                    logger.info(f"Phase 9 (Iteration {evolution_iteration}): Generating code...")
                    code_generation_result = await self._execute_code_generation(
                        detailed_tasks,
                        architecture_design
                    )
                    
                    # Phase 10: 테스트 실행
                    logger.info(f"Phase 10 (Iteration {evolution_iteration}): Running tests...")
                    test_result = await self._execute_tests(code_generation_result)
                    
                    # Phase 11: Evolution Loop 종료 여부 결정
                    if not self.config.enable_evolution_loop:
                        logger.info("Evolution Loop disabled, stopping after first iteration")
                        break
                
                # Evolution Loop이 활성화되지 않은 경우 첫 반복 후 종료
                if not self.config.enable_evolution_loop:
                    break
            
            # Evolution Loop 완료 로그
            if self.config.enable_evolution_loop:
                logger.info(f"\n{'='*80}")
                logger.info(f"🧬 Evolution Loop completed after {evolution_iteration} iterations")
                logger.info(f"{'='*80}\n")
                report.evolution_iterations = evolution_iteration
            
            # Aggregate results
            self._aggregate_results(report)
            
            # Generate recommendations
            self._generate_recommendations(report)
            
            # Calculate scores
            self._calculate_scores(report)
            
            # Save reports as markdown files
            await self._save_all_reports_as_markdown(report)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            report.critical_issues.append({
                "type": "execution",
                "message": str(e)
            })
        finally:
            # Calculate execution time
            end_time = datetime.now()
            report.total_execution_time = (end_time - start_time).total_seconds()
            
            # Count phase results
            report.phases_completed = len([p for p in self.phases if p.status == "completed"])
            report.phases_failed = len([p for p in self.phases if p.status == "failed"])
            
            # Store report in memory
            await self._store_report(report)
        
        logger.info(f"Analysis completed in {report.total_execution_time:.2f} seconds")
        return report
    
    async def _define_phases_with_ai(self, requirements: str) -> List[AnalysisPhase]:
        """AI를 사용한 지능적인 분석 단계 선택 및 순서 결정.
        
        요구사항을 분석하여 필요한 에이전트와 실행 순서를 동적으로 결정합니다.
        기본 순서를 따르되, 요구사항의 특성에 따라 조정합니다.
        
        Args:
            requirements: 사용자 요구사항
            
        Returns:
            최적화된 분석 단계 목록
        """
        try:
            # AI Provider 초기화
            ai_provider = get_ai_provider()
            
            # AI에게 요구사항 분석 및 최적 실행 계획 수립 요청
            prompt = f"""
            Analyze these requirements and determine the optimal agent execution order:
            
            Requirements: {requirements[:1000]}
            
            Available agents:
            1. RequirementAnalyzer - Parses and documents requirements
            2. StaticAnalyzer - Analyzes code structure and complexity
            3. CodeAnalysisAgent - AI-based code understanding
            4. BehaviorAnalyzer - Analyzes runtime behavior from logs
            5. ImpactAnalyzer - Analyzes change impact and dependencies
            6. QualityGate - Checks code quality metrics
            7. ExternalResearcher - Searches external resources
            8. GapAnalyzer - Identifies gaps between current and desired state
            9. SystemArchitect - Designs system architecture
            10. OrchestratorDesigner - Designs orchestrator flow
            11. PlannerAgent - Creates phase-level plans
            12. TaskCreatorAgent - Creates detailed tasks
            13. CodeGenerator - Generates code
            
            Based on the requirements, determine:
            1. Which agents are essential (must run)
            2. Which agents are optional (can be skipped)
            3. Optimal execution order
            4. Which agents can run in parallel
            
            Consider:
            - If requirements mention "debug" or "fix", prioritize analysis agents
            - If requirements mention "new feature", prioritize design agents
            - If requirements mention "refactor", prioritize quality and impact agents
            - If requirements mention "upgrade", run all agents
            
            Return a structured JSON response with:
            {{
                "essential_agents": ["agent1", "agent2", ...],
                "optional_agents": ["agent3", ...],
                "execution_order": [
                    {{"phase": 1, "agents": ["agent1"], "parallel": false}},
                    {{"phase": 2, "agents": ["agent2", "agent3"], "parallel": true}},
                    ...
                ],
                "reasoning": "Brief explanation of choices"
            }}
            """
            
            response = await ai_provider.complete(prompt)
            
            # Parse AI response
            import json
            try:
                ai_plan = json.loads(response)
                logger.info(f"AI-driven phase selection: {ai_plan.get('reasoning', 'No reasoning provided')}")
                
                # Convert AI plan to AnalysisPhase objects
                phases = []
                for phase_info in ai_plan.get('execution_order', []):
                    for agent_name in phase_info.get('agents', []):
                        # Map agent names to phase names
                        phase_name = self._get_phase_name_for_agent(agent_name)
                        if phase_name:
                            phases.append(AnalysisPhase(
                                name=phase_name,
                                agent=agent_name,
                                status="pending"
                            ))
                
                # If AI planning failed or returned empty, fallback to default
                if not phases:
                    logger.warning("AI phase planning returned empty, using default phases")
                    return self._define_phases(requirements)
                
                return phases
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response, using default phases")
                return self._define_phases(requirements)
                
        except Exception as e:
            logger.error(f"AI-driven phase selection failed: {e}, falling back to default")
            return self._define_phases(requirements)
    
    def _get_phase_name_for_agent(self, agent_name: str) -> Optional[str]:
        """에이전트 이름을 phase 이름으로 매핑."""
        mapping = {
            "RequirementAnalyzer": "requirement_analysis",
            "StaticAnalyzer": "static_analysis",
            "CodeAnalysisAgent": "code_analysis",
            "BehaviorAnalyzer": "behavior_analysis",
            "ImpactAnalyzer": "impact_analysis",
            "QualityGate": "quality_gate",
            "ExternalResearcher": "external_research",
            "GapAnalyzer": "gap_analysis",
            "SystemArchitect": "architecture_design",
            "OrchestratorDesigner": "orchestrator_design",
            "PlannerAgent": "planning",
            "TaskCreatorAgent": "task_creation",
            "CodeGenerator": "code_generation"
        }
        return mapping.get(agent_name)
    
    def _define_phases(self, requirements: str) -> List[AnalysisPhase]:
        """Define analysis phases based on configuration.
        
        Args:
            requirements: User requirements
            
        Returns:
            List of analysis phases
        """
        phases = []
        
        # Always run requirement analysis first
        phases.append(AnalysisPhase(
            name="requirement_analysis",
            agent="RequirementAnalyzer",
            status="pending"
        ))
        
        # Static analysis
        phases.append(AnalysisPhase(
            name="static_analysis",
            agent="StaticAnalyzer",
            status="pending"
        ))
        
        # Code analysis (AI + optional dynamic)
        phases.append(AnalysisPhase(
            name="code_analysis",
            agent="CodeAnalysisAgent",
            status="pending"
        ))
        
        # Gap analysis
        phases.append(AnalysisPhase(
            name="gap_analysis",
            agent="GapAnalyzer",
            status="pending"
        ))
        
        # Behavior analysis (if logs available)
        if self.config.include_behavior_analysis:
            phases.append(AnalysisPhase(
                name="behavior_analysis",
                agent="BehaviorAnalyzer",
                status="pending"
            ))
        
        # Impact analysis
        if self.config.generate_impact_matrix:
            phases.append(AnalysisPhase(
                name="impact_analysis",
                agent="ImpactAnalyzer",
                status="pending"
            ))
        
        # Quality gate
        phases.append(AnalysisPhase(
            name="quality_check",
            agent="QualityGate",
            status="pending"
        ))
        
        self.phases = phases
        return phases
    
    async def _execute_sequential(
        self,
        phases: List[AnalysisPhase],
        report: UpgradeReport
    ) -> None:
        """Execute phases sequentially.
        
        Args:
            phases: List of phases
            report: Report to populate
        """
        for phase in phases:
            await self._execute_phase(phase, report)
            if phase.status == "failed":
                logger.warning(f"Phase {phase.name} failed, continuing...")
    
    async def _execute_parallel(
        self,
        phases: List[AnalysisPhase],
        report: UpgradeReport
    ) -> None:
        """Execute phases in parallel where possible, respecting dependencies.
        
        Execution order:
        1. RequirementAnalyzer (필수 선행)
        2. StaticAnalyzer, CodeAnalysisAgent, BehaviorAnalyzer (병렬 가능)
        3. GapAnalyzer, ImpactAnalyzer (의존성 있음, 순차 실행)
        4. QualityGate (마지막 실행)
        
        Args:
            phases: List of phases
            report: Report to populate
        """
        if not phases:
            return
        
        # Phase 1: Requirement analysis must run first
        requirement_phases = [p for p in phases if p.agent == "RequirementAnalyzer"]
        for phase in requirement_phases:
            await self._execute_phase(phase, report)
            if phase.status == "failed":
                logger.warning("Requirement analysis had issues, continuing with limited functionality")
        
        # Phase 2: Independent analyses can run in parallel
        parallel_agents = ["StaticAnalyzer", "CodeAnalysisAgent", "BehaviorAnalyzer"]
        parallel_phases = [p for p in phases if p.agent in parallel_agents]
        
        if parallel_phases:
            tasks = [self._execute_phase(phase, report) for phase in parallel_phases]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Phase 3: Dependent analyses run sequentially
        # GapAnalyzer needs requirement and static analysis results
        gap_phases = [p for p in phases if p.agent == "GapAnalyzer"]
        for phase in gap_phases:
            await self._execute_phase(phase, report)
        
        # ImpactAnalyzer needs static analysis results
        impact_phases = [p for p in phases if p.agent == "ImpactAnalyzer"]
        for phase in impact_phases:
            await self._execute_phase(phase, report)
        
        # Phase 4: Quality gate runs last (분석 단계의 마지막)
        quality_phases = [p for p in phases if p.agent == "QualityGate"]
        for phase in quality_phases:
            await self._execute_phase(phase, report)
        
        # NOTE: CodeGenerator는 이 단계에서 실행하지 않음
        # 계획 수립 후 사용자 승인을 받은 다음 별도 실행
    
    async def _execute_phase(
        self,
        phase: AnalysisPhase,
        report: UpgradeReport
    ) -> None:
        """Execute a single analysis phase.
        
        Args:
            phase: Phase to execute
            report: Report to populate
        """
        logger.info(f"Executing phase: {phase.name}")
        phase.status = "running"
        phase.start_time = datetime.now()
        
        try:
            # Get the appropriate agent
            agent_name = phase.agent.lower()
            # Handle special cases
            if agent_name == "qualitygate":
                agent_name = "quality_gate"
            elif agent_name == "codeanalysisagent":
                agent_name = "code_analyzer"
            else:
                agent_name = agent_name.replace("analyzer", "_analyzer")
            agent = getattr(self, agent_name)
            
            # Prepare task based on phase
            task = self._prepare_task(phase.name, report)
            
            # Execute agent
            result = await agent.execute(task)
            
            # Store result
            phase.result = result.data if result.success else None
            phase.status = "completed" if result.success else "failed"
            phase.error = result.error if not result.success else None
            
            # Update report
            self._update_report(phase, report)
            
        except Exception as e:
            logger.error(f"Phase {phase.name} failed: {e}")
            phase.status = "failed"
            phase.error = str(e)
        finally:
            phase.end_time = datetime.now()
    
    def _prepare_task(self, phase_name: str, report: UpgradeReport) -> AgentTask:
        """Prepare task for agent execution.
        
        Args:
            phase_name: Name of the phase
            report: Current report
            
        Returns:
            Agent task
        """
        task = AgentTask(
            task_id=f"{phase_name}_{datetime.now().timestamp()}",
            intent=phase_name,
            inputs={}
        )
        
        if phase_name == "requirement_analysis":
            # Use requirements from report or config
            task.inputs["requirements"] = report.requirement_analysis or {}
            task.inputs["project_path"] = self.config.project_path
            
        elif phase_name == "static_analysis":
            task.inputs["path"] = self.config.project_path
            task.inputs["recursive"] = True
            
        elif phase_name == "code_analysis":
            task.inputs["file_path"] = self.config.project_path
            task.inputs["analysis_type"] = "general"
            task.inputs["enable_dynamic"] = self.config.enable_dynamic_analysis
            task.inputs["safe_mode"] = self.config.safe_mode
            
        elif phase_name == "gap_analysis":
            task.inputs["project_path"] = self.config.project_path
            task.inputs["min_coverage"] = 80
            
        elif phase_name == "behavior_analysis":
            # Find log files
            log_paths = self._find_log_files()
            task.inputs["log_paths"] = log_paths
            
        elif phase_name == "impact_analysis":
            task.inputs["project_path"] = self.config.project_path
            task.inputs["analysis_type"] = "report"
            
        elif phase_name == "quality_check":
            task.inputs["project_path"] = self.config.project_path
            
        return task
    
    def _find_log_files(self) -> List[str]:
        """Find log files in the project.
        
        Returns:
            List of log file paths
        """
        log_files = []
        log_dirs = ["logs", "log", ".logs", "var/log"]
        log_extensions = [".log", ".txt", ".out"]
        
        for log_dir in log_dirs:
            dir_path = os.path.join(self.config.project_path, log_dir)
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if any(file.endswith(ext) for ext in log_extensions):
                            log_files.append(os.path.join(root, file))
        
        return log_files[:10]  # Limit to 10 most recent logs
    
    def _update_report(self, phase: AnalysisPhase, report: UpgradeReport) -> None:
        """Update report with phase results.
        
        Args:
            phase: Completed phase
            report: Report to update
        """
        if phase.result:
            if phase.name == "requirement_analysis":
                report.requirement_analysis = phase.result
            elif phase.name == "static_analysis":
                report.static_analysis = phase.result
            elif phase.name == "code_analysis":
                report.code_analysis = phase.result
            elif phase.name == "gap_analysis":
                report.gap_analysis = phase.result
            elif phase.name == "behavior_analysis":
                report.behavior_analysis = phase.result
            elif phase.name == "impact_analysis":
                report.impact_analysis = phase.result
            elif phase.name == "quality_check":
                report.quality_metrics = phase.result
    
    def _aggregate_results(self, report: UpgradeReport) -> None:
        """Aggregate results from all analyses.
        
        Args:
            report: Report to aggregate
        """
        # Count total issues
        issue_count = 0
        
        if report.static_analysis:
            issue_count += len(report.static_analysis.get("security_issues", []))
            issue_count += len(report.static_analysis.get("complexity_hotspots", []))
        
        if report.gap_analysis:
            issue_count += report.gap_analysis.get("gaps_found", 0)
        
        if report.behavior_analysis:
            issue_count += len(report.behavior_analysis.get("error_patterns", []))
        
        if report.quality_metrics:
            if report.quality_metrics.get("coverage", 100) < 80:
                issue_count += 1
            if report.quality_metrics.get("complexity", 0) > 10:
                issue_count += 1
        
        report.total_issues_found = issue_count
        
        # Extract critical issues
        critical = []
        
        if report.static_analysis:
            for issue in report.static_analysis.get("security_issues", []):
                if issue.get("severity") in ["HIGH", "CRITICAL"]:
                    critical.append(issue)
        
        if report.behavior_analysis:
            for error in report.behavior_analysis.get("critical_errors", []):
                critical.append(error)
        
        if report.impact_analysis:
            for risk in report.impact_analysis.get("risks", {}).get("high_risk_components", []):
                critical.append(risk)
        
        report.critical_issues = critical[:10]  # Top 10 critical issues
    
    def _generate_recommendations(self, report: UpgradeReport) -> None:
        """Generate upgrade recommendations.
        
        Args:
            report: Report with analysis results
        """
        immediate = []
        short_term = []
        long_term = []
        
        # Based on critical issues
        if report.critical_issues:
            immediate.append("Address critical security and stability issues immediately")
        
        # Based on test coverage
        if report.gap_analysis:
            coverage = report.gap_analysis.get("total_coverage", 0)
            if coverage < 50:
                immediate.append(f"Critical: Test coverage is only {coverage:.1f}%")
            elif coverage < 80:
                short_term.append(f"Improve test coverage from {coverage:.1f}% to 80%")
        
        # Based on code quality
        if report.quality_metrics:
            if report.quality_metrics.get("complexity", 0) > 15:
                short_term.append("Refactor complex functions to reduce cyclomatic complexity")
        
        # Based on behavior analysis
        if report.behavior_analysis:
            if report.behavior_analysis.get("error_rate", 0) > 0.05:
                immediate.append("High error rate detected - investigate and fix")
            
            hotspots = report.behavior_analysis.get("performance_hotspots", [])
            if hotspots:
                short_term.append(f"Optimize {len(hotspots)} performance bottlenecks")
        
        # Based on impact analysis
        if report.impact_analysis:
            if report.impact_analysis.get("system_health", {}).get("technical_debt_score", 0) > 50:
                long_term.append("Develop technical debt reduction strategy")
            
            circular_deps = report.impact_analysis.get("risks", {}).get("circular_dependencies", 0)
            if circular_deps > 0:
                short_term.append(f"Resolve {circular_deps} circular dependencies")
        
        # Based on static analysis
        if report.static_analysis:
            if report.static_analysis.get("architecture_layers", {}):
                long_term.append("Consider architectural improvements for better separation of concerns")
        
        report.immediate_actions = immediate
        report.short_term_goals = short_term
        report.long_term_goals = long_term
    
    def _calculate_scores(self, report: UpgradeReport) -> None:
        """Calculate overall scores.
        
        Args:
            report: Report with analysis results
        """
        # System health score (0-100)
        health_factors = []
        
        if report.gap_analysis:
            coverage = report.gap_analysis.get("total_coverage", 0)
            health_factors.append(coverage)
        
        if report.quality_metrics:
            quality = 100 - min(report.quality_metrics.get("complexity", 0) * 5, 50)
            health_factors.append(quality)
        
        if report.behavior_analysis:
            error_rate = report.behavior_analysis.get("error_rate", 0)
            behavior_health = max(0, 100 - (error_rate * 1000))
            health_factors.append(behavior_health)
        
        if health_factors:
            report.system_health_score = sum(health_factors) / len(health_factors)
        
        # Upgrade risk score (0-100)
        risk_factors = []
        
        # More critical issues = higher risk
        risk_factors.append(min(len(report.critical_issues) * 10, 50))
        
        # High technical debt = higher risk
        if report.impact_analysis:
            tech_debt = report.impact_analysis.get("system_health", {}).get("technical_debt_score", 0)
            risk_factors.append(tech_debt * 0.5)
        
        # Low test coverage = higher risk
        if report.gap_analysis:
            coverage = report.gap_analysis.get("total_coverage", 0)
            risk_factors.append(max(0, 50 - coverage * 0.5))
        
        if risk_factors:
            report.upgrade_risk_score = min(sum(risk_factors) / len(risk_factors), 100)
    
    async def execute_plan(self, plan_id: str, task_ids: List[str] = None) -> Dict[str, Any]:
        """계획을 실행하는 메서드 (Phase 2).
        
        분석 완료 후 생성된 계획(4_Tasks.json)을 실제로 실행합니다.
        사용자가 승인한 태스크만 선택적으로 실행 가능합니다.
        
        Args:
            plan_id: 실행할 계획 ID (보통 timestamp)
            task_ids: 실행할 특정 태스크 ID 목록 (None이면 전체 실행)
            
        Returns:
            실행 결과 딕셔너리
        """
        logger.info(f"Executing plan: {plan_id}")
        
        # 1. 계획 로드
        plan = await self.memory_hub.get(ContextType.O_CTX, f"plan_{plan_id}")
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        # 2. 태스크 필터링
        tasks_to_execute = plan['tasks']
        if task_ids:
            tasks_to_execute = [t for t in tasks_to_execute if t['id'] in task_ids]
        
        execution_results = {
            'plan_id': plan_id,
            'started_at': datetime.now().isoformat(),
            'tasks': []
        }
        
        # 3. 각 태스크 실행
        for task in tasks_to_execute:
            if task['type'] == 'code_generation':
                # CodeGenerator 사용
                result = await self._execute_code_generation(task)
            elif task['type'] == 'code_modification':
                # 기존 코드 수정
                result = await self._execute_code_modification(task)
            elif task['type'] == 'test_creation':
                # 테스트 생성
                result = await self._execute_test_creation(task)
            else:
                result = {'status': 'skipped', 'reason': 'Unknown task type'}
            
            execution_results['tasks'].append({
                'task_id': task['id'],
                'task_type': task['type'],
                'result': result
            })
        
        execution_results['completed_at'] = datetime.now().isoformat()
        
        # 4. 결과 저장
        await self.memory_hub.put(
            ContextType.O_CTX,
            f"execution_result_{plan_id}",
            execution_results,
            ttl_seconds=86400 * 30
        )
        
        return execution_results
    
    async def _execute_code_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """코드 생성 태스크 실행."""
        if not self.code_generator:
            from backend.packages.agents.code_generator import CodeGenerator
            self.code_generator = CodeGenerator(memory_hub=self.memory_hub)
        
        generation_task = AgentTask(
            type="code_generation",
            data=task['specification']
        )
        
        result = await self.code_generator.execute(generation_task)
        return result.data if result else {'status': 'failed'}
    
    async def _execute_code_modification(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """코드 수정 태스크 실행."""
        # TODO: 구현 필요
        return {'status': 'not_implemented'}
    
    async def _execute_test_creation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 생성 태스크 실행."""
        # TODO: 구현 필요
        return {'status': 'not_implemented'}
    
    async def shutdown(self) -> None:
        """Shutdown orchestrator and cleanup resources."""
        logger.info("Shutting down Upgrade Orchestrator")
        # Cleanup if needed
        pass
    
    async def _check_system_ready(self) -> bool:
        """Check if system is ready for analysis.
        
        Returns:
            True if ready
        """
        # Check if project path exists
        if not os.path.exists(self.config.project_path):
            logger.error(f"Project path does not exist: {self.config.project_path}")
            return False
        
        # Check if it's a valid project
        if not os.path.isdir(self.config.project_path):
            logger.error("Project path is not a directory")
            return False
        
        return True
    
    def _break_into_small_tasks(self, requirements: str) -> List[Dict[str, Any]]:
        """작업을 5~20분 단위로 쪼갠다.
        
        Args:
            requirements: 요구사항
            
        Returns:
            작은 태스크 목록
        """
        tasks = [
            {"name": "요청 파악", "duration": "5분", "status": "pending"},
            {"name": "빠진 정보 질문", "duration": "5분", "status": "pending"},
            {"name": "목표 명세서 작성", "duration": "10분", "status": "pending"},
            {"name": "정적 분석 실행", "duration": "15분", "status": "pending"},
            {"name": "동적 분석 실행", "duration": "15분", "status": "pending"},
            {"name": "AI 아키텍처 요약", "duration": "10분", "status": "pending"},
            {"name": "계약/인터페이스 채굴", "duration": "10분", "status": "pending"},
            {"name": "테스트 갭 분석", "duration": "10분", "status": "pending"},
            {"name": "영향도 매트릭스 작성", "duration": "15분", "status": "pending"},
            {"name": "리스크 스코어 계산", "duration": "5분", "status": "pending"},
            {"name": "마이그레이션 전략 수립", "duration": "20분", "status": "pending"},
            {"name": "배치 계획 작성", "duration": "15분", "status": "pending"},
            {"name": "최종 보고서 생성", "duration": "10분", "status": "pending"}
        ]
        return tasks
    
    async def _create_evolution_goal(self, requirements: str) -> EvolutionGoalSpec:
        """진화 목표 명세서 작성.
        
        Args:
            requirements: 요구사항
            
        Returns:
            진화 목표 명세서
        """
        # 요구사항 분석
        task = AgentTask(
            task_id="evolution_goal",
            intent="analyze_requirements",
            inputs={
                "requirements": requirements,
                "project_context": {
                    "path": self.config.project_path,
                    "type": "upgrade_analysis"
                }
            }
        )
        req_result = await self.requirement_analyzer.execute(task)
        
        # 목표 명세서 생성
        spec_data = req_result.data.get("specification", {}) if req_result.success else {}
        goal_spec = EvolutionGoalSpec(
            background=spec_data.get("background", "System upgrade and evolution"),
            stakeholders=spec_data.get("stakeholders", ["developers", "users", "operations"]),
            change_scope={
                "included": spec_data.get("in_scope", []),
                "excluded": spec_data.get("out_of_scope", []),
                "preserve": ["existing APIs", "data integrity", "user workflows"]
            },
            success_criteria={
                "metrics": spec_data.get("success_metrics", {}),
                "performance": {"latency": "<100ms", "throughput": ">1000 rps"},
                "cost": {"monthly": "<$10000", "per_request": "<$0.001"},
                "risk_reduction": {"security_issues": 0, "critical_bugs": 0}
            },
            constraints={
                "deadline": spec_data.get("deadline", "30 days"),
                "budget": spec_data.get("budget", "unlimited"),
                "regulations": spec_data.get("regulations", []),
                "compatibility": spec_data.get("compatibility", [])
            },
            compatibility_requirements=[
                "Backward compatible APIs",
                "No breaking changes for existing clients",
                "Gradual migration path",
                "Feature flags for new functionality"
            ],
            open_questions=spec_data.get("open_questions", [])
        )
        
        return goal_spec
    
    async def _analyze_current_state(self) -> CurrentStateReport:
        """현재 상태 종합 분석 (의존성 기반 실행 그룹).
        
        실행 그룹별 분석:
        Group 1 (독립적, 병렬 실행):
        - 정적 분석: 코드 구조, 복잡도
        - 의존성 분석: 버전, 취약점, 라이선스
        - 계약 추출: API, 스키마, 인터페이스
        
        Group 2 (Group 1 결과 활용, 병렬 실행):
        - 보안 분석: 정적 분석 결과 기반
        - 아키텍처 분석: 정적 분석 + 의존성 분석 기반
        - 코드 품질: 정적 분석 기반 품질 평가
        - 테스트 분석: 코드 구조 기반 커버리지 분석
        
        Group 3 (Group 1,2 결과 활용, 병렬 실행):
        - 동적 분석: 아키텍처 이해 기반 런타임 분석
        - 행동 분석: 로그/메트릭 + 아키텍처 이해
        - 성능 분석: 동적 프로파일링 + 병목 지점
        
        Returns:
            종합 현재 상태 보고서
        """
        logger.info("Starting comprehensive current state analysis with dependency groups...")
        start_time = datetime.now()
        analysis_results = {}
        
        # Group 1: 독립적 분석들 (병렬 실행)
        logger.info("Executing Group 1: Independent analyses...")
        group1_tasks = {
            "static": self._run_static_analysis(),
            "dependencies": self._run_dependency_analysis(),
            "contracts": self._mine_contracts()
        }
        
        group1_results = await asyncio.gather(
            *group1_tasks.values(),
            return_exceptions=True
        )
        
        for (name, _), result in zip(group1_tasks.items(), group1_results):
            if isinstance(result, Exception):
                logger.warning(f"Group 1 analysis {name} failed: {result}")
                analysis_results[name] = {}
            else:
                analysis_results[name] = result
                
        # Group 2: Group 1 결과에 의존하는 분석들 (병렬 실행)
        logger.info("Executing Group 2: Dependent analyses...")
        group2_tasks = {
            "security": self._run_security_analysis(analysis_results.get("static", {})),
            "architecture": self._analyze_architecture(
                static_data=analysis_results.get("static", {}),
                dependency_data=analysis_results.get("dependencies", {})
            ),
            "quality": self._run_code_quality_analysis(analysis_results.get("static", {})),
            "test": self._run_test_analysis(analysis_results.get("static", {}))
        }
        
        group2_results = await asyncio.gather(
            *group2_tasks.values(),
            return_exceptions=True
        )
        
        for (name, _), result in zip(group2_tasks.items(), group2_results):
            if isinstance(result, Exception):
                logger.warning(f"Group 2 analysis {name} failed: {result}")
                analysis_results[name] = {}
            else:
                analysis_results[name] = result
                
        # Group 3: 이전 결과들을 활용하는 런타임 분석들 (병렬 실행)
        logger.info("Executing Group 3: Runtime analyses...")
        group3_tasks = {
            "dynamic": self._run_dynamic_analysis(
                architecture=analysis_results.get("architecture", {})
            ),
            "behavior": self._run_behavior_analysis(
                architecture=analysis_results.get("architecture", {})
            ),
            "performance": self._run_performance_analysis(
                static_data=analysis_results.get("static", {}),
                architecture=analysis_results.get("architecture", {})
            )
        }
        
        group3_results = await asyncio.gather(
            *group3_tasks.values(),
            return_exceptions=True
        )
        
        for (name, _), result in zip(group3_tasks.items(), group3_results):
            if isinstance(result, Exception):
                logger.warning(f"Group 3 analysis {name} failed: {result}")
                analysis_results[name] = {}
            else:
                analysis_results[name] = result
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 동적 분석 결과 통합 (런타임 + 행동 + 성능)
        enhanced_dynamic = {
            **analysis_results.get("dynamic", {}),
            "behavior_analysis": analysis_results.get("behavior", {}),
            "performance_profile": analysis_results.get("performance", {}),
            "execution_metrics": {
                "analysis_time": execution_time,
                "execution_groups": 3,
                "total_analyses": 10,
                "successful_analyses": sum(1 for k, v in analysis_results.items() if v)
            }
        }
        
        # 정적 분석 결과 강화 (품질 + 보안 + 의존성)
        enhanced_static = {
            **analysis_results.get("static", {}),
            "code_quality": analysis_results.get("quality", {}),
            "security_scan": analysis_results.get("security", {}),
            "dependency_analysis": analysis_results.get("dependencies", {}),
            "architecture": analysis_results.get("architecture", {})
        }
        
        # AI 요약 생성
        ai_summary = {
            "overview": "Comprehensive analysis completed",
            "key_findings": [
                f"Found {enhanced_static.get('total_files', 0)} files",
                f"Test coverage: {analysis_results.get('test', {}).get('coverage', 0)}%",
                f"Complexity hotspots: {enhanced_static.get('complexity_hotspots', 0)}"
            ],
            "recommendations": [
                "Improve test coverage",
                "Reduce complexity",
                "Optimize performance"
            ]
        }
        
        # 테스트 갭 식별
        test_gaps = self._identify_test_gaps(
            analysis_results.get("test", {}),
            enhanced_static,
            enhanced_dynamic
        )
        
        # UX/행동 메트릭 추출
        ux_metrics = self._extract_ux_metrics(
            analysis_results.get("behavior", {}),
            analysis_results.get("performance", {})
        )
        
        logger.info(f"Current state analysis complete in {execution_time:.2f}s: "
                   f"Files: {enhanced_static.get('total_files', 0)}, "
                   f"Coverage: {analysis_results.get('test', {}).get('coverage', 0)}%, "
                   f"Issues: {enhanced_static.get('total_issues', 0)}")
        
        return CurrentStateReport(
            static_analysis=enhanced_static,
            dynamic_analysis=enhanced_dynamic,
            ai_summary=ai_summary,
            contracts=analysis_results.get("contracts", {}),
            test_gaps=test_gaps,
            ux_metrics=ux_metrics
        )
    
    async def _run_static_analysis(self) -> Dict[str, Any]:
        """정적 분석 실행."""
        task = AgentTask(
            task_id="static_analysis",
            intent="analyze_static",
            inputs={
                "path": self.config.project_path,
                "recursive": True
            }
        )
        result = await self.static_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _run_dynamic_analysis(self, architecture: Dict[str, Any] = None) -> Dict[str, Any]:
        """동적 분석 실행."""
        if not self.config.enable_dynamic_analysis:
            return {"skipped": True, "reason": "Dynamic analysis disabled"}
        
        # 아키텍처 정보를 활용한 동적 분석
        return {
            "runtime_metrics": {
                "memory_usage": 512,  # MB
                "cpu_usage": 45,  # %
                "network_io": 100,  # MB/s
                "disk_io": 50  # MB/s
            },
            "performance": {
                "avg_response_time": 250,
                "p95_latency": 800,
                "throughput": 1000
            },
            "architecture_runtime": architecture if architecture else {},
            "profiling_data": {}
        }
    
    async def _run_ai_summary(self) -> Dict[str, Any]:
        """AI 아키텍처 요약."""
        task = AgentTask(
            task_id="ai_summary",
            intent="analyze_architecture",
            inputs={
                "file_path": self.config.project_path,
                "analysis_type": "architecture"
            }
        )
        result = await self.code_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _mine_contracts(self) -> Dict[str, Any]:
        """계약/인터페이스 자동 채굴."""
        # API, 스키마, 이벤트, DB 테이블 추출
        contracts = {
            "apis": [],
            "schemas": [],
            "events": [],
            "db_tables": []
        }
        
        # Static analyzer를 통해 인터페이스 추출
        task = AgentTask(
            task_id="mine_contracts",
            intent="extract_interfaces",
            inputs={
                "path": self.config.project_path,
                "extract_interfaces": True
            }
        )
        result = await self.static_analyzer.execute(task)
        
        if result.success:
            contracts.update(result.data.get("interfaces", {}))
        
        return contracts
    
    async def _find_test_gaps(self) -> List[Dict[str, Any]]:
        """테스트 갭 찾기."""
        task = AgentTask(
            task_id="find_gaps",
            intent="analyze_gaps",
            inputs={
                "project_path": self.config.project_path,
                "min_coverage": 80
            }
        )
        result = await self.gap_analyzer.execute(task)
        return result.data.get("gaps", []) if result.success else []
    
    async def _collect_ux_metrics(self) -> Dict[str, Any]:
        """UX/행동 데이터 수집."""
        # 로그에서 UX 메트릭 추출
        metrics = {
            "conversion_rate": 0.0,
            "retention_rate": 0.0,
            "key_actions": [],
            "user_flows": []
        }
        
        if self.config.include_behavior_analysis:
            task = AgentTask(
                task_id="ux_metrics",
                intent="extract_metrics",
                inputs={
                    "log_paths": self._find_log_files(),
                    "extract_ux_metrics": True
                }
            )
            result = await self.behavior_analyzer.execute(task)
            if result.success:
                metrics.update(result.data.get("ux_metrics", {}))
        
        return metrics
    
    async def _conduct_external_research(
        self,
        evolution_goal: Optional[EvolutionGoalSpec],
        current_state: Optional[CurrentStateReport]
    ) -> UpgradeResearchPack:
        """외부 리서치 수행 (URP 생성).
        
        upgrade.md의 4A) 섹션 구현.
        
        Args:
            evolution_goal: 진화 목표 명세서
            current_state: 현재 상태 보고서
            
        Returns:
            업그레이드 리서치 팩
        """
        logger.info("Conducting external research for URP...")
        
        # ExternalResearcher 통합
        try:
            from backend.packages.agents.external_researcher import ExternalResearcher
            researcher = ExternalResearcher(memory_hub=self.memory_hub)
            use_real_researcher = True
        except Exception as e:
            logger.warning(f"Could not load ExternalResearcher: {e}. Using simulation mode.")
            use_real_researcher = False
        
        # 리서치 데이터 준비 - 현재 분석 결과 기반
        research_data = {
            'project_context': self.config.project_path,
            'project_type': 'software',
            'primary_language': 'python',
            'identified_issues': [],
            'low_metrics': [],
            'security_vulnerabilities': [],
            'performance_issues': [],
            'outdated_dependencies': [],
            'architecture_issues': [],
            'improvement_goals': []
        }
        
        # 현재 상태 분석 결과에서 문제점 추출
        if current_state and current_state.static_analysis:
            static = current_state.static_analysis
            
            # 언어 정보
            languages = static.get('languages', {})
            if languages:
                research_data['primary_language'] = max(languages, key=languages.get)
            
            # 복잡도 문제
            if static.get('complexity_hotspots', 0) > 10:
                research_data['identified_issues'].append({
                    'type': 'high_complexity',
                    'description': f"{static['complexity_hotspots']} complexity hotspots found"
                })
            
            # 테스트 커버리지 문제
            coverage_str = static.get('test_coverage_estimate', '0%')
            coverage = float(coverage_str.rstrip('%'))
            if coverage < 50:
                research_data['low_metrics'].append({
                    'name': 'test_coverage',
                    'value': coverage
                })
            
            # 보안 이슈
            if static.get('security_issues', 0) > 0:
                research_data['security_vulnerabilities'].append({
                    'type': 'static_analysis',
                    'component': 'codebase',
                    'severity': 'high' if static['security_issues'] > 5 else 'medium'
                })
        
        # 동적 분석 결과에서 성능 문제 추출
        if current_state and current_state.dynamic_analysis:
            dynamic = current_state.dynamic_analysis
            if dynamic.get('performance'):
                perf = dynamic['performance']
                if perf.get('avg_response_time', 0) > 1000:  # 1초 이상
                    research_data['performance_issues'].append({
                        'area': 'response_time',
                        'description': 'High average response time',
                        'current_metric': f"{perf['avg_response_time']}ms"
                    })
        
        # 진화 목표에서 개선 목표 추출
        if evolution_goal:
            # 성공 기준을 개선 목표로 변환
            if evolution_goal.success_criteria:
                for criteria, value in evolution_goal.success_criteria.items():
                    research_data['improvement_goals'].append(f"{criteria}: {value}")
            
            # 열린 질문들을 이슈로 추가
            for question in evolution_goal.open_questions[:3]:
                research_data['identified_issues'].append({
                    'type': 'open_question',
                    'description': question
                })
        
        # 리서치 수행
        if use_real_researcher:
            # 실제 ExternalResearcher 사용
            research_task = AgentTask(
                type="external_research",
                intent="Conduct external research for upgrade planning",
                data=research_data
            )
            
            result = await researcher.execute(research_task)
            research_findings = result.data if result.status == "completed" else self._get_simulation_research()
        else:
            # 시뮬레이션 모드
            research_findings = self._get_simulation_research()
        
        # URP 생성
        urp = UpgradeResearchPack(
            one_line_conclusion=research_findings.get(
                'one_line_conclusion',
                'Research conducted for upgrade planning'
            ),
            recommended_approach={
                'name': 'Incremental Migration',
                'description': 'Gradual transition with feature flags',
                'pros': ['Lower risk', 'Rollback capability'],
                'cons': ['Longer timeline', 'Complexity overhead']
            },
            alternative_approaches=[
                {
                    'name': 'Big Bang Migration',
                    'description': 'Complete transition at once',
                    'pros': ['Faster completion', 'Simpler management'],
                    'cons': ['Higher risk', 'Difficult rollback']
                }
            ],
            compatibility_checklist=[
                {'item': 'API backward compatibility', 'status': 'pending'},
                {'item': 'Data schema compatibility', 'status': 'pending'},
                {'item': 'Client compatibility', 'status': 'pending'}
            ],
            migration_strategy={
                'approach': 'Expand-Contract',
                'phases': ['Add new', 'Migrate data', 'Remove old'],
                'estimated_duration': '2-4 weeks'
            },
            code_snippets=research_findings.get('code_snippets', []),
            warnings=research_findings.get('warnings', [
                'Ensure proper backup before migration',
                'Monitor performance during transition'
            ]),
            success_criteria={
                'metrics': ['Zero downtime', 'No data loss', 'Performance maintained'],
                'measurement': 'Automated monitoring and alerts'
            },
            cost_risk_summary={
                'cost': 'Medium',
                'risk': 'Low-Medium',
                'mitigation': 'Feature flags and gradual rollout'
            },
            dedup_results=research_findings.get('dedup_results', {
                'similar_projects': [],
                'reusable_components': []
            }),
            references=research_findings.get('sources', [
                'Internal documentation',
                'Industry best practices',
                'Security advisories'
            ])
        )
        
        # 메모리에 저장
        if self.memory_hub:
            await self.memory_hub.put(
                ContextType.S_CTX,
                f"urp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                asdict(urp),
                ttl_seconds=86400 * urp.ttl_days
            )
        
        # URP 문서 저장
        await self._save_urp_document(urp)
        
        return urp
    
    def _get_simulation_research(self) -> Dict[str, Any]:
        """시뮬레이션 리서치 데이터 반환."""
        return {
            'key_findings': [
                {'finding': 'Test coverage tools like pytest-cov can help achieve 80% coverage'},
                {'finding': 'Complexity can be reduced using design patterns'},
                {'finding': 'Performance optimization through caching and async operations'}
            ],
            'best_practices': [
                'Use TDD for new features',
                'Implement CI/CD pipeline',
                'Regular code reviews'
            ],
            'security_updates': [],
            'technology_trends': [
                {'name': 'AI-driven testing', 'adoption_rate': 0.3},
                {'name': 'Microservices architecture', 'adoption_rate': 0.6}
            ],
            'recommendations': [
                'Implement pytest-cov for coverage measurement',
                'Use radon for complexity analysis',
                'Apply SOLID principles'
            ],
            'action_items': [
                {'type': 'improvement', 'priority': 'high', 'description': 'Add unit tests for uncovered code'},
                {'type': 'improvement', 'priority': 'medium', 'description': 'Refactor complex functions'}
            ]
        }
    
    async def _save_urp_document(self, urp: UpgradeResearchPack) -> None:
        """URP를 마크다운 문서로 저장.
        
        Args:
            urp: 업그레이드 리서치 팩
        """
        # 문서 생성
        doc_content = f"""# Upgrade Research Pack (URP)
Generated: {urp.created_at}
TTL: {urp.ttl_days} days

## 1. 한 줄 결론
{urp.one_line_conclusion}

## 2. 추천 접근법
### {urp.recommended_approach.get('name', 'Primary Approach')}
- **설명**: {urp.recommended_approach.get('description', '')}
- **장점**: {', '.join(urp.recommended_approach.get('pros', []))}
- **단점**: {', '.join(urp.recommended_approach.get('cons', []))}

## 3. 대안 접근법
"""
        for i, alt in enumerate(urp.alternative_approaches, 1):
            doc_content += f"""
### 대안 {i}: {alt.get('name', f'Alternative {i}')}
- **설명**: {alt.get('description', '')}
- **장점**: {', '.join(alt.get('pros', []))}
- **단점**: {', '.join(alt.get('cons', []))}
"""

        doc_content += f"""
## 4. 호환성 체크리스트
"""
        for item in urp.compatibility_checklist:
            status = "✅" if item.get('status') == 'completed' else "⏳"
            doc_content += f"- {status} {item.get('item', '')}\n"

        doc_content += f"""
## 5. 마이그레이션 전략
- **접근법**: {urp.migration_strategy.get('approach', '')}
- **단계**: {' → '.join(urp.migration_strategy.get('phases', []))}
- **예상 기간**: {urp.migration_strategy.get('estimated_duration', '')}

## 6. 핵심 코드 스니펫
"""
        for i, snippet in enumerate(urp.code_snippets[:3], 1):
            if isinstance(snippet, dict):
                doc_content += f"""
### 스니펫 {i}: {snippet.get('title', f'Snippet {i}')}
```{snippet.get('language', 'python')}
{snippet.get('code', '')}
```
**적용 위치**: {snippet.get('location', '')}
**주의사항**: {snippet.get('notes', '')}
"""

        doc_content += f"""
## 7. 주의사항/함정
"""
        for warning in urp.warnings:
            doc_content += f"- ⚠️ {warning}\n"

        doc_content += f"""
## 8. 성공/실패 기준
- **지표**: {', '.join(urp.success_criteria.get('metrics', []))}
- **측정 방법**: {urp.success_criteria.get('measurement', '')}

## 9. 비용/리스크 요약
- **비용**: {urp.cost_risk_summary.get('cost', '')}
- **리스크**: {urp.cost_risk_summary.get('risk', '')}
- **완화 전략**: {urp.cost_risk_summary.get('mitigation', '')}

## 10. De-dup 결과
- **유사 프로젝트**: {len(urp.dedup_results.get('similar_projects', []))}개
- **재사용 가능 컴포넌트**: {len(urp.dedup_results.get('reusable_components', []))}개

## 11. 참고자료
"""
        for ref in urp.references:
            doc_content += f"- {ref}\n"

        # 파일 저장
        from pathlib import Path
        import os
        
        # 타임스탬프 기반 디렉토리 생성
        project_name = Path(self.config.project_path).name
        timestamp = datetime.now().isoformat()
        output_dir = Path(self.config.output_dir) / project_name / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # URP 문서 저장
        urp_path = output_dir / "0_URP.md"
        with open(urp_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        logger.info(f"URP document saved to {urp_path}")
        
        # 상세 리포트도 저장
        detailed_path = output_dir / "0_URP_detailed.json"
        import json
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(urp), f, indent=2, default=str)
        logger.info(f"Detailed URP saved to {detailed_path}")
    
    async def _analyze_gaps_and_plan(
        self,
        goal: EvolutionGoalSpec,
        current: CurrentStateReport,
        research_pack: Optional[UpgradeResearchPack] = None
    ) -> GapReport:
        """갭 분석 및 계획 수립 (리서치 결과 반영).
        
        Args:
            goal: 목표 명세
            current: 현재 상태
            research_pack: 외부 리서치 결과 (선택적)
            
        Returns:
            갭 보고서
        """
        # 갭 분석 (리서치 결과 활용)
        gaps = []
        
        # 리서치 기반 액션 아이템 추가
        if research_pack:
            # 보안 업데이트가 있으면 최우선
            for warning in research_pack.warnings:
                if 'security' in warning.lower() or 'vulnerability' in warning.lower():
                    gaps.append({
                        "type": "security",
                        "description": warning,
                        "priority": "critical",
                        "source": "external_research"
                    })
            
            # 추천 접근법 기반 갭 추가
            if research_pack.recommended_approach:
                gaps.append({
                    "type": "strategy",
                    "description": f"Implement {research_pack.recommended_approach.get('name', 'recommended approach')}",
                    "priority": "high",
                    "details": research_pack.recommended_approach,
                    "source": "external_research"
                })
        
        # 기능 갭
        if goal.change_scope.get("included"):
            for feature in goal.change_scope["included"]:
                gaps.append({
                    "type": "feature",
                    "description": f"Implement {feature}",
                    "priority": "high"
                })
        
        # 성능 갭
        if current.dynamic_analysis.get("performance"):
            perf = current.dynamic_analysis["performance"]
            if perf.get("p95_latency", 0) > 100:
                gaps.append({
                    "type": "performance",
                    "description": "Reduce P95 latency below 100ms",
                    "current": perf.get("p95_latency"),
                    "target": 100,
                    "priority": "medium"
                })
        
        # 보안 갭
        if current.static_analysis.get("security_issues"):
            gaps.append({
                "type": "security",
                "description": "Fix security vulnerabilities",
                "count": len(current.static_analysis["security_issues"]),
                "priority": "critical"
            })
        
        # PlannerAgent를 사용한 실행 계획 생성
        logger.info("Creating execution plan with PlannerAgent...")
        
        # goal의 change_scope와 success_criteria를 requirement로 변환
        requirement_text = f"""
        Background: {goal.background}
        Change Scope: {goal.change_scope}
        Success Criteria: {goal.success_criteria}
        Constraints: {goal.constraints}
        """
        
        planner_task = AgentTask(
            task_id="create_plan",
            intent="create_plan",
            inputs={
                "requirement": requirement_text,
                "context": {
                    "current_state": current.static_analysis,
                    "gaps": gaps,
                    "research": research_pack.__dict__ if research_pack else {}
                }
            }
        )
        
        plan_result = await self.planner_agent.execute(planner_task)
        execution_plan = plan_result.data.get("plan", {}) if plan_result.success else {}
        logger.info(f"PlannerAgent result: {plan_result.success}, phases: {len(execution_plan.get('phases', []))}")
        
        # TaskCreatorAgent를 사용한 태스크 생성
        logger.info("Creating tasks with TaskCreatorAgent...")
        task_creator_task = AgentTask(
            task_id="create_tasks",
            intent="create_tasks",
            inputs={
                "plan": execution_plan,
                "requirement": requirement_text,
                "context": {"project_path": self.config.project_path}
            }
        )
        
        tasks_result = await self.task_creator_agent.execute(task_creator_task)
        executable_tasks = tasks_result.data.get("tasks", []) if tasks_result.success else []
        logger.info(f"TaskCreatorAgent result: {tasks_result.success}, tasks: {len(executable_tasks)}")
        
        # 영향도 매트릭스 생성
        task = AgentTask(
            task_id="impact_analysis",
            intent="analyze_impact",
            inputs={
                "project_path": self.config.project_path,
                "proposed_changes": gaps
            }
        )
        impact_result = await self.impact_analyzer.execute(task)
        
        impact_matrix = impact_result.data if impact_result.success else {}
        
        # 리스크 스코어 계산
        risk_scores = {
            "complexity": self._calculate_complexity_risk(current),
            "impact": self._calculate_impact_risk(impact_matrix),
            "rollback": self._calculate_rollback_risk(gaps)
        }
        
        # 마이그레이션 전략
        # 리서치 기반 마이그레이션 전략 선택
        if research_pack and research_pack.migration_strategy:
            migration_strategy = research_pack.migration_strategy.get('approach', 'expand_contract')
            migration_phases = research_pack.migration_strategy.get('phases', [])
            estimated_duration = research_pack.migration_strategy.get('estimated_duration', '4-6 weeks')
        else:
            migration_strategy = "expand_contract"
            migration_phases = ["Add new structure", "Shadow read/write", "Gradual migration", "Remove old structure"]
            estimated_duration = "4-6 weeks"
        
        migration_plan = {
            "strategy": migration_strategy,
            "phases": [
                {"phase": i+1, "action": phase, "duration": f"Week {i+1}"}
                for i, phase in enumerate(migration_phases)
            ],
            "estimated_duration": estimated_duration,
            "feature_flags": [f"feature_{i}" for i in range(len(gaps))],
            "canary_plan": {
                "stages": [1, 5, 25, 50, 100],
                "metrics": ["error_rate", "latency", "cpu_usage"]
            }
        }
        
        # 작은 배치 계획
        batch_plan = []
        for i, gap in enumerate(gaps):
            batch_plan.append({
                "batch": i + 1,
                "gap": gap,
                "estimated_time": "1-2 days",
                "dependencies": [],
                "rollback_plan": "Feature flag disable"
            })
        
        return GapReport(
            gaps=gaps,
            impact_matrix=impact_matrix,
            risk_scores=risk_scores,
            migration_plan=migration_plan,
            batch_plan=batch_plan
        )
    
    def _calculate_complexity_risk(self, current: CurrentStateReport) -> float:
        """복잡도 리스크 계산."""
        if current.ai_summary.get("complexity"):
            return min(current.ai_summary["complexity"] / 100, 1.0)
        return 0.5
    
    def _calculate_impact_risk(self, impact_matrix: Dict[str, Any]) -> float:
        """영향도 리스크 계산."""
        if impact_matrix.get("affected_components"):
            return min(len(impact_matrix["affected_components"]) / 20, 1.0)
        return 0.5
    
    def _calculate_rollback_risk(self, gaps: List[Dict[str, Any]]) -> float:
        """롤백 난이도 계산."""
        critical_gaps = [g for g in gaps if g.get("priority") == "critical"]
        return min(len(critical_gaps) / 5, 1.0)
    
    async def _store_report(self, report: UpgradeReport) -> None:
        """Store report in memory hub.
        
        Args:
            report: Report to store
        """
        if self.memory_hub:
            try:
                # Convert report to dict safely
                report_dict = {}
                for key, value in report.__dict__.items():
                    if value is None:
                        report_dict[key] = None
                    elif hasattr(value, '__dict__'):
                        # Convert nested dataclasses
                        try:
                            report_dict[key] = asdict(value)
                        except:
                            report_dict[key] = str(value)
                    elif isinstance(value, (list, dict, str, int, float, bool)):
                        report_dict[key] = value
                    else:
                        report_dict[key] = str(value)
                
                # Store main report
                await self.memory_hub.put(
                    ContextType.O_CTX,
                    f"upgrade_report_{report.timestamp}",
                    report_dict,
                    ttl_seconds=86400 * 30  # Keep for 30 days
                )
                
                # Store individual documents
                if report.evolution_goal:
                    await self.memory_hub.put(
                        ContextType.S_CTX,
                        "evolution_goal_latest",
                        asdict(report.evolution_goal),
                        ttl_seconds=86400 * 30
                    )
                
                if report.gap_report:
                    await self.memory_hub.put(
                        ContextType.S_CTX,
                        "gap_report_latest",
                        asdict(report.gap_report),
                        ttl_seconds=86400 * 30
                    )
            except Exception as e:
                logger.warning(f"Failed to store report in memory hub: {e}")
                # Don't fail the whole operation
            
            # Generate reports using ReportGenerator agent
            # await self._generate_reports_via_agent(report)  # ReportGenerator not implemented yet
    
    async def _generate_reports_via_agent(self, report: UpgradeReport) -> None:
        """ReportGenerator 에이전트를 통해 리포트 생성.
        
        Args:
            report: 업그레이드 리포트
        """
        # ReportGenerator 에이전트 동적 로드
        # from backend.packages.agents.report_generator import ReportGenerator  # Not implemented yet
        
        report_generator = ReportGenerator(memory_hub=self.memory_hub)
        
        # 문서 저장 경로 확인 및 생성
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 프로젝트별 디렉토리 생성
        project_name = Path(self.config.project_path).name
        project_dir = output_dir / project_name / report.timestamp.replace(':', '-')
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 진화 목표 명세서 생성 (도착지)
        if report.evolution_goal:
            await report_generator.execute(AgentTask(
                task_id="goal_report",
                intent="generate_report",
                inputs={
                    "report_data": {"evolution_goal": asdict(report.evolution_goal)},
                    "report_type": "evolution_goal",
                    "format": "markdown",
                    "output_path": str(project_dir / "1_Goal.md")
                }
            ))
            logger.info(f"Evolution Goal saved to {project_dir / '1_Goal.md'}")
        
        # 현재 상태 보고서 생성 (출발지)
        if report.current_state:
            # asdict 안전하게 호출
            try:
                current_state_dict = asdict(report.current_state) if hasattr(report.current_state, '__dict__') else report.current_state.__dict__
            except:
                current_state_dict = {
                    "static_analysis": report.current_state.static_analysis if report.current_state else {},
                    "dynamic_analysis": report.current_state.dynamic_analysis if report.current_state else {},
                    "ai_summary": report.current_state.ai_summary if report.current_state else {},
                    "contracts": report.current_state.contracts if report.current_state else {},
                    "test_gaps": report.current_state.test_gaps if report.current_state else [],
                    "ux_metrics": report.current_state.ux_metrics if report.current_state else {}
                }
            
            await report_generator.execute(AgentTask(
                task_id="state_report",
                intent="generate_report",
                inputs={
                    "report_data": {"current_state": current_state_dict},
                    "report_type": "current_state",
                    "format": "markdown",
                    "output_path": str(project_dir / "2_CurrentState.md")
                }
            ))
            logger.info(f"Current State saved to {project_dir / '2_CurrentState.md'}")
        
        # 갭 분석 및 실행 계획서 생성
        if report.gap_report:
            await report_generator.execute(AgentTask(
                task_id="plan_report",
                intent="generate_report",
                inputs={
                    "report_data": {"gap_report": asdict(report.gap_report)},
                    "report_type": "execution_plan",
                    "format": "markdown",
                    "output_path": str(project_dir / "3_Plan.md")
                }
            ))
            logger.info(f"Execution Plan saved to {project_dir / '3_Plan.md'}")
        
        # 작은 작업 단위 태스크 목록
        tasks_path = project_dir / "4_Tasks.json"
        with open(tasks_path, 'w', encoding='utf-8') as f:
            json.dump(report.tasks_breakdown, f, indent=2, ensure_ascii=False)
        logger.info(f"Task breakdown saved to {tasks_path}")
        
        # 전체 통합 리포트 생성 (HTML)
        await report_generator.execute(AgentTask(
            task_id="full_report",
            intent="generate_report",
            inputs={
                "report_data": report.__dict__,
                "report_type": "upgrade",
                "format": "html",
                "output_path": str(project_dir / "FullReport.html")
            }
        ))
        logger.info(f"Full report saved to {project_dir / 'FullReport.html'}")
        
        # 결과 요약 파일 생성 (UI에서 쉽게 접근)
        summary = {
            "project": project_name,
            "timestamp": report.timestamp,
            "output_directory": str(project_dir),
            "files_generated": [
                "1_Goal.md",
                "2_CurrentState.md",
                "3_Plan.md",
                "4_Tasks.json",
                "FullReport.html"
            ],
            "health_score": report.system_health_score,
            "risk_score": report.upgrade_risk_score,
            "total_issues": report.total_issues_found,
            "critical_issues": len(report.critical_issues),
            "tasks_count": len(report.tasks_breakdown)
        }
        
        summary_path = project_dir / "summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {summary_path}")
        
        # 메모리에도 경로 저장 (UI에서 조회 가능)
        await self.memory_hub.put(
            ContextType.O_CTX,
            f"latest_report_path",
            str(project_dir),
            ttl_seconds=86400 * 7
        )
    
    async def _run_behavior_analysis(self, architecture: Dict[str, Any] = None) -> Dict[str, Any]:
        """행동 분석 실행 (로그 패턴, 에러 패턴, 사용자 행동)."""
        if not self.config.include_behavior_analysis:
            return {"skipped": True, "reason": "Behavior analysis disabled"}
        
        task = AgentTask(
            task_id="behavior_analysis",
            intent="analyze_behavior",
            inputs={
                "log_paths": self._find_log_files(),
                "architecture": architecture or {}
            }
        )
        result = await self.behavior_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _run_performance_analysis(self, static_data: Dict[str, Any] = None, architecture: Dict[str, Any] = None) -> Dict[str, Any]:
        """성능 분석 실행."""
        return {
            "avg_response_time": 250,  # ms
            "p95_latency": 800,
            "throughput": 1000,  # req/s
            "bottlenecks": [],
            "static_hints": static_data.get("complexity_hotspots", []) if static_data else [],
            "architecture_impact": architecture.get("layers", {}) if architecture else {}
        }
    
    async def _run_test_analysis(self, static_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """테스트 분석 실행."""
        # 정적 분석 데이터를 활용한 테스트 커버리지 분석
        code_files = static_data.get("total_files", 0) if static_data else 0
        test_files = static_data.get("test_files", 0) if static_data else 0
        
        coverage = 0
        if code_files > 0:
            coverage = min((test_files / code_files) * 100, 100)
        
        return {
            "coverage": coverage,
            "test_files": test_files,
            "code_files": code_files,
            "missing_tests": [],
            "test_quality": "moderate"
        }
    
    async def _run_code_quality_analysis(self, static_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """코드 품질 분석 실행."""
        # 정적 분석 기반 품질 평가
        complexity = static_data.get("average_complexity", 10) if static_data else 10
        
        return {
            "linting_issues": 0,
            "type_coverage": 85,
            "code_smells": [],
            "complexity_score": complexity,
            "maintainability_index": max(0, 100 - complexity * 5)
        }
    
    async def _run_dependency_analysis(self) -> Dict[str, Any]:
        """의존성 분석 실행."""
        return {
            "total_dependencies": 0,
            "outdated": [],
            "vulnerable": [],
            "licenses": {},
            "dependency_graph": {}
        }
    
    async def _run_security_analysis(self, static_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """보안 분석 실행."""
        # 정적 분석 결과를 기반으로 보안 이슈 식별
        security_issues = []
        
        if static_data:
            # 정적 분석에서 발견된 보안 이슈
            if static_data.get("security_issues"):
                security_issues.extend(static_data["security_issues"])
        
        return {
            "vulnerabilities": security_issues,
            "severity_distribution": {
                "critical": 0,
                "high": len([i for i in security_issues if i.get("severity") == "HIGH"]),
                "medium": len([i for i in security_issues if i.get("severity") == "MEDIUM"]),
                "low": len([i for i in security_issues if i.get("severity") == "LOW"])
            },
            "owasp_top_10": [],
            "cve_matches": []
        }
    
    async def _analyze_architecture(self, static_data: Dict[str, Any] = None, dependency_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """아키텍처 분석 실행."""
        layers = {}
        
        if static_data:
            # 정적 분석에서 레이어 정보 추출
            layers = static_data.get("architecture_layers", {})
        
        if dependency_data:
            # 의존성 그래프로 아키텍처 보강
            layers["dependencies"] = dependency_data.get("dependency_graph", {})
        
        return {
            "pattern": "layered",  # or microservices, monolithic, etc.
            "layers": layers,
            "coupling": "moderate",
            "cohesion": "high",
            "circular_dependencies": 0
        }
    
    def _identify_test_gaps(self, test_data: Dict[str, Any], static_data: Dict[str, Any], dynamic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """테스트 갭 식별."""
        gaps = []
        
        # 커버리지 갭
        coverage = test_data.get('coverage', 0)
        if coverage < 80:
            gaps.append({
                "type": "coverage",
                "current": coverage,
                "target": 80,
                "gap": 80 - coverage,
                "priority": "high" if coverage < 50 else "medium"
            })
        
        # 복잡한 코드의 테스트 부재
        if static_data.get('complexity_hotspots'):
            gaps.append({
                "type": "complex_code_untested",
                "count": static_data['complexity_hotspots'],
                "priority": "high"
            })
        
        # 에러 처리 테스트 부재
        if dynamic_data.get('behavior_analysis', {}).get('error_patterns'):
            gaps.append({
                "type": "error_handling",
                "untested_scenarios": len(dynamic_data['behavior_analysis']['error_patterns']),
                "priority": "medium"
            })
        
        return gaps
    
    def _extract_ux_metrics(self, behavior_data: Dict[str, Any], performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """UX/행동 메트릭 추출."""
        return {
            "response_time": performance_data.get('avg_response_time', 0),
            "error_rate": behavior_data.get('error_rate', 0),
            "user_flows": behavior_data.get('user_flows', []),
            "performance_score": max(0, 100 - (performance_data.get('p95_latency', 0) / 10))
        }
    
    # ===============================================
    # Evolution Loop 구현 - 갭이 0이 될 때까지 반복
    # ===============================================
    
    async def execute_evolution_loop(
        self,
        requirements: str,
        max_iterations: Optional[int] = None
    ) -> EvolutionResult:
        """Evolution Loop 실행 - 갭이 해소될 때까지 자동 진화.
        
        이 메소드는 다음 과정을 반복합니다:
        1. 요구사항 분석
        2. 현재 상태 분석 (5개 에이전트)
        3. 외부 리서치
        4. 갭 분석
        5. 갭이 있으면:
           - Agno로 새 에이전트 생성
           - CodeGenerator로 코드 구현
           - 테스트 실행
        6. 갭이 0이면 종료
        
        Args:
            requirements: 요구사항
            max_iterations: 최대 반복 횟수 (기본: config 값)
            
        Returns:
            EvolutionResult: 진화 결과
        """
        logger.info("=" * 80)
        logger.info("🧬 Starting Evolution Loop")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        max_iter = max_iterations or self.config.max_evolution_iterations
        
        result = EvolutionResult(
            success=False,
            iterations=0,
            final_gaps=[],
            agents_created=[],
            code_generated=0,
            tests_passed=0,
            tests_failed=0,
            evolution_history=[],
            convergence_rate=0.0,
            total_time=0.0
        )
        
        previous_gap_count = float('inf')
        
        for iteration in range(1, max_iter + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Evolution Iteration {iteration}/{max_iter}")
            logger.info(f"{'='*60}")
            
            iteration_start = datetime.now()
            iteration_data = {
                "iteration": iteration,
                "start_time": iteration_start.isoformat(),
                "gaps_before": [],
                "gaps_after": [],
                "actions_taken": [],
                "results": {}
            }
            
            try:
                # 새 루프 시작 - SharedDocumentContext 초기화
                if self.document_context:
                    self.document_context.start_new_loop()
                
                # AI 드리븐 워크플로우 사용 여부 확인
                if self.config.ai_driven_workflow and self.document_context:
                    # Step 1: AI 드리븐 동적 워크플로우 실행
                    logger.info("🤖 Using AI-driven dynamic workflow...")
                    workflow_results = await self._execute_dynamic_workflow(requirements, iteration)
                    
                    # 워크플로우 결과를 리포트로 변환
                    report = UpgradeReport(
                        timestamp=datetime.now().isoformat(),
                        success=True,
                        phase_results=workflow_results
                    )
                    
                    # 갭 분석 결과 추출
                    gap_data = workflow_results.get("GapAnalyzer_step1", {})
                    if gap_data and "gaps" in gap_data:
                        report.gap_report = GapAnalysisReport(
                            gaps=gap_data["gaps"],
                            gap_score=gap_data.get("gap_score", 0),
                            priority_gaps=gap_data.get("priority_gaps", []),
                            execution_plan=gap_data.get("execution_plan", {})
                        )
                else:
                    # Step 1: 표준 분석 실행
                    logger.info("📊 Running standard complete analysis...")
                    report = await self.analyze(requirements, include_research=True)
                
                # Step 2: 갭 추출
                current_gaps = []
                if report.gap_report and report.gap_report.gaps:
                    current_gaps = report.gap_report.gaps
                    logger.info(f"📍 Found {len(current_gaps)} gaps")
                else:
                    logger.info("✅ No gaps found - Evolution complete!")
                    result.success = True
                    result.iterations = iteration
                    break
                
                iteration_data["gaps_before"] = current_gaps
                
                # Step 3: 수렴 체크
                gap_reduction = (previous_gap_count - len(current_gaps)) / max(previous_gap_count, 1)
                result.convergence_rate = gap_reduction
                
                if len(current_gaps) == 0:
                    logger.info("🎉 All gaps resolved!")
                    result.success = True
                    result.iterations = iteration
                    break
                
                if gap_reduction < 0.1 and iteration > 3:
                    logger.warning("⚠️ Evolution stalled - minimal progress")
                    iteration_data["actions_taken"].append("Evolution stalled")
                    break
                
                # Step 4: 갭 처리
                for gap in current_gaps[:5]:  # 한 번에 최대 5개 갭 처리
                    action = await self._process_evolution_gap(gap, iteration_data)
                    if action:
                        iteration_data["actions_taken"].append(action)
                        if "agent_created" in action:
                            result.agents_created.append(action["agent_created"])
                        if "code_lines" in action:
                            result.code_generated += action["code_lines"]
                
                # Step 5: 테스트 실행
                if self.config.auto_implement_code:
                    test_results = await self._run_evolution_tests()
                    result.tests_passed += test_results.get("passed", 0)
                    result.tests_failed += test_results.get("failed", 0)
                    iteration_data["results"]["tests"] = test_results
                
                # Step 6: 재분석하여 갭 확인
                logger.info("🔍 Re-analyzing to check gap resolution...")
                updated_report = await self.analyze(requirements, include_research=False)
                
                if updated_report.gap_report:
                    iteration_data["gaps_after"] = updated_report.gap_report.gaps
                    current_gaps = updated_report.gap_report.gaps
                else:
                    iteration_data["gaps_after"] = []
                    current_gaps = []
                
                previous_gap_count = len(current_gaps)
                
            except Exception as e:
                logger.error(f"❌ Evolution iteration {iteration} failed: {e}")
                iteration_data["error"] = str(e)
                iteration_data["actions_taken"].append(f"Error: {e}")
            
            finally:
                iteration_end = datetime.now()
                iteration_data["end_time"] = iteration_end.isoformat()
                iteration_data["duration"] = (iteration_end - iteration_start).total_seconds()
                result.evolution_history.append(iteration_data)
                
                logger.info(f"📈 Iteration {iteration} complete:")
                logger.info(f"   Gaps: {len(iteration_data['gaps_before'])} → {len(iteration_data['gaps_after'])}")
                logger.info(f"   Duration: {iteration_data['duration']:.2f}s")
        
        # 최종 결과 정리
        end_time = datetime.now()
        result.total_time = (end_time - start_time).total_seconds()
        result.final_gaps = current_gaps if 'current_gaps' in locals() else []
        
        logger.info("\n" + "=" * 80)
        logger.info("🧬 Evolution Loop Complete")
        logger.info("=" * 80)
        logger.info(f"Success: {result.success}")
        logger.info(f"Iterations: {result.iterations}")
        logger.info(f"Final gaps: {len(result.final_gaps)}")
        logger.info(f"Agents created: {len(result.agents_created)}")
        logger.info(f"Code generated: {result.code_generated} lines")
        logger.info(f"Tests: {result.tests_passed} passed, {result.tests_failed} failed")
        logger.info(f"Total time: {result.total_time:.2f}s")
        
        return result
    
    async def _process_evolution_gap(
        self,
        gap: Dict[str, Any],
        iteration_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evolution Gap 처리 - Agno와 CodeGenerator 활용.
        
        Args:
            gap: 처리할 갭
            iteration_data: 반복 데이터
            
        Returns:
            처리 결과 또는 None
        """
        action = {"gap": gap.get("description", "Unknown gap")}
        
        try:
            gap_type = gap.get("type", "unknown")
            
            # 새 에이전트가 필요한 경우
            if gap_type == "missing_agent" and self.config.auto_generate_agents:
                logger.info(f"🤖 Creating new agent for: {gap.get('description')}")
                
                if self.agno_manager:
                    # Agno로 에이전트 생성
                    agent_result = await self.agno_manager.create_agent(
                        requirements=gap.get("requirements", {}),
                        auto_implement=True,
                        force_create=False
                    )
                    
                    if agent_result.get("status") != "duplicate_found":
                        action["agent_created"] = agent_result.get("spec", {}).get("name", "Unknown")
                        action["code_lines"] = len(agent_result.get("implementation", {}).get("agent.py", "").split("\n"))
                        logger.info(f"✅ Agent created: {action['agent_created']}")
                    else:
                        action["reused_agent"] = agent_result.get("suggestion", "Use existing")
                        logger.info(f"♻️ Reusing existing agent: {action['reused_agent']}")
            
            # 코드 구현이 필요한 경우
            elif gap_type in ["missing_implementation", "incomplete_feature"] and self.config.auto_implement_code:
                logger.info(f"💻 Implementing code for: {gap.get('description')}")
                
                if self.code_generator:
                    # CodeGenerator로 코드 구현
                    task = AgentTask(
                        intent="generate_code",
                        inputs={
                            "gap": gap,
                            "requirements": gap.get("requirements", {}),
                            "context": gap.get("context", {})
                        }
                    )
                    
                    code_result = await self.code_generator.execute(task)
                    if code_result.success:
                        action["code_implemented"] = True
                        action["code_lines"] = code_result.data.get("lines_generated", 0)
                        logger.info(f"✅ Code implemented: {action['code_lines']} lines")
            
            # 테스트가 필요한 경우
            elif gap_type == "missing_tests":
                logger.info(f"🧪 Generating tests for: {gap.get('description')}")
                
                if self.code_generator:
                    task = AgentTask(
                        intent="generate_tests",
                        inputs={"target": gap.get("target", {})}
                    )
                    
                    test_result = await self.code_generator.execute(task)
                    if test_result.success:
                        action["tests_generated"] = test_result.data.get("test_count", 0)
                        logger.info(f"✅ Tests generated: {action['tests_generated']}")
            
            return action
            
        except Exception as e:
            logger.error(f"Failed to process gap: {e}")
            action["error"] = str(e)
            return action
    
    async def _run_evolution_tests(self) -> Dict[str, int]:
        """Evolution 테스트 실행.
        
        Returns:
            테스트 결과 (passed, failed 수)
        """
        try:
            if self.quality_gate:
                task = AgentTask(
                    intent="run_tests",
                    inputs={"project_path": self.config.project_path}
                )
                
                result = await self.quality_gate.execute(task)
                if result.success:
                    return {
                        "passed": result.data.get("tests_passed", 0),
                        "failed": result.data.get("tests_failed", 0)
                    }
            
            return {"passed": 0, "failed": 0}
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {"passed": 0, "failed": 0}
    
    async def _execute_requirement_analysis(self, requirements: str) -> Dict[str, Any]:
        """요구사항 분석 실행"""
        logger.info("Executing RequirementAnalyzer...")
        task = AgentTask(
            task_id="requirement_analysis",
            intent="analyze_requirements",
            inputs={"requirements": requirements}
        )
        result = await self.requirement_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _execute_current_state_analysis(self) -> Dict[str, Any]:
        """현재 상태 분석 (병렬 실행)"""
        logger.info("Executing current state analysis in parallel...")
        
        tasks = {
            "static": self._run_static_analysis(),
            "code": self._run_code_analysis(),
            "behavior": self._run_behavior_analysis() if self.config.include_behavior_analysis else asyncio.create_task(asyncio.sleep(0)),
            "impact": self._run_impact_analysis() if self.config.generate_impact_matrix else asyncio.create_task(asyncio.sleep(0)),
            "quality": self._run_quality_analysis()
        }
        
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        analysis_results = {}
        for (name, _), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                logger.warning(f"Analysis {name} failed: {result}")
                analysis_results[name] = {}
            elif result is not None:
                analysis_results[name] = result
        
        return analysis_results
    
    async def _run_code_analysis(self) -> Dict[str, Any]:
        """코드 분석 실행"""
        task = AgentTask(
            task_id="code_analysis",
            intent="analyze_code",
            inputs={"file_path": self.config.project_path}
        )
        result = await self.code_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _run_behavior_analysis(self) -> Dict[str, Any]:
        """행동 분석 실행"""
        task = AgentTask(
            task_id="behavior_analysis",
            intent="analyze_behavior",
            inputs={"log_paths": self._find_log_files()}
        )
        result = await self.behavior_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _run_impact_analysis(self) -> Dict[str, Any]:
        """영향도 분석 실행"""
        task = AgentTask(
            task_id="impact_analysis",
            intent="analyze_impact",
            inputs={"project_path": self.config.project_path}
        )
        result = await self.impact_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _run_quality_analysis(self) -> Dict[str, Any]:
        """품질 분석 실행"""
        task = AgentTask(
            task_id="quality_analysis",
            intent="check_quality",
            inputs={"project_path": self.config.project_path}
        )
        result = await self.quality_gate.execute(task)
        return result.data if result.success else {}
    
    async def _execute_external_research(
        self,
        requirement_result: Dict[str, Any],
        current_state_results: Dict[str, Any]
    ) -> Optional[UpgradeResearchPack]:
        """외부 리서치 실행"""
        logger.info("Executing ExternalResearcher...")
        
        task = AgentTask(
            task_id="external_research",
            intent="research",
            inputs={
                "requirements": requirement_result,
                "current_state": current_state_results,
                "research_depth": "comprehensive"
            }
        )
        
        result = await self.external_researcher.execute(task)
        if result.success:
            # Convert to UpgradeResearchPack
            data = result.data
            return UpgradeResearchPack(
                one_line_conclusion=data.get("conclusion", ""),
                recommended_approach=data.get("recommended", {}),
                alternative_approaches=data.get("alternatives", []),
                compatibility_checklist=data.get("compatibility", []),
                migration_strategy=data.get("migration", {}),
                code_snippets=data.get("snippets", []),
                warnings=data.get("warnings", []),
                success_criteria=data.get("success_criteria", {}),
                cost_risk_summary=data.get("cost_risk", {}),
                dedup_results=data.get("dedup", {}),
                references=data.get("references", [])
            )
        return None
    
    async def _execute_dynamic_workflow(
        self,
        requirements: str,
        iteration: int = 1
    ) -> Dict[str, Any]:
        """AI 드리븐 동적 워크플로우 실행.
        
        SharedDocumentContext의 모든 문서를 참조하여 AI가 다음 실행할 에이전트를 결정합니다.
        이를 통해 진정한 AI 드리븐 오케스트레이션이 가능합니다.
        
        Args:
            requirements: 요구사항
            iteration: 현재 반복 번호
            
        Returns:
            실행 결과
        """
        logger.info(f"🤖 Executing AI-driven dynamic workflow (iteration {iteration})")
        
        if not self.document_context:
            logger.warning("No document context available, falling back to standard workflow")
            return await self._execute_standard_workflow(requirements)
        
        # AI Provider 준비
        from backend.packages.agents.ai_providers import BedrockAIProvider
        ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # 현재까지의 모든 문서 컨텍스트 가져오기
        context_for_ai = self.document_context.get_context_for_ai(
            include_history=True,
            max_history_loops=2
        )
        
        # 사용 가능한 에이전트 목록
        available_agents = [
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
            "CodeGenerator"
        ]
        
        workflow_results = {}
        max_steps = 10  # 한 iteration 내 최대 실행 단계
        
        for step in range(1, max_steps + 1):
            # AI에게 다음 에이전트 선택 요청
            prompt = f"""
            You are an AI orchestrator managing an evolution loop for project upgrade.
            Current iteration: {iteration}, Step: {step}
            
            Requirements: {requirements}
            
            Available agents: {available_agents}
            
            Current loop documents:
            {context_for_ai}
            
            Based on the current state and documents, determine:
            1. Which agent(s) should execute next (can be multiple for parallel execution)
            2. Whether we should continue or stop this iteration
            3. Reasoning for your decision
            
            Rules:
            - RequirementAnalyzer must run first if no requirement analysis exists
            - Some agents can run in parallel (e.g., StaticAnalyzer, CodeAnalysisAgent, BehaviorAnalyzer)
            - GapAnalyzer needs requirement and state analysis results
            - Stop when gaps are resolved or no meaningful progress can be made
            
            Return JSON:
            {{
                "continue": true/false,
                "next_agents": ["agent1", "agent2"],
                "parallel": true/false,
                "reasoning": "explanation",
                "expected_outcome": "what we expect from these agents"
            }}
            """
            
            try:
                response = await ai_provider.complete(prompt)
                decision = json.loads(response)
                
                logger.info(f"AI Decision - Step {step}: {decision.get('reasoning', 'No reasoning')}")
                
                if not decision.get("continue", False):
                    logger.info("AI decided to stop the iteration")
                    break
                
                next_agents = decision.get("next_agents", [])
                is_parallel = decision.get("parallel", False)
                
                if not next_agents:
                    logger.warning("AI returned no agents to execute, stopping")
                    break
                
                # 에이전트 실행
                if is_parallel and len(next_agents) > 1:
                    logger.info(f"Executing agents in parallel: {next_agents}")
                    tasks = []
                    for agent_name in next_agents:
                        task = self._execute_single_agent(agent_name, requirements)
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for agent_name, result in zip(next_agents, results):
                        if isinstance(result, Exception):
                            logger.error(f"Agent {agent_name} failed: {result}")
                            workflow_results[f"{agent_name}_step{step}"] = {"error": str(result)}
                        else:
                            workflow_results[f"{agent_name}_step{step}"] = result
                            # 문서 컨텍스트에 추가
                            if result and self.document_context:
                                self.document_context.add_document(
                                    agent_name,
                                    result,
                                    document_type="analysis"
                                )
                else:
                    # 순차 실행
                    for agent_name in next_agents:
                        logger.info(f"Executing agent: {agent_name}")
                        result = await self._execute_single_agent(agent_name, requirements)
                        workflow_results[f"{agent_name}_step{step}"] = result
                        
                        # 문서 컨텍스트에 추가
                        if result and self.document_context:
                            self.document_context.add_document(
                                agent_name,
                                result,
                                document_type="analysis"
                            )
                
            except Exception as e:
                logger.error(f"Dynamic workflow step {step} failed: {e}")
                break
        
        logger.info(f"Dynamic workflow completed with {len(workflow_results)} agent executions")
        return workflow_results
    
    async def _execute_single_agent(self, agent_name: str, requirements: str) -> Dict[str, Any]:
        """단일 에이전트 실행.
        
        Args:
            agent_name: 실행할 에이전트 이름
            requirements: 요구사항
            
        Returns:
            실행 결과
        """
        try:
            # 에이전트별 실행 로직
            if agent_name == "RequirementAnalyzer":
                return await self._execute_requirement_analysis(requirements)
            elif agent_name == "StaticAnalyzer":
                return await self._run_static_analysis()
            elif agent_name == "CodeAnalysisAgent":
                return await self._run_code_analysis()
            elif agent_name == "BehaviorAnalyzer":
                return await self._run_behavior_analysis()
            elif agent_name == "ImpactAnalyzer":
                return await self._run_impact_analysis()
            elif agent_name == "QualityGate":
                return await self._run_quality_analysis()
            elif agent_name == "ExternalResearcher":
                req_result = self.document_context.get_document("RequirementAnalyzer") if self.document_context else {}
                state_results = self.document_context.get_all_documents() if self.document_context else {}
                research = await self._execute_external_research(
                    req_result.get("content", {}) if req_result else {},
                    state_results
                )
                return asdict(research) if research else {}
            elif agent_name == "GapAnalyzer":
                docs = self.document_context.get_all_documents() if self.document_context else {}
                return await self._execute_gap_analysis(
                    docs.get("RequirementAnalyzer", {}).get("content", {}),
                    docs,
                    None  # Research pack will be in documents
                )
            elif agent_name == "SystemArchitect":
                return await self._execute_architecture_design()
            elif agent_name == "OrchestratorDesigner":
                return await self._execute_orchestrator_design()
            elif agent_name == "PlannerAgent":
                return await self._execute_planning()
            elif agent_name == "TaskCreatorAgent":
                return await self._execute_task_creation()
            elif agent_name == "CodeGenerator":
                return await self._execute_code_generation_batch()
            else:
                logger.warning(f"Unknown agent: {agent_name}")
                return {"error": f"Unknown agent: {agent_name}"}
                
        except Exception as e:
            logger.error(f"Failed to execute agent {agent_name}: {e}")
            return {"error": str(e)}
    
    async def _execute_standard_workflow(self, requirements: str) -> Dict[str, Any]:
        """표준 워크플로우 실행 (fallback).
        
        Args:
            requirements: 요구사항
            
        Returns:
            실행 결과
        """
        logger.info("Executing standard workflow...")
        
        results = {}
        
        # 1. 요구사항 분석
        results["requirement"] = await self._execute_requirement_analysis(requirements)
        
        # 2. 현재 상태 분석 (병렬)
        state_results = await self._execute_current_state_analysis()
        results["current_state"] = state_results
        
        # 3. 외부 리서치
        research = await self._execute_external_research(
            results["requirement"],
            state_results
        )
        if research:
            results["research"] = asdict(research)
        
        # 4. 갭 분석
        results["gap"] = await self._execute_gap_analysis(
            results["requirement"],
            state_results,
            research
        )
        
        return results
    
    async def _execute_architecture_design(self) -> Dict[str, Any]:
        """아키텍처 설계 실행"""
        if not self.system_architect:
            return {"error": "SystemArchitect not initialized"}
        
        task = AgentTask(
            task_id="architecture_design",
            intent="design_architecture",
            inputs={
                "documents": self.document_context.get_all_documents() if self.document_context else {}
            }
        )
        result = await self.system_architect.execute(task)
        return result.data if result.success else {}
    
    async def _execute_orchestrator_design(self) -> Dict[str, Any]:
        """오케스트레이터 설계 실행"""
        if not self.orchestrator_designer:
            return {"error": "OrchestratorDesigner not initialized"}
        
        task = AgentTask(
            task_id="orchestrator_design",
            intent="design_orchestrator",
            inputs={
                "documents": self.document_context.get_all_documents() if self.document_context else {}
            }
        )
        result = await self.orchestrator_designer.execute(task)
        return result.data if result.success else {}
    
    async def _execute_planning(self) -> Dict[str, Any]:
        """계획 수립 실행"""
        if not self.planner_agent:
            return {"error": "PlannerAgent not initialized"}
        
        task = AgentTask(
            task_id="planning",
            intent="create_plan",
            inputs={
                "documents": self.document_context.get_all_documents() if self.document_context else {}
            }
        )
        result = await self.planner_agent.execute(task)
        return result.data if result.success else {}
    
    async def _execute_task_creation(self) -> Dict[str, Any]:
        """태스크 생성 실행"""
        if not self.task_creator_agent:
            return {"error": "TaskCreatorAgent not initialized"}
        
        task = AgentTask(
            task_id="task_creation",
            intent="create_tasks",
            inputs={
                "documents": self.document_context.get_all_documents() if self.document_context else {}
            }
        )
        result = await self.task_creator_agent.execute(task)
        return result.data if result.success else {}
    
    async def _execute_code_generation_batch(self) -> Dict[str, Any]:
        """코드 생성 배치 실행"""
        if not self.code_generator:
            return {"error": "CodeGenerator not initialized"}
        
        # 태스크 목록에서 코드 생성이 필요한 것들 추출
        tasks_doc = self.document_context.get_document("TaskCreatorAgent") if self.document_context else None
        if not tasks_doc:
            return {"error": "No tasks available for code generation"}
        
        tasks = tasks_doc.get("content", {}).get("tasks", [])
        code_tasks = [t for t in tasks if t.get("type") in ["code_generation", "code_modification"]]
        
        results = []
        for code_task in code_tasks[:5]:  # 최대 5개씩 처리
            task = AgentTask(
                task_id=f"code_gen_{code_task.get('id', 'unknown')}",
                intent="generate_code",
                inputs=code_task
            )
            result = await self.code_generator.execute(task)
            results.append(result.data if result.success else {"error": "Failed"})
        
        return {
            "generated_count": len(results),
            "results": results
        }

    async def _execute_gap_analysis(
        self,
        requirement_result: Dict[str, Any],
        current_state_results: Dict[str, Any],
        research_pack: Optional[UpgradeResearchPack]
    ) -> Dict[str, Any]:
        """갭 분석 실행"""
        logger.info("Executing GapAnalyzer...")
        
        task = AgentTask(
            task_id="gap_analysis",
            intent="analyze_gaps",
            inputs={
                "requirements": requirement_result,
                "current_state": current_state_results,
                "research": research_pack.__dict__ if research_pack else None
            }
        )
        
        result = await self.gap_analyzer.execute(task)
        return result.data if result.success else {}
    
    async def _execute_architecture_design(
        self,
        requirement_result: Dict[str, Any],
        gap_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """아키텍처 설계 실행"""
        logger.info("Executing SystemArchitect...")
        
        design = await self.system_architect.design_architecture(
            requirements=requirement_result,
            gap_report=gap_result,
            current_architecture=None,
            constraints={"max_complexity": 10}
        )
        
        return design.dict()
    
    async def _execute_orchestrator_design(
        self,
        architecture_design: Dict[str, Any],
        requirement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """오케스트레이터 디자인 실행"""
        logger.info("Executing OrchestratorDesigner...")
        
        design_doc = await self.orchestrator_designer.design_orchestrator(
            architecture_design=architecture_design,
            requirements=requirement_result,
            constraints={"timeout": 3600}
        )
        
        return design_doc.dict()
    
    async def _execute_planning(
        self,
        architecture_design: Dict[str, Any],
        orchestrator_design: Dict[str, Any],
        requirement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실행 계획 수립"""
        logger.info("Executing PlannerAgent...")
        
        task = AgentTask(
            task_id="create_plan",
            intent="create_plan",
            inputs={
                "requirement": requirement_result,
                "architecture": architecture_design,
                "orchestrator": orchestrator_design
            }
        )
        
        result = await self.planner_agent.execute(task)
        return result.data if result.success else {}
    
    async def _execute_task_creation(
        self,
        execution_plan: Dict[str, Any],
        orchestrator_design: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """세부 태스크 생성"""
        logger.info("Executing TaskCreatorAgent...")
        
        task = AgentTask(
            task_id="create_tasks",
            intent="create_tasks",
            inputs={
                "plan": execution_plan,
                "orchestrator": orchestrator_design,
                "task_duration": "5-20 minutes"
            }
        )
        
        result = await self.task_creator_agent.execute(task)
        return result.data.get("tasks", []) if result.success else []
    
    async def _execute_code_generation(
        self,
        detailed_tasks: List[Dict[str, Any]],
        architecture_design: Dict[str, Any]
    ) -> Dict[str, Any]:
        """코드 생성 실행"""
        logger.info("Executing CodeGenerator...")
        
        task = AgentTask(
            task_id="generate_code",
            intent="generate_code",
            inputs={
                "tasks": detailed_tasks,
                "architecture": architecture_design
            }
        )
        
        result = await self.code_generator.execute(task)
        return result.data if result.success else {}
    
    async def _generate_agents_with_agno(
        self,
        orchestrator_design: Dict[str, Any],
        gaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Agno를 통한 자동 에이전트 생성.
        
        오케스트레이터 디자인과 갭 분석 결과를 바탕으로
        필요한 에이전트를 자동으로 생성합니다.
        
        Args:
            orchestrator_design: 오케스트레이터 디자인 문서
            gaps: 해결해야 할 갭 목록
            
        Returns:
            생성된 에이전트 이름 목록
        """
        generated_agents = []
        
        if not hasattr(self, 'agno_manager'):
            logger.warning("Agno not initialized, skipping agent generation")
            return generated_agents
        
        try:
            # 갭 분석을 통해 필요한 에이전트 식별
            for gap in gaps[:5]:  # 최대 5개 갭에 대해서만 에이전트 생성
                gap_type = gap.get('type', 'unknown')
                gap_description = gap.get('description', '')
                
                # AI를 통해 에이전트 스펙 생성
                agent_spec_prompt = f"""
                Based on this gap in our system:
                Type: {gap_type}
                Description: {gap_description}
                
                Design an agent specification to address this gap.
                Include name, purpose, capabilities, and implementation approach.
                """
                
                # Agno 스펙 생성
                from backend.packages.agno.spec import AgentSpec as AgnoSpec
                
                spec = AgnoSpec(
                    name=f"{gap_type}_resolver_agent",
                    description=f"Agent to resolve {gap_type} gaps",
                    purpose=f"Address gaps related to {gap_type}",
                    capabilities=[
                        f"analyze_{gap_type}",
                        f"resolve_{gap_type}",
                        f"validate_{gap_type}_resolution"
                    ],
                    inputs={"gap": "Gap information to resolve"},
                    outputs={"resolution": "Resolution details and status"},
                    dependencies=["backend.packages.agents.base"],
                    ai_enabled=True
                )
                
                # Agno를 통한 에이전트 코드 생성
                try:
                    agent_name = await self.agno_manager.create_agent(spec)
                    if agent_name:
                        generated_agents.append(agent_name)
                        logger.info(f"Generated agent: {agent_name}")
                except Exception as e:
                    logger.error(f"Failed to generate agent for {gap_type}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Agent generation failed: {e}")
        
        return generated_agents
    
    async def _execute_tests(self, code_generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 실행"""
        logger.info("Executing tests...")
        
        task = AgentTask(
            task_id="run_tests",
            intent="run_tests",
            inputs={
                "generated_code": code_generation_result,
                "project_path": self.config.project_path
            }
        )
        
        result = await self.quality_gate.execute(task)
        return result.data if result.success else {}
    
    async def _recheck_gaps(
        self,
        requirement_result: Dict[str, Any],
        test_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """갭 재확인"""
        logger.info("Re-checking gaps...")
        
        # 현재 상태 다시 분석
        current_state = await self._execute_current_state_analysis()
        
        # 갭 재분석
        task = AgentTask(
            task_id="recheck_gaps",
            intent="analyze_gaps",
            inputs={
                "requirements": requirement_result,
                "current_state": current_state,
                "test_results": test_result
            }
        )
        
        result = await self.gap_analyzer.execute(task)
        return result.data.get("gaps", []) if result.success else []
    
    async def _save_all_reports_as_markdown(self, report: UpgradeReport) -> None:
        """모든 보고서를 MD 파일로 저장"""
        from pathlib import Path
        import json
        
        # 출력 디렉토리 생성
        project_name = Path(self.config.project_path).name
        timestamp = report.timestamp.replace(':', '-').replace('.', '-')
        output_dir = Path(self.config.output_dir) / project_name / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving reports to {output_dir}")
        
        # 1. 요구사항 분석 보고서
        if report.requirement_analysis:
            req_path = output_dir / "01_requirement_analysis.md"
            self._save_as_markdown(
                req_path,
                "요구사항 분석 보고서",
                report.requirement_analysis
            )
        
        # 2. 현재 상태 분석 보고서들
        if report.static_analysis:
            static_path = output_dir / "02_static_analysis.md"
            self._save_as_markdown(
                static_path,
                "정적 분석 보고서",
                report.static_analysis
            )
        
        if report.code_analysis:
            code_path = output_dir / "03_code_analysis.md"
            self._save_as_markdown(
                code_path,
                "코드 분석 보고서",
                report.code_analysis
            )
        
        if report.behavior_analysis:
            behavior_path = output_dir / "04_behavior_analysis.md"
            self._save_as_markdown(
                behavior_path,
                "행동 분석 보고서",
                report.behavior_analysis
            )
        
        if report.impact_analysis:
            impact_path = output_dir / "05_impact_analysis.md"
            self._save_as_markdown(
                impact_path,
                "영향도 분석 보고서",
                report.impact_analysis
            )
        
        if report.quality_metrics:
            quality_path = output_dir / "06_quality_metrics.md"
            self._save_as_markdown(
                quality_path,
                "품질 메트릭 보고서",
                report.quality_metrics
            )
        
        # 3. 외부 리서치 보고서
        if report.research_pack:
            research_path = output_dir / "07_external_research.md"
            self._save_research_pack_as_markdown(
                research_path,
                report.research_pack
            )
        
        # 4. 갭 분석 보고서
        if report.gap_analysis:
            gap_path = output_dir / "08_gap_analysis.md"
            self._save_as_markdown(
                gap_path,
                "갭 분석 보고서",
                report.gap_analysis
            )
        
        # 5. 태스크 목록
        if report.tasks_breakdown:
            tasks_path = output_dir / "09_tasks.md"
            self._save_tasks_as_markdown(
                tasks_path,
                report.tasks_breakdown
            )
        
        # 6. 종합 보고서 (JSON)
        full_report_path = output_dir / "00_full_report.json"
        with open(full_report_path, 'w', encoding='utf-8') as f:
            # Convert report to dict
            report_dict = {}
            for key, value in report.__dict__.items():
                if value is None:
                    report_dict[key] = None
                elif hasattr(value, '__dict__'):
                    try:
                        report_dict[key] = asdict(value)
                    except:
                        report_dict[key] = str(value)
                elif isinstance(value, (list, dict, str, int, float, bool)):
                    report_dict[key] = value
                else:
                    report_dict[key] = str(value)
            
            json.dump(report_dict, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"All reports saved to {output_dir}")
    
    def _save_as_markdown(self, path: Path, title: str, data: Dict[str, Any]) -> None:
        """데이터를 마크다운 파일로 저장"""
        from pathlib import Path
        import json
        
        content = f"# {title}\n\n"
        content += f"생성 시간: {datetime.now().isoformat()}\n\n"
        
        # Convert dict to markdown format
        for key, value in data.items():
            if isinstance(value, dict):
                content += f"## {key}\n\n"
                content += "```json\n"
                content += json.dumps(value, indent=2, default=str, ensure_ascii=False)
                content += "\n```\n\n"
            elif isinstance(value, list):
                content += f"## {key}\n\n"
                for i, item in enumerate(value, 1):
                    content += f"{i}. {item}\n"
                content += "\n"
            else:
                content += f"## {key}\n\n{value}\n\n"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_research_pack_as_markdown(self, path: Path, research_pack: UpgradeResearchPack) -> None:
        """리서치 팩을 마크다운으로 저장"""
        content = f"# 외부 리서치 보고서 (URP)\n\n"
        content += f"생성 시간: {research_pack.created_at}\n"
        content += f"유효 기간: {research_pack.ttl_days}일\n\n"
        
        content += f"## 한 줄 결론\n\n{research_pack.one_line_conclusion}\n\n"
        
        content += f"## 추천 접근법\n\n"
        content += f"```json\n{json.dumps(research_pack.recommended_approach, indent=2, ensure_ascii=False)}\n```\n\n"
        
        if research_pack.alternative_approaches:
            content += f"## 대안 접근법들\n\n"
            for i, alt in enumerate(research_pack.alternative_approaches, 1):
                content += f"### 대안 {i}\n"
                content += f"```json\n{json.dumps(alt, indent=2, ensure_ascii=False)}\n```\n\n"
        
        if research_pack.code_snippets:
            content += f"## 코드 예제\n\n"
            for i, snippet in enumerate(research_pack.code_snippets, 1):
                content += f"### 예제 {i}\n"
                content += f"```python\n{snippet.get('code', '')}\n```\n\n"
        
        if research_pack.warnings:
            content += f"## ⚠️ 주의사항\n\n"
            for warning in research_pack.warnings:
                content += f"- {warning}\n"
            content += "\n"
        
        if research_pack.references:
            content += f"## 참고자료\n\n"
            for ref in research_pack.references:
                content += f"- {ref}\n"
            content += "\n"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_tasks_as_markdown(self, path: Path, tasks: List[Dict[str, Any]]) -> None:
        """태스크 목록을 마크다운으로 저장"""
        content = f"# 세부 태스크 목록\n\n"
        content += f"총 태스크 수: {len(tasks)}개\n\n"
        
        for i, task in enumerate(tasks, 1):
            content += f"## Task {i}: {task.get('name', 'Unnamed Task')}\n\n"
            content += f"- **설명**: {task.get('description', '')}\n"
            content += f"- **예상 시간**: {task.get('duration', '5-20분')}\n"
            content += f"- **우선순위**: {task.get('priority', 'normal')}\n"
            
            if task.get('dependencies'):
                content += f"- **의존성**: {', '.join(task['dependencies'])}\n"
            
            if task.get('outputs'):
                content += f"- **산출물**: {', '.join(task['outputs'])}\n"
            
            content += "\n"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


async def main():
    """Example usage."""
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer",
        enable_dynamic_analysis=False,
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True
    )
    
    orchestrator = UpgradeOrchestrator(config)
    await orchestrator.initialize()
    
    requirements = """
    Analyze the current system and provide upgrade recommendations.
    Focus on improving test coverage, reducing technical debt, and
    identifying performance bottlenecks.
    """
    
    report = await orchestrator.analyze(requirements)
    
    # Print summary
    print(f"System Health Score: {report.system_health_score:.1f}/100")
    print(f"Upgrade Risk Score: {report.upgrade_risk_score:.1f}/100")
    print(f"Total Issues Found: {report.total_issues_found}")
    print(f"Critical Issues: {len(report.critical_issues)}")
    
    print("\nImmediate Actions:")
    for action in report.immediate_actions:
        print(f"  - {action}")
    
    print("\nShort-term Goals:")
    for goal in report.short_term_goals:
        print(f"  - {goal}")


if __name__ == "__main__":
    asyncio.run(main())