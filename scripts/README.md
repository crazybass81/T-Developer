# T-Developer Scripts

## 📁 디렉토리 구조

```
scripts/
├── aws/                    # AWS 환경변수 관리
├── code-generator/         # 코드 생성 템플릿
└── *.sh, *.py             # 유틸리티 스크립트
```

## 🔧 스크립트 목록

### AWS 관리 (`aws/`)
| 스크립트 | 설명 |
|----------|------|
| `setup-parameters.sh` | Parameter Store에 일반 설정 저장 |
| `setup-secrets.sh` | Secrets Manager에 민감 정보 저장 |
| `add-missing-parameters.sh` | 누락된 파라미터 추가 |
| `update-ai-keys.sh` | AI API 키 업데이트 |

### 환경 설정
| 스크립트 | 설명 |
|----------|------|
| `check-requirements.sh` | 개발 환경 요구사항 확인 |
| `install-backend-deps.sh` | 백엔드 의존성 설치 |
| `install-python-deps.sh` | Python 패키지 설치 |
| `install-global-tools.sh` | 전역 개발 도구 설치 |
| `install-agno.sh` | Agno 모니터링 도구 설치 |
| `install-tracing-deps.sh` | 트레이싱 의존성 설치 |

### 개발 환경
| 스크립트 | 설명 |
|----------|------|
| `start-dev-env.sh` | 개발 환경 시작 (Docker 포함) |
| `stop-dev-env.sh` | 개발 환경 종료 |
| `start-monitoring.sh` | 모니터링 서비스 시작 |

### AWS 리소스
| 스크립트 | 설명 |
|----------|------|
| `create-s3-buckets.py` | S3 버킷 생성 |
| `create-lambda-layers.sh` | Lambda 레이어 생성 |
| `create-cloudwatch-dashboard.py` | CloudWatch 대시보드 생성 |
| `setup-aws-profile.py` | AWS 프로필 설정 |

### 테스트
| 스크립트 | 설명 |
|----------|------|
| `run-tests.sh` | 전체 테스트 실행 |
| `run-e2e-tests.sh` | E2E 테스트 실행 |
| `run-phase1-validation.py` | Phase 1 검증 |
| `test-agno-performance.py` | Agno 성능 테스트 |
| `test_uv_compatibility.py` | UV 호환성 테스트 |

### 보안 & 유틸리티
| 스크립트 | 설명 |
|----------|------|
| `generate-ssl-certs.sh` | SSL 인증서 생성 |
| `setup-git-hooks.sh` | Git 훅 설정 |
| `health-check.sh` | 헬스 체크 |
| `docker-health-check.sh` | Docker 컨테이너 헬스 체크 |

### 기타
| 스크립트 | 설명 |
|----------|------|
| `init-repository.sh` | Git 저장소 초기화 |
| `setup-python-env.py` | Python 가상환경 설정 |

## 🚀 사용 예시

### 1. 초기 환경 설정
```bash
# 요구사항 확인
./check-requirements.sh

# 의존성 설치
./install-backend-deps.sh
./install-python-deps.sh
```

### 2. AWS 환경변수 설정
```bash
# Parameter Store 설정
./aws/setup-parameters.sh development

# Secrets Manager 설정
./aws/setup-secrets.sh development
```

### 3. 개발 환경 실행
```bash
# 개발 환경 시작
./start-dev-env.sh

# 개발 환경 종료
./stop-dev-env.sh
```

### 4. 테스트 실행
```bash
# 모든 테스트
./run-tests.sh

# E2E 테스트만
./run-e2e-tests.sh
```

## 📝 정리된 내용

### 삭제된 스크립트 (100개+)
- `test-*.js` 파일들 (개별 기능 테스트)
- `phase*.sh` 파일들 (임시 phase 관련)
- `*-simple.js` 파일들 (중복 버전)
- `*-final.js` 파일들 (중복 버전)
- `demo-*.js` 파일들 (데모용)
- `verify-*.js` 파일들 (검증용)
- 중복된 `.js`/`.ts` 버전들

### 유지된 스크립트
- 환경 설정 관련 필수 스크립트
- AWS 리소스 관리 스크립트
- 개발 환경 관리 스크립트
- 테스트 실행 스크립트

## 🔒 보안 주의사항

- AWS 자격 증명은 환경변수로 설정
- 민감한 정보는 Secrets Manager 사용
- 로컬에 .env 파일 저장 금지