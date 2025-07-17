# T-Developer 프론트엔드

T-Developer 시스템의 프론트엔드 애플리케이션입니다.

## 기능

- 프로젝트 생성 및 설정
- 자연어로 기능 요청 입력
- 작업 진행 상황 실시간 모니터링
- 코드 변경사항 및 테스트 결과 확인

## 시작하기

### 필수 조건

- Node.js 14.x 이상
- npm 6.x 이상

### 설치

```bash
# 의존성 설치
npm install
```

### 개발 서버 실행

```bash
npm start
```

브라우저에서 [http://localhost:3000](http://localhost:3000)으로 접속하여 애플리케이션을 확인할 수 있습니다.

### 빌드

```bash
npm run build
```

빌드된 파일은 `build` 디렉토리에 생성됩니다.

## 프로젝트 구조

- `src/components`: 재사용 가능한 UI 컴포넌트
- `src/pages`: 페이지 컴포넌트
- `src/styles`: CSS 스타일 파일
- `public`: 정적 파일

## 백엔드 연동

프론트엔드는 T-Developer 백엔드 API와 통신합니다. 기본적으로 `http://localhost:8000`에 연결되도록 설정되어 있습니다. 다른 주소를 사용하려면 `package.json`의 `proxy` 설정을 변경하세요.