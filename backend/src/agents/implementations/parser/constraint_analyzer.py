from typing import Dict, List, Any
import re
from ..parser_agent import RequirementType, ParsedRequirement
from datetime import datetime

class ConstraintAnalyzer:
    """제약사항 분석기"""

    def __init__(self):
        self.constraint_patterns = self._load_constraint_patterns()
        self.constraint_types = self._load_constraint_types()

    def _load_constraint_patterns(self) -> Dict[str, List[str]]:
        """제약사항 패턴 로드"""
        return {
            'technical': [
                r'must\s+use\s+(.+)',
                r'required\s+to\s+use\s+(.+)',
                r'technology\s+constraint:?\s*(.+)',
                r'platform\s+must\s+be\s+(.+)',
                r'database\s+must\s+be\s+(.+)'
            ],
            'performance': [
                r'response\s+time\s+must\s+not\s+exceed\s+(.+)',
                r'maximum\s+(.+)\s+users?',
                r'load\s+time\s+under\s+(.+)',
                r'throughput\s+at\s+least\s+(.+)'
            ],
            'security': [
                r'must\s+comply\s+with\s+(.+)',
                r'security\s+standard:?\s*(.+)',
                r'encryption\s+required\s+for\s+(.+)',
                r'authentication\s+must\s+use\s+(.+)'
            ],
            'business': [
                r'budget\s+constraint:?\s*(.+)',
                r'timeline:?\s*(.+)',
                r'deadline:?\s*(.+)',
                r'cost\s+must\s+not\s+exceed\s+(.+)'
            ],
            'regulatory': [
                r'must\s+comply\s+with\s+(gdpr|hipaa|pci|sox)',
                r'regulatory\s+requirement:?\s*(.+)',
                r'compliance\s+with\s+(.+)',
                r'legal\s+constraint:?\s*(.+)'
            ],
            'operational': [
                r'maintenance\s+window:?\s*(.+)',
                r'backup\s+frequency:?\s*(.+)',
                r'monitoring\s+requirement:?\s*(.+)',
                r'support\s+hours:?\s*(.+)'
            ]
        }

    def _load_constraint_types(self) -> Dict[str, Dict[str, Any]]:
        """제약사항 타입 정의"""
        return {
            'technical': {
                'priority': 'high',
                'impact': 'architecture',
                'flexibility': 'low'
            },
            'performance': {
                'priority': 'high',
                'impact': 'system_design',
                'flexibility': 'medium'
            },
            'security': {
                'priority': 'critical',
                'impact': 'all_layers',
                'flexibility': 'low'
            },
            'business': {
                'priority': 'high',
                'impact': 'scope',
                'flexibility': 'medium'
            },
            'regulatory': {
                'priority': 'critical',
                'impact': 'compliance',
                'flexibility': 'none'
            },
            'operational': {
                'priority': 'medium',
                'impact': 'deployment',
                'flexibility': 'high'
            }
        }

    async def analyze(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """제약사항 분석"""
        constraints = []
        text = str(base_structure)

        # 패턴 기반 제약사항 추출
        for constraint_type, patterns in self.constraint_patterns.items():
            type_constraints = self._extract_constraints_by_type(
                text, 
                constraint_type, 
                patterns
            )
            constraints.extend(type_constraints)

        # 암시적 제약사항 추론
        implicit_constraints = self._infer_implicit_constraints(base_structure)
        constraints.extend(implicit_constraints)

        # 제약사항 검증 및 정제
        validated_constraints = self._validate_constraints(constraints)

        return validated_constraints

    def _extract_constraints_by_type(
        self, 
        text: str, 
        constraint_type: str, 
        patterns: List[str]
    ) -> List[ParsedRequirement]:
        """타입별 제약사항 추출"""
        constraints = []
        type_config = self.constraint_types[constraint_type]

        for idx, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match_idx, match in enumerate(matches):
                constraint_id = f"CON-{constraint_type.upper()}-{idx+1:02d}-{match_idx+1:02d}"
                
                constraint = ParsedRequirement(
                    id=constraint_id,
                    type=RequirementType.CONSTRAINT,
                    category=constraint_type,
                    description=self._clean_constraint_description(match.group()),
                    priority=type_config['priority'],
                    technical_details={
                        'constraint_value': match.group(1) if len(match.groups()) > 0 else None,
                        'impact_area': type_config['impact'],
                        'flexibility': type_config['flexibility'],
                        'pattern_matched': pattern
                    },
                    metadata={
                        'extracted_at': datetime.utcnow().isoformat(),
                        'extraction_method': 'pattern_matching',
                        'confidence': self._calculate_confidence(match, pattern)
                    }
                )
                constraints.append(constraint)

        return constraints

    def _clean_constraint_description(self, raw_description: str) -> str:
        """제약사항 설명 정제"""
        # 불필요한 공백 제거
        cleaned = re.sub(r'\s+', ' ', raw_description.strip())
        
        # 첫 글자 대문자로
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # 마침표 추가
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
        
        return cleaned

    def _calculate_confidence(self, match, pattern: str) -> float:
        """신뢰도 계산"""
        # 패턴의 구체성에 따라 신뢰도 결정
        if 'must' in pattern.lower():
            return 0.9
        elif 'required' in pattern.lower():
            return 0.85
        elif 'should' in pattern.lower():
            return 0.7
        else:
            return 0.6

    def _infer_implicit_constraints(
        self, 
        base_structure: Dict[str, Any]
    ) -> List[ParsedRequirement]:
        """암시적 제약사항 추론"""
        constraints = []
        project_info = base_structure.get('project_info', {})
        
        # 프로젝트 타입에 따른 암시적 제약사항
        project_type = project_info.get('type', '').lower()
        
        if 'web' in project_type:
            constraints.extend(self._get_web_constraints())
        elif 'mobile' in project_type:
            constraints.extend(self._get_mobile_constraints())
        elif 'api' in project_type:
            constraints.extend(self._get_api_constraints())

        # 도메인별 제약사항
        domain_text = str(base_structure).lower()
        if 'healthcare' in domain_text or 'medical' in domain_text:
            constraints.extend(self._get_healthcare_constraints())
        elif 'finance' in domain_text or 'payment' in domain_text:
            constraints.extend(self._get_finance_constraints())
        elif 'education' in domain_text:
            constraints.extend(self._get_education_constraints())

        return constraints

    def _get_web_constraints(self) -> List[ParsedRequirement]:
        """웹 애플리케이션 제약사항"""
        return [
            ParsedRequirement(
                id="CON-WEB-001",
                type=RequirementType.CONSTRAINT,
                category='technical',
                description="Application must be responsive and work on different screen sizes.",
                priority='high',
                technical_details={
                    'constraint_type': 'responsive_design',
                    'impact_area': 'frontend'
                }
            ),
            ParsedRequirement(
                id="CON-WEB-002",
                type=RequirementType.CONSTRAINT,
                category='performance',
                description="Page load time should not exceed 3 seconds.",
                priority='high',
                technical_details={
                    'constraint_type': 'performance',
                    'metric': 'page_load_time',
                    'threshold': '3 seconds'
                }
            )
        ]

    def _get_mobile_constraints(self) -> List[ParsedRequirement]:
        """모바일 애플리케이션 제약사항"""
        return [
            ParsedRequirement(
                id="CON-MOB-001",
                type=RequirementType.CONSTRAINT,
                category='technical',
                description="Application must support iOS 12+ and Android 8+.",
                priority='high',
                technical_details={
                    'constraint_type': 'platform_compatibility',
                    'ios_version': '12+',
                    'android_version': '8+'
                }
            ),
            ParsedRequirement(
                id="CON-MOB-002",
                type=RequirementType.CONSTRAINT,
                category='performance',
                description="App size should not exceed 100MB.",
                priority='medium',
                technical_details={
                    'constraint_type': 'size_limit',
                    'max_size': '100MB'
                }
            )
        ]

    def _get_api_constraints(self) -> List[ParsedRequirement]:
        """API 제약사항"""
        return [
            ParsedRequirement(
                id="CON-API-001",
                type=RequirementType.CONSTRAINT,
                category='technical',
                description="API must follow RESTful design principles.",
                priority='high',
                technical_details={
                    'constraint_type': 'architectural_pattern',
                    'pattern': 'REST'
                }
            ),
            ParsedRequirement(
                id="CON-API-002",
                type=RequirementType.CONSTRAINT,
                category='security',
                description="All API endpoints must require authentication.",
                priority='critical',
                technical_details={
                    'constraint_type': 'security_requirement',
                    'requirement': 'authentication'
                }
            )
        ]

    def _get_healthcare_constraints(self) -> List[ParsedRequirement]:
        """헬스케어 도메인 제약사항"""
        return [
            ParsedRequirement(
                id="CON-HC-001",
                type=RequirementType.CONSTRAINT,
                category='regulatory',
                description="System must comply with HIPAA regulations.",
                priority='critical',
                technical_details={
                    'constraint_type': 'regulatory_compliance',
                    'regulation': 'HIPAA'
                }
            ),
            ParsedRequirement(
                id="CON-HC-002",
                type=RequirementType.CONSTRAINT,
                category='security',
                description="All patient data must be encrypted at rest and in transit.",
                priority='critical',
                technical_details={
                    'constraint_type': 'data_encryption',
                    'scope': 'patient_data'
                }
            )
        ]

    def _get_finance_constraints(self) -> List[ParsedRequirement]:
        """금융 도메인 제약사항"""
        return [
            ParsedRequirement(
                id="CON-FIN-001",
                type=RequirementType.CONSTRAINT,
                category='regulatory',
                description="System must comply with PCI DSS standards.",
                priority='critical',
                technical_details={
                    'constraint_type': 'regulatory_compliance',
                    'regulation': 'PCI_DSS'
                }
            ),
            ParsedRequirement(
                id="CON-FIN-002",
                type=RequirementType.CONSTRAINT,
                category='security',
                description="Financial transactions must use two-factor authentication.",
                priority='critical',
                technical_details={
                    'constraint_type': 'authentication_requirement',
                    'method': '2FA'
                }
            )
        ]

    def _get_education_constraints(self) -> List[ParsedRequirement]:
        """교육 도메인 제약사항"""
        return [
            ParsedRequirement(
                id="CON-EDU-001",
                type=RequirementType.CONSTRAINT,
                category='regulatory',
                description="System must comply with FERPA regulations for student data.",
                priority='high',
                technical_details={
                    'constraint_type': 'regulatory_compliance',
                    'regulation': 'FERPA'
                }
            ),
            ParsedRequirement(
                id="CON-EDU-002",
                type=RequirementType.CONSTRAINT,
                category='usability',
                description="Interface must be accessible according to WCAG 2.1 AA standards.",
                priority='high',
                technical_details={
                    'constraint_type': 'accessibility_requirement',
                    'standard': 'WCAG_2.1_AA'
                }
            )
        ]

    def _validate_constraints(
        self, 
        constraints: List[ParsedRequirement]
    ) -> List[ParsedRequirement]:
        """제약사항 검증"""
        validated = []
        
        for constraint in constraints:
            # 중복 제거
            if not self._is_duplicate(constraint, validated):
                # 충돌 검사
                conflicts = self._check_conflicts(constraint, validated)
                if conflicts:
                    constraint.metadata['conflicts'] = conflicts
                
                # 실현 가능성 검사
                feasibility = self._check_feasibility(constraint)
                constraint.metadata['feasibility'] = feasibility
                
                validated.append(constraint)
        
        return validated

    def _is_duplicate(
        self, 
        constraint: ParsedRequirement, 
        existing: List[ParsedRequirement]
    ) -> bool:
        """중복 제약사항 확인"""
        for existing_constraint in existing:
            if (constraint.category == existing_constraint.category and
                self._similarity_score(constraint.description, existing_constraint.description) > 0.8):
                return True
        return False

    def _similarity_score(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def _check_conflicts(
        self, 
        constraint: ParsedRequirement, 
        existing: List[ParsedRequirement]
    ) -> List[str]:
        """제약사항 충돌 검사"""
        conflicts = []
        
        # 기술적 충돌 검사
        if constraint.category == 'technical':
            for existing_constraint in existing:
                if existing_constraint.category == 'technical':
                    if self._has_technical_conflict(constraint, existing_constraint):
                        conflicts.append(existing_constraint.id)
        
        return conflicts

    def _has_technical_conflict(
        self, 
        constraint1: ParsedRequirement, 
        constraint2: ParsedRequirement
    ) -> bool:
        """기술적 충돌 확인"""
        # 간단한 충돌 검사 로직
        desc1 = constraint1.description.lower()
        desc2 = constraint2.description.lower()
        
        # 상반된 기술 요구사항 검사
        conflicts = [
            ('mysql', 'postgresql'),
            ('react', 'vue'),
            ('rest', 'graphql')
        ]
        
        for tech1, tech2 in conflicts:
            if tech1 in desc1 and tech2 in desc2:
                return True
            if tech2 in desc1 and tech1 in desc2:
                return True
        
        return False

    def _check_feasibility(self, constraint: ParsedRequirement) -> str:
        """실현 가능성 검사"""
        # 간단한 실현 가능성 평가
        if constraint.priority == 'critical':
            return 'high'
        elif constraint.category == 'regulatory':
            return 'high'
        elif 'must' in constraint.description.lower():
            return 'medium'
        else:
            return 'high'