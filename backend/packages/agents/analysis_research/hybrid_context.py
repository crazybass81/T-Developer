"""
Hybrid Context Analyzer Agent for T-Developer v2.

경험 기반 정적 분석과 선택적 AI 분석을 결합한 하이브리드 접근 방식.
AI는 복잡한 케이스나 낮은 신뢰도 상황에서만 사용됩니다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from backend.core.shared_context import SharedContextStore
from backend.packages.agents.base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent


# ContextAnalysis를 직접 정의 (의존성 문제 해결)
@dataclass
class ContextAnalysis:
    """컨텍스트 분석 결과."""

    analysis_id: str
    context_type: str
    relevance_score: float
    key_elements: list[str]
    dependencies: list[str]
    risks: list[str]
    recommendations: list[str]
    patterns_detected: list[str]
    metadata: dict[str, Any]


logger = logging.getLogger(__name__)


@dataclass
class ConfidenceScore:
    """분석 결과의 신뢰도 점수."""

    score: float  # 0.0 - 1.0
    reasons: list[str]
    requires_ai: bool

    def is_high_confidence(self) -> bool:
        """높은 신뢰도인지 확인."""
        return self.score >= 0.8

    def is_low_confidence(self) -> bool:
        """낮은 신뢰도인지 확인."""
        return self.score < 0.6


@dataclass
class HybridAnalysisResult:
    """하이브리드 분석 결과."""

    static_analysis: dict[str, Any]
    memory_insights: dict[str, Any]
    ai_analysis: Optional[dict[str, Any]] = None
    confidence: Optional[ConfidenceScore] = None
    recommendations: list[str] = None

    def merge_results(self) -> dict[str, Any]:
        """모든 분석 결과 병합."""
        merged = {
            "static": self.static_analysis,
            "memory": self.memory_insights,
            "confidence": self.confidence.score if self.confidence else 0.0,
        }

        if self.ai_analysis:
            merged["ai"] = self.ai_analysis

        if self.recommendations:
            merged["recommendations"] = self.recommendations

        return merged


class HybridContextAnalyzer(BaseAgent):
    """
    하이브리드 컨텍스트 분석기.

    분석 전략:
    1. 항상: 정적 분석 (AST, 메트릭, 패턴)
    2. 항상: 메모리 기반 분석 (과거 경험)
    3. 선택적: AI 분석 (복잡하거나 신뢰도 낮을 때)

    AI 사용 기준:
    - 정적 분석 신뢰도 < 60%
    - 복잡도 매우 높음 (>100)
    - 새로운 패턴 발견
    - 사용자 명시적 요청
    """

    # AI 모델 설정 (빠르고 저렴한 모델 사용)
    AI_MODEL = "claude-3-haiku-20240307"  # 빠른 응답, 낮은 비용
    AI_TIMEOUT = 10  # 10초 타임아웃

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """하이브리드 분석기 초기화."""
        super().__init__(config or {})
        self.context_store = SharedContextStore()

        # AI 사용 설정
        self.ai_enabled = config.get("ai_enabled", True) if config else True
        self.ai_threshold = config.get("ai_threshold", 0.6) if config else 0.6
        self.ai_cache = {}  # AI 응답 캐시

        # 패턴 라이브러리
        self.pattern_library = self._load_pattern_library()

        # 메트릭
        self.static_analysis_count = 0
        self.ai_analysis_count = 0
        self.cache_hits = 0

    async def execute(self, input: AgentInput) -> AgentOutput:
        """하이브리드 분석 실행."""
        try:
            target = input.payload.get("target", "")
            analysis_type = input.payload.get("type", "code")
            force_ai = input.payload.get("force_ai", False)

            logger.info(f"Starting hybrid analysis: {analysis_type} on {target}")

            # Phase 1: 정적 분석 (항상 실행)
            static_result = await self._perform_static_analysis(target, analysis_type)
            self.static_analysis_count += 1

            # Phase 2: 메모리 기반 분석 (항상 실행)
            memory_result = await self._perform_memory_analysis(target, analysis_type)

            # Phase 3: 신뢰도 평가
            confidence = self._evaluate_confidence(static_result, memory_result)

            # Phase 4: AI 분석 (선택적)
            ai_result = None
            if self._should_use_ai(confidence, force_ai):
                ai_result = await self._perform_ai_analysis(
                    target, analysis_type, static_result, memory_result
                )
                self.ai_analysis_count += 1

                # AI 결과로 신뢰도 재평가
                confidence = self._reevaluate_confidence(confidence, ai_result)

            # Phase 5: 통합 및 권장사항 생성
            recommendations = self._generate_recommendations(
                static_result, memory_result, ai_result, confidence
            )

            # 결과 조합
            hybrid_result = HybridAnalysisResult(
                static_analysis=static_result,
                memory_insights=memory_result,
                ai_analysis=ai_result,
                confidence=confidence,
                recommendations=recommendations,
            )

            # 결과 저장
            await self._store_analysis_result(target, hybrid_result)

            # 응답 생성
            artifact = Artifact(
                kind="analysis", ref="hybrid_analysis", content=hybrid_result.merge_results()
            )

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[artifact],
                metrics={
                    "confidence": confidence.score,
                    "ai_used": ai_result is not None,
                    "static_count": self.static_analysis_count,
                    "ai_count": self.ai_analysis_count,
                    "cache_hits": self.cache_hits,
                },
            )

        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    async def _perform_static_analysis(self, target: str, analysis_type: str) -> dict[str, Any]:
        """정적 분석 수행."""
        result = {"type": analysis_type, "target": target, "timestamp": datetime.now().isoformat()}

        if analysis_type == "code" and Path(target).exists():
            with open(target) as f:
                content = f.read()

            # AST 분석
            result["ast"] = self._analyze_ast(content)

            # 메트릭 계산
            result["metrics"] = self._calculate_metrics(content)

            # 패턴 탐지
            result["patterns"] = self._detect_patterns(content)

            # 코드 스멜 탐지
            result["code_smells"] = self._detect_code_smells(content)

            # 복잡도 분석
            result["complexity"] = self._analyze_complexity(content)

        elif analysis_type == "architecture":
            # 아키텍처 분석
            result["components"] = self._analyze_architecture(target)
            result["dependencies"] = self._analyze_dependencies(target)

        elif analysis_type == "performance":
            # 성능 분석
            result["bottlenecks"] = self._find_bottlenecks(target)
            result["optimizations"] = self._suggest_optimizations(target)

        return result

    async def _perform_memory_analysis(self, target: str, analysis_type: str) -> dict[str, Any]:
        """메모리 기반 분석 수행."""
        try:
            # MemoryCurator import 회피 (의존성 문제)
            # 대신 SharedContext에서 과거 분석 조회
            contexts = await self.context_store.get_all_contexts()

            relevant_memories = []
            for ctx in contexts[-10:]:  # 최근 10개만
                if ctx.original_analysis:
                    relevant_memories.append(
                        {
                            "id": ctx.evolution_id,
                            "timestamp": ctx.created_at.isoformat(),
                            "insights": ctx.original_analysis.get("summary", {}),
                        }
                    )

            return {
                "relevant_memories": len(relevant_memories),
                "past_patterns": self._extract_patterns_from_memories(relevant_memories),
                "success_indicators": self._find_success_indicators(relevant_memories),
                "failure_warnings": self._find_failure_warnings(relevant_memories),
            }

        except Exception as e:
            logger.warning(f"Memory analysis failed: {e}")
            return {"error": str(e), "relevant_memories": 0}

    def _evaluate_confidence(
        self, static_result: dict[str, Any], memory_result: dict[str, Any]
    ) -> ConfidenceScore:
        """분석 결과의 신뢰도 평가."""
        score = 0.5  # 기본 점수
        reasons = []

        # 정적 분석 품질 평가
        if static_result.get("metrics"):
            score += 0.2
            reasons.append("메트릭 계산 성공")

        if static_result.get("patterns"):
            pattern_count = len(static_result["patterns"])
            if pattern_count > 5:
                score += 0.15
                reasons.append(f"{pattern_count}개 패턴 발견")

        # 복잡도 평가
        complexity = static_result.get("complexity", {})
        if complexity.get("cyclomatic", 0) > 50:
            score -= 0.2
            reasons.append("매우 높은 복잡도")
        elif complexity.get("cyclomatic", 0) < 10:
            score += 0.1
            reasons.append("낮은 복잡도")

        # 메모리 인사이트 평가
        if memory_result.get("relevant_memories", 0) > 5:
            score += 0.15
            reasons.append("풍부한 과거 경험")

        # 코드 스멜 평가
        code_smells = static_result.get("code_smells", [])
        if len(code_smells) > 10:
            score -= 0.15
            reasons.append("많은 코드 스멜 발견")

        # 점수 정규화
        score = max(0.0, min(1.0, score))

        # AI 필요 여부 결정
        requires_ai = (
            score < self.ai_threshold
            or complexity.get("cyclomatic", 0) > 100
            or "새로운 패턴" in " ".join(reasons)
        )

        return ConfidenceScore(score=score, reasons=reasons, requires_ai=requires_ai)

    def _should_use_ai(self, confidence: ConfidenceScore, force_ai: bool) -> bool:
        """AI 사용 여부 결정."""
        if not self.ai_enabled:
            return False

        if force_ai:
            return True

        return confidence.requires_ai or confidence.is_low_confidence()

    async def _perform_ai_analysis(
        self,
        target: str,
        analysis_type: str,
        static_result: dict[str, Any],
        memory_result: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """AI 기반 분석 수행."""
        # 캐시 확인
        cache_key = f"{target}:{analysis_type}"
        if cache_key in self.ai_cache:
            self.cache_hits += 1
            return self.ai_cache[cache_key]

        try:
            # Anthropic API 사용
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set, skipping AI analysis")
                return None

            import anthropic

            client = anthropic.AsyncAnthropic(api_key=api_key)

            # 프롬프트 생성
            prompt = self._create_ai_prompt(target, analysis_type, static_result, memory_result)

            # AI 호출 (타임아웃 적용)
            response = await asyncio.wait_for(
                client.messages.create(
                    model=self.AI_MODEL,
                    max_tokens=1000,
                    temperature=0.3,  # 일관성 있는 분석을 위해 낮은 temperature
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=self.AI_TIMEOUT,
            )

            # 응답 파싱
            ai_result = self._parse_ai_response(response.content[0].text)

            # 캐시 저장
            self.ai_cache[cache_key] = ai_result

            return ai_result

        except asyncio.TimeoutError:
            logger.warning("AI analysis timed out")
            return {"error": "timeout", "fallback": "static_only"}
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": str(e), "fallback": "static_only"}

    def _create_ai_prompt(
        self,
        target: str,
        analysis_type: str,
        static_result: dict[str, Any],
        memory_result: dict[str, Any],
    ) -> str:
        """AI 분석을 위한 프롬프트 생성."""
        prompt = f"""코드 분석 전문가로서 다음을 분석해주세요:

타겟: {target}
분석 유형: {analysis_type}

정적 분석 결과:
- 발견된 패턴: {len(static_result.get('patterns', []))}개
- 복잡도: {static_result.get('complexity', {}).get('cyclomatic', 'N/A')}
- 코드 스멜: {len(static_result.get('code_smells', []))}개

과거 경험:
- 관련 메모리: {memory_result.get('relevant_memories', 0)}개
- 성공 지표: {memory_result.get('success_indicators', [])}

다음을 JSON 형식으로 제공하세요:
1. hidden_issues: 정적 분석이 놓친 숨겨진 문제들
2. improvement_suggestions: 구체적인 개선 제안
3. risk_assessment: 위험도 평가 (low/medium/high)
4. architectural_insights: 아키텍처 레벨 인사이트
5. confidence_boost: 이 분석이 신뢰도를 얼마나 높이는지 (0.0-1.0)

JSON만 반환하고 다른 텍스트는 포함하지 마세요."""

        return prompt

    def _parse_ai_response(self, response_text: str) -> dict[str, Any]:
        """AI 응답 파싱."""
        try:
            # JSON 부분 추출
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # JSON이 없으면 텍스트를 구조화
                return {"raw_response": response_text, "parsed": False}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return {"raw_response": response_text, "error": str(e), "parsed": False}

    def _reevaluate_confidence(
        self, original: ConfidenceScore, ai_result: Optional[dict[str, Any]]
    ) -> ConfidenceScore:
        """AI 결과를 반영한 신뢰도 재평가."""
        if not ai_result or "error" in ai_result:
            return original

        # AI가 제공한 신뢰도 부스트 적용
        boost = ai_result.get("confidence_boost", 0.0)
        new_score = min(1.0, original.score + boost)

        new_reasons = original.reasons.copy()
        new_reasons.append(f"AI 분석 완료 (+{boost:.2f})")

        return ConfidenceScore(score=new_score, reasons=new_reasons, requires_ai=False)  # 이미 AI 사용함

    def _generate_recommendations(
        self,
        static_result: dict[str, Any],
        memory_result: dict[str, Any],
        ai_result: Optional[dict[str, Any]],
        confidence: ConfidenceScore,
    ) -> list[str]:
        """통합 권장사항 생성."""
        recommendations = []

        # 정적 분석 기반 권장사항
        if static_result.get("code_smells"):
            recommendations.append("발견된 코드 스멜을 리팩토링하세요")

        complexity = static_result.get("complexity", {})
        if complexity.get("cyclomatic", 0) > 20:
            recommendations.append("복잡한 함수를 더 작은 단위로 분해하세요")

        # 메모리 기반 권장사항
        if memory_result.get("failure_warnings"):
            recommendations.append("과거 실패 패턴이 감지되었습니다. 주의가 필요합니다")

        if memory_result.get("success_indicators"):
            recommendations.append("과거 성공 패턴을 참고하여 구현하세요")

        # AI 기반 권장사항 (있는 경우)
        if ai_result and not ai_result.get("error"):
            ai_suggestions = ai_result.get("improvement_suggestions", [])
            if isinstance(ai_suggestions, list):
                recommendations.extend(ai_suggestions[:3])  # 상위 3개만

            risk = ai_result.get("risk_assessment")
            if risk == "high":
                recommendations.insert(0, "⚠️ 높은 위험도 감지 - 신중한 검토 필요")

        # 신뢰도 기반 권장사항
        if confidence.is_low_confidence():
            recommendations.append("신뢰도가 낮습니다. 수동 검토를 권장합니다")

        return recommendations[:10]  # 최대 10개 권장사항

    async def _store_analysis_result(self, target: str, result: HybridAnalysisResult) -> None:
        """분석 결과 저장."""
        try:
            # SharedContext에 저장
            context_id = await self.context_store.create_context(
                f"hybrid_{datetime.now().timestamp()}"
            )

            await self.context_store.store_original_analysis(
                result.merge_results(), evolution_id=context_id
            )

            logger.debug(f"Stored hybrid analysis result for {target}")

        except Exception as e:
            logger.error(f"Failed to store analysis result: {e}")

    # === 정적 분석 헬퍼 메서드들 ===

    def _analyze_ast(self, content: str) -> dict[str, Any]:
        """AST 분석."""
        import ast

        try:
            tree = ast.parse(content)
            return {
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "async_functions": len(
                    [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
                ),
            }
        except SyntaxError:
            return {"error": "syntax_error"}

    def _calculate_metrics(self, content: str) -> dict[str, Any]:
        """코드 메트릭 계산."""
        lines = content.split("\n")
        return {
            "loc": len(lines),
            "sloc": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "comments": len([l for l in lines if l.strip().startswith("#")]),
            "docstrings": content.count('"""'),
        }

    def _detect_patterns(self, content: str) -> list[str]:
        """패턴 탐지."""
        patterns = []
        for name, regex in self.pattern_library.items():
            if re.search(regex, content):
                patterns.append(name)
        return patterns

    def _detect_code_smells(self, content: str) -> list[dict[str, Any]]:
        """코드 스멜 탐지."""
        smells = []

        # Long method
        for match in re.finditer(r"def\s+\w+.*?(?=\n(?:def|class|\Z))", content, re.DOTALL):
            if len(match.group().split("\n")) > 50:
                smells.append(
                    {"type": "long_method", "line": content[: match.start()].count("\n") + 1}
                )

        # Duplicate code (simplified)
        lines = content.split("\n")
        for i in range(len(lines) - 5):
            block = "\n".join(lines[i : i + 5])
            if content.count(block) > 1 and len(block) > 100:
                smells.append({"type": "duplicate_code", "line": i + 1})
                break

        return smells

    def _analyze_complexity(self, content: str) -> dict[str, Any]:
        """복잡도 분석."""
        # Simplified cyclomatic complexity
        conditions = len(re.findall(r"\b(if|elif|for|while|except)\b", content))
        functions = len(re.findall(r"\bdef\s+\w+", content))

        cyclomatic = conditions + 1
        avg_complexity = cyclomatic / max(functions, 1)

        return {
            "cyclomatic": cyclomatic,
            "average": avg_complexity,
            "rating": "high" if avg_complexity > 10 else "medium" if avg_complexity > 5 else "low",
        }

    def _analyze_architecture(self, target: str) -> list[str]:
        """아키텍처 컴포넌트 분석."""
        # Simplified architecture analysis
        components = []
        if Path(target).is_dir():
            for file in Path(target).rglob("*.py"):
                if "agent" in file.name.lower():
                    components.append(f"agent:{file.stem}")
                elif "service" in file.name.lower():
                    components.append(f"service:{file.stem}")
                elif "model" in file.name.lower():
                    components.append(f"model:{file.stem}")
        return components

    def _analyze_dependencies(self, target: str) -> dict[str, list[str]]:
        """의존성 분석."""
        deps = {"internal": [], "external": []}

        if Path(target).exists() and target.endswith(".py"):
            with open(target) as f:
                content = f.read()

            for match in re.finditer(r"^import\s+(\S+)", content, re.MULTILINE):
                module = match.group(1)
                if module.startswith("backend") or module.startswith("packages"):
                    deps["internal"].append(module)
                else:
                    deps["external"].append(module)

            for match in re.finditer(r"^from\s+(\S+)\s+import", content, re.MULTILINE):
                module = match.group(1)
                if module.startswith("backend") or module.startswith("packages"):
                    deps["internal"].append(module)
                else:
                    deps["external"].append(module)

        return deps

    def _find_bottlenecks(self, target: str) -> list[str]:
        """성능 병목 지점 찾기."""
        bottlenecks = []

        if Path(target).exists() and target.endswith(".py"):
            with open(target) as f:
                content = f.read()

            # Nested loops
            if re.search(r"for.*?\n.*?for", content, re.DOTALL):
                bottlenecks.append("nested_loops")

            # Synchronous I/O in async function
            if re.search(r"async def.*?open\(", content, re.DOTALL):
                bottlenecks.append("sync_io_in_async")

            # Large list comprehensions
            if re.search(r"\[.*?for.*?for.*?\]", content):
                bottlenecks.append("complex_list_comprehension")

        return bottlenecks

    def _suggest_optimizations(self, target: str) -> list[str]:
        """최적화 제안."""
        suggestions = []
        bottlenecks = self._find_bottlenecks(target)

        if "nested_loops" in bottlenecks:
            suggestions.append("중첩 루프를 벡터화하거나 더 효율적인 알고리즘 사용")

        if "sync_io_in_async" in bottlenecks:
            suggestions.append("비동기 함수에서 aiofiles 등 비동기 I/O 사용")

        if "complex_list_comprehension" in bottlenecks:
            suggestions.append("복잡한 리스트 컴프리헨션을 제너레이터로 변경")

        return suggestions

    def _extract_patterns_from_memories(self, memories: list[dict[str, Any]]) -> list[str]:
        """메모리에서 패턴 추출."""
        patterns = []
        for memory in memories:
            insights = memory.get("insights", {})
            if "patterns" in insights:
                patterns.extend(insights["patterns"])
        return list(set(patterns))[:10]

    def _find_success_indicators(self, memories: list[dict[str, Any]]) -> list[str]:
        """성공 지표 찾기."""
        indicators = []
        for memory in memories:
            insights = memory.get("insights", {})
            if insights.get("success", False):
                indicators.append(f"Success in {memory.get('id', 'unknown')}")
        return indicators[:5]

    def _find_failure_warnings(self, memories: list[dict[str, Any]]) -> list[str]:
        """실패 경고 찾기."""
        warnings = []
        for memory in memories:
            insights = memory.get("insights", {})
            if insights.get("failed", False):
                warnings.append(f"Failure pattern from {memory.get('id', 'unknown')}")
        return warnings[:5]

    def _load_pattern_library(self) -> dict[str, str]:
        """패턴 탐지 라이브러리 로드."""
        return {
            "singleton": r"class\s+\w+.*:\s*_instance\s*=\s*None",
            "factory": r"class\s+\w*Factory",
            "observer": r"class\s+\w*Observer",
            "strategy": r"class\s+\w*Strategy",
            "decorator": r"@\w+",
            "context_manager": r"__enter__.*__exit__",
            "generator": r"\byield\b",
            "async_pattern": r"async\s+def",
            "type_hints": r":\s*(?:str|int|float|bool|List|Dict|Optional)",
            "dataclass": r"@dataclass",
        }

    async def validate(self, output: AgentOutput) -> bool:
        """에이전트 출력 검증."""
        if output.status != AgentStatus.OK:
            return False

        if not output.artifacts:
            return False

        # 신뢰도 점수가 있는지 확인
        if "confidence" not in output.metrics:
            return False

        return True

    def get_capabilities(self) -> dict[str, Any]:
        """에이전트 능력 반환."""
        return {
            "name": "HybridContextAnalyzer",
            "version": "1.0.0",
            "description": "경험 기반 정적 분석과 선택적 AI를 결합한 하이브리드 분석기",
            "features": [
                "정적 코드 분석 (AST, 메트릭, 패턴)",
                "메모리 기반 경험 활용",
                "선택적 AI 분석 (낮은 신뢰도 시)",
                "신뢰도 평가 시스템",
                "통합 권장사항 생성",
                "AI 응답 캐싱",
            ],
            "ai_model": self.AI_MODEL,
            "ai_threshold": self.ai_threshold,
            "metrics": {
                "static_analysis_count": self.static_analysis_count,
                "ai_analysis_count": self.ai_analysis_count,
                "cache_hits": self.cache_hits,
                "ai_usage_rate": self.ai_analysis_count / max(self.static_analysis_count, 1),
            },
        }
