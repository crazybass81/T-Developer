# UI Selection Agent

UI 프레임워크 선택을 위한 지능형 에이전트 시스템입니다.

## 🎯 주요 기능

### 1. 프레임워크 분석 및 선택
- React, Vue, Angular, Next.js, Svelte 등 주요 프레임워크 지원
- 프로젝트 요구사항 기반 최적 프레임워크 추천
- 성능, SEO, 팀 전문성, 생태계 성숙도 종합 평가

### 2. 디자인 시스템 매칭
- Material-UI, Ant Design, Chakra UI, Vuetify 등 지원
- 프레임워크 호환성 및 요구사항 매칭
- 커스터마이제이션 수준 및 접근성 고려

### 3. 컴포넌트 라이브러리 추천
- 필요한 컴포넌트 기반 라이브러리 매칭
- 설치 복잡도 및 번들 크기 분석
- 유지보수 상태 및 커뮤니티 지원 평가

### 4. 보일러플레이트 생성
- 선택된 프레임워크 기반 프로젝트 템플릿 생성
- TypeScript, PWA, ESLint 등 옵션 지원
- 설치 가이드 및 사용 예제 제공

## 🚀 사용 방법

```python
from ui_selection_agent import UISelectionAgent

agent = UISelectionAgent()

# 프레임워크 선택
requirements = {
    "seo_critical": True,
    "expected_users": 50000,
    "team_expertise": {"react": "intermediate"},
    "timeline": "medium",
    "performance_critical": True
}

recommendation = await agent.select_ui_framework(requirements)

print(f"추천 프레임워크: {recommendation.framework}")
print(f"신뢰도: {recommendation.confidence_score:.2f}")
print(f"이유: {recommendation.reasons}")
```

## 📊 평가 기준

### 프레임워크 스코어링 가중치
- 프로젝트 타입 매칭: 25%
- 성능: 20%
- SEO 능력: 15%
- 팀 전문성: 15%
- 생태계 성숙도: 15%
- 학습 곡선: 10%

### 지원 프레임워크
- **React**: 복잡한 SPA, 대시보드, 실시간 애플리케이션
- **Next.js**: SEO ���요, 전자상거래, 마케팅 사이트
- **Vue**: 빠른 프로토타이핑, 중소규모 프로젝트
- **Angular**: 엔터프라이즈, 대규모 팀, 복잡한 폼
- **Svelte**: 성능 중요, 작은 번들 크기

## 🔧 설정

환경 변수:
```bash
# AWS Bedrock 설정
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-v2:0
```

## 📈 성능 목표

- 프레임워크 선택 응답시간: < 2초
- 추천 정확도: > 85%
- 동시 요청 처리: 100+ requests/sec