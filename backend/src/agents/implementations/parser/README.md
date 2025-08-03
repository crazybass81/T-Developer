# Parser Agent (요구사항 파싱 에이전트)

Parser Agent는 자연어로 작성된 프로젝트 요구사항을 구조화된 데이터로 변환하는 T-Developer의 핵심 에이전트입니다.

## 🎯 주요 기능

### 1. 요구사항 파싱
- **기능 요구사항**: 시스템이 수행해야 할 기능들을 추출
- **비기능 요구사항**: 성능, 보안, 확장성 등의 품질 속성 추출
- **기술 요구사항**: 사용할 기술 스택과 아키텍처 제약사항 추출
- **비즈니스 요구사항**: 비즈니스 목표와 제약사항 추출

### 2. 구조화된 산출물 생성
- **사용자 스토리**: Agile 개발을 위한 사용자 스토리 자동 생성
- **데이터 모델**: 엔티티와 관계를 포함한 데이터베이스 스키마 추출
- **API 명세**: RESTful API 엔드포인트와 스키마 정의
- **UI 컴포넌트**: 필요한 사용자 인터페이스 요소 식별

### 3. 요구사항 검증
- **완성도 검증**: 필수 정보의 누락 여부 확인
- **일관성 검증**: 요구사항 간의 모순이나 충돌 검사
- **명확성 검증**: 모호한 표현이나 불분명한 요구사항 식별
- **추적성 검증**: 요구사항 간의 의존성과 관계 검증

## 🏗️ 아키텍처

```
ParserAgent
├── Main Parser (Claude 3 Sonnet)     # 주 파싱 엔진
├── Detail Parser (GPT-4)             # 세부 분석
├── Parsing Rules Engine               # 규칙 기반 추출
├── Requirement Extractor              # 요구사항 추출기
├── User Story Generator               # 사용자 스토리 생성기
├── Data Model Parser                  # 데이터 모델 파서
├── API Specification Parser           # API 명세 파서
├── Constraint Analyzer                # 제약사항 분석기
└── Requirement Validator              # 요구사항 검증기
```

## 📊 성능 목표

- **파싱 시간**: 평균 2초 이내 (일반적인 요구사항 문서 기준)
- **정확도**: 요구사항 분류 정확도 90% 이상
- **완성도**: 추출된 요구사항의 완성도 85% 이상
- **검증 점수**: 요구사항 품질 검증 점수 0.8 이상

## 🚀 사용법

### 기본 사용법

```python
from parser_agent import ParserAgent

# Parser Agent 초기화
parser = ParserAgent()

# 요구사항 파싱
result = await parser.parse_requirements(
    raw_description="""
    Build an e-commerce platform with user authentication,
    product catalog, shopping cart, and payment processing.
    The system must support 10,000 concurrent users and
    respond within 200ms for all operations.
    """,
    project_context={
        'project_type': 'web_application',
        'domain': 'ecommerce'
    }
)

# 결과 확인
print(f"Functional Requirements: {len(result.functional_requirements)}")
print(f"Data Models: {len(result.data_models)}")
print(f"API Specifications: {len(result.api_specifications)}")
```

### 고급 사용법

```python
# 파싱 옵션 설정
parsing_options = {
    'extract_user_stories': True,
    'generate_api_specs': True,
    'validate_requirements': True,
    'infer_data_models': True
}

result = await parser.parse_requirements(
    raw_description=requirements_text,
    project_context=context,
    parsing_options=parsing_options
)

# 검증 결과 확인
validation = result.project_info['validation']
print(f"Validation Score: {validation['validation_score']}")
print(f"Issues Found: {len(validation['validation_results']['completeness']['issues'])}")
```

## 📋 출력 구조

### ParsedProject
```python
@dataclass
class ParsedProject:
    project_info: Dict[str, Any]                    # 프로젝트 기본 정보
    functional_requirements: List[ParsedRequirement] # 기능 요구사항
    non_functional_requirements: List[ParsedRequirement] # 비기능 요구사항
    technical_requirements: List[ParsedRequirement]  # 기술 요구사항
    business_requirements: List[ParsedRequirement]   # 비즈니스 요구사항
    constraints: List[ParsedRequirement]             # 제약사항
    assumptions: List[ParsedRequirement]             # 가정사항
    user_stories: List[Dict[str, Any]]              # 사용자 스토리
    use_cases: List[Dict[str, Any]]                 # 사용 사례
    data_models: List[Dict[str, Any]]               # 데이터 모델
    api_specifications: List[Dict[str, Any]]        # API 명세
    ui_components: List[Dict[str, Any]]             # UI 컴포넌트
    integration_points: List[Dict[str, Any]]        # 통합 지점
```

### ParsedRequirement
```python
@dataclass
class ParsedRequirement:
    id: str                                # 고유 식별자 (예: FR-001)
    type: RequirementType                  # 요구사항 타입
    category: str                          # 세부 카테고리
    description: str                       # 요구사항 설명
    priority: str                          # 우선순위 (critical/high/medium/low)
    dependencies: List[str]                # 의존성 목록
    acceptance_criteria: List[str]         # 수용 기준
    technical_details: Dict[str, Any]      # 기술적 세부사항
    metadata: Dict[str, Any]               # 메타데이터
```

## 🔧 설정

### 환경 변수
```bash
# AWS Bedrock 설정
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# OpenAI 설정 (Detail Parser용)
OPENAI_API_KEY=your-openai-key

# Parser 설정
PARSER_TIMEOUT=30
PARSER_MAX_RETRIES=3
PARSER_TEMPERATURE=0.2
```

### 파싱 규칙 커스터마이징
```python
# 커스텀 파싱 규칙 추가
parser.parsing_rules.add_rule(
    name="custom_performance_rule",
    pattern=r'latency\s+under\s+(\d+)\s*ms',
    extractor=custom_performance_extractor,
    category="performance",
    priority=1
)
```

## 🧪 테스트

```bash
# 단위 테스트 실행
pytest backend/tests/agents/parser/test_parser_agent.py -v

# 성능 테스트 실행
pytest backend/tests/agents/parser/test_parser_agent.py::TestParserAgent::test_parsing_performance -v

# 통합 테스트 실행
pytest backend/tests/agents/parser/ -m integration
```

## 📈 모니터링

Parser Agent는 다음 메트릭을 제공합니다:

- **파싱 시간**: 요구사항 파싱에 소요된 시간
- **추출된 요구사항 수**: 각 타입별 요구사항 개수
- **검증 점수**: 요구사항 품질 검증 결과
- **에러율**: 파싱 실패율
- **토큰 사용량**: LLM 토큰 소비량

## 🔍 문제 해결

### 일반적인 문제

1. **파싱 결과가 부정확한 경우**
   - 입력 텍스트의 품질을 확인
   - 프로젝트 컨텍스트 정보를 더 상세히 제공
   - 파싱 규칙을 커스터마이징

2. **성능이 느린 경우**
   - 입력 텍스트 길이를 적절히 조절
   - 불필요한 파싱 옵션 비활성화
   - 캐싱 활용

3. **검증 점수가 낮은 경우**
   - 요구사항 작성 가이드라인 참조
   - 더 구체적이고 명확한 표현 사용
   - 필수 정보 누락 여부 확인

### 로그 확인
```python
import logging
logging.getLogger('parser_agent').setLevel(logging.DEBUG)
```

## 🤝 기여

Parser Agent 개선에 기여하려면:

1. 새로운 파싱 규칙 추가
2. 도메인별 특화 로직 구현
3. 검증 규칙 개선
4. 테스트 케이스 추가

## 📚 참고 자료

- [요구사항 작성 가이드](./docs/requirements-writing-guide.md)
- [파싱 규칙 개발 가이드](./docs/parsing-rules-guide.md)
- [API 문서](./docs/api-reference.md)
- [성능 최적화 가이드](./docs/performance-optimization.md)