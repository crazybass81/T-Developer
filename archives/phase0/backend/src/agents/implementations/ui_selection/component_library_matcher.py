# backend/src/agents/implementations/ui_selection/component_library_matcher.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ComponentLibrary:
    name: str
    framework: str
    components: List[str]
    score: float
    bundle_size: str
    typescript_support: bool
    accessibility_score: float
    maintenance_status: str

class ComponentLibraryMatcher:
    """컴포넌트 라이브러리 매칭 시스템"""
    
    COMPONENT_LIBRARIES = {
        'react': {
            'react-bootstrap': {
                'components': ['Button', 'Modal', 'Form', 'Table', 'Card', 'Navbar'],
                'bundle_size': 'medium',
                'typescript': True,
                'accessibility': 0.8,
                'maintenance': 'active',
                'use_cases': ['bootstrap_design', 'rapid_prototyping']
            },
            'semantic-ui-react': {
                'components': ['Button', 'Menu', 'Form', 'Grid', 'Card', 'Modal'],
                'bundle_size': 'large',
                'typescript': True,
                'accessibility': 0.7,
                'maintenance': 'maintenance',
                'use_cases': ['semantic_design', 'content_heavy']
            },
            'react-select': {
                'components': ['Select', 'AsyncSelect', 'CreatableSelect'],
                'bundle_size': 'small',
                'typescript': True,
                'accessibility': 0.9,
                'maintenance': 'active',
                'use_cases': ['forms', 'data_selection']
            }
        },
        'vue': {
            'element-plus': {
                'components': ['Button', 'Form', 'Table', 'Dialog', 'Menu', 'DatePicker'],
                'bundle_size': 'large',
                'typescript': True,
                'accessibility': 0.8,
                'maintenance': 'active',
                'use_cases': ['admin_panels', 'enterprise']
            },
            'quasar': {
                'components': ['QBtn', 'QForm', 'QTable', 'QDialog', 'QMenu'],
                'bundle_size': 'large',
                'typescript': True,
                'accessibility': 0.85,
                'maintenance': 'active',
                'use_cases': ['spa', 'mobile', 'desktop']
            }
        },
        'angular': {
            'ng-bootstrap': {
                'components': ['NgbModal', 'NgbDropdown', 'NgbDatepicker'],
                'bundle_size': 'medium',
                'typescript': True,
                'accessibility': 0.9,
                'maintenance': 'active',
                'use_cases': ['bootstrap_integration']
            },
            'primeng': {
                'components': ['Button', 'DataTable', 'Calendar', 'Dialog'],
                'bundle_size': 'large',
                'typescript': True,
                'accessibility': 0.8,
                'maintenance': 'active',
                'use_cases': ['enterprise', 'data_heavy']
            }
        }
    }

    async def match_libraries(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> List[ComponentLibrary]:
        """컴포넌트 라이브러리 매칭"""
        
        framework_libraries = self.COMPONENT_LIBRARIES.get(framework, {})
        if not framework_libraries:
            return []
        
        matched_libraries = []
        required_components = requirements.get('required_components', [])
        
        for lib_name, lib_specs in framework_libraries.items():
            # 컴포넌트 매칭 점수 계산
            match_score = self._calculate_match_score(
                lib_specs, requirements, required_components
            )
            
            if match_score > 0.3:  # 최소 매칭 임계값
                library = ComponentLibrary(
                    name=lib_name,
                    framework=framework,
                    components=lib_specs['components'],
                    score=match_score,
                    bundle_size=lib_specs['bundle_size'],
                    typescript_support=lib_specs['typescript'],
                    accessibility_score=lib_specs['accessibility'],
                    maintenance_status=lib_specs['maintenance']
                )
                matched_libraries.append(library)
        
        # 점수 기준 정렬
        matched_libraries.sort(key=lambda x: x.score, reverse=True)
        return matched_libraries[:5]  # 상위 5개만 반환

    def _calculate_match_score(
        self,
        lib_specs: Dict[str, Any],
        requirements: Dict[str, Any],
        required_components: List[str]
    ) -> float:
        """매칭 점수 계산"""
        
        score = 0.0
        
        # 필수 컴포넌트 매칭
        if required_components:
            matched_components = set(lib_specs['components']) & set(required_components)
            component_match_ratio = len(matched_components) / len(required_components)
            score += component_match_ratio * 0.4
        else:
            score += 0.4  # 필수 컴포넌트가 없으면 기본 점수
        
        # TypeScript 지원
        if requirements.get('typescript_required', False):
            if lib_specs['typescript']:
                score += 0.2
        else:
            score += 0.1
        
        # 접근성 요구사항
        if requirements.get('accessibility_important', False):
            score += lib_specs['accessibility'] * 0.2
        
        # 번들 크기 고려
        performance_critical = requirements.get('performance_critical', False)
        if performance_critical:
            bundle_scores = {'small': 0.2, 'medium': 0.1, 'large': 0.0}
            score += bundle_scores.get(lib_specs['bundle_size'], 0)
        else:
            score += 0.1
        
        # 유지보수 상태
        maintenance_scores = {'active': 0.1, 'maintenance': 0.05, 'deprecated': 0.0}
        score += maintenance_scores.get(lib_specs['maintenance'], 0)
        
        return min(1.0, score)

    async def get_component_recommendations(
        self,
        framework: str,
        component_type: str
    ) -> List[Dict[str, Any]]:
        """특정 컴포넌트 타입에 대한 추천"""
        
        recommendations = []
        framework_libraries = self.COMPONENT_LIBRARIES.get(framework, {})
        
        for lib_name, lib_specs in framework_libraries.items():
            if component_type in lib_specs['components']:
                recommendations.append({
                    'library': lib_name,
                    'component': component_type,
                    'accessibility_score': lib_specs['accessibility'],
                    'bundle_size': lib_specs['bundle_size'],
                    'typescript_support': lib_specs['typescript']
                })
        
        return recommendations