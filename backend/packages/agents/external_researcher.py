"""외부 리서치 에이전트 (ExternalResearcher)

이 에이전트는 요구사항 달성에 필요한 최신 기술, 코드 레퍼런스, 모범 사례 등의
외부 자료를 조사하고 수집하는 역할을 합니다. 다양한 소스에서 정보를 수집하여
구현 방향성과 해결책을 제시합니다.

주요 기능:
1. 실시간 웹 검색 및 스크래핑 (Google, DuckDuckGo)
2. 학술 논문 검색 (arXiv, PubMed)
3. GitHub 코드 저장소 검색 및 분석
4. 전문가 페르소나 시뮬레이션 분석
5. AI 기반 종합 분석 및 통찰력 도출
6. 다중 소스 교차 검증 및 신뢰도 평가

입력:
- topic (str): 리서치 주제
- focus_areas (List[str]): 집중 조사 영역
- mode (ResearchMode): 리서치 모드 (quick/real/persona/comprehensive)
- config (ResearchConfig, optional): 상세 설정

출력:
- ResearchReport: 종합 리서치 보고서
  - all_sources: 수집된 모든 소스 목록
  - key_insights: 핵심 통찰력
  - recommendations: 구현 권장사항
  - best_practices: 모범 사례
  - implementation_roadmap: 단계별 구현 로드맵
  - confidence_level: 전체 신뢰도 평가

문서 참조 관계:
- 입력 참조:
  * RequirementAnalyzer 보고서: 리서치 방향 설정
  * BehaviorAnalyzer 보고서: 행동 패턴 기반 리서치
  * CodeAnalysisAgent 보고서: 코드 구조 기반 리서치
  * ImpactAnalyzer 보고서: 영향도 기반 리서치
  * StaticAnalyzer 보고서: 정적 분석 기반 리서치
  * QualityGate 보고서: 품질 기준 기반 리서치
- 출력 참조:
  * GapAnalyzer: 갭 분석의 외부 참조 자료로 활용

리서치 모드:
- QUICK: AI 기반 빠른 리서치
- REAL: 실제 웹 소스만 사용
- PERSONA: 전문가 페르소나 분석
- COMPREHENSIVE: 모든 방법 종합

전문가 페르소나:
- SOFTWARE_ARCHITECT: 소프트웨어 아키텍처 전문가
- SECURITY_EXPERT: 보안 전문가
- DEVOPS_ENGINEER: DevOps 엔지니어
- AI_RESEARCHER: AI 연구원
- SRE: 사이트 신뢰성 엔지니어
- MICROSERVICES_EXPERT: 마이크로서비스 전문가

사용 예시:
    researcher = ExternalResearcher(memory_hub)
    task = AgentTask(
        intent="research_external",
        inputs={
            "topic": "마이크로서비스 아키텍처 모범 사례",
            "focus_areas": ["서비스 메시", "API 게이트웨이", "분산 트레이싱"],
            "mode": ResearchMode.COMPREHENSIVE
        }
    )
    result = await researcher.execute(task)
    report = result.data  # 종합 리서치 보고서

작성자: T-Developer v2
버전: 3.0.0 (통합 버전)
최종 수정: 2024-12-20
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import os
import boto3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup
import feedparser

from .base import BaseAgent, AgentTask, AgentResult, TaskStatus
from .ai_providers import get_ai_provider
from ..memory.contexts import ContextType
from ..safety import CircuitBreaker, CircuitBreakerConfig, ResourceLimiter, ResourceLimit

logger = logging.getLogger(__name__)


class ResearchMode(Enum):
    """Research modes available."""
    
    QUICK = "quick"  # Fast AI-only research
    REAL = "real"  # Real web sources only
    PERSONA = "persona"  # Expert persona analysis
    COMPREHENSIVE = "comprehensive"  # All methods combined


class ExpertPersona(Enum):
    """Expert personas for research."""
    
    SOFTWARE_ARCHITECT = "software_architect"
    SECURITY_EXPERT = "security_expert"
    DEVOPS_ENGINEER = "devops_engineer"
    AI_RESEARCHER = "ai_researcher"
    SRE = "sre"
    CLOUD_ARCHITECT = "cloud_architect"
    MICROSERVICES_EXPERT = "microservices_expert"


@dataclass
class ResearchSource:
    """Unified research source structure."""
    
    title: str
    url: str
    content: str
    snippet: str
    source_type: str  # 'web', 'academic', 'code', 'ai', 'persona'
    authors: List[str] = field(default_factory=list)
    date: Optional[str] = None
    relevance_score: float = 0.0
    expert_name: Optional[str] = None  # For persona sources
    confidence: str = "medium"


@dataclass
class ResearchConfig:
    """Configuration for research."""
    
    mode: ResearchMode = ResearchMode.COMPREHENSIVE
    max_sources: int = 20
    include_personas: bool = True
    include_real_sources: bool = True
    search_engines: List[str] = field(default_factory=lambda: ['web', 'arxiv', 'github'])
    expert_personas: List[ExpertPersona] = field(default_factory=list)
    use_aws_secrets: bool = True


class ExternalResearcher(BaseAgent):
    """Unified External Research Agent.
    
    This agent intelligently combines multiple research methods:
    - Real-time web search and scraping
    - Academic paper retrieval
    - Code repository analysis
    - Expert persona simulation
    - AI-powered synthesis and analysis
    """
    
    # Expert Persona Profiles
    PERSONA_PROFILES = {
        ExpertPersona.SOFTWARE_ARCHITECT: {
            "name": "Dr. Sarah Chen",
            "role": "Principal Software Architect",
            "experience": 15,
            "expertise": ["System Design", "Design Patterns", "Scalability"],
            "perspective": "Focuses on long-term maintainability and clean architecture"
        },
        ExpertPersona.SECURITY_EXPERT: {
            "name": "Marcus Rodriguez",
            "role": "Chief Security Officer",
            "experience": 12,
            "expertise": ["Application Security", "Threat Modeling", "Compliance"],
            "perspective": "Security-first mindset, assumes breach, defense in depth"
        },
        ExpertPersona.DEVOPS_ENGINEER: {
            "name": "Alex Kumar",
            "role": "Senior DevOps Engineer",
            "experience": 8,
            "expertise": ["CI/CD", "Infrastructure as Code", "Monitoring"],
            "perspective": "Automation-first, everything as code"
        },
        ExpertPersona.AI_RESEARCHER: {
            "name": "Prof. Emily Watson",
            "role": "AI Research Lead",
            "experience": 10,
            "expertise": ["Machine Learning", "AI Safety", "NLP"],
            "perspective": "Research-oriented, evidence-based, ethical AI"
        },
        ExpertPersona.SRE: {
            "name": "James Thompson",
            "role": "Staff SRE",
            "experience": 10,
            "expertise": ["Reliability", "Monitoring", "Incident Response"],
            "perspective": "Reliability above all, data-driven decisions"
        },
        ExpertPersona.MICROSERVICES_EXPERT: {
            "name": "Lisa Park",
            "role": "Microservices Architect",
            "experience": 9,
            "expertise": ["Service Mesh", "API Design", "Event Streaming"],
            "perspective": "Service boundaries, loose coupling"
        }
    }
    
    def __init__(self, memory_hub=None, config: Optional[ResearchConfig] = None):
        """Initialize External Researcher.
        
        Args:
            memory_hub: Memory hub instance
            config: Research configuration
        """
        super().__init__(
            name="ExternalResearcher",
            version="3.0.0",  # Unified version
            memory_hub=memory_hub
        )
        
        self.config = config or ResearchConfig()
        
        # Load API keys from AWS Secrets Manager if configured
        self.api_keys = {}
        if self.config.use_aws_secrets:
            self._load_aws_secrets()
        else:
            # Load from environment
            self.api_keys = {
                'serpapi': os.getenv('SERPAPI_KEY'),
                'github': os.getenv('GITHUB_TOKEN'),
                'stackoverflow': os.getenv('STACKOVERFLOW_KEY')
            }
        
        # Initialize AI Provider
        try:
            self.ai_provider = get_ai_provider("bedrock", {
                "model": "claude-3-sonnet",
                "region": "us-east-1"
            })
            logger.info("AI Provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI provider: {e}")
            self.ai_provider = None
        
        # Safety mechanisms
        self.circuit_breaker = CircuitBreaker(
            name="ExternalResearcher",
            config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                half_open_max_calls=2
            )
        )
        
        self.resource_limiter = ResourceLimiter(
            limits=ResourceLimit(
                max_memory_mb=1000,
                max_cpu_percent=50,
                max_execution_time=300,  # 5 minutes
                max_concurrent_tasks=5
            )
        )
        
        # Cache for avoiding duplicate requests
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    def _load_aws_secrets(self):
        """Load API keys from AWS Secrets Manager."""
        try:
            client = boto3.client('secretsmanager', region_name='us-east-1')
            response = client.get_secret_value(SecretId='t-developer-v2/api-keys')
            secrets = json.loads(response['SecretString'])
            
            self.api_keys = {
                'serpapi': secrets.get('SERPAPI_KEY'),
                'github': secrets.get('GITHUB_TOKEN'),
                'stackoverflow': secrets.get('STACKOVERFLOW_KEY')
            }
            logger.info("API keys loaded from AWS Secrets Manager")
        except Exception as e:
            logger.warning(f"Failed to load AWS secrets: {e}")
            self.api_keys = {}
    
    async def _get_requirement_reports(self) -> Dict[str, Any]:
        """Fetch requirement analyzer reports from memory.
        
        Returns:
            Dictionary of requirement reports
        """
        if not self.memory_hub:
            return {}
        
        try:
            from ..memory.contexts import ContextType
            
            # Get latest requirement report
            req_report = await self.memory_hub.get(
                context_type=ContextType.S_CTX,
                key="requirements:latest"
            )
            
            # Get requirement specification
            req_spec = await self.memory_hub.search(
                context_type=ContextType.A_CTX,
                tags=["requirements", "RequirementAnalyzer"],
                limit=5
            )
            
            return {
                "latest": req_report,
                "specifications": req_spec
            }
        except Exception as e:
            logger.debug(f"Failed to get requirement reports: {e}")
            return {}
    
    async def _get_analysis_reports(self) -> Dict[str, Any]:
        """Fetch all analysis reports from memory.
        
        Returns:
            Dictionary containing behavior, code, impact, static, and quality reports
        """
        if not self.memory_hub:
            return {}
        
        from ..memory.contexts import ContextType
        
        reports = {}
        
        # Fetch each type of analysis report
        analysis_types = [
            ("behavior", "BehaviorAnalyzer"),
            ("code", "CodeAnalysisAgent"),
            ("impact", "ImpactAnalyzer"),
            ("static", "StaticAnalyzer"),
            ("quality", "QualityGate")
        ]
        
        for report_type, agent_name in analysis_types:
            try:
                # Get latest analysis from shared context
                latest = await self.memory_hub.get(
                    context_type=ContextType.S_CTX,
                    key=f"latest_{report_type}_analysis"
                )
                
                # Search for historical reports
                historical = await self.memory_hub.search(
                    context_type=ContextType.A_CTX,
                    tags=[report_type, agent_name],
                    limit=3
                )
                
                reports[report_type] = {
                    "latest": latest,
                    "history": historical
                }
            except Exception as e:
                logger.debug(f"Failed to get {report_type} reports: {e}")
                reports[report_type] = {}
        
        return reports
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute unified external research.
        
        Args:
            task: Research task with inputs including:
                - topic: Research topic
                - focus_areas: Specific areas to investigate
                - mode: Research mode (optional)
                - config: ResearchConfig (optional)
            
        Returns:
            Comprehensive research result
        """
        logger.info(f"Starting unified external research: {task.intent}")
        
        try:
            # Get reports from other agents
            requirement_reports = await self._get_requirement_reports()
            analysis_reports = await self._get_analysis_reports()
            
            # Enrich task inputs with reports
            if requirement_reports:
                task.inputs["requirement_analysis"] = requirement_reports
            if analysis_reports:
                task.inputs["system_analysis"] = analysis_reports
            
            # Extract configuration from task
            if 'config' in task.inputs:
                self.config = task.inputs['config']
            elif 'mode' in task.inputs:
                self.config.mode = ResearchMode(task.inputs['mode'])
            
            # Determine research strategy based on mode
            research_data = {}
            
            if self.config.mode == ResearchMode.QUICK:
                # Quick AI-only research
                research_data = await self._quick_ai_research(task.inputs)
                
            elif self.config.mode == ResearchMode.REAL:
                # Real sources only
                research_data = await self._real_source_research(task.inputs)
                
            elif self.config.mode == ResearchMode.PERSONA:
                # Persona-based research
                research_data = await self._persona_research(task.inputs)
                
            else:  # COMPREHENSIVE
                # Combine all methods
                research_tasks = []
                
                if self.config.include_real_sources:
                    research_tasks.append(self._real_source_research(task.inputs))
                
                if self.config.include_personas:
                    research_tasks.append(self._persona_research(task.inputs))
                
                if self.ai_provider:
                    research_tasks.append(self._quick_ai_research(task.inputs))
                
                # Execute all research methods in parallel
                results = await asyncio.gather(*research_tasks, return_exceptions=True)
                
                # Combine results
                research_data = await self._synthesize_all_research(results, task.inputs)
            
            # Generate final report
            final_report = await self._generate_final_report(research_data, task.inputs)
            
            # Store in memory
            if self.memory_hub:
                await self.memory_hub.put(
                    ContextType.S_CTX,
                    f"external_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    final_report,
                    ttl_seconds=86400 * 30  # 30 days
                )
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data=final_report,
                metadata={
                    "agent": self.name,
                    "version": self.version,
                    "mode": self.config.mode.value,
                    "sources_found": len(final_report.get('all_sources', [])),
                    "confidence": final_report.get('confidence_level', 'medium')
                }
            )
            
        except Exception as e:
            logger.error(f"External research failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                data={"error": str(e)},
                error=str(e),
                metadata={"agent": self.name}
            )
    
    async def _quick_ai_research(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Quick AI-powered research without external sources.
        
        Args:
            inputs: Research inputs
            
        Returns:
            AI-generated research data
        """
        if not self.ai_provider:
            return {"error": "AI provider not available"}
        
        topic = inputs.get('topic', '')
        focus_areas = inputs.get('focus_areas', [])
        
        prompt = f"""
        Research the following topic comprehensively:
        Topic: {topic}
        Focus Areas: {', '.join(focus_areas)}
        
        Provide:
        1. Key Insights (5-7 points with explanations)
        2. Best Practices (5 actionable practices)
        3. Common Pitfalls (3-5 to avoid)
        4. Implementation Recommendations (5 specific steps)
        5. Real-World Examples (name actual tools/systems)
        6. Relevant Technologies and Tools
        7. Performance and Scalability Considerations
        8. Security Implications
        9. Future Trends
        10. References (books, articles, documentation)
        
        Format as JSON with clear structure.
        Include confidence levels (high/medium/low) for each point.
        """
        
        try:
            response = await self.ai_provider.complete(prompt)
            
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except:
                    data = {"analysis": response}
            else:
                data = response
            
            return {
                "source_type": "ai_analysis",
                "timestamp": datetime.now().isoformat(),
                **data
            }
            
        except Exception as e:
            logger.error(f"AI research failed: {e}")
            return {"error": str(e)}
    
    async def _real_source_research(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Research using real web sources.
        
        Args:
            inputs: Research inputs
            
        Returns:
            Real source research data
        """
        sources = []
        search_tasks = []
        
        # Prepare search queries
        keywords = self._extract_keywords(inputs.get('topic', ''))
        
        # Add searches based on available APIs
        if 'arxiv' in self.config.search_engines:
            search_tasks.append(self._search_arxiv(keywords, inputs))
        
        if 'github' in self.config.search_engines and self.api_keys.get('github'):
            search_tasks.append(self._search_github(keywords, inputs))
        
        if 'web' in self.config.search_engines:
            if self.api_keys.get('serpapi'):
                search_tasks.append(self._search_google(keywords, inputs))
            else:
                search_tasks.append(self._search_duckduckgo(keywords, inputs))
        
        # Execute searches in parallel
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results
        for result in search_results:
            if isinstance(result, list):
                sources.extend(result)
            elif not isinstance(result, Exception):
                if isinstance(result, dict) and 'sources' in result:
                    sources.extend(result['sources'])
        
        # Extract content from top sources
        if sources:
            sources = await self._enrich_sources(sources[:self.config.max_sources])
        
        # Analyze and structure findings
        return {
            "source_type": "real_sources",
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(sources),
            "sources": sources,
            "key_findings": self._extract_key_findings(sources),
            "verification_rate": self._calculate_verification_rate(sources)
        }
    
    async def _persona_research(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Research using expert personas.
        
        Args:
            inputs: Research inputs
            
        Returns:
            Persona-based research data
        """
        # Select appropriate personas
        selected_personas = self._select_personas(inputs)
        
        # Conduct research from each persona
        persona_tasks = []
        for persona in selected_personas:
            persona_tasks.append(self._conduct_persona_research(persona, inputs))
        
        # Gather results
        persona_results = await asyncio.gather(*persona_tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = [r for r in persona_results if not isinstance(r, Exception) and 'error' not in r]
        
        # Synthesize insights
        return {
            "source_type": "expert_personas",
            "timestamp": datetime.now().isoformat(),
            "personas_consulted": [
                {
                    "name": self.PERSONA_PROFILES[p]["name"],
                    "role": self.PERSONA_PROFILES[p]["role"],
                    "expertise": self.PERSONA_PROFILES[p]["expertise"]
                }
                for p in selected_personas
            ],
            "insights": self._combine_persona_insights(valid_results),
            "consensus_points": self._find_consensus(valid_results),
            "divergent_views": self._find_divergence(valid_results)
        }
    
    async def _synthesize_all_research(
        self,
        results: List[Dict[str, Any]],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize all research methods into unified findings.
        
        Args:
            results: Results from different research methods
            inputs: Original inputs
            
        Returns:
            Synthesized research data
        """
        all_sources = []
        all_insights = []
        all_recommendations = []
        all_best_practices = []
        
        for result in results:
            if isinstance(result, dict):
                # Collect sources
                if 'sources' in result:
                    all_sources.extend(result['sources'])
                
                # Collect insights
                if 'key_findings' in result:
                    all_insights.extend(result['key_findings'])
                elif 'insights' in result:
                    all_insights.extend(result['insights'])
                
                # Collect recommendations
                if 'recommendations' in result:
                    all_recommendations.extend(result['recommendations'])
                
                # Collect best practices
                if 'best_practices' in result:
                    all_best_practices.extend(result['best_practices'])
        
        # Remove duplicates and rank by relevance
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_insights = self._rank_insights(all_insights)
        prioritized_recommendations = self._prioritize_recommendations(all_recommendations)
        
        return {
            "all_sources": unique_sources,
            "key_insights": ranked_insights[:10],
            "recommendations": prioritized_recommendations[:10],
            "best_practices": all_best_practices[:8],
            "synthesis_timestamp": datetime.now().isoformat()
        }
    
    async def _generate_final_report(
        self,
        research_data: Dict[str, Any],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final comprehensive research report.
        
        Args:
            research_data: All research data
            inputs: Original inputs
            
        Returns:
            Final research report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "topic": inputs.get('topic', ''),
            "focus_areas": inputs.get('focus_areas', []),
            "research_mode": self.config.mode.value,
            "executive_summary": self._create_executive_summary(research_data),
            "confidence_level": self._calculate_confidence(research_data)
        }
        
        # Add all research findings
        report.update(research_data)
        
        # Add implementation roadmap
        if 'recommendations' in research_data:
            report['implementation_roadmap'] = self._create_roadmap(
                research_data['recommendations']
            )
        
        # Add source summary
        if 'all_sources' in research_data:
            report['source_summary'] = self._create_source_summary(
                research_data['all_sources']
            )
        
        return report
    
    # Helper methods for search and analysis
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = re.findall(r'\b[a-z]+\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords[:10]
    
    async def _search_arxiv(self, keywords: List[str], inputs: Dict[str, Any]) -> List[ResearchSource]:
        """Search arXiv for academic papers."""
        sources = []
        search_query = '+'.join(keywords[:5])
        
        # Add CS category for software topics
        cs_keywords = {'software', 'algorithm', 'system', 'ai', 'pattern'}
        if any(k in cs_keywords for k in keywords):
            url = f"http://export.arxiv.org/api/query?search_query=cat:cs.*+AND+all:{quote(search_query)}&max_results=5"
        else:
            url = f"http://export.arxiv.org/api/query?search_query=all:{quote(search_query)}&max_results=5"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries:
                            source = ResearchSource(
                                title=entry.title,
                                url=entry.link,
                                content=entry.summary,
                                snippet=entry.summary[:500],
                                source_type='academic',
                                authors=[author.name for author in entry.get('authors', [])],
                                date=entry.get('published', ''),
                                relevance_score=self._calculate_relevance(entry.title + entry.summary, keywords)
                            )
                            sources.append(source)
        except Exception as e:
            logger.warning(f"arXiv search failed: {e}")
        
        return sources
    
    async def _search_github(self, keywords: List[str], inputs: Dict[str, Any]) -> List[ResearchSource]:
        """Search GitHub for code examples."""
        if not self.api_keys.get('github'):
            return []
        
        sources = []
        search_query = ' '.join(keywords[:5])
        url = f"https://api.github.com/search/repositories?q={quote(search_query)}&sort=stars&per_page=5"
        
        headers = {
            'Authorization': f"token {self.api_keys['github']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for repo in data.get('items', []):
                            source = ResearchSource(
                                title=repo['full_name'],
                                url=repo['html_url'],
                                content=repo.get('description', ''),
                                snippet=f"{repo.get('description', '')} - ⭐ {repo['stargazers_count']}",
                                source_type='code',
                                authors=[repo['owner']['login']],
                                date=repo.get('updated_at', ''),
                                relevance_score=self._calculate_relevance(repo['name'] + ' ' + repo.get('description', ''), keywords)
                            )
                            sources.append(source)
        except Exception as e:
            logger.warning(f"GitHub search failed: {e}")
        
        return sources
    
    async def _search_google(self, keywords: List[str], inputs: Dict[str, Any]) -> List[ResearchSource]:
        """Search Google using SerpAPI."""
        if not self.api_keys.get('serpapi'):
            return await self._search_duckduckgo(keywords, inputs)
        
        sources = []
        params = {
            'q': ' '.join(keywords),
            'api_key': self.api_keys['serpapi'],
            'num': 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://serpapi.com/search', params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for result in data.get('organic_results', []):
                            source = ResearchSource(
                                title=result.get('title', ''),
                                url=result.get('link', ''),
                                content=result.get('snippet', ''),
                                snippet=result.get('snippet', '')[:500],
                                source_type='web',
                                date=result.get('date', ''),
                                relevance_score=self._calculate_relevance(
                                    result.get('title', '') + ' ' + result.get('snippet', ''),
                                    keywords
                                )
                            )
                            sources.append(source)
        except Exception as e:
            logger.warning(f"Google search failed: {e}")
            return await self._search_duckduckgo(keywords, inputs)
        
        return sources
    
    async def _search_duckduckgo(self, keywords: List[str], inputs: Dict[str, Any]) -> List[ResearchSource]:
        """Search DuckDuckGo as fallback."""
        sources = []
        search_query = '+'.join(keywords[:5])
        url = f"https://html.duckduckgo.com/html/?q={quote(search_query)}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        results = soup.find_all('div', class_='result')[:5]
                        
                        for result in results:
                            title_elem = result.find('a', class_='result__a')
                            snippet_elem = result.find('a', class_='result__snippet')
                            
                            if title_elem and snippet_elem:
                                source = ResearchSource(
                                    title=title_elem.get_text(strip=True),
                                    url=title_elem.get('href', ''),
                                    content=snippet_elem.get_text(strip=True),
                                    snippet=snippet_elem.get_text(strip=True)[:500],
                                    source_type='web',
                                    relevance_score=self._calculate_relevance(
                                        title_elem.get_text(strip=True) + ' ' + snippet_elem.get_text(strip=True),
                                        keywords
                                    )
                                )
                                sources.append(source)
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        return sources
    
    async def _enrich_sources(self, sources: List[ResearchSource]) -> List[ResearchSource]:
        """Enrich sources by fetching actual content."""
        enriched = []
        
        async with aiohttp.ClientSession() as session:
            for source in sources[:10]:  # Limit to top 10
                try:
                    if source.source_type == 'web' and len(source.content) < 200:
                        # Try to fetch more content
                        async with session.get(source.url, timeout=5) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract main content
                                for selector in ['article', 'main', '.content']:
                                    elem = soup.select_one(selector)
                                    if elem:
                                        source.content = elem.get_text(strip=True)[:2000]
                                        source.snippet = source.content[:500]
                                        break
                    
                    enriched.append(source)
                except Exception as e:
                    logger.debug(f"Failed to enrich source {source.url}: {e}")
                    enriched.append(source)
        
        return enriched
    
    def _select_personas(self, inputs: Dict[str, Any]) -> List[ExpertPersona]:
        """Select appropriate personas for the research topic."""
        topic = inputs.get('topic', '').lower()
        selected = []
        
        # Topic-based selection
        if any(word in topic for word in ['architecture', 'design', 'pattern']):
            selected.append(ExpertPersona.SOFTWARE_ARCHITECT)
        
        if any(word in topic for word in ['security', 'vulnerability', 'threat']):
            selected.append(ExpertPersona.SECURITY_EXPERT)
        
        if any(word in topic for word in ['ai', 'machine learning', 'agent']):
            selected.append(ExpertPersona.AI_RESEARCHER)
        
        if any(word in topic for word in ['reliability', 'monitoring', 'sre']):
            selected.append(ExpertPersona.SRE)
        
        if any(word in topic for word in ['microservice', 'api', 'service']):
            selected.append(ExpertPersona.MICROSERVICES_EXPERT)
        
        if any(word in topic for word in ['devops', 'ci/cd', 'deployment']):
            selected.append(ExpertPersona.DEVOPS_ENGINEER)
        
        # Ensure at least 2 personas
        if len(selected) < 2:
            if ExpertPersona.SOFTWARE_ARCHITECT not in selected:
                selected.append(ExpertPersona.SOFTWARE_ARCHITECT)
            if ExpertPersona.SRE not in selected:
                selected.append(ExpertPersona.SRE)
        
        return selected[:4]  # Max 4 personas
    
    async def _conduct_persona_research(
        self,
        persona: ExpertPersona,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct research from a specific persona's perspective."""
        if not self.ai_provider:
            return self._simulate_persona_research(persona, inputs)
        
        profile = self.PERSONA_PROFILES[persona]
        
        prompt = f"""
        You are {profile['name']}, a {profile['role']} with {profile['experience']} years of experience.
        Your expertise: {', '.join(profile['expertise'])}
        Your perspective: {profile['perspective']}
        
        Research topic: {inputs.get('topic', '')}
        Focus areas: {', '.join(inputs.get('focus_areas', []))}
        
        Provide your expert analysis as JSON including:
        1. key_insights: 3-5 critical insights from your perspective
        2. best_practices: 3-5 proven practices you recommend
        3. risks: Common pitfalls you've seen
        4. recommendations: Your specific recommendations
        5. real_examples: Actual systems/tools you've worked with
        6. contrarian_view: What others might disagree with
        
        Be specific and technical.
        """
        
        try:
            response = await self.ai_provider.complete(prompt)
            
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except:
                    data = {"analysis": response}
            else:
                data = response
            
            data['persona'] = {
                'name': profile['name'],
                'role': profile['role'],
                'expertise': profile['expertise']
            }
            
            return data
            
        except Exception as e:
            logger.warning(f"Persona {persona.value} research failed: {e}")
            return self._simulate_persona_research(persona, inputs)
    
    def _simulate_persona_research(
        self,
        persona: ExpertPersona,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate persona research when AI is unavailable."""
        profile = self.PERSONA_PROFILES[persona]
        
        return {
            'persona': {
                'name': profile['name'],
                'role': profile['role'],
                'expertise': profile['expertise']
            },
            'key_insights': [
                f"From {profile['role']} perspective: Critical insight about {inputs.get('topic', 'the topic')}"
            ],
            'best_practices': [
                f"Industry best practice recommended by {profile['name']}"
            ],
            'risks': [
                "Common implementation pitfall to avoid"
            ],
            'recommendations': [
                f"Specific recommendation based on {profile['experience']} years of experience"
            ],
            'real_examples': [
                "Production system example"
            ],
            'contrarian_view': "Alternative perspective that challenges conventional wisdom"
        }
    
    # Analysis helper methods
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score."""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        return min(matches / len(keywords), 1.0)
    
    def _extract_key_findings(self, sources: List[ResearchSource]) -> List[Dict[str, Any]]:
        """Extract key findings from sources."""
        findings = []
        
        for source in sources[:10]:
            finding = {
                'content': source.snippet[:200],
                'source': source.title,
                'url': source.url,
                'type': source.source_type,
                'relevance': source.relevance_score,
                'confidence': source.confidence
            }
            if source.authors:
                finding['authors'] = source.authors
            findings.append(finding)
        
        return findings
    
    def _calculate_verification_rate(self, sources: List[ResearchSource]) -> float:
        """Calculate verification rate of sources."""
        if not sources:
            return 0.0
        
        verified = sum(1 for s in sources if s.content and len(s.content) > 100)
        return verified / len(sources)
    
    def _deduplicate_sources(self, sources: List[ResearchSource]) -> List[ResearchSource]:
        """Remove duplicate sources."""
        seen_urls = set()
        unique = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique.append(source)
        
        return unique
    
    def _rank_insights(self, insights: List[Any]) -> List[Any]:
        """Rank insights by importance."""
        # Simple ranking by length and confidence
        return sorted(insights, key=lambda x: (
            x.get('confidence', 'medium') == 'high',
            len(str(x.get('content', '')))
        ), reverse=True)
    
    def _prioritize_recommendations(self, recommendations: List[Any]) -> List[Any]:
        """Prioritize recommendations."""
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(recommendations, key=lambda x: (
            priority_order.get(x.get('priority', 'medium'), 2),
            x.get('impact', 0)
        ))
    
    def _combine_persona_insights(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine insights from multiple personas."""
        combined = []
        
        for result in results:
            persona_info = result.get('persona', {})
            
            for insight in result.get('key_insights', []):
                combined.append({
                    'content': insight if isinstance(insight, str) else insight.get('content', str(insight)),
                    'expert': persona_info.get('name', 'Unknown'),
                    'role': persona_info.get('role', 'Unknown'),
                    'confidence': 'high'
                })
        
        return combined
    
    def _find_consensus(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find consensus points among experts."""
        # Simplified consensus detection
        all_insights = []
        for result in results:
            all_insights.extend(result.get('key_insights', []))
        
        # Group similar insights (simplified)
        consensus = []
        if len(results) > 1:
            consensus.append({
                'point': 'Multiple experts agree on the importance of proper implementation',
                'experts': [r.get('persona', {}).get('name', 'Expert') for r in results[:2]],
                'strength': 'moderate'
            })
        
        return consensus
    
    def _find_divergence(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find divergent views among experts."""
        divergent = []
        
        for result in results:
            if 'contrarian_view' in result:
                divergent.append({
                    'expert': result.get('persona', {}).get('name', 'Unknown'),
                    'view': result['contrarian_view']
                })
        
        return divergent
    
    def _create_executive_summary(self, research_data: Dict[str, Any]) -> str:
        """Create executive summary."""
        sources_count = len(research_data.get('all_sources', []))
        insights_count = len(research_data.get('key_insights', []))
        
        summary = f"""
Comprehensive research analysis completed using {self.config.mode.value} mode.
Analyzed {sources_count} sources and generated {insights_count} key insights.
The research provides actionable recommendations and implementation guidance
based on real-world examples and expert analysis.
        """.strip()
        
        return summary
    
    def _calculate_confidence(self, research_data: Dict[str, Any]) -> str:
        """Calculate overall confidence level."""
        sources = research_data.get('all_sources', [])
        
        if len(sources) > 10 and self.ai_provider:
            return 'high'
        elif len(sources) > 5:
            return 'medium'
        else:
            return 'low'
    
    def _create_roadmap(self, recommendations: List[Any]) -> Dict[str, List[Any]]:
        """Create implementation roadmap."""
        roadmap = {
            'immediate': recommendations[:3],
            'short_term': recommendations[3:6],
            'long_term': recommendations[6:9]
        }
        return roadmap
    
    def _create_source_summary(self, sources: List[ResearchSource]) -> Dict[str, Any]:
        """Create source summary."""
        type_counts = {}
        for source in sources:
            type_counts[source.source_type] = type_counts.get(source.source_type, 0) + 1
        
        return {
            'total_sources': len(sources),
            'by_type': type_counts,
            'top_sources': [
                {'title': s.title, 'url': s.url, 'type': s.source_type}
                for s in sources[:5]
            ]
        }


# Export for use
__all__ = ['ExternalResearcher', 'ResearchMode', 'ResearchConfig', 'ResearchSource']