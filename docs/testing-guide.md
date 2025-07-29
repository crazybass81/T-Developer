# T-Developer 테스트 가이드

## 📋 테스트 구조

### 테스트 레벨
1. **단위 테스트** (`tests/utils/`) - 개별 함수/클래스 테스트
2. **통합 테스트** (`tests/integration/`) - API 엔드포인트 테스트
3. **E2E 테스트** (`tests/e2e/`) - 전체 시스템 플로우 테스트

## 🧪 테스트 실행

### 단위 테스트
```bash
cd backend
npm run test:unit
```

### 통합 테스트
```bash
npm run test:integration
```

### E2E 테스트
```bash
# 스크립트 사용 (권장)
../scripts/run-e2e-tests.sh

# 또는 직접 실행
npm run test:e2e
```

### 모든 테스트
```bash
npm test
```

## 🔧 테스트 헬퍼 사용법

### TestDataGenerator
```typescript
import { TestDataGenerator } from '../helpers/test-utils';

const project = TestDataGenerator.project({
  name: 'Custom Project Name'
});
```

### 인증 테스트
```typescript
import { AuthTestHelpers } from '../helpers/auth-helpers';

const authHelpers = new AuthTestHelpers();
const tokens = await authHelpers.generateTestTokens();
```

### 데이터베이스 모킹
```typescript
import { DatabaseTestHelpers } from '../helpers/database-helpers';

DatabaseTestHelpers.mockGetItem({ id: 'test', name: 'Test Item' });
```

## 🐳 E2E 테스트 환경

### 필요 조건
- Docker Desktop 실행 중
- 포트 8000, 6379, 8080 사용 가능

### 환경 구성
- **DynamoDB Local**: 포트 8000
- **Redis**: 포트 6379  
- **애플리케이션**: 포트 8080

### 자동 정리
E2E 테스트는 완료 후 자동으로 Docker 컨테이너를 정리합니다.

## 📊 커버리지 리포트

```bash
npm run test:coverage
```

리포트는 `coverage/` 디렉토리에 생성됩니다:
- `coverage/lcov-report/index.html` - HTML 리포트
- `coverage/lcov.info` - LCOV 형식

## 🌱 테스트 데이터 시딩

### 기본 시딩
```bash
npm run test:seed
```

### 시나리오별 시딩
```typescript
import { TestScenarios } from '../fixtures/test-scenarios';

const scenarios = new TestScenarios(seeder);
await scenarios.createBasicScenario();  // 기본 시나리오
await scenarios.createLargeScenario();  // 대용량 시나리오
```

## ⚠️ 주의사항

1. **E2E 테스트는 순차 실행**: Docker 컨테이너 충돌 방지
2. **포트 충돌 확인**: 테스트 포트가 사용 중이면 실패
3. **Docker 상태 확인**: E2E 테스트 전 Docker 실행 확인
4. **환경 변수**: 테스트용 환경 변수 자동 설정
5. **데이터 시딩**: 테스트 전 필요한 데이터 시딩 실행