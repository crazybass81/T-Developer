# backend/src/agents/implementations/ui_selection/design_system_selector.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class DesignSystemRecommendation:
    name: str
    framework_compatibility: List[str]
    component_count: int
    customization_level: str
    theme_support: bool
    accessibility_score: float
    bundle_size: str
    learning_curve: str
    documentation_quality: str
    community_size: str

class DesignSystemSelector:
    """디자인 시스템 선택기"""
    
    DESIGN_SYSTEMS = {
        'material-ui': {
            'frameworks': ['react'],
            'components': 60,
            'customization': 'high',
            'themes': True,
            'accessibility': 0.9,
            'bundle_size': 'large',
            'learning_curve': 'moderate',
            'documentation': 'excellent',
            'community': 'large',
            'use_cases': ['enterprise', 'admin', 'dashboard']
        },
        'ant-design': {
            'frameworks': ['react'],
            'components': 80,
            'customization': 'high',
            'themes': True,
            'accessibility': 0.85,
            'bundle_size': 'large',
            'learning_curve': 'moderate',
            'documentation': 'excellent',
            'community': 'large',
            'use_cases': ['enterprise', 'admin', 'complex_forms']
        },
        'chakra-ui': {
            'frameworks': ['react'],
            'components': 50,
            'customization': 'very_high',
            'themes': True,
            'accessibility': 0.95,
            'bundle_size': 'medium',
            'learning_curve': 'easy',
            'documentation': 'excellent',
            'community': 'medium',
            'use_cases': ['modern', 'accessible', 'customizable']
        },
        'vuetify': {
            'frameworks': ['vue'],
            'components': 80,
            'customization': 'high',
            'themes': True,
            'accessibility': 0.85,
            'bundle_size': 'large',
            'learning_curve': 'easy',
            'documentation': 'good',
            'community': 'medium',
            'use_cases': ['rapid_development', 'material_design']
        },
        'tailwind-ui': {
            'frameworks': ['react', 'vue', 'angular'],
            'components': 100,
            'customization': 'very_high',
            'themes': True,
            'accessibility': 0.9,
            'bundle_size': 'small',
            'learning_curve': 'moderate',
            'documentation': 'excellent',
            'community': 'large',
            'use_cases': ['custom_design', 'utility_first', 'modern']
        }
    }

    async def select_design_system(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> DesignSystemRecommendation:
        """디자인 시스템 선택"""
        
        # 프레임워크 호환 시스템 필터링
        compatible_systems = {
            name: specs for name, specs in self.DESIGN_SYSTEMS.items()
            if framework in specs['frameworks']
        }
        
        if not compatible_systems:
            return self._get_default_recommendation(framework)
        
        # 요구사항 기반 스코어링
        scored_systems = {}
        for name, specs in compatible_systems.items():
            score = self._calculate_design_system_score(specs, requirements)
            scored_systems[name] = score
        
        # 최고 점수 시스템 선택
        best_system = max(scored_systems.items(), key=lambda x: x[1])
        system_name = best_system[0]
        system_specs = self.DESIGN_SYSTEMS[system_name]
        
        return DesignSystemRecommendation(
            name=system_name,
            framework_compatibility=system_specs['frameworks'],
            component_count=system_specs['components'],
            customization_level=system_specs['customization'],
            theme_support=system_specs['themes'],
            accessibility_score=system_specs['accessibility'],
            bundle_size=system_specs['bundle_size'],
            learning_curve=system_specs['learning_curve'],
            documentation_quality=system_specs['documentation'],
            community_size=system_specs['community']
        )

    def _calculate_design_system_score(
        self,
        specs: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> float:
        """디자인 시스템 점수 계산"""
        
        score = 0.0
        
        # 컴포넌트 수 점수
        component_need = requirements.get('component_complexity', 'medium')
        if component_need == 'high' and specs['components'] > 70:
            score += 0.2
        elif component_need == 'medium' and specs['components'] > 40:
            score += 0.2
        elif component_need == 'low':
            score += 0.2
        
        # 커스터마이제이션 점수
        custom_need = requirements.get('customization_need', 'medium')
        customization_scores = {
            'very_high': {'high': 0.2, 'very_high': 0.2},
            'high': {'high': 0.2, 'very_high': 0.15, 'medium': 0.1},
            'medium': {'medium': 0.2, 'high': 0.15},
            'low': {'low': 0.2, 'medium': 0.15}
        }
        score += customization_scores.get(custom_need, {}).get(specs['customization'], 0)
        
        # 접근성 점수
        if requirements.get('accessibility_important', False):
            score += specs['accessibility'] * 0.2
        
        # 번들 크기 점수
        performance_critical = requirements.get('performance_critical', False)
        if performance_critical:
            bundle_scores = {'small': 0.2, 'medium': 0.1, 'large': 0.0}
            score += bundle_scores.get(specs['bundle_size'], 0)
        
        # 학습 곡선 점수
        timeline = requirements.get('timeline', 'medium')
        if timeline == 'short':
            learning_scores = {'easy': 0.2, 'moderate': 0.1, 'steep': 0.0}
            score += learning_scores.get(specs['learning_curve'], 0)
        
        return score

    def _get_default_recommendation(self, framework: str) -> DesignSystemRecommendation:
        """기본 추천"""
        
        defaults = {
            'react': 'material-ui',
            'vue': 'vuetify',
            'angular': 'angular-material'
        }
        
        default_system = defaults.get(framework, 'tailwind-ui')
        
        if default_system in self.DESIGN_SYSTEMS:
            specs = self.DESIGN_SYSTEMS[default_system]
            return DesignSystemRecommendation(
                name=default_system,
                framework_compatibility=specs['frameworks'],
                component_count=specs['components'],
                customization_level=specs['customization'],
                theme_support=specs['themes'],
                accessibility_score=specs['accessibility'],
                bundle_size=specs['bundle_size'],
                learning_curve=specs['learning_curve'],
                documentation_quality=specs['documentation'],
                community_size=specs['community']
            )
        
        # 폴백
        return DesignSystemRecommendation(
            name='custom',
            framework_compatibility=[framework],
            component_count=0,
            customization_level='very_high',
            theme_support=False,
            accessibility_score=0.5,
            bundle_size='small',
            learning_curve='steep',
            documentation_quality='none',
            community_size='none'
        )