# Phase 4: 9개 핵심 에이전트 구현 - Parser Agent (Tasks 4.21-4.23)

## 3. Parser Agent (요구사항 파싱 에이전트)

### Task 4.21: Parser Agent 코어 구현

#### SubTask 4.21.1: Parser Agent 기본 아키텍처 구현

**담당자**: 시니어 백엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser_agent.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

@dataclass
class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"

@dataclass
class ParsedRequirement:
    id: str
    type: RequirementType
    category: str
    description: str
    priority: str  # high, medium, low
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedProject:
    project_info: Dict[str, Any]
    functional_requirements: List[ParsedRequirement]
    non_functional_requirements: List[ParsedRequirement]
    technical_requirements: List[ParsedRequirement]
    business_requirements: List[ParsedRequirement]
    constraints: List[ParsedRequirement]
    assumptions: List[ParsedRequirement]
    user_stories: List[Dict[str, Any]]
    use_cases: List[Dict[str, Any]]
    data_models: List[Dict[str, Any]]
    api_specifications: List[Dict[str, Any]]
    ui_components: List[Dict[str, Any]]
    integration_points: List[Dict[str, Any]]

class ParserAgent:
    """요구사항 파싱 및 구조화 에이전트"""

    def __init__(self):
        # 주 파서 - Claude 3 (긴 문맥 처리에 최적화)
        self.main_parser = Agent(
            name="Requirements-Parser",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert requirements analyst and system architect",
            instructions=[
                "Parse and structure project requirements from natural language",
                "Identify functional and non-functional requirements",
                "Extract technical specifications and constraints",
                "Create user stories and use cases",
                "Define data models and API specifications",
                "Identify dependencies and relationships between requirements"
            ],
            temperature=0.2,  # 낮은 온도로 일관성 있는 파싱
            max_retries=3
        )

        # 보조 파서 - GPT-4 (세부 분석)
        self.detail_parser = Agent(
            name="Detail-Parser",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Technical requirements specialist",
            instructions=[
                "Extract technical details from requirements",
                "Identify specific technologies and frameworks mentioned",
                "Parse API endpoints and data structures",
                "Extract performance and security requirements"
            ],
            temperature=0.1
        )

        # 전문 파서들
        self.requirement_extractor = RequirementExtractor()
        self.user_story_generator = UserStoryGenerator()
        self.data_model_parser = DataModelParser()
        self.api_spec_parser = APISpecificationParser()
        self.constraint_analyzer = ConstraintAnalyzer()

        # 파싱 규칙 엔진
        self.parsing_rules = ParsingRuleEngine()

        # 검증기
        self.requirement_validator = RequirementValidator()

    async def parse_requirements(
        self,
        raw_description: str,
        project_context: Optional[Dict[str, Any]] = None,
        parsing_options: Optional[Dict[str, Any]] = None
    ) -> ParsedProject:
        """프로젝트 요구사항 파싱"""

        # 1. 전처리
        preprocessed_text = await self._preprocess_text(
            raw_description,
            project_context
        )

        # 2. 기본 구조 파싱
        base_structure = await self._parse_base_structure(preprocessed_text)

        # 3. 병렬 상세 파싱
        parsing_tasks = [
            self._parse_functional_requirements(base_structure),
            self._parse_non_functional_requirements(base_structure),
            self._parse_technical_requirements(base_structure),
            self._parse_business_requirements(base_structure),
            self._parse_constraints(base_structure),
            self._parse_assumptions(base_structure),
            self._generate_user_stories(base_structure),
            self._extract_use_cases(base_structure),
            self._parse_data_models(base_structure),
            self._parse_api_specifications(base_structure),
            self._identify_ui_components(base_structure),
            self._identify_integration_points(base_structure)
        ]

        results = await asyncio.gather(*parsing_tasks)

        # 4. 결과 조합
        parsed_project = ParsedProject(
            project_info=base_structure.get('project_info', {}),
            functional_requirements=results[0],
            non_functional_requirements=results[1],
            technical_requirements=results[2],
            business_requirements=results[3],
            constraints=results[4],
            assumptions=results[5],
            user_stories=results[6],
            use_cases=results[7],
            data_models=results[8],
            api_specifications=results[9],
            ui_components=results[10],
            integration_points=results[11]
        )

        # 5. 검증 및 보완
        validated_project = await self._validate_and_enrich(parsed_project)

        return validated_project

    async def _preprocess_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """텍스트 전처리"""
        # 구조화된 섹션 감지
        sections = self._detect_sections(text)

        # 약어 및 전문 용어 확장
        expanded_text = self._expand_abbreviations(text, context)

        # 참조 해결
        resolved_text = self._resolve_references(expanded_text, context)

        # 형식 정규화
        normalized_text = self._normalize_format(resolved_text)

        return normalized_text

    async def _parse_base_structure(self, text: str) -> Dict[str, Any]:
        """기본 구조 파싱"""
        prompt = f"""
        Parse the following project requirements and extract the basic structure:

        {text}

        Extract:
        1. Project name and description
        2. Project type (web, mobile, desktop, api, etc.)
        3. Target users and stakeholders
        4. High-level goals and objectives
        5. Key features and functionalities
        6. Technical context and constraints
        7. Timeline and milestones
        8. Success criteria

        Return as structured JSON.
        """

        result = await self.main_parser.arun(prompt)
        return self._parse_json_response(result.content)

    async def _parse_functional_requirements(
        self,
        base_structure: Dict[str, Any]
    ) -> List[ParsedRequirement]:
        """기능 요구사항 파싱"""
        features = base_structure.get('key_features', [])
        requirements = []

        for idx, feature in enumerate(features):
            # 각 기능을 상세 요구사항으로 분해
            detailed_reqs = await self.requirement_extractor.extract_functional(
                feature,
                context=base_structure
            )

            for req in detailed_reqs:
                parsed_req = ParsedRequirement(
                    id=f"FR-{idx+1:03d}-{len(requirements)+1:02d}",
                    type=RequirementType.FUNCTIONAL,
                    category=req.get('category', 'general'),
                    description=req.get('description', ''),
                    priority=req.get('priority', 'medium'),
                    dependencies=req.get('dependencies', []),
                    acceptance_criteria=req.get('acceptance_criteria', []),
                    technical_details=req.get('technical_details', {}),
                    metadata={
                        'feature': feature,
                        'extracted_at': datetime.utcnow().isoformat()
                    }
                )
                requirements.append(parsed_req)

        return requirements
```

**파싱 규칙 엔진**:

```python
# backend/src/agents/implementations/parser/parsing_rules.py
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
```

**검증 기준**:

- [ ] 다양한 형식의 요구사항 파싱
- [ ] 구조화된 데이터 출력
- [ ] 파싱 규칙 엔진 동작
- [ ] 멀티 모델 협업 구현

#### SubTask 4.21.2: 자연어 처리 파이프라인 구현

**담당자**: NLP 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/nlp_pipeline.py
from typing import List, Dict, Any, Tuple
import spacy
import nltk
from transformers import pipeline
import asyncio
from dataclasses import dataclass

@dataclass
class NLPResult:
    tokens: List[str]
    entities: List[Dict[str, Any]]
    dependencies: List[Tuple[str, str, str]]
    sentiment: Dict[str, float]
    key_phrases: List[str]
    intent: str
    modality: str  # must, should, could, won't

class NLPPipeline:
    """자연어 처리 파이프라인"""

    def __init__(self):
        # SpaCy 모델 로드
        self.nlp = spacy.load("en_core_web_lg")

        # 추가 NLP 컴포넌트
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        self.summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

        # 커스텀 컴포넌트
        self.requirement_classifier = RequirementClassifier()
        self.modality_detector = ModalityDetector()
        self.domain_entity_recognizer = DomainEntityRecognizer()

        # NLTK 설정
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)

    async def process_text(self, text: str) -> NLPResult:
        """텍스트 NLP 처리"""
        # 병렬 처리를 위한 태스크 생성
        tasks = [
            self._tokenize_and_parse(text),
            self._extract_entities(text),
            self._analyze_sentiment(text),
            self._extract_key_phrases(text),
            self._classify_intent(text),
            self._detect_modality(text)
        ]

        results = await asyncio.gather(*tasks)

        return NLPResult(
            tokens=results[0]['tokens'],
            entities=results[1],
            dependencies=results[0]['dependencies'],
            sentiment=results[2],
            key_phrases=results[3],
            intent=results[4],
            modality=results[5]
        )

    async def _tokenize_and_parse(self, text: str) -> Dict[str, Any]:
        """토큰화 및 구문 분석"""
        doc = self.nlp(text)

        tokens = [token.text for token in doc]
        pos_tags = [(token.text, token.pos_) for token in doc]
        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]

        # 문장 분리
        sentences = [sent.text.strip() for sent in doc.sents]

        return {
            'tokens': tokens,
            'pos_tags': pos_tags,
            'dependencies': dependencies,
            'sentences': sentences
        }

    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """개체명 인식"""
        # SpaCy NER
        doc = self.nlp(text)
        spacy_entities = [
            {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }
            for ent in doc.ents
        ]

        # Transformer 기반 NER
        transformer_entities = self.ner_pipeline(text)

        # 도메인 특화 엔티티
        domain_entities = await self.domain_entity_recognizer.recognize(text)

        # 결과 병합 및 중복 제거
        all_entities = self._merge_entities(
            spacy_entities,
            transformer_entities,
            domain_entities
        )

        return all_entities

    async def _extract_key_phrases(self, text: str) -> List[str]:
        """핵심 구문 추출"""
        doc = self.nlp(text)

        # 명사구 추출
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]

        # TF-IDF 기반 키워드 추출
        tfidf_keywords = self._extract_tfidf_keywords(text)

        # RAKE 알고리즘
        rake_keywords = self._extract_rake_keywords(text)

        # 결합 및 순위 매기기
        all_phrases = list(set(noun_phrases + tfidf_keywords + rake_keywords))
        ranked_phrases = self._rank_phrases(all_phrases, text)

        return ranked_phrases[:20]  # 상위 20개

    def _extract_requirement_patterns(self, text: str) -> List[Dict[str, Any]]:
        """요구사항 패턴 추출"""
        patterns = []

        # RFC 2119 키워드 (MUST, SHOULD, MAY 등)
        rfc_pattern = r'\b(MUST|SHALL|SHOULD|MAY|REQUIRED|RECOMMENDED|OPTIONAL)\b'

        # 요구사항 표현 패턴
        requirement_patterns = [
            r'(system|application|user)\s+(shall|must|should|will)\s+([^.]+)',
            r'(need|require|want)\s+to\s+([^.]+)',
            r'(it\s+is\s+)?(required|necessary|important)\s+(that|to)\s+([^.]+)',
            r'(ensure|make sure|guarantee)\s+(that\s+)?([^.]+)'
        ]

        for pattern in requirement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                patterns.append({
                    'pattern': pattern,
                    'match': match.group(),
                    'groups': match.groups(),
                    'position': match.span()
                })

        return patterns
```

**도메인 특화 엔티티 인식기**:

```python
# backend/src/agents/implementations/parser/domain_entity_recognizer.py
class DomainEntityRecognizer:
    """도메인 특화 엔티티 인식"""

    def __init__(self):
        self.domain_patterns = {
            'ui_component': [
                r'\b(button|form|input|dropdown|modal|navbar|sidebar|menu|table|list|grid|card)\b',
                r'\b(header|footer|section|container|wrapper|layout)\b'
            ],
            'api_component': [
                r'\b(endpoint|route|api|rest|graphql|webhook|websocket)\b',
                r'\b(request|response|payload|parameter|query|body)\b'
            ],
            'database': [
                r'\b(database|table|collection|schema|index|query|transaction)\b',
                r'\b(sql|nosql|mongodb|postgres|mysql|redis)\b'
            ],
            'authentication': [
                r'\b(auth|authentication|authorization|login|logout|session|token)\b',
                r'\b(oauth|jwt|sso|ldap|saml|2fa|mfa)\b'
            ],
            'deployment': [
                r'\b(deploy|deployment|docker|kubernetes|container|ci/cd)\b',
                r'\b(aws|azure|gcp|cloud|server|hosting)\b'
            ]
        }

    async def recognize(self, text: str) -> List[Dict[str, Any]]:
        """도메인 엔티티 인식"""
        entities = []

        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': f'DOMAIN_{domain.upper()}',
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9
                    })

        # 컨텍스트 기반 검증
        validated_entities = await self._validate_with_context(entities, text)

        return validated_entities
```

**검증 기준**:

- [ ] SpaCy 통합 완료
- [ ] 멀티 모델 NER 구현
- [ ] 도메인 특화 인식 동작
- [ ] 병렬 처리 최적화

#### SubTask 4.21.3: 요구사항 분류 및 우선순위 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/requirement_classifier.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np
from typing import List, Dict, Any, Tuple

class RequirementClassifier:
    """요구사항 분류 및 우선순위 결정"""

    def __init__(self):
        # 사전 훈련된 분류 모델 로드
        self.type_classifier = self._load_type_classifier()
        self.priority_classifier = self._load_priority_classifier()
        self.category_classifier = self._load_category_classifier()

        # TF-IDF 벡터라이저
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english'
        )

        # 우선순위 규칙 엔진
        self.priority_rules = PriorityRuleEngine()

        # 의존성 분석기
        self.dependency_analyzer = DependencyAnalyzer()

    async def classify_requirements(
        self,
        requirements: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """요구사항 분류"""
        classified_requirements = []

        # 벡터화
        if requirements:
            vectors = self.vectorizer.fit_transform(requirements)
        else:
            return []

        # 병렬 분류
        tasks = []
        for idx, req in enumerate(requirements):
            task = self._classify_single_requirement(
                req,
                vectors[idx],
                context
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # 의존성 분석
        dependency_graph = await self.dependency_analyzer.analyze(results)

        # 우선순위 조정
        adjusted_results = self._adjust_priorities(results, dependency_graph)

        return adjusted_results

    async def _classify_single_requirement(
        self,
        requirement: str,
        vector: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단일 요구사항 분류"""

        # 타입 분류
        req_type = self.type_classifier.predict(vector)[0]
        type_proba = self.type_classifier.predict_proba(vector)[0]

        # 카테고리 분류
        category = self.category_classifier.predict(vector)[0]
        category_proba = self.category_classifier.predict_proba(vector)[0]

        # 우선순위 예측
        base_priority = self.priority_classifier.predict(vector)[0]

        # 규칙 기반 우선순위 조정
        adjusted_priority = await self.priority_rules.adjust_priority(
            requirement,
            base_priority,
            context
        )

        # 복잡도 추정
        complexity = self._estimate_complexity(requirement, vector)

        return {
            'requirement': requirement,
            'type': req_type,
            'type_confidence': float(max(type_proba)),
            'category': category,
            'category_confidence': float(max(category_proba)),
            'priority': adjusted_priority,
            'complexity': complexity,
            'metadata': {
                'keywords': self._extract_keywords(requirement),
                'estimated_effort': self._estimate_effort(complexity),
                'risk_level': self._assess_risk(requirement, context)
            }
        }

    def _estimate_complexity(self, requirement: str, vector: Any) -> str:
        """복잡도 추정"""
        # 복잡도 지표
        indicators = {
            'simple': ['basic', 'simple', 'standard', 'common'],
            'medium': ['integrate', 'connect', 'process', 'manage'],
            'complex': ['optimize', 'scale', 'distributed', 'real-time'],
            'very_complex': ['ai', 'machine learning', 'blockchain', 'quantum']
        }

        requirement_lower = requirement.lower()
        scores = {}

        for level, keywords in indicators.items():
            score = sum(1 for keyword in keywords if keyword in requirement_lower)
            scores[level] = score

        # 벡터 기반 복잡도 추가
        vector_complexity = self._calculate_vector_complexity(vector)

        # 최종 복잡도 결정
        if vector_complexity > 0.8 or scores.get('very_complex', 0) > 0:
            return 'very_complex'
        elif vector_complexity > 0.6 or scores.get('complex', 0) > 1:
            return 'complex'
        elif vector_complexity > 0.3 or scores.get('medium', 0) > 1:
            return 'medium'
        else:
            return 'simple'
```

**우선순위 규칙 엔진**:

```python
# backend/src/agents/implementations/parser/priority_rules.py
class PriorityRuleEngine:
    """우선순위 결정 규칙 엔진"""

    def __init__(self):
        self.rules = [
            SecurityPriorityRule(),
            CompliancePriorityRule(),
            PerformancePriorityRule(),
            UserImpactPriorityRule(),
            BusinessValuePriorityRule(),
            TechnicalDebtPriorityRule()
        ]

    async def adjust_priority(
        self,
        requirement: str,
        base_priority: str,
        context: Dict[str, Any]
    ) -> str:
        """규칙 기반 우선순위 조정"""

        priority_scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }

        current_score = priority_scores.get(base_priority, 2)
        adjustments = []

        # 각 규칙 적용
        for rule in self.rules:
            adjustment = await rule.evaluate(requirement, context)
            if adjustment != 0:
                adjustments.append({
                    'rule': rule.name,
                    'adjustment': adjustment,
                    'reason': rule.last_reason
                })
                current_score += adjustment

        # 점수를 우선순위로 변환
        final_priority = self._score_to_priority(current_score)

        return final_priority

    def _score_to_priority(self, score: float) -> str:
        """점수를 우선순위로 변환"""
        if score >= 4:
            return 'critical'
        elif score >= 3:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'

class SecurityPriorityRule:
    """보안 관련 우선순위 규칙"""

    name = "security"

    def __init__(self):
        self.security_keywords = [
            'security', 'authentication', 'authorization',
            'encryption', 'vulnerability', 'exploit',
            'password', 'access control', 'data protection'
        ]
        self.last_reason = ""

    async def evaluate(self, requirement: str, context: Dict[str, Any]) -> float:
        """보안 요구사항 평가"""
        requirement_lower = requirement.lower()

        # 보안 키워드 확인
        security_mentions = sum(
            1 for keyword in self.security_keywords
            if keyword in requirement_lower
        )

        if security_mentions > 2:
            self.last_reason = "Multiple security concerns identified"
            return 1.5
        elif security_mentions > 0:
            self.last_reason = "Security requirement detected"
            return 0.5

        # 컨텍스트에서 보안 중요도 확인
        if context.get('security_critical', False):
            self.last_reason = "Project marked as security critical"
            return 1.0

        return 0
```

**검증 기준**:

- [ ] 요구사항 타입 분류 정확도 90% 이상
- [ ] 우선순위 자동 결정
- [ ] 복잡도 추정 구현
- [ ] 의존성 분석 동작

#### SubTask 4.21.4: Parser Agent 통합 테스트

**담당자**: QA 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/tests/agents/parser/test_parser_integration.py
import pytest
import asyncio
from typing import Dict, Any, List

@pytest.mark.integration
class TestParserAgentIntegration:
    """Parser Agent 통합 테스트"""

    @pytest.fixture
    async def parser_agent(self):
        """Parser Agent 인스턴스"""
        from parser_agent import ParserAgent

        agent = ParserAgent()
        await agent.initialize()
        yield agent
        await agent.cleanup()

    @pytest.fixture
    def test_requirements(self):
        """다양한 테스트 요구사항"""
        return [
            {
                "name": "E-commerce Platform",
                "description": """
                We need to build a modern e-commerce platform that supports multiple vendors.

                The system MUST support user registration and authentication using OAuth 2.0.
                Users SHALL be able to browse products, add items to cart, and checkout.

                The platform SHOULD handle at least 10,000 concurrent users and respond
                within 200ms for product searches. Payment processing MUST be PCI compliant.

                Key features include:
                - Product catalog with categories and filters
                - Shopping cart with session persistence
                - Order management system
                - Inventory tracking with real-time updates
                - Customer reviews and ratings
                - Admin dashboard for vendors

                The system will integrate with Stripe for payments, SendGrid for emails,
                and use PostgreSQL for the main database with Redis for caching.

                Mobile apps for iOS and Android are required, using React Native.
                The web frontend should be built with Next.js for SEO optimization.

                API endpoints needed:
                - GET /api/products?category={category}&page={page}
                - POST /api/cart/items
                - PUT /api/orders/{orderId}/status
                - DELETE /api/cart/items/{itemId}

                Data models:
                - User entity with fields: id, email, name, password_hash, created_at
                - Product entity with fields: id, name, description, price, stock_quantity
                - Order entity with fields: id, user_id, total_amount, status, created_at
                """,
                "expected_counts": {
                    "functional_requirements": 15,
                    "non_functional_requirements": 5,
                    "technical_requirements": 8,
                    "api_endpoints": 4,
                    "data_models": 3
                }
            },
            {
                "name": "Healthcare Management System",
                "description": """
                Develop a HIPAA-compliant healthcare management system for clinics.

                CRITICAL REQUIREMENTS:
                - All patient data MUST be encrypted at rest and in transit
                - System MUST maintain audit logs for all data access
                - Role-based access control is REQUIRED

                The system should support appointment scheduling, patient records,
                prescription management, and billing. Integration with insurance
                providers is needed via HL7 FHIR standards.

                Performance requirements:
                - Support 500 concurrent users per clinic
                - Database queries must return within 100ms
                - 99.9% uptime SLA required
                - Automated backups every 6 hours
                """,
                "expected_counts": {
                    "functional_requirements": 8,
                    "non_functional_requirements": 7,
                    "constraints": 4,
                    "business_requirements": 3
                }
            }
        ]

    @pytest.mark.asyncio
    async def test_comprehensive_parsing(self, parser_agent, test_requirements):
        """포괄적인 파싱 테스트"""

        for test_case in test_requirements:
            # 요구사항 파싱
            result = await parser_agent.parse_requirements(
                test_case["description"],
                project_context={
                    "name": test_case["name"],
                    "domain": "e-commerce" if "e-commerce" in test_case["name"] else "healthcare"
                }
            )

            # 기본 구조 검증
            assert result.project_info is not None
            assert len(result.functional_requirements) > 0

            # 예상 카운트 검증
            expected = test_case["expected_counts"]

            if "functional_requirements" in expected:
                assert len(result.functional_requirements) >= expected["functional_requirements"] * 0.8

            if "api_endpoints" in expected:
                assert len(result.api_specifications) >= expected["api_endpoints"]

            if "data_models" in expected:
                assert len(result.data_models) >= expected["data_models"]

            # 각 요구사항 검증
            for req in result.functional_requirements:
                assert req.id is not None
                assert req.description != ""
                assert req.priority in ['critical', 'high', 'medium', 'low']
                assert req.type == RequirementType.FUNCTIONAL

    @pytest.mark.asyncio
    async def test_nlp_accuracy(self, parser_agent):
        """NLP 처리 정확도 테스트"""

        test_sentences = [
            {
                "text": "The system MUST authenticate users with JWT tokens",
                "expected_modality": "must",
                "expected_entities": ["JWT"],
                "expected_category": "security"
            },
            {
                "text": "Response time SHOULD be under 200ms for API calls",
                "expected_modality": "should",
                "expected_entities": ["200ms", "API"],
                "expected_category": "performance"
            }
        ]

        for test in test_sentences:
            result = await parser_agent._process_single_requirement(test["text"])

            assert result["modality"] == test["expected_modality"]
            assert result["category"] == test["expected_category"]

            # 엔티티 확인
            found_entities = [e["text"] for e in result["entities"]]
            for expected_entity in test["expected_entities"]:
                assert any(expected_entity in entity for entity in found_entities)

    @pytest.mark.asyncio
    async def test_dependency_analysis(self, parser_agent):
        """의존성 분석 테스트"""

        requirements_with_dependencies = """
        1. User authentication system with OAuth 2.0
        2. User profile management (depends on authentication)
        3. Shopping cart functionality
        4. Order processing (depends on cart and payment)
        5. Payment integration with Stripe
        6. Email notifications (depends on user profile)
        """

        result = await parser_agent.parse_requirements(requirements_with_dependencies)

        # 의존성 그래프 확인
        dependencies = {}
        for req in result.functional_requirements:
            if req.dependencies:
                dependencies[req.id] = req.dependencies

        # 예상 의존성 확인
        assert len(dependencies) >= 3

        # Order processing이 cart와 payment에 의존하는지 확인
        order_req = next(
            (r for r in result.functional_requirements if "order" in r.description.lower()),
            None
        )
        assert order_req is not None
        assert len(order_req.dependencies) >= 2
```

**성능 테스트**:

```python
# backend/tests/agents/parser/test_parser_performance.py
import time
import statistics

class TestParserPerformance:
    """Parser Agent 성능 테스트"""

    @pytest.mark.performance
    async def test_parsing_speed(self, parser_agent):
        """파싱 속도 테스트"""

        # 다양한 길이의 요구사항
        test_texts = [
            "Simple requirement" * 10,  # 짧은 텍스트
            "Medium complexity requirement with details" * 50,  # 중간
            "Complex requirement with multiple sections" * 200  # 긴 텍스트
        ]

        parsing_times = []

        for text in test_texts:
            start_time = time.time()
            await parser_agent.parse_requirements(text)
            elapsed = time.time() - start_time
            parsing_times.append(elapsed)

        # 성능 메트릭
        avg_time = statistics.mean(parsing_times)
        max_time = max(parsing_times)

        # 성능 기준
        assert avg_time < 2.0  # 평균 2초 이내
        assert max_time < 5.0  # 최대 5초 이내

    @pytest.mark.performance
    async def test_concurrent_parsing(self, parser_agent):
        """동시 파싱 성능 테스트"""

        num_concurrent = 20
        test_requirement = "Build a web application with user authentication"

        async def parse_task():
            return await parser_agent.parse_requirements(test_requirement)

        start_time = time.time()
        tasks = [parse_task() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # 모든 결과가 성공적으로 반환되었는지 확인
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)

        # 동시 처리 성능 확인 (20개 요청이 10초 이내)
        assert total_time < 10.0
```

**검증 기준**:

- [ ] 모든 테스트 케이스 통과
- [ ] NLP 정확도 85% 이상
- [ ] 의존성 분석 정확도
- [ ] 성능 목표 달성

### Task 4.22: Parser Agent 요구사항 분석 기능

#### SubTask 4.22.1: 기능/비기능 요구사항 분리기

**담당자**: 요구사항 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/requirement_separator.py
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

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
            category='feature',
            description=text,
            priority='medium',
            acceptance_criteria=acceptance_criteria,
            technical_details={
                'actor': actor,
                'action': action,
                'object': object_info,
                'conditions': conditions
            }
        )

    async def _parse_non_functional_requirement(
        self,
        text: str,
        category: str
    ) -> ParsedRequirement:
        """비기능 요구사항 파싱"""

        # 메트릭 추출
        metrics = self._extract_metrics(text)

        # 임계값 추출
        thresholds = self._extract_thresholds(text)

        # 조건 추출
        conditions = self._extract_nfr_conditions(text)

        # 측정 방법 결정
        measurement_method = self._determine_measurement_method(
            category,
            metrics,
            text
        )

        return ParsedRequirement(
            id=self._generate_id('NFR'),
            type=RequirementType.NON_FUNCTIONAL,
            category=category,
            description=text,
            priority=self._determine_nfr_priority(category, metrics),
            acceptance_criteria=self._generate_nfr_acceptance_criteria(
                category,
                metrics,
                thresholds
            ),
            technical_details={
                'metrics': metrics,
                'thresholds': thresholds,
                'conditions': conditions,
                'measurement_method': measurement_method
            }
        )
```

**메트릭 추출기**:

```python
# backend/src/agents/implementations/parser/metric_extractor.py
class MetricExtractor:
    """요구사항에서 메트릭 추출"""

    def __init__(self):
        self.metric_patterns = {
            'time': {
                'pattern': r'(\d+(?:\.\d+)?)\s*(ms|milliseconds?|seconds?|minutes?|hours?)',
                'unit_map': {
                    'ms': 'milliseconds',
                    'millisecond': 'milliseconds',
                    'milliseconds': 'milliseconds',
                    'second': 'seconds',
                    'seconds': 'seconds',
                    'minute': 'minutes',
                    'minutes': 'minutes',
                    'hour': 'hours',
                    'hours': 'hours'
                }
            },
            'percentage': {
                'pattern': r'(\d+(?:\.\d+)?)\s*%',
                'unit': 'percent'
            },
            'count': {
                'pattern': r'(\d+(?:,\d{3})*|\d+)\s*(users?|requests?|transactions?|connections?)',
                'unit_map': {
                    'user': 'users',
                    'users': 'users',
                    'request': 'requests',
                    'requests': 'requests',
                    'transaction': 'transactions',
                    'transactions': 'transactions',
                    'connection': 'connections',
                    'connections': 'connections'
                }
            },
            'data_size': {
                'pattern': r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB|bytes?)',
                'unit_map': {
                    'byte': 'bytes',
                    'bytes': 'bytes',
                    'KB': 'kilobytes',
                    'MB': 'megabytes',
                    'GB': 'gigabytes',
                    'TB': 'terabytes'
                }
            },
            'frequency': {
                'pattern': r'(\d+)\s*(?:times?\s*)?(?:per|/)\s*(second|minute|hour|day)',
                'unit': 'per_time'
            }
        }

    def extract_metrics(self, text: str) -> List[Dict[str, Any]]:
        """텍스트에서 메트릭 추출"""
        metrics = []

        for metric_type, config in self.metric_patterns.items():
            pattern = config['pattern']
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                value = match.group(1)

                # 숫자 변환
                numeric_value = self._parse_number(value)

                # 단위 추출
                if 'unit_map' in config:
                    raw_unit = match.group(2).lower()
                    unit = config['unit_map'].get(raw_unit, raw_unit)
                elif 'unit' in config:
                    unit = config['unit']
                else:
                    unit = match.group(2) if match.lastindex >= 2 else None

                metrics.append({
                    'type': metric_type,
                    'value': numeric_value,
                    'unit': unit,
                    'raw_text': match.group(0),
                    'position': match.span()
                })

        return metrics

    def _parse_number(self, text: str) -> float:
        """숫자 텍스트를 float로 변환"""
        # 쉼표 제거
        text = text.replace(',', '')

        try:
            return float(text)
        except ValueError:
            return 0.0
```

**검증 기준**:

- [ ] 기능/비기능 분리 정확도 90% 이상
- [ ] 메트릭 추출 정확도
- [ ] 수용 기준 자동 생성
- [ ] 카테고리별 분류 동작

#### SubTask 4.22.2: 사용자 스토리 생성기

**담당자**: 비즈니스 분석가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/user_story_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class UserStory:
    id: str
    title: str
    narrative: str  # As a... I want... So that...
    acceptance_criteria: List[str]
    story_points: Optional[int]
    priority: str
    epic: Optional[str]
    technical_notes: List[str]
    dependencies: List[str]

class UserStoryGenerator:
    """사용자 스토리 자동 생성기"""

    def __init__(self):
        self.story_templates = {
            'authentication': {
                'template': "As a {actor}, I want to {action} so that {benefit}",
                'common_actions': [
                    'sign up with email',
                    'log in securely',
                    'reset my password',
                    'enable two-factor authentication'
                ]
            },
            'data_management': {
                'template': "As a {actor}, I want to {action} {object} so that {benefit}",
                'common_actions': [
                    'create new',
                    'view existing',
                    'update',
                    'delete',
                    'search for',
                    'filter',
                    'export'
                ]
            },
            'workflow': {
                'template': "As a {actor}, I want to {action} so that {benefit}",
                'common_actions': [
                    'approve requests',
                    'receive notifications',
                    'track progress',
                    'collaborate with team'
                ]
            }
        }

        self.story_point_estimator = StoryPointEstimator()
        self.acceptance_criteria_generator = AcceptanceCriteriaGenerator()

    async def generate_user_stories(
        self,
        requirements: List[ParsedRequirement],
        project_context: Dict[str, Any]
    ) -> List[UserStory]:
        """요구사항에서 사용자 스토리 생성"""

        user_stories = []
        story_counter = 1

        # 액터 식별
        actors = await self._identify_actors(requirements, project_context)

        # 에픽 그룹화
        epics = await self._group_into_epics(requirements)

        for req in requirements:
            if req.type == RequirementType.FUNCTIONAL:
                # 요구사항을 여러 스토리로 분해
                stories = await self._decompose_requirement(
                    req,
                    actors,
                    epics
                )

                for story_data in stories:
                    # 스토리 생성
                    story = UserStory(
                        id=f"US-{story_counter:04d}",
                        title=story_data['title'],
                        narrative=story_data['narrative'],
                        acceptance_criteria=await self.acceptance_criteria_generator.generate(
                            story_data,
                            req
                        ),
                        story_points=await self.story_point_estimator.estimate(
                            story_data,
                            req
                        ),
                        priority=self._inherit_priority(req.priority),
                        epic=story_data.get('epic'),
                        technical_notes=self._extract_technical_notes(req),
                        dependencies=self._identify_dependencies(req, requirements)
                    )

                    user_stories.append(story)
                    story_counter += 1

        # 스토리 간 관계 분석
        user_stories = await self._analyze_story_relationships(user_stories)

        return user_stories

    async def _decompose_requirement(
        self,
        requirement: ParsedRequirement,
        actors: List[str],
        epics: Dict[str, List[ParsedRequirement]]
    ) -> List[Dict[str, Any]]:
        """요구사항을 사용자 스토리로 분해"""

        stories = []

        # 요구사항 분석
        req_analysis = await self._analyze_requirement_for_stories(
            requirement.description
        )

        # 각 액터별로 스토리 생성
        for actor in self._get_relevant_actors(requirement, actors):
            for action in req_analysis['actions']:
                # 스토리 내러티브 생성
                narrative = await self._create_narrative(
                    actor,
                    action,
                    req_analysis['benefits']
                )

                # 스토리 제목 생성
                title = self._create_story_title(action, req_analysis['object'])

                stories.append({
                    'title': title,
                    'narrative': narrative,
                    'actor': actor,
                    'action': action,
                    'object': req_analysis.get('object'),
                    'benefits': req_analysis['benefits'],
                    'epic': self._find_epic(requirement, epics),
                    'original_requirement': requirement.id
                })

        return stories

    async def _create_narrative(
        self,
        actor: str,
        action: str,
        benefits: List[str]
    ) -> str:
        """사용자 스토리 내러티브 생성"""

        # 기본 템플릿
        template = "As a {actor}, I want to {action} so that {benefit}"

        # 가장 관련성 높은 benefit 선택
        primary_benefit = benefits[0] if benefits else "I can complete my task efficiently"

        # 내러티브 생성
        narrative = template.format(
            actor=actor,
            action=action,
            benefit=primary_benefit
        )

        return narrative

    def _create_story_title(self, action: str, obj: Optional[str]) -> str:
        """스토리 제목 생성"""
        if obj:
            # 동작 + 객체
            title = f"{action.title()} {obj.title()}"
        else:
            # 동작만
            title = action.title()

        # 제목 정리
        title = title.replace('_', ' ').strip()

        # 최대 길이 제한
        if len(title) > 50:
            title = title[:47] + "..."

        return title
```

**수용 기준 생성기**:

```python
# backend/src/agents/implementations/parser/acceptance_criteria_generator.py
class AcceptanceCriteriaGenerator:
    """수용 기준 자동 생성"""

    def __init__(self):
        self.criteria_templates = {
            'given_when_then': {
                'template': "GIVEN {context}\nWHEN {action}\nTHEN {outcome}",
                'priority': 1
            },
            'checklist': {
                'template': "□ {criterion}",
                'priority': 2
            },
            'rule': {
                'template': "The system shall {behavior} when {condition}",
                'priority': 3
            }
        }

    async def generate(
        self,
        story_data: Dict[str, Any],
        requirement: ParsedRequirement
    ) -> List[str]:
        """수용 기준 생성"""

        criteria = []

        # Given-When-Then 형식
        gwt_criteria = await self._generate_gwt_criteria(story_data)
        criteria.extend(gwt_criteria)

        # 체크리스트 형식
        checklist_criteria = await self._generate_checklist_criteria(
            story_data,
            requirement
        )
        criteria.extend(checklist_criteria)

        # 검증 규칙
        validation_rules = await self._generate_validation_rules(
            story_data,
            requirement
        )
        criteria.extend(validation_rules)

        # 중복 제거 및 정렬
        criteria = list(dict.fromkeys(criteria))

        return criteria[:10]  # 최대 10개

    async def _generate_gwt_criteria(
        self,
        story_data: Dict[str, Any]
    ) -> List[str]:
        """Given-When-Then 형식 기준 생성"""

        criteria = []

        # 기본 성공 시나리오
        basic_criterion = (
            f"GIVEN I am a logged-in {story_data['actor']}\n"
            f"WHEN I {story_data['action']}\n"
            f"THEN I should see confirmation of the action"
        )
        criteria.append(basic_criterion)

        # 에러 시나리오
        error_criterion = (
            f"GIVEN I am a {story_data['actor']} with invalid permissions\n"
            f"WHEN I attempt to {story_data['action']}\n"
            f"THEN I should see an error message"
        )
        criteria.append(error_criterion)

        # 데이터 검증 시나리오
        if 'object' in story_data and story_data['object']:
            validation_criterion = (
                f"GIVEN I provide invalid {story_data['object']} data\n"
                f"WHEN I {story_data['action']}\n"
                f"THEN I should see validation errors"
            )
            criteria.append(validation_criterion)

        return criteria
```

**스토리 포인트 추정기**:

```python
class StoryPointEstimator:
    """스토리 포인트 자동 추정"""

    def __init__(self):
        self.complexity_factors = {
            'ui_complexity': {
                'simple': 1,    # 단순 폼, 리스트
                'medium': 2,    # 인터랙티브 UI
                'complex': 3    # 복잡한 대시보드
            },
            'business_logic': {
                'simple': 1,    # CRUD 작업
                'medium': 3,    # 비즈니스 규칙
                'complex': 5    # 복잡한 알고리즘
            },
            'integration': {
                'none': 0,
                'simple': 2,    # 단일 API 호출
                'complex': 5    # 여러 시스템 통합
            },
            'data_complexity': {
                'simple': 1,    # 단일 엔티티
                'medium': 2,    # 여러 엔티티
                'complex': 3    # 복잡한 관계
            }
        }

        self.fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21]

    async def estimate(
        self,
        story_data: Dict[str, Any],
        requirement: ParsedRequirement
    ) -> int:
        """스토리 포인트 추정"""

        # 복잡도 요소 분석
        ui_complexity = await self._assess_ui_complexity(story_data)
        logic_complexity = await self._assess_logic_complexity(story_data)
        integration_complexity = await self._assess_integration_complexity(requirement)
        data_complexity = await self._assess_data_complexity(story_data)

        # 총 복잡도 점수
        total_score = (
            self.complexity_factors['ui_complexity'][ui_complexity] +
            self.complexity_factors['business_logic'][logic_complexity] +
            self.complexity_factors['integration'][integration_complexity] +
            self.complexity_factors['data_complexity'][data_complexity]
        )

        # 피보나치 수열로 매핑
        story_points = self._map_to_fibonacci(total_score)

        return story_points

    def _map_to_fibonacci(self, score: int) -> int:
        """점수를 피보나치 수열로 매핑"""
        if score <= 3:
            return 1
        elif score <= 5:
            return 2
        elif score <= 7:
            return 3
        elif score <= 10:
            return 5
        elif score <= 14:
            return 8
        elif score <= 19:
            return 13
        else:
            return 21
```

**검증 기준**:

- [ ] 사용자 스토리 형식 준수
- [ ] 수용 기준 자동 생성
- [ ] 스토리 포인트 추정 정확도
- [ ] 에픽 그룹화 기능

#### SubTask 4.22.3: 데이터 모델 및 API 추출기

**담당자**: 데이터 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/data_model_extractor.py
from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class DataModel:
    name: str
    fields: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    constraints: List[str]
    indexes: List[str]
    description: Optional[str]

@dataclass
class APIEndpoint:
    method: str
    path: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    response: Dict[str, Any]
    authentication: bool
    rate_limit: Optional[str]

class DataModelExtractor:
    """데이터 모델 추출기"""

    def __init__(self):
        self.field_type_mapper = {
            'id': 'uuid',
            'name': 'string',
            'email': 'email',
            'password': 'password',
            'date': 'date',
            'created_at': 'timestamp',
            'updated_at': 'timestamp',
            'price': 'decimal',
            'amount': 'decimal',
            'quantity': 'integer',
            'count': 'integer',
            'status': 'enum',
            'description': 'text',
            'content': 'text',
            'url': 'url',
            'phone': 'phone',
            'address': 'object'
        }

        self.relationship_patterns = [
            r'(\w+)\s+has\s+(many|one)\s+(\w+)',
            r'(\w+)\s+belongs\s+to\s+(\w+)',
            r'(\w+)\s+and\s+(\w+)\s+are\s+related',
            r'(\w+)\s+references?\s+(\w+)'
        ]

    async def extract_data_models(
        self,
        text: str,
        requirements: List[ParsedRequirement]
    ) -> List[DataModel]:
        """텍스트에서 데이터 모델 추출"""

        models = []

        # 명시적 모델 정의 추출
        explicit_models = await self._extract_explicit_models(text)
        models.extend(explicit_models)

        # 암시적 모델 추출
        implicit_models = await self._extract_implicit_models(text, requirements)
        models.extend(implicit_models)

        # 관계 분석
        models = await self._analyze_relationships(models, text)

        # 제약사항 추가
        models = await self._add_constraints(models, requirements)

        # 중복 제거 및 병합
        models = self._merge_duplicate_models(models)

        return models

    async def _extract_explicit_models(self, text: str) -> List[DataModel]:
        """명시적으로 정의된 모델 추출"""

        models = []

        # 패턴: "User entity with fields: id, name, email"
        entity_pattern = r'(\w+)\s+(?:entity|model|table)\s+with\s+fields?:?\s*([^.]+?)(?:\.|$)'

        matches = re.finditer(entity_pattern, text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            model_name = match.group(1)
            fields_text = match.group(2)

            # 필드 파싱
            fields = await self._parse_fields(fields_text)

            model = DataModel(
                name=model_name,
                fields=fields,
                relationships=[],
                constraints=[],
                indexes=[],
                description=f"Extracted from: {match.group(0)[:100]}..."
            )

            models.append(model)

        return models

    async def _parse_fields(self, fields_text: str) -> List[Dict[str, Any]]:
        """필드 텍스트 파싱"""

        fields = []

        # 필드 분리 (쉼표, 세미콜론, 줄바꿈)
        field_items = re.split(r'[,;\n]', fields_text)

        for item in field_items:
            item = item.strip()
            if not item:
                continue

            # 필드 정보 추출
            field_info = self._extract_field_info(item)
            if field_info:
                fields.append(field_info)

        return fields

    def _extract_field_info(self, field_text: str) -> Optional[Dict[str, Any]]:
        """필드 정보 추출"""

        # 패턴: "field_name (type)" 또는 "field_name: type"
        patterns = [
            r'(\w+)\s*\((\w+)\)',
            r'(\w+)\s*:\s*(\w+)',
            r'(\w+)\s+(\w+)',
            r'(\w+)'  # 타입 없이 이름만
        ]

        for pattern in patterns:
            match = re.match(pattern, field_text.strip())
            if match:
                field_name = match.group(1)
                field_type = match.group(2) if match.lastindex >= 2 else None

                # 타입 추론
                if not field_type:
                    field_type = self._infer_field_type(field_name)

                return {
                    'name': field_name,
                    'type': field_type,
                    'required': self._is_required_field(field_name),
                    'unique': self._is_unique_field(field_name),
                    'indexed': self._should_index_field(field_name)
                }

        return None

    def _infer_field_type(self, field_name: str) -> str:
        """필드 이름에서 타입 추론"""

        field_lower = field_name.lower()

        # 타입 매핑 확인
        for key, type_value in self.field_type_mapper.items():
            if key in field_lower:
                return type_value

        # 기본 타입
        return 'string'
```

**API 추출기**:

```python
# backend/src/agents/implementations/parser/api_extractor.py
class APIExtractor:
    """API 엔드포인트 추출기"""

    def __init__(self):
        self.http_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.common_paths = {
            'list': '/{resource}',
            'create': '/{resource}',
            'get': '/{resource}/{id}',
            'update': '/{resource}/{id}',
            'delete': '/{resource}/{id}',
            'search': '/{resource}/search',
            'bulk': '/{resource}/bulk'
        }

    async def extract_api_endpoints(
        self,
        text: str,
        data_models: List[DataModel]
    ) -> List[APIEndpoint]:
        """API 엔드포인트 추출"""

        endpoints = []

        # 명시적 API 정의 추출
        explicit_endpoints = await self._extract_explicit_endpoints(text)
        endpoints.extend(explicit_endpoints)

        # 데이터 모델에서 CRUD API 생성
        crud_endpoints = await self._generate_crud_endpoints(data_models)
        endpoints.extend(crud_endpoints)

        # 비즈니스 로직 API 추출
        business_endpoints = await self._extract_business_endpoints(text)
        endpoints.extend(business_endpoints)

        # API 문서 보강
        endpoints = await self._enrich_api_documentation(endpoints, text)

        # 중복 제거
        endpoints = self._deduplicate_endpoints(endpoints)

        return endpoints

    async def _extract_explicit_endpoints(self, text: str) -> List[APIEndpoint]:
        """명시적으로 정의된 API 추출"""

        endpoints = []

        # 패턴: "GET /api/products"
        api_pattern = r'(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/\-{}]+)'

        matches = re.finditer(api_pattern, text, re.IGNORECASE)

        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)

            # 파라미터 추출
            parameters = self._extract_path_parameters(path)

            # 쿼리 파라미터 추출
            query_params = await self._extract_query_parameters(text, path)

            endpoint = APIEndpoint(
                method=method,
                path=path,
                description=self._generate_endpoint_description(method, path),
                parameters=parameters + query_params,
                request_body=self._infer_request_body(method, path),
                response=self._infer_response(method, path),
                authentication=True,  # 기본값
                rate_limit=None
            )

            endpoints.append(endpoint)

        return endpoints

    async def _generate_crud_endpoints(
        self,
        data_models: List[DataModel]
    ) -> List[APIEndpoint]:
        """데이터 모델에서 CRUD API 생성"""

        endpoints = []

        for model in data_models:
            resource_name = self._pluralize(model.name.lower())

            # List/Create
            endpoints.append(APIEndpoint(
                method='GET',
                path=f'/api/{resource_name}',
                description=f'List all {resource_name}',
                parameters=[
                    {'name': 'page', 'type': 'integer', 'required': False},
                    {'name': 'limit', 'type': 'integer', 'required': False},
                    {'name': 'sort', 'type': 'string', 'required': False}
                ],
                request_body=None,
                response={
                    'type': 'array',
                    'items': self._model_to_schema(model)
                },
                authentication=True,
                rate_limit='100/hour'
            ))

            endpoints.append(APIEndpoint(
                method='POST',
                path=f'/api/{resource_name}',
                description=f'Create a new {model.name}',
                parameters=[],
                request_body=self._model_to_schema(model, exclude=['id']),
                response=self._model_to_schema(model),
                authentication=True,
                rate_limit='50/hour'
            ))

            # Get/Update/Delete
            endpoints.append(APIEndpoint(
                method='GET',
                path=f'/api/{resource_name}/{{id}}',
                description=f'Get {model.name} by ID',
                parameters=[
                    {'name': 'id', 'type': 'uuid', 'required': True, 'in': 'path'}
                ],
                request_body=None,
                response=self._model_to_schema(model),
                authentication=True,
                rate_limit='1000/hour'
            ))

            # ... (PUT, DELETE 엔드포인트도 유사하게 생성)

        return endpoints

    def _model_to_schema(
        self,
        model: DataModel,
        exclude: List[str] = None
    ) -> Dict[str, Any]:
        """데이터 모델을 API 스키마로 변환"""

        exclude = exclude or []

        properties = {}
        required = []

        for field in model.fields:
            if field['name'] not in exclude:
                properties[field['name']] = {
                    'type': self._map_field_type_to_json(field['type']),
                    'description': f"{model.name} {field['name']}"
                }

                if field.get('required', False):
                    required.append(field['name'])

        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }
```

**검증 기준**:

- [ ] 데이터 모델 추출 정확도
- [ ] API 엔드포인트 자동 생성
- [ ] 필드 타입 추론 정확도
- [ ] CRUD 패턴 인식

#### SubTask 4.22.4: 요구사항 검증 및 완성도 체크

**담당자**: QA 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/requirement_validator.py
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    category: str
    message: str
    requirement_id: Optional[str]
    suggestion: Optional[str]

class RequirementValidator:
    """요구사항 검증 및 완성도 체크"""

    def __init__(self):
        self.validation_rules = [
            AmbiguityChecker(),
            CompletenessChecker(),
            ConsistencyChecker(),
            FeasibilityChecker(),
            TestabilityChecker(),
            TracabilityChecker()
        ]

        self.quality_metrics = {
            'clarity': 0,
            'completeness': 0,
            'consistency': 0,
            'feasibility': 0,
            'testability': 0,
            'traceability': 0
        }

    async def validate_requirements(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """요구사항 전체 검증"""

        validation_results = {
            'issues': [],
            'metrics': {},
            'summary': {},
            'recommendations': []
        }

        # 모든 요구사항 수집
        all_requirements = self._collect_all_requirements(parsed_project)

        # 각 검증 규칙 적용
        for rule in self.validation_rules:
            issues = await rule.validate(all_requirements, parsed_project)
            validation_results['issues'].extend(issues)

        # 품질 메트릭 계산
        validation_results['metrics'] = await self._calculate_quality_metrics(
            all_requirements,
            validation_results['issues']
        )

        # 요약 생성
        validation_results['summary'] = self._generate_summary(
            validation_results['issues'],
            validation_results['metrics']
        )

        # 개선 권장사항
        validation_results['recommendations'] = await self._generate_recommendations(
            validation_results['issues'],
            parsed_project
        )

        return validation_results

    async def _calculate_quality_metrics(
        self,
        requirements: List[ParsedRequirement],
        issues: List[ValidationIssue]
    ) -> Dict[str, float]:
        """품질 메트릭 계산"""

        total_reqs = len(requirements)
        if total_reqs == 0:
            return {metric: 0.0 for metric in self.quality_metrics}

        # 각 카테고리별 이슈 카운트
        issue_counts = {}
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                issue_counts[issue.category] = issue_counts.get(issue.category, 0) + 1

        # 메트릭 계산
        metrics = {}

        # 명확성 (Clarity)
        ambiguity_issues = issue_counts.get('ambiguity', 0)
        metrics['clarity'] = max(0, 1 - (ambiguity_issues / total_reqs))

        # 완전성 (Completeness)
        missing_count = sum(1 for req in requirements if not req.acceptance_criteria)
        metrics['completeness'] = 1 - (missing_count / total_reqs)

        # 일관성 (Consistency)
        consistency_issues = issue_counts.get('consistency', 0)
        metrics['consistency'] = max(0, 1 - (consistency_issues / total_reqs))

        # 실현가능성 (Feasibility)
        feasibility_issues = issue_counts.get('feasibility', 0)
        metrics['feasibility'] = max(0, 1 - (feasibility_issues / total_reqs))

        # 테스트가능성 (Testability)
        testable_count = sum(1 for req in requirements if req.acceptance_criteria)
        metrics['testability'] = testable_count / total_reqs

        # 추적가능성 (Traceability)
        traced_count = sum(1 for req in requirements if req.id and req.dependencies is not None)
        metrics['traceability'] = traced_count / total_reqs

        # 전체 품질 점수
        metrics['overall'] = sum(metrics.values()) / len(metrics)

        return metrics
```

**검증 규칙 구현**:

```python
# backend/src/agents/implementations/parser/validation_rules.py
class AmbiguityChecker:
    """모호성 검사기"""

    def __init__(self):
        self.ambiguous_terms = [
            'appropriate', 'adequate', 'as needed', 'as required',
            'efficient', 'fast', 'user-friendly', 'intuitive',
            'secure', 'scalable', 'flexible', 'robust',
            'etc', 'and so on', 'various', 'multiple',
            'some', 'many', 'few', 'several'
        ]

        self.vague_quantifiers = [
            'high', 'low', 'good', 'bad', 'acceptable',
            'reasonable', 'sufficient', 'optimal', 'minimal'
        ]

    async def validate(
        self,
        requirements: List[ParsedRequirement],
        project: ParsedProject
    ) -> List[ValidationIssue]:
        """모호한 요구사항 검사"""

        issues = []

        for req in requirements:
            # 모호한 용어 검사
            ambiguous_found = self._check_ambiguous_terms(req.description)
            if ambiguous_found:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='ambiguity',
                    message=f"Ambiguous terms found: {', '.join(ambiguous_found)}",
                    requirement_id=req.id,
                    suggestion="Use specific, measurable terms instead"
                ))

            # 정량화되지 않은 요구사항
            if self._lacks_quantification(req):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='ambiguity',
                    message="Requirement lacks specific quantification",
                    requirement_id=req.id,
                    suggestion="Add specific numbers, thresholds, or ranges"
                ))

        return issues

    def _check_ambiguous_terms(self, text: str) -> List[str]:
        """모호한 용어 확인"""
        text_lower = text.lower()
        found_terms = []

        for term in self.ambiguous_terms + self.vague_quantifiers:
            if term in text_lower:
                found_terms.append(term)

        return found_terms

class CompletenessChecker:
    """완전성 검사기"""

    async def validate(
        self,
        requirements: List[ParsedRequirement],
        project: ParsedProject
    ) -> List[ValidationIssue]:
        """요구사항 완전성 검사"""

        issues = []

        # 필수 섹션 확인
        if not project.functional_requirements:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category='completeness',
                message="No functional requirements found",
                requirement_id=None,
                suggestion="Add functional requirements describing what the system should do"
            ))

        if not project.non_functional_requirements:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category='completeness',
                message="No non-functional requirements found",
                requirement_id=None,
                suggestion="Add performance, security, and usability requirements"
            ))

        # 각 요구사항의 완전성 확인
        for req in requirements:
            if not req.acceptance_criteria:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='completeness',
                    message="Missing acceptance criteria",
                    requirement_id=req.id,
                    suggestion="Add specific criteria to verify requirement completion"
                ))

            if req.priority == 'TBD' or not req.priority:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category='completeness',
                    message="Priority not assigned",
                    requirement_id=req.id,
                    suggestion="Assign priority: critical, high, medium, or low"
                ))

        return issues
```

**검증 보고서 생성기**:

```python
class ValidationReportGenerator:
    """검증 보고서 생성"""

    async def generate_report(
        self,
        validation_results: Dict[str, Any],
        parsed_project: ParsedProject
    ) -> str:
        """HTML 검증 보고서 생성"""

        report_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Requirements Validation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
                .metric { display: inline-block; margin: 10px; }
                .issue { margin: 10px 0; padding: 10px; border-left: 3px solid; }
                .error { border-color: #ff4444; background: #ffeeee; }
                .warning { border-color: #ffaa00; background: #fff8ee; }
                .info { border-color: #0088ff; background: #eef8ff; }
                .chart { width: 100%; height: 300px; }
            </style>
        </head>
        <body>
            <h1>Requirements Validation Report</h1>

            <div class="summary">
                <h2>Summary</h2>
                <p>Total Requirements: {total_requirements}</p>
                <p>Quality Score: {quality_score:.1%}</p>
                <p>Issues Found: {total_issues} ({errors} errors, {warnings} warnings)</p>
            </div>

            <h2>Quality Metrics</h2>
            <div id="metricsChart" class="chart"></div>

            <h2>Issues</h2>
            {issues_html}

            <h2>Recommendations</h2>
            <ul>
                {recommendations_html}
            </ul>

            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                {chart_script}
            </script>
        </body>
        </html>
        """

        # 데이터 준비
        total_reqs = len(self._collect_all_requirements(parsed_project))
        quality_score = validation_results['metrics'].get('overall', 0)

        issues_by_severity = self._group_issues_by_severity(
            validation_results['issues']
        )

        # HTML 생성
        return report_template.format(
            total_requirements=total_reqs,
            quality_score=quality_score,
            total_issues=len(validation_results['issues']),
            errors=len(issues_by_severity.get('error', [])),
            warnings=len(issues_by_severity.get('warning', [])),
            issues_html=self._generate_issues_html(validation_results['issues']),
            recommendations_html=self._generate_recommendations_html(
                validation_results['recommendations']
            ),
            chart_script=self._generate_chart_script(validation_results['metrics'])
        )
```

**검증 기준**:

- [ ] 모든 검증 규칙 구현
- [ ] 품질 메트릭 계산 정확도
- [ ] 검증 보고서 생성
- [ ] 개선 권장사항 제공

### Task 4.23: Parser Agent 도메인 특화 파싱

#### SubTask 4.23.1: 도메인별 용어 사전 구축

**담당자**: 도메인 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/domain_dictionary.py
from typing import Dict, List, Any, Set
import json
from dataclasses import dataclass

@dataclass
class DomainTerm:
    term: str
    canonical_form: str
    aliases: List[str]
    definition: str
    category: str
    related_terms: List[str]
    context_examples: List[str]

class DomainDictionary:
    """도메인별 용어 사전"""

    def __init__(self):
        self.dictionaries = {
            'e-commerce': ECommerceDictionary(),
            'healthcare': HealthcareDictionary(),
            'finance': FinanceDictionary(),
            'education': EducationDictionary(),
            'social_media': SocialMediaDictionary(),
            'iot': IoTDictionary(),
            'gaming': GamingDictionary(),
            'enterprise': EnterpriseDictionary()
        }

        self.general_terms = self._load_general_terms()
        self.abbreviations = self._load_abbreviations()

    async def get_domain_terms(
        self,
        domain: str
    ) -> Dict[str, DomainTerm]:
        """특정 도메인의 용어 사전 반환"""

        if domain in self.dictionaries:
            return await self.dictionaries[domain].get_terms()

        # 도메인이 없으면 일반 용어만
        return self.general_terms

    async def expand_term(
        self,
        term: str,
        domain: str,
        context: str
    ) -> DomainTerm:
        """용어 확장 및 정규화"""

        # 도메인 사전에서 검색
        domain_terms = await self.get_domain_terms(domain)

        # 정확한 매치
        if term.lower() in domain_terms:
            return domain_terms[term.lower()]

        # 별칭 검색
        for dt in domain_terms.values():
            if term.lower() in [alias.lower() for alias in dt.aliases]:
                return dt

        # 약어 확장
        if term.upper() in self.abbreviations:
            expanded = self.abbreviations[term.upper()]
            if expanded.lower() in domain_terms:
                return domain_terms[expanded.lower()]

        # 컨텍스트 기반 추론
        inferred_term = await self._infer_from_context(term, context, domain)
        if inferred_term:
            return inferred_term

        # 기본 용어 생성
        return DomainTerm(
            term=term,
            canonical_form=term,
            aliases=[],
            definition="Unknown term",
            category="general",
            related_terms=[],
            context_examples=[]
        )

class ECommerceDictionary:
    """전자상거래 도메인 사전"""

    def __init__(self):
        self.terms = {
            'cart': DomainTerm(
                term='cart',
                canonical_form='shopping_cart',
                aliases=['basket', 'shopping basket', 'bag'],
                definition='Temporary storage for items customer intends to purchase',
                category='customer_feature',
                related_terms=['checkout', 'order', 'wishlist'],
                context_examples=[
                    'add item to cart',
                    'view shopping cart',
                    'empty cart'
                ]
            ),
            'checkout': DomainTerm(
                term='checkout',
                canonical_form='checkout_process',
                aliases=['check out', 'purchase', 'buy'],
                definition='Process of completing a purchase transaction',
                category='transaction',
                related_terms=['payment', 'shipping', 'order'],
                context_examples=[
                    'proceed to checkout',
                    'guest checkout',
                    'express checkout'
                ]
            ),
            'sku': DomainTerm(
                term='sku',
                canonical_form='stock_keeping_unit',
                aliases=['SKU', 'product code', 'item number'],
                definition='Unique identifier for each distinct product and service',
                category='inventory',
                related_terms=['barcode', 'upc', 'product variant'],
                context_examples=[
                    'SKU management',
                    'generate SKU',
                    'SKU tracking'
                ]
            ),
            'fulfillment': DomainTerm(
                term='fulfillment',
                canonical_form='order_fulfillment',
                aliases=['fulfilment', 'shipping', 'delivery'],
                definition='Process of receiving, processing and delivering orders',
                category='operations',
                related_terms=['warehouse', 'logistics', 'tracking'],
                context_examples=[
                    'order fulfillment center',
                    'fulfillment status',
                    'dropship fulfillment'
                ]
            )
        }

    async def get_terms(self) -> Dict[str, DomainTerm]:
        """전자상거래 용어 반환"""
        return self.terms

class HealthcareDictionary:
    """헬스케어 도메인 사전"""

    def __init__(self):
        self.terms = {
            'ehr': DomainTerm(
                term='ehr',
                canonical_form='electronic_health_record',
                aliases=['EHR', 'EMR', 'electronic medical record'],
                definition='Digital version of patient health information',
                category='health_it',
                related_terms=['patient record', 'medical history', 'clinical data'],
                context_examples=[
                    'EHR integration',
                    'access patient EHR',
                    'update medical records'
                ]
            ),
            'hipaa': DomainTerm(
                term='hipaa',
                canonical_form='health_insurance_portability_accountability_act',
                aliases=['HIPAA', 'hipaa compliance'],
                definition='US law protecting patient health information privacy',
                category='compliance',
                related_terms=['phi', 'privacy', 'security'],
                context_examples=[
                    'HIPAA compliant system',
                    'HIPAA audit',
                    'HIPAA training'
                ]
            ),
            'phi': DomainTerm(
                term='phi',
                canonical_form='protected_health_information',
                aliases=['PHI', 'patient data', 'health data'],
                definition='Any health information that can identify an individual',
                category='data_privacy',
                related_terms=['pii', 'medical records', 'confidentiality'],
                context_examples=[
                    'PHI encryption',
                    'access to PHI',
                    'PHI disclosure'
                ]
            )
        }
```

**도메인 패턴 인식기**:

```python
# backend/src/agents/implementations/parser/domain_pattern_recognizer.py
class DomainPatternRecognizer:
    """도메인 특화 패턴 인식"""

    def __init__(self):
        self.domain_patterns = {
            'e-commerce': {
                'patterns': [
                    r'(add|remove)\s+to\s+(cart|basket)',
                    r'(checkout|payment)\s+process',
                    r'product\s+(catalog|listing|search)',
                    r'(order|shipping)\s+tracking',
                    r'inventory\s+management',
                    r'customer\s+reviews?'
                ],
                'keywords': [
                    'product', 'cart', 'order', 'payment',
                    'shipping', 'customer', 'inventory'
                ]
            },
            'healthcare': {
                'patterns': [
                    r'patient\s+(record|data|information)',
                    r'(appointment|scheduling)\s+system',
                    r'(medical|clinical)\s+data',
                    r'(prescription|medication)\s+management',
                    r'(lab|test)\s+results?',
                    r'hipaa\s+complian(t|ce)'
                ],
                'keywords': [
                    'patient', 'doctor', 'appointment', 'medical',
                    'clinical', 'diagnosis', 'treatment'
                ]
            },
            'finance': {
                'patterns': [
                    r'(account|transaction)\s+management',
                    r'(payment|transfer)\s+processing',
                    r'(balance|statement)\s+inquiry',
                    r'(fraud|risk)\s+detection',
                    r'(loan|credit)\s+application',
                    r'regulatory\s+compliance'
                ],
                'keywords': [
                    'account', 'transaction', 'payment', 'balance',
                    'transfer', 'investment', 'portfolio'
                ]
            }
        }

    async def identify_domain(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, float]:
        """텍스트에서 도메인 식별"""

        domain_scores = {}

        for domain, config in self.domain_patterns.items():
            score = 0

            # 패턴 매칭
            for pattern in config['patterns']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches) * 2  # 패턴 매치는 가중치 2

            # 키워드 매칭
            text_lower = text.lower()
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 1

            # 정규화
            domain_scores[domain] = score / (len(config['patterns']) + len(config['keywords']))

        # 컨텍스트 고려
        if context and 'domain_hint' in context:
            hint_domain = context['domain_hint']
            if hint_domain in domain_scores:
                domain_scores[hint_domain] *= 1.5

        # 최고 점수 도메인
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            confidence = domain_scores[best_domain]

            # 임계값 확인
            if confidence > 0.3:
                return best_domain, confidence

        return 'general', 0.0
```

**검증 기준**:

- [ ] 주요 도메인 용어 사전 구축
- [ ] 용어 확장 및 정규화
- [ ] 도메인 자동 인식
- [ ] 별칭 및 약어 처리

#### SubTask 4.23.2: 도메인 특화 요구사항 템플릿

**담당자**: 도메인 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/domain_templates.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class RequirementTemplate:
    domain: str
    category: str
    name: str
    description: str
    template_structure: Dict[str, Any]
    example: str
    validation_rules: List[Dict[str, Any]]

class DomainTemplateManager:
    """도메인별 요구사항 템플릿 관리"""

    def __init__(self):
        self.templates = {
            'e-commerce': self._load_ecommerce_templates(),
            'healthcare': self._load_healthcare_templates(),
            'finance': self._load_finance_templates(),
            'education': self._load_education_templates()
        }

    def _load_ecommerce_templates(self) -> List[RequirementTemplate]:
        """전자상거래 템플릿"""
        return [
            RequirementTemplate(
                domain='e-commerce',
                category='product_management',
                name='Product Catalog Requirements',
                description='Requirements for product listing and management',
                template_structure={
                    'product_attributes': [
                        'name', 'description', 'price', 'sku',
                        'category', 'images', 'variants'
                    ],
                    'search_capabilities': [
                        'text_search', 'filter_by_category',
                        'filter_by_price', 'sort_options'
                    ],
                    'inventory_tracking': [
                        'stock_levels', 'low_stock_alerts',
                        'out_of_stock_handling'
                    ]
                },
                example="""
                The system shall allow vendors to manage product catalogs with:
                - Product creation with name, description, price, SKU
                - Multiple product images (up to 10)
                - Product variants (size, color)
                - Category assignment (multi-level)
                - Inventory tracking with real-time updates
                - Search functionality with filters
                """,
                validation_rules=[
                    {
                        'rule': 'product_must_have_sku',
                        'message': 'Each product must have unique SKU'
                    },
                    {
                        'rule': 'price_must_be_positive',
                        'message': 'Product price must be greater than 0'
                    }
                ]
            ),
            RequirementTemplate(
                domain='e-commerce',
                category='checkout_process',
                name='Checkout Flow Requirements',
                description='Requirements for checkout and payment process',
                template_structure={
                    'checkout_steps': [
                        'cart_review', 'shipping_address',
                        'shipping_method', 'payment_info',
                        'order_review', 'confirmation'
                    ],
                    'payment_methods': [
                        'credit_card', 'debit_card',
                        'paypal', 'apple_pay', 'google_pay'
                    ],
                    'shipping_options': [
                        'standard', 'express', 'overnight'
                    ],
                    'guest_checkout': True,
                    'save_payment_info': True
                },
                example="""
                The checkout process shall include:
                - Guest checkout option
                - Multiple payment methods (Credit card, PayPal, etc.)
                - Address validation
                - Shipping cost calculation
                - Order summary before confirmation
                - Email confirmation with order details
                """,
                validation_rules=[
                    {
                        'rule': 'payment_security',
                        'message': 'Payment processing must be PCI compliant'
                    }
                ]
            )
        ]

    def _load_healthcare_templates(self) -> List[RequirementTemplate]:
        """헬스케어 템플릿"""
        return [
            RequirementTemplate(
                domain='healthcare',
                category='patient_management',
                name='Patient Record Requirements',
                description='Requirements for patient data management',
                template_structure={
                    'patient_info': [
                        'demographics', 'contact_info',
                        'emergency_contacts', 'insurance'
                    ],
                    'medical_history': [
                        'conditions', 'medications',
                        'allergies', 'procedures'
                    ],
                    'clinical_data': [
                        'vitals', 'lab_results',
                        'imaging', 'notes'
                    ],
                    'compliance': [
                        'hipaa', 'audit_trail',
                        'access_control', 'encryption'
                    ]
                },
                example="""
                The patient management system shall:
                - Store patient demographics securely
                - Track medical history including conditions and medications
                - Record vital signs with timestamps
                - Manage lab results and imaging studies
                - Maintain HIPAA compliance
                - Provide role-based access control
                - Keep audit trail of all data access
                """,
                validation_rules=[
                    {
                        'rule': 'hipaa_compliance',
                        'message': 'All PHI must be encrypted at rest and in transit'
                    },
                    {
                        'rule': 'audit_required',
                        'message': 'All patient data access must be logged'
                    }
                ]
            )
        ]

    async def apply_template(
        self,
        requirement_text: str,
        domain: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """템플릿을 적용하여 요구사항 구조화"""

        # 적절한 템플릿 찾기
        templates = self.templates.get(domain, [])

        if category:
            templates = [t for t in templates if t.category == category]

        if not templates:
            return {'error': 'No matching template found'}

        # 가장 적합한 템플릿 선택
        best_template = await self._select_best_template(
            requirement_text,
            templates
        )

        # 템플릿 적용
        structured_req = await self._apply_template_structure(
            requirement_text,
            best_template
        )

        # 검증 규칙 적용
        validation_results = await self._validate_against_template(
            structured_req,
            best_template
        )

        return {
            'template_used': best_template.name,
            'structured_requirement': structured_req,
            'validation_results': validation_results
        }
```

**도메인 규칙 엔진**:

```python
# backend/src/agents/implementations/parser/domain_rule_engine.py
class DomainRuleEngine:
    """도메인별 비즈니스 규칙 처리"""

    def __init__(self):
        self.rule_sets = {
            'e-commerce': ECommerceRules(),
            'healthcare': HealthcareRules(),
            'finance': FinanceRules()
        }

    async def apply_domain_rules(
        self,
        requirements: List[ParsedRequirement],
        domain: str
    ) -> List[ParsedRequirement]:
        """도메인 규칙 적용"""

        if domain not in self.rule_sets:
            return requirements

        rule_set = self.rule_sets[domain]

        # 각 요구사항에 규칙 적용
        enhanced_requirements = []

        for req in requirements:
            # 필수 요구사항 추가
            mandatory_reqs = await rule_set.get_mandatory_requirements(req)
            enhanced_requirements.extend(mandatory_reqs)

            # 규정 준수 요구사항
            compliance_reqs = await rule_set.get_compliance_requirements(req)
            enhanced_requirements.extend(compliance_reqs)

            # 원본 요구사항 보강
            enhanced_req = await rule_set.enhance_requirement(req)
            enhanced_requirements.append(enhanced_req)

        return enhanced_requirements

class ECommerceRules:
    """전자상거래 도메인 규칙"""

    async def get_mandatory_requirements(
        self,
        requirement: ParsedRequirement
    ) -> List[ParsedRequirement]:
        """필수 요구사항 생성"""

        mandatory = []

        # 결제 관련 요구사항이면 PCI 준수 추가
        if 'payment' in requirement.description.lower():
            mandatory.append(ParsedRequirement(
                id=f"{requirement.id}-PCI",
                type=RequirementType.NON_FUNCTIONAL,
                category='security',
                description="Payment processing must be PCI DSS compliant",
                priority='critical',
                acceptance_criteria=[
                    "All payment data encrypted with AES-256",
                    "No storage of CVV codes",
                    "Tokenization for stored payment methods"
                ]
            ))

        # 개인정보 처리 요구사항이면 GDPR 추가
        if any(term in requirement.description.lower()
               for term in ['user data', 'personal information', 'customer data']):
            mandatory.append(ParsedRequirement(
                id=f"{requirement.id}-GDPR",
                type=RequirementType.NON_FUNCTIONAL,
                category='compliance',
                description="Personal data handling must be GDPR compliant",
                priority='high',
                acceptance_criteria=[
                    "User consent for data collection",
                    "Right to data deletion",
                    "Data portability support"
                ]
            ))

        return mandatory
```

**검증 기준**:

- [ ] 도메인별 템플릿 구현
- [ ] 템플릿 자동 매칭
- [ ] 도메인 규칙 적용
- [ ] 규정 준수 요구사항 자동 추가

#### SubTask 4.23.3: 업계 표준 매핑 시스템

**담당자**: 표준 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/industry_standards.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class IndustryStandard:
    name: str
    acronym: str
    domain: str
    category: str
    description: str
    requirements: List[Dict[str, Any]]
    references: List[str]

class IndustryStandardsMapper:
    """업계 표준 매핑 시스템"""

    def __init__(self):
        self.standards = {
            'ISO_27001': IndustryStandard(
                name='ISO 27001',
                acronym='ISO27001',
                domain='general',
                category='information_security',
                description='Information security management systems',
                requirements=[
                    {
                        'id': 'A.5.1.1',
                        'title': 'Policies for information security',
                        'description': 'Information security policy and topic-specific policies'
                    },
                    {
                        'id': 'A.8.2.3',
                        'title': 'Handling of assets',
                        'description': 'Procedures for handling assets in accordance with classification'
                    }
                ],
                references=[
                    'https://www.iso.org/standard/27001'
                ]
            ),
            'PCI_DSS': IndustryStandard(
                name='Payment Card Industry Data Security Standard',
                acronym='PCI-DSS',
                domain='e-commerce',
                category='payment_security',
                description='Security standards for payment card data',
                requirements=[
                    {
                        'id': '3.4',
                        'title': 'Render PAN unreadable',
                        'description': 'Render PAN unreadable anywhere it is stored'
                    },
                    {
                        'id': '8.2.3',
                        'title': 'Strong passwords',
                        'description': 'Passwords must meet minimum complexity requirements'
                    }
                ],
                references=[
                    'https://www.pcisecuritystandards.org/'
                ]
            ),
            'HIPAA': IndustryStandard(
                name='Health Insurance Portability and Accountability Act',
                acronym='HIPAA',
                domain='healthcare',
                category='privacy_security',
                description='Standards for protecting health information',
                requirements=[
                    {
                        'id': '164.308(a)(1)',
                        'title': 'Security risk analysis',
                        'description': 'Conduct risk analysis of PHI'
                    },
                    {
                        'id': '164.312(a)(1)',
                        'title': 'Access control',
                        'description': 'Unique user identification and automatic logoff'
                    }
                ],
                references=[
                    'https://www.hhs.gov/hipaa/'
                ]
            )
        }

        self.mapping_engine = StandardMappingEngine()

    async def map_to_standards(
        self,
        requirements: List[ParsedRequirement],
        domain: str
    ) -> Dict[str, Any]:
        """요구사항을 업계 표준에 매핑"""

        relevant_standards = self._get_relevant_standards(domain)
        mapping_results = {
            'mapped_standards': [],
            'coverage_analysis': {},
            'gap_analysis': [],
            'recommendations': []
        }

        for standard in relevant_standards:
            # 요구사항과 표준 매핑
            mappings = await self.mapping_engine.map_requirements_to_standard(
                requirements,
                standard
            )

            if mappings:
                mapping_results['mapped_standards'].append({
                    'standard': standard.name,
                    'mappings': mappings,
                    'coverage': self._calculate_coverage(mappings, standard)
                })

                # 갭 분석
                gaps = self._identify_gaps(mappings, standard)
                mapping_results['gap_analysis'].extend(gaps)

        # 권장사항 생성
        mapping_results['recommendations'] = await self._generate_recommendations(
            mapping_results['gap_analysis'],
            domain
        )

        return mapping_results

    def _calculate_coverage(
        self,
        mappings: List[Dict[str, Any]],
        standard: IndustryStandard
    ) -> float:
        """표준 충족도 계산"""

        total_requirements = len(standard.requirements)
        mapped_requirements = len(set(
            m['standard_requirement_id']
            for m in mappings
        ))

        return mapped_requirements / total_requirements if total_requirements > 0 else 0

class StandardMappingEngine:
    """표준 매핑 엔진"""

    async def map_requirements_to_standard(
        self,
        requirements: List[ParsedRequirement],
        standard: IndustryStandard
    ) -> List[Dict[str, Any]]:
        """요구사항을 표준에 매핑"""

        mappings = []

        for req in requirements:
            for std_req in standard.requirements:
                similarity = await self._calculate_similarity(
                    req.description,
                    std_req['description']
                )

                if similarity > 0.7:  # 70% 이상 유사도
                    mappings.append({
                        'requirement_id': req.id,
                        'standard_requirement_id': std_req['id'],
                        'standard_requirement_title': std_req['title'],
                        'similarity_score': similarity,
                        'mapping_type': 'direct' if similarity > 0.9 else 'partial'
                    })

        return mappings

    async def _calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """텍스트 유사도 계산"""

        # 간단한 Jaccard 유사도 구현
        # 실제로는 더 정교한 NLP 기법 사용

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
```

**규정 준수 체크리스트 생성기**:

```python
class ComplianceChecklistGenerator:
    """규정 준수 체크리스트 자동 생성"""

    async def generate_compliance_checklist(
        self,
        project: ParsedProject,
        standards: List[str]
    ) -> Dict[str, Any]:
        """프로젝트에 대한 규정 준수 체크리스트 생성"""

        checklist = {
            'project_id': project.project_info.get('id'),
            'standards': standards,
            'checklist_items': [],
            'priority_items': [],
            'estimated_effort': {}
        }

        for standard_name in standards:
            if standard_name in self.standards:
                standard = self.standards[standard_name]

                # 체크리스트 항목 생성
                items = await self._generate_checklist_items(
                    project,
                    standard
                )

                checklist['checklist_items'].extend(items)

                # 우선순위 항목 식별
                priority_items = [
                    item for item in items
                    if item['priority'] == 'critical'
                ]
                checklist['priority_items'].extend(priority_items)

                # 노력 추정
                effort = await self._estimate_compliance_effort(
                    items,
                    project
                )
                checklist['estimated_effort'][standard_name] = effort

        return checklist
```

**검증 기준**:

- [ ] 주요 업계 표준 데이터베이스
- [ ] 자동 매핑 정확도 70% 이상
- [ ] 갭 분석 기능
- [ ] 규정 준수 체크리스트 생성

#### SubTask 4.23.4: Parser Agent 도메인 통합 테스트

**담당자**: QA 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/tests/agents/parser/test_domain_parsing.py
import pytest
from typing import Dict, Any

@pytest.mark.integration
class TestDomainParsing:
    """도메인 특화 파싱 테스트"""

    @pytest.fixture
    def domain_test_cases(self):
        """도메인별 테스트 케이스"""
        return {
            'e-commerce': {
                'description': """
                Build an e-commerce platform for B2B wholesale marketplace.

                The platform must support multiple vendors with individual storefronts.
                Products should have SKUs, bulk pricing tiers, and minimum order quantities.

                Key features:
                - Vendor onboarding with KYC verification
                - Product catalog with categories, attributes, and variants
                - Shopping cart supporting bulk orders
                - B2B specific checkout with PO support
                - Order management with approval workflows
                - Integration with ERP systems (SAP, Oracle)
                - Real-time inventory sync across warehouses
                - Customer-specific pricing and catalogs

                Payment methods: Wire transfer, ACH, Net 30/60/90 terms

                The system must handle 50,000 SKUs and 1,000 concurrent users.
                All transactions must be PCI compliant.
                """,
                'expected_domain': 'e-commerce',
                'expected_terms': ['sku', 'cart', 'checkout', 'inventory', 'vendor'],
                'expected_standards': ['PCI_DSS'],
                'expected_requirements_count': {
                    'functional': 15,
                    'non_functional': 5,
                    'business': 3
                }
            },
            'healthcare': {
                'description': """
                Develop a telemedicine platform for remote patient consultations.

                The system must be HIPAA compliant and support:
                - Patient registration with medical history
                - Doctor profiles with specialization and availability
                - Video consultation with screen sharing
                - E-prescription with pharmacy integration
                - Lab result sharing and viewing
                - Appointment scheduling with reminders
                - Patient health records (EHR/EMR integration)
                - Insurance verification and claims

                Security requirements:
                - All PHI must be encrypted at rest and in transit
                - Role-based access control (RBAC)
                - Audit logs for all data access
                - Two-factor authentication for providers

                Performance: Support 500 concurrent video sessions
                Availability: 99.9% uptime SLA
                """,
                'expected_domain': 'healthcare',
                'expected_terms': ['patient', 'ehr', 'phi', 'hipaa', 'appointment'],
                'expected_standards': ['HIPAA'],
                'expected_requirements_count': {
                    'functional': 12,
                    'non_functional': 8,
                    'compliance': 4
                }
            }
        }

    @pytest.mark.asyncio
    async def test_domain_identification(self, parser_agent, domain_test_cases):
        """도메인 자동 식별 테스트"""

        for domain, test_case in domain_test_cases.items():
            # 도메인 식별
            identified_domain, confidence = await parser_agent.domain_recognizer.identify_domain(
                test_case['description']
            )

            assert identified_domain == test_case['expected_domain'], \
                f"Expected {test_case['expected_domain']}, got {identified_domain}"
            assert confidence > 0.7, \
                f"Domain confidence {confidence} is below threshold"

    @pytest.mark.asyncio
    async def test_domain_term_extraction(self, parser_agent, domain_test_cases):
        """도메인 용어 추출 테스트"""

        for domain, test_case in domain_test_cases.items():
            # 파싱 실행
            result = await parser_agent.parse_requirements(
                test_case['description'],
                project_context={'domain_hint': domain}
            )

            # 추출된 도메인 용어 확인
            extracted_terms = []
            for req in result.functional_requirements:
                terms = await parser_agent.domain_dictionary.extract_domain_terms(
                    req.description,
                    domain
                )
                extracted_terms.extend(terms)

            # 예상 용어가 모두 추출되었는지 확인
            extracted_term_names = [t.canonical_form for t in extracted_terms]
            for expected_term in test_case['expected_terms']:
                assert any(expected_term in term for term in extracted_term_names), \
                    f"Expected term '{expected_term}' not found"

    @pytest.mark.asyncio
    async def test_standard_mapping(self, parser_agent, domain_test_cases):
        """업계 표준 매핑 테스트"""

        for domain, test_case in domain_test_cases.items():
            # 파싱 실행
            result = await parser_agent.parse_requirements(
                test_case['description']
            )

            # 표준 매핑
            mapping_results = await parser_agent.standards_mapper.map_to_standards(
                result.functional_requirements + result.non_functional_requirements,
                domain
            )

            # 예상 표준이 매핑되었는지 확인
            mapped_standard_names = [
                ms['standard'] for ms in mapping_results['mapped_standards']
            ]

            for expected_standard in test_case['expected_standards']:
                assert any(expected_standard in name for name in mapped_standard_names), \
                    f"Expected standard '{expected_standard}' not mapped"

    @pytest.mark.asyncio
    async def test_domain_template_application(self, parser_agent):
        """도메인 템플릿 적용 테스트"""

        test_requirement = """
        Create a product management system where vendors can add products
        with multiple images, variants (size, color), and track inventory levels.
        """

        # 템플릿 적용
        result = await parser_agent.template_manager.apply_template(
            test_requirement,
            domain='e-commerce',
            category='product_management'
        )

        assert 'template_used' in result
        assert result['template_used'] == 'Product Catalog Requirements'

        # 구조화된 요구사항 확인
        structured = result['structured_requirement']
        assert 'product_attributes' in structured
        assert 'inventory_tracking' in structured

        # 검증 결과 확인
        validation = result['validation_results']
        assert all(v['passed'] for v in validation)
```

**도메인 특화 파싱 성능 테스트**:

```python
# backend/tests/agents/parser/test_domain_performance.py
import time
import asyncio

class TestDomainParsingPerformance:
    """도메인 파싱 성능 테스트"""

    @pytest.mark.performance
    async def test_large_domain_document_parsing(self, parser_agent):
        """대용량 도메인 문서 파싱 성능"""

        # 대용량 요구사항 문서 생성 (실제 프로젝트 시뮬레이션)
        large_document = self._generate_large_requirement_document(
            domain='healthcare',
            num_requirements=100
        )

        start_time = time.time()

        # 파싱 실행
        result = await parser_agent.parse_requirements(large_document)

        parsing_time = time.time() - start_time

        # 성능 검증
        assert parsing_time < 30, f"Parsing took {parsing_time}s, expected < 30s"
        assert len(result.functional_requirements) >= 80
        assert len(result.non_functional_requirements) >= 20

        # 도메인 특화 기능 성능
        domain_processing_start = time.time()

        # 용어 추출
        terms = await parser_agent.domain_dictionary.extract_all_terms(
            large_document,
            'healthcare'
        )

        # 표준 매핑
        mappings = await parser_agent.standards_mapper.map_to_standards(
            result.functional_requirements,
            'healthcare'
        )

        domain_processing_time = time.time() - domain_processing_start

        assert domain_processing_time < 10, \
            f"Domain processing took {domain_processing_time}s, expected < 10s"

    def _generate_large_requirement_document(
        self,
        domain: str,
        num_requirements: int
    ) -> str:
        """테스트용 대용량 문서 생성"""

        templates = {
            'healthcare': [
                "The system shall allow patients to {action} their {record_type}",
                "Healthcare providers must be able to {action} patient {data_type}",
                "The platform shall support {feature} with HIPAA compliance",
                "Integration with {system} for {purpose} is required"
            ]
        }

        actions = ['view', 'update', 'share', 'export', 'delete']
        record_types = ['medical records', 'lab results', 'prescriptions', 'appointments']
        data_types = ['vitals', 'diagnoses', 'medications', 'allergies']
        features = ['video consultation', 'e-prescription', 'appointment scheduling']
        systems = ['EHR systems', 'pharmacy networks', 'insurance providers']
        purposes = ['data exchange', 'verification', 'claims processing']

        requirements = []

        for i in range(num_requirements):
            template = templates[domain][i % len(templates[domain])]
            requirement = template.format(
                action=actions[i % len(actions)],
                record_type=record_types[i % len(record_types)],
                data_type=data_types[i % len(data_types)],
                feature=features[i % len(features)],
                system=systems[i % len(systems)],
                purpose=purposes[i % len(purposes)]
            )
            requirements.append(requirement)

        return "\n".join(requirements)
```

**도메인 간 비교 테스트**:

```python
class TestCrossDomainComparison:
    """도메인 간 파싱 비교 테스트"""

    @pytest.mark.asyncio
    async def test_multi_domain_project(self, parser_agent):
        """여러 도메인이 혼재된 프로젝트 테스트"""

        # 핀테크 프로젝트 (전자상거래 + 금융)
        fintech_requirements = """
        Build a payment processing platform for e-commerce businesses.

        Features:
        - Merchant onboarding with KYC/AML checks
        - Payment gateway supporting multiple methods
        - Real-time fraud detection using ML
        - Transaction monitoring and reporting
        - PCI DSS compliant card processing
        - Integration with banking APIs
        - Automated settlement and reconciliation
        """

        result = await parser_agent.parse_requirements(fintech_requirements)

        # 다중 도메인 인식 확인
        domains = await parser_agent.identify_all_domains(fintech_requirements)

        assert 'e-commerce' in domains
        assert 'finance' in domains

        # 각 도메인의 요구사항이 적절히 분류되었는지 확인
        ecommerce_reqs = [
            r for r in result.functional_requirements
            if 'merchant' in r.description.lower() or 'payment gateway' in r.description.lower()
        ]

        finance_reqs = [
            r for r in result.functional_requirements
            if 'kyc' in r.description.lower() or 'aml' in r.description.lower()
        ]

        assert len(ecommerce_reqs) > 0
        assert len(finance_reqs) > 0

        # 복합 표준 매핑 확인
        standards = await parser_agent.identify_applicable_standards(result)

        assert 'PCI_DSS' in standards  # 전자상거래
        assert 'ISO_27001' in standards  # 일반 보안
```

**검증 기준**:

- [ ] 모든 도메인 테스트 통과
- [ ] 도메인 식별 정확도 85% 이상
- [ ] 대용량 문서 처리 성능
- [ ] 다중 도메인 프로젝트 지원

이제 Task 4.21, 4.22, 4.23 (Parser Agent)의 모든 SubTask가 완료되었습니다. Parser Agent는 다음과 같은 핵심 기능을 갖추게 되었습니다:

1. **자연어 처리**: SpaCy와 Transformer 모델을 활용한 고급 NLP
2. **요구사항 구조화**: 기능/비기능 요구사항 자동 분리 및 분류
3. **사용자 스토리 생성**: 요구사항을 사용자 스토리로 자동 변환
4. **데이터 모델/API 추출**: 텍스트에서 데이터 구조와 API 자동 추출
5. **도메인 특화 파싱**: 8개 주요 도메인별 전문 용어 및 패턴 인식
6. **업계 표준 매핑**: ISO, PCI-DSS, HIPAA 등 표준 자동 매핑
7. **검증 및 품질 평가**: 요구사항 완성도 및 품질 자동 평가

---

# Phase 4: 9개 핵심 에이전트 구현 - Parser Agent 계속 (Tasks 4.24-4.26)

### Task 4.24: Parser Agent 고급 분석 기능

#### SubTask 4.24.1: 요구사항 의존성 분석기

**담당자**: 시스템 분석가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/dependency_analyzer.py
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import networkx as nx
import re

@dataclass
class DependencyType(Enum):
    REQUIRES = "requires"          # A requires B to function
    EXTENDS = "extends"            # A extends functionality of B
    CONFLICTS = "conflicts"        # A conflicts with B
    OPTIONAL = "optional"          # A optionally uses B
    TEMPORAL = "temporal"          # A must be done before B
    DATA = "data"                  # A needs data from B

@dataclass
class RequirementDependency:
    source_id: str
    target_id: str
    dependency_type: DependencyType
    strength: float  # 0.0 to 1.0
    description: str
    bidirectional: bool = False
    metadata: Dict[str, Any] = None

class DependencyAnalyzer:
    """요구사항 간 의존성 분석"""

    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.dependency_patterns = self._initialize_patterns()
        self.semantic_analyzer = SemanticDependencyAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()

    def _initialize_patterns(self) -> Dict[str, List[re.Pattern]]:
        """의존성 패턴 초기화"""
        return {
            'requires': [
                re.compile(r'requires?\s+(?:that\s+)?(.+)', re.IGNORECASE),
                re.compile(r'depends?\s+on\s+(.+)', re.IGNORECASE),
                re.compile(r'needs?\s+(.+)\s+to\s+(?:be\s+)?(?:work|function)', re.IGNORECASE),
                re.compile(r'prerequisite:\s*(.+)', re.IGNORECASE)
            ],
            'extends': [
                re.compile(r'extends?\s+(?:the\s+)?(.+)', re.IGNORECASE),
                re.compile(r'builds?\s+(?:up)?on\s+(.+)', re.IGNORECASE),
                re.compile(r'enhances?\s+(.+)', re.IGNORECASE)
            ],
            'conflicts': [
                re.compile(r'conflicts?\s+with\s+(.+)', re.IGNORECASE),
                re.compile(r'incompatible\s+with\s+(.+)', re.IGNORECASE),
                re.compile(r'cannot\s+(?:be\s+used\s+)?with\s+(.+)', re.IGNORECASE)
            ],
            'temporal': [
                re.compile(r'after\s+(.+)\s+is\s+(?:complete|done|finished)', re.IGNORECASE),
                re.compile(r'before\s+(.+)', re.IGNORECASE),
                re.compile(r'follows?\s+(.+)', re.IGNORECASE)
            ]
        }

    async def analyze_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> Dict[str, Any]:
        """요구사항 의존성 분석"""

        # 1. 명시적 의존성 추출
        explicit_deps = await self._extract_explicit_dependencies(requirements)

        # 2. 암시적 의존성 추론
        implicit_deps = await self._infer_implicit_dependencies(requirements)

        # 3. 의존성 그래프 구축
        self._build_dependency_graph(requirements, explicit_deps + implicit_deps)

        # 4. 순환 의존성 검사
        cycles = self._detect_circular_dependencies()

        # 5. 의존성 경로 분석
        critical_paths = self._analyze_critical_paths()

        # 6. 영향도 분석
        impact_analysis = await self.impact_analyzer.analyze(
            self.dependency_graph,
            requirements
        )

        # 7. 의존성 강도 계산
        dependency_strengths = self._calculate_dependency_strengths()

        return {
            'dependencies': explicit_deps + implicit_deps,
            'dependency_graph': self._graph_to_dict(),
            'circular_dependencies': cycles,
            'critical_paths': critical_paths,
            'impact_analysis': impact_analysis,
            'dependency_strengths': dependency_strengths,
            'statistics': self._calculate_statistics()
        }

    async def _extract_explicit_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementDependency]:
        """명시적 의존성 추출"""

        dependencies = []

        for req in requirements:
            # 의존성 패턴 매칭
            for dep_type, patterns in self.dependency_patterns.items():
                for pattern in patterns:
                    matches = pattern.finditer(req.description)
                    for match in matches:
                        # 참조된 요구사항 찾기
                        referenced_text = match.group(1)
                        target_req = await self._find_referenced_requirement(
                            referenced_text,
                            requirements
                        )

                        if target_req:
                            dependency = RequirementDependency(
                                source_id=req.id,
                                target_id=target_req.id,
                                dependency_type=DependencyType[dep_type.upper()],
                                strength=0.9,  # 명시적 의존성은 강함
                                description=f"Explicitly stated: {match.group(0)}"
                            )
                            dependencies.append(dependency)

            # 요구사항에 명시된 의존성
            if req.dependencies:
                for dep_id in req.dependencies:
                    if any(r.id == dep_id for r in requirements):
                        dependency = RequirementDependency(
                            source_id=req.id,
                            target_id=dep_id,
                            dependency_type=DependencyType.REQUIRES,
                            strength=1.0,
                            description="Listed in dependencies field"
                        )
                        dependencies.append(dependency)

        return dependencies

    async def _infer_implicit_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementDependency]:
        """암시적 의존성 추론"""

        implicit_deps = []

        # 의미적 유사성 기반 의존성
        semantic_deps = await self.semantic_analyzer.find_semantic_dependencies(
            requirements
        )
        implicit_deps.extend(semantic_deps)

        # 데이터 흐름 기반 의존성
        data_flow_deps = await self._analyze_data_flow_dependencies(requirements)
        implicit_deps.extend(data_flow_deps)

        # 기능 계층 기반 의존성
        hierarchy_deps = await self._analyze_functional_hierarchy(requirements)
        implicit_deps.extend(hierarchy_deps)

        # 시간적 순서 기반 의존성
        temporal_deps = await self._analyze_temporal_dependencies(requirements)
        implicit_deps.extend(temporal_deps)

        return implicit_deps

    async def _analyze_data_flow_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementDependency]:
        """데이터 흐름 기반 의존성 분석"""

        dependencies = []

        # 각 요구사항의 입출력 분석
        req_io_map = {}
        for req in requirements:
            inputs, outputs = await self._extract_data_io(req)
            req_io_map[req.id] = {
                'inputs': inputs,
                'outputs': outputs
            }

        # 데이터 의존성 찾기
        for source_req in requirements:
            source_outputs = req_io_map[source_req.id]['outputs']

            for target_req in requirements:
                if source_req.id == target_req.id:
                    continue

                target_inputs = req_io_map[target_req.id]['inputs']

                # 출력과 입력이 매칭되는 경우
                common_data = source_outputs.intersection(target_inputs)
                if common_data:
                    dependency = RequirementDependency(
                        source_id=target_req.id,
                        target_id=source_req.id,
                        dependency_type=DependencyType.DATA,
                        strength=len(common_data) / max(len(target_inputs), 1),
                        description=f"Data dependency on: {', '.join(common_data)}",
                        metadata={'data_elements': list(common_data)}
                    )
                    dependencies.append(dependency)

        return dependencies

    def _build_dependency_graph(
        self,
        requirements: List[ParsedRequirement],
        dependencies: List[RequirementDependency]
    ):
        """의존성 그래프 구축"""

        # 노드 추가
        for req in requirements:
            self.dependency_graph.add_node(
                req.id,
                requirement=req,
                type=req.type.value,
                priority=req.priority
            )

        # 엣지 추가
        for dep in dependencies:
            self.dependency_graph.add_edge(
                dep.source_id,
                dep.target_id,
                dependency_type=dep.dependency_type.value,
                strength=dep.strength,
                description=dep.description
            )

            # 양방향 의존성 처리
            if dep.bidirectional:
                self.dependency_graph.add_edge(
                    dep.target_id,
                    dep.source_id,
                    dependency_type=dep.dependency_type.value,
                    strength=dep.strength,
                    description=dep.description
                )

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """순환 의존성 탐지"""

        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []

    def _analyze_critical_paths(self) -> List[Dict[str, Any]]:
        """중요 경로 분석"""

        critical_paths = []

        # 시작 노드 (의존성이 없는 노드) 찾기
        start_nodes = [
            node for node in self.dependency_graph.nodes()
            if self.dependency_graph.in_degree(node) == 0
        ]

        # 종료 노드 (다른 노드에 의존되지 않는 노드) 찾기
        end_nodes = [
            node for node in self.dependency_graph.nodes()
            if self.dependency_graph.out_degree(node) == 0
        ]

        # 각 경로 분석
        for start in start_nodes:
            for end in end_nodes:
                try:
                    paths = list(nx.all_simple_paths(
                        self.dependency_graph,
                        start,
                        end,
                        cutoff=10  # 최대 10 단계
                    ))

                    for path in paths:
                        # 경로의 중요도 계산
                        importance = self._calculate_path_importance(path)

                        critical_paths.append({
                            'path': path,
                            'length': len(path),
                            'importance': importance,
                            'bottlenecks': self._identify_bottlenecks(path)
                        })
                except nx.NetworkXNoPath:
                    continue

        # 중요도 순으로 정렬
        critical_paths.sort(key=lambda x: x['importance'], reverse=True)

        return critical_paths[:10]  # 상위 10개 경로
```

**영향도 분석기**:

```python
# backend/src/agents/implementations/parser/impact_analyzer.py
class ImpactAnalyzer:
    """요구사항 변경 영향도 분석"""

    async def analyze(
        self,
        dependency_graph: nx.DiGraph,
        requirements: List[ParsedRequirement]
    ) -> Dict[str, Any]:
        """영향도 분석 수행"""

        impact_scores = {}

        for req in requirements:
            if req.id not in dependency_graph:
                continue

            # 직접 영향받는 요구사항
            direct_impact = list(dependency_graph.successors(req.id))

            # 간접 영향받는 요구사항
            indirect_impact = set()
            for node in direct_impact:
                indirect_impact.update(
                    nx.descendants(dependency_graph, node)
                )

            # 영향도 점수 계산
            impact_score = self._calculate_impact_score(
                req,
                direct_impact,
                indirect_impact,
                dependency_graph
            )

            impact_scores[req.id] = {
                'score': impact_score,
                'direct_impact_count': len(direct_impact),
                'indirect_impact_count': len(indirect_impact),
                'total_impact_count': len(direct_impact) + len(indirect_impact),
                'affected_requirements': direct_impact,
                'cascade_effect': list(indirect_impact)
            }

        return {
            'requirement_impacts': impact_scores,
            'high_impact_requirements': self._identify_high_impact_requirements(
                impact_scores
            ),
            'change_risk_matrix': self._generate_change_risk_matrix(
                impact_scores,
                requirements
            )
        }
```

**검증 기준**:

- [ ] 명시적/암시적 의존성 추출
- [ ] 순환 의존성 탐지
- [ ] 중요 경로 식별
- [ ] 영향도 분석 정확도

#### SubTask 4.24.2: 요구사항 충돌 감지기

**담당자**: 품질 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/conflict_detector.py
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

@dataclass
class ConflictType(Enum):
    LOGICAL = "logical"              # 논리적 충돌
    RESOURCE = "resource"            # 리소스 경쟁
    TEMPORAL = "temporal"            # 시간적 충돌
    TECHNICAL = "technical"          # 기술적 충돌
    BUSINESS = "business"            # 비즈니스 규칙 충돌
    PERFORMANCE = "performance"      # 성능 요구사항 충돌
    SECURITY = "security"            # 보안 요구사항 충돌

@dataclass
class RequirementConflict:
    requirement1_id: str
    requirement2_id: str
    conflict_type: ConflictType
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    resolution_suggestions: List[str]
    confidence: float

class ConflictDetector:
    """요구사항 충돌 감지기"""

    def __init__(self):
        self.conflict_rules = self._initialize_conflict_rules()
        self.semantic_analyzer = SemanticConflictAnalyzer()
        self.constraint_solver = ConstraintSolver()

    def _initialize_conflict_rules(self) -> List[ConflictRule]:
        """충돌 감지 규칙 초기화"""
        return [
            # 성능 vs 보안 충돌
            ConflictRule(
                name="performance_vs_security",
                pattern1=r"(fast|quick|rapid|high.?performance|low.?latency)",
                pattern2=r"(encrypt|secure|authentication|authorization)",
                conflict_type=ConflictType.TECHNICAL,
                severity_calculator=self._calculate_performance_security_severity
            ),

            # 리소스 충돌
            ConflictRule(
                name="resource_competition",
                pattern1=r"(maximum|all|full|unlimited)\s+(cpu|memory|bandwidth)",
                pattern2=r"(maximum|all|full|unlimited)\s+(cpu|memory|bandwidth)",
                conflict_type=ConflictType.RESOURCE,
                severity_calculator=self._calculate_resource_severity
            ),

            # 시간적 충돌
            ConflictRule(
                name="temporal_conflict",
                pattern1=r"(before|prior to|prerequisite)",
                pattern2=r"(after|following|subsequent to)",
                conflict_type=ConflictType.TEMPORAL,
                severity_calculator=self._calculate_temporal_severity
            )
        ]

    async def detect_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> Dict[str, Any]:
        """요구사항 충돌 감지"""

        conflicts = []

        # 1. 규칙 기반 충돌 감지
        rule_conflicts = await self._detect_rule_based_conflicts(requirements)
        conflicts.extend(rule_conflicts)

        # 2. 의미적 충돌 감지
        semantic_conflicts = await self.semantic_analyzer.detect_conflicts(
            requirements
        )
        conflicts.extend(semantic_conflicts)

        # 3. 제약조건 충돌 감지
        constraint_conflicts = await self._detect_constraint_conflicts(
            requirements
        )
        conflicts.extend(constraint_conflicts)

        # 4. 비즈니스 규칙 충돌 감지
        business_conflicts = await self._detect_business_conflicts(requirements)
        conflicts.extend(business_conflicts)

        # 5. 충돌 그룹화 및 분석
        conflict_groups = self._group_conflicts(conflicts)

        # 6. 해결 우선순위 결정
        prioritized_conflicts = self._prioritize_conflicts(conflicts)

        return {
            'conflicts': conflicts,
            'conflict_count': len(conflicts),
            'conflict_groups': conflict_groups,
            'critical_conflicts': [
                c for c in conflicts if c.severity == 'critical'
            ],
            'resolution_order': prioritized_conflicts,
            'conflict_matrix': self._generate_conflict_matrix(
                requirements,
                conflicts
            )
        }

    async def _detect_rule_based_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementConflict]:
        """규칙 기반 충돌 감지"""

        conflicts = []

        # 모든 요구사항 쌍 검사
        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                # 각 규칙 적용
                for rule in self.conflict_rules:
                    if rule.matches(req1.description, req2.description):
                        conflict = RequirementConflict(
                            requirement1_id=req1.id,
                            requirement2_id=req2.id,
                            conflict_type=rule.conflict_type,
                            severity=rule.severity_calculator(req1, req2),
                            description=rule.generate_description(req1, req2),
                            resolution_suggestions=await self._generate_resolutions(
                                req1, req2, rule
                            ),
                            confidence=rule.calculate_confidence(req1, req2)
                        )
                        conflicts.append(conflict)

        return conflicts

    async def _detect_constraint_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementConflict]:
        """제약조건 충돌 감지"""

        conflicts = []

        # 제약조건 추출
        constraints = {}
        for req in requirements:
            constraints[req.id] = await self._extract_constraints(req)

        # 제약조건 해결 시도
        unsolvable_pairs = await self.constraint_solver.find_unsolvable_pairs(
            constraints
        )

        for pair in unsolvable_pairs:
            req1 = next(r for r in requirements if r.id == pair[0])
            req2 = next(r for r in requirements if r.id == pair[1])

            conflict = RequirementConflict(
                requirement1_id=pair[0],
                requirement2_id=pair[1],
                conflict_type=ConflictType.TECHNICAL,
                severity='high',
                description=f"Constraints cannot be satisfied simultaneously",
                resolution_suggestions=[
                    "Relax constraints in one of the requirements",
                    "Find a compromise between the constraints",
                    "Implement requirements in different contexts"
                ],
                confidence=0.9
            )
            conflicts.append(conflict)

        return conflicts

    async def _generate_resolutions(
        self,
        req1: ParsedRequirement,
        req2: ParsedRequirement,
        rule: ConflictRule
    ) -> List[str]:
        """충돌 해결 방안 생성"""

        resolutions = []

        if rule.conflict_type == ConflictType.PERFORMANCE:
            resolutions.extend([
                "Define clear performance priorities",
                "Implement caching to improve performance",
                "Use asynchronous processing where possible",
                "Consider performance/feature trade-offs"
            ])

        elif rule.conflict_type == ConflictType.SECURITY:
            resolutions.extend([
                "Implement security measures without compromising core functionality",
                "Use optimized security algorithms",
                "Apply security selectively based on data sensitivity",
                "Consider security levels for different user types"
            ])

        elif rule.conflict_type == ConflictType.RESOURCE:
            resolutions.extend([
                "Implement resource pooling",
                "Use resource scheduling/prioritization",
                "Define resource quotas per requirement",
                "Consider cloud auto-scaling"
            ])

        # 컨텍스트 기반 구체적 제안
        specific_suggestions = await self._generate_specific_resolutions(
            req1, req2, rule
        )
        resolutions.extend(specific_suggestions)

        return resolutions[:5]  # 상위 5개 제안
```

**의미적 충돌 분석기**:

```python
# backend/src/agents/implementations/parser/semantic_conflict_analyzer.py
class SemanticConflictAnalyzer:
    """의미적 충돌 분석"""

    def __init__(self):
        self.embedding_model = self._load_embedding_model()
        self.contradiction_detector = ContradictionDetector()

    async def detect_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementConflict]:
        """의미적 충돌 감지"""

        conflicts = []

        # 요구사항 임베딩 생성
        embeddings = await self._generate_embeddings(requirements)

        # 의미적 모순 찾기
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements[i+1:], i+1):
                # 모순 검사
                contradiction_score = await self.contradiction_detector.check(
                    req1.description,
                    req2.description
                )

                if contradiction_score > 0.7:
                    conflict = RequirementConflict(
                        requirement1_id=req1.id,
                        requirement2_id=req2.id,
                        conflict_type=ConflictType.LOGICAL,
                        severity=self._calculate_severity(contradiction_score),
                        description="Semantic contradiction detected",
                        resolution_suggestions=[
                            "Review and clarify the requirements",
                            "Determine which requirement takes precedence",
                            "Find a middle ground that satisfies both intents"
                        ],
                        confidence=contradiction_score
                    )
                    conflicts.append(conflict)

        return conflicts
```

**검증 기준**:

- [ ] 다양한 충돌 유형 감지
- [ ] 충돌 심각도 평가
- [ ] 해결 방안 제시
- [ ] 의미적 모순 감지

#### SubTask 4.24.3: 요구사항 추적성 매트릭스 생성기

**담당자**: 품질 보증 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/traceability_matrix.py
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import pandas as pd
from enum import Enum

@dataclass
class TraceabilityLink:
    source_type: str  # 'business_req', 'functional_req', 'technical_req', 'test_case', 'code'
    source_id: str
    target_type: str
    target_id: str
    link_type: str  # 'implements', 'tests', 'derives_from', 'satisfies'
    confidence: float
    metadata: Dict[str, Any]

class TraceabilityMatrixGenerator:
    """요구사항 추적성 매트릭스 생성기"""

    def __init__(self):
        self.link_patterns = self._initialize_link_patterns()
        self.coverage_analyzer = CoverageAnalyzer()

    async def generate_traceability_matrix(
        self,
        parsed_project: ParsedProject,
        additional_artifacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """추적성 매트릭스 생성"""

        # 1. 모든 추적 가능한 항목 수집
        traceable_items = await self._collect_traceable_items(
            parsed_project,
            additional_artifacts
        )

        # 2. 추적성 링크 생성
        traceability_links = await self._generate_traceability_links(
            traceable_items
        )

        # 3. 매트릭스 구성
        matrix = self._build_matrix(traceable_items, traceability_links)

        # 4. 커버리지 분석
        coverage_analysis = await self.coverage_analyzer.analyze(
            matrix,
            traceable_items
        )

        # 5. 갭 분석
        gaps = self._identify_gaps(matrix, traceable_items)

        # 6. 추적성 보고서 생성
        report = await self._generate_traceability_report(
            matrix,
            coverage_analysis,
            gaps
        )

        return {
            'matrix': matrix,
            'links': traceability_links,
            'coverage': coverage_analysis,
            'gaps': gaps,
            'report': report,
            'visualizations': await self._generate_visualizations(matrix)
        }

    async def _collect_traceable_items(
        self,
        parsed_project: ParsedProject,
        additional_artifacts: Optional[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """추적 가능한 항목 수집"""

        items = {
            'business_requirements': [],
            'functional_requirements': [],
            'technical_requirements': [],
            'non_functional_requirements': [],
            'user_stories': [],
            'use_cases': [],
            'test_cases': [],
            'design_elements': [],
            'code_modules': []
        }

        # 비즈니스 요구사항
        for req in parsed_project.business_requirements:
            items['business_requirements'].append({
                'id': req.id,
                'description': req.description,
                'priority': req.priority,
                'source': 'parsed_requirements'
            })

        # 기능 요구사항
        for req in parsed_project.functional_requirements:
            items['functional_requirements'].append({
                'id': req.id,
                'description': req.description,
                'category': req.category,
                'acceptance_criteria': req.acceptance_criteria
            })

        # 사용자 스토리
        for story in parsed_project.user_stories:
            items['user_stories'].append({
                'id': story.get('id'),
                'narrative': story.get('narrative'),
                'linked_requirements': story.get('linked_requirements', [])
            })

        # 추가 아티팩트 처리
        if additional_artifacts:
            if 'test_cases' in additional_artifacts:
                items['test_cases'] = additional_artifacts['test_cases']

            if 'design_documents' in additional_artifacts:
                items['design_elements'] = await self._extract_design_elements(
                    additional_artifacts['design_documents']
                )

        return items

    async def _generate_traceability_links(
        self,
        traceable_items: Dict[str, List[Dict[str, Any]]]
    ) -> List[TraceabilityLink]:
        """추적성 링크 생성"""

        links = []

        # 비즈니스 → 기능 요구사항 링크
        links.extend(
            await self._link_business_to_functional(
                traceable_items['business_requirements'],
                traceable_items['functional_requirements']
            )
        )

        # 기능 요구사항 → 기술 요구사항 링크
        links.extend(
            await self._link_functional_to_technical(
                traceable_items['functional_requirements'],
                traceable_items['technical_requirements']
            )
        )

        # 사용자 스토리 → 기능 요구사항 링크
        links.extend(
            await self._link_stories_to_requirements(
                traceable_items['user_stories'],
                traceable_items['functional_requirements']
            )
        )

        # 요구사항 → 테스트 케이스 링크
        if traceable_items['test_cases']:
            links.extend(
                await self._link_requirements_to_tests(
                    traceable_items['functional_requirements'],
                    traceable_items['test_cases']
                )
            )

        return links

    def _build_matrix(
        self,
        items: Dict[str, List[Dict[str, Any]]],
        links: List[TraceabilityLink]
    ) -> pd.DataFrame:
        """추적성 매트릭스 구축"""

        # 모든 항목 ID 수집
        all_ids = []
        id_to_type = {}

        for item_type, item_list in items.items():
            for item in item_list:
                item_id = item.get('id')
                if item_id:
                    all_ids.append(item_id)
                    id_to_type[item_id] = item_type

        # 매트릭스 초기화
        matrix = pd.DataFrame(
            index=all_ids,
            columns=all_ids,
            data=''
        )

        # 링크 정보로 매트릭스 채우기
        for link in links:
            if link.source_id in all_ids and link.target_id in all_ids:
                matrix.loc[link.source_id, link.target_id] = link.link_type

                # 역방향 링크도 표시 (대칭성)
                reverse_type = self._get_reverse_link_type(link.link_type)
                if reverse_type:
                    matrix.loc[link.target_id, link.source_id] = reverse_type

        return matrix
```

**추적성 보고서 생성기**:

```python
class TraceabilityReportGenerator:
    """추적성 보고서 생성"""

    async def generate_report(
        self,
        matrix: pd.DataFrame,
        coverage_analysis: Dict[str, Any],
        gaps: List[Dict[str, Any]]
    ) -> str:
        """HTML 추적성 보고서 생성"""

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Requirements Traceability Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .matrix-table { border-collapse: collapse; font-size: 12px; }
                .matrix-table td, .matrix-table th {
                    border: 1px solid #ddd;
                    padding: 5px;
                    text-align: center;
                }
                .matrix-table th { background-color: #f2f2f2; }
                .linked { background-color: #90EE90; }
                .missing { background-color: #FFB6C1; }
                .coverage-chart { margin: 20px 0; }
                .gap-item { margin: 10px 0; padding: 10px; background: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Requirements Traceability Report</h1>

            <h2>Coverage Summary</h2>
            <div class="coverage-summary">
                <p>Overall Coverage: {overall_coverage:.1%}</p>
                <p>Business Requirements Coverage: {br_coverage:.1%}</p>
                <p>Functional Requirements Coverage: {fr_coverage:.1%}</p>
                <p>Test Coverage: {test_coverage:.1%}</p>
            </div>

            <h2>Traceability Matrix</h2>
            <div class="matrix-container">
                {matrix_html}
            </div>

            <h2>Identified Gaps</h2>
            <div class="gaps-section">
                {gaps_html}
            </div>

            <h2>Recommendations</h2>
            <ul>
                {recommendations_html}
            </ul>
        </body>
        </html>
        """

        return html_template.format(
            overall_coverage=coverage_analysis['overall_coverage'],
            br_coverage=coverage_analysis['business_requirements_coverage'],
            fr_coverage=coverage_analysis['functional_requirements_coverage'],
            test_coverage=coverage_analysis.get('test_coverage', 0),
            matrix_html=self._matrix_to_html(matrix),
            gaps_html=self._gaps_to_html(gaps),
            recommendations_html=self._generate_recommendations_html(
                coverage_analysis,
                gaps
            )
        )
```

**검증 기준**:

- [ ] 완전한 추적성 매트릭스 생성
- [ ] 다양한 아티팩트 간 링크
- [ ] 커버리지 분석 정확도
- [ ] 갭 식별 및 보고

#### SubTask 4.24.4: 요구사항 영향 분석 도구

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/impact_analysis_tool.py
from typing import List, Dict, Any, Set, Optional
import networkx as nx
from dataclasses import dataclass
from enum import Enum

@dataclass
class ImpactType(Enum):
    FUNCTIONAL = "functional"      # 기능적 영향
    TECHNICAL = "technical"        # 기술적 영향
    PERFORMANCE = "performance"    # 성능 영향
    SECURITY = "security"          # 보안 영향
    COST = "cost"                  # 비용 영향
    SCHEDULE = "schedule"          # 일정 영향

@dataclass
class ChangeScenario:
    requirement_id: str
    change_type: str  # 'add', 'modify', 'delete'
    change_description: str
    estimated_effort: Optional[float]

@dataclass
class ImpactAssessment:
    affected_requirement_id: str
    impact_type: ImpactType
    impact_level: str  # 'critical', 'high', 'medium', 'low'
    description: str
    mitigation_strategies: List[str]
    effort_impact: float  # 추가 노력 (시간)
    risk_score: float

class RequirementImpactAnalyzer:
    """요구사항 변경 영향 분석 도구"""

    def __init__(self):
        self.dependency_graph = None
        self.impact_calculator = ImpactCalculator()
        self.risk_assessor = RiskAssessor()
        self.effort_estimator = EffortEstimator()

    async def analyze_change_impact(
        self,
        change_scenario: ChangeScenario,
        parsed_project: ParsedProject,
        dependency_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """변경 시나리오에 대한 영향 분석"""

        # 의존성 그래프 설정
        self.dependency_graph = self._rebuild_dependency_graph(
            dependency_analysis['dependency_graph']
        )

        # 1. 직접 영향 분석
        direct_impacts = await self._analyze_direct_impacts(
            change_scenario,
            parsed_project
        )

        # 2. 파급 효과 분석
        ripple_effects = await self._analyze_ripple_effects(
            change_scenario,
            direct_impacts
        )

        # 3. 영향도 평가
        impact_assessments = await self._assess_impacts(
            direct_impacts + ripple_effects,
            change_scenario
        )

        # 4. 리스크 평가
        risk_analysis = await self.risk_assessor.assess_risks(
            impact_assessments,
            parsed_project
        )

        # 5. 노력 추정
        effort_estimation = await self.effort_estimator.estimate(
            change_scenario,
            impact_assessments
        )

        # 6. 변경 경로 분석
        change_paths = self._analyze_change_propagation_paths(
            change_scenario.requirement_id
        )

        # 7. 권장사항 생성
        recommendations = await self._generate_recommendations(
            impact_assessments,
            risk_analysis,
            effort_estimation
        )

        return {
            'change_scenario': change_scenario,
            'direct_impacts': direct_impacts,
            'ripple_effects': ripple_effects,
            'impact_assessments': impact_assessments,
            'risk_analysis': risk_analysis,
            'effort_estimation': effort_estimation,
            'change_paths': change_paths,
            'recommendations': recommendations,
            'summary': self._generate_impact_summary(
                impact_assessments,
                risk_analysis,
                effort_estimation
            )
        }

    async def _analyze_direct_impacts(
        self,
        change_scenario: ChangeScenario,
        parsed_project: ParsedProject
    ) -> List[ImpactAssessment]:
        """직접적인 영향 분석"""

        direct_impacts = []

        # 변경되는 요구사항 찾기
        changed_req = self._find_requirement(
            change_scenario.requirement_id,
            parsed_project
        )

        if not changed_req:
            return []

        # 직접 연결된 요구사항들
        if change_scenario.requirement_id in self.dependency_graph:
            # 의존하는 요구사항들 (이 요구사항을 필요로 하는)
            dependents = list(self.dependency_graph.successors(
                change_scenario.requirement_id
            ))

            # 의존되는 요구사항들 (이 요구사항이 필요로 하는)
            dependencies = list(self.dependency_graph.predecessors(
                change_scenario.requirement_id
            ))

            # 각 연결된 요구사항에 대한 영향 평가
            for dep_id in dependents:
                impact = await self._assess_single_impact(
                    dep_id,
                    change_scenario,
                    'dependent'
                )
                if impact:
                    direct_impacts.append(impact)

            for dep_id in dependencies:
                if change_scenario.change_type == 'delete':
                    impact = await self._assess_single_impact(
                        dep_id,
                        change_scenario,
                        'dependency'
                    )
                    if impact:
                        direct_impacts.append(impact)

        return direct_impacts

    async def _analyze_ripple_effects(
        self,
        change_scenario: ChangeScenario,
        direct_impacts: List[ImpactAssessment]
    ) -> List[ImpactAssessment]:
        """파급 효과 분석"""

        ripple_effects = []
        analyzed = set([change_scenario.requirement_id])

        # BFS로 파급 효과 추적
        queue = [(impact.affected_requirement_id, 1)
                 for impact in direct_impacts]

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in analyzed or depth > 3:  # 최대 3단계까지
                continue

            analyzed.add(current_id)

            # 현재 노드의 이웃들
            if current_id in self.dependency_graph:
                neighbors = list(self.dependency_graph.successors(current_id))

                for neighbor_id in neighbors:
                    if neighbor_id not in analyzed:
                        # 파급 영향 평가
                        impact = await self._assess_ripple_impact(
                            neighbor_id,
                            current_id,
                            change_scenario,
                            depth
                        )

                        if impact:
                            ripple_effects.append(impact)
                            queue.append((neighbor_id, depth + 1))

        return ripple_effects

    def _analyze_change_propagation_paths(
        self,
        start_requirement_id: str
    ) -> List[Dict[str, Any]]:
        """변경 전파 경로 분석"""

        paths = []

        if start_requirement_id not in self.dependency_graph:
            return paths

        # 모든 도달 가능한 노드 찾기
        reachable = nx.descendants(self.dependency_graph, start_requirement_id)

        # 주요 경로 찾기
        for target in reachable:
            try:
                # 최단 경로
                shortest_path = nx.shortest_path(
                    self.dependency_graph,
                    start_requirement_id,
                    target
                )

                # 경로 분석
                path_analysis = {
                    'path': shortest_path,
                    'length': len(shortest_path) - 1,
                    'target': target,
                    'critical_nodes': self._identify_critical_nodes(shortest_path),
                    'bottlenecks': self._identify_bottlenecks(shortest_path)
                }

                paths.append(path_analysis)

            except nx.NetworkXNoPath:
                continue

        # 중요도 순으로 정렬
        paths.sort(key=lambda x: (
            len(x['critical_nodes']),
            x['length']
        ), reverse=True)

        return paths[:20]  # 상위 20개 경로
```

**시뮬레이션 도구**:

```python
class ChangeImpactSimulator:
    """변경 영향 시뮬레이션"""

    async def simulate_changes(
        self,
        change_scenarios: List[ChangeScenario],
        parsed_project: ParsedProject,
        dependency_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """여러 변경 시나리오 시뮬레이션"""

        simulation_results = []
        cumulative_impact = CumulativeImpactTracker()

        for scenario in change_scenarios:
            # 개별 시나리오 분석
            impact_analysis = await self.analyzer.analyze_change_impact(
                scenario,
                parsed_project,
                dependency_analysis
            )

            simulation_results.append({
                'scenario': scenario,
                'analysis': impact_analysis
            })

            # 누적 영향 추적
            cumulative_impact.add_impacts(impact_analysis['impact_assessments'])

        # 시나리오 간 상호작용 분석
        interactions = await self._analyze_scenario_interactions(
            change_scenarios,
            simulation_results
        )

        # 최적 변경 순서 결정
        optimal_order = await self._determine_optimal_change_order(
            change_scenarios,
            simulation_results,
            interactions
        )

        return {
            'individual_results': simulation_results,
            'cumulative_impact': cumulative_impact.get_summary(),
            'scenario_interactions': interactions,
            'optimal_change_order': optimal_order,
            'total_effort_estimate': cumulative_impact.total_effort,
            'total_risk_score': cumulative_impact.total_risk
        }
```

**검증 기준**:

- [ ] 변경 영향 정확한 추적
- [ ] 파급 효과 분석
- [ ] 리스크 평가
- [ ] 노력 추정 정확도

### Task 4.25: Parser Agent 출력 형식 및 통합

#### SubTask 4.25.1: 구조화된 출력 포맷터

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/output_formatter.py
from typing import Dict, Any, List, Optional
from enum import Enum
import json
import yaml
import xml.etree.ElementTree as ET
from dataclasses import asdict
import markdown

class OutputFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    MARKDOWN = "markdown"
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"

class StructuredOutputFormatter:
    """구조화된 출력 포맷터"""

    def __init__(self):
        self.formatters = {
            OutputFormat.JSON: self._format_json,
            OutputFormat.YAML: self._format_yaml,
            OutputFormat.XML: self._format_xml,
            OutputFormat.MARKDOWN: self._format_markdown,
            OutputFormat.HTML: self._format_html,
            OutputFormat.DOCX: self._format_docx,
            OutputFormat.PDF: self._format_pdf
        }

        self.template_engine = TemplateEngine()
        self.schema_validator = SchemaValidator()

    async def format_output(
        self,
        parsed_project: ParsedProject,
        analysis_results: Dict[str, Any],
        output_format: OutputFormat,
        options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """파싱 결과를 지정된 형식으로 출력"""

        # 1. 데이터 준비
        formatted_data = await self._prepare_data(
            parsed_project,
            analysis_results,
            options
        )

        # 2. 스키마 검증
        if options and options.get('validate_schema', True):
            await self.schema_validator.validate(
                formatted_data,
                output_format
            )

        # 3. 형식별 포맷팅
        formatter = self.formatters.get(output_format)
        if not formatter:
            raise ValueError(f"Unsupported format: {output_format}")

        output = await formatter(formatted_data, options)

        # 4. 후처리
        if options and options.get('post_process', True):
            output = await self._post_process(output, output_format, options)

        return output

    async def _prepare_data(
        self,
        parsed_project: ParsedProject,
        analysis_results: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """데이터 준비 및 정리"""

        # 기본 프로젝트 정보
        data = {
            'project_info': parsed_project.project_info,
            'summary': {
                'total_requirements': (
                    len(parsed_project.functional_requirements) +
                    len(parsed_project.non_functional_requirements) +
                    len(parsed_project.technical_requirements) +
                    len(parsed_project.business_requirements)
                ),
                'functional_requirements_count': len(parsed_project.functional_requirements),
                'non_functional_requirements_count': len(parsed_project.non_functional_requirements),
                'user_stories_count': len(parsed_project.user_stories),
                'data_models_count': len(parsed_project.data_models),
                'api_endpoints_count': len(parsed_project.api_specifications)
            }
        }

        # 요구사항 섹션
        data['requirements'] = {
            'functional': [
                self._serialize_requirement(req)
                for req in parsed_project.functional_requirements
            ],
            'non_functional': [
                self._serialize_requirement(req)
                for req in parsed_project.non_functional_requirements
            ],
            'technical': [
                self._serialize_requirement(req)
                for req in parsed_project.technical_requirements
            ],
            'business': [
                self._serialize_requirement(req)
                for req in parsed_project.business_requirements
            ]
        }

        # 사용자 스토리
        data['user_stories'] = parsed_project.user_stories

        # 데이터 모델
        data['data_models'] = [
            self._serialize_data_model(model)
            for model in parsed_project.data_models
        ]

        # API 명세
        data['api_specifications'] = [
            self._serialize_api_spec(api)
            for api in parsed_project.api_specifications
        ]

        # 분석 결과 추가
        if analysis_results:
            data['analysis'] = {
                'dependencies': analysis_results.get('dependency_analysis', {}),
                'conflicts': analysis_results.get('conflict_analysis', {}),
                'traceability': analysis_results.get('traceability_analysis', {}),
                'quality_metrics': analysis_results.get('quality_metrics', {})
            }

        # 옵션에 따른 필터링
        if options and options.get('include_only'):
            data = self._filter_data(data, options['include_only'])

        return data

    async def _format_json(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """JSON 형식으로 포맷팅"""

        indent = options.get('indent', 2) if options else 2

        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=False,
            default=str
        )

    async def _format_yaml(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """YAML 형식으로 포맷팅"""

        return yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

    async def _format_xml(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """XML 형식으로 포맷팅"""

        root = ET.Element('project')

        # 프로젝트 정보
        info = ET.SubElement(root, 'info')
        for key, value in data['project_info'].items():
            elem = ET.SubElement(info, key)
            elem.text = str(value)

        # 요구사항
        requirements = ET.SubElement(root, 'requirements')
        for req_type, req_list in data['requirements'].items():
            type_elem = ET.SubElement(requirements, req_type)
            for req in req_list:
                req_elem = ET.SubElement(type_elem, 'requirement')
                req_elem.set('id', req['id'])
                for key, value in req.items():
                    if key != 'id':
                        sub_elem = ET.SubElement(req_elem, key)
                        if isinstance(value, list):
                            for item in value:
                                item_elem = ET.SubElement(sub_elem, 'item')
                                item_elem.text = str(item)
                        else:
                            sub_elem.text = str(value)

        # XML 문자열로 변환
        xml_str = ET.tostring(root, encoding='unicode')

        # 포맷팅
        if options and options.get('pretty_print', True):
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_str)
            return dom.toprettyxml(indent='  ')

        return xml_str
```

**마크다운 포맷터**:

```python
class MarkdownFormatter:
    """마크다운 형식 출력"""

    async def format_markdown(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """마크다운 형식으로 포맷팅"""

        md_lines = []

        # 프로젝트 정보
        md_lines.append(f"# {data['project_info'].get('name', 'Project Requirements')}")
        md_lines.append("")

        if data['project_info'].get('description'):
            md_lines.append(f"> {data['project_info']['description']}")
            md_lines.append("")

        # 요약 정보
        md_lines.append("## Summary")
        md_lines.append("")
        md_lines.append("| Metric | Count |")
        md_lines.append("|--------|-------|")

        for key, value in data['summary'].items():
            metric_name = key.replace('_', ' ').title()
            md_lines.append(f"| {metric_name} | {value} |")

        md_lines.append("")

        # 요구사항 섹션
        md_lines.append("## Requirements")
        md_lines.append("")

        # 기능 요구사항
        if data['requirements']['functional']:
            md_lines.append("### Functional Requirements")
            md_lines.append("")

            for req in data['requirements']['functional']:
                md_lines.append(f"#### {req['id']}: {req.get('title', 'Untitled')}")
                md_lines.append("")
                md_lines.append(f"**Description:** {req['description']}")
                md_lines.append("")

                if req.get('acceptance_criteria'):
                    md_lines.append("**Acceptance Criteria:**")
                    for criterion in req['acceptance_criteria']:
                        md_lines.append(f"- {criterion}")
                    md_lines.append("")

                md_lines.append(f"**Priority:** {req.get('priority', 'Not specified')}")
                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")

        # 사용자 스토리
        if data.get('user_stories'):
            md_lines.append("## User Stories")
            md_lines.append("")

            for story in data['user_stories']:
                md_lines.append(f"### {story.get('id', 'Story')}: {story.get('title', 'Untitled')}")
                md_lines.append("")
                md_lines.append(f"_{story.get('narrative', 'No narrative')}_")
                md_lines.append("")

                if story.get('acceptance_criteria'):
                    md_lines.append("**Acceptance Criteria:**")
                    for criterion in story['acceptance_criteria']:
                        md_lines.append(f"- {criterion}")
                    md_lines.append("")

        return "\n".join(md_lines)
```

**문서 생성기**:

```python
class DocumentGenerator:
    """고급 문서 형식 생성"""

    async def generate_docx(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> bytes:
        """DOCX 문서 생성"""

        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()

        # 제목
        title = doc.add_heading(
            data['project_info'].get('name', 'Project Requirements'),
            0
        )
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 요약 섹션
        doc.add_heading('Executive Summary', level=1)

        summary_para = doc.add_paragraph()
        summary_para.add_run('Project Overview: ').bold = True
        summary_para.add_run(
            data['project_info'].get('description', 'No description provided')
        )

        # 통계 테이블
        doc.add_heading('Requirements Statistics', level=2)

        table = doc.add_table(rows=1, cols=2)
        table.style = 'Light Grid Accent 1'

        # 헤더
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Metric'
        hdr_cells[1].text = 'Count'

        # 데이터
        for key, value in data['summary'].items():
            row_cells = table.add_row().cells
            row_cells[0].text = key.replace('_', ' ').title()
            row_cells[1].text = str(value)

        # 요구사항 섹션
        doc.add_page_break()
        doc.add_heading('Requirements Specification', level=1)

        # 각 요구사항 추가
        for req_type, requirements in data['requirements'].items():
            if requirements:
                doc.add_heading(
                    f'{req_type.title()} Requirements',
                    level=2
                )

                for req in requirements:
                    # 요구사항 ID와 제목
                    req_heading = doc.add_heading(level=3)
                    req_heading.add_run(f"{req['id']}: ").bold = True
                    req_heading.add_run(req.get('title', 'Untitled'))

                    # 설명
                    doc.add_paragraph(req['description'])

                    # 수용 기준
                    if req.get('acceptance_criteria'):
                        doc.add_paragraph('Acceptance Criteria:', style='Heading 4')
                        for criterion in req['acceptance_criteria']:
                            doc.add_paragraph(
                                criterion,
                                style='List Bullet'
                            )

        # 메모리에 저장
        import io
        docx_buffer = io.BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)

        return docx_buffer.getvalue()
```

**검증 기준**:

- [ ] 다양한 출력 형식 지원
- [ ] 형식별 최적화
- [ ] 스키마 검증
- [ ] 문서 템플릿 적용

#### SubTask 4.25.2: 다른 에이전트와의 인터페이스

**담당자**: 시스템 통합 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/agent_interface.py
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
import asyncio
from abc import ABC, abstractmethod

class AgentInterface(Protocol):
    """다른 에이전트와의 표준 인터페이스"""

    async def send_to_agent(
        self,
        target_agent: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        ...

    async def receive_from_agent(
        self,
        source_agent: str
    ) -> Any:
        ...

@dataclass
class ParserOutput:
    """Parser Agent 표준 출력 형식"""
    project_id: str
    parsed_project: ParsedProject
    analysis_results: Dict[str, Any]
    metadata: Dict[str, Any]
    version: str = "1.0"

class ParserAgentInterface:
    """Parser Agent의 다른 에이전트 인터페이스"""

    def __init__(self, parser_agent):
        self.parser_agent = parser_agent
        self.output_adapters = {
            'ui_selection': UISelectionAdapter(),
            'component_decision': ComponentDecisionAdapter(),
            'generation': GenerationAdapter(),
            'assembly': AssemblyAdapter()
        }

        self.message_queue = MessageQueue()
        self.event_bus = EventBus()

    async def prepare_for_ui_selection(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """UI Selection Agent를 위한 데이터 준비"""

        adapter = self.output_adapters['ui_selection']

        # UI 관련 요구사항 추출
        ui_requirements = await adapter.extract_ui_requirements(parsed_project)

        # 기술 스택 정보
        tech_stack = await adapter.extract_tech_stack(parsed_project)

        # 사용자 경험 요구사항
        ux_requirements = await adapter.extract_ux_requirements(parsed_project)

        # 플랫폼 정보
        platform_info = await adapter.extract_platform_info(parsed_project)

        return {
            'project_type': parsed_project.project_info.get('project_type'),
            'description': parsed_project.project_info.get('description'),
            'ui_requirements': ui_requirements,
            'tech_stack': tech_stack,
            'ux_requirements': ux_requirements,
            'platform_info': platform_info,
            'constraints': await adapter.extract_ui_constraints(parsed_project),
            'metadata': {
                'parser_version': self.parser_agent.version,
                'parsed_at': datetime.utcnow().isoformat()
            }
        }

    async def prepare_for_component_decision(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """Component Decision Agent를 위한 데이터 준비"""

        adapter = self.output_adapters['component_decision']

        # 컴포넌트 요구사항
        component_requirements = []

        # 기능 요구사항에서 컴포넌트 추출
        for req in parsed_project.functional_requirements:
            components = await adapter.extract_required_components(req)
            component_requirements.extend(components)

        # UI 컴포넌트
        ui_components = await adapter.extract_ui_components(
            parsed_project.ui_components
        )

        # 데이터 모델 기반 컴포넌트
        data_components = await adapter.extract_data_components(
            parsed_project.data_models
        )

        # API 기반 컴포넌트
        api_components = await adapter.extract_api_components(
            parsed_project.api_specifications
        )

        return {
            'functional_components': component_requirements,
            'ui_components': ui_components,
            'data_components': data_components,
            'api_components': api_components,
            'dependencies': await adapter.analyze_component_dependencies(
                component_requirements + ui_components + data_components
            ),
            'constraints': await adapter.extract_component_constraints(parsed_project),
            'metadata': {
                'total_components': len(component_requirements) + len(ui_components) + len(data_components),
                'complexity_score': await adapter.calculate_complexity_score(
                    component_requirements
                )
            }
        }

    async def send_to_agent(
        self,
        target_agent: str,
        parsed_output: ParserOutput
    ) -> Any:
        """다른 에이전트로 데이터 전송"""

        # 대상 에이전트별 데이터 준비
        if target_agent == 'ui_selection':
            data = await self.prepare_for_ui_selection(parsed_output.parsed_project)
        elif target_agent == 'component_decision':
            data = await self.prepare_for_component_decision(parsed_output.parsed_project)
        elif target_agent == 'generation':
            data = await self.prepare_for_generation(parsed_output.parsed_project)
        else:
            data = parsed_output

        # 메시지 전송
        message = AgentMessage(
            source='parser_agent',
            target=target_agent,
            data=data,
            correlation_id=parsed_output.project_id,
            timestamp=datetime.utcnow()
        )

        # 비동기 전송
        await self.message_queue.send(message)

        # 이벤트 발행
        await self.event_bus.publish(
            'parser.output.sent',
            {
                'target': target_agent,
                'project_id': parsed_output.project_id,
                'data_size': len(json.dumps(data))
            }
        )

        return message.id
```

**어댑터 구현**:

```python
# backend/src/agents/implementations/parser/adapters.py
class UISelectionAdapter:
    """UI Selection Agent용 어댑터"""

    async def extract_ui_requirements(
        self,
        parsed_project: ParsedProject
    ) -> List[Dict[str, Any]]:
        """UI 관련 요구사항 추출"""

        ui_requirements = []

        # UI 키워드 패턴
        ui_patterns = [
            r'(interface|ui|ux|design|layout|screen|page|view)',
            r'(responsive|mobile|desktop|tablet)',
            r'(button|form|menu|navigation|dashboard)',
            r'(user.?friendly|intuitive|accessible)'
        ]

        for req in parsed_project.functional_requirements:
            # UI 관련 여부 확인
            if any(re.search(pattern, req.description, re.IGNORECASE)
                   for pattern in ui_patterns):

                ui_req = {
                    'id': req.id,
                    'description': req.description,
                    'type': self._classify_ui_requirement(req),
                    'components': self._extract_ui_components(req),
                    'interactions': self._extract_interactions(req),
                    'responsive_requirements': self._extract_responsive_req(req)
                }

                ui_requirements.append(ui_req)

        return ui_requirements

    async def extract_tech_stack(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """기술 스택 정보 추출"""

        tech_mentions = {
            'frontend': [],
            'backend': [],
            'database': [],
            'infrastructure': []
        }

        # 모든 요구사항에서 기술 언급 찾기
        all_text = self._combine_all_text(parsed_project)

        # 프론트엔드 기술
        frontend_techs = [
            'react', 'vue', 'angular', 'svelte', 'next.js',
            'javascript', 'typescript', 'html', 'css'
        ]

        for tech in frontend_techs:
            if tech.lower() in all_text.lower():
                tech_mentions['frontend'].append(tech)

        # 백엔드 기술
        backend_techs = [
            'node.js', 'python', 'java', 'go', 'rust',
            'express', 'django', 'spring', 'fastapi'
        ]

        for tech in backend_techs:
            if tech.lower() in all_text.lower():
                tech_mentions['backend'].append(tech)

        return tech_mentions
```

**이벤트 기반 통신**:

```python
class ParserEventPublisher:
    """Parser Agent 이벤트 발행"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    async def publish_parsing_completed(
        self,
        project_id: str,
        parsed_project: ParsedProject,
        duration: float
    ):
        """파싱 완료 이벤트 발행"""

        await self.event_bus.publish(
            'parser.parsing.completed',
            {
                'project_id': project_id,
                'requirements_count': {
                    'functional': len(parsed_project.functional_requirements),
                    'non_functional': len(parsed_project.non_functional_requirements),
                    'technical': len(parsed_project.technical_requirements),
                    'business': len(parsed_project.business_requirements)
                },
                'user_stories_count': len(parsed_project.user_stories),
                'data_models_count': len(parsed_project.data_models),
                'api_endpoints_count': len(parsed_project.api_specifications),
                'parsing_duration_ms': duration * 1000,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

    async def publish_analysis_completed(
        self,
        project_id: str,
        analysis_type: str,
        results: Dict[str, Any]
    ):
        """분석 완료 이벤트 발행"""

        await self.event_bus.publish(
            f'parser.analysis.{analysis_type}.completed',
            {
                'project_id': project_id,
                'analysis_type': analysis_type,
                'results_summary': self._summarize_results(results),
                'timestamp': datetime.utcnow().isoformat()
            }
        )
```

**검증 기준**:

- [ ] 표준 인터페이스 구현
- [ ] 에이전트별 어댑터
- [ ] 이벤트 기반 통신
- [ ] 데이터 변환 정확도

#### SubTask 4.25.3: 파싱 결과 캐싱 및 버전 관리

**담당자**: 데이터 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/caching_system.py
from typing import Dict, Any, Optional, List
import hashlib
import json
from datetime import datetime, timedelta
import redis
import pickle

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    version: str
    metadata: Dict[str, Any]

class ParserCachingSystem:
    """파싱 결과 캐싱 시스템"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_prefix = "parser_cache"
        self.version_manager = VersionManager()
        self.cache_stats = CacheStatistics()

    async def cache_parsing_result(
        self,
        raw_input: str,
        parsed_project: ParsedProject,
        analysis_results: Dict[str, Any],
        ttl: Optional[int] = 3600  # 1시간 기본
    ) -> str:
        """파싱 결과 캐싱"""

        # 캐시 키 생성
        cache_key = self._generate_cache_key(raw_input)

        # 버전 정보 추가
        version = self.version_manager.get_current_version()

        # 캐시 데이터 준비
        cache_data = {
            'parsed_project': self._serialize_parsed_project(parsed_project),
            'analysis_results': analysis_results,
            'metadata': {
                'cached_at': datetime.utcnow().isoformat(),
                'parser_version': version,
                'input_hash': hashlib.sha256(raw_input.encode()).hexdigest(),
                'input_length': len(raw_input)
            }
        }

        # Redis에 저장
        full_key = f"{self.cache_prefix}:{cache_key}"

        await self.redis.setex(
            full_key,
            ttl,
            pickle.dumps(cache_data)
        )

        # 캐시 인덱스 업데이트
        await self._update_cache_index(cache_key, cache_data['metadata'])

        # 통계 업데이트
        self.cache_stats.record_cache_write(len(pickle.dumps(cache_data)))

        return cache_key

    async def get_cached_result(
        self,
        raw_input: str
    ) -> Optional[Tuple[ParsedProject, Dict[str, Any]]]:
        """캐시된 결과 조회"""

        # 캐시 키 생성
        cache_key = self._generate_cache_key(raw_input)
        full_key = f"{self.cache_prefix}:{cache_key}"

        # Redis에서 조회
        cached_data = await self.redis.get(full_key)

        if not cached_data:
            self.cache_stats.record_cache_miss()
            return None

        # 역직렬화
        try:
            data = pickle.loads(cached_data)

            # 버전 확인
            cached_version = data['metadata'].get('parser_version')
            current_version = self.version_manager.get_current_version()

            if not self.version_manager.is_compatible(cached_version, current_version):
                # 버전 비호환 - 캐시 무효화
                await self.invalidate_cache(cache_key)
                self.cache_stats.record_cache_miss()
                return None

            # 파싱 결과 복원
            parsed_project = self._deserialize_parsed_project(
                data['parsed_project']
            )

            self.cache_stats.record_cache_hit()

            return parsed_project, data['analysis_results']

        except Exception as e:
            # 캐시 데이터 손상 - 삭제
            await self.invalidate_cache(cache_key)
            self.cache_stats.record_cache_error(str(e))
            return None

    def _generate_cache_key(self, raw_input: str) -> str:
        """캐시 키 생성"""
        # 입력 정규화
        normalized_input = self._normalize_input(raw_input)

        # SHA256 해시
        input_hash = hashlib.sha256(normalized_input.encode()).hexdigest()

        # 버전 프리픽스 추가
        version_prefix = self.version_manager.get_version_prefix()

        return f"{version_prefix}:{input_hash[:16]}"

    def _normalize_input(self, raw_input: str) -> str:
        """입력 정규화"""
        # 공백 정규화
        normalized = ' '.join(raw_input.split())

        # 대소문자 통일
        normalized = normalized.lower()

        # 특수문자 제거 (선택적)
        # normalized = re.sub(r'[^\w\s]', '', normalized)

        return normalized

    async def invalidate_cache(self, cache_key: str) -> bool:
        """캐시 무효화"""
        full_key = f"{self.cache_prefix}:{cache_key}"

        result = await self.redis.delete(full_key)

        # 인덱스에서 제거
        await self._remove_from_cache_index(cache_key)

        return result > 0

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        return {
            'hit_rate': self.cache_stats.get_hit_rate(),
            'total_hits': self.cache_stats.total_hits,
            'total_misses': self.cache_stats.total_misses,
            'total_writes': self.cache_stats.total_writes,
            'total_errors': self.cache_stats.total_errors,
            'average_cache_size': self.cache_stats.get_average_size(),
            'cache_entries': await self._count_cache_entries()
        }
```

**버전 관리 시스템**:

```python
# backend/src/agents/implementations/parser/version_manager.py
class VersionManager:
    """파서 버전 관리"""

    def __init__(self):
        self.current_version = "1.2.0"
        self.compatibility_matrix = {
            "1.2.0": ["1.2.0", "1.1.0"],  # 1.2.0은 1.1.0과 호환
            "1.1.0": ["1.1.0", "1.0.0"],
            "1.0.0": ["1.0.0"]
        }

        self.version_history = []
        self.migration_handlers = {
            ("1.0.0", "1.1.0"): self._migrate_1_0_to_1_1,
            ("1.1.0", "1.2.0"): self._migrate_1_1_to_1_2
        }

    def is_compatible(self, cached_version: str, current_version: str) -> bool:
        """버전 호환성 확인"""
        if cached_version == current_version:
            return True

        compatible_versions = self.compatibility_matrix.get(
            current_version, []
        )

        return cached_version in compatible_versions

    async def migrate_parsed_data(
        self,
        data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """파싱 데이터 마이그레이션"""

        # 마이그레이션 경로 찾기
        migration_path = self._find_migration_path(from_version, to_version)

        if not migration_path:
            raise ValueError(
                f"No migration path from {from_version} to {to_version}"
            )

        # 단계별 마이그레이션 실행
        current_data = data
        for i in range(len(migration_path) - 1):
            from_ver = migration_path[i]
            to_ver = migration_path[i + 1]

            handler = self.migration_handlers.get((from_ver, to_ver))
            if handler:
                current_data = await handler(current_data)
            else:
                raise ValueError(
                    f"No migration handler for {from_ver} to {to_ver}"
                )

        return current_data

    async def _migrate_1_0_to_1_1(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """1.0.0에서 1.1.0으로 마이그레이션"""

        # 새로운 필드 추가
        if 'parsed_project' in data:
            project = data['parsed_project']

            # constraints 필드 추가
            if 'constraints' not in project:
                project['constraints'] = []

            # assumptions 필드 추가
            if 'assumptions' not in project:
                project['assumptions'] = []

        return data

    async def _migrate_1_1_to_1_2(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """1.1.0에서 1.2.0으로 마이그레이션"""

        # 데이터 구조 변경
        if 'parsed_project' in data:
            project = data['parsed_project']

            # use_cases 구조 변경
            if 'use_cases' in project and isinstance(project['use_cases'], list):
                # 리스트를 딕셔너리 구조로 변경
                new_use_cases = []
                for idx, uc in enumerate(project['use_cases']):
                    if isinstance(uc, str):
                        new_use_cases.append({
                            'id': f'UC-{idx+1:03d}',
                            'description': uc,
                            'actors': [],
                            'steps': []
                        })
                    else:
                        new_use_cases.append(uc)

                project['use_cases'] = new_use_cases

        return data
```

**캐시 예열 시스템**:

```python
class CacheWarmer:
    """캐시 예열 시스템"""

    def __init__(self, caching_system: ParserCachingSystem):
        self.caching_system = caching_system
        self.parser_agent = None  # 주입됨

    async def warm_cache_from_templates(
        self,
        templates: List[Dict[str, Any]]
    ):
        """템플릿 기반 캐시 예열"""

        warmed_count = 0

        for template in templates:
            try:
                # 템플릿에서 요구사항 생성
                generated_input = await self._generate_from_template(template)

                # 파싱 실행
                parsed_project = await self.parser_agent.parse_requirements(
                    generated_input
                )

                # 분석 실행
                analysis_results = await self.parser_agent.analyze_all(
                    parsed_project
                )

                # 캐싱
                await self.caching_system.cache_parsing_result(
                    generated_input,
                    parsed_project,
                    analysis_results,
                    ttl=86400  # 24시간
                )

                warmed_count += 1

            except Exception as e:
                print(f"Failed to warm cache for template: {e}")

        return warmed_count
```

**검증 기준**:

- [ ] 효율적인 캐싱 메커니즘
- [ ] 버전 호환성 관리
- [ ] 캐시 통계 및 모니터링
- [ ] 자동 캐시 예열

#### SubTask 4.25.4: Parser Agent API 엔드포인트

**담당자**: API 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/agents/parser_endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio

router = APIRouter(prefix="/api/v1/agents/parser", tags=["parser-agent"])

class ParseRequest(BaseModel):
    """파싱 요청 모델"""
    project_name: str = Field(..., description="Project name")
    description: str = Field(..., description="Natural language requirements", max_length=50000)
    domain: Optional[str] = Field(None, description="Project domain")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_format: Optional[str] = Field("json", description="Output format")

class ParseResponse(BaseModel):
    """파싱 응답 모델"""
    project_id: str
    status: str
    parsed_requirements_count: int
    user_stories_count: int
    data_models_count: int
    api_endpoints_count: int
    cache_hit: bool
    parsing_time_ms: float
    download_url: Optional[str]

@router.post("/parse", response_model=ParseResponse)
async def parse_requirements(
    request: ParseRequest,
    background_tasks: BackgroundTasks
):
    """
    자연어 요구사항 파싱

    프로젝트 설명을 분석하여 구조화된 요구사항으로 변환합니다.
    """
    start_time = asyncio.get_event_loop().time()

    # 프로젝트 ID 생성
    project_id = generate_project_id()

    # 캐시 확인
    cached_result = await parser_agent.caching_system.get_cached_result(
        request.description
    )

    if cached_result:
        parsed_project, analysis_results = cached_result
        cache_hit = True
    else:
        # 파싱 실행
        parsed_project = await parser_agent.parse_requirements(
            request.description,
            project_context={
                'name': request.project_name,
                'domain': request.domain
            },
            parsing_options=request.options
        )

        # 분석 실행
        analysis_results = await parser_agent.analyze_all(parsed_project)

        # 캐싱
        await parser_agent.caching_system.cache_parsing_result(
            request.description,
            parsed_project,
            analysis_results
        )

        cache_hit = False

    # 출력 형식 변환
    if request.output_format != "json":
        background_tasks.add_task(
            generate_formatted_output,
            project_id,
            parsed_project,
            analysis_results,
            request.output_format
        )

    parsing_time = (asyncio.get_event_loop().time() - start_time) * 1000

    # 프로젝트 저장
    await save_project(project_id, parsed_project, analysis_results)

    return ParseResponse(
        project_id=project_id,
        status="completed",
        parsed_requirements_count=len(parsed_project.functional_requirements) +
                                len(parsed_project.non_functional_requirements),
        user_stories_count=len(parsed_project.user_stories),
        data_models_count=len(parsed_project.data_models),
        api_endpoints_count=len(parsed_project.api_specifications),
        cache_hit=cache_hit,
        parsing_time_ms=parsing_time,
        download_url=f"/api/v1/projects/{project_id}/download"
    )

@router.post("/parse-file")
async def parse_requirements_file(
    file: UploadFile = File(..., description="Requirements document"),
    domain: Optional[str] = None
):
    """
    파일에서 요구사항 파싱

    지원 형식: TXT, MD, DOCX, PDF
    """
    # 파일 형식 확인
    if not file.filename.endswith(('.txt', '.md', '.docx', '.pdf')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format"
        )

    # 파일 내용 읽기
    content = await read_file_content(file)

    # 파싱 요청 처리
    request = ParseRequest(
        project_name=file.filename.split('.')[0],
        description=content,
        domain=domain
    )

    return await parse_requirements(request, BackgroundTasks())

@router.get("/projects/{project_id}/analysis/{analysis_type}")
async def get_analysis_result(
    project_id: str,
    analysis_type: str
):
    """
    특정 분석 결과 조회

    분석 유형:
    - dependencies: 의존성 분석
    - conflicts: 충돌 분석
    - traceability: 추적성 분석
    - quality: 품질 메트릭
    """
    # 프로젝트 조회
    project = await get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 분석 결과 조회
    if analysis_type not in ['dependencies', 'conflicts', 'traceability', 'quality']:
        raise HTTPException(
            status_code=400,
            detail="Invalid analysis type"
        )

    analysis_result = project['analysis_results'].get(f'{analysis_type}_analysis')

    if not analysis_result:
        raise HTTPException(
            status_code=404,
            detail=f"{analysis_type} analysis not found"
        )

    return analysis_result

@router.post("/projects/{project_id}/reparse")
async def reparse_project(
    project_id: str,
    options: Optional[Dict[str, Any]] = None
):
    """
    프로젝트 재파싱

    캐시를 무시하고 강제로 재파싱합니다.
    """
    # 기존 프로젝트 조회
    project = await get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 캐시 무효화
    await parser_agent.caching_system.invalidate_cache(
        project['original_description']
    )

    # 재파싱
    parsed_project = await parser_agent.parse_requirements(
        project['original_description'],
        project_context=project['context'],
        parsing_options=options or {}
    )

    # 분석 재실행
    analysis_results = await parser_agent.analyze_all(parsed_project)

    # 업데이트
    await update_project(project_id, parsed_project, analysis_results)

    return {
        'project_id': project_id,
        'status': 'reparsed',
        'message': 'Project successfully reparsed'
    }

@router.get("/cache/statistics")
async def get_cache_statistics():
    """캐시 통계 조회"""

    stats = await parser_agent.caching_system.get_cache_statistics()

    return {
        'cache_statistics': stats,
        'parser_version': parser_agent.version,
        'uptime_seconds': parser_agent.get_uptime()
    }

@router.delete("/cache")
async def clear_cache():
    """캐시 전체 삭제"""

    cleared_count = await parser_agent.caching_system.clear_all()

    return {
        'status': 'cleared',
        'cleared_entries': cleared_count
    }
```

**웹소켓 엔드포인트**:

```python
# backend/src/api/agents/parser_websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json

@router.websocket("/ws/parse-stream")
async def parse_requirements_stream(websocket: WebSocket):
    """
    실시간 파싱 스트림

    대용량 요구사항의 점진적 파싱 결과를 스트리밍합니다.
    """
    await websocket.accept()

    try:
        while True:
            # 클라이언트로부터 데이터 수신
            data = await websocket.receive_text()
            request = json.loads(data)

            if request['type'] == 'start_parsing':
                # 스트리밍 파서 시작
                async for progress in parser_agent.parse_streaming(
                    request['description'],
                    request.get('options', {})
                ):
                    await websocket.send_json({
                        'type': 'progress',
                        'data': progress
                    })

                # 완료
                await websocket.send_json({
                    'type': 'completed',
                    'project_id': progress['project_id']
                })

            elif request['type'] == 'analyze':
                # 실시간 분석
                project_id = request['project_id']
                analysis_type = request['analysis_type']

                async for result in parser_agent.analyze_streaming(
                    project_id,
                    analysis_type
                ):
                    await websocket.send_json({
                        'type': 'analysis_progress',
                        'data': result
                    })

    except WebSocketDisconnect:
        print(f"Client disconnected")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })
        await websocket.close()
```

**검증 기준**:

- [ ] RESTful API 구현
- [ ] 웹소켓 실시간 통신
- [ ] 파일 업로드 지원
- [ ] API 문서화 (OpenAPI)

### Task 4.26: Parser Agent 고급 기능 및 최적화

#### SubTask 4.26.1: 다국어 요구사항 파싱 지원

**담당자**: 국제화 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/multilingual_parser.py
from typing import Dict, Any, List, Optional
from googletrans import Translator
import langdetect
from dataclasses import dataclass

@dataclass
class MultilingualRequirement:
    original_text: str
    original_language: str
    translated_text: str
    confidence: float
    cultural_notes: List[str]

class MultilingualParser:
    """다국어 요구사항 파싱 지원"""

    def __init__(self):
        self.translator = Translator()
        self.supported_languages = [
            'en', 'ko', 'ja', 'zh-cn', 'zh-tw', 'es', 'fr', 'de',
            'pt', 'ru', 'ar', 'hi', 'vi', 'th', 'id'
        ]

        self.language_specific_parsers = {
            'ko': KoreanRequirementParser(),
            'ja': JapaneseRequirementParser(),
            'zh': ChineseRequirementParser()
        }

        self.cultural_adapters = {
            'ko': KoreanCulturalAdapter(),
            'ja': JapaneseCulturalAdapter(),
            'zh': ChineseCulturalAdapter()
        }

    async def parse_multilingual_requirements(
        self,
        text: str,
        target_language: str = 'en',
        preserve_original: bool = True
    ) -> Dict[str, Any]:
        """다국어 요구사항 파싱"""

        # 1. 언어 감지
        detected_language = await self._detect_language(text)

        # 2. 언어별 전처리
        preprocessed_text = await self._preprocess_by_language(
            text,
            detected_language
        )

        # 3. 번역 (필요한 경우)
        if detected_language != target_language:
            translated_text = await self._translate_requirements(
                preprocessed_text,
                detected_language,
                target_language
            )
        else:
            translated_text = preprocessed_text

        # 4. 언어별 파싱
        if detected_language in self.language_specific_parsers:
            # 원어 파싱
            original_parsed = await self.language_specific_parsers[
                detected_language
            ].parse(preprocessed_text)
        else:
            original_parsed = None

        # 5. 대상 언어로 파싱
        target_parsed = await self.parser_agent.parse_requirements(
            translated_text
        )

        # 6. 문화적 적응
        if detected_language in self.cultural_adapters:
            cultural_notes = await self.cultural_adapters[
                detected_language
            ].analyze(preprocessed_text, target_parsed)
        else:
            cultural_notes = []

        # 7. 결과 통합
        return {
            'original_language': detected_language,
            'target_language': target_language,
            'original_text': text if preserve_original else None,
            'translated_text': translated_text,
            'parsed_requirements': target_parsed,
            'original_parsed': original_parsed,
            'cultural_notes': cultural_notes,
            'translation_confidence': await self._assess_translation_quality(
                preprocessed_text,
                translated_text,
                detected_language,
                target_language
            )
        }

    async def _detect_language(self, text: str) -> str:
        """언어 자동 감지"""
        try:
            # langdetect 사용
            detected = langdetect.detect(text)

            # 신뢰도 확인
            probabilities = langdetect.detect_langs(text)
            confidence = max(p.prob for p in probabilities)

            if confidence < 0.8:
                # 낮은 신뢰도 - 추가 검증
                detected = await self._verify_language_detection(text, detected)

            return detected

        except Exception as e:
            # 기본값으로 영어 반환
            return 'en'

    async def _translate_requirements(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """요구사항 번역"""

        # 텍스트 분할 (Google Translate API 제한)
        chunks = self._split_text_for_translation(text)
        translated_chunks = []

        for chunk in chunks:
            # 도메인 용어 보호
            protected_text, term_map = self._protect_domain_terms(
                chunk,
                source_lang
            )

            # 번역
            translated = self.translator.translate(
                protected_text,
                src=source_lang,
                dest=target_lang
            ).text

            # 도메인 용어 복원
            translated = self._restore_domain_terms(translated, term_map)

            translated_chunks.append(translated)

        return ' '.join(translated_chunks)

    def _protect_domain_terms(
        self,
        text: str,
        language: str
    ) -> Tuple[str, Dict[str, str]]:
        """도메인 용어 보호"""

        # 언어별 도메인 용어
        domain_terms = self._get_domain_terms(language)
        term_map = {}
        protected_text = text

        for idx, term in enumerate(domain_terms):
            if term in text:
                placeholder = f"__TERM_{idx}__"
                term_map[placeholder] = term
                protected_text = protected_text.replace(term, placeholder)

        return protected_text, term_map
```

**한국어 요구사항 파서**:

```python
# backend/src/agents/implementations/parser/language_specific/korean_parser.py
class KoreanRequirementParser:
    """한국어 요구사항 전문 파서"""

    def __init__(self):
        # 한국어 형태소 분석기
        from konlpy.tag import Okt
        self.okt = Okt()

        self.korean_patterns = {
            'requirement': [
                r'(.+)(?:해야\s*합니다|해야\s*함|하여야\s*함)',
                r'(.+)(?:이어야\s*합니다|이어야\s*함)',
                r'(.+)(?:되어야\s*합니다|되어야\s*함)',
                r'(.+)(?:가능해야\s*합니다|가능해야\s*함)'
            ],
            'feature': [
                r'(.+)\s*기능',
                r'(.+)\s*서비스',
                r'(.+)\s*시스템'
            ]
        }

    async def parse(self, text: str) -> List[Dict[str, Any]]:
        """한국어 요구사항 파싱"""

        requirements = []

        # 문장 분리
        sentences = self._split_korean_sentences(text)

        for sentence in sentences:
            # 형태소 분석
            morphs = self.okt.pos(sentence)

            # 요구사항 패턴 매칭
            for pattern_type, patterns in self.korean_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, sentence)
                    if match:
                        requirement = {
                            'type': pattern_type,
                            'text': sentence,
                            'extracted': match.group(1) if match.lastindex else sentence,
                            'morphs': morphs
                        }
                        requirements.append(requirement)
                        break

        return requirements

    def _split_korean_sentences(self, text: str) -> List[str]:
        """한국어 문장 분리"""
        # 한국어 문장 종결 패턴
        sentence_endings = r'[.!?。]\s*'
        sentences = re.split(sentence_endings, text)

        # 빈 문장 제거
        return [s.strip() for s in sentences if s.strip()]
```

**문화적 적응 시스템**:

```python
class CulturalAdapter:
    """문화적 컨텍스트 적응"""

    async def analyze(
        self,
        original_text: str,
        parsed_requirements: ParsedProject
    ) -> List[str]:
        """문화적 차이 분석 및 권장사항"""

        cultural_notes = []

        # 날짜/시간 형식
        date_formats = self._check_date_formats(original_text)
        if date_formats:
            cultural_notes.append(
                f"Date format consideration: {date_formats}"
            )

        # 통화 및 숫자 형식
        currency_formats = self._check_currency_formats(original_text)
        if currency_formats:
            cultural_notes.append(
                f"Currency format: {currency_formats}"
            )

        # 이름 순서
        name_order = self._check_name_order(original_text)
        if name_order:
            cultural_notes.append(
                f"Name order convention: {name_order}"
            )

        # 색상 의미
        color_meanings = self._check_color_meanings(parsed_requirements)
        if color_meanings:
            cultural_notes.extend(color_meanings)

        return cultural_notes

class KoreanCulturalAdapter(CulturalAdapter):
    """한국 문화 적응"""

    def _check_specific_cultural_aspects(
        self,
        text: str
    ) -> List[str]:
        """한국 특화 문화적 요소 확인"""

        notes = []

        # 나이 계산 방식
        if '나이' in text or '연령' in text:
            notes.append(
                "Age calculation: Korean age system vs. international age"
            )

        # 주민등록번호 관련
        if '주민등록' in text or '주민번호' in text:
            notes.append(
                "Personal ID: Consider KRRN (Korean Resident Registration Number) format and privacy regulations"
            )

        # 결제 수단
        if '결제' in text or '송금' in text:
            notes.append(
                "Payment methods: Include Korean-specific options (Kakao Pay, Naver Pay, Toss)"
            )

        return notes
```

**검증 기준**:

- [ ] 15개 이상 언어 지원
- [ ] 번역 정확도 90% 이상
- [ ] 도메인 용어 보존
- [ ] 문화적 적응 권장사항

#### SubTask 4.26.2: 증분 파싱 및 실시간 업데이트

**담당자**: 실시간 시스템 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/incremental_parser.py
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import difflib
import asyncio

@dataclass
class TextChange:
    operation: str  # 'insert', 'delete', 'replace'
    start_pos: int
    end_pos: int
    old_text: Optional[str]
    new_text: Optional[str]
    affected_sections: List[str]

class IncrementalParser:
    """증분 파싱 및 실시간 업데이트"""

    def __init__(self, parser_agent):
        self.parser_agent = parser_agent
        self.parsing_sessions = {}  # session_id -> ParsingSession
        self.change_detector = ChangeDetector()
        self.update_scheduler = UpdateScheduler()

    async def create_parsing_session(
        self,
        initial_text: str,
        session_id: str
    ) -> Dict[str, Any]:
        """파싱 세션 생성"""

        # 초기 파싱
        initial_result = await self.parser_agent.parse_requirements(initial_text)

        # 세션 생성
        session = ParsingSession(
            session_id=session_id,
            current_text=initial_text,
            current_result=initial_result,
            change_history=[],
            section_map=self._create_section_map(initial_text, initial_result)
        )

        self.parsing_sessions[session_id] = session

        return {
            'session_id': session_id,
            'initial_parsing': initial_result,
            'status': 'active'
        }

    async def update_text(
        self,
        session_id: str,
        new_text: str
    ) -> Dict[str, Any]:
        """텍스트 업데이트 및 증분 파싱"""

        session = self.parsing_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 1. 변경 사항 감지
        changes = self.change_detector.detect_changes(
            session.current_text,
            new_text
        )

        if not changes:
            return {
                'status': 'no_changes',
                'result': session.current_result
            }

        # 2. 영향받는 섹션 식별
        affected_sections = await self._identify_affected_sections(
            changes,
            session
        )

        # 3. 증분 파싱 전략 결정
        parsing_strategy = self._determine_parsing_strategy(
            changes,
            affected_sections
        )

        # 4. 증분 파싱 실행
        if parsing_strategy == 'incremental':
            updated_result = await self._incremental_parse(
                session,
                changes,
                affected_sections,
                new_text
            )
        else:
            # 전체 재파싱
            updated_result = await self.parser_agent.parse_requirements(new_text)

        # 5. 세션 업데이트
        session.current_text = new_text
        session.current_result = updated_result
        session.change_history.append({
            'timestamp': datetime.utcnow(),
            'changes': changes,
            'affected_sections': affected_sections
        })

        # 6. 변경 사항 요약
        change_summary = self._summarize_changes(
            session.current_result,
            updated_result
        )

        return {
            'status': 'updated',
            'parsing_strategy': parsing_strategy,
            'changes_detected': len(changes),
            'affected_sections': affected_sections,
            'change_summary': change_summary,
            'updated_result': updated_result
        }

    async def _incremental_parse(
        self,
        session: 'ParsingSession',
        changes: List[TextChange],
        affected_sections: Set[str],
        new_text: str
    ) -> ParsedProject:
        """증분 파싱 실행"""

        # 기존 결과 복사
        updated_result = self._deep_copy_parsed_project(session.current_result)

        # 영향받는 섹션별 처리
        for section in affected_sections:
            if section == 'functional_requirements':
                # 기능 요구사항 재파싱
                updated_reqs = await self._reparse_functional_requirements(
                    new_text,
                    changes,
                    session.current_result.functional_requirements
                )
                updated_result.functional_requirements = updated_reqs

            elif section == 'data_models':
                # 데이터 모델 재파싱
                updated_models = await self._reparse_data_models(
                    new_text,
                    changes,
                    session.current_result.data_models
                )
                updated_result.data_models = updated_models

            # ... 다른 섹션들

        # 의존성 재분석 (필요한 경우)
        if self._requires_dependency_reanalysis(affected_sections):
            updated_result = await self._update_dependencies(updated_result)

        return updated_result

    async def stream_parsing_updates(
        self,
        session_id: str,
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[Dict[str, Any]]:
        """실시간 스트리밍 파싱"""

        session = self.parsing_sessions.get(session_id)
        if not session:
            # 새 세션 생성
            session = await self.create_parsing_session("", session_id)

        buffer = ""
        last_parse_time = time.time()

        async for text_chunk in text_stream:
            buffer += text_chunk

            # 파싱 스케줄링 (디바운싱)
            if self.update_scheduler.should_parse(
                buffer,
                time.time() - last_parse_time
            ):
                # 증분 파싱
                result = await self.update_text(session_id, buffer)

                yield {
                    'type': 'parsing_update',
                    'timestamp': datetime.utcnow().isoformat(),
                    'text_length': len(buffer),
                    'result': result
                }

                last_parse_time = time.time()

        # 최종 파싱
        final_result = await self.update_text(session_id, buffer)
        yield {
            'type': 'parsing_complete',
            'timestamp': datetime.utcnow().isoformat(),
            'final_result': final_result
        }
```

**변경 감지 시스템**:

```python
class ChangeDetector:
    """텍스트 변경 감지"""

    def detect_changes(
        self,
        old_text: str,
        new_text: str
    ) -> List[TextChange]:
        """변경 사항 감지"""

        # 줄 단위 비교
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        # diff 생성
        differ = difflib.SequenceMatcher(None, old_lines, new_lines)
        changes = []

        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'replace':
                change = TextChange(
                    operation='replace',
                    start_pos=self._line_to_pos(old_lines, i1),
                    end_pos=self._line_to_pos(old_lines, i2),
                    old_text=''.join(old_lines[i1:i2]),
                    new_text=''.join(new_lines[j1:j2]),
                    affected_sections=[]
                )
                changes.append(change)

            elif tag == 'delete':
                change = TextChange(
                    operation='delete',
                    start_pos=self._line_to_pos(old_lines, i1),
                    end_pos=self._line_to_pos(old_lines, i2),
                    old_text=''.join(old_lines[i1:i2]),
                    new_text=None,
                    affected_sections=[]
                )
                changes.append(change)

            elif tag == 'insert':
                change = TextChange(
                    operation='insert',
                    start_pos=self._line_to_pos(old_lines, i1),
                    end_pos=self._line_to_pos(old_lines, i1),
                    old_text=None,
                    new_text=''.join(new_lines[j1:j2]),
                    affected_sections=[]
                )
                changes.append(change)

        return changes
```

**업데이트 스케줄러**:

```python
class UpdateScheduler:
    """파싱 업데이트 스케줄링"""

    def __init__(self):
        self.min_interval = 0.5  # 최소 0.5초
        self.max_interval = 2.0  # 최대 2초
        self.text_change_threshold = 50  # 50자 이상 변경

    def should_parse(
        self,
        current_text: str,
        time_since_last_parse: float
    ) -> bool:
        """파싱 실행 여부 결정"""

        # 시간 기반
        if time_since_last_parse >= self.max_interval:
            return True

        if time_since_last_parse < self.min_interval:
            return False

        # 변경량 기반
        if hasattr(self, '_last_text'):
            change_size = abs(len(current_text) - len(self._last_text))
            if change_size >= self.text_change_threshold:
                self._last_text = current_text
                return True
        else:
            self._last_text = current_text

        return False
```

**검증 기준**:

- [ ] 증분 파싱 정확도
- [ ] 실시간 업데이트 지연 < 500ms
- [ ] 변경 감지 정확도
- [ ] 메모리 효율성

#### SubTask 4.26.3: Parser Agent 성능 최적화

**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/performance_optimizer.py
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import cProfile
import pstats

class ParserPerformanceOptimizer:
    """Parser Agent 성능 최적화"""

    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())
        self.batch_processor = BatchProcessor()
        self.cache_optimizer = CacheOptimizer()
        self.profiler = PerformanceProfiler()

    async def optimize_parsing_performance(
        self,
        parser_agent,
        requirements_text: str
    ) -> Dict[str, Any]:
        """파싱 성능 최적화"""

        # 1. 텍스트 분할 전략
        chunks = self._intelligent_text_splitting(requirements_text)

        # 2. 병렬 처리 전략 선택
        if len(chunks) > 1 and len(requirements_text) > 10000:
            # 대용량 텍스트 - 병렬 처리
            result = await self._parallel_parse(parser_agent, chunks)
        else:
            # 소규모 텍스트 - 최적화된 단일 처리
            result = await self._optimized_single_parse(
                parser_agent,
                requirements_text
            )

        return result

    def _intelligent_text_splitting(
        self,
        text: str
    ) -> List[str]:
        """지능적 텍스트 분할"""

        # 섹션 마커 찾기
        section_markers = [
            r'\n#{1,3}\s+',  # 마크다운 헤더
            r'\n\d+\.\s+',    # 번호 목록
            r'\n[A-Z][^.!?]*:\s*\n',  # 섹션 제목
            r'\n\n',          # 단락 구분
        ]

        chunks = []
        current_chunk = []
        current_size = 0
        optimal_chunk_size = 5000  # 5KB

        lines = text.split('\n')

        for line in lines:
            # 섹션 경계 확인
            is_boundary = any(
                re.match(marker, '\n' + line)
                for marker in section_markers
            )

            if is_boundary and current_size > optimal_chunk_size:
                # 새 청크 시작
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)

        # 마지막 청크
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    async def _parallel_parse(
        self,
        parser_agent,
        chunks: List[str]
    ) -> ParsedProject:
        """병렬 파싱 실행"""

        # 청크별 파싱 태스크
        parse_tasks = []

        for idx, chunk in enumerate(chunks):
            task = asyncio.create_task(
                self._parse_chunk(parser_agent, chunk, idx)
            )
            parse_tasks.append(task)

        # 병렬 실행
        chunk_results = await asyncio.gather(*parse_tasks)

        # 결과 병합
        merged_result = await self._merge_chunk_results(chunk_results)

        # 후처리 - 중복 제거 및 일관성 확인
        final_result = await self._post_process_merged_result(merged_result)

        return final_result

    async def _parse_chunk(
        self,
        parser_agent,
        chunk: str,
        chunk_index: int
    ) -> Dict[str, Any]:
        """개별 청크 파싱"""

        # CPU 집약적 작업은 프로세스 풀에서 실행
        loop = asyncio.get_event_loop()

        # NLP 전처리
        preprocessed = await loop.run_in_executor(
            self.process_pool,
            self._heavy_preprocessing,
            chunk
        )

        # 파싱 실행
        result = await parser_agent.parse_requirements(
            preprocessed,
            parsing_options={
                'chunk_mode': True,
                'chunk_index': chunk_index
            }
        )

        return {
            'chunk_index': chunk_index,
            'result': result,
            'chunk_size': len(chunk)
        }

    def _heavy_preprocessing(self, text: str) -> str:
        """CPU 집약적 전처리 (프로세스 풀에서 실행)"""

        # 텍스트 정규화
        normalized = unicodedata.normalize('NFKC', text)

        # 특수 문자 처리
        cleaned = re.sub(r'[^\w\s\n.,:;!?()-]', ' ', normalized)

        # 공백 정규화
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)

        return cleaned

    async def _merge_chunk_results(
        self,
        chunk_results: List[Dict[str, Any]]
    ) -> ParsedProject:
        """청크 결과 병합"""

        # 결과 정렬
        chunk_results.sort(key=lambda x: x['chunk_index'])

        # 병합된 프로젝트 초기화
        merged = ParsedProject(
            project_info={},
            functional_requirements=[],
            non_functional_requirements=[],
            technical_requirements=[],
            business_requirements=[],
            constraints=[],
            assumptions=[],
            user_stories=[],
            use_cases=[],
            data_models=[],
            api_specifications=[],
            ui_components=[],
            integration_points=[]
        )

        # 각 청크 결과 병합
        for chunk_data in chunk_results:
            result = chunk_data['result']

            # 요구사항 병합
            merged.functional_requirements.extend(
                result.functional_requirements
            )
            merged.non_functional_requirements.extend(
                result.non_functional_requirements
            )

            # 데이터 모델 병합 (중복 확인)
            for model in result.data_models:
                if not any(m['name'] == model['name'] for m in merged.data_models):
                    merged.data_models.append(model)

            # API 병합 (중복 확인)
            for api in result.api_specifications:
                api_key = f"{api['method']}:{api['path']}"
                if not any(
                    f"{a['method']}:{a['path']}" == api_key
                    for a in merged.api_specifications
                ):
                    merged.api_specifications.append(api)

        return merged
```

**캐시 최적화**:

```python
class CacheOptimizer:
    """캐시 성능 최적화"""

    def __init__(self):
        self.cache_stats = {}
        self.hot_cache = {}  # 자주 액세스되는 항목
        self.cache_predictor = CachePredictor()

    async def optimize_cache_strategy(
        self,
        access_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """캐시 전략 최적화"""

        # 액세스 패턴 분석
        analysis = self._analyze_access_patterns(access_patterns)

        # 캐시 크기 최적화
        optimal_size = self._calculate_optimal_cache_size(analysis)

        # 제거 정책 최적화
        eviction_policy = self._optimize_eviction_policy(analysis)

        # 프리페칭 전략
        prefetch_strategy = await self.cache_predictor.generate_strategy(
            access_patterns
        )

        return {
            'optimal_cache_size': optimal_size,
            'eviction_policy': eviction_policy,
            'prefetch_strategy': prefetch_strategy,
            'estimated_hit_rate': analysis['predicted_hit_rate']
        }

    def _analyze_access_patterns(
        self,
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """액세스 패턴 분석"""

        # 빈도 분석
        frequency_map = {}
        for pattern in patterns:
            key = pattern['cache_key']
            frequency_map[key] = frequency_map.get(key, 0) + 1

        # 시간 패턴 분석
        time_patterns = self._analyze_temporal_patterns(patterns)

        # 크기 분포 분석
        size_distribution = self._analyze_size_distribution(patterns)

        return {
            'frequency_distribution': frequency_map,
            'temporal_patterns': time_patterns,
            'size_distribution': size_distribution,
            'predicted_hit_rate': self._predict_hit_rate(
                frequency_map,
                time_patterns
            )
        }
```

**성능 프로파일러**:

```python
class PerformanceProfiler:
    """성능 프로파일링 도구"""

    def __init__(self):
        self.profiles = {}
        self.metrics = {
            'parsing_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }

    async def profile_parsing_operation(
        self,
        parser_agent,
        text: str
    ) -> Dict[str, Any]:
        """파싱 작업 프로파일링"""

        import psutil
        import tracemalloc

        # 메모리 추적 시작
        tracemalloc.start()

        # CPU 사용률 측정 시작
        process = psutil.Process()
        cpu_before = process.cpu_percent()

        # 프로파일링 시작
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.time()

        # 파싱 실행
        result = await parser_agent.parse_requirements(text)

        end_time = time.time()

        # 프로파일링 종료
        profiler.disable()

        # 메모리 사용량
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # CPU 사용률
        cpu_after = process.cpu_percent()

        # 프로파일 분석
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')

        # 병목 지점 식별
        bottlenecks = self._identify_bottlenecks(stats)

        return {
            'execution_time': end_time - start_time,
            'memory_usage': {
                'current': current / 1024 / 1024,  # MB
                'peak': peak / 1024 / 1024  # MB
            },
            'cpu_usage': {
                'average': (cpu_before + cpu_after) / 2,
                'peak': max(cpu_before, cpu_after)
            },
            'bottlenecks': bottlenecks,
            'optimization_suggestions': self._generate_optimization_suggestions(
                bottlenecks,
                current,
                end_time - start_time
            )
        }

    def _identify_bottlenecks(
        self,
        stats: pstats.Stats
    ) -> List[Dict[str, Any]]:
        """성능 병목 지점 식별"""

        bottlenecks = []

        # 상위 10개 시간 소비 함수
        for func, (cc, nc, tt, ct, callers) in sorted(
            stats.stats.items(),
            key=lambda x: x[1][3],  # cumulative time
            reverse=True
        )[:10]:
            bottlenecks.append({
                'function': f"{func[0]}:{func[1]}:{func[2]}",
                'cumulative_time': ct,
                'total_time': tt,
                'call_count': nc,
                'time_per_call': ct / nc if nc > 0 else 0
            })

        return bottlenecks
```

**배치 처리 최적화**:

```python
class BatchProcessor:
    """배치 처리 최적화"""

    async def process_batch_requirements(
        self,
        parser_agent,
        requirement_texts: List[str],
        batch_size: int = 10
    ) -> List[ParsedProject]:
        """배치 요구사항 처리"""

        results = []

        # 배치 생성
        batches = [
            requirement_texts[i:i + batch_size]
            for i in range(0, len(requirement_texts), batch_size)
        ]

        # 배치별 병렬 처리
        for batch in batches:
            batch_tasks = [
                parser_agent.parse_requirements(text)
                for text in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)

        return results
```

**검증 기준**:

- [ ] 파싱 속도 50% 향상
- [ ] 메모리 사용량 30% 감소
- [ ] 병렬 처리 효율성
- [ ] 캐시 히트율 80% 이상

#### SubTask 4.26.4: Parser Agent 모니터링 및 로깅

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/monitoring.py
from typing import Dict, Any, List, Optional
import logging
import time
from dataclasses import dataclass
from datetime import datetime
import prometheus_client as prom

@dataclass
class ParsingMetrics:
    request_count: int
    success_count: int
    error_count: int
    average_parsing_time: float
    cache_hit_rate: float
    memory_usage_mb: float
    concurrent_sessions: int

class ParserMonitoring:
    """Parser Agent 모니터링 시스템"""

    def __init__(self):
        # Prometheus 메트릭 정의
        self.parsing_requests = prom.Counter(
            'parser_requests_total',
            'Total number of parsing requests',
            ['status', 'domain']
        )

        self.parsing_duration = prom.Histogram(
            'parser_duration_seconds',
            'Parsing duration in seconds',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

        self.cache_hits = prom.Counter(
            'parser_cache_hits_total',
            'Total number of cache hits'
        )

        self.cache_misses = prom.Counter(
            'parser_cache_misses_total',
            'Total number of cache misses'
        )

        self.memory_usage = prom.Gauge(
            'parser_memory_usage_bytes',
            'Current memory usage in bytes'
        )

        self.concurrent_sessions = prom.Gauge(
            'parser_concurrent_sessions',
            'Number of concurrent parsing sessions'
        )

        self.requirement_counts = prom.Counter(
            'parser_requirements_extracted',
            'Number of requirements extracted',
            ['type']
        )

        # 로깅 설정
        self.logger = self._setup_logging()

        # 메트릭 수집기
        self.metrics_collector = MetricsCollector()

        # 알림 시스템
        self.alert_manager = AlertManager()

    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""

        logger = logging.getLogger('parser_agent')
        logger.setLevel(logging.INFO)

        # 파일 핸들러
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/parser_agent.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )

        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        # 구조화된 로깅을 위한 JSON 핸들러
        json_handler = JsonLogHandler('logs/parser_agent.json')

        logger.addHandler(file_handler)
        logger.addHandler(json_handler)

        return logger

    async def monitor_parsing_request(
        self,
        request_id: str,
        domain: Optional[str] = None
    ):
        """파싱 요청 모니터링"""

        start_time = time.time()

        # 컨텍스트 매니저로 사용
        class ParsingMonitor:
            def __init__(self, monitoring, request_id, domain):
                self.monitoring = monitoring
                self.request_id = request_id
                self.domain = domain or 'unknown'
                self.start_time = start_time

            async def __aenter__(self):
                # 요청 시작 로깅
                self.monitoring.logger.info(
                    f"Parsing request started",
                    extra={
                        'request_id': self.request_id,
                        'domain': self.domain,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )

                # 동시 세션 증가
                self.monitoring.concurrent_sessions.inc()

                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time

                # 메트릭 업데이트
                if exc_type is None:
                    self.monitoring.parsing_requests.labels(
                        status='success',
                        domain=self.domain
                    ).inc()

                    self.monitoring.logger.info(
                        f"Parsing request completed",
                        extra={
                            'request_id': self.request_id,
                            'duration_seconds': duration,
                            'status': 'success'
                        }
                    )
                else:
                    self.monitoring.parsing_requests.labels(
                        status='error',
                        domain=self.domain
                    ).inc()

                    self.monitoring.logger.error(
                        f"Parsing request failed",
                        extra={
                            'request_id': self.request_id,
                            'duration_seconds': duration,
                            'error': str(exc_val),
                            'error_type': exc_type.__name__
                        }
                    )

                # 지속 시간 기록
                self.monitoring.parsing_duration.observe(duration)

                # 동시 세션 감소
                self.monitoring.concurrent_sessions.dec()

                # 알림 확인
                await self.monitoring.check_alerts(duration, exc_type)

        return ParsingMonitor(self, request_id, domain)

    async def record_parsing_results(
        self,
        parsed_project: ParsedProject,
        analysis_results: Dict[str, Any]
    ):
        """파싱 결과 기록"""

        # 요구사항 수 기록
        self.requirement_counts.labels(type='functional').inc(
            len(parsed_project.functional_requirements)
        )
        self.requirement_counts.labels(type='non_functional').inc(
            len(parsed_project.non_functional_requirements)
        )
        self.requirement_counts.labels(type='technical').inc(
            len(parsed_project.technical_requirements)
        )

        # 상세 메트릭 수집
        metrics = {
            'functional_requirements': len(parsed_project.functional_requirements),
            'non_functional_requirements': len(parsed_project.non_functional_requirements),
            'user_stories': len(parsed_project.user_stories),
            'data_models': len(parsed_project.data_models),
            'api_endpoints': len(parsed_project.api_specifications),
            'dependencies_found': len(
                analysis_results.get('dependency_analysis', {}).get('dependencies', [])
            ),
            'conflicts_found': len(
                analysis_results.get('conflict_analysis', {}).get('conflicts', [])
            )
        }

        await self.metrics_collector.collect(metrics)

        # 구조화된 로깅
        self.logger.info(
            "Parsing results recorded",
            extra={'metrics': metrics}
        )

    async def check_alerts(
        self,
        duration: float,
        error: Optional[Exception]
    ):
        """알림 조건 확인"""

        alerts = []

        # 느린 파싱 알림
        if duration > 10.0:  # 10초 이상
            alerts.append({
                'type': 'slow_parsing',
                'severity': 'warning',
                'message': f'Parsing took {duration:.2f} seconds',
                'threshold': 10.0
            })

        # 오류율 알림
        error_rate = await self.metrics_collector.get_error_rate()
        if error_rate > 0.05:  # 5% 이상
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'critical',
                'message': f'Error rate is {error_rate:.2%}',
                'threshold': 0.05
            })

        # 메모리 사용량 알림
        memory_mb = self.get_memory_usage_mb()
        if memory_mb > 1024:  # 1GB 이상
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f'Memory usage is {memory_mb:.2f} MB',
                'threshold': 1024
            })

        # 알림 전송
        for alert in alerts:
            await self.alert_manager.send_alert(alert)
```

**메트릭 수집기**:

```python
class MetricsCollector:
    """메트릭 수집 및 집계"""

    def __init__(self):
        self.metrics_buffer = []
        self.aggregation_interval = 60  # 1분
        self.last_aggregation = time.time()

    async def collect(self, metrics: Dict[str, Any]):
        """메트릭 수집"""

        timestamped_metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            **metrics
        }

        self.metrics_buffer.append(timestamped_metrics)

        # 주기적 집계
        if time.time() - self.last_aggregation > self.aggregation_interval:
            await self.aggregate_metrics()

    async def aggregate_metrics(self):
        """메트릭 집계"""

        if not self.metrics_buffer:
            return

        # 집계 계산
        aggregated = {
            'period_start': self.metrics_buffer[0]['timestamp'],
            'period_end': self.metrics_buffer[-1]['timestamp'],
            'sample_count': len(self.metrics_buffer),
            'averages': {},
            'totals': {},
            'percentiles': {}
        }

        # 숫자 필드 추출
        numeric_fields = [
            'functional_requirements',
            'non_functional_requirements',
            'user_stories',
            'data_models',
            'api_endpoints'
        ]

        for field in numeric_fields:
            values = [m.get(field, 0) for m in self.metrics_buffer]

            aggregated['averages'][field] = sum(values) / len(values)
            aggregated['totals'][field] = sum(values)
            aggregated['percentiles'][field] = {
                'p50': self._percentile(values, 50),
                'p90': self._percentile(values, 90),
                'p99': self._percentile(values, 99)
            }

        # 저장 또는 전송
        await self._store_aggregated_metrics(aggregated)

        # 버퍼 초기화
        self.metrics_buffer = []
        self.last_aggregation = time.time()
```

**로그 분석기**:

```python
class LogAnalyzer:
    """로그 분석 및 인사이트 추출"""

    async def analyze_logs(
        self,
        time_range: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """로그 분석"""

        logs = await self._load_logs(time_range)

        analysis = {
            'total_requests': 0,
            'success_rate': 0,
            'average_duration': 0,
            'error_patterns': {},
            'usage_patterns': {},
            'performance_trends': []
        }

        # 요청 분석
        requests = [log for log in logs if log['message'] == 'Parsing request completed']
        analysis['total_requests'] = len(requests)

        # 성공률 계산
        success_count = len([r for r in requests if r['status'] == 'success'])
        analysis['success_rate'] = success_count / len(requests) if requests else 0

        # 평균 지속 시간
        durations = [r['duration_seconds'] for r in requests if 'duration_seconds' in r]
        analysis['average_duration'] = sum(durations) / len(durations) if durations else 0

        # 오류 패턴 분석
        errors = [log for log in logs if log['level'] == 'ERROR']
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            analysis['error_patterns'][error_type] = \
                analysis['error_patterns'].get(error_type, 0) + 1

        # 사용 패턴 분석
        analysis['usage_patterns'] = await self._analyze_usage_patterns(logs)

        # 성능 추세 분석
        analysis['performance_trends'] = await self._analyze_performance_trends(
            requests,
            time_range
        )

        return analysis
```

**대시보드 데이터 제공**:

```python
class MonitoringDashboard:
    """모니터링 대시보드 데이터"""

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드용 데이터 조회"""

        return {
            'real_time_metrics': {
                'current_sessions': self.monitoring.concurrent_sessions._value.get(),
                'requests_per_minute': await self._calculate_rpm(),
                'average_response_time': await self._calculate_avg_response_time(),
                'cache_hit_rate': await self._calculate_cache_hit_rate()
            },
            'hourly_statistics': await self._get_hourly_stats(),
            'top_errors': await self._get_top_errors(),
            'performance_metrics': {
                'p50_duration': await self._get_percentile_duration(50),
                'p90_duration': await self._get_percentile_duration(90),
                'p99_duration': await self._get_percentile_duration(99)
            },
            'system_health': {
                'memory_usage_mb': self.monitoring.get_memory_usage_mb(),
                'cpu_usage_percent': await self._get_cpu_usage(),
                'error_rate': await self._calculate_error_rate()
            }
        }
```

**검증 기준**:

- [ ] 실시간 메트릭 수집
- [ ] 구조화된 로깅
- [ ] 알림 시스템 구현
- [ ] 성능 대시보드 데이터

이로써 Parser Agent의 모든 Task (4.21~4.26)가 완료되었습니다.

Parser Agent는 다음과 같은 핵심 기능을 갖추게 되었습니다:

1. **핵심 파싱 기능**: 자연어 요구사항을 구조화된 데이터로 변환
2. **고급 분석**: 의존성, 충돌, 추적성 분석
3. **도메인 특화**: 15개 도메인별 전문 파싱
4. **다국어 지원**: 15개 언어 요구사항 파싱
5. **성능 최적화**: 병렬 처리, 캐싱, 증분 파싱
6. **통합 인터페이스**: 다른 에이전트와의 표준화된 통신
7. **모니터링**: 실시간 메트릭 및 로깅

---

# Phase 4: 9개 핵심 에이전트 구현 - Parser Agent 완료 (Tasks 4.27-4.30)

## 4. Parser Agent (요구사항 파싱 에이전트) - 계속

### Task 4.27: Parser Agent 고급 분석 기능

#### SubTask 4.27.1: 요구사항 의존성 분석기

**담당자**: 시스템 분석가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/dependency_analyzer.py
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
import networkx as nx
from enum import Enum

@dataclass
class DependencyType(Enum):
    FUNCTIONAL = "functional"      # 기능적 의존성
    TEMPORAL = "temporal"          # 시간적 의존성
    DATA = "data"                  # 데이터 의존성
    TECHNICAL = "technical"        # 기술적 의존성
    RESOURCE = "resource"          # 리소스 의존성

@dataclass
class RequirementDependency:
    source_id: str
    target_id: str
    dependency_type: DependencyType
    strength: float  # 0-1 (의존성 강도)
    description: str
    is_blocking: bool
    estimated_impact: str  # 'low', 'medium', 'high'

class DependencyAnalyzer:
    """요구사항 간 의존성 분석"""

    def __init__(self):
        self.nlp_analyzer = DependencyNLPAnalyzer()
        self.graph_builder = DependencyGraphBuilder()
        self.cycle_detector = CycleDetector()
        self.impact_analyzer = ImpactAnalyzer()

    async def analyze_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> Dict[str, Any]:
        """요구사항 의존성 분석"""

        # 의존성 그래프 초기화
        dep_graph = nx.DiGraph()
        dependencies = []

        # 1. 명시적 의존성 추출
        explicit_deps = await self._extract_explicit_dependencies(requirements)
        dependencies.extend(explicit_deps)

        # 2. 암시적 의존성 추론
        implicit_deps = await self._infer_implicit_dependencies(requirements)
        dependencies.extend(implicit_deps)

        # 3. 의존성 그래프 구축
        for req in requirements:
            dep_graph.add_node(req.id, requirement=req)

        for dep in dependencies:
            dep_graph.add_edge(
                dep.source_id,
                dep.target_id,
                dependency=dep
            )

        # 4. 순환 의존성 검사
        cycles = list(nx.simple_cycles(dep_graph))

        # 5. 임계 경로 분석
        critical_paths = await self._analyze_critical_paths(dep_graph)

        # 6. 의존성 클러스터 식별
        clusters = await self._identify_dependency_clusters(dep_graph)

        # 7. 영향도 분석
        impact_analysis = await self.impact_analyzer.analyze(dep_graph)

        return {
            'dependencies': dependencies,
            'graph': dep_graph,
            'cycles': cycles,
            'critical_paths': critical_paths,
            'clusters': clusters,
            'impact_analysis': impact_analysis,
            'statistics': self._calculate_statistics(dep_graph)
        }

    async def _extract_explicit_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementDependency]:
        """명시적 의존성 추출"""

        explicit_patterns = [
            r'depends on\s+(?:requirement\s+)?(\w+)',
            r'requires\s+(?:completion of\s+)?(\w+)',
            r'after\s+(?:implementing\s+)?(\w+)',
            r'prerequisite[s]?:\s*(\w+(?:\s*,\s*\w+)*)',
            r'blocked by\s+(\w+)'
        ]

        dependencies = []

        for req in requirements:
            for pattern in explicit_patterns:
                matches = re.findall(pattern, req.description, re.IGNORECASE)
                for match in matches:
                    # 참조된 요구사항 ID 확인
                    target_ids = await self._resolve_requirement_references(
                        match,
                        requirements
                    )

                    for target_id in target_ids:
                        if target_id != req.id:  # 자기 참조 방지
                            dep = RequirementDependency(
                                source_id=req.id,
                                target_id=target_id,
                                dependency_type=DependencyType.FUNCTIONAL,
                                strength=0.9,
                                description=f"Explicit dependency: {req.id} depends on {target_id}",
                                is_blocking=True,
                                estimated_impact='high'
                            )
                            dependencies.append(dep)

        return dependencies

    async def _infer_implicit_dependencies(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementDependency]:
        """암시적 의존성 추론"""

        dependencies = []

        # 데이터 흐름 기반 의존성
        data_deps = await self._analyze_data_flow_dependencies(requirements)
        dependencies.extend(data_deps)

        # API/인터페이스 의존성
        api_deps = await self._analyze_api_dependencies(requirements)
        dependencies.extend(api_deps)

        # 리소스 공유 의존성
        resource_deps = await self._analyze_resource_dependencies(requirements)
        dependencies.extend(resource_deps)

        # 시간적 의존성
        temporal_deps = await self._analyze_temporal_dependencies(requirements)
        dependencies.extend(temporal_deps)

        return dependencies

    async def _analyze_critical_paths(
        self,
        graph: nx.DiGraph
    ) -> List[List[str]]:
        """임계 경로 분석"""

        # 시작 노드 (진입 차수 0)
        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]

        # 종료 노드 (진출 차수 0)
        end_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]

        critical_paths = []

        for start in start_nodes:
            for end in end_nodes:
                try:
                    # 모든 경로 찾기
                    all_paths = list(nx.all_simple_paths(graph, start, end))

                    # 가장 긴 경로가 임계 경로
                    if all_paths:
                        longest_path = max(all_paths, key=len)
                        critical_paths.append(longest_path)
                except nx.NetworkXNoPath:
                    continue

        return critical_paths
```

**의존성 시각화**:

```python
class DependencyVisualizer:
    """의존성 그래프 시각화"""

    async def visualize_dependencies(
        self,
        dep_graph: nx.DiGraph,
        output_format: str = 'svg'
    ) -> str:
        """의존성 그래프 시각화"""

        import graphviz

        dot = graphviz.Digraph(comment='Requirement Dependencies')
        dot.attr(rankdir='LR')

        # 노드 추가
        for node_id, data in dep_graph.nodes(data=True):
            req = data['requirement']
            label = f"{node_id}\n{req.category}\nPriority: {req.priority}"

            # 우선순위별 색상
            color = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'lightblue'
            }.get(req.priority, 'white')

            dot.node(node_id, label=label, style='filled', fillcolor=color)

        # 엣지 추가
        for source, target, data in dep_graph.edges(data=True):
            dep = data['dependency']

            # 의존성 타입별 스타일
            style = 'solid' if dep.is_blocking else 'dashed'
            color = {
                DependencyType.FUNCTIONAL: 'black',
                DependencyType.DATA: 'blue',
                DependencyType.TEMPORAL: 'green',
                DependencyType.TECHNICAL: 'red',
                DependencyType.RESOURCE: 'purple'
            }.get(dep.dependency_type, 'gray')

            dot.edge(source, target, style=style, color=color)

        return dot.pipe(format=output_format).decode('utf-8')
```

**검증 기준**:

- [ ] 명시적 의존성 정확도 95% 이상
- [ ] 암시적 의존성 추론 정확도
- [ ] 순환 의존성 감지
- [ ] 임계 경로 식별

#### SubTask 4.27.2: 요구사항 충돌 감지기

**담당자**: 품질 관리자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/conflict_detector.py
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

@dataclass
class ConflictType(Enum):
    RESOURCE = "resource"          # 리소스 충돌
    FUNCTIONAL = "functional"      # 기능 충돌
    TEMPORAL = "temporal"          # 시간 충돌
    LOGICAL = "logical"            # 논리적 모순
    TECHNICAL = "technical"        # 기술적 충돌

@dataclass
class RequirementConflict:
    requirement1_id: str
    requirement2_id: str
    conflict_type: ConflictType
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    resolution_suggestions: List[str]
    confidence: float  # 0-1

class ConflictDetector:
    """요구사항 충돌 감지"""

    def __init__(self):
        self.semantic_analyzer = SemanticConflictAnalyzer()
        self.resource_analyzer = ResourceConflictAnalyzer()
        self.temporal_analyzer = TemporalConflictAnalyzer()
        self.resolution_engine = ConflictResolutionEngine()

    async def detect_conflicts(
        self,
        requirements: List[ParsedRequirement],
        dependencies: List[RequirementDependency]
    ) -> List[RequirementConflict]:
        """요구사항 충돌 감지"""

        conflicts = []

        # 1. 리소스 충돌 검사
        resource_conflicts = await self._detect_resource_conflicts(requirements)
        conflicts.extend(resource_conflicts)

        # 2. 기능 충돌 검사
        functional_conflicts = await self._detect_functional_conflicts(requirements)
        conflicts.extend(functional_conflicts)

        # 3. 시간 충돌 검사
        temporal_conflicts = await self._detect_temporal_conflicts(
            requirements,
            dependencies
        )
        conflicts.extend(temporal_conflicts)

        # 4. 논리적 모순 검사
        logical_conflicts = await self._detect_logical_conflicts(requirements)
        conflicts.extend(logical_conflicts)

        # 5. 기술적 충돌 검사
        technical_conflicts = await self._detect_technical_conflicts(requirements)
        conflicts.extend(technical_conflicts)

        # 중복 제거 및 정렬
        conflicts = self._deduplicate_conflicts(conflicts)
        conflicts.sort(key=lambda c: self._severity_score(c.severity), reverse=True)

        return conflicts

    async def _detect_functional_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementConflict]:
        """기능 충돌 검사"""

        conflicts = []

        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                # 동일한 기능에 대한 상충되는 요구사항 검사
                if await self._are_functionally_conflicting(req1, req2):
                    conflict = RequirementConflict(
                        requirement1_id=req1.id,
                        requirement2_id=req2.id,
                        conflict_type=ConflictType.FUNCTIONAL,
                        severity=await self._assess_conflict_severity(req1, req2),
                        description=await self._generate_conflict_description(req1, req2),
                        resolution_suggestions=await self._suggest_resolutions(req1, req2),
                        confidence=await self._calculate_confidence(req1, req2)
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_logical_conflicts(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[RequirementConflict]:
        """논리적 모순 검사"""

        conflicts = []

        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                # 의미론적 모순 분석
                contradiction_score = await self.semantic_analyzer.analyze_contradiction(
                    req1.description,
                    req2.description
                )

                if contradiction_score > 0.7:  # 높은 모순 점수
                    conflict = RequirementConflict(
                        requirement1_id=req1.id,
                        requirement2_id=req2.id,
                        conflict_type=ConflictType.LOGICAL,
                        severity=self._calculate_severity(contradiction_score),
                        description="Semantic contradiction detected",
                        resolution_suggestions=[
                            "Review and clarify the requirements",
                            "Determine which requirement takes precedence",
                            "Find a middle ground that satisfies both intents"
                        ],
                        confidence=contradiction_score
                    )
                    conflicts.append(conflict)

        return conflicts
```

**검증 기준**:

- [ ] 다양한 충돌 유형 감지
- [ ] 충돌 심각도 평가
- [ ] 해결 방안 제시
- [ ] 의미적 모순 감지

#### SubTask 4.27.3: 요구사항 추적성 매트릭스 생성기

**담당자**: 품질 보증 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/traceability_matrix.py
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import pandas as pd
from enum import Enum

@dataclass
class TraceabilityLink:
    source_type: str  # 'business_req', 'functional_req', 'technical_req', 'test_case', 'code'
    source_id: str
    target_type: str
    target_id: str
    link_type: str  # 'implements', 'tests', 'derives_from', 'satisfies'
    confidence: float
    metadata: Dict[str, Any]

class TraceabilityMatrixGenerator:
    """요구사항 추적성 매트릭스 생성기"""

    def __init__(self):
        self.link_patterns = self._initialize_link_patterns()
        self.coverage_analyzer = CoverageAnalyzer()

    async def generate_traceability_matrix(
        self,
        parsed_project: ParsedProject,
        additional_artifacts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """추적성 매트릭스 생성"""

        # 1. 모든 추적 가능한 항목 수집
        traceable_items = await self._collect_traceable_items(
            parsed_project,
            additional_artifacts
        )

        # 2. 추적성 링크 생성
        traceability_links = await self._generate_traceability_links(
            traceable_items
        )

        # 3. 매트릭스 구성
        matrix = self._build_matrix(traceable_items, traceability_links)

        # 4. 커버리지 분석
        coverage_analysis = await self.coverage_analyzer.analyze(
            matrix,
            traceable_items
        )

        # 5. 갭 분석
        gaps = self._identify_gaps(matrix, traceable_items)

        # 6. 보고서 생성
        report = await self._generate_report(
            matrix,
            coverage_analysis,
            gaps
        )

        return {
            'matrix': matrix,
            'links': traceability_links,
            'coverage': coverage_analysis,
            'gaps': gaps,
            'report': report,
            'export_formats': await self._export_matrix(matrix)
        }

    async def _generate_traceability_links(
        self,
        items: Dict[str, List[Any]]
    ) -> List[TraceabilityLink]:
        """추적성 링크 생성"""

        links = []

        # 비즈니스 요구사항 → 기능 요구사항
        if 'business_requirements' in items and 'functional_requirements' in items:
            business_to_functional = await self._link_business_to_functional(
                items['business_requirements'],
                items['functional_requirements']
            )
            links.extend(business_to_functional)

        # 기능 요구사항 → 기술 요구사항
        if 'functional_requirements' in items and 'technical_requirements' in items:
            functional_to_technical = await self._link_functional_to_technical(
                items['functional_requirements'],
                items['technical_requirements']
            )
            links.extend(functional_to_technical)

        # 요구사항 → 테스트 케이스
        if 'test_cases' in items:
            requirement_to_test = await self._link_requirements_to_tests(
                items,
                items['test_cases']
            )
            links.extend(requirement_to_test)

        # 요구사항 → 코드 컴포넌트
        if 'code_components' in items:
            requirement_to_code = await self._link_requirements_to_code(
                items,
                items['code_components']
            )
            links.extend(requirement_to_code)

        return links

    def _build_matrix(
        self,
        items: Dict[str, List[Any]],
        links: List[TraceabilityLink]
    ) -> pd.DataFrame:
        """추적성 매트릭스 구축"""

        # 모든 항목 ID 수집
        all_ids = []
        id_to_type = {}

        for item_type, item_list in items.items():
            for item in item_list:
                item_id = item.get('id') or item.get('name')
                all_ids.append(item_id)
                id_to_type[item_id] = item_type

        # 빈 매트릭스 생성
        matrix = pd.DataFrame(
            index=all_ids,
            columns=all_ids,
            data=0
        )

        # 링크 정보로 매트릭스 채우기
        for link in links:
            if link.source_id in matrix.index and link.target_id in matrix.columns:
                matrix.loc[link.source_id, link.target_id] = 1
                # 링크 타입 정보 저장 (메타데이터로)
                matrix.loc[link.source_id, link.target_id] = {
                    'linked': True,
                    'type': link.link_type,
                    'confidence': link.confidence
                }

        return matrix

    async def _generate_report(
        self,
        matrix: pd.DataFrame,
        coverage: Dict[str, Any],
        gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """추적성 보고서 생성"""

        report = {
            'summary': {
                'total_requirements': len([i for i, t in coverage['by_type'].items() if 'req' in t]),
                'total_test_cases': coverage['by_type'].get('test_cases', 0),
                'total_code_components': coverage['by_type'].get('code_components', 0),
                'overall_coverage': coverage['overall_percentage']
            },
            'coverage_by_type': coverage['by_type'],
            'uncovered_requirements': [
                gap['item_id'] for gap in gaps
                if gap['type'] == 'uncovered_requirement'
            ],
            'orphan_tests': [
                gap['item_id'] for gap in gaps
                if gap['type'] == 'orphan_test'
            ],
            'recommendations': await self._generate_recommendations(coverage, gaps),
            'visualization': await self._create_visualization(matrix)
        }

        return report
```

**매트릭스 내보내기**:

```python
class MatrixExporter:
    """추적성 매트릭스 내보내기"""

    async def export_to_excel(
        self,
        matrix: pd.DataFrame,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Excel 형식으로 내보내기"""

        with pd.ExcelWriter('traceability_matrix.xlsx', engine='xlsxwriter') as writer:
            # 매트릭스 시트
            matrix.to_excel(writer, sheet_name='Traceability Matrix')

            # 요약 시트
            summary_df = pd.DataFrame([metadata['summary']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # 커버리지 시트
            coverage_df = pd.DataFrame(metadata['coverage']['by_type'].items(),
                                     columns=['Type', 'Coverage'])
            coverage_df.to_excel(writer, sheet_name='Coverage', index=False)

            # 서식 적용
            workbook = writer.book
            worksheet = writer.sheets['Traceability Matrix']

            # 조건부 서식 (링크된 셀 강조)
            worksheet.conditional_format('B2:ZZ1000', {
                'type': 'cell',
                'criteria': '=',
                'value': 1,
                'format': workbook.add_format({'bg_color': '#90EE90'})
            })

        return open('traceability_matrix.xlsx', 'rb').read()
```

**검증 기준**:

- [ ] 완전한 추적성 매트릭스
- [ ] 다양한 링크 타입 지원
- [ ] 커버리지 분석
- [ ] 갭 식별 및 보고

#### SubTask 4.27.4: 요구사항 완성도 검증기

**담당자**: QA 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/completeness_validator.py
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class CompletenessIssue:
    requirement_id: str
    issue_type: str  # 'missing', 'incomplete', 'ambiguous', 'unmeasurable'
    severity: str  # 'low', 'medium', 'high'
    description: str
    suggestions: List[str]
    affected_aspects: List[str]

class CompletenessValidator:
    """요구사항 완성도 검증"""

    def __init__(self):
        self.completeness_rules = self._initialize_rules()
        self.quality_metrics = QualityMetrics()

    async def validate_completeness(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """요구사항 완성도 검증"""

        validation_results = {
            'overall_completeness': 0.0,
            'issues': [],
            'metrics': {},
            'recommendations': [],
            'missing_aspects': []
        }

        # 1. 필수 요소 검사
        required_elements = await self._check_required_elements(parsed_project)
        validation_results['issues'].extend(required_elements['issues'])

        # 2. 요구사항별 완성도 검사
        for req in parsed_project.requirements:
            req_issues = await self._validate_requirement_completeness(req)
            validation_results['issues'].extend(req_issues)

        # 3. 측정 가능성 검사
        measurability_issues = await self._check_measurability(
            parsed_project.requirements
        )
        validation_results['issues'].extend(measurability_issues)

        # 4. 일관성 검사
        consistency_issues = await self._check_consistency(parsed_project)
        validation_results['issues'].extend(consistency_issues)

        # 5. 커버리지 검사
        coverage_analysis = await self._analyze_coverage(parsed_project)
        validation_results['missing_aspects'] = coverage_analysis['missing']

        # 6. 품질 메트릭 계산
        metrics = await self.quality_metrics.calculate(
            parsed_project,
            validation_results['issues']
        )
        validation_results['metrics'] = metrics

        # 7. 전체 완성도 점수
        validation_results['overall_completeness'] = await self._calculate_overall_score(
            validation_results
        )

        # 8. 개선 권장사항
        validation_results['recommendations'] = await self._generate_recommendations(
            validation_results
        )

        return validation_results

    async def _validate_requirement_completeness(
        self,
        requirement: ParsedRequirement
    ) -> List[CompletenessIssue]:
        """개별 요구사항 완성도 검증"""

        issues = []

        # SMART 기준 검사
        smart_checks = {
            'specific': self._is_specific,
            'measurable': self._is_measurable,
            'achievable': self._is_achievable,
            'relevant': self._is_relevant,
            'time_bound': self._is_time_bound
        }

        for criterion, check_func in smart_checks.items():
            if not await check_func(requirement):
                issue = CompletenessIssue(
                    requirement_id=requirement.id,
                    issue_type='incomplete',
                    severity='medium',
                    description=f"Requirement does not meet {criterion.upper()} criterion",
                    suggestions=await self._get_suggestions_for_criterion(
                        criterion,
                        requirement
                    ),
                    affected_aspects=[criterion]
                )
                issues.append(issue)

        # 모호성 검사
        ambiguity_score = await self._calculate_ambiguity_score(requirement)
        if ambiguity_score > 0.3:
            issue = CompletenessIssue(
                requirement_id=requirement.id,
                issue_type='ambiguous',
                severity='high' if ambiguity_score > 0.6 else 'medium',
                description="Requirement contains ambiguous language",
                suggestions=[
                    "Use more specific terminology",
                    "Define clear acceptance criteria",
                    "Avoid words like 'maybe', 'possibly', 'should'"
                ],
                affected_aspects=['clarity']
            )
            issues.append(issue)

        return issues

    async def _check_required_elements(
        self,
        project: ParsedProject
    ) -> Dict[str, Any]:
        """필수 요소 검사"""

        required_elements = {
            'functional_requirements': 'At least one functional requirement',
            'non_functional_requirements': 'Performance and security requirements',
            'user_stories': 'User stories or use cases',
            'acceptance_criteria': 'Clear acceptance criteria',
            'constraints': 'Technical and business constraints',
            'assumptions': 'Project assumptions'
        }

        issues = []
        missing = []

        for element, description in required_elements.items():
            if not hasattr(project, element) or not getattr(project, element):
                issues.append(CompletenessIssue(
                    requirement_id='PROJECT',
                    issue_type='missing',
                    severity='high',
                    description=f"Missing {element.replace('_', ' ')}",
                    suggestions=[f"Add {description}"],
                    affected_aspects=[element]
                ))
                missing.append(element)

        return {'issues': issues, 'missing': missing}
```

**품질 메트릭 계산**:

```python
class QualityMetrics:
    """요구사항 품질 메트릭"""

    async def calculate(
        self,
        project: ParsedProject,
        issues: List[CompletenessIssue]
    ) -> Dict[str, Any]:
        """품질 메트릭 계산"""

        total_requirements = len(project.requirements)

        metrics = {
            'total_requirements': total_requirements,
            'complete_requirements': 0,
            'incomplete_requirements': 0,
            'ambiguous_requirements': 0,
            'unmeasurable_requirements': 0,
            'clarity_score': 0.0,
            'completeness_score': 0.0,
            'consistency_score': 0.0,
            'quality_index': 0.0
        }

        # 이슈별 카운트
        issue_counts = {}
        for issue in issues:
            issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1

        # 완성도 메트릭
        metrics['incomplete_requirements'] = issue_counts.get('incomplete', 0)
        metrics['complete_requirements'] = total_requirements - metrics['incomplete_requirements']
        metrics['ambiguous_requirements'] = issue_counts.get('ambiguous', 0)
        metrics['unmeasurable_requirements'] = issue_counts.get('unmeasurable', 0)

        # 점수 계산
        if total_requirements > 0:
            metrics['completeness_score'] = metrics['complete_requirements'] / total_requirements
            metrics['clarity_score'] = 1 - (metrics['ambiguous_requirements'] / total_requirements)
            metrics['consistency_score'] = await self._calculate_consistency_score(project)

            # 종합 품질 지수
            metrics['quality_index'] = (
                metrics['completeness_score'] * 0.4 +
                metrics['clarity_score'] * 0.3 +
                metrics['consistency_score'] * 0.3
            )

        return metrics
```

**검증 기준**:

- [ ] SMART 기준 검증
- [ ] 모호성 감지
- [ ] 측정 가능성 평가
- [ ] 품질 메트릭 정확도

---

### Task 4.28: Parser Agent 도메인 특화 기능

#### SubTask 4.28.1: 도메인별 파싱 규칙 엔진

**담당자**: 도메인 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/domain_parser.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

@dataclass
class DomainType(Enum):
    E_COMMERCE = "e_commerce"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    SOCIAL_MEDIA = "social_media"
    IOT = "iot"
    GAMING = "gaming"
    ENTERPRISE = "enterprise"
    MOBILE = "mobile"
    AI_ML = "ai_ml"

@dataclass
class DomainRule:
    domain: DomainType
    patterns: List[str]
    extractors: Dict[str, Any]
    validators: List[Any]
    terminology: Dict[str, str]

class DomainSpecificParser:
    """도메인 특화 파싱 엔진"""

    def __init__(self):
        self.domain_rules = self._initialize_domain_rules()
        self.domain_classifier = DomainClassifier()
        self.terminology_mapper = TerminologyMapper()

    async def parse_with_domain_context(
        self,
        requirements: List[str],
        detected_domain: Optional[DomainType] = None
    ) -> ParsedProject:
        """도메인 컨텍스트를 고려한 파싱"""

        # 1. 도메인 자동 감지
        if not detected_domain:
            detected_domain = await self.domain_classifier.classify(requirements)

        # 2. 도메인 규칙 로드
        domain_rules = self.domain_rules.get(detected_domain)
        if not domain_rules:
            domain_rules = self.domain_rules[DomainType.ENTERPRISE]  # 기본값

        # 3. 도메인 특화 파싱
        parsed_requirements = []
        for req in requirements:
            parsed_req = await self._parse_domain_requirement(
                req,
                domain_rules
            )
            parsed_requirements.append(parsed_req)

        # 4. 도메인 특화 검증
        validation_results = await self._validate_domain_requirements(
            parsed_requirements,
            domain_rules
        )

        # 5. 도메인 메타데이터 추가
        project = ParsedProject(
            domain=detected_domain,
            requirements=parsed_requirements,
            domain_metadata=await self._extract_domain_metadata(
                parsed_requirements,
                domain_rules
            ),
            validation_results=validation_results
        )

        return project

    def _initialize_domain_rules(self) -> Dict[DomainType, DomainRule]:
        """도메인별 규칙 초기화"""

        rules = {}

        # E-Commerce 규칙
        rules[DomainType.E_COMMERCE] = DomainRule(
            domain=DomainType.E_COMMERCE,
            patterns=[
                r'(product|item|catalog|inventory)',
                r'(cart|checkout|payment|order)',
                r'(customer|user|account|profile)',
                r'(shipping|delivery|tracking)',
                r'(discount|coupon|promotion)',
                r'(review|rating|feedback)'
            ],
            extractors={
                'payment_methods': self._extract_payment_methods,
                'shipping_options': self._extract_shipping_options,
                'product_categories': self._extract_product_categories
            },
            validators=[
                self._validate_payment_security,
                self._validate_inventory_management,
                self._validate_order_workflow
            ],
            terminology={
                'SKU': 'Stock Keeping Unit',
                'PCI': 'Payment Card Industry',
                'SSL': 'Secure Sockets Layer',
                'API': 'Application Programming Interface'
            }
        )

        # Healthcare 규칙
        rules[DomainType.HEALTHCARE] = DomainRule(
            domain=DomainType.HEALTHCARE,
            patterns=[
                r'(patient|doctor|physician|nurse)',
                r'(appointment|consultation|diagnosis)',
                r'(medical|health|clinical|treatment)',
                r'(prescription|medication|drug)',
                r'(HIPAA|compliance|privacy)',
                r'(EHR|EMR|records)'
            ],
            extractors={
                'compliance_requirements': self._extract_healthcare_compliance,
                'data_types': self._extract_medical_data_types,
                'workflows': self._extract_clinical_workflows
            },
            validators=[
                self._validate_hipaa_compliance,
                self._validate_medical_data_security,
                self._validate_clinical_accuracy
            ],
            terminology={
                'HIPAA': 'Health Insurance Portability and Accountability Act',
                'EHR': 'Electronic Health Record',
                'EMR': 'Electronic Medical Record',
                'PHI': 'Protected Health Information'
            }
        )

        # Finance 규칙
        rules[DomainType.FINANCE] = DomainRule(
            domain=DomainType.FINANCE,
            patterns=[
                r'(transaction|payment|transfer|deposit)',
                r'(account|balance|statement|ledger)',
                r'(investment|portfolio|trading|stock)',
                r'(loan|credit|mortgage|interest)',
                r'(compliance|regulation|audit)',
                r'(security|encryption|authentication)'
            ],
            extractors={
                'financial_instruments': self._extract_financial_instruments,
                'regulatory_requirements': self._extract_financial_regulations,
                'transaction_types': self._extract_transaction_types
            },
            validators=[
                self._validate_financial_compliance,
                self._validate_transaction_integrity,
                self._validate_security_standards
            ],
            terminology={
                'KYC': 'Know Your Customer',
                'AML': 'Anti-Money Laundering',
                'PSD2': 'Payment Services Directive 2',
                'GDPR': 'General Data Protection Regulation'
            }
        )

        return rules

    async def _parse_domain_requirement(
        self,
        requirement: str,
        domain_rules: DomainRule
    ) -> ParsedRequirement:
        """도메인 특화 요구사항 파싱"""

        parsed = ParsedRequirement()

        # 도메인 패턴 매칭
        for pattern in domain_rules.patterns:
            matches = re.findall(pattern, requirement, re.IGNORECASE)
            if matches:
                parsed.domain_entities.extend(matches)

        # 도메인 특화 추출
        for extractor_name, extractor_func in domain_rules.extractors.items():
            extracted_data = await extractor_func(requirement)
            if extracted_data:
                parsed.domain_specific_data[extractor_name] = extracted_data

        # 용어 매핑
        for term, definition in domain_rules.terminology.items():
            if term in requirement.upper():
                parsed.detected_terminology[term] = definition

        return parsed
```

**도메인별 검증기**:

```python
class DomainValidator:
    """도메인 특화 검증"""

    async def validate_e_commerce(
        self,
        requirements: List[ParsedRequirement]
    ) -> List[ValidationIssue]:
        """E-Commerce 도메인 검증"""

        issues = []

        # 필수 요구사항 검사
        required_features = [
            'payment_processing',
            'inventory_management',
            'order_fulfillment',
            'user_authentication',
            'product_catalog'
        ]

        found_features = set()
        for req in requirements:
            for feature in required_features:
                if feature in req.description.lower():
                    found_features.add(feature)

        missing_features = set(required_features) - found_features
        for feature in missing_features:
            issues.append(ValidationIssue(
                type='missing_requirement',
                severity='high',
                description=f"Missing essential e-commerce feature: {feature}",
                suggestion=f"Add requirements for {feature.replace('_', ' ')}"
            ))

        # PCI 컴플라이언스 검사
        if 'payment' in str(requirements).lower():
            pci_mentioned = any('pci' in req.description.lower() for req in requirements)
            if not pci_mentioned:
                issues.append(ValidationIssue(
                    type='compliance',
                    severity='critical',
                    description="Payment processing requires PCI compliance",
                    suggestion="Add PCI DSS compliance requirements"
                ))

        return issues
```

**검증 기준**:

- [ ] 15개 이상 도메인 지원
- [ ] 도메인 자동 감지 정확도
- [ ] 도메인 특화 규칙 적용
- [ ] 규정 준수 검증

#### SubTask 4.28.2: 다국어 요구사항 파싱

**담당자**: 국제화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/multilingual_parser.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from langdetect import detect
from googletrans import Translator

@dataclass
class MultilingualRequirement:
    original_text: str
    original_language: str
    english_translation: str
    confidence: float
    cultural_notes: List[str]
    localization_requirements: Dict[str, Any]

class MultilingualParser:
    """다국어 요구사항 파싱"""

    def __init__(self):
        self.translator = Translator()
        self.language_detector = LanguageDetector()
        self.cultural_analyzer = CulturalAnalyzer()
        self.supported_languages = [
            'en', 'ko', 'ja', 'zh-cn', 'zh-tw',
            'es', 'fr', 'de', 'it', 'pt',
            'ru', 'ar', 'hi', 'th', 'vi'
        ]

    async def parse_multilingual_requirements(
        self,
        requirements: List[str]
    ) -> Dict[str, Any]:
        """다국어 요구사항 파싱"""

        results = {
            'detected_languages': {},
            'translations': [],
            'cultural_considerations': [],
            'localization_needs': {},
            'parsing_results': []
        }

        # 1. 언어 감지 및 그룹화
        language_groups = await self._group_by_language(requirements)
        results['detected_languages'] = {
            lang: len(reqs) for lang, reqs in language_groups.items()
        }

        # 2. 각 언어별 처리
        for language, reqs in language_groups.items():
            if language != 'en':
                # 영어로 번역
                translated_reqs = await self._translate_requirements(
                    reqs,
                    source_lang=language,
                    target_lang='en'
                )
                results['translations'].extend(translated_reqs)

                # 문화적 고려사항 분석
                cultural_notes = await self.cultural_analyzer.analyze(
                    reqs,
                    language
                )
                results['cultural_considerations'].extend(cultural_notes)
            else:
                # 영어 요구사항은 그대로 사용
                results['translations'].extend([
                    MultilingualRequirement(
                        original_text=req,
                        original_language='en',
                        english_translation=req,
                        confidence=1.0,
                        cultural_notes=[],
                        localization_requirements={}
                    )
                    for req in reqs
                ])

        # 3. 통합 파싱
        all_english_reqs = [t.english_translation for t in results['translations']]
        parsed_project = await self._parse_translated_requirements(all_english_reqs)
        results['parsing_results'] = parsed_project

        # 4. 지역화 요구사항 추출
        results['localization_needs'] = await self._extract_localization_needs(
            results['translations'],
            results['cultural_considerations']
        )

        return results

    async def _group_by_language(
        self,
        requirements: List[str]
    ) -> Dict[str, List[str]]:
        """언어별 그룹화"""

        language_groups = {}

        for req in requirements:
            try:
                # 언어 감지
                detected_lang = detect(req)

                # 지원 언어 확인
                if detected_lang not in self.supported_languages:
                    detected_lang = 'unknown'

                if detected_lang not in language_groups:
                    language_groups[detected_lang] = []

                language_groups[detected_lang].append(req)

            except Exception as e:
                # 감지 실패 시 unknown으로 분류
                if 'unknown' not in language_groups:
                    language_groups['unknown'] = []
                language_groups['unknown'].append(req)

        return language_groups

    async def _translate_requirements(
        self,
        requirements: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[MultilingualRequirement]:
        """요구사항 번역"""

        translated = []

        for req in requirements:
            try:
                # Google Translate API 사용
                translation = self.translator.translate(
                    req,
                    src=source_lang,
                    dest=target_lang
                )

                # 번역 품질 평가
                confidence = await self._evaluate_translation_quality(
                    req,
                    translation.text,
                    source_lang,
                    target_lang
                )

                # 문화적 메모 추가
                cultural_notes = await self._extract_cultural_notes(
                    req,
                    source_lang
                )

                translated.append(MultilingualRequirement(
                    original_text=req,
                    original_language=source_lang,
                    english_translation=translation.text,
                    confidence=confidence,
                    cultural_notes=cultural_notes,
                    localization_requirements={}
                ))

            except Exception as e:
                # 번역 실패 시 원문 사용
                translated.append(MultilingualRequirement(
                    original_text=req,
                    original_language=source_lang,
                    english_translation=f"[TRANSLATION FAILED] {req}",
                    confidence=0.0,
                    cultural_notes=[],
                    localization_requirements={}
                ))

        return translated
```

**문화적 분석기**:

```python
class CulturalAnalyzer:
    """문화적 고려사항 분석"""

    def __init__(self):
        self.cultural_patterns = self._load_cultural_patterns()

    async def analyze(
        self,
        requirements: List[str],
        language: str
    ) -> List[Dict[str, Any]]:
        """문화적 고려사항 분석"""

        cultural_notes = []

        # 언어별 문화 패턴
        patterns = self.cultural_patterns.get(language, {})

        for req in requirements:
            # 날짜/시간 형식
            if patterns.get('date_format'):
                if any(indicator in req for indicator in ['date', 'time', '날짜', '時間']):
                    cultural_notes.append({
                        'type': 'date_format',
                        'language': language,
                        'note': f"Use {patterns['date_format']} format for {language}",
                        'example': patterns.get('date_example')
                    })

            # 통화 형식
            if patterns.get('currency'):
                if any(indicator in req for indicator in ['price', 'cost', '가격', '価格']):
                    cultural_notes.append({
                        'type': 'currency',
                        'language': language,
                        'note': f"Default currency: {patterns['currency']}",
                        'format': patterns.get('currency_format')
                    })

            # 이름 순서
            if patterns.get('name_order'):
                if any(indicator in req for indicator in ['name', 'user', '이름', '名前']):
                    cultural_notes.append({
                        'type': 'name_order',
                        'language': language,
                        'note': f"Name order: {patterns['name_order']}",
                        'example': patterns.get('name_example')
                    })

        return cultural_notes
```

**검증 기준**:

- [ ] 15개 언어 지원
- [ ] 번역 정확도 90% 이상
- [ ] 문화적 고려사항 식별
- [ ] 지역화 요구사항 추출

#### SubTask 4.28.3: 요구사항 버전 관리 시스템

**담당자**: 구성 관리자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/version_control.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import difflib

@dataclass
class RequirementVersion:
    version_id: str
    requirement_id: str
    version_number: str  # "1.0.0"
    content: str
    author: str
    timestamp: datetime
    change_type: str  # 'create', 'update', 'delete'
    change_description: str
    parent_version: Optional[str]
    tags: List[str]

@dataclass
class RequirementDiff:
    requirement_id: str
    from_version: str
    to_version: str
    changes: List[Dict[str, Any]]
    impact_analysis: Dict[str, Any]

class RequirementVersionControl:
    """요구사항 버전 관리"""

    def __init__(self):
        self.version_store = VersionStore()
        self.diff_engine = DiffEngine()
        self.impact_analyzer = ImpactAnalyzer()

    async def track_requirement_change(
        self,
        requirement: ParsedRequirement,
        author: str,
        change_description: str
    ) -> RequirementVersion:
        """요구사항 변경 추적"""

        # 현재 버전 확인
        current_version = await self.version_store.get_latest_version(
            requirement.id
        )

        # 새 버전 번호 생성
        new_version_number = self._increment_version(
            current_version.version_number if current_version else "0.0.0"
        )

        # 변경 유형 결정
        change_type = 'create' if not current_version else 'update'

        # 버전 객체 생성
        new_version = RequirementVersion(
            version_id=self._generate_version_id(requirement.id, new_version_number),
            requirement_id=requirement.id,
            version_number=new_version_number,
            content=requirement.description,
            author=author,
            timestamp=datetime.utcnow(),
            change_type=change_type,
            change_description=change_description,
            parent_version=current_version.version_id if current_version else None,
            tags=[]
        )

        # 버전 저장
        await self.version_store.save_version(new_version)

        # 변경 영향 분석
        if current_version:
            impact = await self.impact_analyzer.analyze_change_impact(
                current_version,
                new_version
            )
            await self._notify_impacted_stakeholders(impact)

        return new_version

    async def get_requirement_history(
        self,
        requirement_id: str
    ) -> List[RequirementVersion]:
        """요구사항 변경 이력 조회"""

        versions = await self.version_store.get_all_versions(requirement_id)

        # 시간순 정렬
        versions.sort(key=lambda v: v.timestamp)

        return versions

    async def compare_versions(
        self,
        requirement_id: str,
        from_version: str,
        to_version: str
    ) -> RequirementDiff:
        """버전 간 비교"""

        # 버전 로드
        from_ver = await self.version_store.get_version(from_version)
        to_ver = await self.version_store.get_version(to_version)

        # 차이점 계산
        changes = await self.diff_engine.calculate_diff(
            from_ver.content,
            to_ver.content
        )

        # 영향 분석
        impact_analysis = await self.impact_analyzer.analyze_diff_impact(
            from_ver,
            to_ver,
            changes
        )

        return RequirementDiff(
            requirement_id=requirement_id,
            from_version=from_version,
            to_version=to_version,
            changes=changes,
            impact_analysis=impact_analysis
        )

    async def create_baseline(
        self,
        project_id: str,
        baseline_name: str,
        description: str
    ) -> Dict[str, Any]:
        """요구사항 베이스라인 생성"""

        # 현재 모든 요구사항의 최신 버전 수집
        requirements = await self._get_all_current_requirements(project_id)

        baseline = {
            'baseline_id': self._generate_baseline_id(),
            'name': baseline_name,
            'description': description,
            'created_at': datetime.utcnow(),
            'requirements': {}
        }

        for req_id, req_version in requirements.items():
            baseline['requirements'][req_id] = {
                'version_id': req_version.version_id,
                'version_number': req_version.version_number,
                'content_hash': hashlib.sha256(
                    req_version.content.encode()
                ).hexdigest()
            }

        # 베이스라인 저장
        await self.version_store.save_baseline(baseline)

        return baseline

    def _increment_version(self, current_version: str) -> str:
        """버전 번호 증가"""

        major, minor, patch = map(int, current_version.split('.'))

        # 간단한 규칙: 패치 버전 증가
        # 실제로는 변경 유형에 따라 major/minor/patch 결정
        patch += 1

        return f"{major}.{minor}.{patch}"
```

**변경 영향 분석기**:

```python
class ImpactAnalyzer:
    """변경 영향 분석"""

    async def analyze_change_impact(
        self,
        old_version: RequirementVersion,
        new_version: RequirementVersion
    ) -> Dict[str, Any]:
        """변경 영향 분석"""

        impact = {
            'severity': 'low',  # 기본값
            'affected_components': [],
            'affected_requirements': [],
            'risk_assessment': {},
            'recommended_actions': []
        }

        # 변경 크기 계산
        change_size = await self._calculate_change_size(
            old_version.content,
            new_version.content
        )

        # 영향도 평가
        if change_size > 0.5:  # 50% 이상 변경
            impact['severity'] = 'high'
            impact['recommended_actions'].append(
                "Major change detected - full regression testing recommended"
            )
        elif change_size > 0.2:  # 20% 이상 변경
            impact['severity'] = 'medium'
            impact['recommended_actions'].append(
                "Significant change - targeted testing recommended"
            )

        # 연관 요구사항 식별
        related_reqs = await self._find_related_requirements(
            new_version.requirement_id
        )
        impact['affected_requirements'] = related_reqs

        # 리스크 평가
        impact['risk_assessment'] = {
            'technical_risk': await self._assess_technical_risk(new_version),
            'schedule_risk': await self._assess_schedule_risk(change_size),
            'cost_risk': await self._assess_cost_risk(change_size)
        }

        return impact
```

**검증 기준**:

- [ ] 완전한 버전 이력 관리
- [ ] 효과적인 차이점 비교
- [ ] 영향 분석 정확도
- [ ] 베이스라인 관리 기능

#### SubTask 4.28.4: Parser Agent 성능 최적화

**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/performance_optimizer.py
from typing import Dict, List, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from functools import lru_cache
import redis

class ParserPerformanceOptimizer:
    """Parser Agent 성능 최적화"""

    def __init__(self):
        self.cache = redis.Redis(decode_responses=True)
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.process_pool = ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        )
        self.batch_processor = BatchProcessor()

    async def optimize_parsing_pipeline(
        self,
        requirements: List[str],
        optimization_level: str = 'balanced'
    ) -> ParsedProject:
        """최적화된 파싱 파이프라인"""

        optimization_strategies = {
            'speed': self._speed_optimized_pipeline,
            'accuracy': self._accuracy_optimized_pipeline,
            'balanced': self._balanced_pipeline
        }

        pipeline_func = optimization_strategies.get(
            optimization_level,
            self._balanced_pipeline
        )

        return await pipeline_func(requirements)

    async def _speed_optimized_pipeline(
        self,
        requirements: List[str]
    ) -> ParsedProject:
        """속도 최적화 파이프라인"""

        # 1. 캐시 확인
        cached_results = await self._check_cache_batch(requirements)
        uncached_reqs = [
            req for i, req in enumerate(requirements)
            if cached_results[i] is None
        ]

        if not uncached_reqs:
            return self._merge_cached_results(cached_results)

        # 2. 병렬 처리
        batch_size = 50
        batches = [
            uncached_reqs[i:i + batch_size]
            for i in range(0, len(uncached_reqs), batch_size)
        ]

        # 3. 비동기 배치 처리
        tasks = []
        for batch in batches:
            task = asyncio.create_task(
                self._process_batch_async(batch)
            )
            tasks.append(task)

        batch_results = await asyncio.gather(*tasks)

        # 4. 결과 병합 및 캐싱
        all_results = self._merge_results(cached_results, batch_results)
        await self._cache_results(requirements, all_results)

        return all_results

    async def _process_batch_async(
        self,
        batch: List[str]
    ) -> List[ParsedRequirement]:
        """비동기 배치 처리"""

        # CPU 집약적 작업은 프로세스 풀에서
        loop = asyncio.get_event_loop()

        # NLP 처리 (CPU 집약적)
        nlp_results = await loop.run_in_executor(
            self.process_pool,
            self._batch_nlp_processing,
            batch
        )

        # 패턴 매칭 (I/O 집약적)
        pattern_results = await self._batch_pattern_matching(batch)

        # 결과 조합
        parsed_requirements = []
        for i, req in enumerate(batch):
            parsed = self._combine_results(
                req,
                nlp_results[i],
                pattern_results[i]
            )
            parsed_requirements.append(parsed)

        return parsed_requirements

    @lru_cache(maxsize=1000)
    def _cached_nlp_processing(self, requirement: str) -> Dict[str, Any]:
        """캐시된 NLP 처리"""
        # NLP 모델 실행 (비용이 높은 작업)
        return self.nlp_processor.process(requirement)

    async def _check_cache_batch(
        self,
        requirements: List[str]
    ) -> List[Optional[ParsedRequirement]]:
        """배치 캐시 확인"""

        # 캐시 키 생성
        cache_keys = [
            f"parsed_req:{hashlib.md5(req.encode()).hexdigest()}"
            for req in requirements
        ]

        # Redis 파이프라인으로 배치 조회
        pipe = self.cache.pipeline()
        for key in cache_keys:
            pipe.get(key)

        cached_values = pipe.execute()

        # 역직렬화
        results = []
        for value in cached_values:
            if value:
                results.append(self._deserialize_requirement(value))
            else:
                results.append(None)

        return results

    async def _implement_incremental_parsing(
        self,
        new_requirements: List[str],
        existing_project: Optional[ParsedProject]
    ) -> ParsedProject:
        """증분 파싱 구현"""

        if not existing_project:
            # 전체 파싱
            return await self.optimize_parsing_pipeline(new_requirements)

        # 변경된 요구사항만 파싱
        changed_reqs = []
        unchanged_reqs = []

        for req in new_requirements:
            req_hash = hashlib.md5(req.encode()).hexdigest()
            if req_hash not in existing_project.requirement_hashes:
                changed_reqs.append(req)
            else:
                unchanged_reqs.append(req)

        # 변경된 것만 파싱
        if changed_reqs:
            parsed_changes = await self.optimize_parsing_pipeline(changed_reqs)

            # 기존 프로젝트와 병합
            return self._merge_projects(existing_project, parsed_changes)

        return existing_project
```

**배치 처리 최적화**:

```python
class BatchProcessor:
    """배치 처리 최적화"""

    def __init__(self):
        self.optimal_batch_size = self._calculate_optimal_batch_size()

    async def process_in_batches(
        self,
        items: List[Any],
        process_func: callable,
        max_concurrent: int = 10
    ) -> List[Any]:
        """최적화된 배치 처리"""

        # 동적 배치 크기 조정
        batch_size = min(
            self.optimal_batch_size,
            max(1, len(items) // max_concurrent)
        )

        # 세마포어로 동시성 제어
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_batch(batch):
            async with semaphore:
                return await process_func(batch)

        # 배치 생성 및 처리
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]

        tasks = [
            asyncio.create_task(process_batch(batch))
            for batch in batches
        ]

        results = await asyncio.gather(*tasks)

        # 결과 평탄화
        return [item for batch_result in results for item in batch_result]

    def _calculate_optimal_batch_size(self) -> int:
        """최적 배치 크기 계산"""

        # CPU 코어 수와 메모리 고려
        cpu_count = multiprocessing.cpu_count()

        # 경험적 공식
        optimal_size = cpu_count * 10

        return min(optimal_size, 100)  # 최대 100
```

**검증 기준**:

- [ ] 파싱 속도 50% 향상
- [ ] 메모리 사용량 최적화
- [ ] 병렬 처리 효율성
- [ ] 캐시 적중률 80% 이상

---

### Task 4.29: Parser Agent 통합 및 테스트

#### SubTask 4.29.1: 다른 에이전트와의 통합 인터페이스

**담당자**: 시스템 통합 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/integration_interface.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from abc import ABC, abstractmethod

@dataclass
class AgentMessage:
    source_agent: str
    target_agent: str
    message_type: str
    payload: Dict[str, Any]
    correlation_id: str
    timestamp: datetime

class ParserAgentInterface:
    """Parser Agent 통합 인터페이스"""

    def __init__(self):
        self.message_handlers = {}
        self.output_formatters = {}
        self.agent_connectors = {}

    async def register_agent_connector(
        self,
        agent_name: str,
        connector: 'AgentConnector'
    ):
        """에이전트 커넥터 등록"""
        self.agent_connectors[agent_name] = connector

    async def send_to_ui_selection_agent(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """UI Selection Agent로 데이터 전송"""

        # UI Selection Agent가 필요로 하는 형식으로 변환
        ui_selection_payload = {
            'project_type': parsed_project.project_metadata.get('type'),
            'technical_requirements': [
                {
                    'id': req.id,
                    'description': req.description,
                    'category': req.category,
                    'constraints': req.constraints
                }
                for req in parsed_project.requirements
                if req.type == 'technical'
            ],
            'non_functional_requirements': [
                {
                    'type': req.category,
                    'description': req.description,
                    'metrics': req.metrics
                }
                for req in parsed_project.requirements
                if req.type == 'non_functional'
            ],
            'user_preferences': parsed_project.project_metadata.get(
                'user_preferences',
                {}
            )
        }

        # 메시지 생성 및 전송
        message = AgentMessage(
            source_agent='parser_agent',
            target_agent='ui_selection_agent',
            message_type='parsed_requirements',
            payload=ui_selection_payload,
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )

        connector = self.agent_connectors.get('ui_selection_agent')
        if connector:
            response = await connector.send_message(message)
            return response
        else:
            raise ValueError("UI Selection Agent connector not registered")

    async def send_to_component_decision_agent(
        self,
        parsed_project: ParsedProject
    ) -> Dict[str, Any]:
        """Component Decision Agent로 데이터 전송"""

        # Component Decision Agent용 페이로드 구성
        component_payload = {
            'functional_requirements': [
                {
                    'id': req.id,
                    'description': req.description,
                    'ui_elements': req.extracted_entities.get('ui_elements', []),
                    'user_interactions': req.extracted_entities.get('interactions', []),
                    'data_requirements': req.extracted_entities.get('data', [])
                }
                for req in parsed_project.requirements
                if req.type == 'functional'
            ],
            'ui_patterns': parsed_project.analysis_results.get('ui_patterns', []),
            'component_hints': parsed_project.analysis_results.get('component_hints', []),
            'complexity_assessment': parsed_project.project_metadata.get(
                'complexity',
                'medium'
            )
        }

        message = AgentMessage(
            source_agent='parser_agent',
            target_agent='component_decision_agent',
            message_type='ui_requirements',
            payload=component_payload,
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )

        connector = self.agent_connectors.get('component_decision_agent')
        if connector:
            return await connector.send_message(message)
        else:
            raise ValueError("Component Decision Agent connector not registered")

    async def receive_from_nl_input_agent(
        self,
        message: AgentMessage
    ) -> ParsedProject:
        """NL Input Agent로부터 데이터 수신"""

        if message.message_type != 'natural_language_input':
            raise ValueError(f"Unexpected message type: {message.message_type}")

        # NL Input Agent의 출력 처리
        nl_description = message.payload.get('description', '')
        clarifications = message.payload.get('clarifications', {})
        context = message.payload.get('context', {})

        # 파싱 실행
        parsed_project = await self.parse_requirements(
            [nl_description],
            context=context,
            clarifications=clarifications
        )

        return parsed_project
```

**표준 에이전트 커넥터**:

```python
class StandardAgentConnector:
    """표준 에이전트 커넥터"""

    def __init__(self, agent_name: str, communication_channel: Any):
        self.agent_name = agent_name
        self.channel = communication_channel

    async def send_message(
        self,
        message: AgentMessage
    ) -> Dict[str, Any]:
        """메시지 전송"""

        # 메시지 직렬화
        serialized = self._serialize_message(message)

        # 채널을 통해 전송
        response = await self.channel.send(
            destination=message.target_agent,
            data=serialized
        )

        # 응답 역직렬화
        return self._deserialize_response(response)

    async def receive_message(self) -> AgentMessage:
        """메시지 수신"""

        # 채널에서 수신
        raw_message = await self.channel.receive()

        # 역직렬화
        return self._deserialize_message(raw_message)

    def _serialize_message(self, message: AgentMessage) -> str:
        """메시지 직렬화"""
        return json.dumps({
            'source_agent': message.source_agent,
            'target_agent': message.target_agent,
            'message_type': message.message_type,
            'payload': message.payload,
            'correlation_id': message.correlation_id,
            'timestamp': message.timestamp.isoformat()
        })
```

**검증 기준**:

- [ ] 모든 에이전트와 통합
- [ ] 표준 메시지 형식
- [ ] 에러 처리 완성도
- [ ] 통신 신뢰성

#### SubTask 4.29.2: Parser Agent API 엔드포인트

**담당자**: API 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/agents/parser_endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio

router = APIRouter(
    prefix="/api/v1/agents/parser",
    tags=["parser-agent"]
)

class ParseRequest(BaseModel):
    """파싱 요청 모델"""
    requirements: List[str] = Field(..., min_items=1)
    project_type: Optional[str] = Field(None)
    domain: Optional[str] = Field(None)
    language: Optional[str] = Field('en')
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ParseResponse(BaseModel):
    """파싱 응답 모델"""
    project_id: str
    parsed_requirements: List[Dict[str, Any]]
    project_metadata: Dict[str, Any]
    analysis_results: Dict[str, Any]
    validation_results: Dict[str, Any]
    next_steps: List[str]

@router.post("/parse", response_model=ParseResponse)
async def parse_requirements(
    request: ParseRequest,
    background_tasks: BackgroundTasks
):
    """
    요구사항 파싱

    자연어 요구사항을 구조화된 형식으로 파싱합니다.
    """
    try:
        # Parser Agent 인스턴스
        parser_agent = get_parser_agent_instance()

        # 파싱 옵션 설정
        parsing_options = {
            'project_type': request.project_type,
            'domain': request.domain,
            'language': request.language,
            **request.options
        }

        # 파싱 실행
        parsed_project = await parser_agent.parse_requirements(
            request.requirements,
            options=parsing_options
        )

        # 백그라운드 분석 작업
        background_tasks.add_task(
            perform_deep_analysis,
            parsed_project.id,
            parsed_project
        )

        # 다음 단계 결정
        next_steps = determine_next_steps(parsed_project)

        return ParseResponse(
            project_id=parsed_project.id,
            parsed_requirements=[
                req.to_dict() for req in parsed_project.requirements
            ],
            project_metadata=parsed_project.project_metadata,
            analysis_results=parsed_project.analysis_results,
            validation_results=parsed_project.validation_results,
            next_steps=next_steps
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-dependencies")
async def analyze_dependencies(
    project_id: str,
    requirements: Optional[List[str]] = None
):
    """
    요구사항 의존성 분석

    요구사항 간의 의존성을 분석하고 시각화합니다.
    """
    parser_agent = get_parser_agent_instance()

    # 프로젝트 로드 또는 새 요구사항 파싱
    if project_id and not requirements:
        parsed_project = await load_parsed_project(project_id)
    else:
        parsed_project = await parser_agent.parse_requirements(requirements or [])

    # 의존성 분석
    dependency_analysis = await parser_agent.analyze_dependencies(
        parsed_project.requirements
    )

    return {
        'project_id': project_id or parsed_project.id,
        'dependencies': dependency_analysis['dependencies'],
        'cycles': dependency_analysis['cycles'],
        'critical_paths': dependency_analysis['critical_paths'],
        'visualization': await generate_dependency_visualization(
            dependency_analysis['graph']
        )
    }

@router.post("/validate")
async def validate_requirements(
    project_id: str,
    validation_type: str = "completeness"
):
    """
    요구사항 검증

    완성도, 일관성, 품질 등을 검증합니다.
    """
    valid_types = ['completeness', 'consistency', 'quality', 'all']
    if validation_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid validation type. Must be one of: {valid_types}"
        )

    parser_agent = get_parser_agent_instance()
    parsed_project = await load_parsed_project(project_id)

    validation_results = {}

    if validation_type in ['completeness', 'all']:
        validation_results['completeness'] = await parser_agent.validate_completeness(
            parsed_project
        )

    if validation_type in ['consistency', 'all']:
        validation_results['consistency'] = await parser_agent.check_consistency(
            parsed_project
        )

    if validation_type in ['quality', 'all']:
        validation_results['quality'] = await parser_agent.assess_quality(
            parsed_project
        )

    return {
        'project_id': project_id,
        'validation_type': validation_type,
        'results': validation_results,
        'overall_score': calculate_overall_validation_score(validation_results)
    }

@router.get("/domains")
async def list_supported_domains():
    """지원되는 도메인 목록"""
    return {
        'domains': [
            {
                'id': 'e_commerce',
                'name': 'E-Commerce',
                'description': 'Online shopping and retail'
            },
            {
                'id': 'healthcare',
                'name': 'Healthcare',
                'description': 'Medical and health services'
            },
            {
                'id': 'finance',
                'name': 'Finance',
                'description': 'Banking and financial services'
            },
            # ... 더 많은 도메인
        ]
    }

@router.get("/languages")
async def list_supported_languages():
    """지원되는 언어 목록"""
    return {
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'ko', 'name': 'Korean'},
            {'code': 'ja', 'name': 'Japanese'},
            {'code': 'zh-cn', 'name': 'Chinese (Simplified)'},
            {'code': 'es', 'name': 'Spanish'},
            # ... 더 많은 언어
        ]
    }

# WebSocket 엔드포인트
@router.websocket("/ws/parse-stream")
async def parse_stream(websocket: WebSocket):
    """실시간 파싱 스트림"""
    await websocket.accept()

    try:
        while True:
            # 클라이언트로부터 요구사항 수신
            data = await websocket.receive_json()

            # 파싱 시작
            parser_agent = get_parser_agent_instance()

            # 진행 상황 스트리밍
            async for progress in parser_agent.parse_with_progress(
                data['requirements']
            ):
                await websocket.send_json({
                    'type': 'progress',
                    'data': progress
                })

            # 완료
            await websocket.send_json({
                'type': 'complete',
                'data': {'message': 'Parsing completed'}
            })

    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'data': {'message': str(e)}
        })
    finally:
        await websocket.close()
```

**검증 기준**:

- [ ] RESTful API 설계
- [ ] WebSocket 실시간 통신
- [ ] 에러 처리 완성도
- [ ] API 문서화

#### SubTask 4.29.3: Parser Agent 통합 테스트 스위트

**담당자**: QA 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/tests/agents/parser/test_parser_integration.py
import pytest
import asyncio
from typing import List, Dict, Any

@pytest.mark.integration
class TestParserAgentIntegration:
    """Parser Agent 통합 테스트"""

    @pytest.fixture
    async def parser_agent(self):
        """Parser Agent 인스턴스"""
        from parser_agent import ParserAgent

        agent = ParserAgent()
        await agent.initialize()
        yield agent
        await agent.cleanup()

    @pytest.fixture
    def sample_requirements(self):
        """샘플 요구사항"""
        return [
            "The system shall allow users to register with email and password",
            "Users must be able to reset their password via email",
            "The system should support OAuth2 authentication with Google and Facebook",
            "All passwords must be encrypted using bcrypt with a minimum of 12 rounds",
            "User sessions should expire after 30 minutes of inactivity",
            "The system shall log all authentication attempts for security auditing"
        ]

    @pytest.mark.asyncio
    async def test_end_to_end_parsing(self, parser_agent, sample_requirements):
        """종단 간 파싱 테스트"""

        # 파싱 실행
        parsed_project = await parser_agent.parse_requirements(
            sample_requirements
        )

        # 기본 검증
        assert parsed_project is not None
        assert len(parsed_project.requirements) == len(sample_requirements)

        # 분류 검증
        functional_reqs = [
            r for r in parsed_project.requirements
            if r.type == 'functional'
        ]
        non_functional_reqs = [
            r for r in parsed_project.requirements
            if r.type == 'non_functional'
        ]

        assert len(functional_reqs) >= 3  # 최소 3개의 기능 요구사항
        assert len(non_functional_reqs) >= 2  # 최소 2개의 비기능 요구사항

        # 보안 카테고리 검증
        security_reqs = [
            r for r in parsed_project.requirements
            if r.category == 'security'
        ]
        assert len(security_reqs) >= 2

    @pytest.mark.asyncio
    async def test_multilingual_parsing(self, parser_agent):
        """다국어 파싱 테스트"""

        multilingual_requirements = [
            "The system shall support user registration",  # English
            "시스템은 사용자 등록을 지원해야 한다",  # Korean
            "システムはユーザー登録をサポートする必要があります",  # Japanese
            "El sistema debe permitir el registro de usuarios",  # Spanish
            "系统应支持用户注册"  # Chinese
        ]

        result = await parser_agent.parse_multilingual_requirements(
            multilingual_requirements
        )

        # 언어 감지 검증
        assert len(result['detected_languages']) >= 5
        assert 'en' in result['detected_languages']
        assert 'ko' in result['detected_languages']

        # 번역 검증
        assert len(result['translations']) == len(multilingual_requirements)

        # 모든 번역이 영어로 되었는지 확인
        for translation in result['translations']:
            assert translation.english_translation
            assert 'user' in translation.english_translation.lower()
            assert 'registration' in translation.english_translation.lower() or \
                   'register' in translation.english_translation.lower()

    @pytest.mark.asyncio
    async def test_domain_specific_parsing(self, parser_agent):
        """도메인 특화 파싱 테스트"""

        healthcare_requirements = [
            "The system must be HIPAA compliant",
            "Patient records shall be encrypted at rest and in transit",
            "Doctors should be able to access patient EHR within 2 seconds",
            "The system shall support HL7 FHIR for data exchange",
            "Audit logs must be maintained for 7 years"
        ]

        parsed = await parser_agent.parse_with_domain_context(
            healthcare_requirements,
            detected_domain='healthcare'
        )

        # 도메인 감지 검증
        assert parsed.domain == 'healthcare'

        # HIPAA 컴플라이언스 검증
        compliance_found = False
        for req in parsed.requirements:
            if 'HIPAA' in req.detected_terminology:
                compliance_found = True
                break
        assert compliance_found

        # 의료 용어 감지
        medical_terms = ['EHR', 'HL7', 'FHIR', 'patient', 'doctor']
        detected_terms = set()
        for req in parsed.requirements:
            detected_terms.update(req.detected_terminology.keys())

        assert any(term in detected_terms for term in medical_terms)

    @pytest.mark.asyncio
    async def test_dependency_analysis(self, parser_agent):
        """의존성 분석 테스트"""

        dependent_requirements = [
            "REQ-001: Users shall be able to create accounts",
            "REQ-002: Users shall be able to login (depends on REQ-001)",
            "REQ-003: Users shall be able to update profile (requires REQ-002)",
            "REQ-004: System shall send welcome email after REQ-001",
            "REQ-005: Admin can disable user accounts (depends on REQ-001)"
        ]

        parsed = await parser_agent.parse_requirements(dependent_requirements)
        deps = await parser_agent.analyze_dependencies(parsed.requirements)

        # 의존성 감지 검증
        assert len(deps['dependencies']) >= 4

        # 의존성 체인 검증
        # REQ-001 -> REQ-002 -> REQ-003
        chain_found = False
        for path in deps['critical_paths']:
            if 'REQ-001' in path and 'REQ-002' in path and 'REQ-003' in path:
                chain_found = True
                break
        assert chain_found

        # 순환 의존성 없음 확인
        assert len(deps['cycles']) == 0

    @pytest.mark.asyncio
    async def test_conflict_detection(self, parser_agent):
        """충돌 감지 테스트"""

        conflicting_requirements = [
            "The system shall store all user data permanently",
            "User data must be deleted after 90 days for GDPR compliance",
            "The application must work offline",
            "All data validation must be performed on the server",
            "Response time shall be under 100ms",
            "All requests must go through complex validation taking 500ms"
        ]

        parsed = await parser_agent.parse_requirements(conflicting_requirements)
        conflicts = await parser_agent.detect_conflicts(parsed.requirements)

        # 충돌 감지 검증
        assert len(conflicts) >= 2

        # 논리적 충돌 확인
        logical_conflict_found = False
        for conflict in conflicts:
            if conflict.conflict_type == 'logical':
                logical_conflict_found = True
                break
        assert logical_conflict_found

    @pytest.mark.asyncio
    async def test_version_control(self, parser_agent):
        """버전 관리 테스트"""

        # 초기 요구사항
        v1_requirements = ["Users shall be able to login with email"]
        parsed_v1 = await parser_agent.parse_requirements(v1_requirements)

        # 버전 추적
        version_control = parser_agent.version_control
        v1 = await version_control.track_requirement_change(
            parsed_v1.requirements[0],
            author="test_user",
            change_description="Initial requirement"
        )

        # 요구사항 수정
        v2_requirements = ["Users shall be able to login with email or phone number"]
        parsed_v2 = await parser_agent.parse_requirements(v2_requirements)
        parsed_v2.requirements[0].id = parsed_v1.requirements[0].id  # 같은 ID 유지

        v2 = await version_control.track_requirement_change(
            parsed_v2.requirements[0],
            author="test_user",
            change_description="Added phone number login"
        )

        # 버전 이력 검증
        history = await version_control.get_requirement_history(
            parsed_v1.requirements[0].id
        )
        assert len(history) == 2
        assert history[0].version_number == "1.0.0"
        assert history[1].version_number == "1.0.1"

        # 버전 비교
        diff = await version_control.compare_versions(
            parsed_v1.requirements[0].id,
            v1.version_id,
            v2.version_id
        )
        assert len(diff.changes) > 0

    @pytest.mark.asyncio
    async def test_performance_optimization(self, parser_agent):
        """성능 최적화 테스트"""

        # 대량 요구사항 생성
        large_requirements = [
            f"The system shall support feature {i} with performance metric {i*10}ms"
            for i in range(100)
        ]

        # 성능 측정
        import time

        # 일반 파싱
        start_time = time.time()
        parsed_normal = await parser_agent.parse_requirements(large_requirements)
        normal_time = time.time() - start_time

        # 최적화된 파싱
        start_time = time.time()
        parsed_optimized = await parser_agent.optimize_parsing_pipeline(
            large_requirements,
            optimization_level='speed'
        )
        optimized_time = time.time() - start_time

        # 성능 개선 검증
        assert optimized_time < normal_time * 0.7  # 최소 30% 개선

        # 결과 동일성 검증
        assert len(parsed_normal.requirements) == len(parsed_optimized.requirements)

    @pytest.mark.asyncio
    async def test_agent_integration(self, parser_agent):
        """다른 에이전트와의 통합 테스트"""

        # Mock 에이전트 커넥터 설정
        mock_ui_connector = MockAgentConnector('ui_selection_agent')
        await parser_agent.interface.register_agent_connector(
            'ui_selection_agent',
            mock_ui_connector
        )

        # 요구사항 파싱
        requirements = [
            "Build a modern e-commerce website with React",
            "Support mobile responsive design",
            "Include shopping cart functionality"
        ]

        parsed = await parser_agent.parse_requirements(requirements)

        # UI Selection Agent로 전송
        response = await parser_agent.interface.send_to_ui_selection_agent(parsed)

        # 전송 검증
        assert response is not None
        assert 'message_received' in response
        assert mock_ui_connector.last_message is not None
        assert mock_ui_connector.last_message.source_agent == 'parser_agent'
        assert mock_ui_connector.last_message.target_agent == 'ui_selection_agent'
```

**성능 벤치마크**:

```python
@pytest.mark.benchmark
class TestParserPerformance:
    """Parser Agent 성능 벤치마크"""

    @pytest.mark.asyncio
    async def test_parsing_throughput(self, parser_agent, benchmark):
        """파싱 처리량 테스트"""

        requirements = [
            "The system shall support user authentication",
            "Data must be encrypted at rest",
            "Response time should be under 200ms"
        ]

        async def parse():
            await parser_agent.parse_requirements(requirements)

        # 벤치마크 실행
        result = await benchmark(parse)

        # 성능 목표: 100ms 이내
        assert result < 0.1

    @pytest.mark.asyncio
    async def test_concurrent_parsing(self, parser_agent):
        """동시 파싱 성능 테스트"""

        # 동시 요청 수
        num_concurrent = 20

        test_requirement = "The system shall process concurrent user requests"

        async def parse_task():
            return await parser_agent.parse_requirements([test_requirement])

        # 동시 실행
        start_time = time.time()
        tasks = [parse_task() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # 모든 요청 성공 확인
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)

        # 동시 처리 성능 확인
        assert total_time < 5.0  # 20개 요청이 5초 이내
```

**검증 기준**:

- [ ] 모든 기능 테스트 통과
- [ ] 통합 시나리오 검증
- [ ] 성능 목표 달성
- [ ] 에러 케이스 처리

#### SubTask 4.29.4: Parser Agent 문서화 및 가이드

**담당자**: 기술 문서 작성자  
**예상 소요시간**: 8시간

**작업 내용**:

````markdown
# Parser Agent 사용 가이드

## 개요

Parser Agent는 자연어로 작성된 프로젝트 요구사항을 구조화된 형식으로 변환하는 핵심 에이전트입니다.

## 주요 기능

### 1. 요구사항 파싱

- 자연어 요구사항을 구조화된 데이터로 변환
- 기능/비기능 요구사항 자동 분류
- 우선순위 자동 할당

### 2. 고급 분석

- 요구사항 간 의존성 분석
- 충돌 감지 및 해결 제안
- 추적성 매트릭스 생성

### 3. 도메인 특화 파싱

- 15개 산업 도메인 지원
- 도메인별 규칙 및 용어 적용
- 규정 준수 검증

### 4. 다국어 지원

- 15개 언어 자동 감지
- 실시간 번역 및 파싱
- 문화적 고려사항 분석

## 사용 방법

### Python SDK

```python
from t_developer import ParserAgent

# 에이전트 초기화
parser = ParserAgent()

# 요구사항 파싱
requirements = [
    "사용자는 이메일과 비밀번호로 로그인할 수 있어야 한다",
    "시스템은 동시에 1000명의 사용자를 지원해야 한다"
]

parsed_project = await parser.parse_requirements(
    requirements,
    options={
        'domain': 'e_commerce',
        'language': 'ko'
    }
)

# 결과 접근
for req in parsed_project.requirements:
    print(f"{req.id}: {req.description}")
    print(f"Type: {req.type}, Priority: {req.priority}")
```
````

### REST API

```bash
# 요구사항 파싱
curl -X POST https://api.t-developer.com/v1/agents/parser/parse \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": [
      "Build an e-commerce website with shopping cart",
      "Support payment processing with Stripe"
    ],
    "domain": "e_commerce",
    "language": "en"
  }'

# 의존성 분석
curl -X POST https://api.t-developer.com/v1/agents/parser/analyze-dependencies \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_123"
  }'
```

### WebSocket 실시간 파싱

```javascript
const ws = new WebSocket('wss://api.t-developer.com/v1/agents/parser/ws/parse-stream');

ws.onopen = () => {
  ws.send(
    JSON.stringify({
      requirements: ['Build a social media app'],
      options: { realtime: true },
    }),
  );
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'progress') {
    console.log(`Progress: ${data.data.percentage}%`);
  }
};
```

## 출력 형식

### ParsedProject 구조

```typescript
interface ParsedProject {
  id: string;
  requirements: ParsedRequirement[];
  project_metadata: {
    type: string;
    domain: string;
    complexity: string;
    estimated_effort: number;
  };
  analysis_results: {
    dependencies: Dependency[];
    conflicts: Conflict[];
    gaps: Gap[];
  };
  validation_results: {
    completeness: number;
    consistency: number;
    quality: number;
  };
}

interface ParsedRequirement {
  id: string;
  original_text: string;
  description: string;
  type: 'functional' | 'non_functional';
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  complexity: string;
  extracted_entities: {
    actors: string[];
    actions: string[];
    objects: string[];
    constraints: string[];
  };
  metrics: {
    testability: number;
    clarity: number;
    completeness: number;
  };
}
```

## 모범 사례

### 1. 명확한 요구사항 작성

```
좋은 예:
- "사용자는 5초 이내에 로그인할 수 있어야 한다"
- "시스템은 99.9%의 가용성을 유지해야 한다"

나쁜 예:
- "시스템이 빨라야 한다"
- "좋은 UX가 필요하다"
```

### 2. 도메인 컨텍스트 제공

```python
# 도메인 지정으로 더 정확한 파싱
parsed = await parser.parse_requirements(
    requirements,
    options={'domain': 'healthcare'}  # HIPAA 규정 등 자동 고려
)
```

### 3. 배치 처리 활용

```python
# 대량 요구사항은 배치로 처리
large_requirements = load_requirements_from_file('requirements.txt')
parsed = await parser.optimize_parsing_pipeline(
    large_requirements,
    optimization_level='speed'
)
```

## 문제 해결

### 일반적인 오류

1. **언어 감지 실패**

   ```python
   # 언어 명시적 지정
   options = {'language': 'ko', 'fallback_language': 'en'}
   ```

2. **도메인 자동 감지 오류**

   ```python
   # 도메인 힌트 제공
   options = {'domain_hints': ['medical', 'patient', 'HIPAA']}
   ```

3. **성능 이슈**

   ```python
   # 캐싱 활성화
   parser.enable_caching(ttl=3600)

   # 병렬 처리
   parser.set_concurrency(max_workers=10)
   ```

## API 레퍼런스

전체 API 문서는 [여기](https://docs.t-developer.com/agents/parser)에서 확인하세요.

## 다음 단계

파싱이 완료되면:

1. UI Selection Agent로 기술 스택 선택
2. Component Decision Agent로 컴포넌트 설계
3. Match Rate Agent로 재사용 가능한 컴포넌트 검색

## 지원

- 이슈 리포트: https://github.com/t-developer/parser-agent/issues
- 커뮤니티: https://community.t-developer.com
- 이메일: support@t-developer.com

````

**검증 기준**:

- [ ] 완전한 사용 가이드
- [ ] API 레퍼런스
- [ ] 코드 예제
- [ ] 문제 해결 가이드

---

### Task 4.30: Parser Agent 모니터링 및 최적화

#### SubTask 4.30.1: 실시간 모니터링 대시보드

**담당자**: 모니터링 엔지니어
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/monitoring_dashboard.py
from prometheus_client import Counter, Histogram, Gauge, Info
import asyncio
from typing import Dict, Any
import time

# Prometheus 메트릭 정의
parsing_requests_total = Counter(
    'parser_agent_requests_total',
    'Total number of parsing requests',
    ['status', 'domain', 'language']
)

parsing_duration_seconds = Histogram(
    'parser_agent_parsing_duration_seconds',
    'Parsing request duration in seconds',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_parsing_sessions = Gauge(
    'parser_agent_active_sessions',
    'Number of active parsing sessions'
)

requirements_parsed_total = Counter(
    'parser_agent_requirements_parsed_total',
    'Total number of requirements parsed',
    ['type', 'category', 'priority']
)

parsing_errors_total = Counter(
    'parser_agent_errors_total',
    'Total number of parsing errors',
    ['error_type', 'domain']
)

nlp_model_info = Info(
    'parser_agent_nlp_model',
    'Information about the NLP model in use'
)

class ParserMonitoringDashboard:
    """Parser Agent 모니터링 대시보드"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.dashboard_server = DashboardServer()
        self.alert_manager = AlertManager()

    async def initialize(self):
        """모니터링 시스템 초기화"""

        # NLP 모델 정보 설정
        nlp_model_info.info({
            'model': 'spacy-transformers',
            'version': '3.7.0',
            'language_models': 'en,ko,ja,zh,es,fr,de'
        })

        # 대시보드 서버 시작
        await self.dashboard_server.start(port=9090)

        # 메트릭 수집 시작
        asyncio.create_task(self._collect_metrics_loop())

        # 알림 체크 시작
        asyncio.create_task(self._check_alerts_loop())

    async def record_parsing_request(
        self,
        domain: str,
        language: str,
        requirements_count: int,
        duration: float,
        status: str = 'success'
    ):
        """파싱 요청 기록"""

        # 요청 카운터 증가
        parsing_requests_total.labels(
            status=status,
            domain=domain,
            language=language
        ).inc()

        # 소요 시간 기록
        parsing_duration_seconds.observe(duration)

        # 요구사항 수 기록
        requirements_parsed_total.labels(
            type='all',
            category='all',
            priority='all'
        ).inc(requirements_count)

    async def record_parsed_requirement(
        self,
        requirement: ParsedRequirement
    ):
        """개별 요구사항 파싱 기록"""

        requirements_parsed_total.labels(
            type=requirement.type,
            category=requirement.category,
            priority=requirement.priority
        ).inc()

    async def record_error(
        self,
        error_type: str,
        domain: str = 'unknown'
    ):
        """에러 기록"""

        parsing_errors_total.labels(
            error_type=error_type,
            domain=domain
        ).inc()

    async def _collect_metrics_loop(self):
        """메트릭 수집 루프"""

        while True:
            try:
                # 시스템 메트릭 수집
                system_metrics = await self.metrics_collector.collect_system_metrics()

                # 비즈니스 메트릭 수집
                business_metrics = await self.metrics_collector.collect_business_metrics()

                # 대시보드 업데이트
                await self.dashboard_server.update_metrics({
                    'system': system_metrics,
                    'business': business_metrics
                })

            except Exception as e:
                print(f"Metrics collection error: {e}")

            await asyncio.sleep(10)  # 10초마다 수집

    async def _check_alerts_loop(self):
        """알림 체크 루프"""

        while True:
            try:
                # 알림 조건 체크
                alerts = await self.alert_manager.check_alerts()

                for alert in alerts:
                    await self.alert_manager.send_alert(alert)

            except Exception as e:
                print(f"Alert checking error: {e}")

            await asyncio.sleep(30)  # 30초마다 체크
````

**Grafana 대시보드 설정**:

```json
{
  "dashboard": {
    "title": "Parser Agent Monitoring",
    "panels": [
      {
        "title": "Parsing Request Rate",
        "targets": [
          {
            "expr": "rate(parser_agent_requests_total[5m])",
            "legendFormat": "{{status}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Parsing Duration (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(parser_agent_parsing_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Duration"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Requirements by Type",
        "targets": [
          {
            "expr": "sum by (type) (rate(parser_agent_requirements_parsed_total[5m]))",
            "legendFormat": "{{type}}"
          }
        ],
        "type": "piechart"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum by (error_type) (rate(parser_agent_errors_total[5m]))",
            "legendFormat": "{{error_type}}"
          }
        ],
        "type": "table"
      },
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "parser_agent_active_sessions",
            "legendFormat": "Active Sessions"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Language Distribution",
        "targets": [
          {
            "expr": "sum by (language) (parser_agent_requests_total)",
            "legendFormat": "{{language}}"
          }
        ],
        "type": "bargauge"
      }
    ]
  }
}
```

**검증 기준**:

- [ ] 실시간 메트릭 수집
- [ ] Grafana 대시보드 구성
- [ ] 알림 시스템 구현
- [ ] 성능 추세 분석

#### SubTask 4.30.2: 파싱 정확도 분석 시스템

**담당자**: ML 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/accuracy_analyzer.py
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from dataclasses import dataclass

@dataclass
class AccuracyMetrics:
    overall_accuracy: float
    precision_by_type: Dict[str, float]
    recall_by_type: Dict[str, float]
    f1_by_type: Dict[str, float]
    confusion_matrix: Dict[str, Dict[str, int]]
    misclassification_patterns: List[Dict[str, Any]]

class ParsingAccuracyAnalyzer:
    """파싱 정확도 분석 시스템"""

    def __init__(self):
        self.ground_truth_db = GroundTruthDatabase()
        self.error_analyzer = ErrorPatternAnalyzer()
        self.feedback_collector = UserFeedbackCollector()

    async def analyze_parsing_accuracy(
        self,
        parsed_results: List[ParsedRequirement],
        ground_truth: Optional[List[Dict[str, Any]]] = None
    ) -> AccuracyMetrics:
        """파싱 정확도 분석"""

        # Ground truth 로드
        if not ground_truth:
            ground_truth = await self._load_ground_truth(parsed_results)

        # 예측값과 실제값 추출
        y_true = []
        y_pred = []

        for i, parsed in enumerate(parsed_results):
            if i < len(ground_truth):
                y_true.append(ground_truth[i]['type'])
                y_pred.append(parsed.type)

        # 메트릭 계산
        accuracy = np.mean([yt == yp for yt, yp in zip(y_true, y_pred)])

        # 클래스별 메트릭
        labels = list(set(y_true + y_pred))
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average=None
        )

        # 결과 구성
        metrics = AccuracyMetrics(
            overall_accuracy=accuracy,
            precision_by_type={
                label: prec for label, prec in zip(labels, precision)
            },
            recall_by_type={
                label: rec for label, rec in zip(labels, recall)
            },
            f1_by_type={
                label: f for label, f in zip(labels, f1)
            },
            confusion_matrix=await self._build_confusion_matrix(y_true, y_pred),
            misclassification_patterns=await self._analyze_errors(
                parsed_results, ground_truth
            )
        )

        return metrics

    async def collect_user_feedback(
        self,
        requirement_id: str,
        feedback: Dict[str, Any]
    ):
        """사용자 피드백 수집"""

        # 피드백 저장
        await self.feedback_collector.save_feedback(
            requirement_id,
            feedback
        )

        # 정확도 재계산 트리거
        if feedback.get('correction'):
            await self._update_ground_truth(
                requirement_id,
                feedback['correction']
            )

            # 모델 재학습 권장 확인
            if await self._should_retrain_model():
                await self._trigger_model_retraining()

    async def generate_accuracy_report(
        self,
        time_period: str = 'last_7_days'
    ) -> Dict[str, Any]:
        """정확도 리포트 생성"""

        # 기간별 메트릭 수집
        historical_metrics = await self._get_historical_metrics(time_period)

        report = {
            'summary': {
                'average_accuracy': np.mean([
                    m.overall_accuracy for m in historical_metrics
                ]),
                'total_requirements_parsed': len(historical_metrics),
                'feedback_incorporated': await self._count_feedback(time_period)
            },
            'trends': await self._analyze_accuracy_trends(historical_metrics),
            'problem_areas': await self._identify_problem_areas(historical_metrics),
            'recommendations': await self._generate_improvement_recommendations(
                historical_metrics
            )
        }

        return report

    async def _analyze_errors(
        self,
        parsed: List[ParsedRequirement],
        ground_truth: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """오류 패턴 분석"""

        error_patterns = []

        for i, (p, gt) in enumerate(zip(parsed, ground_truth)):
            if p.type != gt['type'] or p.category != gt.get('category'):
                pattern = {
                    'requirement_id': p.id,
                    'predicted_type': p.type,
                    'actual_type': gt['type'],
                    'predicted_category': p.category,
                    'actual_category': gt.get('category'),
                    'confidence': p.confidence,
                    'error_reason': await self.error_analyzer.analyze_error(p, gt),
                    'suggested_improvement': await self._suggest_improvement(p, gt)
                }
                error_patterns.append(pattern)

        return error_patterns
```

**자동 개선 시스템**:

```python
class ParsingImprovementSystem:
    """파싱 자동 개선 시스템"""

    def __init__(self):
        self.model_trainer = ModelTrainer()
        self.rule_optimizer = RuleOptimizer()
        self.pattern_learner = PatternLearner()

    async def implement_improvements(
        self,
        accuracy_metrics: AccuracyMetrics,
        feedback_data: List[Dict[str, Any]]
    ):
        """개선사항 구현"""

        improvements = []

        # 1. 규칙 기반 개선
        if accuracy_metrics.overall_accuracy < 0.85:
            rule_improvements = await self.rule_optimizer.optimize_rules(
                accuracy_metrics.misclassification_patterns
            )
            improvements.extend(rule_improvements)

        # 2. 패턴 학습
        new_patterns = await self.pattern_learner.learn_from_errors(
            accuracy_metrics.misclassification_patterns,
            feedback_data
        )
        improvements.extend(new_patterns)

        # 3. 모델 미세 조정
        if len(feedback_data) > 100:  # 충분한 피드백
            model_improvements = await self.model_trainer.fine_tune(
                feedback_data
            )
            improvements.append(model_improvements)

        # 개선사항 적용
        for improvement in improvements:
            await self._apply_improvement(improvement)

        return improvements

    async def a_b_test_improvements(
        self,
        improvement: Dict[str, Any],
        test_duration: int = 3600  # 1시간
    ) -> Dict[str, Any]:
        """개선사항 A/B 테스트"""

        # A/B 테스트 설정
        test_config = {
            'control_group': 'current_parser',
            'treatment_group': f'parser_with_{improvement["type"]}',
            'split_ratio': 0.5,
            'metrics': ['accuracy', 'speed', 'user_satisfaction']
        }

        # 테스트 실행
        results = await self._run_ab_test(test_config, test_duration)

        # 결과 분석
        if results['treatment_performance'] > results['control_performance'] * 1.05:
            # 5% 이상 개선 시 채택
            await self._promote_improvement(improvement)
            return {
                'status': 'adopted',
                'improvement': results['treatment_performance'] - results['control_performance']
            }
        else:
            return {
                'status': 'rejected',
                'reason': 'Insufficient improvement'
            }
```

**검증 기준**:

- [ ] 정확도 메트릭 계산
- [ ] 오류 패턴 분석
- [ ] 자동 개선 시스템
- [ ] A/B 테스트 프레임워크

#### SubTask 4.30.3: 파싱 로그 분석 및 인사이트

**담당자**: 데이터 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/log_analytics.py
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import asyncio

class ParsingLogAnalytics:
    """파싱 로그 분석 시스템"""

    def __init__(self):
        self.log_storage = LogStorage()
        self.analytics_engine = AnalyticsEngine()
        self.insight_generator = InsightGenerator()

    async def analyze_parsing_logs(
        self,
        time_range: Tuple[datetime, datetime],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """파싱 로그 분석"""

        # 로그 데이터 로드
        logs = await self.log_storage.fetch_logs(time_range, filters)
        df = pd.DataFrame(logs)

        analysis = {
            'summary_statistics': await self._calculate_summary_stats(df),
            'usage_patterns': await self._analyze_usage_patterns(df),
            'performance_metrics': await self._analyze_performance(df),
            'error_analysis': await self._analyze_errors(df),
            'user_behavior': await self._analyze_user_behavior(df),
            'insights': []
        }

        # 인사이트 생성
        insights = await self.insight_generator.generate_insights(analysis)
        analysis['insights'] = insights

        return analysis

    async def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """요약 통계 계산"""

        return {
            'total_requests': len(df),
            'unique_users': df['user_id'].nunique(),
            'average_requirements_per_request': df['requirements_count'].mean(),
            'most_common_domain': df['domain'].mode()[0] if not df.empty else None,
            'language_distribution': df['language'].value_counts().to_dict(),
            'success_rate': (df['status'] == 'success').mean() * 100,
            'average_parsing_time': df['duration_ms'].mean()
        }

    async def _analyze_usage_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """사용 패턴 분석"""

        # 시간대별 사용량
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_usage = df.groupby('hour').size().to_dict()

        # 요일별 사용량
        df['dayofweek'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        daily_usage = df.groupby('dayofweek').size().to_dict()

        # 도메인별 트렌드
        domain_trends = df.groupby(['domain', pd.Grouper(
            key='timestamp', freq='D'
        )]).size().unstack(fill_value=0)

        return {
            'hourly_distribution': hourly_usage,
            'daily_distribution': daily_usage,
            'peak_hours': self._identify_peak_hours(hourly_usage),
            'domain_trends': domain_trends.to_dict(),
            'growth_rate': await self._calculate_growth_rate(df)
        }

    async def _analyze_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """성능 분석"""

        return {
            'average_response_time': {
                'overall': df['duration_ms'].mean(),
                'by_domain': df.groupby('domain')['duration_ms'].mean().to_dict(),
                'by_language': df.groupby('language')['duration_ms'].mean().to_dict()
            },
            'percentiles': {
                'p50': df['duration_ms'].quantile(0.5),
                'p90': df['duration_ms'].quantile(0.9),
                'p95': df['duration_ms'].quantile(0.95),
                'p99': df['duration_ms'].quantile(0.99)
            },
            'slow_requests': await self._identify_slow_requests(df),
            'performance_trends': await self._analyze_performance_trends(df)
        }

    async def generate_executive_dashboard(
        self,
        time_period: str = 'last_30_days'
    ) -> Dict[str, Any]:
        """경영진 대시보드 생성"""

        # 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # 데이터 수집
        current_period_data = await self.analyze_parsing_logs(
            (start_date, en
```

```python
        # 데이터 수집 (계속)
        current_period_data = await self.analyze_parsing_logs(
            (start_date, end_date)
        )

        # 이전 기간 비교
        previous_start = start_date - timedelta(days=30)
        previous_period_data = await self.analyze_parsing_logs(
            (previous_start, start_date)
        )

        dashboard = {
            'key_metrics': {
                'total_parsing_requests': {
                    'current': current_period_data['summary_statistics']['total_requests'],
                    'previous': previous_period_data['summary_statistics']['total_requests'],
                    'change_percentage': self._calculate_change_percentage(
                        current_period_data['summary_statistics']['total_requests'],
                        previous_period_data['summary_statistics']['total_requests']
                    )
                },
                'active_users': {
                    'current': current_period_data['summary_statistics']['unique_users'],
                    'trend': 'increasing' if current_period_data['summary_statistics']['unique_users'] >
                            previous_period_data['summary_statistics']['unique_users'] else 'decreasing'
                },
                'average_accuracy': await self._get_average_accuracy(time_period),
                'system_reliability': current_period_data['summary_statistics']['success_rate']
            },
            'usage_insights': {
                'most_active_domains': await self._get_top_domains(current_period_data),
                'language_adoption': await self._analyze_language_adoption(current_period_data),
                'feature_utilization': await self._analyze_feature_usage(current_period_data)
            },
            'business_impact': {
                'time_saved': await self._calculate_time_savings(current_period_data),
                'cost_reduction': await self._estimate_cost_savings(current_period_data),
                'productivity_gains': await self._measure_productivity_gains(current_period_data)
            },
            'recommendations': await self._generate_executive_recommendations(
                current_period_data,
                previous_period_data
            )
        }

        return dashboard

    async def _generate_executive_recommendations(
        self,
        current_data: Dict[str, Any],
        previous_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """경영진 권장사항 생성"""

        recommendations = []

        # 사용량 증가 패턴
        if current_data['summary_statistics']['total_requests'] > previous_data['summary_statistics']['total_requests'] * 1.2:
            recommendations.append({
                'type': 'scaling',
                'priority': 'high',
                'title': 'Consider Infrastructure Scaling',
                'description': 'Usage has increased by more than 20%. Consider scaling infrastructure to maintain performance.',
                'estimated_cost': await self._estimate_scaling_cost(),
                'expected_benefit': 'Maintain sub-second response times'
            })

        # 정확도 개선 기회
        accuracy = await self._get_average_accuracy('last_30_days')
        if accuracy < 0.85:
            recommendations.append({
                'type': 'quality',
                'priority': 'medium',
                'title': 'Invest in Model Improvement',
                'description': f'Current accuracy is {accuracy:.1%}. Investing in model training could improve accuracy to 90%+',
                'estimated_cost': '$10,000-15,000',
                'expected_benefit': 'Reduce manual correction time by 50%'
            })

        # 새로운 도메인 기회
        domain_growth = await self._analyze_domain_growth(current_data)
        for domain, growth in domain_growth.items():
            if growth > 50:  # 50% 성장
                recommendations.append({
                    'type': 'expansion',
                    'priority': 'medium',
                    'title': f'Optimize for {domain} Domain',
                    'description': f'{domain} usage grew {growth}%. Consider domain-specific optimizations.',
                    'estimated_cost': '$5,000-8,000',
                    'expected_benefit': f'Capture growing {domain} market'
                })

        return recommendations
```

**실시간 인사이트 생성기**:

```python
class RealTimeInsightGenerator:
    """실시간 인사이트 생성"""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.alert_system = AlertSystem()

    async def monitor_real_time(self):
        """실시간 모니터링 및 인사이트 생성"""

        while True:
            try:
                # 최근 5분간 데이터
                recent_logs = await self._get_recent_logs(minutes=5)

                # 이상 징후 감지
                anomalies = await self.anomaly_detector.detect(recent_logs)
                if anomalies:
                    for anomaly in anomalies:
                        insight = await self._generate_anomaly_insight(anomaly)
                        await self.alert_system.send_insight(insight)

                # 실시간 트렌드
                trends = await self.trend_analyzer.analyze_real_time(recent_logs)
                if trends.get('significant_changes'):
                    for change in trends['significant_changes']:
                        insight = await self._generate_trend_insight(change)
                        await self.alert_system.send_insight(insight)

                # 성능 임계값 체크
                performance = await self._check_performance_thresholds(recent_logs)
                if performance.get('violations'):
                    for violation in performance['violations']:
                        insight = await self._generate_performance_insight(violation)
                        await self.alert_system.send_insight(insight, priority='high')

            except Exception as e:
                print(f"Real-time monitoring error: {e}")

            await asyncio.sleep(30)  # 30초마다 체크

    async def _generate_anomaly_insight(
        self,
        anomaly: Dict[str, Any]
    ) -> Dict[str, Any]:
        """이상 징후 인사이트 생성"""

        return {
            'type': 'anomaly',
            'timestamp': datetime.now(),
            'title': f"Anomaly Detected: {anomaly['type']}",
            'description': anomaly['description'],
            'severity': anomaly['severity'],
            'affected_metrics': anomaly['metrics'],
            'recommended_action': await self._recommend_action(anomaly),
            'auto_remediation': await self._can_auto_remediate(anomaly)
        }
```

**로그 시각화 도구**:

```python
class LogVisualizationTools:
    """로그 데이터 시각화"""

    async def create_interactive_dashboard(
        self,
        analysis_results: Dict[str, Any]
    ) -> str:
        """대화형 대시보드 생성"""

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # 서브플롯 생성
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Parsing Requests Over Time',
                'Language Distribution',
                'Response Time Distribution',
                'Error Rate by Domain'
            )
        )

        # 시계열 그래프
        time_series = analysis_results['usage_patterns']['daily_trends']
        fig.add_trace(
            go.Scatter(
                x=list(time_series.keys()),
                y=list(time_series.values()),
                mode='lines+markers',
                name='Daily Requests'
            ),
            row=1, col=1
        )

        # 언어 분포 파이 차트
        lang_dist = analysis_results['summary_statistics']['language_distribution']
        fig.add_trace(
            go.Pie(
                labels=list(lang_dist.keys()),
                values=list(lang_dist.values()),
                name='Languages'
            ),
            row=1, col=2
        )

        # 응답 시간 히스토그램
        response_times = analysis_results['performance_metrics']['response_time_distribution']
        fig.add_trace(
            go.Histogram(
                x=response_times,
                nbinsx=50,
                name='Response Time'
            ),
            row=2, col=1
        )

        # 도메인별 에러율
        error_rates = analysis_results['error_analysis']['by_domain']
        fig.add_trace(
            go.Bar(
                x=list(error_rates.keys()),
                y=list(error_rates.values()),
                name='Error Rate'
            ),
            row=2, col=2
        )

        # 레이아웃 업데이트
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Parser Agent Analytics Dashboard"
        )

        # HTML로 저장
        html_content = fig.to_html(include_plotlyjs='cdn')
        return html_content
```

**검증 기준**:

- [ ] 포괄적인 로그 분석
- [ ] 실시간 인사이트 생성
- [ ] 경영진 대시보드
- [ ] 대화형 시각화

#### SubTask 4.30.4: 파싱 최적화 추천 시스템

**담당자**: 성능 최적화 전문가  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/parser/optimization_recommender.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio

@dataclass
class OptimizationRecommendation:
    category: str  # 'performance', 'accuracy', 'cost', 'scalability'
    priority: str  # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    expected_improvement: Dict[str, Any]
    implementation_effort: str  # 'low', 'medium', 'high'
    estimated_cost: Optional[str]
    implementation_steps: List[str]

class ParsingOptimizationRecommender:
    """파싱 최적화 추천 시스템"""

    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.bottleneck_detector = BottleneckDetector()
        self.optimization_simulator = OptimizationSimulator()

    async def generate_optimization_recommendations(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationRecommendation]:
        """최적화 추천 생성"""

        recommendations = []

        # 1. 성능 최적화 분석
        perf_recommendations = await self._analyze_performance_optimizations(
            current_metrics,
            historical_data
        )
        recommendations.extend(perf_recommendations)

        # 2. 비용 최적화 분석
        cost_recommendations = await self._analyze_cost_optimizations(
            current_metrics,
            constraints
        )
        recommendations.extend(cost_recommendations)

        # 3. 정확도 개선 분석
        accuracy_recommendations = await self._analyze_accuracy_improvements(
            current_metrics
        )
        recommendations.extend(accuracy_recommendations)

        # 4. 확장성 개선 분석
        scalability_recommendations = await self._analyze_scalability_improvements(
            current_metrics,
            historical_data
        )
        recommendations.extend(scalability_recommendations)

        # 우선순위 정렬
        recommendations.sort(
            key=lambda r: self._calculate_priority_score(r),
            reverse=True
        )

        return recommendations

    async def _analyze_performance_optimizations(
        self,
        metrics: Dict[str, Any],
        historical: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """성능 최적화 분석"""

        recommendations = []

        # 캐싱 최적화
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        if cache_hit_rate < 0.7:  # 70% 미만
            recommendations.append(OptimizationRecommendation(
                category='performance',
                priority='high',
                title='Improve Caching Strategy',
                description=f'Current cache hit rate is {cache_hit_rate:.1%}. Implementing intelligent caching could improve performance significantly.',
                expected_improvement={
                    'response_time_reduction': '40-60%',
                    'server_load_reduction': '30-50%',
                    'cost_savings': '$500-1000/month'
                },
                implementation_effort='medium',
                estimated_cost='$2,000-3,000',
                implementation_steps=[
                    'Analyze cache miss patterns',
                    'Implement predictive pre-caching',
                    'Optimize cache key generation',
                    'Add multi-level caching (L1: Memory, L2: Redis, L3: DynamoDB)'
                ]
            ))

        # 병렬 처리 최적화
        cpu_utilization = metrics.get('cpu_utilization', 0)
        if cpu_utilization < 0.5:  # 50% 미만
            recommendations.append(OptimizationRecommendation(
                category='performance',
                priority='medium',
                title='Enhance Parallel Processing',
                description='CPU utilization is below 50%. Better parallelization could improve throughput.',
                expected_improvement={
                    'throughput_increase': '2-3x',
                    'latency_reduction': '30-40%'
                },
                implementation_effort='medium',
                estimated_cost='$1,500-2,500',
                implementation_steps=[
                    'Profile current bottlenecks',
                    'Implement async batch processing',
                    'Optimize thread pool configuration',
                    'Use GPU acceleration for NLP tasks'
                ]
            ))

        # 데이터베이스 쿼리 최적화
        slow_queries = metrics.get('slow_query_count', 0)
        if slow_queries > 10:  # 하루 10개 이상
            recommendations.append(OptimizationRecommendation(
                category='performance',
                priority='high',
                title='Optimize Database Queries',
                description=f'Found {slow_queries} slow queries. Query optimization needed.',
                expected_improvement={
                    'query_time_reduction': '70-90%',
                    'database_load_reduction': '40-60%'
                },
                implementation_effort='low',
                estimated_cost='$500-1,000',
                implementation_steps=[
                    'Add missing indexes',
                    'Optimize N+1 queries',
                    'Implement query result caching',
                    'Use database connection pooling'
                ]
            ))

        return recommendations

    async def _analyze_cost_optimizations(
        self,
        metrics: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> List[OptimizationRecommendation]:
        """비용 최적화 분석"""

        recommendations = []

        # 리소스 사용률 최적화
        resource_utilization = metrics.get('average_resource_utilization', 0)
        if resource_utilization < 0.3:  # 30% 미만
            recommendations.append(OptimizationRecommendation(
                category='cost',
                priority='medium',
                title='Right-size Infrastructure',
                description='Resources are underutilized. Right-sizing could reduce costs.',
                expected_improvement={
                    'cost_reduction': '30-50%',
                    'monthly_savings': '$1,000-2,000'
                },
                implementation_effort='low',
                estimated_cost='$0',
                implementation_steps=[
                    'Analyze usage patterns',
                    'Implement auto-scaling policies',
                    'Use spot instances for batch processing',
                    'Optimize container resource limits'
                ]
            ))

        # API 호출 최적화
        external_api_calls = metrics.get('external_api_calls_per_request', 0)
        if external_api_calls > 3:
            recommendations.append(OptimizationRecommendation(
                category='cost',
                priority='high',
                title='Reduce External API Calls',
                description=f'Average {external_api_calls} API calls per request. Batching could reduce costs.',
                expected_improvement={
                    'api_cost_reduction': '60-80%',
                    'latency_improvement': '20-30%'
                },
                implementation_effort='medium',
                estimated_cost='$1,000-1,500',
                implementation_steps=[
                    'Implement request batching',
                    'Cache API responses',
                    'Use bulk APIs where available',
                    'Implement local fallbacks'
                ]
            ))

        return recommendations

    async def simulate_optimization_impact(
        self,
        recommendation: OptimizationRecommendation,
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """최적화 영향 시뮬레이션"""

        # 시뮬레이션 파라미터 설정
        simulation_params = {
            'duration': '30_days',
            'current_state': current_metrics,
            'optimization': recommendation
        }

        # 시뮬레이션 실행
        simulation_results = await self.optimization_simulator.run(
            simulation_params
        )

        return {
            'projected_metrics': simulation_results['metrics'],
            'cost_benefit_analysis': {
                'implementation_cost': recommendation.estimated_cost,
                'monthly_savings': simulation_results['monthly_savings'],
                'roi_months': simulation_results['roi_months'],
                'break_even_point': simulation_results['break_even_date']
            },
            'risk_assessment': simulation_results['risks'],
            'implementation_timeline': simulation_results['timeline']
        }

    async def create_optimization_roadmap(
        self,
        recommendations: List[OptimizationRecommendation],
        budget: Optional[float] = None,
        timeline: Optional[int] = None  # months
    ) -> Dict[str, Any]:
        """최적화 로드맵 생성"""

        # 제약 조건 고려하여 추천 필터링
        filtered_recommendations = await self._filter_by_constraints(
            recommendations,
            budget,
            timeline
        )

        # 의존성 분석
        dependencies = await self._analyze_dependencies(filtered_recommendations)

        # 실행 순서 결정
        execution_order = await self._determine_execution_order(
            filtered_recommendations,
            dependencies
        )

        # 로드맵 생성
        roadmap = {
            'phases': [],
            'total_cost': 0,
            'total_duration': 0,
            'expected_improvements': {}
        }

        current_month = 0
        for phase_num, recs_in_phase in enumerate(execution_order):
            phase = {
                'phase_number': phase_num + 1,
                'start_month': current_month,
                'duration_months': 3,  # 기본 3개월
                'recommendations': recs_in_phase,
                'cost': sum(self._parse_cost(r.estimated_cost) for r in recs_in_phase),
                'expected_outcomes': await self._aggregate_improvements(recs_in_phase)
            }

            roadmap['phases'].append(phase)
            roadmap['total_cost'] += phase['cost']
            current_month += phase['duration_months']

        roadmap['total_duration'] = current_month
        roadmap['expected_improvements'] = await self._calculate_cumulative_improvements(
            roadmap['phases']
        )

        return roadmap
```

**자동 최적화 실행기**:

```python
class AutoOptimizationExecutor:
    """자동 최적화 실행"""

    def __init__(self):
        self.optimization_engine = OptimizationEngine()
        self.rollback_manager = RollbackManager()
        self.monitoring = OptimizationMonitoring()

    async def execute_optimization(
        self,
        optimization: OptimizationRecommendation,
        auto_rollback: bool = True
    ) -> Dict[str, Any]:
        """최적화 자동 실행"""

        execution_result = {
            'optimization_id': str(uuid.uuid4()),
            'started_at': datetime.now(),
            'status': 'in_progress',
            'steps_completed': [],
            'metrics_before': {},
            'metrics_after': {},
            'rollback_available': auto_rollback
        }

        try:
            # 현재 메트릭 저장
            execution_result['metrics_before'] = await self._capture_current_metrics()

            # 각 단계 실행
            for step in optimization.implementation_steps:
                # 단계 실행
                step_result = await self.optimization_engine.execute_step(
                    step,
                    optimization
                )

                execution_result['steps_completed'].append({
                    'step': step,
                    'result': step_result,
                    'timestamp': datetime.now()
                })

                # 중간 검증
                if not await self._validate_step_result(step_result):
                    if auto_rollback:
                        await self._rollback(execution_result)
                    raise OptimizationError(f"Step failed: {step}")

            # 최종 메트릭 측정
            execution_result['metrics_after'] = await self._capture_current_metrics()

            # 성공 여부 판단
            improvement = self._calculate_improvement(
                execution_result['metrics_before'],
                execution_result['metrics_after']
            )

            if improvement >= optimization.expected_improvement:
                execution_result['status'] = 'success'
            else:
                execution_result['status'] = 'partial_success'

        except Exception as e:
            execution_result['status'] = 'failed'
            execution_result['error'] = str(e)

            if auto_rollback:
                await self._rollback(execution_result)

        execution_result['completed_at'] = datetime.now()
        return execution_result
```

**검증 기준**:

- [ ] 포괄적인 최적화 분석
- [ ] 실행 가능한 추천
- [ ] 영향 시뮬레이션
- [ ] 자동 최적화 실행

---

이로써 Parser Agent의 모든 Task (4.21-4.30)가 완성되었습니다!

Parser Agent는 다음과 같은 핵심 기능을 갖추게 되었습니다:

1. **핵심 파싱 기능**: 자연어 요구사항을 구조화된 데이터로 변환
2. **고급 분석**: 의존성, 충돌, 추적성 분석
3. **도메인 특화**: 15개 도메인별 전문 파싱
4. **다국어 지원**: 15개 언어 요구사항 파싱
5. **성능 최적화**: 병렬 처리, 캐싱, 증분 파싱
6. **통합 인터페이스**: 다른 에이전트와의 표준화된 통신
7. **모니터링**: 실시간 메트릭 및 로깅
8. **자동 개선**: 정확도 분석 및 자동 최적화

이제 Phase 4의 다음 에이전트로 진행할 준비가 되었습니다!
