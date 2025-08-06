from typing import Dict, List, Any, Pattern
import re
from dataclasses import dataclass

@dataclass
class ParsingRule:
    name: str
    pattern: Pattern
    extractor: callable
    category: str
    priority: int

class ParsingRuleEngine:
    """요구사항 파싱 규칙 엔진"""

    def __init__(self):
        self.rules = self._initialize_rules()
        self.keyword_mappings = self._load_keyword_mappings()

    def _initialize_rules(self) -> List[ParsingRule]:
        """파싱 규칙 초기화"""
        return [
            # 성능 요구사항 규칙
            ParsingRule(
                name="performance_requirement",
                pattern=re.compile(
                    r'(should|must|need to)\s+(respond|load|process|handle)'
                    r'.*?within\s+(\d+)\s*(ms|milliseconds|seconds|s)',
                    re.IGNORECASE
                ),
                extractor=self._extract_performance_requirement,
                category="performance",
                priority=1
            ),

            # 사용자 수 요구사항
            ParsingRule(
                name="user_capacity",
                pattern=re.compile(
                    r'(support|handle|accommodate)\s+'
                    r'(up to\s+)?(\d+[,\d]*)\s+'
                    r'(concurrent\s+)?(users|connections|requests)',
                    re.IGNORECASE
                ),
                extractor=self._extract_capacity_requirement,
                category="scalability",
                priority=1
            ),

            # API 엔드포인트 규칙
            ParsingRule(
                name="api_endpoint",
                pattern=re.compile(
                    r'(GET|POST|PUT|DELETE|PATCH)\s+'
                    r'(/[\w/\-{}]+)',
                    re.IGNORECASE
                ),
                extractor=self._extract_api_endpoint,
                category="api",
                priority=2
            ),

            # 데이터 모델 규칙
            ParsingRule(
                name="data_model",
                pattern=re.compile(
                    r'(entity|model|table|collection)\s+'
                    r'["\']?(\w+)["\']?\s+'
                    r'(with|contains|has)\s+'
                    r'(fields?|attributes?|properties?):?\s*'
                    r'([^.]+)',
                    re.IGNORECASE
                ),
                extractor=self._extract_data_model,
                category="data",
                priority=2
            ),

            # 보안 요구사항 규칙
            ParsingRule(
                name="security_requirement",
                pattern=re.compile(
                    r'(require|implement|use|enable)\s+'
                    r'(authentication|authorization|encryption|ssl|tls|oauth|jwt)',
                    re.IGNORECASE
                ),
                extractor=self._extract_security_requirement,
                category="security",
                priority=1
            )
        ]

    def _load_keyword_mappings(self) -> Dict[str, List[str]]:
        """키워드 매핑 로드"""
        return {
            'performance': ['fast', 'quick', 'speed', 'latency', 'response time'],
            'security': ['secure', 'auth', 'encrypt', 'protect', 'safe'],
            'scalability': ['scale', 'users', 'concurrent', 'load', 'capacity'],
            'usability': ['user-friendly', 'easy', 'intuitive', 'simple'],
            'reliability': ['reliable', 'stable', 'available', 'uptime']
        }

    def apply_rules(self, text: str) -> Dict[str, List[Any]]:
        """텍스트에 규칙 적용"""
        results = {
            'performance': [],
            'scalability': [],
            'api': [],
            'data': [],
            'security': [],
            'other': []
        }

        # 우선순위 순으로 규칙 적용
        sorted_rules = sorted(self.rules, key=lambda r: r.priority)

        for rule in sorted_rules:
            matches = rule.pattern.finditer(text)
            for match in matches:
                extracted = rule.extractor(match, text)
                if extracted:
                    results[rule.category].append(extracted)

        return results

    def _extract_performance_requirement(self, match, text: str) -> Dict[str, Any]:
        """성능 요구사항 추출"""
        return {
            'type': 'performance',
            'description': match.group(),
            'value': match.group(3),
            'unit': match.group(4),
            'action': match.group(2)
        }

    def _extract_capacity_requirement(self, match, text: str) -> Dict[str, Any]:
        """용량 요구사항 추출"""
        return {
            'type': 'capacity',
            'description': match.group(),
            'count': match.group(3).replace(',', ''),
            'resource_type': match.group(5)
        }

    def _extract_api_endpoint(self, match, text: str) -> Dict[str, Any]:
        """API 엔드포인트 추출"""
        return {
            'type': 'api_endpoint',
            'method': match.group(1).upper(),
            'path': match.group(2),
            'description': match.group()
        }

    def _extract_data_model(self, match, text: str) -> Dict[str, Any]:
        """데이터 모델 추출"""
        return {
            'type': 'data_model',
            'name': match.group(2),
            'fields': match.group(5).split(','),
            'description': match.group()
        }

    def _extract_security_requirement(self, match, text: str) -> Dict[str, Any]:
        """보안 요구사항 추출"""
        return {
            'type': 'security',
            'action': match.group(1),
            'mechanism': match.group(2),
            'description': match.group()
        }