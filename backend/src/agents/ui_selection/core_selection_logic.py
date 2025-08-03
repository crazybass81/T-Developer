"""
UI Selection Agent - Core Selection Logic
SubTasks 4.21.2-4.21.4 Implementation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ProjectType(Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    STATIC_SITE = "static_site"

@dataclass
class UISelectionCriteria:
    project_type: ProjectType
    team_size: int
    timeline: str
    performance_requirements: Dict[str, Any]
    target_platforms: List[str]

@dataclass
class FrameworkScore:
    framework: str
    score: float
    reasoning: List[str]
    pros: List[str]
    cons: List[str]

class CoreSelectionLogic:
    """Core UI framework selection logic"""
    
    def __init__(self):
        self.framework_matrix = {
            'react': {
                'learning_curve': 'medium',
                'performance': 'high',
                'best_for': ['web_app', 'mobile_app'],
                'team_size_fit': {'small': 0.9, 'medium': 1.0, 'large': 0.8}
            },
            'vue': {
                'learning_curve': 'low',
                'performance': 'high',
                'best_for': ['web_app'],
                'team_size_fit': {'small': 1.0, 'medium': 0.9, 'large': 0.7}
            },
            'nextjs': {
                'learning_curve': 'medium',
                'performance': 'excellent',
                'best_for': ['web_app', 'static_site'],
                'team_size_fit': {'small': 0.8, 'medium': 1.0, 'large': 0.9}
            }
        }
    
    async def select_framework(self, criteria: UISelectionCriteria) -> List[FrameworkScore]:
        """Select optimal UI framework"""
        scores = []
        
        for framework, config in self.framework_matrix.items():
            score = await self._calculate_framework_score(framework, config, criteria)
            scores.append(score)
        
        return sorted(scores, key=lambda x: x.score, reverse=True)
    
    async def _calculate_framework_score(
        self, 
        framework: str, 
        config: Dict[str, Any], 
        criteria: UISelectionCriteria
    ) -> FrameworkScore:
        """Calculate framework compatibility score"""
        base_score = 0.5
        pros = []
        cons = []
        
        # Project type compatibility
        if criteria.project_type.value in config['best_for']:
            base_score += 0.3
            pros.append(f"Optimized for {criteria.project_type.value}")
        
        # Team size fit
        team_category = 'small' if criteria.team_size <= 3 else 'large' if criteria.team_size >= 10 else 'medium'
        team_fit = config['team_size_fit'].get(team_category, 0.5)
        base_score += team_fit * 0.2
        
        if team_fit > 0.8:
            pros.append(f"Excellent fit for {team_category} teams")
        
        # Performance requirements
        if criteria.performance_requirements.get('high_performance', False):
            if config['performance'] == 'excellent':
                base_score += 0.2
                pros.append("Excellent performance")
        
        return FrameworkScore(
            framework=framework,
            score=min(1.0, max(0.0, base_score)),
            reasoning=[],
            pros=pros,
            cons=cons
        )

class UIComponentAnalyzer:
    """Analyze UI component requirements"""
    
    async def analyze_ui_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze UI component needs"""
        components = {
            'forms': self._detect_forms(requirements),
            'data_display': self._detect_data_display(requirements),
            'navigation': self._detect_navigation(requirements)
        }
        
        return {
            'components': components,
            'complexity': self._calculate_ui_complexity(components),
            'recommended_libraries': self._recommend_ui_libraries(components)
        }
    
    def _detect_forms(self, requirements: Dict[str, Any]) -> List[str]:
        """Detect form requirements"""
        forms = []
        text = str(requirements).lower()
        
        if any(word in text for word in ['login', 'register', 'signup']):
            forms.append('authentication_forms')
        if any(word in text for word in ['contact', 'feedback']):
            forms.append('contact_forms')
            
        return forms
    
    def _detect_data_display(self, requirements: Dict[str, Any]) -> List[str]:
        """Detect data display needs"""
        displays = []
        text = str(requirements).lower()
        
        if any(word in text for word in ['table', 'list', 'grid']):
            displays.append('data_tables')
        if any(word in text for word in ['chart', 'graph']):
            displays.append('charts')
            
        return displays
    
    def _detect_navigation(self, requirements: Dict[str, Any]) -> List[str]:
        """Detect navigation requirements"""
        nav = []
        text = str(requirements).lower()
        
        if any(word in text for word in ['menu', 'navbar']):
            nav.append('main_navigation')
        if any(word in text for word in ['sidebar', 'drawer']):
            nav.append('sidebar_navigation')
            
        return nav
    
    def _calculate_ui_complexity(self, components: Dict[str, List[str]]) -> str:
        """Calculate UI complexity level"""
        total_components = sum(len(comp_list) for comp_list in components.values())
        
        if total_components <= 3:
            return 'low'
        elif total_components <= 8:
            return 'medium'
        else:
            return 'high'
    
    def _recommend_ui_libraries(self, components: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Recommend UI component libraries"""
        recommendations = {'react': [], 'vue': []}
        
        if components['forms']:
            recommendations['react'].extend(['react-hook-form'])
            recommendations['vue'].extend(['vee-validate'])
        
        if components['data_display']:
            recommendations['react'].extend(['react-table'])
            recommendations['vue'].extend(['vue-good-table'])
        
        return recommendations