"""
Parser Agent - Requirement Separator Implementation
SubTask 4.22.1: 기능/비기능 요구사항 분리기 완성
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime

@dataclass
class ParsedRequirement:
    id: str
    type: str
    category: str
    description: str
    priority: str
    dependencies: List[str]
    acceptance_criteria: List[str]
    technical_details: Dict[str, Any]
    metadata: Dict[str, Any]

class RequirementSeparator:
    """기능/비기능 요구사항 분리기"""

    def __init__(self):
        # 비기능 요구사항 패턴
        self.nfr_patterns = {
            'performance': [
                r'(response time|latency|throughput|speed|performance)',
                r'within\s+\d+\s*(ms|milliseconds|seconds)',
                r'(handle|support)\s+\d+\s*(users|requests|transactions)',
                r'(fast|quick|rapid|efficient|optimize)'
            ],
            'security': [
                r'(secure|security|encrypt|authentication|authorization)',
                r'(protect|safeguard|defend|shield)',
                r'(compliance|compliant|conform|adhere)',
                r'(vulnerability|threat|risk|attack)'
            ],
            'scalability': [
                r'(scale|scalable|scalability|elastic)',
                r'(grow|expand|extend|increase)',
                r'(concurrent|simultaneous|parallel)',
                r'(distributed|cluster|load balance)'
            ],
            'reliability': [
                r'(reliable|reliability|availability|uptime)',
                r'(fault tolerant|failover|redundancy|backup)',
                r'(recover|recovery|resilient|robust)',
                r'\d+(\.\d+)?%\s*(uptime|availability|SLA)'
            ],
            'usability': [
                r'(user friendly|easy to use|intuitive|simple)',
                r'(accessibility|accessible|WCAG|ADA)',
                r'(responsive|mobile|cross-platform)',
                r'(user experience|UX|user interface|UI)'
            ],
            'maintainability': [
                r'(maintainable|maintainability|modular|extensible)',
                r'(documented|documentation|readable|clean code)',
                r'(testable|test coverage|unit test)',
                r'(refactor|technical debt|code quality)'
            ]
        }

        # 기능 요구사항 패턴
        self.fr_patterns = [
            r'(user|system|application)\s+(shall|must|should|can|will)\s+',
            r'(feature|function|capability|ability)\s+',
            r'(create|read|update|delete|manage|process)',
            r'(display|show|present|render|visualize)',
            r'(calculate|compute|generate|produce|transform)'
        ]
        
        self.req_counter = {'FR': 0, 'NFR': 0, 'TR': 0, 'BR': 0}

    async def separate_requirements(
        self,
        requirements: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ParsedRequirement], List[ParsedRequirement]]:
        """요구사항을 기능/비기능으로 분리"""

        functional_reqs = []
        non_functional_reqs = []

        for req_text in requirements:
            # 요구사항 타입 결정
            req_type = await self._determine_requirement_type(req_text)

            # 세부 분석
            if req_type == 'functional':
                parsed_req = await self._parse_functional_requirement(req_text)
                functional_reqs.append(parsed_req)
            else:
                parsed_req = await self._parse_non_functional_requirement(
                    req_text,
                    req_type
                )
                non_functional_reqs.append(parsed_req)

        # 교차 검증
        validated_functional, validated_non_functional = await self._cross_validate(
            functional_reqs,
            non_functional_reqs
        )

        return validated_functional, validated_non_functional

    async def _determine_requirement_type(self, text: str) -> str:
        """요구사항 타입 결정"""
        text_lower = text.lower()

        # NFR 점수 계산
        nfr_scores = {}
        for category, patterns in self.nfr_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            nfr_scores[category] = score

        # FR 점수 계산
        fr_score = 0
        for pattern in self.fr_patterns:
            if re.search(pattern, text_lower):
                fr_score += 1

        # 최고 NFR 점수
        max_nfr_category = max(nfr_scores, key=nfr_scores.get)
        max_nfr_score = nfr_scores[max_nfr_category]

        # 타입 결정
        if max_nfr_score > fr_score and max_nfr_score > 0:
            return max_nfr_category  # NFR 카테고리 반환
        else:
            return 'functional'

    async def _parse_functional_requirement(self, text: str) -> ParsedRequirement:
        """기능 요구사항 파싱"""
        
        # 액터 추출
        actor = self._extract_actor(text)
        
        # 동작 추출
        action = self._extract_action(text)
        
        # 객체 추출
        object_info = self._extract_object(text)
        
        # 조건 추출
        conditions = self._extract_conditions(text)
        
        # 수용 기준 생성
        acceptance_criteria = self._generate_acceptance_criteria(
            actor, action, object_info, conditions
        )
        
        return ParsedRequirement(
            id=self._generate_id('FR'),
            type='functional',
            category=self._categorize_functional_req(text),
            description=text,
            priority=self._determine_priority(text),
            dependencies=[],
            acceptance_criteria=acceptance_criteria,
            technical_details={
                'actor': actor,
                'action': action,
                'object': object_info,
                'conditions': conditions
            },
            metadata={
                'parsed_at': datetime.utcnow().isoformat(),
                'source': 'requirement_separator'
            }
        )

    async def _parse_non_functional_requirement(self, text: str, category: str) -> ParsedRequirement:
        """비기능 요구사항 파싱"""
        
        # 메트릭 추출
        metrics = self._extract_metrics(text, category)
        
        # 제약사항 추출
        constraints = self._extract_constraints(text)
        
        return ParsedRequirement(
            id=self._generate_id('NFR'),
            type='non_functional',
            category=category,
            description=text,
            priority=self._determine_priority(text),
            dependencies=[],
            acceptance_criteria=self._generate_nfr_acceptance_criteria(text, category),
            technical_details={
                'metrics': metrics,
                'constraints': constraints,
                'measurement_method': self._suggest_measurement_method(category)
            },
            metadata={
                'parsed_at': datetime.utcnow().isoformat(),
                'nfr_category': category
            }
        )

    def _extract_actor(self, text: str) -> str:
        """액터 추출"""
        actors = ['user', 'admin', 'system', 'application', 'service', 'customer']
        text_lower = text.lower()
        
        for actor in actors:
            if actor in text_lower:
                return actor
        return 'user'  # 기본값

    def _extract_action(self, text: str) -> str:
        """동작 추출"""
        actions = ['create', 'read', 'update', 'delete', 'login', 'logout', 'search', 'view', 'manage']
        text_lower = text.lower()
        
        for action in actions:
            if action in text_lower:
                return action
        
        # 동사 패턴 매칭
        verb_match = re.search(r'\b(\w+)\b', text_lower)
        if verb_match:
            return verb_match.group(1)
        
        return 'perform'  # 기본값

    def _extract_object(self, text: str) -> str:
        """객체 추출"""
        objects = ['data', 'information', 'record', 'file', 'document', 'account', 'profile']
        text_lower = text.lower()
        
        for obj in objects:
            if obj in text_lower:
                return obj
        return 'item'  # 기본값

    def _extract_conditions(self, text: str) -> List[str]:
        """조건 추출"""
        conditions = []
        
        # 조건 패턴
        condition_patterns = [
            r'if\s+([^,\.]+)',
            r'when\s+([^,\.]+)',
            r'provided\s+([^,\.]+)',
            r'given\s+([^,\.]+)'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend(matches)
        
        return conditions

    def _generate_acceptance_criteria(self, actor: str, action: str, obj: str, conditions: List[str]) -> List[str]:
        """수용 기준 생성"""
        criteria = []
        
        # 기본 수용 기준
        criteria.append(f"Given {actor} wants to {action} {obj}, when they perform the action, then it should succeed")
        
        # 조건별 수용 기준
        for condition in conditions:
            criteria.append(f"Given {condition}, the {action} should work correctly")
        
        # 에러 처리
        criteria.append(f"When {action} fails, appropriate error message should be displayed")
        
        return criteria

    def _generate_nfr_acceptance_criteria(self, text: str, category: str) -> List[str]:
        """비기능 요구사항 수용 기준 생성"""
        criteria = []
        
        if category == 'performance':
            criteria.append("Response time should meet specified requirements")
            criteria.append("System should handle specified load without degradation")
        elif category == 'security':
            criteria.append("Security measures should be properly implemented")
            criteria.append("Unauthorized access should be prevented")
        elif category == 'scalability':
            criteria.append("System should scale according to requirements")
            criteria.append("Performance should remain acceptable under increased load")
        
        return criteria

    def _extract_metrics(self, text: str, category: str) -> Dict[str, Any]:
        """메트릭 추출"""
        metrics = {}
        
        if category == 'performance':
            # 응답 시간 추출
            time_match = re.search(r'(\d+)\s*(ms|milliseconds|seconds?)', text, re.IGNORECASE)
            if time_match:
                metrics['response_time'] = {
                    'value': int(time_match.group(1)),
                    'unit': time_match.group(2)
                }
            
            # 사용자 수 추출
            user_match = re.search(r'(\d+)\s*(users?|concurrent)', text, re.IGNORECASE)
            if user_match:
                metrics['concurrent_users'] = int(user_match.group(1))
        
        elif category == 'reliability':
            # 가용성 추출
            availability_match = re.search(r'(\d+(?:\.\d+)?)%\s*(uptime|availability)', text, re.IGNORECASE)
            if availability_match:
                metrics['availability'] = float(availability_match.group(1))
        
        return metrics

    def _extract_constraints(self, text: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        
        constraint_patterns = [
            r'must not\s+([^,\.]+)',
            r'cannot\s+([^,\.]+)',
            r'limited to\s+([^,\.]+)',
            r'restricted to\s+([^,\.]+)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            constraints.extend(matches)
        
        return constraints

    def _categorize_functional_req(self, text: str) -> str:
        """기능 요구사항 분류"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['auth', 'login', 'signin']):
            return 'authentication'
        elif any(word in text_lower for word in ['user', 'profile', 'account']):
            return 'user_management'
        elif any(word in text_lower for word in ['data', 'crud', 'database']):
            return 'data_management'
        elif any(word in text_lower for word in ['search', 'find', 'query']):
            return 'search'
        elif any(word in text_lower for word in ['report', 'analytics', 'dashboard']):
            return 'reporting'
        else:
            return 'general'

    def _determine_priority(self, text: str) -> str:
        """우선순위 결정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'essential', 'must']):
            return 'critical'
        elif any(word in text_lower for word in ['important', 'should', 'required']):
            return 'high'
        elif any(word in text_lower for word in ['nice', 'could', 'optional']):
            return 'low'
        else:
            return 'medium'

    def _suggest_measurement_method(self, category: str) -> str:
        """측정 방법 제안"""
        methods = {
            'performance': 'Load testing with monitoring tools',
            'security': 'Security audit and penetration testing',
            'scalability': 'Stress testing with increasing load',
            'reliability': 'Uptime monitoring and failure analysis',
            'usability': 'User testing and usability studies',
            'maintainability': 'Code quality metrics and review'
        }
        return methods.get(category, 'Manual verification')

    def _generate_id(self, prefix: str) -> str:
        """ID 생성"""
        self.req_counter[prefix] += 1
        return f"{prefix}-{self.req_counter[prefix]:03d}"

    async def _cross_validate(self, functional_reqs: List[ParsedRequirement], 
                            non_functional_reqs: List[ParsedRequirement]) -> Tuple[List[ParsedRequirement], List[ParsedRequirement]]:
        """교차 검증"""
        # 간단한 검증 - 실제로는 더 복잡한 로직 필요
        validated_functional = [req for req in functional_reqs if len(req.description) > 10]
        validated_non_functional = [req for req in non_functional_reqs if len(req.description) > 10]
        
        return validated_functional, validated_non_functional