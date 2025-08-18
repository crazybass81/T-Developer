"""
AI 분석을 위한 템플릿과 목적 정의.

각 분석 유형별로 명확한 목적, 범위, 기대 결과를 사전 정의하여
AI가 일관되고 효과적인 분석을 수행할 수 있도록 합니다.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class AnalysisType(Enum):
    """분석 유형 정의."""

    # 코드 분석
    CODE_QUALITY = "code_quality"  # 코드 품질 평가
    SECURITY_AUDIT = "security_audit"  # 보안 취약점 분석
    PERFORMANCE_REVIEW = "performance_review"  # 성능 병목 분석
    REFACTORING = "refactoring"  # 리팩토링 제안
    BUG_ANALYSIS = "bug_analysis"  # 버그 원인 분석

    # 아키텍처 분석
    ARCHITECTURE_REVIEW = "architecture_review"  # 아키텍처 평가
    DESIGN_PATTERNS = "design_patterns"  # 디자인 패턴 적용
    SCALABILITY = "scalability"  # 확장성 분석
    DEPENDENCY_ANALYSIS = "dependency_analysis"  # 의존성 분석

    # 리서치 분석
    SOLUTION_COMPARISON = "solution_comparison"  # 솔루션 비교
    TECHNOLOGY_SELECTION = "technology_selection"  # 기술 선택
    IMPLEMENTATION_GUIDE = "implementation_guide"  # 구현 가이드
    TREND_ANALYSIS = "trend_analysis"  # 트렌드 분석
    COST_BENEFIT = "cost_benefit"  # 비용-효익 분석


@dataclass
class AnalysisTemplate:
    """분석 템플릿."""

    type: AnalysisType
    purpose: str  # 분석 목적
    scope: list[str]  # 분석 범위
    key_questions: list[str]  # 핵심 질문들
    expected_outputs: list[str]  # 기대 산출물
    evaluation_criteria: dict[str, Any]  # 평가 기준
    max_depth: int = 3  # 분석 깊이
    time_budget: int = 30  # 시간 예산 (초)
    priority_focus: Optional[list[str]] = None  # 우선순위 초점


class AnalysisTemplateLibrary:
    """분석 템플릿 라이브러리."""

    @staticmethod
    def get_template(analysis_type: AnalysisType) -> AnalysisTemplate:
        """분석 유형별 템플릿 반환."""

        templates = {
            # ===== 코드 분석 템플릿 =====
            AnalysisType.CODE_QUALITY: AnalysisTemplate(
                type=AnalysisType.CODE_QUALITY,
                purpose="코드 품질을 종합적으로 평가하고 개선점을 도출",
                scope=[
                    "코드 복잡도 (Cyclomatic, Cognitive)",
                    "코드 중복도",
                    "명명 규칙 준수",
                    "SOLID 원칙 준수",
                    "테스트 커버리지",
                    "문서화 수준",
                ],
                key_questions=[
                    "이 코드의 주요 품질 문제는 무엇인가?",
                    "가장 시급한 개선사항 3가지는?",
                    "리팩토링이 필요한 핫스팟은 어디인가?",
                    "테스트 가능성은 어느 정도인가?",
                    "유지보수성 점수는 몇 점인가?",
                ],
                expected_outputs=[
                    "품질 점수 (0-100)",
                    "우선순위별 개선사항 목록",
                    "리팩토링 대상 함수/클래스",
                    "코드 스멜 목록",
                    "구체적 개선 예시 코드",
                ],
                evaluation_criteria={
                    "complexity_threshold": 10,
                    "duplication_threshold": 5,
                    "coverage_target": 80,
                    "documentation_target": 70,
                },
                priority_focus=["complexity", "duplication", "testability"],
            ),
            AnalysisType.SECURITY_AUDIT: AnalysisTemplate(
                type=AnalysisType.SECURITY_AUDIT,
                purpose="보안 취약점을 식별하고 해결 방안 제시",
                scope=[
                    "OWASP Top 10 취약점",
                    "인증/인가 문제",
                    "입력 검증",
                    "SQL Injection",
                    "XSS 취약점",
                    "민감 정보 노출",
                    "암호화 미적용",
                ],
                key_questions=[
                    "어떤 보안 취약점이 존재하는가?",
                    "각 취약점의 심각도는?",
                    "즉시 패치가 필요한 취약점은?",
                    "보안 모범 사례를 따르고 있는가?",
                    "컴플라이언스 요구사항을 충족하는가?",
                ],
                expected_outputs=["취약점 목록 (심각도별)", "CVE 매핑", "패치 우선순위", "보안 패치 코드", "보안 체크리스트"],
                evaluation_criteria={
                    "severity_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    "compliance_standards": ["OWASP", "CWE", "SANS"],
                    "immediate_action_threshold": "HIGH",
                },
                max_depth=5,
                priority_focus=["authentication", "injection", "data_exposure"],
            ),
            AnalysisType.PERFORMANCE_REVIEW: AnalysisTemplate(
                type=AnalysisType.PERFORMANCE_REVIEW,
                purpose="성능 병목 지점을 찾고 최적화 방안 제시",
                scope=[
                    "시간 복잡도",
                    "공간 복잡도",
                    "데이터베이스 쿼리",
                    "API 호출 패턴",
                    "캐싱 기회",
                    "비동기 처리 가능성",
                    "리소스 사용량",
                ],
                key_questions=[
                    "주요 성능 병목은 어디인가?",
                    "O(n²) 이상의 복잡도를 가진 로직은?",
                    "N+1 쿼리 문제가 있는가?",
                    "캐싱으로 개선 가능한 부분은?",
                    "병렬 처리 가능한 작업은?",
                ],
                expected_outputs=[
                    "병목 지점 Top 5",
                    "복잡도 분석 결과",
                    "최적화 제안 (예상 개선율)",
                    "캐싱 전략",
                    "벤치마크 코드",
                ],
                evaluation_criteria={
                    "acceptable_complexity": "O(n log n)",
                    "query_limit": 10,
                    "response_time_target": 200,  # ms
                    "memory_limit": 512,  # MB
                },
                priority_focus=["time_complexity", "database_queries", "caching"],
            ),
            AnalysisType.BUG_ANALYSIS: AnalysisTemplate(
                type=AnalysisType.BUG_ANALYSIS,
                purpose="버그의 근본 원인을 분석하고 해결책 제시",
                scope=["에러 스택 트레이스", "변수 상태 추적", "경계 조건", "동시성 문제", "타입 불일치", "null/undefined 처리"],
                key_questions=[
                    "버그의 근본 원인은 무엇인가?",
                    "어떤 조건에서 재현되는가?",
                    "관련된 다른 잠재 버그는?",
                    "왜 테스트에서 발견되지 않았는가?",
                    "유사한 패턴의 버그가 다른 곳에도 있는가?",
                ],
                expected_outputs=["근본 원인 분석 (RCA)", "재현 단계", "수정 코드", "회귀 테스트 케이스", "예방 조치"],
                evaluation_criteria={
                    "root_cause_confidence": 0.8,
                    "fix_verification": True,
                    "test_coverage_increase": 5,
                },
                max_depth=5,
            ),
            # ===== 아키텍처 분석 템플릿 =====
            AnalysisType.ARCHITECTURE_REVIEW: AnalysisTemplate(
                type=AnalysisType.ARCHITECTURE_REVIEW,
                purpose="시스템 아키텍처를 평가하고 개선 방향 제시",
                scope=["레이어 분리", "모듈 결합도", "의존성 방향", "확장 포인트", "인터페이스 설계", "데이터 흐름"],
                key_questions=[
                    "아키텍처가 SOLID 원칙을 따르는가?",
                    "순환 의존성이 있는가?",
                    "확장성 병목은 어디인가?",
                    "마이크로서비스로 분리 가능한가?",
                    "기술 부채는 얼마나 되는가?",
                ],
                expected_outputs=["아키텍처 다이어그램", "의존성 그래프", "개선 로드맵", "리팩토링 우선순위", "마이그레이션 전략"],
                evaluation_criteria={
                    "coupling_threshold": 0.3,
                    "cohesion_target": 0.8,
                    "cyclic_dependencies": 0,
                    "interface_segregation": True,
                },
                max_depth=4,
                priority_focus=["coupling", "scalability", "maintainability"],
            ),
            AnalysisType.DESIGN_PATTERNS: AnalysisTemplate(
                type=AnalysisType.DESIGN_PATTERNS,
                purpose="적절한 디자인 패턴 적용 기회 식별",
                scope=["GoF 패턴", "아키텍처 패턴", "동시성 패턴", "클라우드 패턴", "안티패턴 탐지"],
                key_questions=[
                    "어떤 디자인 패턴이 적용되어 있는가?",
                    "추가로 적용 가능한 패턴은?",
                    "안티패턴이 있는가?",
                    "과도한 패턴 사용(over-engineering)은 없는가?",
                    "패턴이 문제를 올바르게 해결하는가?",
                ],
                expected_outputs=[
                    "현재 패턴 목록",
                    "추천 패턴 (적용 위치)",
                    "안티패턴 제거 방안",
                    "패턴 적용 예시 코드",
                    "트레이드오프 분석",
                ],
                evaluation_criteria={
                    "pattern_appropriateness": 0.8,
                    "complexity_increase": 0.2,
                    "maintainability_improvement": 0.3,
                },
            ),
            # ===== 리서치 분석 템플릿 =====
            AnalysisType.SOLUTION_COMPARISON: AnalysisTemplate(
                type=AnalysisType.SOLUTION_COMPARISON,
                purpose="여러 솔루션을 비교 분석하여 최적안 도출",
                scope=["기능 완성도", "성능 벤치마크", "커뮤니티 활성도", "라이선스", "학습 곡선", "유지보수성", "비용"],
                key_questions=[
                    "각 솔루션의 핵심 장단점은?",
                    "우리 요구사항에 가장 적합한 것은?",
                    "장기적 관점에서 최선의 선택은?",
                    "마이그레이션 비용은 얼마나 되는가?",
                    "벤더 락인 위험은 있는가?",
                ],
                expected_outputs=["비교 매트릭스", "점수 기반 순위", "추천 솔루션 + 근거", "POC 계획", "리스크 분석"],
                evaluation_criteria={
                    "weights": {
                        "functionality": 0.3,
                        "performance": 0.2,
                        "community": 0.2,
                        "cost": 0.15,
                        "maintainability": 0.15,
                    },
                    "minimum_score": 0.7,
                },
                priority_focus=["functionality", "long_term_viability", "cost"],
            ),
            AnalysisType.TECHNOLOGY_SELECTION: AnalysisTemplate(
                type=AnalysisType.TECHNOLOGY_SELECTION,
                purpose="프로젝트에 적합한 기술 스택 선정",
                scope=["프로그래밍 언어", "프레임워크", "데이터베이스", "메시지 큐", "캐시 솔루션", "모니터링 도구", "CI/CD 도구"],
                key_questions=[
                    "팀의 기술 역량과 맞는가?",
                    "확장성 요구사항을 충족하는가?",
                    "생태계가 충분히 성숙했는가?",
                    "한국 시장에서 인력 수급이 가능한가?",
                    "총 소유 비용(TCO)은 얼마인가?",
                ],
                expected_outputs=["기술 스택 구성", "선정 근거", "대안 스택", "교육 계획", "도입 로드맵"],
                evaluation_criteria={
                    "team_expertise_match": 0.7,
                    "market_availability": 0.6,
                    "ecosystem_maturity": 0.8,
                    "total_cost": "budget",
                },
                priority_focus=["team_fit", "scalability", "korean_market"],
            ),
            AnalysisType.IMPLEMENTATION_GUIDE: AnalysisTemplate(
                type=AnalysisType.IMPLEMENTATION_GUIDE,
                purpose="선택된 솔루션의 구체적 구현 가이드 제공",
                scope=["아키텍처 설계", "단계별 구현 계획", "통합 포인트", "테스트 전략", "배포 전략", "모니터링 설정"],
                key_questions=[
                    "첫 단계는 무엇인가?",
                    "크리티컬 패스는 무엇인가?",
                    "주요 리스크 포인트는?",
                    "MVP는 언제 준비되는가?",
                    "롤백 계획은 있는가?",
                ],
                expected_outputs=["상세 구현 로드맵", "마일스톤 정의", "코드 샘플", "설정 가이드", "체크리스트"],
                evaluation_criteria={"completeness": 0.9, "clarity": 0.85, "feasibility": 0.95},
                time_budget=60,  # 더 많은 시간 필요
                max_depth=5,
            ),
            AnalysisType.COST_BENEFIT: AnalysisTemplate(
                type=AnalysisType.COST_BENEFIT,
                purpose="투자 대비 효과를 분석하여 의사결정 지원",
                scope=["초기 구현 비용", "운영 비용", "유지보수 비용", "기회 비용", "예상 수익/절감액", "ROI 기간"],
                key_questions=[
                    "총 투자 비용은 얼마인가?",
                    "손익분기점은 언제인가?",
                    "정량적 이익은 얼마인가?",
                    "정성적 이익은 무엇인가?",
                    "대안 대비 경제성은?",
                ],
                expected_outputs=["비용 분석표", "ROI 계산", "민감도 분석", "시나리오별 예측", "투자 권고안"],
                evaluation_criteria={
                    "roi_threshold": 1.5,
                    "payback_period": 24,  # months
                    "risk_tolerance": "medium",
                },
                priority_focus=["total_cost", "roi", "risk"],
            ),
        }

        return templates.get(analysis_type)

    @staticmethod
    def create_analysis_prompt(template: AnalysisTemplate, context: dict[str, Any]) -> str:
        """템플릿 기반 분석 프롬프트 생성."""

        prompt = f"""
# {template.type.value.upper()} 분석

## 분석 목적
{template.purpose}

## 분석 범위
{chr(10).join(f'- {scope}' for scope in template.scope)}

## 핵심 질문
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(template.key_questions))}

## 컨텍스트
- 대상: {context.get('target', 'N/A')}
- 언어/프레임워크: {context.get('tech_stack', 'N/A')}
- 팀 규모: {context.get('team_size', 'N/A')}
- 제약사항: {context.get('constraints', 'N/A')}

## 평가 기준
{chr(10).join(f'- {k}: {v}' for k, v in template.evaluation_criteria.items())}

## 우선순위 초점
{chr(10).join(f'- {focus}' for focus in (template.priority_focus or []))}

## 기대 산출물
다음 항목들을 포함한 구조화된 분석 결과를 제공하세요:
{chr(10).join(f'{i+1}. {output}' for i, output in enumerate(template.expected_outputs))}

## 분석 깊이
- 최대 깊이: {template.max_depth} 레벨
- 시간 예산: {template.time_budget}초

구체적이고 실행 가능한 인사이트를 제공해주세요.
"""

        # 추가 데이터가 있으면 포함
        if "additional_data" in context:
            prompt += f"\n## 추가 데이터\n{context['additional_data']}"

        return prompt

    @staticmethod
    def get_all_types() -> list[AnalysisType]:
        """모든 분석 유형 반환."""
        return list(AnalysisType)

    @staticmethod
    def get_types_by_category(category: str) -> list[AnalysisType]:
        """카테고리별 분석 유형 반환."""
        categories = {
            "code": [
                AnalysisType.CODE_QUALITY,
                AnalysisType.SECURITY_AUDIT,
                AnalysisType.PERFORMANCE_REVIEW,
                AnalysisType.REFACTORING,
                AnalysisType.BUG_ANALYSIS,
            ],
            "architecture": [
                AnalysisType.ARCHITECTURE_REVIEW,
                AnalysisType.DESIGN_PATTERNS,
                AnalysisType.SCALABILITY,
                AnalysisType.DEPENDENCY_ANALYSIS,
            ],
            "research": [
                AnalysisType.SOLUTION_COMPARISON,
                AnalysisType.TECHNOLOGY_SELECTION,
                AnalysisType.IMPLEMENTATION_GUIDE,
                AnalysisType.TREND_ANALYSIS,
                AnalysisType.COST_BENEFIT,
            ],
        }
        return categories.get(category, [])
