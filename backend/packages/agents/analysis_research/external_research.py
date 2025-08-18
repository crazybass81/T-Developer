"""
Enhanced External Research Agent with AI-powered analysis and Chain of Thought.

이 에이전트는 외부 API 데이터를 수집한 후, AI를 사용하여 심층 분석하고
Chain of Thought 방식으로 최적의 솔루션을 추천합니다.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
import yaml

from backend.core.shared_context import get_context_store

from ..base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent
from .templates import AnalysisTemplate, AnalysisTemplateLibrary, AnalysisType

logger = logging.getLogger("agents.enhanced_external_research")


@dataclass
class Solution:
    """Represents a technology solution."""

    name: str
    category: str
    type: str  # oss, saas, library, framework
    pros: list[str]
    cons: list[str]
    use_cases: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    korean_cases: list[dict[str, Any]] = field(default_factory=list)
    pricing: Optional[dict[str, str]] = None
    alternatives: list[str] = field(default_factory=list)
    integration_effort: Optional[dict[str, str]] = None


@dataclass
class TechnologyTrend:
    """Represents a technology trend."""

    name: str
    category: str
    status: str  # rising, stable, declining
    momentum: str  # high, medium, low
    adoption_stage: str  # innovator, early_adopter, early_majority, late_majority
    metrics: dict[str, Any] = field(default_factory=dict)
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    recommendation: dict[str, str] = field(default_factory=dict)


@dataclass
class ResearchAnalysis:
    """AI 분석 결과."""

    solutions_comparison: dict[str, Any]
    best_solution: str
    reasoning_chain: list[str]  # Chain of Thought 단계들
    implementation_guide: dict[str, Any]
    risk_assessment: dict[str, Any]
    confidence: float
    alternatives: list[dict[str, Any]]
    korean_context: Optional[dict[str, Any]] = None


@dataclass
class EnhancedResearchConfig:
    """향상된 외부 리서치 설정."""

    # API 검색 설정
    enable_github_search: bool = True
    enable_npm_search: bool = True
    enable_pypi_search: bool = True
    enable_awesome_lists: bool = True
    enable_trend_analysis: bool = True
    max_external_searches: int = 10

    # AI 분석 설정
    enable_ai_analysis: bool = True
    ai_model: str = "claude-3-sonnet-20240229"  # 깊이 있는 분석용
    ai_temperature: float = 0.3  # 일관된 분석을 위해 낮은 temperature
    ai_max_tokens: int = 2000  # 충분한 분석 공간
    ai_timeout: int = 30  # 30초 타임아웃

    # Chain of Thought 설정
    use_chain_of_thought: bool = True
    cot_steps: int = 5  # CoT 단계 수

    # 저장 설정
    save_to_library: bool = True
    reference_library_path: str = "backend/references"
    cache_ai_responses: bool = True


class ReferenceSearcher:
    """Searches external sources for references."""

    def __init__(self, cache_dir: str = ".reference_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_github(
        self, query: str, language: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Search GitHub for relevant repositories."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Check cache first
            cache_key = f"github_{query}_{language}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached

            # Build GitHub search query
            search_query = quote(query)
            if language:
                search_query += f"+language:{language}"

            url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&per_page=10"

            headers = {}
            if github_token := os.getenv("GITHUB_TOKEN"):
                headers["Authorization"] = f"token {github_token}"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    repos = []

                    for repo in data.get("items", []):
                        repos.append(
                            {
                                "name": repo.get("full_name", ""),
                                "stars": repo.get("stargazers_count", 0),
                                "description": repo.get("description", ""),
                                "url": repo.get("html_url", ""),
                                "language": repo.get("language", ""),
                                "topics": repo.get("topics", []),
                                "last_updated": repo.get("updated_at", ""),
                                "license": repo.get("license", {}).get("spdx_id")
                                if repo.get("license")
                                else None,
                            }
                        )

                    self._set_cache(cache_key, repos)
                    return repos
                else:
                    logger.warning(f"GitHub search failed: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"GitHub search error: {e}")
            return []

    async def search_npm(self, package_name: str) -> Optional[dict[str, Any]]:
        """Get NPM package information."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            cache_key = f"npm_{package_name}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached

            url = f"https://registry.npmjs.org/{package_name}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Get download stats
                    stats_url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
                    async with self.session.get(stats_url) as stats_response:
                        downloads = 0
                        if stats_response.status == 200:
                            stats_data = await stats_response.json()
                            downloads = stats_data.get("downloads", 0)

                    info = {
                        "name": data["name"],
                        "version": data.get("dist-tags", {}).get("latest"),
                        "description": data.get("description"),
                        "weekly_downloads": downloads,
                        "license": data.get("license"),
                        "repository": data.get("repository", {}).get("url"),
                        "keywords": data.get("keywords", []),
                        "dependencies": list(data.get("dependencies", {}).keys()),
                        "created": data.get("time", {}).get("created"),
                        "modified": data.get("time", {}).get("modified"),
                    }

                    self._set_cache(cache_key, info)
                    return info

        except Exception as e:
            logger.error(f"NPM search error: {e}")
            return None

    async def search_pypi(self, package_name: str) -> Optional[dict[str, Any]]:
        """Get PyPI package information."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            cache_key = f"pypi_{package_name}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached

            url = f"https://pypi.org/pypi/{package_name}/json"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    info_data = data.get("info", {})

                    info = {
                        "name": info_data.get("name"),
                        "version": info_data.get("version"),
                        "description": info_data.get("summary"),
                        "license": info_data.get("license"),
                        "home_page": info_data.get("home_page"),
                        "keywords": info_data.get("keywords", "").split(),
                        "requires_python": info_data.get("requires_python"),
                        "author": info_data.get("author"),
                        "classifiers": info_data.get("classifiers", []),
                    }

                    self._set_cache(cache_key, info)
                    return info

        except Exception as e:
            logger.error(f"PyPI search error: {e}")
            return None

    async def search_awesome_lists(self, topic: str) -> list[dict[str, Any]]:
        """Search awesome lists for curated resources."""
        # Search for awesome lists on GitHub
        awesome_query = f"awesome-{topic}"
        repos = await self.search_github(awesome_query)

        awesome_lists = []
        for repo in repos:
            if "awesome" in repo["name"].lower():
                awesome_lists.append(
                    {
                        "name": repo["name"],
                        "stars": repo["stars"],
                        "url": repo["url"],
                        "description": repo["description"],
                    }
                )

        return awesome_lists

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cached data if fresh."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            # Check if cache is less than 24 hours old
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if age < timedelta(hours=24):
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception:
                    pass
        return None

    def _set_cache(self, key: str, data: Any):
        """Set cache data."""
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")


class TrendAnalyzer:
    """Analyzes technology trends."""

    def __init__(self):
        self.trends_data: dict[str, TechnologyTrend] = {}

    async def analyze_technology(
        self,
        tech_name: str,
        github_data: Optional[dict[str, Any]] = None,
        package_data: Optional[dict[str, Any]] = None,
    ) -> TechnologyTrend:
        """Analyze a technology's trend."""
        # Determine momentum based on activity
        momentum = "medium"
        if github_data:
            stars = github_data.get("stars", 0)
            if stars > 50000:
                momentum = "high"
            elif stars < 5000:
                momentum = "low"

        # Determine adoption stage
        adoption_stage = "early_adopter"
        if package_data:
            downloads = package_data.get("weekly_downloads", 0)
            if downloads > 1000000:
                adoption_stage = "early_majority"
            elif downloads > 10000000:
                adoption_stage = "late_majority"
            elif downloads < 10000:
                adoption_stage = "innovator"

        # Determine status
        status = "stable"
        if momentum == "high" and adoption_stage in ["innovator", "early_adopter"]:
            status = "rising"
        elif momentum == "low" and adoption_stage == "late_majority":
            status = "declining"

        trend = TechnologyTrend(
            name=tech_name,
            category="unknown",
            status=status,
            momentum=momentum,
            adoption_stage=adoption_stage,
            metrics={
                "github_stars": github_data.get("stars", 0) if github_data else 0,
                "weekly_downloads": package_data.get("weekly_downloads", 0) if package_data else 0,
            },
            recommendation={
                "production": "wait" if adoption_stage == "innovator" else "consider",
                "learning": "recommended" if status == "rising" else "optional",
            },
        )

        return trend

    def compare_technologies(self, techs: list[TechnologyTrend]) -> dict[str, Any]:
        """Compare multiple technologies."""
        comparison = {"winner": None, "by_criteria": {}, "recommendation": ""}

        if not techs:
            return comparison

        # Compare by different criteria
        criteria = {
            "popularity": lambda t: t.metrics.get("github_stars", 0),
            "adoption": lambda t: t.metrics.get("weekly_downloads", 0),
            "momentum": lambda t: {"high": 3, "medium": 2, "low": 1}.get(t.momentum, 0),
        }

        for criterion, scorer in criteria.items():
            scores = [(t.name, scorer(t)) for t in techs]
            scores.sort(key=lambda x: x[1], reverse=True)
            comparison["by_criteria"][criterion] = scores[0][0]

        # Overall winner (simple majority)
        winners = list(comparison["by_criteria"].values())
        if winners:
            comparison["winner"] = max(set(winners), key=winners.count)
            comparison[
                "recommendation"
            ] = f"Based on analysis, {comparison['winner']} leads in most criteria"

        return comparison


class ReferenceLibrary:
    """Manages the reference knowledge base."""

    def __init__(self, library_path: str = "references"):
        self.library_path = Path(library_path)
        self.library_path.mkdir(exist_ok=True)
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure library directory structure exists."""
        dirs = [
            "solutions/authentication",
            "solutions/realtime",
            "solutions/payments",
            "solutions/storage",
            "patterns/microservices",
            "patterns/serverless",
            "benchmarks",
            "case-studies/korean",
            "case-studies/global",
            "trends",
        ]

        for dir_path in dirs:
            (self.library_path / dir_path).mkdir(parents=True, exist_ok=True)

    def save_solution(self, solution: Solution, category: str):
        """Save a solution reference."""
        file_path = self.library_path / f"solutions/{category}/{solution.name.lower()}.yaml"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "name": solution.name,
            "category": solution.category,
            "type": solution.type,
            "metadata": solution.metadata,
            "pros": solution.pros,
            "cons": solution.cons,
            "use_cases": solution.use_cases,
            "korean_cases": solution.korean_cases,
            "alternatives": solution.alternatives,
            "pricing": solution.pricing,
            "integration_effort": solution.integration_effort,
            "last_updated": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def get_solution(self, name: str, category: str) -> Optional[Solution]:
        """Get a solution reference."""
        file_path = self.library_path / f"solutions/{category}/{name.lower()}.yaml"

        if not file_path.exists():
            return None

        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            return Solution(
                name=data["name"],
                category=data["category"],
                type=data["type"],
                pros=data.get("pros", []),
                cons=data.get("cons", []),
                use_cases=data.get("use_cases", []),
                metadata=data.get("metadata", {}),
                korean_cases=data.get("korean_cases", []),
                pricing=data.get("pricing"),
                alternatives=data.get("alternatives", []),
                integration_effort=data.get("integration_effort"),
            )
        except Exception as e:
            logger.error(f"Failed to load solution: {e}")
            return None

    def search_solutions(
        self, problem: str, requirements: Optional[list[str]] = None
    ) -> list[Solution]:
        """Search for solutions to a problem."""
        solutions = []

        # Map problems to categories
        category_map = {
            "auth": "authentication",
            "login": "authentication",
            "realtime": "realtime",
            "websocket": "realtime",
            "payment": "payments",
            "billing": "payments",
        }

        # Find relevant category
        category = None
        for keyword, cat in category_map.items():
            if keyword in problem.lower():
                category = cat
                break

        if not category:
            return solutions

        # Load all solutions in category
        category_path = self.library_path / f"solutions/{category}"
        if category_path.exists():
            for file_path in category_path.glob("*.yaml"):
                solution = self.get_solution(file_path.stem, category)
                if solution:
                    # Filter by requirements if provided
                    if requirements:
                        matches = sum(
                            1
                            for req in requirements
                            if any(req.lower() in uc.lower() for uc in solution.use_cases)
                        )
                        if matches > 0:
                            solutions.append(solution)
                    else:
                        solutions.append(solution)

        return solutions

    def save_trend(self, trend: TechnologyTrend):
        """Save a technology trend."""
        # Sanitize filename - remove invalid characters
        safe_name = re.sub(r"[^\w\s-]", "", trend.name.lower())
        safe_name = re.sub(r"[-\s]+", "-", safe_name)
        file_path = self.library_path / f"trends/{safe_name}.yaml"

        data = {
            "name": trend.name,
            "category": trend.category,
            "status": trend.status,
            "momentum": trend.momentum,
            "adoption_stage": trend.adoption_stage,
            "metrics": trend.metrics,
            "risks": trend.risks,
            "opportunities": trend.opportunities,
            "recommendation": trend.recommendation,
            "last_updated": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def get_recommendations(
        self, problem: str, constraints: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Get recommendations for a problem."""
        solutions = self.search_solutions(problem)

        if not solutions:
            return {
                "recommended": None,
                "reasoning": "No solutions found in library",
                "alternatives": [],
            }

        # Score solutions based on constraints
        scored = []
        for solution in solutions:
            score = 0
            reasoning = []

            # Check Korean support
            if constraints and constraints.get("korean_market"):
                if solution.korean_cases:
                    score += 2
                    reasoning.append("Has Korean market cases")

            # Check budget
            if constraints and "budget" in constraints:
                if solution.pricing:
                    if constraints["budget"] == "low" and solution.type == "oss":
                        score += 2
                        reasoning.append("Open source fits budget")
                    elif constraints["budget"] == "high" and solution.type == "saas":
                        score += 1
                        reasoning.append("SaaS acceptable for budget")

            # Check timeline
            if constraints and "timeline" in constraints:
                if solution.integration_effort:
                    setup = solution.integration_effort.get("initial_setup", "")
                    if "hour" in setup and constraints["timeline"] == "urgent":
                        score += 2
                        reasoning.append("Quick setup time")

            scored.append((solution, score, reasoning))

        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        # Prepare recommendation
        best = scored[0] if scored else None

        return {
            "recommended": {
                "solution": best[0].name,
                "type": best[0].type,
                "reasoning": best[2],
                "pros": best[0].pros[:3],
                "cons": best[0].cons[:2],
                "korean_cases": best[0].korean_cases[:2],
            }
            if best
            else None,
            "alternatives": [
                {"solution": s[0].name, "score": s[1], "reasoning": s[2][:1]} for s in scored[1:4]
            ],
        }


class EnhancedResearchAgent:
    """Enhanced Research Agent with reference capabilities."""

    def __init__(self):
        self.searcher = ReferenceSearcher()
        self.analyzer = TrendAnalyzer()
        self.library = ReferenceLibrary()

    async def research_solution(
        self,
        problem: str,
        requirements: Optional[list[str]] = None,
        constraints: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Research solutions for a problem."""
        async with self.searcher:
            # Search multiple sources
            github_results = await self.searcher.search_github(problem)
            awesome_lists = await self.searcher.search_awesome_lists(problem)

            # Check library for existing solutions
            library_solutions = self.library.search_solutions(problem, requirements)

            # Get recommendations
            recommendations = self.library.get_recommendations(problem, constraints)

            # Analyze trends for top solutions
            trends = []
            for repo in github_results[:3]:
                trend = await self.analyzer.analyze_technology(repo["name"], repo)
                trends.append(trend)

            # Compare technologies
            comparison = self.analyzer.compare_technologies(trends)

            return {
                "problem": problem,
                "requirements": requirements,
                "constraints": constraints,
                "recommendations": recommendations,
                "external_references": {
                    "github": github_results[:5],
                    "awesome_lists": awesome_lists[:3],
                },
                "trends": [
                    {
                        "name": t.name,
                        "status": t.status,
                        "momentum": t.momentum,
                        "recommendation": t.recommendation,
                    }
                    for t in trends
                ],
                "comparison": comparison,
                "library_matches": len(library_solutions),
                "report_generated": datetime.now().isoformat(),
            }

    async def save_research(self, research: dict[str, Any], category: str):
        """Save research results to library."""
        # Extract and save solutions
        if "recommendations" in research and research["recommendations"]["recommended"]:
            rec = research["recommendations"]["recommended"]
            solution = Solution(
                name=rec["solution"],
                category=category,
                type=rec["type"],
                pros=rec.get("pros", []),
                cons=rec.get("cons", []),
                use_cases=[],
                korean_cases=rec.get("korean_cases", []),
            )
            self.library.save_solution(solution, category)

        # Save trends
        for trend_data in research.get("trends", []):
            trend = TechnologyTrend(
                name=trend_data["name"],
                category=category,
                status=trend_data["status"],
                momentum=trend_data["momentum"],
                adoption_stage="unknown",
                recommendation=trend_data.get("recommendation", {}),
            )
            self.library.save_trend(trend)


class EnhancedExternalResearchAgent(BaseAgent):
    """
    AI 기반 외부 리서치 에이전트.

    특징:
    1. 외부 API로 데이터 수집 (GitHub, NPM, PyPI)
    2. AI로 심층 분석 (Claude Sonnet)
    3. Chain of Thought로 논리적 추론
    4. 한국 시장 컨텍스트 고려
    5. 구현 가이드 제공
    """

    def __init__(
        self,
        name: str = "enhanced_external_research",
        config: Optional[EnhancedResearchConfig] = None,
    ):
        """향상된 외부 리서치 에이전트 초기화."""
        super().__init__(name, {"timeout": 600})
        self.config = config or EnhancedResearchConfig()
        self.searcher = ReferenceSearcher()
        self.analyzer = TrendAnalyzer()
        self.library = ReferenceLibrary(self.config.reference_library_path)
        self.context_store = get_context_store()

        # AI 캐시
        self.ai_cache = {}
        self.api_calls = 0
        self.ai_calls = 0

    async def execute(self, input: AgentInput) -> AgentOutput:
        """외부 리서치 실행 (API + AI 분석)."""
        try:
            logger.info("Starting enhanced external research")

            # Phase 0: 분석 유형 및 템플릿 결정
            analysis_type = self._determine_analysis_type(input)
            template = (
                AnalysisTemplateLibrary.get_template(analysis_type) if analysis_type else None
            )

            # Phase 1: 입력 파싱 및 컨텍스트 로드
            problem, requirements, constraints = await self._parse_input(input)

            if not problem:
                raise ValueError("No problem specified for research")

            # Phase 2: 외부 API 데이터 수집
            logger.info("Collecting external data from APIs...")
            api_results = await self._collect_external_data(problem, requirements, constraints)
            self.api_calls += (
                len(api_results.get("github", []))
                + len(api_results.get("npm", []))
                + len(api_results.get("pypi", []))
            )

            # Phase 3: AI 분석 (선택적)
            ai_analysis = None
            if self.config.enable_ai_analysis and api_results:
                logger.info("Performing AI-powered analysis...")
                ai_analysis = await self._perform_ai_analysis(
                    problem, requirements, constraints, api_results, template
                )
                self.ai_calls += 1

            # Phase 4: 결과 통합 및 권장사항 생성
            final_report = self._create_final_report(api_results, ai_analysis)

            # Phase 5: 결과 저장
            if self.config.save_to_library:
                await self._save_to_library(final_report, input.payload.get("category", "general"))

            # SharedContext에 저장
            evolution_id = input.payload.get("evolution_id") or (
                input.context.get("evolution_id") if input.context else None
            )
            if evolution_id:
                await self._store_in_context(evolution_id, final_report)

            # 응답 생성
            artifact = Artifact(
                kind="research", ref="enhanced_research_report", content=final_report
            )

            return AgentOutput(
                task_id=input.task_id,
                status=AgentStatus.OK,
                artifacts=[artifact],
                metrics={
                    "api_calls": self.api_calls,
                    "ai_calls": self.ai_calls,
                    "github_solutions": len(api_results.get("github", [])),
                    "npm_packages": len(api_results.get("npm", [])),
                    "pypi_packages": len(api_results.get("pypi", [])),
                    "ai_confidence": ai_analysis.confidence if ai_analysis else 0.0,
                    "recommendations": len(final_report.get("recommendations", [])),
                    "execution_time": 0,  # Would be tracked
                },
                context={"evolution_id": evolution_id} if evolution_id else None,
            )

        except Exception as e:
            logger.error(f"Enhanced research failed: {e}")
            return AgentOutput(task_id=input.task_id, status=AgentStatus.FAIL, error=str(e))

    async def _parse_input(self, input: AgentInput) -> tuple[str, list[str], dict[str, Any]]:
        """입력 파싱 및 컨텍스트 로드."""
        evolution_id = input.payload.get("evolution_id") or (
            input.context.get("evolution_id") if input.context else None
        )

        if evolution_id:
            # SharedContext에서 분석 결과 읽기
            context = await self.context_store.get_context(evolution_id)
            if context and context.current_state:
                # 코드 분석 결과에서 문제 추출
                top_issues = context.current_state.get("top_issues", [])
                top_improvements = context.current_state.get("top_improvements", [])

                problem = f"Issues: {', '.join([i.get('type', '') for i in top_issues[:3]])}"
                requirements = [imp.get("type", "") for imp in top_improvements[:3]]
                constraints = input.payload.get("constraints", {})

                return problem, requirements, constraints

        # 직접 입력
        problem = input.payload.get("problem", "")
        requirements = input.payload.get("requirements", [])
        constraints = input.payload.get("constraints", {})

        return problem, requirements, constraints

    async def _collect_external_data(
        self, problem: str, requirements: list[str], constraints: dict[str, Any]
    ) -> dict[str, Any]:
        """외부 데이터 수집 (MCP 우선, API 폴백)."""
        results = {}

        # GitHub 검색 - MCP 우선 시도
        if self.config.enable_github_search:
            github_results = await self._search_github_with_mcp(problem, requirements)
            if not github_results:
                # MCP 실패시 API 폴백
                logger.info("MCP not available, falling back to GitHub API")
                async with self.searcher:
                    github_results = await self.searcher.search_github(problem)
            results["github"] = github_results

        # NPM 검색
        if self.config.enable_npm_search and "javascript" in str(requirements).lower():
            # NPM 패키지 검색
            npm_results = []
            async with self.searcher:
                # 문제를 키워드로 변환
                keywords = problem.lower().split()[:3]  # 상위 3개 키워드
                for keyword in keywords:
                    result = await self.searcher.search_npm(keyword)
                    if result:
                        npm_results.append(result)
            results["npm"] = npm_results[: self.config.max_external_searches]

        # PyPI 검색
        if self.config.enable_pypi_search and "python" in str(requirements).lower():
            # PyPI 패키지 검색
            pypi_results = []
            async with self.searcher:
                # 문제를 키워드로 변환
                keywords = problem.lower().split()[:3]  # 상위 3개 키워드
                for keyword in keywords:
                    result = await self.searcher.search_pypi(keyword)
                    if result:
                        pypi_results.append(result)
            results["pypi"] = pypi_results[: self.config.max_external_searches]

        # Awesome Lists 검색
        if self.config.enable_awesome_lists:
            async with self.searcher:
                results["awesome"] = await self.searcher.search_awesome_lists(problem)

        # 트렌드 분석
        if self.config.enable_trend_analysis:
            # 트렌드 분석은 수집된 데이터 기반으로 수행
            trends = []
            for repo in results.get("github", [])[:3]:
                trend = await self.analyzer.analyze_technology(repo["name"], repo)
                trends.append(trend)
            results["trends"] = trends

        return results

    async def _search_github_with_mcp(
        self, problem: str, requirements: list[str]
    ) -> Optional[list[dict[str, Any]]]:
        """MCP를 통한 GitHub 검색.

        MCP (Model Context Protocol)를 사용하면:
        - 더 풍부한 컨텍스트 정보 제공
        - 자동 페이지네이션
        - 더 나은 검색 관련성
        - Rate limiting 자동 처리
        """
        try:
            # MCP GitHub 도구 확인
            # Claude의 MCP 도구는 mcp__ 접두사를 가짐

            # MCP 도구가 있는지 확인
            mcp_available = False
            for name in dir():
                if name.startswith("mcp__github"):
                    mcp_available = True
                    break

            if not mcp_available:
                logger.debug("MCP GitHub tools not available")
                return None

            # MCP를 통한 검색 시도
            # 실제로는 Claude가 MCP 도구를 자동으로 제공
            search_query = f"{problem} {' '.join(requirements)}"

            # MCP 도구 사용 (Claude가 자동으로 제공하는 경우)
            # 예: mcp__github__search_repositories(query=search_query)

            logger.info(f"Searching GitHub via MCP: {search_query}")

            # MCP 결과 포맷팅
            # MCP는 더 구조화된 데이터를 제공
            mcp_results = []

            # 여기서는 MCP가 사용 불가능하므로 None 반환
            return None

        except Exception as e:
            logger.warning(f"MCP GitHub search failed: {e}")
            return None

    def _determine_analysis_type(self, input: AgentInput) -> Optional[AnalysisType]:
        """입력으로부터 분석 유형 결정."""

        # 명시적 분석 유형
        if "analysis_type" in input.payload:
            type_str = input.payload["analysis_type"]
            try:
                return AnalysisType(type_str)
            except ValueError:
                logger.warning(f"Unknown analysis type: {type_str}")

        # 문제/요구사항 기반 자동 추론
        problem = input.payload.get("problem", "").lower()
        requirements = input.payload.get("requirements", [])

        # 키워드 기반 매칭
        if any(word in problem for word in ["compare", "vs", "versus", "choose"]):
            return AnalysisType.SOLUTION_COMPARISON
        elif any(word in problem for word in ["implement", "build", "create"]):
            return AnalysisType.IMPLEMENTATION_GUIDE
        elif any(word in problem for word in ["select", "pick", "decide", "technology"]):
            return AnalysisType.TECHNOLOGY_SELECTION
        elif any(word in problem for word in ["cost", "budget", "roi", "investment"]):
            return AnalysisType.COST_BENEFIT
        elif any(word in problem for word in ["trend", "future", "emerging"]):
            return AnalysisType.TREND_ANALYSIS

        # 기본값: 솔루션 비교
        return AnalysisType.SOLUTION_COMPARISON

    async def _perform_ai_analysis(
        self,
        problem: str,
        requirements: list[str],
        constraints: dict[str, Any],
        api_results: dict[str, Any],
        template: Optional[AnalysisTemplate] = None,
    ) -> Optional[ResearchAnalysis]:
        """AI를 사용한 심층 분석 (Chain of Thought 포함)."""

        # 캐시 확인
        cache_key = f"{problem}:{':'.join(requirements)}"
        if self.config.cache_ai_responses and cache_key in self.ai_cache:
            logger.info("Using cached AI response")
            return self.ai_cache[cache_key]

        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set, skipping AI analysis")
                return None

            import anthropic

            client = anthropic.AsyncAnthropic(api_key=api_key)

            # 템플릿 기반 또는 기본 프롬프트 생성
            if template:
                prompt = self._create_template_based_prompt(
                    template, problem, requirements, constraints, api_results
                )
            else:
                prompt = self._create_cot_prompt(problem, requirements, constraints, api_results)

            # AI 호출
            response = await asyncio.wait_for(
                client.messages.create(
                    model=self.config.ai_model,
                    max_tokens=self.config.ai_max_tokens,
                    temperature=self.config.ai_temperature,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=self.config.ai_timeout,
            )

            # 응답 파싱
            analysis = self._parse_ai_response(response.content[0].text)

            # 캐시 저장
            if self.config.cache_ai_responses:
                self.ai_cache[cache_key] = analysis

            return analysis

        except asyncio.TimeoutError:
            logger.warning("AI analysis timed out")
            return None
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None

    def _create_template_based_prompt(
        self,
        template: AnalysisTemplate,
        problem: str,
        requirements: list[str],
        constraints: dict[str, Any],
        api_results: dict[str, Any],
    ) -> str:
        """템플릿 기반 분석 프롬프트 생성."""

        # GitHub 결과 요약
        github_summary = self._summarize_github_results(api_results.get("github", []))
        package_summary = self._summarize_package_results(api_results)

        # 템플릿 컨텍스트 준비
        context = {
            "target": problem,
            "tech_stack": ", ".join(requirements) if requirements else "Not specified",
            "team_size": constraints.get("team_size", "Unknown"),
            "constraints": constraints,
            "additional_data": f"""
### 발견된 솔루션
{github_summary}

### 패키지 정보
{package_summary}

### 요구사항
- {chr(10).join(f'- {req}' for req in requirements)}

### 제약사항
- 예산: {constraints.get('budget', 'Not specified')}
- 타임라인: {constraints.get('timeline', 'Not specified')}
- 기술 스택: {constraints.get('tech_stack', 'Not specified')}
""",
        }

        # 템플릿 프롬프트 생성
        base_prompt = AnalysisTemplateLibrary.create_analysis_prompt(template, context)

        # 한국 컨텍스트 추가
        korean_context = """
### 한국 시장 고려사항
- 한국 개발자 커뮤니티 활성도
- 한국어 문서/자료 가용성
- 로컬 기술 지원 가능 여부
- 한국 시장 특화 요구사항
"""

        # JSON 출력 형식 지정
        output_format = (
            """
## 출력 형식
반드시 다음 JSON 형식으로 응답하세요:
```json
{
  "analysis_type": "%s",
  "best_solution": "추천 솔루션",
  "reasoning_chain": ["단계별 추론..."],
  "solutions_comparison": {...},
  "implementation_guide": {...},
  "risk_assessment": {...},
  "korean_context": {...},
  "confidence": 0.0-1.0,
  "alternatives": [...]
}
```
"""
            % template.type.value
        )

        return base_prompt + korean_context + output_format

    def _summarize_github_results(self, github_repos: list[dict[str, Any]]) -> str:
        """GitHub 검색 결과 요약."""
        if not github_repos:
            return "GitHub 저장소를 찾을 수 없음"

        summary = "#### GitHub 저장소 (상위 5개)\n"
        for repo in github_repos[:5]:
            summary += f"- **{repo.get('name', 'Unknown')}**: ⭐{repo.get('stars', 0)} "
            summary += f"({repo.get('description', 'No description')[:80]})\n"
            summary += f"  - 언어: {repo.get('language', 'Unknown')}\n"
            summary += f"  - 최근 업데이트: {repo.get('updated_at', 'Unknown')[:10]}\n"
        return summary

    def _summarize_package_results(self, api_results: dict[str, Any]) -> str:
        """패키지 검색 결과 요약."""
        summary = ""

        if api_results.get("npm"):
            summary += "#### NPM 패키지\n"
            for pkg in api_results["npm"][:3]:
                summary += f"- {pkg.get('name')}: {pkg.get('description', '')[:60]}\n"

        if api_results.get("pypi"):
            summary += "#### PyPI 패키지\n"
            for pkg in api_results["pypi"][:3]:
                summary += f"- {pkg.get('name')}: {pkg.get('summary', '')[:60]}\n"

        return summary or "패키지 정보 없음"

    def _create_cot_prompt(
        self,
        problem: str,
        requirements: list[str],
        constraints: dict[str, Any],
        api_results: dict[str, Any],
    ) -> str:
        """Chain of Thought 프롬프트 생성."""

        # GitHub 결과 요약
        github_summary = ""
        if "github" in api_results:
            repos = api_results["github"][:5]  # 상위 5개만
            github_summary = "\n".join(
                [
                    f"- {repo.get('name', 'Unknown')}: ⭐{repo.get('stars', 0)} "
                    f"({repo.get('description', 'No description')[:100]})"
                    for repo in repos
                ]
            )

        # NPM/PyPI 결과 요약
        package_summary = ""
        if "npm" in api_results:
            packages = api_results["npm"][:3]
            package_summary += "NPM:\n" + "\n".join(
                [
                    f"- {pkg.get('name', 'Unknown')}: {pkg.get('description', '')[:80]}"
                    for pkg in packages
                ]
            )
        if "pypi" in api_results:
            packages = api_results["pypi"][:3]
            package_summary += "\nPyPI:\n" + "\n".join(
                [
                    f"- {pkg.get('name', 'Unknown')}: {pkg.get('summary', '')[:80]}"
                    for pkg in packages
                ]
            )

        prompt = """당신은 소프트웨어 아키텍처 전문가이자 기술 리서치 분석가입니다.
다음 문제에 대한 최적의 솔루션을 Chain of Thought 방식으로 분석해주세요.

## 문제 정의
{problem}

## 요구사항
{requirements}

## 제약사항
- 예산: {budget}
- 타임라인: {timeline}
- 팀 규모: {team_size}
- 기술 스택: {tech_stack}

## 발견된 외부 솔루션

### GitHub 저장소
{github_summary}

### 패키지
{package_summary}

## Chain of Thought 분석 요청

다음 5단계로 체계적으로 분석해주세요:

### Step 1: 문제 분해 및 핵심 요구사항 파악
- 문제의 본질은 무엇인가?
- 가장 중요한 요구사항 3가지는?
- 기술적 도전과제는?

### Step 2: 솔루션 옵션 평가
- 각 GitHub 솔루션의 장단점
- 직접 구현 vs 라이브러리 사용
- 각 옵션의 리스크 평가

### Step 3: 한국 시장/환경 고려사항
- 한국 개발 환경에서의 적합성
- 로컬라이제이션 필요 여부
- 한국 개발자 커뮤니티 지원

### Step 4: 구현 전략 수립
- 단계별 구현 로드맵
- 필요한 리소스와 기술
- 예상 소요 시간

### Step 5: 최종 추천 및 근거
- 최적 솔루션 선택
- 선택 근거 (명확한 이유 3가지)
- 대안 솔루션 2개

## 출력 형식

반드시 다음 JSON 형식으로 응답하세요:

```json
{
  "reasoning_chain": [
    "Step 1 분석 내용...",
    "Step 2 분석 내용...",
    "Step 3 분석 내용...",
    "Step 4 분석 내용...",
    "Step 5 분석 내용..."
  ],
  "best_solution": "추천 솔루션 이름",
  "solutions_comparison": {
    "solution1": {"pros": [...], "cons": [...], "score": 0.8},
    "solution2": {"pros": [...], "cons": [...], "score": 0.6}
  },
  "implementation_guide": {
    "phase1": {"task": "...", "duration": "1주", "dependencies": [...]},
    "phase2": {"task": "...", "duration": "2주", "dependencies": [...]}
  },
  "risk_assessment": {
    "technical_risks": [...],
    "business_risks": [...],
    "mitigation_strategies": [...]
  },
  "korean_context": {
    "localization_needed": true/false,
    "local_alternatives": [...],
    "community_support": "활발/보통/부족"
  },
  "alternatives": [
    {"name": "대안1", "when_to_use": "..."},
    {"name": "대안2", "when_to_use": "..."}
  ],
  "confidence": 0.85
}
```

깊이 있고 실용적인 분석을 제공해주세요."""

        # Format the prompt with variables
        prompt = prompt.format(
            problem=problem,
            requirements=", ".join(requirements) if requirements else "특별한 요구사항 없음",
            budget=constraints.get("budget", "중간"),
            timeline=constraints.get("timeline", "보통"),
            team_size=constraints.get("team_size", "중소규모"),
            tech_stack=constraints.get("tech_stack", "제한 없음"),
            github_summary=github_summary if github_summary else "관련 저장소 없음",
            package_summary=package_summary if package_summary else "관련 패키지 없음",
        )

        return prompt

    def _parse_ai_response(self, response_text: str) -> ResearchAnalysis:
        """AI 응답을 구조화된 분석 결과로 파싱."""
        try:
            # JSON 추출
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1) if "```" in response_text else json_match.group(0)
                data = json.loads(json_str)

                return ResearchAnalysis(
                    solutions_comparison=data.get("solutions_comparison", {}),
                    best_solution=data.get("best_solution", "Unknown"),
                    reasoning_chain=data.get("reasoning_chain", []),
                    implementation_guide=data.get("implementation_guide", {}),
                    risk_assessment=data.get("risk_assessment", {}),
                    confidence=data.get("confidence", 0.5),
                    alternatives=data.get("alternatives", []),
                    korean_context=data.get("korean_context"),
                )
            else:
                # 파싱 실패시 기본 구조
                return ResearchAnalysis(
                    solutions_comparison={},
                    best_solution="Unable to parse",
                    reasoning_chain=["AI response parsing failed"],
                    implementation_guide={},
                    risk_assessment={},
                    confidence=0.0,
                    alternatives=[],
                )

        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return ResearchAnalysis(
                solutions_comparison={},
                best_solution="Parse error",
                reasoning_chain=[str(e)],
                implementation_guide={},
                risk_assessment={},
                confidence=0.0,
                alternatives=[],
            )

    def _create_final_report(
        self, api_results: dict[str, Any], ai_analysis: Optional[ResearchAnalysis]
    ) -> dict[str, Any]:
        """최종 리서치 보고서 생성."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "api_results": {
                "github": api_results.get("github", [])[:10],
                "npm": api_results.get("npm", [])[:5],
                "pypi": api_results.get("pypi", [])[:5],
                "awesome_lists": api_results.get("awesome", []),
                "trends": api_results.get("trends", {}),
            },
            "statistics": {
                "total_solutions_found": (
                    len(api_results.get("github", []))
                    + len(api_results.get("npm", []))
                    + len(api_results.get("pypi", []))
                ),
                "api_calls_made": self.api_calls,
                "ai_analysis_performed": ai_analysis is not None,
            },
        }

        # AI 분석 결과 추가
        if ai_analysis:
            report["ai_analysis"] = {
                "best_solution": ai_analysis.best_solution,
                "confidence": ai_analysis.confidence,
                "reasoning_chain": ai_analysis.reasoning_chain,
                "solutions_comparison": ai_analysis.solutions_comparison,
                "implementation_guide": ai_analysis.implementation_guide,
                "risk_assessment": ai_analysis.risk_assessment,
                "korean_context": ai_analysis.korean_context,
                "alternatives": ai_analysis.alternatives,
            }

            # 권장사항 생성
            report["recommendations"] = self._generate_recommendations(ai_analysis)
        else:
            # AI 없이 기본 권장사항
            report["recommendations"] = self._generate_basic_recommendations(api_results)

        return report

    def _generate_recommendations(self, analysis: ResearchAnalysis) -> list[str]:
        """AI 분석 기반 권장사항 생성."""
        recommendations = []

        # 최고 추천 솔루션
        if analysis.best_solution and analysis.confidence > 0.7:
            recommendations.append(
                f"🎯 **추천**: {analysis.best_solution} 사용 (신뢰도: {analysis.confidence:.0%})"
            )

        # 구현 가이드 요약
        if analysis.implementation_guide:
            phases = len(analysis.implementation_guide)
            recommendations.append(f"📋 {phases}단계 구현 로드맵 준비됨")

        # 위험 요소
        if analysis.risk_assessment.get("technical_risks"):
            risk_count = len(analysis.risk_assessment["technical_risks"])
            recommendations.append(f"⚠️ {risk_count}개 기술적 위험 식별 - 완화 전략 필요")

        # 한국 컨텍스트
        if analysis.korean_context and analysis.korean_context.get("localization_needed"):
            recommendations.append("🇰🇷 한국 시장 맞춤 로컬라이제이션 필요")

        # 대안
        if analysis.alternatives:
            recommendations.append(f"🔄 {len(analysis.alternatives)}개 대안 솔루션 제시됨")

        # Chain of Thought 인사이트
        if analysis.reasoning_chain and len(analysis.reasoning_chain) >= 5:
            recommendations.append("✅ 5단계 체계적 분석 완료")

        return recommendations[:10]  # 최대 10개

    def _generate_basic_recommendations(self, api_results: dict[str, Any]) -> list[str]:
        """기본 권장사항 생성 (AI 없이)."""
        recommendations = []

        # GitHub 기반
        if api_results.get("github"):
            top_repo = api_results["github"][0] if api_results["github"] else {}
            if top_repo.get("stars", 0) > 1000:
                recommendations.append(
                    f"⭐ 인기 솔루션: {top_repo.get('name')} ({top_repo.get('stars')} stars)"
                )

        # 패키지 기반
        if api_results.get("npm"):
            recommendations.append(f"📦 {len(api_results['npm'])}개 NPM 패키지 발견")

        if api_results.get("pypi"):
            recommendations.append(f"🐍 {len(api_results['pypi'])}개 PyPI 패키지 발견")

        # 트렌드
        if api_results.get("trends"):
            recommendations.append("📈 최신 트렌드 분석 포함")

        return recommendations

    async def _save_to_library(self, report: dict[str, Any], category: str) -> None:
        """리서치 결과를 라이브러리에 저장."""
        try:
            library_path = Path(self.config.reference_library_path) / category
            library_path.mkdir(parents=True, exist_ok=True)

            filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = library_path / filename

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"Research saved to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save research: {e}")

    async def _store_in_context(self, evolution_id: str, report: dict[str, Any]) -> None:
        """SharedContext에 리서치 결과 저장."""
        try:
            context = await self.context_store.get_context(evolution_id)
            if context:
                # 외부 리서치 저장
                best_practices = []
                references = []
                patterns = []

                if "ai_analysis" in report:
                    ai = report["ai_analysis"]
                    best_practices.append(
                        {
                            "solution": ai["best_solution"],
                            "confidence": ai["confidence"],
                            "guide": ai.get("implementation_guide", {}),
                        }
                    )
                    patterns = ai.get("reasoning_chain", [])[:3]

                references = report.get("api_results", {})

                await self.context_store.store_external_research(
                    best_practices=best_practices,
                    references=[references],
                    patterns=patterns,
                    evolution_id=evolution_id,
                )

                logger.info(f"Research stored in context {evolution_id}")

        except Exception as e:
            logger.error(f"Failed to store in context: {e}")

    async def validate(self, output: AgentOutput) -> bool:
        """출력 검증."""
        if output.status != AgentStatus.OK:
            return False

        if not output.artifacts:
            return False

        # API 호출이 있었는지 확인
        if output.metrics.get("api_calls", 0) == 0:
            return False

        return True

    def get_capabilities(self) -> dict[str, Any]:
        """에이전트 능력 반환."""
        return {
            "name": "EnhancedExternalResearchAgent",
            "version": "2.0.0",
            "description": "AI 기반 외부 리서치 에이전트 (Chain of Thought)",
            "features": [
                "GitHub/NPM/PyPI API 검색",
                "AI 심층 분석 (Claude Sonnet)",
                "Chain of Thought 추론",
                "한국 시장 컨텍스트 고려",
                "구현 가이드 및 리스크 평가",
                "솔루션 비교 분석",
                "결과 캐싱",
            ],
            "ai_model": self.config.ai_model,
            "ai_enabled": self.config.enable_ai_analysis,
            "cot_enabled": self.config.use_chain_of_thought,
            "metrics": {
                "total_api_calls": self.api_calls,
                "total_ai_calls": self.ai_calls,
                "cache_size": len(self.ai_cache),
            },
        }
