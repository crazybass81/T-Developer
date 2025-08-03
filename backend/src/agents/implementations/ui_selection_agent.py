# backend/src/agents/implementations/ui_selection_agent.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock

@dataclass
class UIFrameworkRecommendation:
    framework: str
    confidence_score: float
    reasons: List[str]
    pros: List[str]
    cons: List[str]
    alternatives: List[Dict[str, Any]]
    setup_complexity: str
    learning_curve: str
    community_support: str
    performance_score: float
    seo_friendliness: float
    mobile_readiness: float
    ecosystem_maturity: float

class ProjectType(Enum):
    SPA = "single_page_application"
    MPA = "multi_page_application"
    SSG = "static_site_generation"
    SSR = "server_side_rendering"
    PWA = "progressive_web_app"
    HYBRID = "hybrid_application"

class UISelectionAgent:
    """프로젝트 요구사항에 따른 최적의 UI 프레임워크 선택"""

    FRAMEWORK_MATRIX = {
        'react': {
            'type': ['spa', 'ssr', 'ssg', 'pwa'],
            'ecosystem': 'excellent',
            'performance': 'good',
            'seo': 'moderate',
            'mobile': 'react-native',
            'learning_curve': 'moderate',
            'use_cases': ['complex_spa', 'dashboard', 'real_time', 'enterprise'],
            'strengths': ['component_reusability', 'ecosystem', 'flexibility', 'community'],
            'weaknesses': ['learning_curve', 'boilerplate', 'decision_fatigue']
        },
        'nextjs': {
            'type': ['ssr', 'ssg', 'spa', 'pwa'],
            'ecosystem': 'excellent',
            'performance': 'excellent',
            'seo': 'excellent',
            'mobile': 'responsive',
            'learning_curve': 'moderate',
            'use_cases': ['seo_critical', 'ecommerce', 'blog', 'marketing', 'saas'],
            'strengths': ['seo', 'performance', 'dx', 'full_stack'],
            'weaknesses': ['vendor_lock', 'complexity', 'opinionated']
        },
        'vue': {
            'type': ['spa', 'ssr', 'pwa'],
            'ecosystem': 'good',
            'performance': 'excellent',
            'seo': 'good',
            'mobile': 'responsive',
            'learning_curve': 'easy',
            'use_cases': ['rapid_prototype', 'small_medium', 'incremental', 'interactive'],
            'strengths': ['gentle_learning', 'flexibility', 'performance', 'documentation'],
            'weaknesses': ['smaller_ecosystem', 'enterprise_adoption', 'scaling_concerns']
        },
        'angular': {
            'type': ['spa', 'pwa', 'enterprise'],
            'ecosystem': 'good',
            'performance': 'good',
            'seo': 'moderate',
            'mobile': 'ionic',
            'learning_curve': 'steep',
            'use_cases': ['enterprise', 'large_team', 'complex_forms', 'long_term'],
            'strengths': ['typescript', 'structure', 'tooling', 'enterprise_ready'],
            'weaknesses': ['complexity', 'bundle_size', 'learning_curve', 'verbose']
        },
        'svelte': {
            'type': ['spa', 'ssg', 'pwa'],
            'ecosystem': 'growing',
            'performance': 'excellent',
            'seo': 'good',
            'mobile': 'responsive',
            'learning_curve': 'easy',
            'use_cases': ['performance_critical', 'small_bundle', 'innovative', 'interactive'],
            'strengths': ['performance', 'simplicity', 'no_virtual_dom', 'compile_time'],
            'weaknesses': ['ecosystem', 'job_market', 'enterprise_adoption', 'tooling']
        }
    }

    def __init__(self):
        self.analyzer = Agent(
            name="UI-Framework-Analyzer",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Senior frontend architect specializing in framework selection",
            instructions=[
                "Analyze project requirements for optimal UI framework selection",
                "Consider performance, SEO, team expertise, and project constraints",
                "Provide detailed reasoning for recommendations",
                "Evaluate ecosystem maturity and long-term viability"
            ],
            temperature=0.3
        )
        
        self.performance_analyzer = PerformanceAnalyzer()
        self.compatibility_checker = CompatibilityChecker()
        self.trend_analyzer = TrendAnalyzer()
        
        # UI Selection 모듈들
        from .ui_selection import DesignSystemSelector, ComponentLibraryMatcher, BoilerplateGenerator
        self.design_system_selector = DesignSystemSelector()
        self.component_library_matcher = ComponentLibraryMatcher()
        self.boilerplate_generator = BoilerplateGenerator()

    async def select_ui_framework(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> UIFrameworkRecommendation:
        """UI 프레임워크 선택"""
        
        # 요구사항 분석
        analyzed_reqs = await self._analyze_requirements(requirements)
        
        # 프레임워크 스코어링
        framework_scores = await self._score_frameworks(analyzed_reqs, context)
        
        # 최적 프레임워크 선택
        best_framework = max(framework_scores.items(), key=lambda x: x[1]['total_score'])
        
        # 상세 분석
        detailed_analysis = await self._detailed_analysis(
            best_framework[0],
            analyzed_reqs,
            context
        )
        
        return UIFrameworkRecommendation(
            framework=best_framework[0],
            confidence_score=best_framework[1]['total_score'],
            reasons=detailed_analysis['reasons'],
            pros=detailed_analysis['pros'],
            cons=detailed_analysis['cons'],
            alternatives=self._get_alternatives(framework_scores, best_framework[0]),
            setup_complexity=detailed_analysis['setup_complexity'],
            learning_curve=detailed_analysis['learning_curve'],
            community_support=detailed_analysis['community_support'],
            performance_score=best_framework[1]['performance'],
            seo_friendliness=best_framework[1]['seo'],
            mobile_readiness=best_framework[1]['mobile'],
            ecosystem_maturity=best_framework[1]['ecosystem']
        )

    async def _analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """요구사항 분석"""
        
        project_type = self._determine_project_type(requirements)
        performance_needs = self._assess_performance_needs(requirements)
        seo_importance = self._assess_seo_importance(requirements)
        team_expertise = requirements.get('team_expertise', {})
        timeline = requirements.get('timeline', 'medium')
        
        return {
            'project_type': project_type,
            'performance_needs': performance_needs,
            'seo_importance': seo_importance,
            'team_expertise': team_expertise,
            'timeline': timeline,
            'target_platforms': requirements.get('target_platforms', ['web']),
            'expected_scale': requirements.get('expected_scale', 'medium'),
            'budget_constraints': requirements.get('budget_constraints', 'medium')
        }

    async def _score_frameworks(
        self,
        analyzed_reqs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """프레임워크 스코어링"""
        
        scores = {}
        
        for framework, specs in self.FRAMEWORK_MATRIX.items():
            score = await self._calculate_framework_score(
                framework,
                specs,
                analyzed_reqs,
                context
            )
            scores[framework] = score
            
        return scores

    async def _calculate_framework_score(
        self,
        framework: str,
        specs: Dict[str, Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """개별 프레임워크 점수 계산"""
        
        # 프로젝트 타입 매칭
        type_score = self._score_project_type_match(
            requirements['project_type'],
            specs['type']
        )
        
        # 성능 점수
        performance_score = await self.performance_analyzer.analyze(
            framework,
            requirements['performance_needs']
        )
        
        # SEO 점수
        seo_score = self._score_seo_capability(
            specs['seo'],
            requirements['seo_importance']
        )
        
        # 팀 전문성 매칭
        expertise_score = self._score_team_expertise(
            framework,
            requirements['team_expertise']
        )
        
        # 생태계 성숙도
        ecosystem_score = self._score_ecosystem(specs['ecosystem'])
        
        # 학습 곡선
        learning_score = self._score_learning_curve(
            specs['learning_curve'],
            requirements['timeline']
        )
        
        # 가중 평균
        total_score = (
            type_score * 0.25 +
            performance_score * 0.20 +
            seo_score * 0.15 +
            expertise_score * 0.15 +
            ecosystem_score * 0.15 +
            learning_score * 0.10
        )
        
        return {
            'total_score': total_score,
            'type_match': type_score,
            'performance': performance_score,
            'seo': seo_score,
            'expertise': expertise_score,
            'ecosystem': ecosystem_score,
            'learning': learning_score
        }

    def _determine_project_type(self, requirements: Dict[str, Any]) -> str:
        """프로젝트 타입 결정"""
        
        # SEO 중요도가 높으면 SSR/SSG
        if requirements.get('seo_critical', False):
            return 'ssr'
            
        # 정적 콘텐츠가 많으면 SSG
        if requirements.get('content_type') == 'static':
            return 'ssg'
            
        # 실시간 기능이 많으면 SPA
        if requirements.get('real_time_features', False):
            return 'spa'
            
        # 모바일 앱도 필요하면 PWA
        if 'mobile' in requirements.get('target_platforms', []):
            return 'pwa'
            
        return 'spa'  # 기본값

    def _assess_performance_needs(self, requirements: Dict[str, Any]) -> str:
        """성능 요구사항 평가"""
        
        expected_users = requirements.get('expected_users', 1000)
        
        if expected_users > 100000:
            return 'high'
        elif expected_users > 10000:
            return 'medium'
        else:
            return 'low'

    def _assess_seo_importance(self, requirements: Dict[str, Any]) -> str:
        """SEO 중요도 평가"""
        
        if requirements.get('seo_critical', False):
            return 'critical'
        elif requirements.get('marketing_site', False):
            return 'high'
        elif requirements.get('public_facing', True):
            return 'medium'
        else:
            return 'low'

class PerformanceAnalyzer:
    """성능 분석기"""
    
    async def analyze(self, framework: str, performance_needs: str) -> float:
        """프레임워크 성능 분석"""
        
        performance_ratings = {
            'react': {'high': 0.7, 'medium': 0.8, 'low': 0.9},
            'nextjs': {'high': 0.9, 'medium': 0.95, 'low': 0.95},
            'vue': {'high': 0.85, 'medium': 0.9, 'low': 0.95},
            'angular': {'high': 0.75, 'medium': 0.8, 'low': 0.85},
            'svelte': {'high': 0.95, 'medium': 0.95, 'low': 0.95}
        }
        
        return performance_ratings.get(framework, {}).get(performance_needs, 0.5)

class CompatibilityChecker:
    """호환성 검사기"""
    
    async def check_browser_compatibility(
        self,
        framework: str,
        target_browsers: List[str]
    ) -> Dict[str, bool]:
        """브라우저 호환성 검사"""
        
        compatibility_matrix = {
            'react': {
                'chrome': True,
                'firefox': True,
                'safari': True,
                'edge': True,
                'ie11': False
            },
            'vue': {
                'chrome': True,
                'firefox': True,
                'safari': True,
                'edge': True,
                'ie11': True
            },
            'angular': {
                'chrome': True,
                'firefox': True,
                'safari': True,
                'edge': True,
                'ie11': True
            }
        }
        
        framework_compat = compatibility_matrix.get(framework, {})
        return {browser: framework_compat.get(browser, False) for browser in target_browsers}

class TrendAnalyzer:
    """트렌드 분석기"""
    
    async def analyze_trends(self, framework: str) -> Dict[str, Any]:
        """프레임워크 트렌드 분석"""
        
        # 실제로는 GitHub API, npm 다운로드 등을 사용
        trend_data = {
            'react': {
                'popularity_trend': 'stable',
                'job_market': 'excellent',
                'github_stars': 200000,
                'npm_downloads': 20000000,
                'community_activity': 'very_high'
            },
            'vue': {
                'popularity_trend': 'growing',
                'job_market': 'good',
                'github_stars': 200000,
                'npm_downloads': 4000000,
                'community_activity': 'high'
            },
            'angular': {
                'popularity_trend': 'declining',
                'job_market': 'good',
                'github_stars': 90000,
                'npm_downloads': 3000000,
                'community_activity': 'medium'
            }
        }
        
        return trend_data.get(framework, {})

    def _score_project_type_match(self, project_type: str, supported_types: List[str]) -> float:
        """프로젝트 타입 매칭 점수"""
        if project_type in supported_types:
            return 1.0
        # 유사 타입 매칭
        similar_matches = {
            'spa': ['pwa'],
            'ssr': ['ssg'],
            'pwa': ['spa']
        }
        if any(similar in supported_types for similar in similar_matches.get(project_type, [])):
            return 0.8
        return 0.3
    
    def _score_seo_capability(self, framework_seo: str, importance: str) -> float:
        """SEO 능력 점수"""
        seo_scores = {
            'excellent': {'critical': 1.0, 'high': 1.0, 'medium': 0.9, 'low': 0.8},
            'good': {'critical': 0.8, 'high': 0.9, 'medium': 0.8, 'low': 0.7},
            'moderate': {'critical': 0.5, 'high': 0.6, 'medium': 0.7, 'low': 0.8},
            'poor': {'critical': 0.2, 'high': 0.3, 'medium': 0.5, 'low': 0.7}
        }
        return seo_scores.get(framework_seo, {}).get(importance, 0.5)
    
    def _score_team_expertise(self, framework: str, team_expertise: Dict[str, str]) -> float:
        """팀 전문성 매칭"""
        expertise_level = team_expertise.get(framework, 'none')
        expertise_scores = {
            'expert': 1.0,
            'advanced': 0.8,
            'intermediate': 0.6,
            'beginner': 0.3,
            'none': 0.0
        }
        return expertise_scores.get(expertise_level, 0.0)
    
    def _score_ecosystem(self, ecosystem: str) -> float:
        """생태계 성숙도 점수"""
        ecosystem_scores = {
            'excellent': 1.0,
            'good': 0.8,
            'growing': 0.6,
            'emerging': 0.4
        }
        return ecosystem_scores.get(ecosystem, 0.5)
    
    def _score_learning_curve(self, learning_curve: str, timeline: str) -> float:
        """학습 곡선 점수"""
        if timeline == 'short':
            curve_scores = {'easy': 1.0, 'moderate': 0.6, 'steep': 0.2}
        elif timeline == 'medium':
            curve_scores = {'easy': 1.0, 'moderate': 0.8, 'steep': 0.5}
        else:  # long
            curve_scores = {'easy': 1.0, 'moderate': 0.9, 'steep': 0.8}
        return curve_scores.get(learning_curve, 0.5)
    
    def _get_alternatives(self, framework_scores: Dict[str, Dict[str, float]], selected: str) -> List[Dict[str, Any]]:
        """대안 프레임워크 목록 생성"""
        alternatives = []
        sorted_frameworks = sorted(
            framework_scores.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        
        for framework, scores in sorted_frameworks:
            if framework != selected and len(alternatives) < 3:
                alternatives.append({
                    'framework': framework,
                    'score': scores['total_score'],
                    'reason': f"Alternative with {scores['total_score']:.2f} score"
                })
        return alternatives
    
    async def _detailed_analysis(
        self,
        framework: str,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """상세 분석"""
        specs = self.FRAMEWORK_MATRIX[framework]
        
        return {
            'reasons': [
                f"Excellent match for {requirements['project_type']} projects",
                f"Strong {specs['ecosystem']} ecosystem support",
                f"Suitable for {requirements['timeline']} timeline"
            ],
            'pros': specs['strengths'],
            'cons': specs['weaknesses'],
            'setup_complexity': 'medium',
            'learning_curve': specs['learning_curve'],
            'community_support': specs['ecosystem']
        }