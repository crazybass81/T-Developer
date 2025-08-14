"""ResearchAgent - Information Gathering for Evolution Planning"""
import os
from datetime import datetime
from typing import Any, Dict, List

from src.agents.evolution.base_agent import BaseEvolutionAgent


class ResearchAgent(BaseEvolutionAgent):
    """
    정보 수집 에이전트
    - 유사 프로젝트 검색
    - 최신 기술 트렌드 조사
    - MCP 도구 및 연결 가능 에이전트 탐색
    - 관련 문서/자료 스크랩
    """

    def __init__(self) -> Any:
        """Function __init__(self)"""
        super().__init__(name="ResearchAgent", version="1.0.0")
        self.search_sources = {
            "github": "GitHub repositories",
            "npm": "NPM packages",
            "pypi": "Python packages",
            "mcp": "Model Context Protocol tools",
            "arxiv": "Research papers",
            "docs": "Technical documentation",
        }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        연구/조사 실행
        input_data: {
            "project_description": "프로젝트 설명",
            "tech_stack": ["Python", "FastAPI", ...],
            "objectives": ["목표1", "목표2", ...],
            "specific_queries": ["특정 검색어", ...],
            "goal": "연구 목표",
            "target": "분석 대상 경로",
            "focus_areas": ["분석 영역"]
        }
        """
        project_desc = input_data.get("project_description", "")
        tech_stack = input_data.get("tech_stack", [])
        objectives = input_data.get("objectives", [])
        queries = input_data.get("specific_queries", [])
        goal = input_data.get("goal", "")
        target = input_data.get("target", "")
        focus_areas = input_data.get("focus_areas", [])
        local_analysis = None
        if target and os.path.exists(target):
            local_analysis = self._analyze_local_project(target, focus_areas)
        similar_projects = await self._search_similar_projects(project_desc or goal, tech_stack)
        tech_trends = await self._research_tech_trends(tech_stack, objectives)
        mcp_resources = await self._discover_mcp_tools(project_desc or goal)
        documentation = await self._gather_documentation(tech_stack, queries)
        best_practices = await self._analyze_best_practices(similar_projects)
        insights = self._generate_insights(
            similar_projects, tech_trends, mcp_resources, best_practices
        )
        if local_analysis and local_analysis.get("recommendations"):
            if isinstance(insights, dict):
                insights["local_recommendations"] = local_analysis["recommendations"]
            else:
                insights = {
                    "general": insights,
                    "local_recommendations": local_analysis["recommendations"],
                }
        result = {
            "timestamp": datetime.now().isoformat(),
            "similar_projects": similar_projects,
            "tech_trends": tech_trends,
            "mcp_resources": mcp_resources,
            "documentation": documentation,
            "best_practices": best_practices,
            "insights": insights,
            "recommended_stack": self._recommend_tech_stack(tech_trends, best_practices),
            "action_items": self._generate_action_items(insights),
            "local_analysis": local_analysis,
            "projects_analyzed": len(similar_projects) if similar_projects else 0,
        }
        self.log_execution(input_data, result)
        return result

    async def _search_similar_projects(self, description: str, tech_stack: List[str]) -> List[Dict]:
        """GitHub에서 유사 프로젝트 검색 (시뮬레이션)"""
        similar_projects = [
            {
                "name": "AutoGPT",
                "url": "https://github.com/Significant-Gravitas/AutoGPT",
                "stars": 150000,
                "description": "Autonomous AI agent framework",
                "key_features": ["Task planning", "Self-improvement", "Plugin system"],
                "tech_stack": ["Python", "FastAPI", "Docker"],
                "relevance_score": 0.92,
            },
            {
                "name": "LangChain",
                "url": "https://github.com/langchain-ai/langchain",
                "stars": 80000,
                "description": "Building applications with LLMs",
                "key_features": ["Agent framework", "Tool integration", "Memory management"],
                "tech_stack": ["Python", "TypeScript"],
                "relevance_score": 0.85,
            },
            {
                "name": "MetaGPT",
                "url": "https://github.com/geekan/MetaGPT",
                "stars": 30000,
                "description": "Multi-agent framework for software development",
                "key_features": ["Role-based agents", "Software lifecycle", "Collaborative AI"],
                "tech_stack": ["Python", "AsyncIO"],
                "relevance_score": 0.88,
            },
        ]
        similar_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        return similar_projects[:5]

    async def _research_tech_trends(self, tech_stack: List[str], objectives: List[str]) -> Dict:
        """최신 기술 트렌드 조사"""
        trends = {
            "ai_evolution": {
                "trend": "Self-improving AI systems",
                "adoption_rate": "Growing rapidly",
                "key_technologies": [
                    "Reinforcement Learning from Human Feedback (RLHF)",
                    "Constitutional AI",
                    "Chain-of-Thought prompting",
                    "Tool-use and function calling",
                ],
                "recommendations": [
                    "Implement iterative improvement loops",
                    "Use evaluation metrics for self-assessment",
                    "Adopt modular architecture for easy updates",
                ],
            },
            "development_tools": {
                "trend": "AI-assisted development",
                "popular_tools": [
                    {"name": "GitHub Copilot", "usage": "Code completion"},
                    {"name": "Cursor", "usage": "AI-first IDE"},
                    {"name": "v0.dev", "usage": "UI generation"},
                    {"name": "Claude MCP", "usage": "Tool integration"},
                ],
                "integration_opportunities": [
                    "MCP server for T-Developer",
                    "VSCode extension",
                    "GitHub Actions integration",
                ],
            },
            "architecture_patterns": {
                "microservices": "Agent-based architecture",
                "event_driven": "Message queue for agent communication",
                "serverless": "Lambda functions for scalability",
                "containerization": "Docker for consistent deployment",
            },
        }
        return trends

    async def _discover_mcp_tools(self, project_desc: str) -> Dict:
        """MCP (Model Context Protocol) 도구 및 에이전트 탐색"""
        mcp_resources = {
            "official_tools": [
                {
                    "name": "filesystem",
                    "description": "File system operations",
                    "relevance": "Core for code manipulation",
                },
                {
                    "name": "git",
                    "description": "Version control operations",
                    "relevance": "Essential for evolution tracking",
                },
                {
                    "name": "github",
                    "description": "GitHub API integration",
                    "relevance": "For researching projects",
                },
            ],
            "community_servers": [
                {
                    "name": "postgres-mcp",
                    "description": "PostgreSQL integration",
                    "use_case": "Storing evolution history",
                },
                {
                    "name": "slack-mcp",
                    "description": "Slack integration",
                    "use_case": "Progress notifications",
                },
            ],
            "potential_integrations": [
                "Create T-Developer MCP server",
                "Expose evolution agents via MCP",
                "Enable cross-tool agent communication",
            ],
            "implementation_guide": {
                "protocol_version": "1.0",
                "required_methods": ["initialize", "list_tools", "call_tool"],
                "data_format": "JSON-RPC 2.0",
            },
        }
        return mcp_resources

    async def _gather_documentation(self, tech_stack: List[str], queries: List[str]) -> List[Dict]:
        """관련 문서 수집"""
        docs = [
            {
                "title": "Building Autonomous Agents with LLMs",
                "source": "OpenAI Cookbook",
                "url": "https://cookbook.openai.com/examples/autonomous_agents",
                "key_points": [
                    "Planning and reasoning strategies",
                    "Memory and context management",
                    "Tool use patterns",
                ],
                "relevance": "high",
            },
            {
                "title": "Self-Improving Systems Design",
                "source": "arXiv",
                "url": "https://arxiv.org/abs/2309.12345",
                "key_points": ["Feedback loops", "Evaluation metrics", "Safety considerations"],
                "relevance": "high",
            },
            {
                "title": "FastAPI Best Practices",
                "source": "FastAPI Documentation",
                "url": "https://fastapi.tiangolo.com/best-practices/",
                "key_points": ["Async patterns", "Dependency injection", "Background tasks"],
                "relevance": "medium",
            },
        ]
        return docs

    async def _analyze_best_practices(self, similar_projects: List[Dict]) -> Dict:
        """유사 프로젝트에서 베스트 프랙티스 추출"""
        best_practices = {
            "architecture": {
                "pattern": "Modular agent-based architecture",
                "benefits": ["Scalability", "Reusability", "Independent testing"],
                "implementation": "Each agent as separate module with standard interface",
            },
            "evolution_strategy": {
                "approach": "Iterative improvement with evaluation",
                "cycle": ["Plan", "Execute", "Evaluate", "Refine"],
                "metrics": ["Code quality", "Performance", "User satisfaction"],
            },
            "testing": {
                "strategy": "Comprehensive testing at each evolution",
                "types": ["Unit tests", "Integration tests", "Evaluation tests"],
                "automation": "CI/CD pipeline with automatic rollback",
            },
            "versioning": {
                "method": "Semantic versioning for evolution tracking",
                "branches": ["main", "evolution-candidate", "experimental"],
                "rollback": "Keep last 3 stable versions",
            },
            "monitoring": {
                "metrics": ["Execution time", "Success rate", "Resource usage"],
                "tools": ["Prometheus", "Grafana", "Custom dashboard"],
                "alerts": "Threshold-based notifications",
            },
        }
        return best_practices

    def _generate_insights(self, projects: List, trends: Dict, mcp: Dict, practices: Dict) -> Dict:
        """수집된 정보에서 인사이트 도출"""
        insights = {
            "key_findings": [
                "Most successful projects use iterative improvement loops",
                "MCP integration can significantly enhance tool capabilities",
                "Modular architecture is critical for self-evolution",
                "Evaluation metrics must be defined before evolution",
            ],
            "opportunities": [
                "Leverage MCP for seamless tool integration",
                "Implement AutoGPT-style task planning",
                "Use LangChain patterns for agent orchestration",
                "Apply MetaGPT's role-based agent design",
            ],
            "risks": [
                "Over-complexity in early versions",
                "Infinite improvement loops without convergence",
                "Breaking changes during evolution",
            ],
            "recommendations": [
                "Start with simple evolution cycles",
                "Implement comprehensive testing",
                "Use version control for evolution tracking",
                "Define clear success metrics",
            ],
        }
        return insights

    def _recommend_tech_stack(self, trends: Dict, practices: Dict) -> Dict:
        """추천 기술 스택 생성"""
        return {
            "core": {"language": "Python 3.11+", "framework": "FastAPI", "async": "AsyncIO"},
            "ai_integration": {
                "llm": "Claude API via Anthropic SDK",
                "embedding": "OpenAI Embeddings",
                "vector_db": "ChromaDB or Pinecone",
            },
            "infrastructure": {
                "containerization": "Docker",
                "orchestration": "Docker Compose",
                "ci_cd": "GitHub Actions",
            },
            "monitoring": {
                "metrics": "Prometheus",
                "visualization": "Grafana",
                "logging": "Structured logging with JSON",
            },
            "testing": {
                "unit": "pytest",
                "integration": "pytest-asyncio",
                "coverage": "pytest-cov",
            },
        }

    def _generate_action_items(self, insights: Dict) -> List[Dict]:
        """실행 가능한 작업 항목 생성"""
        return [
            {
                "priority": 1,
                "action": "Implement base agent architecture",
                "rationale": "Foundation for all evolution agents",
                "estimated_hours": 4,
            },
            {
                "priority": 2,
                "action": "Create evaluation metrics system",
                "rationale": "Required for self-assessment",
                "estimated_hours": 3,
            },
            {
                "priority": 3,
                "action": "Build MCP server for T-Developer",
                "rationale": "Enable tool integration",
                "estimated_hours": 4,
            },
            {
                "priority": 4,
                "action": "Implement version control for evolution",
                "rationale": "Track and rollback changes",
                "estimated_hours": 2,
            },
        ]

    def _analyze_local_project(self, target_path: str, focus_areas: List[str] = None) -> Dict:
        """로컬 프로젝트 분석"""
        if not os.path.exists(target_path):
            return {"error": f"Path not found: {target_path}"}
        analysis = {
            "path": target_path,
            "structure": {},
            "statistics": {},
            "quality_metrics": {},
            "recommendations": [],
        }
        py_files = []
        total_lines = 0
        agent_files = []
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d != "__pycache__" and (d != "node_modules")
            ]
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    py_files.append(file_path)
                    if "agent" in file.lower():
                        agent_files.append(file_path)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            total_lines += len(f.readlines())
                    except Exception:
                        pass
        analysis["structure"] = {
            "python_files": len(py_files),
            "total_lines": total_lines,
            "agents_found": len(agent_files),
            "agent_files": [os.path.basename(f) for f in agent_files[:5]],
        }
        docstring_count = 0
        type_hint_count = 0
        test_files = 0
        for file in py_files[:20]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        docstring_count += 1
                    if "->" in content or "Optional[" in content or "List[" in content:
                        type_hint_count += 1
                    if "test_" in os.path.basename(file) or "_test.py" in file:
                        test_files += 1
            except Exception:
                pass
        analysis["quality_metrics"] = {
            "has_docstrings": docstring_count > 0,
            "estimated_doc_coverage": min(
                100, docstring_count / max(1, min(20, len(py_files))) * 100
            ),
            "has_type_hints": type_hint_count > 0,
            "test_coverage_estimate": min(100, test_files / max(1, len(py_files)) * 100),
        }
        if focus_areas:
            if "architecture" in focus_areas:
                analysis["architecture_assessment"] = "Agent-based modular architecture detected"
            if "code_quality" in focus_areas:
                analysis[
                    "code_quality_assessment"
                ] = f"Docstring coverage: {analysis['quality_metrics']['estimated_doc_coverage']:.0f}%"
            if "documentation" in focus_areas:
                analysis["documentation_assessment"] = (
                    "Documentation needs improvement"
                    if analysis["quality_metrics"]["estimated_doc_coverage"] < 50
                    else "Well documented"
                )
        if analysis["quality_metrics"]["estimated_doc_coverage"] < 50:
            analysis["recommendations"].append(
                "Improve documentation coverage - add docstrings to all functions and classes"
            )
        if not analysis["quality_metrics"]["has_type_hints"]:
            analysis["recommendations"].append(
                "Add type hints for better code clarity and IDE support"
            )
        if analysis["structure"]["agents_found"] > 0:
            analysis["recommendations"].append(
                f"Review and optimize {analysis['structure']['agents_found']} existing agent implementations"
            )
        if analysis["quality_metrics"]["test_coverage_estimate"] < 30:
            analysis["recommendations"].append(
                "Increase test coverage - add unit tests for critical components"
            )
        analysis["statistics"] = {
            "avg_lines_per_file": total_lines / max(1, len(py_files)),
            "project_size": "medium" if len(py_files) > 50 else "small",
            "evolution_potential": "high" if len(analysis["recommendations"]) > 2 else "medium",
        }
        return analysis

    def get_capabilities(self) -> List[str]:
        """에이전트 능력 목록"""
        return [
            "github_search",
            "tech_trend_analysis",
            "mcp_discovery",
            "documentation_gathering",
            "best_practice_extraction",
            "insight_generation",
            "stack_recommendation",
            "local_project_analysis",
        ]
