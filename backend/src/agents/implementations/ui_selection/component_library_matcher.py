# backend/src/agents/implementations/ui_selection/component_library_matcher.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class ComponentLibraryMatch:
    library_name: str
    compatibility_score: float
    available_components: List[str]
    missing_components: List[str]
    installation_complexity: str
    bundle_impact: str
    maintenance_status: str

class ComponentLibraryMatcher:
    """컴포넌트 라이브러리 매칭"""
    
    COMPONENT_LIBRARIES = {
        'react': {
            'material-ui': {
                'components': ['Button', 'TextField', 'Select', 'Table', 'Dialog', 'Drawer', 'AppBar', 'Card', 'Chip', 'Avatar'],
                'bundle_size': 'large',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'high'
            },
            'ant-design': {
                'components': ['Button', 'Input', 'Select', 'Table', 'Modal', 'Drawer', 'Menu', 'Card', 'Tag', 'Avatar', 'Form', 'DatePicker'],
                'bundle_size': 'large',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'high'
            },
            'chakra-ui': {
                'components': ['Button', 'Input', 'Select', 'Table', 'Modal', 'Drawer', 'Box', 'Flex', 'Text', 'Heading'],
                'bundle_size': 'medium',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'medium'
            },
            'react-bootstrap': {
                'components': ['Button', 'Form', 'Table', 'Modal', 'Navbar', 'Card', 'Alert', 'Badge'],
                'bundle_size': 'medium',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'medium'
            }
        },
        'vue': {
            'vuetify': {
                'components': ['VBtn', 'VTextField', 'VSelect', 'VDataTable', 'VDialog', 'VNavigationDrawer', 'VAppBar', 'VCard'],
                'bundle_size': 'large',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'high'
            },
            'quasar': {
                'components': ['QBtn', 'QInput', 'QSelect', 'QTable', 'QDialog', 'QDrawer', 'QHeader', 'QCard'],
                'bundle_size': 'medium',
                'installation': 'moderate',
                'maintenance': 'active',
                'popularity': 'medium'
            },
            'element-plus': {
                'components': ['ElButton', 'ElInput', 'ElSelect', 'ElTable', 'ElDialog', 'ElDrawer', 'ElMenu', 'ElCard'],
                'bundle_size': 'medium',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'medium'
            }
        },
        'angular': {
            'angular-material': {
                'components': ['MatButton', 'MatInput', 'MatSelect', 'MatTable', 'MatDialog', 'MatSidenav', 'MatToolbar', 'MatCard'],
                'bundle_size': 'large',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'high'
            },
            'ng-bootstrap': {
                'components': ['NgbButton', 'NgbInput', 'NgbSelect', 'NgbTable', 'NgbModal', 'NgbNavbar', 'NgbCard'],
                'bundle_size': 'medium',
                'installation': 'easy',
                'maintenance': 'active',
                'popularity': 'medium'
            }
        }
    }

    async def find_best_matches(
        self,
        framework: str,
        design_system: str,
        required_components: List[str]
    ) -> List[ComponentLibraryMatch]:
        """최적의 컴포넌트 라이브러리 찾기"""
        
        framework_libraries = self.COMPONENT_LIBRARIES.get(framework, {})
        matches = []
        
        for lib_name, lib_specs in framework_libraries.items():
            match = await self._evaluate_library_match(
                lib_name,
                lib_specs,
                required_components,
                design_system
            )
            matches.append(match)
        
        # 호환성 점수로 정렬
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        return matches

    async def _evaluate_library_match(
        self,
        library_name: str,
        library_specs: Dict[str, Any],
        required_components: List[str],
        design_system: str
    ) -> ComponentLibraryMatch:
        """라이브러리 매칭 평가"""
        
        available_components = library_specs['components']
        
        # 컴포넌트 매칭 계산
        matched_components = []
        missing_components = []
        
        for req_comp in required_components:
            if self._component_exists(req_comp, available_components):
                matched_components.append(req_comp)
            else:
                # 유사 컴포넌트 찾기
                similar = self._find_similar_component(req_comp, available_components)
                if similar:
                    matched_components.append(f"{req_comp} (as {similar})")
                else:
                    missing_components.append(req_comp)
        
        # 호환성 점수 계산
        compatibility_score = len(matched_components) / len(required_components) if required_components else 1.0
        
        # 디자인 시스템과의 호환성 보너스
        if self._is_design_system_compatible(library_name, design_system):
            compatibility_score += 0.1
        
        return ComponentLibraryMatch(
            library_name=library_name,
            compatibility_score=min(compatibility_score, 1.0),
            available_components=matched_components,
            missing_components=missing_components,
            installation_complexity=library_specs['installation'],
            bundle_impact=library_specs['bundle_size'],
            maintenance_status=library_specs['maintenance']
        )

    def _component_exists(self, required: str, available: List[str]) -> bool:
        """컴포넌트 존재 여부 확인"""
        
        # 정확한 매칭
        if required in available:
            return True
        
        # 대소문자 무시 매칭
        required_lower = required.lower()
        for comp in available:
            if comp.lower() == required_lower:
                return True
        
        # 부분 매칭
        for comp in available:
            if required_lower in comp.lower() or comp.lower() in required_lower:
                return True
        
        return False

    def _find_similar_component(self, required: str, available: List[str]) -> Optional[str]:
        """유사한 컴포넌트 찾기"""
        
        # 컴포넌트 매핑 테이블
        component_mappings = {
            'button': ['btn', 'button'],
            'input': ['textfield', 'input', 'field'],
            'select': ['dropdown', 'select', 'picker'],
            'table': ['datatable', 'table', 'grid'],
            'modal': ['dialog', 'modal', 'popup'],
            'drawer': ['sidebar', 'drawer', 'sidenav'],
            'navbar': ['appbar', 'toolbar', 'header', 'navbar'],
            'card': ['card', 'panel'],
            'form': ['form', 'formgroup'],
            'datepicker': ['datepicker', 'calendar']
        }
        
        required_lower = required.lower()
        
        for canonical, variants in component_mappings.items():
            if required_lower in variants:
                # 사용 가능한 컴포넌트에서 매칭되는 것 찾기
                for comp in available:
                    comp_lower = comp.lower()
                    for variant in variants:
                        if variant in comp_lower:
                            return comp
        
        return None

    def _is_design_system_compatible(self, library_name: str, design_system: str) -> bool:
        """디자인 시스템과의 호환성 확인"""
        
        compatibility_map = {
            'material-ui': ['material-ui', 'material-design'],
            'ant-design': ['ant-design'],
            'chakra-ui': ['chakra-ui'],
            'vuetify': ['vuetify', 'material-design'],
            'quasar': ['quasar'],
            'angular-material': ['angular-material', 'material-design']
        }
        
        compatible_systems = compatibility_map.get(library_name, [])
        return design_system in compatible_systems

    async def generate_installation_guide(
        self,
        matches: List[ComponentLibraryMatch],
        framework: str
    ) -> Dict[str, Any]:
        """설치 가이드 생성"""
        
        if not matches:
            return {'error': 'No compatible libraries found'}
        
        best_match = matches[0]
        
        installation_commands = {
            'react': {
                'material-ui': [
                    'npm install @mui/material @emotion/react @emotion/styled',
                    'npm install @mui/icons-material'
                ],
                'ant-design': [
                    'npm install antd',
                    'npm install @ant-design/icons'
                ],
                'chakra-ui': [
                    'npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion'
                ]
            },
            'vue': {
                'vuetify': [
                    'npm install vuetify',
                    'npm install @mdi/font'
                ],
                'quasar': [
                    'npm install quasar @quasar/extras'
                ]
            },
            'angular': {
                'angular-material': [
                    'ng add @angular/material'
                ]
            }
        }
        
        commands = installation_commands.get(framework, {}).get(best_match.library_name, [])
        
        return {
            'recommended_library': best_match.library_name,
            'installation_commands': commands,
            'setup_steps': self._generate_setup_steps(best_match.library_name, framework),
            'import_examples': self._generate_import_examples(best_match.library_name, framework),
            'basic_usage': self._generate_usage_examples(best_match.library_name, framework)
        }

    def _generate_setup_steps(self, library: str, framework: str) -> List[str]:
        """설정 단계 생성"""
        
        setup_steps = {
            'material-ui': [
                'Install the package and dependencies',
                'Wrap your app with ThemeProvider',
                'Import and use components'
            ],
            'ant-design': [
                'Install the package',
                'Import CSS in your main file',
                'Import and use components'
            ],
            'chakra-ui': [
                'Install the package and dependencies',
                'Wrap your app with ChakraProvider',
                'Import and use components'
            ]
        }
        
        return setup_steps.get(library, ['Install the package', 'Configure as needed', 'Import and use components'])

    def _generate_import_examples(self, library: str, framework: str) -> List[str]:
        """임포트 예제 생성"""
        
        import_examples = {
            'material-ui': [
                "import { Button, TextField } from '@mui/material';",
                "import { ThemeProvider, createTheme } from '@mui/material/styles';"
            ],
            'ant-design': [
                "import { Button, Input } from 'antd';",
                "import 'antd/dist/antd.css';"
            ],
            'chakra-ui': [
                "import { Button, Input } from '@chakra-ui/react';",
                "import { ChakraProvider } from '@chakra-ui/react';"
            ]
        }
        
        return import_examples.get(library, [f"import {{ Component }} from '{library}';"])

    def _generate_usage_examples(self, library: str, framework: str) -> List[str]:
        """사용 예제 생성"""
        
        usage_examples = {
            'material-ui': [
                '<Button variant="contained" color="primary">Click me</Button>',
                '<TextField label="Name" variant="outlined" />'
            ],
            'ant-design': [
                '<Button type="primary">Click me</Button>',
                '<Input placeholder="Enter name" />'
            ],
            'chakra-ui': [
                '<Button colorScheme="blue">Click me</Button>',
                '<Input placeholder="Enter name" />'
            ]
        }
        
        return usage_examples.get(library, ['<Component>Example</Component>'])