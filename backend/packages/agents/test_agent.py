#!/usr/bin/env python3
"""테스트 실행 및 분석 에이전트

이 에이전트는 Evolution Loop에서 코드 생성/수정 후 테스트를 실행하고
결과를 분석하여 품질을 검증합니다. 테스트 프레임워크를 자동으로 감지하고
실패한 테스트에 대한 AI 기반 원인 분석을 제공합니다.

주요 기능:
- 테스트 프레임워크 자동 감지 (pytest, unittest, jest, mocha 등)
- 테스트 실행 및 커버리지 측정
- 실패 원인 AI 분석
- 개선 권장사항 제시
- SharedDocumentContext 통합
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import asyncio
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
import re

from .base import BaseAgent, AgentTask, AgentResult
from .personas import get_persona
from ..ai_providers import BedrockAIProvider

logger = logging.getLogger(__name__)


@dataclass
class TestReport:
    """테스트 실행 결과 리포트
    
    테스트 실행의 모든 측면을 담은 종합 리포트입니다.
    Evolution Loop에서 품질 검증의 핵심 데이터가 됩니다.
    """
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float = 0.0
    failed_tests: List[Dict[str, Any]] = field(default_factory=list)
    test_duration: float = 0.0
    test_output: str = ""
    recommendations: List[str] = field(default_factory=list)
    framework: str = "unknown"
    files_covered: int = 0
    lines_covered: int = 0
    lines_total: int = 0
    branch_coverage: float = 0.0


class TestAgent(BaseAgent):
    """테스트 실행 및 분석 에이전트
    
    품질 검증관 페르소나:
    - 엄격하고 철저한 테스트 수행
    - 모든 엣지 케이스 고려
    - 실패에 대한 명확한 원인 분석
    - 개선을 위한 구체적 권고
    
    이 에이전트는 "테스트되지 않은 코드는 고장난 코드다"라는
    철학으로 시스템의 품질을 보장합니다.
    """
    
    def __init__(self, memory_hub=None, config=None, document_context=None):
        """TestAgent 초기화
        
        Args:
            memory_hub: 메모리 허브 인스턴스
            config: 에이전트 설정
            document_context: SharedDocumentContext 인스턴스
        """
        # AI Provider 설정
        ai_provider = BedrockAIProvider(
            model="claude-3-sonnet",
            region="us-east-1"
        )
        
        super().__init__(
            name="TestAgent",
            version="1.0.0",
            memory_hub=memory_hub,
            document_context=document_context,
            ai_provider=ai_provider
        )
        
        self.config = config or {}
        self.persona = get_persona("TestAgent")
        self.capabilities = ["test", "analyze", "validate", "coverage"]
        
        # 지원하는 테스트 프레임워크
        self.supported_frameworks = {
            "python": ["pytest", "unittest", "nose2", "doctest"],
            "javascript": ["jest", "mocha", "jasmine", "vitest"],
            "typescript": ["jest", "mocha", "vitest"],
            "go": ["go test"],
            "java": ["junit", "testng"],
            "rust": ["cargo test"]
        }
        
    async def execute(self, task: AgentTask) -> AgentResult:
        """테스트 실행 및 분석
        
        Args:
            task: 테스트 실행 태스크
                - project_path: 프로젝트 경로
                - test_command: 테스트 명령 (선택사항)
                - coverage_threshold: 커버리지 임계값 (기본 80%)
                - test_pattern: 테스트 파일 패턴
            
        Returns:
            테스트 결과 및 분석
        """
        try:
            logger.info(f"[{self.persona.name}] 테스트 실행 시작...")
            
            project_path = task.inputs.get("project_path", ".")
            test_command = task.inputs.get("test_command")
            coverage_threshold = task.inputs.get("coverage_threshold", 80.0)
            
            # 1. 테스트 프레임워크 감지
            if not test_command:
                logger.info("테스트 프레임워크 자동 감지 중...")
                test_command = await self._detect_test_framework(project_path)
                logger.info(f"감지된 테스트 명령: {test_command}")
            
            # 2. 테스트 실행
            logger.info(f"테스트 실행: {test_command}")
            test_report = await self._run_tests(project_path, test_command)
            
            # 3. 커버리지 분석
            if test_report.coverage < coverage_threshold:
                test_report.recommendations.append(
                    f"⚠️ 테스트 커버리지({test_report.coverage:.1f}%)가 "
                    f"목표치({coverage_threshold}%)보다 낮습니다."
                )
            
            # 4. 실패한 테스트 AI 분석
            if test_report.failed > 0:
                logger.info(f"실패한 테스트 {test_report.failed}개 분석 중...")
                failure_analysis = await self._analyze_failures(test_report)
                test_report.recommendations.extend(failure_analysis)
            
            # 5. SharedDocumentContext에 결과 추가
            if self.document_context:
                self.document_context.add_document(
                    "TestAgent",
                    {
                        "test_report": test_report.__dict__,
                        "quality_status": "passed" if test_report.failed == 0 else "failed",
                        "coverage": test_report.coverage,
                        "framework": test_report.framework,
                        "timestamp": datetime.now().isoformat()
                    },
                    document_type="test_result"
                )
            
            # 6. 메모리 허브에 저장
            if self.memory_hub:
                from ..memory.context_types import ContextType
                await self.memory_hub.put(
                    ContextType.S_CTX,
                    f"test_report_{task.task_id}",
                    test_report.__dict__,
                    ttl_seconds=86400
                )
            
            # 성공 여부 결정
            success = test_report.failed == 0 and test_report.coverage >= coverage_threshold
            
            return AgentResult(
                success=success,
                data={
                    "tests_passed": test_report.passed,
                    "tests_failed": test_report.failed,
                    "tests_skipped": test_report.skipped,
                    "total_tests": test_report.total_tests,
                    "coverage": test_report.coverage,
                    "duration": test_report.test_duration,
                    "framework": test_report.framework,
                    "recommendations": test_report.recommendations,
                    "full_report": test_report.__dict__
                },
                message=f"{self.persona.catchphrase} - "
                       f"테스트: {test_report.passed}/{test_report.total_tests} 통과, "
                       f"커버리지: {test_report.coverage:.1f}%",
                metadata={
                    "agent": self.name,
                    "persona": self.persona.name,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"테스트 실행 실패: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                data={},
                message=f"테스트 실행 중 오류 발생: {e}"
            )
    
    async def _detect_test_framework(self, project_path: str) -> str:
        """테스트 프레임워크 자동 감지
        
        프로젝트의 설정 파일과 의존성을 분석하여
        적절한 테스트 명령을 자동으로 찾습니다.
        """
        path = Path(project_path)
        
        # Python 프로젝트
        if (path / "pytest.ini").exists() or (path / "setup.cfg").exists():
            return "pytest --cov=. --cov-report=term-missing -v"
        elif (path / "pyproject.toml").exists():
            with open(path / "pyproject.toml") as f:
                content = f.read()
                if "pytest" in content:
                    return "pytest --cov=. --cov-report=term-missing -v"
        elif (path / "manage.py").exists():  # Django
            return "python manage.py test --verbosity=2"
        elif (path / "setup.py").exists():
            return "python -m pytest"
        
        # JavaScript/TypeScript
        elif (path / "package.json").exists():
            with open(path / "package.json") as f:
                pkg = json.load(f)
                scripts = pkg.get("scripts", {})
                
                # package.json에 정의된 테스트 스크립트 사용
                if "test" in scripts:
                    return "npm test"
                elif "test:coverage" in scripts:
                    return "npm run test:coverage"
                    
                # 의존성 기반 감지
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "jest" in deps:
                    return "npx jest --coverage"
                elif "mocha" in deps:
                    return "npx mocha --recursive"
                elif "vitest" in deps:
                    return "npx vitest run --coverage"
        
        # Go 프로젝트
        elif (path / "go.mod").exists():
            return "go test -v -cover ./..."
        
        # Rust 프로젝트
        elif (path / "Cargo.toml").exists():
            return "cargo test --verbose"
        
        # Java 프로젝트
        elif (path / "pom.xml").exists():  # Maven
            return "mvn test"
        elif (path / "build.gradle").exists():  # Gradle
            return "gradle test"
        
        # 기본값 (Python pytest)
        logger.warning("테스트 프레임워크를 감지할 수 없습니다. pytest를 시도합니다.")
        return "pytest"
    
    async def _run_tests(self, project_path: str, command: str) -> TestReport:
        """테스트 실행
        
        지정된 명령으로 테스트를 실행하고 결과를 파싱합니다.
        """
        import time
        start_time = time.time()
        
        report = TestReport()
        report.framework = self._identify_framework(command)
        
        try:
            # 테스트 실행
            logger.info(f"실행 명령: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            report.test_duration = time.time() - start_time
            report.test_output = result.stdout + result.stderr
            
            # 결과 파싱
            report = self._parse_test_output(report, report.test_output)
            
            return report
            
        except subprocess.TimeoutExpired:
            report.test_output = "테스트 실행 타임아웃 (5분 초과)"
            report.test_duration = 300
            report.recommendations.append("테스트 실행 시간이 너무 깁니다. 테스트 최적화가 필요합니다.")
            return report
            
        except Exception as e:
            report.test_output = f"테스트 실행 오류: {e}"
            report.recommendations.append(f"테스트 실행 환경을 확인하세요: {e}")
            return report
    
    def _identify_framework(self, command: str) -> str:
        """명령어에서 테스트 프레임워크 식별"""
        command_lower = command.lower()
        
        if "pytest" in command_lower:
            return "pytest"
        elif "unittest" in command_lower:
            return "unittest"
        elif "jest" in command_lower:
            return "jest"
        elif "mocha" in command_lower:
            return "mocha"
        elif "vitest" in command_lower:
            return "vitest"
        elif "go test" in command_lower:
            return "go"
        elif "cargo test" in command_lower:
            return "rust"
        elif "mvn test" in command_lower or "gradle test" in command_lower:
            return "java"
        else:
            return "unknown"
    
    def _parse_test_output(self, report: TestReport, output: str) -> TestReport:
        """테스트 출력 파싱
        
        각 테스트 프레임워크의 출력 형식에 맞게 결과를 파싱합니다.
        """
        # pytest 스타일 파싱
        if report.framework == "pytest" or "passed" in output or "failed" in output:
            # 예: "5 passed, 2 failed, 1 skipped in 3.24s"
            pattern = r'(\d+)\s+passed'
            match = re.search(pattern, output)
            if match:
                report.passed = int(match.group(1))
            
            pattern = r'(\d+)\s+failed'
            match = re.search(pattern, output)
            if match:
                report.failed = int(match.group(1))
            
            pattern = r'(\d+)\s+skipped'
            match = re.search(pattern, output)
            if match:
                report.skipped = int(match.group(1))
            
            # 커버리지 파싱 (pytest-cov)
            # 예: "TOTAL                     1234    567    54%"
            pattern = r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%'
            match = re.search(pattern, output)
            if match:
                report.lines_total = int(match.group(1))
                report.lines_covered = report.lines_total - int(match.group(2))
                report.coverage = float(match.group(3))
            
            # 실패한 테스트 추출
            if report.failed > 0:
                report.failed_tests = self._extract_failed_tests(output, "pytest")
        
        # Jest 스타일 파싱
        elif report.framework == "jest":
            # 예: "Tests:       2 failed, 5 passed, 7 total"
            pattern = r'Tests:\s+(\d+)\s+failed,\s+(\d+)\s+passed,\s+(\d+)\s+total'
            match = re.search(pattern, output)
            if match:
                report.failed = int(match.group(1))
                report.passed = int(match.group(2))
                report.total_tests = int(match.group(3))
            
            # 커버리지 파싱
            pattern = r'All files\s+\|\s+([\d.]+)\s+\|'
            match = re.search(pattern, output)
            if match:
                report.coverage = float(match.group(1))
        
        # Go test 스타일 파싱
        elif report.framework == "go":
            # PASS/FAIL 카운트
            report.passed = output.count("PASS")
            report.failed = output.count("FAIL")
            
            # 커버리지 파싱
            pattern = r'coverage:\s+([\d.]+)%'
            match = re.search(pattern, output)
            if match:
                report.coverage = float(match.group(1))
        
        # 총 테스트 수 계산
        report.total_tests = report.passed + report.failed + report.skipped
        
        return report
    
    def _extract_failed_tests(self, output: str, framework: str) -> List[Dict[str, Any]]:
        """실패한 테스트 정보 추출"""
        failed_tests = []
        
        if framework == "pytest":
            # FAILED 라인 찾기
            lines = output.split("\n")
            for i, line in enumerate(lines):
                if "FAILED" in line:
                    test_info = {
                        "name": line.split("FAILED")[0].strip(),
                        "error": ""
                    }
                    
                    # 에러 메시지 찾기 (다음 몇 줄)
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip():
                            test_info["error"] += lines[j] + "\n"
                        else:
                            break
                    
                    failed_tests.append(test_info)
        
        return failed_tests
    
    async def _analyze_failures(self, report: TestReport) -> List[str]:
        """실패한 테스트 AI 분석
        
        AI를 활용하여 테스트 실패 원인을 분석하고
        구체적인 해결 방안을 제시합니다.
        """
        if not self.ai_provider or not report.failed_tests:
            return ["테스트 출력을 확인하여 실패 원인을 파악하세요."]
        
        # 페르소나 적용
        persona_prompt = self.persona.to_prompt() if self.persona else ""
        
        # 현재 문서 컨텍스트 가져오기
        context = ""
        if self.document_context:
            all_docs = self.document_context.get_all_documents()
            # 관련 문서만 추출 (코드 변경, 태스크 등)
            relevant_docs = {
                k: v for k, v in all_docs.items()
                if k in ["CodeGenerator", "TaskCreatorAgent", "PlannerAgent"]
            }
            if relevant_docs:
                context = f"\n최근 변경사항:\n{json.dumps(relevant_docs, indent=2)[:2000]}"
        
        prompt = f"""{persona_prompt}

다음 테스트 실패를 분석하고 해결 방안을 제시하세요:

테스트 프레임워크: {report.framework}
실패한 테스트 수: {report.failed}
전체 테스트 수: {report.total_tests}

실패한 테스트들:
{json.dumps(report.failed_tests[:5], indent=2)}  # 최대 5개만

테스트 출력 (마지막 부분):
{report.test_output[-2000:]}  # 마지막 2000자
{context}

다음 형식으로 분석 결과를 제공하세요:
1. 주요 실패 원인 (한 줄 요약)
2. 구체적 해결 방안 (3개 이내)
3. 우선순위 (높음/중간/낮음)
4. 예상 수정 시간

JSON 형식으로 응답하세요:
{{
    "main_cause": "...",
    "solutions": ["solution1", "solution2", "solution3"],
    "priority": "high|medium|low",
    "estimated_time": "5-10 minutes"
}}
"""
        
        try:
            response = await self.ai_provider.complete(prompt)
            analysis = json.loads(response)
            
            recommendations = [
                f"🔍 주요 원인: {analysis.get('main_cause', '분석 실패')}",
                f"⚡ 우선순위: {analysis.get('priority', 'medium')}",
                f"⏱️ 예상 시간: {analysis.get('estimated_time', '알 수 없음')}"
            ]
            
            for i, solution in enumerate(analysis.get('solutions', []), 1):
                recommendations.append(f"  {i}. {solution}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"AI 분석 실패: {e}")
            return [
                "AI 분석이 실패했습니다. 테스트 출력을 직접 확인하세요.",
                f"에러: {str(e)}"
            ]
    
    async def generate_test_improvement_plan(self) -> Dict[str, Any]:
        """테스트 개선 계획 생성
        
        현재 테스트 상태를 분석하고 개선 계획을 수립합니다.
        """
        if not self.document_context:
            return {"error": "No document context available"}
        
        # 모든 테스트 관련 문서 수집
        all_docs = self.document_context.get_all_documents()
        test_docs = {k: v for k, v in all_docs.items() if "test" in k.lower()}
        
        if not test_docs:
            return {"message": "No test documents found"}
        
        # AI를 활용한 개선 계획 수립
        if self.ai_provider:
            prompt = f"""{self.persona.to_prompt() if self.persona else ''}

현재 테스트 상태를 분석하고 개선 계획을 수립하세요:

테스트 문서들:
{json.dumps(test_docs, indent=2)[:3000]}

다음을 포함한 개선 계획을 작성하세요:
1. 현재 테스트 커버리지 상태
2. 부족한 테스트 영역
3. 테스트 품질 개선 방안
4. 구체적 실행 계획

JSON 형식으로 응답하세요.
"""
            
            try:
                response = await self.ai_provider.complete(prompt)
                return json.loads(response)
            except Exception as e:
                logger.error(f"개선 계획 생성 실패: {e}")
                return {"error": str(e)}
        
        return {"message": "AI provider not available"}