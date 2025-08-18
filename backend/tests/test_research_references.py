"""Tests for Research Agent Reference Library functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from packages.agents.analysis_research.external_research import (
    EnhancedResearchAgent,
    ReferenceLibrary,
    ReferenceSearcher,
    Solution,
    TechnologyTrend,
    TrendAnalyzer,
)


class TestSolution:
    """Test Solution dataclass."""

    def test_solution_creation(self):
        """Test creating a solution."""
        solution = Solution(
            name="Auth0",
            category="authentication",
            type="saas",
            pros=["Easy setup", "Secure"],
            cons=["Vendor lock-in"],
            use_cases=["B2C apps"],
        )

        assert solution.name == "Auth0"
        assert solution.type == "saas"
        assert "Easy setup" in solution.pros
        assert len(solution.cons) == 1

    def test_solution_with_korean_cases(self):
        """Test solution with Korean cases."""
        solution = Solution(
            name="Socket.io",
            category="realtime",
            type="oss",
            pros=["Battle-tested"],
            cons=["Scaling issues"],
            use_cases=["Chat apps"],
            korean_cases=[{"company": "Kakao", "scale": "50M users"}],
        )

        assert len(solution.korean_cases) == 1
        assert solution.korean_cases[0]["company"] == "Kakao"


class TestReferenceSearcher:
    """Test reference searcher."""

    @pytest.fixture
    def searcher(self, tmp_path):
        """Create searcher with temp cache."""
        return ReferenceSearcher(cache_dir=str(tmp_path / "cache"))

    @pytest.mark.asyncio
    async def test_github_search(self, searcher):
        """Test GitHub repository search."""
        with patch.object(searcher, "_get_cache", return_value=None):
            with patch.object(searcher, "_set_cache"):
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(
                    return_value={
                        "items": [
                            {
                                "full_name": "facebook/react",
                                "stargazers_count": 200000,
                                "description": "A JavaScript library",
                                "html_url": "https://github.com/facebook/react",
                                "language": "JavaScript",
                                "topics": ["react", "javascript"],
                                "updated_at": "2024-01-15",
                                "license": {"spdx_id": "MIT"},
                            }
                        ]
                    }
                )

                async with searcher:
                    # Create async context manager
                    async def async_context():
                        return mock_response

                    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                    mock_response.__aexit__ = AsyncMock(return_value=None)

                    with patch.object(searcher.session, "get", return_value=mock_response):
                        repos = await searcher.search_github("react")

                assert len(repos) == 1
                assert repos[0]["name"] == "facebook/react"
                assert repos[0]["stars"] == 200000

    @pytest.mark.asyncio
    async def test_npm_search(self, searcher):
        """Test NPM package search."""
        with patch.object(searcher, "_get_cache", return_value=None):
            with patch.object(searcher, "_set_cache"):
                # Mock main package response
                mock_pkg_response = MagicMock()
                mock_pkg_response.status = 200
                mock_pkg_response.json = AsyncMock(
                    return_value={
                        "name": "express",
                        "dist-tags": {"latest": "4.18.2"},
                        "description": "Fast web framework",
                        "license": "MIT",
                        "repository": {"url": "git://github.com/expressjs/express.git"},
                        "keywords": ["web", "framework"],
                        "dependencies": {"accepts": "~1.3.8"},
                        "time": {"created": "2010-12-29", "modified": "2024-01-10"},
                    }
                )

                # Mock download stats response
                mock_stats_response = MagicMock()
                mock_stats_response.status = 200
                mock_stats_response.json = AsyncMock(return_value={"downloads": 5000000})

                async with searcher:
                    # Create async context managers
                    mock_pkg_response.__aenter__ = AsyncMock(return_value=mock_pkg_response)
                    mock_pkg_response.__aexit__ = AsyncMock(return_value=None)
                    mock_stats_response.__aenter__ = AsyncMock(return_value=mock_stats_response)
                    mock_stats_response.__aexit__ = AsyncMock(return_value=None)

                    with patch.object(
                        searcher.session,
                        "get",
                        side_effect=[mock_pkg_response, mock_stats_response],
                    ):
                        info = await searcher.search_npm("express")

                assert info["name"] == "express"
                assert info["weekly_downloads"] == 5000000
                assert info["license"] == "MIT"

    @pytest.mark.asyncio
    async def test_cache_usage(self, searcher, tmp_path):
        """Test cache is used for repeated searches."""
        cached_data = [{"name": "cached/repo", "stars": 1000}]

        with patch.object(searcher, "_get_cache", return_value=cached_data):
            async with searcher:
                repos = await searcher.search_github("test")

            assert repos == cached_data


class TestTrendAnalyzer:
    """Test trend analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create trend analyzer."""
        return TrendAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_technology(self, analyzer):
        """Test technology trend analysis."""
        github_data = {"stars": 75000, "name": "hot-framework"}
        package_data = {"weekly_downloads": 2000000}

        trend = await analyzer.analyze_technology("hot-framework", github_data, package_data)

        assert trend.name == "hot-framework"
        assert trend.momentum == "high"
        assert trend.adoption_stage == "early_majority"
        assert trend.status in ["rising", "stable", "declining"]

    def test_compare_technologies(self, analyzer):
        """Test technology comparison."""
        trends = [
            TechnologyTrend(
                name="Framework A",
                category="web",
                status="rising",
                momentum="high",
                adoption_stage="early_adopter",
                metrics={"github_stars": 50000, "weekly_downloads": 1000000},
            ),
            TechnologyTrend(
                name="Framework B",
                category="web",
                status="stable",
                momentum="medium",
                adoption_stage="early_majority",
                metrics={"github_stars": 30000, "weekly_downloads": 2000000},
            ),
        ]

        comparison = analyzer.compare_technologies(trends)

        assert "winner" in comparison
        assert "by_criteria" in comparison
        assert "recommendation" in comparison


class TestReferenceLibrary:
    """Test reference library."""

    @pytest.fixture
    def library(self, tmp_path):
        """Create library with temp path."""
        return ReferenceLibrary(str(tmp_path / "library"))

    def test_save_and_get_solution(self, library):
        """Test saving and retrieving solutions."""
        solution = Solution(
            name="TestAuth",
            category="authentication",
            type="oss",
            pros=["Free", "Open"],
            cons=["Complex"],
            use_cases=["Enterprise"],
        )

        library.save_solution(solution, "authentication")
        retrieved = library.get_solution("TestAuth", "authentication")

        assert retrieved is not None
        assert retrieved.name == "TestAuth"
        assert "Free" in retrieved.pros

    def test_search_solutions(self, library):
        """Test searching for solutions."""
        # Save test solutions
        auth_solution = Solution(
            name="Auth0",
            category="authentication",
            type="saas",
            pros=["Easy"],
            cons=["Cost"],
            use_cases=["OAuth", "SSO"],
        )
        library.save_solution(auth_solution, "authentication")

        # Search
        results = library.search_solutions("user authentication", requirements=["OAuth"])

        assert len(results) > 0
        assert results[0].name == "Auth0"

    def test_get_recommendations(self, library):
        """Test getting recommendations."""
        # Save test solution
        solution = Solution(
            name="Supabase",
            category="authentication",
            type="oss",
            pros=["Open source"],
            cons=["Self-host complexity"],
            use_cases=["Authentication"],
            korean_cases=[{"company": "StartupX"}],
            pricing={"free_tier": "50000 MAU"},
            integration_effort={"initial_setup": "2 hours"},
        )
        library.save_solution(solution, "authentication")

        # Get recommendations
        recommendations = library.get_recommendations(
            "auth system",
            constraints={"korean_market": True, "budget": "low", "timeline": "urgent"},
        )

        assert recommendations["recommended"] is not None
        assert recommendations["recommended"]["solution"] == "Supabase"
        assert len(recommendations["recommended"]["reasoning"]) > 0


class TestEnhancedResearchAgent:
    """Test enhanced research agent."""

    @pytest.fixture
    def agent(self):
        """Create enhanced research agent."""
        return EnhancedResearchAgent()

    @pytest.mark.asyncio
    async def test_research_solution(self, agent):
        """Test researching solutions."""
        with patch.object(
            agent.searcher, "search_github", return_value=[{"name": "auth-lib", "stars": 5000}]
        ):
            with patch.object(agent.searcher, "search_awesome_lists", return_value=[]):
                with patch.object(agent.library, "search_solutions", return_value=[]):
                    with patch.object(
                        agent.library,
                        "get_recommendations",
                        return_value={
                            "recommended": {"solution": "TestAuth", "reasoning": ["Good fit"]},
                            "alternatives": [],
                        },
                    ):
                        research = await agent.research_solution(
                            "authentication system",
                            requirements=["oauth"],
                            constraints={"budget": "medium"},
                        )

        assert "problem" in research
        assert research["problem"] == "authentication system"
        assert "recommendations" in research
        assert research["recommendations"]["recommended"]["solution"] == "TestAuth"
        assert "external_references" in research

    @pytest.mark.asyncio
    async def test_save_research(self, agent):
        """Test saving research results."""
        research = {
            "recommendations": {
                "recommended": {
                    "solution": "Socket.io",
                    "type": "oss",
                    "pros": ["Real-time"],
                    "cons": ["Scaling"],
                    "korean_cases": [],
                }
            },
            "trends": [{"name": "WebSockets", "status": "stable", "momentum": "medium"}],
        }

        with patch.object(agent.library, "save_solution") as mock_save_solution:
            with patch.object(agent.library, "save_trend") as mock_save_trend:
                await agent.save_research(research, "realtime")

        mock_save_solution.assert_called_once()
        mock_save_trend.assert_called_once()
