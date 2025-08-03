# backend/src/agents/ui_selection/advanced_selection_features.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import numpy as np

@dataclass
class AdvancedSelectionCriteria:
    performance_weight: float = 0.3
    ecosystem_weight: float = 0.25
    learning_curve_weight: float = 0.2
    maintenance_weight: float = 0.15
    innovation_weight: float = 0.1

@dataclass
class FrameworkAnalysis:
    name: str
    performance_score: float
    ecosystem_score: float
    learning_curve_score: float
    maintenance_score: float
    innovation_score: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]

class AdvancedUISelectionEngine:
    """고급 UI 선택 기능"""
    
    def __init__(self):
        self.ml_predictor = MLFrameworkPredictor()
        self.trend_analyzer = TrendAnalyzer()
        self.compatibility_checker = CompatibilityChecker()
        
    async def analyze_frameworks(
        self,
        requirements: Dict[str, Any],
        criteria: AdvancedSelectionCriteria
    ) -> List[FrameworkAnalysis]:
        """프레임워크 고급 분석"""
        
        frameworks = ['react', 'vue', 'angular', 'svelte', 'nextjs']
        analyses = []
        
        for framework in frameworks:
            # 성능 분석
            perf_score = await self._analyze_performance(framework, requirements)
            
            # 생태계 분석
            eco_score = await self._analyze_ecosystem(framework)
            
            # 학습 곡선 분석
            learning_score = await self._analyze_learning_curve(framework, requirements)
            
            # 유지보수성 분석
            maintenance_score = await self._analyze_maintenance(framework)
            
            # 혁신성 분석
            innovation_score = await self._analyze_innovation(framework)
            
            # 종합 점수
            overall = (
                perf_score * criteria.performance_weight +
                eco_score * criteria.ecosystem_weight +
                learning_score * criteria.learning_curve_weight +
                maintenance_score * criteria.maintenance_weight +
                innovation_score * criteria.innovation_weight
            )
            
            analyses.append(FrameworkAnalysis(
                name=framework,
                performance_score=perf_score,
                ecosystem_score=eco_score,
                learning_curve_score=learning_score,
                maintenance_score=maintenance_score,
                innovation_score=innovation_score,
                overall_score=overall,
                strengths=await self._identify_strengths(framework),
                weaknesses=await self._identify_weaknesses(framework)
            ))
        
        return sorted(analyses, key=lambda x: x.overall_score, reverse=True)
    
    async def _analyze_performance(self, framework: str, requirements: Dict[str, Any]) -> float:
        """성능 분석"""
        metrics = {
            'react': {'bundle_size': 42.2, 'runtime_perf': 85, 'ssr_support': 90},
            'vue': {'bundle_size': 34.8, 'runtime_perf': 88, 'ssr_support': 85},
            'angular': {'bundle_size': 130.0, 'runtime_perf': 82, 'ssr_support': 95},
            'svelte': {'bundle_size': 10.3, 'runtime_perf': 95, 'ssr_support': 80},
            'nextjs': {'bundle_size': 65.0, 'runtime_perf': 90, 'ssr_support': 98}
        }
        
        fw_metrics = metrics.get(framework, {})
        
        # 번들 크기 점수 (작을수록 좋음)
        bundle_score = max(0, 100 - fw_metrics.get('bundle_size', 50))
        
        # 런타임 성능 점수
        runtime_score = fw_metrics.get('runtime_perf', 70)
        
        # SSR 지원 점수
        ssr_score = fw_metrics.get('ssr_support', 70)
        
        return (bundle_score * 0.3 + runtime_score * 0.4 + ssr_score * 0.3) / 100

class MLFrameworkPredictor:
    """ML 기반 프레임워크 예측기"""
    
    async def predict_best_framework(
        self,
        project_features: Dict[str, Any]
    ) -> Tuple[str, float]:
        """최적 프레임워크 예측"""
        
        # 특성 벡터 생성
        features = self._extract_features(project_features)
        
        # 간단한 규칙 기반 예측 (실제로는 ML 모델 사용)
        scores = {
            'react': self._calculate_react_score(features),
            'vue': self._calculate_vue_score(features),
            'angular': self._calculate_angular_score(features),
            'svelte': self._calculate_svelte_score(features),
            'nextjs': self._calculate_nextjs_score(features)
        }
        
        best_framework = max(scores, key=scores.get)
        confidence = scores[best_framework]
        
        return best_framework, confidence
    
    def _extract_features(self, project: Dict[str, Any]) -> np.ndarray:
        """프로젝트 특성 추출"""
        features = []
        
        # 프로젝트 크기
        size_map = {'small': 1, 'medium': 2, 'large': 3}
        features.append(size_map.get(project.get('size', 'medium'), 2))
        
        # 복잡도
        complexity_map = {'low': 1, 'medium': 2, 'high': 3}
        features.append(complexity_map.get(project.get('complexity', 'medium'), 2))
        
        # 팀 경험
        exp_map = {'junior': 1, 'mid': 2, 'senior': 3}
        features.append(exp_map.get(project.get('team_experience', 'mid'), 2))
        
        # 성능 요구사항
        features.append(1 if project.get('high_performance', False) else 0)
        
        # SEO 요구사항
        features.append(1 if project.get('seo_required', False) else 0)
        
        return np.array(features)

class TrendAnalyzer:
    """트렌드 분석기"""
    
    async def analyze_trends(self) -> Dict[str, Dict[str, float]]:
        """프레임워크 트렌드 분석"""
        
        # GitHub Stars, NPM Downloads, Job Market 등 기반
        trends = {
            'react': {
                'popularity': 0.95,
                'growth_rate': 0.15,
                'job_market': 0.90,
                'community_activity': 0.92
            },
            'vue': {
                'popularity': 0.75,
                'growth_rate': 0.25,
                'job_market': 0.65,
                'community_activity': 0.80
            },
            'angular': {
                'popularity': 0.70,
                'growth_rate': 0.05,
                'job_market': 0.75,
                'community_activity': 0.70
            },
            'svelte': {
                'popularity': 0.45,
                'growth_rate': 0.40,
                'job_market': 0.30,
                'community_activity': 0.60
            },
            'nextjs': {
                'popularity': 0.85,
                'growth_rate': 0.35,
                'job_market': 0.80,
                'community_activity': 0.85
            }
        }
        
        return trends

class CompatibilityChecker:
    """호환성 검사기"""
    
    async def check_compatibility(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, bool]:
        """프레임워크 호환성 검사"""
        
        compatibility = {
            'typescript': True,
            'mobile_responsive': True,
            'ssr': True,
            'pwa': True,
            'testing': True
        }
        
        # 프레임워크별 특수 호환성
        if framework == 'svelte':
            compatibility['ssr'] = requirements.get('ssr_required', False) == False
        elif framework == 'angular':
            compatibility['lightweight'] = requirements.get('bundle_size_critical', False) == False
        
        return compatibility

class AdaptiveUISelector:
    """적응형 UI 선택기"""
    
    def __init__(self):
        self.user_feedback = UserFeedbackCollector()
        self.performance_monitor = PerformanceMonitor()
        
    async def adaptive_selection(
        self,
        requirements: Dict[str, Any],
        user_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """사용자 히스토리 기반 적응형 선택"""
        
        # 사용자 선호도 분석
        preferences = await self._analyze_user_preferences(user_history)
        
        # 과거 프로젝트 성공률 분석
        success_rates = await self._analyze_success_rates(user_history)
        
        # 적응형 가중치 계산
        adaptive_weights = self._calculate_adaptive_weights(
            preferences,
            success_rates,
            requirements
        )
        
        return {
            'preferences': preferences,
            'success_rates': success_rates,
            'adaptive_weights': adaptive_weights,
            'recommendation_confidence': self._calculate_confidence(adaptive_weights)
        }
    
    async def _analyze_user_preferences(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """사용자 선호도 분석"""
        
        framework_usage = {}
        total_projects = len(history)
        
        for project in history:
            framework = project.get('framework')
            if framework:
                framework_usage[framework] = framework_usage.get(framework, 0) + 1
        
        # 정규화
        preferences = {
            fw: count / total_projects
            for fw, count in framework_usage.items()
        }
        
        return preferences