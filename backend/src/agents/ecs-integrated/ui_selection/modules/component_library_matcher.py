"""
Component Library Matcher Module
컴포넌트 라이브러리 매칭 로직
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ComponentLibraryMatcher:
    """컴포넌트 라이브러리 매처"""
    
    COMPONENT_LIBRARIES = {
        'react': {
            'material-ui': {
                'name': 'Material-UI (MUI)',
                'score': 95,
                'components': 100,
                'design_system': 'Material Design',
                'customization': 'high',
                'bundle_size': 'large',
                'learning_curve': 'medium',
                'best_for': ['enterprise', 'admin', 'dashboard']
            },
            'ant-design': {
                'name': 'Ant Design',
                'score': 93,
                'components': 90,
                'design_system': 'Ant Design',
                'customization': 'high',
                'bundle_size': 'large',
                'learning_curve': 'medium',
                'best_for': ['enterprise', 'admin', 'forms']
            },
            'chakra-ui': {
                'name': 'Chakra UI',
                'score': 90,
                'components': 60,
                'design_system': 'Modular',
                'customization': 'very_high',
                'bundle_size': 'medium',
                'learning_curve': 'low',
                'best_for': ['modern', 'saas', 'startups']
            },
            'tailwind-ui': {
                'name': 'Tailwind UI',
                'score': 88,
                'components': 50,
                'design_system': 'Utility-first',
                'customization': 'very_high',
                'bundle_size': 'small',
                'learning_curve': 'low-medium',
                'best_for': ['custom', 'marketing', 'landing']
            },
            'react-bootstrap': {
                'name': 'React Bootstrap',
                'score': 85,
                'components': 40,
                'design_system': 'Bootstrap',
                'customization': 'medium',
                'bundle_size': 'medium',
                'learning_curve': 'low',
                'best_for': ['rapid', 'prototype', 'standard']
            }
        },
        'vue': {
            'vuetify': {
                'name': 'Vuetify',
                'score': 94,
                'components': 80,
                'design_system': 'Material Design',
                'customization': 'high',
                'bundle_size': 'large',
                'learning_curve': 'medium',
                'best_for': ['enterprise', 'admin', 'dashboard']
            },
            'element-plus': {
                'name': 'Element Plus',
                'score': 92,
                'components': 70,
                'design_system': 'Element',
                'customization': 'high',
                'bundle_size': 'medium',
                'learning_curve': 'low-medium',
                'best_for': ['enterprise', 'admin', 'forms']
            },
            'quasar': {
                'name': 'Quasar',
                'score': 90,
                'components': 90,
                'design_system': 'Material Design',
                'customization': 'high',
                'bundle_size': 'large',
                'learning_curve': 'medium-high',
                'best_for': ['cross-platform', 'mobile', 'desktop']
            },
            'naive-ui': {
                'name': 'Naive UI',
                'score': 87,
                'components': 60,
                'design_system': 'Modern',
                'customization': 'high',
                'bundle_size': 'small',
                'learning_curve': 'low',
                'best_for': ['modern', 'clean', 'minimal']
            }
        },
        'angular': {
            'angular-material': {
                'name': 'Angular Material',
                'score': 95,
                'components': 70,
                'design_system': 'Material Design',
                'customization': 'medium',
                'bundle_size': 'large',
                'learning_curve': 'medium',
                'best_for': ['enterprise', 'google-style', 'standard']
            },
            'ng-bootstrap': {
                'name': 'NG Bootstrap',
                'score': 88,
                'components': 40,
                'design_system': 'Bootstrap',
                'customization': 'medium',
                'bundle_size': 'medium',
                'learning_curve': 'low',
                'best_for': ['rapid', 'prototype', 'standard']
            },
            'primeng': {
                'name': 'PrimeNG',
                'score': 91,
                'components': 90,
                'design_system': 'PrimeNG',
                'customization': 'high',
                'bundle_size': 'large',
                'learning_curve': 'medium',
                'best_for': ['enterprise', 'data-heavy', 'forms']
            }
        }
    }
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """모듈 초기화"""
        self.initialized = True
        logger.info("ComponentLibraryMatcher initialized")
        return True
    
    async def match(
        self,
        framework: Dict[str, Any],
        requirements: Dict[str, Any],
        design_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        프레임워크에 맞는 컴포넌트 라이브러리 매칭
        
        Args:
            framework: 선택된 프레임워크 정보
            requirements: 프로젝트 요구사항
            design_preferences: 디자인 선호도
            
        Returns:
            매칭된 컴포넌트 라이브러리 정보
        """
        
        framework_name = framework.get('name', 'react').lower()
        
        # 프레임워크별 라이브러리 후보
        candidates = self.COMPONENT_LIBRARIES.get(framework_name, {})
        
        if not candidates:
            return self._create_default_result()
        
        # 점수 계산
        scores = {}
        for lib_name, lib_data in candidates.items():
            score = await self._calculate_library_score(
                lib_name,
                lib_data,
                requirements,
                design_preferences
            )
            scores[lib_name] = score
        
        # 최고 점수 라이브러리 선택
        best_library = max(scores, key=scores.get)
        best_data = candidates[best_library]
        
        return self._create_library_result(best_library, best_data, scores[best_library])
    
    async def _calculate_library_score(
        self,
        lib_name: str,
        lib_data: Dict[str, Any],
        requirements: Dict[str, Any],
        design_preferences: Dict[str, Any]
    ) -> float:
        """라이브러리 점수 계산"""
        
        base_score = lib_data['score']
        adjustments = 0
        
        # 프로젝트 타입 매칭
        project_type = requirements.get('project_type', '')
        if project_type in lib_data['best_for']:
            adjustments += 15
        
        # 디자인 시스템 선호도
        preferred_design = design_preferences.get('design_system', '')
        if preferred_design and preferred_design.lower() in lib_data['design_system'].lower():
            adjustments += 20
        
        # 커스터마이징 요구도
        if requirements.get('high_customization', False):
            if lib_data['customization'] in ['very_high', 'high']:
                adjustments += 10
            else:
                adjustments -= 10
        
        # 번들 크기 고려
        if requirements.get('performance_critical', False):
            if lib_data['bundle_size'] == 'small':
                adjustments += 15
            elif lib_data['bundle_size'] == 'large':
                adjustments -= 15
        
        # 학습 곡선 고려
        team_experience = requirements.get('team_experience', 'medium')
        if team_experience == 'beginner':
            if lib_data['learning_curve'] == 'low':
                adjustments += 10
            elif lib_data['learning_curve'] in ['medium-high', 'high']:
                adjustments -= 10
        
        # 컴포넌트 수 고려
        if requirements.get('complex_ui', False):
            adjustments += (lib_data['components'] - 50) * 0.2
        
        return base_score + adjustments
    
    def _create_library_result(
        self,
        lib_key: str,
        lib_data: Dict[str, Any],
        final_score: float
    ) -> Dict[str, Any]:
        """라이브러리 결과 생성"""
        
        return {
            'key': lib_key,
            'name': lib_data['name'],
            'score': final_score,
            'components_count': lib_data['components'],
            'design_system': lib_data['design_system'],
            'customization_level': lib_data['customization'],
            'bundle_size': lib_data['bundle_size'],
            'learning_curve': lib_data['learning_curve'],
            'best_for': lib_data['best_for'],
            'installation': self._get_installation_command(lib_key),
            'imports': self._get_import_examples(lib_key),
            'theme_setup': self._get_theme_setup(lib_key),
            'additional_deps': self._get_additional_deps(lib_key)
        }
    
    def _get_installation_command(self, lib_key: str) -> str:
        """설치 명령어 반환"""
        commands = {
            'material-ui': 'npm install @mui/material @emotion/react @emotion/styled',
            'ant-design': 'npm install antd',
            'chakra-ui': 'npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion',
            'tailwind-ui': 'npm install tailwindcss @headlessui/react @heroicons/react',
            'react-bootstrap': 'npm install react-bootstrap bootstrap',
            'vuetify': 'npm install vuetify',
            'element-plus': 'npm install element-plus',
            'quasar': 'npm install quasar',
            'naive-ui': 'npm install naive-ui',
            'angular-material': 'ng add @angular/material',
            'ng-bootstrap': 'npm install @ng-bootstrap/ng-bootstrap',
            'primeng': 'npm install primeng primeicons'
        }
        return commands.get(lib_key, 'npm install')
    
    def _get_import_examples(self, lib_key: str) -> List[str]:
        """임포트 예제 반환"""
        examples = {
            'material-ui': [
                "import { Button, TextField } from '@mui/material';",
                "import { ThemeProvider, createTheme } from '@mui/material/styles';"
            ],
            'ant-design': [
                "import { Button, Input, Card } from 'antd';",
                "import 'antd/dist/reset.css';"
            ],
            'chakra-ui': [
                "import { Button, Input, Box } from '@chakra-ui/react';",
                "import { ChakraProvider } from '@chakra-ui/react';"
            ],
            'tailwind-ui': [
                "import { Dialog, Transition } from '@headlessui/react';",
                "import { XMarkIcon } from '@heroicons/react/24/outline';"
            ]
        }
        return examples.get(lib_key, [])
    
    def _get_theme_setup(self, lib_key: str) -> Dict[str, Any]:
        """테마 설정 반환"""
        setups = {
            'material-ui': {
                'provider': 'ThemeProvider',
                'create_theme': 'createTheme',
                'customizable': True,
                'dark_mode': True
            },
            'ant-design': {
                'provider': 'ConfigProvider',
                'create_theme': 'theme',
                'customizable': True,
                'dark_mode': True
            },
            'chakra-ui': {
                'provider': 'ChakraProvider',
                'create_theme': 'extendTheme',
                'customizable': True,
                'dark_mode': True
            }
        }
        return setups.get(lib_key, {})
    
    def _get_additional_deps(self, lib_key: str) -> List[str]:
        """추가 의존성 반환"""
        deps = {
            'material-ui': ['@mui/icons-material', '@mui/lab'],
            'ant-design': ['@ant-design/icons', '@ant-design/pro-components'],
            'chakra-ui': ['@chakra-ui/icons'],
            'tailwind-ui': ['@tailwindcss/forms', '@tailwindcss/typography']
        }
        return deps.get(lib_key, [])
    
    def _create_default_result(self) -> Dict[str, Any]:
        """기본 결과 생성"""
        return {
            'key': 'custom',
            'name': 'Custom Components',
            'score': 70,
            'components_count': 0,
            'design_system': 'Custom',
            'customization_level': 'full',
            'bundle_size': 'minimal',
            'learning_curve': 'varies',
            'best_for': ['unique', 'custom', 'minimal'],
            'installation': '',
            'imports': [],
            'theme_setup': {},
            'additional_deps': []
        }