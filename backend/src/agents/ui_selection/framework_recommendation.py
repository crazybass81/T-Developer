"""
UI Selection Agent - Framework Recommendation System
SubTasks 4.22.2-4.22.4 Implementation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class FrameworkRecommendation:
    framework: str
    confidence: float
    reasons: List[str]
    alternatives: List[str]
    implementation_guide: Dict[str, Any]

class FrameworkRecommendationEngine:
    """Framework recommendation engine with ML-based scoring"""
    
    def __init__(self):
        self.recommendation_rules = self._load_recommendation_rules()
        self.framework_profiles = self._load_framework_profiles()
        
    def _load_recommendation_rules(self) -> List[Dict[str, Any]]:
        """Load recommendation rules"""
        return [
            {
                'condition': 'static_site',
                'frameworks': ['nextjs', 'gatsby'],
                'weight': 0.9,
                'reason': 'Static site generation optimized'
            },
            {
                'condition': 'small_team',
                'frameworks': ['vue', 'svelte'],
                'weight': 0.8,
                'reason': 'Easy learning curve for small teams'
            },
            {
                'condition': 'enterprise',
                'frameworks': ['angular', 'react'],
                'weight': 0.7,
                'reason': 'Enterprise-grade features'
            }
        ]
    
    def _load_framework_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load framework profiles"""
        return {
            'react': {
                'strengths': ['large_ecosystem', 'job_market', 'flexibility'],
                'weaknesses': ['learning_curve', 'decision_fatigue'],
                'best_use_cases': ['spa', 'complex_ui', 'mobile_app'],
                'team_size': {'min': 2, 'optimal': 5, 'max': 20}
            },
            'vue': {
                'strengths': ['easy_learning', 'documentation', 'progressive'],
                'weaknesses': ['smaller_ecosystem', 'enterprise_adoption'],
                'best_use_cases': ['spa', 'progressive_enhancement'],
                'team_size': {'min': 1, 'optimal': 3, 'max': 10}
            },
            'nextjs': {
                'strengths': ['seo', 'performance', 'full_stack'],
                'weaknesses': ['vendor_lock_in', 'complexity'],
                'best_use_cases': ['static_site', 'seo_critical', 'full_stack'],
                'team_size': {'min': 2, 'optimal': 4, 'max': 15}
            }
        }
    
    async def recommend_framework(
        self, 
        project_requirements: Dict[str, Any],
        team_context: Dict[str, Any]
    ) -> FrameworkRecommendation:
        """Generate framework recommendation"""
        
        # Calculate scores for each framework
        framework_scores = {}
        for framework in self.framework_profiles.keys():
            score = await self._calculate_framework_fit(
                framework, 
                project_requirements, 
                team_context
            )
            framework_scores[framework] = score
        
        # Get top recommendation
        best_framework = max(framework_scores, key=framework_scores.get)
        confidence = framework_scores[best_framework]
        
        # Generate reasons
        reasons = await self._generate_reasons(
            best_framework, 
            project_requirements, 
            team_context
        )
        
        # Get alternatives
        alternatives = self._get_alternatives(framework_scores, best_framework)
        
        # Generate implementation guide
        implementation_guide = await self._generate_implementation_guide(
            best_framework, 
            project_requirements
        )
        
        return FrameworkRecommendation(
            framework=best_framework,
            confidence=confidence,
            reasons=reasons,
            alternatives=alternatives,
            implementation_guide=implementation_guide
        )
    
    async def _calculate_framework_fit(
        self,
        framework: str,
        project_requirements: Dict[str, Any],
        team_context: Dict[str, Any]
    ) -> float:
        """Calculate framework fit score"""
        
        profile = self.framework_profiles[framework]
        score = 0.5  # Base score
        
        # Team size fit
        team_size = team_context.get('size', 3)
        optimal_size = profile['team_size']['optimal']
        size_diff = abs(team_size - optimal_size) / optimal_size
        score += (1 - size_diff) * 0.2
        
        # Use case alignment
        project_type = project_requirements.get('type', 'spa')
        if project_type in profile['best_use_cases']:
            score += 0.3
        
        # Apply recommendation rules
        for rule in self.recommendation_rules:
            if self._rule_matches(rule, project_requirements, team_context):
                if framework in rule['frameworks']:
                    score += rule['weight'] * 0.1
        
        return min(1.0, score)
    
    def _rule_matches(
        self, 
        rule: Dict[str, Any], 
        project_requirements: Dict[str, Any], 
        team_context: Dict[str, Any]
    ) -> bool:
        """Check if rule matches current context"""
        
        condition = rule['condition']
        
        if condition == 'static_site':
            return project_requirements.get('type') == 'static_site'
        elif condition == 'small_team':
            return team_context.get('size', 3) <= 3
        elif condition == 'enterprise':
            return project_requirements.get('scale') == 'enterprise'
        
        return False
    
    async def _generate_reasons(
        self,
        framework: str,
        project_requirements: Dict[str, Any],
        team_context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendation reasons"""
        
        reasons = []
        profile = self.framework_profiles[framework]
        
        # Team size reasoning
        team_size = team_context.get('size', 3)
        if profile['team_size']['min'] <= team_size <= profile['team_size']['max']:
            reasons.append(f"Good fit for team size of {team_size}")
        
        # Use case reasoning
        project_type = project_requirements.get('type', 'spa')
        if project_type in profile['best_use_cases']:
            reasons.append(f"Optimized for {project_type} applications")
        
        # Strength-based reasoning
        for strength in profile['strengths'][:2]:  # Top 2 strengths
            reasons.append(f"Strong {strength.replace('_', ' ')}")
        
        return reasons
    
    def _get_alternatives(
        self, 
        framework_scores: Dict[str, float], 
        best_framework: str
    ) -> List[str]:
        """Get alternative framework recommendations"""
        
        sorted_frameworks = sorted(
            framework_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top 2 alternatives (excluding the best)
        alternatives = []
        for framework, score in sorted_frameworks:
            if framework != best_framework and len(alternatives) < 2:
                alternatives.append(framework)
        
        return alternatives
    
    async def _generate_implementation_guide(
        self,
        framework: str,
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation guide"""
        
        guides = {
            'react': {
                'setup_commands': [
                    'npx create-react-app my-app',
                    'cd my-app',
                    'npm start'
                ],
                'recommended_packages': [
                    'react-router-dom',
                    'axios',
                    'styled-components'
                ],
                'folder_structure': {
                    'src/components': 'Reusable components',
                    'src/pages': 'Page components',
                    'src/hooks': 'Custom hooks',
                    'src/utils': 'Utility functions'
                }
            },
            'vue': {
                'setup_commands': [
                    'npm create vue@latest my-app',
                    'cd my-app',
                    'npm install',
                    'npm run dev'
                ],
                'recommended_packages': [
                    'vue-router',
                    'pinia',
                    'axios'
                ],
                'folder_structure': {
                    'src/components': 'Vue components',
                    'src/views': 'Page views',
                    'src/stores': 'Pinia stores',
                    'src/composables': 'Composition functions'
                }
            },
            'nextjs': {
                'setup_commands': [
                    'npx create-next-app@latest my-app',
                    'cd my-app',
                    'npm run dev'
                ],
                'recommended_packages': [
                    'next-auth',
                    'prisma',
                    'tailwindcss'
                ],
                'folder_structure': {
                    'pages': 'Page routes',
                    'components': 'Reusable components',
                    'lib': 'Utility libraries',
                    'public': 'Static assets'
                }
            }
        }
        
        return guides.get(framework, {})

class PerformanceAnalyzer:
    """Analyze performance requirements for framework selection"""
    
    async def analyze_performance_needs(
        self, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance requirements"""
        
        performance_profile = {
            'load_time_target': self._extract_load_time(requirements),
            'user_count': self._extract_user_count(requirements),
            'data_volume': self._extract_data_volume(requirements),
            'real_time_needs': self._detect_real_time_needs(requirements)
        }
        
        framework_recommendations = self._recommend_for_performance(performance_profile)
        
        return {
            'performance_profile': performance_profile,
            'framework_recommendations': framework_recommendations,
            'optimization_strategies': self._suggest_optimizations(performance_profile)
        }
    
    def _extract_load_time(self, requirements: Dict[str, Any]) -> str:
        """Extract load time requirements"""
        text = str(requirements).lower()
        
        if any(word in text for word in ['fast', 'quick', 'instant']):
            return 'under_2s'
        elif any(word in text for word in ['slow', 'acceptable']):
            return 'under_5s'
        else:
            return 'under_3s'
    
    def _extract_user_count(self, requirements: Dict[str, Any]) -> str:
        """Extract expected user count"""
        text = str(requirements).lower()
        
        if any(word in text for word in ['million', '1000000']):
            return 'high_scale'
        elif any(word in text for word in ['thousand', '1000']):
            return 'medium_scale'
        else:
            return 'low_scale'
    
    def _extract_data_volume(self, requirements: Dict[str, Any]) -> str:
        """Extract data volume requirements"""
        text = str(requirements).lower()
        
        if any(word in text for word in ['big data', 'large dataset']):
            return 'high_volume'
        elif any(word in text for word in ['analytics', 'reporting']):
            return 'medium_volume'
        else:
            return 'low_volume'
    
    def _detect_real_time_needs(self, requirements: Dict[str, Any]) -> bool:
        """Detect real-time requirements"""
        text = str(requirements).lower()
        return any(word in text for word in ['real-time', 'live', 'instant'])
    
    def _recommend_for_performance(self, profile: Dict[str, Any]) -> List[str]:
        """Recommend frameworks based on performance needs"""
        recommendations = []
        
        if profile['load_time_target'] == 'under_2s':
            recommendations.extend(['nextjs', 'svelte'])
        
        if profile['user_count'] == 'high_scale':
            recommendations.extend(['react', 'vue'])
        
        if profile['real_time_needs']:
            recommendations.extend(['react', 'vue'])
        
        return list(set(recommendations))
    
    def _suggest_optimizations(self, profile: Dict[str, Any]) -> List[str]:
        """Suggest optimization strategies"""
        optimizations = []
        
        if profile['load_time_target'] in ['under_2s', 'under_3s']:
            optimizations.extend([
                'Code splitting',
                'Lazy loading',
                'Image optimization'
            ])
        
        if profile['user_count'] == 'high_scale':
            optimizations.extend([
                'CDN usage',
                'Caching strategies',
                'Server-side rendering'
            ])
        
        return optimizations