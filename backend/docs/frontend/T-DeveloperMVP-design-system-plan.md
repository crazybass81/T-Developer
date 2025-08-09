# T-Developer MVP 종합 디자인 계획서

## 1. 디자인 컨셉 및 철학

### 브랜드 아이덴티티
**"Simplicity Meets Intelligence"** - 복잡한 AI 기술을 직관적인 인터페이스로 전달

- **핵심 가치**: 접근성, 투명성, 협업, 혁신
- **비주얼 메타포**: 9개의 에이전트가 하나의 오케스트라처럼 조화롭게 작동
- **톤 앤 매너**: 전문적이면서도 친근한, 기술적이지만 인간적인

### 디자인 원칙 (Design Principles)

1. **Progressive Disclosure**: 복잡성을 단계적으로 노출
   - 초보자는 간단한 채팅 인터페이스만 보임
   - 고급 사용자는 에이전트 파이프라인 제어 가능

2. **Real-time Feedback**: 모든 상호작용에 즉각적 피드백
   - AI 처리 과정의 실시간 시각화
   - 스트리밍 응답으로 체감 속도 향상

3. **Visual-First Approach**: 코드보다 비주얼 우선
   - 드래그 앤 드롭 인터페이스
   - 노드 기반 워크플로우 편집기

4. **Accessibility by Default**: 접근성 기본 탑재
   - WCAG 2.1 AA 준수
   - 키보드 네비게이션 완벽 지원

### 타겟 사용자 경험 목표

- **신규 사용자**: 5분 내 첫 앱 생성
- **일반 사용자**: 자연어만으로 복잡한 앱 구축
- **파워 사용자**: 에이전트 커스터마이징 및 최적화

## 2. 컬러 시스템

### 모노톤 팔레트 (그레이 스케일)
```css
:root {
  /* Neutral Scale - 11단계 그레이 */
  --gray-50: #FAFAFA;
  --gray-100: #F5F5F5;
  --gray-200: #E5E5E5;
  --gray-300: #D4D4D4;
  --gray-400: #A3A3A3;
  --gray-500: #737373;
  --gray-600: #525252;
  --gray-700: #404040;
  --gray-800: #262626;
  --gray-900: #171717;
  --gray-950: #0A0A0A;
}
```

### 포인트 컬러
```css
:root {
  /* Primary - Electric Blue */
  --primary-50: #EFF6FF;
  --primary-100: #DBEAFE;
  --primary-200: #BFDBFE;
  --primary-300: #93C5FD;
  --primary-400: #60A5FA;
  --primary-500: #3B82F6; /* Main */
  --primary-600: #2563EB;
  --primary-700: #1D4ED8;
  --primary-800: #1E40AF;
  --primary-900: #1E3A8A;
  
  /* Secondary - Purple Accent */
  --secondary-50: #FAF5FF;
  --secondary-100: #F3E8FF;
  --secondary-200: #E9D5FF;
  --secondary-300: #D8B4FE;
  --secondary-400: #C084FC;
  --secondary-500: #A855F7; /* Main */
  --secondary-600: #9333EA;
  --secondary-700: #7E22CE;
  --secondary-800: #6B21A8;
  --secondary-900: #581C87;
}
```

### 시맨틱 컬러
```css
:root {
  /* Semantic Colors */
  --color-success: #10B981;
  --color-success-light: #D1FAE5;
  --color-success-dark: #065F46;
  
  --color-warning: #F59E0B;
  --color-warning-light: #FEF3C7;
  --color-warning-dark: #92400E;
  
  --color-error: #EF4444;
  --color-error-light: #FEE2E2;
  --color-error-dark: #991B1B;
  
  --color-info: #3B82F6;
  --color-info-light: #DBEAFE;
  --color-info-dark: #1E40AF;
}
```

### 다크모드/라이트모드 대응
```css
/* Light Mode (Default) */
:root {
  --bg-primary: var(--gray-50);
  --bg-secondary: white;
  --bg-tertiary: var(--gray-100);
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-tertiary: var(--gray-500);
  --border-default: var(--gray-200);
  --border-hover: var(--gray-300);
}

/* Dark Mode */
[data-theme="dark"] {
  --bg-primary: var(--gray-900);
  --bg-secondary: var(--gray-950);
  --bg-tertiary: var(--gray-800);
  --text-primary: var(--gray-100);
  --text-secondary: var(--gray-400);
  --text-tertiary: var(--gray-500);
  --border-default: var(--gray-800);
  --border-hover: var(--gray-700);
  
  /* 다크모드용 채도 조정 */
  --primary-500: #5B8DEF;
  --secondary-500: #B77FF8;
}
```

## 3. 타이포그래피 시스템

### 폰트 선택 및 이유
```css
:root {
  /* Primary Font - Inter: 가독성과 현대성 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  /* Code Font - JetBrains Mono: 코드 가독성 최적화 */
  --font-mono: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
  
  /* Display Font - Outfit: 헤드라인용 기하학적 폰트 */
  --font-display: 'Outfit', var(--font-sans);
}
```

### 타입 스케일
```css
:root {
  /* Type Scale - 1.25 (Major Third) */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */
  --text-6xl: 3.75rem;   /* 60px */
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

### 행간, 자간 규칙
```css
:root {
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
  
  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}

/* Typography Classes */
.heading-1 {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw + 1rem, 3rem);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.body-text {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  letter-spacing: var(--tracking-normal);
}

.code-block {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  letter-spacing: var(--tracking-normal);
}
```

## 4. 그리드 및 레이아웃 시스템

### 8px 그리드 시스템
```css
:root {
  /* Base Unit */
  --grid-unit: 8px;
  
  /* Spacing Scale */
  --space-0: 0;
  --space-1: calc(var(--grid-unit) * 0.5);   /* 4px */
  --space-2: calc(var(--grid-unit) * 1);     /* 8px */
  --space-3: calc(var(--grid-unit) * 1.5);   /* 12px */
  --space-4: calc(var(--grid-unit) * 2);     /* 16px */
  --space-5: calc(var(--grid-unit) * 2.5);   /* 20px */
  --space-6: calc(var(--grid-unit) * 3);     /* 24px */
  --space-8: calc(var(--grid-unit) * 4);     /* 32px */
  --space-10: calc(var(--grid-unit) * 5);    /* 40px */
  --space-12: calc(var(--grid-unit) * 6);    /* 48px */
  --space-16: calc(var(--grid-unit) * 8);    /* 64px */
  --space-20: calc(var(--grid-unit) * 10);   /* 80px */
  --space-24: calc(var(--grid-unit) * 12);   /* 96px */
}
```

### 반응형 브레이크포인트
```css
:root {
  --bp-xs: 320px;   /* Mobile Small */
  --bp-sm: 480px;   /* Mobile Large */
  --bp-md: 768px;   /* Tablet */
  --bp-lg: 1024px;  /* Desktop Small */
  --bp-xl: 1280px;  /* Desktop */
  --bp-2xl: 1536px; /* Desktop Large */
  --bp-3xl: 1920px; /* Desktop Ultra */
}

/* Container Widths */
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

@media (min-width: 768px) {
  .container { max-width: 768px; padding: 0 var(--space-6); }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; padding: 0 var(--space-8); }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}

@media (min-width: 1536px) {
  .container { max-width: 1440px; }
}
```

### 컨테이너 및 여백 규칙
```css
/* Layout Grid */
.layout-grid {
  display: grid;
  gap: var(--space-6);
  grid-template-columns: repeat(12, 1fr);
}

/* Sidebar Layout */
.layout-sidebar {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  min-height: 100vh;
}

/* Content Spacing */
.content-section {
  padding-block: var(--space-12);
}

.card-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}
```

## 5. 컴포넌트 디자인 시스템

### 버튼 스타일
```css
/* Base Button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  border-radius: 6px;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  white-space: nowrap;
}

/* Primary Button */
.btn-primary {
  background: var(--primary-500);
  color: white;
  border: 1px solid var(--primary-500);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-primary:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.btn-primary:active {
  transform: translateY(0);
}

/* Secondary Button */
.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-hover);
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.btn-ghost:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* Danger Button */
.btn-danger {
  background: var(--color-error);
  color: white;
  border: 1px solid var(--color-error);
}

.btn-danger:hover {
  background: var(--color-error-dark);
}

/* Button Sizes */
.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
}
```

### 입력 필드 디자인
```css
/* Input Field */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  transition: all 150ms ease-out;
}

.input:hover {
  border-color: var(--border-hover);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Input with Label */
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

/* Textarea */
.textarea {
  min-height: 120px;
  resize: vertical;
}

/* Input States */
.input-error {
  border-color: var(--color-error);
}

.input-success {
  border-color: var(--color-success);
}
```

### 카드 컴포넌트
```css
/* Card Base */
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: var(--space-6);
  transition: all 200ms ease-out;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-200);
}

/* Card Variants */
.card-elevated {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-bordered {
  box-shadow: none;
  border-width: 2px;
}

/* Card Sections */
.card-header {
  margin: calc(var(--space-6) * -1);
  margin-bottom: var(--space-6);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-default);
}

.card-footer {
  margin: calc(var(--space-6) * -1);
  margin-top: var(--space-6);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-default);
  background: var(--bg-tertiary);
}
```

### 모달 및 오버레이
```css
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 200ms ease-out;
}

/* Modal Content */
.modal {
  background: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 560px;
  width: 90%;
  max-height: 85vh;
  overflow: auto;
  animation: slideUp 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-default);
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--border-default);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 네비게이션 패턴
```css
/* Sidebar Navigation */
.nav-sidebar {
  width: 280px;
  height: 100vh;
  background: var(--bg-tertiary);
  border-right: 1px solid var(--border-default);
  padding: var(--space-4);
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: 6px;
  color: var(--text-secondary);
  transition: all 150ms ease-out;
  cursor: pointer;
}

.nav-item:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary-100);
  color: var(--primary-700);
}

/* Top Navigation Bar */
.nav-top {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
  justify-content: space-between;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.breadcrumb-separator {
  color: var(--text-tertiary);
}
```

## 6. 아이콘 및 일러스트레이션

### 아이콘 스타일 가이드
```css
/* Icon System */
.icon {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-sm { width: 16px; height: 16px; }
.icon-lg { width: 24px; height: 24px; }
.icon-xl { width: 32px; height: 32px; }

/* Icon Style: Outline (Default) */
.icon svg {
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

/* Icon Animation */
.icon-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### AI 에이전트 시각화 방식
```css
/* Agent Avatar */
.agent-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  position: relative;
}

/* Agent Colors - 9개 에이전트별 고유 컬러 */
.agent-1 { background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); }
.agent-2 { background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%); }
.agent-3 { background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%); }
.agent-4 { background: linear-gradient(135deg, #43E97B 0%, #38F9D7 100%); }
.agent-5 { background: linear-gradient(135deg, #FA709A 0%, #FEE140 100%); }
.agent-6 { background: linear-gradient(135deg, #30CFD0 0%, #330867 100%); }
.agent-7 { background: linear-gradient(135deg, #A8EDEA 0%, #FED6E3 100%); }
.agent-8 { background: linear-gradient(135deg, #FD6585 0%, #0D25B9 100%); }
.agent-9 { background: linear-gradient(135deg, #FFC837 0%, #FF6F3C 100%); }

/* Agent Status Indicator */
.agent-status {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--bg-secondary);
}

.agent-status.active {
  background: var(--color-success);
  animation: pulse 2s infinite;
}

.agent-status.processing {
  background: var(--color-warning);
  animation: pulse 1s infinite;
}

.agent-status.error {
  background: var(--color-error);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

### 일러스트레이션 스타일
```css
/* Empty State Illustration */
.illustration-empty {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  opacity: 0.5;
  filter: grayscale(100%);
}

/* Success Illustration */
.illustration-success {
  color: var(--color-success);
  animation: scaleIn 400ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
```

## 7. 모션 및 인터랙션

### 마이크로 인터랙션
```css
/* Interaction Timings */
:root {
  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 800ms;
  
  /* Easing Functions */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* Hover Effects */
.interactive {
  transition: all var(--duration-fast) var(--ease-out);
}

.interactive:hover {
  transform: translateY(-2px);
}

.interactive:active {
  transform: translateY(0);
  transition-duration: var(--duration-instant);
}

/* Click Ripple Effect */
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transform: translate(-50%, -50%);
  transition: width var(--duration-normal), height var(--duration-normal);
}

.ripple:active::before {
  width: 300px;
  height: 300px;
}
```

### 페이지 전환 효과
```css
/* Page Transitions */
.page-enter {
  opacity: 0;
  transform: translateX(20px);
}

.page-enter-active {
  opacity: 1;
  transform: translateX(0);
  transition: all var(--duration-normal) var(--ease-out);
}

.page-exit {
  opacity: 1;
  transform: translateX(0);
}

.page-exit-active {
  opacity: 0;
  transform: translateX(-20px);
  transition: all var(--duration-normal) var(--ease-in);
}

/* Fade Transition */
.fade-enter {
  opacity: 0;
}

.fade-enter-active {
  opacity: 1;
  transition: opacity var(--duration-normal) var(--ease-out);
}
```

### 로딩 및 프로그레스 표시
```css
/* Loading Spinner */
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--primary-500);
  border-radius: 50%;
  animation: spin var(--duration-slower) linear infinite;
}

/* Progress Bar */
.progress {
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: var(--primary-500);
  border-radius: 2px;
  transition: width var(--duration-normal) var(--ease-out);
}

/* Indeterminate Progress */
.progress-indeterminate .progress-bar {
  width: 30%;
  animation: indeterminate 1.5s linear infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

/* Skeleton Loading */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### 호버/클릭 피드백
```css
/* Button Press Effect */
.btn-press {
  transform-style: preserve-3d;
  transition: transform var(--duration-fast) var(--ease-out);
}

.btn-press:active {
  transform: translateY(2px) scale(0.98);
}

/* Card Hover Lift */
.card-lift {
  transition: all var(--duration-normal) var(--ease-out);
}

.card-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Focus Glow */
.focus-glow:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
  animation: glow var(--duration-slow) ease-in-out;
}

@keyframes glow {
  from { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
  to { box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5); }
}
```

## 8. 특수 UI 요소 (T-Developer 특화)

### AI 에이전트 파이프라인 시각화
```css
/* Pipeline Container */
.pipeline-container {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: var(--space-6);
  min-height: 400px;
  position: relative;
}

/* Pipeline Node */
.pipeline-node {
  width: 120px;
  height: 80px;
  background: var(--bg-secondary);
  border: 2px solid var(--border-default);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: absolute;
  cursor: move;
  transition: all var(--duration-fast) var(--ease-out);
}

.pipeline-node:hover {
  border-color: var(--primary-500);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.pipeline-node.active {
  background: var(--primary-100);
  border-color: var(--primary-500);
}

.pipeline-node.processing::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 10px;
  padding: 2px;
  background: linear-gradient(45deg, var(--primary-500), var(--secondary-500));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: exclude;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Pipeline Connection */
.pipeline-connection {
  stroke: var(--gray-400);
  stroke-width: 2;
  fill: none;
  stroke-dasharray: 5, 5;
  animation: dash 20s linear infinite;
}

@keyframes dash {
  to { stroke-dashoffset: -100; }
}

.pipeline-connection.active {
  stroke: var(--primary-500);
  stroke-width: 3;
  stroke-dasharray: none;
}
```

### 자연어 채팅 인터페이스
```css
/* Chat Container */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Message Bubble */
.message {
  max-width: 70%;
  animation: messageSlide var(--duration-normal) var(--ease-out);
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  align-self: flex-end;
  background: var(--primary-500);
  color: white;
  padding: var(--space-3) var(--space-4);
  border-radius: 18px 18px 4px 18px;
}

.message-ai {
  align-self: flex-start;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: var(--space-3) var(--space-4);
  border-radius: 18px 18px 18px 4px;
}

/* Chat Input */
.chat-input-container {
  padding: var(--space-4);
  border-top: 1px solid var(--border-default);
  background: var(--bg-primary);
}

.chat-input {
  display: flex;
  gap: var(--space-2);
}

.chat-input-field {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 24px;
  resize: none;
  min-height: 48px;
  max-height: 120px;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--space-3);
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: var(--gray-400);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}
```

### 코드 생성 진행상황 표시
```css
/* Code Generation Progress */
.code-generation {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: var(--space-4);
}

.code-generation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.code-generation-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.code-generation-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.generation-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-200);
  color: var(--gray-500);
  transition: all var(--duration-normal) var(--ease-out);
}

.step-icon.completed {
  background: var(--color-success);
  color: white;
}

.step-icon.active {
  background: var(--primary-500);
  color: white;
  animation: pulse 2s infinite;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.step-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* Code Preview */
.code-preview {
  margin-top: var(--space-4);
  background: var(--gray-950);
  border-radius: 6px;
  padding: var(--space-4);
  overflow-x: auto;
}

.code-preview pre {
  margin: 0;
  color: var(--gray-100);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

/* Line Numbers */
.code-line {
  display: flex;
  gap: var(--space-3);
}

.line-number {
  color: var(--gray-600);
  user-select: none;
  min-width: 40px;
  text-align: right;
}

.line-content {
  flex: 1;
}

/* Syntax Highlighting (Basic) */
.token-keyword { color: #C678DD; }
.token-string { color: #98C379; }
.token-function { color: #61AFEF; }
.token-comment { color: #5C6370; }
.token-number { color: #D19A66; }
```

### 실시간 프리뷰 영역
```css
/* Preview Container */
.preview-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

/* Preview Header */
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.preview-tabs {
  display: flex;
  gap: var(--space-1);
}

.preview-tab {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.preview-tab:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.preview-tab.active {
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

/* Preview Actions */
.preview-actions {
  display: flex;
  gap: var(--space-2);
}

.preview-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.preview-action:hover {
  background: var(--bg-primary);
}

/* Preview Frame */
.preview-frame {
  width: 100%;
  height: 600px;
  border: none;
  background: white;
}

/* Device Frames */
.device-frame {
  position: relative;
  margin: var(--space-6) auto;
}

.device-frame.mobile {
  width: 375px;
  height: 812px;
  border-radius: 36px;
  padding: 12px;
  background: var(--gray-900);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.device-frame.tablet {
  width: 768px;
  height: 1024px;
  border-radius: 24px;
  padding: 24px;
  background: var(--gray-900);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.device-screen {
  width: 100%;
  height: 100%;
  border-radius: 24px;
  overflow: hidden;
  background: white;
}

/* Responsive Indicators */
.responsive-indicator {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  padding: var(--space-1) var(--space-2);
  background: var(--gray-900);
  color: white;
  font-size: var(--text-xs);
  border-radius: 4px;
  font-family: var(--font-mono);
}
```

## 9. 접근성 고려사항

### WCAG 2.1 AA 준수
```css
/* Focus States */
*:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Skip to Content */
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--primary-500);
  color: white;
  padding: var(--space-2) var(--space-4);
  text-decoration: none;
  border-radius: 0 0 8px 0;
  z-index: 10000;
}

.skip-to-content:focus {
  top: 0;
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  :root {
    --primary-500: #0066CC;
    --color-error: #CC0000;
    --border-default: var(--gray-600);
  }
  
  *:focus-visible {
    outline-width: 3px;
    outline-color: Highlight;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### 컬러 대비율
```css
/* Minimum Contrast Ratios */
:root {
  /* Text on Background - 4.5:1 minimum */
  --contrast-text-primary: var(--gray-900); /* on white: 15.3:1 */
  --contrast-text-secondary: var(--gray-600); /* on white: 4.5:1 */
  
  /* Large Text - 3:1 minimum */
  --contrast-heading: var(--gray-800); /* on white: 10.1:1 */
  
  /* UI Components - 3:1 minimum */
  --contrast-border: var(--gray-300); /* on white: 3.2:1 */
  --contrast-icon: var(--gray-500); /* on white: 5.8:1 */
}

/* Dark Mode Contrast */
[data-theme="dark"] {
  --contrast-text-primary: var(--gray-100); /* on gray-900: 13.1:1 */
  --contrast-text-secondary: var(--gray-400); /* on gray-900: 4.6:1 */
}

/* Error State Contrast */
.error-message {
  color: var(--color-error-dark); /* Ensures 4.5:1 on light backgrounds */
  background: var(--color-error-light);
}
```

### 포커스 상태 디자인
```css
/* Interactive Element Focus */
.interactive-focus {
  position: relative;
}

.interactive-focus::after {
  content: '';
  position: absolute;
  inset: -4px;
  border: 2px solid transparent;
  border-radius: 8px;
  pointer-events: none;
  transition: all var(--duration-fast) var(--ease-out);
}

.interactive-focus:focus-visible::after {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* Focus Trap for Modals */
.focus-trap {
  isolation: isolate;
}

.focus-trap:focus-within {
  z-index: 9999;
}
```

### 키보드 네비게이션
```css
/* Tab Order Indicators */
[tabindex]:not([tabindex="-1"]) {
  position: relative;
}

[tabindex]:not([tabindex="-1"]):focus::before {
  content: attr(tabindex);
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gray-900);
  color: white;
  padding: 2px 6px;
  font-size: 10px;
  border-radius: 4px;
  pointer-events: none;
  opacity: 0;
  animation: showTabIndex var(--duration-fast) forwards;
}

@keyframes showTabIndex {
  to { opacity: 1; }
}

/* Keyboard Shortcuts Display */
.kbd {
  display: inline-block;
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  box-shadow: 0 2px 0 var(--border-default);
}
```

## 10. 디자인 토큰 및 구현

### CSS 변수 정의
```css
/* Design Tokens Root */
:root {
  /* Core Tokens */
  --design-token-version: "1.0.0";
  
  /* Breakpoints */
  --breakpoint-xs: 320px;
  --breakpoint-sm: 480px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  
  /* Z-Index Scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  /* Blur */
  --blur-sm: 4px;
  --blur-md: 8px;
  --blur-lg: 16px;
  --blur-xl: 24px;
}
```

### Tailwind 설정
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        gray: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0A0A0A',
        },
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        secondary: {
          50: '#FAF5FF',
          100: '#F3E8FF',
          200: '#E9D5FF',
          300: '#D8B4FE',
          400: '#C084FC',
          500: '#A855F7',
          600: '#9333EA',
          700: '#7E22CE',
          800: '#6B21A8',
          900: '#581C87',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-up': 'slideUp 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      transitionTimingFunction: {
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
}
```

### 컴포넌트 라이브러리 추천

#### 1. Radix UI (Headless Components)
```bash
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tabs
```

```jsx
// Example: Accessible Dialog
import * as Dialog from '@radix-ui/react-dialog';

const Modal = ({ children, ...props }) => (
  <Dialog.Root {...props}>
    <Dialog.Trigger asChild>
      <button className="btn btn-primary">Open</button>
    </Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="modal-overlay" />
      <Dialog.Content className="modal">
        {children}
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
);
```

#### 2. Framer Motion (Animation)
```bash
npm install framer-motion
```

```jsx
// Example: Animated Component
import { motion } from 'framer-motion';

const AnimatedCard = ({ children }) => (
  <motion.div
    className="card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3, ease: "easeOut" }}
    whileHover={{ y: -4 }}
    whileTap={{ scale: 0.98 }}
  >
    {children}
  </motion.div>
);
```

#### 3. React Flow (Node-based UI)
```bash
npm install reactflow
```

```jsx
// Example: Agent Pipeline Visualization
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap 
} from 'reactflow';

const AgentPipeline = () => {
  const nodes = [
    {
      id: '1',
      type: 'agent',
      data: { label: 'Agent 1' },
      position: { x: 100, y: 100 },
    },
    // ... more nodes
  ];

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
    >
      <Background variant="dots" gap={12} size={1} />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
};
```

---

## 구현 로드맵

### Phase 1: 기초 설정 (Week 1)
- [ ] 컬러 시스템 및 다크모드 구현
- [ ] 타이포그래피 스케일 설정
- [ ] 8-point 그리드 시스템 구축
- [ ] CSS 변수 및 디자인 토큰 설정

### Phase 2: 핵심 컴포넌트 (Week 2)
- [ ] 버튼, 입력 필드, 카드 컴포넌트
- [ ] 네비게이션 시스템
- [ ] 모달 및 오버레이
- [ ] 로딩 및 프로그레스 인디케이터

### Phase 3: T-Developer 특화 UI (Week 3)
- [ ] AI 에이전트 파이프라인 시각화
- [ ] 자연어 채팅 인터페이스
- [ ] 코드 생성 진행상황 표시
- [ ] 실시간 프리뷰 시스템

### Phase 4: 인터랙션 및 최적화 (Week 4)
- [ ] 마이크로 인터랙션 구현
- [ ] 접근성 감사 및 개선
- [ ] 성능 최적화
- [ ] 사용자 테스트 및 피드백 반영

---

이 디자인 시스템은 T-Developer의 핵심 가치인 "복잡한 AI 기술을 누구나 사용할 수 있게"를 구현합니다. 노코드 플랫폼의 직관성과 AI의 강력함을 조화롭게 표현하며, 확장 가능하고 유지보수가 용이한 구조로 설계되었습니다.