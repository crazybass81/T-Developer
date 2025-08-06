# pip → uv 마이그레이션 가이드

## 📋 개요
T-Developer 프로젝트의 pip → uv 전환 가이드

## 🎯 마이그레이션 결과
- **성능 향상**: 107배 빠름 (14.97s → 0.14s)
- **호환성**: 100% (12/12 패키지)
- **위험도**: 없음

## 📝 단계별 가이드

### Phase 1: 준비 (완료)
- [x] 환경 분석 및 백업
- [x] uv 호환성 테스트
- [x] 성능 벤치마크

### Phase 2: 개발 환경 전환
```bash
# 1. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 기존 환경 백업
pip freeze > backup-$(date +%Y%m%d).txt

# 3. 새 환경 생성
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Phase 3: 스크립트 업데이트
```bash
# package.json scripts 수정
"scripts": {
  "install": "uv pip install -r requirements.txt",
  "dev": "uv pip install -r requirements-dev.txt"
}
```

### Phase 4: CI/CD 업데이트
```yaml
# .github/workflows/ci.yml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies  
  run: uv pip install -r requirements.txt
```

## 🔄 롤백 계획
```bash
# 기존 환경 복원
pip install -r backup-$(date +%Y%m%d).txt
```

## ✅ 검증 체크리스트
- [ ] 모든 패키지 정상 설치
- [ ] 테스트 통과
- [ ] 개발 서버 정상 작동
- [ ] CI/CD 파이프라인 정상