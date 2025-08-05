from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import json
import re

# Data Models
class ProjectType(Enum):
    WEB_APPLICATION = "web_application"
    MOBILE_APPLICATION = "mobile_application"
    API_SERVICE = "api_service"
    CLI_TOOL = "cli_tool"
    FULL_STACK = "full_stack"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TechnicalRequirement:
    id: str
    description: str
    category: str
    priority: Priority
    measurable_criteria: Optional[str] = None

@dataclass
class ProjectRequirements:
    description: str
    project_type: ProjectType
    estimated_complexity: str
    functional_requirements: List[str] = field(default_factory=list)
    technical_requirements: List[TechnicalRequirement] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    technology_preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    ambiguities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

# Core NL Input Agent
class NLInputAgent:
    """자연어 프로젝트 설명을 분석하고 요구사항을 추출하는 에이전트"""

    def __init__(self):
        self.project_type_classifier = ProjectTypeClassifier()
        self.requirement_extractor = RequirementExtractor()
        self.tech_stack_analyzer = TechStackAnalyzer()
        self.entity_recognizer = EntityRecognizer()
        self.validation_engine = RequirementValidator()

    async def process_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """자연어 프로젝트 설명 처리"""
        
        # 1. 프로젝트 타입 분류
        project_type = await self.project_type_classifier.classify(description)
        
        # 2. 복잡도 추정
        complexity = self._estimate_complexity(description)
        
        # 3. 요구사항 추출
        functional_reqs = await self.requirement_extractor.extract_functional(description)
        technical_reqs = await self.requirement_extractor.extract_technical(description)
        non_functional_reqs = await self.requirement_extractor.extract_non_functional(description)
        
        # 4. 기술 스택 분석
        tech_preferences = await self.tech_stack_analyzer.analyze(description)
        
        # 5. 엔티티 인식
        entities = await self.entity_recognizer.recognize(description)
        
        # 6. 제약사항 식별
        constraints = self._extract_constraints(description)
        
        # 7. 신뢰도 계산
        confidence = self._calculate_confidence(description, functional_reqs, technical_reqs)
        
        # 8. 모호성 식별
        ambiguities = self._identify_ambiguities(description, tech_preferences)
        
        return ProjectRequirements(
            description=description,
            project_type=project_type,
            estimated_complexity=complexity,
            functional_requirements=functional_reqs,
            technical_requirements=technical_reqs,
            non_functional_requirements=non_functional_reqs,
            technology_preferences=tech_preferences,
            constraints=constraints,
            extracted_entities=entities,
            confidence_score=confidence,
            ambiguities=ambiguities
        )

    def _estimate_complexity(self, description: str) -> str:
        """복잡도 추정"""
        complexity_indicators = {
            'simple': ['basic', 'simple', 'crud', 'static'],
            'medium': ['api', 'database', 'auth', 'responsive'],
            'complex': ['real-time', 'microservice', 'scale', 'distributed'],
            'very_complex': ['ai', 'ml', 'blockchain', 'big data']
        }
        
        desc_lower = description.lower()
        scores = {}
        
        for level, keywords in complexity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in desc_lower)
            scores[level] = score
        
        return max(scores, key=scores.get) if scores else 'medium'

    def _extract_constraints(self, description: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        constraint_patterns = [
            r'budget.*?(\$[\d,]+|\d+\s*dollars?)',
            r'deadline.*?(\d+\s*(?:days?|weeks?|months?))',
            r'must use\s+([^.]+)',
            r'cannot use\s+([^.]+)',
            r'compliance.*?(gdpr|hipaa|sox|pci)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                constraints.append(match.group().strip())
        
        return constraints

    def _calculate_confidence(self, description: str, functional_reqs: List[str], technical_reqs: List[TechnicalRequirement]) -> float:
        """신뢰도 계산"""
        factors = []
        
        # 설명 길이
        desc_length = len(description.split())
        length_score = min(desc_length / 50, 1.0)
        factors.append(length_score)
        
        # 요구사항 수
        req_count = len(functional_reqs) + len(technical_reqs)
        req_score = min(req_count / 10, 1.0)
        factors.append(req_score)
        
        # 기술적 세부사항
        tech_keywords = ['api', 'database', 'framework', 'library', 'service']
        tech_mentions = sum(1 for keyword in tech_keywords if keyword in description.lower())
        tech_score = min(tech_mentions / 5, 1.0)
        factors.append(tech_score)
        
        return sum(factors) / len(factors)

    def _identify_ambiguities(self, description: str, tech_preferences: Dict[str, Any]) -> List[str]:
        """모호성 식별"""
        ambiguities = []
        
        if not tech_preferences.get('frontend'):
            ambiguities.append("Frontend framework not specified")
        
        if not tech_preferences.get('backend'):
            ambiguities.append("Backend technology not specified")
        
        if 'database' not in description.lower():
            ambiguities.append("Database requirements unclear")
        
        if not re.search(r'\d+\s*users?', description, re.IGNORECASE):
            ambiguities.append("Expected user count not specified")
        
        return ambiguities

# Supporting Classes
class ProjectTypeClassifier:
    async def classify(self, description: str) -> ProjectType:
        """프로젝트 타입 분류"""
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in ['web', 'website', 'webapp', 'browser']):
            return ProjectType.WEB_APPLICATION
        elif any(keyword in desc_lower for keyword in ['mobile', 'ios', 'android', 'app']):
            return ProjectType.MOBILE_APPLICATION
        elif any(keyword in desc_lower for keyword in ['api', 'rest', 'graphql', 'service']):
            return ProjectType.API_SERVICE
        elif any(keyword in desc_lower for keyword in ['cli', 'command', 'terminal', 'script']):
            return ProjectType.CLI_TOOL
        else:
            return ProjectType.FULL_STACK

class RequirementExtractor:
    async def extract_functional(self, description: str) -> List[str]:
        """기능 요구사항 추출"""
        functional_patterns = [
            r'user(?:s)?\s+(?:can|should|must|will)\s+([^.]+)',
            r'system\s+(?:should|must|will)\s+([^.]+)',
            r'feature(?:s)?:?\s*([^.]+)',
            r'functionality:?\s*([^.]+)'
        ]
        
        requirements = []
        for pattern in functional_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                req = match.group(1).strip()
                if req and len(req) > 5:
                    requirements.append(req)
        
        return list(set(requirements))

    async def extract_technical(self, description: str) -> List[TechnicalRequirement]:
        """기술 요구사항 추출"""
        tech_patterns = [
            (r'performance.*?(\d+\s*(?:ms|seconds?|requests?))', 'performance', Priority.HIGH),
            (r'security.*?(encrypt|auth|ssl|https)', 'security', Priority.CRITICAL),
            (r'scalability.*?(\d+\s*users?)', 'scalability', Priority.MEDIUM),
            (r'availability.*?(\d+\.?\d*%)', 'reliability', Priority.HIGH)
        ]
        
        requirements = []
        for i, (pattern, category, priority) in enumerate(tech_patterns):
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for j, match in enumerate(matches):
                req = TechnicalRequirement(
                    id=f"TR-{i+1:02d}-{j+1:02d}",
                    description=match.group().strip(),
                    category=category,
                    priority=priority,
                    measurable_criteria=match.group(1) if match.groups() else None
                )
                requirements.append(req)
        
        return requirements

    async def extract_non_functional(self, description: str) -> List[str]:
        """비기능 요구사항 추출"""
        nfr_patterns = [
            r'usability.*?([^.]+)',
            r'maintainability.*?([^.]+)',
            r'compatibility.*?([^.]+)',
            r'portability.*?([^.]+)'
        ]
        
        requirements = []
        for pattern in nfr_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                req = match.group().strip()
                if req and len(req) > 5:
                    requirements.append(req)
        
        return list(set(requirements))

class TechStackAnalyzer:
    async def analyze(self, description: str) -> Dict[str, Any]:
        """기술 스택 분석"""
        tech_mapping = {
            'frontend': {
                'react': ['react', 'jsx', 'next.js'],
                'vue': ['vue', 'nuxt'],
                'angular': ['angular', 'typescript'],
                'vanilla': ['html', 'css', 'javascript']
            },
            'backend': {
                'node': ['node', 'express', 'fastify'],
                'python': ['python', 'django', 'flask', 'fastapi'],
                'java': ['java', 'spring', 'springboot'],
                'go': ['go', 'golang', 'gin']
            },
            'database': {
                'postgresql': ['postgres', 'postgresql'],
                'mysql': ['mysql'],
                'mongodb': ['mongo', 'mongodb'],
                'redis': ['redis', 'cache']
            }
        }
        
        preferences = {}
        desc_lower = description.lower()
        
        for category, techs in tech_mapping.items():
            detected = []
            for tech, keywords in techs.items():
                if any(keyword in desc_lower for keyword in keywords):
                    detected.append(tech)
            
            if detected:
                preferences[category] = {
                    'preferred': detected,
                    'alternatives': [],
                    'constraints': []
                }
        
        return preferences

class EntityRecognizer:
    async def recognize(self, description: str) -> Dict[str, Any]:
        """엔티티 인식"""
        entities = {
            'technologies': [],
            'features': [],
            'user_types': [],
            'metrics': []
        }
        
        # 기술 엔티티
        tech_pattern = r'\b(react|vue|angular|node|python|java|mysql|postgres|redis|docker|aws)\b'
        tech_matches = re.finditer(tech_pattern, description, re.IGNORECASE)
        for match in tech_matches:
            entities['technologies'].append(match.group())
        
        # 메트릭 엔티티
        metric_pattern = r'\b(\d+(?:,\d{3})*)\s*(users?|requests?|ms|seconds?|%)\b'
        metric_matches = re.finditer(metric_pattern, description, re.IGNORECASE)
        for match in metric_matches:
            entities['metrics'].append(f"{match.group(1)} {match.group(2)}")
        
        return entities

class RequirementValidator:
    async def validate(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """요구사항 검증"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # 기본 검증
        if not requirements.functional_requirements:
            validation_result['warnings'].append("No functional requirements identified")
        
        if not requirements.technology_preferences:
            validation_result['warnings'].append("No technology preferences specified")
        
        if requirements.confidence_score < 0.5:
            validation_result['warnings'].append("Low confidence in requirement extraction")
        
        # 일관성 검증
        if requirements.project_type == ProjectType.API_SERVICE and 'frontend' in requirements.technology_preferences:
            validation_result['suggestions'].append("API service typically doesn't need frontend framework")
        
        return validation_result