"""Reference Library and External Search for Research Agent."""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
import yaml

logger = logging.getLogger("agents.research.references")


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
        """Search GitHub for relevant repositories.

        Args:
            query: Search query
            language: Programming language filter

        Returns:
            List of repository information
        """
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
                                "name": repo["full_name"],
                                "stars": repo["stargazers_count"],
                                "description": repo["description"],
                                "url": repo["html_url"],
                                "language": repo["language"],
                                "topics": repo.get("topics", []),
                                "last_updated": repo["updated_at"],
                                "license": repo.get("license", {}).get("spdx_id"),
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
        """Get NPM package information.

        Args:
            package_name: NPM package name

        Returns:
            Package information
        """
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
        """Get PyPI package information.

        Args:
            package_name: PyPI package name

        Returns:
            Package information
        """
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
        """Search awesome lists for curated resources.

        Args:
            topic: Topic to search

        Returns:
            List of awesome list resources
        """
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
        """Get cached data if fresh.

        Args:
            key: Cache key

        Returns:
            Cached data or None
        """
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
        """Set cache data.

        Args:
            key: Cache key
            data: Data to cache
        """
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
        """Analyze a technology's trend.

        Args:
            tech_name: Technology name
            github_data: GitHub repository data
            package_data: Package manager data

        Returns:
            Technology trend analysis
        """
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
        """Compare multiple technologies.

        Args:
            techs: List of technologies to compare

        Returns:
            Comparison analysis
        """
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
        """Save a solution reference.

        Args:
            solution: Solution to save
            category: Solution category
        """
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
        """Get a solution reference.

        Args:
            name: Solution name
            category: Solution category

        Returns:
            Solution or None
        """
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
        """Search for solutions to a problem.

        Args:
            problem: Problem description
            requirements: List of requirements

        Returns:
            List of matching solutions
        """
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
        """Save a technology trend.

        Args:
            trend: Trend to save
        """
        file_path = self.library_path / f"trends/{trend.name.lower()}.yaml"

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
        """Get recommendations for a problem.

        Args:
            problem: Problem description
            constraints: Constraints (budget, timeline, skills)

        Returns:
            Recommendations with reasoning
        """
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
        """Research solutions for a problem.

        Args:
            problem: Problem description
            requirements: List of requirements
            constraints: Constraints (budget, timeline, etc.)

        Returns:
            Research report with recommendations
        """
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
        """Save research results to library.

        Args:
            research: Research results
            category: Solution category
        """
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
