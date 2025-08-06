# uv 개발자 가이드

## 🚀 시작하기

### uv 설치
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```

### 기본 사용법

#### 가상환경 생성
```bash
# 기본 가상환경
uv venv

# Python 버전 지정
uv venv --python python3.11

# 특정 경로
uv venv .venv-project
```

#### 패키지 설치
```bash
# requirements.txt 설치
uv pip install -r requirements.txt

# 단일 패키지
uv pip install requests

# 개발 의존성
uv pip install -e ".[dev]"
```

## ⚡ 성능 비교

| 도구 | 설치 시간 | 속도 향상 |
|------|-----------|-----------|
| pip  | 14.97초   | 1x        |
| uv   | 0.14초    | **107x**  |

## 🔧 마이그레이션 가이드

### 1. 기존 환경 백업
```bash
pip freeze > backup-requirements.txt
```

### 2. uv 환경 생성
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. 스크립트 업데이트
```bash
# 이전
pip install -r requirements.txt

# 이후  
uv pip install -r requirements.txt
```

## 📋 체크리스트

- [ ] uv 설치 완료
- [ ] 가상환경 재생성
- [ ] requirements.txt 호환성 확인
- [ ] 개발 스크립트 업데이트
- [ ] CI/CD 파이프라인 수정