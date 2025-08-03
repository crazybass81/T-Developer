# backend/src/agents/implementations/parser_requirement_separator.py
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
import asyncio

class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"

@dataclass
class ParsedRequirement:
    id: str
    type: RequirementType
    category: str
    description: str
    priority: str
    actor: Optional[str] = None
    action: Optional[str] = None
    object_info: Optional[str] = None
    conditions: List[str] = None
    acceptance_criteria: List[str] = None

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

        return functional_reqs, non_functional_reqs

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
            return max_nfr_category
        else:
            return 'functional'

    async def _parse_functional_requirement(
        self,
        text: str
    ) -> ParsedRequirement:
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
            type=RequirementType.FUNCTIONAL,
            category='functional',
            description=text,
            priority=self._extract_priority(text),
            actor=actor,
            action=action,
            object_info=object_info,
            conditions=conditions,
            acceptance_criteria=acceptance_criteria
        )

    async def _parse_non_functional_requirement(
        self,
        text: str,
        category: str
    ) -> ParsedRequirement:
        """비기능 요구사항 파싱"""

        # 메트릭 추출
        metrics = self._extract_metrics(text, category)

        # 제약사항 추출
        constraints = self._extract_constraints(text)

        return ParsedRequirement(
            id=self._generate_id('NFR'),
            type=RequirementType.NON_FUNCTIONAL,
            category=category,
            description=text,
            priority=self._extract_priority(text),
            conditions=constraints,
            acceptance_criteria=self._generate_nfr_criteria(metrics, category)
        )

    def _extract_actor(self, text: str) -> Optional[str]:
        """액터 추출"""
        patterns = [
            r'(user|admin|customer|client|system|application)',
            r'(the\s+)?(\w+)\s+(shall|must|should|can|will)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(3)
        
        return None

    def _extract_action(self, text: str) -> Optional[str]:
        """동작 추출"""
        action_patterns = [
            r'(create|read|update|delete|manage|process|display|calculate)',
            r'(shall|must|should|can|will)\s+(\w+)'
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(2)
        
        return None

    def _extract_object(self, text: str) -> Optional[str]:
        """객체 추출"""
        # 명사구 추출 로직
        object_patterns = [
            r'(create|manage|process|display)\s+([a-zA-Z\s]+?)(?:\s+that|\s+which|\.|$)',
            r'(the|a|an)\s+([a-zA-Z\s]+?)(?:\s+shall|\s+must|\s+should|\.|$)'
        ]
        
        for pattern in object_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(2).strip()
        
        return None

    def _extract_conditions(self, text: str) -> List[str]:
        """조건 추출"""
        conditions = []
        condition_patterns = [
            r'when\s+([^.]+)',
            r'if\s+([^.]+)',
            r'provided\s+that\s+([^.]+)',
            r'given\s+([^.]+)'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend(matches)
        
        return conditions

    def _extract_priority(self, text: str) -> str:
        """우선순위 추출"""
        if re.search(r'\b(critical|must|shall)\b', text, re.IGNORECASE):
            return 'high'
        elif re.search(r'\b(should|important)\b', text, re.IGNORECASE):
            return 'medium'
        elif re.search(r'\b(may|could|optional)\b', text, re.IGNORECASE):
            return 'low'
        else:
            return 'medium'

    def _extract_metrics(self, text: str, category: str) -> Dict[str, Any]:
        """메트릭 추출"""
        metrics = {}
        
        if category == 'performance':
            # 응답 시간
            time_match = re.search(r'(\d+)\s*(ms|milliseconds|seconds)', text, re.IGNORECASE)
            if time_match:
                metrics['response_time'] = {
                    'value': int(time_match.group(1)),
                    'unit': time_match.group(2)
                }
            
            # 처리량
            throughput_match = re.search(r'(\d+)\s*(requests|transactions|users)', text, re.IGNORECASE)
            if throughput_match:
                metrics['throughput'] = {
                    'value': int(throughput_match.group(1)),
                    'unit': throughput_match.group(2)
                }
        
        elif category == 'reliability':
            # 가용성
            availability_match = re.search(r'(\d+(?:\.\d+)?)%\s*(uptime|availability)', text, re.IGNORECASE)
            if availability_match:
                metrics['availability'] = {
                    'value': float(availability_match.group(1)),
                    'unit': 'percentage'
                }
        
        return metrics

    def _extract_constraints(self, text: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        constraint_patterns = [
            r'must\s+not\s+([^.]+)',
            r'cannot\s+([^.]+)',
            r'limited\s+to\s+([^.]+)',
            r'within\s+([^.]+)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            constraints.extend(matches)
        
        return constraints

    def _generate_acceptance_criteria(
        self,
        actor: Optional[str],
        action: Optional[str],
        object_info: Optional[str],
        conditions: List[str]
    ) -> List[str]:
        """수용 기준 생성"""
        criteria = []
        
        if actor and action and object_info:
            criteria.append(f"Given {actor} wants to {action} {object_info}")
            criteria.append(f"When {actor} performs the {action} operation")
            criteria.append(f"Then the {object_info} should be {action}d successfully")
        
        for condition in conditions:
            criteria.append(f"And {condition}")
        
        return criteria

    def _generate_nfr_criteria(self, metrics: Dict[str, Any], category: str) -> List[str]:
        """비기능 요구사항 수용 기준 생성"""
        criteria = []
        
        for metric_name, metric_data in metrics.items():
            value = metric_data['value']
            unit = metric_data['unit']
            criteria.append(f"The {metric_name} must be {value} {unit} or better")
        
        return criteria

    def _generate_id(self, prefix: str) -> str:
        """ID 생성"""
        import uuid
        return f"{prefix}-{str(uuid.uuid4())[:8]}"