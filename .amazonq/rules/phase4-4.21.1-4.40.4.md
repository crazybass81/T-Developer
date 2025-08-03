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

---

# Phase 4: 9개 핵심 에이전트 구현 - Component Decision Agent (Tasks 4.31-4.40)

## 4. Component Decision Agent (컴포넌트 결정 에이전트)

### Task 4.31: Component Decision Agent 코어 구현

#### SubTask 4.31.1: Component Decision Agent 기본 아키텍처

**담당자**: 시니어 소프트웨어 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision_agent.py
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

@dataclass
class ComponentType(Enum):
    UI_COMPONENT = "ui_component"
    BACKEND_SERVICE = "backend_service"
    DATA_MODEL = "data_model"
    API_ENDPOINT = "api_endpoint"
    UTILITY_FUNCTION = "utility_function"
    MIDDLEWARE = "middleware"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"

@dataclass
class ComponentDecision:
    id: str
    name: str
    type: ComponentType
    description: str
    requirements: List[str]  # 관련 요구사항 ID
    dependencies: List[str]  # 다른 컴포넌트 ID
    interfaces: Dict[str, Any]
    properties: Dict[str, Any]
    constraints: List[str]
    reusability_score: float  # 0-1
    complexity_score: float   # 0-1
    priority: int            # 1-10
    implementation_notes: str
    estimated_effort: int    # story points
    technology_stack: List[str]

@dataclass
class ComponentArchitecture:
    components: List[ComponentDecision]
    relationships: List[Dict[str, Any]]
    layers: Dict[str, List[str]]  # layer_name -> component_ids
    patterns: List[str]  # 적용된 디자인 패턴
    constraints: List[str]
    quality_attributes: Dict[str, Any]

class ComponentDecisionAgent:
    """파싱된 요구사항을 기반으로 컴포넌트 아키텍처 결정"""

    def __init__(self):
        # 주 결정 엔진 - Claude 3 (아키텍처 설계에 최적화)
        self.decision_engine = Agent(
            name="Component-Architect",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert software architect specializing in component design",
            instructions=[
                "Analyze parsed requirements and design component architecture",
                "Identify necessary UI components, services, and data models",
                "Apply appropriate design patterns and best practices",
                "Consider reusability, scalability, and maintainability",
                "Define clear interfaces and contracts between components",
                "Estimate complexity and implementation effort"
            ],
            temperature=0.3  # 일관된 아키텍처 결정
        )

        # 패턴 분석기 - GPT-4 (디자인 패턴 적용)
        self.pattern_analyzer = Agent(
            name="Pattern-Specialist",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Design pattern expert",
            instructions=[
                "Identify applicable design patterns for components",
                "Suggest architectural patterns (MVC, MVVM, etc.)",
                "Recommend integration patterns",
                "Apply SOLID principles"
            ],
            temperature=0.2
        )

        # 전문 분석기들
        self.ui_component_analyzer = UIComponentAnalyzer()
        self.service_designer = ServiceDesigner()
        self.data_model_designer = DataModelDesigner()
        self.dependency_analyzer = ComponentDependencyAnalyzer()
        self.reusability_evaluator = ReusabilityEvaluator()

        # 컴포넌트 라이브러리
        self.component_library = ComponentLibrary()

        # 아키텍처 검증기
        self.architecture_validator = ArchitectureValidator()

    async def decide_components(
        self,
        parsed_requirements: ParsedProject,
        ui_framework: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> ComponentArchitecture:
        """요구사항을 기반으로 컴포넌트 아키텍처 결정"""

        # 1. 요구사항 분석 및 그룹화
        requirement_groups = await self._analyze_and_group_requirements(
            parsed_requirements
        )

        # 2. 컴포넌트 식별 (병렬 처리)
        identification_tasks = [
            self._identify_ui_components(requirement_groups, ui_framework),
            self._identify_backend_services(requirement_groups),
            self._identify_data_models(requirement_groups),
            self._identify_api_endpoints(requirement_groups),
            self._identify_utilities(requirement_groups),
            self._identify_integrations(requirement_groups)
        ]

        component_lists = await asyncio.gather(*identification_tasks)
        all_components = [c for sublist in component_lists for c in sublist]

        # 3. 컴포넌트 관계 분석
        relationships = await self._analyze_component_relationships(
            all_components
        )

        # 4. 아키텍처 레이어 구성
        layers = await self._organize_architectural_layers(
            all_components
        )

        # 5. 디자인 패턴 적용
        patterns = await self._apply_design_patterns(
            all_components,
            relationships
        )

        # 6. 컴포넌트 최적화
        optimized_components = await self._optimize_components(
            all_components,
            relationships
        )

        # 7. 아키텍처 검증
        architecture = ComponentArchitecture(
            components=optimized_components,
            relationships=relationships,
            layers=layers,
            patterns=patterns,
            constraints=parsed_requirements.constraints,
            quality_attributes=await self._define_quality_attributes(
                parsed_requirements
            )
        )

        validation_result = await self.architecture_validator.validate(
            architecture
        )

        if not validation_result.is_valid:
            # 문제 해결 및 재설계
            architecture = await self._resolve_architecture_issues(
                architecture,
                validation_result.issues
            )

        return architecture

    async def _analyze_and_group_requirements(
        self,
        parsed_requirements: ParsedProject
    ) -> Dict[str, List[ParsedRequirement]]:
        """요구사항 분석 및 그룹화"""

        groups = {
            'authentication': [],
            'user_management': [],
            'data_processing': [],
            'reporting': [],
            'integration': [],
            'ui_features': [],
            'business_logic': [],
            'infrastructure': []
        }

        # 요구사항을 카테고리별로 그룹화
        for req in parsed_requirements.functional_requirements:
            category = await self._categorize_requirement(req)
            if category in groups:
                groups[category].append(req)
            else:
                groups['business_logic'].append(req)

        return groups
```

**검증 기준**:

- [ ] 요구사항 기반 컴포넌트 식별
- [ ] 컴포넌트 타입별 분류
- [ ] 의존성 관계 분석
- [ ] 아키텍처 검증 시스템

#### SubTask 4.31.2: UI 컴포넌트 분석기

**담당자**: UI/UX 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/ui_analyzer.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class UIComponentPattern(Enum):
    ATOMIC = "atomic"          # 버튼, 입력 필드 등
    MOLECULAR = "molecular"    # 폼, 카드 등
    ORGANISM = "organism"      # 헤더, 사이드바 등
    TEMPLATE = "template"      # 페이지 레이아웃
    PAGE = "page"             # 완전한 페이지

@dataclass
class UIComponent:
    id: str
    name: str
    pattern: UIComponentPattern
    description: str
    props: Dict[str, Any]
    state: Dict[str, Any]
    events: List[str]
    children: List[str]  # 자식 컴포넌트 ID
    styling: Dict[str, Any]
    accessibility: Dict[str, Any]
    responsive: Dict[str, List[str]]  # breakpoint -> styles
    data_bindings: List[Dict[str, Any]]
    animations: List[Dict[str, Any]]

class UIComponentAnalyzer:
    """UI 컴포넌트 분석 및 설계"""

    def __init__(self):
        self.component_patterns = self._load_component_patterns()
        self.ui_best_practices = self._load_ui_best_practices()
        self.accessibility_checker = AccessibilityChecker()

    async def analyze_ui_requirements(
        self,
        requirements: List[ParsedRequirement],
        ui_framework: str
    ) -> List[UIComponent]:
        """UI 요구사항 분석 및 컴포넌트 도출"""

        ui_components = []

        # 1. UI 관련 요구사항 추출
        ui_requirements = await self._extract_ui_requirements(requirements)

        # 2. 화면 단위 분석
        screens = await self._identify_screens(ui_requirements)

        # 3. 각 화면별 컴포넌트 도출
        for screen in screens:
            # 페이지 컴포넌트
            page_component = await self._create_page_component(screen)
            ui_components.append(page_component)

            # 템플릿 컴포넌트
            template = await self._create_template_component(screen)
            ui_components.append(template)

            # 유기체 컴포넌트 (헤더, 네비게이션 등)
            organisms = await self._create_organism_components(screen)
            ui_components.extend(organisms)

            # 분자 컴포넌트 (폼, 카드 등)
            molecules = await self._create_molecular_components(screen)
            ui_components.extend(molecules)

            # 원자 컴포넌트 (버튼, 입력 필드 등)
            atoms = await self._create_atomic_components(screen)
            ui_components.extend(atoms)

        # 4. 컴포넌트 최적화
        optimized_components = await self._optimize_ui_components(
            ui_components,
            ui_framework
        )

        # 5. 접근성 검증
        for component in optimized_components:
            component.accessibility = await self.accessibility_checker.check(
                component
            )

        return optimized_components

    async def _create_atomic_components(
        self,
        screen: Dict[str, Any]
    ) -> List[UIComponent]:
        """원자 컴포넌트 생성"""

        atomic_components = []

        # 버튼 컴포넌트
        if 'buttons' in screen:
            for button in screen['buttons']:
                component = UIComponent(
                    id=f"btn_{button['action']}",
                    name=f"{button['label']}Button",
                    pattern=UIComponentPattern.ATOMIC,
                    description=f"Button for {button['action']}",
                    props={
                        'label': button['label'],
                        'variant': button.get('variant', 'primary'),
                        'size': button.get('size', 'medium'),
                        'disabled': False,
                        'loading': False,
                        'icon': button.get('icon'),
                        'onClick': f"handle{button['action'].title()}"
                    },
                    state={
                        'isHovered': False,
                        'isFocused': False,
                        'isPressed': False
                    },
                    events=['click', 'hover', 'focus', 'blur'],
                    children=[],
                    styling={
                        'base': 'px-4 py-2 rounded-md font-medium',
                        'variants': {
                            'primary': 'bg-blue-600 text-white hover:bg-blue-700',
                            'secondary': 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                        }
                    },
                    accessibility={
                        'role': 'button',
                        'aria-label': button['label'],
                        'tabIndex': 0
                    },
                    responsive={
                        'sm': ['text-sm', 'px-3', 'py-1'],
                        'md': ['text-base', 'px-4', 'py-2'],
                        'lg': ['text-lg', 'px-5', 'py-3']
                    },
                    data_bindings=[],
                    animations=[{
                        'trigger': 'hover',
                        'animation': 'scale-105',
                        'duration': 200
                    }]
                )
                atomic_components.append(component)

        # 입력 필드 컴포넌트
        if 'inputs' in screen:
            for input_field in screen['inputs']:
                component = UIComponent(
                    id=f"input_{input_field['name']}",
                    name=f"{input_field['name'].title()}Input",
                    pattern=UIComponentPattern.ATOMIC,
                    description=f"Input field for {input_field['label']}",
                    props={
                        'type': input_field.get('type', 'text'),
                        'placeholder': input_field.get('placeholder', ''),
                        'label': input_field['label'],
                        'required': input_field.get('required', False),
                        'validation': input_field.get('validation', {}),
                        'value': '',
                        'error': '',
                        'helperText': input_field.get('helperText', '')
                    },
                    state={
                        'isFocused': False,
                        'isDirty': False,
                        'isValid': True,
                        'isTouched': False
                    },
                    events=['change', 'focus', 'blur', 'input'],
                    children=[],
                    styling={
                        'container': 'mb-4',
                        'label': 'block text-sm font-medium mb-1',
                        'input': 'w-full px-3 py-2 border rounded-md',
                        'error': 'text-red-600 text-sm mt-1'
                    },
                    accessibility={
                        'role': 'textbox',
                        'aria-label': input_field['label'],
                        'aria-required': input_field.get('required', False),
                        'aria-invalid': False
                    },
                    responsive={
                        'sm': ['text-sm'],
                        'md': ['text-base'],
                        'lg': ['text-lg']
                    },
                    data_bindings=[{
                        'model': input_field['name'],
                        'updateOn': 'change'
                    }],
                    animations=[]
                )
                atomic_components.append(component)

        return atomic_components
```

**검증 기준**:

- [ ] Atomic Design 패턴 적용
- [ ] 컴포넌트 재사용성 평가
- [ ] 접근성 표준 준수
- [ ] 반응형 디자인 지원

#### SubTask 4.31.3: 백엔드 서비스 설계기

**담당자**: 백엔드 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/service_designer.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class ServiceType(Enum):
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    BACKGROUND_JOB = "background_job"
    SCHEDULED_TASK = "scheduled_task"

@dataclass
class ServiceComponent:
    id: str
    name: str
    type: ServiceType
    description: str
    endpoints: List[Dict[str, Any]]
    data_models: List[str]  # 관련 데이터 모델 ID
    dependencies: List[str]  # 다른 서비스 ID
    authentication: Dict[str, Any]
    authorization: Dict[str, Any]
    rate_limiting: Dict[str, Any]
    caching: Dict[str, Any]
    error_handling: Dict[str, Any]
    monitoring: Dict[str, Any]
    scalability: Dict[str, Any]

class ServiceDesigner:
    """백엔드 서비스 설계"""

    def __init__(self):
        self.service_patterns = self._load_service_patterns()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_optimizer = PerformanceOptimizer()

    async def design_backend_services(
        self,
        requirements: List[ParsedRequirement],
        data_models: List[DataModel]
    ) -> List[ServiceComponent]:
        """백엔드 서비스 설계"""

        services = []

        # 1. 서비스 경계 식별
        service_boundaries = await self._identify_service_boundaries(
            requirements
        )

        # 2. 각 서비스별 설계
        for boundary in service_boundaries:
            # 서비스 타입 결정
            service_type = await self._determine_service_type(boundary)

            # 엔드포인트 설계
            endpoints = await self._design_endpoints(boundary, service_type)

            # 서비스 컴포넌트 생성
            service = ServiceComponent(
                id=f"svc_{boundary['name']}",
                name=f"{boundary['name'].title()}Service",
                type=service_type,
                description=boundary['description'],
                endpoints=endpoints,
                data_models=boundary['data_models'],
                dependencies=boundary['dependencies'],
                authentication=await self._design_authentication(boundary),
                authorization=await self._design_authorization(boundary),
                rate_limiting=await self._design_rate_limiting(boundary),
                caching=await self._design_caching(boundary),
                error_handling=await self._design_error_handling(boundary),
                monitoring=await self._design_monitoring(boundary),
                scalability=await self._design_scalability(boundary)
            )

            services.append(service)

        # 3. 서비스 간 통신 설계
        communication_patterns = await self._design_service_communication(
            services
        )

        # 4. API Gateway 설계
        if len(services) > 3:  # 마이크로서비스 아키텍처
            api_gateway = await self._design_api_gateway(services)
            services.append(api_gateway)

        # 5. 보안 강화
        for service in services:
            service.security = await self.security_analyzer.enhance_security(
                service
            )

        return services

    async def _design_endpoints(
        self,
        boundary: Dict[str, Any],
        service_type: ServiceType
    ) -> List[Dict[str, Any]]:
        """서비스 엔드포인트 설계"""

        endpoints = []

        if service_type == ServiceType.REST_API:
            # RESTful 엔드포인트
            for operation in boundary['operations']:
                endpoint = {
                    'path': f"/api/v1/{boundary['resource']}/{operation['path']}",
                    'method': operation['method'],
                    'description': operation['description'],
                    'request': {
                        'params': operation.get('params', []),
                        'query': operation.get('query', []),
                        'body': operation.get('body', {}),
                        'headers': operation.get('headers', [])
                    },
                    'response': {
                        'success': {
                            'status': operation.get('success_status', 200),
                            'schema': operation.get('response_schema', {})
                        },
                        'errors': operation.get('errors', [])
                    },
                    'middleware': [
                        'authentication',
                        'authorization',
                        'validation',
                        'rate_limiting'
                    ]
                }
                endpoints.append(endpoint)

        elif service_type == ServiceType.GRAPHQL:
            # GraphQL 스키마
            endpoint = {
                'path': '/graphql',
                'schema': await self._generate_graphql_schema(boundary),
                'resolvers': await self._generate_resolvers(boundary),
                'subscriptions': boundary.get('subscriptions', [])
            }
            endpoints.append(endpoint)

        elif service_type == ServiceType.WEBSOCKET:
            # WebSocket 이벤트
            endpoint = {
                'path': f"/ws/{boundary['resource']}",
                'events': boundary.get('events', []),
                'rooms': boundary.get('rooms', []),
                'authentication': 'token-based'
            }
            endpoints.append(endpoint)

        return endpoints

    async def _design_caching(
        self,
        boundary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """캐싱 전략 설계"""

        caching_strategy = {
            'enabled': True,
            'provider': 'redis',
            'strategies': []
        }

        # 읽기 중심 작업에 캐싱 적용
        if boundary.get('read_heavy', False):
            caching_strategy['strategies'].append({
                'type': 'query_result_cache',
                'ttl': 300,  # 5분
                'invalidation': 'on_write',
                'key_pattern': f"{boundary['name']}:{{entity_id}}"
            })

        # 자주 접근되는 데이터
        if boundary.get('hot_data', []):
            for hot_data in boundary['hot_data']:
                caching_strategy['strategies'].append({
                    'type': 'data_cache',
                    'data': hot_data,
                    'ttl': 3600,  # 1시간
                    'preload': True
                })

        # API 응답 캐싱
        if boundary.get('cacheable_endpoints', []):
            caching_strategy['strategies'].append({
                'type': 'response_cache',
                'endpoints': boundary['cacheable_endpoints'],
                'ttl': 60,
                'vary_by': ['user_id', 'query_params']
            })

        return caching_strategy
```

**검증 기준**:

- [ ] 서비스 경계 명확성
- [ ] RESTful/GraphQL 설계
- [ ] 보안 요구사항 충족
- [ ] 확장성 고려

#### SubTask 4.31.4: 데이터 모델 설계기

**담당자**: 데이터 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/data_model_designer.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class DataType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    UUID = "uuid"
    JSON = "json"

@dataclass
class DataField:
    name: str
    type: DataType
    required: bool
    unique: bool = False
    indexed: bool = False
    default: Any = None
    validation: Dict[str, Any] = None
    description: str = ""
    references: Optional[str] = None  # Foreign key reference

@dataclass
class DataModel:
    id: str
    name: str
    description: str
    fields: List[DataField]
    indexes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    methods: List[Dict[str, Any]]  # 비즈니스 로직 메서드
    hooks: Dict[str, List[str]]  # lifecycle hooks
    audit_fields: bool = True
    soft_delete: bool = True
    versioning: bool = False

class DataModelDesigner:
    """데이터 모델 설계"""

    def __init__(self):
        self.normalization_analyzer = NormalizationAnalyzer()
        self.relationship_mapper = RelationshipMapper()
        self.index_optimizer = IndexOptimizer()

    async def design_data_models(
        self,
        requirements: List[ParsedRequirement],
        domain_models: List[Dict[str, Any]]
    ) -> List[DataModel]:
        """데이터 모델 설계"""

        data_models = []

        # 1. 엔티티 식별
        entities = await self._identify_entities(requirements, domain_models)

        # 2. 각 엔티티별 모델 설계
        for entity in entities:
            # 필드 정의
            fields = await self._design_fields(entity)

            # 관계 설계
            relationships = await self._design_relationships(entity, entities)

            # 인덱스 설계
            indexes = await self._design_indexes(entity, fields)

            # 제약조건 설계
            constraints = await self._design_constraints(entity, fields)

            # 비즈니스 메서드 설계
            methods = await self._design_business_methods(entity)

            # 데이터 모델 생성
            model = DataModel(
                id=f"model_{entity['name'].lower()}",
                name=entity['name'],
                description=entity['description'],
                fields=fields,
                indexes=indexes,
                relationships=relationships,
                constraints=constraints,
                methods=methods,
                hooks=await self._design_lifecycle_hooks(entity),
                audit_fields=entity.get('auditable', True),
                soft_delete=entity.get('soft_delete', True),
                versioning=entity.get('versioning', False)
            )

            data_models.append(model)

        # 3. 정규화 검증
        normalization_result = await self.normalization_analyzer.analyze(
            data_models
        )

        if not normalization_result.is_normalized:
            data_models = await self._apply_normalization(
                data_models,
                normalization_result.suggestions
            )

        # 4. 성능 최적화
        for model in data_models:
            model.indexes = await self.index_optimizer.optimize_indexes(
                model
            )

        return data_models

    async def _design_fields(
        self,
        entity: Dict[str, Any]
    ) -> List[DataField]:
        """엔티티 필드 설계"""

        fields = []

        # ID 필드 (기본)
        fields.append(DataField(
            name='id',
            type=DataType.UUID,
            required=True,
            unique=True,
            indexed=True,
            description=f"Unique identifier for {entity['name']}"
        ))

        # 엔티티 속성 필드
        for attribute in entity.get('attributes', []):
            field = DataField(
                name=attribute['name'],
                type=self._map_data_type(attribute['type']),
                required=attribute.get('required', False),
                unique=attribute.get('unique', False),
                indexed=attribute.get('indexed', False),
                default=attribute.get('default'),
                validation=self._create_validation_rules(attribute),
                description=attribute.get('description', ''),
                references=attribute.get('references')
            )
            fields.append(field)

        # 감사 필드 (audit fields)
        if entity.get('auditable', True):
            audit_fields = [
                DataField(
                    name='created_at',
                    type=DataType.DATETIME,
                    required=True,
                    indexed=True,
                    description='Creation timestamp'
                ),
                DataField(
                    name='updated_at',
                    type=DataType.DATETIME,
                    required=True,
                    indexed=True,
                    description='Last update timestamp'
                ),
                DataField(
                    name='created_by',
                    type=DataType.STRING,
                    required=False,
                    description='User who created the record'
                ),
                DataField(
                    name='updated_by',
                    type=DataType.STRING,
                    required=False,
                    description='User who last updated the record'
                )
            ]
            fields.extend(audit_fields)

        # Soft delete 필드
        if entity.get('soft_delete', True):
            fields.append(DataField(
                name='deleted_at',
                type=DataType.DATETIME,
                required=False,
                indexed=True,
                description='Soft deletion timestamp'
            ))

        return fields

    def _create_validation_rules(
        self,
        attribute: Dict[str, Any]
    ) -> Dict[str, Any]:
        """필드 검증 규칙 생성"""

        rules = {}

        # 문자열 검증
        if attribute['type'] == 'string':
            if 'min_length' in attribute:
                rules['minLength'] = attribute['min_length']
            if 'max_length' in attribute:
                rules['maxLength'] = attribute['max_length']
            if 'pattern' in attribute:
                rules['pattern'] = attribute['pattern']
            if 'format' in attribute:
                rules['format'] = attribute['format']  # email, url, etc.

        # 숫자 검증
        elif attribute['type'] in ['number', 'integer']:
            if 'min' in attribute:
                rules['minimum'] = attribute['min']
            if 'max' in attribute:
                rules['maximum'] = attribute['max']
            if 'multiple_of' in attribute:
                rules['multipleOf'] = attribute['multiple_of']

        # 배열 검증
        elif attribute['type'] == 'array':
            if 'min_items' in attribute:
                rules['minItems'] = attribute['min_items']
            if 'max_items' in attribute:
                rules['maxItems'] = attribute['max_items']
            if 'unique_items' in attribute:
                rules['uniqueItems'] = attribute['unique_items']

        # 커스텀 검증
        if 'custom_validation' in attribute:
            rules['custom'] = attribute['custom_validation']

        return rules
```

**검증 기준**:

- [ ] 데이터 정규화 적용
- [ ] 인덱스 최적화
- [ ] 관계 무결성 보장
- [ ] 확장 가능한 스키마

### Task 4.32: 컴포넌트 분석 시스템

#### SubTask 4.32.1: 요구사항-컴포넌트 매핑 시스템

**담당자**: 시스템 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/requirement_mapper.py
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@dataclass
class RequirementComponentMapping:
    requirement_id: str
    component_ids: List[str]
    mapping_type: str  # direct, derived, implicit
    confidence: float  # 0-1
    rationale: str
    coverage: float  # 요구사항 충족도 0-1

class RequirementComponentMapper:
    """요구사항과 컴포넌트 간 매핑"""

    def __init__(self):
        self.nlp_analyzer = NLPAnalyzer()
        self.similarity_calculator = SimilarityCalculator()
        self.coverage_analyzer = CoverageAnalyzer()
        self.mapping_validator = MappingValidator()

    async def map_requirements_to_components(
        self,
        requirements: List[ParsedRequirement],
        components: List[ComponentDecision]
    ) -> Dict[str, Any]:
        """요구사항을 컴포넌트에 매핑"""

        mappings = []
        unmapped_requirements = []

        # 1. 직접 매핑 (명시적 관계)
        direct_mappings = await self._create_direct_mappings(
            requirements,
            components
        )
        mappings.extend(direct_mappings)

        # 2. 파생 매핑 (간접적 관계)
        derived_mappings = await self._create_derived_mappings(
            requirements,
            components,
            direct_mappings
        )
        mappings.extend(derived_mappings)

        # 3. 암시적 매핑 (유사성 기반)
        implicit_mappings = await self._create_implicit_mappings(
            requirements,
            components,
            existing_mappings=mappings
        )
        mappings.extend(implicit_mappings)

        # 4. 매핑 검증
        validated_mappings = await self._validate_mappings(mappings)

        # 5. 커버리지 분석
        coverage_report = await self.coverage_analyzer.analyze(
            requirements,
            components,
            validated_mappings
        )

        # 6. 매핑되지 않은 요구사항 식별
        mapped_req_ids = set(m.requirement_id for m in validated_mappings)
        unmapped_requirements = [
            req for req in requirements
            if req.id not in mapped_req_ids
        ]

        return {
            'mappings': validated_mappings,
            'coverage_report': coverage_report,
            'unmapped_requirements': unmapped_requirements,
            'mapping_quality_score': await self._calculate_mapping_quality(
                validated_mappings
            ),
            'recommendations': await self._generate_recommendations(
                unmapped_requirements,
                coverage_report
            )
        }

    async def _create_direct_mappings(
        self,
        requirements: List[ParsedRequirement],
        components: List[ComponentDecision]
    ) -> List[RequirementComponentMapping]:
        """직접적인 요구사항-컴포넌트 매핑"""

        direct_mappings = []

        for req in requirements:
            # 컴포넌트에서 직접 참조하는 요구사항 찾기
            matching_components = [
                comp for comp in components
                if req.id in comp.requirements
            ]

            if matching_components:
                mapping = RequirementComponentMapping(
                    requirement_id=req.id,
                    component_ids=[comp.id for comp in matching_components],
                    mapping_type='direct',
                    confidence=1.0,
                    rationale=f"Component explicitly implements requirement {req.id}",
                    coverage=1.0
                )
                direct_mappings.append(mapping)

        return direct_mappings

    async def _create_implicit_mappings(
        self,
        requirements: List[ParsedRequirement],
        components: List[ComponentDecision],
        existing_mappings: List[RequirementComponentMapping]
    ) -> List[RequirementComponentMapping]:
        """유사성 기반 암시적 매핑"""

        implicit_mappings = []

        # 이미 매핑된 요구사항 제외
        mapped_req_ids = set(m.requirement_id for m in existing_mappings)
        unmapped_reqs = [r for r in requirements if r.id not in mapped_req_ids]

        if not unmapped_reqs:
            return implicit_mappings

        # 텍스트 벡터화
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )

        # 요구사항 텍스트
        req_texts = [
            f"{req.description} {' '.join(req.acceptance_criteria)}"
            for req in unmapped_reqs
        ]

        # 컴포넌트 텍스트
        comp_texts = [
            f"{comp.name} {comp.description} {comp.implementation_notes}"
            for comp in components
        ]

        # 벡터화 및 유사도 계산
        all_texts = req_texts + comp_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        req_vectors = tfidf_matrix[:len(req_texts)]
        comp_vectors = tfidf_matrix[len(req_texts):]

        # 코사인 유사도 계산
        similarity_matrix = cosine_similarity(req_vectors, comp_vectors)

        # 임계값 이상의 유사도를 가진 매핑 생성
        threshold = 0.3
        for i, req in enumerate(unmapped_reqs):
            similar_components = []

            for j, comp in enumerate(components):
                similarity = similarity_matrix[i, j]
                if similarity > threshold:
                    similar_components.append((comp.id, similarity))

            if similar_components:
                # 유사도 순으로 정렬
                similar_components.sort(key=lambda x: x[1], reverse=True)

                mapping = RequirementComponentMapping(
                    requirement_id=req.id,
                    component_ids=[comp_id for comp_id, _ in similar_components[:3]],
                    mapping_type='implicit',
                    confidence=similar_components[0][1],  # 최고 유사도
                    rationale=f"Semantic similarity detected (score: {similar_components[0][1]:.2f})",
                    coverage=min(similar_components[0][1], 0.8)  # 암시적 매핑은 최대 80% 커버리지
                )
                implicit_mappings.append(mapping)

        return implicit_mappings
```

**검증 기준**:

- [ ] 요구사항 100% 추적성
- [ ] 매핑 정확도 검증
- [ ] 커버리지 분석 완료
- [ ] 갭 분석 및 권고사항

#### SubTask 4.32.2: 컴포넌트 복잡도 분석기

**담당자**: 소프트웨어 메트릭 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/complexity_analyzer.py
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

@dataclass
class ComplexityMetrics:
    cyclomatic_complexity: int
    cognitive_complexity: int
    structural_complexity: float
    data_complexity: float
    interface_complexity: float
    total_complexity_score: float
    complexity_level: str  # low, medium, high, very_high
    risk_factors: List[str]
    recommendations: List[str]

class ComponentComplexityAnalyzer:
    """컴포넌트 복잡도 분석"""

    def __init__(self):
        self.complexity_calculators = {
            'cyclomatic': CyclomaticComplexityCalculator(),
            'cognitive': CognitiveComplexityCalculator(),
            'structural': StructuralComplexityCalculator(),
            'data': DataComplexityCalculator(),
            'interface': InterfaceComplexityCalculator()
        }
        self.risk_assessor = ComplexityRiskAssessor()

    async def analyze_component_complexity(
        self,
        component: ComponentDecision
    ) -> ComplexityMetrics:
        """컴포넌트 복잡도 종합 분석"""

        # 1. 순환 복잡도 계산
        cyclomatic = await self._calculate_cyclomatic_complexity(component)

        # 2. 인지 복잡도 계산
        cognitive = await self._calculate_cognitive_complexity(component)

        # 3. 구조적 복잡도 계산
        structural = await self._calculate_structural_complexity(component)

        # 4. 데이터 복잡도 계산
        data = await self._calculate_data_complexity(component)

        # 5. 인터페이스 복잡도 계산
        interface = await self._calculate_interface_complexity(component)

        # 6. 종합 점수 계산
        total_score = self._calculate_total_complexity_score({
            'cyclomatic': cyclomatic,
            'cognitive': cognitive,
            'structural': structural,
            'data': data,
            'interface': interface
        })

        # 7. 복잡도 수준 결정
        complexity_level = self._determine_complexity_level(total_score)

        # 8. 위험 요소 식별
        risk_factors = await self.risk_assessor.identify_risks(
            component,
            total_score
        )

        # 9. 개선 권고사항 생성
        recommendations = await self._generate_recommendations(
            component,
            complexity_level,
            risk_factors
        )

        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            structural_complexity=structural,
            data_complexity=data,
            interface_complexity=interface,
            total_complexity_score=total_score,
            complexity_level=complexity_level,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

    async def _calculate_cyclomatic_complexity(
        self,
        component: ComponentDecision
    ) -> int:
        """순환 복잡도 계산"""

        complexity = 1  # 기본값

        # 조건문 수 계산
        if component.type == ComponentType.UI_COMPONENT:
            # UI 컴포넌트의 조건부 렌더링
            complexity += len(component.properties.get('conditionals', []))
            complexity += len(component.properties.get('event_handlers', []))

        elif component.type == ComponentType.BACKEND_SERVICE:
            # 백엔드 서비스의 분기 로직
            for endpoint in component.interfaces.get('endpoints', []):
                complexity += endpoint.get('branch_count', 0)
                complexity += len(endpoint.get('validations', []))

        # 의존성에 따른 복잡도 증가
        complexity += len(component.dependencies) // 3

        return complexity

    async def _calculate_data_complexity(
        self,
        component: ComponentDecision
    ) -> float:
        """데이터 복잡도 계산"""

        complexity = 0.0

        # 상태 관리 복잡도
        if component.type == ComponentType.UI_COMPONENT:
            state_count = len(component.properties.get('state', {}))
            prop_count = len(component.properties.get('props', {}))

            # 상태와 props의 조합 복잡도
            complexity += math.log(state_count + 1) * 0.5
            complexity += math.log(prop_count + 1) * 0.3

        # 데이터 모델 복잡도
        elif component.type == ComponentType.DATA_MODEL:
            field_count = len(component.properties.get('fields', []))
            relation_count = len(component.properties.get('relationships', []))

            complexity += field_count * 0.1
            complexity += relation_count * 0.3

            # 중첩 구조 복잡도
            for field in component.properties.get('fields', []):
                if field.get('type') in ['object', 'array']:
                    complexity += 0.5

        # 데이터 변환 복잡도
        transformation_count = len(
            component.properties.get('transformations', [])
        )
        complexity += transformation_count * 0.2

        return round(complexity, 2)

    def _calculate_total_complexity_score(
        self,
        metrics: Dict[str, float]
    ) -> float:
        """종합 복잡도 점수 계산"""

        # 가중치 정의
        weights = {
            'cyclomatic': 0.25,
            'cognitive': 0.25,
            'structural': 0.20,
            'data': 0.15,
            'interface': 0.15
        }

        # 정규화 및 가중 합산
        normalized_scores = {}

        # 각 메트릭 정규화 (0-10 스케일)
        normalized_scores['cyclomatic'] = min(metrics['cyclomatic'] / 10, 10)
        normalized_scores['cognitive'] = min(metrics['cognitive'] / 20, 10)
        normalized_scores['structural'] = min(metrics['structural'], 10)
        normalized_scores['data'] = min(metrics['data'], 10)
        normalized_scores['interface'] = min(metrics['interface'], 10)

        # 가중 합산
        total_score = sum(
            normalized_scores[key] * weights[key]
            for key in weights
        )

        return round(total_score, 2)

    def _determine_complexity_level(self, score: float) -> str:
        """복잡도 수준 결정"""

        if score < 3:
            return 'low'
        elif score < 5:
            return 'medium'
        elif score < 7:
            return 'high'
        else:
            return 'very_high'
```

**검증 기준**:

- [ ] 다차원 복잡도 분석
- [ ] 위험 요소 식별
- [ ] 개선 권고사항 제공
- [ ] 메트릭 기반 평가

#### SubTask 4.32.3: 컴포넌트 품질 평가기

**담당자**: 품질 보증 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/quality_evaluator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class QualityMetrics:
    maintainability: float  # 0-100
    reusability: float     # 0-100
    testability: float     # 0-100
    modularity: float      # 0-100
    reliability: float     # 0-100
    security: float        # 0-100
    performance: float     # 0-100
    usability: float       # 0-100
    overall_quality: float # 0-100
    quality_grade: str     # A, B, C, D, F
    issues: List[Dict[str, Any]]
    improvements: List[Dict[str, Any]]

class ComponentQualityEvaluator:
    """컴포넌트 품질 평가"""

    def __init__(self):
        self.quality_checkers = {
            'maintainability': MaintainabilityChecker(),
            'reusability': ReusabilityChecker(),
            'testability': TestabilityChecker(),
            'modularity': ModularityChecker(),
            'reliability': ReliabilityChecker(),
            'security': SecurityChecker(),
            'performance': PerformanceChecker(),
            'usability': UsabilityChecker()
        }
        self.quality_rules = QualityRules()
        self.benchmarks = QualityBenchmarks()

    async def evaluate_component_quality(
        self,
        component: ComponentDecision,
        context: Optional[Dict[str, Any]] = None
    ) -> QualityMetrics:
        """컴포넌트 품질 종합 평가"""

        # 1. 유지보수성 평가
        maintainability = await self._evaluate_maintainability(component)

        # 2. 재사용성 평가
        reusability = await self._evaluate_reusability(component)

        # 3. 테스트 가능성 평가
        testability = await self._evaluate_testability(component)

        # 4. 모듈성 평가
        modularity = await self._evaluate_modularity(component)

        # 5. 신뢰성 평가
        reliability = await self._evaluate_reliability(component)

        # 6. 보안성 평가
        security = await self._evaluate_security(component)

        # 7. 성능 평가
        performance = await self._evaluate_performance(component)

        # 8. 사용성 평가
        usability = await self._evaluate_usability(component)

        # 9. 종합 품질 점수
        overall_quality = self._calculate_overall_quality({
            'maintainability': maintainability,
            'reusability': reusability,
            'testability': testability,
            'modularity': modularity,
            'reliability': reliability,
            'security': security,
            'performance': performance,
            'usability': usability
        })

        # 10. 품질 등급 결정
        quality_grade = self._determine_quality_grade(overall_quality)

        # 11. 이슈 식별
        issues = await self._identify_quality_issues(
            component,
            {
                'maintainability': maintainability,
                'reusability': reusability,
                'testability': testability,
                'modularity': modularity,
                'reliability': reliability,
                'security': security,
                'performance': performance,
                'usability': usability
            }
        )

        # 12. 개선 제안
        improvements = await self._generate_improvements(
            component,
            issues,
            quality_grade
        )

        return QualityMetrics(
            maintainability=maintainability,
            reusability=reusability,
            testability=testability,
            modularity=modularity,
            reliability=reliability,
            security=security,
            performance=performance,
            usability=usability,
            overall_quality=overall_quality,
            quality_grade=quality_grade,
            issues=issues,
            improvements=improvements
        )

    async def _evaluate_maintainability(
        self,
        component: ComponentDecision
    ) -> float:
        """유지보수성 평가"""

        score = 100.0

        # 1. 코드 복잡도 영향
        if hasattr(component, 'complexity_score'):
            complexity_penalty = min(component.complexity_score * 5, 30)
            score -= complexity_penalty

        # 2. 문서화 수준
        documentation_score = self._evaluate_documentation(component)
        if documentation_score < 0.7:
            score -= (1 - documentation_score) * 20

        # 3. 네이밍 일관성
        naming_consistency = self._check_naming_consistency(component)
        if naming_consistency < 0.8:
            score -= (1 - naming_consistency) * 15

        # 4. 의존성 관리
        dependency_score = self._evaluate_dependency_management(component)
        score -= (1 - dependency_score) * 10

        # 5. 변경 영향도
        change_impact = len(component.dependencies) / 10
        score -= min(change_impact * 10, 15)

        return max(score, 0)

    async def _evaluate_reusability(
        self,
        component: ComponentDecision
    ) -> float:
        """재사용성 평가"""

        score = 100.0

        # 1. 인터페이스 명확성
        interface_clarity = self._evaluate_interface_clarity(component)
        score *= interface_clarity

        # 2. 결합도 (Coupling)
        coupling_score = self._calculate_coupling(component)
        if coupling_score > 0.5:
            score -= (coupling_score - 0.5) * 40

        # 3. 응집도 (Cohesion)
        cohesion_score = self._calculate_cohesion(component)
        score *= cohesion_score

        # 4. 파라미터화 수준
        parameterization = self._evaluate_parameterization(component)
        score *= parameterization

        # 5. 도메인 독립성
        domain_independence = self._evaluate_domain_independence(component)
        score *= domain_independence

        return round(score, 1)

    def _calculate_overall_quality(
        self,
        metrics: Dict[str, float]
    ) -> float:
        """종합 품질 점수 계산"""

        # ISO 25010 기반 가중치
        weights = {
            'maintainability': 0.20,
            'reusability': 0.15,
            'testability': 0.15,
            'modularity': 0.10,
            'reliability': 0.15,
            'security': 0.10,
            'performance': 0.10,
            'usability': 0.05
        }

        # 가중 평균 계산
        overall_score = sum(
            metrics[key] * weights[key]
            for key in weights
        )

        return round(overall_score, 1)

    def _determine_quality_grade(self, score: float) -> str:
        """품질 등급 결정"""

        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
```

**검증 기준**:

- [ ] ISO 25010 품질 모델 적용
- [ ] 정량적 품질 메트릭
- [ ] 실행 가능한 개선 제안
- [ ] 벤치마크 대비 평가

#### SubTask 4.32.4: 컴포넌트 영향도 분석기

**담당자**: 영향 분석 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/impact_analyzer.py
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class ImpactAnalysis:
    component_id: str
    impact_scope: str  # local, module, system, global
    affected_components: List[str]
    affected_requirements: List[str]
    affected_users: List[str]
    change_scenarios: List[Dict[str, Any]]
    risk_level: str  # low, medium, high, critical
    mitigation_strategies: List[str]
    estimated_effort: int  # story points
    ripple_effects: List[Dict[str, Any]]

class ComponentImpactAnalyzer:
    """컴포넌트 변경 영향도 분석"""

    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.change_propagator = ChangePropagator()
        self.risk_calculator = RiskCalculator()
        self.effort_estimator = EffortEstimator()

    async def analyze_component_impact(
        self,
        component: ComponentDecision,
        all_components: List[ComponentDecision],
        change_type: str = 'modification'
    ) -> ImpactAnalysis:
        """컴포넌트 변경 영향도 분석"""

        # 1. 의존성 그래프 구축
        self._build_dependency_graph(all_components)

        # 2. 직접 영향받는 컴포넌트 식별
        direct_impacts = self._find_direct_impacts(component.id)

        # 3. 간접 영향받는 컴포넌트 식별 (전이적 의존성)
        indirect_impacts = self._find_indirect_impacts(
            component.id,
            max_depth=3
        )

        # 4. 영향 범위 결정
        impact_scope = self._determine_impact_scope(
            len(direct_impacts),
            len(indirect_impacts),
            len(all_components)
        )

        # 5. 영향받는 요구사항 식별
        affected_requirements = self._find_affected_requirements(
            component,
            direct_impacts + indirect_impacts,
            all_components
        )

        # 6. 영향받는 사용자 그룹 식별
        affected_users = await self._identify_affected_users(
            component,
            affected_requirements
        )

        # 7. 변경 시나리오 생성
        change_scenarios = await self._generate_change_scenarios(
            component,
            change_type,
            direct_impacts,
            indirect_impacts
        )

        # 8. 위험 수준 계산
        risk_level = await self.risk_calculator.calculate_risk(
            component,
            impact_scope,
            len(affected_components),
            change_scenarios
        )

        # 9. 완화 전략 수립
        mitigation_strategies = await self._generate_mitigation_strategies(
            risk_level,
            change_scenarios
        )

        # 10. 노력 추정
        estimated_effort = await self.effort_estimator.estimate(
            component,
            direct_impacts,
            indirect_impacts,
            change_type
        )

        # 11. 파급 효과 분석
        ripple_effects = await self._analyze_ripple_effects(
            component,
            all_components
        )

        return ImpactAnalysis(
            component_id=component.id,
            impact_scope=impact_scope,
            affected_components=direct_impacts + indirect_impacts,
            affected_requirements=affected_requirements,
            affected_users=affected_users,
            change_scenarios=change_scenarios,
            risk_level=risk_level,
            mitigation_strategies=mitigation_strategies,
            estimated_effort=estimated_effort,
            ripple_effects=ripple_effects
        )

    def _build_dependency_graph(
        self,
        components: List[ComponentDecision]
    ) -> None:
        """컴포넌트 의존성 그래프 구축"""

        # 노드 추가
        for component in components:
            self.dependency_graph.add_node(
                component.id,
                component=component
            )

        # 엣지 추가 (의존성)
        for component in components:
            for dep_id in component.dependencies:
                self.dependency_graph.add_edge(
                    component.id,
                    dep_id,
                    weight=1.0
                )

    def _find_direct_impacts(self, component_id: str) -> List[str]:
        """직접 영향받는 컴포넌트 찾기"""

        # 이 컴포넌트에 의존하는 컴포넌트들
        dependents = list(self.dependency_graph.predecessors(component_id))

        return dependents

    def _find_indirect_impacts(
        self,
        component_id: str,
        max_depth: int = 3
    ) -> List[str]:
        """간접 영향받는 컴포넌트 찾기"""

        indirect_impacts = set()

        # BFS로 전이적 의존성 탐색
        current_level = {component_id}
        visited = {component_id}

        for depth in range(max_depth):
            next_level = set()

            for node in current_level:
                predecessors = set(self.dependency_graph.predecessors(node))
                new_predecessors = predecessors - visited

                if depth > 0:  # 첫 번째 레벨은 직접 영향이므로 제외
                    indirect_impacts.update(new_predecessors)

                next_level.update(new_predecessors)
                visited.update(new_predecessors)

            current_level = next_level

            if not current_level:
                break

        return list(indirect_impacts)

    async def _generate_change_scenarios(
        self,
        component: ComponentDecision,
        change_type: str,
        direct_impacts: List[str],
        indirect_impacts: List[str]
    ) -> List[Dict[str, Any]]:
        """변경 시나리오 생성"""

        scenarios = []

        # 기본 시나리오
        base_scenario = {
            'name': f'{change_type.title()} of {component.name}',
            'type': change_type,
            'description': f'Direct {change_type} to component {component.name}',
            'direct_impacts': len(direct_impacts),
            'indirect_impacts': len(indirect_impacts),
            'estimated_duration': self._estimate_duration(
                change_type,
                component.complexity_score
            ),
            'rollback_strategy': self._define_rollback_strategy(change_type)
        }
        scenarios.append(base_scenario)

        # 인터페이스 변경 시나리오
        if change_type in ['modification', 'major_update']:
            interface_scenario = {
                'name': f'Interface change for {component.name}',
                'type': 'interface_change',
                'description': 'Changes to component interface affecting dependents',
                'breaking_changes': self._identify_breaking_changes(component),
                'migration_required': True,
                'affected_contracts': self._find_affected_contracts(component)
            }
            scenarios.append(interface_scenario)

        # 제거 시나리오
        if change_type == 'removal':
            removal_scenario = {
                'name': f'Removal of {component.name}',
                'type': 'removal',
                'description': 'Complete removal of component',
                'replacement_needed': True,
                'alternative_components': await self._find_alternatives(component),
                'data_migration': self._requires_data_migration(component)
            }
            scenarios.append(removal_scenario)

        return scenarios
```

**검증 기준**:

- [ ] 전이적 영향 분석
- [ ] 위험 수준 정량화
- [ ] 변경 시나리오 시뮬레이션
- [ ] 실행 가능한 완화 전략

---

### Task 4.33: 컴포넌트 최적화 시스템

#### SubTask 4.33.1: 컴포넌트 재사용성 최적화기

**담당자**: 소프트웨어 재사용 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/reusability_optimizer.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

@dataclass
class ReusabilityOptimization:
    component_id: str
    original_score: float
    optimized_score: float
    modifications: List[Dict[str, Any]]
    abstraction_level: str  # concrete, abstract, generic
    parameterization: Dict[str, Any]
    interface_changes: List[Dict[str, Any]]
    estimated_effort: int
    roi_analysis: Dict[str, float]

class ComponentReusabilityOptimizer:
    """컴포넌트 재사용성 최적화"""

    def __init__(self):
        self.abstraction_analyzer = AbstractionAnalyzer()
        self.interface_optimizer = InterfaceOptimizer()
        self.dependency_reducer = DependencyReducer()
        self.pattern_applier = DesignPatternApplier()
        self.roi_calculator = ROICalculator()

    async def optimize_reusability(
        self,
        component: ComponentDecision,
        context: Dict[str, Any]
    ) -> ReusabilityOptimization:
        """컴포넌트 재사용성 최적화"""

        # 1. 현재 재사용성 평가
        original_score = await self._evaluate_current_reusability(component)

        # 2. 최적화 기회 식별
        optimization_opportunities = await self._identify_opportunities(
            component,
            original_score
        )

        # 3. 추상화 수준 최적화
        abstraction_optimization = await self._optimize_abstraction(
            component,
            optimization_opportunities
        )

        # 4. 인터페이스 최적화
        interface_optimization = await self._optimize_interface(
            component,
            abstraction_optimization
        )

        # 5. 의존성 최소화
        dependency_optimization = await self._minimize_dependencies(
            component
        )

        # 6. 파라미터화 적용
        parameterization = await self._apply_parameterization(
            component,
            interface_optimization
        )

        # 7. 디자인 패턴 적용
        pattern_optimization = await self._apply_design_patterns(
            component,
            optimization_opportunities
        )

        # 8. 최적화 결과 통합
        optimized_component = await self._integrate_optimizations(
            component,
            [
                abstraction_optimization,
                interface_optimization,
                dependency_optimization,
                parameterization,
                pattern_optimization
            ]
        )

        # 9. 최적화된 재사용성 점수
        optimized_score = await self._evaluate_current_reusability(
            optimized_component
        )

        # 10. ROI 분석
        roi_analysis = await self.roi_calculator.calculate_roi(
            original_score,
            optimized_score,
            self._calculate_optimization_effort(optimization_opportunities)
        )

        return ReusabilityOptimization(
            component_id=component.id,
            original_score=original_score,
            optimized_score=optimized_score,
            modifications=self._summarize_modifications(
                optimization_opportunities
            ),
            abstraction_level=abstraction_optimization['level'],
            parameterization=parameterization,
            interface_changes=interface_optimization['changes'],
            estimated_effort=self._calculate_optimization_effort(
                optimization_opportunities
            ),
            roi_analysis=roi_analysis
        )

    async def _optimize_abstraction(
        self,
        component: ComponentDecision,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """추상화 수준 최적화"""

        current_abstraction = self._analyze_current_abstraction(component)

        # 추상화 전략 결정
        if current_abstraction['level'] == 'concrete':
            # 구체적인 구현을 추상화
            abstraction_strategy = {
                'level': 'abstract',
                'techniques': [
                    'extract_interface',
                    'generalize_types',
                    'abstract_common_behavior'
                ],
                'changes': []
            }

            # 인터페이스 추출
            if component.type == ComponentType.BACKEND_SERVICE:
                abstraction_strategy['changes'].append({
                    'type': 'extract_interface',
                    'description': f'Extract I{component.name} interface',
                    'benefits': ['Dependency inversion', 'Testability'],
                    'code_template': self._generate_interface_template(component)
                })

            # 타입 일반화
            generic_types = self._identify_generic_opportunities(component)
            for generic in generic_types:
                abstraction_strategy['changes'].append({
                    'type': 'generalize_type',
                    'from': generic['specific_type'],
                    'to': generic['generic_type'],
                    'benefits': ['Flexibility', 'Wider applicability']
                })

        elif current_abstraction['level'] == 'overly_abstract':
            # 과도한 추상화 조정
            abstraction_strategy = {
                'level': 'balanced',
                'techniques': ['reduce_abstraction_layers'],
                'changes': []
            }

        else:
            abstraction_strategy = current_abstraction

        return abstraction_strategy

    async def _optimize_interface(
        self,
        component: ComponentDecision,
        abstraction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """인터페이스 최적화"""

        interface_optimization = {
            'changes': [],
            'principles_applied': []
        }

        # 1. 인터페이스 분리 원칙 (ISP) 적용
        if len(component.interfaces.get('methods', [])) > 7:
            segregated_interfaces = self._segregate_interface(component)
            interface_optimization['changes'].extend(segregated_interfaces)
            interface_optimization['principles_applied'].append('ISP')

        # 2. 의존성 역전 원칙 (DIP) 적용
        concrete_dependencies = self._find_concrete_dependencies(component)
        if concrete_dependencies:
            abstracted_deps = self._abstract_dependencies(concrete_dependencies)
            interface_optimization['changes'].extend(abstracted_deps)
            interface_optimization['principles_applied'].append('DIP')

        # 3. 파라미터 객체 패턴 적용
        methods_with_many_params = [
            m for m in component.interfaces.get('methods', [])
            if len(m.get('parameters', [])) > 3
        ]

        for method in methods_with_many_params:
            param_object = {
                'type': 'parameter_object',
                'method': method['name'],
                'object_name': f"{method['name']}Params",
                'benefits': ['Cleaner interface', 'Easier to extend']
            }
            interface_optimization['changes'].append(param_object)

        # 4. 플루언트 인터페이스 고려
        if self._is_builder_candidate(component):
            fluent_interface = {
                'type': 'fluent_interface',
                'pattern': 'builder',
                'benefits': ['Better readability', 'Chainable calls']
            }
            interface_optimization['changes'].append(fluent_interface)

        return interface_optimization

    async def _apply_parameterization(
        self,
        component: ComponentDecision,
        interface_optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """파라미터화 적용"""

        parameterization = {
            'configuration_points': [],
            'templates': [],
            'policies': []
        }

        # 1. 설정 가능한 포인트 식별
        configurable_aspects = self._identify_configurable_aspects(component)

        for aspect in configurable_aspects:
            config_point = {
                'name': aspect['name'],
                'type': aspect['type'],
                'default_value': aspect['default'],
                'validation': aspect['validation'],
                'description': aspect['description']
            }
            parameterization['configuration_points'].append(config_point)

        # 2. 템플릿 메서드 패턴 적용 가능성
        template_candidates = self._find_template_method_candidates(component)

        for candidate in template_candidates:
            template = {
                'method': candidate['method'],
                'variable_steps': candidate['variable_steps'],
                'hook_points': candidate['hook_points']
            }
            parameterization['templates'].append(template)

        # 3. 전략 패턴 적용 가능성
        strategy_candidates = self._find_strategy_candidates(component)

        for candidate in strategy_candidates:
            policy = {
                'behavior': candidate['behavior'],
                'strategies': candidate['strategies'],
                'selection_criteria': candidate['criteria']
            }
            parameterization['policies'].append(policy)

        return parameterization
```

**검증 기준**:

- [ ] 재사용성 점수 향상
- [ ] SOLID 원칙 적용
- [ ] 파라미터화 수준 증가
- [ ] ROI 분석 완료

#### SubTask 4.33.2: 컴포넌트 성능 최적화기

**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/performance_optimizer.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import time

@dataclass
class PerformanceOptimization:
    component_id: str
    performance_metrics: Dict[str, float]
    optimizations_applied: List[Dict[str, Any]]
    performance_gain: Dict[str, float]
    resource_usage: Dict[str, Any]
    scalability_improvements: List[str]
    bottlenecks_resolved: List[str]
    trade_offs: List[Dict[str, Any]]

class ComponentPerformanceOptimizer:
    """컴포넌트 성능 최적화"""

    def __init__(self):
        self.profiler = ComponentProfiler()
        self.bottleneck_analyzer = BottleneckAnalyzer()
        self.cache_optimizer = CacheOptimizer()
        self.async_optimizer = AsyncOptimizer()
        self.resource_optimizer = ResourceOptimizer()

    async def optimize_performance(
        self,
        component: ComponentDecision,
        performance_requirements: Dict[str, Any]
    ) -> PerformanceOptimization:
        """컴포넌트 성능 최적화"""

        # 1. 현재 성능 프로파일링
        current_metrics = await self.profiler.profile_component(component)

        # 2. 병목 지점 분석
        bottlenecks = await self.bottleneck_analyzer.analyze(
            component,
            current_metrics
        )

        # 3. 최적화 전략 수립
        optimization_strategy = await self._create_optimization_strategy(
            component,
            bottlenecks,
            performance_requirements
        )

        # 4. 캐싱 최적화
        cache_optimizations = await self._optimize_caching(
            component,
            bottlenecks
        )

        # 5. 비동기 처리 최적화
        async_optimizations = await self._optimize_async_processing(
            component,
            bottlenecks
        )

        # 6. 데이터 구조 최적화
        data_structure_optimizations = await self._optimize_data_structures(
            component
        )

        # 7. 알고리즘 최적화
        algorithm_optimizations = await self._optimize_algorithms(
            component,
            bottlenecks
        )

        # 8. 리소스 사용 최적화
        resource_optimizations = await self._optimize_resource_usage(
            component
        )

        # 9. 최적화 적용 및 측정
        optimized_metrics = await self._apply_and_measure_optimizations(
            component,
            [
                cache_optimizations,
                async_optimizations,
                data_structure_optimizations,
                algorithm_optimizations,
                resource_optimizations
            ]
        )

        # 10. 성능 향상 계산
        performance_gain = self._calculate_performance_gain(
            current_metrics,
            optimized_metrics
        )

        # 11. 트레이드오프 분석
        trade_offs = await self._analyze_trade_offs(
            component,
            optimization_strategy
        )

        return PerformanceOptimization(
            component_id=component.id,
            performance_metrics=optimized_metrics,
            optimizations_applied=self._summarize_optimizations([
                cache_optimizations,
                async_optimizations,
                data_structure_optimizations,
                algorithm_optimizations,
                resource_optimizations
            ]),
            performance_gain=performance_gain,
            resource_usage=await self._measure_resource_usage(component),
            scalability_improvements=self._identify_scalability_improvements(
                optimization_strategy
            ),
            bottlenecks_resolved=[b['id'] for b in bottlenecks],
            trade_offs=trade_offs
        )

    async def _optimize_caching(
        self,
        component: ComponentDecision,
        bottlenecks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """캐싱 최적화"""

        cache_optimization = {
            'strategies': [],
            'cache_points': [],
            'invalidation_policies': []
        }

        # 1. 캐시 가능한 작업 식별
        cacheable_operations = self._identify_cacheable_operations(
            component,
            bottlenecks
        )

        for operation in cacheable_operations:
            # 캐시 전략 결정
            if operation['frequency'] > 100:  # 고빈도 작업
                strategy = {
                    'type': 'memory_cache',
                    'ttl': 300,  # 5분
                    'max_entries': 1000,
                    'eviction_policy': 'LRU'
                }
            elif operation['computation_cost'] > 1000:  # 고비용 연산
                strategy = {
                    'type': 'distributed_cache',
                    'backend': 'redis',
                    'ttl': 3600,  # 1시간
                    'compression': True
                }
            else:
                strategy = {
                    'type': 'local_cache',
                    'ttl': 60,
                    'max_entries': 100
                }

            cache_optimization['strategies'].append({
                'operation': operation['name'],
                'strategy': strategy,
                'expected_hit_rate': operation['repeatability'] * 0.8,
                'performance_impact': operation['computation_cost'] * 0.7
            })

        # 2. 캐시 무효화 정책
        for cache_point in cache_optimization['strategies']:
            invalidation_policy = self._design_invalidation_policy(
                component,
                cache_point
            )
            cache_optimization['invalidation_policies'].append(
                invalidation_policy
            )

        return cache_optimization

    async def _optimize_async_processing(
        self,
        component: ComponentDecision,
        bottlenecks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """비동기 처리 최적화"""

        async_optimization = {
            'parallelizable_tasks': [],
            'async_patterns': [],
            'concurrency_limits': {}
        }

        # 1. 병렬화 가능한 작업 식별
        if component.type == ComponentType.BACKEND_SERVICE:
            # I/O 바운드 작업 찾기
            io_operations = [
                op for op in component.interfaces.get('operations', [])
                if op.get('type') in ['database', 'api_call', 'file_io']
            ]

            for op in io_operations:
                if self._can_parallelize(op):
                    async_optimization['parallelizable_tasks'].append({
                        'operation': op['name'],
                        'current_time': op.get('avg_duration', 1000),
                        'parallel_time': op.get('avg_duration', 1000) / 3,
                        'pattern': 'async/await'
                    })

        # 2. 비동기 패턴 적용
        if len(async_optimization['parallelizable_tasks']) > 3:
            async_optimization['async_patterns'].append({
                'pattern': 'batch_processing',
                'description': 'Batch multiple requests for efficiency',
                'batch_size': 10,
                'timeout': 100
            })

        # 3. 동시성 제한 설정
        async_optimization['concurrency_limits'] = {
            'max_concurrent_requests': 50,
            'rate_limit': '1000/minute',
            'circuit_breaker': {
                'failure_threshold': 5,
                'timeout': 30000,
                'half_open_requests': 3
            }
        }

        return async_optimization

    async def _optimize_algorithms(
        self,
        component: ComponentDecision,
        bottlenecks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """알고리즘 최적화"""

        algorithm_optimization = {
            'optimized_algorithms': [],
            'complexity_improvements': [],
            'space_time_tradeoffs': []
        }

        # 알고리즘 복잡도 분석
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'computational':
                current_complexity = bottleneck.get('complexity', 'O(n²)')

                # 최적화 가능성 평가
                if 'sorting' in bottleneck['operation']:
                    algorithm_optimization['optimized_algorithms'].append({
                        'operation': bottleneck['operation'],
                        'current': 'bubble_sort',
                        'optimized': 'quicksort',
                        'complexity_change': 'O(n²) -> O(n log n)',
                        'expected_speedup': '10x for n=1000'
                    })

                elif 'search' in bottleneck['operation']:
                    algorithm_optimization['optimized_algorithms'].append({
                        'operation': bottleneck['operation'],
                        'current': 'linear_search',
                        'optimized': 'binary_search',
                        'complexity_change': 'O(n) -> O(log n)',
                        'prerequisite': 'sorted data',
                        'expected_speedup': '100x for n=10000'
                    })

        return algorithm_optimization
```

**검증 기준**:

- [ ] 성능 병목 지점 해결
- [ ] 응답 시간 개선
- [ ] 리소스 사용 최적화
- [ ] 확장성 향상

#### SubTask 4.33.3: 컴포넌트 보안 강화기

**담당자**: 보안 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/security_enhancer.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import secrets

@dataclass
class SecurityThreat(Enum):
    INJECTION = "injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA = "sensitive_data_exposure"
    XXE = "xml_external_entities"
    BROKEN_ACCESS = "broken_access_control"
    SECURITY_MISCONFIG = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    VULNERABLE_COMPONENTS = "using_vulnerable_components"
    INSUFFICIENT_LOGGING = "insufficient_logging"

@dataclass
class SecurityEnhancement:
    component_id: str
    security_score_before: float
    security_score_after: float
    vulnerabilities_found: List[Dict[str, Any]]
    mitigations_applied: List[Dict[str, Any]]
    security_patterns: List[str]
    compliance_requirements: Dict[str, bool]
    security_tests: List[Dict[str, Any]]
    recommendations: List[str]

class ComponentSecurityEnhancer:
    """컴포넌트 보안 강화"""

    def __init__(self):
        self.vulnerability_scanner = VulnerabilityScanner()
        self.security_pattern_library = SecurityPatternLibrary()
        self.compliance_checker = ComplianceChecker()
        self.threat_modeler = ThreatModeler()
        self.security_test_generator = SecurityTestGenerator()

    async def enhance_security(
        self,
        component: ComponentDecision,
        security_requirements: Optional[Dict[str, Any]] = None
    ) -> SecurityEnhancement:
        """컴포넌트 보안 강화"""

        # 1. 현재 보안 수준 평가
        current_security_score = await self._assess_security_level(component)

        # 2. 위협 모델링
        threat_model = await self.threat_modeler.model_threats(component)

        # 3. 취약점 스캔
        vulnerabilities = await self.vulnerability_scanner.scan(
            component,
            threat_model
        )

        # 4. 보안 패턴 적용
        security_patterns = await self._apply_security_patterns(
            component,
            vulnerabilities
        )

        # 5. 인증/인가 강화
        auth_enhancements = await self._enhance_authentication(component)

        # 6. 데이터 보호 강화
        data_protection = await self._enhance_data_protection(component)

        # 7. 입력 검증 강화
        input_validation = await self._enhance_input_validation(component)

        # 8. 보안 헤더 및 설정
        security_configs = await self._apply_security_configurations(component)

        # 9. 규정 준수 검증
        compliance_results = await self.compliance_checker.check(
            component,
            security_requirements
        )

        # 10. 보안 테스트 생성
        security_tests = await self.security_test_generator.generate(
            component,
            vulnerabilities
        )

        # 11. 최종 보안 점수
        final_security_score = await self._assess_security_level(
            self._apply_enhancements(component, [
                security_patterns,
                auth_enhancements,
                data_protection,
                input_validation,
                security_configs
            ])
        )

        return SecurityEnhancement(
            component_id=component.id,
            security_score_before=current_security_score,
            security_score_after=final_security_score,
            vulnerabilities_found=vulnerabilities,
            mitigations_applied=self._summarize_mitigations([
                security_patterns,
                auth_enhancements,
                data_protection,
                input_validation,
                security_configs
            ]),
            security_patterns=[p['name'] for p in security_patterns],
            compliance_requirements=compliance_results,
            security_tests=security_tests,
            recommendations=await self._generate_recommendations(
                component,
                vulnerabilities,
                compliance_results
            )
        )

    async def _apply_security_patterns(
        self,
        component: ComponentDecision,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """보안 패턴 적용"""

        applied_patterns = []

        # 1. 인증 패턴
        if any(v['type'] == SecurityThreat.BROKEN_AUTH for v in vulnerabilities):
            auth_pattern = {
                'name': 'secure_authentication_pattern',
                'components': {
                    'authenticator': {
                        'type': 'jwt_based',
                        'algorithm': 'RS256',
                        'token_expiry': 900,  # 15분
                        'refresh_token_expiry': 604800  # 7일
                    },
                    'session_manager': {
                        'storage': 'redis',
                        'session_timeout': 1800,
                        'concurrent_sessions': 3
                    },
                    'mfa': {
                        'enabled': True,
                        'methods': ['totp', 'sms', 'email']
                    }
                },
                'implementation': self._generate_auth_implementation(component)
            }
            applied_patterns.append(auth_pattern)

        # 2. 입력 검증 패턴
        if component.type in [ComponentType.API_ENDPOINT, ComponentType.UI_COMPONENT]:
            validation_pattern = {
                'name': 'input_validation_pattern',
                'validators': [
                    {
                        'type': 'schema_validation',
                        'library': 'joi' if component.technology_stack[0] == 'nodejs' else 'pydantic',
                        'strict_mode': True
                    },
                    {
                        'type': 'sanitization',
                        'methods': ['html_escape', 'sql_escape', 'command_escape']
                    },
                    {
                        'type': 'rate_limiting',
                        'limits': {
                            'per_ip': '100/hour',
                            'per_user': '1000/hour'
                        }
                    }
                ],
                'implementation': self._generate_validation_implementation(component)
            }
            applied_patterns.append(validation_pattern)

        # 3. 보안 프록시 패턴
        if component.type == ComponentType.BACKEND_SERVICE:
            proxy_pattern = {
                'name': 'security_proxy_pattern',
                'proxy_type': 'api_gateway',
                'features': [
                    'request_filtering',
                    'response_sanitization',
                    'audit_logging',
                    'threat_detection'
                ],
                'rules': self._generate_proxy_rules(component)
            }
            applied_patterns.append(proxy_pattern)

        return applied_patterns

    async def _enhance_data_protection(
        self,
        component: ComponentDecision
    ) -> Dict[str, Any]:
        """데이터 보호 강화"""

        data_protection = {
            'encryption': {},
            'masking': {},
            'access_control': {},
            'audit': {}
        }

        # 1. 암호화
        if component.type == ComponentType.DATA_MODEL:
            data_protection['encryption'] = {
                'at_rest': {
                    'algorithm': 'AES-256-GCM',
                    'key_management': 'AWS KMS',
                    'fields': self._identify_sensitive_fields(component)
                },
                'in_transit': {
                    'protocol': 'TLS 1.3',
                    'cipher_suites': [
                        'TLS_AES_256_GCM_SHA384',
                        'TLS_CHACHA20_POLY1305_SHA256'
                    ]
                }
            }

        # 2. 데이터 마스킹
        sensitive_data_types = ['email', 'phone', 'ssn', 'credit_card']
        data_protection['masking'] = {
            'rules': [
                {
                    'field_type': dtype,
                    'masking_function': self._get_masking_function(dtype),
                    'unmask_permission': f'unmask_{dtype}'
                }
                for dtype in sensitive_data_types
            ]
        }

        # 3. 접근 제어
        data_protection['access_control'] = {
            'model': 'RBAC',  # Role-Based Access Control
            'policies': [
                {
                    'resource': component.name,
                    'actions': ['read', 'write', 'delete'],
                    'conditions': {
                        'ip_whitelist': True,
                        'mfa_required': True,
                        'time_restrictions': True
                    }
                }
            ]
        }

        # 4. 감사 로깅
        data_protection['audit'] = {
            'enabled': True,
            'events': [
                'data_access',
                'data_modification',
                'permission_change',
                'failed_access_attempt'
            ],
            'retention': '90_days',
            'immutable_storage': True
        }

        return data_protection
```

**검증 기준**:

- [ ] OWASP Top 10 대응
- [ ] 보안 점수 향상
- [ ] 규정 준수 검증
- [ ] 보안 테스트 자동화

#### SubTask 4.33.4: 컴포넌트 통합 최적화기

**담당자**: 통합 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/integration_optimizer.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import networkx as nx

@dataclass
class IntegrationOptimization:
    component_id: str
    integration_points: List[Dict[str, Any]]
    communication_patterns: List[str]
    data_contracts: List[Dict[str, Any]]
    error_handling: Dict[str, Any]
    monitoring_setup: Dict[str, Any]
    performance_impact: Dict[str, float]
    integration_tests: List[Dict[str, Any]]

class ComponentIntegrationOptimizer:
    """컴포넌트 통합 최적화"""

    def __init__(self):
        self.pattern_selector = IntegrationPatternSelector()
        self.contract_designer = ContractDesigner()
        self.resilience_builder = ResilienceBuilder()
        self.test_generator = IntegrationTestGenerator()

    async def optimize_integration(
        self,
        component: ComponentDecision,
        related_components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> IntegrationOptimization:
        """컴포넌트 통합 최적화"""

        # 1. 통합 포인트 분석
        integration_points = await self._analyze_integration_points(
            component,
            related_components
        )

        # 2. 통신 패턴 선택
        communication_patterns = await self._select_communication_patterns(
            component,
            integration_points,
            architecture
        )

        # 3. 데이터 계약 설계
        data_contracts = await self._design_data_contracts(
            component,
            integration_points
        )

        # 4. 오류 처리 전략
        error_handling = await self._design_error_handling(
            component,
            communication_patterns
        )

        # 5. 회복탄력성 패턴 적용
        resilience_patterns = await self._apply_resilience_patterns(
            component,
            integration_points
        )

        # 6. 모니터링 설정
        monitoring_setup = await self._setup_monitoring(
            component,
            integration_points
        )

        # 7. 성능 영향 분석
        performance_impact = await self._analyze_performance_impact(
            component,
            communication_patterns
        )

        # 8. 통합 테스트 생성
        integration_tests = await self.test_generator.generate_tests(
            component,
            integration_points,
            data_contracts
        )

        return IntegrationOptimization(
            component_id=component.id,
            integration_points=integration_points,
            communication_patterns=[p['name'] for p in communication_patterns],
            data_contracts=data_contracts,
            error_handling=error_handling,
            monitoring_setup=monitoring_setup,
            performance_impact=performance_impact,
            integration_tests=integration_tests
        )

    async def _select_communication_patterns(
        self,
        component: ComponentDecision,
        integration_points: List[Dict[str, Any]],
        architecture: ComponentArchitecture
    ) -> List[Dict[str, Any]]:
        """통신 패턴 선택"""

        selected_patterns = []

        for point in integration_points:
            # 통신 특성 분석
            characteristics = {
                'sync_required': point.get('requires_immediate_response', False),
                'data_volume': point.get('data_volume', 'medium'),
                'frequency': point.get('call_frequency', 'medium'),
                'reliability_required': point.get('reliability', 'high')
            }

            # 패턴 선택
            if characteristics['sync_required']:
                if characteristics['data_volume'] == 'small':
                    pattern = {
                        'name': 'request_response',
                        'protocol': 'REST',
                        'timeout': 5000,
                        'retry_policy': {
                            'max_attempts': 3,
                            'backoff': 'exponential'
                        }
                    }
                else:
                    pattern = {
                        'name': 'streaming',
                        'protocol': 'gRPC',
                        'stream_type': 'bidirectional'
                    }
            else:
                # 비동기 통신
                if characteristics['reliability_required'] == 'high':
                    pattern = {
                        'name': 'message_queue',
                        'broker': 'RabbitMQ',
                        'delivery_guarantee': 'exactly_once',
                        'persistence': True
                    }
                else:
                    pattern = {
                        'name': 'event_streaming',
                        'platform': 'Kafka',
                        'retention': '7_days'
                    }

            selected_patterns.append({
                'integration_point': point['id'],
                'pattern': pattern,
                'rationale': self._explain_pattern_choice(
                    characteristics,
                    pattern
                )
            })

        return selected_patterns

    async def _design_data_contracts(
        self,
        component: ComponentDecision,
        integration_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """데이터 계약 설계"""

        contracts = []

        for point in integration_points:
            contract = {
                'id': f"contract_{component.id}_{point['target']}",
                'version': '1.0.0',
                'provider': component.id,
                'consumer': point['target'],
                'request_schema': {},
                'response_schema': {},
                'error_schema': {},
                'sla': {},
                'versioning_strategy': 'semantic'
            }

            # 요청 스키마
            if point.get('input_data'):
                contract['request_schema'] = {
                    'type': 'object',
                    'properties': self._generate_schema_properties(
                        point['input_data']
                    ),
                    'required': point.get('required_fields', [])
                }

            # 응답 스키마
            if point.get('output_data'):
                contract['response_schema'] = {
                    'type': 'object',
                    'properties': self._generate_schema_properties(
                        point['output_data']
                    )
                }

            # 오류 스키마
            contract['error_schema'] = {
                'type': 'object',
                'properties': {
                    'error_code': {'type': 'string'},
                    'message': {'type': 'string'},
                    'details': {'type': 'object'},
                    'timestamp': {'type': 'string', 'format': 'date-time'}
                },
                'required': ['error_code', 'message']
            }

            # SLA
            contract['sla'] = {
                'availability': '99.9%',
                'response_time_p95': point.get('expected_latency', 1000),
                'throughput': point.get('expected_tps', 100)
            }

            contracts.append(contract)

        return contracts

    async def _apply_resilience_patterns(
        self,
        component: ComponentDecision,
        integration_points: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """회복탄력성 패턴 적용"""

        resilience_config = {
            'circuit_breaker': {},
            'retry': {},
            'timeout': {},
            'bulkhead': {},
            'fallback': {}
        }

        # 1. 서킷 브레이커
        resilience_config['circuit_breaker'] = {
            'enabled': True,
            'failure_threshold': 5,
            'success_threshold': 2,
            'timeout': 60000,  # 1분
            'monitoring_period': 10000  # 10초
        }

        # 2. 재시도 정책
        resilience_config['retry'] = {
            'max_attempts': 3,
            'initial_delay': 100,
            'max_delay': 5000,
            'backoff_multiplier': 2,
            'retryable_errors': [
                'NETWORK_ERROR',
                'TIMEOUT',
                'SERVICE_UNAVAILABLE'
            ]
        }

        # 3. 타임아웃
        resilience_config['timeout'] = {
            'default': 5000,
            'per_operation': {
                op['name']: op.get('timeout', 5000)
                for op in component.interfaces.get('operations', [])
            }
        }

        # 4. 벌크헤드 (격리)
        resilience_config['bulkhead'] = {
            'max_concurrent_calls': 50,
            'max_wait_duration': 1000,
            'type': 'thread_pool'
        }

        # 5. 폴백
        resilience_config['fallback'] = {
            'strategies': [
                {
                    'condition': 'circuit_open',
                    'action': 'return_cached_value'
                },
                {
                    'condition': 'timeout',
                    'action': 'return_default_value'
                },
                {
                    'condition': 'error',
                    'action': 'graceful_degradation'
                }
            ]
        }

        return resilience_config
```

**검증 기준**:

- [ ] 통합 복잡도 감소
- [ ] 회복탄력성 향상
- [ ] 명확한 데이터 계약
- [ ] 통합 테스트 커버리지

### Task 4.34: 컴포넌트 패턴 라이브러리

#### SubTask 4.34.1: UI 컴포넌트 패턴 라이브러리

**담당자**: UI 패턴 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/ui_pattern_library.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class UIPattern:
    id: str
    name: str
    category: str
    description: str
    use_cases: List[str]
    components: List[Dict[str, Any]]
    implementation: Dict[str, Any]
    examples: List[Dict[str, Any]]
    best_practices: List[str]
    accessibility: Dict[str, Any]
    responsive_behavior: Dict[str, Any]

class UIComponentPatternLibrary:
    """UI 컴포넌트 패턴 라이브러리"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.pattern_matcher = PatternMatcher()
        self.pattern_composer = PatternComposer()

    def _initialize_patterns(self) -> Dict[str, UIPattern]:
        """UI 패턴 초기화"""

        patterns = {}

        # 1. 폼 패턴
        patterns['form_wizard'] = UIPattern(
            id='form_wizard',
            name='Multi-Step Form Wizard',
            category='forms',
            description='Progressive disclosure form with multiple steps',
            use_cases=[
                'User registration',
                'Complex data entry',
                'Order checkout',
                'Application submission'
            ],
            components=[
                {
                    'name': 'WizardContainer',
                    'props': {
                        'steps': 'array',
                        'currentStep': 'number',
                        'onStepChange': 'function',
                        'validationSchema': 'object'
                    }
                },
                {
                    'name': 'StepIndicator',
                    'props': {
                        'steps': 'array',
                        'currentStep': 'number',
                        'completedSteps': 'array'
                    }
                },
                {
                    'name': 'StepContent',
                    'props': {
                        'children': 'node',
                        'isActive': 'boolean'
                    }
                },
                {
                    'name': 'NavigationControls',
                    'props': {
                        'onNext': 'function',
                        'onPrevious': 'function',
                        'canGoNext': 'boolean',
                        'canGoPrevious': 'boolean'
                    }
                }
            ],
            implementation={
                'react': self._get_react_form_wizard_implementation(),
                'vue': self._get_vue_form_wizard_implementation(),
                'angular': self._get_angular_form_wizard_implementation()
            },
            examples=[
                {
                    'title': 'User Registration Wizard',
                    'code': self._get_registration_wizard_example()
                }
            ],
            best_practices=[
                'Show clear progress indication',
                'Allow backward navigation',
                'Preserve data between steps',
                'Validate on step change',
                'Provide step summaries'
            ],
            accessibility={
                'aria_attributes': {
                    'role': 'form',
                    'aria-label': 'Multi-step form',
                    'aria-describedby': 'step-indicator'
                },
                'keyboard_navigation': True,
                'screen_reader_support': True
            },
            responsive_behavior={
                'mobile': 'vertical_steps',
                'tablet': 'horizontal_steps',
                'desktop': 'horizontal_steps_with_labels'
            }
        )

        # 2. 데이터 디스플레이 패턴
        patterns['data_table_advanced'] = UIPattern(
            id='data_table_advanced',
            name='Advanced Data Table',
            category='data_display',
            description='Feature-rich data table with sorting, filtering, and pagination',
            use_cases=[
                'Admin dashboards',
                'Data management',
                'Report displays',
                'Search results'
            ],
            components=[
                {
                    'name': 'DataTable',
                    'props': {
                        'data': 'array',
                        'columns': 'array',
                        'onSort': 'function',
                        'onFilter': 'function',
                        'onPageChange': 'function'
                    }
                },
                {
                    'name': 'TableHeader',
                    'features': ['sortable', 'resizable', 'reorderable']
                },
                {
                    'name': 'TableFilters',
                    'types': ['text', 'select', 'date_range', 'numeric_range']
                },
                {
                    'name': 'TablePagination',
                    'props': {
                        'totalItems': 'number',
                        'itemsPerPage': 'number',
                        'currentPage': 'number'
                    }
                }
            ],
            implementation={
                'features': {
                    'virtual_scrolling': True,
                    'column_pinning': True,
                    'row_selection': True,
                    'cell_editing': True,
                    'export_functionality': True
                }
            },
            examples=[
                {
                    'title': 'User Management Table',
                    'features': ['search', 'filter', 'bulk_actions']
                }
            ],
            best_practices=[
                'Implement virtual scrolling for large datasets',
                'Provide clear sorting indicators',
                'Support keyboard navigation',
                'Include loading states',
                'Optimize for mobile viewing'
            ],
            accessibility={
                'table_structure': 'proper_thead_tbody',
                'sortable_headers': 'aria-sort',
                'filter_announcements': True
            },
            responsive_behavior={
                'mobile': 'card_view',
                'tablet': 'horizontal_scroll',
                'desktop': 'full_table'
            }
        )

        # 3. 네비게이션 패턴
        patterns['mega_menu'] = UIPattern(
            id='mega_menu',
            name='Mega Menu Navigation',
            category='navigation',
            description='Multi-column dropdown navigation for complex site structures',
            use_cases=[
                'E-commerce sites',
                'Corporate websites',
                'Content-heavy platforms',
                'Multi-product sites'
            ],
            components=[
                {
                    'name': 'MegaMenu',
                    'structure': {
                        'trigger': 'hover_or_click',
                        'columns': 'dynamic',
                        'sections': 'categorized'
                    }
                }
            ],
            implementation={
                'animation': 'fade_slide',
                'delay': 200,
                'close_on_outside_click': True
            },
            examples=[],
            best_practices=[
                'Group related items',
                'Use clear headings',
                'Include visual hints',
                'Optimize for touch devices'
            ],
            accessibility={
                'keyboard_navigation': 'arrow_keys',
                'escape_to_close': True,
                'aria_expanded': True
            },
            responsive_behavior={
                'mobile': 'accordion',
                'tablet': 'simplified_dropdown',
                'desktop': 'full_mega_menu'
            }
        )

        return patterns

    async def recommend_patterns(
        self,
        requirements: List[ParsedRequirement],
        ui_framework: str
    ) -> List[UIPattern]:
        """요구사항에 맞는 UI 패턴 추천"""

        recommended_patterns = []

        # 요구사항 분석
        ui_needs = self._analyze_ui_needs(requirements)

        # 패턴 매칭
        for need in ui_needs:
            matching_patterns = self.pattern_matcher.find_matches(
                need,
                self.patterns,
                ui_framework
            )
            recommended_patterns.extend(matching_patterns)

        # 패턴 조합 최적화
        optimized_patterns = await self.pattern_composer.optimize_combination(
            recommended_patterns
        )

        return optimized_patterns

    def _get_react_form_wizard_implementation(self) -> str:
        """React 폼 위자드 구현"""

        return '''
import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const FormWizard = ({ steps, onComplete, validationSchema }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [completedSteps, setCompletedSteps] = useState(new Set());

  const handleNext = useCallback(async () => {
    const isValid = await validateStep(currentStep, formData, validationSchema);

    if (isValid) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));

      if (currentStep < steps.length - 1) {
        setCurrentStep(prev => prev + 1);
      } else {
        onComplete(formData);
      }
    }
  }, [currentStep, formData, steps.length, onComplete, validationSchema]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const updateFormData = useCallback((stepData) => {
    setFormData(prev => ({ ...prev, ...stepData }));
  }, []);

  return (
    <div className="form-wizard">
      <StepIndicator
        steps={steps}
        currentStep={currentStep}
        completedSteps={completedSteps}
      />

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <StepContent
            step={steps[currentStep]}
            data={formData}
            onChange={updateFormData}
          />
        </motion.div>
      </AnimatePresence>

      <NavigationControls
        onNext={handleNext}
        onPrevious={handlePrevious}
        canGoNext={currentStep < steps.length - 1}
        canGoPrevious={currentStep > 0}
        isLastStep={currentStep === steps.length - 1}
      />
    </div>
  );
};
'''
```

**검증 기준**:

- [ ] 포괄적인 패턴 라이브러리
- [ ] 프레임워크별 구현
- [ ] 접근성 표준 준수
- [ ] 반응형 디자인 지원

---

#### SubTask 4.34.2: 백엔드 서비스 패턴 라이브러리

**담당자**: 백엔드 패턴 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/backend_pattern_library.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class BackendPattern:
    id: str
    name: str
    category: str
    description: str
    use_cases: List[str]
    components: List[Dict[str, Any]]
    implementation: Dict[str, Any]
    benefits: List[str]
    considerations: List[str]
    example_code: Dict[str, str]
    related_patterns: List[str]

class BackendServicePatternLibrary:
    """백엔드 서비스 패턴 라이브러리"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.pattern_analyzer = PatternAnalyzer()
        self.code_generator = PatternCodeGenerator()

    def _initialize_patterns(self) -> Dict[str, BackendPattern]:
        """백엔드 패턴 초기화"""

        patterns = {}

        # 1. Repository 패턴
        patterns['repository'] = BackendPattern(
            id='repository',
            name='Repository Pattern',
            category='data_access',
            description='Abstraction layer between domain and data mapping layers',
            use_cases=[
                'Database operations abstraction',
                'Unit testing with mocks',
                'Switching data sources',
                'Complex query encapsulation'
            ],
            components=[
                {
                    'name': 'IRepository',
                    'type': 'interface',
                    'methods': [
                        'find', 'findAll', 'create',
                        'update', 'delete', 'exists'
                    ]
                },
                {
                    'name': 'BaseRepository',
                    'type': 'abstract_class',
                    'implements': 'IRepository'
                },
                {
                    'name': 'ConcreteRepository',
                    'type': 'class',
                    'extends': 'BaseRepository'
                }
            ],
            implementation={
                'structure': {
                    'interfaces': 'domain/repositories',
                    'implementations': 'infrastructure/repositories',
                    'models': 'domain/models'
                },
                'features': {
                    'pagination': True,
                    'filtering': True,
                    'sorting': True,
                    'transactions': True,
                    'caching': True
                }
            },
            benefits=[
                'Testability improvement',
                'Loose coupling',
                'Centralized query logic',
                'Easy to switch databases'
            ],
            considerations=[
                'Additional abstraction layer',
                'Potential over-engineering for simple apps',
                'Learning curve'
            ],
            example_code={
                'typescript': self._get_repository_typescript_example(),
                'python': self._get_repository_python_example()
            },
            related_patterns=['unit_of_work', 'specification']
        )

        # 2. CQRS 패턴
        patterns['cqrs'] = BackendPattern(
            id='cqrs',
            name='Command Query Responsibility Segregation',
            category='architecture',
            description='Separate read and write operations for scalability',
            use_cases=[
                'High-performance applications',
                'Complex domain logic',
                'Event sourcing systems',
                'Read-heavy applications'
            ],
            components=[
                {
                    'name': 'CommandBus',
                    'responsibility': 'Route commands to handlers'
                },
                {
                    'name': 'QueryBus',
                    'responsibility': 'Route queries to handlers'
                },
                {
                    'name': 'CommandHandler',
                    'responsibility': 'Execute write operations'
                },
                {
                    'name': 'QueryHandler',
                    'responsibility': 'Execute read operations'
                }
            ],
            implementation={
                'separation_level': ['method', 'class', 'service', 'database'],
                'read_models': {
                    'denormalized': True,
                    'cached': True,
                    'eventual_consistency': True
                },
                'write_models': {
                    'normalized': True,
                    'transactional': True,
                    'domain_driven': True
                }
            },
            benefits=[
                'Independent scaling of reads/writes',
                'Optimized read models',
                'Better performance',
                'Clear separation of concerns'
            ],
            considerations=[
                'Increased complexity',
                'Eventual consistency challenges',
                'Data synchronization'
            ],
            example_code={
                'typescript': self._get_cqrs_typescript_example()
            },
            related_patterns=['event_sourcing', 'saga', 'mediator']
        )

        # 3. Saga 패턴
        patterns['saga'] = BackendPattern(
            id='saga',
            name='Saga Pattern',
            category='distributed_transactions',
            description='Manage distributed transactions across microservices',
            use_cases=[
                'Microservices transactions',
                'Long-running processes',
                'Compensation logic',
                'Cross-service operations'
            ],
            components=[
                {
                    'name': 'SagaOrchestrator',
                    'type': 'orchestration',
                    'responsibility': 'Coordinate saga steps'
                },
                {
                    'name': 'SagaStep',
                    'methods': ['execute', 'compensate']
                },
                {
                    'name': 'SagaState',
                    'tracks': ['progress', 'failures', 'compensations']
                }
            ],
            implementation={
                'types': {
                    'orchestration': {
                        'centralized': True,
                        'explicit_flow': True
                    },
                    'choreography': {
                        'decentralized': True,
                        'event_driven': True
                    }
                },
                'persistence': 'saga_state_store',
                'timeout_handling': True,
                'retry_logic': True
            },
            benefits=[
                'Distributed transaction management',
                'Failure recovery',
                'Business process visibility',
                'Audit trail'
            ],
            considerations=[
                'Complex error handling',
                'Idempotency requirements',
                'State management overhead'
            ],
            example_code={
                'typescript': self._get_saga_typescript_example()
            },
            related_patterns=['event_sourcing', 'outbox', 'compensation']
        )

        # 4. Circuit Breaker 패턴
        patterns['circuit_breaker'] = BackendPattern(
            id='circuit_breaker',
            name='Circuit Breaker Pattern',
            category='resilience',
            description='Prevent cascading failures in distributed systems',
            use_cases=[
                'External API calls',
                'Database connections',
                'Microservice communication',
                'Resource protection'
            ],
            components=[
                {
                    'name': 'CircuitBreaker',
                    'states': ['closed', 'open', 'half_open'],
                    'transitions': 'threshold_based'
                },
                {
                    'name': 'HealthCheck',
                    'monitors': 'service_health'
                },
                {
                    'name': 'Fallback',
                    'provides': 'alternative_response'
                }
            ],
            implementation={
                'thresholds': {
                    'failure_count': 5,
                    'failure_rate': 0.5,
                    'timeout': 60000,
                    'reset_timeout': 30000
                },
                'monitoring': {
                    'metrics': ['failure_rate', 'response_time', 'throughput'],
                    'alerts': True
                }
            },
            benefits=[
                'Fault isolation',
                'Fast failure detection',
                'Automatic recovery',
                'System stability'
            ],
            considerations=[
                'Fallback strategy needed',
                'Configuration tuning',
                'Testing complexity'
            ],
            example_code={
                'typescript': self._get_circuit_breaker_example()
            },
            related_patterns=['retry', 'timeout', 'bulkhead']
        )

        # 5. Event Sourcing 패턴
        patterns['event_sourcing'] = BackendPattern(
            id='event_sourcing',
            name='Event Sourcing Pattern',
            category='data_persistence',
            description='Store state changes as sequence of events',
            use_cases=[
                'Audit requirements',
                'Time-travel debugging',
                'Event-driven architectures',
                'Complex state machines'
            ],
            components=[
                {
                    'name': 'EventStore',
                    'stores': 'immutable_events'
                },
                {
                    'name': 'Aggregate',
                    'applies': 'events_to_state'
                },
                {
                    'name': 'Projection',
                    'creates': 'read_models'
                },
                {
                    'name': 'Snapshot',
                    'optimizes': 'replay_performance'
                }
            ],
            implementation={
                'event_schema': {
                    'id': 'uuid',
                    'aggregate_id': 'uuid',
                    'type': 'string',
                    'data': 'json',
                    'metadata': 'json',
                    'timestamp': 'datetime',
                    'version': 'integer'
                },
                'storage_options': ['postgresql', 'eventstore', 'kafka'],
                'snapshot_strategy': {
                    'frequency': 100,  # events
                    'compression': True
                }
            },
            benefits=[
                'Complete audit trail',
                'Temporal queries',
                'Event replay capability',
                'Debugging ease'
            ],
            considerations=[
                'Storage requirements',
                'Event schema evolution',
                'Eventual consistency'
            ],
            example_code={
                'typescript': self._get_event_sourcing_example()
            },
            related_patterns=['cqrs', 'saga', 'projection']
        )

        return patterns

    def _get_repository_typescript_example(self) -> str:
        """TypeScript Repository 패턴 예제"""

        return '''
// Domain layer - Repository interface
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findAll(filter?: UserFilter): Promise<User[]>;
  create(user: User): Promise<User>;
  update(id: string, user: Partial<User>): Promise<User>;
  delete(id: string): Promise<void>;
}

// Infrastructure layer - Implementation
export class UserRepository implements IUserRepository {
  constructor(private readonly db: Database) {}

  async findById(id: string): Promise<User | null> {
    const result = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0] ? this.mapToUser(result.rows[0]) : null;
  }

  async create(user: User): Promise<User> {
    const result = await this.db.query(
      `INSERT INTO users (id, email, name, created_at)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [user.id, user.email, user.name, new Date()]
    );
    return this.mapToUser(result.rows[0]);
  }

  private mapToUser(row: any): User {
    return new User(
      row.id,
      row.email,
      row.name,
      row.created_at
    );
  }
}

// Usage in service layer
export class UserService {
  constructor(private readonly userRepo: IUserRepository) {}

  async registerUser(dto: RegisterUserDTO): Promise<User> {
    const existingUser = await this.userRepo.findByEmail(dto.email);
    if (existingUser) {
      throw new ConflictError('User already exists');
    }

    const user = new User(
      generateId(),
      dto.email,
      dto.name
    );

    return this.userRepo.create(user);
  }
}
'''

    def _get_cqrs_typescript_example(self) -> str:
        """TypeScript CQRS 패턴 예제"""

        return '''
// Command side
export class CreateOrderCommand {
  constructor(
    public readonly customerId: string,
    public readonly items: OrderItem[],
    public readonly shippingAddress: Address
  ) {}
}

export class CreateOrderHandler implements ICommandHandler<CreateOrderCommand> {
  constructor(
    private readonly orderRepo: IOrderRepository,
    private readonly eventBus: IEventBus
  ) {}

  async handle(command: CreateOrderCommand): Promise<void> {
    const order = Order.create(
      command.customerId,
      command.items,
      command.shippingAddress
    );

    await this.orderRepo.save(order);

    // Publish domain events
    const events = order.getUncommittedEvents();
    for (const event of events) {
      await this.eventBus.publish(event);
    }
  }
}

// Query side
export class GetOrderDetailsQuery {
  constructor(public readonly orderId: string) {}
}

export class GetOrderDetailsHandler implements IQueryHandler<GetOrderDetailsQuery, OrderDetailsDTO> {
  constructor(private readonly readDb: IReadDatabase) {}

  async handle(query: GetOrderDetailsQuery): Promise<OrderDetailsDTO> {
    const result = await this.readDb.query(
      `SELECT o.*,
              json_agg(oi.*) as items,
              c.name as customer_name
       FROM order_read_model o
       JOIN order_items_read_model oi ON oi.order_id = o.id
       JOIN customers_read_model c ON c.id = o.customer_id
       WHERE o.id = $1
       GROUP BY o.id, c.name`,
      [query.orderId]
    );

    return this.mapToDTO(result.rows[0]);
  }
}

// Usage
const commandBus = new CommandBus();
const queryBus = new QueryBus();

// Write operation
await commandBus.send(new CreateOrderCommand(
  customerId,
  items,
  address
));

// Read operation
const orderDetails = await queryBus.send(
  new GetOrderDetailsQuery(orderId)
);
'''

    async def recommend_patterns(
        self,
        service_requirements: List[Dict[str, Any]],
        architecture_style: str
    ) -> List[BackendPattern]:
        """서비스 요구사항에 맞는 백엔드 패턴 추천"""

        recommended_patterns = []

        # 요구사항 분석
        pattern_needs = await self.pattern_analyzer.analyze_needs(
            service_requirements,
            architecture_style
        )

        # 패턴 매칭 및 추천
        for need in pattern_needs:
            matching_patterns = self._find_matching_patterns(
                need,
                self.patterns
            )

            # 호환성 검사
            compatible_patterns = self._check_pattern_compatibility(
                matching_patterns,
                recommended_patterns
            )

            recommended_patterns.extend(compatible_patterns)

        return self._prioritize_patterns(recommended_patterns)
```

**검증 기준**:

- [ ] 주요 백엔드 패턴 포함
- [ ] 실제 구현 예제 제공
- [ ] 패턴 간 호환성 검증
- [ ] 아키텍처 스타일별 추천

#### SubTask 4.34.3: 데이터 모델 패턴 라이브러리

**담당자**: 데이터 모델링 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/data_model_pattern_library.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class DataModelPattern:
    id: str
    name: str
    category: str
    description: str
    use_cases: List[str]
    structure: Dict[str, Any]
    constraints: List[str]
    benefits: List[str]
    trade_offs: List[str]
    example_schema: Dict[str, Any]
    migration_strategy: Dict[str, Any]

class DataModelPatternLibrary:
    """데이터 모델 패턴 라이브러리"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.schema_generator = SchemaGenerator()
        self.migration_planner = MigrationPlanner()

    def _initialize_patterns(self) -> Dict[str, DataModelPattern]:
        """데이터 모델 패턴 초기화"""

        patterns = {}

        # 1. 다형성 패턴 (Polymorphic Pattern)
        patterns['polymorphic'] = DataModelPattern(
            id='polymorphic',
            name='Polymorphic Association Pattern',
            category='relationships',
            description='Handle multiple types in a single association',
            use_cases=[
                'Comments on multiple entities',
                'Attachments for various objects',
                'Notifications for different events',
                'Tags across multiple models'
            ],
            structure={
                'single_table_inheritance': {
                    'discriminator_column': 'type',
                    'shared_columns': True,
                    'nullable_columns': True
                },
                'class_table_inheritance': {
                    'base_table': 'parent',
                    'child_tables': ['child_a', 'child_b'],
                    'join_strategy': 'foreign_key'
                },
                'concrete_table_inheritance': {
                    'no_base_table': True,
                    'repeated_columns': True,
                    'union_queries': True
                }
            },
            constraints=[
                'Type safety challenges',
                'Query complexity',
                'Index optimization needed'
            ],
            benefits=[
                'Flexible associations',
                'Reduced table count',
                'Unified interface'
            ],
            trade_offs=[
                'Referential integrity complexity',
                'Performance considerations',
                'Migration difficulty'
            ],
            example_schema={
                'comments': {
                    'id': 'uuid',
                    'commentable_type': 'string',  # 'Post', 'Photo', 'Video'
                    'commentable_id': 'uuid',
                    'content': 'text',
                    'author_id': 'uuid',
                    'created_at': 'timestamp'
                },
                'indexes': [
                    ['commentable_type', 'commentable_id'],
                    ['author_id', 'created_at']
                ]
            },
            migration_strategy={
                'from_separate_tables': 'gradual_migration',
                'to_separate_tables': 'type_based_split'
            }
        )

        # 2. 시계열 데이터 패턴
        patterns['time_series'] = DataModelPattern(
            id='time_series',
            name='Time Series Data Pattern',
            category='temporal',
            description='Optimized structure for time-based data',
            use_cases=[
                'IoT sensor data',
                'Financial market data',
                'Application metrics',
                'User activity logs'
            ],
            structure={
                'partitioning': {
                    'strategy': 'time_based',
                    'interval': 'monthly',
                    'retention': '2_years'
                },
                'compression': {
                    'algorithm': 'zstd',
                    'level': 3,
                    'after_days': 7
                },
                'aggregations': {
                    'continuous': ['1min', '5min', '1hour'],
                    'materialized': ['daily', 'weekly', 'monthly']
                }
            },
            constraints=[
                'Write-heavy workload',
                'Query pattern optimization',
                'Storage management'
            ],
            benefits=[
                'Efficient time-range queries',
                'Automatic data lifecycle',
                'Optimized storage'
            ],
            trade_offs=[
                'Complex partitioning logic',
                'Aggregation maintenance',
                'Point query performance'
            ],
            example_schema={
                'sensor_data': {
                    'time': 'timestamptz',
                    'sensor_id': 'integer',
                    'value': 'double',
                    'quality': 'smallint'
                },
                'hypertable_config': {
                    'chunk_time_interval': '1 day',
                    'compression_after': '7 days',
                    'retention_policy': '2 years'
                }
            },
            migration_strategy={
                'batch_insert': True,
                'parallel_migration': True
            }
        )

        # 3. 소프트 삭제 패턴
        patterns['soft_delete'] = DataModelPattern(
            id='soft_delete',
            name='Soft Delete Pattern',
            category='data_lifecycle',
            description='Mark records as deleted without physical removal',
            use_cases=[
                'Audit requirements',
                'Data recovery needs',
                'Historical reporting',
                'Compliance requirements'
            ],
            structure={
                'implementation_types': {
                    'timestamp_based': {
                        'column': 'deleted_at',
                        'type': 'timestamp',
                        'null_means_active': True
                    },
                    'flag_based': {
                        'column': 'is_deleted',
                        'type': 'boolean',
                        'default': False
                    },
                    'status_based': {
                        'column': 'status',
                        'type': 'enum',
                        'values': ['active', 'deleted', 'archived']
                    }
                },
                'scope_queries': {
                    'default_scope': 'WHERE deleted_at IS NULL',
                    'include_deleted': 'unscoped()',
                    'only_deleted': 'WHERE deleted_at IS NOT NULL'
                }
            },
            constraints=[
                'Index consideration',
                'Unique constraint complexity',
                'Cascading deletes'
            ],
            benefits=[
                'Data recovery capability',
                'Audit trail maintenance',
                'Referential integrity'
            ],
            trade_offs=[
                'Storage overhead',
                'Query complexity',
                'Performance impact'
            ],
            example_schema={
                'implementation': '''
                -- Timestamp-based soft delete
                ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
                CREATE INDEX idx_users_active ON users(id) WHERE deleted_at IS NULL;

                -- View for active records
                CREATE VIEW active_users AS
                SELECT * FROM users WHERE deleted_at IS NULL;

                -- Unique constraint for active records
                CREATE UNIQUE INDEX unique_active_email
                ON users(email) WHERE deleted_at IS NULL;
                '''
            },
            migration_strategy={
                'add_column': 'non_blocking',
                'update_queries': 'gradual',
                'index_creation': 'concurrent'
            }
        )

        # 4. 이벤트 소싱 스키마 패턴
        patterns['event_store'] = DataModelPattern(
            id='event_store',
            name='Event Store Pattern',
            category='event_sourcing',
            description='Schema for storing domain events',
            use_cases=[
                'Event sourcing systems',
                'Audit logs',
                'Change data capture',
                'CQRS implementations'
            ],
            structure={
                'event_table': {
                    'id': 'bigserial',
                    'aggregate_id': 'uuid',
                    'aggregate_type': 'string',
                    'event_type': 'string',
                    'event_data': 'jsonb',
                    'event_metadata': 'jsonb',
                    'occurred_at': 'timestamptz',
                    'version': 'integer'
                },
                'snapshot_table': {
                    'aggregate_id': 'uuid',
                    'version': 'integer',
                    'state': 'jsonb',
                    'created_at': 'timestamptz'
                },
                'projection_tables': 'domain_specific'
            },
            constraints=[
                'Append-only writes',
                'No updates allowed',
                'Event ordering critical'
            ],
            benefits=[
                'Complete audit trail',
                'Event replay capability',
                'Temporal queries'
            ],
            trade_offs=[
                'Storage growth',
                'Query complexity',
                'Eventual consistency'
            ],
            example_schema={
                'sql': '''
                CREATE TABLE events (
                    id BIGSERIAL PRIMARY KEY,
                    aggregate_id UUID NOT NULL,
                    aggregate_type VARCHAR(255) NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    event_data JSONB NOT NULL,
                    event_metadata JSONB DEFAULT '{}',
                    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    version INTEGER NOT NULL,
                    UNIQUE(aggregate_id, version)
                );

                CREATE INDEX idx_events_aggregate ON events(aggregate_id, version);
                CREATE INDEX idx_events_type ON events(event_type, occurred_at);
                '''
            },
            migration_strategy={
                'event_replay': True,
                'projection_rebuild': True
            }
        )

        # 5. 다국어 지원 패턴
        patterns['multilingual'] = DataModelPattern(
            id='multilingual',
            name='Multilingual Data Pattern',
            category='internationalization',
            description='Support for multiple languages in data model',
            use_cases=[
                'Product catalogs',
                'Content management',
                'User interfaces',
                'Documentation systems'
            ],
            structure={
                'approaches': {
                    'column_per_language': {
                        'structure': 'name_en, name_fr, name_es',
                        'pros': 'Simple queries',
                        'cons': 'Schema changes for new languages'
                    },
                    'translation_table': {
                        'structure': 'separate translations table',
                        'pros': 'Flexible language addition',
                        'cons': 'Join complexity'
                    },
                    'json_translations': {
                        'structure': "translations JSONB {'en': '...', 'fr': '...'}",
                        'pros': 'Flexible and simple',
                        'cons': 'Index limitations'
                    }
                }
            },
            constraints=[
                'Query performance',
                'Index strategy',
                'Fallback language logic'
            ],
            benefits=[
                'Global application support',
                'Dynamic language addition',
                'Centralized translation'
            ],
            trade_offs=[
                'Storage overhead',
                'Query complexity',
                'Cache invalidation'
            ],
            example_schema={
                'translation_table_approach': '''
                -- Main entity table
                CREATE TABLE products (
                    id UUID PRIMARY KEY,
                    sku VARCHAR(100) UNIQUE,
                    price DECIMAL(10,2),
                    created_at TIMESTAMPTZ
                );

                -- Translations table
                CREATE TABLE product_translations (
                    id UUID PRIMARY KEY,
                    product_id UUID REFERENCES products(id),
                    language_code VARCHAR(5),
                    name VARCHAR(255),
                    description TEXT,
                    UNIQUE(product_id, language_code)
                );

                -- Optimized view
                CREATE VIEW products_localized AS
                SELECT p.*,
                       COALESCE(t.name, dt.name) as name,
                       COALESCE(t.description, dt.description) as description
                FROM products p
                LEFT JOIN product_translations t ON p.id = t.product_id
                    AND t.language_code = current_setting('app.language')
                LEFT JOIN product_translations dt ON p.id = dt.product_id
                    AND dt.language_code = 'en'; -- fallback
                '''
            },
            migration_strategy={
                'from_single_language': 'gradual_extraction',
                'add_language': 'copy_from_default'
            }
        )

        return patterns

    async def recommend_data_patterns(
        self,
        data_requirements: List[Dict[str, Any]],
        scalability_needs: Dict[str, Any]
    ) -> List[DataModelPattern]:
        """데이터 요구사항에 맞는 패턴 추천"""

        recommendations = []

        # 데이터 특성 분석
        data_characteristics = self._analyze_data_characteristics(
            data_requirements
        )

        # 패턴 매칭
        for characteristic in data_characteristics:
            if characteristic['type'] == 'temporal':
                recommendations.append(self.patterns['time_series'])

            elif characteristic['type'] == 'multi_type_association':
                recommendations.append(self.patterns['polymorphic'])

            elif characteristic.get('soft_delete_required'):
                recommendations.append(self.patterns['soft_delete'])

            elif characteristic.get('audit_required'):
                recommendations.append(self.patterns['event_store'])

            elif characteristic.get('multilingual'):
                recommendations.append(self.patterns['multilingual'])

        # 확장성 요구사항 기반 조정
        recommendations = self._adjust_for_scalability(
            recommendations,
            scalability_needs
        )

        return recommendations
```

**검증 기준**:

- [ ] 실용적인 데이터 패턴
- [ ] 구체적인 스키마 예제
- [ ] 마이그레이션 전략 포함
- [ ] 성능 고려사항 명시

#### SubTask 4.34.4: 통합 패턴 라이브러리

**담당자**: 통합 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/integration_pattern_library.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class IntegrationPattern:
    id: str
    name: str
    category: str
    description: str
    use_cases: List[str]
    components: List[Dict[str, Any]]
    communication_style: str  # sync, async, streaming
    implementation: Dict[str, Any]
    error_handling: Dict[str, Any]
    monitoring: Dict[str, Any]
    example_scenario: Dict[str, Any]

class IntegrationPatternLibrary:
    """통합 패턴 라이브러리"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.scenario_analyzer = ScenarioAnalyzer()
        self.pattern_composer = PatternComposer()

    def _initialize_patterns(self) -> Dict[str, IntegrationPattern]:
        """통합 패턴 초기화"""

        patterns = {}

        # 1. API Gateway 패턴
        patterns['api_gateway'] = IntegrationPattern(
            id='api_gateway',
            name='API Gateway Pattern',
            category='api_management',
            description='Single entry point for all client requests',
            use_cases=[
                'Microservices architecture',
                'Mobile backend',
                'Partner API management',
                'Rate limiting and throttling'
            ],
            components=[
                {
                    'name': 'Gateway',
                    'responsibilities': [
                        'Request routing',
                        'Authentication',
                        'Rate limiting',
                        'Response aggregation'
                    ]
                },
                {
                    'name': 'ServiceRegistry',
                    'maintains': 'service_endpoints'
                },
                {
                    'name': 'LoadBalancer',
                    'distributes': 'requests'
                }
            ],
            communication_style='sync',
            implementation={
                'routing_strategies': {
                    'path_based': '/api/v1/users -> user-service',
                    'header_based': 'X-Service-Version',
                    'query_based': '?service=users'
                },
                'features': {
                    'authentication': ['JWT', 'OAuth2', 'API_Key'],
                    'rate_limiting': {
                        'strategies': ['token_bucket', 'sliding_window'],
                        'limits': 'per_client_per_endpoint'
                    },
                    'caching': {
                        'levels': ['edge', 'gateway', 'service'],
                        'invalidation': 'event_based'
                    },
                    'transformation': {
                        'request': 'protocol_translation',
                        'response': 'format_conversion'
                    }
                }
            },
            error_handling={
                'retry_policy': {
                    'max_attempts': 3,
                    'backoff': 'exponential'
                },
                'circuit_breaker': True,
                'fallback': 'cached_response'
            },
            monitoring={
                'metrics': [
                    'request_rate',
                    'error_rate',
                    'latency_percentiles',
                    'backend_health'
                ],
                'logging': 'structured',
                'tracing': 'distributed'
            },
            example_scenario={
                'client_request': 'GET /api/v1/orders/123',
                'gateway_actions': [
                    'Validate JWT token',
                    'Check rate limit',
                    'Route to order-service',
                    'Add correlation ID',
                    'Forward request',
                    'Cache response'
                ]
            }
        )

        # 2. Backend for Frontend (BFF) 패턴
        patterns['bff'] = IntegrationPattern(
            id='bff',
            name='Backend for Frontend Pattern',
            category='api_aggregation',
            description='Dedicated backend for each frontend type',
            use_cases=[
                'Multiple client types',
                'Optimized mobile APIs',
                'Frontend-specific logic',
                'Response aggregation'
            ],
            components=[
                {
                    'name': 'MobileBFF',
                    'optimizes_for': 'mobile_constraints'
                },
                {
                    'name': 'WebBFF',
                    'optimizes_for': 'web_requirements'
                },
                {
                    'name': 'ServiceAggregator',
                    'combines': 'multiple_service_calls'
                }
            ],
            communication_style='sync',
            implementation={
                'aggregation_strategies': {
                    'parallel_calls': 'Promise.all() or asyncio.gather()',
                    'sequential_calls': 'when_dependent',
                    'conditional_calls': 'based_on_client_needs'
                },
                'optimization_techniques': {
                    'field_filtering': 'GraphQL-like selection',
                    'data_compression': 'gzip, brotli',
                    'pagination': 'cursor_based',
                    'partial_responses': '206 status'
                }
            },
            error_handling={
                'partial_failure': 'return_available_data',
                'timeout_strategy': 'aggressive_timeouts',
                'degraded_mode': True
            },
            monitoring={
                'client_metrics': True,
                'backend_metrics': True,
                'aggregation_performance': True
            },
            example_scenario={
                'mobile_request': 'GET /mobile/api/dashboard',
                'bff_orchestration': [
                    'Fetch user profile (user-service)',
                    'Fetch notifications (notification-service)',
                    'Fetch summary stats (analytics-service)',
                    'Combine and optimize response',
                    'Compress for mobile'
                ]
            }
        )

        # 3. Event-Driven Integration 패턴
        patterns['event_driven'] = IntegrationPattern(
            id='event_driven',
            name='Event-Driven Integration Pattern',
            category='async_messaging',
            description='Loosely coupled integration via events',
            use_cases=[
                'Microservices communication',
                'Real-time updates',
                'CQRS implementations',
                'Workflow orchestration'
            ],
            components=[
                {
                    'name': 'EventBus',
                    'type': 'message_broker',
                    'examples': ['Kafka', 'RabbitMQ', 'AWS EventBridge']
                },
                {
                    'name': 'EventProducer',
                    'publishes': 'domain_events'
                },
                {
                    'name': 'EventConsumer',
                    'subscribes_to': 'event_topics'
                },
                {
                    'name': 'EventStore',
                    'persists': 'event_history'
                }
            ],
            communication_style='async',
            implementation={
                'event_schema': {
                    'header': {
                        'event_id': 'uuid',
                        'event_type': 'string',
                        'timestamp': 'iso8601',
                        'correlation_id': 'uuid',
                        'source': 'service_name'
                    },
                    'payload': 'domain_specific',
                    'metadata': {
                        'version': 'semver',
                        'schema_url': 'string'
                    }
                },
                'delivery_guarantees': {
                    'at_least_once': 'default',
                    'exactly_once': 'transactional_outbox',
                    'ordering': 'partition_key_based'
                },
                'patterns': {
                    'event_sourcing': True,
                    'event_collaboration': True,
                    'event_notification': True
                }
            },
            error_handling={
                'dead_letter_queue': True,
                'retry_with_backoff': True,
                'poison_message_handling': True,
                'compensating_transactions': True
            },
            monitoring={
                'event_flow_visualization': True,
                'lag_monitoring': True,
                'throughput_metrics': True
            },
            example_scenario={
                'order_placed_event': {
                    'producers': ['order-service'],
                    'consumers': [
                        'inventory-service (reserve items)',
                        'payment-service (charge card)',
                        'shipping-service (prepare shipment)',
                        'email-service (send confirmation)'
                    ]
                }
            }
        )

        # 4. Strangler Fig 패턴
        patterns['strangler_fig'] = IntegrationPattern(
            id='strangler_fig',
            name='Strangler Fig Pattern',
            category='migration',
            description='Gradually replace legacy system',
            use_cases=[
                'Legacy modernization',
                'Monolith to microservices',
                'Technology migration',
                'Risk-free replacement'
            ],
            components=[
                {
                    'name': 'Facade',
                    'routes_between': ['legacy', 'new_system']
                },
                {
                    'name': 'Router',
                    'decides': 'request_destination'
                },
                {
                    'name': 'Synchronizer',
                    'maintains': 'data_consistency'
                }
            ],
            communication_style='sync',
            implementation={
                'routing_strategies': {
                    'feature_flag': 'toggle_per_feature',
                    'canary': 'percentage_based',
                    'user_based': 'specific_user_groups',
                    'url_based': 'path_patterns'
                },
                'migration_phases': [
                    {
                        'phase': 'identify',
                        'action': 'Map legacy boundaries'
                    },
                    {
                        'phase': 'transform',
                        'action': 'Create new implementation'
                    },
                    {
                        'phase': 'coexist',
                        'action': 'Route between systems'
                    },
                    {
                        'phase': 'eliminate',
                        'action': 'Remove legacy code'
                    }
                ],
                'data_sync': {
                    'strategies': ['dual_write', 'event_sync', 'batch_sync'],
                    'conflict_resolution': 'last_write_wins'
                }
            },
            error_handling={
                'fallback_to_legacy': True,
                'monitoring_both_systems': True,
                'gradual_rollback': True
            },
            monitoring={
                'comparison_metrics': True,
                'migration_progress': True,
                'system_parity': True
            },
            example_scenario={
                'ecommerce_migration': {
                    'legacy': 'monolithic_jsp_app',
                    'new': 'microservices_react',
                    'current_progress': '40%',
                    'migrated_features': [
                        'product_catalog',
                        'user_authentication'
                    ],
                    'remaining': [
                        'checkout_process',
                        'order_management'
                    ]
                }
            }
        )

        # 5. Anti-Corruption Layer 패턴
        patterns['anti_corruption_layer'] = IntegrationPattern(
            id='anti_corruption_layer',
            name='Anti-Corruption Layer Pattern',
            category='boundary',
            description='Isolate different subsystems with translation layer',
            use_cases=[
                'Third-party integrations',
                'Legacy system boundaries',
                'Different domain models',
                'External API consumption'
            ],
            components=[
                {
                    'name': 'Translator',
                    'converts': 'between_models'
                },
                {
                    'name': 'Adapter',
                    'wraps': 'external_interface'
                },
                {
                    'name': 'Facade',
                    'simplifies': 'complex_interface'
                }
            ],
            communication_style='sync',
            implementation={
                'translation_types': {
                    'data_model': 'DTO to domain model',
                    'protocol': 'REST to gRPC',
                    'format': 'XML to JSON',
                    'semantics': 'external to internal concepts'
                },
                'isolation_techniques': {
                    'interface_segregation': True,
                    'dependency_inversion': True,
                    'repository_pattern': True
                }
            },
            error_handling={
                'validation': 'strict_input_validation',
                'transformation_errors': 'detailed_logging',
                'external_failures': 'circuit_breaker'
            },
            monitoring={
                'translation_performance': True,
                'external_api_health': True,
                'data_quality_metrics': True
            },
            example_scenario={
                'payment_provider_integration': {
                    'external_api': 'Stripe',
                    'internal_model': 'PaymentDomain',
                    'translations': [
                        'Stripe Customer -> User',
                        'Stripe Charge -> Payment',
                        'Webhook -> Domain Event'
                    ]
                }
            }
        )

        return patterns

    async def recommend_integration_patterns(
        self,
        integration_requirements: List[Dict[str, Any]],
        architecture_context: Dict[str, Any]
    ) -> List[IntegrationPattern]:
        """통합 요구사항에 맞는 패턴 추천"""

        recommendations = []

        # 통합 시나리오 분석
        scenarios = await self.scenario_analyzer.analyze(
            integration_requirements,
            architecture_context
        )

        # 각 시나리오에 맞는 패턴 선택
        for scenario in scenarios:
            if scenario['type'] == 'api_aggregation':
                if scenario.get('multiple_clients'):
                    recommendations.append(self.patterns['bff'])
                else:
                    recommendations.append(self.patterns['api_gateway'])

            elif scenario['type'] == 'async_communication':
                recommendations.append(self.patterns['event_driven'])

            elif scenario['type'] == 'legacy_migration':
                recommendations.append(self.patterns['strangler_fig'])

            elif scenario['type'] == 'external_integration':
                recommendations.append(self.patterns['anti_corruption_layer'])

        # 패턴 조합 최적화
        optimized_patterns = await self.pattern_composer.optimize(
            recommendations,
            architecture_context
        )

        return optimized_patterns
```

**검증 기준**:

- [ ] 주요 통합 패턴 포함
- [ ] 실제 시나리오 예제
- [ ] 에러 처리 전략 명시
- [ ] 모니터링 가이드라인

### Task 4.35: 컴포넌트 검증 시스템

#### SubTask 4.35.1: 컴포넌트 일관성 검증기

**담당자**: 품질 검증 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/consistency_validator.py
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

@dataclass
class ConsistencyViolation:
    component_id: str
    violation_type: str
    severity: str  # critical, high, medium, low
    description: str
    affected_components: List[str]
    resolution_suggestion: str
    auto_fixable: bool

@dataclass
class ConsistencyReport:
    is_consistent: bool
    violations: List[ConsistencyViolation]
    consistency_score: float  # 0-100
    validation_coverage: float  # 0-100
    recommendations: List[str]
    validation_metadata: Dict[str, Any]

class ComponentConsistencyValidator:
    """컴포넌트 일관성 검증"""

    def __init__(self):
        self.naming_validator = NamingConsistencyValidator()
        self.interface_validator = InterfaceConsistencyValidator()
        self.data_flow_validator = DataFlowConsistencyValidator()
        self.pattern_validator = PatternConsistencyValidator()
        self.dependency_validator = DependencyConsistencyValidator()

    async def validate_consistency(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> ConsistencyReport:
        """전체 컴포넌트 일관성 검증"""

        violations = []

        # 1. 네이밍 일관성 검증
        naming_violations = await self._validate_naming_consistency(components)
        violations.extend(naming_violations)

        # 2. 인터페이스 일관성 검증
        interface_violations = await self._validate_interface_consistency(
            components
        )
        violations.extend(interface_violations)

        # 3. 데이터 흐름 일관성 검증
        data_flow_violations = await self._validate_data_flow_consistency(
            components,
            architecture
        )
        violations.extend(data_flow_violations)

        # 4. 패턴 일관성 검증
        pattern_violations = await self._validate_pattern_consistency(
            components,
            architecture.patterns
        )
        violations.extend(pattern_violations)

        # 5. 의존성 일관성 검증
        dependency_violations = await self._validate_dependency_consistency(
            components
        )
        violations.extend(dependency_violations)

        # 6. 기술 스택 일관성 검증
        tech_stack_violations = await self._validate_tech_stack_consistency(
            components
        )
        violations.extend(tech_stack_violations)

        # 7. 보안 정책 일관성 검증
        security_violations = await self._validate_security_consistency(
            components
        )
        violations.extend(security_violations)

        # 8. 일관성 점수 계산
        consistency_score = self._calculate_consistency_score(
            violations,
            components
        )

        # 9. 검증 커버리지 계산
        validation_coverage = self._calculate_validation_coverage(
            components
        )

        # 10. 권고사항 생성
        recommendations = await self._generate_recommendations(
            violations,
            consistency_score
        )

        return ConsistencyReport(
            is_consistent=len(violations) == 0,
            violations=violations,
            consistency_score=consistency_score,
            validation_coverage=validation_coverage,
            recommendations=recommendations,
            validation_metadata={
                'total_components': len(components),
                'validation_timestamp': datetime.utcnow(),
                'validation_rules_applied': self._get_applied_rules()
            }
        )

    async def _validate_naming_consistency(
        self,
        components: List[ComponentDecision]
    ) -> List[ConsistencyViolation]:
        """네이밍 일관성 검증"""

        violations = []
        naming_patterns = {}

        # 네이밍 패턴 추출
        for component in components:
            pattern = self._extract_naming_pattern(component.name)
            if pattern not in naming_patterns:
                naming_patterns[pattern] = []
            naming_patterns[pattern].append(component)

        # 일관성 검사
        if len(naming_patterns) > 1:
            # 가장 많이 사용된 패턴 찾기
            dominant_pattern = max(
                naming_patterns.items(),
                key=lambda x: len(x[1])
            )[0]

            for pattern, components_list in naming_patterns.items():
                if pattern != dominant_pattern:
                    for comp in components_list:
                        violations.append(ConsistencyViolation(
                            component_id=comp.id,
                            violation_type='naming_inconsistency',
                            severity='medium',
                            description=f"Component naming pattern '{pattern}' differs from dominant pattern '{dominant_pattern}'",
                            affected_components=[c.id for c in components_list],
                            resolution_suggestion=f"Rename to follow '{dominant_pattern}' pattern",
                            auto_fixable=True
                        ))

        # 예약어 및 금지어 검사
        for component in components:
            if self._contains_reserved_words(component.name):
                violations.append(ConsistencyViolation(
                    component_id=component.id,
                    violation_type='reserved_word_usage',
                    severity='high',
                    description=f"Component name contains reserved word",
                    affected_components=[component.id],
                    resolution_suggestion="Choose a different name avoiding reserved words",
                    auto_fixable=False
                ))

        return violations

    async def _validate_interface_consistency(
        self,
        components: List[ComponentDecision]
    ) -> List[ConsistencyViolation]:
        """인터페이스 일관성 검증"""

        violations = []

        # API 버전 일관성
        api_versions = {}
        for component in components:
            if component.type == ComponentType.API_ENDPOINT:
                version = self._extract_api_version(component)
                if version not in api_versions:
                    api_versions[version] = []
                api_versions[version].append(component)

        if len(api_versions) > 1:
            latest_version = max(api_versions.keys())
            for version, components_list in api_versions.items():
                if version != latest_version:
                    for comp in components_list:
                        violations.append(ConsistencyViolation(
                            component_id=comp.id,
                            violation_type='api_version_inconsistency',
                            severity='high',
                            description=f"API version {version} is not the latest ({latest_version})",
                            affected_components=[c.id for c in components_list],
                            resolution_suggestion=f"Update to API version {latest_version}",
                            auto_fixable=False
                        ))

        # 메서드 시그니처 일관성
        similar_operations = self._find_similar_operations(components)
        for op_group in similar_operations:
            signatures = set()
            for comp, operation in op_group:
                sig = self._get_method_signature(operation)
                signatures.add(sig)

            if len(signatures) > 1:
                violations.append(ConsistencyViolation(
                    component_id=op_group[0][0].id,
                    violation_type='method_signature_inconsistency',
                    severity='medium',
                    description='Similar operations have different signatures',
                    affected_components=[comp.id for comp, _ in op_group],
                    resolution_suggestion='Standardize method signatures across similar operations',
                    auto_fixable=False
                ))

        return violations

    async def _validate_data_flow_consistency(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> List[ConsistencyViolation]:
        """데이터 흐름 일관성 검증"""

        violations = []

        # 데이터 타입 불일치 검사
        for relationship in architecture.relationships:
            source_comp = next((c for c in components if c.id == relationship['source']), None)
            target_comp = next((c for c in components if c.id == relationship['target']), None)

            if source_comp and target_comp:
                # 출력과 입력 타입 매칭 검사
                output_type = self._get_output_type(source_comp, relationship)
                input_type = self._get_input_type(target_comp, relationship)

                if not self._are_types_compatible(output_type, input_type):
                    violations.append(ConsistencyViolation(
                        component_id=source_comp.id,
                        violation_type='data_type_mismatch',
                        severity='critical',
                        description=f"Output type '{output_type}' incompatible with input type '{input_type}'",
                        affected_components=[source_comp.id, target_comp.id],
                        resolution_suggestion='Add data transformation or update types to match',
                        auto_fixable=False
                    ))

        # 순환 데이터 흐름 검사
        cycles = self._detect_data_flow_cycles(components, architecture)
        for cycle in cycles:
            violations.append(ConsistencyViolation(
                component_id=cycle[0],
                violation_type='circular_data_flow',
                severity='high',
                description=f"Circular data dependency detected: {' -> '.join(cycle)}",
                affected_components=cycle,
                resolution_suggestion='Refactor to remove circular dependency',
                auto_fixable=False
            ))

        return violations

    def _calculate_consistency_score(
        self,
        violations: List[ConsistencyViolation],
        components: List[ComponentDecision]
    ) -> float:
        """일관성 점수 계산"""

        if not components:
            return 100.0

        # 위반 사항별 가중치
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }

        # 총 위반 점수 계산
        total_penalty = sum(
            severity_weights.get(v.severity, 0)
            for v in violations
        )

        # 컴포넌트당 최대 허용 점수
        max_penalty = len(components) * 5

        # 점수 계산 (0-100)
        score = max(0, 100 - (total_penalty / max_penalty * 100))

        return round(score, 1)
```

**검증 기준**:

- [ ] 포괄적인 일관성 검사
- [ ] 자동 수정 가능 항목 식별
- [ ] 명확한 해결 제안
- [ ] 정량적 일관성 점수

---

#### SubTask 4.35.2: 컴포넌트 완전성 검증기

**담당자**: 시스템 검증 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/completeness_validator.py
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

@dataclass
class CompletenessCriteria:
    category: str
    required_elements: List[str]
    optional_elements: List[str]
    validation_rules: List[Dict[str, Any]]

@dataclass
class CompletenessGap:
    component_id: str
    gap_type: str
    missing_elements: List[str]
    severity: str  # critical, high, medium, low
    impact: str
    resolution_steps: List[str]
    estimated_effort: int  # story points

@dataclass
class CompletenessReport:
    overall_completeness: float  # 0-100
    component_scores: Dict[str, float]
    gaps: List[CompletenessGap]
    coverage_by_category: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]

class ComponentCompletenessValidator:
    """컴포넌트 완전성 검증"""

    def __init__(self):
        self.criteria_registry = self._initialize_criteria()
        self.gap_analyzer = GapAnalyzer()
        self.impact_assessor = ImpactAssessor()
        self.roadmap_generator = RoadmapGenerator()

    def _initialize_criteria(self) -> Dict[str, CompletenessCriteria]:
        """완전성 기준 초기화"""

        criteria = {}

        # UI 컴포넌트 완전성 기준
        criteria['ui_component'] = CompletenessCriteria(
            category='ui_component',
            required_elements=[
                'props_definition',
                'state_management',
                'event_handlers',
                'render_logic',
                'styling',
                'accessibility',
                'error_boundaries',
                'loading_states'
            ],
            optional_elements=[
                'animations',
                'internationalization',
                'theme_support',
                'performance_optimization'
            ],
            validation_rules=[
                {
                    'rule': 'must_have_prop_types',
                    'check': lambda c: 'props' in c.properties
                },
                {
                    'rule': 'must_handle_errors',
                    'check': lambda c: 'error_handling' in c.properties
                }
            ]
        )

        # 백엔드 서비스 완전성 기준
        criteria['backend_service'] = CompletenessCriteria(
            category='backend_service',
            required_elements=[
                'api_endpoints',
                'data_validation',
                'error_handling',
                'authentication',
                'authorization',
                'logging',
                'monitoring',
                'documentation'
            ],
            optional_elements=[
                'caching',
                'rate_limiting',
                'versioning',
                'webhooks'
            ],
            validation_rules=[
                {
                    'rule': 'must_have_auth',
                    'check': lambda c: 'authentication' in c.properties
                },
                {
                    'rule': 'must_validate_input',
                    'check': lambda c: 'validation' in c.interfaces
                }
            ]
        )

        # 데이터 모델 완전성 기준
        criteria['data_model'] = CompletenessCriteria(
            category='data_model',
            required_elements=[
                'field_definitions',
                'primary_key',
                'indexes',
                'constraints',
                'relationships',
                'validation_rules',
                'migration_scripts'
            ],
            optional_elements=[
                'triggers',
                'stored_procedures',
                'views',
                'partitioning'
            ],
            validation_rules=[
                {
                    'rule': 'must_have_primary_key',
                    'check': lambda c: 'primary_key' in c.properties
                }
            ]
        )

        return criteria

    async def validate_completeness(
        self,
        components: List[ComponentDecision],
        requirements: List[ParsedRequirement]
    ) -> CompletenessReport:
        """컴포넌트 완전성 검증"""

        gaps = []
        component_scores = {}

        # 1. 각 컴포넌트별 완전성 검사
        for component in components:
            criteria = self.criteria_registry.get(
                component.type.value,
                self.criteria_registry['backend_service']  # default
            )

            # 필수 요소 검사
            missing_required = self._check_required_elements(
                component,
                criteria
            )

            # 선택 요소 검사
            missing_optional = self._check_optional_elements(
                component,
                criteria
            )

            # 검증 규칙 적용
            validation_failures = self._apply_validation_rules(
                component,
                criteria
            )

            # 갭 분석
            if missing_required or validation_failures:
                gap = CompletenessGap(
                    component_id=component.id,
                    gap_type='missing_required_elements',
                    missing_elements=missing_required + validation_failures,
                    severity=self._determine_severity(
                        missing_required,
                        validation_failures
                    ),
                    impact=await self.impact_assessor.assess_impact(
                        component,
                        missing_required
                    ),
                    resolution_steps=self._generate_resolution_steps(
                        component,
                        missing_required,
                        validation_failures
                    ),
                    estimated_effort=self._estimate_effort(
                        missing_required,
                        validation_failures
                    )
                )
                gaps.append(gap)

            # 컴포넌트 점수 계산
            component_scores[component.id] = self._calculate_component_score(
                criteria,
                missing_required,
                missing_optional,
                validation_failures
            )

        # 2. 요구사항 커버리지 검사
        coverage_gaps = await self._check_requirement_coverage(
            components,
            requirements
        )
        gaps.extend(coverage_gaps)

        # 3. 통합 포인트 완전성 검사
        integration_gaps = await self._check_integration_completeness(
            components
        )
        gaps.extend(integration_gaps)

        # 4. 카테고리별 커버리지 계산
        coverage_by_category = self._calculate_category_coverage(
            components,
            component_scores
        )

        # 5. 전체 완전성 점수
        overall_completeness = self._calculate_overall_completeness(
            component_scores,
            coverage_by_category
        )

        # 6. 권고사항 생성
        recommendations = await self._generate_recommendations(
            gaps,
            overall_completeness
        )

        # 7. 완성 로드맵 생성
        roadmap = await self.roadmap_generator.generate_roadmap(
            gaps,
            components,
            requirements
        )

        return CompletenessReport(
            overall_completeness=overall_completeness,
            component_scores=component_scores,
            gaps=gaps,
            coverage_by_category=coverage_by_category,
            recommendations=recommendations,
            roadmap=roadmap
        )

    def _check_required_elements(
        self,
        component: ComponentDecision,
        criteria: CompletenessCriteria
    ) -> List[str]:
        """필수 요소 검사"""

        missing = []

        for element in criteria.required_elements:
            if not self._has_element(component, element):
                missing.append(element)

        return missing

    def _has_element(
        self,
        component: ComponentDecision,
        element: str
    ) -> bool:
        """요소 존재 여부 확인"""

        # 속성에서 확인
        if element in component.properties:
            return True

        # 인터페이스에서 확인
        if element in component.interfaces:
            return True

        # 특수 케이스 처리
        element_mappings = {
            'props_definition': lambda c: 'props' in c.properties,
            'state_management': lambda c: 'state' in c.properties,
            'event_handlers': lambda c: any('on' in k for k in c.properties.get('events', [])),
            'api_endpoints': lambda c: 'endpoints' in c.interfaces,
            'field_definitions': lambda c: 'fields' in c.properties
        }

        if element in element_mappings:
            return element_mappings[element](component)

        return False

    async def _check_requirement_coverage(
        self,
        components: List[ComponentDecision],
        requirements: List[ParsedRequirement]
    ) -> List[CompletenessGap]:
        """요구사항 커버리지 검사"""

        gaps = []

        # 각 요구사항이 컴포넌트에 반영되었는지 확인
        for requirement in requirements:
            covering_components = [
                c for c in components
                if requirement.id in c.requirements
            ]

            if not covering_components:
                gap = CompletenessGap(
                    component_id='system',
                    gap_type='uncovered_requirement',
                    missing_elements=[f"Requirement: {requirement.description}"],
                    severity='high',
                    impact=f"Requirement {requirement.id} is not implemented",
                    resolution_steps=[
                        f"Create component to implement {requirement.id}",
                        "Or add requirement to existing component"
                    ],
                    estimated_effort=self._estimate_requirement_effort(requirement)
                )
                gaps.append(gap)

        return gaps

    def _calculate_component_score(
        self,
        criteria: CompletenessCriteria,
        missing_required: List[str],
        missing_optional: List[str],
        validation_failures: List[str]
    ) -> float:
        """컴포넌트 완전성 점수 계산"""

        total_required = len(criteria.required_elements)
        total_optional = len(criteria.optional_elements)
        total_rules = len(criteria.validation_rules)

        # 필수 요소 점수 (70%)
        required_score = (
            (total_required - len(missing_required)) / total_required * 70
            if total_required > 0 else 70
        )

        # 선택 요소 점수 (20%)
        optional_score = (
            (total_optional - len(missing_optional)) / total_optional * 20
            if total_optional > 0 else 20
        )

        # 검증 규칙 점수 (10%)
        validation_score = (
            (total_rules - len(validation_failures)) / total_rules * 10
            if total_rules > 0 else 10
        )

        return round(required_score + optional_score + validation_score, 1)

    async def _generate_recommendations(
        self,
        gaps: List[CompletenessGap],
        overall_completeness: float
    ) -> List[Dict[str, Any]]:
        """권고사항 생성"""

        recommendations = []

        # 심각도별 갭 그룹화
        critical_gaps = [g for g in gaps if g.severity == 'critical']
        high_gaps = [g for g in gaps if g.severity == 'high']

        # 긴급 조치 필요 항목
        if critical_gaps:
            recommendations.append({
                'priority': 'immediate',
                'title': 'Critical Gaps Requiring Immediate Attention',
                'items': [
                    {
                        'component': g.component_id,
                        'issue': g.missing_elements,
                        'action': g.resolution_steps[0] if g.resolution_steps else 'Review and fix'
                    }
                    for g in critical_gaps[:5]  # Top 5
                ]
            })

        # 단계별 개선 계획
        if overall_completeness < 80:
            recommendations.append({
                'priority': 'high',
                'title': 'Phased Improvement Plan',
                'phases': [
                    {
                        'phase': 1,
                        'focus': 'Complete all required elements',
                        'target_completeness': 85,
                        'estimated_effort': sum(g.estimated_effort for g in high_gaps)
                    },
                    {
                        'phase': 2,
                        'focus': 'Add optional enhancements',
                        'target_completeness': 95,
                        'estimated_effort': 20  # story points
                    }
                ]
            })

        return recommendations
```

**검증 기준**:

- [ ] 포괄적인 완전성 검사
- [ ] 요구사항 커버리지 확인
- [ ] 명확한 갭 분석
- [ ] 실행 가능한 로드맵

#### SubTask 4.35.3: 컴포넌트 호환성 검증기

**담당자**: 시스템 통합 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/compatibility_validator.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import semver

@dataclass
class CompatibilityIssue:
    source_component: str
    target_component: str
    issue_type: str
    severity: str  # blocker, warning, info
    description: str
    technical_details: Dict[str, Any]
    resolution_options: List[str]
    workaround_available: bool

@dataclass
class CompatibilityMatrix:
    components: List[str]
    compatibility_scores: Dict[Tuple[str, str], float]
    issues: List[CompatibilityIssue]
    technology_conflicts: List[Dict[str, Any]]
    version_conflicts: List[Dict[str, Any]]
    integration_risks: List[Dict[str, Any]]

class ComponentCompatibilityValidator:
    """컴포넌트 호환성 검증"""

    def __init__(self):
        self.tech_compatibility_db = TechnologyCompatibilityDatabase()
        self.version_resolver = VersionResolver()
        self.api_compatibility_checker = APICompatibilityChecker()
        self.data_format_validator = DataFormatValidator()

    async def validate_compatibility(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> CompatibilityMatrix:
        """컴포넌트 간 호환성 검증"""

        issues = []
        compatibility_scores = {}

        # 1. 기술 스택 호환성 검사
        tech_conflicts = await self._check_technology_compatibility(components)
        issues.extend(self._tech_conflicts_to_issues(tech_conflicts))

        # 2. 버전 호환성 검사
        version_conflicts = await self._check_version_compatibility(components)
        issues.extend(self._version_conflicts_to_issues(version_conflicts))

        # 3. API 호환성 검사
        api_issues = await self._check_api_compatibility(
            components,
            architecture.relationships
        )
        issues.extend(api_issues)

        # 4. 데이터 형식 호환성 검사
        data_format_issues = await self._check_data_format_compatibility(
            components,
            architecture
        )
        issues.extend(data_format_issues)

        # 5. 통신 프로토콜 호환성 검사
        protocol_issues = await self._check_protocol_compatibility(
            components,
            architecture
        )
        issues.extend(protocol_issues)

        # 6. 보안 정책 호환성 검사
        security_issues = await self._check_security_compatibility(components)
        issues.extend(security_issues)

        # 7. 성능 특성 호환성 검사
        performance_issues = await self._check_performance_compatibility(
            components,
            architecture
        )
        issues.extend(performance_issues)

        # 8. 호환성 점수 계산
        for i, comp1 in enumerate(components):
            for j, comp2 in enumerate(components):
                if i < j:  # 중복 방지
                    score = await self._calculate_compatibility_score(
                        comp1,
                        comp2,
                        issues
                    )
                    compatibility_scores[(comp1.id, comp2.id)] = score

        # 9. 통합 위험 평가
        integration_risks = await self._assess_integration_risks(
            components,
            issues
        )

        return CompatibilityMatrix(
            components=[c.id for c in components],
            compatibility_scores=compatibility_scores,
            issues=issues,
            technology_conflicts=tech_conflicts,
            version_conflicts=version_conflicts,
            integration_risks=integration_risks
        )

    async def _check_technology_compatibility(
        self,
        components: List[ComponentDecision]
    ) -> List[Dict[str, Any]]:
        """기술 스택 호환성 검사"""

        conflicts = []

        # 기술 스택 추출
        tech_stacks = {}
        for component in components:
            tech_stacks[component.id] = set(component.technology_stack)

        # 프론트엔드 프레임워크 충돌 검사
        frontend_frameworks = {
            'react', 'vue', 'angular', 'svelte', 'solid'
        }

        frontend_components = [
            c for c in components
            if c.type == ComponentType.UI_COMPONENT
        ]

        used_frameworks = set()
        for comp in frontend_components:
            comp_frameworks = tech_stacks[comp.id] & frontend_frameworks
            if comp_frameworks:
                used_frameworks.update(comp_frameworks)

        if len(used_frameworks) > 1:
            conflicts.append({
                'type': 'multiple_frontend_frameworks',
                'frameworks': list(used_frameworks),
                'affected_components': [c.id for c in frontend_components],
                'severity': 'warning',
                'recommendation': 'Consider using a single frontend framework'
            })

        # 백엔드 언어 호환성
        backend_languages = {
            'python': {'compatible_with': ['python', 'javascript', 'java']},
            'javascript': {'compatible_with': ['javascript', 'python', 'java']},
            'java': {'compatible_with': ['java', 'python', 'javascript']},
            'go': {'compatible_with': ['go', 'python', 'javascript']},
            'rust': {'compatible_with': ['rust', 'python', 'javascript']}
        }

        backend_components = [
            c for c in components
            if c.type == ComponentType.BACKEND_SERVICE
        ]

        for i, comp1 in enumerate(backend_components):
            for comp2 in backend_components[i+1:]:
                lang1 = self._extract_language(tech_stacks[comp1.id])
                lang2 = self._extract_language(tech_stacks[comp2.id])

                if lang1 and lang2 and lang1 != lang2:
                    compat_info = backend_languages.get(lang1, {})
                    if lang2 not in compat_info.get('compatible_with', []):
                        conflicts.append({
                            'type': 'language_compatibility',
                            'component1': comp1.id,
                            'component2': comp2.id,
                            'language1': lang1,
                            'language2': lang2,
                            'severity': 'warning',
                            'recommendation': 'Use RPC or API for communication'
                        })

        return conflicts

    async def _check_version_compatibility(
        self,
        components: List[ComponentDecision]
    ) -> List[Dict[str, Any]]:
        """버전 호환성 검사"""

        conflicts = []

        # 공통 의존성 버전 추출
        dependencies = {}
        for component in components:
            comp_deps = component.properties.get('dependencies', {})
            for dep, version in comp_deps.items():
                if dep not in dependencies:
                    dependencies[dep] = {}
                dependencies[dep][component.id] = version

        # 버전 충돌 검사
        for dep, versions_by_component in dependencies.items():
            if len(set(versions_by_component.values())) > 1:
                # 버전 범위 해석
                try:
                    resolved_version = self.version_resolver.resolve(
                        list(versions_by_component.values())
                    )

                    if not resolved_version:
                        conflicts.append({
                            'type': 'version_conflict',
                            'dependency': dep,
                            'versions': versions_by_component,
                            'severity': 'blocker',
                            'recommendation': 'Align dependency versions'
                        })
                except Exception as e:
                    conflicts.append({
                        'type': 'version_resolution_error',
                        'dependency': dep,
                        'error': str(e),
                        'severity': 'warning'
                    })

        return conflicts

    async def _check_api_compatibility(
        self,
        components: List[ComponentDecision],
        relationships: List[Dict[str, Any]]
    ) -> List[CompatibilityIssue]:
        """API 호환성 검사"""

        issues = []

        for relationship in relationships:
            if relationship.get('type') == 'api_call':
                source = next((c for c in components if c.id == relationship['source']), None)
                target = next((c for c in components if c.id == relationship['target']), None)

                if source and target:
                    # 요청/응답 형식 호환성
                    source_format = source.interfaces.get('output_format', 'json')
                    target_format = target.interfaces.get('input_format', 'json')

                    if source_format != target_format:
                        issues.append(CompatibilityIssue(
                            source_component=source.id,
                            target_component=target.id,
                            issue_type='format_mismatch',
                            severity='blocker',
                            description=f"Output format '{source_format}' incompatible with input format '{target_format}'",
                            technical_details={
                                'source_format': source_format,
                                'target_format': target_format
                            },
                            resolution_options=[
                                'Add format converter',
                                'Standardize on single format',
                                'Use API gateway for transformation'
                            ],
                            workaround_available=True
                        ))

                    # API 버전 호환성
                    source_api_version = source.interfaces.get('api_version')
                    target_api_version = target.interfaces.get('supported_versions', [])

                    if source_api_version and target_api_version:
                        if source_api_version not in target_api_version:
                            issues.append(CompatibilityIssue(
                                source_component=source.id,
                                target_component=target.id,
                                issue_type='api_version_mismatch',
                                severity='warning',
                                description=f"API version {source_api_version} not in supported versions",
                                technical_details={
                                    'provided_version': source_api_version,
                                    'supported_versions': target_api_version
                                },
                                resolution_options=[
                                    'Update API version',
                                    'Add version adapter',
                                    'Support multiple versions'
                                ],
                                workaround_available=True
                            ))

        return issues

    async def _check_security_compatibility(
        self,
        components: List[ComponentDecision]
    ) -> List[CompatibilityIssue]:
        """보안 정책 호환성 검사"""

        issues = []

        # 인증 방식 호환성
        auth_methods = {}
        for component in components:
            auth = component.properties.get('authentication', {})
            if auth:
                auth_methods[component.id] = auth.get('method', 'none')

        # 서로 통신하는 컴포넌트 간 인증 방식 확인
        for comp1 in components:
            for comp2 in components:
                if comp1.id != comp2.id and self._components_communicate(comp1, comp2):
                    auth1 = auth_methods.get(comp1.id, 'none')
                    auth2 = auth_methods.get(comp2.id, 'none')

                    if auth1 != auth2 and auth1 != 'none' and auth2 != 'none':
                        issues.append(CompatibilityIssue(
                            source_component=comp1.id,
                            target_component=comp2.id,
                            issue_type='authentication_mismatch',
                            severity='warning',
                            description=f"Different authentication methods: {auth1} vs {auth2}",
                            technical_details={
                                'component1_auth': auth1,
                                'component2_auth': auth2
                            },
                            resolution_options=[
                                'Standardize authentication method',
                                'Use auth proxy/gateway',
                                'Implement auth translation layer'
                            ],
                            workaround_available=True
                        ))

        # 암호화 수준 호환성
        for comp1 in components:
            for comp2 in components:
                if comp1.id != comp2.id and self._components_communicate(comp1, comp2):
                    enc1 = comp1.properties.get('encryption', {}).get('level', 'none')
                    enc2 = comp2.properties.get('encryption', {}).get('level', 'none')

                    if enc1 != enc2 and (enc1 != 'none' or enc2 != 'none'):
                        issues.append(CompatibilityIssue(
                            source_component=comp1.id,
                            target_component=comp2.id,
                            issue_type='encryption_level_mismatch',
                            severity='blocker' if enc1 == 'none' or enc2 == 'none' else 'warning',
                            description='Mismatched encryption levels',
                            technical_details={
                                'component1_encryption': enc1,
                                'component2_encryption': enc2
                            },
                            resolution_options=[
                                'Upgrade lower encryption level',
                                'Use encrypted channel',
                                'Add encryption proxy'
                            ],
                            workaround_available=False
                        ))

        return issues

    def _components_communicate(
        self,
        comp1: ComponentDecision,
        comp2: ComponentDecision
    ) -> bool:
        """두 컴포넌트가 통신하는지 확인"""

        # 의존성 확인
        if comp2.id in comp1.dependencies or comp1.id in comp2.dependencies:
            return True

        # 인터페이스 연결 확인
        comp1_outputs = set(comp1.interfaces.get('outputs', []))
        comp2_inputs = set(comp2.interfaces.get('inputs', []))

        if comp1_outputs & comp2_inputs:
            return True

        return False

    async def _calculate_compatibility_score(
        self,
        comp1: ComponentDecision,
        comp2: ComponentDecision,
        issues: List[CompatibilityIssue]
    ) -> float:
        """두 컴포넌트 간 호환성 점수 계산"""

        score = 100.0

        # 해당 컴포넌트 쌍과 관련된 이슈 찾기
        related_issues = [
            issue for issue in issues
            if (issue.source_component == comp1.id and issue.target_component == comp2.id) or
               (issue.source_component == comp2.id and issue.target_component == comp1.id)
        ]

        # 심각도별 감점
        severity_penalties = {
            'blocker': 30,
            'warning': 10,
            'info': 2
        }

        for issue in related_issues:
            penalty = severity_penalties.get(issue.severity, 0)
            score -= penalty

        # 기술 스택 유사성 보너스
        tech_similarity = len(
            set(comp1.technology_stack) & set(comp2.technology_stack)
        ) / max(
            len(comp1.technology_stack),
            len(comp2.technology_stack),
            1
        )
        score += tech_similarity * 10

        return max(0, min(100, score))
```

**검증 기준**:

- [ ] 다층적 호환성 검사
- [ ] 기술 스택 충돌 감지
- [ ] 버전 호환성 확인
- [ ] 해결 방안 제시

#### SubTask 4.35.4: 컴포넌트 품질 게이트

**담당자**: 품질 보증 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/quality_gate.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class QualityGateCriteria:
    name: str
    category: str
    threshold: float
    weight: float
    is_mandatory: bool
    evaluation_method: str

@dataclass
class QualityGateResult:
    passed: bool
    score: float
    passed_criteria: List[str]
    failed_criteria: List[Dict[str, Any]]
    warnings: List[str]
    blocking_issues: List[str]
    improvement_suggestions: List[Dict[str, Any]]
    certification_level: str  # bronze, silver, gold, platinum

class ComponentQualityGate:
    """컴포넌트 품질 게이트"""

    def __init__(self):
        self.criteria = self._initialize_quality_criteria()
        self.evaluators = self._initialize_evaluators()
        self.certification_rules = self._initialize_certification_rules()

    def _initialize_quality_criteria(self) -> List[QualityGateCriteria]:
        """품질 게이트 기준 초기화"""

        return [
            # 기능적 품질
            QualityGateCriteria(
                name='requirement_coverage',
                category='functional',
                threshold=90.0,
                weight=0.15,
                is_mandatory=True,
                evaluation_method='coverage_analysis'
            ),
            QualityGateCriteria(
                name='test_coverage',
                category='functional',
                threshold=80.0,
                weight=0.10,
                is_mandatory=True,
                evaluation_method='test_analysis'
            ),

            # 기술적 품질
            QualityGateCriteria(
                name='code_complexity',
                category='technical',
                threshold=15.0,  # max cyclomatic complexity
                weight=0.10,
                is_mandatory=False,
                evaluation_method='complexity_analysis'
            ),
            QualityGateCriteria(
                name='maintainability_index',
                category='technical',
                threshold=70.0,
                weight=0.10,
                is_mandatory=True,
                evaluation_method='maintainability_analysis'
            ),

            # 보안 품질
            QualityGateCriteria(
                name='security_score',
                category='security',
                threshold=85.0,
                weight=0.15,
                is_mandatory=True,
                evaluation_method='security_analysis'
            ),
            QualityGateCriteria(
                name='vulnerability_count',
                category='security',
                threshold=0,  # zero critical vulnerabilities
                weight=0.10,
                is_mandatory=True,
                evaluation_method='vulnerability_scan'
            ),

            # 성능 품질
            QualityGateCriteria(
                name='performance_score',
                category='performance',
                threshold=75.0,
                weight=0.10,
                is_mandatory=False,
                evaluation_method='performance_analysis'
            ),

            # 아키텍처 품질
            QualityGateCriteria(
                name='design_consistency',
                category='architecture',
                threshold=85.0,
                weight=0.10,
                is_mandatory=True,
                evaluation_method='consistency_check'
            ),
            QualityGateCriteria(
                name='coupling_score',
                category='architecture',
                threshold=0.3,  # max coupling coefficient
                weight=0.05,
                is_mandatory=False,
                evaluation_method='coupling_analysis'
            ),

            # 문서화 품질
            QualityGateCriteria(
                name='documentation_completeness',
                category='documentation',
                threshold=80.0,
                weight=0.05,
                is_mandatory=False,
                evaluation_method='documentation_check'
            )
        ]

    async def evaluate_components(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture,
        context: Dict[str, Any]
    ) -> QualityGateResult:
        """컴포넌트 품질 게이트 평가"""

        passed_criteria = []
        failed_criteria = []
        warnings = []
        blocking_issues = []

        total_score = 0.0
        total_weight = 0.0

        # 1. 각 기준별 평가
        for criterion in self.criteria:
            evaluator = self.evaluators.get(criterion.evaluation_method)
            if not evaluator:
                warnings.append(f"No evaluator for {criterion.name}")
                continue

            # 평가 실행
            evaluation_result = await evaluator.evaluate(
                components,
                architecture,
                criterion,
                context
            )

            # 기준 통과 여부 확인
            if evaluation_result['passed']:
                passed_criteria.append(criterion.name)
                score_contribution = criterion.weight * 100
            else:
                failed_detail = {
                    'criterion': criterion.name,
                    'category': criterion.category,
                    'actual_value': evaluation_result['actual_value'],
                    'threshold': criterion.threshold,
                    'gap': evaluation_result['gap'],
                    'impact': evaluation_result['impact']
                }
                failed_criteria.append(failed_detail)

                if criterion.is_mandatory:
                    blocking_issues.append(
                        f"{criterion.name} failed (mandatory): "
                        f"{evaluation_result['actual_value']} < {criterion.threshold}"
                    )

                # 부분 점수 계산
                score_contribution = criterion.weight * evaluation_result.get('partial_score', 0)

            total_score += score_contribution
            total_weight += criterion.weight

        # 2. 정규화된 총점 계산
        normalized_score = (total_score / total_weight) if total_weight > 0 else 0

        # 3. 품질 게이트 통과 여부
        gate_passed = len(blocking_issues) == 0 and normalized_score >= 70

        # 4. 인증 수준 결정
        certification_level = self._determine_certification_level(
            normalized_score,
            passed_criteria,
            failed_criteria
        )

        # 5. 개선 제안 생성
        improvement_suggestions = await self._generate_improvements(
            failed_criteria,
            warnings,
            components,
            architecture
        )

        return QualityGateResult(
            passed=gate_passed,
            score=round(normalized_score, 1),
            passed_criteria=passed_criteria,
            failed_criteria=failed_criteria,
            warnings=warnings,
            blocking_issues=blocking_issues,
            improvement_suggestions=improvement_suggestions,
            certification_level=certification_level
        )

    def _determine_certification_level(
        self,
        score: float,
        passed_criteria: List[str],
        failed_criteria: List[Dict[str, Any]]
    ) -> str:
        """품질 인증 수준 결정"""

        # 필수 기준 확인
        mandatory_criteria = [c for c in self.criteria if c.is_mandatory]
        mandatory_passed = all(
            c.name in passed_criteria
            for c in mandatory_criteria
        )

        if not mandatory_passed:
            return 'none'

        # 점수 기반 인증 수준
        if score >= 95 and len(failed_criteria) == 0:
            return 'platinum'
        elif score >= 90:
            return 'gold'
        elif score >= 80:
            return 'silver'
        elif score >= 70:
            return 'bronze'
        else:
            return 'none'

    async def _generate_improvements(
        self,
        failed_criteria: List[Dict[str, Any]],
        warnings: List[str],
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> List[Dict[str, Any]]:
        """개선 제안 생성"""

        improvements = []

        # 실패한 기준별 개선 제안
        for failure in failed_criteria:
            criterion_name = failure['criterion']

            if criterion_name == 'requirement_coverage':
                improvements.append({
                    'area': 'Requirement Coverage',
                    'priority': 'high',
                    'current_state': f"{failure['actual_value']}%",
                    'target_state': f"{failure['threshold']}%",
                    'actions': [
                        'Review uncovered requirements',
                        'Add missing components or features',
                        'Update component-requirement mappings'
                    ],
                    'estimated_effort': '5-10 story points'
                })

            elif criterion_name == 'security_score':
                improvements.append({
                    'area': 'Security',
                    'priority': 'critical',
                    'current_state': f"{failure['actual_value']}",
                    'target_state': f"{failure['threshold']}",
                    'actions': [
                        'Implement missing security controls',
                        'Add input validation',
                        'Enable encryption',
                        'Configure authentication/authorization'
                    ],
                    'estimated_effort': '10-15 story points'
                })

            elif criterion_name == 'code_complexity':
                improvements.append({
                    'area': 'Code Complexity',
                    'priority': 'medium',
                    'current_state': f"Complexity: {failure['actual_value']}",
                    'target_state': f"Complexity < {failure['threshold']}",
                    'actions': [
                        'Refactor complex methods',
                        'Extract helper functions',
                        'Simplify conditional logic',
                        'Apply design patterns'
                    ],
                    'estimated_effort': '3-5 story points per component'
                })

        # 일반적인 개선 제안
        if len(components) > 20:
            improvements.append({
                'area': 'Architecture',
                'priority': 'medium',
                'observation': 'High number of components',
                'actions': [
                    'Consider component consolidation',
                    'Review for redundant functionality',
                    'Implement facade pattern for complex subsystems'
                ],
                'estimated_effort': '8-12 story points'
            })

        return improvements

    def _initialize_evaluators(self) -> Dict[str, Any]:
        """평가기 초기화"""

        return {
            'coverage_analysis': RequirementCoverageEvaluator(),
            'test_analysis': TestCoverageEvaluator(),
            'complexity_analysis': ComplexityEvaluator(),
            'maintainability_analysis': MaintainabilityEvaluator(),
            'security_analysis': SecurityEvaluator(),
            'vulnerability_scan': VulnerabilityScanner(),
            'performance_analysis': PerformanceEvaluator(),
            'consistency_check': ConsistencyEvaluator(),
            'coupling_analysis': CouplingEvaluator(),
            'documentation_check': DocumentationEvaluator()
        }
```

**검증 기준**:

- [ ] 종합적인 품질 평가
- [ ] 명확한 통과/실패 기준
- [ ] 인증 수준 시스템
- [ ] 구체적인 개선 가이드

### Task 4.36: 컴포넌트 문서화 시스템

#### SubTask 4.36.1: 컴포넌트 문서 생성기

**담당자**: 기술 문서 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/documentation_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import markdown
from jinja2 import Template

@dataclass
class DocumentationSection:
    title: str
    content: str
    subsections: List['DocumentationSection']
    code_examples: List[Dict[str, str]]
    diagrams: List[Dict[str, Any]]
    references: List[str]

@dataclass
class ComponentDocumentation:
    component_id: str
    component_name: str
    overview: str
    sections: List[DocumentationSection]
    api_documentation: Dict[str, Any]
    usage_examples: List[Dict[str, str]]
    integration_guide: str
    troubleshooting: List[Dict[str, str]]
    changelog: List[Dict[str, Any]]
    generated_at: str

class ComponentDocumentationGenerator:
    """컴포넌트 문서 생성기"""

    def __init__(self):
        self.template_loader = TemplateLoader()
        self.diagram_generator = DiagramGenerator()
        self.code_formatter = CodeFormatter()
        self.api_doc_generator = APIDocumentationGenerator()

    async def generate_documentation(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture,
        context: Optional[Dict[str, Any]] = None
    ) -> ComponentDocumentation:
        """컴포넌트 문서 생성"""

        # 1. 개요 섹션 생성
        overview = await self._generate_overview(component, architecture)

        # 2. 아키텍처 섹션
        architecture_section = await self._generate_architecture_section(
            component,
            architecture
        )

        # 3. API 문서 생성
        api_documentation = await self._generate_api_documentation(component)

        # 4. 구현 가이드
        implementation_guide = await self._generate_implementation_guide(
            component
        )

        # 5. 사용 예제
        usage_examples = await self._generate_usage_examples(component)

        # 6. 통합 가이드
        integration_guide = await self._generate_integration_guide(
            component,
            architecture
        )

        # 7. 성능 고려사항
        performance_section = await self._generate_performance_section(
            component
        )

        # 8. 보안 고려사항
        security_section = await self._generate_security_section(component)

        # 9. 테스트 가이드
        testing_section = await self._generate_testing_section(component)

        # 10. 문제 해결 가이드
        troubleshooting = await self._generate_troubleshooting_guide(
            component
        )

        # 섹션 조합
        sections = [
            architecture_section,
            implementation_guide,
            performance_section,
            security_section,
            testing_section
        ]

        return ComponentDocumentation(
            component_id=component.id,
            component_name=component.name,
            overview=overview,
            sections=sections,
            api_documentation=api_documentation,
            usage_examples=usage_examples,
            integration_guide=integration_guide,
            troubleshooting=troubleshooting,
            changelog=[],
            generated_at=datetime.utcnow().isoformat()
        )

    async def _generate_overview(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> str:
        """개요 섹션 생성"""

        template = Template("""
# {{ component.name }}

## Overview

{{ component.description }}

### Key Features

{% for feature in features %}
- {{ feature }}
{% endfor %}

### Component Type

**Type**: {{ component.type.value }}
**Category**: {{ category }}
**Complexity**: {{ complexity_level }}
**Reusability**: {{ reusability_level }}

### Dependencies

{% if dependencies %}
This component depends on:
{% for dep in dependencies %}
- `{{ dep }}`: {{ dep_descriptions[dep] }}
{% endfor %}
{% else %}
This component has no external dependencies.
{% endif %}

### Requirements Coverage

This component implements the following requirements:
{% for req_id in component.requirements %}
- {{ req_id }}: {{ requirement_descriptions[req_id] }}
{% endfor %}

### Technology Stack

{% for tech in component.technology_stack %}
- {{ tech }}
{% endfor %}
""")

        # 특징 추출
        features = self._extract_key_features(component)

        # 카테고리 결정
        category = self._determine_category(component)

        # 복잡도 수준
        complexity_level = self._get_complexity_level(component.complexity_score)

        # 재사용성 수준
        reusability_level = self._get_reusability_level(
            component.reusability_score
        )

        # 의존성 설명
        dep_descriptions = await self._get_dependency_descriptions(
            component.dependencies,
            architecture
        )

        # 요구사항 설명
        requirement_descriptions = {}  # 실제로는 요구사항 시스템에서 가져옴

        return template.render(
            component=component,
            features=features,
            category=category,
            complexity_level=complexity_level,
            reusability_level=reusability_level,
            dependencies=component.dependencies,
            dep_descriptions=dep_descriptions,
            requirement_descriptions=requirement_descriptions
        )

    async def _generate_architecture_section(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> DocumentationSection:
        """아키텍처 섹션 생성"""

        # 컴포넌트 다이어그램 생성
        component_diagram = await self.diagram_generator.generate_component_diagram(
            component,
            architecture
        )

        # 데이터 흐름 다이어그램
        data_flow_diagram = await self.diagram_generator.generate_data_flow_diagram(
            component,
            architecture
        )

        content = f"""
## Architecture

### Component Structure

{component.name} follows the {self._identify_pattern(component)} pattern.

### Responsibilities

{self._format_responsibilities(component)}

### Interfaces

{self._format_interfaces(component)}

### Data Flow

The component processes data as follows:

1. Input received through {self._get_input_interfaces(component)}
2. Data validation and transformation
3. Core processing logic
4. Output generation via {self._get_output_interfaces(component)}
"""

        return DocumentationSection(
            title="Architecture",
            content=content,
            subsections=[
                DocumentationSection(
                    title="Design Patterns",
                    content=self._document_patterns(component),
                    subsections=[],
                    code_examples=[],
                    diagrams=[],
                    references=[]
                ),
                DocumentationSection(
                    title="Component Interactions",
                    content=self._document_interactions(component, architecture),
                    subsections=[],
                    code_examples=[],
                    diagrams=[data_flow_diagram],
                    references=[]
                )
            ],
            code_examples=[],
            diagrams=[component_diagram],
            references=[]
        )

    async def _generate_api_documentation(
        self,
        component: ComponentDecision
    ) -> Dict[str, Any]:
        """API 문서 생성"""

        api_doc = {
            'endpoints': [],
            'data_models': [],
            'error_codes': [],
            'authentication': {},
            'rate_limiting': {}
        }

        if component.type == ComponentType.API_ENDPOINT:
            # 엔드포인트 문서화
            for endpoint in component.interfaces.get('endpoints', []):
                endpoint_doc = {
                    'path': endpoint['path'],
                    'method': endpoint['method'],
                    'description': endpoint['description'],
                    'parameters': self._document_parameters(endpoint),
                    'request_body': self._document_request_body(endpoint),
                    'responses': self._document_responses(endpoint),
                    'examples': self._generate_api_examples(endpoint),
                    'security': endpoint.get('security', [])
                }
                api_doc['endpoints'].append(endpoint_doc)

            # 데이터 모델 문서화
            api_doc['data_models'] = self._document_data_models(component)

            # 에러 코드 문서화
            api_doc['error_codes'] = self._document_error_codes(component)

        return api_doc

    async def _generate_usage_examples(
        self,
        component: ComponentDecision
    ) -> List[Dict[str, str]]:
        """사용 예제 생성"""

        examples = []

        if component.type == ComponentType.UI_COMPONENT:
            # React 예제
            examples.append({
                'title': 'Basic Usage (React)',
                'language': 'jsx',
                'code': self._generate_react_example(component)
            })

            # Props 예제
            examples.append({
                'title': 'With Custom Props',
                'language': 'jsx',
                'code': self._generate_props_example(component)
            })

            # 이벤트 처리 예제
            if component.properties.get('events'):
                examples.append({
                    'title': 'Event Handling',
                    'language': 'jsx',
                    'code': self._generate_event_example(component)
                })

        elif component.type == ComponentType.BACKEND_SERVICE:
            # API 호출 예제
            examples.append({
                'title': 'API Call Example',
                'language': 'typescript',
                'code': self._generate_api_call_example(component)
            })

            # 에러 처리 예제
            examples.append({
                'title': 'Error Handling',
                'language': 'typescript',
                'code': self._generate_error_handling_example(component)
            })

        elif component.type == ComponentType.DATA_MODEL:
            # CRUD 예제
            examples.append({
                'title': 'CRUD Operations',
                'language': 'typescript',
                'code': self._generate_crud_example(component)
            })

        return examples

    def _generate_react_example(self, component: ComponentDecision) -> str:
        """React 사용 예제 생성"""

        props = component.properties.get('props', {})

        return f"""
import React from 'react';
import {{ {component.name} }} from '@/components/{component.name}';

function Example() {{
  return (
    <{component.name}
      {self._format_props_for_example(props)}
    />
  );
}}

export default Example;
"""

    def _format_props_for_example(self, props: Dict[str, Any]) -> str:
        """예제용 props 포맷팅"""

        formatted = []
        for prop_name, prop_info in props.items():
            if prop_info.get('required'):
                default_value = self._get_default_prop_value(prop_info)
                formatted.append(f'{prop_name}={{{default_value}}}')

        return '\n      '.join(formatted)

    async def _generate_troubleshooting_guide(
        self,
        component: ComponentDecision
    ) -> List[Dict[str, str]]:
        """문제 해결 가이드 생성"""

        troubleshooting_items = []

        # 일반적인 문제들
        common_issues = [
            {
                'issue': 'Component not rendering',
                'possible_causes': [
                    'Missing required props',
                    'Import path incorrect',
                    'Parent component not mounted'
                ],
                'solutions': [
                    'Check console for prop validation errors',
                    'Verify import statement matches export',
                    'Ensure parent component is properly rendered'
                ]
            },
            {
                'issue': 'Performance degradation',
                'possible_causes': [
                    'Unnecessary re-renders',
                    'Large data sets without pagination',
                    'Missing memoization'
                ],
                'solutions': [
                    'Use React.memo() or useMemo()',
                    'Implement virtual scrolling',
                    'Add proper key props to lists'
                ]
            }
        ]

        # 컴포넌트별 특정 문제
        if component.type == ComponentType.API_ENDPOINT:
            common_issues.append({
                'issue': 'API returns 401 Unauthorized',
                'possible_causes': [
                    'Missing authentication token',
                    'Expired token',
                    'Incorrect token format'
                ],
                'solutions': [
                    'Ensure token is included in headers',
                    'Implement token refresh logic',
                    'Verify token format matches expected'
                ]
            })

        return common_issues
```

**검증 기준**:

- [ ] 포괄적인 문서 구조
- [ ] 실용적인 예제 코드
- [ ] 시각적 다이어그램 포함
- [ ] 문제 해결 가이드

#### SubTask 4.36.2: API 문서 자동화

**담당자**: API 문서화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/api_documentation.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import yaml
import json

@dataclass
class APIEndpoint:
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    security: List[Dict[str, Any]]
    tags: List[str]
    examples: List[Dict[str, Any]]

@dataclass
class APIDocumentation:
    openapi_version: str
    info: Dict[str, Any]
    servers: List[Dict[str, Any]]
    paths: Dict[str, Dict[str, Any]]
    components: Dict[str, Any]
    security_schemes: Dict[str, Any]
    tags: List[Dict[str, Any]]

class APIDocumentationGenerator:
    """API 문서 자동 생성"""

    def __init__(self):
        self.schema_generator = SchemaGenerator()
        self.example_generator = ExampleGenerator()
        self.openapi_builder = OpenAPIBuilder()

    async def generate_api_documentation(
        self,
        components: List[ComponentDecision],
        api_metadata: Dict[str, Any]
    ) -> APIDocumentation:
        """API 문서 생성"""

        # 1. API 컴포넌트 필터링
        api_components = [
            c for c in components
            if c.type in [ComponentType.API_ENDPOINT, ComponentType.BACKEND_SERVICE]
        ]

        # 2. OpenAPI 기본 구조 생성
        openapi_doc = self._create_openapi_structure(api_metadata)

        # 3. 경로별 문서화
        paths = {}
        for component in api_components:
            component_paths = await self._document_component_endpoints(
                component
            )
            paths.update(component_paths)

        # 4. 컴포넌트 스키마 생성
        schemas = await self._generate_schemas(api_components)

        # 5. 보안 스키마 생성
        security_schemes = self._generate_security_schemes(api_components)

        # 6. 태그 생성
        tags = self._generate_tags(api_components)

        # 7. 서버 정보
        servers = self._generate_server_info(api_metadata)

        return APIDocumentation(
            openapi_version="3.0.3",
            info=openapi_doc['info'],
            servers=servers,
            paths=paths,
            components={
                'schemas': schemas,
                'securitySchemes': security_schemes,
                'parameters': self._generate_common_parameters(),
                'responses': self._generate_common_responses()
            },
            security_schemes=security_schemes,
            tags=tags
        )

    async def _document_component_endpoints(
        self,
        component: ComponentDecision
    ) -> Dict[str, Dict[str, Any]]:
        """컴포넌트 엔드포인트 문서화"""

        paths = {}

        for endpoint in component.interfaces.get('endpoints', []):
            path = endpoint['path']
            method = endpoint['method'].lower()

            if path not in paths:
                paths[path] = {}

            # 엔드포인트 문서
            endpoint_doc = {
                'summary': endpoint.get('summary', f"{method.upper()} {path}"),
                'description': endpoint.get('description', ''),
                'operationId': self._generate_operation_id(component, endpoint),
                'tags': [component.name],
                'parameters': await self._document_parameters(endpoint),
                'responses': await self._document_responses(endpoint, component)
            }

            # Request Body
            if method in ['post', 'put', 'patch']:
                request_body = await self._document_request_body(
                    endpoint,
                    component
                )
                if request_body:
                    endpoint_doc['requestBody'] = request_body

            # Security
            if endpoint.get('authentication_required', True):
                endpoint_doc['security'] = self._get_endpoint_security(endpoint)

            # Examples
            examples = await self.example_generator.generate_examples(
                endpoint,
                component
            )
            if examples:
                endpoint_doc['x-examples'] = examples

            paths[path][method] = endpoint_doc

        return paths

    async def _document_parameters(
        self,
        endpoint: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """파라미터 문서화"""

        parameters = []

        # Path parameters
        path_params = self._extract_path_parameters(endpoint['path'])
        for param_name in path_params:
            param_info = endpoint.get('path_params', {}).get(param_name, {})
            parameters.append({
                'name': param_name,
                'in': 'path',
                'required': True,
                'description': param_info.get('description', f'{param_name} parameter'),
                'schema': {
                    'type': param_info.get('type', 'string'),
                    'format': param_info.get('format'),
                    'pattern': param_info.get('pattern'),
                    'example': param_info.get('example')
                }
            })

        # Query parameters
        for param_name, param_info in endpoint.get('query_params', {}).items():
            parameters.append({
                'name': param_name,
                'in': 'query',
                'required': param_info.get('required', False),
                'description': param_info.get('description', ''),
                'schema': {
                    'type': param_info.get('type', 'string'),
                    'format': param_info.get('format'),
                    'enum': param_info.get('enum'),
                    'default': param_info.get('default'),
                    'example': param_info.get('example')
                }
            })

        # Header parameters
        for param_name, param_info in endpoint.get('headers', {}).items():
            if param_name.lower() not in ['authorization', 'content-type']:
                parameters.append({
                    'name': param_name,
                    'in': 'header',
                    'required': param_info.get('required', False),
                    'description': param_info.get('description', ''),
                    'schema': {
                        'type': param_info.get('type', 'string'),
                        'example': param_info.get('example')
                    }
                })

        return parameters

    async def _document_request_body(
        self,
        endpoint: Dict[str, Any],
        component: ComponentDecision
    ) -> Optional[Dict[str, Any]]:
        """Request Body 문서화"""

        if not endpoint.get('request_body'):
            return None

        request_body_schema = endpoint['request_body']

        # 스키마 생성
        schema = await self.schema_generator.generate_schema(
            request_body_schema,
            component
        )

        # 예제 생성
        examples = await self.example_generator.generate_request_examples(
            request_body_schema,
            component
        )

        return {
            'description': request_body_schema.get('description', 'Request body'),
            'required': request_body_schema.get('required', True),
            'content': {
                'application/json': {
                    'schema': schema,
                    'examples': examples
                }
            }
        }

    async def _document_responses(
        self,
        endpoint: Dict[str, Any],
        component: ComponentDecision
    ) -> Dict[str, Dict[str, Any]]:
        """응답 문서화"""

        responses = {}

        # 성공 응답
        success_response = endpoint.get('responses', {}).get('200', {})
        responses['200'] = {
            'description': success_response.get('description', 'Successful response'),
            'content': {
                'application/json': {
                    'schema': await self.schema_generator.generate_schema(
                        success_response.get('schema', {}),
                        component
                    ),
                    'examples': await self.example_generator.generate_response_examples(
                        success_response,
                        component
                    )
                }
            }
        }

        # 에러 응답
        error_responses = {
            '400': {
                'description': 'Bad Request',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Error'
                        },
                        'example': {
                            'error': {
                                'code': 'INVALID_REQUEST',
                                'message': 'The request is invalid',
                                'details': {}
                            }
                        }
                    }
                }
            },
            '401': {
                'description': 'Unauthorized',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Error'
                        }
                    }
                }
            },
            '404': {
                'description': 'Not Found',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Error'
                        }
                    }
                }
            },
            '500': {
                'description': 'Internal Server Error',
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Error'
                        }
                    }
                }
            }
        }

        # 엔드포인트별 특정 에러 응답 추가
        for status_code, error_info in endpoint.get('error_responses', {}).items():
            error_responses[status_code] = {
                'description': error_info.get('description', ''),
                'content': {
                    'application/json': {
                        'schema': error_info.get('schema', {
                            '$ref': '#/components/schemas/Error'
                        }),
                        'example': error_info.get('example')
                    }
                }
            }

        responses.update(error_responses)

        return responses

    def _generate_operation_id(
        self,
        component: ComponentDecision,
        endpoint: Dict[str, Any]
    ) -> str:
        """Operation ID 생성"""

        # 경로에서 리소스 추출
        path_parts = endpoint['path'].strip('/').split('/')
        resource = path_parts[-1] if path_parts else 'resource'

        # 동사 결정
        method = endpoint['method'].lower()
        verb_mapping = {
            'get': 'get' if '{' in endpoint['path'] else 'list',
            'post': 'create',
            'put': 'update',
            'patch': 'patch',
            'delete': 'delete'
        }
        verb = verb_mapping.get(method, method)

        # camelCase로 변환
        resource_camel = ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(resource.split('_'))
        )

        return f"{verb}{resource_camel}"

    async def export_documentation(
        self,
        documentation: APIDocumentation,
        format: str = 'yaml'
    ) -> str:
        """문서 내보내기"""

        doc_dict = {
            'openapi': documentation.openapi_version,
            'info': documentation.info,
            'servers': documentation.servers,
            'paths': documentation.paths,
            'components': documentation.components,
            'tags': documentation.tags
        }

        if format == 'yaml':
            return yaml.dump(doc_dict, sort_keys=False, default_flow_style=False)
        elif format == 'json':
            return json.dumps(doc_dict, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

**검증 기준**:

- [ ] OpenAPI 3.0 스펙 준수
- [ ] 자동 스키마 생성
- [ ] 실제 요청/응답 예제
- [ ] 다양한 포맷 지원

#### SubTask 4.36.3: 컴포넌트 다이어그램 생성기

**담당자**: 시각화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/diagram_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import graphviz
import plantuml

@dataclass
class Diagram:
    type: str  # component, sequence, class, deployment
    title: str
    description: str
    format: str  # svg, png, plantuml
    content: str
    metadata: Dict[str, Any]

class DiagramGenerator:
    """컴포넌트 다이어그램 생성"""

    def __init__(self):
        self.plantuml_generator = PlantUMLGenerator()
        self.mermaid_generator = MermaidGenerator()
        self.graphviz_generator = GraphvizGenerator()

    async def generate_component_diagram(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> Diagram:
        """컴포넌트 다이어그램 생성"""

        # PlantUML 컴포넌트 다이어그램
        plantuml_code = f"""
@startuml
!theme plain
title {component.name} - Component Diagram

package "{component.name}" #LightBlue {{
    {self._generate_component_internals(component)}
}}

{self._generate_component_dependencies(component, architecture)}

{self._generate_component_interfaces(component)}

note right of {component.name}
  Type: {component.type.value}
  Complexity: {component.complexity_score}
  Reusability: {component.reusability_score}
end note

@enduml
"""

        return Diagram(
            type='component',
            title=f"{component.name} Component Diagram",
            description=f"Component structure and dependencies for {component.name}",
            format='plantuml',
            content=plantuml_code,
            metadata={
                'component_id': component.id,
                'generated_with': 'plantuml'
            }
        )

    async def generate_data_flow_diagram(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> Diagram:
        """데이터 흐름 다이어그램 생성"""

        mermaid_code = f"""
graph LR
    %% Data Flow for {component.name}

    {self._generate_data_flow_nodes(component, architecture)}

    {self._generate_data_flow_edges(component, architecture)}

    %% Styling
    classDef inputNode fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef processNode fill:#87CEEB,stroke:#4682B4,stroke-width:2px
    classDef outputNode fill:#FFB6C1,stroke:#DC143C,stroke-width:2px

    {self._apply_node_styles(component)}
"""

        return Diagram(
            type='data_flow',
            title=f"{component.name} Data Flow",
            description=f"Data flow through {component.name}",
            format='mermaid',
            content=mermaid_code,
            metadata={
                'component_id': component.id,
                'flow_type': 'data'
            }
        )

    async def generate_sequence_diagram(
        self,
        component: ComponentDecision,
        scenario: str
    ) -> Diagram:
        """시퀀스 다이어그램 생성"""

        # 시나리오별 시퀀스 생성
        sequences = self._generate_sequences_for_scenario(component, scenario)

        plantuml_code = f"""
@startuml
!theme plain
title {component.name} - {scenario}

{self._generate_participants(component, sequences)}

{self._generate_sequence_interactions(sequences)}

@enduml
"""

        return Diagram(
            type='sequence',
            title=f"{component.name} - {scenario}",
            description=f"Sequence diagram for {scenario}",
            format='plantuml',
            content=plantuml_code,
            metadata={
                'component_id': component.id,
                'scenario': scenario
            }
        )

    async def generate_class_diagram(
        self,
        component: ComponentDecision
    ) -> Diagram:
        """클래스 다이어그램 생성"""

        if component.type != ComponentType.DATA_MODEL:
            return None

        plantuml_code = f"""
@startuml
!theme plain
title {component.name} - Class Diagram

class {component.name} {{
    {self._generate_class_fields(component)}
    --
    {self._generate_class_methods(component)}
}}

{self._generate_class_relationships(component)}

@enduml
"""

        return Diagram(
            type='class',
            title=f"{component.name} Class Diagram",
            description=f"Class structure for {component.name}",
            format='plantuml',
            content=plantuml_code,
            metadata={
                'component_id': component.id,
                'model_type': 'class'
            }
        )

    async def generate_deployment_diagram(
        self,
        components: List[ComponentDecision],
        deployment_config: Dict[str, Any]
    ) -> Diagram:
        """배포 다이어그램 생성"""

        plantuml_code = """
@startuml
!theme plain
title Deployment Architecture

"""

        # 노드 생성
        for env in deployment_config.get('environments', []):
            plantuml_code += f"""
node "{env['name']}" as {env['id']} {{
"""

            # 컨테이너/서비스
            for service in env.get('services', []):
                component = next(
                    (c for c in components if c.id == service['component_id']),
                    None
                )
                if component:
                    plantuml_code += f"""
    component "[{component.name}]" as {component.id}_{env['id']}
"""

            plantuml_code += "}\n"

        # 연결 관계
        plantuml_code += self._generate_deployment_connections(
            components,
            deployment_config
        )

        plantuml_code += "@enduml"

        return Diagram(
            type='deployment',
            title='Deployment Architecture',
            description='System deployment architecture',
            format='plantuml',
            content=plantuml_code,
            metadata={
                'environments': [e['name'] for e in deployment_config.get('environments', [])]
            }
        )

    def _generate_component_internals(
        self,
        component: ComponentDecision
    ) -> str:
        """컴포넌트 내부 구조 생성"""

        internals = []

        if component.type == ComponentType.UI_COMPONENT:
            # UI 컴포넌트 내부
            if component.properties.get('state'):
                internals.append('    [State Management] as state')
            if component.properties.get('events'):
                internals.append('    [Event Handlers] as events')
            internals.append('    [Render Logic] as render')

        elif component.type == ComponentType.BACKEND_SERVICE:
            # 백엔드 서비스 내부
            internals.append('    [Controller] as controller')
            internals.append('    [Service Logic] as service')
            if component.properties.get('database'):
                internals.append('    [Data Access] as dao')

        elif component.type == ComponentType.DATA_MODEL:
            # 데이터 모델 내부
            internals.append('    [Entity] as entity')
            internals.append('    [Repository] as repository')
            if component.properties.get('validation'):
                internals.append('    [Validation] as validation')

        return '\n'.join(internals)

    def _generate_data_flow_nodes(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> str:
        """데이터 흐름 노드 생성"""

        nodes = []

        # 입력 노드
        for input_source in component.interfaces.get('inputs', []):
            nodes.append(f"    {input_source['id']}[{input_source['name']}]:::inputNode")

        # 처리 노드
        nodes.append(f"    {component.id}[{component.name}]:::processNode")

        # 내부 처리 단계
        if component.properties.get('processing_steps'):
            for step in component.properties['processing_steps']:
                nodes.append(f"    {step['id']}[{step['name']}]:::processNode")

        # 출력 노드
        for output_target in component.interfaces.get('outputs', []):
            nodes.append(f"    {output_target['id']}[{output_target['name']}]:::outputNode")

        return '\n'.join(nodes)

    async def export_diagram(
        self,
        diagram: Diagram,
        output_format: str = 'svg'
    ) -> bytes:
        """다이어그램 내보내기"""

        if diagram.format == 'plantuml':
            return await self.plantuml_generator.render(
                diagram.content,
                output_format
            )
        elif diagram.format == 'mermaid':
            return await self.mermaid_generator.render(
                diagram.content,
                output_format
            )
        elif diagram.format == 'graphviz':
            return await self.graphviz_generator.render(
                diagram.content,
                output_format
            )
        else:
            raise ValueError(f"Unsupported diagram format: {diagram.format}")
```

**검증 기준**:

- [ ] 다양한 다이어그램 타입
- [ ] 자동 레이아웃 생성
- [ ] 다중 포맷 지원
- [ ] 시각적 명확성

#### SubTask 4.36.4: 문서 버전 관리 시스템

**담당자**: 문서 관리 전문가  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/documentation_versioning.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import difflib
import hashlib

@dataclass
class DocumentVersion:
    version_id: str
    version_number: str  # semantic versioning
    component_id: str
    created_at: datetime
    created_by: str
    changes: List[Dict[str, Any]]
    change_summary: str
    document_hash: str
    is_latest: bool
    is_published: bool

@dataclass
class DocumentationHistory:
    component_id: str
    versions: List[DocumentVersion]
    current_version: str
    published_version: Optional[str]
    change_log: List[Dict[str, Any]]

class DocumentationVersionManager:
    """문서 버전 관리"""

    def __init__(self):
        self.version_storage = VersionStorage()
        self.diff_generator = DiffGenerator()
        self.change_tracker = ChangeTracker()

    async def create_version(
        self,
        documentation: ComponentDocumentation,
        author: str,
        change_summary: str,
        previous_version: Optional[DocumentVersion] = None
    ) -> DocumentVersion:
        """새 문서 버전 생성"""

        # 1. 버전 번호 생성
        version_number = self._generate_version_number(
            previous_version,
            change_summary
        )

        # 2. 문서 해시 생성
        document_hash = self._generate_document_hash(documentation)

        # 3. 변경사항 추출
        changes = []
        if previous_version:
            previous_doc = await self.version_storage.get_documentation(
                previous_version.version_id
            )
            changes = await self._extract_changes(
                previous_doc,
                documentation
            )

        # 4. 버전 객체 생성
        version = DocumentVersion(
            version_id=self._generate_version_id(),
            version_number=version_number,
            component_id=documentation.component_id,
            created_at=datetime.utcnow(),
            created_by=author,
            changes=changes,
            change_summary=change_summary,
            document_hash=document_hash,
            is_latest=True,
            is_published=False
        )

        # 5. 이전 버전 업데이트
        if previous_version:
            previous_version.is_latest = False
            await self.version_storage.update_version(previous_version)

        # 6. 새 버전 저장
        await self.version_storage.save_version(version, documentation)

        # 7. 변경 이력 추가
        await self.change_tracker.track_change(
            component_id=documentation.component_id,
            version_id=version.version_id,
            change_type='documentation_update',
            changes=changes
        )

        return version

    async def get_version_history(
        self,
        component_id: str
    ) -> DocumentationHistory:
        """버전 이력 조회"""

        # 모든 버전 조회
        versions = await self.version_storage.get_versions(component_id)

        # 정렬 (최신순)
        versions.sort(key=lambda v: v.created_at, reverse=True)

        # 현재 버전 찾기
        current_version = next(
            (v for v in versions if v.is_latest),
            versions[0] if versions else None
        )

        # 게시된 버전 찾기
        published_version = next(
            (v for v in versions if v.is_published),
            None
        )

        # 변경 로그 생성
        change_log = await self._generate_change_log(versions)

        return DocumentationHistory(
            component_id=component_id,
            versions=versions,
            current_version=current_version.version_id if current_version else None,
            published_version=published_version.version_id if published_version else None,
            change_log=change_log
        )

    async def compare_versions(
        self,
        version1_id: str,
        version2_id: str
    ) -> Dict[str, Any]:
        """버전 간 비교"""

        # 문서 로드
        doc1 = await self.version_storage.get_documentation(version1_id)
        doc2 = await self.version_storage.get_documentation(version2_id)

        # 섹션별 비교
        comparison = {
            'version1': version1_id,
            'version2': version2_id,
            'overview_changes': await self._compare_text(
                doc1.overview,
                doc2.overview
            ),
            'section_changes': await self._compare_sections(
                doc1.sections,
                doc2.sections
            ),
            'api_changes': await self._compare_api_documentation(
                doc1.api_documentation,
                doc2.api_documentation
            ),
            'example_changes': await self._compare_examples(
                doc1.usage_examples,
                doc2.usage_examples
            ),
            'summary': {
                'additions': 0,
                'deletions': 0,
                'modifications': 0
            }
        }

        # 변경 요약 계산
        comparison['summary'] = self._calculate_change_summary(comparison)

        return comparison

    async def publish_version(
        self,
        version_id: str,
        publisher: str
    ) -> DocumentVersion:
        """버전 게시"""

        # 버전 조회
        version = await self.version_storage.get_version(version_id)

        if version.is_published:
            raise ValueError(f"Version {version_id} is already published")

        # 이전 게시 버전 해제
        component_versions = await self.version_storage.get_versions(
            version.component_id
        )
        for v in component_versions:
            if v.is_published:
                v.is_published = False
                await self.version_storage.update_version(v)

        # 현재 버전 게시
        version.is_published = True
        await self.version_storage.update_version(version)

        # 게시 이벤트 기록
        await self.change_tracker.track_change(
            component_id=version.component_id,
            version_id=version_id,
            change_type='documentation_published',
            metadata={
                'publisher': publisher,
                'published_at': datetime.utcnow().isoformat()
            }
        )

        return version

    def _generate_version_number(
        self,
        previous_version: Optional[DocumentVersion],
        change_summary: str
    ) -> str:
        """버전 번호 생성 (Semantic Versioning)"""

        if not previous_version:
            return "1.0.0"

        prev_major, prev_minor, prev_patch = map(
            int,
            previous_version.version_number.split('.')
        )

        # 변경 유형에 따른 버전 증가
        if 'breaking' in change_summary.lower() or 'major' in change_summary.lower():
            return f"{prev_major + 1}.0.0"
        elif 'feature' in change_summary.lower() or 'add' in change_summary.lower():
            return f"{prev_major}.{prev_minor + 1}.0"
        else:
            return f"{prev_major}.{prev_minor}.{prev_patch + 1}"

    async def _extract_changes(
        self,
        old_doc: ComponentDocumentation,
        new_doc: ComponentDocumentation
    ) -> List[Dict[str, Any]]:
        """문서 간 변경사항 추출"""

        changes = []

        # 개요 변경
        if old_doc.overview != new_doc.overview:
            changes.append({
                'type': 'overview_updated',
                'section': 'overview',
                'diff': self._generate_diff(old_doc.overview, new_doc.overview)
            })

        # 섹션 변경
        old_sections = {s.title: s for s in old_doc.sections}
        new_sections = {s.title: s for s in new_doc.sections}

        # 추가된 섹션
        for title in set(new_sections) - set(old_sections):
            changes.append({
                'type': 'section_added',
                'section': title,
                'content': new_sections[title].content[:100] + '...'
            })

        # 삭제된 섹션
        for title in set(old_sections) - set(new_sections):
            changes.append({
                'type': 'section_removed',
                'section': title
            })

        # 수정된 섹션
        for title in set(old_sections) & set(new_sections):
            if old_sections[title].content != new_sections[title].content:
                changes.append({
                    'type': 'section_modified',
                    'section': title,
                    'diff': self._generate_diff(
                        old_sections[title].content,
                        new_sections[title].content
                    )
                })

        # API 변경
        api_changes = await self._detect_api_changes(
            old_doc.api_documentation,
            new_doc.api_documentation
        )
        changes.extend(api_changes)

        return changes

    def _generate_diff(self, old_text: str, new_text: str) -> str:
        """텍스트 차이 생성"""

        diff = difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            lineterm=''
        )

        return ''.join(diff)

    async def rollback_version(
        self,
        component_id: str,
        target_version_id: str,
        rollback_by: str,
        reason: str
    ) -> DocumentVersion:
        """특정 버전으로 롤백"""

        # 대상 버전 조회
        target_version = await self.version_storage.get_version(target_version_id)
        target_doc = await self.version_storage.get_documentation(target_version_id)

        # 새 버전으로 생성 (롤백도 새 버전)
        rollback_version = await self.create_version(
            documentation=target_doc,
            author=rollback_by,
            change_summary=f"Rollback to version {target_version.version_number}: {reason}",
            previous_version=await self._get_latest_version(component_id)
        )

        return rollback_version
```

**검증 기준**:

- [ ] Semantic Versioning 지원
- [ ] 변경사항 추적
- [ ] 버전 간 비교 기능
- [ ] 롤백 기능 구현

### Task 4.37: 컴포넌트 테스트 생성기

#### SubTask 4.37.1: 단위 테스트 생성기

**담당자**: 테스트 자동화 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/unit_test_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import ast

@dataclass
class UnitTest:
    test_name: str
    test_description: str
    test_type: str  # positive, negative, edge_case
    setup_code: str
    test_code: str
    assertions: List[str]
    teardown_code: Optional[str]
    dependencies: List[str]
    coverage_targets: List[str]

@dataclass
class TestSuite:
    component_id: str
    component_name: str
    test_framework: str
    tests: List[UnitTest]
    setup_code: str
    teardown_code: str
    coverage_report: Dict[str, Any]
    test_data: Dict[str, Any]

class UnitTestGenerator:
    """단위 테스트 자동 생성"""

    def __init__(self):
        self.test_case_analyzer = TestCaseAnalyzer()
        self.assertion_generator = AssertionGenerator()
        self.mock_generator = MockGenerator()
        self.test_data_generator = TestDataGenerator()

    async def generate_unit_tests(
        self,
        component: ComponentDecision,
        test_framework: str = 'jest'
    ) -> TestSuite:
        """컴포넌트 단위 테스트 생성"""

        tests = []

        # 1. 컴포넌트 타입별 테스트 생성
        if component.type == ComponentType.UI_COMPONENT:
            tests.extend(await self._generate_ui_component_tests(
                component,
                test_framework
            ))
        elif component.type == ComponentType.BACKEND_SERVICE:
            tests.extend(await self._generate_service_tests(
                component,
                test_framework
            ))
        elif component.type == ComponentType.DATA_MODEL:
            tests.extend(await self._generate_model_tests(
                component,
                test_framework
            ))

        # 2. 공통 테스트 생성
        tests.extend(await self._generate_common_tests(component))

        # 3. 엣지 케이스 테스트
        tests.extend(await self._generate_edge_case_tests(component))

        # 4. 에러 처리 테스트
        tests.extend(await self._generate_error_handling_tests(component))

        # 5. 성능 테스트
        if component.properties.get('performance_critical'):
            tests.extend(await self._generate_performance_tests(component))

        # 6. 테스트 데이터 생성
        test_data = await self.test_data_generator.generate_test_data(
            component,
            tests
        )

        # 7. 테스트 스위트 설정
        setup_code = self._generate_suite_setup(component, test_framework)
        teardown_code = self._generate_suite_teardown(component, test_framework)

        # 8. 커버리지 분석
        coverage_report = await self._analyze_test_coverage(component, tests)

        return TestSuite(
            component_id=component.id,
            component_name=component.name,
            test_framework=test_framework,
            tests=tests,
            setup_code=setup_code,
            teardown_code=teardown_code,
            coverage_report=coverage_report,
            test_data=test_data
        )

    async def _generate_ui_component_tests(
        self,
        component: ComponentDecision,
        framework: str
    ) -> List[UnitTest]:
        """UI 컴포넌트 테스트 생성"""

        tests = []

        # 렌더링 테스트
        tests.append(UnitTest(
            test_name=f"should_render_{component.name}_without_errors",
            test_description=f"Verify {component.name} renders without throwing",
            test_type='positive',
            setup_code=self._generate_ui_test_setup(component, framework),
            test_code=self._generate_render_test(component, framework),
            assertions=[
                f"expect(component).toBeTruthy()",
                f"expect(container.querySelector('.{component.name.lower()}')).toBeInTheDocument()"
            ],
            teardown_code="cleanup()",
            dependencies=['@testing-library/react', 'jest'],
            coverage_targets=['render']
        ))

        # Props 검증 테스트
        for prop_name, prop_info in component.properties.get('props', {}).items():
            if prop_info.get('required'):
                tests.append(self._generate_required_prop_test(
                    component,
                    prop_name,
                    prop_info,
                    framework
                ))

        # 이벤트 핸들러 테스트
        for event in component.properties.get('events', []):
            tests.append(self._generate_event_handler_test(
                component,
                event,
                framework
            ))

        # 상태 변경 테스트
        if component.properties.get('state'):
            tests.extend(self._generate_state_tests(component, framework))

        # 접근성 테스트
        tests.append(self._generate_accessibility_test(component, framework))

        return tests

    def _generate_render_test(
        self,
        component: ComponentDecision,
        framework: str
    ) -> str:
        """렌더링 테스트 코드 생성"""

        if framework == 'jest':
            return f"""
const {{ render, screen }} = require('@testing-library/react');
const {{ {component.name} }} = require('../{component.name}');

test('renders without crashing', () => {{
  const {{ container }} = render(
    <{component.name}
      {self._generate_required_props(component)}
    />
  );

  expect(container).toBeTruthy();
}});
"""
        elif framework == 'vitest':
            return f"""
import {{ render, screen }} from '@testing-library/react';
import {{ {component.name} }} from '../{component.name}';
import {{ describe, it, expect }} from 'vitest';

describe('{component.name}', () => {{
  it('renders without crashing', () => {{
    const {{ container }} = render(
      <{component.name}
        {self._generate_required_props(component)}
      />
    );

    expect(container).toBeTruthy();
  }});
}});
"""

    def _generate_required_prop_test(
        self,
        component: ComponentDecision,
        prop_name: str,
        prop_info: Dict[str, Any],
        framework: str
    ) -> UnitTest:
        """필수 prop 테스트 생성"""

        return UnitTest(
            test_name=f"should_require_{prop_name}_prop",
            test_description=f"Verify {prop_name} is required",
            test_type='negative',
            setup_code="",
            test_code=f"""
// Suppress console.error for this test
const originalError = console.error;
beforeAll(() => {{ console.error = jest.fn(); }});
afterAll(() => {{ console.error = originalError; }});

test('throws error when {prop_name} is missing', () => {{
  expect(() => {{
    render(<{component.name} {self._generate_props_without(component, prop_name)} />);
  }}).toThrow();
}});
""",
            assertions=[
                "expect(console.error).toHaveBeenCalled()"
            ],
            teardown_code=None,
            dependencies=['prop-types'],
            coverage_targets=['prop_validation']
        )

    async def _generate_service_tests(
        self,
        component: ComponentDecision,
        framework: str
    ) -> List[UnitTest]:
        """백엔드 서비스 테스트 생성"""

        tests = []

        # 각 엔드포인트별 테스트
        for endpoint in component.interfaces.get('endpoints', []):
            # 성공 케이스
            tests.append(await self._generate_endpoint_success_test(
                component,
                endpoint,
                framework
            ))

            # 실패 케이스
            tests.append(await self._generate_endpoint_failure_test(
                component,
                endpoint,
                framework
            ))

            # 입력 검증 테스트
            if endpoint.get('validation'):
                tests.append(await self._generate_validation_test(
                    component,
                    endpoint,
                    framework
                ))

        # 인증/인가 테스트
        if component.properties.get('authentication'):
            tests.extend(await self._generate_auth_tests(component, framework))

        # 데이터베이스 트랜잭션 테스트
        if component.properties.get('uses_database'):
            tests.extend(await self._generate_transaction_tests(
                component,
                framework
            ))

        return tests

    async def _generate_endpoint_success_test(
        self,
        component: ComponentDecision,
        endpoint: Dict[str, Any],
        framework: str
    ) -> UnitTest:
        """엔드포인트 성공 테스트 생성"""

        test_data = await self.test_data_generator.generate_valid_data(endpoint)

        return UnitTest(
            test_name=f"should_handle_{endpoint['method']}_{endpoint['path']}_successfully",
            test_description=f"Test successful {endpoint['method']} request to {endpoint['path']}",
            test_type='positive',
            setup_code=f"""
const request = require('supertest');
const app = require('../app');
const {{ {component.name}Service }} = require('../services/{component.name}Service');

// Mock service
jest.mock('../services/{component.name}Service');
""",
            test_code=f"""
test('{endpoint['method']} {endpoint['path']} - success', async () => {{
  // Arrange
  const mockResponse = {self._generate_mock_response(endpoint)};
  {component.name}Service.{endpoint['handler']}.mockResolvedValue(mockResponse);

  // Act
  const response = await request(app)
    .{endpoint['method'].lower()}('{endpoint['path']}')
    .send({test_data})
    .expect(200);

  // Assert
  expect(response.body).toEqual(mockResponse);
  expect({component.name}Service.{endpoint['handler']}).toHaveBeenCalledWith({test_data});
}});
""",
            assertions=[
                "expect(response.status).toBe(200)",
                "expect(response.body).toHaveProperty('success', true)"
            ],
            teardown_code=None,
            dependencies=['supertest', 'jest'],
            coverage_targets=[f"endpoint_{endpoint['handler']}"]
        )

    async def _generate_model_tests(
        self,
        component: ComponentDecision,
        framework: str
    ) -> List[UnitTest]:
        """데이터 모델 테스트 생성"""

        tests = []

        # 모델 생성 테스트
        tests.append(self._generate_model_creation_test(component, framework))

        # 필드 검증 테스트
        for field in component.properties.get('fields', []):
            if field.get('validation'):
                tests.append(self._generate_field_validation_test(
                    component,
                    field,
                    framework
                ))

        # 관계 테스트
        for relationship in component.properties.get('relationships', []):
            tests.append(self._generate_relationship_test(
                component,
                relationship,
                framework
            ))

        # 메서드 테스트
        for method in component.properties.get('methods', []):
            tests.append(self._generate_method_test(
                component,
                method,
                framework
            ))

        return tests

    def _generate_suite_setup(
        self,
        component: ComponentDecision,
        framework: str
    ) -> str:
        """테스트 스위트 설정 코드"""

        if framework == 'jest':
            return f"""
// Test setup for {component.name}
const {{ setupTestEnvironment, teardownTestEnvironment }} = require('./test-utils');

beforeAll(async () => {{
  await setupTestEnvironment();
}});

afterAll(async () => {{
  await teardownTestEnvironment();
}});

beforeEach(() => {{
  jest.clearAllMocks();
}});
"""
        elif framework == 'pytest':
            return f"""
# Test setup for {component.name}
import pytest
from test_utils import setup_test_environment, teardown_test_environment

@pytest.fixture(scope='session')
def test_environment():
    setup_test_environment()
    yield
    teardown_test_environment()

@pytest.fixture(autouse=True)
def reset_mocks():
    yield
    # Reset all mocks after each test
"""

    async def _generate_edge_case_tests(
        self,
        component: ComponentDecision
    ) -> List[UnitTest]:
        """엣지 케이스 테스트 생성"""

        edge_cases = []

        # Null/undefined 입력
        edge_cases.append(self._generate_null_input_test(component))

        # 빈 데이터
        edge_cases.append(self._generate_empty_data_test(component))

        # 경계값
        edge_cases.append(self._generate_boundary_value_test(component))

        # 대용량 데이터
        if component.properties.get('handles_bulk_data'):
            edge_cases.append(self._generate_large_data_test(component))

        # 동시성
        if component.properties.get('concurrent_access'):
            edge_cases.append(self._generate_concurrency_test(component))

        return edge_cases

    async def export_test_suite(
        self,
        test_suite: TestSuite,
        output_format: str = 'file'
    ) -> str:
        """테스트 스위트 내보내기"""

        if output_format == 'file':
            # 파일별로 테스트 구성
            test_files = {}

            # 메인 테스트 파일
            main_file = f"{test_suite.component_name}.test.js"
            test_files[main_file] = self._generate_test_file(test_suite)

            # 헬퍼 파일
            if test_suite.test_data:
                test_files['test-data.js'] = self._generate_test_data_file(
                    test_suite.test_data
                )

            return test_files

        elif output_format == 'single':
            # 단일 파일로 모든 테스트
            return self._generate_single_test_file(test_suite)
```

**검증 기준**:

- [ ] 다양한 테스트 케이스 생성
- [ ] 테스트 프레임워크 지원
- [ ] 모의 객체 자동 생성
- [ ] 커버리지 목표 달성

---

#### SubTask 4.37.2: 통합 테스트 생성기

**담당자**: 통합 테스트 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/integration_test_generator.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class IntegrationTest:
    test_name: str
    test_description: str
    components_involved: List[str]
    test_scenario: str
    preconditions: List[str]
    test_steps: List[Dict[str, Any]]
    expected_results: List[str]
    cleanup_steps: List[str]
    test_data: Dict[str, Any]
    dependencies: List[str]

@dataclass
class IntegrationTestSuite:
    suite_name: str
    components: List[str]
    test_environment: Dict[str, Any]
    tests: List[IntegrationTest]
    setup_script: str
    teardown_script: str
    test_data_setup: str
    execution_order: List[str]

class IntegrationTestGenerator:
    """통합 테스트 생성기"""

    def __init__(self):
        self.scenario_generator = ScenarioGenerator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.data_flow_analyzer = DataFlowAnalyzer()
        self.environment_builder = TestEnvironmentBuilder()

    async def generate_integration_tests(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture,
        test_framework: str = 'jest'
    ) -> IntegrationTestSuite:
        """컴포넌트 통합 테스트 생성"""

        # 1. 통합 포인트 식별
        integration_points = await self._identify_integration_points(
            components,
            architecture
        )

        # 2. 테스트 시나리오 생성
        test_scenarios = await self.scenario_generator.generate_scenarios(
            integration_points,
            components
        )

        # 3. 각 시나리오별 테스트 생성
        tests = []
        for scenario in test_scenarios:
            test = await self._generate_integration_test(
                scenario,
                components,
                test_framework
            )
            tests.append(test)

        # 4. 데이터 흐름 테스트
        data_flow_tests = await self._generate_data_flow_tests(
            components,
            architecture
        )
        tests.extend(data_flow_tests)

        # 5. 에러 전파 테스트
        error_propagation_tests = await self._generate_error_propagation_tests(
            components,
            architecture
        )
        tests.extend(error_propagation_tests)

        # 6. 성능 통합 테스트
        performance_tests = await self._generate_performance_integration_tests(
            components,
            architecture
        )
        tests.extend(performance_tests)

        # 7. 테스트 환경 설정
        test_environment = await self.environment_builder.build_environment(
            components,
            test_framework
        )

        # 8. 실행 순서 결정
        execution_order = self._determine_execution_order(tests)

        return IntegrationTestSuite(
            suite_name=f"Integration Tests - {architecture.name}",
            components=[c.id for c in components],
            test_environment=test_environment,
            tests=tests,
            setup_script=self._generate_setup_script(components, test_framework),
            teardown_script=self._generate_teardown_script(components, test_framework),
            test_data_setup=self._generate_test_data_setup(tests),
            execution_order=execution_order
        )

    async def _identify_integration_points(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> List[Dict[str, Any]]:
        """통합 포인트 식별"""

        integration_points = []

        # API 통합 포인트
        for relationship in architecture.relationships:
            if relationship['type'] == 'api_call':
                source = next((c for c in components if c.id == relationship['source']), None)
                target = next((c for c in components if c.id == relationship['target']), None)

                if source and target:
                    integration_points.append({
                        'type': 'api_integration',
                        'source': source,
                        'target': target,
                        'interface': relationship.get('interface'),
                        'data_flow': relationship.get('data_flow')
                    })

        # 이벤트 기반 통합
        event_producers = [c for c in components if c.properties.get('produces_events')]
        event_consumers = [c for c in components if c.properties.get('consumes_events')]

        for producer in event_producers:
            for event_type in producer.properties.get('event_types', []):
                consumers = [
                    c for c in event_consumers
                    if event_type in c.properties.get('subscribed_events', [])
                ]

                for consumer in consumers:
                    integration_points.append({
                        'type': 'event_integration',
                        'source': producer,
                        'target': consumer,
                        'event_type': event_type
                    })

        # 데이터베이스 공유
        db_components = [
            c for c in components
            if c.properties.get('database_access')
        ]

        # 같은 데이터베이스를 사용하는 컴포넌트 그룹화
        db_groups = {}
        for comp in db_components:
            db_name = comp.properties.get('database_name')
            if db_name not in db_groups:
                db_groups[db_name] = []
            db_groups[db_name].append(comp)

        for db_name, comps in db_groups.items():
            if len(comps) > 1:
                integration_points.append({
                    'type': 'database_integration',
                    'components': comps,
                    'database': db_name,
                    'shared_tables': self._find_shared_tables(comps)
                })

        return integration_points

    async def _generate_integration_test(
        self,
        scenario: Dict[str, Any],
        components: List[ComponentDecision],
        framework: str
    ) -> IntegrationTest:
        """통합 테스트 생성"""

        if scenario['type'] == 'api_integration':
            return await self._generate_api_integration_test(
                scenario,
                framework
            )
        elif scenario['type'] == 'event_integration':
            return await self._generate_event_integration_test(
                scenario,
                framework
            )
        elif scenario['type'] == 'database_integration':
            return await self._generate_database_integration_test(
                scenario,
                framework
            )
        else:
            return await self._generate_generic_integration_test(
                scenario,
                framework
            )

    async def _generate_api_integration_test(
        self,
        scenario: Dict[str, Any],
        framework: str
    ) -> IntegrationTest:
        """API 통합 테스트 생성"""

        source = scenario['source']
        target = scenario['target']

        test_steps = [
            {
                'step': 'Setup target service',
                'code': f"""
// Start {target.name} service
const {target.name.lower()}Server = await start{target.name}Server({{
  port: TEST_PORT + 1,
  database: testDatabase
}});
"""
            },
            {
                'step': 'Setup source service',
                'code': f"""
// Configure {source.name} to use test {target.name} endpoint
process.env.{target.name.upper()}_URL = `http://localhost:${{TEST_PORT + 1}}`;
const {source.name.lower()}Server = await start{source.name}Server({{
  port: TEST_PORT,
  database: testDatabase
}});
"""
            },
            {
                'step': 'Execute integration scenario',
                'code': f"""
// Make request to {source.name} that triggers call to {target.name}
const response = await request({source.name.lower()}Server)
  .post('/api/{scenario["endpoint"]}')
  .send(testData)
  .expect(200);
"""
            },
            {
                'step': 'Verify integration',
                'code': f"""
// Verify {target.name} was called correctly
expect({target.name.lower()}Server.getReceivedRequests()).toHaveLength(1);
expect({target.name.lower()}Server.getLastRequest()).toMatchObject({{
  path: '{scenario["target_endpoint"]}',
  method: '{scenario["method"]}',
  body: expect.objectContaining(testData.expectedPayload)
}});

// Verify response contains data from {target.name}
expect(response.body).toHaveProperty('data');
expect(response.body.data).toMatchObject(expectedIntegratedData);
"""
            }
        ]

        return IntegrationTest(
            test_name=f"test_{source.name}_to_{target.name}_api_integration",
            test_description=f"Test API integration between {source.name} and {target.name}",
            components_involved=[source.id, target.id],
            test_scenario=scenario.get('description', 'API call integration'),
            preconditions=[
                f"{target.name} service is running",
                f"{source.name} service is configured with {target.name} endpoint",
                "Test database is initialized"
            ],
            test_steps=test_steps,
            expected_results=[
                f"{source.name} successfully calls {target.name} API",
                "Data is correctly transformed and passed",
                "Response includes integrated data from both services"
            ],
            cleanup_steps=[
                f"await {source.name.lower()}Server.close();",
                f"await {target.name.lower()}Server.close();",
                "await testDatabase.cleanup();"
            ],
            test_data=self._generate_integration_test_data(scenario),
            dependencies=[source.id, target.id]
        )

    async def _generate_event_integration_test(
        self,
        scenario: Dict[str, Any],
        framework: str
    ) -> IntegrationTest:
        """이벤트 통합 테스트 생성"""

        producer = scenario['source']
        consumer = scenario['target']
        event_type = scenario['event_type']

        test_steps = [
            {
                'step': 'Setup event bus',
                'code': """
// Initialize test event bus
const eventBus = new TestEventBus();
await eventBus.start();
"""
            },
            {
                'step': 'Setup consumer',
                'code': f"""
// Start {consumer.name} with event subscription
const {consumer.name.lower()} = new {consumer.name}({{
  eventBus,
  handlers: {{
    '{event_type}': jest.fn()
  }}
}});
await {consumer.name.lower()}.start();
"""
            },
            {
                'step': 'Setup producer',
                'code': f"""
// Start {producer.name} with event publishing
const {producer.name.lower()} = new {producer.name}({{
  eventBus
}});
"""
            },
            {
                'step': 'Trigger event',
                'code': f"""
// Perform action that triggers event
const result = await {producer.name.lower()}.{scenario['trigger_action']}(testData);

// Wait for event propagation
await waitForExpect(() => {{
  expect({consumer.name.lower()}.handlers['{event_type}']).toHaveBeenCalled();
}}, 5000);
"""
            },
            {
                'step': 'Verify event handling',
                'code': f"""
// Verify consumer received and processed event
const eventCall = {consumer.name.lower()}.handlers['{event_type}'].mock.calls[0][0];
expect(eventCall).toMatchObject({{
  type: '{event_type}',
  payload: expect.objectContaining({{
    ...expectedEventPayload
  }}),
  metadata: expect.objectContaining({{
    producer: '{producer.id}',
    timestamp: expect.any(String)
  }})
}});

// Verify consumer state changed appropriately
const consumerState = await {consumer.name.lower()}.getState();
expect(consumerState).toMatchObject(expectedStateAfterEvent);
"""
            }
        ]

        return IntegrationTest(
            test_name=f"test_{producer.name}_to_{consumer.name}_event_integration",
            test_description=f"Test event-based integration for {event_type}",
            components_involved=[producer.id, consumer.id],
            test_scenario=f"{producer.name} publishes {event_type}, {consumer.name} consumes",
            preconditions=[
                "Event bus is running",
                f"{consumer.name} is subscribed to {event_type}",
                "Test data is prepared"
            ],
            test_steps=test_steps,
            expected_results=[
                f"{event_type} event is published by {producer.name}",
                f"{consumer.name} receives and processes the event",
                "Consumer state is updated correctly"
            ],
            cleanup_steps=[
                "await eventBus.stop();",
                f"await {consumer.name.lower()}.stop();",
                "jest.clearAllMocks();"
            ],
            test_data=self._generate_event_test_data(scenario),
            dependencies=[producer.id, consumer.id, 'event_bus']
        )

    async def _generate_data_flow_tests(
        self,
        components: List[ComponentDecision],
        architecture: ComponentArchitecture
    ) -> List[IntegrationTest]:
        """데이터 흐름 테스트 생성"""

        tests = []

        # 데이터 흐름 경로 식별
        data_flows = await self.data_flow_analyzer.analyze_flows(
            components,
            architecture
        )

        for flow in data_flows:
            test_name = f"test_data_flow_{flow['name']}"

            # 데이터 변환 체인 테스트
            test_steps = []
            for i, step in enumerate(flow['steps']):
                test_steps.append({
                    'step': f"Step {i+1}: {step['component']} processes data",
                    'code': f"""
// Input data for {step['component']}
const input{i} = {self._generate_step_input(step)};

// Process through {step['component']}
const output{i} = await {step['component'].lower()}.process(input{i});

// Verify transformation
expect(output{i}).toMatchObject({self._generate_expected_output(step)});
"""
                })

            tests.append(IntegrationTest(
                test_name=test_name,
                test_description=f"Test data flow: {flow['description']}",
                components_involved=[s['component_id'] for s in flow['steps']],
                test_scenario=flow['description'],
                preconditions=flow.get('preconditions', []),
                test_steps=test_steps,
                expected_results=[
                    "Data flows correctly through all components",
                    "Each transformation is applied correctly",
                    "Final output matches expected format"
                ],
                cleanup_steps=[],
                test_data=flow.get('test_data', {}),
                dependencies=[s['component_id'] for s in flow['steps']]
            ))

        return tests

    def _generate_setup_script(
        self,
        components: List[ComponentDecision],
        framework: str
    ) -> str:
        """통합 테스트 설정 스크립트 생성"""

        if framework == 'jest':
            return f"""
// Integration test setup
const {{ MongoMemoryServer }} = require('mongodb-memory-server');
const {{ createTestDatabase }} = require('./test-utils/database');
const {{ TestEventBus }} = require('./test-utils/event-bus');
const {{ TestAPIServer }} = require('./test-utils/api-server');

let mongoServer;
let testDatabase;
let eventBus;

global.beforeAll(async () => {{
  // Start in-memory MongoDB
  mongoServer = await MongoMemoryServer.create();
  const mongoUri = mongoServer.getUri();

  // Create test database
  testDatabase = await createTestDatabase(mongoUri);
  global.testDatabase = testDatabase;

  // Initialize event bus
  eventBus = new TestEventBus();
  await eventBus.start();
  global.eventBus = eventBus;

  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.DATABASE_URL = mongoUri;
  process.env.EVENT_BUS_URL = 'memory://test';

  // Initialize component services
  {self._generate_component_initialization(components)}
}});

global.afterAll(async () => {{
  // Cleanup
  await testDatabase.close();
  await mongoServer.stop();
  await eventBus.stop();

  // Stop all services
  {self._generate_component_cleanup(components)}
}});
"""

    def _determine_execution_order(
        self,
        tests: List[IntegrationTest]
    ) -> List[str]:
        """테스트 실행 순서 결정"""

        # 의존성 그래프 생성
        dependency_graph = {}
        for test in tests:
            dependency_graph[test.test_name] = test.dependencies

        # 위상 정렬로 실행 순서 결정
        execution_order = []
        visited = set()

        def visit(test_name):
            if test_name in visited:
                return
            visited.add(test_name)

            for dep in dependency_graph.get(test_name, []):
                if dep in dependency_graph:  # dep이 테스트 이름인 경우
                    visit(dep)

            execution_order.append(test_name)

        for test_name in dependency_graph:
            visit(test_name)

        return execution_order
```

**검증 기준**:

- [ ] 컴포넌트 간 통합 포인트 식별
- [ ] 데이터 흐름 검증
- [ ] 이벤트 기반 통합 테스트
- [ ] 실행 순서 최적화

#### SubTask 4.37.3: E2E 테스트 생성기

**담당자**: E2E 테스트 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/e2e_test_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class E2ETestScenario:
    scenario_name: str
    description: str
    user_story: str
    test_steps: List[Dict[str, Any]]
    assertions: List[Dict[str, Any]]
    test_data: Dict[str, Any]
    screenshots: List[str]
    video_recording: bool

@dataclass
class E2ETestSuite:
    suite_name: str
    test_framework: str  # cypress, playwright, selenium
    base_url: str
    scenarios: List[E2ETestScenario]
    global_setup: str
    global_teardown: str
    config: Dict[str, Any]
    page_objects: Dict[str, str]

class E2ETestGenerator:
    """E2E 테스트 생성기"""

    def __init__(self):
        self.user_flow_analyzer = UserFlowAnalyzer()
        self.page_object_generator = PageObjectGenerator()
        self.test_data_factory = TestDataFactory()
        self.assertion_builder = AssertionBuilder()

    async def generate_e2e_tests(
        self,
        components: List[ComponentDecision],
        user_stories: List[Dict[str, Any]],
        test_framework: str = 'cypress'
    ) -> E2ETestSuite:
        """E2E 테스트 생성"""

        # 1. UI 컴포넌트 필터링
        ui_components = [
            c for c in components
            if c.type == ComponentType.UI_COMPONENT
        ]

        # 2. 페이지 객체 생성
        page_objects = await self._generate_page_objects(
            ui_components,
            test_framework
        )

        # 3. 사용자 플로우 분석
        user_flows = await self.user_flow_analyzer.analyze_flows(
            user_stories,
            ui_components
        )

        # 4. 각 플로우별 E2E 시나리오 생성
        scenarios = []
        for flow in user_flows:
            scenario = await self._generate_e2e_scenario(
                flow,
                ui_components,
                test_framework
            )
            scenarios.append(scenario)

        # 5. 크리티컬 패스 테스트
        critical_scenarios = await self._generate_critical_path_tests(
            user_stories,
            ui_components,
            test_framework
        )
        scenarios.extend(critical_scenarios)

        # 6. 에러 시나리오 테스트
        error_scenarios = await self._generate_error_scenarios(
            ui_components,
            test_framework
        )
        scenarios.extend(error_scenarios)

        # 7. 성능 E2E 테스트
        performance_scenarios = await self._generate_performance_e2e_tests(
            user_flows,
            test_framework
        )
        scenarios.extend(performance_scenarios)

        # 8. 테스트 설정 생성
        config = self._generate_test_config(test_framework)
        global_setup = self._generate_global_setup(test_framework)
        global_teardown = self._generate_global_teardown(test_framework)

        return E2ETestSuite(
            suite_name="E2E Test Suite",
            test_framework=test_framework,
            base_url=config['baseUrl'],
            scenarios=scenarios,
            global_setup=global_setup,
            global_teardown=global_teardown,
            config=config,
            page_objects=page_objects
        )

    async def _generate_e2e_scenario(
        self,
        flow: Dict[str, Any],
        ui_components: List[ComponentDecision],
        framework: str
    ) -> E2ETestScenario:
        """E2E 시나리오 생성"""

        test_steps = []
        assertions = []

        # 각 플로우 단계별 테스트 스텝 생성
        for step in flow['steps']:
            if framework == 'cypress':
                test_step = self._generate_cypress_step(step, ui_components)
            elif framework == 'playwright':
                test_step = self._generate_playwright_step(step, ui_components)
            else:
                test_step = self._generate_selenium_step(step, ui_components)

            test_steps.append(test_step)

            # 단계별 검증
            step_assertions = self._generate_step_assertions(
                step,
                ui_components,
                framework
            )
            assertions.extend(step_assertions)

        # 테스트 데이터 생성
        test_data = await self.test_data_factory.generate_e2e_data(flow)

        return E2ETestScenario(
            scenario_name=flow['name'],
            description=flow['description'],
            user_story=flow.get('user_story', ''),
            test_steps=test_steps,
            assertions=assertions,
            test_data=test_data,
            screenshots=self._determine_screenshot_points(flow),
            video_recording=flow.get('critical', False)
        )

    def _generate_cypress_step(
        self,
        step: Dict[str, Any],
        ui_components: List[ComponentDecision]
    ) -> Dict[str, Any]:
        """Cypress 테스트 스텝 생성"""

        action_type = step['action']
        target = step.get('target', '')
        data = step.get('data', {})

        code = ""

        if action_type == 'navigate':
            code = f"cy.visit('{step['url']}');"

        elif action_type == 'click':
            code = f"""
cy.get('{self._get_selector(target, ui_components)}')
  .should('be.visible')
  .click();
"""

        elif action_type == 'type':
            code = f"""
cy.get('{self._get_selector(target, ui_components)}')
  .should('be.visible')
  .clear()
  .type('{data.get('text', '')}');
"""

        elif action_type == 'select':
            code = f"""
cy.get('{self._get_selector(target, ui_components)}')
  .select('{data.get('value', '')}');
"""

        elif action_type == 'wait':
            code = f"cy.wait({step.get('duration', 1000)});"

        elif action_type == 'upload':
            code = f"""
cy.get('{self._get_selector(target, ui_components)}')
  .selectFile('{data.get('file_path', '')}');
"""

        elif action_type == 'drag_drop':
            code = f"""
cy.get('{self._get_selector(step['source'], ui_components)}')
  .drag('{self._get_selector(step['target'], ui_components)}');
"""

        return {
            'step_name': step.get('name', f"{action_type} {target}"),
            'code': code,
            'description': step.get('description', ''),
            'wait_before': step.get('wait_before', 0),
            'wait_after': step.get('wait_after', 0)
        }

    async def _generate_page_objects(
        self,
        ui_components: List[ComponentDecision],
        framework: str
    ) -> Dict[str, str]:
        """페이지 객체 생성"""

        page_objects = {}

        # 페이지별로 UI 컴포넌트 그룹화
        pages = self._group_components_by_page(ui_components)

        for page_name, components in pages.items():
            if framework == 'cypress':
                page_object = self._generate_cypress_page_object(
                    page_name,
                    components
                )
            elif framework == 'playwright':
                page_object = self._generate_playwright_page_object(
                    page_name,
                    components
                )
            else:
                page_object = self._generate_selenium_page_object(
                    page_name,
                    components
                )

            page_objects[page_name] = page_object

        return page_objects

    def _generate_cypress_page_object(
        self,
        page_name: str,
        components: List[ComponentDecision]
    ) -> str:
        """Cypress 페이지 객체 생성"""

        class_name = f"{page_name}Page"

        # 셀렉터 정의
        selectors = {}
        for component in components:
            selector_name = self._to_camel_case(component.name)
            selector_value = self._generate_component_selector(component)
            selectors[selector_name] = selector_value

        # 메서드 생성
        methods = []
        for component in components:
            if component.properties.get('events'):
                for event in component.properties['events']:
                    if event.startswith('on'):
                        method = self._generate_page_method(
                            component,
                            event,
                            'cypress'
                        )
                        methods.append(method)

        code = f"""
class {class_name} {{
  constructor() {{
    this.selectors = {self._format_selectors(selectors)};
  }}

  // Navigation
  visit() {{
    cy.visit('/{page_name.lower()}');
    return this;
  }}

  // Element getters
{self._generate_element_getters(selectors, 'cypress')}

  // Actions
{chr(10).join(methods)}

  // Assertions
  shouldBeVisible() {{
    Object.values(this.selectors).forEach(selector => {{
      cy.get(selector).should('be.visible');
    }});
    return this;
  }}

  // Wait for page load
  waitForLoad() {{
    cy.get(this.selectors.{next(iter(selectors))}).should('be.visible');
    return this;
  }}
}}

export default new {class_name}();
"""

        return code

    async def _generate_critical_path_tests(
        self,
        user_stories: List[Dict[str, Any]],
        ui_components: List[ComponentDecision],
        framework: str
    ) -> List[E2ETestScenario]:
        """크리티컬 패스 테스트 생성"""

        critical_scenarios = []

        # 핵심 사용자 스토리 식별
        critical_stories = [
            story for story in user_stories
            if story.get('priority') == 'critical' or story.get('is_happy_path')
        ]

        for story in critical_stories:
            # Happy path 시나리오
            happy_path = E2ETestScenario(
                scenario_name=f"critical_path_{story['id']}",
                description=f"Critical path test for: {story['title']}",
                user_story=story['description'],
                test_steps=self._generate_happy_path_steps(
                    story,
                    ui_components,
                    framework
                ),
                assertions=self._generate_critical_assertions(story),
                test_data=await self.test_data_factory.generate_happy_path_data(
                    story
                ),
                screenshots=['before_action', 'after_action', 'final_state'],
                video_recording=True  # 크리티컬 패스는 항상 녹화
            )
            critical_scenarios.append(happy_path)

        return critical_scenarios

    def _generate_test_config(self, framework: str) -> Dict[str, Any]:
        """테스트 프레임워크 설정 생성"""

        if framework == 'cypress':
            return {
                'baseUrl': 'http://localhost:3000',
                'viewportWidth': 1280,
                'viewportHeight': 720,
                'video': True,
                'screenshotOnRunFailure': True,
                'chromeWebSecurity': False,
                'defaultCommandTimeout': 10000,
                'requestTimeout': 10000,
                'responseTimeout': 10000,
                'pageLoadTimeout': 30000,
                'retries': {
                    'runMode': 2,
                    'openMode': 0
                },
                'env': {
                    'API_URL': 'http://localhost:8080/api',
                    'TEST_USER_EMAIL': 'test@example.com',
                    'TEST_USER_PASSWORD': 'TestPassword123!'
                }
            }

        elif framework == 'playwright':
            return {
                'use': {
                    'baseURL': 'http://localhost:3000',
                    'viewport': {'width': 1280, 'height': 720},
                    'screenshot': 'only-on-failure',
                    'video': 'retain-on-failure',
                    'trace': 'retain-on-failure',
                    'actionTimeout': 10000,
                    'navigationTimeout': 30000
                },
                'projects': [
                    {
                        'name': 'chromium',
                        'use': {'browserName': 'chromium'}
                    },
                    {
                        'name': 'firefox',
                        'use': {'browserName': 'firefox'}
                    },
                    {
                        'name': 'webkit',
                        'use': {'browserName': 'webkit'}
                    }
                ],
                'reporter': [
                    ['html', {'open': 'never'}],
                    ['junit', {'outputFile': 'test-results/junit.xml'}]
                ]
            }

    async def export_e2e_tests(
        self,
        suite: E2ETestSuite,
        output_dir: str
    ) -> Dict[str, str]:
        """E2E 테스트 내보내기"""

        files = {}

        # 테스트 시나리오 파일
        for scenario in suite.scenarios:
            filename = f"{scenario.scenario_name}.spec.js"
            if suite.test_framework == 'cypress':
                files[f"cypress/e2e/{filename}"] = self._export_cypress_test(
                    scenario,
                    suite
                )
            elif suite.test_framework == 'playwright':
                files[f"tests/{filename}"] = self._export_playwright_test(
                    scenario,
                    suite
                )

        # 페이지 객체 파일
        for page_name, page_object in suite.page_objects.items():
            if suite.test_framework == 'cypress':
                files[f"cypress/pages/{page_name}.page.js"] = page_object
            else:
                files[f"tests/pages/{page_name}.page.js"] = page_object

        # 설정 파일
        if suite.test_framework == 'cypress':
            files['cypress.config.js'] = self._export_cypress_config(suite.config)
        elif suite.test_framework == 'playwright':
            files['playwright.config.js'] = self._export_playwright_config(
                suite.config
            )

        # 헬퍼 파일
        files['support/commands.js'] = self._generate_custom_commands(suite)
        files['support/test-data.js'] = self._export_test_data(suite)

        return files
```

**검증 기준**:

- [ ] 사용자 시나리오 기반 테스트
- [ ] 페이지 객체 패턴 적용
- [ ] 크로스 브라우저 테스트
- [ ] 스크린샷/비디오 캡처

#### SubTask 4.37.4: 테스트 데이터 생성기

**담당자**: 테스트 데이터 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/test_data_generator.py
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from faker import Faker
import random
import string

@dataclass
class TestDataSet:
    name: str
    description: str
    data_type: str  # valid, invalid, edge_case, performance
    data: Dict[str, Any]
    expected_results: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class TestDataCollection:
    component_id: str
    datasets: List[TestDataSet]
    factories: Dict[str, Any]
    generators: Dict[str, Any]
    relationships: Dict[str, List[str]]

class TestDataGenerator:
    """테스트 데이터 생성기"""

    def __init__(self):
        self.faker = Faker()
        self.schema_analyzer = SchemaAnalyzer()
        self.constraint_resolver = ConstraintResolver()
        self.relationship_builder = RelationshipBuilder()

    async def generate_test_data(
        self,
        component: ComponentDecision,
        test_scenarios: List[Any]
    ) -> TestDataCollection:
        """컴포넌트 테스트 데이터 생성"""

        datasets = []

        # 1. 스키마 분석
        schemas = await self.schema_analyzer.analyze_component_schemas(component)

        # 2. 유효한 데이터셋 생성
        valid_datasets = await self._generate_valid_datasets(
            component,
            schemas
        )
        datasets.extend(valid_datasets)

        # 3. 무효한 데이터셋 생성
        invalid_datasets = await self._generate_invalid_datasets(
            component,
            schemas
        )
        datasets.extend(invalid_datasets)

        # 4. 엣지 케이스 데이터셋
        edge_case_datasets = await self._generate_edge_case_datasets(
            component,
            schemas
        )
        datasets.extend(edge_case_datasets)

        # 5. 성능 테스트 데이터셋
        if component.properties.get('performance_critical'):
            performance_datasets = await self._generate_performance_datasets(
                component,
                schemas
            )
            datasets.extend(performance_datasets)

        # 6. 시나리오별 데이터셋
        for scenario in test_scenarios:
            scenario_data = await self._generate_scenario_data(
                scenario,
                component,
                schemas
            )
            datasets.append(scenario_data)

        # 7. 팩토리 함수 생성
        factories = self._generate_factories(component, schemas)

        # 8. 제너레이터 함수 생성
        generators = self._generate_generators(component, schemas)

        # 9. 관계 데이터 생성
        relationships = await self.relationship_builder.build_relationships(
            component,
            datasets
        )

        return TestDataCollection(
            component_id=component.id,
            datasets=datasets,
            factories=factories,
            generators=generators,
            relationships=relationships
        )

    async def _generate_valid_datasets(
        self,
        component: ComponentDecision,
        schemas: Dict[str, Any]
    ) -> List[TestDataSet]:
        """유효한 테스트 데이터 생성"""

        valid_datasets = []

        # 최소 필수 데이터
        minimal_data = TestDataSet(
            name=f"{component.name}_minimal_valid",
            description="Minimal valid data with only required fields",
            data_type='valid',
            data=self._generate_minimal_valid_data(schemas),
            expected_results={
                'validation': 'pass',
                'processing': 'success'
            },
            metadata={
                'coverage': 'required_fields_only',
                'complexity': 'minimal'
            }
        )
        valid_datasets.append(minimal_data)

        # 전체 필드 데이터
        complete_data = TestDataSet(
            name=f"{component.name}_complete_valid",
            description="Complete valid data with all fields",
            data_type='valid',
            data=self._generate_complete_valid_data(schemas),
            expected_results={
                'validation': 'pass',
                'processing': 'success',
                'all_fields_processed': True
            },
            metadata={
                'coverage': 'all_fields',
                'complexity': 'complete'
            }
        )
        valid_datasets.append(complete_data)

        # 실제 시나리오 데이터
        realistic_data = TestDataSet(
            name=f"{component.name}_realistic",
            description="Realistic data based on actual use cases",
            data_type='valid',
            data=await self._generate_realistic_data(component, schemas),
            expected_results={
                'validation': 'pass',
                'processing': 'success',
                'business_rules': 'satisfied'
            },
            metadata={
                'coverage': 'realistic_scenario',
                'complexity': 'moderate',
                'based_on': 'production_patterns'
            }
        )
        valid_datasets.append(realistic_data)

        return valid_datasets

    async def _generate_invalid_datasets(
        self,
        component: ComponentDecision,
        schemas: Dict[str, Any]
    ) -> List[TestDataSet]:
        """무효한 테스트 데이터 생성"""

        invalid_datasets = []

        # 필수 필드 누락
        for field_name, field_schema in schemas.get('required_fields', {}).items():
            missing_field_data = self._generate_complete_valid_data(schemas)
            del missing_field_data[field_name]

            invalid_datasets.append(TestDataSet(
                name=f"{component.name}_missing_{field_name}",
                description=f"Invalid data missing required field: {field_name}",
                data_type='invalid',
                data=missing_field_data,
                expected_results={
                    'validation': 'fail',
                    'error_type': 'missing_required_field',
                    'error_field': field_name
                },
                metadata={
                    'test_target': 'required_field_validation',
                    'field': field_name
                }
            ))

        # 타입 불일치
        for field_name, field_schema in schemas.get('fields', {}).items():
            wrong_type_data = self._generate_complete_valid_data(schemas)
            wrong_type_data[field_name] = self._generate_wrong_type_value(
                field_schema['type']
            )

            invalid_datasets.append(TestDataSet(
                name=f"{component.name}_wrong_type_{field_name}",
                description=f"Invalid data with wrong type for: {field_name}",
                data_type='invalid',
                data=wrong_type_data,
                expected_results={
                    'validation': 'fail',
                    'error_type': 'type_mismatch',
                    'error_field': field_name
                },
                metadata={
                    'test_target': 'type_validation',
                    'field': field_name,
                    'expected_type': field_schema['type'],
                    'actual_type': type(wrong_type_data[field_name]).__name__
                }
            ))

        # 제약조건 위반
        constraints = schemas.get('constraints', {})
        for constraint_name, constraint_rule in constraints.items():
            constraint_violation_data = await self._generate_constraint_violation(
                constraint_name,
                constraint_rule,
                schemas
            )

            invalid_datasets.append(TestDataSet(
                name=f"{component.name}_violates_{constraint_name}",
                description=f"Invalid data violating constraint: {constraint_name}",
                data_type='invalid',
                data=constraint_violation_data,
                expected_results={
                    'validation': 'fail',
                    'error_type': 'constraint_violation',
                    'constraint': constraint_name
                },
                metadata={
                    'test_target': 'constraint_validation',
                    'constraint': constraint_name,
                    'rule': constraint_rule
                }
            ))

        return invalid_datasets

    async def _generate_edge_case_datasets(
        self,
        component: ComponentDecision,
        schemas: Dict[str, Any]
    ) -> List[TestDataSet]:
        """엣지 케이스 데이터 생성"""

        edge_cases = []

        # 경계값 테스트
        for field_name, field_schema in schemas.get('fields', {}).items():
            if field_schema['type'] in ['number', 'integer']:
                # 최소값
                if 'minimum' in field_schema:
                    min_value_data = self._generate_complete_valid_data(schemas)
                    min_value_data[field_name] = field_schema['minimum']

                    edge_cases.append(TestDataSet(
                        name=f"{component.name}_{field_name}_min_value",
                        description=f"Edge case: minimum value for {field_name}",
                        data_type='edge_case',
                        data=min_value_data,
                        expected_results={
                            'validation': 'pass',
                            'processing': 'success'
                        },
                        metadata={
                            'test_target': 'boundary_value',
                            'field': field_name,
                            'boundary': 'minimum'
                        }
                    ))

                # 최대값
                if 'maximum' in field_schema:
                    max_value_data = self._generate_complete_valid_data(schemas)
                    max_value_data[field_name] = field_schema['maximum']

                    edge_cases.append(TestDataSet(
                        name=f"{component.name}_{field_name}_max_value",
                        description=f"Edge case: maximum value for {field_name}",
                        data_type='edge_case',
                        data=max_value_data,
                        expected_results={
                            'validation': 'pass',
                            'processing': 'success'
                        },
                        metadata={
                            'test_target': 'boundary_value',
                            'field': field_name,
                            'boundary': 'maximum'
                        }
                    ))

            elif field_schema['type'] == 'string':
                # 빈 문자열
                if not field_schema.get('minLength'):
                    empty_string_data = self._generate_complete_valid_data(schemas)
                    empty_string_data[field_name] = ''

                    edge_cases.append(TestDataSet(
                        name=f"{component.name}_{field_name}_empty",
                        description=f"Edge case: empty string for {field_name}",
                        data_type='edge_case',
                        data=empty_string_data,
                        expected_results={
                            'validation': 'pass' if not field_schema.get('required') else 'fail',
                            'processing': 'success' if not field_schema.get('required') else 'fail'
                        },
                        metadata={
                            'test_target': 'empty_value',
                            'field': field_name
                        }
                    ))

                # 최대 길이
                if 'maxLength' in field_schema:
                    max_length_data = self._generate_complete_valid_data(schemas)
                    max_length_data[field_name] = 'a' * field_schema['maxLength']

                    edge_cases.append(TestDataSet(
                        name=f"{component.name}_{field_name}_max_length",
                        description=f"Edge case: maximum length for {field_name}",
                        data_type='edge_case',
                        data=max_length_data,
                        expected_results={
                            'validation': 'pass',
                            'processing': 'success'
                        },
                        metadata={
                            'test_target': 'max_length',
                            'field': field_name,
                            'length': field_schema['maxLength']
                        }
                    ))

        # 특수 문자 테스트
        special_chars_data = self._generate_complete_valid_data(schemas)
        for field_name, field_schema in schemas.get('fields', {}).items():
            if field_schema['type'] == 'string':
                special_chars_data[field_name] = self._generate_special_chars_string()

        edge_cases.append(TestDataSet(
            name=f"{component.name}_special_characters",
            description="Edge case: special characters in string fields",
            data_type='edge_case',
            data=special_chars_data,
            expected_results={
                'validation': 'pass',
                'processing': 'success',
                'encoding': 'preserved'
            },
            metadata={
                'test_target': 'special_characters',
                'includes': 'unicode, emoji, symbols'
            }
        ))

        return edge_cases

    def _generate_factories(
        self,
        component: ComponentDecision,
        schemas: Dict[str, Any]
    ) -> Dict[str, Any]:
        """팩토리 함수 생성"""

        factories = {}

        # 기본 팩토리
        factories['default'] = f"""
function create{component.name}(overrides = {{}}) {{
  const defaults = {self._generate_complete_valid_data(schemas)};
  return {{ ...defaults, ...overrides }};
}}
"""

        # 상태별 팩토리
        if component.properties.get('states'):
            for state in component.properties['states']:
                factories[state] = f"""
function create{component.name}{state.title()}(overrides = {{}}) {{
  const base = create{component.name}();
  const stateData = {{
    state: '{state}',
    {self._generate_state_specific_data(state, schemas)}
  }};
  return {{ ...base, ...stateData, ...overrides }};
}}
"""

        # 시나리오별 팩토리
        factories['withRelations'] = f"""
function create{component.name}WithRelations(overrides = {{}}) {{
  const base = create{component.name}();
  const relations = {{
    {self._generate_relation_data(component)}
  }};
  return {{ ...base, ...relations, ...overrides }};
}}
"""

        return factories

    def _generate_generators(
        self,
        component: ComponentDecision,
        schemas: Dict[str, Any]
    ) -> Dict[str, Any]:
        """제너레이터 함수 생성"""

        generators = {}

        # 배치 생성기
        generators['batch'] = f"""
function* generate{component.name}Batch(count = 10) {{
  for (let i = 0; i < count; i++) {{
    yield create{component.name}({{
      id: faker.datatype.uuid(),
      {self._generate_sequential_data('i')}
    }});
  }}
}}
"""

        # 시계열 생성기
        if component.properties.get('temporal'):
            generators['timeSeries'] = f"""
function* generate{component.name}TimeSeries(startDate, endDate, interval = 'hour') {{
  const current = new Date(startDate);
  const end = new Date(endDate);

  while (current <= end) {{
    yield create{component.name}({{
      timestamp: current.toISOString(),
      {self._generate_time_based_data()}
    }});

    // Increment based on interval
    if (interval === 'hour') current.setHours(current.getHours() + 1);
    else if (interval === 'day') current.setDate(current.getDate() + 1);
  }}
}}
"""

        # 연관 데이터 생성기
        generators['connected'] = f"""
function* generate{component.name}Graph(nodes = 5, edgesPerNode = 2) {{
  const generated = [];

  // Generate nodes
  for (let i = 0; i < nodes; i++) {{
    generated.push(create{component.name}({{ id: `node_${{i}}` }}));
  }}

  // Generate edges
  for (let i = 0; i < nodes; i++) {{
    for (let j = 0; j < edgesPerNode; j++) {{
      const targetIndex = Math.floor(Math.random() * nodes);
      if (targetIndex !== i) {{
        generated[i].connections = generated[i].connections || [];
        generated[i].connections.push(generated[targetIndex].id);
      }}
    }}
  }}

  yield* generated;
}}
"""

        return generators

    def _generate_special_chars_string(self) -> str:
        """특수 문자 문자열 생성"""

        special_sets = [
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",  # 일반 특수문자
            "àáäâèéëêìíïîòóöôùúüû",  # 유럽 문자
            "你好世界",  # 중국어
            "こんにちは",  # 일본어
            "🎉🔥💻🚀",  # 이모지
            "\n\r\t",  # 제어 문자
            "\\\"'`",  # 이스케이프 문자
        ]

        return ''.join(random.choice(special_sets))

    async def export_test_data(
        self,
        collection: TestDataCollection,
        format: str = 'json'
    ) -> str:
        """테스트 데이터 내보내기"""

        if format == 'json':
            return json.dumps({
                'component_id': collection.component_id,
                'datasets': [
                    {
                        'name': ds.name,
                        'description': ds.description,
                        'data': ds.data,
                        'expected': ds.expected_results
                    }
                    for ds in collection.datasets
                ],
                'factories': collection.factories,
                'generators': collection.generators
            }, indent=2)

        elif format == 'javascript':
            return f"""
// Test data for {collection.component_id}
const faker = require('faker');

// Datasets
{self._export_datasets_js(collection.datasets)}

// Factories
{self._export_factories_js(collection.factories)}

// Generators
{self._export_generators_js(collection.generators)}

module.exports = {{
  datasets,
  factories,
  generators
}};
"""
```

**검증 기준**:

- [ ] 다양한 데이터 타입 지원
- [ ] 유효/무효 데이터 생성
- [ ] 엣지 케이스 커버
- [ ] 팩토리 패턴 구현

### Task 4.38: 컴포넌트 의존성 관리

#### SubTask 4.38.1: 의존성 분석기

**담당자**: 의존성 관리 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/dependency_analyzer.py
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import networkx as nx

@dataclass
class Dependency:
    source_id: str
    target_id: str
    dependency_type: str  # compile, runtime, test, optional
    version_constraint: str
    is_direct: bool
    is_circular: bool
    metadata: Dict[str, Any]

@dataclass
class DependencyAnalysis:
    component_id: str
    direct_dependencies: List[Dependency]
    transitive_dependencies: List[Dependency]
    dependency_tree: Dict[str, Any]
    circular_dependencies: List[List[str]]
    dependency_depth: int
    risk_score: float
    vulnerabilities: List[Dict[str, Any]]
    update_suggestions: List[Dict[str, Any]]

class ComponentDependencyAnalyzer:
    """컴포넌트 의존성 분석기"""

    def __init__(self):
        self.graph_builder = DependencyGraphBuilder()
        self.cycle_detector = CycleDetector()
        self.version_analyzer = VersionAnalyzer()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.impact_calculator = ImpactCalculator()

    async def analyze_dependencies(
        self,
        component: ComponentDecision,
        all_components: List[ComponentDecision],
        external_dependencies: Optional[Dict[str, Any]] = None
    ) -> DependencyAnalysis:
        """컴포넌트 의존성 분석"""

        # 1. 의존성 그래프 구축
        dependency_graph = await self.graph_builder.build_graph(
            component,
            all_components,
            external_dependencies
        )

        # 2. 직접 의존성 추출
        direct_dependencies = self._extract_direct_dependencies(
            component,
            all_components,
            external_dependencies
        )

        # 3. 전이적 의존성 계산
        transitive_dependencies = await self._calculate_transitive_dependencies(
            component,
            dependency_graph
        )

        # 4. 순환 의존성 검출
        circular_dependencies = await self.cycle_detector.detect_cycles(
            dependency_graph
        )

        # 5. 의존성 트리 생성
        dependency_tree = self._build_dependency_tree(
            component,
            direct_dependencies,
            transitive_dependencies
        )

        # 6. 의존성 깊이 계산
        dependency_depth = self._calculate_dependency_depth(
            dependency_tree
        )

        # 7. 위험도 평가
        risk_score = await self._assess_dependency_risk(
            direct_dependencies,
            transitive_dependencies,
            circular_dependencies,
            dependency_depth
        )

        # 8. 취약점 스캔
        vulnerabilities = await self.vulnerability_scanner.scan_dependencies(
            direct_dependencies + transitive_dependencies,
            external_dependencies
        )

        # 9. 업데이트 제안
        update_suggestions = await self._generate_update_suggestions(
            direct_dependencies,
            vulnerabilities
        )

        return DependencyAnalysis(
            component_id=component.id,
            direct_dependencies=direct_dependencies,
            transitive_dependencies=transitive_dependencies,
            dependency_tree=dependency_tree,
            circular_dependencies=circular_dependencies,
            dependency_depth=dependency_depth,
            risk_score=risk_score,
            vulnerabilities=vulnerabilities,
            update_suggestions=update_suggestions
        )

    def _extract_direct_dependencies(
        self,
        component: ComponentDecision,
        all_components: List[ComponentDecision],
        external_dependencies: Optional[Dict[str, Any]]
    ) -> List[Dependency]:
        """직접 의존성 추출"""

        direct_deps = []

        # 내부 컴포넌트 의존성
        for dep_id in component.dependencies:
            dep_component = next(
                (c for c in all_components if c.id == dep_id),
                None
            )

            if dep_component:
                direct_deps.append(Dependency(
                    source_id=component.id,
                    target_id=dep_id,
                    dependency_type='runtime',
                    version_constraint='*',  # 내부 컴포넌트는 버전 제약 없음
                    is_direct=True,
                    is_circular=False,  # 나중에 검사
                    metadata={
                        'component_type': dep_component.type.value,
                        'internal': True
                    }
                ))

        # 외부 라이브러리 의존성
        if external_dependencies:
            for lib_name, lib_info in external_dependencies.items():
                direct_deps.append(Dependency(
                    source_id=component.id,
                    target_id=lib_name,
                    dependency_type=lib_info.get('type', 'runtime'),
                    version_constraint=lib_info.get('version', '*'),
                    is_direct=True,
                    is_circular=False,
                    metadata={
                        'package_manager': lib_info.get('package_manager', 'npm'),
                        'license': lib_info.get('license'),
                        'external': True
                    }
                ))

        return direct_deps

    async def _calculate_transitive_dependencies(
        self,
        component: ComponentDecision,
        dependency_graph: nx.DiGraph
    ) -> List[Dependency]:
        """전이적 의존성 계산"""

        transitive_deps = []
        visited = set()

        def traverse_dependencies(node_id: str, path: List[str]):
            if node_id in visited:
                return

            visited.add(node_id)

            # 현재 노드의 의존성 탐색
            for successor in dependency_graph.successors(node_id):
                if successor not in path:  # 순환 방지
                    # 전이적 의존성 추가
                    if len(path) > 1:  # 직접 의존성 제외
                        edge_data = dependency_graph.get_edge_data(
                            node_id,
                            successor
                        )

                        transitive_deps.append(Dependency(
                            source_id=component.id,
                            target_id=successor,
                            dependency_type=edge_data.get('type', 'runtime'),
                            version_constraint=edge_data.get('version', '*'),
                            is_direct=False,
                            is_circular=False,
                            metadata={
                                'path': path + [successor],
                                'distance': len(path)
                            }
                        ))

                    # 재귀적으로 탐색
                    traverse_dependencies(successor, path + [successor])

        # 컴포넌트부터 시작
        traverse_dependencies(component.id, [component.id])

        return transitive_deps

    def _build_dependency_tree(
        self,
        component: ComponentDecision,
        direct_deps: List[Dependency],
        transitive_deps: List[Dependency]
    ) -> Dict[str, Any]:
        """의존성 트리 생성"""

        tree = {
            'id': component.id,
            'name': component.name,
            'version': component.properties.get('version', '1.0.0'),
            'dependencies': {}
        }

        # 직접 의존성 추가
        for dep in direct_deps:
            tree['dependencies'][dep.target_id] = {
                'id': dep.target_id,
                'version': dep.version_constraint,
                'type': dep.dependency_type,
                'direct': True,
                'dependencies': {}
            }

        # 전이적 의존성을 트리에 추가
        for trans_dep in transitive_deps:
            path = trans_dep.metadata.get('path', [])
            current_node = tree['dependencies']

            # 경로를 따라 트리 구축
            for i, node_id in enumerate(path[1:-1]):  # 첫 번째와 마지막 제외
                if node_id not in current_node:
                    current_node[node_id] = {
                        'id': node_id,
                        'dependencies': {}
                    }
                current_node = current_node[node_id]['dependencies']

            # 마지막 노드 추가
            if len(path) > 1:
                last_node_id = path[-1]
                current_node[last_node_id] = {
                    'id': last_node_id,
                    'version': trans_dep.version_constraint,
                    'type': trans_dep.dependency_type,
                    'direct': False,
                    'dependencies': {}
                }

        return tree

    async def _assess_dependency_risk(
        self,
        direct_deps: List[Dependency],
        transitive_deps: List[Dependency],
        circular_deps: List[List[str]],
        depth: int
    ) -> float:
        """의존성 위험도 평가"""

        risk_score = 0.0

        # 1. 의존성 수에 따른 위험도
        total_deps = len(direct_deps) + len(transitive_deps)
        if total_deps > 50:
            risk_score += 20
        elif total_deps > 20:
            risk_score += 10
        elif total_deps > 10:
            risk_score += 5

        # 2. 의존성 깊이에 따른 위험도
        if depth > 10:
            risk_score += 25
        elif depth > 5:
            risk_score += 15
        elif depth > 3:
            risk_score += 5

        # 3. 순환 의존성에 따른 위험도
        if circular_deps:
            risk_score += len(circular_deps) * 15

        # 4. 외부 의존성 비율
        external_deps = [
            d for d in direct_deps + transitive_deps
            if d.metadata.get('external', False)
        ]
        external_ratio = len(external_deps) / max(total_deps, 1)
        risk_score += external_ratio * 10

        # 5. 버전 제약 엄격성
        strict_versions = [
            d for d in direct_deps
            if self._is_strict_version_constraint(d.version_constraint)
        ]
        if len(strict_versions) / max(len(direct_deps), 1) > 0.5:
            risk_score += 10

        # 6. 라이선스 위험도
        risky_licenses = ['GPL', 'AGPL', 'LGPL']
        for dep in direct_deps + transitive_deps:
            if dep.metadata.get('license') in risky_licenses:
                risk_score += 5

        # 정규화 (0-100)
        return min(risk_score, 100.0)

    async def _generate_update_suggestions(
        self,
        dependencies: List[Dependency],
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """업데이트 제안 생성"""

        suggestions = []

        # 취약점이 있는 의존성 업데이트
        for vuln in vulnerabilities:
            dep = next(
                (d for d in dependencies if d.target_id == vuln['package']),
                None
            )

            if dep and vuln.get('fixed_version'):
                suggestions.append({
                    'type': 'security_update',
                    'package': dep.target_id,
                    'current_version': dep.version_constraint,
                    'suggested_version': vuln['fixed_version'],
                    'reason': f"Security vulnerability: {vuln['vulnerability_id']}",
                    'severity': vuln['severity'],
                    'priority': 'high'
                })

        # 오래된 버전 업데이트
        for dep in dependencies:
            if dep.metadata.get('external'):
                latest_version = await self.version_analyzer.get_latest_version(
                    dep.target_id,
                    dep.metadata.get('package_manager', 'npm')
                )

                if latest_version and self._is_outdated(
                    dep.version_constraint,
                    latest_version
                ):
                    suggestions.append({
                        'type': 'version_update',
                        'package': dep.target_id,
                        'current_version': dep.version_constraint,
                        'suggested_version': latest_version,
                        'reason': 'Newer version available',
                        'priority': 'medium'
                    })

        # 중복 의존성 제거
        duplicate_packages = self._find_duplicate_dependencies(dependencies)
        for dup_group in duplicate_packages:
            suggestions.append({
                'type': 'deduplicate',
                'packages': dup_group,
                'reason': 'Multiple versions of same package',
                'priority': 'low'
            })

        return suggestions

    def _calculate_dependency_depth(self, tree: Dict[str, Any]) -> int:
        """의존성 트리 깊이 계산"""

        def get_max_depth(node: Dict[str, Any], current_depth: int = 0) -> int:
            if not node.get('dependencies'):
                return current_depth

            max_child_depth = current_depth
            for child in node['dependencies'].values():
                child_depth = get_max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

            return max_child_depth

        return get_max_depth(tree)

    async def generate_dependency_report(
        self,
        analysis: DependencyAnalysis
    ) -> str:
        """의존성 분석 보고서 생성"""

        report = f"""
# Dependency Analysis Report for {analysis.component_id}

## Summary
- Direct Dependencies: {len(analysis.direct_dependencies)}
- Transitive Dependencies: {len(analysis.transitive_dependencies)}
- Maximum Dependency Depth: {analysis.dependency_depth}
- Risk Score: {analysis.risk_score}/100
- Circular Dependencies: {len(analysis.circular_dependencies)}
- Vulnerabilities Found: {len(analysis.vulnerabilities)}

## Dependency Tree
```

{self.\_format_dependency_tree(analysis.dependency_tree)}

```

## Risk Assessment
{self._format_risk_assessment(analysis)}

## Vulnerabilities
{self._format_vulnerabilities(analysis.vulnerabilities)}

## Update Recommendations
{self._format_update_suggestions(analysis.update_suggestions)}

## Circular Dependencies
{self._format_circular_dependencies(analysis.circular_dependencies)}
"""

        return report
```

**검증 기준**:

- [ ] 전이적 의존성 추적
- [ ] 순환 의존성 검출
- [ ] 취약점 스캔 통합
- [ ] 위험도 정량화

#### SubTask 4.38.2: 버전 호환성 관리기

**담당자**: 버전 관리 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/version_compatibility_manager.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import semver
from packaging import version

@dataclass
class VersionConstraint:
    constraint_type: str  # exact, range, caret, tilde
    version_spec: str
    min_version: Optional[str]
    max_version: Optional[str]
    includes_prerelease: bool

@dataclass
class CompatibilityResult:
    is_compatible: bool
    conflicts: List[Dict[str, Any]]
    resolution_suggestions: List[Dict[str, Any]]
    compatible_version_range: Optional[str]
    upgrade_path: List[Dict[str, Any]]

class VersionCompatibilityManager:
    """버전 호환성 관리기"""

    def __init__(self):
        self.constraint_parser = ConstraintParser()
        self.version_resolver = VersionResolver()
        self.conflict_resolver = ConflictResolver()
        self.upgrade_planner = UpgradePlanner()

    async def check_compatibility(
        self,
        component: ComponentDecision,
        dependencies: List[Dependency],
        target_versions: Optional[Dict[str, str]] = None
    ) -> CompatibilityResult:
        """버전 호환성 검사"""

        conflicts = []

        # 1. 의존성 버전 제약 파싱
        constraints = {}
        for dep in dependencies:
            constraint = self.constraint_parser.parse(dep.version_constraint)
            if dep.target_id not in constraints:
                constraints[dep.target_id] = []
            constraints[dep.target_id].append({
                'source': dep.source_id,
                'constraint': constraint
            })

        # 2. 버전 충돌 검사
        for package_id, package_constraints in constraints.items():
            if len(package_constraints) > 1:
                conflict = self._check_constraint_conflicts(
                    package_id,
                    package_constraints
                )
                if conflict:
                    conflicts.append(conflict)

        # 3. 타겟 버전과의 호환성 검사
        if target_versions:
            for package_id, target_version in target_versions.items():
                if package_id in constraints:
                    for constraint_info in constraints[package_id]:
                        if not self._satisfies_constraint(
                            target_version,
                            constraint_info['constraint']
                        ):
                            conflicts.append({
                                'type': 'target_version_conflict',
                                'package': package_id,
                                'target_version': target_version,
                                'constraint': constraint_info['constraint'],
                                'source': constraint_info['source']
                            })

        # 4. 호환 가능한 버전 범위 계산
        compatible_ranges = {}
        for package_id, package_constraints in constraints.items():
            compatible_range = self._calculate_compatible_range(
                package_constraints
            )
            if compatible_range:
                compatible_ranges[package_id] = compatible_range

        # 5. 충돌 해결 제안
        resolution_suggestions = []
        if conflicts:
            resolution_suggestions = await self.conflict_resolver.resolve_conflicts(
                conflicts,
                constraints
            )

        # 6. 업그레이드 경로 계획
        upgrade_path = []
        if conflicts or target_versions:
            upgrade_path = await self.upgrade_planner.plan_upgrade(
                component,
                dependencies,
                target_versions,
                conflicts
            )

        return CompatibilityResult(
            is_compatible=len(conflicts) == 0,
            conflicts=conflicts,
            resolution_suggestions=resolution_suggestions,
            compatible_version_range=self._format_version_ranges(compatible_ranges),
            upgrade_path=upgrade_path
        )

    def _check_constraint_conflicts(
        self,
        package_id: str,
        constraints: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """제약조건 충돌 검사"""

        # 모든 제약조건을 만족하는 버전이 있는지 확인
        all_constraints = [c['constraint'] for c in constraints]

        # 교집합 계산
        intersection = self._intersect_constraints(all_constraints)

        if not intersection:
            return {
                'type': 'version_constraint_conflict',
                'package': package_id,
                'constraints': [
                    {
                        'source': c['source'],
                        'constraint': c['constraint'].version_spec
                    }
                    for c in constraints
                ],
                'reason': 'No version satisfies all constraints'
            }

        return None

    def _intersect_constraints(
        self,
        constraints: List[VersionConstraint]
    ) -> Optional[VersionConstraint]:
        """제약조건 교집합 계산"""

        if not constraints:
            return None

        # 최소/최대 버전 계산
        min_version = None
        max_version = None

        for constraint in constraints:
            if constraint.min_version:
                if not min_version or version.parse(constraint.min_version) > version.parse(min_version):
                    min_version = constraint.min_version

            if constraint.max_version:
                if not max_version or version.parse(constraint.max_version) < version.parse(max_version):
                    max_version = constraint.max_version

        # 유효한 범위인지 확인
        if min_version and max_version:
            if version.parse(min_version) > version.parse(max_version):
                return None

        return VersionConstraint(
            constraint_type='range',
            version_spec=f">={min_version} <={max_version}" if min_version and max_version else '*',
            min_version=min_version,
            max_version=max_version,
            includes_prerelease=any(c.includes_prerelease for c in constraints)
        )

    def _satisfies_constraint(
        self,
        version_str: str,
        constraint: VersionConstraint
    ) -> bool:
        """버전이 제약조건을 만족하는지 확인"""

        try:
            ver = version.parse(version_str)

            if constraint.constraint_type == 'exact':
                return ver == version.parse(constraint.version_spec)

            elif constraint.constraint_type == 'range':
                if constraint.min_version:
                    if ver < version.parse(constraint.min_version):
                        return False
                if constraint.max_version:
                    if ver > version.parse(constraint.max_version):
                        return False
                return True

            elif constraint.constraint_type == 'caret':
                # ^1.2.3 := >=1.2.3 <2.0.0
                base = version.parse(constraint.version_spec.lstrip('^'))
                if base.major == 0:
                    # 0.x.y의 경우 마이너 버전 고정
                    return (ver.major == base.major and
                           ver.minor == base.minor and
                           ver.micro >= base.micro)
                else:
                    return (ver.major == base.major and
                           ver >= base)

            elif constraint.constraint_type == 'tilde':
                # ~1.2.3 := >=1.2.3 <1.3.0
                base = version.parse(constraint.version_spec.lstrip('~'))
                return (ver.major == base.major and
                       ver.minor == base.minor and
                       ver.micro >= base.micro)

        except Exception:
            return False

        return True

    async def analyze_breaking_changes(
        self,
        component: ComponentDecision,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """브레이킹 체인지 분석"""

        breaking_changes = {
            'has_breaking_changes': False,
            'api_changes': [],
            'behavior_changes': [],
            'dependency_changes': [],
            'migration_required': False,
            'migration_guide': None
        }

        # Semantic Versioning 기준 메이저 버전 변경 확인
        from_ver = semver.VersionInfo.parse(from_version)
        to_ver = semver.VersionInfo.parse(to_version)

        if to_ver.major > from_ver.major:
            breaking_changes['has_breaking_changes'] = True
            breaking_changes['migration_required'] = True

        # API 변경사항 분석
        if component.type == ComponentType.API_ENDPOINT:
            api_changes = await self._analyze_api_changes(
                component,
                from_version,
                to_version
            )
            breaking_changes['api_changes'] = api_changes

        # 의존성 변경사항 분석
        dependency_changes = await self._analyze_dependency_changes(
            component,
            from_version,
            to_version
        )
        breaking_changes['dependency_changes'] = dependency_changes

        # 마이그레이션 가이드 생성
        if breaking_changes['has_breaking_changes']:
            breaking_changes['migration_guide'] = await self._generate_migration_guide(
                component,
                from_version,
                to_version,
                breaking_changes
            )

        return breaking_changes

    async def _analyze_api_changes(
        self,
        component: ComponentDecision,
        from_version: str,
        to_version: str
    ) -> List[Dict[str, Any]]:
        """API 변경사항 분석"""

        api_changes = []

        # 엔드포인트 변경 확인
        old_endpoints = component.properties.get(f'endpoints_v{from_version}', [])
        new_endpoints = component.properties.get(f'endpoints_v{to_version}', [])

        # 제거된 엔드포인트
        removed = set(old_endpoints) - set(new_endpoints)
        for endpoint in removed:
            api_changes.append({
                'type': 'endpoint_removed',
                'endpoint': endpoint,
                'breaking': True,
                'migration': f"Replace calls to {endpoint}"
            })

        # 추가된 엔드포인트
        added = set(new_endpoints) - set(old_endpoints)
        for endpoint in added:
            api_changes.append({
                'type': 'endpoint_added',
                'endpoint': endpoint,
                'breaking': False
            })

        # 변경된 엔드포인트 (시그니처, 파라미터 등)
        # 실제 구현에서는 더 상세한 비교 필요

        return api_changes

    async def create_version_lock_file(
        self,
        component: ComponentDecision,
        resolved_versions: Dict[str, str]
    ) -> str:
        """버전 잠금 파일 생성"""

        lock_file_content = {
            'component': {
                'id': component.id,
                'name': component.name,
                'version': component.properties.get('version', '1.0.0')
            },
            'lockfileVersion': 1,
            'dependencies': {},
            'resolved_at': datetime.utcnow().isoformat()
        }

        # 의존성 정보 추가
        for dep_id, dep_version in resolved_versions.items():
            lock_file_content['dependencies'][dep_id] = {
                'version': dep_version,
                'resolved': dep_version,
                'integrity': await self._calculate_integrity_hash(
                    dep_id,
                    dep_version
                )
            }

        # 플랫폼별 포맷
        if component.technology_stack[0] == 'nodejs':
            return self._format_npm_lock(lock_file_content)
        elif component.technology_stack[0] == 'python':
            return self._format_pipfile_lock(lock_file_content)
        else:
            return json.dumps(lock_file_content, indent=2)

    def _calculate_compatible_range(
        self,
        constraints: List[Dict[str, Any]]
    ) -> Optional[str]:
        """호환 가능한 버전 범위 계산"""

        all_constraints = [c['constraint'] for c in constraints]
        intersection = self._intersect_constraints(all_constraints)

        if intersection:
            return intersection.version_spec

        return None
```

**검증 기준**:

- [ ] Semantic Versioning 준수
- [ ] 버전 충돌 감지
- [ ] 브레이킹 체인지 분석
- [ ] 버전 잠금 파일 생성

#### SubTask 4.38.3: 의존성 주입 시스템

**담당자**: DI 컨테이너 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/dependency_injection.py
from typing import List, Dict, Any, Optional, Type, Callable
from dataclasses import dataclass
from enum import Enum
import inspect
from abc import ABC, abstractmethod

@dataclass
class ServiceDefinition:
    service_id: str
    service_class: Type
    scope: str  # singleton, transient, scoped
    factory: Optional[Callable]
    dependencies: List[str]
    metadata: Dict[str, Any]

@dataclass
class InjectionPoint:
    target_class: Type
    injection_type: str  # constructor, property, method
    parameter_name: str
    service_id: str
    is_optional: bool

class DependencyInjectionSystem:
    """의존성 주입 시스템"""

    def __init__(self):
        self.container = DIContainer()
        self.service_registry = ServiceRegistry()
        self.injection_analyzer = InjectionAnalyzer()
        self.lifecycle_manager = LifecycleManager()

    async def configure_di_for_component(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> Dict[str, Any]:
        """컴포넌트를 위한 DI 설정"""

        di_config = {
            'container_config': {},
            'service_definitions': [],
            'injection_points': [],
            'bindings': [],
            'modules': []
        }

        # 1. 서비스 정의 생성
        services = await self._generate_service_definitions(
            component,
            architecture
        )
        di_config['service_definitions'] = services

        # 2. 주입 포인트 분석
        injection_points = await self._analyze_injection_points(
            component,
            services
        )
        di_config['injection_points'] = injection_points

        # 3. 바인딩 생성
        bindings = self._generate_bindings(
            component,
            services,
            injection_points
        )
        di_config['bindings'] = bindings

        # 4. DI 모듈 생성
        modules = await self._generate_di_modules(
            component,
            services,
            bindings
        )
        di_config['modules'] = modules

        # 5. 컨테이너 설정
        di_config['container_config'] = self._generate_container_config(
            component
        )

        return di_config

    async def _generate_service_definitions(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> List[ServiceDefinition]:
        """서비스 정의 생성"""

        services = []

        # 컴포넌트 타입별 서비스 생성
        if component.type == ComponentType.BACKEND_SERVICE:
            # 컨트롤러 서비스
            services.append(ServiceDefinition(
                service_id=f"{component.name}Controller",
                service_class=f"{component.name}Controller",
                scope='singleton',
                factory=None,
                dependencies=self._extract_controller_dependencies(component),
                metadata={
                    'component_id': component.id,
                    'type': 'controller'
                }
            ))

            # 서비스 레이어
            services.append(ServiceDefinition(
                service_id=f"{component.name}Service",
                service_class=f"{component.name}Service",
                scope='singleton',
                factory=None,
                dependencies=self._extract_service_dependencies(component),
                metadata={
                    'component_id': component.id,
                    'type': 'service'
                }
            ))

            # 리포지토리
            if component.properties.get('uses_database'):
                services.append(ServiceDefinition(
                    service_id=f"{component.name}Repository",
                    service_class=f"{component.name}Repository",
                    scope='singleton',
                    factory=None,
                    dependencies=['DatabaseConnection'],
                    metadata={
                        'component_id': component.id,
                        'type': 'repository'
                    }
                ))

        # 공통 서비스
        services.extend(self._generate_common_services(component))

        # 의존 컴포넌트 서비스
        for dep_id in component.dependencies:
            dep_component = next(
                (c for c in architecture.components if c.id == dep_id),
                None
            )
            if dep_component:
                services.append(ServiceDefinition(
                    service_id=f"{dep_component.name}Client",
                    service_class=f"{dep_component.name}Client",
                    scope='singleton',
                    factory=self._create_client_factory(dep_component),
                    dependencies=[],
                    metadata={
                        'component_id': dep_component.id,
                        'type': 'client',
                        'remote': True
                    }
                ))

        return services

    def _generate_bindings(
        self,
        component: ComponentDecision,
        services: List[ServiceDefinition],
        injection_points: List[InjectionPoint]
    ) -> List[Dict[str, Any]]:
        """바인딩 생성"""

        bindings = []

        # 인터페이스 바인딩
        for service in services:
            interface_name = f"I{service.service_class}"
            bindings.append({
                'interface': interface_name,
                'implementation': service.service_class,
                'scope': service.scope,
                'name': service.service_id
            })

        # 팩토리 바인딩
        factory_services = [s for s in services if s.factory]
        for service in factory_services:
            bindings.append({
                'interface': service.service_class,
                'factory': service.factory,
                'scope': service.scope,
                'name': service.service_id
            })

        # 조건부 바인딩
        if component.properties.get('environment_specific'):
            bindings.extend(self._generate_conditional_bindings(component))

        return bindings

    async def _generate_di_modules(
        self,
        component: ComponentDecision,
        services: List[ServiceDefinition],
        bindings: List[Dict[str, Any]]
    ) -> List[str]:
        """DI 모듈 코드 생성"""

        modules = []

        # TypeScript (InversifyJS)
        if 'typescript' in component.technology_stack:
            modules.append(self._generate_inversify_module(
                component,
                services,
                bindings
            ))

        # Python (dependency-injector)
        elif 'python' in component.technology_stack:
            modules.append(self._generate_python_di_module(
                component,
                services,
                bindings
            ))

        # Java (Spring)
        elif 'java' in component.technology_stack:
            modules.append(self._generate_spring_config(
                component,
                services,
                bindings
            ))

        # .NET (Microsoft.Extensions.DependencyInjection)
        elif 'csharp' in component.technology_stack:
            modules.append(self._generate_dotnet_di_config(
                component,
                services,
                bindings
            ))

        return modules

    def _generate_inversify_module(
        self,
        component: ComponentDecision,
        services: List[ServiceDefinition],
        bindings: List[Dict[str, Any]]
    ) -> str:
        """InversifyJS 모듈 생성"""

        module_code = f"""
import {{ Container, injectable, inject, ContainerModule }} from 'inversify';
import 'reflect-metadata';

// Service identifiers
export const TYPES = {{
    {chr(10).join(f"{s.service_id}: Symbol.for('{s.service_id}')," for s in services)}
}};

// Module definition
export const {component.name}Module = new ContainerModule((bind) => {{
    // Service bindings
    {self._generate_inversify_bindings(bindings)}

    // Factory bindings
    {self._generate_inversify_factories(services)}
}});

// Container configuration
export function configure{component.name}Container(container: Container): void {{
    container.load({component.name}Module);

    // Middleware configuration
    container.applyMiddleware(
        ...{component.name}Middleware
    );
}}

// Service decorators
{self._generate_service_decorators(services)}
"""

        return module_code

    def _generate_python_di_module(
        self,
        component: ComponentDecision,
        services: List[ServiceDefinition],
        bindings: List[Dict[str, Any]]
    ) -> str:
        """Python dependency-injector 모듈 생성"""

        module_code = f"""
from dependency_injector import containers, providers
from typing import Dict, Any

class {component.name}Container(containers.DeclarativeContainer):
    \"\"\"DI container for {component.name}\"\"\"

    # Configuration
    config = providers.Configuration()

    # Infrastructure
    database = providers.Singleton(
        DatabaseConnection,
        connection_string=config.database.connection_string
    )

    # Repositories
    {self._generate_python_repositories(services)}

    # Services
    {self._generate_python_services(services)}

    # Controllers
    {self._generate_python_controllers(services)}

# Wire decorator
def wire_dependencies(func):
    \"\"\"Decorator to wire dependencies\"\"\"
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        container = {component.name}Container()
        container.wire(modules=[__name__])
        return func(*args, **kwargs)
    return wrapper

# Auto-wiring setup
def setup_autowiring():
    container = {component.name}Container()
    container.config.from_yaml('config.yaml')
    container.wire(modules=[
        '{component.name.lower()}.controllers',
        '{component.name.lower()}.services',
        '{component.name.lower()}.repositories'
    ])
    return container
"""

        return module_code

    def _generate_spring_config(
        self,
        component: ComponentDecision,
        services: List[ServiceDefinition],
        bindings: List[Dict[str, Any]]
    ) -> str:
        """Spring Configuration 생성"""

        config_code = f"""
package com.example.{component.name.lower()}.config;

import org.springframework.context.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;

@Configuration
@ComponentScan(basePackages = "{component.name.lower()}")
public class {component.name}Configuration {{

    // Service beans
    {self._generate_spring_beans(services)}

    // Conditional beans
    {self._generate_spring_conditional_beans(component)}

    // Factory beans
    {self._generate_spring_factories(services)}
}}

// Service annotations
{self._generate_spring_service_annotations(services)}
"""

        return config_code

    async def generate_dependency_graph_visualization(
        self,
        component: ComponentDecision,
        di_config: Dict[str, Any]
    ) -> str:
        """의존성 그래프 시각화"""

        mermaid_code = f"""
graph TD
    subgraph "{component.name} Dependency Graph"
"""

        # 서비스 노드 추가
        for service in di_config['service_definitions']:
            node_style = self._get_node_style(service.scope)
            mermaid_code += f"        {service.service_id}[{service.service_id}]{node_style}\n"

        # 의존성 엣지 추가
        for service in di_config['service_definitions']:
            for dep in service.dependencies:
                mermaid_code += f"        {service.service_id} --> {dep}\n"

        mermaid_code += "    end\n"

        # 범례 추가
        mermaid_code += """

    classDef singleton fill:#f9f,stroke:#333,stroke-width:2px
    classDef transient fill:#bbf,stroke:#333,stroke-width:2px
    classDef scoped fill:#bfb,stroke:#333,stroke-width:2px
"""

        return mermaid_code

    def _get_node_style(self, scope: str) -> str:
        """노드 스타일 결정"""

        styles = {
            'singleton': ':::singleton',
            'transient': ':::transient',
            'scoped': ':::scoped'
        }

        return styles.get(scope, '')
```

**검증 기준**:

- [ ] 다양한 DI 프레임워크 지원
- [ ] 자동 와이어링 설정
- [ ] 생명주기 관리
- [ ] 의존성 그래프 시각화

#### SubTask 4.38.4: 의존성 업데이트 자동화

**담당자**: DevOps 자동화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/dependency_updater.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

@dataclass
class UpdateStrategy:
    strategy_type: str  # conservative, balanced, aggressive
    version_jump: str   # patch, minor, major
    auto_merge: bool
    require_tests: bool
    rollback_on_failure: bool

@dataclass
class UpdateResult:
    package_name: str
    previous_version: str
    new_version: str
    update_type: str  # security, feature, patch
    status: str       # success, failed, skipped
    test_results: Dict[str, Any]
    rollback_performed: bool
    notes: List[str]

class DependencyUpdateAutomation:
    """의존성 업데이트 자동화"""

    def __init__(self):
        self.update_checker = UpdateChecker()
        self.test_runner = TestRunner()
        self.version_bumper = VersionBumper()
        self.pr_creator = PullRequestCreator()
        self.rollback_manager = RollbackManager()

    async def setup_automated_updates(
        self,
        component: ComponentDecision,
        update_strategy: UpdateStrategy
    ) -> Dict[str, Any]:
        """자동 업데이트 설정"""

        automation_config = {
            'schedule': self._determine_update_schedule(update_strategy),
            'github_actions': await self._generate_github_actions(
                component,
                update_strategy
            ),
            'dependabot_config': self._generate_dependabot_config(
                component,
                update_strategy
            ),
            'renovate_config': self._generate_renovate_config(
                component,
                update_strategy
            ),
            'custom_scripts': await self._generate_update_scripts(
                component,
                update_strategy
            )
        }

        return automation_config

    async def _generate_github_actions(
        self,
        component: ComponentDecision,
        strategy: UpdateStrategy
    ) -> str:
        """GitHub Actions 워크플로우 생성"""

        workflow = f"""
name: Automated Dependency Updates
on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Mondays
  workflow_dispatch:

jobs:
  update-dependencies:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
      with:
        token: ${{{{ secrets.GITHUB_TOKEN }}}}

    - name: Setup environment
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Check for updates
      id: check-updates
      run: |
        npm outdated --json > outdated.json || true
        echo "::set-output name=has_updates::$([ -s outdated.json ] && echo 'true' || echo 'false')"

    - name: Update dependencies
      if: steps.check-updates.outputs.has_updates == 'true'
      run: |
        {self._generate_update_commands(component, strategy)}

    - name: Run tests
      if: steps.check-updates.outputs.has_updates == 'true'
      run: |
        npm test
        npm run test:integration
        npm run test:e2e

    - name: Security audit
      run: |
        npm audit --production

    - name: Create Pull Request
      if: steps.check-updates.outputs.has_updates == 'true'
      uses: peter-evans/create-pull-request@v4
      with:
        token: ${{{{ secrets.GITHUB_TOKEN }}}}
        commit-message: 'chore: update dependencies'
        title: '[Auto] Dependency Updates'
        body: |
          ## Automated Dependency Updates

          This PR was automatically created to update dependencies.

          ### Changes
          ${{{{ steps.update-summary.outputs.summary }}}}

          ### Test Results
          - ✅ Unit Tests: Passed
          - ✅ Integration Tests: Passed
          - ✅ Security Audit: No vulnerabilities

        branch: auto-update/dependencies
        delete-branch: true
"""

        return workflow

    def _generate_dependabot_config(
        self,
        component: ComponentDecision,
        strategy: UpdateStrategy
    ) -> str:
        """Dependabot 설정 생성"""

        # 업데이트 빈도 결정
        schedule_interval = {
            'conservative': 'monthly',
            'balanced': 'weekly',
            'aggressive': 'daily'
        }.get(strategy.strategy_type, 'weekly')

        config = f"""
version: 2
updates:
  # Package manager configurations
  {self._generate_package_manager_config(component, schedule_interval)}

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "{schedule_interval}"
    reviewers:
      - "@your-team"
    labels:
      - "dependencies"
      - "docker"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "{schedule_interval}"
    labels:
      - "dependencies"
      - "github-actions"

# Update strategies
registries:
  npm-registry:
    type: npm-registry
    url: https://npm.pkg.github.com
    token: ${{{{ secrets.NPM_TOKEN }}}}
"""

        return config

    def _generate_renovate_config(
        self,
        component: ComponentDecision,
        strategy: UpdateStrategy
    ) -> Dict[str, Any]:
        """Renovate 설정 생성"""

        config = {
            "extends": [
                "config:base",
                f"schedule:{strategy.strategy_type}"
            ],
            "packageRules": [
                {
                    "matchUpdateTypes": ["major"],
                    "enabled": strategy.version_jump == "major",
                    "automerge": False
                },
                {
                    "matchUpdateTypes": ["minor"],
                    "enabled": strategy.version_jump in ["minor", "major"],
                    "automerge": strategy.auto_merge and strategy.version_jump != "patch"
                },
                {
                    "matchUpdateTypes": ["patch"],
                    "enabled": True,
                    "automerge": strategy.auto_merge
                },
                {
                    "matchDepTypes": ["devDependencies"],
                    "automerge": True
                }
            ],
            "vulnerabilityAlerts": {
                "enabled": True,
                "labels": ["security"],
                "automerge": True
            },
            "prConcurrentLimit": 3,
            "prHourlyLimit": 2,
            "semanticCommits": "enabled",
            "commitMessagePrefix": "chore:",
            "commitMessageTopic": "{{depName}}",
            "commitMessageExtra": "from {{currentVersion}} to {{newVersion}}"
        }

        # 컴포넌트별 특수 규칙
        if component.properties.get('critical_dependencies'):
            config["packageRules"].append({
                "matchPackageNames": component.properties['critical_dependencies'],
                "enabled": True,
                "automerge": False,
                "labels": ["critical", "requires-review"],
                "reviewers": ["@tech-lead", "@security-team"]
            })

        return config

    async def _generate_update_scripts(
        self,
        component: ComponentDecision,
        strategy: UpdateStrategy
    ) -> Dict[str, str]:
        """커스텀 업데이트 스크립트 생성"""

        scripts = {}

        # 메인 업데이트 스크립트
        scripts['update.sh'] = f"""#!/bin/bash
set -e

echo "🔄 Starting dependency update for {component.name}"

# Backup current state
cp package.json package.json.backup
cp package-lock.json package-lock.json.backup

# Update dependencies based on strategy
{self._generate_update_logic(strategy)}

# Run tests
echo "🧪 Running tests..."
npm test || {{
    echo "❌ Tests failed, rolling back..."
    mv package.json.backup package.json
    mv package-lock.json.backup package-lock.json
    npm install
    exit 1
}}

# Security audit
echo "🔒 Running security audit..."
npm audit --production || {{
    echo "⚠️  Security vulnerabilities found"
    # Continue based on strategy
    {self._generate_security_handling(strategy)}
}}

# Generate update report
node scripts/generate-update-report.js > update-report.md

echo "✅ Update completed successfully"
"""

        # 업데이트 리포트 생성 스크립트
        scripts['generate-update-report.js'] = """
const fs = require('fs');
const { execSync } = require('child_process');

function generateUpdateReport() {
    const outdated = JSON.parse(
        execSync('npm outdated --json || echo "{}"').toString()
    );

    const report = [`# Dependency Update Report`, ''];
    report.push(`Generated: ${new Date().toISOString()}`);
    report.push('');

    // Updated packages
    report.push('## Updated Packages');
    Object.entries(outdated).forEach(([pkg, info]) => {
        report.push(`- **${pkg}**: ${info.current} → ${info.latest}`);
    });

    // Test results
    report.push('');
    report.push('## Test Results');
    report.push('- ✅ All tests passed');

    // Security audit
    report.push('');
    report.push('## Security Audit');
    const auditResult = execSync('npm audit --json || echo "{}"');
    const audit = JSON.parse(auditResult.toString());
    report.push(`- Vulnerabilities: ${audit.metadata?.vulnerabilities?.total || 0}`);

    return report.join('\\n');
}

console.log(generateUpdateReport());
"""

        # 롤백 스크립트
        scripts['rollback.sh'] = """#!/bin/bash
echo "🔄 Rolling back dependency updates..."

# Restore from backup
if [ -f package.json.backup ]; then
    mv package.json.backup package.json
    mv package-lock.json.backup package-lock.json
    npm install
    echo "✅ Rollback completed"
else
    echo "❌ No backup found"
    exit 1
fi
"""

        return scripts

    async def execute_update(
        self,
        component: ComponentDecision,
        target_packages: Optional[List[str]] = None
    ) -> List[UpdateResult]:
        """업데이트 실행"""

        results = []

        # 1. 업데이트 가능한 패키지 확인
        available_updates = await self.update_checker.check_updates(
            component,
            target_packages
        )

        # 2. 각 패키지 업데이트
        for update in available_updates:
            result = await self._update_single_package(
                component,
                update
            )
            results.append(result)

        # 3. 통합 테스트 실행
        if results and all(r.status == 'success' for r in results):
            integration_test_passed = await self._run_integration_tests(component)

            if not integration_test_passed:
                # 모든 업데이트 롤백
                for result in results:
                    if result.status == 'success':
                        await self._rollback_update(component, result)
                        result.rollback_performed = True

        return results

    async def _update_single_package(
        self,
        component: ComponentDecision,
        update_info: Dict[str, Any]
    ) -> UpdateResult:
        """단일 패키지 업데이트"""

        package_name = update_info['package']
        current_version = update_info['current']
        target_version = update_info['target']

        try:
            # 1. 버전 업데이트
            await self.version_bumper.update_version(
                component,
                package_name,
                target_version
            )

            # 2. 의존성 설치
            install_success = await self._install_dependencies(component)

            if not install_success:
                raise Exception("Failed to install dependencies")

            # 3. 테스트 실행
            test_results = await self.test_runner.run_tests(
                component,
                test_types=['unit', 'integration']
            )

            if not test_results['passed']:
                raise Exception("Tests failed after update")

            return UpdateResult(
                package_name=package_name,
                previous_version=current_version,
                new_version=target_version,
                update_type=update_info['type'],
                status='success',
                test_results=test_results,
                rollback_performed=False,
                notes=[]
            )

        except Exception as e:
            # 롤백
            await self._rollback_update(
                component,
                UpdateResult(
                    package_name=package_name,
                    previous_version=current_version,
                    new_version=target_version,
                    update_type=update_info['type'],
                    status='failed',
                    test_results={},
                    rollback_performed=True,
                    notes=[str(e)]
                )
            )

            return UpdateResult(
                package_name=package_name,
                previous_version=current_version,
                new_version=target_version,
                update_type=update_info['type'],
                status='failed',
                test_results={},
                rollback_performed=True,
                notes=[f"Update failed: {str(e)}"]
            )
```

**검증 기준**:

- [ ] 자동 업데이트 워크플로우
- [ ] 다양한 업데이트 전략
- [ ] 테스트 통합
- [ ] 롤백 메커니즘

### Task 4.39: 컴포넌트 배포 전략

#### SubTask 4.39.1: 배포 전략 생성기

**담당자**: 배포 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/deployment_strategy_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class DeploymentStrategy:
    strategy_type: str  # blue-green, canary, rolling, recreate
    component_id: str
    environments: List[str]
    rollout_config: Dict[str, Any]
    health_checks: List[Dict[str, Any]]
    rollback_triggers: List[Dict[str, Any]]
    monitoring_config: Dict[str, Any]
    scaling_policy: Dict[str, Any]

@dataclass
class DeploymentPlan:
    component_id: str
    strategy: DeploymentStrategy
    infrastructure: Dict[str, Any]
    ci_cd_pipeline: Dict[str, Any]
    deployment_scripts: Dict[str, str]
    configuration_templates: Dict[str, Any]
    security_policies: Dict[str, Any]

class DeploymentStrategyGenerator:
    """배포 전략 생성기"""

    def __init__(self):
        self.infrastructure_analyzer = InfrastructureAnalyzer()
        self.strategy_selector = StrategySelector()
        self.pipeline_builder = PipelineBuilder()
        self.config_generator = ConfigurationGenerator()

    async def generate_deployment_strategy(
        self,
        component: ComponentDecision,
        deployment_requirements: Dict[str, Any]
    ) -> DeploymentPlan:
        """컴포넌트 배포 전략 생성"""

        # 1. 최적 배포 전략 선택
        strategy = await self.strategy_selector.select_strategy(
            component,
            deployment_requirements
        )

        # 2. 인프라 요구사항 분석
        infrastructure = await self.infrastructure_analyzer.analyze_requirements(
            component,
            strategy
        )

        # 3. CI/CD 파이프라인 생성
        pipeline = await self.pipeline_builder.build_pipeline(
            component,
            strategy,
            infrastructure
        )

        # 4. 배포 스크립트 생성
        deployment_scripts = await self._generate_deployment_scripts(
            component,
            strategy,
            infrastructure
        )

        # 5. 설정 템플릿 생성
        config_templates = await self.config_generator.generate_templates(
            component,
            strategy,
            infrastructure
        )

        # 6. 보안 정책 생성
        security_policies = await self._generate_security_policies(
            component,
            infrastructure
        )

        return DeploymentPlan(
            component_id=component.id,
            strategy=strategy,
            infrastructure=infrastructure,
            ci_cd_pipeline=pipeline,
            deployment_scripts=deployment_scripts,
            configuration_templates=config_templates,
            security_policies=security_policies
        )

    async def _generate_deployment_scripts(
        self,
        component: ComponentDecision,
        strategy: DeploymentStrategy,
        infrastructure: Dict[str, Any]
    ) -> Dict[str, str]:
        """배포 스크립트 생성"""

        scripts = {}

        # 플랫폼별 배포 스크립트
        if infrastructure['platform'] == 'kubernetes':
            scripts.update(self._generate_kubernetes_scripts(
                component,
                strategy
            ))
        elif infrastructure['platform'] == 'ecs':
            scripts.update(self._generate_ecs_scripts(
                component,
                strategy
            ))
        elif infrastructure['platform'] == 'lambda':
            scripts.update(self._generate_lambda_scripts(
                component,
                strategy
            ))

        # 공통 스크립트
        scripts['deploy.sh'] = self._generate_main_deploy_script(
            component,
            strategy,
            infrastructure
        )
        scripts['rollback.sh'] = self._generate_rollback_script(
            component,
            strategy
        )
        scripts['health-check.sh'] = self._generate_health_check_script(
            component
        )

        return scripts

    def _generate_kubernetes_scripts(
        self,
        component: ComponentDecision,
        strategy: DeploymentStrategy
    ) -> Dict[str, str]:
        """Kubernetes 배포 스크립트"""

        scripts = {}

        # Deployment YAML
        scripts['deployment.yaml'] = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {component.name.lower()}
  labels:
    app: {component.name.lower()}
    version: v{{{{ VERSION }}}}
spec:
  replicas: {{{{ REPLICAS }}}}
  strategy:
    {self._generate_k8s_strategy(strategy)}
  selector:
    matchLabels:
      app: {component.name.lower()}
  template:
    metadata:
      labels:
        app: {component.name.lower()}
        version: v{{{{ VERSION }}}}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: {component.name.lower()}
        image: {{{{ REGISTRY }}}}/{component.name.lower()}:{{{{ VERSION }}}}
        ports:
        - containerPort: 8080
        env:
        - name: NODE_ENV
          value: "{{{{ ENVIRONMENT }}}}"
        - name: SERVICE_NAME
          value: "{component.name}"
        resources:
          {self._generate_k8s_resources(component)}
        livenessProbe:
          {self._generate_k8s_probe(component, 'liveness')}
        readinessProbe:
          {self._generate_k8s_probe(component, 'readiness')}
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: {component.name.lower()}-config
"""

        # Service YAML
        scripts['service.yaml'] = f"""
apiVersion: v1
kind: Service
metadata:
  name: {component.name.lower()}
  labels:
    app: {component.name.lower()}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: {component.name.lower()}
"""

        # HPA YAML
        if strategy.scaling_policy.get('enabled'):
            scripts['hpa.yaml'] = self._generate_k8s_hpa(
                component,
                strategy.scaling_policy
            )

        # Blue-Green 배포 스크립트
        if strategy.strategy_type == 'blue-green':
            scripts['blue-green-deploy.sh'] = self._generate_blue_green_k8s_script(
                component
            )

        # Canary 배포 스크립트
        elif strategy.strategy_type == 'canary':
            scripts['canary-deploy.sh'] = self._generate_canary_k8s_script(
                component,
                strategy
            )

        return scripts

    def _generate_k8s_strategy(self, strategy: DeploymentStrategy) -> str:
        """Kubernetes 배포 전략 설정"""

        if strategy.strategy_type == 'rolling':
            return f"""
type: RollingUpdate
rollingUpdate:
  maxSurge: {strategy.rollout_config.get('max_surge', '25%')}
  maxUnavailable: {strategy.rollout_config.get('max_unavailable', '25%')}
"""
        elif strategy.strategy_type == 'recreate':
            return "type: Recreate"
        else:
            # Blue-Green이나 Canary는 별도 처리
            return "type: RollingUpdate"

    def _generate_main_deploy_script(
        self,
        component: ComponentDecision,
        strategy: DeploymentStrategy,
        infrastructure: Dict[str, Any]
    ) -> str:
        """메인 배포 스크립트"""

        return f"""#!/bin/bash
set -e

# Deployment script for {component.name}
echo "🚀 Starting deployment of {component.name}"

# Configuration
COMPONENT_NAME="{component.name.lower()}"
ENVIRONMENT="${{1:-staging}}"
VERSION="${{2:-latest}}"
STRATEGY="{strategy.strategy_type}"

# Validate inputs
if [ -z "$VERSION" ]; then
    echo "❌ Error: Version not specified"
    exit 1
fi

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."
{self._generate_pre_deployment_checks(component)}

# Build and push image
echo "🏗️  Building Docker image..."
docker build -t $COMPONENT_NAME:$VERSION .
docker tag $COMPONENT_NAME:$VERSION $REGISTRY/$COMPONENT_NAME:$VERSION
docker push $REGISTRY/$COMPONENT_NAME:$VERSION

# Deploy based on strategy
case $STRATEGY in
    "blue-green")
        echo "🔵🟢 Deploying using Blue-Green strategy..."
        ./blue-green-deploy.sh $ENVIRONMENT $VERSION
        ;;
    "canary")
        echo "🐤 Deploying using Canary strategy..."
        ./canary-deploy.sh $ENVIRONMENT $VERSION
        ;;
    "rolling")
        echo "🔄 Deploying using Rolling update..."
        kubectl set image deployment/$COMPONENT_NAME $COMPONENT_NAME=$REGISTRY/$COMPONENT_NAME:$VERSION
        kubectl rollout status deployment/$COMPONENT_NAME
        ;;
    *)
        echo "❌ Unknown deployment strategy: $STRATEGY"
        exit 1
        ;;
esac

# Post-deployment validation
echo "✅ Running post-deployment validation..."
{self._generate_post_deployment_validation(component)}

echo "🎉 Deployment completed successfully!"
"""

    def _generate_blue_green_k8s_script(self, component: ComponentDecision) -> str:
        """Blue-Green Kubernetes 배포 스크립트"""

        return f"""#!/bin/bash
set -e

COMPONENT_NAME="{component.name.lower()}"
ENVIRONMENT="${{1}}"
VERSION="${{2}}"

echo "🔵 Deploying Blue environment..."

# Deploy to blue environment
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $COMPONENT_NAME-blue
  labels:
    app: $COMPONENT_NAME
    slot: blue
spec:
  replicas: {{{{ REPLICAS }}}}
  selector:
    matchLabels:
      app: $COMPONENT_NAME
      slot: blue
  template:
    metadata:
      labels:
        app: $COMPONENT_NAME
        slot: blue
        version: $VERSION
    spec:
      containers:
      - name: $COMPONENT_NAME
        image: $REGISTRY/$COMPONENT_NAME:$VERSION
        ports:
        - containerPort: 8080
EOF

# Wait for blue deployment to be ready
kubectl rollout status deployment/$COMPONENT_NAME-blue

# Run smoke tests on blue
echo "🧪 Running smoke tests on blue environment..."
./smoke-test.sh blue

# Switch traffic to blue
echo "🔄 Switching traffic to blue..."
kubectl patch service $COMPONENT_NAME -p '{{
  "spec": {{
    "selector": {{
      "app": "'$COMPONENT_NAME'",
      "slot": "blue"
    }}
  }}
}}'

# Wait for traffic switch
sleep 10

# Verify blue is serving traffic
echo "✅ Verifying blue deployment..."
./health-check.sh

# Clean up green deployment
echo "🧹 Cleaning up green deployment..."
kubectl delete deployment $COMPONENT_NAME-green --ignore-not-found=true

# Rename blue to green for next deployment
kubectl patch deployment $COMPONENT_NAME-blue -p '{{
  "metadata": {{
    "name": "'$COMPONENT_NAME-green'"
  }}
}}'

echo "✅ Blue-Green deployment completed!"
"""

    def _generate_canary_k8s_script(
        self,
        component: ComponentDecision,
        strategy: DeploymentStrategy
    ) -> str:
        """Canary Kubernetes 배포 스크립트"""

        canary_steps = strategy.rollout_config.get('canary_steps', [10, 50, 100])

        return f"""#!/bin/bash
set -e

COMPONENT_NAME="{component.name.lower()}"
ENVIRONMENT="${{1}}"
VERSION="${{2}}"
CANARY_STEPS=({' '.join(str(s) for s in canary_steps)})

echo "🐤 Starting Canary deployment..."

# Deploy canary version
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $COMPONENT_NAME-canary
  labels:
    app: $COMPONENT_NAME
    track: canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $COMPONENT_NAME
      track: canary
  template:
    metadata:
      labels:
        app: $COMPONENT_NAME
        track: canary
        version: $VERSION
    spec:
      containers:
      - name: $COMPONENT_NAME
        image: $REGISTRY/$COMPONENT_NAME:$VERSION
        ports:
        - containerPort: 8080
EOF

# Wait for canary to be ready
kubectl rollout status deployment/$COMPONENT_NAME-canary

# Progressive rollout
for PERCENTAGE in "${{CANARY_STEPS[@]}}"; do
    echo "📈 Rolling out to $PERCENTAGE% of traffic..."

    # Update traffic split
    kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: $COMPONENT_NAME
spec:
  hosts:
  - $COMPONENT_NAME
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: $COMPONENT_NAME
        subset: canary
      weight: 100
  - route:
    - destination:
        host: $COMPONENT_NAME
        subset: stable
      weight: $((100 - PERCENTAGE))
    - destination:
        host: $COMPONENT_NAME
        subset: canary
      weight: $PERCENTAGE
EOF

    # Monitor metrics
    echo "📊 Monitoring canary metrics..."
    sleep {strategy.rollout_config.get('step_duration', 300)}

    # Check canary health
    CANARY_HEALTHY=$(./check-canary-health.sh)
    if [ "$CANARY_HEALTHY" != "true" ]; then
        echo "❌ Canary health check failed! Rolling back..."
        ./rollback.sh
        exit 1
    fi
done

# Promote canary to stable
echo "🎯 Promoting canary to stable..."
kubectl set image deployment/$COMPONENT_NAME $COMPONENT_NAME=$REGISTRY/$COMPONENT_NAME:$VERSION
kubectl rollout status deployment/$COMPONENT_NAME

# Clean up canary
kubectl delete deployment $COMPONENT_NAME-canary

echo "✅ Canary deployment completed successfully!"
"""

    async def _generate_security_policies(
        self,
        component: ComponentDecision,
        infrastructure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """보안 정책 생성"""

        policies = {
            'network_policies': [],
            'rbac_policies': [],
            'pod_security_policies': [],
            'secrets_management': {},
            'compliance_checks': []
        }

        # 네트워크 정책
        if infrastructure['platform'] == 'kubernetes':
            policies['network_policies'].append({
                'name': f"{component.name}-network-policy",
                'spec': {
                    'podSelector': {
                        'matchLabels': {
                            'app': component.name.lower()
                        }
                    },
                    'policyTypes': ['Ingress', 'Egress'],
                    'ingress': self._generate_ingress_rules(component),
                    'egress': self._generate_egress_rules(component)
                }
            })

        # RBAC 정책
        policies['rbac_policies'] = self._generate_rbac_policies(component)

        # 시크릿 관리
        policies['secrets_management'] = {
            'provider': infrastructure.get('secrets_provider', 'kubernetes'),
            'encryption': {
                'at_rest': True,
                'in_transit': True
            },
            'rotation_policy': {
                'enabled': True,
                'frequency': '90d'
            }
        }

        return policies
```

**검증 기준**:

- [ ] 다양한 배포 전략 지원
- [ ] 플랫폼별 스크립트 생성
- [ ] 헬스 체크 및 롤백
- [ ] 보안 정책 통합

#### SubTask 4.39.2: CI/CD 파이프라인 생성기

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/cicd_pipeline_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class PipelineStage:
    name: str
    jobs: List[Dict[str, Any]]
    dependencies: List[str]
    conditions: Dict[str, Any]
    environment: str
    timeout: int
    retry_policy: Dict[str, Any]

@dataclass
class CICDPipeline:
    pipeline_type: str  # github_actions, gitlab_ci, jenkins, azure_devops
    component_id: str
    stages: List[PipelineStage]
    triggers: Dict[str, Any]
    variables: Dict[str, Any]
    artifacts: Dict[str, Any]
    notifications: Dict[str, Any]

class CICDPipelineGenerator:
    """CI/CD 파이프라인 생성기"""

    def __init__(self):
        self.stage_builder = StageBuilder()
        self.job_generator = JobGenerator()
        self.security_scanner = SecurityScanner()
        self.quality_gates = QualityGates()

    async def generate_pipeline(
        self,
        component: ComponentDecision,
        deployment_strategy: DeploymentStrategy,
        pipeline_type: str = 'github_actions'
    ) -> CICDPipeline:
        """CI/CD 파이프라인 생성"""

        # 1. 파이프라인 스테이지 정의
        stages = await self._define_pipeline_stages(
            component,
            deployment_strategy
        )

        # 2. 트리거 설정
        triggers = self._define_triggers(component)

        # 3. 환경 변수 및 시크릿
        variables = self._define_variables(component)

        # 4. 아티팩트 설정
        artifacts = self._define_artifacts(component)

        # 5. 알림 설정
        notifications = self._define_notifications(component)

        # 6. 파이프라인 생성
        pipeline = CICDPipeline(
            pipeline_type=pipeline_type,
            component_id=component.id,
            stages=stages,
            triggers=triggers,
            variables=variables,
            artifacts=artifacts,
            notifications=notifications
        )

        # 7. 플랫폼별 구성 파일 생성
        config_file = await self._generate_pipeline_config(
            pipeline,
            pipeline_type
        )

        return pipeline, config_file

    async def _define_pipeline_stages(
        self,
        component: ComponentDecision,
        deployment_strategy: DeploymentStrategy
    ) -> List[PipelineStage]:
        """파이프라인 스테이지 정의"""

        stages = []

        # 1. Build Stage
        build_stage = PipelineStage(
            name='build',
            jobs=[
                {
                    'name': 'compile',
                    'steps': await self._generate_build_steps(component)
                },
                {
                    'name': 'unit-tests',
                    'steps': await self._generate_unit_test_steps(component)
                }
            ],
            dependencies=[],
            conditions={'branches': ['main', 'develop', 'feature/*']},
            environment='build',
            timeout=1800,  # 30 minutes
            retry_policy={'max_attempts': 2}
        )
        stages.append(build_stage)

        # 2. Quality Gate Stage
        quality_stage = PipelineStage(
            name='quality',
            jobs=[
                {
                    'name': 'code-analysis',
                    'steps': await self._generate_code_analysis_steps(component)
                },
                {
                    'name': 'security-scan',
                    'steps': await self._generate_security_scan_steps(component)
                },
                {
                    'name': 'dependency-check',
                    'steps': await self._generate_dependency_check_steps(component)
                }
            ],
            dependencies=['build'],
            conditions={'quality_gate': 'enabled'},
            environment='quality',
            timeout=1200,  # 20 minutes
            retry_policy={'max_attempts': 1}
        )
        stages.append(quality_stage)

        # 3. Integration Test Stage
        integration_stage = PipelineStage(
            name='integration',
            jobs=[
                {
                    'name': 'integration-tests',
                    'steps': await self._generate_integration_test_steps(component)
                },
                {
                    'name': 'contract-tests',
                    'steps': await self._generate_contract_test_steps(component)
                }
            ],
            dependencies=['quality'],
            conditions={'branches': ['main', 'develop']},
            environment='test',
            timeout=2400,  # 40 minutes
            retry_policy={'max_attempts': 2}
        )
        stages.append(integration_stage)

        # 4. Package Stage
        package_stage = PipelineStage(
            name='package',
            jobs=[
                {
                    'name': 'docker-build',
                    'steps': await self._generate_docker_build_steps(component)
                },
                {
                    'name': 'helm-package',
                    'steps': await self._generate_helm_package_steps(component)
                }
            ],
            dependencies=['integration'],
            conditions={'tags': 'v*'},
            environment='package',
            timeout=900,  # 15 minutes
            retry_policy={'max_attempts': 2}
        )
        stages.append(package_stage)

        # 5. Deploy Stages (환경별)
        for env in ['staging', 'production']:
            deploy_stage = await self._create_deploy_stage(
                component,
                deployment_strategy,
                env
            )
            stages.append(deploy_stage)

        return stages

    async def _generate_pipeline_config(
        self,
        pipeline: CICDPipeline,
        pipeline_type: str
    ) -> str:
        """파이프라인 구성 파일 생성"""

        if pipeline_type == 'github_actions':
            return self._generate_github_actions_config(pipeline)
        elif pipeline_type == 'gitlab_ci':
            return self._generate_gitlab_ci_config(pipeline)
        elif pipeline_type == 'jenkins':
            return self._generate_jenkinsfile(pipeline)
        elif pipeline_type == 'azure_devops':
            return self._generate_azure_pipelines_config(pipeline)
        else:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")

    def _generate_github_actions_config(self, pipeline: CICDPipeline) -> str:
        """GitHub Actions 워크플로우 생성"""

        config = f"""
name: CI/CD Pipeline for {pipeline.component_id}

on:
  {self._format_github_triggers(pipeline.triggers)}

env:
  {self._format_github_env_vars(pipeline.variables)}

jobs:
"""

        for stage in pipeline.stages:
            for job in stage.jobs:
                config += f"""
  {job['name']}:
    name: {job['name'].replace('-', ' ').title()}
    runs-on: ubuntu-latest
    {self._format_github_job_conditions(stage.conditions)}
    {self._format_github_dependencies(stage.dependencies, job['name'])}

    steps:
"""
                for step in job['steps']:
                    config += f"""
    - name: {step['name']}
      {self._format_github_step(step)}
"""

                # 아티팩트 업로드
                if stage.name in ['build', 'package']:
                    config += f"""
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: {stage.name}-artifacts
        path: |
          {self._format_artifact_paths(pipeline.artifacts)}
"""

        # 알림 설정
        config += self._generate_github_notifications(pipeline.notifications)

        return config

    def _generate_gitlab_ci_config(self, pipeline: CICDPipeline) -> str:
        """GitLab CI 구성 생성"""

        config = f"""
variables:
  {self._format_gitlab_variables(pipeline.variables)}

stages:
  {self._format_gitlab_stages(pipeline.stages)}

.default_rules:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS'
      when: never
    - if: '$CI_COMMIT_BRANCH'

"""

        for stage in pipeline.stages:
            for job in stage.jobs:
                config += f"""
{job['name']}:
  stage: {stage.name}
  image: {self._get_job_image(job)}
  {self._format_gitlab_rules(stage.conditions)}
  {self._format_gitlab_dependencies(stage.dependencies)}
  script:
"""
                for step in job['steps']:
                    config += f"    - {step.get('run', step.get('script', ''))}\n"

                # 아티팩트 설정
                if stage.name in ['build', 'package']:
                    config += f"""
  artifacts:
    paths:
      {self._format_gitlab_artifacts(pipeline.artifacts)}
    expire_in: 1 week
"""

        return config

    def _generate_jenkinsfile(self, pipeline: CICDPipeline) -> str:
        """Jenkinsfile 생성"""

        jenkinsfile = f"""
pipeline {{
    agent any

    environment {{
        {self._format_jenkins_env(pipeline.variables)}
    }}

    options {{
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 2, unit: 'HOURS')
        timestamps()
    }}

    stages {{
"""

        for stage in pipeline.stages:
            jenkinsfile += f"""
        stage('{stage.name}') {{
            {self._format_jenkins_conditions(stage.conditions)}
            parallel {{
"""
            for job in stage.jobs:
                jenkinsfile += f"""
                '{job['name']}': {{
                    steps {{
                        script {{
"""
                for step in job['steps']:
                    jenkinsfile += f"""
                            sh '''
                                {step.get('run', step.get('script', ''))}
                            '''
"""
                jenkinsfile += """
                        }
                    }
                }}
"""
            jenkinsfile += """
            }
        }
"""

        jenkinsfile += """
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // Send success notification
        }
        failure {
            echo 'Pipeline failed!'
            // Send failure notification
        }
    }
}
"""

        return jenkinsfile

    async def _generate_build_steps(
        self,
        component: ComponentDecision
    ) -> List[Dict[str, Any]]:
        """빌드 스텝 생성"""

        steps = [
            {
                'name': 'Checkout code',
                'uses': 'actions/checkout@v3'
            },
            {
                'name': 'Setup build environment',
                'run': self._get_setup_script(component)
            }
        ]

        # 언어별 빌드 스텝
        if 'nodejs' in component.technology_stack:
            steps.extend([
                {
                    'name': 'Setup Node.js',
                    'uses': 'actions/setup-node@v3',
                    'with': {
                        'node-version': '18',
                        'cache': 'npm'
                    }
                },
                {
                    'name': 'Install dependencies',
                    'run': 'npm ci'
                },
                {
                    'name': 'Build',
                    'run': 'npm run build'
                }
            ])
        elif 'python' in component.technology_stack:
            steps.extend([
                {
                    'name': 'Setup Python',
                    'uses': 'actions/setup-python@v4',
                    'with': {
                        'python-version': '3.11',
                        'cache': 'pip'
                    }
                },
                {
                    'name': 'Install dependencies',
                    'run': 'pip install -r requirements.txt'
                },
                {
                    'name': 'Build',
                    'run': 'python setup.py build'
                }
            ])

        return steps

    async def _generate_security_scan_steps(
        self,
        component: ComponentDecision
    ) -> List[Dict[str, Any]]:
        """보안 스캔 스텝 생성"""

        steps = [
            {
                'name': 'Run SAST scan',
                'uses': 'github/super-linter@v4',
                'env': {
                    'DEFAULT_BRANCH': 'main',
                    'GITHUB_TOKEN': '${{ secrets.GITHUB_TOKEN }}'
                }
            },
            {
                'name': 'Dependency vulnerability scan',
                'run': 'npm audit --production' if 'nodejs' in component.technology_stack else 'pip-audit'
            },
            {
                'name': 'Container scan',
                'uses': 'aquasecurity/trivy-action@master',
                'with': {
                    'scan-type': 'fs',
                    'scan-ref': '.',
                    'format': 'sarif',
                    'output': 'trivy-results.sarif'
                }
            },
            {
                'name': 'Upload scan results',
                'uses': 'github/codeql-action/upload-sarif@v2',
                'with': {
                    'sarif_file': 'trivy-results.sarif'
                }
            }
        ]

        # 시크릿 스캔
        if component.properties.get('handles_secrets'):
            steps.append({
                'name': 'Secret scanning',
                'uses': 'trufflesecurity/trufflehog@main',
                'with': {
                    'path': './',
                    'base': '${{ github.event.repository.default_branch }}',
                    'head': 'HEAD'
                }
            })

        return steps

    async def _create_deploy_stage(
        self,
        component: ComponentDecision,
        deployment_strategy: DeploymentStrategy,
        environment: str
    ) -> PipelineStage:
        """배포 스테이지 생성"""

        jobs = []

        # Pre-deployment 검증
        jobs.append({
            'name': f'pre-deploy-{environment}',
            'steps': [
                {
                    'name': 'Validate deployment config',
                    'run': f'./scripts/validate-deployment.sh {environment}'
                },
                {
                    'name': 'Check environment readiness',
                    'run': f'./scripts/check-environment.sh {environment}'
                }
            ]
        })

        # 배포 작업
        deploy_job = {
            'name': f'deploy-{environment}',
            'steps': await self._generate_deployment_steps(
                component,
                deployment_strategy,
                environment
            )
        }
        jobs.append(deploy_job)

        # Post-deployment 검증
        jobs.append({
            'name': f'verify-{environment}',
            'steps': [
                {
                    'name': 'Run smoke tests',
                    'run': f'./scripts/smoke-tests.sh {environment}'
                },
                {
                    'name': 'Health check',
                    'run': f'./scripts/health-check.sh {environment}'
                },
                {
                    'name': 'Performance baseline',
                    'run': f'./scripts/performance-check.sh {environment}'
                }
            ]
        })

        # 조건 설정
        conditions = {
            'branches': ['main'] if environment == 'production' else ['main', 'develop'],
            'manual_approval': environment == 'production'
        }

        return PipelineStage(
            name=f'deploy-{environment}',
            jobs=jobs,
            dependencies=['package'],
            conditions=conditions,
            environment=environment,
            timeout=3600,  # 60 minutes
            retry_policy={'max_attempts': 1}
        )
```

**검증 기준**:

- [ ] 다양한 CI/CD 플랫폼 지원
- [ ] 품질 게이트 통합
- [ ] 보안 스캔 자동화
- [ ] 환경별 배포 설정

#### SubTask 4.39.3: 환경 설정 관리기

**담당자**: 설정 관리 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/environment_config_manager.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import json

@dataclass
class EnvironmentConfig:
    environment: str  # dev, staging, production
    component_id: str
    config_values: Dict[str, Any]
    secrets: List[str]
    feature_flags: Dict[str, bool]
    resource_limits: Dict[str, Any]
    scaling_config: Dict[str, Any]
    network_config: Dict[str, Any]

@dataclass
class ConfigurationSet:
    component_id: str
    environments: List[EnvironmentConfig]
    shared_config: Dict[str, Any]
    config_templates: Dict[str, str]
    validation_rules: Dict[str, Any]
    encryption_settings: Dict[str, Any]

class EnvironmentConfigManager:
    """환경 설정 관리기"""

    def __init__(self):
        self.config_generator = ConfigGenerator()
        self.secret_manager = SecretManager()
        self.validator = ConfigValidator()
        self.encryptor = ConfigEncryptor()

    async def generate_environment_configs(
        self,
        component: ComponentDecision,
        environments: List[str]
    ) -> ConfigurationSet:
        """환경별 설정 생성"""

        env_configs = []

        # 1. 공통 설정 추출
        shared_config = await self._extract_shared_config(component)

        # 2. 각 환경별 설정 생성
        for env in environments:
            env_config = await self._generate_environment_config(
                component,
                env,
                shared_config
            )
            env_configs.append(env_config)

        # 3. 설정 템플릿 생성
        config_templates = await self._generate_config_templates(
            component,
            env_configs
        )

        # 4. 검증 규칙 생성
        validation_rules = self._generate_validation_rules(component)

        # 5. 암호화 설정
        encryption_settings = await self._setup_encryption(component)

        return ConfigurationSet(
            component_id=component.id,
            environments=env_configs,
            shared_config=shared_config,
            config_templates=config_templates,
            validation_rules=validation_rules,
            encryption_settings=encryption_settings
        )

    async def _generate_environment_config(
        self,
        component: ComponentDecision,
        environment: str,
        shared_config: Dict[str, Any]
    ) -> EnvironmentConfig:
        """환경별 설정 생성"""

        # 기본 설정값
        config_values = {
            'app': {
                'name': component.name,
                'version': component.properties.get('version', '1.0.0'),
                'environment': environment,
                'debug': environment != 'production',
                'log_level': 'DEBUG' if environment == 'dev' else 'INFO'
            },
            'server': {
                'port': self._get_port_for_env(environment),
                'host': '0.0.0.0',
                'workers': self._get_workers_for_env(environment),
                'timeout': 30
            }
        }

        # 데이터베이스 설정
        if component.properties.get('uses_database'):
            config_values['database'] = {
                'host': f'{environment}-db.internal',
                'port': 5432,
                'name': f'{component.name}_{environment}',
                'pool_size': self._get_db_pool_size(environment),
                'ssl': environment == 'production'
            }

        # 캐시 설정
        if component.properties.get('uses_cache'):
            config_values['cache'] = {
                'provider': 'redis',
                'host': f'{environment}-redis.internal',
                'port': 6379,
                'ttl': 300,
                'max_memory': self._get_cache_memory(environment)
            }

        # API 설정
        if component.type == ComponentType.API_ENDPOINT:
            config_values['api'] = {
                'base_url': self._get_api_url(component, environment),
                'version': 'v1',
                'rate_limit': self._get_rate_limit(environment),
                'cors': {
                    'enabled': True,
                    'origins': self._get_cors_origins(environment)
                }
            }

        # 시크릿 참조
        secrets = await self._identify_secrets(component, environment)

        # Feature flags
        feature_flags = self._generate_feature_flags(component, environment)

        # 리소스 제한
        resource_limits = self._calculate_resource_limits(component, environment)

        # 스케일링 설정
        scaling_config = self._generate_scaling_config(component, environment)

        # 네트워크 설정
        network_config = self._generate_network_config(component, environment)

        return EnvironmentConfig(
            environment=environment,
            component_id=component.id,
            config_values=config_values,
            secrets=secrets,
            feature_flags=feature_flags,
            resource_limits=resource_limits,
            scaling_config=scaling_config,
            network_config=network_config
        )

    async def _generate_config_templates(
        self,
        component: ComponentDecision,
        env_configs: List[EnvironmentConfig]
    ) -> Dict[str, str]:
        """설정 템플릿 생성"""

        templates = {}

        # Kubernetes ConfigMap
        templates['k8s_configmap'] = self._generate_k8s_configmap(
            component,
            env_configs[0]  # 템플릿용으로 첫 번째 환경 사용
        )

        # Helm values.yaml
        templates['helm_values'] = self._generate_helm_values(
            component,
            env_configs
        )

        # Docker Compose
        templates['docker_compose'] = self._generate_docker_compose(
            component,
            env_configs[0]
        )

        # .env 파일
        templates['env_file'] = self._generate_env_file(
            component,
            env_configs[0]
        )

        # Terraform variables
        if component.properties.get('infrastructure_as_code'):
            templates['terraform_vars'] = self._generate_terraform_vars(
                component,
                env_configs
            )

        return templates

    def _generate_k8s_configmap(
        self,
        component: ComponentDecision,
        env_config: EnvironmentConfig
    ) -> str:
        """Kubernetes ConfigMap 생성"""

        return f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {component.name.lower()}-config
  namespace: {{{{ .Values.namespace }}}}
data:
  config.yaml: |
    {yaml.dump(env_config.config_values, indent=4)}

  application.properties: |
    # Application Properties
    app.name={component.name}
    app.environment={{{{ .Values.environment }}}}
    app.version={{{{ .Values.image.tag }}}}

    # Server Configuration
    server.port={env_config.config_values['server']['port']}
    server.compression.enabled=true

    # Database Configuration
    spring.datasource.url=jdbc:postgresql://{{{{ .Values.database.host }}}}:{{{{ .Values.database.port }}}}/{{{{ .Values.database.name }}}}
    spring.datasource.username={{{{ .Values.database.username }}}}
    spring.jpa.hibernate.ddl-auto=validate

    # Logging
    logging.level.root={{{{ .Values.logging.level }}}}
    logging.pattern.console=%d{{yyyy-MM-dd HH:mm:ss}} - %msg%n
"""

    def _generate_helm_values(
        self,
        component: ComponentDecision,
        env_configs: List[EnvironmentConfig]
    ) -> str:
        """Helm values.yaml 생성"""

        # 기본값 (dev 환경 기준)
        dev_config = next(c for c in env_configs if c.environment == 'dev')

        values = {
            'replicaCount': 1,
            'image': {
                'repository': f"{component.name.lower()}",
                'pullPolicy': 'IfNotPresent',
                'tag': 'latest'
            },
            'service': {
                'type': 'ClusterIP',
                'port': 80,
                'targetPort': dev_config.config_values['server']['port']
            },
            'resources': dev_config.resource_limits,
            'autoscaling': dev_config.scaling_config,
            'config': dev_config.config_values,
            'secrets': {
                'create': True,
                'items': dev_config.secrets
            }
        }

        # 환경별 오버라이드
        values['environments'] = {}
        for env_config in env_configs:
            values['environments'][env_config.environment] = {
                'replicaCount': env_config.scaling_config.get('min_replicas', 1),
                'resources': env_config.resource_limits,
                'config': env_config.config_values
            }

        return yaml.dump(values, default_flow_style=False)

    def _calculate_resource_limits(
        self,
        component: ComponentDecision,
        environment: str
    ) -> Dict[str, Any]:
        """리소스 제한 계산"""

        # 기본값
        base_cpu = 100  # millicores
        base_memory = 128  # MB

        # 컴포넌트 복잡도에 따른 조정
        complexity_multiplier = 1 + (component.complexity_score / 10)

        # 환경별 조정
        env_multipliers = {
            'dev': 1.0,
            'staging': 1.5,
            'production': 2.0
        }
        env_multiplier = env_multipliers.get(environment, 1.0)

        # 컴포넌트 타입별 조정
        type_multipliers = {
            ComponentType.API_ENDPOINT: 1.5,
            ComponentType.BACKEND_SERVICE: 2.0,
            ComponentType.DATA_MODEL: 1.0,
            ComponentType.UI_COMPONENT: 1.2
        }
        type_multiplier = type_multipliers.get(component.type, 1.0)

        # 최종 계산
        final_multiplier = complexity_multiplier * env_multiplier * type_multiplier

        return {
            'limits': {
                'cpu': f"{int(base_cpu * final_multiplier * 4)}m",
                'memory': f"{int(base_memory * final_multiplier * 4)}Mi"
            },
            'requests': {
                'cpu': f"{int(base_cpu * final_multiplier)}m",
                'memory': f"{int(base_memory * final_multiplier)}Mi"
            }
        }

    def _generate_scaling_config(
        self,
        component: ComponentDecision,
        environment: str
    ) -> Dict[str, Any]:
        """스케일링 설정 생성"""

        # 환경별 기본값
        env_configs = {
            'dev': {
                'enabled': False,
                'min_replicas': 1,
                'max_replicas': 2
            },
            'staging': {
                'enabled': True,
                'min_replicas': 2,
                'max_replicas': 4
            },
            'production': {
                'enabled': True,
                'min_replicas': 3,
                'max_replicas': 10
            }
        }

        config = env_configs.get(environment, env_configs['dev'])

        # HPA 설정
        if config['enabled']:
            config['metrics'] = [
                {
                    'type': 'cpu',
                    'target_utilization': 70
                },
                {
                    'type': 'memory',
                    'target_utilization': 80
                }
            ]

            # 커스텀 메트릭
            if component.properties.get('custom_metrics'):
                config['metrics'].append({
                    'type': 'custom',
                    'metric': 'requests_per_second',
                    'target_value': 1000
                })

        return config

    async def export_configs(
        self,
        config_set: ConfigurationSet,
        format: str = 'yaml'
    ) -> Dict[str, str]:
        """설정 내보내기"""

        exported = {}

        for env_config in config_set.environments:
            env_name = env_config.environment

            # YAML 형식
            if format == 'yaml':
                exported[f'config.{env_name}.yaml'] = yaml.dump(
                    env_config.config_values,
                    default_flow_style=False
                )

            # JSON 형식
            elif format == 'json':
                exported[f'config.{env_name}.json'] = json.dumps(
                    env_config.config_values,
                    indent=2
                )

            # Properties 형식
            elif format == 'properties':
                exported[f'application-{env_name}.properties'] = self._to_properties(
                    env_config.config_values
                )

        # 템플릿 내보내기
        for template_name, template_content in config_set.config_templates.items():
            exported[f'templates/{template_name}'] = template_content

        return exported

    def _to_properties(self, config: Dict[str, Any], prefix: str = '') -> str:
        """딕셔너리를 properties 형식으로 변환"""

        lines = []

        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                lines.append(self._to_properties(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    lines.append(f"{full_key}[{i}]={item}")
            else:
                lines.append(f"{full_key}={value}")

        return '\n'.join(lines)
```

**검증 기준**:

- [ ] 환경별 설정 분리
- [ ] 시크릿 관리 통합
- [ ] 다양한 설정 포맷 지원
- [ ] 설정 검증 및 암호화

#### SubTask 4.39.4: 모니터링 설정 생성기

**담당자**: 모니터링 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/monitoring_config_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class MonitoringMetric:
    name: str
    type: str  # counter, gauge, histogram, summary
    description: str
    labels: List[str]
    unit: str
    aggregation: str  # sum, avg, max, min, p50, p95, p99

@dataclass
class Alert:
    name: str
    condition: str
    threshold: float
    duration: str
    severity: str  # critical, warning, info
    annotations: Dict[str, str]
    actions: List[str]

@dataclass
class Dashboard:
    name: str
    title: str
    panels: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    refresh_interval: str
    time_range: str

@dataclass
class MonitoringConfiguration:
    component_id: str
    metrics: List[MonitoringMetric]
    alerts: List[Alert]
    dashboards: List[Dashboard]
    log_config: Dict[str, Any]
    trace_config: Dict[str, Any]
    health_checks: List[Dict[str, Any]]
    slo_definitions: List[Dict[str, Any]]

class MonitoringConfigGenerator:
    """모니터링 설정 생성기"""

    def __init__(self):
        self.metric_generator = MetricGenerator()
        self.alert_builder = AlertBuilder()
        self.dashboard_creator = DashboardCreator()
        self.slo_calculator = SLOCalculator()

    async def generate_monitoring_config(
        self,
        component: ComponentDecision,
        deployment_strategy: DeploymentStrategy
    ) -> MonitoringConfiguration:
        """모니터링 설정 생성"""

        # 1. 메트릭 정의
        metrics = await self._define_metrics(component)

        # 2. 알림 규칙 생성
        alerts = await self._create_alerts(component, metrics)

        # 3. 대시보드 생성
        dashboards = await self._create_dashboards(component, metrics)

        # 4. 로그 설정
        log_config = self._configure_logging(component)

        # 5. 트레이싱 설정
        trace_config = self._configure_tracing(component)

        # 6. 헬스 체크 정의
        health_checks = self._define_health_checks(component)

        # 7. SLO 정의
        slo_definitions = await self._define_slos(component)

        return MonitoringConfiguration(
            component_id=component.id,
            metrics=metrics,
            alerts=alerts,
            dashboards=dashboards,
            log_config=log_config,
            trace_config=trace_config,
            health_checks=health_checks,
            slo_definitions=slo_definitions
        )

    async def _define_metrics(
        self,
        component: ComponentDecision
    ) -> List[MonitoringMetric]:
        """메트릭 정의"""

        metrics = []

        # 기본 시스템 메트릭
        metrics.extend([
            MonitoringMetric(
                name=f"{component.name}_cpu_usage",
                type='gauge',
                description='CPU usage percentage',
                labels=['instance', 'pod'],
                unit='percent',
                aggregation='avg'
            ),
            MonitoringMetric(
                name=f"{component.name}_memory_usage",
                type='gauge',
                description='Memory usage in bytes',
                labels=['instance', 'pod'],
                unit='bytes',
                aggregation='avg'
            ),
            MonitoringMetric(
                name=f"{component.name}_disk_usage",
                type='gauge',
                description='Disk usage in bytes',
                labels=['instance', 'pod', 'mount_point'],
                unit='bytes',
                aggregation='avg'
            )
        ])

        # API 메트릭
        if component.type == ComponentType.API_ENDPOINT:
            metrics.extend([
                MonitoringMetric(
                    name=f"{component.name}_http_requests_total",
                    type='counter',
                    description='Total HTTP requests',
                    labels=['method', 'endpoint', 'status_code'],
                    unit='requests',
                    aggregation='sum'
                ),
                MonitoringMetric(
                    name=f"{component.name}_http_request_duration",
                    type='histogram',
                    description='HTTP request duration',
                    labels=['method', 'endpoint'],
                    unit='seconds',
                    aggregation='p95'
                ),
                MonitoringMetric(
                    name=f"{component.name}_active_connections",
                    type='gauge',
                    description='Number of active connections',
                    labels=['instance'],
                    unit='connections',
                    aggregation='sum'
                )
            ])

        # 데이터베이스 메트릭
        if component.properties.get('uses_database'):
            metrics.extend([
                MonitoringMetric(
                    name=f"{component.name}_db_connections",
                    type='gauge',
                    description='Database connection pool status',
                    labels=['pool_name', 'state'],
                    unit='connections',
                    aggregation='sum'
                ),
                MonitoringMetric(
                    name=f"{component.name}_db_query_duration",
                    type='histogram',
                    description='Database query duration',
                    labels=['query_type', 'table'],
                    unit='seconds',
                    aggregation='p95'
                )
            ])

        # 비즈니스 메트릭
        business_metrics = await self._generate_business_metrics(component)
        metrics.extend(business_metrics)

        return metrics

    async def _create_alerts(
        self,
        component: ComponentDecision,
        metrics: List[MonitoringMetric]
    ) -> List[Alert]:
        """알림 규칙 생성"""

        alerts = []

        # 기본 시스템 알림
        alerts.extend([
            Alert(
                name=f"{component.name}_high_cpu",
                condition=f"{component.name}_cpu_usage > 80",
                threshold=80,
                duration='5m',
                severity='warning',
                annotations={
                    'summary': f'High CPU usage on {component.name}',
                    'description': 'CPU usage has been above 80% for 5 minutes'
                },
                actions=['notify_slack', 'create_incident']
            ),
            Alert(
                name=f"{component.name}_high_memory",
                condition=f"{component.name}_memory_usage > 90",
                threshold=90,
                duration='5m',
                severity='critical',
                annotations={
                    'summary': f'High memory usage on {component.name}',
                    'description': 'Memory usage has been above 90% for 5 minutes'
                },
                actions=['notify_pagerduty', 'scale_up']
            )
        ])

        # API 관련 알림
        if component.type == ComponentType.API_ENDPOINT:
            alerts.extend([
                Alert(
                    name=f"{component.name}_high_error_rate",
                    condition='rate({component.name}_http_requests_total{status_code=~"5.."}[5m]) > 0.05',
                    threshold=0.05,
                    duration='2m',
                    severity='critical',
                    annotations={
                        'summary': 'High error rate detected',
                        'description': 'Error rate is above 5% for 2 minutes'
                    },
                    actions=['notify_oncall', 'create_incident']
                ),
                Alert(
                    name=f"{component.name}_high_latency",
                    condition=f'histogram_quantile(0.95, {component.name}_http_request_duration) > 1',
                    threshold=1.0,
                    duration='5m',
                    severity='warning',
                    annotations={
                        'summary': 'High API latency detected',
                        'description': 'P95 latency is above 1 second'
                    },
                    actions=['notify_slack', 'check_dependencies']
                )
            ])

        # SLO 기반 알림
        slo_alerts = await self._generate_slo_alerts(component)
        alerts.extend(slo_alerts)

        return alerts

    async def _create_dashboards(
        self,
        component: ComponentDecision,
        metrics: List[MonitoringMetric]
    ) -> List[Dashboard]:
        """대시보드 생성"""

        dashboards = []

        # 메인 대시보드
        main_dashboard = Dashboard(
            name=f"{component.name}_overview",
            title=f"{component.name} Overview Dashboard",
            panels=[
                # 시스템 메트릭 패널
                {
                    'title': 'CPU Usage',
                    'type': 'graph',
                    'gridPos': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
                    'targets': [{
                        'expr': f'avg({component.name}_cpu_usage) by (instance)',
                        'legendFormat': '{{instance}}'
                    }]
                },
                {
                    'title': 'Memory Usage',
                    'type': 'graph',
                    'gridPos': {'x': 12, 'y': 0, 'w': 12, 'h': 8},
                    'targets': [{
                        'expr': f'avg({component.name}_memory_usage) by (instance)',
                        'legendFormat': '{{instance}}'
                    }]
                },
                # 요청 메트릭 패널
                {
                    'title': 'Request Rate',
                    'type': 'graph',
                    'gridPos': {'x': 0, 'y': 8, 'w': 12, 'h': 8},
                    'targets': [{
                        'expr': f'sum(rate({component.name}_http_requests_total[5m])) by (method)',
                        'legendFormat': '{{method}}'
                    }]
                },
                {
                    'title': 'Error Rate',
                    'type': 'graph',
                    'gridPos': {'x': 12, 'y': 8, 'w': 12, 'h': 8},
                    'targets': [{
                        'expr': f'sum(rate({component.name}_http_requests_total{{status_code=~"5.."}}[5m]))',
                        'legendFormat': 'Errors'
                    }]
                }
            ],
            variables=[
                {
                    'name': 'environment',
                    'type': 'query',
                    'query': 'label_values(environment)',
                    'current': 'production'
                },
                {
                    'name': 'instance',
                    'type': 'query',
                    'query': f'label_values({component.name}_cpu_usage, instance)',
                    'multi': True
                }
            ],
            refresh_interval='30s',
            time_range='6h'
        )
        dashboards.append(main_dashboard)

        # SLO 대시보드
        if component.properties.get('slo_enabled'):
            slo_dashboard = await self._create_slo_dashboard(component)
            dashboards.append(slo_dashboard)

        return dashboards

    def _configure_logging(self, component: ComponentDecision) -> Dict[str, Any]:
        """로깅 설정"""

        return {
            'level': 'INFO',
            'format': 'json',
            'fields': {
                'timestamp': True,
                'level': True,
                'message': True,
                'component': component.name,
                'trace_id': True,
                'span_id': True,
                'user_id': True,
                'request_id': True
            },
            'outputs': [
                {
                    'type': 'stdout',
                    'format': 'json'
                },
                {
                    'type': 'file',
                    'path': f'/var/log/{component.name}/app.log',
                    'rotation': {
                        'max_size': '100MB',
                        'max_files': 10
                    }
                }
            ],
            'filters': [
                {
                    'type': 'sensitive_data',
                    'patterns': ['password', 'token', 'api_key']
                }
            ]
        }

    def _configure_tracing(self, component: ComponentDecision) -> Dict[str, Any]:
        """트레이싱 설정"""

        return {
            'enabled': True,
            'provider': 'opentelemetry',
            'exporter': {
                'type': 'jaeger',
                'endpoint': 'http://jaeger-collector:14268/api/traces',
                'service_name': component.name
            },
            'sampling': {
                'strategy': 'adaptive',
                'initial_rate': 0.1,
                'max_rate': 1.0,
                'target_latency': 1000  # ms
            },
            'propagators': ['tracecontext', 'baggage'],
            'instrumentation': {
                'http': True,
                'database': True,
                'redis': True,
                'custom_spans': True
            }
        }

    async def _define_slos(self, component: ComponentDecision) -> List[Dict[str, Any]]:
        """SLO (Service Level Objectives) 정의"""

        slos = []

        if component.type == ComponentType.API_ENDPOINT:
            # 가용성 SLO
            slos.append({
                'name': f"{component.name}_availability",
                'description': 'API availability',
                'target': 99.9,  # 99.9%
                'window': '30d',
                'indicator': {
                    'type': 'ratio',
                    'good': f'sum(rate({component.name}_http_requests_total{{status_code!~"5.."}}[5m]))',
                    'total': f'sum(rate({component.name}_http_requests_total[5m]))'
                }
            })

            # 레이턴시 SLO
            slos.append({
                'name': f"{component.name}_latency",
                'description': 'API latency',
                'target': 95,  # 95% of requests under 200ms
                'window': '7d',
                'indicator': {
                    'type': 'histogram',
                    'metric': f'{component.name}_http_request_duration',
                    'threshold': 0.2  # 200ms
                }
            })

        return slos

    async def export_monitoring_configs(
        self,
        config: MonitoringConfiguration
    ) -> Dict[str, str]:
        """모니터링 설정 내보내기"""

        exports = {}

        # Prometheus 규칙
        exports['prometheus-rules.yaml'] = self._export_prometheus_rules(config)

        # Grafana 대시보드
        for dashboard in config.dashboards:
            exports[f'dashboards/{dashboard.name}.json'] = self._export_grafana_dashboard(dashboard)

        # AlertManager 설정
        exports['alertmanager-config.yaml'] = self._export_alertmanager_config(config)

        # OpenTelemetry 설정
        exports['otel-config.yaml'] = self._export_otel_config(config)

        return exports

    def _export_prometheus_rules(self, config: MonitoringConfiguration) -> str:
        """Prometheus 규칙 내보내기"""

        rules = {
            'groups': [
                {
                    'name': f"{config.component_id}_alerts",
                    'interval': '30s',
                    'rules': []
                }
            ]
        }

        for alert in config.alerts:
            rule = {
                'alert': alert.name,
                'expr': alert.condition,
                'for': alert.duration,
                'labels': {
                    'severity': alert.severity,
                    'component': config.component_id
                },
                'annotations': alert.annotations
            }
            rules['groups'][0]['rules'].append(rule)

        return yaml.dump(rules, default_flow_style=False)
```

**검증 기준**:

- [ ] 포괄적인 메트릭 정의
- [ ] SLO 기반 모니터링
- [ ] 다양한 모니터링 도구 지원
- [ ] 자동 알림 규칙 생성

### Task 4.40: 컴포넌트 레포트 및 분석

#### SubTask 4.40.1: 컴포넌트 분석 레포트 생성기

**담당자**: 기술 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/report_generator.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

@dataclass
class ComponentAnalysisReport:
    component_id: str
    executive_summary: str
    detailed_analysis: Dict[str, Any]
    metrics_summary: Dict[str, float]
    risk_assessment: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    generated_at: datetime

class ComponentReportGenerator:
    """컴포넌트 분석 레포트 생성기"""

    def __init__(self):
        self.analyzer = ComponentAnalyzer()
        self.visualizer = DataVisualizer()
        self.report_formatter = ReportFormatter()

    async def generate_analysis_report(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> ComponentAnalysisReport:
        """컴포넌트 분석 레포트 생성"""

        # 1. 요약 생성
        executive_summary = await self._generate_executive_summary(
            component,
            analysis_results
        )

        # 2. 상세 분석
        detailed_analysis = await self._perform_detailed_analysis(
            component,
            analysis_results
        )

        # 3. 메트릭 요약
        metrics_summary = self._summarize_metrics(analysis_results)

        # 4. 위험 평가
        risk_assessment = await self._assess_risks(
            component,
            analysis_results
        )

        # 5. 권고사항 생성
        recommendations = await self._generate_recommendations(
            component,
            detailed_analysis,
            risk_assessment
        )

        # 6. 시각화 생성
        visualizations = await self._create_visualizations(
            component,
            analysis_results
        )

        return ComponentAnalysisReport(
            component_id=component.id,
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            metrics_summary=metrics_summary,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            visualizations=visualizations,
            generated_at=datetime.utcnow()
        )

    async def _generate_executive_summary(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> str:
        """경영진 요약 생성"""

        template = Template("""
# Executive Summary - {{ component.name }}

## Overview
{{ component.description }}

## Key Findings
- **Component Type**: {{ component.type.value }}
- **Complexity Score**: {{ component.complexity_score }}/10
- **Quality Score**: {{ quality_score }}/100
- **Risk Level**: {{ risk_level }}
- **Estimated Effort**: {{ component.estimated_effort }} story points

## Critical Issues
{% for issue in critical_issues %}
- {{ issue.description }} (Impact: {{ issue.impact }})
{% endfor %}

## Top Recommendations
{% for rec in top_recommendations[:3] %}
{{ loop.index }}. {{ rec.title }}
   - **Priority**: {{ rec.priority }}
   - **Expected Benefit**: {{ rec.benefit }}
{% endfor %}

## Implementation Timeline
- **Development**: {{ timeline.development }} weeks
- **Testing**: {{ timeline.testing }} weeks
- **Deployment**: {{ timeline.deployment }} weeks
- **Total**: {{ timeline.total }} weeks
""")

        return template.render(
            component=component,
            quality_score=analysis_results.get('quality_score', 0),
            risk_level=self._determine_risk_level(analysis_results),
            critical_issues=self._extract_critical_issues(analysis_results),
            top_recommendations=analysis_results.get('recommendations', []),
            timeline=self._calculate_timeline(component)
        )

    async def _create_visualizations(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """시각화 생성"""

        visualizations = []

        # 1. 컴포넌트 복잡도 레이더 차트
        complexity_chart = await self._create_complexity_radar_chart(
            component,
            analysis_results
        )
        visualizations.append(complexity_chart)

        # 2. 의존성 그래프
        dependency_graph = await self._create_dependency_graph(
            component,
            analysis_results
        )
        visualizations.append(dependency_graph)

        # 3. 품질 메트릭 히트맵
        quality_heatmap = await self._create_quality_heatmap(
            component,
            analysis_results
        )
        visualizations.append(quality_heatmap)

        # 4. 리스크 매트릭스
        risk_matrix = await self._create_risk_matrix(
            component,
            analysis_results
        )
        visualizations.append(risk_matrix)

        # 5. 구현 타임라인
        timeline_chart = await self._create_timeline_chart(
            component
        )
        visualizations.append(timeline_chart)

        return visualizations

    async def _create_complexity_radar_chart(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """복잡도 레이더 차트 생성"""

        categories = [
            'Cyclomatic',
            'Cognitive',
            'Structural',
            'Data',
            'Interface',
            'Integration'
        ]

        values = [
            analysis_results.get('cyclomatic_complexity', 0) / 10,
            analysis_results.get('cognitive_complexity', 0) / 20,
            analysis_results.get('structural_complexity', 0),
            analysis_results.get('data_complexity', 0),
            analysis_results.get('interface_complexity', 0),
            len(component.dependencies) / 10
        ]

        # 차트 생성
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]

        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_ylim(0, 1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(f'{component.name} Complexity Analysis', size=20, y=1.1)

        # 이미지로 저장
        plt.savefig(f'/tmp/{component.id}_complexity.png', bbox_inches='tight')
        plt.close()

        return {
            'type': 'radar_chart',
            'title': 'Component Complexity Analysis',
            'path': f'/tmp/{component.id}_complexity.png',
            'description': 'Multi-dimensional complexity analysis'
        }

    async def export_report(
        self,
        report: ComponentAnalysisReport,
        format: str = 'html'
    ) -> str:
        """레포트 내보내기"""

        if format == 'html':
            return self._export_html_report(report)
        elif format == 'pdf':
            return await self._export_pdf_report(report)
        elif format == 'markdown':
            return self._export_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_html_report(self, report: ComponentAnalysisReport) -> str:
        """HTML 레포트 생성"""

        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Component Analysis Report - {{ report.component_id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1, h2, h3 { color: #333; }
        .metric { display: inline-block; margin: 10px; padding: 15px;
                  background: #f0f0f0; border-radius: 5px; }
        .risk-high { color: #d9534f; }
        .risk-medium { color: #f0ad4e; }
        .risk-low { color: #5cb85c; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .visualization { margin: 20px 0; text-align: center; }
        .recommendation { background: #e8f4f8; padding: 15px;
                         margin: 10px 0; border-left: 4px solid #337ab7; }
    </style>
</head>
<body>
    <h1>Component Analysis Report</h1>
    <p><strong>Generated:</strong> {{ report.generated_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>

    <div class="executive-summary">
        {{ report.executive_summary | safe }}
    </div>

    <h2>Key Metrics</h2>
    <div class="metrics">
        {% for metric, value in report.metrics_summary.items() %}
        <div class="metric">
            <strong>{{ metric.replace('_', ' ').title() }}:</strong> {{ "%.2f"|format(value) }}
        </div>
        {% endfor %}
    </div>

    <h2>Risk Assessment</h2>
    <table>
        <tr>
            <th>Risk Category</th>
            <th>Level</th>
            <th>Description</th>
            <th>Mitigation</th>
        </tr>
        {% for risk in report.risk_assessment.risks %}
        <tr>
            <td>{{ risk.category }}</td>
            <td class="risk-{{ risk.level }}">{{ risk.level.upper() }}</td>
            <td>{{ risk.description }}</td>
            <td>{{ risk.mitigation }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Recommendations</h2>
    {% for rec in report.recommendations %}
    <div class="recommendation">
        <h3>{{ rec.title }}</h3>
        <p>{{ rec.description }}</p>
        <p><strong>Priority:</strong> {{ rec.priority }} |
           <strong>Effort:</strong> {{ rec.effort }} |
           <strong>Impact:</strong> {{ rec.impact }}</p>
    </div>
    {% endfor %}

    <h2>Visualizations</h2>
    {% for viz in report.visualizations %}
    <div class="visualization">
        <h3>{{ viz.title }}</h3>
        <img src="{{ viz.path }}" alt="{{ viz.title }}" style="max-width: 100%;">
        <p>{{ viz.description }}</p>
    </div>
    {% endfor %}
</body>
</html>
""")

        return template.render(report=report)
```

**검증 기준**:

- [ ] 종합적인 분석 레포트
- [ ] 시각화 자료 포함
- [ ] 실행 가능한 권고사항
- [ ] 다양한 출력 포맷

이렇게 Component Decision Agent의 모든 Task (4.31-4.40)가 완성되었습니다.

주요 구현 내용:

1. **컴포넌트 결정 시스템**: 요구사항 기반 컴포넌트 아키텍처 설계
2. **분석 시스템**: 완전성, 일관성, 호환성, 품질 검증
3. **최적화 시스템**: 재사용성, 성능, 보안 최적화
4. **패턴 라이브러리**: UI, 백엔드, 데이터, 통합 패턴
5. **검증 시스템**: 품질 게이트 및 자동 검증
6. **문서화 시스템**: 자동 문서 및 다이어그램 생성
7. **테스트 생성**: 단위, 통합, E2E 테스트 자동 생성
8. **의존성 관리**: 분석, 버전 관리, DI, 자동 업데이트
9. **배포 전략**: CI/CD, 환경 설정, 모니터링
10. **분석 레포트**: 종합 분석 및 시각화

아니요! Task 4.40에는 4개의 SubTask가 있습니다. 지금까지 4.40.1만 작성했고, 나머지 3개를 계속 작성하겠습니다.

#### SubTask 4.40.2: 아키텍처 영향도 분석기

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/architecture_impact_analyzer.py
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import networkx as nx

@dataclass
class ArchitectureImpact:
    impact_type: str  # structural, behavioral, quality_attribute
    severity: str  # low, medium, high, critical
    affected_components: List[str]
    affected_layers: List[str]
    affected_patterns: List[str]
    propagation_path: List[str]
    mitigation_required: bool
    estimated_rework: int  # hours

@dataclass
class ArchitectureImpactReport:
    component_id: str
    total_impact_score: float
    impacts: List[ArchitectureImpact]
    affected_quality_attributes: Dict[str, float]
    architectural_debt_increase: float
    refactoring_suggestions: List[Dict[str, Any]]
    risk_matrix: Dict[str, Any]

class ArchitectureImpactAnalyzer:
    """아키텍처 영향도 분석기"""

    def __init__(self):
        self.graph_analyzer = ArchitectureGraphAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.quality_assessor = QualityAttributeAssessor()
        self.debt_calculator = TechnicalDebtCalculator()

    async def analyze_architecture_impact(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture,
        change_type: str = 'addition'
    ) -> ArchitectureImpactReport:
        """아키텍처 영향도 분석"""

        # 1. 아키텍처 그래프 구축
        arch_graph = await self.graph_analyzer.build_architecture_graph(
            architecture
        )

        # 2. 구조적 영향 분석
        structural_impacts = await self._analyze_structural_impact(
            component,
            arch_graph,
            change_type
        )

        # 3. 행동적 영향 분석
        behavioral_impacts = await self._analyze_behavioral_impact(
            component,
            architecture,
            change_type
        )

        # 4. 품질 속성 영향 분석
        quality_impacts = await self._analyze_quality_impact(
            component,
            architecture
        )

        # 5. 패턴 영향 분석
        pattern_impacts = await self._analyze_pattern_impact(
            component,
            architecture
        )

        # 6. 전체 영향도 점수 계산
        total_impact_score = self._calculate_total_impact_score(
            structural_impacts + behavioral_impacts + quality_impacts + pattern_impacts
        )

        # 7. 기술 부채 증가량 계산
        debt_increase = await self.debt_calculator.calculate_debt_increase(
            component,
            architecture,
            structural_impacts
        )

        # 8. 리팩토링 제안 생성
        refactoring_suggestions = await self._generate_refactoring_suggestions(
            component,
            structural_impacts + behavioral_impacts,
            architecture
        )

        # 9. 위험 매트릭스 생성
        risk_matrix = self._create_risk_matrix(
            structural_impacts + behavioral_impacts + quality_impacts
        )

        return ArchitectureImpactReport(
            component_id=component.id,
            total_impact_score=total_impact_score,
            impacts=structural_impacts + behavioral_impacts + quality_impacts + pattern_impacts,
            affected_quality_attributes=quality_impacts,
            architectural_debt_increase=debt_increase,
            refactoring_suggestions=refactoring_suggestions,
            risk_matrix=risk_matrix
        )

    async def _analyze_structural_impact(
        self,
        component: ComponentDecision,
        arch_graph: nx.DiGraph,
        change_type: str
    ) -> List[ArchitectureImpact]:
        """구조적 영향 분석"""

        impacts = []

        # 1. 레이어 위반 검사
        layer_violations = self._check_layer_violations(
            component,
            arch_graph
        )

        if layer_violations:
            impacts.append(ArchitectureImpact(
                impact_type='structural',
                severity='high',
                affected_components=layer_violations['violating_components'],
                affected_layers=layer_violations['layers'],
                affected_patterns=[],
                propagation_path=layer_violations['path'],
                mitigation_required=True,
                estimated_rework=20
            ))

        # 2. 순환 의존성 영향
        if change_type == 'addition':
            new_cycles = self._detect_new_cycles(component, arch_graph)
            if new_cycles:
                impacts.append(ArchitectureImpact(
                    impact_type='structural',
                    severity='critical',
                    affected_components=list(set(sum(new_cycles, []))),
                    affected_layers=[],
                    affected_patterns=['layered_architecture'],
                    propagation_path=new_cycles[0],
                    mitigation_required=True,
                    estimated_rework=40
                ))

        # 3. 결합도 증가 영향
        coupling_impact = await self._analyze_coupling_impact(
            component,
            arch_graph
        )

        if coupling_impact['increase'] > 0.2:
            impacts.append(ArchitectureImpact(
                impact_type='structural',
                severity='medium',
                affected_components=coupling_impact['highly_coupled'],
                affected_layers=coupling_impact['layers'],
                affected_patterns=['loose_coupling'],
                propagation_path=[],
                mitigation_required=coupling_impact['increase'] > 0.3,
                estimated_rework=15
            ))

        # 4. 모듈성 영향
        modularity_impact = self._analyze_modularity_impact(
            component,
            arch_graph
        )

        if modularity_impact['degradation'] > 0.1:
            impacts.append(ArchitectureImpact(
                impact_type='structural',
                severity='medium',
                affected_components=modularity_impact['affected_modules'],
                affected_layers=[],
                affected_patterns=['modular_architecture'],
                propagation_path=[],
                mitigation_required=False,
                estimated_rework=10
            ))

        return impacts

    async def _analyze_behavioral_impact(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture,
        change_type: str
    ) -> List[ArchitectureImpact]:
        """행동적 영향 분석"""

        impacts = []

        # 1. 상호작용 패턴 변경
        interaction_changes = await self._analyze_interaction_changes(
            component,
            architecture
        )

        if interaction_changes['significant_changes']:
            impacts.append(ArchitectureImpact(
                impact_type='behavioral',
                severity='high',
                affected_components=interaction_changes['affected_components'],
                affected_layers=[],
                affected_patterns=['interaction_patterns'],
                propagation_path=interaction_changes['change_path'],
                mitigation_required=True,
                estimated_rework=25
            ))

        # 2. 상태 관리 영향
        if component.properties.get('stateful'):
            state_impact = await self._analyze_state_impact(
                component,
                architecture
            )

            if state_impact['complexity_increase'] > 0.3:
                impacts.append(ArchitectureImpact(
                    impact_type='behavioral',
                    severity='medium',
                    affected_components=state_impact['affected_components'],
                    affected_layers=['application'],
                    affected_patterns=['state_management'],
                    propagation_path=[],
                    mitigation_required=True,
                    estimated_rework=20
                ))

        # 3. 이벤트 흐름 영향
        event_impact = await self._analyze_event_flow_impact(
            component,
            architecture
        )

        if event_impact['flow_disruption']:
            impacts.append(ArchitectureImpact(
                impact_type='behavioral',
                severity='high',
                affected_components=event_impact['affected_components'],
                affected_layers=['integration'],
                affected_patterns=['event_driven_architecture'],
                propagation_path=event_impact['disrupted_flows'],
                mitigation_required=True,
                estimated_rework=30
            ))

        return impacts

    async def _analyze_quality_impact(
        self,
        component: ComponentDecision,
        architecture: ComponentArchitecture
    ) -> Dict[str, float]:
        """품질 속성 영향 분석"""

        quality_impacts = {}

        # 1. 성능 영향
        performance_impact = await self._calculate_performance_impact(
            component,
            architecture
        )
        quality_impacts['performance'] = performance_impact

        # 2. 확장성 영향
        scalability_impact = self._calculate_scalability_impact(
            component,
            architecture
        )
        quality_impacts['scalability'] = scalability_impact

        # 3. 유지보수성 영향
        maintainability_impact = self._calculate_maintainability_impact(
            component,
            architecture
        )
        quality_impacts['maintainability'] = maintainability_impact

        # 4. 보안 영향
        security_impact = await self._calculate_security_impact(
            component,
            architecture
        )
        quality_impacts['security'] = security_impact

        # 5. 신뢰성 영향
        reliability_impact = self._calculate_reliability_impact(
            component,
            architecture
        )
        quality_impacts['reliability'] = reliability_impact

        return quality_impacts

    def _check_layer_violations(
        self,
        component: ComponentDecision,
        arch_graph: nx.DiGraph
    ) -> Optional[Dict[str, Any]]:
        """레이어 위반 검사"""

        layer_hierarchy = {
            'presentation': 0,
            'application': 1,
            'domain': 2,
            'infrastructure': 3
        }

        violations = []

        # 컴포넌트 레이어 결정
        component_layer = self._determine_component_layer(component)
        component_level = layer_hierarchy.get(component_layer, 0)

        # 의존성 검사
        for dep_id in component.dependencies:
            if dep_id in arch_graph:
                dep_layer = arch_graph.nodes[dep_id].get('layer')
                dep_level = layer_hierarchy.get(dep_layer, 0)

                # 상위 레이어가 하위 레이어에 의존하는 것은 정상
                # 하위 레이어가 상위 레이어에 의존하는 것은 위반
                if component_level > dep_level:
                    violations.append({
                        'from': component.id,
                        'to': dep_id,
                        'from_layer': component_layer,
                        'to_layer': dep_layer
                    })

        if violations:
            return {
                'violating_components': [v['from'] for v in violations],
                'layers': list(set([v['from_layer'], v['to_layer']] for v in violations)),
                'path': [violations[0]['from'], violations[0]['to']]
            }

        return None

    def _create_risk_matrix(
        self,
        impacts: List[ArchitectureImpact]
    ) -> Dict[str, Any]:
        """위험 매트릭스 생성"""

        risk_matrix = {
            'high_probability_high_impact': [],
            'high_probability_low_impact': [],
            'low_probability_high_impact': [],
            'low_probability_low_impact': []
        }

        for impact in impacts:
            # 확률 계산
            probability = self._calculate_impact_probability(impact)

            # 영향도 계산
            impact_level = self._calculate_impact_level(impact)

            # 매트릭스에 배치
            if probability > 0.6 and impact_level > 0.6:
                risk_matrix['high_probability_high_impact'].append({
                    'type': impact.impact_type,
                    'description': self._describe_impact(impact),
                    'mitigation': impact.mitigation_required
                })
            elif probability > 0.6 and impact_level <= 0.6:
                risk_matrix['high_probability_low_impact'].append({
                    'type': impact.impact_type,
                    'description': self._describe_impact(impact)
                })
            elif probability <= 0.6 and impact_level > 0.6:
                risk_matrix['low_probability_high_impact'].append({
                    'type': impact.impact_type,
                    'description': self._describe_impact(impact)
                })
            else:
                risk_matrix['low_probability_low_impact'].append({
                    'type': impact.impact_type,
                    'description': self._describe_impact(impact)
                })

        return risk_matrix

    async def _generate_refactoring_suggestions(
        self,
        component: ComponentDecision,
        impacts: List[ArchitectureImpact],
        architecture: ComponentArchitecture
    ) -> List[Dict[str, Any]]:
        """리팩토링 제안 생성"""

        suggestions = []

        # 순환 의존성 해결
        circular_impacts = [i for i in impacts if 'circular' in str(i.propagation_path)]
        if circular_impacts:
            suggestions.append({
                'type': 'dependency_inversion',
                'title': 'Apply Dependency Inversion Principle',
                'description': 'Introduce interfaces to break circular dependencies',
                'affected_components': list(set(sum([i.affected_components for i in circular_impacts], []))),
                'effort': 'medium',
                'priority': 'high',
                'steps': [
                    'Extract interfaces for dependent components',
                    'Implement dependency injection',
                    'Update component references'
                ]
            })

        # 레이어 위반 수정
        layer_violations = [i for i in impacts if i.impact_type == 'structural' and i.affected_layers]
        if layer_violations:
            suggestions.append({
                'type': 'layer_restructuring',
                'title': 'Fix Layer Architecture Violations',
                'description': 'Restructure components to follow proper layer hierarchy',
                'affected_components': list(set(sum([i.affected_components for i in layer_violations], []))),
                'effort': 'high',
                'priority': 'high',
                'steps': [
                    'Move business logic to domain layer',
                    'Extract infrastructure concerns',
                    'Update component dependencies'
                ]
            })

        # 높은 결합도 해결
        high_coupling = [i for i in impacts if 'coupling' in str(i.affected_patterns)]
        if high_coupling:
            suggestions.append({
                'type': 'decouple_components',
                'title': 'Reduce Component Coupling',
                'description': 'Apply patterns to reduce coupling between components',
                'affected_components': list(set(sum([i.affected_components for i in high_coupling], []))),
                'effort': 'medium',
                'priority': 'medium',
                'patterns': ['Mediator', 'Observer', 'Event Bus'],
                'steps': [
                    'Identify tightly coupled interfaces',
                    'Introduce mediator or event bus',
                    'Refactor direct dependencies'
                ]
            })

        return suggestions

    def _calculate_total_impact_score(
        self,
        impacts: List[ArchitectureImpact]
    ) -> float:
        """전체 영향도 점수 계산"""

        severity_weights = {
            'critical': 10.0,
            'high': 7.0,
            'medium': 4.0,
            'low': 1.0
        }

        impact_type_weights = {
            'structural': 1.2,
            'behavioral': 1.0,
            'quality_attribute': 0.8
        }

        total_score = 0.0

        for impact in impacts:
            severity_score = severity_weights.get(impact.severity, 0)
            type_weight = impact_type_weights.get(impact.impact_type, 1.0)

            # 영향받는 컴포넌트 수에 따른 가중치
            component_weight = 1 + (len(impact.affected_components) * 0.1)

            # 완화 필요 여부에 따른 가중치
            mitigation_weight = 1.5 if impact.mitigation_required else 1.0

            impact_score = severity_score * type_weight * component_weight * mitigation_weight
            total_score += impact_score

        # 0-100 스케일로 정규화
        normalized_score = min(total_score / len(impacts) * 10, 100) if impacts else 0

        return round(normalized_score, 2)
```

**검증 기준**:

- [ ] 구조적/행동적 영향 분석
- [ ] 품질 속성 영향 평가
- [ ] 리팩토링 제안 생성
- [ ] 위험 매트릭스 제공

#### SubTask 4.40.3: 기술 부채 평가기

**담당자**: 기술 부채 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/technical_debt_evaluator.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class TechnicalDebtItem:
    debt_type: str  # design, code, test, documentation, infrastructure
    component_id: str
    description: str
    principal: float  # 초기 부채 (시간)
    interest_rate: float  # 이자율 (일일)
    accumulated_interest: float  # 누적 이자
    impact_area: str
    resolution_effort: float  # 해결 노력 (시간)
    priority: str  # high, medium, low
    created_date: datetime

@dataclass
class TechnicalDebtReport:
    component_id: str
    total_debt_hours: float
    debt_ratio: float  # 부채 / 전체 개발 시간
    debt_items: List[TechnicalDebtItem]
    debt_by_type: Dict[str, float]
    payment_plan: List[Dict[str, Any]]
    roi_analysis: Dict[str, float]
    debt_trend: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

class TechnicalDebtEvaluator:
    """기술 부채 평가기"""

    def __init__(self):
        self.debt_detector = DebtDetector()
        self.interest_calculator = InterestCalculator()
        self.payment_planner = DebtPaymentPlanner()
        self.roi_analyzer = ROIAnalyzer()

    async def evaluate_technical_debt(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> TechnicalDebtReport:
        """기술 부채 평가"""

        # 1. 부채 항목 식별
        debt_items = await self._identify_debt_items(
            component,
            analysis_results
        )

        # 2. 부채 정량화
        quantified_debt = await self._quantify_debt(
            debt_items,
            component
        )

        # 3. 이자 계산
        debt_with_interest = self._calculate_interest(
            quantified_debt,
            historical_data
        )

        # 4. 전체 부채 계산
        total_debt = sum(
            item.principal + item.accumulated_interest
            for item in debt_with_interest
        )

        # 5. 부채 비율 계산
        debt_ratio = self._calculate_debt_ratio(
            total_debt,
            component.estimated_effort
        )

        # 6. 타입별 부채 분석
        debt_by_type = self._analyze_debt_by_type(debt_with_interest)

        # 7. 상환 계획 수립
        payment_plan = await self.payment_planner.create_payment_plan(
            debt_with_interest,
            component
        )

        # 8. ROI 분석
        roi_analysis = await self.roi_analyzer.analyze_debt_payment_roi(
            debt_with_interest,
            payment_plan,
            component
        )

        # 9. 부채 추세 분석
        debt_trend = self._analyze_debt_trend(
            debt_with_interest,
            historical_data
        )

        # 10. 권고사항 생성
        recommendations = await self._generate_recommendations(
            debt_with_interest,
            debt_ratio,
            roi_analysis
        )

        return TechnicalDebtReport(
            component_id=component.id,
            total_debt_hours=total_debt,
            debt_ratio=debt_ratio,
            debt_items=debt_with_interest,
            debt_by_type=debt_by_type,
            payment_plan=payment_plan,
            roi_analysis=roi_analysis,
            debt_trend=debt_trend,
            recommendations=recommendations
        )

    async def _identify_debt_items(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[TechnicalDebtItem]:
        """부채 항목 식별"""

        debt_items = []

        # 1. 설계 부채
        design_debt = await self._identify_design_debt(component, analysis_results)
        debt_items.extend(design_debt)

        # 2. 코드 부채
        code_debt = await self._identify_code_debt(component, analysis_results)
        debt_items.extend(code_debt)

        # 3. 테스트 부채
        test_debt = await self._identify_test_debt(component, analysis_results)
        debt_items.extend(test_debt)

        # 4. 문서화 부채
        doc_debt = await self._identify_documentation_debt(component, analysis_results)
        debt_items.extend(doc_debt)

        # 5. 인프라 부채
        infra_debt = await self._identify_infrastructure_debt(component, analysis_results)
        debt_items.extend(infra_debt)

        return debt_items

    async def _identify_design_debt(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[TechnicalDebtItem]:
        """설계 부채 식별"""

        design_debt = []

        # 높은 복잡도
        if component.complexity_score > 7:
            design_debt.append(TechnicalDebtItem(
                debt_type='design',
                component_id=component.id,
                description='High component complexity requiring refactoring',
                principal=20.0,  # 20시간
                interest_rate=0.02,  # 2% 일일 이자
                accumulated_interest=0.0,
                impact_area='maintainability',
                resolution_effort=30.0,
                priority='high',
                created_date=datetime.now()
            ))

        # 순환 의존성
        if analysis_results.get('circular_dependencies'):
            design_debt.append(TechnicalDebtItem(
                debt_type='design',
                component_id=component.id,
                description='Circular dependencies in architecture',
                principal=15.0,
                interest_rate=0.03,  # 3% - 높은 이자율
                accumulated_interest=0.0,
                impact_area='architecture',
                resolution_effort=25.0,
                priority='high',
                created_date=datetime.now()
            ))

        # 레이어 위반
        if analysis_results.get('layer_violations'):
            design_debt.append(TechnicalDebtItem(
                debt_type='design',
                component_id=component.id,
                description='Layer architecture violations',
                principal=10.0,
                interest_rate=0.025,
                accumulated_interest=0.0,
                impact_area='architecture',
                resolution_effort=15.0,
                priority='medium',
                created_date=datetime.now()
            ))

        return design_debt

    async def _identify_code_debt(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[TechnicalDebtItem]:
        """코드 부채 식별"""

        code_debt = []

        # 코드 중복
        duplication_ratio = analysis_results.get('code_duplication', 0)
        if duplication_ratio > 0.1:  # 10% 이상
            code_debt.append(TechnicalDebtItem(
                debt_type='code',
                component_id=component.id,
                description=f'Code duplication ({duplication_ratio*100:.1f}%)',
                principal=duplication_ratio * 50,  # 중복 비율에 비례
                interest_rate=0.015,
                accumulated_interest=0.0,
                impact_area='maintainability',
                resolution_effort=duplication_ratio * 40,
                priority='medium',
                created_date=datetime.now()
            ))

        # 긴 메서드
        long_methods = analysis_results.get('long_methods', [])
        if long_methods:
            code_debt.append(TechnicalDebtItem(
                debt_type='code',
                component_id=component.id,
                description=f'{len(long_methods)} methods exceed complexity threshold',
                principal=len(long_methods) * 3,
                interest_rate=0.01,
                accumulated_interest=0.0,
                impact_area='readability',
                resolution_effort=len(long_methods) * 5,
                priority='low',
                created_date=datetime.now()
            ))

        # 코드 스멜
        code_smells = analysis_results.get('code_smells', [])
        for smell in code_smells:
            if smell['severity'] == 'high':
                code_debt.append(TechnicalDebtItem(
                    debt_type='code',
                    component_id=component.id,
                    description=f"Code smell: {smell['type']}",
                    principal=5.0,
                    interest_rate=0.02,
                    accumulated_interest=0.0,
                    impact_area='code_quality',
                    resolution_effort=8.0,
                    priority='medium',
                    created_date=datetime.now()
                ))

        return code_debt

    async def _identify_test_debt(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[TechnicalDebtItem]:
        """테스트 부채 식별"""

        test_debt = []

        # 낮은 테스트 커버리지
        test_coverage = analysis_results.get('test_coverage', 0)
        if test_coverage < 0.8:  # 80% 미만
            coverage_gap = 0.8 - test_coverage
            test_debt.append(TechnicalDebtItem(
                debt_type='test',
                component_id=component.id,
                description=f'Test coverage below 80% (current: {test_coverage*100:.1f}%)',
                principal=coverage_gap * 100,  # 커버리지 갭에 비례
                interest_rate=0.025,  # 테스트 부채는 이자율 높음
                accumulated_interest=0.0,
                impact_area='quality',
                resolution_effort=coverage_gap * 80,
                priority='high',
                created_date=datetime.now()
            ))

        # 누락된 통합 테스트
        if not analysis_results.get('has_integration_tests'):
            test_debt.append(TechnicalDebtItem(
                debt_type='test',
                component_id=component.id,
                description='Missing integration tests',
                principal=20.0,
                interest_rate=0.02,
                accumulated_interest=0.0,
                impact_area='reliability',
                resolution_effort=30.0,
                priority='high',
                created_date=datetime.now()
            ))

        # 성능 테스트 부재
        if component.properties.get('performance_critical') and not analysis_results.get('has_performance_tests'):
            test_debt.append(TechnicalDebtItem(
                debt_type='test',
                component_id=component.id,
                description='Missing performance tests for critical component',
                principal=15.0,
                interest_rate=0.03,
                accumulated_interest=0.0,
                impact_area='performance',
                resolution_effort=25.0,
                priority='high',
                created_date=datetime.now()
            ))

        return test_debt

    def _calculate_interest(
        self,
        debt_items: List[TechnicalDebtItem],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> List[TechnicalDebtItem]:
        """이자 계산"""

        for item in debt_items:
            # 부채 생성일로부터 경과일 계산
            days_elapsed = (datetime.now() - item.created_date).days

            # 복리 이자 계산
            # A = P(1 + r)^t
            accumulated_amount = item.principal * ((1 + item.interest_rate) ** days_elapsed)
            item.accumulated_interest = accumulated_amount - item.principal

            # 이자율 조정 (시간이 지날수록 증가)
            if days_elapsed > 90:
                item.interest_rate *= 1.5  # 90일 후 이자율 50% 증가
            elif days_elapsed > 180:
                item.interest_rate *= 2.0  # 180일 후 이자율 100% 증가

        return debt_items

    def _analyze_debt_by_type(
        self,
        debt_items: List[TechnicalDebtItem]
    ) -> Dict[str, float]:
        """타입별 부채 분석"""

        debt_by_type = {
            'design': 0.0,
            'code': 0.0,
            'test': 0.0,
            'documentation': 0.0,
            'infrastructure': 0.0
        }

        for item in debt_items:
            total_debt = item.principal + item.accumulated_interest
            debt_by_type[item.debt_type] += total_debt

        # 백분율 계산
        total_debt = sum(debt_by_type.values())
        if total_debt > 0:
            debt_by_type_percentage = {
                f"{k}_percentage": (v / total_debt * 100)
                for k, v in debt_by_type.items()
            }
            debt_by_type.update(debt_by_type_percentage)

        return debt_by_type

    async def _generate_recommendations(
        self,
        debt_items: List[TechnicalDebtItem],
        debt_ratio: float,
        roi_analysis: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """권고사항 생성"""

        recommendations = []

        # 1. 높은 부채 비율 경고
        if debt_ratio > 0.3:  # 30% 이상
            recommendations.append({
                'type': 'critical',
                'title': 'High Technical Debt Ratio',
                'description': f'Technical debt is {debt_ratio*100:.1f}% of total development effort',
                'action': 'Allocate dedicated sprint for debt reduction',
                'priority': 'immediate',
                'expected_benefit': 'Improved velocity and code quality'
            })

        # 2. 높은 이자율 항목 우선 처리
        high_interest_items = sorted(
            debt_items,
            key=lambda x: x.interest_rate,
            reverse=True
        )[:3]

        for item in high_interest_items:
            recommendations.append({
                'type': 'high_priority',
                'title': f'Address {item.debt_type} debt',
                'description': item.description,
                'action': f'Allocate {item.resolution_effort} hours',
                'priority': 'high',
                'roi': roi_analysis.get(item.component_id, 0)
            })

        # 3. 빠른 승리 (Quick Wins)
        quick_wins = [
            item for item in debt_items
            if item.resolution_effort < 5 and item.priority != 'low'
        ]

        if quick_wins:
            recommendations.append({
                'type': 'quick_win',
                'title': 'Quick Win Opportunities',
                'description': f'{len(quick_wins)} debt items can be resolved quickly',
                'action': 'Address in current sprint',
                'items': [
                    {
                        'description': item.description,
                        'effort': item.resolution_effort
                    }
                    for item in quick_wins
                ],
                'total_effort': sum(item.resolution_effort for item in quick_wins)
            })

        # 4. 부채 예방 조치
        if any(item.debt_type == 'test' for item in debt_items):
            recommendations.append({
                'type': 'prevention',
                'title': 'Implement Test-Driven Development',
                'description': 'Prevent future test debt accumulation',
                'action': 'Adopt TDD practices',
                'priority': 'medium',
                'long_term_benefit': 'Reduced future debt accumulation'
            })

        return recommendations

    def _calculate_debt_ratio(
        self,
        total_debt: float,
        estimated_effort: float
    ) -> float:
        """부채 비율 계산"""

        if estimated_effort == 0:
            return 0.0

        # 스토리 포인트를 시간으로 변환 (1 포인트 = 8시간 가정)
        total_effort_hours = estimated_effort * 8

        return min(total_debt / total_effort_hours, 1.0)

    def _analyze_debt_trend(
        self,
        current_debt: List[TechnicalDebtItem],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """부채 추세 분석"""

        trend_data = []

        if historical_data:
            # 과거 데이터에서 추세 추출
            for data_point in historical_data:
                trend_data.append({
                    'date': data_point['date'],
                    'total_debt': data_point['total_debt'],
                    'debt_ratio': data_point['debt_ratio']
                })

        # 현재 데이터 추가
        current_total = sum(
            item.principal + item.accumulated_interest
            for item in current_debt
        )

        trend_data.append({
            'date': datetime.now(),
            'total_debt': current_total,
            'debt_ratio': self._calculate_debt_ratio(
                current_total,
                100  # 가정된 effort
            )
        })

        # 추세 계산 (선형 회귀)
        if len(trend_data) > 1:
            dates = [(d['date'] - trend_data[0]['date']).days for d in trend_data]
            debts = [d['total_debt'] for d in trend_data]

            # 간단한 선형 추세
            if len(dates) > 1:
                slope = (debts[-1] - debts[0]) / (dates[-1] - dates[0])
                trend_data[-1]['trend'] = 'increasing' if slope > 0 else 'decreasing'
                trend_data[-1]['rate'] = abs(slope)

        return trend_data
```

**검증 기준**:

- [ ] 다차원 부채 식별
- [ ] 이자율 기반 정량화
- [ ] 상환 계획 수립
- [ ] ROI 분석 제공

#### SubTask 4.40.4: 컴포넌트 최종 검토 시스템

**담당자**: 품질 검토 리드  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/component_decision/final_review_system.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ReviewChecklist:
    category: str
    items: List[Dict[str, Any]]
    passed_items: int
    total_items: int
    score: float
    notes: List[str]

@dataclass
class ApprovalDecision:
    approved: bool
    approval_level: str  # unconditional, conditional, rejected
    conditions: List[str]
    blockers: List[str]
    approvers: List[str]
    approval_date: datetime

@dataclass
class FinalReviewReport:
    component_id: str
    review_date: datetime
    overall_score: float
    readiness_level: str  # ready, needs_work, not_ready
    checklists: List[ReviewChecklist]
    approval_decision: ApprovalDecision
    action_items: List[Dict[str, Any]]
    sign_off_requirements: List[Dict[str, Any]]
    next_steps: List[str]

class ComponentFinalReviewSystem:
    """컴포넌트 최종 검토 시스템"""

    def __init__(self):
        self.checklist_manager = ChecklistManager()
        self.readiness_assessor = ReadinessAssessor()
        self.approval_processor = ApprovalProcessor()
        self.action_item_generator = ActionItemGenerator()

    async def conduct_final_review(
        self,
        component: ComponentDecision,
        all_analysis_results: Dict[str, Any],
        stakeholders: List[str]
    ) -> FinalReviewReport:
        """컴포넌트 최종 검토 수행"""

        # 1. 체크리스트 검토
        checklists = await self._review_all_checklists(
            component,
            all_analysis_results
        )

        # 2. 전체 점수 계산
        overall_score = self._calculate_overall_score(checklists)

        # 3. 준비도 평가
        readiness_level = await self.readiness_assessor.assess_readiness(
            component,
            checklists,
            overall_score
        )

        # 4. 승인 결정
        approval_decision = await self._make_approval_decision(
            component,
            checklists,
            readiness_level,
            stakeholders
        )

        # 5. 조치 항목 생성
        action_items = await self.action_item_generator.generate_items(
            component,
            checklists,
            approval_decision
        )

        # 6. 사인오프 요구사항
        sign_off_requirements = self._define_signoff_requirements(
            component,
            approval_decision
        )

        # 7. 다음 단계 정의
        next_steps = self._define_next_steps(
            readiness_level,
            approval_decision
        )

        return FinalReviewReport(
            component_id=component.id,
            review_date=datetime.now(),
            overall_score=overall_score,
            readiness_level=readiness_level,
            checklists=checklists,
            approval_decision=approval_decision,
            action_items=action_items,
            sign_off_requirements=sign_off_requirements,
            next_steps=next_steps
        )

    async def _review_all_checklists(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> List[ReviewChecklist]:
        """모든 체크리스트 검토"""

        checklists = []

        # 1. 기능 요구사항 체크리스트
        functional_checklist = await self._review_functional_requirements(
            component,
            analysis_results
        )
        checklists.append(functional_checklist)

        # 2. 기술 아키텍처 체크리스트
        architecture_checklist = await self._review_architecture(
            component,
            analysis_results
        )
        checklists.append(architecture_checklist)

        # 3. 코드 품질 체크리스트
        quality_checklist = await self._review_code_quality(
            component,
            analysis_results
        )
        checklists.append(quality_checklist)

        # 4. 보안 체크리스트
        security_checklist = await self._review_security(
            component,
            analysis_results
        )
        checklists.append(security_checklist)

        # 5. 성능 체크리스트
        performance_checklist = await self._review_performance(
            component,
            analysis_results
        )
        checklists.append(performance_checklist)

        # 6. 테스트 체크리스트
        testing_checklist = await self._review_testing(
            component,
            analysis_results
        )
        checklists.append(testing_checklist)

        # 7. 문서화 체크리스트
        documentation_checklist = await self._review_documentation(
            component,
            analysis_results
        )
        checklists.append(documentation_checklist)

        # 8. 배포 준비 체크리스트
        deployment_checklist = await self._review_deployment_readiness(
            component,
            analysis_results
        )
        checklists.append(deployment_checklist)

        return checklists

    async def _review_functional_requirements(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> ReviewChecklist:
        """기능 요구사항 검토"""

        items = [
            {
                'item': 'All functional requirements mapped',
                'checked': analysis_results.get('requirement_coverage', 0) >= 0.95,
                'notes': f"Coverage: {analysis_results.get('requirement_coverage', 0)*100:.1f}%"
            },
            {
                'item': 'Acceptance criteria defined',
                'checked': all(req.acceptance_criteria for req in component.requirements),
                'notes': 'All requirements have clear acceptance criteria'
            },
            {
                'item': 'Business logic validated',
                'checked': analysis_results.get('business_logic_review', False),
                'notes': 'Business stakeholders have validated logic'
            },
            {
                'item': 'Edge cases considered',
                'checked': analysis_results.get('edge_cases_covered', False),
                'notes': 'Edge cases identified and handled'
            },
            {
                'item': 'User stories complete',
                'checked': analysis_results.get('user_stories_complete', False),
                'notes': 'All user stories have been addressed'
            }
        ]

        passed = sum(1 for item in items if item['checked'])

        return ReviewChecklist(
            category='Functional Requirements',
            items=items,
            passed_items=passed,
            total_items=len(items),
            score=(passed / len(items)) * 100,
            notes=[item['notes'] for item in items if not item['checked']]
        )

    async def _review_architecture(
        self,
        component: ComponentDecision,
        analysis_results: Dict[str, Any]
    ) -> ReviewChecklist:
        """아키텍처 검토"""

        items = [
            {
                'item': 'Architecture patterns appropriate',
                'checked': analysis_results.get('pattern_appropriateness', 0) >= 0.8,
                'notes': 'Selected patterns fit the use case'
            },
            {
                'item': 'No circular dependencies',
                'checked': len(analysis_results.get('circular_dependencies', [])) == 0,
                'notes': f"{len(analysis_results.get('circular_dependencies', []))} circular dependencies found"
            },
            {
                'item': 'Layer architecture respected',
                'checked': not analysis_results.get('layer_violations', []),
                'notes': 'Clean layer separation maintained'
            },
            {
                'item': 'Coupling within limits',
                'checked': analysis_results.get('coupling_score', 1.0) < 0.3,
                'notes': f"Coupling score: {analysis_results.get('coupling_score', 0)}"
            },
            {
                'item': 'Scalability considered',
                'checked': component.properties.get('scalability_ready', False),
                'notes': 'Component designed for horizontal scaling'
            },
            {
                'item': 'Integration points defined',
                'checked': len(component.interfaces) > 0,
                'notes': f"{len(component.interfaces)} integration points defined"
            }
        ]

        passed = sum(1 for item in items if item['checked'])

        return ReviewChecklist(
            category='Technical Architecture',
            items=items,
            passed_items=passed,
            total_items=len(items),
            score=(passed / len(items)) * 100,
            notes=[item['notes'] for item in items if not item['checked']]
        )

    async def _make_approval_decision(
        self,
        component: ComponentDecision,
        checklists: List[ReviewChecklist],
        readiness_level: str,
        stakeholders: List[str]
    ) -> ApprovalDecision:
        """승인 결정"""

        # 차단 사항 확인
        blockers = []
        conditions = []

        # 필수 체크리스트 항목 확인
        for checklist in checklists:
            if checklist.category in ['Security', 'Functional Requirements']:
                if checklist.score < 90:
                    blockers.append(
                        f"{checklist.category} score below 90% ({checklist.score:.1f}%)"
                    )
            elif checklist.score < 70:
                conditions.append(
                    f"Improve {checklist.category} (current: {checklist.score:.1f}%)"
                )

        # 준비도 수준 확인
        if readiness_level == 'not_ready':
            blockers.append('Component readiness level: Not Ready')

        # 승인 수준 결정
        if blockers:
            approval_level = 'rejected'
            approved = False
        elif conditions:
            approval_level = 'conditional'
            approved = True
        else:
            approval_level = 'unconditional'
            approved = True

        return ApprovalDecision(
            approved=approved,
            approval_level=approval_level,
            conditions=conditions,
            blockers=blockers,
            approvers=stakeholders,
            approval_date=datetime.now()
        )

    def _define_signoff_requirements(
        self,
        component: ComponentDecision,
        approval_decision: ApprovalDecision
    ) -> List[Dict[str, Any]]:
        """사인오프 요구사항 정의"""

        requirements = [
            {
                'role': 'Technical Lead',
                'required': True,
                'criteria': 'Architecture and code quality approval',
                'status': 'pending'
            },
            {
                'role': 'Product Owner',
                'required': True,
                'criteria': 'Functional requirements met',
                'status': 'pending'
            },
            {
                'role': 'Security Officer',
                'required': component.properties.get('handles_sensitive_data', False),
                'criteria': 'Security requirements satisfied',
                'status': 'pending'
            },
            {
                'role': 'QA Lead',
                'required': True,
                'criteria': 'Test coverage and quality gates passed',
                'status': 'pending'
            }
        ]

        # 조건부 승인인 경우 추가 요구사항
        if approval_decision.approval_level == 'conditional':
            requirements.append({
                'role': 'Project Manager',
                'required': True,
                'criteria': 'Risk acceptance for conditional items',
                'status': 'pending'
            })

        return requirements

    def _define_next_steps(
        self,
        readiness_level: str,
        approval_decision: ApprovalDecision
    ) -> List[str]:
        """다음 단계 정의"""

        next_steps = []

        if approval_decision.approved:
            if approval_decision.approval_level == 'unconditional':
                next_steps.extend([
                    'Proceed to implementation phase',
                    'Set up development environment',
                    'Create implementation tasks in project management tool',
                    'Schedule kick-off meeting with development team'
                ])
            else:  # conditional
                next_steps.extend([
                    'Address conditional approval items',
                    'Schedule follow-up review',
                    'Update component design based on conditions',
                    'Get re-approval after conditions are met'
                ])
        else:  # rejected
            next_steps.extend([
                'Address all blocking issues',
                'Revise component design',
                'Schedule design review session',
                'Update analysis based on feedback',
                'Resubmit for approval'
            ])

        # 준비도별 추가 단계
        if readiness_level == 'needs_work':
            next_steps.extend([
                'Complete missing documentation',
                'Improve test coverage plan',
                'Refine architecture based on review feedback'
            ])

        return next_steps

    async def export_review_report(
        self,
        report: FinalReviewReport,
        format: str = 'pdf'
    ) -> bytes:
        """검토 보고서 내보내기"""

        if format == 'pdf':
            return await self._export_pdf_report(report)
        elif format == 'html':
            return self._export_html_report(report)
        elif format == 'json':
            return self._export_json_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _calculate_overall_score(
        self,
        checklists: List[ReviewChecklist]
    ) -> float:
        """전체 점수 계산"""

        # 카테고리별 가중치
        weights = {
            'Functional Requirements': 0.25,
            'Technical Architecture': 0.20,
            'Code Quality': 0.15,
            'Security': 0.15,
            'Performance': 0.10,
            'Testing': 0.10,
            'Documentation': 0.05
        }

        weighted_score = 0.0
        total_weight = 0.0

        for checklist in checklists:
            weight = weights.get(checklist.category, 0.1)
            weighted_score += checklist.score * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0
```

**검증 기준**:

- [ ] 포괄적인 체크리스트
- [ ] 명확한 승인 프로세스
- [ ] 조건부 승인 지원
- [ ] 실행 가능한 다음 단계

---
