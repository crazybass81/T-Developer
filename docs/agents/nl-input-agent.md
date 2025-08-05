# NL Input Agent

## 개요
NL Input Agent는 자연어 프로젝트 설명을 분석하고 구조화된 요구사항으로 변환하는 에이전트입니다.

## 주요 기능

### 1. 자연어 처리 엔진
- Bedrock Claude 3 Sonnet 기반 분석
- 멀티모달 입력 지원 (텍스트, 이미지, PDF)
- 7개 언어 지원

### 2. 요구사항 추출
- 기능적/비기능적 요구사항 분리
- 기술 스택 선호도 분석
- 제약사항 식별

### 3. 실시간 피드백
- WebSocket 기반 실시간 통신
- 명확화 질문 생성
- 사용자 응답 처리

## 구현 상태
- **진행률**: 100% 완료 ✅
- **성능**: 평균 응답시간 < 2초
- **정확도**: 95% 이상

## 사용 예시

```python
from agents.nl_input_agent import NLInputAgent

agent = NLInputAgent()
result = await agent.process_description(
    "React로 할일 관리 앱을 만들어주세요"
)

print(f"프로젝트 타입: {result.project_type}")
print(f"기술 요구사항: {result.technical_requirements}")
```

## API 참조

### `process_description(description: str) -> ProjectRequirements`
자연어 설명을 구조화된 요구사항으로 변환합니다.

### `generate_clarification_questions(requirements) -> List[Question]`
모호한 부분에 대한 명확화 질문을 생성합니다.