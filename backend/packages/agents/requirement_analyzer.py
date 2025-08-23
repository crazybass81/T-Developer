"""요구사항 분석 에이전트 (RequirementAnalyzer)

이 에이전트는 자연어로 작성된 요구사항을 분석하여 구조화된 명세로 변환합니다.
요구사항의 모호성을 제거하고, 기능적/비기능적 요구사항을 분류하며,
구현에 필요한 컴포넌트와 의존성을 식별합니다.

주요 기능:
1. 자연어 요구사항 파싱 및 분석
   - 핵심 의도 파악
   - 구체적인 기능 요구사항 추출
   - 제약사항 및 가정 식별
   
2. 요구사항 분류
   - 기능적 요구사항 (Functional Requirements)
   - 비기능적 요구사항 (Non-functional Requirements)
   - 기술적 제약사항 (Constraints)
   - 비즈니스 가정 (Assumptions)
   
3. 컴포넌트 도출
   - 필요한 컴포넌트 식별
   - 컴포넌트 간 의존성 분석
   - 외부 의존성 파악

입력:
- requirements (str): 자연어 요구사항 텍스트
- context (Dict, optional): 추가 컨텍스트 정보

출력:
- RequirementSpec: 구조화된 요구사항 명세
  * functional_requirements: 기능 요구사항 목록
  * non_functional_requirements: 비기능 요구사항 목록
  * constraints: 제약사항 목록
  * assumptions: 가정 목록
  * components: 필요 컴포넌트 정의
  * dependencies: 외부 의존성 목록

문서 참조 관계:
- 출력 참조:
  * ExternalResearcher: 관련 기술 조사
  * GapAnalyzer: 현재와 목표 상태 비교
  * SystemArchitect: 아키텍처 설계
  * PlannerAgent: 구현 계획 수립
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from .base import BaseAgent, AgentTask, AgentResult, TaskStatus
from .ai_providers import get_ai_provider
from ..memory.contexts import ContextType

logger = logging.getLogger(__name__)


@dataclass
class RequirementSpec:
    """분석된 요구사항 명세."""
    
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    components: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high
    priority: str = "medium"  # low, medium, high
    estimated_effort: str = ""  # e.g., "2-3 days"
    risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RequirementAnalyzer(BaseAgent):
    """요구사항 분석 에이전트.
    
    이 에이전트는:
    1. 자연어 요구사항을 받아 분석
    2. 구조화된 명세로 변환
    3. 구현 가능성 평가
    4. 필요한 컴포넌트 식별
    """
    
    def __init__(self, memory_hub=None, config: Optional[Dict[str, Any]] = None, document_context=None):
        """RequirementAnalyzer 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            config: 에이전트 설정
            document_context: SharedDocumentContext 인스턴스
        """
        super().__init__(
            name="RequirementAnalyzer",
            version="1.0.0",
            memory_hub=memory_hub,
            document_context=document_context
        )
        
        # 설정 저장
        self.config = config or {}
        self.capabilities = ["analyze", "structure", "evaluate"]
        
        # 페르소나 적용 - 요구사항 해석가
        from .personas import get_persona
        self.persona = get_persona("RequirementAnalyzer")
        if self.persona:
            logger.info(f"🎭 {self.persona.name}: {self.persona.catchphrase}")
        
        # AI Provider 초기화
        self.ai_provider = get_ai_provider("bedrock", {
            "model": "claude-3-sonnet",
            "region": "us-east-1"
        })
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """요구사항 분석 실행.
        
        Args:
            task: AgentTask with inputs:
                - requirements: 자연어 요구사항
                - project_context: 프로젝트 컨텍스트 (선택)
                - focus_area: 집중 영역 (선택)
                
        Returns:
            AgentResult with analysis
        """
        # Handle both Dict and AgentTask for backward compatibility
        if isinstance(task, dict):
            task_inputs = task
        else:
            task_inputs = task.inputs if hasattr(task, 'inputs') else task
            
        logger.info(f"Analyzing requirements: {task_inputs.get('requirements', '')[:100]}...")
        
        try:
            # 입력 검증
            requirements = task_inputs.get("requirements", "")
            if not requirements:
                return AgentResult(
                    success=False,
                    status=TaskStatus.FAILED,
                    data={},
                    error="No requirements provided"
                )
            
            # 프로젝트 컨텍스트 수집
            project_context = await self._gather_context(task_inputs)
            
            # AI를 사용한 요구사항 분석
            analysis = await self._analyze_requirements(
                requirements,
                project_context,
                task_inputs.get("focus_area")
            )
            
            # 구조화된 명세 생성
            spec = await self._create_specification(analysis)
            
            # 구현 가능성 평가
            feasibility = await self._evaluate_feasibility(spec)
            
            # 메모리에 저장
            if self.memory_hub:
                await self._store_analysis(spec, feasibility)
            
            result_data = {
                "specification": spec.__dict__,
                "feasibility": feasibility,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data=result_data,
                error=None
            )
            
        except Exception as e:
            logger.error(f"Requirement analysis failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _gather_context(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 컨텍스트 수집.
        
        Args:
            task: 태스크 정보
            
        Returns:
            수집된 컨텍스트
        """
        context = {
            "project": task.get("project_context", {}),
            "existing_components": [],
            "constraints": [],
            "standards": []
        }
        
        # 메모리에서 관련 정보 검색
        if self.memory_hub:
            # 현재는 간단하게 처리 (추후 패턴 매칭 구현)
            # 기존 컴포넌트 정보는 SHARED 컨텍스트에서 가져오기
            context["existing_components"] = []
            context["constraints"] = []
        
        return context
    
    async def _analyze_requirements(
        self,
        requirements: str,
        context: Dict[str, Any],
        focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """AI를 사용한 요구사항 분석.
        
        Args:
            requirements: 자연어 요구사항
            context: 프로젝트 컨텍스트
            focus_area: 집중 영역
            
        Returns:
            분석 결과
        """
        # 프롬프트 구성
        prompt = f"""Analyze the following software requirements and provide a structured analysis.

Requirements:
{requirements}

{f"Focus Area: {focus_area}" if focus_area else ""}

Project Context:
- Existing Components: {len(context.get('existing_components', []))} components
- Constraints: {', '.join(context.get('constraints', [])) or 'None specified'}

Please analyze and provide a JSON response with:
1. functional_requirements: List of specific functional requirements
2. non_functional_requirements: List of non-functional requirements (performance, security, etc.)
3. components: List of components needed (name, type, responsibility)
4. dependencies: External dependencies or services required
5. complexity: Overall complexity (low/medium/high)
6. priority: Implementation priority (low/medium/high)
7. risks: Potential risks or challenges
8. success_criteria: Measurable success criteria
9. estimated_effort: Rough effort estimate
10. assumptions: Key assumptions made

Ensure the response is valid JSON."""

        # 페르소나 적용
        persona_prompt = self.persona.to_prompt() if self.persona else ""
        
        system_prompt = f"""{persona_prompt}

You are an expert software architect and requirement analyst.
Analyze requirements thoroughly and provide structured, actionable specifications.
Focus on clarity, completeness, and implementability."""

        # AI 호출
        response = await self.ai_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # 낮은 temperature로 일관성 있는 분석
        )
        
        if not response.success:
            raise Exception(f"AI analysis failed: {response.error}")
        
        # JSON 파싱
        try:
            # JSON 추출
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            analysis = json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # 기본 구조 반환
            analysis = {
                "functional_requirements": [requirements],
                "non_functional_requirements": [],
                "components": [],
                "complexity": "medium",
                "raw_analysis": response.content
            }
        
        return analysis
    
    async def _create_specification(self, analysis: Dict[str, Any]) -> RequirementSpec:
        """구조화된 명세 생성.
        
        Args:
            analysis: AI 분석 결과
            
        Returns:
            RequirementSpec 객체
        """
        spec = RequirementSpec(
            functional_requirements=analysis.get("functional_requirements", []),
            non_functional_requirements=analysis.get("non_functional_requirements", []),
            constraints=analysis.get("constraints", []),
            assumptions=analysis.get("assumptions", []),
            components=analysis.get("components", []),
            dependencies=analysis.get("dependencies", []),
            complexity=analysis.get("complexity", "medium"),
            priority=analysis.get("priority", "medium"),
            estimated_effort=analysis.get("estimated_effort", ""),
            risks=analysis.get("risks", []),
            success_criteria=analysis.get("success_criteria", []),
            metadata={
                "analyzed_at": datetime.now().isoformat(),
                "analyzer_version": self.version,
                "raw_analysis": analysis.get("raw_analysis")
            }
        )
        
        # 컴포넌트 정보 보강
        for i, component in enumerate(spec.components):
            if isinstance(component, str):
                # 문자열을 딕셔너리로 변환
                spec.components[i] = {
                    "name": component,
                    "type": "unknown",
                    "responsibility": ""
                }
            elif isinstance(component, dict):
                # 필수 필드 확인
                component.setdefault("name", f"Component{i+1}")
                component.setdefault("type", "service")
                component.setdefault("responsibility", "")
        
        return spec
    
    async def _evaluate_feasibility(self, spec: RequirementSpec) -> Dict[str, Any]:
        """구현 가능성 평가.
        
        Args:
            spec: 요구사항 명세
            
        Returns:
            가능성 평가 결과
        """
        feasibility = {
            "overall_score": 0.0,
            "technical_feasibility": True,
            "resource_availability": True,
            "time_feasibility": True,
            "risk_level": "low",
            "recommendations": [],
            "warnings": [],
            "blockers": []
        }
        
        # 복잡도 기반 점수
        complexity_scores = {"low": 0.9, "medium": 0.7, "high": 0.5}
        feasibility["overall_score"] = complexity_scores.get(spec.complexity, 0.6)
        
        # 위험 수준 평가
        if len(spec.risks) > 5:
            feasibility["risk_level"] = "high"
            feasibility["overall_score"] *= 0.8
        elif len(spec.risks) > 2:
            feasibility["risk_level"] = "medium"
            feasibility["overall_score"] *= 0.9
        
        # 의존성 확인
        if len(spec.dependencies) > 10:
            feasibility["warnings"].append("High number of dependencies may increase complexity")
            feasibility["overall_score"] *= 0.9
        
        # 컴포넌트 수 확인
        if len(spec.components) > 20:
            feasibility["warnings"].append("Large number of components may require phased implementation")
            feasibility["recommendations"].append("Consider breaking down into smaller milestones")
        
        # 권장사항 생성
        if spec.complexity == "high":
            feasibility["recommendations"].append("Start with a proof of concept")
            feasibility["recommendations"].append("Allocate extra time for testing and iteration")
        
        if not spec.success_criteria:
            feasibility["warnings"].append("No success criteria defined - consider adding measurable goals")
        
        # 전체 점수 정규화
        feasibility["overall_score"] = min(1.0, max(0.0, feasibility["overall_score"]))
        
        return feasibility
    
    async def _store_analysis(
        self,
        spec: RequirementSpec,
        feasibility: Dict[str, Any]
    ) -> None:
        """분석 결과를 메모리에 저장.
        
        Args:
            spec: 요구사항 명세
            feasibility: 가능성 평가
        """
        if not self.memory_hub:
            return
        
        # 요구사항 명세 저장
        await self.memory_hub.put(
            context_type=ContextType.A_CTX,  # AGENT 컨텍스트
            key=f"requirement:spec:{datetime.now().timestamp()}",
            value={
                "specification": spec.__dict__,
                "feasibility": feasibility
            },
            ttl_seconds=86400  # 24시간
        )
        
        # 컴포넌트 정보 공유 메모리에 저장
        for component in spec.components:
            await self.memory_hub.put(
                context_type=ContextType.S_CTX,  # SHARED 컨텍스트
                key=f"component:identified:{component.get('name', 'unknown')}",
                value=component,
                ttl_seconds=86400
            )
        
        logger.info(f"Stored analysis with {len(spec.components)} components")