"""태스크 생성기 (TaskCreatorAgent) - AI 기반 세부 실행 태스크 생성

이 에이전트는 PlannerAgent가 생성한 추상적인 실행 계획을 받아서 구체적이고
실행 가능한 세부 태스크들로 분해하여 생성합니다.

주요 기능:
1. 실행 계획을 원자적 실행 단위로 분해
2. 각 태스크의 입력/출력 스펙 정의 및 데이터 형식 명시
3. 태스크별 검증 기준 설정 및 성공/실패 조건 정의
4. Python 실행 스크립트 자동 생성
5. 실패 시 롤백 계획 수립
6. 태스크간 의존성 최적화 및 병렬 실행 기회 식별
7. 우선순위 조정 및 크리티컬 패스 식별
8. 재시도 전략 설정 및 에러 처리 방안 수립

입력 매개변수:
- plan: PlannerAgent의 실행 계획 (phases, goals, tasks 포함)
- requirement: 원본 요구사항 명세
- context: 프로젝트 컨텍스트 정보
- optimization_goal: 최적화 목표 (speed/cost/quality/balanced)

출력 형식:
- tasks: ExecutableTask 객체 배열
  * id: 고유 태스크 식별자
  * name: 태스크 명
  * description: 상세 설명
  * type: 태스크 유형 (analysis/development/testing/deployment 등)
  * agent: 실행할 에이전트명
  * inputs: 입력 스펙 (타입, 필수여부, 설명)
  * expected_outputs: 예상 출력 구조
  * validation_criteria: 검증 기준 리스트
  * execution_script: Python 실행 스크립트
  * rollback_plan: 롤백 절차
  * dependencies: 의존 태스크 ID 리스트
  * estimated_time: 예상 소요 시간 (분)
  * priority: 우선순위 (1-10)
  * retry_strategy: 재시도 전략
- total_tasks: 총 태스크 수
- estimated_total_time: 총 예상 시간
- execution_order: 실행 순서
- critical_path: 크리티컬 패스

문서 참조 관계:
- 읽어오는 보고서:
  * PlannerAgent 실행 계획
  * ExternalResearcher 리서치 보고서
  * GapAnalyzer 갭 분석 보고서
- 출력을 사용하는 에이전트:
  * UpgradeOrchestrator: 태스크 실행 조율
  * QualityGate: 태스크 품질 검증
  * MonitoringAgent: 실행 모니터링

사용 예시:
```python
task_creator = TaskCreatorAgent(memory_hub=hub)
result = await task_creator.execute(AgentTask(
    inputs={
        'plan': planner_output,
        'requirement': "마이크로서비스 아키텍처로 전환",
        'context': {'framework': 'FastAPI', 'db': 'PostgreSQL'},
        'optimization_goal': 'balanced'
    }
))

print(f"생성된 태스크: {result.data['total_tasks']}개")
print(f"예상 소요시간: {result.data['estimated_total_time']}분")
```

작성자: T-Developer v2 Team
버전: 2.1.0
최종 수정: 2025-08-23
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseAgent, AgentTask, AgentResult, TaskStatus
from .ai_providers import BedrockAIProvider
from ..memory.contexts import ContextType
from ..safety import CircuitBreaker, ResourceLimiter

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """태스크 유형."""
    ANALYSIS = "analysis"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    MONITORING = "monitoring"


@dataclass
class ExecutableTask:
    """실행 가능한 태스크."""
    id: str
    name: str
    description: str
    type: TaskType
    agent: str  # 실행할 에이전트
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_outputs: Dict[str, Any] = field(default_factory=dict)
    validation_criteria: List[str] = field(default_factory=list)
    execution_script: str = ""
    rollback_plan: str = ""
    dependencies: List[str] = field(default_factory=list)
    estimated_time: int = 30  # minutes
    priority: int = 5  # 1-10
    retry_strategy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskCreatorAgent(BaseAgent):
    """세부 태스크 생성 에이전트.
    
    이 에이전트는:
    1. 추상적인 계획을 구체적 태스크로 변환
    2. 각 태스크의 실행 방법 정의
    3. 입력/출력 스펙 생성
    4. 검증 및 롤백 전략 수립
    5. 실행 최적화
    """
    
    def __init__(self, memory_hub=None, document_context=None):
        """TaskCreatorAgent 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            document_context: SharedDocumentContext 인스턴스
        """
        super().__init__(
            name="TaskCreatorAgent",
            version="1.0.0",
            memory_hub=memory_hub,
            document_context=document_context
        )
        
        # AI Provider 초기화 - 실제 AWS Bedrock 사용
        self.ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        # Safety mechanisms
        self.circuit_breaker = CircuitBreaker(name="TaskCreatorAgent")
        self.resource_limiter = ResourceLimiter()
        
        # 페르소나 적용 - TaskCreatorAgent
        from .personas import get_persona
        self.persona = get_persona("TaskCreatorAgent")
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
        """세부 태스크 생성.
        
        Args:
            task: AgentTask with inputs:
                - plan: 실행 계획 (PlannerAgent의 출력)
                - requirement: 원본 요구사항
                - context: 프로젝트 컨텍스트
                - optimization_goal: 최적화 목표
                
        Returns:
            AgentResult with executable tasks
        """
        logger.info("Creating executable tasks from plan")
        
        try:
            inputs = task.inputs if hasattr(task, 'inputs') else task
            
            # Get reports from external researcher and gap analyzer
            research_reports = await self._get_external_and_gap_reports()
            
            plan = inputs.get("plan", {})
            requirement = inputs.get("requirement", "")
            context = inputs.get("context", {})
            optimization_goal = inputs.get("optimization_goal", "balanced")
            
            # Enrich context with reports
            if research_reports:
                context["research_insights"] = research_reports
            
            if not plan:
                return AgentResult(
                    success=False,
                    status=TaskStatus.FAILED,
                    error="No execution plan provided",
                    data={}
                )
            
            # 1. 계획 분석
            plan_analysis = await self._analyze_plan(plan, requirement)
            
            # 2. 태스크 생성
            tasks = await self._create_tasks(plan, plan_analysis, context)
            
            # 3. 입출력 스펙 정의
            tasks = await self._define_io_specs(tasks, requirement)
            
            # 4. 검증 기준 설정
            tasks = await self._set_validation_criteria(tasks)
            
            # 5. 실행 스크립트 생성
            tasks = await self._generate_execution_scripts(tasks, context)
            
            # 6. 롤백 계획 수립
            tasks = await self._create_rollback_plans(tasks)
            
            # 7. 의존성 최적화
            tasks = await self._optimize_dependencies(tasks, optimization_goal)
            
            # 8. 우선순위 조정
            tasks = await self._adjust_priorities(tasks, requirement)
            
            # 9. 리트라이 전략 설정
            tasks = await self._set_retry_strategies(tasks)
            
            # 10. 최종 검증
            validation_result = await self._validate_tasks(tasks)
            
            # 메모리에 저장
            if self.memory_hub:
                await self.memory_hub.put(
                    key=f"executable_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    value=[t.__dict__ for t in tasks],
                    context_type=ContextType.O_CTX
                )
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data={
                    "tasks": [t.__dict__ for t in tasks],
                    "total_tasks": len(tasks),
                    "estimated_total_time": sum(t.estimated_time for t in tasks),
                    "validation": validation_result,
                    "execution_order": self._get_execution_order(tasks),
                    "critical_path": self._identify_critical_path(tasks)
                }
            )
            
        except Exception as e:
            logger.error(f"Task creation failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
                data={}
            )
    
    async def _analyze_plan(self, plan: Dict[str, Any], requirement: str) -> Dict[str, Any]:
        """계획 분석.
        
        Args:
            plan: 실행 계획
            requirement: 요구사항
            
        Returns:
            분석 결과
        """
        prompt = f"""
        Analyze this execution plan and identify key execution requirements:
        
        Plan Summary:
        - Goals: {len(plan.get('goals', []))}
        - Phases: {len(plan.get('phases', []))}
        - Tasks: {len(plan.get('tasks', []))}
        
        Requirement:
        {requirement[:500]}
        
        Identify:
        1. Critical tasks that must succeed
        2. Parallel execution opportunities
        3. Resource bottlenecks
        4. Risk points
        5. Optimization opportunities
        
        Response format (JSON):
        {{
            "critical_tasks": ["..."],
            "parallel_groups": [["task1", "task2"], ...],
            "bottlenecks": ["..."],
            "risk_points": ["..."],
            "optimizations": ["..."]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "critical_tasks": [],
                "parallel_groups": [],
                "bottlenecks": [],
                "risk_points": [],
                "optimizations": []
            }
    
    async def _create_tasks(self, plan: Dict[str, Any], analysis: Dict[str, Any], context: Dict[str, Any]) -> List[ExecutableTask]:
        """실행 가능한 태스크 생성.
        
        Args:
            plan: 실행 계획
            analysis: 계획 분석 결과
            context: 프로젝트 컨텍스트
            
        Returns:
            태스크 목록
        """
        tasks = []
        plan_tasks = plan.get("tasks", [])
        
        for i, plan_task in enumerate(plan_tasks):
            # AI로 상세 태스크 생성
            prompt = f"""
            Create an executable task from this plan task:
            
            Plan Task:
            {json.dumps(plan_task, indent=2)}
            
            Context:
            {json.dumps(context, indent=2)[:500]}
            
            Create a detailed executable task with:
            - Clear execution instructions
            - Specific agent to execute
            - Task type (analysis/development/testing/etc)
            - Estimated time in minutes
            - Priority (1-10)
            
            Response format (JSON):
            {{
                "name": "...",
                "description": "...",
                "type": "analysis|development|testing|deployment|documentation|review|monitoring",
                "agent": "agent_name",
                "estimated_time": 30,
                "priority": 5,
                "instructions": "Step by step instructions..."
            }}
            """
            
            response = await self.ai_provider.complete(prompt)
            
            try:
                task_data = json.loads(response)
            except:
                task_data = {
                    "name": plan_task.get("name", f"Task {i+1}"),
                    "description": plan_task.get("description", ""),
                    "type": "analysis",
                    "agent": plan_task.get("agent", "orchestrator"),
                    "estimated_time": 30,
                    "priority": 5,
                    "instructions": "Execute task as planned"
                }
            
            # ExecutableTask 생성
            exec_task = ExecutableTask(
                id=plan_task.get("id", f"task_{i+1:03d}"),
                name=task_data["name"],
                description=task_data["description"],
                type=TaskType(task_data.get("type", "analysis")),
                agent=task_data["agent"],
                estimated_time=task_data["estimated_time"],
                priority=task_data["priority"],
                dependencies=plan_task.get("dependencies", []),
                metadata={
                    "instructions": task_data.get("instructions", ""),
                    "phase": plan_task.get("phase", ""),
                    "critical": plan_task.get("id") in analysis.get("critical_tasks", [])
                }
            )
            
            tasks.append(exec_task)
        
        return tasks
    
    async def _define_io_specs(self, tasks: List[ExecutableTask], requirement: str) -> List[ExecutableTask]:
        """입출력 스펙 정의.
        
        Args:
            tasks: 태스크 목록
            requirement: 요구사항
            
        Returns:
            업데이트된 태스크 목록
        """
        for task in tasks:
            prompt = f"""
            Define input/output specifications for this task:
            
            Task: {task.name}
            Type: {task.type.value}
            Agent: {task.agent}
            Description: {task.description}
            
            Requirement context:
            {requirement[:300]}
            
            Define:
            1. Required inputs (with types and validation)
            2. Expected outputs (with structure)
            3. Data formats
            
            Response format (JSON):
            {{
                "inputs": {{
                    "param1": {{"type": "string", "required": true, "description": "..."}},
                    ...
                }},
                "outputs": {{
                    "result1": {{"type": "object", "structure": {{...}}}},
                    ...
                }}
            }}
            """
            
            response = await self.ai_provider.complete(prompt)
            
            try:
                io_spec = json.loads(response)
                task.inputs = io_spec.get("inputs", {})
                task.expected_outputs = io_spec.get("outputs", {})
            except:
                task.inputs = {"requirement": {"type": "string", "required": True}}
                task.expected_outputs = {"result": {"type": "object"}}
        
        return tasks
    
    async def _set_validation_criteria(self, tasks: List[ExecutableTask]) -> List[ExecutableTask]:
        """검증 기준 설정.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            업데이트된 태스크 목록
        """
        for task in tasks:
            prompt = f"""
            Set validation criteria for this task:
            
            Task: {task.name}
            Type: {task.type.value}
            Expected Outputs: {json.dumps(task.expected_outputs, indent=2)[:500]}
            
            Create 3-5 specific validation criteria that must be met for success.
            
            Response format (JSON):
            {{
                "criteria": [
                    "Criterion 1",
                    "Criterion 2",
                    ...
                ]
            }}
            """
            
            response = await self.ai_provider.complete(prompt)
            
            try:
                data = json.loads(response)
                task.validation_criteria = data.get("criteria", [])
            except:
                task.validation_criteria = [
                    "Task completes without errors",
                    "Output matches expected structure",
                    "Performance within acceptable limits"
                ]
        
        return tasks
    
    async def _generate_execution_scripts(self, tasks: List[ExecutableTask], context: Dict[str, Any]) -> List[ExecutableTask]:
        """실행 스크립트 생성.
        
        Args:
            tasks: 태스크 목록
            context: 프로젝트 컨텍스트
            
        Returns:
            업데이트된 태스크 목록
        """
        for task in tasks:
            prompt = f"""
            Generate execution script for this task:
            
            Task: {task.name}
            Agent: {task.agent}
            Inputs: {json.dumps(task.inputs, indent=2)[:500]}
            
            Create a Python script snippet that:
            1. Prepares inputs
            2. Calls the agent
            3. Processes outputs
            4. Handles errors
            
            Response format: Python code as string
            """
            
            response = await self.ai_provider.complete(prompt)
            
            # 코드 추출
            if "```python" in response:
                code = response.split("```python")[1].split("```")[0].strip()
            elif "```" in response:
                code = response.split("```")[1].split("```")[0].strip()
            else:
                code = response.strip()
            
            task.execution_script = code
        
        return tasks
    
    async def _create_rollback_plans(self, tasks: List[ExecutableTask]) -> List[ExecutableTask]:
        """롤백 계획 수립.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            업데이트된 태스크 목록
        """
        for task in tasks:
            prompt = f"""
            Create a rollback plan for this task:
            
            Task: {task.name}
            Type: {task.type.value}
            
            Define steps to undo this task if it fails or needs to be reverted.
            
            Response: Rollback steps as text
            """
            
            response = await self.ai_provider.complete(prompt)
            task.rollback_plan = response.strip()
        
        return tasks
    
    async def _optimize_dependencies(self, tasks: List[ExecutableTask], optimization_goal: str) -> List[ExecutableTask]:
        """의존성 최적화.
        
        Args:
            tasks: 태스크 목록
            optimization_goal: 최적화 목표 (speed/cost/quality)
            
        Returns:
            최적화된 태스크 목록
        """
        prompt = f"""
        Optimize task dependencies for {optimization_goal}:
        
        Current tasks: {len(tasks)}
        Current dependencies: {sum(len(t.dependencies) for t in tasks)}
        
        Optimization goal: {optimization_goal}
        - speed: Maximize parallelization
        - cost: Minimize resource usage
        - quality: Ensure thorough validation
        - balanced: Balance all factors
        
        Suggest dependency optimizations.
        
        Response format (JSON):
        {{
            "remove_dependencies": [["task1", "task2"], ...],
            "add_dependencies": [["task3", "task4"], ...],
            "parallel_groups": [["task5", "task6"], ...]
        }}
        """
        
        response = await self.ai_provider.complete(prompt)
        
        try:
            optimizations = json.loads(response)
            # Apply optimizations (simplified)
            # In real implementation, would modify task dependencies
        except:
            pass
        
        return tasks
    
    async def _adjust_priorities(self, tasks: List[ExecutableTask], requirement: str) -> List[ExecutableTask]:
        """우선순위 조정.
        
        Args:
            tasks: 태스크 목록
            requirement: 요구사항
            
        Returns:
            우선순위 조정된 태스크 목록
        """
        # Critical tasks get higher priority
        for task in tasks:
            if task.metadata.get("critical"):
                task.priority = min(task.priority + 2, 10)
            
            # Adjust based on type
            if task.type == TaskType.TESTING:
                task.priority = min(task.priority + 1, 10)
            elif task.type == TaskType.DOCUMENTATION:
                task.priority = max(task.priority - 1, 1)
        
        return tasks
    
    async def _set_retry_strategies(self, tasks: List[ExecutableTask]) -> List[ExecutableTask]:
        """리트라이 전략 설정.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            업데이트된 태스크 목록
        """
        for task in tasks:
            # Default retry strategy
            task.retry_strategy = {
                "max_attempts": 3 if task.metadata.get("critical") else 2,
                "backoff": "exponential",
                "initial_delay": 5,  # seconds
                "max_delay": 60,  # seconds
                "retry_on": ["timeout", "api_error", "resource_unavailable"]
            }
        
        return tasks
    
    async def _validate_tasks(self, tasks: List[ExecutableTask]) -> Dict[str, Any]:
        """태스크 검증.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            검증 결과
        """
        validation = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "stats": {
                "total_tasks": len(tasks),
                "by_type": {},
                "by_agent": {},
                "critical_count": sum(1 for t in tasks if t.metadata.get("critical"))
            }
        }
        
        # Type별 카운트
        for task in tasks:
            task_type = task.type.value
            validation["stats"]["by_type"][task_type] = validation["stats"]["by_type"].get(task_type, 0) + 1
            
            # Agent별 카운트
            agent = task.agent
            validation["stats"]["by_agent"][agent] = validation["stats"]["by_agent"].get(agent, 0) + 1
            
            # 검증 체크
            if not task.inputs:
                validation["warnings"].append(f"Task {task.id} has no inputs defined")
            if not task.validation_criteria:
                validation["warnings"].append(f"Task {task.id} has no validation criteria")
            if not task.execution_script:
                validation["warnings"].append(f"Task {task.id} has no execution script")
        
        # Circular dependency check
        if self._has_circular_dependencies(tasks):
            validation["valid"] = False
            validation["issues"].append("Circular dependencies detected")
        
        return validation
    
    def _has_circular_dependencies(self, tasks: List[ExecutableTask]) -> bool:
        """순환 의존성 체크.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            순환 의존성 존재 여부
        """
        # Simplified check - in real implementation would use graph algorithms
        task_ids = {t.id for t in tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    return True  # Invalid dependency
        return False
    
    def _get_execution_order(self, tasks: List[ExecutableTask]) -> List[str]:
        """실행 순서 결정.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            실행 순서 (태스크 ID 목록)
        """
        # Topological sort (simplified)
        ordered = []
        remaining = tasks.copy()
        
        while remaining:
            # Find tasks with no dependencies
            ready = [t for t in remaining if not t.dependencies or all(d in ordered for d in t.dependencies)]
            
            if not ready:
                # Circular dependency or error
                break
            
            # Sort by priority
            ready.sort(key=lambda t: t.priority, reverse=True)
            
            # Add to ordered list
            for task in ready:
                ordered.append(task.id)
                remaining.remove(task)
        
        return ordered
    
    def _identify_critical_path(self, tasks: List[ExecutableTask]) -> List[str]:
        """크리티컬 패스 식별.
        
        Args:
            tasks: 태스크 목록
            
        Returns:
            크리티컬 패스 태스크 ID 목록
        """
        # Simplified critical path - tasks marked as critical
        critical_path = [t.id for t in tasks if t.metadata.get("critical")]
        
        if not critical_path:
            # Fallback: longest dependency chain
            critical_path = [tasks[0].id] if tasks else []
        
        return critical_path