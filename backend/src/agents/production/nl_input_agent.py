"""
NL Input Agent - Production Implementation
Analyzes natural language input and extracts structured requirements
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class NLAnalysisResult:
    """Result from NL Input analysis"""
    project_type: str
    project_name: str
    description: str
    features: List[str]
    framework: str
    ui_requirements: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    confidence_score: float


class NLInputAgent:
    """Production NL Input Agent that actually analyzes user input"""
    
    def __init__(self):
        self.keywords = {
            'project_types': {
                'todo': ['todo', 'task', 'list', '할일', '투두'],
                'blog': ['blog', 'post', 'article', '블로그', '글쓰기'],
                'ecommerce': ['shop', 'store', 'cart', 'product', '쇼핑', '상품'],
                'dashboard': ['dashboard', 'admin', 'analytics', '대시보드', '관리자'],
                'chat': ['chat', 'message', 'conversation', '채팅', '메시지'],
                'portfolio': ['portfolio', 'gallery', 'showcase', '포트폴리오'],
            },
            'frameworks': {
                'react': ['react', 'nextjs', 'next.js', '리액트'],
                'vue': ['vue', 'nuxt', '뷰'],
                'angular': ['angular', '앵귤러'],
                'svelte': ['svelte', '스벨트'],
            },
            'features': {
                'auth': ['login', 'auth', 'user', 'signin', '로그인', '인증'],
                'database': ['database', 'db', 'storage', 'save', '데이터베이스', '저장'],
                'api': ['api', 'backend', 'server', 'rest', 'graphql'],
                'responsive': ['responsive', 'mobile', 'tablet', '반응형', '모바일'],
                'realtime': ['realtime', 'live', 'websocket', '실시간'],
                'typescript': ['typescript', 'ts', '타입스크립트'],
                'tailwind': ['tailwind', 'tailwindcss', '테일윈드'],
                'testing': ['test', 'testing', 'jest', '테스트'],
            }
        }
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process natural language input and extract structured data
        
        Args:
            input_data: Dictionary containing user_input, project_name, etc.
            
        Returns:
            Structured analysis result
        """
        
        user_input = input_data.get('user_input', '').lower()
        project_name = input_data.get('project_name', 'my-app')
        
        # Analyze project type
        project_type = self._detect_project_type(user_input)
        
        # Detect framework preference
        framework = self._detect_framework(user_input)
        
        # Extract features
        features = self._extract_features(user_input)
        
        # Extract UI requirements
        ui_requirements = self._analyze_ui_requirements(user_input, project_type)
        
        # Extract technical requirements
        technical_requirements = self._analyze_technical_requirements(user_input, features)
        
        # Calculate confidence based on clarity of requirements
        confidence_score = self._calculate_confidence(user_input, project_type, framework)
        
        result = NLAnalysisResult(
            project_type=project_type,
            project_name=project_name,
            description=input_data.get('user_input', ''),
            features=features,
            framework=framework,
            ui_requirements=ui_requirements,
            technical_requirements=technical_requirements,
            confidence_score=confidence_score
        )
        
        return asdict(result)
    
    def _detect_project_type(self, text: str) -> str:
        """Detect the type of project from text"""
        
        scores = {}
        for ptype, keywords in self.keywords['project_types'].items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[ptype] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # Default to web app if no specific type detected
        return 'web'
    
    def _detect_framework(self, text: str) -> str:
        """Detect preferred framework from text"""
        
        for framework, keywords in self.keywords['frameworks'].items():
            for keyword in keywords:
                if keyword in text:
                    return framework
        
        # Default to React if no framework specified
        return 'react'
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract requested features from text"""
        
        features = []
        for feature, keywords in self.keywords['features'].items():
            for keyword in keywords:
                if keyword in text:
                    features.append(feature)
                    break
        
        # Add default features based on text analysis
        if '타입' in text or 'type' in text:
            features.append('typescript')
        
        if '스타일' in text or 'style' in text or 'design' in text:
            features.append('tailwind')
            
        if '모바일' in text or 'mobile' in text:
            features.append('responsive')
        
        return list(set(features))  # Remove duplicates
    
    def _analyze_ui_requirements(self, text: str, project_type: str) -> Dict[str, Any]:
        """Analyze UI-specific requirements"""
        
        ui_reqs = {
            'theme': 'light',
            'primary_color': '#3498db',
            'layout': 'responsive',
            'components': []
        }
        
        # Detect theme preference
        if 'dark' in text or '다크' in text:
            ui_reqs['theme'] = 'dark'
        
        # Suggest components based on project type
        if project_type == 'todo':
            ui_reqs['components'] = ['TodoList', 'TodoItem', 'AddTodo', 'FilterBar']
        elif project_type == 'blog':
            ui_reqs['components'] = ['PostList', 'PostDetail', 'Sidebar', 'Comments']
        elif project_type == 'ecommerce':
            ui_reqs['components'] = ['ProductGrid', 'Cart', 'Checkout', 'ProductDetail']
        elif project_type == 'dashboard':
            ui_reqs['components'] = ['Charts', 'Stats', 'Tables', 'Sidebar']
        elif project_type == 'chat':
            ui_reqs['components'] = ['MessageList', 'InputBox', 'UserList', 'ChatHeader']
        else:
            ui_reqs['components'] = ['Header', 'Main', 'Footer', 'Navigation']
        
        # Detect specific UI preferences
        if 'material' in text:
            ui_reqs['design_system'] = 'material-ui'
        elif 'bootstrap' in text:
            ui_reqs['design_system'] = 'bootstrap'
        elif 'ant' in text:
            ui_reqs['design_system'] = 'antd'
        else:
            ui_reqs['design_system'] = 'custom'
        
        return ui_reqs
    
    def _analyze_technical_requirements(self, text: str, features: List[str]) -> Dict[str, Any]:
        """Analyze technical requirements"""
        
        tech_reqs = {
            'performance': 'standard',
            'seo': False,
            'pwa': False,
            'accessibility': True,
            'browser_support': 'modern'
        }
        
        # Performance requirements
        if 'fast' in text or '빠른' in text or 'performance' in text:
            tech_reqs['performance'] = 'optimized'
        
        # SEO requirements
        if 'seo' in text or 'search' in text or '검색' in text:
            tech_reqs['seo'] = True
        
        # PWA requirements
        if 'pwa' in text or 'offline' in text or '오프라인' in text:
            tech_reqs['pwa'] = True
        
        # Accessibility
        if 'a11y' in text or 'accessibility' in text or '접근성' in text:
            tech_reqs['accessibility'] = True
        
        # Database requirements
        if 'database' in features or 'db' in text:
            tech_reqs['database'] = {
                'type': 'postgresql' if 'postgres' in text else 'mongodb',
                'orm': 'prisma' if 'prisma' in text else 'native'
            }
        
        # API requirements
        if 'api' in features:
            tech_reqs['api'] = {
                'type': 'graphql' if 'graphql' in text else 'rest',
                'auth': 'jwt' if 'auth' in features else None
            }
        
        return tech_reqs
    
    def _calculate_confidence(self, text: str, project_type: str, framework: str) -> float:
        """Calculate confidence score based on clarity of requirements"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear project type
        if project_type != 'web':
            confidence += 0.2
        
        # Increase confidence for specified framework
        if framework in text:
            confidence += 0.15
        
        # Increase confidence based on text length (more detail = higher confidence)
        word_count = len(text.split())
        if word_count > 20:
            confidence += 0.1
        if word_count > 50:
            confidence += 0.05
        
        # Cap at 0.95
        return min(confidence, 0.95)