# Matching Rate Agent

## 개요
Matching Rate Agent는 요구사항과 컴포넌트 간의 호환성을 다차원적으로 분석하여 정확한 매칭 점수를 제공합니다.

## 주요 기능

### 1. 다차원 매칭 알고리즘
- 기능적 호환성 (40%)
- 기술적 호환성 (30%)
- 성능 호환성 (20%)
- 일반 호환성 (10%)

```python
matcher = MultiDimensionalMatcher()
result = await matcher.calculate_matching_score(requirement, component)
```

### 2. 의미적 유사도 분석
- 텍스트 임베딩 기반 유사도 계산
- AWS Bedrock Titan Embeddings 활용

```python
analyzer = SemanticSimilarityAnalyzer()
similarity = await analyzer.calculate_semantic_similarity(text1, text2)
```

### 3. 동적 가중치 조정
- 프로젝트 컨텍스트 기반 가중치 조정
- 사용자 선호도 반영

```python
adjuster = DynamicWeightAdjuster()
weights = await adjuster.adjust_weights(project_context, user_preferences)
```

### 4. 매칭 결과 설명
- 점수 산출 근거 제공
- 개선 제안 생성

```python
explainer = MatchingExplainer()
explanation = await explainer.generate_explanation(result, requirement, component)
```

## 사용 예시

```python
from matching_rate.matching_rate_agent import MultiDimensionalMatcher

# 매칭 점수 계산
matcher = MultiDimensionalMatcher()
result = await matcher.calculate_matching_score(
    requirement={'features': ['responsive', 'fast']},
    component={'features': ['responsive', 'accessible']}
)

print(f"Overall Score: {result.overall_score}")
print(f"Confidence: {result.confidence}")
```

## 설정

환경 변수:
- `BEDROCK_REGION`: AWS Bedrock 리전
- `EMBEDDING_MODEL`: 임베딩 모델 ID
- `MATCHING_THRESHOLD`: 매칭 임계값 (기본: 0.7)