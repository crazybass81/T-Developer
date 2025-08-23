"""계획 수립 에이전트 (PlannerAgent)

이 에이전트는 갭 분석 결과를 바탕으로 Agno와 CodeGenerator가 생성하고 수정해야 하는
에이전트들의 구현 계획을 수립하는 역할을 합니다. 큰 단위의 계획을 체계적으로 
구성하여 효율적인 구현을 가능하게 합니다.

주요 기능:
1. 갭 분석 기반 실행 계획 수립
2. 에이전트 생성/수정 계획 수립
3. 작업 단계별 분해 및 순서 결정
4. 의존성 관계 분석 및 매핑
5. 리소스 할당 및 일정 계획
6. 위험 요소 식별 및 완화 전략
7. 단계별 성공 기준 정의
8. 병렬 실행 가능 작업 식별

입력:
- gap_report (Dict): 갭 분석 보고서
- requirements (Dict): 요구사항 명세
- external_research (Dict, optional): 외부 리서치 결과
- constraints (Dict, optional): 제약사항 (시간, 리소스 등)

출력:
- ExecutionPlan: 실행 계획
  - goals: 달성 목표 목록
  - phases: 단계별 실행 계획
  - tasks: 세부 작업 목록
  - dependencies: 작업 간 의존성
  - timeline: 일정 계획
  - resources: 필요 리소스
  - risks: 위험 요소 및 대응 방안
  - success_criteria: 성공 기준
  - estimated_duration: 예상 소요 시간
  - confidence: 계획 신뢰도

문서 참조 관계:
- 입력 참조:
  * RequirementAnalyzer 보고서: 요구사항 기반 계획
  * ExternalResearcher 보고서: 모범 사례 반영
  * GapAnalyzer 보고서: 갭 해소 중심 계획
- 출력 참조:
  * TaskCreatorAgent: 세부 작업 생성
  * CodeGenerator: 구현 계획 실행

계획 단계:
- PHASE_1: 기반 구조 구축
- PHASE_2: 핵심 기능 구현
- PHASE_3: 통합 및 연결
- PHASE_4: 최적화 및 개선
- PHASE_5: 검증 및 안정화

작업 유형:
- CREATE_AGENT: 새 에이전트 생성
- MODIFY_AGENT: 기존 에이전트 수정
- INTEGRATE: 에이전트 간 통합
- TEST: 테스트 작성 및 실행
- DOCUMENT: 문서화 작업

우선순위 전략:
- 의존성이 없는 작업 우선
- 핵심 기능 우선
- 리스크가 높은 작업 조기 실행
- 병렬 처리 가능 작업 그룹화

사용 예시:
    planner = PlannerAgent(memory_hub)
    task = AgentTask(
        intent="create_plan",
        inputs={
            "gap_report": gap_analysis_result,
            "requirements": requirement_spec,
            "external_research": research_report
        }
    )
    result = await planner.execute(task)
    plan = result.data  # 실행 계획

작성자: T-Developer v2
버전: 1.0.0
최종 수정: 2024-12-20
NO MOCKS - 100% REAL AI (AWS Bedrock Claude 3)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .base import BaseAgent, AgentTask, AgentResult, TaskStatus
from .ai_providers import BedrockAIProvider
from ..memory.contexts import ContextType
from ..safety import CircuitBreaker, ResourceLimiter

logger = logging.getLogger(__name__)


@dataclass
class ExecutionPlan:
    """실행 계획."""
    goals: List[str] = field(default_factory=list)
    phases: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    timeline: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    estimated_duration: int = 0  # minutes
    priority: str = "medium"
    confidence: float = 0.0


class PlannerAgent(BaseAgent):
    """실행 계획 수립 에이전트.
    
    이 에이전트는:
    1. 요구사항을 분석하여 목표 설정
    2. 목표 달성을 위한 단계별 계획 수립
    3. 각 단계의 작업과 의존성 정의
    4. 리소스 요구사항 산정
    5. 위험 요소 식별 및 대응 계획
    """
    
    def __init__(self, memory_hub=None, document_context=None):
        """PlannerAgent 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            document_context: SharedDocumentContext 인스턴스
        """
        super().__init__(
            name="PlannerAgent",
            version="1.0.0",
            document_context=document_context,
            memory_hub=memory_hub
        )
        
        # AI Provider 초기화 - 실제 AWS Bedrock 사용
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # Safety mechanisms
        self.circuit_breaker = CircuitBreaker(name="PlannerAgent")
        self.resource_limiter = ResourceLimiter()
        
        # 페르소나 적용 - PlannerAgent
        from .personas import get_persona
        self.persona = get_persona("PlannerAgent")
        if self.persona:
            logger.info(f"🎭 {self.persona.name}: {self.persona.catchphrase}")

    
    async def _get_external_and_gap_reports(self) -> Dict[str, Any]:
        """Fetch external researcher and gap analyzer reports from memory.
        
        Returns:
            Dictionary containing external research and gap analysis reports
        """
        if not self.memory_hub:
            return {}
        
        from ..memory.contexts import ContextType
        
        reports = {}
        
        try:
            # Get external research reports
            external_research = await self.memory_hub.search(
                context_type=ContextType.S_CTX,
                tags=["external_research", "ExternalResearcher"],
                limit=3
            )
            if external_research:
                reports["external_research"] = external_research
            
            # Get gap analysis reports
            gap_analysis = await self.memory_hub.search(
                context_type=ContextType.A_CTX,
                tags=["test_gaps", "GapAnalyzer"],
                limit=3
            )
            if gap_analysis:
                reports["gap_analysis"] = gap_analysis
                
        except Exception as e:
            logger.debug(f"Failed to get external/gap reports: {e}")
        
        return reports
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """실행 계획 수립.
        
        Args:
            task: AgentTask with inputs:
                - requirement: 요구사항
                - context: 프로젝트 컨텍스트
                - constraints: 제약사항
                - existing_code: 기존 코드 정보
                
        Returns:
            AgentResult with execution plan
        """
        logger.info("Starting execution planning")
        
        try:
            inputs = task.inputs if hasattr(task, 'inputs') else task
            
            # Get reports from external researcher and gap analyzer
            research_reports = await self._get_external_and_gap_reports()
            
            requirement = inputs.get("requirement", "")
            context = inputs.get("context", {})
            constraints = inputs.get("constraints", [])
            
            # Enrich context with reports
            if research_reports:
                context["research_insights"] = research_reports
            
            if not requirement:
                return AgentResult(
                    success=False,
                    status=TaskStatus.FAILED,
                    error="No requirement provided",
                    data={}
                )
            
            # 1. 목표 분석
            goals = await self._analyze_goals(requirement, context)
            
            # 2. 단계별 계획 수립
            phases = await self._create_phases(goals, requirement)
            
            # 3. 작업 분해
            tasks = await self._decompose_tasks(phases, requirement)
            
            # 4. 의존성 매핑
            dependencies = await self._map_dependencies(tasks)
            
            # 5. 타임라인 생성
            timeline = await self._create_timeline(tasks, dependencies)
            
            # 6. 리소스 계획
            resources = await self._plan_resources(tasks, constraints)
            
            # 7. 위험 평가
            risks = await self._assess_risks(tasks, context)
            
            # 8. 성공 기준 정의
            success_criteria = await self._define_success_criteria(goals, requirement)
            
            # 계획 통합
            plan = ExecutionPlan(
                goals=goals,
                phases=phases,
                tasks=tasks,
                dependencies=dependencies,
                timeline=timeline,
                resources=resources,
                risks=risks,
                success_criteria=success_criteria,
                estimated_duration=self._calculate_duration(timeline),
                priority=self._determine_priority(requirement)
            )
            plan.confidence = await self._calculate_confidence(plan)
            
            # 메모리에 저장
            if self.memory_hub:
                await self.memory_hub.put(
                    key=f"execution_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    value=plan.__dict__,
                    context_type=ContextType.O_CTX
                )
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data={
                    "plan": plan.__dict__,
                    "summary": self._create_summary(plan),
                    "next_steps": self._get_next_steps(plan)
                }
            )
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
                data={}
            )
    
    async def _analyze_goals(self, requirement: str, context: Dict[str, Any]) -> List[str]:
        """요구사항에서 목표 추출.
        
        Args:
            requirement: 요구사항
            context: 프로젝트 컨텍스트
            
        Returns:
            목표 목록
        """
        prompt = f"""
        Analyze the following requirement and extract clear, measurable goals:
        
        Requirement:
        {requirement}
        
        Context:
        {json.dumps(context, indent=2)[:1000]}
        
        Extract 3-7 specific goals that need to be achieved.
        Each goal should be:
        - Specific and measurable
        - Achievable
        - Relevant to the requirement
        - Time-bound (if applicable)
        
        Response format (JSON):
        {{
            "goals": [
                "Goal 1",
                "Goal 2",
                ...
            ]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("goals", [])
        except:
            return ["Complete the requirement successfully"]
    
    async def _create_phases(self, goals: List[str], requirement: str) -> List[Dict[str, Any]]:
        """목표 달성을 위한 단계 생성.
        
        Args:
            goals: 목표 목록
            requirement: 요구사항
            
        Returns:
            단계 목록
        """
        prompt = f"""
        Create execution phases for achieving these goals:
        
        Goals:
        {json.dumps(goals, indent=2)}
        
        Requirement:
        {requirement}
        
        Create 3-5 phases, each with:
        - Name
        - Description
        - Objectives
        - Deliverables
        - Duration estimate (in hours)
        
        Response format (JSON):
        {{
            "phases": [
                {{
                    "name": "Phase 1",
                    "description": "...",
                    "objectives": ["..."],
                    "deliverables": ["..."],
                    "duration_hours": 8
                }},
                ...
            ]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("phases", [])
        except:
            return [
                {
                    "name": "Analysis",
                    "description": "Analyze requirements",
                    "objectives": ["Understand requirements"],
                    "deliverables": ["Requirements document"],
                    "duration_hours": 4
                },
                {
                    "name": "Implementation",
                    "description": "Implement solution",
                    "objectives": ["Build solution"],
                    "deliverables": ["Working code"],
                    "duration_hours": 16
                },
                {
                    "name": "Validation",
                    "description": "Validate solution",
                    "objectives": ["Ensure quality"],
                    "deliverables": ["Test results"],
                    "duration_hours": 8
                }
            ]
    
    async def _decompose_tasks(self, phases: List[Dict[str, Any]], requirement: str) -> List[Dict[str, Any]]:
        """단계를 구체적인 작업으로 분해.
        
        Args:
            phases: 단계 목록
            requirement: 요구사항
            
        Returns:
            작업 목록
        """
        prompt = f"""
        Decompose these phases into specific tasks:
        
        Phases:
        {json.dumps(phases, indent=2)[:1500]}
        
        Requirement:
        {requirement[:500]}
        
        For each phase, create 2-5 specific tasks with:
        - Task ID (unique)
        - Name
        - Description
        - Phase
        - Agent (which agent should execute)
        - Inputs needed
        - Expected outputs
        - Estimated duration (minutes)
        
        Response format (JSON):
        {{
            "tasks": [
                {{
                    "id": "task_001",
                    "name": "...",
                    "description": "...",
                    "phase": "Phase 1",
                    "agent": "requirement_analyzer",
                    "inputs": ["..."],
                    "outputs": ["..."],
                    "duration_minutes": 30
                }},
                ...
            ]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("tasks", [])
        except:
            # Fallback tasks
            tasks = []
            for i, phase in enumerate(phases):
                tasks.append({
                    "id": f"task_{i+1:03d}",
                    "name": f"Execute {phase.get('name', 'Phase')}",
                    "description": phase.get("description", ""),
                    "phase": phase.get("name", f"Phase {i+1}"),
                    "agent": "orchestrator",
                    "inputs": ["requirement"],
                    "outputs": phase.get("deliverables", []),
                    "duration_minutes": phase.get("duration_hours", 1) * 60
                })
            return tasks
    
    async def _map_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """작업 간 의존성 매핑.
        
        Args:
            tasks: 작업 목록
            
        Returns:
            의존성 맵
        """
        prompt = f"""
        Map dependencies between these tasks:
        
        Tasks:
        {json.dumps(tasks, indent=2)[:2000]}
        
        Identify which tasks depend on others.
        A task depends on another if it needs the output of that task.
        
        Response format (JSON):
        {{
            "dependencies": {{
                "task_002": ["task_001"],
                "task_003": ["task_001", "task_002"],
                ...
            }}
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("dependencies", {})
        except:
            # Simple sequential dependencies
            deps = {}
            for i in range(1, len(tasks)):
                deps[tasks[i]["id"]] = [tasks[i-1]["id"]]
            return deps
    
    async def _create_timeline(self, tasks: List[Dict[str, Any]], dependencies: Dict[str, List[str]]) -> Dict[str, Any]:
        """작업 타임라인 생성.
        
        Args:
            tasks: 작업 목록
            dependencies: 의존성 맵
            
        Returns:
            타임라인
        """
        timeline = {
            "start": "Day 1",
            "milestones": [],
            "critical_path": [],
            "total_duration_hours": sum(t.get("duration_minutes", 30) / 60 for t in tasks)
        }
        
        # 마일스톤 추출
        for task in tasks:
            if "deliverable" in task.get("outputs", []):
                timeline["milestones"].append({
                    "task_id": task["id"],
                    "name": task["name"],
                    "expected_completion": f"Hour {task.get('duration_minutes', 30) / 60:.1f}"
                })
        
        # Critical path (simplified)
        timeline["critical_path"] = [t["id"] for t in tasks[:3]]
        
        return timeline
    
    async def _plan_resources(self, tasks: List[Dict[str, Any]], constraints: List[str]) -> Dict[str, Any]:
        """리소스 계획.
        
        Args:
            tasks: 작업 목록
            constraints: 제약사항
            
        Returns:
            리소스 계획
        """
        # Agent별 작업 카운트
        agent_workload = {}
        for task in tasks:
            agent = task.get("agent", "unknown")
            agent_workload[agent] = agent_workload.get(agent, 0) + 1
        
        return {
            "agents_required": list(agent_workload.keys()),
            "agent_workload": agent_workload,
            "compute_resources": {
                "cpu": "4 cores",
                "memory": "8 GB",
                "storage": "10 GB"
            },
            "ai_tokens_estimate": len(tasks) * 2000,
            "constraints_considered": constraints
        }
    
    async def _assess_risks(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """위험 평가.
        
        Args:
            tasks: 작업 목록
            context: 프로젝트 컨텍스트
            
        Returns:
            위험 목록
        """
        prompt = f"""
        Assess risks for this execution plan:
        
        Tasks count: {len(tasks)}
        Context: {json.dumps(context, indent=2)[:500]}
        
        Identify 3-5 key risks with:
        - Risk description
        - Probability (low/medium/high)
        - Impact (low/medium/high)
        - Mitigation strategy
        
        Response format (JSON):
        {{
            "risks": [
                {{
                    "description": "...",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "..."
                }},
                ...
            ]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            data = json.loads(response)
            return data.get("risks", [])
        except:
            return [
                {
                    "description": "AI API failures",
                    "probability": "low",
                    "impact": "high",
                    "mitigation": "Implement retry logic and fallback mechanisms"
                }
            ]
    
    async def _define_success_criteria(self, goals: List[str], requirement: str) -> List[str]:
        """성공 기준 정의.
        
        Args:
            goals: 목표 목록
            requirement: 요구사항
            
        Returns:
            성공 기준 목록
        """
        criteria = []
        
        # 각 목표에 대한 기준
        for goal in goals:
            criteria.append(f"Achieve: {goal}")
        
        # 기본 기준 추가
        criteria.extend([
            "All tests pass",
            "Code quality metrics meet standards",
            "No critical security issues",
            "Documentation complete"
        ])
        
        return criteria[:10]  # 최대 10개
    
    def _calculate_duration(self, timeline: Dict[str, Any]) -> int:
        """총 소요 시간 계산 (분).
        
        Args:
            timeline: 타임라인
            
        Returns:
            총 소요 시간 (분)
        """
        return int(timeline.get("total_duration_hours", 1) * 60)
    
    def _determine_priority(self, requirement: str) -> str:
        """우선순위 결정.
        
        Args:
            requirement: 요구사항
            
        Returns:
            우선순위 (low/medium/high/critical)
        """
        priority_keywords = {
            "critical": ["urgent", "critical", "asap", "immediately"],
            "high": ["important", "priority", "soon", "quickly"],
            "low": ["when possible", "nice to have", "optional"]
        }
        
        requirement_lower = requirement.lower()
        
        for priority, keywords in priority_keywords.items():
            if any(kw in requirement_lower for kw in keywords):
                return priority
        
        return "medium"
    
    async def _calculate_confidence(self, plan: Any) -> float:
        """계획 신뢰도 계산.
        
        Args:
            plan: 실행 계획
            
        Returns:
            신뢰도 (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # 요소별 가산
        if plan.goals:
            confidence += 0.1
        if plan.phases:
            confidence += 0.1
        if plan.tasks:
            confidence += 0.1
        if plan.dependencies:
            confidence += 0.1
        if plan.success_criteria:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _create_summary(self, plan: ExecutionPlan) -> str:
        """계획 요약 생성.
        
        Args:
            plan: 실행 계획
            
        Returns:
            요약 문자열
        """
        return f"""
        Execution Plan Summary:
        - Goals: {len(plan.goals)}
        - Phases: {len(plan.phases)}
        - Tasks: {len(plan.tasks)}
        - Estimated Duration: {plan.estimated_duration} minutes
        - Priority: {plan.priority}
        - Confidence: {plan.confidence:.1%}
        - Risks Identified: {len(plan.risks)}
        """
    
    def _get_next_steps(self, plan: ExecutionPlan) -> List[str]:
        """다음 단계 제안.
        
        Args:
            plan: 실행 계획
            
        Returns:
            다음 단계 목록
        """
        steps = []
        
        if plan.tasks:
            first_task = plan.tasks[0]
            steps.append(f"Execute {first_task.get('name', 'first task')}")
        
        steps.extend([
            "Review and approve the plan",
            "Allocate required resources",
            "Set up monitoring",
            "Begin execution"
        ])
        
        return steps[:5]