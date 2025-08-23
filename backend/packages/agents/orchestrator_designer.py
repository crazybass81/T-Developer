"""오케스트레이터 디자이너 에이전트 (OrchestratorDesigner)

이 에이전트는 SystemArchitect가 설계한 아키텍처를 바탕으로 실제 오케스트레이터와
에이전트들의 상세 구현 명세를 작성합니다. 각 에이전트의 입출력 스키마, 
오케스트레이터의 실행 플로우, 에러 처리 전략 등을 구체화합니다.

주요 기능:
1. 오케스트레이터 상세 설계
   - 실행 플로우 구체화
   - 조건부 분기 로직
   - 병렬/순차 실행 전략
   - 에러 핸들링 및 롤백
   
2. 에이전트 상세 명세
   - 입출력 스키마 정의
   - 메서드 시그니처
   - 의존성 주입 패턴
   - 테스트 시나리오
   
3. 통합 지점 설계
   - 에이전트 간 데이터 전달
   - 메시지 포맷 정의
   - 타임아웃 및 재시도 정책

입력:
- architecture_design (Dict): SystemArchitect의 아키텍처 설계
- requirements (Dict): 요구사항 분석 결과
- constraints (Dict, optional): 기술적 제약사항

출력:
- OrchestratorSpec: 오케스트레이터 구현 명세
  - execution_flow: 상세 실행 플로우
  - agent_specs: 에이전트별 구현 명세
  - integration_specs: 통합 명세
  - test_scenarios: 테스트 시나리오

문서 참조 관계:
- 입력 참조:
  * SystemArchitect 설계 문서: 전체 아키텍처
  * RequirementAnalyzer 보고서: 기능 요구사항
  * GapAnalyzer 보고서: 구현 갭
- 출력 참조:
  * PlannerAgent: 구현 계획 수립
  * TaskCreatorAgent: 세부 태스크 생성
  * CodeGenerator: 실제 코드 생성
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio

from .base import BaseAgent
from .ai_providers import BedrockAIProvider
from ..memory import MemoryHub, ContextType


class ExecutionStrategy(str, Enum):
    """실행 전략"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PIPELINE = "pipeline"


class RetryStrategy(str, Enum):
    """재시도 전략"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"


class ErrorHandlingStrategy(str, Enum):
    """에러 처리 전략"""
    FAIL_FAST = "fail_fast"
    RETRY_THEN_FAIL = "retry_then_fail"
    RETRY_THEN_SKIP = "retry_then_skip"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"


class AgentMethodSpec(BaseModel):
    """에이전트 메서드 명세"""
    name: str = Field(..., description="메서드 이름")
    description: str = Field(..., description="메서드 설명")
    parameters: List[Dict[str, Any]] = Field(..., description="파라미터 명세")
    return_type: str = Field(..., description="반환 타입")
    is_async: bool = Field(default=True, description="비동기 메서드 여부")
    timeout_seconds: int = Field(default=300, description="타임아웃 시간")


class AgentImplementationSpec(BaseModel):
    """에이전트 구현 명세"""
    name: str = Field(..., description="에이전트 이름")
    class_name: str = Field(..., description="클래스 이름")
    base_class: str = Field(default="BaseAgent", description="베이스 클래스")
    
    # 메서드 명세
    methods: List[AgentMethodSpec] = Field(..., description="메서드 목록")
    
    # 입출력 명세
    input_schema: Dict[str, Any] = Field(..., description="입력 스키마")
    output_schema: Dict[str, Any] = Field(..., description="출력 스키마")
    
    # 의존성
    dependencies: List[str] = Field(default_factory=list, description="의존 에이전트")
    required_services: List[str] = Field(default_factory=list, description="필요 서비스")
    
    # 설정
    config: Dict[str, Any] = Field(default_factory=dict, description="에이전트 설정")
    
    # 테스트
    test_scenarios: List[Dict[str, Any]] = Field(default_factory=list, description="테스트 시나리오")


class ExecutionFlowNode(BaseModel):
    """실행 플로우 노드"""
    id: str = Field(..., description="노드 ID")
    type: ExecutionStrategy = Field(..., description="실행 유형")
    agent: Optional[str] = Field(None, description="실행할 에이전트")
    agents: Optional[List[str]] = Field(None, description="병렬 실행 에이전트들")
    
    # 조건부 실행
    condition: Optional[str] = Field(None, description="실행 조건")
    true_branch: Optional[List['ExecutionFlowNode']] = Field(None, description="True 분기")
    false_branch: Optional[List['ExecutionFlowNode']] = Field(None, description="False 분기")
    
    # 루프
    loop_condition: Optional[str] = Field(None, description="루프 조건")
    max_iterations: Optional[int] = Field(None, description="최대 반복 횟수")
    
    # 에러 처리
    error_handling: ErrorHandlingStrategy = Field(
        default=ErrorHandlingStrategy.RETRY_THEN_FAIL
    )
    retry_strategy: RetryStrategy = Field(default=RetryStrategy.EXPONENTIAL_BACKOFF)
    max_retries: int = Field(default=3)
    
    # 타임아웃
    timeout_seconds: int = Field(default=300)
    
    # 데이터 변환
    input_transform: Optional[str] = Field(None, description="입력 변환 로직")
    output_transform: Optional[str] = Field(None, description="출력 변환 로직")


class OrchestratorImplementationSpec(BaseModel):
    """오케스트레이터 구현 명세"""
    name: str = Field(..., description="오케스트레이터 이름")
    class_name: str = Field(..., description="클래스 이름")
    description: str = Field(..., description="설명")
    
    # 실행 플로우
    execution_flow: List[ExecutionFlowNode] = Field(..., description="실행 플로우")
    
    # 전역 설정
    global_timeout: int = Field(default=3600, description="전역 타임아웃")
    max_parallel_agents: int = Field(default=5, description="최대 병렬 에이전트")
    
    # 에러 처리
    global_error_handling: ErrorHandlingStrategy = Field(
        default=ErrorHandlingStrategy.FAIL_FAST
    )
    rollback_strategy: Dict[str, Any] = Field(default_factory=dict, description="롤백 전략")
    
    # 모니터링
    metrics_enabled: bool = Field(default=True, description="메트릭 수집 여부")
    logging_level: str = Field(default="INFO", description="로깅 레벨")
    
    # 통합 테스트
    integration_tests: List[Dict[str, Any]] = Field(default_factory=list)


class IntegrationSpec(BaseModel):
    """통합 명세"""
    source_agent: str = Field(..., description="소스 에이전트")
    target_agent: str = Field(..., description="타겟 에이전트")
    data_mapping: Dict[str, str] = Field(..., description="데이터 매핑")
    transform_function: Optional[str] = Field(None, description="변환 함수")
    validation_rules: List[str] = Field(default_factory=list, description="검증 규칙")


class OrchestratorDesignDocument(BaseModel):
    """오케스트레이터 디자인 문서"""
    version: str = Field(default="1.0.0", description="문서 버전")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # 핵심 설계
    orchestrator_spec: OrchestratorImplementationSpec
    agent_specs: List[AgentImplementationSpec]
    integration_specs: List[IntegrationSpec]
    
    # 메타데이터
    design_rationale: str = Field(..., description="설계 근거")
    assumptions: List[str] = Field(default_factory=list, description="가정사항")
    risks: List[str] = Field(default_factory=list, description="위험요소")
    
    # 구현 가이드
    implementation_order: List[str] = Field(..., description="구현 순서")
    estimated_effort: Dict[str, int] = Field(..., description="예상 작업량 (시간)")
    required_skills: List[str] = Field(default_factory=list, description="필요 기술")


class OrchestratorDesigner(BaseAgent):
    """오케스트레이터 디자이너 에이전트"""
    
    def __init__(self, memory_hub: Optional[MemoryHub] = None):
        super().__init__(
            name="OrchestratorDesigner",
            memory_hub=memory_hub
        )
        self.role = "Orchestrator Implementation Designer"
        self.capabilities = ["design", "specify", "validate"]
        self.ai_provider = BedrockAIProvider(
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
    
    async def design_orchestrator(
        self,
        architecture_design: Dict[str, Any],
        requirements: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> OrchestratorDesignDocument:
        """오케스트레이터 상세 설계
        
        Args:
            architecture_design: SystemArchitect의 아키텍처 설계
            requirements: 요구사항
            constraints: 제약사항
            
        Returns:
            OrchestratorDesignDocument: 오케스트레이터 디자인 문서
        """
        # AI를 통한 상세 설계
        design_prompt = self._create_design_prompt(
            architecture_design, requirements, constraints
        )
        response = await self.ai_provider.complete(design_prompt)
        
        # 설계 파싱
        design_doc = self._parse_design_response(response)
        
        # 설계 검증
        validation_result = await self._validate_design(design_doc)
        if not validation_result["valid"]:
            # 설계 수정
            design_doc = await self._refine_design(design_doc, validation_result)
        
        # 메모리에 저장
        await self._store_design_in_memory(design_doc)
        
        return design_doc
    
    def _create_design_prompt(
        self,
        architecture: Dict[str, Any],
        requirements: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """디자인 프롬프트 생성"""
        
        prompt = f"""
        You are designing the implementation details for an orchestrator and agents.
        
        Architecture Design:
        {json.dumps(architecture, indent=2)}
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Constraints:
        {json.dumps(constraints or {}, indent=2)}
        
        Please create a detailed implementation specification that includes:
        
        1. Orchestrator Implementation:
           - Detailed execution flow with conditions and loops
           - Error handling at each step
           - Timeout and retry policies
           - Data transformation between agents
        
        2. Agent Implementations:
           - Method signatures with parameters and return types
           - Input/output schemas with validation
           - Dependencies and service requirements
           - Test scenarios
        
        3. Integration Points:
           - Data mapping between agents
           - Message formats
           - Validation rules
        
        Provide the design in the following JSON format:
        {{
            "orchestrator_spec": {{
                "name": "UpgradeOrchestrator",
                "class_name": "UpgradeOrchestrator",
                "description": "...",
                "execution_flow": [
                    {{
                        "id": "step1",
                        "type": "sequential",
                        "agent": "RequirementAnalyzer",
                        "error_handling": "retry_then_fail",
                        "timeout_seconds": 300
                    }}
                ],
                "global_timeout": 3600
            }},
            "agent_specs": [
                {{
                    "name": "RequirementAnalyzer",
                    "class_name": "RequirementAnalyzer",
                    "methods": [
                        {{
                            "name": "analyze",
                            "description": "Analyze requirements",
                            "parameters": [{{"name": "text", "type": "str"}}],
                            "return_type": "Dict[str, Any]"
                        }}
                    ],
                    "input_schema": {{}},
                    "output_schema": {{}}
                }}
            ],
            "integration_specs": [
                {{
                    "source_agent": "RequirementAnalyzer",
                    "target_agent": "GapAnalyzer",
                    "data_mapping": {{"requirements": "input_requirements"}}
                }}
            ],
            "design_rationale": "...",
            "implementation_order": ["agent1", "agent2"]
        }}
        """
        
        return prompt
    
    def _parse_design_response(self, response: str) -> OrchestratorDesignDocument:
        """AI 응답 파싱"""
        try:
            # JSON 추출
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                design_dict = json.loads(json_match.group())
                
                # 디자인 문서 생성
                return OrchestratorDesignDocument(
                    orchestrator_spec=OrchestratorImplementationSpec(
                        **design_dict.get("orchestrator_spec", {})
                    ),
                    agent_specs=[
                        AgentImplementationSpec(**spec) 
                        for spec in design_dict.get("agent_specs", [])
                    ],
                    integration_specs=[
                        IntegrationSpec(**spec)
                        for spec in design_dict.get("integration_specs", [])
                    ],
                    design_rationale=design_dict.get("design_rationale", ""),
                    implementation_order=design_dict.get("implementation_order", []),
                    estimated_effort=design_dict.get("estimated_effort", {})
                )
            else:
                return self._create_fallback_design()
                
        except Exception as e:
            self.logger.error(f"Failed to parse design response: {e}")
            return self._create_fallback_design()
    
    def _create_fallback_design(self) -> OrchestratorDesignDocument:
        """폴백 디자인"""
        return OrchestratorDesignDocument(
            orchestrator_spec=OrchestratorImplementationSpec(
                name="DefaultOrchestrator",
                class_name="DefaultOrchestrator",
                description="Fallback orchestrator",
                execution_flow=[
                    ExecutionFlowNode(
                        id="step1",
                        type=ExecutionStrategy.SEQUENTIAL,
                        agent="DefaultAgent"
                    )
                ]
            ),
            agent_specs=[],
            integration_specs=[],
            design_rationale="Fallback design due to parsing error",
            implementation_order=[]
        )
    
    async def _validate_design(
        self,
        design: OrchestratorDesignDocument
    ) -> Dict[str, Any]:
        """디자인 검증"""
        issues = []
        
        # 에이전트 존재 확인
        defined_agents = {spec.name for spec in design.agent_specs}
        referenced_agents = set()
        
        for node in design.orchestrator_spec.execution_flow:
            if node.agent:
                referenced_agents.add(node.agent)
            if node.agents:
                referenced_agents.update(node.agents)
        
        missing_agents = referenced_agents - defined_agents
        if missing_agents:
            issues.append(f"Missing agent specifications: {missing_agents}")
        
        # 순환 의존성 확인
        # ... (구현 생략)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    async def _refine_design(
        self,
        design: OrchestratorDesignDocument,
        validation_result: Dict[str, Any]
    ) -> OrchestratorDesignDocument:
        """디자인 개선"""
        # AI를 통한 디자인 개선
        # ... (구현 생략)
        return design
    
    async def _store_design_in_memory(self, design: OrchestratorDesignDocument):
        """디자인을 메모리에 저장"""
        await self.memory_hub.store(
            key=f"orchestrator_design_{design.version}",
            value=design.dict(),
            context_type=ContextType.SHARED,
            tags=["orchestrator", "design", "implementation"]
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 실행"""
        design_doc = await self.design_orchestrator(
            architecture_design=inputs.get("architecture_design", {}),
            requirements=inputs.get("requirements", {}),
            constraints=inputs.get("constraints")
        )
        
        return {
            "orchestrator_design": design_doc.dict(),
            "summary": f"Designed orchestrator with {len(design_doc.agent_specs)} agents",
            "implementation_order": design_doc.implementation_order,
            "estimated_effort_hours": sum(design_doc.estimated_effort.values()),
            "next_steps": [
                "Review and approve design",
                "Create implementation plan with PlannerAgent",
                "Generate detailed tasks with TaskCreatorAgent",
                "Implement with CodeGenerator"
            ]
        }