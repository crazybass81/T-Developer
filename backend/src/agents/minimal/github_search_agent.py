"""GitHub Search Agent - Minimal unit for searching GitHub repositories"""
import json
import random
from typing import Any, Dict, List

from src.agents.evolution.base_agent import BaseEvolutionAgent


class GitHubSearchAgent(BaseEvolutionAgent):
    """GitHub 프로젝트 검색 최소 단위 에이전트"""

    def __init__(self):
        super().__init__(name="GitHubSearchAgent", version="1.0.0")
        self.search_endpoint = "https://api.github.com/search/repositories"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        GitHub 프로젝트 검색 실행
        input_data: {
            "query": "검색어",
            "language": "프로그래밍 언어",
            "sort": "stars/forks/updated",
            "limit": 10
        }
        """
        query = input_data.get("query", "")
        language = input_data.get("language", "Python")
        sort = input_data.get("sort", "stars")
        limit = input_data.get("limit", 5)

        # 실제 구현시 GitHub API 호출
        # 현재는 시뮬레이션 데이터 반환
        projects = self._simulate_github_search(query, language, limit)

        result = {
            "query": query,
            "language": language,
            "total_found": len(projects),
            "projects": projects,
            "search_metadata": {
                "endpoint": self.search_endpoint,
                "sort": sort,
                "timestamp": "2025-08-14T10:00:00Z",
            },
        }

        self.log_execution(input_data, result)
        return result

    def _simulate_github_search(self, query: str, language: str, limit: int) -> List[Dict]:
        """GitHub 검색 시뮬레이션"""
        sample_projects = [
            {
                "name": "AutoGPT",
                "full_name": "Significant-Gravitas/AutoGPT",
                "description": "An experimental open-source attempt to make GPT-4 fully autonomous",
                "stars": 163000,
                "forks": 43000,
                "language": "Python",
                "topics": ["ai", "gpt-4", "autonomous", "agents"],
                "url": "https://github.com/Significant-Gravitas/AutoGPT",
                "relevance_score": 0.95,
            },
            {
                "name": "langchain",
                "full_name": "langchain-ai/langchain",
                "description": "Building applications with LLMs through composability",
                "stars": 89000,
                "forks": 14000,
                "language": "Python",
                "topics": ["llm", "ai", "nlp", "agents"],
                "url": "https://github.com/langchain-ai/langchain",
                "relevance_score": 0.88,
            },
            {
                "name": "MetaGPT",
                "full_name": "geekan/MetaGPT",
                "description": "The Multi-Agent Framework",
                "stars": 42000,
                "forks": 5000,
                "language": "Python",
                "topics": ["multi-agent", "software-development", "ai"],
                "url": "https://github.com/geekan/MetaGPT",
                "relevance_score": 0.92,
            },
            {
                "name": "SuperAGI",
                "full_name": "TransformerOptimus/SuperAGI",
                "description": "A dev-first open source autonomous AI agent framework",
                "stars": 15000,
                "forks": 1800,
                "language": "Python",
                "topics": ["agi", "autonomous-agents", "ai"],
                "url": "https://github.com/TransformerOptimus/SuperAGI",
                "relevance_score": 0.85,
            },
            {
                "name": "AgentGPT",
                "full_name": "reworkd/AgentGPT",
                "description": "Assemble, configure, and deploy autonomous AI Agents",
                "stars": 30000,
                "forks": 9000,
                "language": "TypeScript",
                "topics": ["agent", "gpt", "autonomous", "web"],
                "url": "https://github.com/reworkd/AgentGPT",
                "relevance_score": 0.82,
            },
        ]

        # 언어 필터링
        if language:
            sample_projects = [
                p for p in sample_projects if p["language"].lower() == language.lower()
            ]

        # 쿼리 관련성 정렬
        if query:
            for project in sample_projects:
                # 간단한 관련성 점수 계산
                score = 0
                query_lower = query.lower()
                if query_lower in project["name"].lower():
                    score += 0.3
                if query_lower in project["description"].lower():
                    score += 0.2
                for topic in project["topics"]:
                    if query_lower in topic:
                        score += 0.1
                project["relevance_score"] = min(1.0, project["relevance_score"] + score)

        # 정렬 및 제한
        sample_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        return sample_projects[:limit]

    def get_capabilities(self) -> List[str]:
        return [
            "github_search",
            "repository_analysis",
            "star_ranking",
            "language_filter",
            "topic_search",
            "relevance_scoring",
        ]
