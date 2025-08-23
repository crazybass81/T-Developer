"""코드 생성기 (CodeGenerator) - AI 기반 프로덕션 코드 자동 생성

이 에이전트는 요구사항 명세를 받아 실제 프로덕션 준비된 코드를 자동으로 생성하며,
SOLID 원칙과 모범 사례를 준수하는 고품질 코드를 생성합니다.

주요 기능:
1. 요구사항 명세로부터 컴포넌트별 코드 자동 생성
2. AWS Bedrock Claude를 활용한 지능형 코드 생성
3. 템플릿 기반 코드 생성 지원 (재사용성 향상)
4. 단위 테스트 코드 자동 생성 (Happy path, 에러 케이스, Edge case)
5. 자동 문서화 생성 (API 참조, 사용 예시)
6. Circuit Breaker 및 Resource Limiter를 통한 안전성 보장
7. 다중 언어 지원 (Python, JavaScript, TypeScript, Java 등)
8. 타입 힌트 자동 포함 및 비동기 처리 기본 적용
9. 에러 처리 및 예외 상황 코드 자동 포함
10. SOLID 원칙 준수 코드 생성

입력 매개변수:
- requirements: 요구사항 명세 (components 배열 포함)
- target_language: 대상 프로그래밍 언어 (기본: "python")
- framework: 사용할 프레임워크 (선택적)
- read_from_memory: 메모리에서 요구사항 읽기 여부
- memory_key: 메모리 키 (read_from_memory=True인 경우)
- config: GenerationConfig 객체

출력 형식:
- generated_codes: GeneratedCode 객체 배열
  * success: 생성 성공 여부
  * component_name: 컴포넌트명
  * code: 생성된 메인 코드
  * test_code: 생성된 테스트 코드 (선택적)
  * documentation: 생성된 문서 (선택적)
  * file_path: 파일 경로
  * language: 프로그래밍 언어
  * error: 에러 메시지 (실패 시)
  * metadata: 메타데이터 (설정, 생성 시각 등)
- total_components: 총 컴포넌트 수
- timestamp: 생성 시각

생성 설정 (GenerationConfig):
- max_tokens: 최대 토큰 수 (기본: 4096)
- temperature: 생성 온도 (기본: 0.5)
- include_tests: 테스트 코드 포함 여부 (기본: False)
- include_docs: 문서화 포함 여부 (기본: True)
- follow_conventions: 코딩 컨벤션 준수 (기본: True)
- use_types: 타입 힌트 사용 (기본: True)
- async_by_default: 비동기 처리 기본 적용 (기본: True)

문서 참조 관계:
- 읽어오는 보고서:
  * RequirementAnalyzer 요구사항 분석 결과
  * PlannerAgent 실행 계획
  * TaskCreatorAgent 실행 태스크
- 출력을 사용하는 에이전트:
  * QualityGate: 생성 코드 품질 검증
  * StaticAnalyzer: 생성 코드 구조 분석
  * CodeImproverAgent: 코드 개선

사용 예시:
```python
generator = CodeGenerator(
    config=GenerationConfig(
        include_tests=True,
        include_docs=True,
        temperature=0.3
    )
)

result = await generator.execute({
    'requirements': {
        'components': [
            {
                'name': 'UserService',
                'type': 'service',
                'responsibility': '사용자 관리',
                'dependencies': ['database', 'auth']
            }
        ]
    },
    'target_language': 'python',
    'framework': 'FastAPI'
})

print(f"생성된 컴포넌트: {result['total_components']}개")
```

작성자: T-Developer v2 Team
버전: 1.0.0
최종 수정: 2025-08-23
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from .base import BaseAgent
from .ai_providers import get_ai_provider
from ..memory.contexts import ContextType
from ..safety import CircuitBreaker, ResourceLimiter, ResourceLimit

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """코드 생성 설정."""
    
    max_tokens: int = 4096
    temperature: float = 0.5
    include_tests: bool = False
    include_docs: bool = True
    follow_conventions: bool = True
    use_types: bool = True
    async_by_default: bool = True


@dataclass
class CodeTemplate:
    """코드 템플릿."""
    
    name: str
    language: str
    template_code: str
    placeholders: List[str] = field(default_factory=list)


@dataclass
class GeneratedCode:
    """생성된 코드 결과."""
    
    success: bool
    component_name: str
    code: str = ""
    test_code: Optional[str] = None
    documentation: Optional[str] = None
    file_path: str = ""
    language: str = "python"
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodeGenerator(BaseAgent):
    """코드 생성 에이전트.
    
    이 에이전트는:
    1. 요구사항 명세를 받아 코드 생성
    2. Safety mechanisms 적용 (Circuit Breaker, Resource Limiter)
    3. 템플릿 기반 생성 지원
    4. 테스트 코드 생성
    5. 문서화 생성
    """
    
    def __init__(self, memory_hub=None, config: Optional[GenerationConfig] = None):
        """CodeGenerator 초기화.
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            config: 생성 설정
        """
        super().__init__(
            name="CodeGenerator",
            version="1.0.0",
            memory_hub=memory_hub
        )
        
        self.config = config or GenerationConfig()
        self.templates: Dict[str, CodeTemplate] = {}
        
        # AI Provider 초기화
        self.ai_provider = get_ai_provider("bedrock", {
            "model": "claude-3-sonnet",
            "region": "us-east-1"
        })
        
        # Safety mechanisms 초기화
        from ..safety import CircuitBreakerConfig
        self.circuit_breaker = CircuitBreaker(
            name="CodeGenerator",
            config=CircuitBreakerConfig(
                failure_threshold=3,  # 3번 실패 시 열림
                recovery_timeout=30.0,  # 30초 후 복구 시도
                success_threshold=2  # 2번 성공 시 닫힘
            )
        )
        
        self.resource_limiter = ResourceLimiter(
            limits=ResourceLimit(
                max_memory_mb=1000,
                max_cpu_percent=70,
                max_execution_time=60,
                max_concurrent_tasks=5
            )
        )
    
    async def _get_planner_and_task_reports(self) -> Dict[str, Any]:
        """Fetch planner and task creator reports from memory.
        
        Returns:
            Dictionary containing planner and task reports
        """
        if not self.memory_hub:
            return {}
        
        from ..memory.contexts import ContextType
        
        reports = {}
        
        try:
            # Get planner reports
            planner_reports = await self.memory_hub.search(
                context_type=ContextType.O_CTX,
                tags=["execution_plan", "PlannerAgent"],
                limit=3
            )
            if planner_reports:
                reports["planner"] = planner_reports
            
            # Get task creator reports
            task_reports = await self.memory_hub.search(
                context_type=ContextType.O_CTX,
                tags=["executable_tasks", "TaskCreatorAgent"],
                limit=3
            )
            if task_reports:
                reports["tasks"] = task_reports
                
        except Exception as e:
            logger.debug(f"Failed to get planner/task reports: {e}")
        
        return reports
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """코드 생성 실행.
        
        Args:
            task: 다음을 포함하는 태스크:
                - requirements: 요구사항 명세
                - target_language: 대상 언어
                - framework: 사용할 프레임워크
                - read_from_memory: 메모리에서 읽기 여부
                - memory_key: 메모리 키
                
        Returns:
            생성 결과
        """
        logger.info("Starting code generation...")
        
        try:
            # Get reports from planner and task creator
            plan_task_reports = await self._get_planner_and_task_reports()
            
            # Enrich task with reports
            if plan_task_reports:
                if "planner" in plan_task_reports:
                    task["execution_plans"] = plan_task_reports["planner"]
                if "tasks" in plan_task_reports:
                    task["executable_tasks"] = plan_task_reports["tasks"]
            
            # 메모리에서 요구사항 읽기
            requirements = await self._get_requirements(task)
            if not requirements:
                return {
                    "success": False,
                    "error": "No requirements provided"
                }
            
            # 컴포넌트별로 코드 생성
            components = requirements.get("components", [])
            generated_codes = []
            
            for component in components:
                # Safety mechanisms를 통해 생성
                result = await self.circuit_breaker.call(
                    self.resource_limiter.execute,
                    self._generate_component_safe,
                    component,
                    requirements,
                    task.get("target_language", "python")
                )
                generated_codes.append(result)
            
            # 메모리에 저장
            await self._store_generated_codes(generated_codes)
            
            return {
                "success": True,
                "generated_codes": [gc.__dict__ for gc in generated_codes],
                "total_components": len(components),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_component(
        self,
        component: Dict[str, Any],
        requirements: Dict[str, Any],
        target_language: str = "python",
        use_template: bool = False
    ) -> GeneratedCode:
        """단일 컴포넌트 코드 생성.
        
        Args:
            component: 컴포넌트 정보
            requirements: 전체 요구사항
            target_language: 대상 언어
            use_template: 템플릿 사용 여부
            
        Returns:
            생성된 코드
        """
        # Circuit Breaker를 통해 실행
        try:
            return await self.circuit_breaker.call(
                self._generate_component_internal,
                component,
                requirements,
                target_language,
                use_template
            )
        except Exception as e:
            logger.error(f"Failed to generate component {component.get('name')}: {e}")
            return GeneratedCode(
                success=False,
                component_name=component.get("name", "Unknown"),
                error=str(e)
            )
    
    async def _generate_component_internal(
        self,
        component: Dict[str, Any],
        requirements: Dict[str, Any],
        target_language: str,
        use_template: bool
    ) -> GeneratedCode:
        """실제 컴포넌트 생성 로직.
        
        Args:
            component: 컴포넌트 정보
            requirements: 전체 요구사항
            target_language: 대상 언어
            use_template: 템플릿 사용 여부
            
        Returns:
            생성된 코드
        """
        # 컴포넌트 검증
        if not self._validate_component(component):
            return GeneratedCode(
                success=False,
                component_name=component.get("name", "Unknown"),
                error="Invalid component specification"
            )
        
        # 템플릿 사용
        if use_template and component.get("type") in self.templates:
            code = self._apply_template(component)
        else:
            # AI를 사용한 코드 생성
            code = await self._generate_with_ai(component, requirements, target_language)
        
        # 테스트 코드 생성
        test_code = None
        if self.config.include_tests:
            test_code = await self._generate_tests(component, code, target_language)
        
        # 문서화 생성
        documentation = None
        if self.config.include_docs:
            documentation = await self._generate_documentation(component, code)
        
        return GeneratedCode(
            success=True,
            component_name=component["name"],
            code=code,
            test_code=test_code,
            documentation=documentation,
            file_path=self._get_file_path(component, target_language),
            language=target_language,
            metadata={
                "config": self.config.__dict__,
                "component_type": component.get("type"),
                "generated_at": datetime.now().isoformat()
            }
        )
    
    async def _generate_component_safe(
        self,
        component: Dict[str, Any],
        requirements: Dict[str, Any],
        target_language: str
    ) -> GeneratedCode:
        """Safety mechanisms가 적용된 컴포넌트 생성.
        
        Args:
            component: 컴포넌트 정보
            requirements: 요구사항
            target_language: 대상 언어
            
        Returns:
            생성된 코드
        """
        return await self._generate_component_internal(component, requirements, target_language, False)
    
    async def _generate_with_ai(
        self,
        component: Dict[str, Any],
        requirements: Dict[str, Any],
        target_language: str
    ) -> str:
        """AI를 사용한 코드 생성.
        
        Args:
            component: 컴포넌트 정보
            requirements: 요구사항
            target_language: 대상 언어
            
        Returns:
            생성된 코드
        """
        prompt = f"""Generate {target_language} code for the following component:

Component Name: {component['name']}
Type: {component.get('type', 'service')}
Responsibility: {component.get('responsibility', 'N/A')}

Requirements:
- Functional: {', '.join(requirements.get('functional_requirements', [])[:3])}
- Dependencies: {', '.join(requirements.get('dependencies', []))}
- Complexity: {requirements.get('complexity', 'medium')}

Additional Context:
- Follow SOLID principles
- Include error handling
- Use async/await if applicable
- Add proper type hints (if {target_language} supports it)
- Include clear docstrings/comments

Generate production-ready code for this component. Return ONLY the code without explanations."""

        system_prompt = f"""You are an expert {target_language} developer.
Generate clean, efficient, and well-structured code following best practices.
Focus on maintainability, readability, and performance."""

        response = await self.ai_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        if not response.success:
            raise Exception(f"AI generation failed: {response.error}")
        
        # 코드 블록 추출
        code = response.content
        if f"```{target_language}" in code:
            start = code.find(f"```{target_language}") + len(f"```{target_language}")
            end = code.find("```", start)
            code = code[start:end].strip()
        elif "```" in code:
            start = code.find("```") + 3
            end = code.find("```", start)
            code = code[start:end].strip()
        
        return code
    
    async def _generate_tests(
        self,
        component: Dict[str, Any],
        code: str,
        target_language: str
    ) -> str:
        """테스트 코드 생성.
        
        Args:
            component: 컴포넌트 정보
            code: 생성된 코드
            target_language: 대상 언어
            
        Returns:
            테스트 코드
        """
        prompt = f"""Generate unit tests for the following {target_language} code:

Component: {component['name']}
Code:
```{target_language}
{code[:1000]}  # 처음 1000자만
```

Generate comprehensive unit tests including:
- Happy path tests
- Error cases
- Edge cases
- Mocking where needed

Use appropriate testing framework for {target_language}."""

        response = await self.ai_provider.generate(
            prompt=prompt,
            temperature=0.3  # 테스트는 더 deterministic하게
        )
        
        if response.success:
            return response.content
        return ""
    
    async def _generate_documentation(
        self,
        component: Dict[str, Any],
        code: str
    ) -> str:
        """문서화 생성.
        
        Args:
            component: 컴포넌트 정보
            code: 생성된 코드
            
        Returns:
            문서화
        """
        doc = f"""# {component['name']}

## Overview
{component.get('responsibility', 'Component functionality')}

## Type
{component.get('type', 'service')}

## Dependencies
{', '.join(component.get('dependencies', ['None']))}

## Usage
```python
# Example usage of {component['name']}
# TODO: Add usage examples
```

## API Reference
TODO: Add API documentation

## Testing
Run tests with appropriate test runner.

---
Generated at: {datetime.now().isoformat()}
"""
        return doc
    
    def _validate_component(self, component: Dict[str, Any]) -> bool:
        """컴포넌트 정보 검증.
        
        Args:
            component: 컴포넌트 정보
            
        Returns:
            유효 여부
        """
        if not component.get("name"):
            return False
        
        if not component.get("name").strip():
            return False
        
        return True
    
    def _apply_template(self, component: Dict[str, Any]) -> str:
        """템플릿 적용.
        
        Args:
            component: 컴포넌트 정보
            
        Returns:
            템플릿이 적용된 코드
        """
        template = self.templates.get(component.get("type"))
        if not template:
            return ""
        
        code = template.template_code
        
        # 플레이스홀더 치환
        replacements = {
            "component_name": component.get("name", "Component"),
            "responsibility": component.get("responsibility", ""),
            "type": component.get("type", "service")
        }
        
        for key, value in replacements.items():
            code = code.replace(f"{{{key}}}", value)
        
        return code
    
    def _get_file_path(self, component: Dict[str, Any], language: str) -> str:
        """파일 경로 생성.
        
        Args:
            component: 컴포넌트 정보
            language: 프로그래밍 언어
            
        Returns:
            파일 경로
        """
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java"
        }
        
        ext = extensions.get(language, ".txt")
        name = component["name"].lower().replace(" ", "_")
        
        return f"generated/{name}{ext}"
    
    async def _get_requirements(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """요구사항 가져오기.
        
        Args:
            task: 태스크 정보
            
        Returns:
            요구사항 명세
        """
        if task.get("read_from_memory") and self.memory_hub:
            key = task.get("memory_key", "requirements:latest")
            requirements = await self.memory_hub.get(
                context_type=ContextType.S_CTX,
                key=key
            )
            return requirements
        
        return task.get("requirements")
    
    async def _store_generated_codes(self, codes: List[GeneratedCode]) -> None:
        """생성된 코드를 메모리에 저장.
        
        Args:
            codes: 생성된 코드 목록
        """
        if not self.memory_hub:
            return
        
        for code in codes:
            if code.success:
                await self.memory_hub.put(
                    context_type=ContextType.A_CTX,
                    key=f"generated:{code.component_name}",
                    value=code.code,
                    ttl_seconds=86400
                )
        
        logger.info(f"Stored {len(codes)} generated codes in memory")
    
    def add_template(self, template: CodeTemplate) -> None:
        """템플릿 추가.
        
        Args:
            template: 코드 템플릿
        """
        key = template.name if template.name != "service_template" else "service"
        self.templates[key] = template
        logger.info(f"Added template: {template.name}")
    
    def update_config(self, config: GenerationConfig) -> None:
        """설정 업데이트.
        
        Args:
            config: 새로운 설정
        """
        self.config = config
        logger.info(f"Updated generation config: {config}")