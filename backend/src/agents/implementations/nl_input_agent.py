"""
NL Input Agent - Production Implementation
First agent in the pipeline that analyzes natural language input
"""
import asyncio
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from src.core.interfaces import (
    BaseAgent, AgentInput, AgentResult, ProcessingStatus, 
    PipelineContext, ValidationResult
)
from src.core.agent_models import NLInputResult
from src.core.event_bus import publish_agent_event, EventType
from src.core.monitoring import get_metrics_collector, get_performance_tracker
from src.core.security import InputValidator
import logging

logger = logging.getLogger(__name__)


class NLInputAgent(BaseAgent):
    """
    Natural Language Input Agent
    Analyzes user input and extracts structured requirements
    """
    
    def __init__(self):
        super().__init__(name="nl_input", version="2.0.0")
        
        # Metrics and monitoring
        self.metrics = get_metrics_collector()
        self.perf_tracker = get_performance_tracker()
        
        # Enhanced keyword dictionaries
        self.keywords = {
            'project_types': {
                'todo': ['todo', 'task', 'list', 'checklist', '할일', '투두', '작업'],
                'blog': ['blog', 'post', 'article', 'writing', '블로그', '글쓰기', '포스트'],
                'ecommerce': ['shop', 'store', 'cart', 'product', 'payment', '쇼핑', '상품', '결제'],
                'dashboard': ['dashboard', 'admin', 'analytics', 'metrics', '대시보드', '관리자', '분석'],
                'chat': ['chat', 'message', 'conversation', 'messenger', '채팅', '메시지', '대화'],
                'portfolio': ['portfolio', 'gallery', 'showcase', 'resume', '포트폴리오', '갤러리'],
                'social': ['social', 'network', 'community', 'forum', '소셜', '커뮤니티', '포럼'],
                'saas': ['saas', 'subscription', 'service', 'platform', '서비스', '플랫폼'],
                'game': ['game', 'play', 'score', 'level', '게임', '플레이', '점수'],
                'education': ['education', 'learning', 'course', 'tutorial', '교육', '학습', '강의']
            },
            'frameworks': {
                'react': ['react', 'nextjs', 'next.js', 'next', '리액트', '넥스트'],
                'vue': ['vue', 'nuxt', 'vuejs', '뷰', '뷰제이에스'],
                'angular': ['angular', 'ng', '앵귤러'],
                'svelte': ['svelte', 'sveltekit', '스벨트'],
                'solid': ['solid', 'solidjs', '솔리드'],
                'express': ['express', 'node', 'nodejs', '익스프레스', '노드'],
                'fastapi': ['fastapi', 'python', '패스트API', '파이썬'],
                'django': ['django', '장고'],
                'rails': ['rails', 'ruby', '레일즈', '루비']
            },
            'features': {
                'auth': ['login', 'auth', 'user', 'signin', 'signup', 'oauth', '로그인', '인증', '회원'],
                'database': ['database', 'db', 'storage', 'persist', 'save', '데이터베이스', '저장', 'DB'],
                'api': ['api', 'backend', 'server', 'rest', 'graphql', 'endpoint', 'API', '백엔드'],
                'responsive': ['responsive', 'mobile', 'tablet', 'adaptive', '반응형', '모바일', '태블릿'],
                'realtime': ['realtime', 'live', 'websocket', 'streaming', '실시간', '라이브', '웹소켓'],
                'typescript': ['typescript', 'ts', 'typed', '타입스크립트', '타입'],
                'tailwind': ['tailwind', 'tailwindcss', 'utility', '테일윈드'],
                'testing': ['test', 'testing', 'jest', 'vitest', 'cypress', '테스트', '테스팅'],
                'docker': ['docker', 'container', 'kubernetes', '도커', '컨테이너'],
                'ci_cd': ['ci', 'cd', 'pipeline', 'deploy', 'github actions', 'CI/CD', '배포'],
                'seo': ['seo', 'search', 'meta', 'sitemap', 'SEO', '검색', '메타'],
                'pwa': ['pwa', 'offline', 'service worker', 'PWA', '오프라인'],
                'payment': ['payment', 'stripe', 'paypal', 'checkout', '결제', '페이먼트'],
                'email': ['email', 'mail', 'smtp', 'newsletter', '이메일', '메일'],
                'notification': ['notification', 'alert', 'push', 'notify', '알림', '푸시'],
                'search': ['search', 'filter', 'query', 'find', '검색', '필터', '찾기'],
                'upload': ['upload', 'file', 'image', 'media', '업로드', '파일', '이미지'],
                'chart': ['chart', 'graph', 'visualization', 'plot', '차트', '그래프', '시각화'],
                'map': ['map', 'location', 'gps', 'geocoding', '지도', '위치', 'GPS'],
                'ai': ['ai', 'ml', 'machine learning', 'gpt', 'AI', '인공지능', '머신러닝']
            },
            'ui_preferences': {
                'dark_mode': ['dark', 'night', 'dark mode', 'dark theme', '다크', '다크모드', '어두운'],
                'light_mode': ['light', 'bright', 'light mode', '라이트', '밝은'],
                'minimalist': ['minimal', 'simple', 'clean', 'minimalist', '미니멀', '심플', '깔끔'],
                'modern': ['modern', 'contemporary', 'trendy', '모던', '현대적', '트렌디'],
                'colorful': ['colorful', 'vibrant', 'bright colors', '컬러풀', '화려한', '밝은색'],
                'professional': ['professional', 'business', 'corporate', '전문적', '비즈니스', '기업']
            }
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'simple': ['simple', 'basic', 'easy', 'quick', '간단한', '기본', '쉬운', '빠른'],
            'medium': ['standard', 'normal', 'typical', '표준', '일반적인', '보통'],
            'complex': ['complex', 'advanced', 'sophisticated', 'enterprise', '복잡한', '고급', '정교한', '엔터프라이즈']
        }
    
    async def validate_input(self, input_data: AgentInput[Dict]) -> ValidationResult:
        """Enhanced input validation"""
        result = await super().validate_input(input_data)
        
        # Additional NL-specific validation
        if not input_data.data:
            result.add_error("Input data is empty")
            return result
        
        query = input_data.data.get('query', '').strip()
        
        # Use security validator
        validation = InputValidator.validate_project_query(query)
        if not validation['valid']:
            for error in validation['errors']:
                result.add_error(error)
        
        for warning in validation.get('warnings', []):
            result.add_warning(warning)
        
        return result
    
    async def process(self, input_data: AgentInput[Dict]) -> AgentResult[NLInputResult]:
        """Process natural language input"""
        timer_id = self.perf_tracker.start_timer("nl_input_processing")
        
        try:
            # Extract and sanitize query
            query = InputValidator.sanitize_string(
                input_data.data.get('query', ''),
                max_length=1000
            )
            
            # Publish start event
            await publish_agent_event(
                EventType.AGENT_STARTED,
                self.name,
                input_data.context.pipeline_id,
                {"query_length": len(query)}
            )
            
            # Perform analysis
            project_type = self._detect_project_type(query)
            main_functionality = self._extract_main_functionality(query, project_type)
            features = self._extract_features(query)
            technical_reqs = self._analyze_technical_requirements(query, features)
            constraints = self._extract_constraints(query)
            preferences = self._extract_preferences(query)
            complexity = self._assess_complexity(query, features)
            keywords = self._extract_keywords(query)
            
            # Language detection
            language = self._detect_language(query)
            sentiment = self._analyze_sentiment(query)
            clarity_score = self._calculate_clarity_score(query, project_type, features)
            
            # Estimate effort
            estimated_effort = self._estimate_effort(complexity, len(features))
            
            # Calculate confidence
            intent_confidence = self._calculate_confidence(
                query, project_type, features, clarity_score
            )
            
            # Create result
            result_data = NLInputResult(
                project_type=project_type,
                main_functionality=main_functionality,
                technical_requirements=technical_reqs,
                features=features,
                constraints=constraints,
                preferences=preferences,
                complexity=complexity,
                estimated_effort_hours=estimated_effort,
                keywords=keywords,
                intent_confidence=intent_confidence,
                language=language,
                sentiment=sentiment,
                clarity_score=clarity_score
            )
            
            # Stop timer and record metrics
            duration = self.perf_tracker.stop_timer(timer_id)
            self.metrics.increment_counter("nl_input.processed")
            self.metrics.record_histogram("nl_input.features_count", len(features))
            self.metrics.set_gauge("nl_input.confidence", intent_confidence)
            
            # Publish completion event
            await publish_agent_event(
                EventType.AGENT_COMPLETED,
                self.name,
                input_data.context.pipeline_id,
                {
                    "project_type": project_type,
                    "features_count": len(features),
                    "confidence": intent_confidence
                }
            )
            
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                status=ProcessingStatus.COMPLETED,
                data=result_data,
                execution_time_ms=duration,
                confidence=intent_confidence,
                quality_score=clarity_score,
                metadata={
                    "query_length": len(query),
                    "detected_language": language,
                    "features_extracted": len(features)
                }
            )
            
        except Exception as e:
            logger.error(f"NL Input Agent error: {e}")
            self.metrics.increment_counter("nl_input.errors")
            
            await publish_agent_event(
                EventType.AGENT_FAILED,
                self.name,
                input_data.context.pipeline_id,
                {"error": str(e)}
            )
            
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                status=ProcessingStatus.FAILED,
                error=str(e),
                execution_time_ms=self.perf_tracker.stop_timer(timer_id)
            )
    
    def _detect_project_type(self, text: str) -> str:
        """Enhanced project type detection with scoring"""
        text_lower = text.lower()
        scores = {}
        
        for ptype, keywords in self.keywords['project_types'].items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight by keyword length (longer = more specific)
                    score += len(keyword) / 3
            
            if score > 0:
                scores[ptype] = score
        
        if scores:
            # Return type with highest score
            return max(scores, key=scores.get)
        
        # Fallback detection based on general terms
        if any(word in text_lower for word in ['web', 'website', 'site', '웹', '웹사이트']):
            return 'web_application'
        elif any(word in text_lower for word in ['app', 'application', '앱', '애플리케이션']):
            return 'web_application'
        
        return 'web_application'  # Default
    
    def _extract_main_functionality(self, text: str, project_type: str) -> str:
        """Extract the main functionality description"""
        # Try to extract the core purpose from the text
        text_lower = text.lower()
        
        # Remove common prefixes
        prefixes = ['create', 'build', 'make', 'develop', '만들어', '개발', '생성', '구축']
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text_lower = text_lower[len(prefix):].strip()
        
        # Extract first significant phrase
        sentences = re.split(r'[.!?]', text)
        if sentences:
            main_sentence = sentences[0].strip()
            # Limit to reasonable length
            if len(main_sentence) > 100:
                main_sentence = main_sentence[:100] + "..."
            return main_sentence
        
        return f"{project_type} application"
    
    def _extract_features(self, text: str) -> List[str]:
        """Enhanced feature extraction with priority"""
        text_lower = text.lower()
        features = []
        feature_scores = {}
        
        for feature, keywords in self.keywords['features'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Score based on keyword specificity
                    score = len(keyword) / 5
                    if feature not in feature_scores:
                        feature_scores[feature] = 0
                    feature_scores[feature] += score
        
        # Sort by score and take features
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        features = [f[0] for f in sorted_features]
        
        # Add implicit features
        if 'auth' in features and 'database' not in features:
            features.append('database')  # Auth requires database
        
        if 'payment' in features and 'auth' not in features:
            features.append('auth')  # Payment requires auth
        
        if 'realtime' in features and 'api' not in features:
            features.append('api')  # Realtime requires API
        
        return features
    
    def _analyze_technical_requirements(self, text: str, features: List[str]) -> Dict[str, Any]:
        """Comprehensive technical requirements analysis"""
        text_lower = text.lower()
        
        tech_reqs = {
            'frontend': [],
            'backend': [],
            'database': [],
            'infrastructure': [],
            'performance': 'standard',
            'security': 'standard',
            'scalability': 'standard'
        }
        
        # Frontend requirements
        for framework, keywords in self.keywords['frameworks'].items():
            if any(kw in text_lower for kw in keywords):
                tech_reqs['frontend'].append(framework)
                break
        
        if not tech_reqs['frontend']:
            tech_reqs['frontend'].append('react')  # Default
        
        # Add TypeScript if mentioned or implied
        if 'typescript' in features or 'ts' in text_lower or '타입' in text_lower:
            tech_reqs['frontend'].append('typescript')
        
        # Backend requirements
        if 'api' in features or 'backend' in text_lower:
            if 'graphql' in text_lower:
                tech_reqs['backend'].append('graphql')
            else:
                tech_reqs['backend'].append('rest')
            
            # Detect backend framework
            if 'express' in text_lower or 'node' in text_lower:
                tech_reqs['backend'].append('express')
            elif 'fastapi' in text_lower or 'python' in text_lower:
                tech_reqs['backend'].append('fastapi')
            elif 'django' in text_lower:
                tech_reqs['backend'].append('django')
            else:
                tech_reqs['backend'].append('express')  # Default
        
        # Database requirements
        if 'database' in features or 'auth' in features:
            if 'postgres' in text_lower or 'postgresql' in text_lower:
                tech_reqs['database'].append('postgresql')
            elif 'mongo' in text_lower or 'mongodb' in text_lower:
                tech_reqs['database'].append('mongodb')
            elif 'mysql' in text_lower:
                tech_reqs['database'].append('mysql')
            else:
                tech_reqs['database'].append('postgresql')  # Default
        
        # Infrastructure
        if 'docker' in features:
            tech_reqs['infrastructure'].append('docker')
        if 'ci_cd' in features:
            tech_reqs['infrastructure'].append('github_actions')
        if 'deploy' in text_lower or '배포' in text_lower:
            tech_reqs['infrastructure'].append('vercel')
        
        # Performance requirements
        if any(word in text_lower for word in ['fast', 'performance', 'optimize', '빠른', '성능', '최적화']):
            tech_reqs['performance'] = 'optimized'
        elif any(word in text_lower for word in ['enterprise', 'scale', '엔터프라이즈', '대규모']):
            tech_reqs['performance'] = 'enterprise'
        
        # Security requirements
        if any(word in text_lower for word in ['secure', 'security', 'encryption', '보안', '암호화']):
            tech_reqs['security'] = 'enhanced'
        
        # Scalability requirements
        if any(word in text_lower for word in ['scalable', 'scale', 'million', '확장', '백만']):
            tech_reqs['scalability'] = 'high'
        
        return tech_reqs
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract project constraints"""
        constraints = []
        text_lower = text.lower()
        
        # Time constraints
        time_patterns = [
            r'\b(\d+)\s*(day|days|일)\b',
            r'\b(\d+)\s*(week|weeks|주)\b',
            r'\b(\d+)\s*(month|months|개월)\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                constraints.append(f"Time limit: {match.group(0)}")
        
        # Budget constraints
        if any(word in text_lower for word in ['budget', 'cost', 'cheap', 'free', '예산', '비용', '무료']):
            constraints.append("Budget conscious")
        
        # Technical constraints
        if 'no backend' in text_lower or '백엔드 없이' in text_lower:
            constraints.append("No backend required")
        
        if 'offline' in text_lower or '오프라인' in text_lower:
            constraints.append("Offline capability required")
        
        if 'mobile first' in text_lower or '모바일 우선' in text_lower:
            constraints.append("Mobile-first design")
        
        return constraints
    
    def _extract_preferences(self, text: str) -> Dict[str, str]:
        """Extract user preferences"""
        preferences = {}
        text_lower = text.lower()
        
        # UI preferences
        for pref_type, keywords in self.keywords['ui_preferences'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    if 'theme' not in preferences:
                        preferences['theme'] = pref_type
                    if 'style' not in preferences and pref_type not in ['dark_mode', 'light_mode']:
                        preferences['style'] = pref_type
        
        # Set defaults if not specified
        if 'theme' not in preferences:
            preferences['theme'] = 'light_mode'
        if 'style' not in preferences:
            preferences['style'] = 'modern'
        
        # Styling preferences
        if 'tailwind' in text_lower:
            preferences['styling'] = 'tailwind'
        elif 'css modules' in text_lower:
            preferences['styling'] = 'css_modules'
        elif 'styled components' in text_lower:
            preferences['styling'] = 'styled_components'
        else:
            preferences['styling'] = 'tailwind'  # Default
        
        return preferences
    
    def _assess_complexity(self, text: str, features: List[str]) -> str:
        """Assess project complexity"""
        text_lower = text.lower()
        
        # Check for explicit complexity indicators
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        # Assess based on feature count and requirements
        feature_count = len(features)
        
        if feature_count <= 3:
            return 'simple'
        elif feature_count <= 7:
            return 'medium'
        else:
            return 'complex'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove stop words and extract significant terms
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were',
                     'that', 'this', 'these', 'those', 'i', 'you', 'we', 'they',
                     'create', 'build', 'make', 'want', 'need', 'app', 'application'}
        
        # Tokenize and filter
        words = re.findall(r'\b[a-z]+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequency and return top keywords
        from collections import Counter
        word_freq = Counter(keywords)
        
        return [word for word, _ in word_freq.most_common(10)]
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the input"""
        korean_pattern = re.compile(r'[\u3131-\u3163\uac00-\ud7a3]+')
        if korean_pattern.search(text):
            return 'ko'
        return 'en'
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ['love', 'great', 'awesome', 'excellent', 'good', 'nice',
                         '좋은', '훌륭한', '멋진', '최고']
        negative_words = ['hate', 'bad', 'terrible', 'awful', 'poor', 'worst',
                         '나쁜', '최악', '별로']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def _calculate_clarity_score(self, text: str, project_type: str, features: List[str]) -> float:
        """Calculate how clear the requirements are"""
        score = 0.5  # Base score
        
        # Clear project type increases score
        if project_type != 'web_application':  # Not default
            score += 0.15
        
        # Number of identified features
        if len(features) >= 3:
            score += 0.1
        if len(features) >= 5:
            score += 0.1
        
        # Text length (reasonable detail)
        word_count = len(text.split())
        if 20 <= word_count <= 100:
            score += 0.1
        elif word_count > 100:
            score += 0.05
        
        # Presence of technical details
        tech_terms = ['api', 'database', 'frontend', 'backend', 'deploy']
        if any(term in text.lower() for term in tech_terms):
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_effort(self, complexity: str, feature_count: int) -> int:
        """Estimate development effort in hours"""
        base_hours = {
            'simple': 40,
            'medium': 120,
            'complex': 320
        }
        
        hours = base_hours.get(complexity, 120)
        
        # Add hours based on features
        hours += feature_count * 8
        
        return hours
    
    def _calculate_confidence(self, text: str, project_type: str, 
                            features: List[str], clarity_score: float) -> float:
        """Calculate overall confidence in the analysis"""
        confidence = 0.5  # Base confidence
        
        # Project type clarity
        if project_type != 'web_application':
            confidence += 0.15
        
        # Features identified
        if len(features) > 0:
            confidence += min(len(features) * 0.05, 0.2)
        
        # Clarity score contribution
        confidence += clarity_score * 0.15
        
        # Text length contribution
        word_count = len(text.split())
        if word_count >= 20:
            confidence += 0.1
        
        return min(confidence, 0.95)


# Export the agent
__all__ = ['NLInputAgent']