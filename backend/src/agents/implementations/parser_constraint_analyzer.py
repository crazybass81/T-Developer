# backend/src/agents/implementations/parser_constraint_analyzer.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from datetime import datetime, timedelta

@dataclass
class Constraint:
    id: str
    type: str  # 'technical', 'business', 'regulatory', 'resource', 'time'
    category: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    impact: List[str]
    mitigation_strategies: List[str]
    validation_criteria: List[str]

@dataclass
class ResourceConstraint:
    resource_type: str  # 'budget', 'time', 'personnel', 'hardware', 'software'
    limit: Optional[str]
    unit: Optional[str]
    description: str
    flexibility: str  # 'fixed', 'flexible', 'negotiable'

@dataclass
class ComplianceRequirement:
    standard: str  # 'GDPR', 'HIPAA', 'PCI-DSS', 'SOX', 'ISO27001'
    requirements: List[str]
    verification_methods: List[str]
    documentation_needed: List[str]

@dataclass
class ConstraintAnalysis:
    technical_constraints: List[Constraint]
    business_constraints: List[Constraint]
    regulatory_constraints: List[Constraint]
    resource_constraints: List[ResourceConstraint]
    compliance_requirements: List[ComplianceRequirement]
    risk_assessment: Dict[str, Any]

class ConstraintAnalyzer:
    """제약사항 분석기"""

    def __init__(self):
        self.constraint_patterns = {
            'technical': {
                'performance': [
                    r'must\s+(?:respond|load|process)\s+within\s+(\d+)\s*(ms|milliseconds|seconds)',
                    r'(?:response\s+time|latency)\s+(?:must|should)\s+(?:be\s+)?(?:less\s+than|under|below)\s+(\d+)\s*(ms|seconds)',
                    r'(?:handle|support)\s+(?:up\s+to\s+)?(\d+[,\d]*)\s*(?:concurrent\s+)?(?:users|requests|connections)'
                ],
                'scalability': [
                    r'must\s+scale\s+to\s+(\d+[,\d]*)\s*(?:users|requests|transactions)',
                    r'(?:horizontal|vertical)\s+scaling\s+(?:required|needed|must)',
                    r'auto.?scaling\s+(?:required|needed|must)'
                ],
                'compatibility': [
                    r'must\s+(?:support|be\s+compatible\s+with)\s+([^.]+)',
                    r'(?:browser|device|platform)\s+compatibility\s+(?:required|needed)',
                    r'(?:backward|forward)\s+compatibility\s+(?:required|needed)'
                ],
                'security': [
                    r'must\s+(?:encrypt|secure|protect)\s+([^.]+)',
                    r'(?:ssl|tls|https)\s+(?:required|mandatory|must)',
                    r'(?:authentication|authorization)\s+(?:required|mandatory|must)'
                ]
            },
            'business': {
                'budget': [
                    r'budget\s+(?:limit|constraint|cap)\s+(?:of\s+)?[\$€£]?(\d+[,\d]*)',
                    r'cost\s+(?:must\s+)?(?:not\s+exceed|be\s+under|be\s+less\s+than)\s+[\$€£]?(\d+[,\d]*)',
                    r'maximum\s+(?:budget|cost|expense)\s+[\$€£]?(\d+[,\d]*)'
                ],
                'timeline': [
                    r'must\s+be\s+(?:completed|delivered|ready)\s+(?:by|within)\s+([^.]+)',
                    r'deadline\s+(?:is|of)\s+([^.]+)',
                    r'(?:launch|go.?live|release)\s+date\s+(?:is|of)\s+([^.]+)'
                ],
                'scope': [
                    r'(?:scope|feature)\s+(?:limited\s+to|restricted\s+to|must\s+include)\s+([^.]+)',
                    r'(?:must\s+not|cannot|should\s+not)\s+include\s+([^.]+)',
                    r'(?:out\s+of\s+scope|excluded)\s*:\s*([^.]+)'
                ]
            },
            'regulatory': {
                'compliance': [
                    r'\b(GDPR|HIPAA|PCI.?DSS|SOX|ISO\s*27001|CCPA|FERPA)\b',
                    r'(?:compliance|compliant)\s+with\s+([^.]+)',
                    r'(?:regulatory|legal)\s+(?:requirement|constraint|compliance)'
                ],
                'data_protection': [
                    r'(?:data\s+protection|privacy)\s+(?:required|mandatory|must)',
                    r'(?:personal\s+data|pii)\s+(?:protection|encryption|anonymization)',
                    r'(?:right\s+to\s+be\s+forgotten|data\s+deletion)\s+(?:required|must)'
                ],
                'audit': [
                    r'(?:audit\s+trail|audit\s+log)\s+(?:required|mandatory|must)',
                    r'(?:compliance\s+reporting|regulatory\s+reporting)\s+(?:required|needed)',
                    r'(?:documentation|record\s+keeping)\s+(?:required|mandatory)'
                ]
            },
            'resource': {
                'personnel': [
                    r'(?:team\s+size|staff|personnel)\s+(?:limited\s+to|maximum\s+of)\s+(\d+)',
                    r'(?:developer|engineer|designer)\s+(?:availability|constraint|limitation)',
                    r'(?:skill\s+set|expertise)\s+(?:limited\s+to|available\s+in)\s+([^.]+)'
                ],
                'infrastructure': [
                    r'(?:server|hardware|infrastructure)\s+(?:limitation|constraint|restriction)',
                    r'(?:cloud|hosting)\s+(?:budget|limit|constraint)',
                    r'(?:bandwidth|storage|memory)\s+(?:limited\s+to|maximum\s+of)\s+([^.]+)'
                ],
                'technology': [
                    r'(?:must\s+use|limited\s+to|restricted\s+to)\s+([^.]+)(?:\s+technology|\s+stack|\s+framework)',
                    r'(?:cannot\s+use|prohibited|not\s+allowed)\s+([^.]+)',
                    r'(?:legacy\s+system|existing\s+system)\s+(?:constraint|integration\s+required)'
                ]
            }
        }

    async def analyze_constraints(
        self,
        requirements: List[Dict[str, Any]]
    ) -> ConstraintAnalysis:
        """제약사항 분석"""
        
        technical_constraints = []
        business_constraints = []
        regulatory_constraints = []
        resource_constraints = []
        compliance_requirements = []
        
        for req in requirements:
            description = req.get('description', '')
            
            # 기술적 제약사항
            tech_constraints = self._extract_technical_constraints(description)
            technical_constraints.extend(tech_constraints)
            
            # 비즈니스 제약사항
            biz_constraints = self._extract_business_constraints(description)
            business_constraints.extend(biz_constraints)
            
            # 규제 제약사항
            reg_constraints = self._extract_regulatory_constraints(description)
            regulatory_constraints.extend(reg_constraints)
            
            # 리소스 제약사항
            res_constraints = self._extract_resource_constraints(description)
            resource_constraints.extend(res_constraints)
            
            # 컴플라이언스 요구사항
            comp_reqs = self._extract_compliance_requirements(description)
            compliance_requirements.extend(comp_reqs)
        
        # 중복 제거
        unique_technical = self._deduplicate_constraints(technical_constraints)
        unique_business = self._deduplicate_constraints(business_constraints)
        unique_regulatory = self._deduplicate_constraints(regulatory_constraints)
        unique_resource = self._deduplicate_resource_constraints(resource_constraints)
        unique_compliance = self._deduplicate_compliance_requirements(compliance_requirements)
        
        # 위험 평가
        risk_assessment = self._assess_risks(
            unique_technical + unique_business + unique_regulatory
        )
        
        return ConstraintAnalysis(
            technical_constraints=unique_technical,
            business_constraints=unique_business,
            regulatory_constraints=unique_regulatory,
            resource_constraints=unique_resource,
            compliance_requirements=unique_compliance,
            risk_assessment=risk_assessment
        )

    def _extract_technical_constraints(self, text: str) -> List[Constraint]:
        """기술적 제약사항 추출"""
        constraints = []
        
        for category, patterns in self.constraint_patterns['technical'].items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # 제약사항 생성
                    constraint = self._create_technical_constraint(
                        category,
                        match,
                        text
                    )
                    if constraint:
                        constraints.append(constraint)
        
        return constraints

    def _create_technical_constraint(
        self,
        category: str,
        match: re.Match,
        context: str
    ) -> Optional[Constraint]:
        """기술적 제약사항 생성"""
        
        constraint_id = f"TECH_{category.upper()}_{len(match.groups())}"
        description = match.group(0)
        
        # 심각도 결정
        severity = self._determine_severity(description, 'technical')
        
        # 영향 분석
        impact = self._analyze_impact(description, category, 'technical')
        
        # 완화 전략
        mitigation = self._generate_mitigation_strategies(category, 'technical')
        
        # 검증 기준
        validation = self._generate_validation_criteria(category, 'technical')
        
        return Constraint(
            id=constraint_id,
            type='technical',
            category=category,
            description=description,
            severity=severity,
            impact=impact,
            mitigation_strategies=mitigation,
            validation_criteria=validation
        )

    def _extract_business_constraints(self, text: str) -> List[Constraint]:
        """비즈니스 제약사항 추출"""
        constraints = []
        
        for category, patterns in self.constraint_patterns['business'].items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    constraint = self._create_business_constraint(
                        category,
                        match,
                        text
                    )
                    if constraint:
                        constraints.append(constraint)
        
        return constraints

    def _create_business_constraint(
        self,
        category: str,
        match: re.Match,
        context: str
    ) -> Optional[Constraint]:
        """비즈니스 제약사항 생성"""
        
        constraint_id = f"BIZ_{category.upper()}_{hash(match.group(0)) % 1000}"
        description = match.group(0)
        
        # 심각도 결정
        severity = self._determine_severity(description, 'business')
        
        # 영향 분석
        impact = self._analyze_impact(description, category, 'business')
        
        # 완화 전략
        mitigation = self._generate_mitigation_strategies(category, 'business')
        
        # 검증 기준
        validation = self._generate_validation_criteria(category, 'business')
        
        return Constraint(
            id=constraint_id,
            type='business',
            category=category,
            description=description,
            severity=severity,
            impact=impact,
            mitigation_strategies=mitigation,
            validation_criteria=validation
        )

    def _extract_regulatory_constraints(self, text: str) -> List[Constraint]:
        """규제 제약사항 추출"""
        constraints = []
        
        for category, patterns in self.constraint_patterns['regulatory'].items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    constraint = self._create_regulatory_constraint(
                        category,
                        match,
                        text
                    )
                    if constraint:
                        constraints.append(constraint)
        
        return constraints

    def _create_regulatory_constraint(
        self,
        category: str,
        match: re.Match,
        context: str
    ) -> Optional[Constraint]:
        """규제 제약사항 생성"""
        
        constraint_id = f"REG_{category.upper()}_{hash(match.group(0)) % 1000}"
        description = match.group(0)
        
        # 규제 제약사항은 일반적으로 높은 심각도
        severity = 'high' if category == 'compliance' else 'medium'
        
        # 영향 분석
        impact = self._analyze_impact(description, category, 'regulatory')
        
        # 완화 전략
        mitigation = self._generate_mitigation_strategies(category, 'regulatory')
        
        # 검증 기준
        validation = self._generate_validation_criteria(category, 'regulatory')
        
        return Constraint(
            id=constraint_id,
            type='regulatory',
            category=category,
            description=description,
            severity=severity,
            impact=impact,
            mitigation_strategies=mitigation,
            validation_criteria=validation
        )

    def _extract_resource_constraints(self, text: str) -> List[ResourceConstraint]:
        """리소스 제약사항 추출"""
        constraints = []
        
        for resource_type, patterns in self.constraint_patterns['resource'].items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    constraint = self._create_resource_constraint(
                        resource_type,
                        match,
                        text
                    )
                    if constraint:
                        constraints.append(constraint)
        
        return constraints

    def _create_resource_constraint(
        self,
        resource_type: str,
        match: re.Match,
        context: str
    ) -> Optional[ResourceConstraint]:
        """리소스 제약사항 생성"""
        
        description = match.group(0)
        
        # 제한값과 단위 추출
        limit, unit = self._extract_limit_and_unit(match)
        
        # 유연성 결정
        flexibility = self._determine_flexibility(description)
        
        return ResourceConstraint(
            resource_type=resource_type,
            limit=limit,
            unit=unit,
            description=description,
            flexibility=flexibility
        )

    def _extract_compliance_requirements(self, text: str) -> List[ComplianceRequirement]:
        """컴플라이언스 요구사항 추출"""
        requirements = []
        
        # 컴플라이언스 표준 감지
        compliance_standards = {
            'GDPR': [
                'Data protection by design',
                'Right to be forgotten',
                'Data portability',
                'Consent management',
                'Data breach notification'
            ],
            'HIPAA': [
                'PHI encryption',
                'Access controls',
                'Audit logs',
                'Business associate agreements',
                'Risk assessments'
            ],
            'PCI-DSS': [
                'Cardholder data protection',
                'Secure network architecture',
                'Strong access controls',
                'Regular monitoring',
                'Vulnerability management'
            ],
            'SOX': [
                'Financial reporting controls',
                'Audit trails',
                'Change management',
                'Access controls',
                'Documentation requirements'
            ]
        }
        
        for standard, reqs in compliance_standards.items():
            if re.search(rf'\b{standard}\b', text, re.IGNORECASE):
                # 검증 방법 생성
                verification_methods = self._generate_verification_methods(standard)
                
                # 필요 문서 생성
                documentation = self._generate_documentation_requirements(standard)
                
                requirement = ComplianceRequirement(
                    standard=standard,
                    requirements=reqs,
                    verification_methods=verification_methods,
                    documentation_needed=documentation
                )
                requirements.append(requirement)
        
        return requirements

    def _determine_severity(self, description: str, constraint_type: str) -> str:
        """심각도 결정"""
        description_lower = description.lower()
        
        # 키워드 기반 심각도 결정
        if any(keyword in description_lower for keyword in ['critical', 'must', 'mandatory', 'required']):
            return 'critical'
        elif any(keyword in description_lower for keyword in ['important', 'should', 'necessary']):
            return 'high'
        elif any(keyword in description_lower for keyword in ['preferred', 'recommended', 'desired']):
            return 'medium'
        else:
            return 'low'

    def _analyze_impact(self, description: str, category: str, constraint_type: str) -> List[str]:
        """영향 분석"""
        impact = []
        
        # 카테고리별 일반적인 영향
        impact_mapping = {
            'performance': ['user_experience', 'system_scalability', 'resource_usage'],
            'security': ['data_protection', 'compliance', 'user_trust'],
            'budget': ['project_scope', 'timeline', 'resource_allocation'],
            'timeline': ['project_delivery', 'market_opportunity', 'stakeholder_satisfaction'],
            'compliance': ['legal_risk', 'business_continuity', 'reputation']
        }
        
        if category in impact_mapping:
            impact.extend(impact_mapping[category])
        
        # 설명에서 추가 영향 추출
        if 'user' in description.lower():
            impact.append('user_experience')
        if 'cost' in description.lower() or 'budget' in description.lower():
            impact.append('financial_impact')
        if 'time' in description.lower() or 'deadline' in description.lower():
            impact.append('schedule_impact')
        
        return list(set(impact))

    def _generate_mitigation_strategies(self, category: str, constraint_type: str) -> List[str]:
        """완화 전략 생성"""
        strategies = []
        
        strategy_mapping = {
            ('performance', 'technical'): [
                'Implement caching mechanisms',
                'Optimize database queries',
                'Use CDN for static content',
                'Implement load balancing'
            ],
            ('security', 'technical'): [
                'Implement encryption at rest and in transit',
                'Use multi-factor authentication',
                'Regular security audits',
                'Implement access controls'
            ],
            ('budget', 'business'): [
                'Prioritize features by business value',
                'Consider phased implementation',
                'Explore open-source alternatives',
                'Negotiate with vendors'
            ],
            ('timeline', 'business'): [
                'Implement agile development methodology',
                'Parallel development streams',
                'MVP approach',
                'Resource augmentation'
            ],
            ('compliance', 'regulatory'): [
                'Engage compliance experts',
                'Implement compliance by design',
                'Regular compliance audits',
                'Staff training on regulations'
            ]
        }
        
        key = (category, constraint_type)
        if key in strategy_mapping:
            strategies.extend(strategy_mapping[key])
        
        return strategies

    def _generate_validation_criteria(self, category: str, constraint_type: str) -> List[str]:
        """검증 기준 생성"""
        criteria = []
        
        criteria_mapping = {
            ('performance', 'technical'): [
                'Load testing results meet requirements',
                'Response time measurements under threshold',
                'Scalability testing passes',
                'Performance monitoring in place'
            ],
            ('security', 'technical'): [
                'Security audit passes',
                'Penetration testing results acceptable',
                'Encryption implementation verified',
                'Access controls tested'
            ],
            ('budget', 'business'): [
                'Total cost within approved budget',
                'Cost tracking and reporting in place',
                'Budget variance analysis completed',
                'ROI calculations validated'
            ],
            ('compliance', 'regulatory'): [
                'Compliance audit passes',
                'Required documentation complete',
                'Staff training completed',
                'Monitoring systems operational'
            ]
        }
        
        key = (category, constraint_type)
        if key in criteria_mapping:
            criteria.extend(criteria_mapping[key])
        
        return criteria

    def _extract_limit_and_unit(self, match: re.Match) -> tuple[Optional[str], Optional[str]]:
        """제한값과 단위 추출"""
        groups = match.groups()
        
        if groups:
            # 숫자 추출
            for group in groups:
                if group and re.match(r'\d+[,\d]*', group):
                    limit = group.replace(',', '')
                    
                    # 단위 추출
                    full_match = match.group(0).lower()
                    if 'ms' in full_match or 'millisecond' in full_match:
                        unit = 'milliseconds'
                    elif 'second' in full_match:
                        unit = 'seconds'
                    elif 'user' in full_match:
                        unit = 'users'
                    elif 'request' in full_match:
                        unit = 'requests'
                    elif '$' in full_match or 'dollar' in full_match:
                        unit = 'dollars'
                    elif '€' in full_match or 'euro' in full_match:
                        unit = 'euros'
                    else:
                        unit = 'units'
                    
                    return limit, unit
        
        return None, None

    def _determine_flexibility(self, description: str) -> str:
        """유연성 결정"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['must', 'mandatory', 'required', 'fixed']):
            return 'fixed'
        elif any(keyword in description_lower for keyword in ['negotiable', 'flexible', 'adjustable']):
            return 'negotiable'
        else:
            return 'flexible'

    def _generate_verification_methods(self, standard: str) -> List[str]:
        """검증 방법 생성"""
        methods = {
            'GDPR': [
                'Data protection impact assessment',
                'Privacy audit',
                'Consent mechanism testing',
                'Data subject rights verification'
            ],
            'HIPAA': [
                'Security risk assessment',
                'PHI access audit',
                'Encryption verification',
                'Business associate agreement review'
            ],
            'PCI-DSS': [
                'Quarterly security scan',
                'Annual penetration testing',
                'Cardholder data discovery',
                'Network segmentation testing'
            ],
            'SOX': [
                'Internal controls testing',
                'Financial reporting audit',
                'IT general controls review',
                'Change management audit'
            ]
        }
        
        return methods.get(standard, ['Compliance audit', 'Documentation review'])

    def _generate_documentation_requirements(self, standard: str) -> List[str]:
        """문서 요구사항 생성"""
        docs = {
            'GDPR': [
                'Privacy policy',
                'Data processing records',
                'Consent forms',
                'Data breach procedures',
                'Privacy impact assessments'
            ],
            'HIPAA': [
                'Security policies',
                'Risk assessment documentation',
                'Business associate agreements',
                'Incident response procedures',
                'Training records'
            ],
            'PCI-DSS': [
                'Security policies',
                'Network diagrams',
                'Vulnerability scan reports',
                'Penetration test reports',
                'Change control procedures'
            ],
            'SOX': [
                'Internal control documentation',
                'Process flowcharts',
                'Risk assessments',
                'Testing procedures',
                'Remediation plans'
            ]
        }
        
        return docs.get(standard, ['Compliance documentation', 'Audit reports'])

    def _assess_risks(self, constraints: List[Constraint]) -> Dict[str, Any]:
        """위험 평가"""
        risk_assessment = {
            'overall_risk_level': 'medium',
            'critical_constraints': 0,
            'high_risk_areas': [],
            'mitigation_priority': [],
            'risk_factors': {}
        }
        
        # 심각도별 카운트
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for constraint in constraints:
            severity_counts[constraint.severity] += 1
            
            if constraint.severity == 'critical':
                risk_assessment['critical_constraints'] += 1
                risk_assessment['mitigation_priority'].append(constraint.id)
        
        # 전체 위험 수준 결정
        if severity_counts['critical'] > 0:
            risk_assessment['overall_risk_level'] = 'critical'
        elif severity_counts['high'] > 2:
            risk_assessment['overall_risk_level'] = 'high'
        elif severity_counts['medium'] > 5:
            risk_assessment['overall_risk_level'] = 'medium'
        else:
            risk_assessment['overall_risk_level'] = 'low'
        
        # 고위험 영역 식별
        constraint_types = {}
        for constraint in constraints:
            if constraint.type not in constraint_types:
                constraint_types[constraint.type] = []
            constraint_types[constraint.type].append(constraint.severity)
        
        for constraint_type, severities in constraint_types.items():
            if 'critical' in severities or severities.count('high') > 1:
                risk_assessment['high_risk_areas'].append(constraint_type)
        
        risk_assessment['risk_factors'] = severity_counts
        
        return risk_assessment

    def _deduplicate_constraints(self, constraints: List[Constraint]) -> List[Constraint]:
        """중복 제약사항 제거"""
        unique_constraints = {}
        
        for constraint in constraints:
            key = f"{constraint.type}_{constraint.category}_{hash(constraint.description) % 1000}"
            if key not in unique_constraints:
                unique_constraints[key] = constraint
            else:
                # 더 높은 심각도로 업데이트
                existing = unique_constraints[key]
                severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                if severity_order[constraint.severity] > severity_order[existing.severity]:
                    unique_constraints[key] = constraint
        
        return list(unique_constraints.values())

    def _deduplicate_resource_constraints(self, constraints: List[ResourceConstraint]) -> List[ResourceConstraint]:
        """중복 리소스 제약사항 제거"""
        unique_constraints = {}
        
        for constraint in constraints:
            key = f"{constraint.resource_type}_{constraint.description}"
            if key not in unique_constraints:
                unique_constraints[key] = constraint
        
        return list(unique_constraints.values())

    def _deduplicate_compliance_requirements(self, requirements: List[ComplianceRequirement]) -> List[ComplianceRequirement]:
        """중복 컴플라이언스 요구사항 제거"""
        unique_requirements = {}
        
        for requirement in requirements:
            if requirement.standard not in unique_requirements:
                unique_requirements[requirement.standard] = requirement
        
        return list(unique_requirements.values())