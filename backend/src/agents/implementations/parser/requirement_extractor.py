from typing import Dict, List, Any, Optional
import re
from ..parser_agent import RequirementType, ParsedRequirement
from datetime import datetime

class RequirementExtractor:
    """요구사항 추출기"""

    def __init__(self):
        self.functional_patterns = self._load_functional_patterns()
        self.nfr_patterns = self._load_nfr_patterns()

    def _load_functional_patterns(self) -> List[str]:
        """기능 요구사항 패턴"""
        return [
            r'user\s+(can|should|must|shall)\s+(.+)',
            r'system\s+(shall|must|should|will)\s+(.+)',
            r'application\s+(provides|supports|enables)\s+(.+)',
            r'(create|read|update|delete|manage|process)\s+(.+)',
            r'(login|register|authenticate|authorize)\s+(.+)'
        ]

    def _load_nfr_patterns(self) -> Dict[str, List[str]]:
        """비기능 요구사항 패턴"""
        return {
            'performance': [
                r'response\s+time\s+.+\s+(\d+)\s*(ms|seconds)',
                r'load\s+time\s+.+\s+(\d+)\s*(ms|seconds)',
                r'throughput\s+.+\s+(\d+)\s*(requests|transactions)'
            ],
            'scalability': [
                r'support\s+(\d+[,\d]*)\s+(users|connections)',
                r'handle\s+(\d+[,\d]*)\s+(concurrent|simultaneous)',
                r'scale\s+to\s+(\d+[,\d]*)\s+(users|requests)'
            ],
            'security': [
                r'(encrypt|secure|protect)\s+(.+)',
                r'authentication\s+(.+)',
                r'authorization\s+(.+)',
                r'(ssl|tls|https)\s+(.+)'
            ],
            'reliability': [
                r'uptime\s+.+\s+(\d+\.?\d*)%',
                r'availability\s+.+\s+(\d+\.?\d*)%',
                r'backup\s+(.+)',
                r'recovery\s+(.+)'
            ]
        }

    async def extract_functional(
        self, 
        feature: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """기능 요구사항 추출"""
        requirements = []

        for pattern in self.functional_patterns:
            matches = re.finditer(pattern, feature, re.IGNORECASE)
            for match in matches:
                req = {
                    'description': match.group().strip(),
                    'category': self._categorize_functional(match.group()),
                    'priority': self._determine_priority(match.group()),
                    'acceptance_criteria': self._generate_acceptance_criteria(match.group()),
                    'technical_details': {}
                }
                requirements.append(req)

        # 기본 요구사항이 없으면 feature 자체를 요구사항으로
        if not requirements:
            requirements.append({
                'description': f"System shall provide {feature}",
                'category': 'general',
                'priority': 'medium',
                'acceptance_criteria': [f"User can access {feature}"],
                'technical_details': {}
            })

        return requirements

    async def extract_non_functional(
        self, 
        base_structure: Dict[str, Any]
    ) -> List[ParsedRequirement]:
        """비기능 요구사항 추출"""
        requirements = []
        text = str(base_structure)

        for category, patterns in self.nfr_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for idx, match in enumerate(matches):
                    req = ParsedRequirement(
                        id=f"NFR-{category.upper()}-{idx+1:03d}",
                        type=RequirementType.NON_FUNCTIONAL,
                        category=category,
                        description=match.group().strip(),
                        priority=self._determine_nfr_priority(category),
                        metadata={
                            'extracted_at': datetime.utcnow().isoformat(),
                            'pattern_used': pattern
                        }
                    )
                    requirements.append(req)

        return requirements

    async def extract_technical(
        self, 
        base_structure: Dict[str, Any]
    ) -> List[ParsedRequirement]:
        """기술 요구사항 추출"""
        requirements = []
        tech_context = base_structure.get('technical_context', {})

        # 기술 스택 요구사항
        if 'technologies' in tech_context:
            for idx, tech in enumerate(tech_context['technologies']):
                req = ParsedRequirement(
                    id=f"TR-TECH-{idx+1:03d}",
                    type=RequirementType.TECHNICAL,
                    category='technology',
                    description=f"System shall use {tech}",
                    priority='medium',
                    technical_details={'technology': tech}
                )
                requirements.append(req)

        # 아키텍처 요구사항
        if 'architecture' in tech_context:
            req = ParsedRequirement(
                id="TR-ARCH-001",
                type=RequirementType.TECHNICAL,
                category='architecture',
                description=f"System shall follow {tech_context['architecture']} architecture",
                priority='high',
                technical_details={'architecture': tech_context['architecture']}
            )
            requirements.append(req)

        return requirements

    async def extract_business(
        self, 
        base_structure: Dict[str, Any]
    ) -> List[ParsedRequirement]:
        """비즈니스 요구사항 추출"""
        requirements = []
        goals = base_structure.get('goals', [])

        for idx, goal in enumerate(goals):
            req = ParsedRequirement(
                id=f"BR-{idx+1:03d}",
                type=RequirementType.BUSINESS,
                category='business_goal',
                description=goal,
                priority='high',
                metadata={'goal_type': 'business_objective'}
            )
            requirements.append(req)

        return requirements

    def _categorize_functional(self, requirement: str) -> str:
        """기능 요구사항 분류"""
        categories = {
            'authentication': ['login', 'register', 'auth', 'password'],
            'data_management': ['create', 'read', 'update', 'delete', 'crud'],
            'user_interface': ['display', 'show', 'view', 'interface'],
            'integration': ['connect', 'integrate', 'api', 'external'],
            'reporting': ['report', 'export', 'generate', 'analytics']
        }

        req_lower = requirement.lower()
        for category, keywords in categories.items():
            if any(keyword in req_lower for keyword in keywords):
                return category

        return 'general'

    def _determine_priority(self, requirement: str) -> str:
        """우선순위 결정"""
        high_priority_keywords = ['must', 'shall', 'critical', 'essential']
        medium_priority_keywords = ['should', 'important', 'recommended']
        
        req_lower = requirement.lower()
        
        if any(keyword in req_lower for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in req_lower for keyword in medium_priority_keywords):
            return 'medium'
        else:
            return 'low'

    def _determine_nfr_priority(self, category: str) -> str:
        """비기능 요구사항 우선순위"""
        priority_map = {
            'security': 'high',
            'performance': 'high',
            'reliability': 'high',
            'scalability': 'medium',
            'usability': 'medium',
            'maintainability': 'low'
        }
        return priority_map.get(category, 'medium')

    def _generate_acceptance_criteria(self, requirement: str) -> List[str]:
        """수용 기준 생성"""
        criteria = []
        
        if 'login' in requirement.lower():
            criteria = [
                "User can enter valid credentials",
                "System validates credentials",
                "User is redirected to dashboard on success",
                "Error message shown for invalid credentials"
            ]
        elif 'create' in requirement.lower():
            criteria = [
                "User can input required information",
                "System validates input data",
                "New record is saved successfully",
                "Confirmation message is displayed"
            ]
        else:
            criteria = [
                f"System successfully implements {requirement}",
                "User can verify the functionality works",
                "No errors occur during normal operation"
            ]
        
        return criteria