"""시스템 아키텍트 에이전트 (SystemArchitect)

이 에이전트는 요구사항과 갭 분석을 바탕으로 전체 시스템 아키텍처를 설계하고
진화시키는 역할을 합니다. 필요한 에이전트와 오케스트레이터를 결정하고,
에이전트 간의 상호작용과 데이터 플로우를 설계합니다.

주요 기능:
1. 초기 아키텍처 설계
   - 필요한 에이전트 식별 및 역할 정의
   - 오케스트레이터 패턴 선택
   - 데이터 플로우 설계
   
2. 아키텍처 진화/변경
   - 새로운 요구사항에 따른 아키텍처 수정
   - 에이전트 추가/제거/수정 결정
   - 오케스트레이터 패턴 변경
   
3. 아키텍처 최적화
   - 병목 지점 해결
   - 병렬화 전략
   - 리소스 최적화

입력:
- requirements (Dict): 요구사항 분석 결과
- gap_report (Dict): 갭 분석 보고서
- current_architecture (Dict, optional): 현재 아키텍처 (변경 시)
- metrics (Dict, optional): 성능 메트릭 (최적화 시)

출력:
- ArchitectureDesign: 아키텍처 설계
  - agents: 필요한 에이전트 목록
    * name: 에이전트 이름
    * role: 역할과 책임
    * inputs: 입력 스키마
    * outputs: 출력 스키마
    * dependencies: 의존 에이전트
  - orchestrator: 오케스트레이터 설계
    * type: Sequential/Parallel/Hybrid/EventDriven
    * flow: 실행 플로우
    * error_handling: 에러 처리 전략
  - data_flow: 데이터 플로우 매핑
  - integration_points: 통합 지점
  - scalability_plan: 확장성 계획
  - evolution_strategy: 진화 전략

문서 참조 관계:
- 입력 참조:
  * RequirementAnalyzer 보고서: 요구사항 이해
  * GapAnalyzer 보고서: 해결해야 할 갭
  * ExternalResearcher 보고서: 베스트 프랙티스
- 출력 참조:
  * PlannerAgent: 아키텍처 기반 구현 계획
  * Agno: 에이전트 생성 명세
  * CodeGenerator: 오케스트레이터 구현

오케스트레이터 패턴:
- SEQUENTIAL: 순차 실행 (단계별 의존성)
- PARALLEL: 병렬 실행 (독립적 작업)
- HYBRID: 혼합 패턴 (일부 병렬, 일부 순차)
- EVENT_DRIVEN: 이벤트 기반 (비동기 처리)
- PIPELINE: 파이프라인 (스트리밍 처리)
- MAP_REDUCE: 맵리듀스 (대규모 데이터 처리)

아키텍처 결정 기준:
- COMPLEXITY: 요구사항 복잡도
- PERFORMANCE: 성능 요구사항
- SCALABILITY: 확장성 요구사항
- RELIABILITY: 신뢰성 요구사항
- MAINTAINABILITY: 유지보수성
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)
from .ai_providers import BedrockAIProvider
from ..memory import MemoryHub, ContextType


class OrchestratorType(str, Enum):
    """오케스트레이터 타입"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    EVENT_DRIVEN = "event_driven"
    PIPELINE = "pipeline"
    MAP_REDUCE = "map_reduce"


class AgentDesign(BaseModel):
    """에이전트 설계"""
    name: str = Field(..., description="에이전트 이름")
    role: str = Field(..., description="역할과 책임")
    capability: str = Field(..., description="주요 능력")
    inputs: List[Dict[str, Any]] = Field(default_factory=list, description="입력 스키마")
    outputs: List[Dict[str, Any]] = Field(default_factory=list, description="출력 스키마")
    dependencies: List[str] = Field(default_factory=list, description="의존 에이전트")
    priority: int = Field(default=0, description="우선순위")
    is_new: bool = Field(default=True, description="새로 생성 필요 여부")
    modifications: Optional[str] = Field(None, description="기존 에이전트 수정사항")


class OrchestratorDesign(BaseModel):
    """오케스트레이터 설계"""
    type: OrchestratorType = Field(..., description="오케스트레이터 타입")
    flow: List[Dict[str, Any]] = Field(..., description="실행 플로우")
    parallel_groups: List[List[str]] = Field(default_factory=list, description="병렬 실행 그룹")
    error_handling: Dict[str, str] = Field(default_factory=dict, description="에러 처리 전략")
    timeout_strategy: Dict[str, int] = Field(default_factory=dict, description="타임아웃 전략")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="재시도 정책")


class DataFlow(BaseModel):
    """데이터 플로우"""
    source: str = Field(..., description="데이터 소스")
    destination: str = Field(..., description="데이터 목적지")
    transform: Optional[str] = Field(None, description="변환 로직")
    validation: Optional[str] = Field(None, description="검증 로직")


class ArchitectureDesign(BaseModel):
    """아키텍처 설계"""
    version: str = Field(default="1.0.0", description="설계 버전")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # 핵심 설계
    agents: List[AgentDesign] = Field(..., description="에이전트 설계")
    orchestrator: OrchestratorDesign = Field(..., description="오케스트레이터 설계")
    data_flows: List[DataFlow] = Field(..., description="데이터 플로우")
    
    # 통합 및 확장
    integration_points: List[Dict[str, Any]] = Field(default_factory=list)
    scalability_plan: Dict[str, Any] = Field(default_factory=dict)
    evolution_strategy: Dict[str, Any] = Field(default_factory=dict)
    
    # 메타데이터
    rationale: str = Field(..., description="설계 근거")
    trade_offs: List[str] = Field(default_factory=list, description="트레이드오프")
    risks: List[Dict[str, Any]] = Field(default_factory=list, description="위험 요소")
    estimated_complexity: int = Field(default=5, description="예상 복잡도 (1-10)")


class SystemArchitect(BaseAgent):
    """시스템 아키텍트 에이전트"""
    
    def __init__(self, memory_hub: Optional[MemoryHub] = None, document_context=None):
        super().__init__(
            name="SystemArchitect",
            memory_hub=memory_hub,
            document_context=document_context
        )
        self.role = "System Architecture Designer"
        self.capabilities = ["design", "analyze", "optimize"]

        
        # 페르소나 적용 - SystemArchitect
        from .personas import get_persona
        self.persona = get_persona("SystemArchitect")
        if self.persona:
            logger.info(f"🎭 {self.persona.name}: {self.persona.catchphrase}")
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet"  # MODELS 딕셔너리의 키 사용
        )
    
    async def design_architecture(
        self,
        requirements: Dict[str, Any],
        gap_report: Dict[str, Any],
        current_architecture: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> ArchitectureDesign:
        """초기 아키텍처 설계 또는 재설계
        
        Args:
            requirements: 요구사항 분석 결과
            gap_report: 갭 분석 보고서
            current_architecture: 현재 아키텍처 (변경 시)
            constraints: 제약사항
            
        Returns:
            ArchitectureDesign: 아키텍처 설계
        """
        # 설계 프롬프트 생성
        prompt = self._create_design_prompt(
            requirements, gap_report, current_architecture, constraints
        )
        
        # AI를 통한 아키텍처 설계
        response = await self.ai_provider.complete(prompt)
        
        # 설계 파싱 및 검증
        design = self._parse_architecture_design(response)
        
        # 메모리에 저장 (메모리 허브가 있는 경우만)
        if self.memory_hub:
            await self._store_design_in_memory(design)
        
        return design
    
    async def evolve_architecture(
        self,
        current_architecture: Dict[str, Any],
        new_requirements: Dict[str, Any],
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> ArchitectureDesign:
        """아키텍처 진화/변경
        
        Args:
            current_architecture: 현재 아키텍처
            new_requirements: 새로운 요구사항
            performance_metrics: 성능 메트릭
            
        Returns:
            ArchitectureDesign: 진화된 아키텍처
        """
        # 변경 필요성 분석
        changes_needed = await self._analyze_changes_needed(
            current_architecture, new_requirements, performance_metrics
        )
        
        # 진화 전략 수립
        evolution_strategy = await self._create_evolution_strategy(changes_needed)
        
        # 새로운 아키텍처 설계
        evolved_design = await self._apply_evolution(
            current_architecture, evolution_strategy
        )
        
        return evolved_design
    
    async def optimize_architecture(
        self,
        current_architecture: Dict[str, Any],
        metrics: Dict[str, Any],
        optimization_goals: List[str]
    ) -> ArchitectureDesign:
        """아키텍처 최적화
        
        Args:
            current_architecture: 현재 아키텍처
            metrics: 성능 메트릭
            optimization_goals: 최적화 목표
            
        Returns:
            ArchitectureDesign: 최적화된 아키텍처
        """
        # 병목 지점 분석
        bottlenecks = await self._identify_bottlenecks(metrics)
        
        # 최적화 전략 수립
        optimization_plan = await self._create_optimization_plan(
            bottlenecks, optimization_goals
        )
        
        # 최적화 적용
        optimized_design = await self._apply_optimizations(
            current_architecture, optimization_plan
        )
        
        return optimized_design
    
    def _create_design_prompt(
        self,
        requirements: Dict[str, Any],
        gap_report: Dict[str, Any],
        current_architecture: Optional[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """아키텍처 설계 프롬프트 생성"""
        
        mode = "redesign" if current_architecture else "design"
        
        prompt = f"""
        You are a System Architect designing a {mode} for T-Developer v2.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Gap Analysis:
        {json.dumps(gap_report, indent=2)}
        
        {"Current Architecture:" if current_architecture else ""}
        {json.dumps(current_architecture, indent=2) if current_architecture else ""}
        
        Constraints:
        {json.dumps(constraints or {}, indent=2)}
        
        Please design an architecture that:
        1. Identifies all necessary agents and their roles
        2. Selects the appropriate orchestrator pattern
        3. Defines data flow between components
        4. Considers scalability and evolution
        5. Minimizes complexity while meeting requirements
        
        Provide the design in the following JSON format:
        {{
            "agents": [
                {{
                    "name": "AgentName",
                    "role": "What this agent does",
                    "capability": "primary capability",
                    "inputs": ["input1", "input2"],
                    "outputs": ["output1"],
                    "dependencies": ["OtherAgent"],
                    "is_new": true,
                    "priority": 1
                }}
            ],
            "orchestrator": {{
                "type": "sequential|parallel|hybrid|event_driven",
                "flow": [
                    {{"step": 1, "agent": "Agent1", "parallel": false}},
                    {{"step": 2, "agents": ["Agent2", "Agent3"], "parallel": true}}
                ],
                "error_handling": {{
                    "strategy": "retry|fallback|circuit_breaker",
                    "max_retries": 3
                }}
            }},
            "data_flows": [
                {{
                    "source": "Agent1",
                    "destination": "Agent2",
                    "transform": "optional transformation"
                }}
            ],
            "rationale": "Why this design",
            "trade_offs": ["trade off 1", "trade off 2"],
            "estimated_complexity": 5
        }}
        """
        
        return prompt
    
    def _parse_architecture_design(self, response: str) -> ArchitectureDesign:
        """AI 응답을 아키텍처 설계로 파싱"""
        try:
            # JSON 추출
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                design_dict = json.loads(json_match.group())
            else:
                # Fallback to basic design
                design_dict = self._create_fallback_design()
            
            # ArchitectureDesign 객체 생성
            return ArchitectureDesign(
                agents=[AgentDesign(**agent) for agent in design_dict.get("agents", [])],
                orchestrator=OrchestratorDesign(**design_dict.get("orchestrator", {})),
                data_flows=[DataFlow(**flow) for flow in design_dict.get("data_flows", [])],
                rationale=design_dict.get("rationale", ""),
                trade_offs=design_dict.get("trade_offs", []),
                estimated_complexity=design_dict.get("estimated_complexity", 5)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse architecture design: {e}")
            return self._create_fallback_design()
    
    def _create_fallback_design(self) -> ArchitectureDesign:
        """폴백 아키텍처 설계"""
        return ArchitectureDesign(
            agents=[
                AgentDesign(
                    name="DefaultAnalyzer",
                    role="Analyze requirements",
                    capability="analyze",
                    is_new=True
                )
            ],
            orchestrator=OrchestratorDesign(
                type=OrchestratorType.SEQUENTIAL,
                flow=[{"step": 1, "agent": "DefaultAnalyzer"}]
            ),
            data_flows=[],
            rationale="Fallback design due to parsing error"
        )
    
    async def _store_design_in_memory(self, design: ArchitectureDesign):
        """설계를 메모리에 저장"""
        await self.memory_hub.store(
            key=f"architecture_design_{design.version}",
            value=design.dict(),
            context_type=ContextType.SHARED,
            tags=["architecture", "design", "system"]
        )
    
    async def _analyze_changes_needed(
        self,
        current: Dict[str, Any],
        new_reqs: Dict[str, Any],
        metrics: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """필요한 변경사항 분석"""
        # 구현 예정
        return {
            "add_agents": [],
            "remove_agents": [],
            "modify_agents": [],
            "change_orchestrator": False
        }
    
    async def _create_evolution_strategy(
        self,
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진화 전략 수립"""
        # 구현 예정
        return {
            "strategy": "incremental",
            "phases": []
        }
    
    async def _apply_evolution(
        self,
        current: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> ArchitectureDesign:
        """진화 적용"""
        # 구현 예정
        return self._create_fallback_design()
    
    async def _identify_bottlenecks(
        self,
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """병목 지점 식별"""
        # 구현 예정
        return []
    
    async def _create_optimization_plan(
        self,
        bottlenecks: List[Dict[str, Any]],
        goals: List[str]
    ) -> Dict[str, Any]:
        """최적화 계획 수립"""
        # 구현 예정
        return {}
    
    async def _apply_optimizations(
        self,
        current: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> ArchitectureDesign:
        """최적화 적용"""
        # 구현 예정
        return self._create_fallback_design()
    
    async def execute(self, task) -> Dict[str, Any]:
        """에이전트 실행"""
        # task가 AgentTask인 경우 inputs 추출
        if hasattr(task, 'inputs'):
            inputs = task.inputs
        elif isinstance(task, dict):
            inputs = task
        else:
            inputs = {}
        
        mode = inputs.get("mode", "design")
        
        if mode == "design":
            design = await self.design_architecture(
                requirements=inputs.get("requirements", {}),
                gap_report=inputs.get("gap_report", {}),
                current_architecture=inputs.get("current_architecture"),
                constraints=inputs.get("constraints")
            )
        elif mode == "evolve":
            design = await self.evolve_architecture(
                current_architecture=inputs.get("current_architecture", {}),
                new_requirements=inputs.get("new_requirements", {}),
                performance_metrics=inputs.get("performance_metrics")
            )
        elif mode == "optimize":
            design = await self.optimize_architecture(
                current_architecture=inputs.get("current_architecture", {}),
                metrics=inputs.get("metrics", {}),
                optimization_goals=inputs.get("optimization_goals", [])
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        return {
            "architecture_design": design.dict(),
            "summary": f"Designed architecture with {len(design.agents)} agents using {design.orchestrator.type} orchestrator",
            "next_steps": [
                "Review and approve design",
                "Create implementation plan",
                "Generate agents with Agno",
                "Implement orchestrator"
            ]
        }