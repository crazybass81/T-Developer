"""
T-Developer MVP - Ui_selection_agent

ui_selection_agent 구현체

Author: T-Developer Team
Created: 2025-01-31
"""

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import uuid
from datetime import datetime

from .ui_framework_analyzer import UIFrameworkAnalyzer, ProjectScale
from .design_system_selector import DesignSystemSelector
from .component_library_matcher import ComponentLibraryMatcher
from .boilerplate_generator import BoilerplateGenerator
from .realtime_benchmarker import RealtimePerformanceBenchmarker

@dataclass
class UIRecommendation:
    framework: str
    confidence_score: float
    reasoning: List[str]
    design_system: str
    component_libraries: List[str]
    boilerplate_config: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    implementation_guide: str
    metadata: Optional[Dict[str, Any]] = None
    performance_data: Optional[Dict[str, Any]] = None

class UISelectionAgent:
    """UI 프레임워크 선택 에이전트"""
    
    def __init__(self):
        self.agent = Agent(
            name="UI-Selection-Agent",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="UI Framework Selection Expert",
            instructions=[
                "Analyze project requirements for optimal UI framework selection",
                "Consider performance, SEO, team expertise, and project scale",
                "Provide comprehensive recommendations with alternatives"
            ],
            temperature=0.3
        )
        
        self.framework_analyzer = UIFrameworkAnalyzer()
        self.design_system_selector = DesignSystemSelector()
        self.component_library_matcher = ComponentLibraryMatcher()
        self.boilerplate_generator = BoilerplateGenerator()
        self.realtime_benchmarker = RealtimePerformanceBenchmarker()
        
        self.config = {
            'supported_frameworks': [
                'react', 'vue', 'angular', 'svelte', 'nextjs', 
                'nuxtjs', 'gatsby', 'remix', 'sveltekit'
            ],
            'enable_caching': True,
            'cache_ttl': 3600
        }
    
    async def select_ui_framework(
        self,
        requirements: Dict[str, Any]
    ) -> UIRecommendation:
        """UI 프레임워크 선택 메인 함수"""
        
        # 1. 프로젝트 규모 분석
        project_scale = ProjectScale(
            current_users=requirements.get('current_users', 0),
            expected_users_2years=requirements.get('expected_users', 10000),
            feature_complexity=requirements.get('complexity', 'medium'),
            team_size=requirements.get('team_size', 5),
            development_timeline=requirements.get('timeline', 'medium')
        )
        
        # 2. 프레임워크 분석
        framework_analysis = await self.framework_analyzer.analyze_framework_fit(
            requirements, project_scale
        )
        
        # 3. 실시간 성능 벤치마킹 (옵션)
        performance_data = None
        if requirements.get('enable_realtime_benchmarking', False):
            top_frameworks = sorted(
                framework_analysis.items(),
                key=lambda x: x[1]['scores']['final'],
                reverse=True
            )[:3]
            
            performance_data = {}
            for framework, data in top_frameworks:
                perf_result = await self.realtime_benchmarker.benchmark_framework(
                    framework, requirements
                )
                performance_data[framework] = perf_result
                
                # 성능 데이터를 점수에 반영
                data['scores']['final'] += perf_result['normalized_score'] * 0.2
        
        # 4. 최적 프레임워크 선택
        best_framework = max(
            framework_analysis.items(),
            key=lambda x: x[1]['scores']['final']
        )
        
        framework_name = best_framework[0]
        framework_data = best_framework[1]
        
        # 5. 디자인 시스템 선택
        design_system = await self.design_system_selector.select_design_system(
            framework_name, requirements
        )
        
        # 6. 컴포넌트 라이브러리 매칭
        component_libraries = await self.component_library_matcher.match_libraries(
            framework_name, requirements
        )
        
        # 7. 보일러플레이트 설정
        boilerplate_config = await self.boilerplate_generator.generate_config(
            framework_name, design_system.name, requirements
        )
        
        # 8. 대안 프레임워크 준비
        alternatives = [
            {
                'framework': name,
                'score': data['scores']['final'],
                'pros': data['pros'][:3],
                'cons': data['cons'][:3]
            }
            for name, data in sorted(
                framework_analysis.items(),
                key=lambda x: x[1]['scores']['final'],
                reverse=True
            )[1:4]  # 상위 3개 대안
        ]
        
        # 9. 구현 가이드 생성
        implementation_guide = await self._generate_implementation_guide(
            framework_name, design_system.name, requirements
        )
        
        result = UIRecommendation(
            framework=framework_name,
            confidence_score=framework_data['scores']['final'] / 10.0,
            reasoning=framework_data['pros'],
            design_system=design_system.name,
            component_libraries=[lib['name'] for lib in component_libraries],
            boilerplate_config=boilerplate_config,
            alternatives=alternatives,
            implementation_guide=implementation_guide
        )
        
        # 메타데이터 추가
        result.metadata = {
            'selection_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'project_id': requirements.get('project_id')
        }
        
        if performance_data:
            result.performance_data = performance_data
            
        return result
    
    async def _generate_implementation_guide(
        self,
        framework: str,
        design_system: str,
        requirements: Dict[str, Any]
    ) -> str:
        """구현 가이드 생성"""
        
        guide_prompt = f"""
        Generate a step-by-step implementation guide for:
        - Framework: {framework}
        - Design System: {design_system}
        - Project Requirements: {requirements}
        
        Include:
        1. Project setup commands
        2. Essential dependencies
        3. Basic configuration
        4. First component example
        5. Best practices
        """
        
        response = await self.agent.arun(guide_prompt)
        return response.content
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """설정 업데이트"""
        self.config.update(new_config)
    
    async def compare_frameworks(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """다중 프레임워크 비교"""
        frameworks = requirements.get('compare_frameworks', ['react', 'vue', 'angular'])
        comparison_results = {}
        
        for framework in frameworks:
            framework_req = {**requirements, 'preferred_framework': framework}
            analysis = await self.framework_analyzer.analyze_framework_fit(
                framework_req, ProjectScale()
            )
            
            if framework in analysis:
                comparison_results[framework] = {
                    'score': analysis[framework]['scores']['final'],
                    'pros': analysis[framework]['pros'],
                    'cons': analysis[framework]['cons']
                }
        
        return comparison_results
    
    async def analyze_framework(self, framework_name: str) -> Dict[str, Any]:
        """개별 프레임워크 분석"""
        if framework_name not in self.config['supported_frameworks']:
            raise ValueError(f"Unsupported framework: {framework_name}")
        
        return await self.framework_analyzer.analyze_framework_fit(
            {'detailed_analysis': True}, 
            ProjectScale()
        )
    
    async def select_design_system(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """디자인 시스템 선택"""
        framework = requirements.get('framework', 'react')
        design_system = await self.design_system_selector.select_design_system(
            framework, requirements
        )
        
        return {
            'design_system': design_system.name,
            'compatibility_score': design_system.compatibility_score,
            'reasoning': design_system.reasoning,
            'customization_options': design_system.customization_level,
            'metadata': {
                'selection_timestamp': datetime.utcnow().isoformat()
            }
        }
    
    async def recommend_component_libraries(
        self,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """컴포넌트 라이브러리 추천"""
        framework = requirements.get('framework', 'react')
        libraries = await self.component_library_matcher.match_libraries(
            framework, requirements
        )
        
        return [
            {
                'name': lib['name'],
                'compatibility_score': lib.get('score', 0),
                'supported_components': lib.get('components', [])
            }
            for lib in libraries
        ]
