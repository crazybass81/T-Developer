# backend/src/agents/implementations/parser_ui_component_identifier.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class UIComponent:
    name: str
    type: str
    description: str
    properties: Dict[str, Any]
    children: List[str]
    interactions: List[str]
    data_bindings: List[str]

@dataclass
class UIScreen:
    name: str
    description: str
    components: List[UIComponent]
    navigation: List[str]
    layout_type: str

@dataclass
class UISpecification:
    screens: List[UIScreen]
    components: List[UIComponent]
    navigation_flow: Dict[str, List[str]]
    design_system: Dict[str, Any]

class UIComponentIdentifier:
    """UI 컴포넌트 식별기"""

    def __init__(self):
        self.component_patterns = {
            'form': [
                r'\b(form|input|field|textbox|textarea|dropdown|select|checkbox|radio|button)\b',
                r'\b(login|register|signup|contact|search)\s+(form|page|screen)\b',
                r'\b(submit|save|create|update|delete)\s+(button|form)\b'
            ],
            'navigation': [
                r'\b(menu|navbar|navigation|sidebar|breadcrumb|tab|link)\b',
                r'\b(navigate|route|redirect|go\s+to)\b',
                r'\b(header|footer|navigation\s+bar)\b'
            ],
            'display': [
                r'\b(table|list|grid|card|panel|dashboard|chart|graph)\b',
                r'\b(display|show|present|render|view)\b',
                r'\b(report|summary|overview|details)\b'
            ],
            'interaction': [
                r'\b(modal|dialog|popup|tooltip|alert|notification)\b',
                r'\b(click|hover|select|drag|drop|scroll)\b',
                r'\b(expand|collapse|toggle|switch)\b'
            ],
            'media': [
                r'\b(image|photo|video|audio|file|upload|download)\b',
                r'\b(gallery|carousel|slider|preview)\b'
            ]
        }
        
        self.screen_patterns = [
            r'\b(page|screen|view|interface)\s*:\s*([^.]+)',
            r'\b(login|register|dashboard|profile|settings|admin)\s+(page|screen|view)\b',
            r'\b(home|main|landing)\s+(page|screen)\b'
        ]

    async def identify_ui_components(
        self,
        requirements: List[Dict[str, Any]]
    ) -> UISpecification:
        """UI 컴포넌트 식별"""
        
        screens = []
        components = []
        navigation_flow = {}
        
        for req in requirements:
            description = req.get('description', '')
            
            # 화면 식별
            req_screens = self._identify_screens(description)
            screens.extend(req_screens)
            
            # 컴포넌트 식별
            req_components = self._identify_components(description)
            components.extend(req_components)
            
            # 네비게이션 플로우 추출
            nav_flow = self._extract_navigation_flow(description)
            navigation_flow.update(nav_flow)
            
        # 중복 제거
        unique_screens = self._deduplicate_screens(screens)
        unique_components = self._deduplicate_components(components)
        
        # 디자인 시스템 추론
        design_system = self._infer_design_system(requirements)
        
        return UISpecification(
            screens=unique_screens,
            components=unique_components,
            navigation_flow=navigation_flow,
            design_system=design_system
        )

    def _identify_screens(self, text: str) -> List[UIScreen]:
        """화면 식별"""
        screens = []
        
        for pattern in self.screen_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    screen_name = groups[1] if groups[0] in ['page', 'screen', 'view'] else groups[0]
                    screen_type = groups[0] if groups[0] in ['page', 'screen', 'view'] else 'page'
                else:
                    screen_name = groups[0]
                    screen_type = 'page'
                
                # 화면 컴포넌트 추출
                screen_components = self._extract_screen_components(text, screen_name)
                
                # 네비게이션 추출
                navigation = self._extract_screen_navigation(text, screen_name)
                
                # 레이아웃 타입 추론
                layout_type = self._infer_layout_type(text, screen_components)
                
                screen = UIScreen(
                    name=screen_name.strip(),
                    description=f"{screen_name} {screen_type}",
                    components=screen_components,
                    navigation=navigation,
                    layout_type=layout_type
                )
                screens.append(screen)
                
        return screens

    def _identify_components(self, text: str) -> List[UIComponent]:
        """컴포넌트 식별"""
        components = []
        
        for component_type, patterns in self.component_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    component_name = match.group(1) if match.groups() else match.group(0)
                    
                    # 컴포넌트 속성 추출
                    properties = self._extract_component_properties(text, component_name, component_type)
                    
                    # 상호작용 추출
                    interactions = self._extract_component_interactions(text, component_name)
                    
                    # 데이터 바인딩 추출
                    data_bindings = self._extract_data_bindings(text, component_name)
                    
                    # 자식 컴포넌트 추출
                    children = self._extract_child_components(text, component_name)
                    
                    component = UIComponent(
                        name=component_name,
                        type=component_type,
                        description=f"{component_name} {component_type} component",
                        properties=properties,
                        children=children,
                        interactions=interactions,
                        data_bindings=data_bindings
                    )
                    components.append(component)
                    
        return components

    def _extract_screen_components(self, text: str, screen_name: str) -> List[UIComponent]:
        """화면별 컴포넌트 추출"""
        components = []
        
        # 화면 관련 텍스트 추출
        screen_context = self._extract_screen_context(text, screen_name)
        
        # 컴포넌트 식별
        screen_components = self._identify_components(screen_context)
        
        return screen_components

    def _extract_screen_context(self, text: str, screen_name: str) -> str:
        """화면 관련 컨텍스트 추출"""
        # 화면명 주변 텍스트 추출
        pattern = rf'.*{re.escape(screen_name)}.*?(?=\n\n|\.|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        return match.group(0) if match else text

    def _extract_component_properties(
        self,
        text: str,
        component_name: str,
        component_type: str
    ) -> Dict[str, Any]:
        """컴포넌트 속성 추출"""
        properties = {}
        
        # 타입별 기본 속성
        default_properties = {
            'form': {'method': 'POST', 'validation': True},
            'navigation': {'orientation': 'horizontal'},
            'display': {'sortable': False, 'filterable': False},
            'interaction': {'modal': False, 'closable': True},
            'media': {'responsive': True}
        }
        
        properties.update(default_properties.get(component_type, {}))
        
        # 텍스트에서 속성 추출
        property_patterns = {
            'required': r'\b(required|mandatory|must)\b',
            'optional': r'\b(optional|may|can)\b',
            'readonly': r'\b(readonly|read-only|view-only)\b',
            'disabled': r'\b(disabled|inactive)\b',
            'hidden': r'\b(hidden|invisible)\b',
            'responsive': r'\b(responsive|mobile|tablet|desktop)\b',
            'validation': r'\b(validate|validation|check|verify)\b'
        }
        
        for prop, pattern in property_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                properties[prop] = True
                
        # 크기 속성
        size_match = re.search(r'(small|medium|large|xl|xs)', text, re.IGNORECASE)
        if size_match:
            properties['size'] = size_match.group(1).lower()
            
        # 색상 속성
        color_match = re.search(r'(primary|secondary|success|warning|danger|info)', text, re.IGNORECASE)
        if color_match:
            properties['variant'] = color_match.group(1).lower()
            
        return properties

    def _extract_component_interactions(self, text: str, component_name: str) -> List[str]:
        """컴포넌트 상호작용 추출"""
        interactions = []
        
        interaction_patterns = [
            r'(click|tap|press|select|choose)',
            r'(hover|mouseover|focus|blur)',
            r'(drag|drop|swipe|scroll)',
            r'(submit|save|cancel|close|open)',
            r'(expand|collapse|toggle|switch)'
        ]
        
        for pattern in interaction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                interactions.append(pattern.strip('()'))
                
        return interactions

    def _extract_data_bindings(self, text: str, component_name: str) -> List[str]:
        """데이터 바인딩 추출"""
        bindings = []
        
        # 데이터 소스 패턴
        data_patterns = [
            r'(display|show|present)\s+(\w+)',
            r'(bind|connect|link)\s+to\s+(\w+)',
            r'(from|source)\s+(\w+)',
            r'(\w+)\s+(data|information|content)'
        ]
        
        for pattern in data_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    data_source = match[1] if len(match) > 1 else match[0]
                    if data_source.lower() not in ['the', 'a', 'an', 'this', 'that']:
                        bindings.append(data_source)
                        
        return list(set(bindings))

    def _extract_child_components(self, text: str, component_name: str) -> List[str]:
        """자식 컴포넌트 추출"""
        children = []
        
        # 포함 관계 패턴
        containment_patterns = [
            rf'{re.escape(component_name)}\s+(contains|includes|has)\s+([^.]+)',
            rf'(inside|within)\s+{re.escape(component_name)}.*?(\w+)',
            rf'{re.escape(component_name)}\s+with\s+([^.]+)'
        ]
        
        for pattern in containment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    child_text = match[1] if len(match) > 1 else match[0]
                    # 자식 컴포넌트명 추출
                    child_components = re.findall(r'\b(\w+)\b', child_text)
                    children.extend(child_components)
                    
        return list(set(children))

    def _extract_navigation_flow(self, text: str) -> Dict[str, List[str]]:
        """네비게이션 플로우 추출"""
        navigation_flow = {}
        
        # 네비게이션 패턴
        nav_patterns = [
            r'(navigate|go|redirect|route)\s+to\s+(\w+)',
            r'from\s+(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+(leads to|goes to|navigates to)\s+(\w+)',
            r'click\s+(\w+).*?(open|show|display)\s+(\w+)'
        ]
        
        for pattern in nav_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    source = match[0] if len(match) == 2 else match[0]
                    target = match[1] if len(match) == 2 else match[2]
                    
                    if source not in navigation_flow:
                        navigation_flow[source] = []
                    navigation_flow[source].append(target)
                    
        return navigation_flow

    def _extract_screen_navigation(self, text: str, screen_name: str) -> List[str]:
        """화면별 네비게이션 추출"""
        navigation = []
        
        # 화면에서 갈 수 있는 곳들
        nav_patterns = [
            rf'from\s+{re.escape(screen_name)}.*?(navigate|go|redirect)\s+to\s+(\w+)',
            rf'{re.escape(screen_name)}.*?(link|button|menu).*?(\w+)',
            rf'in\s+{re.escape(screen_name)}.*?(click|select).*?(\w+)'
        ]
        
        for pattern in nav_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    target = match[1] if len(match) > 1 else match[0]
                    navigation.append(target)
                    
        return list(set(navigation))

    def _infer_layout_type(self, text: str, components: List[UIComponent]) -> str:
        """레이아웃 타입 추론"""
        text_lower = text.lower()
        
        # 레이아웃 키워드 확인
        if 'grid' in text_lower or 'table' in text_lower:
            return 'grid'
        elif 'list' in text_lower or 'vertical' in text_lower:
            return 'list'
        elif 'card' in text_lower or 'tile' in text_lower:
            return 'card'
        elif 'dashboard' in text_lower:
            return 'dashboard'
        elif 'form' in text_lower:
            return 'form'
        else:
            return 'default'

    def _infer_design_system(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """디자인 시스템 추론"""
        design_system = {
            'framework': 'custom',
            'theme': 'default',
            'responsive': True,
            'accessibility': False,
            'components': []
        }
        
        # 프레임워크 감지
        framework_keywords = {
            'bootstrap': ['bootstrap', 'bs'],
            'material': ['material', 'mui', 'material-ui'],
            'antd': ['antd', 'ant design'],
            'chakra': ['chakra', 'chakra-ui'],
            'tailwind': ['tailwind', 'tailwindcss']
        }
        
        all_text = ' '.join([req.get('description', '') for req in requirements]).lower()
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                design_system['framework'] = framework
                break
                
        # 접근성 요구사항 확인
        if any(keyword in all_text for keyword in ['accessibility', 'a11y', 'wcag', 'screen reader']):
            design_system['accessibility'] = True
            
        # 테마 감지
        if any(keyword in all_text for keyword in ['dark', 'night', 'dark mode']):
            design_system['theme'] = 'dark'
        elif any(keyword in all_text for keyword in ['light', 'bright', 'light mode']):
            design_system['theme'] = 'light'
            
        return design_system

    def _deduplicate_screens(self, screens: List[UIScreen]) -> List[UIScreen]:
        """중복 화면 제거"""
        unique_screens = {}
        
        for screen in screens:
            if screen.name not in unique_screens:
                unique_screens[screen.name] = screen
            else:
                # 컴포넌트 병합
                existing = unique_screens[screen.name]
                existing.components.extend(screen.components)
                existing.navigation.extend(screen.navigation)
                
        return list(unique_screens.values())

    def _deduplicate_components(self, components: List[UIComponent]) -> List[UIComponent]:
        """중복 컴포넌트 제거"""
        unique_components = {}
        
        for component in components:
            key = f"{component.name}_{component.type}"
            if key not in unique_components:
                unique_components[key] = component
            else:
                # 속성 병합
                existing = unique_components[key]
                existing.properties.update(component.properties)
                existing.interactions.extend(component.interactions)
                existing.data_bindings.extend(component.data_bindings)
                existing.children.extend(component.children)
                
        return list(unique_components.values())