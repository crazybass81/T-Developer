# Backend Test Suite

## 📁 테스트 구조

```
tests/
├── unit/           # 단위 테스트
├── integration/    # 통합 테스트
├── e2e/           # End-to-End 테스트
├── fixtures/      # 테스트 데이터
├── helpers/       # 테스트 유틸리티
└── security/      # 보안 테스트
```

## 🧪 테스트 파일

### Unit Tests (`unit/`)
| 파일 | 설명 | 커버리지 |
|-----|------|---------|
| `agent-registry.test.ts` | 에이전트 레지스트리 테스트 | 85% |
| `agent-state-manager.test.ts` | 에이전트 상태 관리 테스트 | 78% |
| `caching.test.ts` | 캐싱 시스템 테스트 | 92% |
| `encryption.test.ts` | 암호화 모듈 테스트 | 88% |
| `garbage-collector.test.ts` | 가비지 컬렉터 테스트 | 75% |
| `workflow-engine.test.ts` | 워크플로우 엔진 테스트 | 80% |

### Integration Tests (`integration/`)
| 파일 | 설명 | 상태 |
|-----|------|------|
| `api.test.ts` | REST API 통합 테스트 | ✅ |
| `test_agent_framework.py` | 에이전트 프레임워크 통합 | ✅ |
| `test_collaboration_management.py` | 협업 관리 테스트 | ✅ |
| `test_communication_framework.py` | 통신 프레임워크 테스트 | ✅ |
| `test_enhanced_framework.py` | 향상된 프레임워크 테스트 | ✅ |
| `test_nl_to_parser_workflow.py` | NL → Parser 워크플로우 | ✅ |

### E2E Tests (`e2e/`)
| 파일 | 설명 | 실행 시간 |
|-----|------|----------|
| `workflow.test.ts` | 전체 워크플로우 테스트 | ~30s |
| `test_complete_workflow.py` | 완전한 시나리오 테스트 | ~45s |

## 🚀 테스트 실행

### 모든 테스트 실행
```bash
npm test
```

### 특정 테스트 실행
```bash
# Unit 테스트만
npm run test:unit

# Integration 테스트만
npm run test:integration

# E2E 테스트만
npm run test:e2e
```

### Python 테스트 실행
```bash
# 모든 Python 테스트
pytest

# 특정 파일
pytest tests/integration/test_agent_framework.py

# 커버리지 포함
pytest --cov=src --cov-report=html
```

### TypeScript 테스트 실행
```bash
# Jest 실행
npm run test

# Watch 모드
npm run test:watch

# 커버리지
npm run test:coverage
```

## 📊 테스트 커버리지

현재 전체 테스트 커버리지: **73%**

| 카테고리 | 커버리지 |
|---------|---------|
| Unit Tests | 82% |
| Integration Tests | 71% |
| E2E Tests | 65% |

## 🛠️ 테스트 도구

- **Jest**: TypeScript/JavaScript 테스트
- **Pytest**: Python 테스트
- **Supertest**: API 테스트
- **Mock Service Worker**: API 모킹

## 📝 테스트 작성 가이드

### 1. 단위 테스트
```typescript
describe('ComponentName', () => {
  it('should do something', () => {
    // Arrange
    const input = 'test';
    
    // Act
    const result = myFunction(input);
    
    // Assert
    expect(result).toBe('expected');
  });
});
```

### 2. 통합 테스트
```python
def test_agent_integration():
    # Given
    agent = NLInputAgent()
    
    # When
    result = agent.process("Create a React component")
    
    # Then
    assert result['status'] == 'success'
```

### 3. E2E 테스트
```typescript
describe('Complete Workflow', () => {
  it('should process from NL to download', async () => {
    const response = await request(app)
      .post('/api/v1/generate')
      .send({ query: 'Create a dashboard' });
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('downloadUrl');
  });
});
```

## 🔧 테스트 환경 설정

### 환경 변수
테스트 실행 시 AWS Secrets Manager에서 자동으로 로드됩니다.

```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
npm test
```

### 모킹
- Database: In-memory SQLite
- Redis: Redis-mock
- AWS Services: LocalStack

## 🐛 트러블슈팅

### 테스트 실패 시
1. 의존성 확인: `npm install`
2. 환경변수 확인: AWS 자격 증명
3. 캐시 정리: `npm run test:clear-cache`

### 느린 테스트
- E2E 테스트는 병렬 실행: `npm run test:e2e -- --parallel`
- 특정 테스트만 실행: `npm test -- --grep "specific test"`

## 📈 CI/CD 통합

GitHub Actions에서 자동 실행:
- PR 생성 시: Unit + Integration 테스트
- Main 병합 시: 전체 테스트 스위트