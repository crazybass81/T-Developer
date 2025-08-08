# T-Developer MVP 제품 완성 작업지시서

## 🎯 목표
**자연어 입력으로 완전한 프로젝트를 생성하고 다운로드할 수 있는 실제 작동하는 MVP 제품 완성**

실제 사용자가 "블로그 만들어줘" → ZIP 파일 다운로드 → 완전히 작동하는 프로젝트 까지의 전체 프로세스가 실제로 동작해야 함

## 📊 현재 완성도 분석

### 전체 완성도: **65%**

| 영역 | 완성도 | 상태 | 설명 |
|------|--------|------|------|
| 아키텍처 설계 | 95% | ✅ | 완벽한 설계 문서 |
| TypeScript 에이전트 | 90% | ✅ | Production 수준 (9/9 완성) |
| Python 에이전트 | 45% | ⚠️ | 4/9 완성, 통합 필요 |
| 프론트엔드 | 85% | ✅ | React UI 완성 |
| 백엔드 통합 | 30% | ⚠️ | Mock API만 동작 |
| 실제 프로젝트 생성 | 10% | ❌ | Mock 데이터만 생성 |
| AWS 배포 | 20% | ❌ | 인프라 준비만 완료 |
| 3대 프레임워크 통합 | 15% | ❌ | 미통합 상태 |

## 🔨 핵심 작업 목록

### Phase 1: 백엔드 핵심 통합 (1주차) - 🔥 최우선

#### 1.1 Python Agent 통합 (3일)
- [ ] TypeScript → Python 에이전트 브릿지 구현
- [ ] `/backend/src/agents/implementations/`의 고급 Python 구현체 활용
- [ ] 9-Agent Pipeline Python 실행 환경 구축
- [ ] 실제 코드 생성 로직 구현 (Mock 제거)

#### 1.2 실제 프로젝트 생성 엔진 (2일)
- [ ] Generation Agent에서 실제 React/Vue/Next.js 프로젝트 생성
- [ ] Assembly Agent에서 실제 파일 조립 및 ZIP 생성
- [ ] Download Agent에서 실제 다운로드 가능한 파일 제공
- [ ] 템플릿 시스템 구축 (기본 프로젝트 뼈대)

#### 1.3 FastAPI 백엔드 완성 (2일)
- [ ] `/backend/src/simple_api.py` → 완전한 FastAPI 서버로 확장
- [ ] TypeScript Express 서버와 병렬 운영 또는 대체
- [ ] Python Agent 호출 통합
- [ ] 에러 핸들링 및 로깅 완성

### Phase 2: 품질 향상 및 연결 (2주차)

#### 2.1 프론트엔드-백엔드 연결 강화 (3일)
- [ ] 실시간 진행상황 WebSocket 연결
- [ ] 에러 처리 및 사용자 피드백 개선
- [ ] 다운로드 프로세스 최적화
- [ ] 프로젝트 미리보기 기능

#### 2.2 핵심 프레임워크 기본 통합 (4일)
- [ ] Agno Framework 기본 통합 (고성능 Agent 생성)
- [ ] AWS Agent Squad 기본 오케스트레이션
- [ ] 성능 모니터링 대시보드
- [ ] 메모리 사용량 최적화

### Phase 3: 테스트, 배포 및 최적화 (3주차)

#### 3.1 테스트 및 검증 (3일)
- [ ] E2E 테스트 시나리오 구현
- [ ] 실제 프로젝트 생성 품질 검증
- [ ] 성능 벤치마크 (30초 이내 생성 목표)
- [ ] 사용자 시나리오 테스트

#### 3.2 AWS 인프라 배포 (2일)
- [ ] EC2/ECS 기본 배포 환경
- [ ] Lambda Functions 경량 Agent 배포
- [ ] S3 정적 파일 서빙
- [ ] CloudFront CDN 구성

#### 3.3 MVP 최종 완성 (2일)
- [ ] 사용자 문서 작성
- [ ] 성능 튜닝
- [ ] 보안 검수
- [ ] 운영 모니터링 설정

## 📋 상세 작업 목록 (우선순위별)

### 🔥 Critical Path - 즉시 시작

| # | 작업명 | 우선순위 | 예상시간 | 위치 | 담당 |
|---|--------|----------|----------|------|------|
| 1 | Python Agent 실행 환경 구축 | P0 | 1일 | `/backend/src/agents/` | BE |
| 2 | 실제 코드 생성 로직 구현 | P0 | 2일 | `/backend/src/agents/generation/` | BE |
| 3 | ZIP 다운로드 파이프라인 | P0 | 1일 | `/backend/src/agents/download/` | BE |
| 4 | FastAPI 서버 완성 | P0 | 1일 | `/backend/src/simple_api.py` | BE |

### 🚀 High Priority - 1주차 완료

| # | 작업명 | 우선순위 | 예상시간 | 위치 | 담당 |
|---|--------|----------|----------|------|------|
| 5 | 프론트엔드 실시간 연결 | P1 | 1일 | `/frontend/src/App.tsx` | FE |
| 6 | 템플릿 시스템 구축 | P1 | 2일 | `/backend/templates/` | BE |
| 7 | 에러 처리 및 로깅 | P1 | 1일 | 전체 백엔드 | BE |
| 8 | 프로젝트 타입별 생성기 | P1 | 2일 | `/backend/src/generators/` | BE |

### 📈 Medium Priority - 2주차 완료

| # | 작업명 | 우선순위 | 예상시간 | 위치 | 담당 |
|---|--------|----------|----------|------|------|
| 9 | AWS 기본 인프라 | P2 | 2일 | `/infrastructure/` | DevOps |
| 10 | 성능 최적화 | P2 | 2일 | 전체 백엔드 | BE |
| 11 | 품질 검증 시스템 | P2 | 1일 | `/backend/src/validators/` | BE |
| 12 | 테스트 코드 작성 | P2 | 3일 | `/backend/tests/`, `/frontend/tests/` | QA |

## ⚠️ 리스크 및 블로커

### 🚨 Critical Risks

1. **Python-TypeScript 통합 복잡성**
   - 리스크: 언어간 브릿지 오버헤드로 성능 저하
   - 대응: subprocess 대신 HTTP API 호출 방식으로 변경
   - 영향도: High - 전체 아키텍처에 영향

2. **실제 코드 생성 품질**
   - 리스크: AI 생성 코드의 일관성 및 실행 가능성
   - 대응: 검증된 템플릿 + AI 커스터마이징 방식 적용
   - 영향도: High - 사용자 만족도 직결

3. **메모리 사용량 폭증**
   - 리스크: 9개 Agent 동시 실행시 메모리 부족
   - 대응: Agent 순차 실행 + 메모리 풀 관리
   - 영향도: Medium - EC2 인스턴스 크기 증가

### ⚡ Technical Blockers

1. **프레임워크 의존성 미해결**
   - Agno Framework, AWS Agent Squad 미통합 상태
   - 임시 대응: 기본 Python Agent 먼저 완성 후 점진적 통합

2. **AWS 권한 설정 복잡성**
   - Lambda, S3, Secrets Manager 등 다중 서비스 권한
   - 대응: IAM 역할 템플릿 사전 준비

3. **대용량 파일 처리**
   - 생성된 프로젝트가 클 경우 메모리/네트워크 이슈
   - 대응: 스트리밍 압축 및 청크 업로드

## 🎯 MVP 성공 기준

### ✅ Functional Requirements (기능적 요구사항)

#### 핵심 사용자 플로우
- [ ] 사용자가 "블로그 만들어줘" 입력
- [ ] 30초 이내에 완전한 React 프로젝트 생성
- [ ] ZIP 파일 다운로드 가능
- [ ] 다운로드한 프로젝트가 `npm install && npm start`로 실행됨

#### 9-Agent Pipeline 동작
- [ ] 모든 9개 Agent가 실제 로직으로 실행
- [ ] 각 Agent별 진행상황 실시간 표시
- [ ] Agent간 데이터 전달 정상 작동

#### 지원 프로젝트 타입
- [ ] React 기본 웹 애플리케이션
- [ ] Vue.js 기본 웹 애플리케이션
- [ ] Next.js 기본 웹 애플리케이션
- [ ] Todo 앱, 블로그, 대시보드 기본 템플릿

### 📊 Performance Requirements (성능 요구사항)

| 지표 | 목표값 | 현재값 | 상태 |
|------|--------|--------|------|
| 응답 시간 | < 30초 | - | ❌ |
| 동시 사용자 | 10+ | - | ❌ |
| 생성 성공률 | > 95% | - | ❌ |
| ZIP 파일 크기 | < 10MB | - | ❌ |
| Agent 메모리 | < 100MB | - | ❌ |

### 🔒 Quality Requirements (품질 요구사항)

- **생성 코드 품질**: ESLint/Prettier 통과
- **실행 가능성**: 생성된 프로젝트 100% 빌드 성공
- **보안**: 사용자 입력 Sanitization 100%
- **에러 처리**: 모든 실패 케이스 적절한 메시지 제공
- **로깅**: 모든 Agent 실행 로그 CloudWatch 전송

### 🎨 User Experience Requirements (사용자 경험 요구사항)

- **직관적 UI**: 비개발자도 쉽게 사용 가능
- **실시간 피드백**: 각 단계별 진행상황 표시
- **명확한 안내**: 다운로드 후 사용법 가이드 제공
- **에러 대응**: 문제 발생시 이해하기 쉬운 메시지

## 🚀 시작 가이드

### 즉시 시작할 작업

#### 1. Python Agent 브릿지 구현
```bash
# TypeScript에서 Python Agent 호출
cd /home/ec2-user/T-DeveloperMVP/backend/src/agents
# bridge.ts 파일 생성하여 Python subprocess 호출
```

#### 2. Generation Agent 실제 구현
```python
# Mock 데이터 대신 실제 프로젝트 파일 생성
cd /home/ec2-user/T-DeveloperMVP/backend/src/agents/implementations/generation
# 실제 React/Vue 프로젝트 생성 로직 구현
```

#### 3. FastAPI 서버 확장
```python
# simple_api.py를 완전한 서버로 확장
cd /home/ec2-user/T-DeveloperMVP/backend
# Agent 호출 및 실제 파일 생성 통합
```

### 개발 환경 설정
```bash
# 1. Python 환경 설정
cd /home/ec2-user/T-DeveloperMVP/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 프론트엔드 환경 설정
cd /home/ec2-user/T-DeveloperMVP/frontend
npm install
npm run build

# 3. 백엔드 서버 실행
cd /home/ec2-user/T-DeveloperMVP/backend
# TypeScript 서버 (현재)
npm run dev
# 또는 Python 서버 (목표)
python src/simple_api.py
```

### 첫 번째 마일스톤 검증
```bash
# 테스트 시나리오
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Create a simple React todo app"}'

# 예상 결과: 실제 React 프로젝트 ZIP 파일 다운로드 가능
# 다운로드한 파일 압축 해제 후
cd generated-project
npm install
npm start
# → 브라우저에서 Todo 앱이 정상 실행되어야 함
```

## 📅 타임라인

### Week 1 (현재 ~ +7일)
- **목표**: 실제 프로젝트 생성 가능
- **산출물**: React Todo 앱 생성 및 다운로드 가능

### Week 2 (+8일 ~ +14일)
- **목표**: 품질 향상 및 다양한 프로젝트 타입 지원
- **산출물**: React/Vue/Next.js 3가지 프레임워크 지원

### Week 3 (+15일 ~ +21일)
- **목표**: 테스트 완료 및 AWS 배포
- **산출물**: EC2에서 실행되는 MVP 서비스

## 👥 역할 분담

| 역할 | 담당 영역 | 주요 작업 |
|------|-----------|-----------|
| Backend Dev | Agent 통합, API 서버 | Python Agent 통합, FastAPI 개발 |
| Frontend Dev | UI/UX | React UI 개선, WebSocket 연결 |
| DevOps | 인프라, 배포 | AWS 설정, CI/CD 구축 |
| QA | 테스트, 품질 | E2E 테스트, 성능 측정 |

## 📝 일일 체크리스트

### 매일 확인 사항
- [ ] 단위 작업 완료시 즉시 Git 커밋 & 푸시
- [ ] 진행 상황 문서 업데이트
- [ ] 블로커 발생시 즉시 공유
- [ ] 테스트 코드 작성
- [ ] 코드 리뷰 요청

### 주간 마일스톤
- [ ] 월요일: 주간 목표 설정
- [ ] 수요일: 중간 점검
- [ ] 금요일: 주간 회고 및 다음 주 계획

## 🎉 성공 지표

### MVP 완성 기준
1. **실제 작동**: Mock 없이 실제 프로젝트 생성
2. **품질 보장**: 생성된 프로젝트 100% 실행 가능
3. **성능 달성**: 30초 이내 생성 완료
4. **사용자 만족**: 직관적 UI와 명확한 피드백

---

**이 작업지시서는 T-Developer MVP의 실제 작동하는 제품 완성을 위한 구체적이고 실행 가능한 로드맵입니다.**

**모든 작업은 "Production-Ready" 원칙을 따라 Mock 없이 실제 동작하는 코드로 구현되어야 합니다.**

**문서 작성일: 2025-08-08**
**다음 업데이트: Week 1 완료 후**