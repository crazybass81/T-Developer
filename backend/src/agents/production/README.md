# Production-Ready Agent Implementations

이 디렉토리는 T-Developer MVP의 9개 핵심 에이전트의 production-ready 구현을 포함합니다.

## 구조

```
production/
├── nl_input/          # NL Input Agent (Task 4.1-4.4)
│   ├── core.py       # 핵심 에이전트 로직
│   ├── multimodal.py # 멀티모달 처리
│   ├── context.py    # 컨텍스트 관리
│   ├── clarification.py # 요구사항 명확화
│   ├── multilingual.py  # 다국어 지원
│   ├── optimizer.py     # 성능 최적화
│   └── __init__.py
│
├── ui_selection/      # UI Selection Agent (Task 4.5-4.8)
│   ├── core.py
│   ├── framework_analyzer.py
│   ├── recommendation.py
│   └── __init__.py
│
├── parser/            # Parser Agent (Task 4.9-4.12)
│   ├── core.py
│   ├── structure_analyzer.py
│   ├── dependency_resolver.py
│   └── __init__.py
│
├── component_decision/ # Component Decision Agent (Task 4.13-4.16)
│   ├── core.py
│   ├── mcdm.py       # Multi-Criteria Decision Making
│   ├── validator.py
│   └── __init__.py
│
├── match_rate/        # Match Rate Agent (Task 4.17-4.20)
│   ├── core.py
│   ├── similarity.py
│   ├── ranking.py
│   └── __init__.py
│
├── search/            # Search Agent (Task 4.21-4.40)
│   ├── core.py
│   ├── vector_search.py
│   ├── caching.py
│   ├── ranking.py
│   └── __init__.py
│
├── generation/        # Generation Agent (Task 4.41-4.60)
│   ├── core.py
│   ├── code_generator.py
│   ├── template_engine.py
│   ├── quality_checker.py
│   └── __init__.py
│
├── assembly/          # Assembly Agent (Task 4.61-4.80)
│   ├── core.py
│   ├── builder.py
│   ├── dependency_installer.py
│   ├── validator.py
│   └── __init__.py
│
└── download/          # Download Agent (Task 4.81-4.90)
    ├── core.py
    ├── packager.py
    ├── optimizer.py
    └── __init__.py
```

## 구현 상태

- [x] NL Input Agent - 핵심 구현 완료, 부가 기능 통합 중
- [x] UI Selection Agent - 핵심 구현 완료
- [x] Parser Agent - 핵심 구현 완료
- [x] Component Decision Agent - 핵심 구현 완료
- [ ] Match Rate Agent - 구현 중
- [ ] Search Agent - 구현 중
- [ ] Generation Agent - 구현 중
- [ ] Assembly Agent - 구현 중
- [ ] Download Agent - 구현 중

## 실행 환경

### Lambda Functions (경량 에이전트)
- NL Input Agent (< 30초)
- UI Selection Agent (< 10초)
- Parser Agent (< 20초)
- Match Rate Agent (< 15초)
- Search Agent (< 10초)

### EC2/ECS/Fargate (무거운 에이전트)
- Component Decision Agent (> 1분)
- Generation Agent (> 2분)
- Assembly Agent (> 2분)
- Download Agent (> 30초)

## 통합 요구사항

1. **Agno Framework 통합**: 3μs 에이전트 인스턴스화
2. **AWS Agent Squad**: 멀티 에이전트 오케스트레이션
3. **AWS Bedrock AgentCore**: 엔터프라이즈 런타임
4. **AWS Services**:
   - Parameter Store: 일반 설정
   - Secrets Manager: 민감한 정보
   - DynamoDB: 세션 저장
   - S3: 아티팩트 저장
   - CloudWatch: 모니터링