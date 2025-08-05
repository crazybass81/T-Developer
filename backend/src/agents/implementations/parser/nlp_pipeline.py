"""
Parser Agent - NLP Pipeline Implementation
SubTask 4.21.2: 자연어 처리 파이프라인 구현
"""

from typing import List, Dict, Any, Tuple
import re
from dataclasses import dataclass
from enum import Enum

@dataclass
class NLPResult:
    tokens: List[str]
    entities: List[Dict[str, Any]]
    key_phrases: List[str]
    sentiment: str
    intent: str
    modality: str  # must, should, could, won't
    dependencies: List[Tuple[str, str, str]]

class NLPPipeline:
    """자연어 처리 파이프라인"""

    def __init__(self):
        self.entity_patterns = self._initialize_entity_patterns()
        self.intent_patterns = self._initialize_intent_patterns()
        self.modality_patterns = self._initialize_modality_patterns()

    async def process(self, text: str) -> NLPResult:
        """텍스트 NLP 처리"""
        
        # 1. 토큰화
        tokens = self._tokenize(text)
        
        # 2. 개체명 인식
        entities = self._extract_entities(text)
        
        # 3. 핵심 구문 추출
        key_phrases = self._extract_key_phrases(text, tokens)
        
        # 4. 감정 분석
        sentiment = self._analyze_sentiment(text)
        
        # 5. 의도 분류
        intent = self._classify_intent(text)
        
        # 6. 양상 감지
        modality = self._detect_modality(text)
        
        # 7. 의존성 분석
        dependencies = self._analyze_dependencies(text)
        
        return NLPResult(
            tokens=tokens,
            entities=entities,
            key_phrases=key_phrases,
            sentiment=sentiment,
            intent=intent,
            modality=modality,
            dependencies=dependencies
        )

    def _tokenize(self, text: str) -> List[str]:
        """토큰화"""
        # 간단한 토큰화 (실제로는 spaCy 등 사용)
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [token for token in tokens if len(token) > 2]

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """개체명 인식"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8
                    })
        
        return entities

    def _extract_key_phrases(self, text: str, tokens: List[str]) -> List[str]:
        """핵심 구문 추출"""
        # TF-IDF 기반 간단한 키워드 추출
        tech_keywords = [
            'authentication', 'database', 'api', 'security', 'performance',
            'scalability', 'user', 'system', 'application', 'service'
        ]
        
        key_phrases = []
        for keyword in tech_keywords:
            if keyword in text.lower():
                key_phrases.append(keyword)
        
        # 명사구 패턴
        noun_phrases = re.findall(r'\b(?:user|system|application)\s+\w+', text, re.IGNORECASE)
        key_phrases.extend(noun_phrases[:5])
        
        return list(set(key_phrases))[:10]

    def _analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'amazing']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _classify_intent(self, text: str) -> str:
        """의도 분류"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent
        return 'general'

    def _detect_modality(self, text: str) -> str:
        """양상 감지 (RFC 2119 키워드)"""
        for modality, patterns in self.modality_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return modality
        return 'should'

    def _analyze_dependencies(self, text: str) -> List[Tuple[str, str, str]]:
        """의존성 분석"""
        dependencies = []
        
        # 간단한 의존성 패턴
        dependency_patterns = [
            r'(\w+)\s+depends on\s+(\w+)',
            r'(\w+)\s+requires\s+(\w+)',
            r'after\s+(\w+),\s+(\w+)'
        ]
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    dependencies.append((match[0], 'depends_on', match[1]))
        
        return dependencies

    def _initialize_entity_patterns(self) -> Dict[str, List[str]]:
        """개체명 패턴 초기화"""
        return {
            'TECHNOLOGY': [
                r'\b(React|Vue|Angular|Node\.js|Python|Java|JavaScript|TypeScript)\b',
                r'\b(MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes)\b'
            ],
            'UI_COMPONENT': [
                r'\b(button|form|input|dropdown|modal|navbar|sidebar|menu|table|list|grid|card)\b',
                r'\b(header|footer|section|container|wrapper|layout)\b'
            ],
            'API_COMPONENT': [
                r'\b(endpoint|route|api|rest|graphql|webhook|websocket)\b',
                r'\b(GET|POST|PUT|DELETE|PATCH)\s+/[\w/\-{}]+',
                r'/api/[\w/\-{}]+'
            ],
            'DATABASE': [
                r'\b(database|table|collection|schema|index|query|transaction)\b',
                r'\b(sql|nosql|mongodb|postgres|mysql|redis)\b'
            ],
            'AUTHENTICATION': [
                r'\b(auth|authentication|authorization|login|logout|session|token)\b',
                r'\b(oauth|jwt|sso|ldap|saml|2fa|mfa)\b'
            ],
            'PERFORMANCE': [
                r'\b(\d+)\s*(ms|milliseconds|seconds?|minutes?)\b',
                r'\b(latency|response time|throughput|performance)\b',
                r'\b(\d+)\s*(users?|requests?|transactions?)\b'
            ]
        }

    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """의도 패턴 초기화"""
        return {
            'create': [r'\b(create|build|develop|make|generate)\b'],
            'update': [r'\b(update|modify|change|edit|alter)\b'],
            'delete': [r'\b(delete|remove|destroy|eliminate)\b'],
            'query': [r'\b(search|find|query|get|retrieve|fetch)\b'],
            'authenticate': [r'\b(login|signin|authenticate|authorize)\b'],
            'integrate': [r'\b(integrate|connect|link|combine)\b'],
            'optimize': [r'\b(optimize|improve|enhance|speed up)\b'],
            'secure': [r'\b(secure|protect|encrypt|safeguard)\b']
        }

    def _initialize_modality_patterns(self) -> Dict[str, List[str]]:
        """양상 패턴 초기화"""
        return {
            'must': [r'\b(must|shall|required|mandatory)\b'],
            'should': [r'\b(should|recommended|preferred)\b'],
            'could': [r'\b(could|may|optional|might)\b'],
            'wont': [r'\b(won\'t|will not|cannot|must not)\b']
        }

class RequirementExtractor:
    """요구사항 추출기"""
    
    def __init__(self):
        self.requirement_patterns = self._initialize_requirement_patterns()
    
    async def extract_functional(self, feature: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기능 요구사항 추출"""
        requirements = []
        
        # 기본 요구사항 생성
        req = {
            'description': feature,
            'category': self._categorize_feature(feature),
            'priority': self._determine_priority(feature),
            'acceptance_criteria': self._generate_acceptance_criteria(feature),
            'technical_details': self._extract_technical_details(feature)
        }
        
        requirements.append(req)
        return requirements
    
    def _categorize_feature(self, feature: str) -> str:
        """기능 분류"""
        feature_lower = feature.lower()
        
        if any(word in feature_lower for word in ['auth', 'login', 'signin']):
            return 'authentication'
        elif any(word in feature_lower for word in ['user', 'profile', 'account']):
            return 'user_management'
        elif any(word in feature_lower for word in ['data', 'crud', 'database']):
            return 'data_management'
        elif any(word in feature_lower for word in ['ui', 'interface', 'form']):
            return 'user_interface'
        elif any(word in feature_lower for word in ['api', 'service', 'endpoint']):
            return 'api'
        else:
            return 'general'
    
    def _determine_priority(self, feature: str) -> str:
        """우선순위 결정"""
        feature_lower = feature.lower()
        
        if any(word in feature_lower for word in ['critical', 'essential', 'must']):
            return 'critical'
        elif any(word in feature_lower for word in ['important', 'should', 'required']):
            return 'high'
        elif any(word in feature_lower for word in ['nice', 'could', 'optional']):
            return 'low'
        else:
            return 'medium'
    
    def _generate_acceptance_criteria(self, feature: str) -> List[str]:
        """수용 기준 생성"""
        criteria = []
        
        # 기본 수용 기준
        criteria.append(f"Given the system, when {feature.lower()}, then it should work correctly")
        
        # 에러 처리
        criteria.append("System should handle errors gracefully")
        
        # 성능
        if 'performance' in feature.lower() or 'speed' in feature.lower():
            criteria.append("Response time should be under 2 seconds")
        
        return criteria
    
    def _extract_technical_details(self, feature: str) -> Dict[str, Any]:
        """기술적 세부사항 추출"""
        details = {}
        
        # 기술 스택 감지
        tech_stack = []
        technologies = ['react', 'vue', 'angular', 'node.js', 'python', 'java']
        for tech in technologies:
            if tech in feature.lower():
                tech_stack.append(tech)
        
        if tech_stack:
            details['technologies'] = tech_stack
        
        # API 엔드포인트 감지
        api_matches = re.findall(r'(GET|POST|PUT|DELETE)\s+(/\S+)', feature, re.IGNORECASE)
        if api_matches:
            details['api_endpoints'] = [{'method': m[0], 'path': m[1]} for m in api_matches]
        
        return details
    
    def _initialize_requirement_patterns(self) -> Dict[str, List[str]]:
        """요구사항 패턴 초기화"""
        return {
            'functional': [
                r'(system|application|user)\s+(shall|must|should|will)\s+([^.]+)',
                r'(need|require|want)\s+to\s+([^.]+)',
                r'(it\s+is\s+)?(required|necessary|important)\s+(that|to)\s+([^.]+)'
            ],
            'non_functional': [
                r'(performance|speed|latency|response time)',
                r'(security|authentication|authorization)',
                r'(scalability|concurrent|users)'
            ]
        }