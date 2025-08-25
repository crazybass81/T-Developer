# 🎨 T-Developer Frontend

T-Developer의 웹 인터페이스 (Streamlit 기반)

## 📂 파일 구조

- **app.py** - 기본 UI (직접 오케스트레이터 import)
- **aws_app.py** - AWS Agent Squad UI (직접 import)
- **api_app.py** - API 클라이언트 UI (백엔드 API 연동) ⭐

## 🚀 실행 방법

### API 연동 버전 (권장)
```bash
# 1. 백엔드 API 서버 실행
python3 -m uvicorn backend.api.upgrade_api:app --port 8000 --reload

# 2. 프론트엔드 실행
streamlit run frontend/api_app.py --server.port 8503
```

### 직접 실행 버전
```bash
# 기본 UI
streamlit run frontend/app.py

# AWS 버전
streamlit run frontend/aws_app.py
```

## 🔗 접속 URL

- **API 연동 UI**: http://localhost:8503 (권장)
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 💡 특징

### api_app.py (권장)
- ✅ 백엔드 API와 통신
- ✅ 비동기 처리로 타임아웃 방지
- ✅ 실시간 진행 상황 표시
- ✅ UpgradeOrchestrator & NewBuilderOrchestrator 지원

### app.py
- 직접 오케스트레이터 import
- 간단한 테스트용
- UpgradeOrchestrator만 지원

### aws_app.py
- AWS Agent Squad 프레임워크 UI
- 페르소나 정보 표시
- Evolution Loop 모니터링

## 📝 참고

- 기존 `ui/` 폴더를 `frontend/`로 이름 변경
- 모든 프론트엔드 파일은 `frontend/` 폴더에 통합
- API 연동 버전(api_app.py) 사용 권장