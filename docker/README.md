# Docker 구조 가이드

T-Developer MVP 프로젝트의 Docker 구조입니다.

## 📁 폴더 구조

```
docker/
├── backend/
│   ├── Dockerfile              # Development build
│   ├── Dockerfile.production   # Production multi-stage build
│   └── Dockerfile.local        # Local testing
├── frontend/
│   └── Dockerfile              # Frontend React build
├── compose/
│   ├── ecs.yml                 # ECS production setup (agent groups)
│   ├── monitoring.yml          # Monitoring stack (Grafana, Prometheus)
│   └── tracing.yml            # Tracing stack (Jaeger, OpenTelemetry)
├── prometheus/
│   └── prometheus.yml          # Prometheus configuration
├── redis/                      # Redis 데이터
└── otel-collector-config.yaml # OpenTelemetry collector config
```

## 🚀 사용법

### 개발 환경 시작 (기본)
```bash
# 루트 디렉토리에서 실행
docker-compose up -d

# 포트:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
# - DynamoDB: localhost:8001
# - DynamoDB Admin: localhost:8002
# - Redis: localhost:6379
# - Elasticsearch: localhost:9200
# - LocalStack: localhost:4566
```

### ECS 프로덕션 환경
```bash
# Agent 그룹별 서비스 실행
docker-compose -f docker/compose/ecs.yml up -d

# 서비스 그룹:
# - Analysis Service: NL Input, UI Selection, Parser
# - Decision Service: Component Decision, Match Rate, Search
# - Generation Service: Generation, Assembly, Download
# - Orchestrator: API Gateway
```

### 모니터링 스택 추가
```bash
# Prometheus, Grafana, StatsD
docker-compose -f docker-compose.yml -f docker/compose/monitoring.yml up -d

# 포트:
# - Grafana: localhost:3001
# - Prometheus: localhost:9090
# - StatsD: localhost:8125
```

### 트레이싱 스택 추가
```bash
# Jaeger, OpenTelemetry
docker-compose -f docker-compose.yml -f docker/compose/tracing.yml up -d

# 포트:
# - Jaeger UI: localhost:16686
# - OTLP gRPC: localhost:4317
# - OTLP HTTP: localhost:4318
```

### 전체 스택 (개발 + 모니터링 + 트레이싱)
```bash
docker-compose \
  -f docker-compose.yml \
  -f docker/compose/monitoring.yml \
  -f docker/compose/tracing.yml \
  up -d
```

## 🔧 개별 서비스 빌드

### Backend만 빌드
```bash
docker build -f docker/backend/Dockerfile -t t-developer-backend .
```

### Frontend만 빌드
```bash
docker build -f docker/frontend/Dockerfile -t t-developer-frontend .
```

## 📊 서비스 포트 매핑

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Backend API | 8000 | Python FastAPI 서버 |
| Frontend | 3000 | React 개발 서버 |
| PostgreSQL | 5432 | 메인 데이터베이스 |
| DynamoDB | 8001 | AWS DynamoDB 로컬 |
| DynamoDB Admin | 8002 | DynamoDB 관리 UI |
| Redis | 6379 | 캐시 및 세션 저장소 |
| Elasticsearch | 9200 | 컴포넌트 검색 엔진 |
| LocalStack | 4566 | AWS 서비스 모킹 |
| Grafana | 3001 | 모니터링 대시보드 |
| Prometheus | 9090 | 메트릭 수집 |
| Kibana | 5601 | 로그 분석 UI |
| Jaeger | 16686 | 분산 추적 UI |

## 🐛 트러블슈팅

### 포트 충돌 해결
```bash
# 사용 중인 포트 확인
lsof -i :8000

# 모든 컨테이너 중지
docker-compose down

# 특정 포트 서비스만 변경하여 시작
docker-compose up -d postgres redis dynamodb
```

### 데이터 초기화
```bash
# 볼륨 포함 완전 삭제
docker-compose down -v

# 이미지까지 삭제
docker-compose down --rmi all -v
```

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
```

## 🏗️ 개발 팁

### 코드 변경 시 자동 재빌드
- Backend: 볼륨 마운트로 핫 리로드 지원
- Frontend: React 개발 서버의 HMR 활용

### 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# Docker Compose에서 환경변수 사용
REDIS_PASSWORD=mypassword docker-compose up -d
```

## 📝 주의사항

1. **포트 충돌**: DynamoDB는 기본 8000 포트 대신 8001 사용
2. **볼륨 권한**: Linux에서 권한 문제 발생 시 `sudo chown -R $USER:$USER docker/`
3. **메모리 사용량**: Elasticsearch는 메모리를 많이 사용하므로 개발 시 필요에 따라 제외
4. **AWS 자격증명**: LocalStack 사용 시 가짜 키 사용 가능

## 🔍 헬스체크

모든 주요 서비스에 헬스체크가 구성되어 있습니다:

```bash
# 서비스 상태 확인
docker-compose ps

# 헬스체크 상세 정보
docker inspect --format='{{json .State.Health}}' <container_name>
```