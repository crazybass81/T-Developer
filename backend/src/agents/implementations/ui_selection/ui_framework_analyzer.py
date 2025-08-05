# Task 4.2: UI Selection Agent - Framework Analysis System
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class FrameworkProfile:
    name: str
    type: str
    learning_curve: float
    performance_score: float
    ecosystem_size: int
    community_activity: float
    enterprise_adoption: float
    mobile_support: bool
    ssr_support: bool
    pwa_support: bool

@dataclass
class ProjectScale:
    current_users: int
    expected_users_2years: int
    feature_complexity: str
    team_size: int
    development_timeline: str

class UIFrameworkAnalyzer:
    """UI 프레임워크 분석 및 선택 시스템"""

    def __init__(self):
        self.agent = Agent(
            name="UI-Framework-Analyzer",
            model=AwsBedrock(id="anthropic.claude-3-opus-v1:0"),
            role="UI Framework Selection Expert",
            instructions=[
                "Analyze project requirements for optimal UI framework selection",
                "Consider performance, scalability, and team expertise",
                "Provide detailed comparison and recommendations"
            ]
        )
        
        self.framework_profiles = self._load_framework_profiles()
        self.compatibility_matrix = CompatibilityMatrix()
        self.performance_benchmarker = PerformanceBenchmarker()

    def _load_framework_profiles(self) -> Dict[str, FrameworkProfile]:
        """프레임워크 프로필 로드"""
        return {
            'react': FrameworkProfile(
                name='React',
                type='library',
                learning_curve=7.0,
                performance_score=8.5,
                ecosystem_size=95,
                community_activity=9.5,
                enterprise_adoption=9.0,
                mobile_support=True,
                ssr_support=True,
                pwa_support=True
            ),
            'vue': FrameworkProfile(
                name='Vue.js',
                type='framework',
                learning_curve=8.5,
                performance_score=8.8,
                ecosystem_size=75,
                community_activity=8.5,
                enterprise_adoption=7.5,
                mobile_support=True,
                ssr_support=True,
                pwa_support=True
            ),
            'angular': FrameworkProfile(
                name='Angular',
                type='framework',
                learning_curve=6.0,
                performance_score=8.0,
                ecosystem_size=85,
                community_activity=8.0,
                enterprise_adoption=9.5,
                mobile_support=True,
                ssr_support=True,
                pwa_support=True
            ),
            'nextjs': FrameworkProfile(
                name='Next.js',
                type='meta-framework',
                learning_curve=7.5,
                performance_score=9.0,
                ecosystem_size=80,
                community_activity=9.0,
                enterprise_adoption=8.5,
                mobile_support=False,
                ssr_support=True,
                pwa_support=True
            )
        }

    async def analyze_framework_fit(
        self,
        requirements: Dict[str, Any],
        project_scale: ProjectScale
    ) -> Dict[str, Any]:
        """프레임워크 적합성 분석"""

        analysis_results = {}
        
        for framework_name, profile in self.framework_profiles.items():
            # 1. 기본 적합성 점수
            base_score = await self._calculate_base_score(profile, requirements)
            
            # 2. 확장성 평가
            scalability_score = await self._evaluate_scalability(profile, project_scale)
            
            # 3. 팀 적합성
            team_fit_score = await self._evaluate_team_fit(profile, requirements)
            
            # 4. 성능 벤치마크
            performance_data = await self.performance_benchmarker.benchmark_framework(
                framework_name, requirements
            )
            
            # 5. 종합 점수 계산
            final_score = (
                base_score * 0.3 +
                scalability_score * 0.25 +
                team_fit_score * 0.25 +
                performance_data['normalized_score'] * 0.2
            )
            
            analysis_results[framework_name] = {
                'profile': profile,
                'scores': {
                    'base': base_score,
                    'scalability': scalability_score,
                    'team_fit': team_fit_score,
                    'performance': performance_data['normalized_score'],
                    'final': final_score
                },
                'performance_data': performance_data,
                'pros': await self._generate_pros(profile, requirements),
                'cons': await self._generate_cons(profile, requirements),
                'recommendation': await self._generate_recommendation(
                    profile, final_score, requirements
                )
            }

        return analysis_results

    async def _calculate_base_score(
        self,
        profile: FrameworkProfile,
        requirements: Dict[str, Any]
    ) -> float:
        """기본 적합성 점수 계산"""
        
        score = 0.0
        
        # 프로젝트 타입 적합성
        project_type = requirements.get('project_type', 'web')
        if project_type == 'mobile' and profile.mobile_support:
            score += 2.0
        elif project_type == 'web':
            score += 1.5
            
        # SSR 요구사항
        if requirements.get('ssr_required') and profile.ssr_support:
            score += 1.5
            
        # PWA 요구사항
        if requirements.get('pwa_required') and profile.pwa_support:
            score += 1.0
            
        # 성능 요구사항
        if requirements.get('high_performance'):
            score += profile.performance_score * 0.3
            
        return min(10.0, score)

    async def _evaluate_scalability(
        self,
        profile: FrameworkProfile,
        project_scale: ProjectScale
    ) -> float:
        """확장성 평가"""
        
        # 사용자 규모에 따른 점수
        if project_scale.expected_users_2years > 1000000:  # 대규모
            if profile.name in ['Angular', 'Next.js']:
                return 9.0
            elif profile.name == 'React':
                return 8.5
            else:
                return 7.0
        elif project_scale.expected_users_2years > 100000:  # 중규모
            return 8.0
        else:  # 소규모
            return 9.0

    async def _evaluate_team_fit(
        self,
        profile: FrameworkProfile,
        requirements: Dict[str, Any]
    ) -> float:
        """팀 적합성 평가"""
        
        team_experience = requirements.get('team_experience', [])
        team_size = requirements.get('team_size', 5)
        
        score = 5.0  # 기본 점수
        
        # 팀 경험 반영
        if profile.name.lower() in [exp.lower() for exp in team_experience]:
            score += 3.0
        
        # 학습 곡선 고려
        if team_size < 3:  # 소규모 팀
            score += (profile.learning_curve - 5.0) * 0.5
        
        # 엔터프라이즈 환경
        if requirements.get('enterprise_environment'):
            score += profile.enterprise_adoption * 0.3
            
        return min(10.0, max(1.0, score))

class CompatibilityMatrix:
    """프레임워크 호환성 매트릭스"""
    
    async def check_compatibility(
        self,
        primary_framework: str,
        additional_tools: List[str]
    ) -> Dict[str, Any]:
        """호환성 검사"""
        
        compatibility_scores = {}
        conflicts = []
        
        for tool in additional_tools:
            score = await self._calculate_compatibility_score(primary_framework, tool)
            compatibility_scores[tool] = score
            
            if score < 5.0:
                conflicts.append({
                    'tool': tool,
                    'issue': f'Low compatibility with {primary_framework}',
                    'severity': 'medium' if score > 3.0 else 'high'
                })
        
        return {
            'scores': compatibility_scores,
            'conflicts': conflicts,
            'overall_compatibility': sum(compatibility_scores.values()) / len(compatibility_scores) if compatibility_scores else 10.0
        }

    async def _calculate_compatibility_score(self, framework: str, tool: str) -> float:
        """호환성 점수 계산"""
        # 실제 구현에서는 데이터베이스나 API에서 호환성 데이터 조회
        compatibility_data = {
            ('react', 'typescript'): 9.5,
            ('react', 'webpack'): 9.0,
            ('vue', 'typescript'): 8.5,
            ('angular', 'typescript'): 10.0,
        }
        
        return compatibility_data.get((framework.lower(), tool.lower()), 7.0)

class PerformanceBenchmarker:
    """성능 벤치마크 시스템"""
    
    async def benchmark_framework(
        self,
        framework_name: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """프레임워크 성능 벤치마크"""
        
        # 실제 구현에서는 실제 벤치마크 실행
        benchmark_data = {
            'react': {
                'bundle_size_kb': 42.2,
                'initial_load_ms': 1200,
                'runtime_performance': 8.5,
                'memory_usage_mb': 15.3
            },
            'vue': {
                'bundle_size_kb': 34.8,
                'initial_load_ms': 950,
                'runtime_performance': 8.8,
                'memory_usage_mb': 12.1
            },
            'angular': {
                'bundle_size_kb': 130.5,
                'initial_load_ms': 1800,
                'runtime_performance': 8.0,
                'memory_usage_mb': 22.7
            },
            'nextjs': {
                'bundle_size_kb': 65.3,
                'initial_load_ms': 800,
                'runtime_performance': 9.0,
                'memory_usage_mb': 18.9
            }
        }
        
        data = benchmark_data.get(framework_name, {})
        
        # 정규화된 점수 계산
        normalized_score = await self._calculate_normalized_score(data, requirements)
        
        return {
            'raw_data': data,
            'normalized_score': normalized_score,
            'performance_grade': self._get_performance_grade(normalized_score)
        }

    async def _calculate_normalized_score(
        self,
        data: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> float:
        """정규화된 성능 점수 계산"""
        
        if not data:
            return 5.0
            
        # 가중치 설정
        weights = {
            'bundle_size': 0.2,
            'initial_load': 0.3,
            'runtime_performance': 0.3,
            'memory_usage': 0.2
        }
        
        # 성능 요구사항에 따른 가중치 조정
        if requirements.get('mobile_first'):
            weights['bundle_size'] = 0.4
            weights['initial_load'] = 0.4
            weights['runtime_performance'] = 0.1
            weights['memory_usage'] = 0.1
        
        # 점수 계산 (낮을수록 좋은 지표들은 역수 사용)
        bundle_score = max(1, 10 - (data.get('bundle_size_kb', 50) / 10))
        load_score = max(1, 10 - (data.get('initial_load_ms', 1000) / 200))
        runtime_score = data.get('runtime_performance', 5.0)
        memory_score = max(1, 10 - (data.get('memory_usage_mb', 20) / 5))
        
        final_score = (
            bundle_score * weights['bundle_size'] +
            load_score * weights['initial_load'] +
            runtime_score * weights['runtime_performance'] +
            memory_score * weights['memory_usage']
        )
        
        return min(10.0, max(1.0, final_score))

    def _get_performance_grade(self, score: float) -> str:
        """성능 등급 반환"""
        if score >= 8.5:
            return 'A'
        elif score >= 7.0:
            return 'B'
        elif score >= 5.5:
            return 'C'
        else:
            return 'D'