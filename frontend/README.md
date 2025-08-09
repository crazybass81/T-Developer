# T-Developer MVP Frontend

T-Developer는 자연어로 웹 애플리케이션을 생성하는 차세대 AI 개발 플랫폼입니다. 9개의 전문 AI 에이전트가 협업하여 완전한 프로덕션 코드를 생성합니다.

## 🚀 주요 기능

- **자연어 기반 개발**: 복잡한 코딩 없이 자연어 대화만으로 앱 생성
- **AI 에이전트 시스템**: 9개의 전문 에이전트가 순차적으로 협업
- **실시간 모니터링**: WebSocket을 통한 실시간 진행 상황 추적  
- **프로덕션 품질**: 실제 서비스에 바로 배포 가능한 고품질 코드
- **다크 모드**: 완전한 다크/라이트 모드 지원
- **반응형 디자인**: 모바일부터 데스크톱까지 최적화된 UI

## 🛠 기술 스택

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Real-time**: WebSocket
- **Animation**: Framer Motion
- **UI Components**: Radix UI
- **Icons**: Lucide React

## 🚦 시작하기

### 설치 및 실행

1. 의존성 설치
```bash
npm install
```

2. 개발 서버 실행
```bash
npm run dev
```

3. 브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

### 환경 변수

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 📱 주요 페이지

- **랜딩 페이지** (`/`): 플랫폼 소개 및 데모
- **프로젝트 생성** (`/create`): 3단계 프로젝트 생성 마법사
- **프로젝트 목록** (`/projects`): 모든 프로젝트 관리
- **파이프라인 모니터링** (`/pipeline`): 실시간 AI 에이전트 추적
- **대시보드** (`/dashboard`): 통계 및 현황 확인

**T-Developer**로 AI와 함께 더 빠르고 스마트한 개발 경험을 시작하세요! 🚀