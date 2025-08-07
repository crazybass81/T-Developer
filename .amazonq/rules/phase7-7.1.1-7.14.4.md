# Phase 7: 프론트엔드 구현 - Tasks 7.1-7.3 SubTask 구조 및 작업지시서

## 📝 세부 작업지시서

### Task 7.1: React 프로젝트 초기화 및 구조 설정

#### SubTask 7.1.1: Vite 기반 React 프로젝트 생성 및 초기 설정
**담당자**: 프론트엔드 리드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```bash
# 프로젝트 생성
cd /workspace
npm create vite@latest frontend -- --template react-ts
cd frontend

# 핵심 의존성 설치
npm install
```

```json
// frontend/package.json
{
  "name": "t-developer-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,css,md}\"",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "@mui/material": "^5.15.0",
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.13.4",
    "zustand": "^4.4.7",
    "socket.io-client": "^4.7.2",
    "react-hook-form": "^7.48.2",
    "react-error-boundary": "^4.0.11",
    "date-fns": "^3.0.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@types/node": "^20.10.5",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.56.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "prettier": "^3.1.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.10",
    "vitest": "^1.1.0",
    "@vitest/ui": "^1.1.0",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "jsdom": "^23.0.1",
    "msw": "^2.0.11"
  }
}
```

**검증 기준**:
- [ ] Vite 개발 서버 정상 구동
- [ ] React 18 기능 활성화
- [ ] TypeScript 컴파일 성공
- [ ] 기본 페이지 렌더링 확인

#### SubTask 7.1.2: 프로젝트 디렉토리 구조 설계 및 생성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```bash
# frontend/scripts/setup-structure.sh
#!/bin/bash

# 디렉토리 구조 생성
mkdir -p src/{api,assets,components,contexts,hooks,layouts,pages,services,store,styles,types,utils}
mkdir -p src/components/{common,forms,charts,modals,tables}
mkdir -p src/assets/{images,fonts,icons}
mkdir -p src/pages/{Dashboard,Projects,Agents,Workflows,Analytics,Settings}
mkdir -p src/store/{slices,middleware,selectors}
mkdir -p public/{images,fonts}
mkdir -p tests/{unit,integration,e2e}

# 기본 파일 생성
touch src/api/{client,endpoints,interceptors}.ts
touch src/contexts/{AuthContext,ThemeContext,WebSocketContext}.tsx
touch src/hooks/{useAuth,useApi,useWebSocket,useNotification}.ts
touch src/types/{api,models,components,global}.d.ts
touch src/utils/{formatters,validators,helpers,constants}.ts
touch src/styles/{theme,globals,variables,mixins}.css

echo "✅ 프로젝트 구조 생성 완료!"
```

**프로젝트 구조**:
```
frontend/
├── public/
│   ├── fonts/
│   ├── images/
│   └── locales/
├── src/
│   ├── api/                    # API 통신 레이어
│   │   ├── client.ts           # Axios 인스턴스
│   │   ├── endpoints.ts        # API 엔드포인트 정의
│   │   └── interceptors.ts     # 요청/응답 인터셉터
│   ├── assets/                 # 정적 자원
│   │   ├── fonts/
│   │   ├── icons/
│   │   └── images/
│   ├── components/             # 재사용 가능한 컴포넌트
│   │   ├── common/             # 공통 컴포넌트
│   │   ├── forms/              # 폼 컴포넌트
│   │   ├── charts/             # 차트 컴포넌트
│   │   ├── modals/             # 모달 컴포넌트
│   │   └── tables/             # 테이블 컴포넌트
│   ├── contexts/               # React Context
│   │   ├── AuthContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── WebSocketContext.tsx
│   ├── hooks/                  # 커스텀 훅
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useWebSocket.ts
│   ├── layouts/                # 레이아웃 컴포넌트
│   │   ├── MainLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   └── DashboardLayout.tsx
│   ├── pages/                  # 페이지 컴포넌트
│   │   ├── Dashboard/
│   │   ├── Projects/
│   │   ├── Agents/
│   │   ├── Workflows/
│   │   ├── Analytics/
│   │   └── Settings/
│   ├── services/               # 비즈니스 로직 서비스
│   │   ├── authService.ts
│   │   ├── projectService.ts
│   │   └── agentService.ts
│   ├── store/                  # 상태 관리 (Zustand)
│   │   ├── index.ts
│   │   ├── slices/
│   │   ├── middleware/
│   │   └── selectors/
│   ├── styles/                 # 글로벌 스타일
│   │   ├── theme.ts
│   │   ├── globals.css
│   │   └── variables.css
│   ├── types/                  # TypeScript 타입 정의
│   │   ├── api.d.ts
│   │   ├── models.d.ts
│   │   └── global.d.ts
│   ├── utils/                  # 유틸리티 함수
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/                      # 테스트 파일
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── tsconfig.json
├── vite.config.ts
└── package.json
```

**검증 기준**:
- [ ] 모든 디렉토리 생성 확인
- [ ] 기본 파일 생성 확인
- [ ] import 경로 테스트
- [ ] 구조 문서화 완료

#### SubTask 7.1.3: 절대 경로 import 및 별칭(alias) 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 2시간

**작업 내용**:

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@api': path.resolve(__dirname, './src/api'),
      '@assets': path.resolve(__dirname, './src/assets'),
      '@components': path.resolve(__dirname, './src/components'),
      '@contexts': path.resolve(__dirname, './src/contexts'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@layouts': path.resolve(__dirname, './src/layouts'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@styles': path.resolve(__dirname, './src/styles'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    }
  },
  server: {
    port: 3000,
    host: true,
    open: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('@mui')) return 'vendor-mui';
            if (id.includes('react')) return 'vendor-react';
            if (id.includes('lodash')) return 'vendor-lodash';
            return 'vendor';
          }
        }
      }
    }
  }
});
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@api/*": ["src/api/*"],
      "@assets/*": ["src/assets/*"],
      "@components/*": ["src/components/*"],
      "@contexts/*": ["src/contexts/*"],
      "@hooks/*": ["src/hooks/*"],
      "@layouts/*": ["src/layouts/*"],
      "@pages/*": ["src/pages/*"],
      "@services/*": ["src/services/*"],
      "@store/*": ["src/store/*"],
      "@styles/*": ["src/styles/*"],
      "@types/*": ["src/types/*"],
      "@utils/*": ["src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**검증 기준**:
- [ ] 별칭 import 작동 확인
- [ ] TypeScript 경로 매핑 확인
- [ ] IDE 자동완성 지원
- [ ] 빌드 시 경로 해석 성공

#### SubTask 7.1.4: 기본 레이아웃 및 App 컴포넌트 구성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/App.tsx
import React, { Suspense } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ErrorBoundary } from 'react-error-boundary';

import { AuthProvider } from '@contexts/AuthContext';
import { WebSocketProvider } from '@contexts/WebSocketContext';
import { NotificationProvider } from '@contexts/NotificationContext';
import { theme } from '@styles/theme';
import { AppRoutes } from './routes';
import { LoadingScreen } from '@components/common/LoadingScreen';
import { ErrorFallback } from '@components/common/ErrorFallback';

// React Query 클라이언트 설정
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5분
      cacheTime: 10 * 60 * 1000, // 10분
    },
    mutations: {
      retry: 2,
    },
  },
});

function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
              <WebSocketProvider>
                <NotificationProvider>
                  <Suspense fallback={<LoadingScreen />}>
                    <AppRoutes />
                  </Suspense>
                </NotificationProvider>
              </WebSocketProvider>
            </AuthProvider>
          </ThemeProvider>
          {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
        </QueryClientProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
```

```typescript
// frontend/src/routes/index.tsx
import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '@layouts/MainLayout';
import { AuthLayout } from '@layouts/AuthLayout';
import { ProtectedRoute } from './ProtectedRoute';

// Lazy load pages
const Dashboard = lazy(() => import('@pages/Dashboard'));
const Projects = lazy(() => import('@pages/Projects'));
const ProjectDetail = lazy(() => import('@pages/Projects/ProjectDetail'));
const Agents = lazy(() => import('@pages/Agents'));
const Workflows = lazy(() => import('@pages/Workflows'));
const Analytics = lazy(() => import('@pages/Analytics'));
const Settings = lazy(() => import('@pages/Settings'));
const Login = lazy(() => import('@pages/Auth/Login'));
const Register = lazy(() => import('@pages/Auth/Register'));
const NotFound = lazy(() => import('@pages/NotFound'));

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings/*" element={<Settings />} />
        </Route>
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};
```

**검증 기준**:
- [ ] 라우팅 시스템 작동
- [ ] 레이아웃 적용 확인
- [ ] 보호된 라우트 동작
- [ ] 에러 바운더리 테스트

---

### Task 7.2: 빌드 및 개발 환경 구성

#### SubTask 7.2.1: Vite 빌드 최적화 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/vite.config.ts (확장)
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import viteCompression from 'vite-plugin-compression';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      react({
        babel: {
          plugins: [
            ['@babel/plugin-transform-react-jsx', { runtime: 'automatic' }]
          ]
        }
      }),
      
      // GZIP 압축
      viteCompression({
        verbose: true,
        disable: false,
        threshold: 10240,
        algorithm: 'gzip',
        ext: '.gz'
      }),
      
      // PWA 지원
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
        manifest: {
          name: 'T-Developer',
          short_name: 'TDev',
          theme_color: '#2196f3',
          icons: [
            {
              src: '/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: '/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        }
      }),
      
      // 번들 분석 (빌드 시에만)
      mode === 'production' && visualizer({
        open: true,
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true
      })
    ],
    
    build: {
      target: 'es2015',
      cssTarget: 'chrome80',
      reportCompressedSize: false,
      chunkSizeWarningLimit: 2000,
      
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'mui-vendor': ['@mui/material', '@emotion/react', '@emotion/styled'],
            'chart-vendor': ['recharts', 'd3-scale', 'd3-shape'],
            'editor-vendor': ['monaco-editor', '@monaco-editor/react'],
            'utils': ['axios', 'date-fns', 'lodash-es']
          },
          
          // 청크 파일명 패턴
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop().split('.')[0] : 'chunk';
            return `js/${facadeModuleId}/[name].[hash].js`;
          },
          
          // 엔트리 파일명 패턴
          entryFileNames: 'js/[name].[hash].js',
          
          // 자산 파일명 패턴
          assetFileNames: (assetInfo) => {
            const extType = assetInfo.name.split('.').pop();
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              return `images/[name].[hash][extname]`;
            }
            if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
              return `fonts/[name].[hash][extname]`;
            }
            return `assets/[name].[hash][extname]`;
          }
        }
      },
      
      // Terser 최적화 옵션
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info']
        }
      }
    },
    
    // 최적화 옵션
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@mui/material',
        '@emotion/react',
        '@emotion/styled'
      ],
      exclude: ['@tanstack/react-query-devtools']
    }
  };
});
```

**검증 기준**:
- [ ] 빌드 시간 최적화
- [ ] 번들 크기 최소화
- [ ] 코드 스플리팅 동작
- [ ] 압축 및 최적화 확인

#### SubTask 7.2.2: 개발 서버 프록시 및 환경 변수 구성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```typescript
// frontend/src/config/environment.ts
export interface Environment {
  readonly API_URL: string;
  readonly WS_URL: string;
  readonly AUTH_DOMAIN: string;
  readonly PUBLIC_URL: string;
  readonly NODE_ENV: 'development' | 'production' | 'test';
  readonly VERSION: string;
  readonly FEATURES: {
    readonly DARK_MODE: boolean;
    readonly ANALYTICS: boolean;
    readonly BETA_FEATURES: boolean;
    readonly DEBUG_MODE: boolean;
  };
}

class EnvironmentConfig {
  private env: Environment;

  constructor() {
    this.env = this.loadEnvironment();
    this.validateEnvironment();
  }

  private loadEnvironment(): Environment {
    return {
      API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
      AUTH_DOMAIN: import.meta.env.VITE_AUTH_DOMAIN || '',
      PUBLIC_URL: import.meta.env.VITE_PUBLIC_URL || '/',
      NODE_ENV: import.meta.env.MODE as Environment['NODE_ENV'],
      VERSION: import.meta.env.VITE_VERSION || '1.0.0',
      FEATURES: {
        DARK_MODE: import.meta.env.VITE_FEATURE_DARK_MODE === 'true',
        ANALYTICS: import.meta.env.VITE_FEATURE_ANALYTICS === 'true',
        BETA_FEATURES: import.meta.env.VITE_FEATURE_BETA === 'true',
        DEBUG_MODE: import.meta.env.VITE_DEBUG === 'true'
      }
    };
  }

  private validateEnvironment(): void {
    const required = ['API_URL', 'WS_URL'];
    const missing = required.filter(key => !this.env[key as keyof Environment]);
    
    if (missing.length > 0) {
      console.warn(`Missing environment variables: ${missing.join(', ')}`);
    }
  }

  get config(): Environment {
    return this.env;
  }

  isDevelopment(): boolean {
    return this.env.NODE_ENV === 'development';
  }

  isProduction(): boolean {
    return this.env.NODE_ENV === 'production';
  }

  isFeatureEnabled(feature: keyof Environment['FEATURES']): boolean {
    return this.env.FEATURES[feature];
  }
}

export const env = new EnvironmentConfig();
```

```bash
# frontend/.env.development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_AUTH_DOMAIN=http://localhost:8000/auth
VITE_PUBLIC_URL=/
VITE_VERSION=1.0.0-dev

# Feature Flags
VITE_FEATURE_DARK_MODE=true
VITE_FEATURE_ANALYTICS=false
VITE_FEATURE_BETA=true
VITE_DEBUG=true

# API Keys (Development)
VITE_GOOGLE_MAPS_KEY=your-dev-key
VITE_SENTRY_DSN=your-dev-dsn
```

**검증 기준**:
- [ ] 환경 변수 로드 확인
- [ ] 프록시 설정 동작
- [ ] Feature flags 작동
- [ ] 환경별 설정 분리

#### SubTask 7.2.3: Docker 컨테이너 및 docker-compose 설정
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 4시간

**작업 내용**:

```dockerfile
# frontend/Dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 캐싱을 위한 package 파일 복사
COPY package*.json ./
RUN npm ci --only=production

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Nginx 설정
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# frontend/nginx.conf
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json application/x-font-ttf
               font/opentype image/svg+xml image/x-icon;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # SPA 라우팅
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API 프록시
        location /api {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket 프록시
        location /ws {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_set_header Host $host;
        }

        # 정적 자산 캐싱
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**검증 기준**:
- [ ] Docker 이미지 빌드 성공
- [ ] 컨테이너 실행 확인
- [ ] Nginx 프록시 동작
- [ ] 헬스체크 통과

#### SubTask 7.2.4: CI/CD 파이프라인 프론트엔드 통합
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 4시간

**작업 내용**:

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Type check
        working-directory: frontend
        run: npm run type-check
      
      - name: Lint
        working-directory: frontend
        run: npm run lint
      
      - name: Unit tests
        working-directory: frontend
        run: npm run test:coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/lcov.info
          flags: frontend
      
      - name: Build
        working-directory: frontend
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist
      
      - name: Deploy to S3
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
        run: |
          aws s3 sync frontend/dist s3://${{ secrets.S3_BUCKET_NAME }} --delete
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} --paths "/*"
```

**검증 기준**:
- [ ] CI 파이프라인 실행
- [ ] 테스트 통과
- [ ] 빌드 아티팩트 생성
- [ ] 자동 배포 동작

---

### Task 7.3: TypeScript 및 린팅 설정

#### SubTask 7.3.1: TypeScript 컴파일러 옵션 구성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```json
// frontend/tsconfig.json (상세 설정)
{
  "compilerOptions": {
    /* Language and Environment */
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    
    /* Modules */
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowImportingTsExtensions": true,
    
    /* JavaScript Support */
    "allowJs": false,
    "checkJs": false,
    
    /* Emit */
    "noEmit": true,
    "sourceMap": true,
    "removeComments": true,
    "importHelpers": true,
    "importsNotUsedAsValues": "remove",
    "downlevelIteration": true,
    
    /* Interop Constraints */
    "isolatedModules": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    
    /* Type Checking */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "allowUnusedLabels": false,
    "allowUnreachableCode": false,
    
    /* Completeness */
    "skipLibCheck": true,
    
    /* Path Mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@api/*": ["src/api/*"],
      "@components/*": ["src/components/*"],
      "@hooks/*": ["src/hooks/*"],
      "@pages/*": ["src/pages/*"],
      "@store/*": ["src/store/*"],
      "@types/*": ["src/types/*"],
      "@utils/*": ["src/utils/*"]
    }
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "src/**/*.d.ts",
    "vite.config.ts"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build",
    "coverage",
    "**/*.spec.ts",
    "**/*.test.ts"
  ],
  "references": [
    { "path": "./tsconfig.node.json" }
  ]
}
```

**검증 기준**:
- [ ] Strict mode 활성화
- [ ] 경로 매핑 작동
- [ ] 타입 체크 통과
- [ ] IDE 지원 확인

#### SubTask 7.3.2: ESLint 및 Prettier 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```json
// frontend/.eslintrc.json
{
  "root": true,
  "env": {
    "browser": true,
    "es2020": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "project": ["./tsconfig.json"],
    "tsconfigRootDir": "__dirname",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": [
    "react-refresh",
    "@typescript-eslint",
    "react",
    "react-hooks",
    "jsx-a11y",
    "import",
    "prettier"
  ],
  "settings": {
    "react": {
      "version": "detect"
    },
    "import/resolver": {
      "typescript": {
        "alwaysTryTypes": true,
        "project": "./tsconfig.json"
      }
    }
  },
  "rules": {
    // TypeScript
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        "argsIgnorePattern": "^_",
        "varsIgnorePattern": "^_"
      }
    ],
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": [
      "error",
      {
        "allowExpressions": true,
        "allowTypedFunctionExpressions": true
      }
    ],
    "@typescript-eslint/no-floating-promises": "error",
    "@typescript-eslint/no-misused-promises": "error",
    "@typescript-eslint/await-thenable": "error",
    "@typescript-eslint/no-unnecessary-type-assertion": "error",
    "@typescript-eslint/naming-convention": [
      "error",
      {
        "selector": "interface",
        "format": ["PascalCase"],
        "prefix": ["I"]
      },
      {
        "selector": "typeAlias",
        "format": ["PascalCase"]
      },
      {
        "selector": "enum",
        "format": ["PascalCase"]
      }
    ],
    
    // React
    "react/prop-types": "off",
    "react/display-name": "off",
    "react-refresh/only-export-components": [
      "warn",
      { "allowConstantExport": true }
    ],
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/jsx-no-target-blank": "error",
    "react/jsx-curly-brace-presence": [
      "error",
      { "props": "never", "children": "never" }
    ],
    "react/self-closing-comp": "error",
    "react/jsx-sort-props": [
      "error",
      {
        "callbacksLast": true,
        "shorthandFirst": true,
        "noSortAlphabetically": false,
        "reservedFirst": true
      }
    ],
    
    // Import
    "import/order": [
      "error",
      {
        "groups": [
          "builtin",
          "external",
          "internal",
          ["parent", "sibling"],
          "index",
          "object",
          "type"
        ],
        "pathGroups": [
          {
            "pattern": "react",
            "group": "external",
            "position": "before"
          },
          {
            "pattern": "@/**",
            "group": "internal",
            "position": "after"
          }
        ],
        "pathGroupsExcludedImportTypes": ["react"],
        "newlines-between": "always",
        "alphabetize": {
          "order": "asc",
          "caseInsensitive": true
        }
      }
    ],
    "import/no-duplicates": "error",
    "import/no-unresolved": "error",
    "import/no-cycle": "error",
    
    // General
    "no-console": [
      "warn",
      {
        "allow": ["warn", "error"]
      }
    ],
    "no-debugger": "error",
    "no-alert": "error",
    "prefer-const": "error",
    "no-var": "error",
    "no-nested-ternary": "error",
    "no-unneeded-ternary": "error"
  },
  "overrides": [
    {
      "files": ["*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx"],
      "rules": {
        "@typescript-eslint/no-explicit-any": "off",
        "@typescript-eslint/no-non-null-assertion": "off"
      }
    }
  ]
}
```

```json
// frontend/.prettierrc
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "quoteProps": "as-needed",
  "jsxSingleQuote": false,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "jsxBracketSameLine": false,
  "arrowParens": "always",
  "proseWrap": "preserve",
  "htmlWhitespaceSensitivity": "css",
  "endOfLine": "lf",
  "embeddedLanguageFormatting": "auto",
  "singleAttributePerLine": false
}
```

```ignore
# frontend/.prettierignore
# Dependencies
node_modules/
package-lock.json
pnpm-lock.yaml
yarn.lock

# Production
dist/
build/
coverage/

# Misc
*.min.js
*.min.css
public/
.next/
.cache/

# Generated files
*.generated.ts
*.generated.tsx
```

**추가 설정 파일**:
```json
// frontend/.eslintignore
node_modules
dist
build
coverage
public
*.config.js
*.config.ts
vite.config.ts
```

**검증 기준**:
- [ ] ESLint 규칙 적용 확인
- [ ] Prettier 포맷팅 동작
- [ ] VSCode 통합 설정
- [ ] 충돌 규칙 해결

#### SubTask 7.3.3: Husky 및 lint-staged Git hooks 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```bash
# Husky 및 lint-staged 설치
cd frontend
npm install -D husky lint-staged
npx husky-init && npm install
```

```json
// frontend/package.json (추가 부분)
{
  "scripts": {
    "prepare": "cd .. && husky install frontend/.husky",
    "pre-commit": "lint-staged",
    "pre-push": "npm run type-check && npm run test"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "vitest related --run"
    ],
    "*.{js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ],
    "*.css": [
      "prettier --write"
    ]
  }
}
```

```bash
#!/usr/bin/env sh
# frontend/.husky/pre-commit
. "$(dirname -- "$0")/_/husky.sh"

cd frontend
npm run pre-commit
```

```bash
#!/usr/bin/env sh
# frontend/.husky/pre-push
. "$(dirname -- "$0")/_/husky.sh"

cd frontend

echo "🔍 Running type check..."
npm run type-check

echo "🧪 Running tests..."
npm run test

echo "📊 Checking bundle size..."
npm run build:analyze

# Bundle size 체크
MAX_SIZE=500000 # 500KB
BUNDLE_SIZE=$(du -sb dist | cut -f1)

if [ $BUNDLE_SIZE -gt $MAX_SIZE ]; then
  echo "❌ Bundle size ($BUNDLE_SIZE) exceeds maximum allowed size ($MAX_SIZE)"
  exit 1
fi

echo "✅ All checks passed!"
```

```bash
#!/usr/bin/env sh
# frontend/.husky/commit-msg
. "$(dirname -- "$0")/_/husky.sh"

cd frontend

# Commit 메시지 검증
commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert)(\(.+\))?: .{1,100}$'
commit_message=$(cat "$1")

if ! echo "$commit_message" | grep -qE "$commit_regex"; then
  echo "❌ Invalid commit message format!"
  echo "📝 Format: <type>(<scope>): <subject>"
  echo "📝 Example: feat(auth): add login functionality"
  echo ""
  echo "Types: feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert"
  exit 1
fi
```

**추가 Git hooks 스크립트**:
```javascript
// frontend/scripts/check-dependencies.js
const fs = require('fs');
const path = require('path');

function checkUnusedDependencies() {
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../package.json'), 'utf-8')
  );
  
  const dependencies = Object.keys(packageJson.dependencies || {});
  const devDependencies = Object.keys(packageJson.devDependencies || {});
  
  // 소스 코드에서 import 문 검색
  const srcPath = path.join(__dirname, '../src');
  const importRegex = /import\s+.*from\s+['"]([^'"]+)['"]/g;
  const requireRegex = /require\s*\(['"]([^'"]+)['"]\)/g;
  
  const usedPackages = new Set();
  
  function scanDirectory(dir) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        scanDirectory(filePath);
      } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
        const content = fs.readFileSync(filePath, 'utf-8');
        
        [...content.matchAll(importRegex), ...content.matchAll(requireRegex)]
          .forEach(match => {
            const packageName = match[1].split('/')[0];
            if (!packageName.startsWith('.') && !packageName.startsWith('@/')) {
              usedPackages.add(packageName.replace('@', ''));
            }
          });
      }
    });
  }
  
  scanDirectory(srcPath);
  
  const unusedDeps = [...dependencies, ...devDependencies]
    .filter(dep => !usedPackages.has(dep));
  
  if (unusedDeps.length > 0) {
    console.warn('⚠️  Potentially unused dependencies:', unusedDeps);
  }
}

checkUnusedDependencies();
```

**검증 기준**:
- [ ] Pre-commit hooks 동작
- [ ] Pre-push hooks 동작
- [ ] Commit 메시지 검증
- [ ] 자동 포맷팅 확인

#### SubTask 7.3.4: 타입 정의 파일 및 공통 인터페이스 구성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/types/models.d.ts
export interface IUser {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
  preferences: IUserPreferences;
}

export interface IUserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    inApp: boolean;
  };
  dashboardLayout?: IDashboardLayout;
}

export interface IProject {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  visibility: 'public' | 'private';
  ownerId: string;
  teamIds: string[];
  tags: string[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  lastActivityAt: Date;
}

export enum ProjectStatus {
  PLANNING = 'planning',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export interface IAgent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  version: string;
  capabilities: string[];
  configuration: IAgentConfiguration;
  metrics: IAgentMetrics;
  lastHeartbeat: Date;
  createdAt: Date;
  updatedAt: Date;
}

export enum AgentType {
  PARSER = 'parser',
  ARCHITECT = 'architect',
  FRONTEND = 'frontend',
  BACKEND = 'backend',
  DATABASE = 'database',
  SECURITY = 'security',
  TESTING = 'testing',
  DOCUMENTATION = 'documentation',
  DEVOPS = 'devops'
}

export enum AgentStatus {
  IDLE = 'idle',
  INITIALIZING = 'initializing',
  READY = 'ready',
  RUNNING = 'running',
  ERROR = 'error',
  OFFLINE = 'offline'
}

export interface IWorkflow {
  id: string;
  name: string;
  description: string;
  projectId: string;
  definition: IWorkflowDefinition;
  status: WorkflowStatus;
  currentStep?: number;
  progress: number;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  results?: any;
}

export interface IWorkflowDefinition {
  steps: IWorkflowStep[];
  variables: Record<string, any>;
  triggers: ITrigger[];
  conditions: ICondition[];
}

export interface IWorkflowStep {
  id: string;
  name: string;
  agentId: string;
  inputs: Record<string, any>;
  outputs?: Record<string, any>;
  dependencies: string[];
  retryPolicy?: IRetryPolicy;
  timeout?: number;
}
```

```typescript
// frontend/src/types/api.d.ts
export interface IApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: IApiError;
  metadata?: IApiMetadata;
}

export interface IApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  traceId?: string;
}

export interface IApiMetadata {
  timestamp: string;
  version: string;
  requestId: string;
  pagination?: IPagination;
}

export interface IPagination {
  page: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface IApiRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  headers?: Record<string, string>;
  params?: Record<string, any>;
  data?: any;
  timeout?: number;
  retries?: number;
}

export interface IWebSocketMessage {
  type: WebSocketMessageType;
  payload: any;
  timestamp: string;
  correlationId?: string;
}

export enum WebSocketMessageType {
  CONNECTION = 'connection',
  AGENT_STATUS = 'agent_status',
  WORKFLOW_UPDATE = 'workflow_update',
  PROJECT_UPDATE = 'project_update',
  NOTIFICATION = 'notification',
  ERROR = 'error',
  PING = 'ping',
  PONG = 'pong'
}
```

```typescript
// frontend/src/types/components.d.ts
import { ReactNode, CSSProperties } from 'react';

export interface IBaseComponentProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
  'data-testid'?: string;
}

export interface IFormFieldProps<T = any> extends IBaseComponentProps {
  name: string;
  label?: string;
  value?: T;
  defaultValue?: T;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  onChange?: (value: T) => void;
  onBlur?: () => void;
  onFocus?: () => void;
}

export interface ITableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => ReactNode;
  headerRender?: () => ReactNode;
}

export interface ITableProps<T = any> extends IBaseComponentProps {
  columns: ITableColumn<T>[];
  data: T[];
  loading?: boolean;
  pagination?: IPaginationProps;
  rowKey?: string | ((record: T) => string);
  onRowClick?: (record: T, index: number) => void;
  onSelectionChange?: (selectedRows: T[]) => void;
  selectable?: boolean;
  expandable?: boolean;
  expandedRowRender?: (record: T) => ReactNode;
}

export interface IModalProps extends IBaseComponentProps {
  open: boolean;
  title?: string;
  width?: number | string;
  closable?: boolean;
  maskClosable?: boolean;
  footer?: ReactNode;
  onClose: () => void;
  onOk?: () => void | Promise<void>;
  okText?: string;
  cancelText?: string;
  loading?: boolean;
}
```

```typescript
// frontend/src/types/global.d.ts
declare global {
  interface Window {
    __REDUX_DEVTOOLS_EXTENSION__?: any;
    __REACT_DEVTOOLS_GLOBAL_HOOK__?: any;
    gtag?: (...args: any[]) => void;
    dataLayer?: any[];
  }

  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
      VITE_API_URL: string;
      VITE_WS_URL: string;
      VITE_AUTH_DOMAIN: string;
      VITE_PUBLIC_URL: string;
      VITE_VERSION: string;
    }
  }
}

// Utility types
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type Maybe<T> = T | null | undefined;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

export type ValueOf<T> = T[keyof T];

export type Entries<T> = {
  [K in keyof T]: [K, T[K]];
}[keyof T][];

// Branded types for type safety
export type Brand<K, T> = K & { __brand: T };
export type UUID = Brand<string, 'UUID'>;
export type Email = Brand<string, 'Email'>;
export type URL = Brand<string, 'URL'>;
export type Timestamp = Brand<number, 'Timestamp'>;

// Module declarations
declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

export {};
```

**검증 기준**:
- [ ] 타입 정의 완성도
- [ ] IDE 자동완성 지원
- [ ] 타입 안정성 확보
- [ ] 모든 모델 타입 정의

---

### Task 7.4: Zustand 상태 관리 구축

#### SubTask 7.4.1: Zustand Store 아키텍처 설계 및 기본 설정
**담당자**: 프론트엔드 리드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/store/index.ts
import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { createAuthSlice, IAuthSlice } from './slices/authSlice';
import { createProjectSlice, IProjectSlice } from './slices/projectSlice';
import { createAgentSlice, IAgentSlice } from './slices/agentSlice';
import { createUISlice, IUISlice } from './slices/uiSlice';
import { createWorkflowSlice, IWorkflowSlice } from './slices/workflowSlice';
import { createNotificationSlice, INotificationSlice } from './slices/notificationSlice';

export interface IAppStore extends 
  IAuthSlice,
  IProjectSlice,
  IAgentSlice,
  IUISlice,
  IWorkflowSlice,
  INotificationSlice {
  // Store-level actions
  resetStore: () => void;
  rehydrate: () => Promise<void>;
}

const useAppStore = create<IAppStore>()(
  devtools(
    subscribeWithSelector(
      persist(
        immer((set, get, store) => ({
          // Combine all slices
          ...createAuthSlice(set, get, store),
          ...createProjectSlice(set, get, store),
          ...createAgentSlice(set, get, store),
          ...createUISlice(set, get, store),
          ...createWorkflowSlice(set, get, store),
          ...createNotificationSlice(set, get, store),
          
          // Store-level actions
          resetStore: () => {
            set((state) => {
              // Reset all slices to initial state
              Object.keys(state).forEach(key => {
                if (typeof state[key as keyof typeof state] === 'object') {
                  state[key as keyof typeof state] = {} as any;
                }
              });
            });
          },
          
          rehydrate: async () => {
            // Rehydrate store from localStorage or API
            try {
              const savedState = localStorage.getItem('app-store');
              if (savedState) {
                const parsed = JSON.parse(savedState);
                set((state) => {
                  Object.assign(state, parsed);
                });
              }
            } catch (error) {
              console.error('Failed to rehydrate store:', error);
            }
          }
        })),
        {
          name: 'app-store',
          partialize: (state) => ({
            // Only persist specific parts of the state
            auth: {
              user: state.user,
              token: state.token,
              isAuthenticated: state.isAuthenticated
            },
            ui: {
              theme: state.theme,
              sidebarOpen: state.sidebarOpen,
              language: state.language
            }
          })
        }
      )
    ),
    {
      name: 'T-Developer Store'
    }
  )
);

// Selectors
export const selectors = {
  // Auth selectors
  isAuthenticated: (state: IAppStore) => state.isAuthenticated,
  currentUser: (state: IAppStore) => state.user,
  
  // Project selectors
  currentProject: (state: IAppStore) => state.currentProject,
  projectById: (id: string) => (state: IAppStore) => 
    state.projects.find(p => p.id === id),
  
  // Agent selectors
  agentsByProject: (projectId: string) => (state: IAppStore) =>
    state.agents.filter(a => a.projectId === projectId),
  activeAgents: (state: IAppStore) =>
    state.agents.filter(a => a.status === 'running'),
  
  // UI selectors
  isDarkMode: (state: IAppStore) => state.theme === 'dark',
  notifications: (state: IAppStore) => state.notifications,
  
  // Workflow selectors
  workflowsByProject: (projectId: string) => (state: IAppStore) =>
    state.workflows.filter(w => w.projectId === projectId),
  runningWorkflows: (state: IAppStore) =>
    state.workflows.filter(w => w.status === 'running')
};

// Computed values
export const computed = {
  totalActiveProjects: () => {
    const state = useAppStore.getState();
    return state.projects.filter(p => p.status !== 'archived').length;
  },
  
  systemHealth: () => {
    const state = useAppStore.getState();
    const totalAgents = state.agents.length;
    const healthyAgents = state.agents.filter(a => a.status === 'ready').length;
    return totalAgents > 0 ? (healthyAgents / totalAgents) * 100 : 0;
  }
};

export default useAppStore;
```

```typescript
// frontend/src/store/types.ts
export interface StoreSlice<T> {
  set: (fn: (state: T) => void) => void;
  get: () => T;
  subscribe: (listener: (state: T) => void) => () => void;
}

export type StateCreator<T> = (
  set: (fn: (state: T) => void) => void,
  get: () => T,
  store: any
) => T;

export interface AsyncAction<T = any> {
  execute: () => Promise<T>;
  loading: boolean;
  error: Error | null;
  data: T | null;
}
```

**검증 기준**:
- [ ] Store 초기화 성공
- [ ] DevTools 통합 확인
- [ ] 상태 구독 메커니즘 동작
- [ ] 타입 안정성 확보

#### SubTask 7.4.2: 인증 및 사용자 상태 관리 슬라이스
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/store/slices/authSlice.ts
import { StateCreator } from '../types';
import { IUser } from '@/types/models';
import { authAPI } from '@/api/auth';
import { jwtDecode } from 'jwt-decode';

export interface IAuthSlice {
  // State
  user: IUser | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  permissions: string[];
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  updateProfile: (updates: Partial<IUser>) => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  verifyToken: () => Promise<boolean>;
  loadUserPermissions: () => Promise<void>;
  
  // Utilities
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  company?: string;
}

interface TokenPayload {
  sub: string;
  email: string;
  exp: number;
  permissions: string[];
}

export const createAuthSlice: StateCreator<IAuthSlice> = (set, get) => ({
  // Initial state
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  permissions: [],
  
  // Actions
  login: async (email, password) => {
    set((state) => {
      state.isLoading = true;
      state.error = null;
    });
    
    try {
      const response = await authAPI.login({ email, password });
      const { user, accessToken, refreshToken } = response.data;
      
      // Decode token to get permissions
      const decoded = jwtDecode<TokenPayload>(accessToken);
      
      set((state) => {
        state.user = user;
        state.token = accessToken;
        state.refreshToken = refreshToken;
        state.isAuthenticated = true;
        state.permissions = decoded.permissions || [];
        state.isLoading = false;
      });
      
      // Save tokens to localStorage
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // Set default authorization header
      authAPI.setAuthHeader(accessToken);
      
      // Start token refresh timer
      get().startTokenRefreshTimer();
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Login failed';
        state.isLoading = false;
        state.isAuthenticated = false;
      });
      throw error;
    }
  },
  
  logout: () => {
    // Clear tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    // Clear auth header
    authAPI.clearAuthHeader();
    
    // Reset state
    set((state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.permissions = [];
      state.error = null;
    });
    
    // Redirect to login
    window.location.href = '/login';
  },
  
  register: async (data) => {
    set((state) => {
      state.isLoading = true;
      state.error = null;
    });
    
    try {
      const response = await authAPI.register(data);
      const { user, accessToken, refreshToken } = response.data;
      
      set((state) => {
        state.user = user;
        state.token = accessToken;
        state.refreshToken = refreshToken;
        state.isAuthenticated = true;
        state.isLoading = false;
      });
      
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      authAPI.setAuthHeader(accessToken);
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Registration failed';
        state.isLoading = false;
      });
      throw error;
    }
  },
  
  refreshAccessToken: async () => {
    const refreshToken = get().refreshToken;
    if (!refreshToken) {
      get().logout();
      return;
    }
    
    try {
      const response = await authAPI.refreshToken(refreshToken);
      const { accessToken, refreshToken: newRefreshToken } = response.data;
      
      set((state) => {
        state.token = accessToken;
        state.refreshToken = newRefreshToken;
      });
      
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', newRefreshToken);
      authAPI.setAuthHeader(accessToken);
      
    } catch (error) {
      get().logout();
      throw error;
    }
  },
  
  updateProfile: async (updates) => {
    set((state) => {
      state.isLoading = true;
    });
    
    try {
      const response = await authAPI.updateProfile(updates);
      
      set((state) => {
        state.user = { ...state.user!, ...response.data };
        state.isLoading = false;
      });
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Profile update failed';
        state.isLoading = false;
      });
      throw error;
    }
  },
  
  changePassword: async (oldPassword, newPassword) => {
    try {
      await authAPI.changePassword({ oldPassword, newPassword });
      
      // Force re-authentication
      get().logout();
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Password change failed';
      });
      throw error;
    }
  },
  
  resetPassword: async (email) => {
    try {
      await authAPI.resetPassword(email);
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Password reset failed';
      });
      throw error;
    }
  },
  
  verifyToken: async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) return false;
    
    try {
      const decoded = jwtDecode<TokenPayload>(token);
      
      // Check if token is expired
      if (decoded.exp * 1000 < Date.now()) {
        await get().refreshAccessToken();
        return true;
      }
      
      // Verify with backend
      const response = await authAPI.verifyToken(token);
      if (response.data.valid) {
        set((state) => {
          state.token = token;
          state.isAuthenticated = true;
          state.permissions = decoded.permissions || [];
        });
        
        authAPI.setAuthHeader(token);
        return true;
      }
      
      return false;
    } catch (error) {
      return false;
    }
  },
  
  loadUserPermissions: async () => {
    try {
      const response = await authAPI.getPermissions();
      set((state) => {
        state.permissions = response.data.permissions;
      });
    } catch (error) {
      console.error('Failed to load permissions:', error);
    }
  },
  
  // Utilities
  hasPermission: (permission) => {
    return get().permissions.includes(permission);
  },
  
  hasAnyPermission: (permissions) => {
    const userPermissions = get().permissions;
    return permissions.some(p => userPermissions.includes(p));
  },
  
  hasAllPermissions: (permissions) => {
    const userPermissions = get().permissions;
    return permissions.every(p => userPermissions.includes(p));
  },
  
  // Private helper
  startTokenRefreshTimer: () => {
    const token = get().token;
    if (!token) return;
    
    try {
      const decoded = jwtDecode<TokenPayload>(token);
      const expiresIn = decoded.exp * 1000 - Date.now();
      
      // Refresh 5 minutes before expiry
      const refreshIn = Math.max(0, expiresIn - 5 * 60 * 1000);
      
      setTimeout(() => {
        get().refreshAccessToken();
      }, refreshIn);
    } catch (error) {
      console.error('Failed to start token refresh timer:', error);
    }
  }
});
```

**검증 기준**:
- [ ] 로그인/로그아웃 동작
- [ ] 토큰 관리 및 갱신
- [ ] 권한 체크 메커니즘
- [ ] 에러 처리 완성도

#### SubTask 7.4.3: 프로젝트 및 에이전트 상태 관리 슬라이스
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/store/slices/projectSlice.ts
import { StateCreator } from '../types';
import { IProject } from '@/types/models';
import { projectAPI } from '@/api/project';

export interface IProjectSlice {
  // State
  projects: IProject[];
  currentProject: IProject | null;
  isLoading: boolean;
  error: string | null;
  filters: ProjectFilters;
  sortBy: SortOption;
  searchQuery: string;
  
  // Actions
  fetchProjects: () => Promise<void>;
  fetchProjectById: (id: string) => Promise<void>;
  createProject: (data: CreateProjectData) => Promise<IProject>;
  updateProject: (id: string, updates: Partial<IProject>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  selectProject: (id: string | null) => void;
  
  // Filtering and sorting
  setFilters: (filters: ProjectFilters) => void;
  setSortBy: (sortBy: SortOption) => void;
  setSearchQuery: (query: string) => void;
  
  // Utilities
  getFilteredProjects: () => IProject[];
  getProjectsByStatus: (status: string) => IProject[];
  getRecentProjects: (limit?: number) => IProject[];
}

interface ProjectFilters {
  status?: string[];
  tags?: string[];
  visibility?: 'public' | 'private' | 'all';
  dateRange?: {
    start: Date;
    end: Date;
  };
}

type SortOption = 'name' | 'createdAt' | 'updatedAt' | 'status';

interface CreateProjectData {
  name: string;
  description: string;
  visibility: 'public' | 'private';
  tags?: string[];
  metadata?: Record<string, any>;
}

export const createProjectSlice: StateCreator<IProjectSlice> = (set, get) => ({
  // Initial state
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,
  filters: {},
  sortBy: 'createdAt',
  searchQuery: '',
  
  // Actions
  fetchProjects: async () => {
    set((state) => {
      state.isLoading = true;
      state.error = null;
    });
    
    try {
      const response = await projectAPI.getProjects({
        filters: get().filters,
        sortBy: get().sortBy,
        search: get().searchQuery
      });
      
      set((state) => {
        state.projects = response.data.projects;
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to fetch projects';
        state.isLoading = false;
      });
    }
  },
  
  fetchProjectById: async (id) => {
    set((state) => {
      state.isLoading = true;
    });
    
    try {
      const response = await projectAPI.getProjectById(id);
      const project = response.data;
      
      set((state) => {
        // Update in projects list
        const index = state.projects.findIndex(p => p.id === id);
        if (index !== -1) {
          state.projects[index] = project;
        } else {
          state.projects.push(project);
        }
        
        // Set as current if it's the selected one
        if (state.currentProject?.id === id) {
          state.currentProject = project;
        }
        
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to fetch project';
        state.isLoading = false;
      });
    }
  },
  
  createProject: async (data) => {
    set((state) => {
      state.isLoading = true;
      state.error = null;
    });
    
    try {
      const response = await projectAPI.createProject(data);
      const newProject = response.data;
      
      set((state) => {
        state.projects.unshift(newProject);
        state.currentProject = newProject;
        state.isLoading = false;
      });
      
      return newProject;
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to create project';
        state.isLoading = false;
      });
      throw error;
    }
  },
  
  updateProject: async (id, updates) => {
    set((state) => {
      state.isLoading = true;
    });
    
    try {
      const response = await projectAPI.updateProject(id, updates);
      const updatedProject = response.data;
      
      set((state) => {
        const index = state.projects.findIndex(p => p.id === id);
        if (index !== -1) {
          state.projects[index] = updatedProject;
        }
        
        if (state.currentProject?.id === id) {
          state.currentProject = updatedProject;
        }
        
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to update project';
        state.isLoading = false;
      });
      throw error;
    }
  },
  
  deleteProject: async (id) => {
    set((state) => {
      state.isLoading = true;
    });
    
    try {
      await projectAPI.deleteProject(id);
      
      set((state) => {
        state.projects = state.projects.filter(p => p.id !== id);
        
        if (state.currentProject?.id === id) {
          state.currentProject = null;
        }
        
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to delete project';
        state.isLoading = false;
      });
      throw error;
    }
  },
  
  selectProject: (id) => {
    const project = id ? get().projects.find(p => p.id === id) : null;
    set((state) => {
      state.currentProject = project || null;
    });
  },
  
  // Filtering and sorting
  setFilters: (filters) => {
    set((state) => {
      state.filters = filters;
    });
    get().fetchProjects();
  },
  
  setSortBy: (sortBy) => {
    set((state) => {
      state.sortBy = sortBy;
    });
    get().fetchProjects();
  },
  
  setSearchQuery: (query) => {
    set((state) => {
      state.searchQuery = query;
    });
    
    // Debounce search
    clearTimeout((window as any).__searchTimeout);
    (window as any).__searchTimeout = setTimeout(() => {
      get().fetchProjects();
    }, 300);
  },
  
  // Utilities
  getFilteredProjects: () => {
    const { projects, filters, searchQuery } = get();
    let filtered = [...projects];
    
    // Apply filters
    if (filters.status?.length) {
      filtered = filtered.filter(p => filters.status!.includes(p.status));
    }
    
    if (filters.visibility && filters.visibility !== 'all') {
      filtered = filtered.filter(p => p.visibility === filters.visibility);
    }
    
    if (filters.tags?.length) {
      filtered = filtered.filter(p => 
        filters.tags!.some(tag => p.tags.includes(tag))
      );
    }
    
    if (filters.dateRange) {
      filtered = filtered.filter(p => {
        const createdAt = new Date(p.createdAt);
        return createdAt >= filters.dateRange!.start && 
               createdAt <= filters.dateRange!.end;
      });
    }
    
    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.description.toLowerCase().includes(query) ||
        p.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    return filtered;
  },
  
  getProjectsByStatus: (status) => {
    return get().projects.filter(p => p.status === status);
  },
  
  getRecentProjects: (limit = 5) => {
    return [...get().projects]
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
      .slice(0, limit);
  }
});
```

```typescript
// frontend/src/store/slices/agentSlice.ts
import { StateCreator } from '../types';
import { IAgent, AgentStatus } from '@/types/models';
import { agentAPI } from '@/api/agent';

export interface IAgentSlice {
  // State
  agents: IAgent[];
  agentStatuses: Map<string, AgentStatus>;
  selectedAgent: IAgent | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchAgents: () => Promise<void>;
  fetchAgentsByProject: (projectId: string) => Promise<void>;
  startAgent: (agentId: string, config?: any) => Promise<void>;
  stopAgent: (agentId: string) => Promise<void>;
  restartAgent: (agentId: string) => Promise<void>;
  updateAgentConfig: (agentId: string, config: any) => Promise<void>;
  
  // Status management
  updateAgentStatus: (agentId: string, status: AgentStatus) => void;
  subscribeToAgentStatus: (agentId: string) => void;
  unsubscribeFromAgentStatus: (agentId: string) => void;
  
  // Utilities
  getAgentById: (id: string) => IAgent | undefined;
  getAgentsByType: (type: string) => IAgent[];
  getActiveAgents: () => IAgent[];
  getAgentMetrics: (agentId: string) => Promise<any>;
}

export const createAgentSlice: StateCreator<IAgentSlice> = (set, get) => ({
  // Initial state
  agents: [],
  agentStatuses: new Map(),
  selectedAgent: null,
  isLoading: false,
  error: null,
  
  // Actions
  fetchAgents: async () => {
    set((state) => {
      state.isLoading = true;
      state.error = null;
    });
    
    try {
      const response = await agentAPI.getAgents();
      
      set((state) => {
        state.agents = response.data.agents;
        
        // Update status map
        response.data.agents.forEach((agent: IAgent) => {
          state.agentStatuses.set(agent.id, agent.status);
        });
        
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to fetch agents';
        state.isLoading = false;
      });
    }
  },
  
  fetchAgentsByProject: async (projectId) => {
    set((state) => {
      state.isLoading = true;
    });
    
    try {
      const response = await agentAPI.getAgentsByProject(projectId);
      
      set((state) => {
        state.agents = response.data.agents;
        state.isLoading = false;
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to fetch project agents';
        state.isLoading = false;
      });
    }
  },
  
  startAgent: async (agentId, config) => {
    try {
      await agentAPI.startAgent(agentId, config);
      
      set((state) => {
        const agent = state.agents.find(a => a.id === agentId);
        if (agent) {
          agent.status = 'initializing';
        }
        state.agentStatuses.set(agentId, 'initializing');
      });
      
      // Subscribe to status updates
      get().subscribeToAgentStatus(agentId);
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to start agent';
      });
      throw error;
    }
  },
  
  stopAgent: async (agentId) => {
    try {
      await agentAPI.stopAgent(agentId);
      
      set((state) => {
        const agent = state.agents.find(a => a.id === agentId);
        if (agent) {
          agent.status = 'offline';
        }
        state.agentStatuses.set(agentId, 'offline');
      });
      
      // Unsubscribe from status updates
      get().unsubscribeFromAgentStatus(agentId);
      
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to stop agent';
      });
      throw error;
    }
  },
  
  restartAgent: async (agentId) => {
    await get().stopAgent(agentId);
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    await get().startAgent(agentId);
  },
  
  updateAgentConfig: async (agentId, config) => {
    try {
      const response = await agentAPI.updateAgentConfig(agentId, config);
      
      set((state) => {
        const index = state.agents.findIndex(a => a.id === agentId);
        if (index !== -1) {
          state.agents[index] = response.data;
        }
      });
    } catch (error: any) {
      set((state) => {
        state.error = error.response?.data?.message || 'Failed to update agent config';
      });
      throw error;
    }
  },
  
  // Status management
  updateAgentStatus: (agentId, status) => {
    set((state) => {
      const agent = state.agents.find(a => a.id === agentId);
      if (agent) {
        agent.status = status;
        agent.lastHeartbeat = new Date();
      }
      state.agentStatuses.set(agentId, status);
    });
  },
  
  subscribeToAgentStatus: (agentId) => {
    // This will be implemented with WebSocket in Task 7.6
    console.log(`Subscribing to agent ${agentId} status updates`);
  },
  
  unsubscribeFromAgentStatus: (agentId) => {
    // This will be implemented with WebSocket in Task 7.6
    console.log(`Unsubscribing from agent ${agentId} status updates`);
  },
  
  // Utilities
  getAgentById: (id) => {
    return get().agents.find(a => a.id === id);
  },
  
  getAgentsByType: (type) => {
    return get().agents.filter(a => a.type === type);
  },
  
  getActiveAgents: () => {
    return get().agents.filter(a => 
      ['ready', 'running'].includes(a.status)
    );
  },
  
  getAgentMetrics: async (agentId) => {
    try {
      const response = await agentAPI.getAgentMetrics(agentId);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agent metrics:', error);
      return null;
    }
  }
});
```

**검증 기준**:
- [ ] 프로젝트 CRUD 동작
- [ ] 에이전트 상태 관리
- [ ] 필터링 및 정렬 기능
- [ ] 실시간 상태 업데이트 준비

#### SubTask 7.4.4: 상태 영속성 및 미들웨어 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/store/middleware/logger.ts
import { StateCreator, StoreMutatorIdentifier } from 'zustand';

type Logger = <
  T extends unknown,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = []
>(
  f: StateCreator<T, Mps, Mcs>,
  name?: string
) => StateCreator<T, Mps, Mcs>;

type LoggerImpl = <T extends unknown>(
  f: StateCreator<T, [], []>,
  name?: string
) => StateCreator<T, [], []>;

const loggerImpl: LoggerImpl = (f, name) => (set, get, store) => {
  type T = ReturnType<typeof f>;
  const loggedSet: typeof set = (...args) => {
    const previousState = get();
    set(...args);
    const nextState = get();
    
    if (import.meta.env.DEV) {
      console.group(
        `%c${name || 'Store'} Action @ ${new Date().toLocaleTimeString()}`,
        'color: #8B5CF6; font-weight: bold;'
      );
      console.log('%cPrevious State:', 'color: #EF4444; font-weight: bold;', previousState);
      console.log('%cNext State:', 'color: #10B981; font-weight: bold;', nextState);
      console.log('%cDiff:', 'color: #F59E0B; font-weight: bold;', 
        getDiff(previousState, nextState)
      );
      console.groupEnd();
    }
  };
  
  return f(loggedSet, get, store);
};

export const logger = loggerImpl as Logger;

// Helper function to get state diff
function getDiff(prev: any, next: any): any {
  const diff: any = {};
  
  // Check for added or modified properties
  for (const key in next) {
    if (!(key in prev)) {
      diff[`+${key}`] = next[key];
    } else if (JSON.stringify(prev[key]) !== JSON.stringify(next[key])) {
      diff[`~${key}`] = {
        from: prev[key],
        to: next[key]
      };
    }
  }
  
  // Check for removed properties
  for (const key in prev) {
    if (!(key in next)) {
      diff[`-${key}`] = prev[key];
    }
  }
  
  return diff;
}
```

```typescript
// frontend/src/store/middleware/persistence.ts
import { StateCreator } from 'zustand';

interface PersistOptions<T> {
  name: string;
  storage?: Storage;
  serialize?: (state: T) => string;
  deserialize?: (str: string) => T;
  partialize?: (state: T) => Partial<T>;
  version?: number;
  migrate?: (persistedState: any, version: number) => T;
  merge?: (persistedState: any, currentState: T) => T;
}

export function createPersistence<T>(
  options: PersistOptions<T>
): StateCreator<T> {
  const {
    name,
    storage = localStorage,
    serialize = JSON.stringify,
    deserialize = JSON.parse,
    partialize = (state) => state,
    version = 0,
    migrate,
    merge = (persisted, current) => ({ ...current, ...persisted })
  } = options;
  
  return (set, get, api) => {
    // Load persisted state
    const loadPersistedState = (): Partial<T> | null => {
      try {
        const item = storage.getItem(name);
        if (!item) return null;
        
        const { state, version: persistedVersion } = deserialize(item);
        
        // Handle migration if needed
        if (migrate && persistedVersion !== version) {
          return migrate(state, persistedVersion);
        }
        
        return state;
      } catch (error) {
        console.error(`Failed to load persisted state for ${name}:`, error);
        return null;
      }
    };
    
    // Save state to storage
    const saveState = (state: T) => {
      try {
        const stateToSave = partialize(state);
        storage.setItem(name, serialize({ state: stateToSave, version }));
      } catch (error) {
        console.error(`Failed to persist state for ${name}:`, error);
      }
    };
    
    // Subscribe to state changes
    api.subscribe((state) => {
      saveState(state);
    });
    
    // Load initial state
    const persistedState = loadPersistedState();
    if (persistedState) {
      set((state) => merge(persistedState, state));
    }
    
    return {} as T;
  };
}
```

```typescript
// frontend/src/store/middleware/sync.ts
import { StateCreator } from 'zustand';

interface SyncOptions {
  channel: string;
  debounce?: number;
  filter?: (state: any) => boolean;
}

export function createSyncMiddleware<T>(
  options: SyncOptions
): StateCreator<T> {
  const { channel, debounce = 100, filter = () => true } = options;
  
  return (set, get, api) => {
    let syncTimeout: NodeJS.Timeout;
    const broadcastChannel = new BroadcastChannel(channel);
    
    // Listen for state changes from other tabs
    broadcastChannel.onmessage = (event) => {
      if (event.data.type === 'STATE_SYNC') {
        set(event.data.state);
      }
    };
    
    // Subscribe to local state changes
    api.subscribe((state) => {
      if (!filter(state)) return;
      
      // Debounce broadcasting
      clearTimeout(syncTimeout);
      syncTimeout = setTimeout(() => {
        broadcastChannel.postMessage({
          type: 'STATE_SYNC',
          state,
          timestamp: Date.now()
        });
      }, debounce);
    });
    
    return {} as T;
  };
}
```

```typescript
// frontend/src/store/middleware/analytics.ts
import { StateCreator } from 'zustand';

interface AnalyticsOptions {
  trackingId: string;
  events: {
    [key: string]: (state: any, prevState: any) => void;
  };
}

export function createAnalyticsMiddleware<T>(
  options: AnalyticsOptions
): StateCreator<T> {
  const { trackingId, events } = options;
  
  return (set, get, api) => {
    let prevState = get();
    
    // Track state changes
    api.subscribe((state) => {
      // Check for events to track
      for (const [eventName, condition] of Object.entries(events)) {
        if (condition(state, prevState)) {
          trackEvent(eventName, {
            trackingId,
            state: JSON.stringify(state),
            timestamp: Date.now()
          });
        }
      }
      
      prevState = state;
    });
    
    return {} as T;
  };
}

function trackEvent(eventName: string, data: any) {
  // Send to analytics service
  if (window.gtag) {
    window.gtag('event', eventName, data);
  }
  
  // Or custom analytics
  console.log('Analytics Event:', eventName, data);
}
```

**검증 기준**:
- [ ] 상태 영속성 동작
- [ ] 로깅 미들웨어 출력
- [ ] 탭 간 상태 동기화
- [ ] 분석 이벤트 추적

---

### Task 7.5: React Query 데이터 페칭 설정

#### SubTask 7.5.1: React Query 기본 설정 및 클라이언트 구성
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/lib/react-query/client.ts
import { 
  QueryClient, 
  QueryCache, 
  MutationCache,
  QueryClientConfig 
} from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

// Query error handler
const queryErrorHandler = (error: unknown) => {
  const message = error instanceof Error 
    ? error.message 
    : 'An unexpected error occurred';
  
  // Don't show error for cancelled requests
  if (message.includes('cancelled')) return;
  
  toast.error(message);
  console.error('Query Error:', error);
};

// Mutation error handler
const mutationErrorHandler = (error: unknown) => {
  const message = error instanceof Error 
    ? error.message 
    : 'An unexpected error occurred';
  
  toast.error(message);
  console.error('Mutation Error:', error);
};

// Create query client with default options
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: how long until data is considered stale
      staleTime: 5 * 60 * 1000, // 5 minutes
      
      // Cache time: how long to keep unused data in cache
      cacheTime: 10 * 60 * 1000, // 10 minutes
      
      // Refetch on window focus
      refetchOnWindowFocus: false,
      
      // Refetch on reconnect
      refetchOnReconnect: 'always',
      
      // Retry configuration
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      
      // Retry delay
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Suspense mode
      suspense: false,
      
      // Track queries in devtools
      notifyOnChangeProps: 'tracked'
    },
    mutations: {
      // Retry configuration for mutations
      retry: 1,
      retryDelay: 1000
    }
  },
  
  // Query cache configuration
  queryCache: new QueryCache({
    onError: queryErrorHandler,
    onSuccess: (data) => {
      console.log('Query Success:', data);
    }
  }),
  
  // Mutation cache configuration
  mutationCache: new MutationCache({
    onError: mutationErrorHandler,
    onSuccess: (data) => {
      console.log('Mutation Success:', data);
    }
  })
});

// Query key factory
export const queryKeys = {
  all: [''] as const,
  
  auth: {
    all: ['auth'] as const,
    user: () => [...queryKeys.auth.all, 'user'] as const,
    permissions: () => [...queryKeys.auth.all, 'permissions'] as const
  },
  
  projects: {
    all: ['projects'] as const,
    lists: () => [...queryKeys.projects.all, 'list'] as const,
    list: (filters?: any) => [...queryKeys.projects.lists(), filters] as const,
    details: () => [...queryKeys.projects.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.projects.details(), id] as const,
    statistics: (id: string) => [...queryKeys.projects.detail(id), 'statistics'] as const
  },
  
  agents: {
    all: ['agents'] as const,
    lists: () => [...queryKeys.agents.all, 'list'] as const,
    list: (projectId?: string) => [...queryKeys.agents.lists(), { projectId }] as const,
    details: () => [...queryKeys.agents.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.agents.details(), id] as const,
    metrics: (id: string) => [...queryKeys.agents.detail(id), 'metrics'] as const,
    logs: (id: string) => [...queryKeys.agents.detail(id), 'logs'] as const
  },
  
  workflows: {
    all: ['workflows'] as const,
    lists: () => [...queryKeys.workflows.all, 'list'] as const,
    list: (projectId?: string) => [...queryKeys.workflows.lists(), { projectId }] as const,
    details: () => [...queryKeys.workflows.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.workflows.details(), id] as const,
    executions: (id: string) => [...queryKeys.workflows.detail(id), 'executions'] as const
  }
};

// Invalidation helpers
export const invalidateQueries = {
  projects: () => queryClient.invalidateQueries(queryKeys.projects.all),
  project: (id: string) => queryClient.invalidateQueries(queryKeys.projects.detail(id)),
  agents: () => queryClient.invalidateQueries(queryKeys.agents.all),
  agent: (id: string) => queryClient.invalidateQueries(queryKeys.agents.detail(id)),
  workflows: () => queryClient.invalidateQueries(queryKeys.workflows.all),
  workflow: (id: string) => queryClient.invalidateQueries(queryKeys.workflows.detail(id))
};
```

**검증 기준**:
- [ ] Query client 초기화
- [ ] 에러 핸들링 동작
- [ ] Query keys 구조화
- [ ] 캐시 무효화 헬퍼

# Phase 7: 프론트엔드 구현 - Tasks 7.5-7.8 SubTask 작업지시서 (계속)

### Task 7.5: React Query 데이터 페칭 설정 (계속)

#### SubTask 7.5.2: API 훅 및 쿼리 함수 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/hooks/queries/useProjects.ts
import { 
  useQuery, 
  useMutation, 
  useInfiniteQuery,
  UseQueryOptions,
  UseMutationOptions 
} from '@tanstack/react-query';
import { projectAPI } from '@/api/project';
import { queryKeys, queryClient } from '@/lib/react-query/client';
import { IProject } from '@/types/models';
import { toast } from 'react-hot-toast';

// Fetch all projects
export const useProjects = (
  filters?: any,
  options?: UseQueryOptions<IProject[]>
) => {
  return useQuery({
    queryKey: queryKeys.projects.list(filters),
    queryFn: async () => {
      const response = await projectAPI.getProjects(filters);
      return response.data.projects;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options
  });
};

// Fetch single project
export const useProject = (
  projectId: string,
  options?: UseQueryOptions<IProject>
) => {
  return useQuery({
    queryKey: queryKeys.projects.detail(projectId),
    queryFn: async () => {
      const response = await projectAPI.getProjectById(projectId);
      return response.data;
    },
    enabled: !!projectId,
    ...options
  });
};

// Infinite scroll for projects
export const useInfiniteProjects = (filters?: any) => {
  return useInfiniteQuery({
    queryKey: queryKeys.projects.list(filters),
    queryFn: async ({ pageParam = 1 }) => {
      const response = await projectAPI.getProjects({
        ...filters,
        page: pageParam,
        limit: 20
      });
      return response.data;
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.hasMore) {
        return pages.length + 1;
      }
      return undefined;
    },
    staleTime: 2 * 60 * 1000
  });
};

// Create project mutation
export const useCreateProject = (
  options?: UseMutationOptions<IProject, Error, any>
) => {
  return useMutation({
    mutationFn: projectAPI.createProject,
    onSuccess: (data) => {
      // Invalidate and refetch projects list
      queryClient.invalidateQueries(queryKeys.projects.lists());
      
      // Add the new project to cache immediately
      queryClient.setQueryData<IProject[]>(
        queryKeys.projects.lists(),
        (old = []) => [data, ...old]
      );
      
      toast.success('Project created successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create project');
    },
    ...options
  });
};

// Update project mutation
export const useUpdateProject = (
  options?: UseMutationOptions<IProject, Error, { id: string; data: Partial<IProject> }>
) => {
  return useMutation({
    mutationFn: ({ id, data }) => projectAPI.updateProject(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(queryKeys.projects.detail(id));
      
      // Snapshot previous value
      const previousProject = queryClient.getQueryData<IProject>(
        queryKeys.projects.detail(id)
      );
      
      // Optimistically update
      if (previousProject) {
        queryClient.setQueryData<IProject>(
          queryKeys.projects.detail(id),
          { ...previousProject, ...data }
        );
      }
      
      return { previousProject };
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousProject) {
        queryClient.setQueryData(
          queryKeys.projects.detail(variables.id),
          context.previousProject
        );
      }
      toast.error(error.message || 'Failed to update project');
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(queryKeys.projects.detail(data.id));
      toast.success('Project updated successfully');
    },
    ...options
  });
};

// Delete project mutation
export const useDeleteProject = (
  options?: UseMutationOptions<void, Error, string>
) => {
  return useMutation({
    mutationFn: projectAPI.deleteProject,
    onMutate: async (projectId) => {
      // Cancel queries
      await queryClient.cancelQueries(queryKeys.projects.lists());
      
      // Remove from cache
      queryClient.setQueryData<IProject[]>(
        queryKeys.projects.lists(),
        (old = []) => old.filter(p => p.id !== projectId)
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries(queryKeys.projects.all);
      toast.success('Project deleted successfully');
    },
    onError: (error) => {
      // Refetch on error to restore state
      queryClient.invalidateQueries(queryKeys.projects.lists());
      toast.error(error.message || 'Failed to delete project');
    },
    ...options
  });
};

// Project statistics
export const useProjectStatistics = (projectId: string) => {
  return useQuery({
    queryKey: queryKeys.projects.statistics(projectId),
    queryFn: async () => {
      const response = await projectAPI.getProjectStatistics(projectId);
      return response.data;
    },
    enabled: !!projectId,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000 // Refetch every minute
  });
};
```

```typescript
// frontend/src/hooks/queries/useAgents.ts
import { useQuery, useMutation, UseQueryOptions } from '@tanstack/react-query';
import { agentAPI } from '@/api/agent';
import { queryKeys, queryClient } from '@/lib/react-query/client';
import { IAgent } from '@/types/models';
import useAppStore from '@/store';

// Fetch agents for a project
export const useAgents = (
  projectId?: string,
  options?: UseQueryOptions<IAgent[]>
) => {
  return useQuery({
    queryKey: queryKeys.agents.list(projectId),
    queryFn: async () => {
      const response = projectId 
        ? await agentAPI.getAgentsByProject(projectId)
        : await agentAPI.getAgents();
      return response.data.agents;
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 10 * 1000, // Refetch every 10 seconds for status updates
    ...options
  });
};

// Fetch single agent
export const useAgent = (
  agentId: string,
  options?: UseQueryOptions<IAgent>
) => {
  return useQuery({
    queryKey: queryKeys.agents.detail(agentId),
    queryFn: async () => {
      const response = await agentAPI.getAgentById(agentId);
      return response.data;
    },
    enabled: !!agentId,
    ...options
  });
};

// Agent metrics with real-time updates
export const useAgentMetrics = (
  agentId: string,
  options?: UseQueryOptions<any>
) => {
  const updateAgentStatus = useAppStore(state => state.updateAgentStatus);
  
  return useQuery({
    queryKey: queryKeys.agents.metrics(agentId),
    queryFn: async () => {
      const response = await agentAPI.getAgentMetrics(agentId);
      
      // Update agent status in store
      if (response.data.status) {
        updateAgentStatus(agentId, response.data.status);
      }
      
      return response.data;
    },
    enabled: !!agentId,
    refetchInterval: 5000, // Update every 5 seconds
    ...options
  });
};

// Agent logs
export const useAgentLogs = (
  agentId: string,
  options?: { 
    limit?: number; 
    level?: string; 
    startTime?: Date;
    endTime?: Date;
  }
) => {
  return useQuery({
    queryKey: queryKeys.agents.logs(agentId),
    queryFn: async () => {
      const response = await agentAPI.getAgentLogs(agentId, options);
      return response.data;
    },
    enabled: !!agentId,
    staleTime: 10 * 1000,
    refetchInterval: false // Manual refresh only
  });
};

// Start agent mutation
export const useStartAgent = () => {
  return useMutation({
    mutationFn: ({ agentId, config }: { agentId: string; config?: any }) =>
      agentAPI.startAgent(agentId, config),
    onMutate: async ({ agentId }) => {
      // Optimistically update status
      const updateAgentStatus = useAppStore.getState().updateAgentStatus;
      updateAgentStatus(agentId, 'initializing');
    },
    onSuccess: (data, { agentId }) => {
      queryClient.invalidateQueries(queryKeys.agents.detail(agentId));
      queryClient.invalidateQueries(queryKeys.agents.metrics(agentId));
    },
    onError: (error, { agentId }) => {
      const updateAgentStatus = useAppStore.getState().updateAgentStatus;
      updateAgentStatus(agentId, 'error');
    }
  });
};

// Stop agent mutation
export const useStopAgent = () => {
  return useMutation({
    mutationFn: agentAPI.stopAgent,
    onMutate: async (agentId) => {
      const updateAgentStatus = useAppStore.getState().updateAgentStatus;
      updateAgentStatus(agentId, 'offline');
    },
    onSuccess: (data, agentId) => {
      queryClient.invalidateQueries(queryKeys.agents.detail(agentId));
      queryClient.removeQueries(queryKeys.agents.metrics(agentId));
    }
  });
};
```

```typescript
// frontend/src/hooks/queries/useWorkflows.ts
import { useQuery, useMutation, UseQueryOptions } from '@tanstack/react-query';
import { workflowAPI } from '@/api/workflow';
import { queryKeys, queryClient } from '@/lib/react-query/client';
import { IWorkflow } from '@/types/models';

// Fetch workflows
export const useWorkflows = (
  projectId?: string,
  options?: UseQueryOptions<IWorkflow[]>
) => {
  return useQuery({
    queryKey: queryKeys.workflows.list(projectId),
    queryFn: async () => {
      const response = await workflowAPI.getWorkflows(projectId);
      return response.data.workflows;
    },
    ...options
  });
};

// Execute workflow mutation with progress tracking
export const useExecuteWorkflow = () => {
  return useMutation({
    mutationFn: ({ 
      workflowId, 
      inputs 
    }: { 
      workflowId: string; 
      inputs: any;
    }) => workflowAPI.executeWorkflow(workflowId, inputs),
    
    onSuccess: (data, { workflowId }) => {
      // Start polling for execution status
      queryClient.invalidateQueries(
        queryKeys.workflows.executions(workflowId)
      );
    }
  });
};

// Workflow execution status with polling
export const useWorkflowExecution = (
  executionId: string,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: ['workflow-execution', executionId],
    queryFn: async () => {
      const response = await workflowAPI.getExecutionStatus(executionId);
      return response.data;
    },
    enabled: !!executionId,
    refetchInterval: (data) => {
      // Stop polling when execution is complete
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    ...options
  });
};
```

**검증 기준**:
- [ ] Query 훅 동작 확인
- [ ] Mutation 훅 동작 확인
- [ ] 에러 처리 메커니즘
- [ ] 실시간 업데이트 폴링

#### SubTask 7.5.3: 뮤테이션 및 낙관적 업데이트 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/hooks/mutations/optimistic-updates.ts
import { useMutation } from '@tanstack/react-query';
import { queryClient } from '@/lib/react-query/client';

interface OptimisticUpdateOptions<TData, TVariables, TContext> {
  mutationFn: (variables: TVariables) => Promise<TData>;
  onMutate?: (variables: TVariables) => Promise<TContext> | TContext;
  onError?: (error: Error, variables: TVariables, context?: TContext) => void;
  onSuccess?: (data: TData, variables: TVariables, context?: TContext) => void;
  onSettled?: (data?: TData, error?: Error, variables?: TVariables, context?: TContext) => void;
}

export function useOptimisticMutation<TData = unknown, TVariables = void, TContext = unknown>(
  options: OptimisticUpdateOptions<TData, TVariables, TContext>
) {
  return useMutation({
    ...options,
    onMutate: async (variables) => {
      // Execute user's onMutate if provided
      const context = options.onMutate ? await options.onMutate(variables) : undefined;
      
      // Return context for rollback
      return context;
    },
    onError: (error, variables, context) => {
      // Execute user's onError
      options.onError?.(error, variables, context);
      
      // Log error for debugging
      console.error('Optimistic update failed:', error);
    },
    onSuccess: (data, variables, context) => {
      // Execute user's onSuccess
      options.onSuccess?.(data, variables, context);
    },
    onSettled: (data, error, variables, context) => {
      // Execute user's onSettled
      options.onSettled?.(data, error, variables, context);
    }
  });
}

// Example: Optimistic task update
export const useOptimisticTaskUpdate = () => {
  return useOptimisticMutation({
    mutationFn: async ({ taskId, updates }: { taskId: string; updates: any }) => {
      const response = await fetch(`/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      return response.json();
    },
    
    onMutate: async ({ taskId, updates }) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries(['task', taskId]);
      
      // Snapshot previous value
      const previousTask = queryClient.getQueryData(['task', taskId]);
      
      // Optimistically update
      if (previousTask) {
        queryClient.setQueryData(['task', taskId], {
          ...previousTask,
          ...updates,
          updatedAt: new Date().toISOString()
        });
      }
      
      // Return context with snapshot
      return { previousTask };
    },
    
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousTask) {
        queryClient.setQueryData(['task', variables.taskId], context.previousTask);
      }
    },
    
    onSettled: (data, error, variables) => {
      // Always refetch after error or success
      queryClient.invalidateQueries(['task', variables?.taskId]);
    }
  });
};
```

```typescript
// frontend/src/hooks/mutations/batch-operations.ts
import { useMutation } from '@tanstack/react-query';
import { queryClient } from '@/lib/react-query/client';

interface BatchOperation<T> {
  id: string;
  operation: 'create' | 'update' | 'delete';
  data?: T;
}

export function useBatchMutation<T>(
  endpoint: string,
  queryKey: readonly unknown[]
) {
  return useMutation({
    mutationFn: async (operations: BatchOperation<T>[]) => {
      const response = await fetch(`/api/${endpoint}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ operations })
      });
      
      if (!response.ok) {
        throw new Error('Batch operation failed');
      }
      
      return response.json();
    },
    
    onMutate: async (operations) => {
      // Cancel queries
      await queryClient.cancelQueries(queryKey);
      
      // Get current data
      const previousData = queryClient.getQueryData<T[]>(queryKey);
      
      // Apply optimistic updates
      if (previousData) {
        const updatedData = [...previousData];
        
        operations.forEach(op => {
          switch (op.operation) {
            case 'create':
              if (op.data) {
                updatedData.push(op.data);
              }
              break;
              
            case 'update':
              const updateIndex = updatedData.findIndex(
                (item: any) => item.id === op.id
              );
              if (updateIndex !== -1 && op.data) {
                updatedData[updateIndex] = {
                  ...updatedData[updateIndex],
                  ...op.data
                };
              }
              break;
              
            case 'delete':
              const deleteIndex = updatedData.findIndex(
                (item: any) => item.id === op.id
              );
              if (deleteIndex !== -1) {
                updatedData.splice(deleteIndex, 1);
              }
              break;
          }
        });
        
        queryClient.setQueryData(queryKey, updatedData);
      }
      
      return { previousData };
    },
    
    onError: (error, operations, context) => {
      // Rollback
      if (context?.previousData) {
        queryClient.setQueryData(queryKey, context.previousData);
      }
    },
    
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries(queryKey);
    }
  });
}
```

```typescript
// frontend/src/hooks/mutations/undo-redo.ts
import { useRef, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';

interface UndoableAction<T> {
  do: () => Promise<T>;
  undo: () => Promise<void>;
  redo: () => Promise<T>;
}

export function useUndoRedoMutation<T>() {
  const historyRef = useRef<UndoableAction<T>[]>([]);
  const currentIndexRef = useRef(-1);
  
  const execute = useMutation({
    mutationFn: async (action: UndoableAction<T>) => {
      const result = await action.do();
      
      // Add to history
      historyRef.current = historyRef.current.slice(0, currentIndexRef.current + 1);
      historyRef.current.push(action);
      currentIndexRef.current++;
      
      return result;
    }
  });
  
  const undo = useCallback(async () => {
    if (currentIndexRef.current >= 0) {
      const action = historyRef.current[currentIndexRef.current];
      await action.undo();
      currentIndexRef.current--;
    }
  }, []);
  
  const redo = useCallback(async () => {
    if (currentIndexRef.current < historyRef.current.length - 1) {
      currentIndexRef.current++;
      const action = historyRef.current[currentIndexRef.current];
      await action.redo();
    }
  }, []);
  
  const canUndo = currentIndexRef.current >= 0;
  const canRedo = currentIndexRef.current < historyRef.current.length - 1;
  
  return {
    execute,
    undo,
    redo,
    canUndo,
    canRedo,
    history: historyRef.current,
    currentIndex: currentIndexRef.current
  };
}
```

**검증 기준**:
- [ ] 낙관적 업데이트 동작
- [ ] 롤백 메커니즘 확인
- [ ] 배치 작업 처리
- [ ] Undo/Redo 기능

#### SubTask 7.5.4: 캐싱 전략 및 백그라운드 리페칭 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/lib/react-query/cache-strategies.ts
import { QueryClient } from '@tanstack/react-query';

export interface CacheStrategy {
  staleTime?: number;
  cacheTime?: number;
  refetchInterval?: number | false | ((data: any) => number | false);
  refetchOnWindowFocus?: boolean | 'always';
  refetchOnReconnect?: boolean | 'always';
  refetchOnMount?: boolean | 'always';
}

// Predefined cache strategies
export const cacheStrategies = {
  // Real-time data (agent status, metrics)
  realtime: {
    staleTime: 0,
    cacheTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5000, // 5 seconds
    refetchOnWindowFocus: 'always',
    refetchOnReconnect: 'always'
  } as CacheStrategy,
  
  // Frequently changing data (projects, workflows)
  frequent: {
    staleTime: 30 * 1000, // 30 seconds
    cacheTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 60 * 1000, // 1 minute
    refetchOnWindowFocus: true,
    refetchOnReconnect: true
  } as CacheStrategy,
  
  // Moderate change frequency (user data, settings)
  moderate: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
    refetchInterval: false,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true
  } as CacheStrategy,
  
  // Rarely changing data (configurations, templates)
  static: {
    staleTime: 60 * 60 * 1000, // 1 hour
    cacheTime: 24 * 60 * 60 * 1000, // 24 hours
    refetchInterval: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false
  } as CacheStrategy,
  
  // Infinite cache (never refetch automatically)
  infinite: {
    staleTime: Infinity,
    cacheTime: Infinity,
    refetchInterval: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false
  } as CacheStrategy
};

// Background sync manager
export class BackgroundSyncManager {
  private syncTasks: Map<string, NodeJS.Timer> = new Map();
  private queryClient: QueryClient;
  
  constructor(queryClient: QueryClient) {
    this.queryClient = queryClient;
    this.setupVisibilityListener();
    this.setupNetworkListener();
  }
  
  // Register background sync task
  registerSync(
    key: string,
    queryKey: readonly unknown[],
    interval: number
  ) {
    // Clear existing sync if any
    this.clearSync(key);
    
    // Setup new sync
    const timer = setInterval(() => {
      this.queryClient.invalidateQueries(queryKey);
    }, interval);
    
    this.syncTasks.set(key, timer);
  }
  
  // Clear sync task
  clearSync(key: string) {
    const timer = this.syncTasks.get(key);
    if (timer) {
      clearInterval(timer);
      this.syncTasks.delete(key);
    }
  }
  
  // Clear all sync tasks
  clearAll() {
    this.syncTasks.forEach(timer => clearInterval(timer));
    this.syncTasks.clear();
  }
  
  // Setup visibility change listener
  private setupVisibilityListener() {
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        // Refetch important queries when page becomes visible
        this.queryClient.invalidateQueries({
          predicate: (query) => {
            const options = query.options;
            return options.refetchOnWindowFocus === 'always' ||
                   (options.refetchOnWindowFocus && query.isStale());
          }
        });
      }
    });
  }
  
  // Setup network status listener
  private setupNetworkListener() {
    window.addEventListener('online', () => {
      // Refetch queries when coming back online
      this.queryClient.invalidateQueries({
        predicate: (query) => {
          const options = query.options;
          return options.refetchOnReconnect === 'always' ||
                 (options.refetchOnReconnect && query.isStale());
        }
      });
    });
  }
}

// Cache utilities
export const cacheUtils = {
  // Prefetch data
  prefetch: async (
    queryClient: QueryClient,
    queryKey: readonly unknown[],
    queryFn: () => Promise<any>,
    strategy: CacheStrategy = cacheStrategies.moderate
  ) => {
    await queryClient.prefetchQuery({
      queryKey,
      queryFn,
      ...strategy
    });
  },
  
  // Selective cache invalidation
  invalidatePattern: (
    queryClient: QueryClient,
    pattern: string | RegExp
  ) => {
    queryClient.invalidateQueries({
      predicate: (query) => {
        const key = JSON.stringify(query.queryKey);
        return typeof pattern === 'string' 
          ? key.includes(pattern)
          : pattern.test(key);
      }
    });
  },
  
  // Clear old cache entries
  clearStaleCache: (
    queryClient: QueryClient,
    maxAge: number = 24 * 60 * 60 * 1000 // 24 hours
  ) => {
    const now = Date.now();
    
    queryClient.getQueryCache().getAll().forEach(query => {
      const lastUpdated = query.state.dataUpdatedAt;
      if (now - lastUpdated > maxAge) {
        queryClient.removeQueries(query.queryKey);
      }
    });
  },
  
  // Get cache size
  getCacheSize: (queryClient: QueryClient) => {
    const cache = queryClient.getQueryCache();
    const queries = cache.getAll();
    
    let totalSize = 0;
    queries.forEach(query => {
      const dataStr = JSON.stringify(query.state.data);
      totalSize += new Blob([dataStr]).size;
    });
    
    return {
      queryCount: queries.length,
      sizeInBytes: totalSize,
      sizeInMB: (totalSize / (1024 * 1024)).toFixed(2)
    };
  }
};
```

```typescript
// frontend/src/hooks/useBackgroundSync.ts
import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { BackgroundSyncManager } from '@/lib/react-query/cache-strategies';

export function useBackgroundSync() {
  const queryClient = useQueryClient();
  const syncManagerRef = useRef<BackgroundSyncManager>();
  
  useEffect(() => {
    // Initialize sync manager
    syncManagerRef.current = new BackgroundSyncManager(queryClient);
    
    // Register critical background syncs
    const syncManager = syncManagerRef.current;
    
    // Sync agent status every 10 seconds
    syncManager.registerSync(
      'agent-status',
      ['agents'],
      10000
    );
    
    // Sync active workflows every 30 seconds
    syncManager.registerSync(
      'active-workflows',
      ['workflows', { status: 'running' }],
      30000
    );
    
    // Sync notifications every minute
    syncManager.registerSync(
      'notifications',
      ['notifications'],
      60000
    );
    
    // Cleanup on unmount
    return () => {
      syncManager.clearAll();
    };
  }, [queryClient]);
  
  return syncManagerRef.current;
}
```

**검증 기준**:
- [ ] 캐싱 전략 적용
- [ ] 백그라운드 동기화
- [ ] 캐시 관리 유틸리티
- [ ] 네트워크 상태 대응

---

### Task 7.6: WebSocket 실시간 통신 구현

#### SubTask 7.6.1: Socket.io 클라이언트 설정 및 연결 관리
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/lib/websocket/socket-client.ts
import { io, Socket } from 'socket.io-client';
import { EventEmitter } from 'events';

export interface SocketConfig {
  url: string;
  path?: string;
  transports?: string[];
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  reconnectionDelayMax?: number;
  timeout?: number;
  autoConnect?: boolean;
  auth?: Record<string, any>;
}

export class SocketClient extends EventEmitter {
  private socket: Socket | null = null;
  private config: SocketConfig;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private connectionState: 'disconnected' | 'connecting' | 'connected' | 'error' = 'disconnected';
  private messageQueue: Array<{ event: string; data: any }> = [];
  private eventHandlers: Map<string, Set<Function>> = new Map();
  
  constructor(config: SocketConfig) {
    super();
    this.config = {
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      autoConnect: true,
      transports: ['websocket', 'polling'],
      ...config
    };
    
    if (this.config.autoConnect) {
      this.connect();
    }
  }
  
  connect(): void {
    if (this.socket?.connected) {
      console.log('Socket already connected');
      return;
    }
    
    this.connectionState = 'connecting';
    this.emit('connecting');
    
    // Get auth token
    const token = localStorage.getItem('accessToken');
    
    this.socket = io(this.config.url, {
      path: this.config.path,
      transports: this.config.transports,
      reconnection: this.config.reconnection,
      reconnectionAttempts: this.config.reconnectionAttempts,
      reconnectionDelay: this.config.reconnectionDelay,
      reconnectionDelayMax: this.config.reconnectionDelayMax,
      timeout: this.config.timeout,
      auth: {
        ...this.config.auth,
        token
      }
    });
    
    this.setupEventListeners();
  }
  
  private setupEventListeners(): void {
    if (!this.socket) return;
    
    // Connection events
    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
      this.connectionState = 'connected';
      this.emit('connected');
      this.flushMessageQueue();
    });
    
    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      this.connectionState = 'disconnected';
      this.emit('disconnected', reason);
      
      if (reason === 'io server disconnect') {
        // Server disconnected, try to reconnect
        this.reconnect();
      }
    });
    
    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      this.connectionState = 'error';
      this.emit('error', error);
    });
    
    // Reconnection events
    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts');
      this.emit('reconnected', attemptNumber);
    });
    
    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log('Socket reconnection attempt:', attemptNumber);
      this.emit('reconnect_attempt', attemptNumber);
    });
    
    this.socket.on('reconnect_failed', () => {
      console.error('Socket reconnection failed');
      this.connectionState = 'error';
      this.emit('reconnect_failed');
    });
    
    // Custom events
    this.socket.onAny((event, ...args) => {
      this.handleIncomingMessage(event, args[0]);
    });
  }
  
  private handleIncomingMessage(event: string, data: any): void {
    // Emit to local listeners
    this.emit(event, data);
    
    // Call registered handlers
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in handler for event ${event}:`, error);
        }
      });
    }
  }
  
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    
    this.connectionState = 'disconnected';
    this.emit('disconnected', 'manual');
  }
  
  reconnect(): void {
    if (this.connectionState === 'connecting') {
      return;
    }
    
    this.disconnect();
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.config.reconnectionDelay);
  }
  
  emit(event: string, data?: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      // Queue message for later
      this.messageQueue.push({ event, data });
    }
  }
  
  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
    
    // Also register with socket if connected
    if (this.socket) {
      this.socket.on(event, handler as any);
    }
  }
  
  off(event: string, handler?: Function): void {
    if (handler) {
      this.eventHandlers.get(event)?.delete(handler);
      this.socket?.off(event, handler as any);
    } else {
      this.eventHandlers.delete(event);
      this.socket?.off(event);
    }
  }
  
  once(event: string, handler: Function): void {
    const wrappedHandler = (...args: any[]) => {
      handler(...args);
      this.off(event, wrappedHandler);
    };
    this.on(event, wrappedHandler);
  }
  
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.emit(message.event, message.data);
      }
    }
  }
  
  getState(): string {
    return this.connectionState;
  }
  
  isConnected(): boolean {
    return this.connectionState === 'connected';
  }
  
  getSocketId(): string | undefined {
    return this.socket?.id;
  }
}

// Singleton instance
let socketInstance: SocketClient | null = null;

export function getSocketClient(): SocketClient {
  if (!socketInstance) {
    socketInstance = new SocketClient({
      url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
      path: '/socket.io'
    });
  }
  return socketInstance;
}
```

**검증 기준**:
- [ ] WebSocket 연결 확립
- [ ] 자동 재연결 메커니즘
- [ ] 메시지 큐잉 시스템
- [ ] 이벤트 핸들러 관리

#### SubTask 7.6.2: 실시간 이벤트 핸들러 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/lib/websocket/event-handlers.ts
import { getSocketClient } from './socket-client';
import useAppStore from '@/store';
import { queryClient } from '@/lib/react-query/client';
import { toast } from 'react-hot-toast';

export interface RealtimeEvent {
  type: string;
  payload: any;
  timestamp: string;
  correlationId?: string;
  userId?: string;
}

export class RealtimeEventHandler {
  private socket = getSocketClient();
  private handlers: Map<string, Function[]> = new Map();
  
  constructor() {
    this.setupDefaultHandlers();
  }
  
  private setupDefaultHandlers(): void {
    // Agent status updates
    this.registerHandler('agent:status', (data: any) => {
      const { agentId, status, metrics } = data;
      
      // Update store
      const store = useAppStore.getState();
      store.updateAgentStatus(agentId, status);
      
      // Update React Query cache
      queryClient.setQueryData(
        ['agents', 'detail', agentId],
        (old: any) => ({
          ...old,
          status,
          lastHeartbeat: new Date(),
          metrics
        })
      );
    });
    
    // Workflow execution updates
    this.registerHandler('workflow:execution', (data: any) => {
      const { workflowId, executionId, status, progress } = data;
      
      // Update workflow execution cache
      queryClient.setQueryData(
        ['workflow-execution', executionId],
        (old: any) => ({
          ...old,
          status,
          progress,
          updatedAt: new Date()
        })
      );
      
      // Show notification for completion
      if (status === 'completed') {
        toast.success(`Workflow execution completed: ${workflowId}`);
      } else if (status === 'failed') {
        toast.error(`Workflow execution failed: ${workflowId}`);
      }
    });
    
    // Project updates
    this.registerHandler('project:update', (data: any) => {
      const { projectId, updates } = data;
      
      // Update project cache
      queryClient.setQueryData(
        ['projects', 'detail', projectId],
        (old: any) => ({
          ...old,
          ...updates,
          updatedAt: new Date()
        })
      );
      
      // Invalidate project list
      queryClient.invalidateQueries(['projects', 'list']);
    });
    
    // Real-time notifications
    this.registerHandler('notification', (data: any) => {
      const { id, type, title, message, severity } = data;
      
      // Add to notification store
      const store = useAppStore.getState();
      store.addNotification({
        id,
        type,
        title,
        message,
        severity,
        timestamp: new Date(),
        read: false
      });
      
      // Show toast based on severity
      switch (severity) {
        case 'success':
          toast.success(message);
          break;
        case 'error':
          toast.error(message);
          break;
        case 'warning':
          toast(message, { icon: '⚠️' });
          break;
        default:
          toast(message);
      }
    });
    
    // Agent logs streaming
    this.registerHandler('agent:log', (data: any) => {
      const { agentId, level, message, timestamp } = data;
      
      // Append to logs cache
      queryClient.setQueryData(
        ['agents', 'logs', agentId],
        (old: any) => {
          const logs = old?.logs || [];
          return {
            ...old,
            logs: [...logs, { level, message, timestamp }].slice(-1000) // Keep last 1000 logs
          };
        }
      );
    });
    
    // System metrics
    this.registerHandler('system:metrics', (data: any) => {
      const { cpu, memory, disk, network } = data;
      
      // Update system metrics in store
      const store = useAppStore.getState();
      store.updateSystemMetrics({
        cpu,
        memory,
        disk,
        network,
        timestamp: new Date()
      });
    });
    
    // Collaboration events
    this.registerHandler('collaboration:user-joined', (data: any) => {
      const { userId, userName, projectId } = data;
      toast(`${userName} joined the project`);
      
      // Update active users
      queryClient.setQueryData(
        ['project', 'active-users', projectId],
        (old: any) => {
          const users = old || [];
          return [...users, { userId, userName, joinedAt: new Date() }];
        }
      );
    });
    
    this.registerHandler('collaboration:user-left', (data: any) => {
      const { userId, userName, projectId } = data;
      
      // Update active users
      queryClient.setQueryData(
        ['project', 'active-users', projectId],
        (old: any) => {
          const users = old || [];
          return users.filter((u: any) => u.userId !== userId);
        }
      );
    });
  }
  
  registerHandler(event: string, handler: Function): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
      
      // Register with socket
      this.socket.on(event, (data: any) => {
        const handlers = this.handlers.get(event) || [];
        handlers.forEach(h => {
          try {
            h(data);
          } catch (error) {
            console.error(`Error in handler for ${event}:`, error);
          }
        });
      });
    }
    
    this.handlers.get(event)!.push(handler);
  }
  
  unregisterHandler(event: string, handler?: Function): void {
    if (handler) {
      const handlers = this.handlers.get(event);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    } else {
      this.handlers.delete(event);
      this.socket.off(event);
    }
  }
  
  // Subscribe to specific channels
  subscribeToProject(projectId: string): void {
    this.socket.emit('subscribe', {
      channel: `project:${projectId}`
    });
  }
  
  unsubscribeFromProject(projectId: string): void {
    this.socket.emit('unsubscribe', {
      channel: `project:${projectId}`
    });
  }
  
  subscribeToAgent(agentId: string): void {
    this.socket.emit('subscribe', {
      channel: `agent:${agentId}`
    });
  }
  
  unsubscribeFromAgent(agentId: string): void {
    this.socket.emit('unsubscribe', {
      channel: `agent:${agentId}`
    });
  }
  
  subscribeToWorkflow(workflowId: string): void {
    this.socket.emit('subscribe', {
      channel: `workflow:${workflowId}`
    });
  }
  
  unsubscribeFromWorkflow(workflowId: string): void {
    this.socket.emit('unsubscribe', {
      channel: `workflow:${workflowId}`
    });
  }
}

// Singleton instance
export const realtimeEventHandler = new RealtimeEventHandler();
```

**검증 기준**:
- [ ] 이벤트 핸들러 등록
- [ ] 실시간 상태 업데이트
- [ ] 채널 구독/구독 해제
- [ ] 에러 처리 메커니즘

#### SubTask 7.6.3: WebSocket Context 및 훅 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/contexts/WebSocketContext.tsx
import React, { 
  createContext, 
  useContext, 
  useEffect, 
  useState, 
  useCallback, 
  useRef 
} from 'react';
import { getSocketClient, SocketClient } from '@/lib/websocket/socket-client';
import { realtimeEventHandler } from '@/lib/websocket/event-handlers';
import useAppStore from '@/store';

interface WebSocketContextValue {
  socket: SocketClient;
  isConnected: boolean;
  connectionState: string;
  emit: (event: string, data?: any) => void;
  on: (event: string, handler: Function) => void;
  off: (event: string, handler?: Function) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  reconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const socket = useRef<SocketClient>(getSocketClient());
  const [isConnected, setIsConnected] = useState(socket.current.isConnected());
  const [connectionState, setConnectionState] = useState(socket.current.getState());
  const isAuthenticated = useAppStore(state => state.isAuthenticated);
  
  useEffect(() => {
    const client = socket.current;
    
    // Connection state listeners
    const handleConnected = () => {
      setIsConnected(true);
      setConnectionState('connected');
      console.log('WebSocket connected');
    };
    
    const handleDisconnected = () => {
      setIsConnected(false);
      setConnectionState('disconnected');
      console.log('WebSocket disconnected');
    };
    
    const handleError = (error: Error) => {
      setConnectionState('error');
      console.error('WebSocket error:', error);
    };
    
    const handleReconnected = () => {
      setIsConnected(true);
      setConnectionState('connected');
      console.log('WebSocket reconnected');
      
      // Re-subscribe to channels after reconnection
      resubscribeToChannels();
    };
    
    client.on('connected', handleConnected);
    client.on('disconnected', handleDisconnected);
    client.on('error', handleError);
    client.on('reconnected', handleReconnected);
    
    // Connect if authenticated
    if (isAuthenticated && !client.isConnected()) {
      client.connect();
    }
    
    return () => {
      client.off('connected', handleConnected);
      client.off('disconnected', handleDisconnected);
      client.off('error', handleError);
      client.off('reconnected', handleReconnected);
    };
  }, [isAuthenticated]);
  
  const resubscribeToChannels = useCallback(() => {
    const state = useAppStore.getState();
    
    // Re-subscribe to current project
    if (state.currentProject) {
      realtimeEventHandler.subscribeToProject(state.currentProject.id);
    }
    
    // Re-subscribe to active agents
    state.agents
      .filter(a => ['ready', 'running'].includes(a.status))
      .forEach(agent => {
        realtimeEventHandler.subscribeToAgent(agent.id);
      });
  }, []);
  
  const emit = useCallback((event: string, data?: any) => {
    socket.current.emit(event, data);
  }, []);
  
  const on = useCallback((event: string, handler: Function) => {
    socket.current.on(event, handler);
  }, []);
  
  const off = useCallback((event: string, handler?: Function) => {
    socket.current.off(event, handler);
  }, []);
  
  const subscribe = useCallback((channel: string) => {
    socket.current.emit('subscribe', { channel });
  }, []);
  
  const unsubscribe = useCallback((channel: string) => {
    socket.current.emit('unsubscribe', { channel });
  }, []);
  
  const reconnect = useCallback(() => {
    socket.current.reconnect();
  }, []);
  
  const value: WebSocketContextValue = {
    socket: socket.current,
    isConnected,
    connectionState,
    emit,
    on,
    off,
    subscribe,
    unsubscribe,
    reconnect
  };
  
  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Hook to use WebSocket context
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

// Hook for subscribing to events
export const useSocketEvent = (
  event: string,
  handler: (data: any) => void,
  deps: React.DependencyList = []
) => {
  const { on, off } = useWebSocket();
  
  useEffect(() => {
    on(event, handler);
    return () => off(event, handler);
  }, [event, ...deps]);
};

// Hook for emitting events
export const useSocketEmit = () => {
  const { emit } = useWebSocket();
  return emit;
};

// Hook for channel subscription
export const useSocketChannel = (channel: string, enabled = true) => {
  const { subscribe, unsubscribe } = useWebSocket();
  
  useEffect(() => {
    if (enabled) {
      subscribe(channel);
      return () => unsubscribe(channel);
    }
  }, [channel, enabled, subscribe, unsubscribe]);
};

// Hook for connection state
export const useSocketConnection = () => {
  const { isConnected, connectionState, reconnect } = useWebSocket();
  return { isConnected, connectionState, reconnect };
};
```

**검증 기준**:
- [ ] Context Provider 동작
- [ ] Custom hooks 기능
- [ ] 이벤트 구독/해제
- [ ] 연결 상태 관리

#### SubTask 7.6.4: 재연결 로직 및 오류 처리
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/lib/websocket/reconnection-manager.ts
export interface ReconnectionConfig {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitter: boolean;
}

export class ReconnectionManager {
  private config: ReconnectionConfig;
  private attempts = 0;
  private timer: NodeJS.Timeout | null = null;
  private isReconnecting = false;
  
  constructor(config: Partial<ReconnectionConfig> = {}) {
    this.config = {
      maxAttempts: 10,
      initialDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 1.5,
      jitter: true,
      ...config
    };
  }
  
  async attemptReconnection(
    connectFn: () => Promise<void>,
    onSuccess?: () => void,
    onFailure?: (error: Error) => void
  ): Promise<void> {
    if (this.isReconnecting) {
      console.log('Already reconnecting...');
      return;
    }
    
    this.isReconnecting = true;
    
    while (this.attempts < this.config.maxAttempts) {
      this.attempts++;
      
      try {
        console.log(`Reconnection attempt ${this.attempts}/${this.config.maxAttempts}`);
        await connectFn();
        
        // Success
        this.reset();
        onSuccess?.();
        return;
        
      } catch (error) {
        console.error(`Reconnection attempt ${this.attempts} failed:`, error);
        
        if (this.attempts >= this.config.maxAttempts) {
          // Max attempts reached
          this.isReconnecting = false;
          onFailure?.(new Error('Max reconnection attempts reached'));
          return;
        }
        
        // Wait before next attempt
        const delay = this.calculateDelay();
        console.log(`Waiting ${delay}ms before next attempt...`);
        
        await new Promise(resolve => {
          this.timer = setTimeout(resolve, delay);
        });
      }
    }
  }
  
  private calculateDelay(): number {
    const baseDelay = Math.min(
      this.config.initialDelay * Math.pow(this.config.backoffMultiplier, this.attempts - 1),
      this.config.maxDelay
    );
    
    if (this.config.jitter) {
      // Add random jitter (±25%)
      const jitter = baseDelay * 0.25 * (Math.random() * 2 - 1);
      return Math.round(baseDelay + jitter);
    }
    
    return baseDelay;
  }
  
  reset(): void {
    this.attempts = 0;
    this.isReconnecting = false;
    
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
  
  getAttempts(): number {
    return this.attempts;
  }
  
  isActive(): boolean {
    return this.isReconnecting;
  }
}

// Error recovery strategies
export class ErrorRecoveryManager {
  private errorCounts: Map<string, number> = new Map();
  private errorTimestamps: Map<string, number[]> = new Map();
  private recoveryStrategies: Map<string, () => void> = new Map();
  
  recordError(type: string, error: Error): void {
    // Increment error count
    const count = (this.errorCounts.get(type) || 0) + 1;
    this.errorCounts.set(type, count);
    
    // Record timestamp
    const timestamps = this.errorTimestamps.get(type) || [];
    timestamps.push(Date.now());
    
    // Keep only recent timestamps (last 5 minutes)
    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
    const recentTimestamps = timestamps.filter(t => t > fiveMinutesAgo);
    this.errorTimestamps.set(type, recentTimestamps);
    
    // Check if recovery action needed
    this.checkRecoveryNeeded(type, recentTimestamps.length);
  }
  
  private checkRecoveryNeeded(type: string, recentErrorCount: number): void {
    // If more than 5 errors in 5 minutes, trigger recovery
    if (recentErrorCount > 5) {
      const strategy = this.recoveryStrategies.get(type);
      if (strategy) {
        console.log(`Triggering recovery strategy for ${type}`);
        strategy();
        
        // Reset error count after recovery
        this.errorCounts.set(type, 0);
        this.errorTimestamps.set(type, []);
      }
    }
  }
  
  registerRecoveryStrategy(type: string, strategy: () => void): void {
    this.recoveryStrategies.set(type, strategy);
  }
  
  getErrorStats(type: string): { count: number; recentCount: number } {
    const count = this.errorCounts.get(type) || 0;
    const timestamps = this.errorTimestamps.get(type) || [];
    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
    const recentCount = timestamps.filter(t => t > fiveMinutesAgo).length;
    
    return { count, recentCount };
  }
  
  reset(type?: string): void {
    if (type) {
      this.errorCounts.delete(type);
      this.errorTimestamps.delete(type);
    } else {
      this.errorCounts.clear();
      this.errorTimestamps.clear();
    }
  }
}
```

```typescript
// frontend/src/components/common/ConnectionStatus.tsx
import React, { useEffect, useState } from 'react';
import { Alert, Snackbar, CircularProgress, Button } from '@mui/material';
import { useSocketConnection } from '@/contexts/WebSocketContext';

export const ConnectionStatus: React.FC = () => {
  const { isConnected, connectionState, reconnect } = useSocketConnection();
  const [showStatus, setShowStatus] = useState(false);
  const [autoHideTimer, setAutoHideTimer] = useState<NodeJS.Timeout | null>(null);
  
  useEffect(() => {
    if (connectionState === 'error' || connectionState === 'disconnected') {
      setShowStatus(true);
      
      // Clear existing timer
      if (autoHideTimer) {
        clearTimeout(autoHideTimer);
      }
    } else if (connectionState === 'connected') {
      // Auto-hide after 3 seconds when connected
      const timer = setTimeout(() => {
        setShowStatus(false);
      }, 3000);
      setAutoHideTimer(timer);
    }
    
    return () => {
      if (autoHideTimer) {
        clearTimeout(autoHideTimer);
      }
    };
  }, [connectionState]);
  
  const handleReconnect = () => {
    reconnect();
  };
  
  const getSeverity = () => {
    switch (connectionState) {
      case 'connected':
        return 'success';
      case 'connecting':
        return 'info';
      case 'disconnected':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };
  
  const getMessage = () => {
    switch (connectionState) {
      case 'connected':
        return 'Connected to server';
      case 'connecting':
        return 'Connecting to server...';
      case 'disconnected':
        return 'Disconnected from server';
      case 'error':
        return 'Connection error';
      default:
        return 'Unknown connection state';
    }
  };
  
  return (
    <Snackbar
      open={showStatus}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      onClose={() => setShowStatus(false)}
    >
      <Alert
        severity={getSeverity()}
        action={
          connectionState === 'disconnected' || connectionState === 'error' ? (
            <Button color="inherit" size="small" onClick={handleReconnect}>
              Reconnect
            </Button>
          ) : connectionState === 'connecting' ? (
            <CircularProgress size={20} color="inherit" />
          ) : null
        }
      >
        {getMessage()}
      </Alert>
    </Snackbar>
  );
};
```

**검증 기준**:
- [ ] 재연결 전략 구현
- [ ] 에러 복구 메커니즘
- [ ] 연결 상태 UI 표시
- [ ] 백오프 알고리즘 동작

---

### Task 7.7: React Router 설정 및 라우트 구조

#### SubTask 7.7.1: 라우터 기본 설정 및 라우트 정의
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/routes/routes.config.ts
import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';
import { 
  DashboardIcon, 
  ProjectIcon, 
  AgentIcon, 
  WorkflowIcon,
  AnalyticsIcon,
  SettingsIcon 
} from '@/components/icons';

export interface RouteConfig extends RouteObject {
  path: string;
  title?: string;
  icon?: React.ComponentType;
  breadcrumb?: string | ((params: any) => string);
  permissions?: string[];
  showInMenu?: boolean;
  children?: RouteConfig[];
  meta?: {
    requiresAuth?: boolean;
    layout?: 'main' | 'auth' | 'blank';
    transition?: 'fade' | 'slide' | 'zoom';
  };
}

// Lazy load pages
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Projects = lazy(() => import('@/pages/Projects'));
const ProjectDetail = lazy(() => import('@/pages/Projects/ProjectDetail'));
const ProjectCreate = lazy(() => import('@/pages/Projects/ProjectCreate'));
const Agents = lazy(() => import('@/pages/Agents'));
const AgentDetail = lazy(() => import('@/pages/Agents/AgentDetail'));
const Workflows = lazy(() => import('@/pages/Workflows'));
const WorkflowBuilder = lazy(() => import('@/pages/Workflows/Builder'));
const WorkflowExecution = lazy(() => import('@/pages/Workflows/Execution'));
const Analytics = lazy(() => import('@/pages/Analytics'));
const Settings = lazy(() => import('@/pages/Settings'));
const Profile = lazy(() => import('@/pages/Settings/Profile'));
const Team = lazy(() => import('@/pages/Settings/Team'));
const Billing = lazy(() => import('@/pages/Settings/Billing'));
const Login = lazy(() => import('@/pages/Auth/Login'));
const Register = lazy(() => import('@/pages/Auth/Register'));
const ForgotPassword = lazy(() => import('@/pages/Auth/ForgotPassword'));
const NotFound = lazy(() => import('@/pages/NotFound'));

export const routes: RouteConfig[] = [
  // Auth routes
  {
    path: '/login',
    element: <Login />,
    title: 'Login',
    meta: {
      requiresAuth: false,
      layout: 'auth'
    }
  },
  {
    path: '/register',
    element: <Register />,
    title: 'Register',
    meta: {
      requiresAuth: false,
      layout: 'auth'
    }
  },
  {
    path: '/forgot-password',
    element: <ForgotPassword />,
    title: 'Forgot Password',
    meta: {
      requiresAuth: false,
      layout: 'auth'
    }
  },
  
  // Main app routes
  {
    path: '/',
    title: 'Dashboard',
    element: <Dashboard />,
    icon: DashboardIcon,
    breadcrumb: 'Dashboard',
    showInMenu: true,
    meta: {
      requiresAuth: true,
      layout: 'main'
    }
  },
  {
    path: '/projects',
    title: 'Projects',
    icon: ProjectIcon,
    breadcrumb: 'Projects',
    showInMenu: true,
    permissions: ['projects:view'],
    meta: {
      requiresAuth: true,
      layout: 'main'
    },
    children: [
      {
        path: '',
        element: <Projects />,
        title: 'All Projects'
      },
      {
        path: 'new',
        element: <ProjectCreate />,
        title: 'Create Project',
        breadcrumb: 'New Project',
        permissions: ['projects:create']
      },
      {
        path: ':projectId',
        element: <ProjectDetail />,
        breadcrumb: (params) => `Project ${params.projectId}`,
        permissions: ['projects:view']
      },
      {
        path: ':projectId/edit',
        element: <ProjectCreate />,
        breadcrumb: 'Edit Project',
        permissions: ['projects:edit']
      }
    ]
  },
  {
    path: '/agents',
    title: 'Agents',
    icon: AgentIcon,
    breadcrumb: 'Agents',
    showInMenu: true,
    permissions: ['agents:view'],
    meta: {
      requiresAuth: true,
      layout: 'main'
    },
    children: [
      {
        path: '',
        element: <Agents />,
        title: 'All Agents'
      },
      {
        path: ':agentId',
        element: <AgentDetail />,
        breadcrumb: (params) => `Agent ${params.agentId}`
      }
    ]
  },
  {
    path: '/workflows',
    title: 'Workflows',
    icon: WorkflowIcon,
    breadcrumb: 'Workflows',
    showInMenu: true,
    permissions: ['workflows:view'],
    meta: {
      requiresAuth: true,
      layout: 'main'
    },
    children: [
      {
        path: '',
        element: <Workflows />,
        title: 'All Workflows'
      },
      {
        path: 'builder',
        element: <WorkflowBuilder />,
        title: 'Workflow Builder',
        breadcrumb: 'Builder',
        permissions: ['workflows:create']
      },
      {
        path: ':workflowId/execution/:executionId',
        element: <WorkflowExecution />,
        breadcrumb: (params) => `Execution ${params.executionId}`
      }
    ]
  },
  {
    path: '/analytics',
    element: <Analytics />,
    title: 'Analytics',
    icon: AnalyticsIcon,
    breadcrumb: 'Analytics',
    showInMenu: true,
    permissions: ['analytics:view'],
    meta: {
      requiresAuth: true,
      layout: 'main'
    }
  },
  {
    path: '/settings',
    title: 'Settings',
    icon: SettingsIcon,
    breadcrumb: 'Settings',
    showInMenu: true,
    meta: {
      requiresAuth: true,
      layout: 'main'
    },
    children: [
      {
        path: '',
        element: <Settings />,
        title: 'General Settings'
      },
      {
        path: 'profile',
        element: <Profile />,
        title: 'Profile',
        breadcrumb: 'Profile'
      },
      {
        path: 'team',
        element: <Team />,
        title: 'Team',
        breadcrumb: 'Team',
        permissions: ['team:view']
      },
      {
        path: 'billing',
        element: <Billing />,
        title: 'Billing',
        breadcrumb: 'Billing',
        permissions: ['billing:view']
      }
    ]
  },
  
  // 404 route
  {
    path: '*',
    element: <NotFound />,
    title: '404 Not Found',
    meta: {
      layout: 'blank'
    }
  }
];

// Helper to get flattened routes
export function getFlattenedRoutes(routes: RouteConfig[]): RouteConfig[] {
  const flatRoutes: RouteConfig[] = [];
  
  const flatten = (routes: RouteConfig[], parentPath = '') => {
    routes.forEach(route => {
      const fullPath = parentPath ? `${parentPath}/${route.path}` : route.path;
      flatRoutes.push({ ...route, path: fullPath });
      
      if (route.children) {
        flatten(route.children, fullPath);
      }
    });
  };
  
  flatten(routes);
  return flatRoutes;
}

// Helper to get menu items
export function getMenuItems(routes: RouteConfig[]): RouteConfig[] {
  return routes.filter(route => route.showInMenu);
}
```

**검증 기준**:
- [ ] 라우트 구조 정의
- [ ] Lazy loading 설정
- [ ] 라우트 메타데이터
- [ ] 중첩 라우트 처리

# Phase 7: 프론트엔드 구현 - Tasks 7.7-7.8 SubTask 작업지시서 (계속)

### Task 7.7: React Router 설정 및 라우트 구조 (계속)

#### SubTask 7.7.2: 보호된 라우트 및 권한 관리
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/routes/ProtectedRoute.tsx
import React, { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import useAppStore from '@/store';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  permissions?: string[];
  redirectTo?: string;
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  permissions = [],
  redirectTo = '/login',
  children
}) => {
  const location = useLocation();
  const { isAuthenticated, isLoading, verifyToken } = useAuth();
  const hasPermission = useAppStore(state => state.hasPermission);
  const hasAllPermissions = useAppStore(state => state.hasAllPermissions);
  
  useEffect(() => {
    // Verify token on mount
    verifyToken();
  }, []);
  
  // Show loading while checking auth
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }
  
  // Check authentication
  if (!isAuthenticated) {
    // Save the attempted location for redirect after login
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }
  
  // Check permissions if specified
  if (permissions.length > 0 && !hasAllPermissions(permissions)) {
    return <Navigate to="/403" replace />;
  }
  
  // Render children or outlet
  return children ? <>{children}</> : <Outlet />;
};

// Role-based route wrapper
export const RoleBasedRoute: React.FC<{
  roles: string[];
  children: React.ReactNode;
}> = ({ roles, children }) => {
  const userRole = useAppStore(state => state.user?.role);
  
  if (!userRole || !roles.includes(userRole)) {
    return <Navigate to="/403" replace />;
  }
  
  return <>{children}</>;
};

// Permission check component
export const PermissionGate: React.FC<{
  permissions: string[];
  fallback?: React.ReactNode;
  children: React.ReactNode;
}> = ({ permissions, fallback = null, children }) => {
  const hasAllPermissions = useAppStore(state => state.hasAllPermissions);
  
  if (!hasAllPermissions(permissions)) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
};
```

```typescript
// frontend/src/routes/AuthGuard.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import useAppStore from '@/store';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  requiredRoles?: string[];
  redirectTo?: string;
  requireVerified?: boolean;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requiredPermissions = [],
  requiredRoles = [],
  redirectTo = '/login',
  requireVerified = false
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  
  const {
    isAuthenticated,
    user,
    hasAllPermissions,
    verifyToken
  } = useAppStore();
  
  useEffect(() => {
    checkAuthorization();
  }, [isAuthenticated, user]);
  
  const checkAuthorization = async () => {
    // Check authentication
    if (!isAuthenticated) {
      const tokenValid = await verifyToken();
      if (!tokenValid) {
        navigate(redirectTo, {
          state: { from: location.pathname }
        });
        return;
      }
    }
    
    // Check email verification if required
    if (requireVerified && user && !user.emailVerified) {
      navigate('/verify-email');
      return;
    }
    
    // Check roles
    if (requiredRoles.length > 0) {
      const hasRole = requiredRoles.some(role => user?.role === role);
      if (!hasRole) {
        navigate('/403');
        return;
      }
    }
    
    // Check permissions
    if (requiredPermissions.length > 0) {
      if (!hasAllPermissions(requiredPermissions)) {
        navigate('/403');
        return;
      }
    }
    
    setIsAuthorized(true);
  };
  
  if (isAuthorized === null) {
    return <div>Checking authorization...</div>;
  }
  
  if (!isAuthorized) {
    return null;
  }
  
  return <>{children}</>;
};
```

```typescript
// frontend/src/routes/RouteGuardProvider.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import useAppStore from '@/store';

interface RouteGuardContextValue {
  canAccess: (path: string) => boolean;
  guardedNavigate: (path: string) => void;
  previousPath: string | null;
}

const RouteGuardContext = createContext<RouteGuardContextValue | null>(null);

export const RouteGuardProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [previousPath, setPreviousPath] = useState<string | null>(null);
  const { isAuthenticated, permissions } = useAppStore();
  
  useEffect(() => {
    // Track previous path
    setPreviousPath(location.pathname);
  }, [location]);
  
  const canAccess = (path: string): boolean => {
    // Get route config for path
    const route = findRouteByPath(path);
    if (!route) return true;
    
    // Check authentication requirement
    if (route.meta?.requiresAuth && !isAuthenticated) {
      return false;
    }
    
    // Check permissions
    if (route.permissions?.length) {
      return route.permissions.every(p => permissions.includes(p));
    }
    
    return true;
  };
  
  const guardedNavigate = (path: string) => {
    if (canAccess(path)) {
      navigate(path);
    } else {
      // Redirect to login or 403
      if (!isAuthenticated) {
        navigate('/login', { state: { from: path } });
      } else {
        navigate('/403');
      }
    }
  };
  
  const value: RouteGuardContextValue = {
    canAccess,
    guardedNavigate,
    previousPath
  };
  
  return (
    <RouteGuardContext.Provider value={value}>
      {children}
    </RouteGuardContext.Provider>
  );
};

export const useRouteGuard = () => {
  const context = useContext(RouteGuardContext);
  if (!context) {
    throw new Error('useRouteGuard must be used within RouteGuardProvider');
  }
  return context;
};

// Helper function to find route by path
function findRouteByPath(path: string): RouteConfig | null {
  // Implementation to find route config by path
  return null;
}
```

**검증 기준**:
- [ ] 인증 확인 메커니즘
- [ ] 권한 검증 로직
- [ ] 리다이렉션 처리
- [ ] 역할 기반 접근 제어

#### SubTask 7.7.3: 동적 라우팅 및 파라미터 처리
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/routes/DynamicRoute.tsx
import React, { Suspense, useEffect, useState } from 'react';
import { useParams, useSearchParams, useLocation } from 'react-router-dom';
import { CircularProgress } from '@mui/material';

interface DynamicRouteProps {
  loader: (params: any) => Promise<React.ComponentType<any>>;
  fallback?: React.ReactNode;
  onError?: (error: Error) => void;
}

export const DynamicRoute: React.FC<DynamicRouteProps> = ({
  loader,
  fallback = <CircularProgress />,
  onError
}) => {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const [Component, setComponent] = useState<React.ComponentType<any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    loadComponent();
  }, [params, location.pathname]);
  
  const loadComponent = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Convert URLSearchParams to object
      const queryParams = Object.fromEntries(searchParams.entries());
      
      // Load component dynamically based on params
      const LoadedComponent = await loader({
        ...params,
        query: queryParams,
        pathname: location.pathname
      });
      
      setComponent(() => LoadedComponent);
    } catch (err) {
      const error = err as Error;
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <>{fallback}</>;
  }
  
  if (error) {
    return <div>Error loading component: {error.message}</div>;
  }
  
  if (!Component) {
    return <div>Component not found</div>;
  }
  
  return (
    <Suspense fallback={fallback}>
      <Component {...params} />
    </Suspense>
  );
};

// Hook for dynamic route parameters
export const useDynamicParams = <T extends Record<string, any> = {}>() => {
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  
  // Parse and validate params
  const parsedParams = React.useMemo(() => {
    const result: any = {};
    
    // Parse route params
    Object.entries(params).forEach(([key, value]) => {
      // Try to parse as number if possible
      const numValue = Number(value);
      result[key] = !isNaN(numValue) ? numValue : value;
    });
    
    // Parse query params
    searchParams.forEach((value, key) => {
      // Handle array params (e.g., ?tags=a&tags=b)
      if (result[key]) {
        if (Array.isArray(result[key])) {
          result[key].push(value);
        } else {
          result[key] = [result[key], value];
        }
      } else {
        result[key] = value;
      }
    });
    
    return result as T;
  }, [params, searchParams]);
  
  // Update query params
  const updateQueryParams = (updates: Record<string, any>) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === undefined) {
        newParams.delete(key);
      } else if (Array.isArray(value)) {
        newParams.delete(key);
        value.forEach(v => newParams.append(key, String(v)));
      } else {
        newParams.set(key, String(value));
      }
    });
    
    setSearchParams(newParams);
  };
  
  return {
    params: parsedParams,
    updateQueryParams,
    pathname: location.pathname,
    state: location.state
  };
};
```

```typescript
// frontend/src/routes/ParameterizedRoute.tsx
import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { z } from 'zod';

interface ParameterizedRouteProps<T> {
  schema: z.ZodSchema<T>;
  component: React.ComponentType<{ params: T }>;
  onValidationError?: (error: z.ZodError) => void;
  errorComponent?: React.ComponentType<{ error: z.ZodError }>;
}

export function ParameterizedRoute<T>({
  schema,
  component: Component,
  onValidationError,
  errorComponent: ErrorComponent
}: ParameterizedRouteProps<T>) {
  const params = useParams();
  
  try {
    // Validate params against schema
    const validatedParams = schema.parse(params);
    
    return <Component params={validatedParams} />;
  } catch (error) {
    if (error instanceof z.ZodError) {
      onValidationError?.(error);
      
      if (ErrorComponent) {
        return <ErrorComponent error={error} />;
      }
      
      return <Navigate to="/404" replace />;
    }
    
    throw error;
  }
}

// Example usage with schema
const ProjectDetailSchema = z.object({
  projectId: z.string().uuid(),
  tab: z.enum(['overview', 'agents', 'workflows', 'settings']).optional()
});

export const ProjectDetailRoute = () => (
  <ParameterizedRoute
    schema={ProjectDetailSchema}
    component={({ params }) => (
      <ProjectDetail projectId={params.projectId} tab={params.tab} />
    )}
    errorComponent={({ error }) => (
      <div>Invalid project parameters: {error.message}</div>
    )}
  />
);
```

```typescript
// frontend/src/hooks/useRouteParams.ts
import { useParams, useSearchParams, useLocation } from 'react-router-dom';
import { useMemo, useCallback } from 'react';

interface RouteParamsOptions {
  parseNumbers?: boolean;
  parseBooleans?: boolean;
  parseArrays?: boolean;
  defaults?: Record<string, any>;
}

export function useRouteParams<T = any>(options: RouteParamsOptions = {}) {
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  
  const {
    parseNumbers = true,
    parseBooleans = true,
    parseArrays = true,
    defaults = {}
  } = options;
  
  // Parse value based on options
  const parseValue = useCallback((value: string): any => {
    if (parseNumbers && /^\d+$/.test(value)) {
      return parseInt(value, 10);
    }
    
    if (parseNumbers && /^\d+\.\d+$/.test(value)) {
      return parseFloat(value);
    }
    
    if (parseBooleans && (value === 'true' || value === 'false')) {
      return value === 'true';
    }
    
    return value;
  }, [parseNumbers, parseBooleans]);
  
  // Combine all params
  const allParams = useMemo(() => {
    const result: any = { ...defaults };
    
    // Add route params
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        result[key] = parseValue(value);
      }
    });
    
    // Add query params
    searchParams.forEach((value, key) => {
      if (parseArrays && key.endsWith('[]')) {
        const arrayKey = key.slice(0, -2);
        if (!result[arrayKey]) {
          result[arrayKey] = [];
        }
        result[arrayKey].push(parseValue(value));
      } else if (result[key] !== undefined && parseArrays) {
        // Convert to array if duplicate keys
        if (!Array.isArray(result[key])) {
          result[key] = [result[key]];
        }
        result[key].push(parseValue(value));
      } else {
        result[key] = parseValue(value);
      }
    });
    
    return result as T;
  }, [params, searchParams, defaults, parseValue, parseArrays]);
  
  // Update specific param
  const setParam = useCallback((key: string, value: any) => {
    const newSearchParams = new URLSearchParams(searchParams);
    
    if (value === null || value === undefined) {
      newSearchParams.delete(key);
    } else if (Array.isArray(value)) {
      newSearchParams.delete(key);
      value.forEach(v => newSearchParams.append(key, String(v)));
    } else {
      newSearchParams.set(key, String(value));
    }
    
    setSearchParams(newSearchParams);
  }, [searchParams, setSearchParams]);
  
  // Batch update params
  const setParams = useCallback((updates: Record<string, any>) => {
    const newSearchParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === undefined) {
        newSearchParams.delete(key);
      } else if (Array.isArray(value)) {
        newSearchParams.delete(key);
        value.forEach(v => newSearchParams.append(key, String(v)));
      } else {
        newSearchParams.set(key, String(value));
      }
    });
    
    setSearchParams(newSearchParams);
  }, [searchParams, setSearchParams]);
  
  // Clear all query params
  const clearParams = useCallback(() => {
    setSearchParams(new URLSearchParams());
  }, [setSearchParams]);
  
  return {
    params: allParams,
    routeParams: params,
    queryParams: Object.fromEntries(searchParams.entries()),
    setParam,
    setParams,
    clearParams,
    pathname: location.pathname,
    state: location.state
  };
}
```

**검증 기준**:
- [ ] 동적 컴포넌트 로딩
- [ ] 파라미터 파싱 및 검증
- [ ] Query string 처리
- [ ] 타입 안전 파라미터

#### SubTask 7.7.4: 라우트 트랜지션 및 애니메이션
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/transitions/RouteTransition.tsx
import React, { useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { motion, AnimatePresence } from 'framer-motion';
import './transitions.css';

interface RouteTransitionProps {
  children: React.ReactNode;
  type?: 'fade' | 'slide' | 'zoom' | 'flip';
  duration?: number;
  direction?: 'left' | 'right' | 'up' | 'down';
}

export const RouteTransition: React.FC<RouteTransitionProps> = ({
  children,
  type = 'fade',
  duration = 300,
  direction = 'right'
}) => {
  const location = useLocation();
  const nodeRef = useRef(null);
  
  const getTransitionClass = () => {
    switch (type) {
      case 'slide':
        return `slide-${direction}`;
      case 'zoom':
        return 'zoom';
      case 'flip':
        return 'flip';
      default:
        return 'fade';
    }
  };
  
  return (
    <TransitionGroup component={null}>
      <CSSTransition
        key={location.pathname}
        nodeRef={nodeRef}
        timeout={duration}
        classNames={getTransitionClass()}
        unmountOnExit
      >
        <div ref={nodeRef} className="route-transition-wrapper">
          {children}
        </div>
      </CSSTransition>
    </TransitionGroup>
  );
};

// Framer Motion based transitions
export const MotionRouteTransition: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const location = useLocation();
  
  const pageVariants = {
    initial: {
      opacity: 0,
      x: -20
    },
    in: {
      opacity: 1,
      x: 0
    },
    out: {
      opacity: 0,
      x: 20
    }
  };
  
  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3
  };
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

// Advanced page transitions with gesture support
export const AdvancedRouteTransition: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const location = useLocation();
  const [direction, setDirection] = React.useState(0);
  const [previousPath, setPreviousPath] = React.useState(location.pathname);
  
  useEffect(() => {
    // Determine direction based on route hierarchy
    const currentDepth = location.pathname.split('/').length;
    const previousDepth = previousPath.split('/').length;
    
    if (currentDepth > previousDepth) {
      setDirection(1); // Forward
    } else if (currentDepth < previousDepth) {
      setDirection(-1); // Backward
    } else {
      setDirection(0); // Same level
    }
    
    setPreviousPath(location.pathname);
  }, [location]);
  
  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  };
  
  const swipeConfidenceThreshold = 10000;
  const swipePower = (offset: number, velocity: number) => {
    return Math.abs(offset) * velocity;
  };
  
  return (
    <AnimatePresence initial={false} custom={direction}>
      <motion.div
        key={location.pathname}
        custom={direction}
        variants={variants}
        initial="enter"
        animate="center"
        exit="exit"
        transition={{
          x: { type: "spring", stiffness: 300, damping: 30 },
          opacity: { duration: 0.2 }
        }}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={1}
        onDragEnd={(e, { offset, velocity }) => {
          const swipe = swipePower(offset.x, velocity.x);
          
          if (swipe < -swipeConfidenceThreshold) {
            // Navigate forward
            console.log('Swipe forward');
          } else if (swipe > swipeConfidenceThreshold) {
            // Navigate backward
            console.log('Swipe backward');
          }
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};
```

```css
/* frontend/src/components/transitions/transitions.css */
.route-transition-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

/* Fade transition */
.fade-enter {
  opacity: 0;
}

.fade-enter-active {
  opacity: 1;
  transition: opacity 300ms ease-in;
}

.fade-exit {
  opacity: 1;
}

.fade-exit-active {
  opacity: 0;
  transition: opacity 300ms ease-out;
}

/* Slide transitions */
.slide-right-enter {
  transform: translateX(100%);
}

.slide-right-enter-active {
  transform: translateX(0);
  transition: transform 300ms ease-out;
}

.slide-right-exit {
  transform: translateX(0);
}

.slide-right-exit-active {
  transform: translateX(-100%);
  transition: transform 300ms ease-in;
}

.slide-left-enter {
  transform: translateX(-100%);
}

.slide-left-enter-active {
  transform: translateX(0);
  transition: transform 300ms ease-out;
}

.slide-left-exit {
  transform: translateX(0);
}

.slide-left-exit-active {
  transform: translateX(100%);
  transition: transform 300ms ease-in;
}

/* Zoom transition */
.zoom-enter {
  transform: scale(0.9);
  opacity: 0;
}

.zoom-enter-active {
  transform: scale(1);
  opacity: 1;
  transition: transform 300ms ease-out, opacity 300ms ease-out;
}

.zoom-exit {
  transform: scale(1);
  opacity: 1;
}

.zoom-exit-active {
  transform: scale(1.1);
  opacity: 0;
  transition: transform 300ms ease-in, opacity 300ms ease-in;
}

/* Flip transition */
.flip-enter {
  transform: rotateY(90deg);
  opacity: 0;
}

.flip-enter-active {
  transform: rotateY(0);
  opacity: 1;
  transition: transform 300ms ease-out, opacity 150ms ease-in 150ms;
}

.flip-exit {
  transform: rotateY(0);
  opacity: 1;
}

.flip-exit-active {
  transform: rotateY(-90deg);
  opacity: 0;
  transition: transform 300ms ease-in, opacity 150ms ease-out;
}
```

**검증 기준**:
- [ ] 트랜지션 효과 적용
- [ ] 애니메이션 성능
- [ ] 제스처 지원
- [ ] 방향성 애니메이션

---

### Task 7.8: 네비게이션 및 브레드크럼 시스템

#### SubTask 7.8.1: 메인 네비게이션 컴포넌트 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/components/navigation/MainNavigation.tsx
import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Badge,
  Tooltip,
  Button
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle,
  Brightness4,
  Brightness7,
  Search as SearchIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import useAppStore from '@/store';
import { SearchBar } from './SearchBar';
import { NotificationPanel } from './NotificationPanel';
import { UserMenu } from './UserMenu';

interface MainNavigationProps {
  onMenuToggle: () => void;
  sidebarOpen: boolean;
}

export const MainNavigation: React.FC<MainNavigationProps> = ({
  onMenuToggle,
  sidebarOpen
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, theme, toggleTheme, notifications } = useAppStore();
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  
  const unreadCount = notifications.filter(n => !n.read).length;
  
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleNotificationOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };
  
  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };
  
  // Get current page title
  const getPageTitle = () => {
    const path = location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    if (segments.length === 0) return 'Dashboard';
    
    return segments[segments.length - 1]
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        transition: (theme) =>
          theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
      }}
    >
      <Toolbar>
        {/* Menu Toggle */}
        <IconButton
          color="inherit"
          aria-label="toggle menu"
          onClick={onMenuToggle}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        {/* Logo/Brand */}
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ display: { xs: 'none', sm: 'block' } }}
        >
          T-Developer
        </Typography>
        
        {/* Page Title */}
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ 
            ml: 3,
            color: 'text.secondary',
            fontSize: '1rem'
          }}
        >
          {getPageTitle()}
        </Typography>
        
        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />
        
        {/* Search */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, mr: 2 }}>
          <SearchBar
            open={searchOpen}
            onToggle={() => setSearchOpen(!searchOpen)}
          />
        </Box>
        
        {/* Search Icon (Mobile) */}
        <IconButton
          color="inherit"
          sx={{ display: { xs: 'flex', md: 'none' } }}
          onClick={() => setSearchOpen(true)}
        >
          <SearchIcon />
        </IconButton>
        
        {/* Theme Toggle */}
        <Tooltip title="Toggle theme">
          <IconButton
            color="inherit"
            onClick={toggleTheme}
            sx={{ ml: 1 }}
          >
            {theme === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Tooltip>
        
        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton
            color="inherit"
            onClick={handleNotificationOpen}
            sx={{ ml: 1 }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>
        
        {/* User Menu */}
        <Tooltip title="Account">
          <IconButton
            onClick={handleUserMenuOpen}
            sx={{ ml: 2 }}
          >
            <Avatar
              alt={user?.name}
              src={user?.avatar}
              sx={{ width: 32, height: 32 }}
            >
              {user?.name?.charAt(0)}
            </Avatar>
          </IconButton>
        </Tooltip>
        
        {/* User Dropdown Menu */}
        <UserMenu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleUserMenuClose}
          user={user}
        />
        
        {/* Notification Panel */}
        <NotificationPanel
          anchorEl={notificationAnchor}
          open={Boolean(notificationAnchor)}
          onClose={handleNotificationClose}
          notifications={notifications}
        />
      </Toolbar>
    </AppBar>
  );
};

// Quick Actions Bar
export const QuickActionsBar: React.FC = () => {
  const navigate = useNavigate();
  const currentProject = useAppStore(state => state.currentProject);
  
  const quickActions = [
    {
      label: 'New Project',
      icon: '➕',
      action: () => navigate('/projects/new'),
      permission: 'projects:create'
    },
    {
      label: 'Run Workflow',
      icon: '▶️',
      action: () => navigate('/workflows/run'),
      permission: 'workflows:execute',
      disabled: !currentProject
    },
    {
      label: 'View Agents',
      icon: '🤖',
      action: () => navigate('/agents'),
      permission: 'agents:view'
    }
  ];
  
  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1,
        p: 1,
        backgroundColor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider'
      }}
    >
      {quickActions.map((action, index) => (
        <PermissionGate key={index} permissions={[action.permission]}>
          <Button
            size="small"
            startIcon={<span>{action.icon}</span>}
            onClick={action.action}
            disabled={action.disabled}
          >
            {action.label}
          </Button>
        </PermissionGate>
      ))}
    </Box>
  );
};
```

**검증 기준**:
- [ ] 네비게이션 바 레이아웃
- [ ] 사용자 메뉴 기능
- [ ] 알림 배지 표시
- [ ] 반응형 디자인

#### SubTask 7.8.2: 브레드크럼 시스템 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/navigation/Breadcrumbs.tsx
import React, { useMemo } from 'react';
import { 
  Breadcrumbs as MUIBreadcrumbs, 
  Link, 
  Typography, 
  Chip,
  Box 
} from '@mui/material';
import { NavigateNext, Home } from '@mui/icons-material';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { routes, RouteConfig } from '@/routes/routes.config';

interface BreadcrumbItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
  active?: boolean;
}

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams();
  
  const breadcrumbs = useMemo(() => {
    const path = location.pathname;
    const segments = path.split('/').filter(Boolean);
    const items: BreadcrumbItem[] = [];
    
    // Always add home
    items.push({
      label: 'Home',
      path: '/',
      icon: <Home fontSize="small" />
    });
    
    // Build breadcrumbs from path segments
    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      // Find matching route
      const route = findRouteByPath(currentPath);
      
      if (route) {
        let label = route.title || segment;
        
        // Handle dynamic breadcrumb
        if (typeof route.breadcrumb === 'function') {
          label = route.breadcrumb(params);
        } else if (route.breadcrumb) {
          label = route.breadcrumb;
        }
        
        items.push({
          label,
          path: currentPath,
          active: index === segments.length - 1
        });
      } else {
        // Fallback for unmatched routes
        items.push({
          label: formatSegment(segment),
          path: currentPath,
          active: index === segments.length - 1
        });
      }
    });
    
    return items;
  }, [location, params]);
  
  const handleClick = (path: string) => {
    navigate(path);
  };
  
  return (
    <Box sx={{ mb: 2 }}>
      <MUIBreadcrumbs
        separator={<NavigateNext fontSize="small" />}
        aria-label="breadcrumb"
      >
        {breadcrumbs.map((item, index) => {
          if (item.active) {
            return (
              <Typography
                key={index}
                color="text.primary"
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                {item.icon}
                {item.label}
              </Typography>
            );
          }
          
          return (
            <Link
              key={index}
              color="inherit"
              href="#"
              onClick={(e) => {
                e.preventDefault();
                handleClick(item.path);
              }}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline'
                }
              }}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </MUIBreadcrumbs>
    </Box>
  );
};

// Context-aware breadcrumbs
export const ContextBreadcrumbs: React.FC = () => {
  const location = useLocation();
  const currentProject = useAppStore(state => state.currentProject);
  const currentAgent = useAppStore(state => state.selectedAgent);
  
  const contextItems = useMemo(() => {
    const items: Array<{ label: string; value: string }> = [];
    
    if (currentProject) {
      items.push({
        label: 'Project',
        value: currentProject.name
      });
    }
    
    if (currentAgent) {
      items.push({
        label: 'Agent',
        value: currentAgent.name
      });
    }
    
    return items;
  }, [currentProject, currentAgent]);
  
  return (
    <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
      <Breadcrumbs />
      {contextItems.length > 0 && (
        <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
          {contextItems.map((item, index) => (
            <Chip
              key={index}
              label={`${item.label}: ${item.value}`}
              size="small"
              variant="outlined"
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

// Helper functions
function findRouteByPath(path: string): RouteConfig | null {
  // Implementation to match path with route config
  // This would need to handle dynamic segments
  return null;
}

function formatSegment(segment: string): string {
  // Format URL segment to readable text
  return segment
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
```

**검증 기준**:
- [ ] 동적 브레드크럼 생성
- [ ] 클릭 가능한 네비게이션
- [ ] 컨텍스트 정보 표시
- [ ] 파라미터 처리

#### SubTask 7.8.3: 사이드바 및 모바일 네비게이션
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/components/navigation/Sidebar.tsx
import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Divider,
  Box,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  ExpandLess,
  ExpandMore,
  ChevronLeft
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { getMenuItems } from '@/routes/routes.config';
import useAppStore from '@/store';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  width?: number;
  variant?: 'permanent' | 'persistent' | 'temporary';
}

export const Sidebar: React.FC<SidebarProps> = ({
  open,
  onClose,
  width = 260,
  variant = 'persistent'
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { hasPermission } = useAppStore();
  
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  
  const menuItems = getMenuItems(routes);
  
  const handleItemClick = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };
  
  const toggleExpand = (path: string) => {
    setExpandedItems(prev =>
      prev.includes(path)
        ? prev.filter(p => p !== path)
        : [...prev, path]
    );
  };
  
  const isActive = (path: string): boolean => {
    return location.pathname === path || 
           location.pathname.startsWith(`${path}/`);
  };
  
  const renderMenuItem = (item: RouteConfig, depth = 0) => {
    // Check permissions
    if (item.permissions?.length && !item.permissions.every(hasPermission)) {
      return null;
    }
    
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.includes(item.path);
    const active = isActive(item.path);
    
    return (
      <React.Fragment key={item.path}>
        <ListItem
          disablePadding
          sx={{ display: 'block' }}
        >
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                toggleExpand(item.path);
              } else {
                handleItemClick(item.path);
              }
            }}
            selected={active}
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: 2.5,
              pl: 2.5 + depth * 2
            }}
          >
            {item.icon && (
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : 'auto',
                  justifyContent: 'center'
                }}
              >
                <item.icon />
              </ListItemIcon>
            )}
            <ListItemText
              primary={item.title}
              sx={{ opacity: open ? 1 : 0 }}
            />
            {hasChildren && open && (
              isExpanded ? <ExpandLess /> : <ExpandMore />
            )}
          </ListItemButton>
        </ListItem>
        
        {hasChildren && (
          <Collapse in={isExpanded && open} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => 
                renderMenuItem(child, depth + 1)
              )}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };
  
  const drawerContent = (
    <Box sx={{ overflow: 'auto' }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2
        }}
      >
        <Typography variant="h6" noWrap>
          Menu
        </Typography>
        <IconButton onClick={onClose} size="small">
          <ChevronLeft />
        </IconButton>
      </Box>
      
      <Divider />
      
      {/* Menu Items */}
      <List>
        {menuItems.map(item => renderMenuItem(item))}
      </List>
      
      <Divider />
      
      {/* Footer */}
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Version 1.0.0
        </Typography>
      </Box>
    </Box>
  );
  
  return (
    <Drawer
      variant={isMobile ? 'temporary' : variant}
      open={open}
      onClose={onClose}
      sx={{
        width: open ? width : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
          top: { xs: 0, sm: 64 },
          height: { xs: '100%', sm: 'calc(100% - 64px)' }
        }
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

// Mobile Bottom Navigation
export const MobileBottomNav: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  if (!isMobile) return null;
  
  const bottomNavItems = [
    { path: '/', icon: '🏠', label: 'Home' },
    { path: '/projects', icon: '📁', label: 'Projects' },
    { path: '/agents', icon: '🤖', label: 'Agents' },
    { path: '/workflows', icon: '⚡', label: 'Workflows' },
    { path: '/settings', icon: '⚙️', label: 'Settings' }
  ];
  
  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'background.paper',
        borderTop: 1,
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-around',
        p: 1,
        zIndex: theme.zIndex.appBar
      }}
    >
      {bottomNavItems.map(item => (
        <IconButton
          key={item.path}
          onClick={() => navigate(item.path)}
          sx={{
            flexDirection: 'column',
            color: location.pathname === item.path ? 'primary.main' : 'text.secondary'
          }}
        >
          <span>{item.icon}</span>
          <Typography variant="caption">{item.label}</Typography>
        </IconButton>
      ))}
    </Box>
  );
};
```

**검증 기준**:
- [ ] 사이드바 토글 기능
- [ ] 중첩 메뉴 지원
- [ ] 모바일 대응
- [ ] 권한 기반 메뉴 필터링

#### SubTask 7.8.4: 네비게이션 상태 관리 및 활성 표시
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```typescript
// frontend/src/hooks/useNavigation.ts
import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import useAppStore from '@/store';

interface NavigationState {
  currentPath: string;
  previousPath: string | null;
  history: string[];
  canGoBack: boolean;
  canGoForward: boolean;
}

export const useNavigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [navigationState, setNavigationState] = useState<NavigationState>({
    currentPath: location.pathname,
    previousPath: null,
    history: [location.pathname],
    canGoBack: false,
    canGoForward: false
  });
  
  useEffect(() => {
    setNavigationState(prev => ({
      ...prev,
      previousPath: prev.currentPath,
      currentPath: location.pathname,
      history: [...prev.history, location.pathname].slice(-50), // Keep last 50
      canGoBack: prev.history.length > 1
    }));
  }, [location]);
  
  const goBack = useCallback(() => {
    if (navigationState.canGoBack) {
      navigate(-1);
    }
  }, [navigate, navigationState.canGoBack]);
  
  const goForward = useCallback(() => {
    navigate(1);
  }, [navigate]);
  
  const goTo = useCallback((path: string, options?: any) => {
    navigate(path, options);
  }, [navigate]);
  
  const isActive = useCallback((path: string, exact = false): boolean => {
    if (exact) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  }, [location]);
  
  const getActiveRoute = useCallback(() => {
    // Find the matching route from config
    return findActiveRoute(location.pathname);
  }, [location]);
  
  return {
    ...navigationState,
    goBack,
    goForward,
    goTo,
    isActive,
    getActiveRoute
  };
};

// Navigation tracker store slice
export const createNavigationSlice = (set: any, get: any) => ({
  navigationHistory: [] as string[],
  activeMenuItems: new Set<string>(),
  expandedMenuItems: new Set<string>(),
  
  pushToHistory: (path: string) => {
    set((state: any) => ({
      navigationHistory: [...state.navigationHistory, path].slice(-100)
    }));
  },
  
  setActiveMenuItem: (path: string) => {
    set((state: any) => {
      state.activeMenuItems.clear();
      state.activeMenuItems.add(path);
      
      // Also expand parent items
      const parents = getParentPaths(path);
      parents.forEach(p => state.expandedMenuItems.add(p));
    });
  },
  
  toggleMenuItem: (path: string) => {
    set((state: any) => {
      if (state.expandedMenuItems.has(path)) {
        state.expandedMenuItems.delete(path);
      } else {
        state.expandedMenuItems.add(path);
      }
    });
  },
  
  clearNavigationHistory: () => {
    set({ navigationHistory: [] });
  }
});

// Helper functions
function findActiveRoute(pathname: string): RouteConfig | null {
  // Implementation to find active route
  return null;
}

function getParentPaths(path: string): string[] {
  const segments = path.split('/').filter(Boolean);
  const parents: string[] = [];
  
  for (let i = 1; i < segments.length; i++) {
    parents.push('/' + segments.slice(0, i).join('/'));
  }
  
  return parents;
}
```

**검증 기준**:
- [ ] 네비게이션 이력 추적
- [ ] 활성 메뉴 표시
- [ ] 메뉴 확장 상태 관리
- [ ] 경로 매칭 로직

---
# Phase 7: 프론트엔드 구현 - Tasks 7.9-7.14 SubTask 구조 및 작업지시서

## 📋 Tasks 7.9-7.14 SubTask 목록

### Task 7.9: 테마 및 디자인 토큰 설정
- **SubTask 7.9.1**: 디자인 토큰 시스템 구축
- **SubTask 7.9.2**: 라이트/다크 테마 구현
- **SubTask 7.9.3**: 컬러 팔레트 및 타이포그래피 설정
- **SubTask 7.9.4**: 반응형 디자인 토큰 및 브레이크포인트

### Task 7.10: Material-UI 커스터마이징
- **SubTask 7.10.1**: MUI 테마 커스터마이징
- **SubTask 7.10.2**: 컴포넌트 스타일 오버라이드
- **SubTask 7.10.3**: 커스텀 MUI 컴포넌트 변형
- **SubTask 7.10.4**: MUI 시스템 유틸리티 설정

### Task 7.11: 글로벌 스타일 및 CSS 시스템
- **SubTask 7.11.1**: 글로벌 CSS 리셋 및 기본 스타일
- **SubTask 7.11.2**: CSS-in-JS 설정 및 스타일드 컴포넌트
- **SubTask 7.11.3**: 애니메이션 및 트랜지션 시스템
- **SubTask 7.11.4**: 유틸리티 클래스 및 믹스인

### Task 7.12: 원자 컴포넌트 (Buttons, Inputs, etc.)
- **SubTask 7.12.1**: 버튼 컴포넌트 시스템
- **SubTask 7.12.2**: 입력 필드 컴포넌트
- **SubTask 7.12.3**: 타이포그래피 및 아이콘 컴포넌트
- **SubTask 7.12.4**: 기타 원자 컴포넌트 (Badge, Chip, Avatar)

### Task 7.13: 분자 컴포넌트 (Forms, Cards, etc.)
- **SubTask 7.13.1**: 폼 컴포넌트 시스템
- **SubTask 7.13.2**: 카드 및 리스트 컴포넌트
- **SubTask 7.13.3**: 모달 및 다이얼로그 컴포넌트
- **SubTask 7.13.4**: 알림 및 토스트 컴포넌트

### Task 7.14: 유기체 컴포넌트 (Headers, Sidebars, etc.)
- **SubTask 7.14.1**: 헤더 및 네비게이션 바 컴포넌트
- **SubTask 7.14.2**: 사이드바 및 드로어 컴포넌트
- **SubTask 7.14.3**: 테이블 및 데이터 그리드 컴포넌트
- **SubTask 7.14.4**: 차트 및 시각화 컴포넌트

---

## 📝 세부 작업지시서

### Task 7.9: 테마 및 디자인 토큰 설정

#### SubTask 7.9.1: 디자인 토큰 시스템 구축
**담당자**: UI/UX 디자이너 & 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/styles/tokens/design-tokens.ts
export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  breakpoints: BreakpointTokens;
  shadows: ShadowTokens;
  borders: BorderTokens;
  animations: AnimationTokens;
  zIndex: ZIndexTokens;
}

// Color system
export interface ColorTokens {
  // Brand colors
  primary: ColorScale;
  secondary: ColorScale;
  tertiary: ColorScale;
  
  // Semantic colors
  success: ColorScale;
  warning: ColorScale;
  error: ColorScale;
  info: ColorScale;
  
  // Neutral colors
  neutral: ColorScale;
  
  // Special colors
  background: {
    primary: string;
    secondary: string;
    tertiary: string;
    elevated: string;
    overlay: string;
  };
  
  text: {
    primary: string;
    secondary: string;
    tertiary: string;
    disabled: string;
    inverse: string;
  };
  
  border: {
    light: string;
    medium: string;
    strong: string;
    focus: string;
  };
}

interface ColorScale {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string; // Main
  600: string;
  700: string;
  800: string;
  900: string;
  A100?: string;
  A200?: string;
  A400?: string;
  A700?: string;
}

// Implementation
export const designTokens: DesignTokens = {
  colors: {
    primary: {
      50: '#E8F0FE',
      100: '#C5DAFC',
      200: '#9EC2FA',
      300: '#77AAF9',
      400: '#5A97F8',
      500: '#3D85F7', // Main
      600: '#377DF4',
      700: '#2F72F0',
      800: '#2768EC',
      900: '#1A55E6',
      A100: '#FFFFFF',
      A200: '#E8F0FF',
      A400: '#B5CCFF',
      A700: '#9CBAFF'
    },
    secondary: {
      50: '#FFF3E0',
      100: '#FFE0B2',
      200: '#FFCC80',
      300: '#FFB74D',
      400: '#FFA726',
      500: '#FF9800', // Main
      600: '#FB8C00',
      700: '#F57C00',
      800: '#EF6C00',
      900: '#E65100'
    },
    success: {
      50: '#E8F5E9',
      100: '#C8E6C9',
      200: '#A5D6A7',
      300: '#81C784',
      400: '#66BB6A',
      500: '#4CAF50', // Main
      600: '#43A047',
      700: '#388E3C',
      800: '#2E7D32',
      900: '#1B5E20'
    },
    warning: {
      50: '#FFF8E1',
      100: '#FFECB3',
      200: '#FFE082',
      300: '#FFD54F',
      400: '#FFCA28',
      500: '#FFC107', // Main
      600: '#FFB300',
      700: '#FFA000',
      800: '#FF8F00',
      900: '#FF6F00'
    },
    error: {
      50: '#FFEBEE',
      100: '#FFCDD2',
      200: '#EF9A9A',
      300: '#E57373',
      400: '#EF5350',
      500: '#F44336', // Main
      600: '#E53935',
      700: '#D32F2F',
      800: '#C62828',
      900: '#B71C1C'
    },
    info: {
      50: '#E3F2FD',
      100: '#BBDEFB',
      200: '#90CAF9',
      300: '#64B5F6',
      400: '#42A5F5',
      500: '#2196F3', // Main
      600: '#1E88E5',
      700: '#1976D2',
      800: '#1565C0',
      900: '#0D47A1'
    },
    neutral: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121'
    },
    background: {
      primary: 'var(--color-bg-primary)',
      secondary: 'var(--color-bg-secondary)',
      tertiary: 'var(--color-bg-tertiary)',
      elevated: 'var(--color-bg-elevated)',
      overlay: 'var(--color-bg-overlay)'
    },
    text: {
      primary: 'var(--color-text-primary)',
      secondary: 'var(--color-text-secondary)',
      tertiary: 'var(--color-text-tertiary)',
      disabled: 'var(--color-text-disabled)',
      inverse: 'var(--color-text-inverse)'
    },
    border: {
      light: 'var(--color-border-light)',
      medium: 'var(--color-border-medium)',
      strong: 'var(--color-border-strong)',
      focus: 'var(--color-border-focus)'
    }
  },
  
  typography: {
    fontFamily: {
      primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      secondary: '"Roboto", "Helvetica Neue", Arial, sans-serif',
      mono: '"JetBrains Mono", "Courier New", monospace'
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
      '6xl': '3.75rem', // 60px
      '7xl': '4.5rem',  // 72px
      '8xl': '6rem',    // 96px
      '9xl': '8rem'     // 128px
    },
    fontWeight: {
      thin: 100,
      extralight: 200,
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
      black: 900
    },
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2
    },
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em'
    }
  },
  
  spacing: {
    0: '0',
    0.5: '0.125rem',  // 2px
    1: '0.25rem',     // 4px
    1.5: '0.375rem',  // 6px
    2: '0.5rem',      // 8px
    2.5: '0.625rem',  // 10px
    3: '0.75rem',     // 12px
    3.5: '0.875rem',  // 14px
    4: '1rem',        // 16px
    5: '1.25rem',     // 20px
    6: '1.5rem',      // 24px
    7: '1.75rem',     // 28px
    8: '2rem',        // 32px
    9: '2.25rem',     // 36px
    10: '2.5rem',     // 40px
    11: '2.75rem',    // 44px
    12: '3rem',       // 48px
    14: '3.5rem',     // 56px
    16: '4rem',       // 64px
    20: '5rem',       // 80px
    24: '6rem',       // 96px
    28: '7rem',       // 112px
    32: '8rem',       // 128px
    36: '9rem',       // 144px
    40: '10rem',      // 160px
    44: '11rem',      // 176px
    48: '12rem',      // 192px
    52: '13rem',      // 208px
    56: '14rem',      // 224px
    60: '15rem',      // 240px
    64: '16rem',      // 256px
    72: '18rem',      // 288px
    80: '20rem',      // 320px
    96: '24rem'       // 384px
  },
  
  breakpoints: {
    xs: 0,
    sm: 600,
    md: 900,
    lg: 1200,
    xl: 1536
  },
  
  shadows: {
    none: 'none',
    xs: '0 0 0 1px rgba(0, 0, 0, 0.05)',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
  },
  
  borders: {
    radius: {
      none: '0',
      sm: '0.125rem',
      base: '0.25rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem',
      '2xl': '1rem',
      '3xl': '1.5rem',
      full: '9999px'
    },
    width: {
      0: '0',
      1: '1px',
      2: '2px',
      4: '4px',
      8: '8px'
    }
  },
  
  animations: {
    duration: {
      instant: '0ms',
      fast: '150ms',
      base: '300ms',
      slow: '500ms',
      slower: '700ms',
      slowest: '1000ms'
    },
    easing: {
      linear: 'linear',
      ease: 'ease',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeInQuad: 'cubic-bezier(0.55, 0.085, 0.68, 0.53)',
      easeInCubic: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
      easeOutCubic: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
      easeInOutCubic: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
      easeInQuart: 'cubic-bezier(0.895, 0.03, 0.685, 0.22)',
      easeOutQuart: 'cubic-bezier(0.165, 0.84, 0.44, 1)',
      easeInOutQuart: 'cubic-bezier(0.77, 0, 0.175, 1)'
    }
  },
  
  zIndex: {
    hide: -1,
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
    toast: 1700
  }
};

// Token accessor utility
export class TokenAccessor {
  static getColor(path: string): string {
    const keys = path.split('.');
    let value: any = designTokens.colors;
    
    for (const key of keys) {
      value = value[key];
      if (!value) return '#000000';
    }
    
    return value;
  }
  
  static getSpacing(size: keyof typeof designTokens.spacing): string {
    return designTokens.spacing[size];
  }
  
  static getFontSize(size: keyof typeof designTokens.typography.fontSize): string {
    return designTokens.typography.fontSize[size];
  }
  
  static getShadow(size: keyof typeof designTokens.shadows): string {
    return designTokens.shadows[size];
  }
  
  static getBorderRadius(size: keyof typeof designTokens.borders.radius): string {
    return designTokens.borders.radius[size];
  }
}
```

**검증 기준**:
- [ ] 디자인 토큰 구조화
- [ ] 타입 안전성 확보
- [ ] 토큰 접근 유틸리티
- [ ] 확장 가능한 구조

#### SubTask 7.9.2: 라이트/다크 테마 구현
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/styles/themes/theme.types.ts
export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeColors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  secondaryLight: string;
  secondaryDark: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  
  background: {
    default: string;
    paper: string;
    elevated: string;
  };
  
  text: {
    primary: string;
    secondary: string;
    disabled: string;
    inverse: string;
  };
  
  divider: string;
  border: string;
  shadow: string;
}

// frontend/src/styles/themes/light-theme.ts
export const lightTheme: ThemeColors = {
  primary: '#3D85F7',
  primaryLight: '#5A97F8',
  primaryDark: '#2768EC',
  secondary: '#FF9800',
  secondaryLight: '#FFB74D',
  secondaryDark: '#F57C00',
  success: '#4CAF50',
  warning: '#FFC107',
  error: '#F44336',
  info: '#2196F3',
  
  background: {
    default: '#F5F5F5',
    paper: '#FFFFFF',
    elevated: '#FFFFFF'
  },
  
  text: {
    primary: 'rgba(0, 0, 0, 0.87)',
    secondary: 'rgba(0, 0, 0, 0.60)',
    disabled: 'rgba(0, 0, 0, 0.38)',
    inverse: '#FFFFFF'
  },
  
  divider: 'rgba(0, 0, 0, 0.12)',
  border: 'rgba(0, 0, 0, 0.23)',
  shadow: 'rgba(0, 0, 0, 0.1)'
};

// frontend/src/styles/themes/dark-theme.ts
export const darkTheme: ThemeColors = {
  primary: '#5A97F8',
  primaryLight: '#77AAF9',
  primaryDark: '#3D85F7',
  secondary: '#FFB74D',
  secondaryLight: '#FFCC80',
  secondaryDark: '#FF9800',
  success: '#66BB6A',
  warning: '#FFCA28',
  error: '#EF5350',
  info: '#42A5F5',
  
  background: {
    default: '#121212',
    paper: '#1E1E1E',
    elevated: '#242424'
  },
  
  text: {
    primary: 'rgba(255, 255, 255, 0.87)',
    secondary: 'rgba(255, 255, 255, 0.60)',
    disabled: 'rgba(255, 255, 255, 0.38)',
    inverse: '#000000'
  },
  
  divider: 'rgba(255, 255, 255, 0.12)',
  border: 'rgba(255, 255, 255, 0.23)',
  shadow: 'rgba(0, 0, 0, 0.3)'
};

// frontend/src/styles/themes/theme-provider.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeProvider as StyledThemeProvider } from '@emotion/react';
import { lightTheme, darkTheme } from './themes';

interface ThemeContextValue {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
  theme: ThemeColors;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('theme-mode');
    return (saved as ThemeMode) || 'system';
  });
  
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>('light');
  
  useEffect(() => {
    // Detect system theme
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setSystemTheme(mediaQuery.matches ? 'dark' : 'light');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  useEffect(() => {
    // Save theme preference
    localStorage.setItem('theme-mode', mode);
    
    // Apply theme to document
    const actualTheme = mode === 'system' ? systemTheme : mode;
    document.documentElement.setAttribute('data-theme', actualTheme);
    
    // Update CSS variables
    updateCSSVariables(actualTheme === 'dark' ? darkTheme : lightTheme);
  }, [mode, systemTheme]);
  
  const toggleTheme = () => {
    setMode(prev => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'system';
      return 'light';
    });
  };
  
  const actualTheme = mode === 'system' ? systemTheme : mode;
  const theme = actualTheme === 'dark' ? darkTheme : lightTheme;
  
  return (
    <ThemeContext.Provider value={{ mode, setMode, toggleTheme, theme }}>
      <StyledThemeProvider theme={theme}>
        {children}
      </StyledThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Update CSS variables
function updateCSSVariables(theme: ThemeColors) {
  const root = document.documentElement;
  
  // Colors
  root.style.setProperty('--color-primary', theme.primary);
  root.style.setProperty('--color-primary-light', theme.primaryLight);
  root.style.setProperty('--color-primary-dark', theme.primaryDark);
  root.style.setProperty('--color-secondary', theme.secondary);
  root.style.setProperty('--color-success', theme.success);
  root.style.setProperty('--color-warning', theme.warning);
  root.style.setProperty('--color-error', theme.error);
  root.style.setProperty('--color-info', theme.info);
  
  // Backgrounds
  root.style.setProperty('--color-bg-default', theme.background.default);
  root.style.setProperty('--color-bg-paper', theme.background.paper);
  root.style.setProperty('--color-bg-elevated', theme.background.elevated);
  
  // Text
  root.style.setProperty('--color-text-primary', theme.text.primary);
  root.style.setProperty('--color-text-secondary', theme.text.secondary);
  root.style.setProperty('--color-text-disabled', theme.text.disabled);
  root.style.setProperty('--color-text-inverse', theme.text.inverse);
  
  // Others
  root.style.setProperty('--color-divider', theme.divider);
  root.style.setProperty('--color-border', theme.border);
}
```

**검증 기준**:
- [ ] 라이트/다크 테마 전환
- [ ] 시스템 테마 감지
- [ ] CSS 변수 업데이트
- [ ] 테마 영속성

#### SubTask 7.9.3: 컬러 팔레트 및 타이포그래피 설정
**담당자**: UI/UX 디자이너  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/styles/palette.ts
export const palette = {
  // Brand colors with semantic meaning
  brand: {
    primary: {
      main: '#3D85F7',
      light: '#5A97F8',
      dark: '#2768EC',
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
      contrastText: '#000000'
    }
  },
  
  // Semantic colors
  semantic: {
    success: {
      light: '#81C784',
      main: '#4CAF50',
      dark: '#388E3C',
      bg: '#E8F5E9'
    },
    warning: {
      light: '#FFD54F',
      main: '#FFC107',
      dark: '#FFA000',
      bg: '#FFF8E1'
    },
    error: {
      light: '#E57373',
      main: '#F44336',
      dark: '#D32F2F',
      bg: '#FFEBEE'
    },
    info: {
      light: '#64B5F6',
      main: '#2196F3',
      dark: '#1976D2',
      bg: '#E3F2FD'
    }
  },
  
  // Gradient presets
  gradients: {
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    success: 'linear-gradient(135deg, #13E780 0%, #00BBF0 100%)',
    warning: 'linear-gradient(135deg, #FFC107 0%, #FF9800 100%)',
    error: 'linear-gradient(135deg, #FF6B6B 0%, #EE5A6F 100%)',
    info: 'linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%)',
    dark: 'linear-gradient(135deg, #434343 0%, #000000 100%)',
    light: 'linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%)'
  },
  
  // Special colors
  special: {
    codeBg: '#1E1E1E',
    codeText: '#D4D4D4',
    highlight: '#FFEB3B',
    focus: '#3D85F7',
    disabled: '#9E9E9E',
    backdrop: 'rgba(0, 0, 0, 0.5)'
  }
};

// frontend/src/styles/typography.ts
export const typography = {
  // Font families
  fontFamily: {
    sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    serif: '"Merriweather", "Georgia", serif',
    mono: '"JetBrains Mono", "Fira Code", "Courier New", monospace',
    display: '"Poppins", "Inter", sans-serif'
  },
  
  // Type scale
  scale: {
    h1: {
      fontSize: '3rem',      // 48px
      lineHeight: 1.2,
      fontWeight: 700,
      letterSpacing: '-0.02em'
    },
    h2: {
      fontSize: '2.25rem',   // 36px
      lineHeight: 1.3,
      fontWeight: 600,
      letterSpacing: '-0.01em'
    },
    h3: {
      fontSize: '1.875rem',  // 30px
      lineHeight: 1.4,
      fontWeight: 600,
      letterSpacing: '0'
    },
    h4: {
      fontSize: '1.5rem',    // 24px
      lineHeight: 1.4,
      fontWeight: 500,
      letterSpacing: '0'
    },
    h5: {
      fontSize: '1.25rem',   // 20px
      lineHeight: 1.5,
      fontWeight: 500,
      letterSpacing: '0'
    },
    h6: {
      fontSize: '1.125rem',  // 18px
      lineHeight: 1.5,
      fontWeight: 500,
      letterSpacing: '0'
    },
    subtitle1: {
      fontSize: '1rem',      // 16px
      lineHeight: 1.75,
      fontWeight: 500,
      letterSpacing: '0.00938em'
    },
    subtitle2: {
      fontSize: '0.875rem',  // 14px
      lineHeight: 1.57,
      fontWeight: 500,
      letterSpacing: '0.00714em'
    },
    body1: {
      fontSize: '1rem',      // 16px
      lineHeight: 1.5,
      fontWeight: 400,
      letterSpacing: '0.00938em'
    },
    body2: {
      fontSize: '0.875rem',  // 14px
      lineHeight: 1.43,
      fontWeight: 400,
      letterSpacing: '0.01071em'
    },
    button: {
      fontSize: '0.875rem',  // 14px
      lineHeight: 1.75,
      fontWeight: 500,
      letterSpacing: '0.02857em',
      textTransform: 'uppercase' as const
    },
    caption: {
      fontSize: '0.75rem',   // 12px
      lineHeight: 1.66,
      fontWeight: 400,
      letterSpacing: '0.03333em'
    },
    overline: {
      fontSize: '0.75rem',   // 12px
      lineHeight: 2.66,
      fontWeight: 500,
      letterSpacing: '0.08333em',
      textTransform: 'uppercase' as const
    },
    code: {
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: '0.875rem',
      lineHeight: 1.5,
      fontWeight: 400
    }
  },
  
  // Responsive typography
  responsive: {
    h1: {
      xs: '2rem',
      sm: '2.5rem',
      md: '3rem'
    },
    h2: {
      xs: '1.75rem',
      sm: '2rem',
      md: '2.25rem'
    },
    h3: {
      xs: '1.5rem',
      sm: '1.75rem',
      md: '1.875rem'
    }
  }
};
```

**검증 기준**:
- [ ] 컬러 팔레트 정의
- [ ] 타이포그래피 스케일
- [ ] 그라디언트 프리셋
- [ ] 반응형 타이포그래피

#### SubTask 7.9.4: 반응형 디자인 토큰 및 브레이크포인트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```typescript
// frontend/src/styles/responsive.ts
export const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 900,
    lg: 1200,
    xl: 1536,
    xxl: 1920
  },
  
  // Media query helpers
  up: (key: keyof typeof breakpoints.values) => 
    `@media (min-width: ${breakpoints.values[key]}px)`,
    
  down: (key: keyof typeof breakpoints.values) => 
    `@media (max-width: ${breakpoints.values[key] - 0.05}px)`,
    
  between: (start: keyof typeof breakpoints.values, end: keyof typeof breakpoints.values) =>
    `@media (min-width: ${breakpoints.values[start]}px) and (max-width: ${breakpoints.values[end] - 0.05}px)`,
    
  only: (key: keyof typeof breakpoints.values) => {
    const keys = Object.keys(breakpoints.values) as Array<keyof typeof breakpoints.values>;
    const index = keys.indexOf(key);
    const nextKey = keys[index + 1];
    
    if (nextKey) {
      return breakpoints.between(key, nextKey);
    }
    return breakpoints.up(key);
  }
};

// Responsive spacing
export const responsiveSpacing = {
  container: {
    xs: '16px',
    sm: '24px',
    md: '32px',
    lg: '48px',
    xl: '64px'
  },
  
  grid: {
    gap: {
      xs: '8px',
      sm: '12px',
      md: '16px',
      lg: '24px',
      xl: '32px'
    }
  },
  
  section: {
    padding: {
      xs: '24px 16px',
      sm: '32px 24px',
      md: '48px 32px',
      lg: '64px 48px',
      xl: '80px 64px'
    }
  }
};

// Responsive utilities
export class ResponsiveUtils {
  static getValue<T>(
    values: { xs?: T; sm?: T; md?: T; lg?: T; xl?: T },
    breakpoint: keyof typeof breakpoints.values
  ): T | undefined {
    const keys = Object.keys(breakpoints.values) as Array<keyof typeof breakpoints.values>;
    const index = keys.indexOf(breakpoint);
    
    for (let i = index; i >= 0; i--) {
      const key = keys[i];
      if (values[key] !== undefined) {
        return values[key];
      }
    }
    
    return undefined;
  }
  
  static generateResponsiveStyles(
    property: string,
    values: { xs?: any; sm?: any; md?: any; lg?: any; xl?: any }
  ): string {
    let styles = '';
    
    Object.entries(values).forEach(([breakpoint, value]) => {
      if (value !== undefined) {
        if (breakpoint === 'xs') {
          styles += `${property}: ${value};`;
        } else {
          styles += `
            ${breakpoints.up(breakpoint as keyof typeof breakpoints.values)} {
              ${property}: ${value};
            }
          `;
        }
      }
    });
    
    return styles;
  }
}

// Responsive hooks
export const useResponsive = () => {
  const [currentBreakpoint, setCurrentBreakpoint] = useState<keyof typeof breakpoints.values>('xs');
  
  useEffect(() => {
    const checkBreakpoint = () => {
      const width = window.innerWidth;
      const breakpointValues = Object.entries(breakpoints.values)
        .sort(([, a], [, b]) => b - a);
      
      for (const [key, value] of breakpointValues) {
        if (width >= value) {
          setCurrentBreakpoint(key as keyof typeof breakpoints.values);
          break;
        }
      }
    };
    
    checkBreakpoint();
    window.addEventListener('resize', checkBreakpoint);
    
    return () => window.removeEventListener('resize', checkBreakpoint);
  }, []);
  
  const isUp = (breakpoint: keyof typeof breakpoints.values) => {
    const currentIndex = Object.keys(breakpoints.values).indexOf(currentBreakpoint);
    const targetIndex = Object.keys(breakpoints.values).indexOf(breakpoint);
    return currentIndex >= targetIndex;
  };
  
  const isDown = (breakpoint: keyof typeof breakpoints.values) => {
    const currentIndex = Object.keys(breakpoints.values).indexOf(currentBreakpoint);
    const targetIndex = Object.keys(breakpoints.values).indexOf(breakpoint);
    return currentIndex <= targetIndex;
  };
  
  return {
    currentBreakpoint,
    isUp,
    isDown,
    isMobile: !isUp('md'),
    isTablet: isUp('sm') && isDown('md'),
    isDesktop: isUp('lg')
  };
};
```

**검증 기준**:
- [ ] 브레이크포인트 정의
- [ ] 미디어 쿼리 헬퍼
- [ ] 반응형 유틸리티
- [ ] 반응형 훅 구현

---

### Task 7.10: Material-UI 커스터마이징

#### SubTask 7.10.1: MUI 테마 커스터마이징
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/styles/mui-theme.ts
import { createTheme, ThemeOptions } from '@mui/material/styles';
import { designTokens } from './tokens/design-tokens';
import { palette } from './palette';
import { typography } from './typography';

const baseThemeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: palette.brand.primary.main,
      light: palette.brand.primary.light,
      dark: palette.brand.primary.dark,
      contrastText: palette.brand.primary.contrastText
    },
    secondary: {
      main: palette.brand.secondary.main,
      light: palette.brand.secondary.light,
      dark: palette.brand.secondary.dark,
      contrastText: palette.brand.secondary.contrastText
    },
    error: {
      main: palette.semantic.error.main,
      light: palette.semantic.error.light,
      dark: palette.semantic.error.dark
    },
    warning: {
      main: palette.semantic.warning.main,
      light: palette.semantic.warning.light,
      dark: palette.semantic.warning.dark
    },
    info: {
      main: palette.semantic.info.main,
      light: palette.semantic.info.light,
      dark: palette.semantic.info.dark
    },
    success: {
      main: palette.semantic.success.main,
      light: palette.semantic.success.light,
      dark: palette.semantic.success.dark
    }
  },
  
  typography: {
    fontFamily: typography.fontFamily.sans,
    h1: typography.scale.h1,
    h2: typography.scale.h2,
    h3: typography.scale.h3,
    h4: typography.scale.h4,
    h5: typography.scale.h5,
    h6: typography.scale.h6,
    subtitle1: typography.scale.subtitle1,
    subtitle2: typography.scale.subtitle2,
    body1: typography.scale.body1,
    body2: typography.scale.body2,
    button: typography.scale.button,
    caption: typography.scale.caption,
    overline: typography.scale.overline
  },
  
  spacing: 8,
  
  shape: {
    borderRadius: 8
  },
  
  breakpoints: {
    values: designTokens.breakpoints
  },
  
  shadows: [
    'none',
    designTokens.shadows.xs,
    designTokens.shadows.sm,
    designTokens.shadows.base,
    designTokens.shadows.md,
    designTokens.shadows.lg,
    designTokens.shadows.xl,
    designTokens.shadows['2xl'],
    ...Array(17).fill(designTokens.shadows.xl)
  ] as any,
  
  transitions: {
    easing: {
      easeInOut: designTokens.animations.easing.easeInOut,
      easeOut: designTokens.animations.easing.easeOut,
      easeIn: designTokens.animations.easing.easeIn,
      sharp: designTokens.animations.easing.easeInOut
    },
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195
    }
  },
  
  zIndex: designTokens.zIndex,
  
  components: {
    // Component default props
    MuiButton: {
      defaultProps: {
        disableElevation: true
      }
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small'
      }
    },
    MuiPaper: {
      defaultProps: {
        elevation: 1
      }
    }
  }
};

// Create light theme
export const lightMuiTheme = createTheme({
  ...baseThemeOptions,
  palette: {
    ...baseThemeOptions.palette,
    mode: 'light',
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF'
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.60)',
      disabled: 'rgba(0, 0, 0, 0.38)'
    },
    divider: 'rgba(0, 0, 0, 0.12)'
  }
});

// Create dark theme
export const darkMuiTheme = createTheme({
  ...baseThemeOptions,
  palette: {
    ...baseThemeOptions.palette,
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#1E1E1E'
    },
    text: {
      primary: 'rgba(255, 255, 255, 0.87)',
      secondary: 'rgba(255, 255, 255, 0.60)',
      disabled: 'rgba(255, 255, 255, 0.38)'
    },
    divider: 'rgba(255, 255, 255, 0.12)'
  }
});

// Theme augmentation for custom properties
declare module '@mui/material/styles' {
  interface Theme {
    custom: {
      gradients: typeof palette.gradients;
      special: typeof palette.special;
    };
  }
  
  interface ThemeOptions {
    custom?: {
      gradients?: typeof palette.gradients;
      special?: typeof palette.special;
    };
  }
  
  interface Palette {
    gradient: {
      primary: string;
      secondary: string;
    };
  }
  
  interface PaletteOptions {
    gradient?: {
      primary?: string;
      secondary?: string;
    };
  }
}

// Extend themes with custom properties
[lightMuiTheme, darkMuiTheme].forEach(theme => {
  theme.custom = {
    gradients: palette.gradients,
    special: palette.special
  };
  
  theme.palette.gradient = {
    primary: palette.gradients.primary,
    secondary: palette.gradients.secondary
  };
});
```

**검증 기준**:
- [ ] MUI 테마 설정
- [ ] 라이트/다크 테마
- [ ] 커스텀 속성 추가
- [ ] 타입 확장

#### SubTask 7.10.2: 컴포넌트 스타일 오버라이드
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/styles/mui-overrides.ts
import { Components, Theme } from '@mui/material/styles';

export const componentOverrides = (theme: Theme): Components => ({
  // Button overrides
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: theme.shape.borderRadius,
        textTransform: 'none',
        fontWeight: 500,
        padding: '8px 16px',
        transition: 'all 0.2s ease-in-out',
        
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: theme.shadows[4]
        }
      },
      
      contained: {
        boxShadow: 'none',
        
        '&:hover': {
          boxShadow: theme.shadows[2]
        }
      },
      
      outlined: {
        borderWidth: 2,
        
        '&:hover': {
          borderWidth: 2,
          backgroundColor: theme.palette.action.hover
        }
      },
      
      text: {
        '&:hover': {
          backgroundColor: theme.palette.action.hover
        }
      },
      
      sizeLarge: {
        padding: '12px 24px',
        fontSize: '1rem'
      },
      
      sizeSmall: {
        padding: '4px 10px',
        fontSize: '0.875rem'
      }
    },
    
    variants: [
      {
        props: { variant: 'gradient' },
        style: {
          background: theme.palette.gradient?.primary,
          color: '#FFFFFF',
          
          '&:hover': {
            background: theme.palette.gradient?.secondary
          }
        }
      }
    ]
  },
  
  // TextField overrides
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: theme.shape.borderRadius,
          
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: theme.palette.primary.main,
            borderWidth: 2
          },
          
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: 2
          }
        }
      }
    }
  },
  
  // Card overrides
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: theme.shape.borderRadius * 1.5,
        boxShadow: theme.shadows[1],
        transition: 'all 0.3s ease-in-out',
        
        '&:hover': {
          boxShadow: theme.shadows[4],
          transform: 'translateY(-2px)'
        }
      }
    }
  },
  
  // Paper overrides
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: 'none'
      },
      
      rounded: {
        borderRadius: theme.shape.borderRadius
      },
      
      elevation1: {
        boxShadow: theme.shadows[1]
      }
    }
  },
  
  // AppBar overrides
  MuiAppBar: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
        boxShadow: theme.shadows[1],
        borderBottom: `1px solid ${theme.palette.divider}`
      },
      
      colorPrimary: {
        backgroundColor: theme.palette.background.paper
      }
    }
  },
  
  // Drawer overrides
  MuiDrawer: {
    styleOverrides: {
      paper: {
        borderRight: 'none',
        boxShadow: theme.shadows[2]
      }
    }
  },
  
  // Dialog overrides
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: theme.shape.borderRadius * 2,
        boxShadow: theme.shadows[8]
      }
    }
  },
  
  // Alert overrides
  MuiAlert: {
    styleOverrides: {
      root: {
        borderRadius: theme.shape.borderRadius,
        alignItems: 'center'
      },
      
      standardSuccess: {
        backgroundColor: palette.semantic.success.bg,
        color: palette.semantic.success.dark
      },
      
      standardError: {
        backgroundColor: palette.semantic.error.bg,
        color: palette.semantic.error.dark
      },
      
      standardWarning: {
        backgroundColor: palette.semantic.warning.bg,
        color: palette.semantic.warning.dark
      },
      
      standardInfo: {
        backgroundColor: palette.semantic.info.bg,
        color: palette.semantic.info.dark
      }
    }
  },
  
  // Chip overrides
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: theme.shape.borderRadius,
        fontWeight: 500
      },
      
      outlined: {
        borderWidth: 2
      }
    }
  },
  
  // Tooltip overrides
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        backgroundColor: theme.palette.grey[900],
        fontSize: '0.75rem',
        padding: '6px 12px',
        borderRadius: theme.shape.borderRadius / 2
      },
      
      arrow: {
        color: theme.palette.grey[900]
      }
    }
  },
  
  // Table overrides
  MuiTableCell: {
    styleOverrides: {
      root: {
        borderBottom: `1px solid ${theme.palette.divider}`
      },
      
      head: {
        fontWeight: 600,
        backgroundColor: theme.palette.action.hover
      }
    }
  },
  
  // Switch overrides
  MuiSwitch: {
    styleOverrides: {
      root: {
        width: 42,
        height: 26,
        padding: 0
      },
      
      switchBase: {
        padding: 0,
        margin: 2,
        transitionDuration: '300ms',
        
        '&.Mui-checked': {
          transform: 'translateX(16px)',
          
          '& + .MuiSwitch-track': {
            backgroundColor: theme.palette.primary.main,
            opacity: 1
          }
        }
      },
      
      thumb: {
        boxSizing: 'border-box',
        width: 22,
        height: 22
      },
      
      track: {
        borderRadius: 26 / 2,
        backgroundColor: theme.palette.grey[400],
        opacity: 1
      }
    }
  }
});

// Apply overrides to theme
export const applyComponentOverrides = (theme: Theme): Theme => {
  theme.components = {
    ...theme.components,
    ...componentOverrides(theme)
  };
  return theme;
};
```

**검증 기준**:
- [ ] 컴포넌트 스타일 오버라이드
- [ ] 일관된 디자인 언어
- [ ] 호버/포커스 효과
- [ ] 커스텀 변형 추가

# Phase 7: 프론트엔드 구현 - Tasks 7.10-7.14 SubTask 작업지시서 (계속)

### Task 7.10: Material-UI 커스터마이징 (계속)

#### SubTask 7.10.3: 커스텀 MUI 컴포넌트 변형
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/styles/mui-variants.ts
import { createTheme } from '@mui/material/styles';

declare module '@mui/material/Button' {
  interface ButtonPropsVariantOverrides {
    gradient: true;
    dashed: true;
    ghost: true;
  }
}

declare module '@mui/material/Paper' {
  interface PaperPropsVariantOverrides {
    outlined: true;
    gradient: true;
  }
}

declare module '@mui/material/Chip' {
  interface ChipPropsColorOverrides {
    gradient: true;
  }
}

export const customVariants = {
  MuiButton: {
    variants: [
      {
        props: { variant: 'gradient' },
        style: ({ theme }: any) => ({
          background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
          border: 0,
          borderRadius: 3,
          boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
          color: 'white',
          height: 48,
          padding: '0 30px',
          
          '&:hover': {
            background: 'linear-gradient(45deg, #FE6B8B 60%, #FF8E53 100%)',
            boxShadow: '0 4px 6px 2px rgba(255, 105, 135, .4)'
          }
        })
      },
      {
        props: { variant: 'dashed' },
        style: ({ theme }: any) => ({
          border: `2px dashed ${theme.palette.primary.main}`,
          backgroundColor: 'transparent',
          color: theme.palette.primary.main,
          
          '&:hover': {
            backgroundColor: theme.palette.action.hover,
            borderStyle: 'solid'
          }
        })
      },
      {
        props: { variant: 'ghost' },
        style: ({ theme }: any) => ({
          backgroundColor: 'transparent',
          color: theme.palette.text.primary,
          
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)'
          },
          
          '&:active': {
            backgroundColor: 'rgba(0, 0, 0, 0.08)'
          }
        })
      }
    ]
  },
  
  MuiPaper: {
    variants: [
      {
        props: { variant: 'outlined' },
        style: ({ theme }: any) => ({
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: 'none'
        })
      },
      {
        props: { variant: 'gradient' },
        style: ({ theme }: any) => ({
          background: `linear-gradient(135deg, ${theme.palette.primary.light} 0%, ${theme.palette.secondary.light} 100%)`,
          color: theme.palette.common.white
        })
      }
    ]
  },
  
  MuiChip: {
    variants: [
      {
        props: { color: 'gradient' },
        style: ({ theme }: any) => ({
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          color: 'white',
          
          '& .MuiChip-deleteIcon': {
            color: 'rgba(255, 255, 255, 0.7)',
            
            '&:hover': {
              color: 'white'
            }
          }
        })
      }
    ]
  },
  
  MuiTextField: {
    variants: [
      {
        props: { variant: 'filled' },
        style: ({ theme }: any) => ({
          '& .MuiFilledInput-root': {
            backgroundColor: theme.palette.action.hover,
            borderRadius: theme.shape.borderRadius,
            
            '&:before, &:after': {
              display: 'none'
            },
            
            '&:hover': {
              backgroundColor: theme.palette.action.selected
            },
            
            '&.Mui-focused': {
              backgroundColor: theme.palette.background.paper,
              boxShadow: `0 0 0 2px ${theme.palette.primary.main}`
            }
          }
        })
      }
    ]
  }
};

// Custom component extensions
export const extendedComponents = {
  // Gradient Button
  GradientButton: ({ children, ...props }: any) => (
    <Button variant="gradient" {...props}>
      {children}
    </Button>
  ),
  
  // Loading Button
  LoadingButton: ({ loading, children, ...props }: any) => (
    <Button
      disabled={loading}
      startIcon={loading ? <CircularProgress size={16} /> : props.startIcon}
      {...props}
    >
      {children}
    </Button>
  ),
  
  // Icon Button with Tooltip
  TooltipIconButton: ({ title, ...props }: any) => (
    <Tooltip title={title}>
      <IconButton {...props} />
    </Tooltip>
  ),
  
  // Status Chip
  StatusChip: ({ status, ...props }: any) => {
    const statusColors: Record<string, any> = {
      active: 'success',
      inactive: 'default',
      pending: 'warning',
      error: 'error'
    };
    
    return (
      <Chip
        color={statusColors[status] || 'default'}
        size="small"
        {...props}
        label={status}
      />
    );
  }
};
```

**검증 기준**:
- [ ] 커스텀 변형 정의
- [ ] 타입 확장
- [ ] 확장 컴포넌트
- [ ] 일관된 스타일링

#### SubTask 7.10.4: MUI 시스템 유틸리티 설정
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```typescript
// frontend/src/styles/mui-system.ts
import { styled, css } from '@mui/material/styles';
import { Box, BoxProps } from '@mui/material';

// Utility props system
export const systemProps = {
  // Spacing utilities
  mt: (value: number) => ({ marginTop: value }),
  mb: (value: number) => ({ marginBottom: value }),
  ml: (value: number) => ({ marginLeft: value }),
  mr: (value: number) => ({ marginRight: value }),
  mx: (value: number) => ({ marginLeft: value, marginRight: value }),
  my: (value: number) => ({ marginTop: value, marginBottom: value }),
  m: (value: number) => ({ margin: value }),
  
  pt: (value: number) => ({ paddingTop: value }),
  pb: (value: number) => ({ paddingBottom: value }),
  pl: (value: number) => ({ paddingLeft: value }),
  pr: (value: number) => ({ paddingRight: value }),
  px: (value: number) => ({ paddingLeft: value, paddingRight: value }),
  py: (value: number) => ({ paddingTop: value, paddingBottom: value }),
  p: (value: number) => ({ padding: value }),
  
  // Display utilities
  d: (value: string) => ({ display: value }),
  flex: () => ({ display: 'flex' }),
  inlineFlex: () => ({ display: 'inline-flex' }),
  block: () => ({ display: 'block' }),
  inlineBlock: () => ({ display: 'inline-block' }),
  none: () => ({ display: 'none' }),
  
  // Flexbox utilities
  flexDirection: (value: string) => ({ flexDirection: value }),
  flexWrap: (value: string) => ({ flexWrap: value }),
  justifyContent: (value: string) => ({ justifyContent: value }),
  alignItems: (value: string) => ({ alignItems: value }),
  alignSelf: (value: string) => ({ alignSelf: value }),
  flexGrow: (value: number) => ({ flexGrow: value }),
  flexShrink: (value: number) => ({ flexShrink: value }),
  
  // Size utilities
  w: (value: string | number) => ({ width: value }),
  h: (value: string | number) => ({ height: value }),
  minW: (value: string | number) => ({ minWidth: value }),
  maxW: (value: string | number) => ({ maxWidth: value }),
  minH: (value: string | number) => ({ minHeight: value }),
  maxH: (value: string | number) => ({ maxHeight: value }),
  
  // Position utilities
  position: (value: string) => ({ position: value }),
  top: (value: string | number) => ({ top: value }),
  right: (value: string | number) => ({ right: value }),
  bottom: (value: string | number) => ({ bottom: value }),
  left: (value: string | number) => ({ left: value }),
  zIndex: (value: number) => ({ zIndex: value })
};

// Styled system components
export const Flex = styled(Box)<{
  direction?: 'row' | 'column';
  wrap?: boolean;
  justify?: string;
  align?: string;
  gap?: number;
}>(({ theme, direction = 'row', wrap = false, justify, align, gap }) => ({
  display: 'flex',
  flexDirection: direction,
  flexWrap: wrap ? 'wrap' : 'nowrap',
  justifyContent: justify,
  alignItems: align,
  gap: gap ? theme.spacing(gap) : undefined
}));

export const Grid = styled(Box)<{
  cols?: number;
  gap?: number;
  minChildWidth?: string;
}>(({ theme, cols, gap = 2, minChildWidth }) => ({
  display: 'grid',
  gridTemplateColumns: cols 
    ? `repeat(${cols}, 1fr)`
    : minChildWidth 
      ? `repeat(auto-fit, minmax(${minChildWidth}, 1fr))`
      : undefined,
  gap: theme.spacing(gap)
}));

export const Stack = styled(Box)<{
  spacing?: number;
  direction?: 'row' | 'column';
  divider?: boolean;
}>(({ theme, spacing = 2, direction = 'column', divider }) => ({
  display: 'flex',
  flexDirection: direction,
  gap: theme.spacing(spacing),
  
  ...(divider && {
    '& > *:not(:last-child)': {
      borderBottom: direction === 'column' ? `1px solid ${theme.palette.divider}` : undefined,
      borderRight: direction === 'row' ? `1px solid ${theme.palette.divider}` : undefined,
      paddingBottom: direction === 'column' ? theme.spacing(spacing) : undefined,
      paddingRight: direction === 'row' ? theme.spacing(spacing) : undefined
    }
  })
}));

export const Center = styled(Box)({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center'
});

export const Container = styled(Box)<{
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}>(({ theme, maxWidth = 'lg' }) => ({
  width: '100%',
  marginLeft: 'auto',
  marginRight: 'auto',
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  
  maxWidth: {
    xs: '444px',
    sm: '600px',
    md: '900px',
    lg: '1200px',
    xl: '1536px'
  }[maxWidth],
  
  [theme.breakpoints.up('sm')]: {
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3)
  }
}));

// System utility hooks
export const useSystemStyles = () => {
  const theme = useTheme();
  
  return {
    spacing: (value: number) => theme.spacing(value),
    
    breakpoint: {
      up: (key: string) => theme.breakpoints.up(key as any),
      down: (key: string) => theme.breakpoints.down(key as any),
      between: (start: string, end: string) => 
        theme.breakpoints.between(start as any, end as any)
    },
    
    shadow: (level: number) => theme.shadows[level],
    
    transition: (props: string[], duration = 'standard') => 
      theme.transitions.create(props, {
        duration: theme.transitions.duration[duration as keyof typeof theme.transitions.duration]
      })
  };
};

// Responsive system
export const responsive = {
  hide: {
    xs: css`
      @media (max-width: 599px) {
        display: none;
      }
    `,
    sm: css`
      @media (min-width: 600px) and (max-width: 899px) {
        display: none;
      }
    `,
    md: css`
      @media (min-width: 900px) and (max-width: 1199px) {
        display: none;
      }
    `,
    lg: css`
      @media (min-width: 1200px) and (max-width: 1535px) {
        display: none;
      }
    `,
    xl: css`
      @media (min-width: 1536px) {
        display: none;
      }
    `
  },
  
  show: {
    xs: css`
      @media (min-width: 600px) {
        display: none;
      }
    `,
    sm: css`
      @media (max-width: 599px), (min-width: 900px) {
        display: none;
      }
    `,
    md: css`
      @media (max-width: 899px), (min-width: 1200px) {
        display: none;
      }
    `,
    lg: css`
      @media (max-width: 1199px), (min-width: 1536px) {
        display: none;
      }
    `,
    xl: css`
      @media (max-width: 1535px) {
        display: none;
      }
    `
  }
};
```

**검증 기준**:
- [ ] 시스템 유틸리티 props
- [ ] 스타일드 시스템 컴포넌트
- [ ] 반응형 유틸리티
- [ ] 시스템 스타일 훅

---

### Task 7.11: 글로벌 스타일 및 CSS 시스템

#### SubTask 7.11.1: 글로벌 CSS 리셋 및 기본 스타일
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```css
/* frontend/src/styles/global.css */
/* CSS Reset and Base Styles */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: var(--font-primary);
  background-color: var(--color-bg-default);
  color: var(--color-text-primary);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  margin: 0;
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}

p {
  margin: 0 0 1rem;
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

/* Lists */
ul, ol {
  margin: 0;
  padding: 0;
  list-style: none;
}

/* Forms */
input, textarea, select, button {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  color: inherit;
}

button {
  cursor: pointer;
  border: none;
  background: transparent;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Images */
img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
  height: auto;
}

/* Tables */
table {
  border-collapse: collapse;
  width: 100%;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border-medium);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-strong);
}

/* Selection */
::selection {
  background: var(--color-primary);
  color: white;
}

/* Focus styles */
*:focus {
  outline: none;
}

*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Utility classes */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.visually-hidden {
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  white-space: nowrap;
  width: 1px;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.break-words {
  word-wrap: break-word;
  word-break: break-word;
}

/* Loading skeleton */
@keyframes skeleton-loading {
  0% {
    background-color: hsl(200, 20%, 80%);
  }
  100% {
    background-color: hsl(200, 20%, 95%);
  }
}

.skeleton {
  animation: skeleton-loading 1s linear infinite alternate;
  border-radius: 4px;
}

/* Transitions */
.transition-all {
  transition: all 0.3s ease;
}

.transition-colors {
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}

.transition-transform {
  transition: transform 0.3s ease;
}

.transition-opacity {
  transition: opacity 0.3s ease;
}
```

```typescript
// frontend/src/styles/GlobalStyles.tsx
import { GlobalStyles as MUIGlobalStyles } from '@mui/material';

export const GlobalStyles = () => (
  <MUIGlobalStyles
    styles={(theme) => ({
      ':root': {
        // Color variables
        '--color-primary': theme.palette.primary.main,
        '--color-primary-light': theme.palette.primary.light,
        '--color-primary-dark': theme.palette.primary.dark,
        '--color-secondary': theme.palette.secondary.main,
        '--color-success': theme.palette.success.main,
        '--color-warning': theme.palette.warning.main,
        '--color-error': theme.palette.error.main,
        '--color-info': theme.palette.info.main,
        
        // Background variables
        '--color-bg-default': theme.palette.background.default,
        '--color-bg-paper': theme.palette.background.paper,
        '--color-bg-elevated': theme.palette.mode === 'light' ? '#FFFFFF' : '#2A2A2A',
        
        // Text variables
        '--color-text-primary': theme.palette.text.primary,
        '--color-text-secondary': theme.palette.text.secondary,
        '--color-text-disabled': theme.palette.text.disabled,
        
        // Border variables
        '--color-border-light': theme.palette.divider,
        '--color-border-medium': theme.palette.mode === 'light' 
          ? 'rgba(0, 0, 0, 0.23)' 
          : 'rgba(255, 255, 255, 0.23)',
        '--color-border-strong': theme.palette.mode === 'light'
          ? 'rgba(0, 0, 0, 0.42)'
          : 'rgba(255, 255, 255, 0.42)',
        
        // Font variables
        '--font-primary': theme.typography.fontFamily,
        '--font-mono': '"JetBrains Mono", monospace',
        '--font-weight-regular': theme.typography.fontWeightRegular,
        '--font-weight-medium': theme.typography.fontWeightMedium,
        '--font-weight-semibold': 600,
        '--font-weight-bold': theme.typography.fontWeightBold,
        
        // Spacing variables
        '--spacing-xs': theme.spacing(0.5),
        '--spacing-sm': theme.spacing(1),
        '--spacing-md': theme.spacing(2),
        '--spacing-lg': theme.spacing(3),
        '--spacing-xl': theme.spacing(4),
        '--spacing-2xl': theme.spacing(6),
        
        // Line height variables
        '--line-height-tight': 1.25,
        '--line-height-normal': 1.5,
        '--line-height-relaxed': 1.75,
        
        // Border radius variables
        '--radius-sm': '4px',
        '--radius-md': '8px',
        '--radius-lg': '12px',
        '--radius-xl': '16px',
        '--radius-full': '9999px',
        
        // Shadow variables
        '--shadow-sm': theme.shadows[1],
        '--shadow-md': theme.shadows[3],
        '--shadow-lg': theme.shadows[6],
        '--shadow-xl': theme.shadows[9],
        
        // Z-index variables
        '--z-dropdown': theme.zIndex.dropdown,
        '--z-sticky': theme.zIndex.appBar,
        '--z-fixed': theme.zIndex.drawer,
        '--z-modal': theme.zIndex.modal,
        '--z-popover': theme.zIndex.tooltip,
        '--z-toast': theme.zIndex.snackbar
      },
      
      // Print styles
      '@media print': {
        body: {
          backgroundColor: 'white',
          color: 'black'
        },
        
        '.no-print': {
          display: 'none !important'
        }
      },
      
      // Accessibility improvements
      '@media (prefers-reduced-motion: reduce)': {
        '*': {
          animationDuration: '0.01ms !important',
          animationIterationCount: '1 !important',
          transitionDuration: '0.01ms !important',
          scrollBehavior: 'auto !important'
        }
      }
    })}
  />
);
```

**검증 기준**:
- [ ] CSS 리셋 적용
- [ ] CSS 변수 정의
- [ ] 유틸리티 클래스
- [ ] 접근성 고려

#### SubTask 7.11.2: CSS-in-JS 설정 및 스타일드 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/styles/styled-components.ts
import { styled } from '@mui/material/styles';
import { shouldForwardProp } from '@mui/system';

// Custom styled utility
export const createStyled = <T extends Record<string, any>>(
  component: any,
  options?: {
    shouldForwardProp?: (prop: string) => boolean;
    name?: string;
    slot?: string;
  }
) => {
  return styled(component, {
    shouldForwardProp: options?.shouldForwardProp || shouldForwardProp,
    name: options?.name,
    slot: options?.slot
  })<T>;
};

// Common styled components
export const PageContainer = styled('div')(({ theme }) => ({
  minHeight: '100vh',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
  
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(2)
  }
}));

export const Section = styled('section')<{
  variant?: 'default' | 'elevated' | 'transparent';
  spacing?: 'sm' | 'md' | 'lg';
}>(({ theme, variant = 'default', spacing = 'md' }) => ({
  padding: {
    sm: theme.spacing(2),
    md: theme.spacing(4),
    lg: theme.spacing(6)
  }[spacing],
  
  backgroundColor: {
    default: theme.palette.background.paper,
    elevated: theme.palette.background.default,
    transparent: 'transparent'
  }[variant],
  
  borderRadius: variant !== 'transparent' ? theme.shape.borderRadius : 0,
  
  ...(variant === 'elevated' && {
    boxShadow: theme.shadows[2]
  })
}));

export const FlexBox = styled('div')<{
  direction?: 'row' | 'column';
  justify?: string;
  align?: string;
  gap?: number;
  wrap?: boolean;
  fullWidth?: boolean;
  fullHeight?: boolean;
}>(({ 
  direction = 'row',
  justify = 'flex-start',
  align = 'stretch',
  gap = 0,
  wrap = false,
  fullWidth = false,
  fullHeight = false,
  theme 
}) => ({
  display: 'flex',
  flexDirection: direction,
  justifyContent: justify,
  alignItems: align,
  flexWrap: wrap ? 'wrap' : 'nowrap',
  gap: theme.spacing(gap),
  width: fullWidth ? '100%' : 'auto',
  height: fullHeight ? '100%' : 'auto'
}));

export const GridBox = styled('div')<{
  columns?: number | string;
  gap?: number;
  autoFit?: boolean;
  minColumnWidth?: string;
}>(({ theme, columns = 1, gap = 2, autoFit = false, minColumnWidth = '250px' }) => ({
  display: 'grid',
  gridTemplateColumns: autoFit 
    ? `repeat(auto-fit, minmax(${minColumnWidth}, 1fr))`
    : typeof columns === 'number' 
      ? `repeat(${columns}, 1fr)`
      : columns,
  gap: theme.spacing(gap)
}));

export const Card = styled('div')<{
  variant?: 'outlined' | 'elevated' | 'flat';
  clickable?: boolean;
  selected?: boolean;
}>(({ theme, variant = 'elevated', clickable = false, selected = false }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  transition: theme.transitions.create(['box-shadow', 'transform', 'border-color'], {
    duration: theme.transitions.duration.short
  }),
  
  ...(variant === 'outlined' && {
    border: `1px solid ${selected ? theme.palette.primary.main : theme.palette.divider}`,
    boxShadow: 'none'
  }),
  
  ...(variant === 'elevated' && {
    boxShadow: theme.shadows[selected ? 4 : 1]
  }),
  
  ...(variant === 'flat' && {
    boxShadow: 'none',
    backgroundColor: theme.palette.action.hover
  }),
  
  ...(clickable && {
    cursor: 'pointer',
    
    '&:hover': {
      boxShadow: theme.shadows[4],
      transform: 'translateY(-2px)'
    },
    
    '&:active': {
      transform: 'translateY(0)'
    }
  })
}));

export const Overlay = styled('div')<{
  visible?: boolean;
  blur?: boolean;
}>(({ theme, visible = true, blur = false }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  display: visible ? 'flex' : 'none',
  justifyContent: 'center',
  alignItems: 'center',
  zIndex: theme.zIndex.modal,
  
  ...(blur && {
    backdropFilter: 'blur(4px)'
  })
}));

export const Badge = styled('span')<{
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  size?: 'small' | 'medium' | 'large';
  variant?: 'filled' | 'outlined' | 'dot';
}>(({ theme, color = 'primary', size = 'medium', variant = 'filled' }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: {
    small: '0.75rem',
    medium: '0.875rem',
    large: '1rem'
  }[size],
  
  padding: variant === 'dot' ? 0 : {
    small: '2px 6px',
    medium: '4px 8px',
    large: '6px 12px'
  }[size],
  
  borderRadius: variant === 'dot' ? '50%' : theme.shape.borderRadius,
  
  ...(variant === 'dot' && {
    width: {
      small: 8,
      medium: 10,
      large: 12
    }[size],
    height: {
      small: 8,
      medium: 10,
      large: 12
    }[size]
  }),
  
  ...(variant === 'filled' && {
    backgroundColor: theme.palette[color].main,
    color: theme.palette[color].contrastText
  }),
  
  ...(variant === 'outlined' && {
    border: `1px solid ${theme.palette[color].main}`,
    color: theme.palette[color].main,
    backgroundColor: 'transparent'
  })
}));
```

**검증 기준**:
- [ ] Styled 컴포넌트 생성
- [ ] 재사용 가능한 스타일드 컴포넌트
- [ ] Props 기반 스타일링
- [ ] 테마 통합

#### SubTask 7.11.3: 애니메이션 및 트랜지션 시스템
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/styles/animations.ts
import { keyframes, css } from '@mui/material/styles';

// Keyframe animations
export const animations = {
  fadeIn: keyframes`
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  `,
  
  fadeOut: keyframes`
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  `,
  
  slideInLeft: keyframes`
    from {
      transform: translateX(-100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  `,
  
  slideInRight: keyframes`
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  `,
  
  slideInUp: keyframes`
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  `,
  
  slideInDown: keyframes`
    from {
      transform: translateY(-100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  `,
  
  zoomIn: keyframes`
    from {
      transform: scale(0);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  `,
  
  zoomOut: keyframes`
    from {
      transform: scale(1);
      opacity: 1;
    }
    to {
      transform: scale(0);
      opacity: 0;
    }
  `,
  
  rotate: keyframes`
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  `,
  
  pulse: keyframes`
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  `,
  
  shake: keyframes`
    0%, 100% {
      transform: translateX(0);
    }
    10%, 30%, 50%, 70%, 90% {
      transform: translateX(-10px);
    }
    20%, 40%, 60%, 80% {
      transform: translateX(10px);
    }
  `,
  
  bounce: keyframes`
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-30px);
    }
    60% {
      transform: translateY(-15px);
    }
  `,
  
  shimmer: keyframes`
    0% {
      background-position: -1000px 0;
    }
    100% {
      background-position: 1000px 0;
    }
  `,
  
  wave: keyframes`
    0% {
      transform: translateX(-100%);
    }
    50% {
      transform: translateX(0);
    }
    100% {
      transform: translateX(100%);
    }
  `
};

// Animation utilities
export const animationUtils = {
  // Apply animation
  apply: (
    name: keyof typeof animations,
    duration = '0.3s',
    timing = 'ease',
    delay = '0s',
    fillMode = 'both'
  ) => css`
    animation: ${animations[name]} ${duration} ${timing} ${delay} ${fillMode};
  `,
  
  // Transition presets
  transition: {
    fast: css`
      transition: all 0.15s ease;
    `,
    
    base: css`
      transition: all 0.3s ease;
    `,
    
    slow: css`
      transition: all 0.5s ease;
    `,
    
    bounce: css`
      transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    `,
    
    smooth: css`
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    `
  },
  
  // Hover effects
  hover: {
    lift: css`
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    `,
    
    scale: css`
      transition: transform 0.2s ease;
      
      &:hover {
        transform: scale(1.05);
      }
    `,
    
    glow: css`
      transition: box-shadow 0.2s ease;
      
      &:hover {
        box-shadow: 0 0 20px rgba(33, 150, 243, 0.4);
      }
    `,
    
    fade: css`
      transition: opacity 0.2s ease;
      
      &:hover {
        opacity: 0.8;
      }
    `
  }
};

// Animation hooks
export const useAnimation = (
  animationName: keyof typeof animations,
  options?: {
    duration?: string;
    delay?: string;
    timing?: string;
    trigger?: boolean;
  }
) => {
  const [isAnimating, setIsAnimating] = useState(false);
  
  useEffect(() => {
    if (options?.trigger) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setIsAnimating(false);
      }, parseInt(options.duration || '300'));
      
      return () => clearTimeout(timer);
    }
  }, [options?.trigger]);
  
  return {
    animationStyle: isAnimating ? animationUtils.apply(
      animationName,
      options?.duration,
      options?.timing,
      options?.delay
    ) : undefined,
    isAnimating
  };
};

// Framer Motion variants
export const motionVariants = {
  // Page transitions
  page: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 }
  },
  
  // Modal animations
  modal: {
    initial: { scale: 0.9, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.9, opacity: 0 }
  },
  
  // List animations
  list: {
    initial: { opacity: 0 },
    animate: { 
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  },
  
  listItem: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  },
  
  // Drawer animations
  drawer: {
    left: {
      initial: { x: '-100%' },
      animate: { x: 0 },
      exit: { x: '-100%' }
    },
    right: {
      initial: { x: '100%' },
      animate: { x: 0 },
      exit: { x: '100%' }
    },
    top: {
      initial: { y: '-100%' },
      animate: { y: 0 },
      exit: { y: '-100%' }
    },
    bottom: {
      initial: { y: '100%' },
      animate: { y: 0 },
      exit: { y: '100%' }
    }
  }
};
```

**검증 기준**:
- [ ] Keyframe 애니메이션 정의
- [ ] 애니메이션 유틸리티
- [ ] 호버 효과 프리셋
- [ ] Motion 변형 정의

#### SubTask 7.11.4: 유틸리티 클래스 및 믹스인
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 3시간

**작업 내용**:

```typescript
// frontend/src/styles/utilities.ts
import { css } from '@mui/material/styles';

// Mixins
export const mixins = {
  // Text truncation
  truncate: (lines = 1) => css`
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: ${lines};
    -webkit-box-orient: vertical;
    word-break: break-word;
  `,
  
  // Absolute positioning
  absolute: (top?: string, right?: string, bottom?: string, left?: string) => css`
    position: absolute;
    ${top !== undefined && `top: ${top};`}
    ${right !== undefined && `right: ${right};`}
    ${bottom !== undefined && `bottom: ${bottom};`}
    ${left !== undefined && `left: ${left};`}
  `,
  
  // Fixed positioning
  fixed: (top?: string, right?: string, bottom?: string, left?: string) => css`
    position: fixed;
    ${top !== undefined && `top: ${top};`}
    ${right !== undefined && `right: ${right};`}
    ${bottom !== undefined && `bottom: ${bottom};`}
    ${left !== undefined && `left: ${left};`}
  `,
  
  // Flexbox center
  flexCenter: css`
    display: flex;
    justify-content: center;
    align-items: center;
  `,
  
  // Flexbox between
  flexBetween: css`
    display: flex;
    justify-content: space-between;
    align-items: center;
  `,
  
  // Cover parent
  coverParent: css`
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  `,
  
  // Circle shape
  circle: (size: string) => css`
    width: ${size};
    height: ${size};
    border-radius: 50%;
  `,
  
  // Aspect ratio
  aspectRatio: (ratio: string) => css`
    position: relative;
    
    &::before {
      content: '';
      display: block;
      padding-bottom: calc(100% / (${ratio}));
    }
    
    & > * {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
  `,
  
  // Glass morphism
  glassMorphism: (blur = '10px', opacity = 0.7) => css`
    backdrop-filter: blur(${blur});
    background: rgba(255, 255, 255, ${opacity});
    border: 1px solid rgba(255, 255, 255, 0.18);
  `,
  
  // Gradient text
  gradientText: (gradient: string) => css`
    background: ${gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  `,
  
  // Custom scrollbar
  customScrollbar: (
    width = '8px',
    trackColor = '#f1f1f1',
    thumbColor = '#888'
  ) => css`
    &::-webkit-scrollbar {
      width: ${width};
      height: ${width};
    }
    
    &::-webkit-scrollbar-track {
      background: ${trackColor};
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: ${thumbColor};
      border-radius: 4px;
      
      &:hover {
        background: ${thumbColor}dd;
      }
    }
  `,
  
  // Hide scrollbar
  hideScrollbar: css`
    scrollbar-width: none;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
  `,
  
  // Safe area insets (for mobile)
  safeArea: css`
    padding-top: env(safe-area-inset-top);
    padding-right: env(safe-area-inset-right);
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
  `
};

// Utility classes generator
export const generateUtilityClasses = () => {
  const utilities: Record<string, any> = {};
  
  // Display utilities
  ['none', 'block', 'inline-block', 'inline', 'flex', 'inline-flex', 'grid'].forEach(value => {
    utilities[`.d-${value}`] = { display: value };
  });
  
  // Position utilities
  ['static', 'relative', 'absolute', 'fixed', 'sticky'].forEach(value => {
    utilities[`.position-${value}`] = { position: value };
  });
  
  // Overflow utilities
  ['auto', 'hidden', 'visible', 'scroll'].forEach(value => {
    utilities[`.overflow-${value}`] = { overflow: value };
    utilities[`.overflow-x-${value}`] = { overflowX: value };
    utilities[`.overflow-y-${value}`] = { overflowY: value };
  });
  
  // Text alignment
  ['left', 'center', 'right', 'justify'].forEach(value => {
    utilities[`.text-${value}`] = { textAlign: value };
  });
  
  // Font weight
  [100, 200, 300, 400, 500, 600, 700, 800, 900].forEach(value => {
    utilities[`.fw-${value}`] = { fontWeight: value };
  });
  
  // Width utilities
  [25, 50, 75, 100].forEach(value => {
    utilities[`.w-${value}`] = { width: `${value}%` };
  });
  
  // Height utilities
  [25, 50, 75, 100].forEach(value => {
    utilities[`.h-${value}`] = { height: `${value}%` };
  });
  
  // Margin utilities
  [0, 1, 2, 3, 4, 5].forEach(value => {
    const spacing = value * 8;
    utilities[`.m-${value}`] = { margin: `${spacing}px` };
    utilities[`.mt-${value}`] = { marginTop: `${spacing}px` };
    utilities[`.mb-${value}`] = { marginBottom: `${spacing}px` };
    utilities[`.ml-${value}`] = { marginLeft: `${spacing}px` };
    utilities[`.mr-${value}`] = { marginRight: `${spacing}px` };
    utilities[`.mx-${value}`] = { marginLeft: `${spacing}px`, marginRight: `${spacing}px` };
    utilities[`.my-${value}`] = { marginTop: `${spacing}px`, marginBottom: `${spacing}px` };
  });
  
  // Padding utilities
  [0, 1, 2, 3, 4, 5].forEach(value => {
    const spacing = value * 8;
    utilities[`.p-${value}`] = { padding: `${spacing}px` };
    utilities[`.pt-${value}`] = { paddingTop: `${spacing}px` };
    utilities[`.pb-${value}`] = { paddingBottom: `${spacing}px` };
    utilities[`.pl-${value}`] = { paddingLeft: `${spacing}px` };
    utilities[`.pr-${value}`] = { paddingRight: `${spacing}px` };
    utilities[`.px-${value}`] = { paddingLeft: `${spacing}px`, paddingRight: `${spacing}px` };
    utilities[`.py-${value}`] = { paddingTop: `${spacing}px`, paddingBottom: `${spacing}px` };
  });
  
  return utilities;
};
```

**검증 기준**:
- [ ] 재사용 가능한 믹스인
- [ ] 유틸리티 클래스 생성
- [ ] 특수 효과 믹스인
- [ ] 반응형 유틸리티

---
# Phase 7: 프론트엔드 구현 - Tasks 7.12-7.14 SubTask 작업지시서 (계속)

### Task 7.12: 원자 컴포넌트 (Buttons, Inputs, etc.)

#### SubTask 7.12.1: 버튼 컴포넌트 시스템
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/atoms/Button/Button.tsx
import React, { forwardRef } from 'react';
import { Button as MUIButton, ButtonProps as MUIButtonProps, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';

export interface ButtonProps extends Omit<MUIButtonProps, 'variant'> {
  variant?: 'contained' | 'outlined' | 'text' | 'gradient' | 'ghost' | 'link';
  loading?: boolean;
  loadingText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'start' | 'end';
  fullWidth?: boolean;
  rounded?: boolean;
  animate?: boolean;
}

const StyledButton = styled(MUIButton, {
  shouldForwardProp: (prop) => 
    !['loading', 'loadingText', 'icon', 'iconPosition', 'rounded', 'animate'].includes(prop as string)
})<ButtonProps>(({ theme, variant, rounded, animate, fullWidth }) => ({
  textTransform: 'none',
  fontWeight: 500,
  transition: 'all 0.2s ease-in-out',
  
  ...(rounded && {
    borderRadius: '9999px'
  }),
  
  ...(animate && {
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: theme.shadows[4]
    },
    '&:active': {
      transform: 'translateY(0)'
    }
  }),
  
  ...(variant === 'gradient' && {
    background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
    color: '#FFFFFF',
    border: 'none',
    
    '&:hover': {
      background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
    }
  }),
  
  ...(variant === 'ghost' && {
    backgroundColor: 'transparent',
    border: 'none',
    
    '&:hover': {
      backgroundColor: theme.palette.action.hover
    }
  }),
  
  ...(variant === 'link' && {
    backgroundColor: 'transparent',
    border: 'none',
    textDecoration: 'underline',
    padding: 0,
    minWidth: 'auto',
    
    '&:hover': {
      backgroundColor: 'transparent',
      textDecoration: 'underline'
    }
  }),
  
  ...(fullWidth && {
    width: '100%'
  })
}));

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    children,
    loading = false,
    loadingText,
    icon,
    iconPosition = 'start',
    disabled,
    startIcon,
    endIcon,
    variant = 'contained',
    ...props 
  }, ref) => {
    const buttonIcon = icon || (iconPosition === 'start' ? startIcon : endIcon);
    
    return (
      <StyledButton
        ref={ref}
        variant={variant === 'gradient' || variant === 'ghost' || variant === 'link' ? 'contained' : variant}
        disabled={disabled || loading}
        startIcon={!loading && iconPosition === 'start' ? buttonIcon : undefined}
        endIcon={!loading && iconPosition === 'end' ? buttonIcon : undefined}
        {...props}
      >
        {loading ? (
          <>
            <CircularProgress size={16} color="inherit" style={{ marginRight: 8 }} />
            {loadingText || children}
          </>
        ) : (
          children
        )}
      </StyledButton>
    );
  }
);

Button.displayName = 'Button';

// Icon Button Component
export interface IconButtonProps {
  icon: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' | 'inherit';
  tooltip?: string;
  badge?: number | string;
  badgeColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = 'medium',
  color = 'inherit',
  tooltip,
  badge,
  badgeColor = 'error',
  onClick,
  disabled = false,
  loading = false
}) => {
  const button = (
    <MUIIconButton
      size={size}
      color={color}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <CircularProgress size={size === 'small' ? 16 : size === 'large' ? 24 : 20} />
      ) : badge !== undefined ? (
        <Badge badgeContent={badge} color={badgeColor}>
          {icon}
        </Badge>
      ) : (
        icon
      )}
    </MUIIconButton>
  );
  
  return tooltip ? (
    <Tooltip title={tooltip}>
      {button}
    </Tooltip>
  ) : button;
};

// Button Group Component
export interface ButtonGroupProps {
  buttons: Array<{
    label: string;
    value: string;
    icon?: React.ReactNode;
    disabled?: boolean;
  }>;
  value?: string;
  onChange?: (value: string) => void;
  variant?: 'contained' | 'outlined' | 'text';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary';
  fullWidth?: boolean;
  exclusive?: boolean;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  buttons,
  value,
  onChange,
  variant = 'outlined',
  size = 'medium',
  color = 'primary',
  fullWidth = false,
  exclusive = true
}) => {
  const handleChange = (_: React.MouseEvent<HTMLElement>, newValue: string | null) => {
    if (newValue !== null && onChange) {
      onChange(newValue);
    }
  };
  
  return (
    <ToggleButtonGroup
      value={value}
      exclusive={exclusive}
      onChange={handleChange}
      fullWidth={fullWidth}
    >
      {buttons.map((button) => (
        <ToggleButton
          key={button.value}
          value={button.value}
          disabled={button.disabled}
          size={size}
        >
          {button.icon && <span style={{ marginRight: 8 }}>{button.icon}</span>}
          {button.label}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
};

// Floating Action Button
export const FAB = styled(Fab)(({ theme }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  zIndex: theme.zIndex.speedDial
}));
```

**검증 기준**:
- [ ] 다양한 버튼 변형
- [ ] 로딩 상태 처리
- [ ] 아이콘 버튼 지원
- [ ] 접근성 고려

#### SubTask 7.12.2: 입력 필드 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/components/atoms/Input/Input.tsx
import React, { forwardRef, useState } from 'react';
import {
  TextField,
  TextFieldProps,
  InputAdornment,
  IconButton,
  FormControl,
  FormLabel,
  FormHelperText,
  OutlinedInput,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  Radio,
  RadioGroup,
  FormControlLabel,
  Switch,
  Slider,
  Autocomplete,
  Chip
} from '@mui/material';
import { Visibility, VisibilityOff, Clear } from '@mui/icons-material';

// Text Input Component
export interface TextInputProps extends Omit<TextFieldProps, 'variant'> {
  label?: string;
  placeholder?: string;
  helperText?: string;
  error?: boolean;
  errorMessage?: string;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  clearable?: boolean;
  onClear?: () => void;
  maxLength?: number;
  showCount?: boolean;
  variant?: 'outlined' | 'filled' | 'standard';
}

export const TextInput = forwardRef<HTMLDivElement, TextInputProps>(
  ({ 
    label,
    helperText,
    error,
    errorMessage,
    startIcon,
    endIcon,
    clearable,
    onClear,
    maxLength,
    showCount,
    value,
    onChange,
    variant = 'outlined',
    ...props 
  }, ref) => {
    const [charCount, setCharCount] = useState(0);
    
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value;
      
      if (maxLength && newValue.length > maxLength) {
        return;
      }
      
      setCharCount(newValue.length);
      
      if (onChange) {
        onChange(event);
      }
    };
    
    const handleClear = () => {
      if (onClear) {
        onClear();
      }
      setCharCount(0);
    };
    
    return (
      <TextField
        ref={ref}
        label={label}
        value={value}
        onChange={handleChange}
        error={error || !!errorMessage}
        helperText={
          errorMessage || 
          (showCount && maxLength ? `${charCount}/${maxLength}` : helperText)
        }
        variant={variant}
        InputProps={{
          startAdornment: startIcon && (
            <InputAdornment position="start">{startIcon}</InputAdornment>
          ),
          endAdornment: (
            <>
              {clearable && value && (
                <InputAdornment position="end">
                  <IconButton onClick={handleClear} edge="end" size="small">
                    <Clear fontSize="small" />
                  </IconButton>
                </InputAdornment>
              )}
              {endIcon && (
                <InputAdornment position="end">{endIcon}</InputAdornment>
              )}
            </>
          )
        }}
        {...props}
      />
    );
  }
);

TextInput.displayName = 'TextInput';

// Password Input Component
export interface PasswordInputProps extends Omit<TextInputProps, 'type'> {
  showStrength?: boolean;
  strengthRules?: Array<{
    regex: RegExp;
    message: string;
  }>;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({
  showStrength,
  strengthRules,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [strength, setStrength] = useState(0);
  
  const calculateStrength = (password: string) => {
    if (!strengthRules) return 0;
    
    const passedRules = strengthRules.filter(rule => rule.regex.test(password));
    return (passedRules.length / strengthRules.length) * 100;
  };
  
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const password = event.target.value;
    
    if (showStrength) {
      setStrength(calculateStrength(password));
    }
    
    if (props.onChange) {
      props.onChange(event);
    }
  };
  
  return (
    <>
      <TextInput
        {...props}
        type={showPassword ? 'text' : 'password'}
        onChange={handleChange}
        endIcon={
          <IconButton
            onClick={() => setShowPassword(!showPassword)}
            edge="end"
            size="small"
          >
            {showPassword ? <VisibilityOff /> : <Visibility />}
          </IconButton>
        }
      />
      {showStrength && props.value && (
        <Box sx={{ mt: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={strength}
            color={strength < 33 ? 'error' : strength < 66 ? 'warning' : 'success'}
          />
          <Typography variant="caption" color="text.secondary">
            Password strength: {strength < 33 ? 'Weak' : strength < 66 ? 'Medium' : 'Strong'}
          </Typography>
        </Box>
      )}
    </>
  );
};

// Select Component
export interface SelectInputProps {
  label?: string;
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  options: Array<{
    value: string;
    label: string;
    disabled?: boolean;
    icon?: React.ReactNode;
  }>;
  multiple?: boolean;
  placeholder?: string;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
  variant?: 'outlined' | 'filled' | 'standard';
  size?: 'small' | 'medium';
  clearable?: boolean;
}

export const SelectInput: React.FC<SelectInputProps> = ({
  label,
  value,
  onChange,
  options,
  multiple = false,
  placeholder,
  error,
  helperText,
  fullWidth = false,
  variant = 'outlined',
  size = 'medium',
  clearable = false
}) => {
  const handleChange = (event: any) => {
    if (onChange) {
      onChange(event.target.value);
    }
  };
  
  return (
    <FormControl 
      variant={variant} 
      error={error} 
      fullWidth={fullWidth}
      size={size}
    >
      {label && <InputLabel>{label}</InputLabel>}
      <Select
        value={value || (multiple ? [] : '')}
        onChange={handleChange}
        multiple={multiple}
        label={label}
        displayEmpty={!!placeholder}
        renderValue={(selected) => {
          if (multiple && Array.isArray(selected)) {
            if (selected.length === 0) return placeholder;
            return (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip 
                    key={value} 
                    label={options.find(o => o.value === value)?.label || value}
                    size="small"
                  />
                ))}
              </Box>
            );
          }
          if (!selected) return placeholder;
          return options.find(o => o.value === selected)?.label || selected;
        }}
      >
        {placeholder && !value && (
          <MenuItem value="" disabled>
            <em>{placeholder}</em>
          </MenuItem>
        )}
        {clearable && value && (
          <MenuItem value="">
            <em>Clear</em>
          </MenuItem>
        )}
        {options.map((option) => (
          <MenuItem 
            key={option.value} 
            value={option.value}
            disabled={option.disabled}
          >
            {option.icon && (
              <ListItemIcon>
                {option.icon}
              </ListItemIcon>
            )}
            <ListItemText primary={option.label} />
          </MenuItem>
        ))}
      </Select>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

// Checkbox Component
export interface CheckboxInputProps {
  label?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  indeterminate?: boolean;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  size?: 'small' | 'medium';
}

export const CheckboxInput: React.FC<CheckboxInputProps> = ({
  label,
  checked = false,
  onChange,
  disabled = false,
  indeterminate = false,
  color = 'primary',
  size = 'medium'
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(event.target.checked);
    }
  };
  
  const checkbox = (
    <Checkbox
      checked={checked}
      onChange={handleChange}
      disabled={disabled}
      indeterminate={indeterminate}
      color={color}
      size={size}
    />
  );
  
  return label ? (
    <FormControlLabel
      control={checkbox}
      label={label}
      disabled={disabled}
    />
  ) : checkbox;
};

// Radio Group Component
export interface RadioGroupInputProps {
  label?: string;
  value?: string;
  onChange?: (value: string) => void;
  options: Array<{
    value: string;
    label: string;
    disabled?: boolean;
  }>;
  row?: boolean;
  error?: boolean;
  helperText?: string;
  color?: 'primary' | 'secondary';
}

export const RadioGroupInput: React.FC<RadioGroupInputProps> = ({
  label,
  value,
  onChange,
  options,
  row = false,
  error = false,
  helperText,
  color = 'primary'
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(event.target.value);
    }
  };
  
  return (
    <FormControl error={error} component="fieldset">
      {label && <FormLabel component="legend">{label}</FormLabel>}
      <RadioGroup
        value={value}
        onChange={handleChange}
        row={row}
      >
        {options.map((option) => (
          <FormControlLabel
            key={option.value}
            value={option.value}
            control={<Radio color={color} />}
            label={option.label}
            disabled={option.disabled}
          />
        ))}
      </RadioGroup>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

// Switch Component
export interface SwitchInputProps {
  label?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  size?: 'small' | 'medium';
  labelPlacement?: 'end' | 'start' | 'top' | 'bottom';
}

export const SwitchInput: React.FC<SwitchInputProps> = ({
  label,
  checked = false,
  onChange,
  disabled = false,
  color = 'primary',
  size = 'medium',
  labelPlacement = 'end'
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(event.target.checked);
    }
  };
  
  const switchControl = (
    <Switch
      checked={checked}
      onChange={handleChange}
      disabled={disabled}
      color={color}
      size={size}
    />
  );
  
  return label ? (
    <FormControlLabel
      control={switchControl}
      label={label}
      disabled={disabled}
      labelPlacement={labelPlacement}
    />
  ) : switchControl;
};

// Slider Component
export interface SliderInputProps {
  label?: string;
  value?: number | number[];
  onChange?: (value: number | number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  marks?: boolean | Array<{ value: number; label?: string }>;
  disabled?: boolean;
  color?: 'primary' | 'secondary';
  size?: 'small' | 'medium';
  valueLabelDisplay?: 'auto' | 'on' | 'off';
  orientation?: 'horizontal' | 'vertical';
}

export const SliderInput: React.FC<SliderInputProps> = ({
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  marks = false,
  disabled = false,
  color = 'primary',
  size = 'medium',
  valueLabelDisplay = 'auto',
  orientation = 'horizontal'
}) => {
  const handleChange = (_: Event, newValue: number | number[]) => {
    if (onChange) {
      onChange(newValue);
    }
  };
  
  return (
    <FormControl fullWidth>
      {label && (
        <Typography gutterBottom>
          {label}
        </Typography>
      )}
      <Slider
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
        step={step}
        marks={marks}
        disabled={disabled}
        color={color}
        size={size}
        valueLabelDisplay={valueLabelDisplay}
        orientation={orientation}
      />
    </FormControl>
  );
};
```

**검증 기준**:
- [ ] 다양한 입력 타입
- [ ] 검증 및 에러 처리
- [ ] 접근성 레이블
- [ ] 커스터마이징 가능

#### SubTask 7.12.3: 타이포그래피 및 아이콘 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/atoms/Typography/Typography.tsx
import React from 'react';
import { Typography as MUITypography, TypographyProps as MUITypographyProps } from '@mui/material';
import { styled } from '@mui/material/styles';

export interface TypographyProps extends MUITypographyProps {
  variant?: MUITypographyProps['variant'] | 'display1' | 'display2' | 'display3';
  gradient?: boolean;
  gradientColors?: [string, string];
  truncate?: boolean | number;
  uppercase?: boolean;
  lowercase?: boolean;
  capitalize?: boolean;
  highlight?: boolean;
  highlightColor?: string;
}

const StyledTypography = styled(MUITypography, {
  shouldForwardProp: (prop) => 
    !['gradient', 'gradientColors', 'truncate', 'uppercase', 'lowercase', 'capitalize', 'highlight', 'highlightColor'].includes(prop as string)
})<TypographyProps>(({ 
  theme, 
  gradient, 
  gradientColors,
  truncate,
  uppercase,
  lowercase,
  capitalize,
  highlight,
  highlightColor
}) => ({
  ...(gradient && {
    background: gradientColors 
      ? `linear-gradient(135deg, ${gradientColors[0]}, ${gradientColors[1]})`
      : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text'
  }),
  
  ...(truncate && {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: typeof truncate === 'number' ? truncate : 1,
    WebkitBoxOrient: 'vertical',
    wordBreak: 'break-word'
  }),
  
  ...(uppercase && { textTransform: 'uppercase' }),
  ...(lowercase && { textTransform: 'lowercase' }),
  ...(capitalize && { textTransform: 'capitalize' }),
  
  ...(highlight && {
    backgroundColor: highlightColor || theme.palette.warning.light,
    padding: '2px 4px',
    borderRadius: '4px',
    display: 'inline-block'
  })
}));

export const Typography: React.FC<TypographyProps> = ({ 
  variant, 
  children,
  ...props 
}) => {
  // Map custom variants to MUI variants
  const muiVariant = variant?.startsWith('display') ? 'h1' : variant;
  
  // Apply custom styles for display variants
  const displayStyles = {
    display1: { fontSize: '4.5rem', fontWeight: 700, lineHeight: 1.1 },
    display2: { fontSize: '3.75rem', fontWeight: 700, lineHeight: 1.2 },
    display3: { fontSize: '3rem', fontWeight: 600, lineHeight: 1.2 }
  };
  
  return (
    <StyledTypography
      variant={muiVariant}
      sx={variant?.startsWith('display') ? displayStyles[variant as keyof typeof displayStyles] : undefined}
      {...props}
    >
      {children}
    </StyledTypography>
  );
};

// Icon Component with multiple icon libraries
export interface IconProps {
  name: string;
  size?: 'small' | 'medium' | 'large' | number;
  color?: string;
  library?: 'mui' | 'feather' | 'fontawesome' | 'custom';
  spin?: boolean;
  pulse?: boolean;
  className?: string;
  onClick?: () => void;
}

export const Icon: React.FC<IconProps> = ({
  name,
  size = 'medium',
  color,
  library = 'mui',
  spin = false,
  pulse = false,
  className,
  onClick
}) => {
  const sizeMap = {
    small: 16,
    medium: 24,
    large: 32
  };
  
  const actualSize = typeof size === 'number' ? size : sizeMap[size];
  
  const iconStyle: React.CSSProperties = {
    fontSize: actualSize,
    color,
    cursor: onClick ? 'pointer' : 'default',
    animation: spin ? 'spin 2s linear infinite' : pulse ? 'pulse 2s ease-in-out infinite' : undefined
  };
  
  // Icon mapping logic based on library
  const getIcon = () => {
    switch (library) {
      case 'mui':
        // Dynamic import MUI icons
        const MUIIcon = require(`@mui/icons-material/${name}`).default;
        return <MUIIcon style={iconStyle} onClick={onClick} className={className} />;
      
      case 'custom':
        // Custom SVG icons
        return (
          <svg
            width={actualSize}
            height={actualSize}
            fill={color || 'currentColor'}
            onClick={onClick}
            className={className}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
          >
            {/* Custom icon paths */}
          </svg>
        );
      
      default:
        return null;
    }
  };
  
  return getIcon();
};

// Text with Icon Component
export interface TextWithIconProps {
  text: string;
  icon: React.ReactNode;
  iconPosition?: 'start' | 'end';
  spacing?: number;
  align?: 'center' | 'start' | 'end';
  onClick?: () => void;
}

export const TextWithIcon: React.FC<TextWithIconProps> = ({
  text,
  icon,
  iconPosition = 'start',
  spacing = 1,
  align = 'center',
  onClick
}) => {
  return (
    <Box
      display="flex"
      alignItems={align}
      gap={spacing}
      onClick={onClick}
      sx={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {iconPosition === 'start' && icon}
      <Typography>{text}</Typography>
      {iconPosition === 'end' && icon}
    </Box>
  );
};

// Code Block Component
export interface CodeBlockProps {
  children: string;
  language?: string;
  showLineNumbers?: boolean;
  highlightLines?: number[];
  copyButton?: boolean;
  theme?: 'light' | 'dark';
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  children,
  language = 'javascript',
  showLineNumbers = false,
  highlightLines = [],
  copyButton = true,
  theme = 'dark'
}) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <Box
      sx={{
        position: 'relative',
        backgroundColor: theme === 'dark' ? '#1E1E1E' : '#F5F5F5',
        borderRadius: 1,
        p: 2,
        fontFamily: 'monospace',
        fontSize: '0.875rem',
        overflow: 'auto'
      }}
    >
      {copyButton && (
        <IconButton
          size="small"
          onClick={handleCopy}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            color: theme === 'dark' ? 'white' : 'black'
          }}
        >
          {copied ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
        </IconButton>
      )}
      <pre style={{ margin: 0 }}>
        <code>
          {children.split('\n').map((line, index) => (
            <div
              key={index}
              style={{
                backgroundColor: highlightLines.includes(index + 1) 
                  ? 'rgba(255, 255, 0, 0.1)' 
                  : 'transparent'
              }}
            >
              {showLineNumbers && (
                <span style={{ 
                  marginRight: '1em', 
                  color: theme === 'dark' ? '#858585' : '#999',
                  userSelect: 'none'
                }}>
                  {(index + 1).toString().padStart(3, ' ')}
                </span>
              )}
              {line}
            </div>
          ))}
        </code>
      </pre>
    </Box>
  );
};
```

**검증 기준**:
- [ ] 타이포그래피 변형
- [ ] 아이콘 시스템
- [ ] 코드 블록 컴포넌트
- [ ] 텍스트 스타일링 옵션

#### SubTask 7.12.4: 기타 원자 컴포넌트 (Badge, Chip, Avatar)
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/atoms/Badge/Badge.tsx
import React from 'react';
import { Badge as MUIBadge, BadgeProps as MUIBadgeProps, styled } from '@mui/material';

export interface BadgeProps extends MUIBadgeProps {
  pulse?: boolean;
  gradient?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const StyledBadge = styled(MUIBadge, {
  shouldForwardProp: (prop) => !['pulse', 'gradient', 'size'].includes(prop as string)
})<BadgeProps>(({ theme, pulse, gradient, size = 'medium' }) => ({
  '& .MuiBadge-badge': {
    ...(gradient && {
      background: `linear-gradient(135deg, ${theme.palette.error.main}, ${theme.palette.warning.main})`,
      color: '#FFFFFF'
    }),
    
    ...(pulse && {
      animation: 'pulse 2s ease-in-out infinite',
      
      '&::after': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        borderRadius: '50%',
        border: '1px solid currentColor',
        animation: 'ping 1.5s ease-in-out infinite'
      }
    }),
    
    ...(size === 'small' && {
      minWidth: 16,
      height: 16,
      fontSize: '0.625rem'
    }),
    
    ...(size === 'large' && {
      minWidth: 24,
      height: 24,
      fontSize: '0.875rem'
    })
  },
  
  '@keyframes pulse': {
    '0%': { transform: 'scale(1)' },
    '50%': { transform: 'scale(1.1)' },
    '100%': { transform: 'scale(1)' }
  },
  
  '@keyframes ping': {
    '0%': { transform: 'scale(1)', opacity: 1 },
    '100%': { transform: 'scale(2)', opacity: 0 }
  }
}));

export const Badge: React.FC<BadgeProps> = (props) => {
  return <StyledBadge {...props} />;
};

// Chip Component
export interface ChipProps {
  label: string;
  variant?: 'filled' | 'outlined' | 'gradient';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  size?: 'small' | 'medium';
  icon?: React.ReactNode;
  avatar?: React.ReactNode;
  onDelete?: () => void;
  onClick?: () => void;
  disabled?: boolean;
  clickable?: boolean;
}

export const Chip: React.FC<ChipProps> = ({
  label,
  variant = 'filled',
  color = 'primary',
  size = 'medium',
  icon,
  avatar,
  onDelete,
  onClick,
  disabled = false,
  clickable = !!onClick
}) => {
  const StyledChip = styled(MUIChip)(({ theme }) => ({
    ...(variant === 'gradient' && {
      background: `linear-gradient(135deg, ${theme.palette[color].light}, ${theme.palette[color].dark})`,
      color: '#FFFFFF',
      border: 'none'
    })
  }));
  
  return (
    <StyledChip
      label={label}
      variant={variant === 'gradient' ? 'filled' : variant}
      color={color}
      size={size}
      icon={icon}
      avatar={avatar}
      onDelete={onDelete}
      onClick={onClick}
      disabled={disabled}
      clickable={clickable}
    />
  );
};

// Avatar Component
export interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'small' | 'medium' | 'large' | number;
  variant?: 'circular' | 'rounded' | 'square';
  color?: string;
  bgcolor?: string;
  online?: boolean;
  badge?: React.ReactNode;
  onClick?: () => void;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  name,
  size = 'medium',
  variant = 'circular',
  color,
  bgcolor,
  online,
  badge,
  onClick
}) => {
  const sizeMap = {
    small: 32,
    medium: 40,
    large: 56
  };
  
  const actualSize = typeof size === 'number' ? size : sizeMap[size];
  
  const getInitials = (name: string) => {
    const names = name.split(' ');
    if (names.length === 1) return names[0][0].toUpperCase();
    return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
  };
  
  const avatar = (
    <MUIAvatar
      src={src}
      alt={alt || name}
      variant={variant}
      onClick={onClick}
      sx={{
        width: actualSize,
        height: actualSize,
        color,
        bgcolor,
        cursor: onClick ? 'pointer' : 'default',
        fontSize: actualSize * 0.4
      }}
    >
      {!src && name && getInitials(name)}
    </MUIAvatar>
  );
  
  if (online !== undefined || badge) {
    return (
      <Badge
        overlap="circular"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        badgeContent={
          online !== undefined ? (
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: online ? 'success.main' : 'grey.500',
                border: '2px solid white'
              }}
            />
          ) : badge
        }
      >
        {avatar}
      </Badge>
    );
  }
  
  return avatar;
};

// Avatar Group Component
export interface AvatarGroupProps {
  avatars: Array<{
    src?: string;
    name?: string;
    alt?: string;
  }>;
  max?: number;
  size?: 'small' | 'medium' | 'large';
  spacing?: 'small' | 'medium';
  renderSurplus?: (surplus: number) => React.ReactNode;
}

export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  avatars,
  max = 3,
  size = 'medium',
  spacing = 'medium',
  renderSurplus
}) => {
  return (
    <MUIAvatarGroup
      max={max}
      spacing={spacing}
      renderSurplus={renderSurplus}
    >
      {avatars.map((avatar, index) => (
        <Avatar
          key={index}
          src={avatar.src}
          name={avatar.name}
          alt={avatar.alt}
          size={size}
        />
      ))}
    </MUIAvatarGroup>
  );
};

// Tag Component (specialized chip)
export interface TagProps {
  label: string;
  color?: string;
  removable?: boolean;
  onRemove?: () => void;
  icon?: React.ReactNode;
}

export const Tag: React.FC<TagProps> = ({
  label,
  color,
  removable = false,
  onRemove,
  icon
}) => {
  return (
    <Chip
      label={label}
      size="small"
      icon={icon}
      onDelete={removable ? onRemove : undefined}
      sx={{
        backgroundColor: color ? `${color}20` : undefined,
        color: color || 'text.primary',
        border: color ? `1px solid ${color}` : undefined
      }}
    />
  );
};

// Progress Indicator Component
export interface ProgressProps {
  value?: number;
  variant?: 'linear' | 'circular';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  size?: 'small' | 'medium' | 'large' | number;
  showLabel?: boolean;
  thickness?: number;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  variant = 'linear',
  color = 'primary',
  size = 'medium',
  showLabel = false,
  thickness = 4
}) => {
  const sizeMap = {
    small: 20,
    medium: 40,
    large: 60
  };
  
  const actualSize = typeof size === 'number' ? size : sizeMap[size];
  
  if (variant === 'circular') {
    return (
      <Box position="relative" display="inline-flex">
        <CircularProgress
          variant={value !== undefined ? 'determinate' : 'indeterminate'}
          value={value}
          color={color}
          size={actualSize}
          thickness={thickness}
        />
        {showLabel && value !== undefined && (
          <Box
            top={0}
            left={0}
            bottom={0}
            right={0}
            position="absolute"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Typography variant="caption" component="div" color="text.secondary">
              {`${Math.round(value)}%`}
            </Typography>
          </Box>
        )}
      </Box>
    );
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
      <Box sx={{ width: '100%', mr: showLabel ? 1 : 0 }}>
        <LinearProgress
          variant={value !== undefined ? 'determinate' : 'indeterminate'}
          value={value}
          color={color}
          sx={{ height: thickness }}
        />
      </Box>
      {showLabel && value !== undefined && (
        <Box sx={{ minWidth: 35 }}>
          <Typography variant="body2" color="text.secondary">
            {`${Math.round(value)}%`}
          </Typography>
        </Box>
      )}
    </Box>
  );
};
```

**검증 기준**:
- [ ] Badge 컴포넌트 변형
- [ ] Chip 커스터마이징
- [ ] Avatar 시스템
- [ ] Progress 인디케이터

---
# Phase 7: 프론트엔드 구현 - Tasks 7.13-7.14 SubTask 작업지시서 (계속)

### Task 7.13: 분자 컴포넌트 (Forms, Cards, etc.)

#### SubTask 7.13.1: 폼 컴포넌트 시스템
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Form/Form.tsx
import React, { useState, useCallback } from 'react';
import { useForm, Controller, FieldValues, UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Grid,
  Stack,
  Button,
  Typography,
  Divider,
  FormControl,
  FormLabel,
  FormHelperText
} from '@mui/material';

// Form Context
interface FormContextValue<T extends FieldValues = FieldValues> {
  form: UseFormReturn<T>;
  isSubmitting: boolean;
  isDirty: boolean;
}

const FormContext = React.createContext<FormContextValue | null>(null);

export const useFormContext = <T extends FieldValues = FieldValues>() => {
  const context = React.useContext(FormContext) as FormContextValue<T>;
  if (!context) {
    throw new Error('useFormContext must be used within FormProvider');
  }
  return context;
};

// Form Component
export interface FormProps<T extends FieldValues = FieldValues> {
  schema?: z.ZodSchema<T>;
  defaultValues?: Partial<T>;
  onSubmit: (data: T) => void | Promise<void>;
  onError?: (errors: any) => void;
  children: React.ReactNode;
  mode?: 'onSubmit' | 'onBlur' | 'onChange' | 'onTouched';
  resetOnSubmit?: boolean;
  debug?: boolean;
}

export function Form<T extends FieldValues = FieldValues>({
  schema,
  defaultValues,
  onSubmit,
  onError,
  children,
  mode = 'onSubmit',
  resetOnSubmit = false,
  debug = false
}: FormProps<T>) {
  const form = useForm<T>({
    defaultValues: defaultValues as any,
    resolver: schema ? zodResolver(schema) : undefined,
    mode
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async (data: T) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      if (resetOnSubmit) {
        form.reset();
      }
    } catch (error) {
      if (onError) {
        onError(error);
      }
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleError = (errors: any) => {
    if (onError) {
      onError(errors);
    }
    if (debug) {
      console.error('Form validation errors:', errors);
    }
  };
  
  return (
    <FormContext.Provider value={{ form, isSubmitting, isDirty: form.formState.isDirty }}>
      <form onSubmit={form.handleSubmit(handleSubmit, handleError)} noValidate>
        {children}
        {debug && (
          <Box mt={2} p={2} bgcolor="grey.100" borderRadius={1}>
            <Typography variant="caption">Form State:</Typography>
            <pre>{JSON.stringify(form.watch(), null, 2)}</pre>
            <Typography variant="caption">Errors:</Typography>
            <pre>{JSON.stringify(form.formState.errors, null, 2)}</pre>
          </Box>
        )}
      </form>
    </FormContext.Provider>
  );
}

// Form Field Component
export interface FormFieldProps {
  name: string;
  label?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'date' | 'time' | 'datetime-local' | 'select' | 'checkbox' | 'radio' | 'switch' | 'textarea' | 'file';
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  autoFocus?: boolean;
  multiline?: boolean;
  rows?: number;
  options?: Array<{ value: string | number; label: string }>;
  accept?: string; // for file input
  multiple?: boolean; // for file and select
  grid?: { xs?: number; sm?: number; md?: number; lg?: number; xl?: number };
}

export const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  type = 'text',
  placeholder,
  helperText,
  required = false,
  disabled = false,
  readOnly = false,
  autoFocus = false,
  multiline = false,
  rows = 4,
  options = [],
  accept,
  multiple = false,
  grid
}) => {
  const { form } = useFormContext();
  const error = form.formState.errors[name];
  
  const fieldContent = (
    <Controller
      name={name}
      control={form.control}
      render={({ field }) => {
        switch (type) {
          case 'select':
            return (
              <SelectInput
                {...field}
                label={label}
                placeholder={placeholder}
                options={options}
                multiple={multiple}
                error={!!error}
                helperText={error?.message || helperText}
                fullWidth
                disabled={disabled}
              />
            );
          
          case 'checkbox':
            return (
              <CheckboxInput
                {...field}
                checked={field.value || false}
                onChange={(checked) => field.onChange(checked)}
                label={label}
                disabled={disabled}
              />
            );
          
          case 'radio':
            return (
              <RadioGroupInput
                {...field}
                label={label}
                options={options}
                error={!!error}
                helperText={error?.message || helperText}
              />
            );
          
          case 'switch':
            return (
              <SwitchInput
                {...field}
                checked={field.value || false}
                onChange={(checked) => field.onChange(checked)}
                label={label}
                disabled={disabled}
              />
            );
          
          case 'textarea':
            return (
              <TextInput
                {...field}
                label={label}
                placeholder={placeholder}
                multiline
                rows={rows}
                error={!!error}
                errorMessage={error?.message}
                helperText={helperText}
                disabled={disabled}
                fullWidth
              />
            );
          
          case 'file':
            return (
              <FileInput
                name={name}
                label={label}
                accept={accept}
                multiple={multiple}
                error={!!error}
                helperText={error?.message || helperText}
                disabled={disabled}
                onChange={(files) => field.onChange(files)}
              />
            );
          
          case 'password':
            return (
              <PasswordInput
                {...field}
                label={label}
                placeholder={placeholder}
                error={!!error}
                errorMessage={error?.message}
                helperText={helperText}
                disabled={disabled}
                fullWidth
                showStrength
              />
            );
          
          default:
            return (
              <TextInput
                {...field}
                type={type}
                label={label}
                placeholder={placeholder}
                error={!!error}
                errorMessage={error?.message}
                helperText={helperText}
                required={required}
                disabled={disabled}
                readOnly={readOnly}
                autoFocus={autoFocus}
                fullWidth
              />
            );
        }
      }}
    />
  );
  
  if (grid) {
    return (
      <Grid item {...grid}>
        {fieldContent}
      </Grid>
    );
  }
  
  return fieldContent;
};

// Form Section Component
export interface FormSectionProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  divider?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  divider = true
}) => {
  return (
    <Box mb={3}>
      {title && (
        <Box mb={2}>
          <Typography variant="h6">{title}</Typography>
          {description && (
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          )}
        </Box>
      )}
      {children}
      {divider && <Divider sx={{ mt: 3 }} />}
    </Box>
  );
};

// Form Actions Component
export interface FormActionsProps {
  submitLabel?: string;
  cancelLabel?: string;
  onCancel?: () => void;
  showReset?: boolean;
  resetLabel?: string;
  align?: 'left' | 'center' | 'right' | 'space-between';
  fullWidth?: boolean;
  submitVariant?: 'contained' | 'outlined' | 'text';
  cancelVariant?: 'contained' | 'outlined' | 'text';
}

export const FormActions: React.FC<FormActionsProps> = ({
  submitLabel = 'Submit',
  cancelLabel = 'Cancel',
  onCancel,
  showReset = false,
  resetLabel = 'Reset',
  align = 'right',
  fullWidth = false,
  submitVariant = 'contained',
  cancelVariant = 'outlined'
}) => {
  const { form, isSubmitting } = useFormContext();
  
  const justifyContent = {
    left: 'flex-start',
    center: 'center',
    right: 'flex-end',
    'space-between': 'space-between'
  }[align];
  
  return (
    <Box
      display="flex"
      justifyContent={justifyContent}
      gap={2}
      mt={3}
    >
      {onCancel && (
        <Button
          variant={cancelVariant}
          onClick={onCancel}
          disabled={isSubmitting}
          fullWidth={fullWidth}
        >
          {cancelLabel}
        </Button>
      )}
      {showReset && (
        <Button
          variant="outlined"
          onClick={() => form.reset()}
          disabled={isSubmitting}
          fullWidth={fullWidth}
        >
          {resetLabel}
        </Button>
      )}
      <Button
        type="submit"
        variant={submitVariant}
        color="primary"
        disabled={isSubmitting || !form.formState.isDirty}
        loading={isSubmitting}
        fullWidth={fullWidth}
      >
        {submitLabel}
      </Button>
    </Box>
  );
};

// File Input Component
interface FileInputProps {
  name: string;
  label?: string;
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // in MB
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  onChange?: (files: File[]) => void;
}

const FileInput: React.FC<FileInputProps> = ({
  name,
  label,
  accept,
  multiple = false,
  maxSize = 10,
  error = false,
  helperText,
  disabled = false,
  onChange
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(Array.from(e.target.files));
    }
  };
  
  const handleFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => {
      const sizeMB = file.size / (1024 * 1024);
      return sizeMB <= maxSize;
    });
    
    if (multiple) {
      setFiles(prev => [...prev, ...validFiles]);
      onChange?.([...files, ...validFiles]);
    } else {
      setFiles(validFiles.slice(0, 1));
      onChange?.(validFiles.slice(0, 1));
    }
  };
  
  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    onChange?.(newFiles);
  };
  
  return (
    <FormControl fullWidth error={error}>
      {label && <FormLabel>{label}</FormLabel>}
      <Box
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          border: `2px dashed ${error ? 'error.main' : dragActive ? 'primary.main' : 'grey.400'}`,
          borderRadius: 1,
          p: 3,
          textAlign: 'center',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.5 : 1
        }}
      >
        <input
          id={name}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          disabled={disabled}
          style={{ display: 'none' }}
        />
        <label htmlFor={name} style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}>
          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body1">
            Drag and drop files here or click to browse
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Max file size: {maxSize}MB
          </Typography>
        </label>
      </Box>
      
      {files.length > 0 && (
        <Box mt={2}>
          <Stack spacing={1}>
            {files.map((file, index) => (
              <Box
                key={index}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                p={1}
                bgcolor="grey.100"
                borderRadius={1}
              >
                <Typography variant="body2">{file.name}</Typography>
                <IconButton size="small" onClick={() => removeFile(index)}>
                  <Close fontSize="small" />
                </IconButton>
              </Box>
            ))}
          </Stack>
        </Box>
      )}
      
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

// Dynamic Form Builder
export interface DynamicFormField {
  name: string;
  type: string;
  label?: string;
  placeholder?: string;
  required?: boolean;
  validation?: z.ZodTypeAny;
  options?: Array<{ value: string; label: string }>;
  grid?: any;
  dependsOn?: string;
  condition?: (value: any) => boolean;
}

export interface DynamicFormProps {
  fields: DynamicFormField[];
  onSubmit: (data: any) => void;
  columns?: number;
  spacing?: number;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  fields,
  onSubmit,
  columns = 1,
  spacing = 2
}) => {
  // Build schema from fields
  const schema = z.object(
    fields.reduce((acc, field) => {
      if (field.validation) {
        acc[field.name] = field.validation;
      }
      return acc;
    }, {} as Record<string, z.ZodTypeAny>)
  );
  
  return (
    <Form schema={schema} onSubmit={onSubmit}>
      <Grid container spacing={spacing}>
        {fields.map((field) => {
          const gridProps = field.grid || {
            xs: 12,
            md: 12 / columns
          };
          
          return (
            <FormField
              key={field.name}
              name={field.name}
              type={field.type as any}
              label={field.label}
              placeholder={field.placeholder}
              required={field.required}
              options={field.options}
              grid={gridProps}
            />
          );
        })}
      </Grid>
      <FormActions />
    </Form>
  );
};
```

**검증 기준**:
- [ ] 폼 컨텍스트 시스템
- [ ] 필드 검증 통합
- [ ] 동적 폼 빌더
- [ ] 파일 업로드 지원

#### SubTask 7.13.2: 카드 및 리스트 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Card/Card.tsx
import React from 'react';
import {
  Card as MUICard,
  CardContent,
  CardHeader,
  CardActions,
  CardMedia,
  Typography,
  IconButton,
  Box,
  Skeleton,
  Collapse,
  Menu,
  MenuItem,
  Chip
} from '@mui/material';
import { MoreVert, Favorite, Share, ExpandMore } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Card Component
export interface CardProps {
  title?: string;
  subtitle?: string;
  content?: React.ReactNode;
  image?: string;
  imageHeight?: number;
  actions?: React.ReactNode;
  headerAction?: React.ReactNode;
  expandable?: boolean;
  expandedContent?: React.ReactNode;
  onClick?: () => void;
  selected?: boolean;
  loading?: boolean;
  variant?: 'outlined' | 'elevated' | 'gradient';
  tags?: string[];
  menu?: Array<{ label: string; onClick: () => void }>;
}

const StyledCard = styled(MUICard, {
  shouldForwardProp: (prop) => !['selected', 'variant'].includes(prop as string)
})<{ selected?: boolean; variant?: string }>(({ theme, selected, variant }) => ({
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  
  ...(selected && {
    borderColor: theme.palette.primary.main,
    borderWidth: 2,
    boxShadow: theme.shadows[4]
  }),
  
  ...(variant === 'gradient' && {
    background: `linear-gradient(135deg, ${theme.palette.primary.light}20, ${theme.palette.secondary.light}20)`
  }),
  
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[6]
  }
}));

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  content,
  image,
  imageHeight = 200,
  actions,
  headerAction,
  expandable = false,
  expandedContent,
  onClick,
  selected = false,
  loading = false,
  variant = 'elevated',
  tags = [],
  menu = []
}) => {
  const [expanded, setExpanded] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  
  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  if (loading) {
    return (
      <MUICard variant={variant === 'outlined' ? 'outlined' : 'elevation'}>
        {image && <Skeleton variant="rectangular" height={imageHeight} />}
        <CardContent>
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
          <Skeleton variant="rectangular" height={100} sx={{ mt: 2 }} />
        </CardContent>
      </MUICard>
    );
  }
  
  return (
    <StyledCard
      variant={variant === 'outlined' ? 'outlined' : 'elevation'}
      onClick={onClick}
      selected={selected}
    >
      {image && (
        <CardMedia
          component="img"
          height={imageHeight}
          image={image}
          alt={title}
        />
      )}
      
      {(title || subtitle || headerAction || menu.length > 0) && (
        <CardHeader
          title={title}
          subheader={subtitle}
          action={
            <>
              {headerAction}
              {menu.length > 0 && (
                <>
                  <IconButton onClick={handleMenuClick}>
                    <MoreVert />
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                  >
                    {menu.map((item, index) => (
                      <MenuItem
                        key={index}
                        onClick={() => {
                          item.onClick();
                          handleMenuClose();
                        }}
                      >
                        {item.label}
                      </MenuItem>
                    ))}
                  </Menu>
                </>
              )}
            </>
          }
        />
      )}
      
      {(content || tags.length > 0) && (
        <CardContent>
          {tags.length > 0 && (
            <Box mb={2} display="flex" flexWrap="wrap" gap={0.5}>
              {tags.map((tag, index) => (
                <Chip key={index} label={tag} size="small" />
              ))}
            </Box>
          )}
          {content}
        </CardContent>
      )}
      
      {(actions || expandable) && (
        <CardActions>
          {actions}
          {expandable && (
            <IconButton
              onClick={handleExpandClick}
              aria-expanded={expanded}
              sx={{
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                marginLeft: 'auto',
                transition: 'transform 0.3s'
              }}
            >
              <ExpandMore />
            </IconButton>
          )}
        </CardActions>
      )}
      
      {expandable && (
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent>
            {expandedContent}
          </CardContent>
        </Collapse>
      )}
    </StyledCard>
  );
};

// List Component
export interface ListItem {
  id: string;
  primary: string;
  secondary?: string;
  avatar?: React.ReactNode;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  onClick?: () => void;
  selected?: boolean;
  disabled?: boolean;
}

export interface ListProps {
  items: ListItem[];
  variant?: 'simple' | 'detailed' | 'compact';
  selectable?: boolean;
  multiSelect?: boolean;
  onSelectionChange?: (selected: string[]) => void;
  emptyMessage?: string;
  loading?: boolean;
  loadingItems?: number;
  divider?: boolean;
  hover?: boolean;
}

export const List: React.FC<ListProps> = ({
  items,
  variant = 'simple',
  selectable = false,
  multiSelect = false,
  onSelectionChange,
  emptyMessage = 'No items',
  loading = false,
  loadingItems = 3,
  divider = true,
  hover = true
}) => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  
  const handleItemClick = (itemId: string) => {
    if (!selectable) return;
    
    let newSelection: string[];
    
    if (multiSelect) {
      if (selectedItems.includes(itemId)) {
        newSelection = selectedItems.filter(id => id !== itemId);
      } else {
        newSelection = [...selectedItems, itemId];
      }
    } else {
      newSelection = [itemId];
    }
    
    setSelectedItems(newSelection);
    onSelectionChange?.(newSelection);
  };
  
  if (loading) {
    return (
      <MUIList>
        {Array.from({ length: loadingItems }).map((_, index) => (
          <ListItem key={index}>
            <ListItemAvatar>
              <Skeleton variant="circular" width={40} height={40} />
            </ListItemAvatar>
            <ListItemText
              primary={<Skeleton variant="text" width="80%" />}
              secondary={<Skeleton variant="text" width="60%" />}
            />
          </ListItem>
        ))}
      </MUIList>
    );
  }
  
  if (items.length === 0) {
    return (
      <Box p={3} textAlign="center">
        <Typography variant="body2" color="text.secondary">
          {emptyMessage}
        </Typography>
      </Box>
    );
  }
  
  return (
    <MUIList>
      {items.map((item, index) => (
        <React.Fragment key={item.id}>
          <MUIListItem
            button={hover || selectable}
            selected={selectedItems.includes(item.id)}
            onClick={() => {
              item.onClick?.();
              handleItemClick(item.id);
            }}
            disabled={item.disabled}
            sx={{
              ...(variant === 'compact' && { py: 0.5 })
            }}
          >
            {(item.avatar || item.icon) && (
              <ListItemAvatar>
                {item.avatar || item.icon}
              </ListItemAvatar>
            )}
            
            <ListItemText
              primary={item.primary}
              secondary={variant !== 'compact' ? item.secondary : undefined}
              primaryTypographyProps={{
                ...(variant === 'compact' && { variant: 'body2' })
              }}
            />
            
            {item.action && (
              <ListItemSecondaryAction>
                {item.action}
              </ListItemSecondaryAction>
            )}
            
            {selectable && (
              <ListItemIcon>
                {multiSelect ? (
                  <Checkbox
                    edge="end"
                    checked={selectedItems.includes(item.id)}
                    tabIndex={-1}
                    disableRipple
                  />
                ) : (
                  <Radio
                    edge="end"
                    checked={selectedItems.includes(item.id)}
                    tabIndex={-1}
                    disableRipple
                  />
                )}
              </ListItemIcon>
            )}
          </MUIListItem>
          
          {divider && index < items.length - 1 && (
            <Divider component="li" />
          )}
        </React.Fragment>
      ))}
    </MUIList>
  );
};

// Stat Card Component
export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  loading?: boolean;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon,
  color = 'primary',
  loading = false,
  onClick
}) => {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" height={40} />
          <Skeleton variant="text" width="30%" />
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card onClick={onClick}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {change !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                <Typography
                  variant="body2"
                  color={change >= 0 ? 'success.main' : 'error.main'}
                >
                  {change >= 0 ? '+' : ''}{change}%
                </Typography>
                {changeLabel && (
                  <Typography variant="body2" color="text.secondary" ml={1}>
                    {changeLabel}
                  </Typography>
                )}
              </Box>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                backgroundColor: `${color}.light`,
                color: `${color}.main`
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
```

**검증 기준**:
- [ ] 카드 컴포넌트 변형
- [ ] 리스트 컴포넌트
- [ ] 통계 카드
- [ ] 선택 기능

#### SubTask 7.13.3: 모달 및 다이얼로그 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Modal/Modal.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  IconButton,
  Typography,
  Box,
  Slide,
  Fade,
  Zoom,
  Backdrop,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { Close, Warning, Info, CheckCircle, Error } from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';

// Transition components
const SlideTransition = React.forwardRef(function Transition(
  props: TransitionProps & { children: React.ReactElement<any, any> },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const FadeTransition = React.forwardRef(function Transition(
  props: TransitionProps & { children: React.ReactElement<any, any> },
  ref: React.Ref<unknown>,
) {
  return <Fade ref={ref} {...props} />;
});

const ZoomTransition = React.forwardRef(function Transition(
  props: TransitionProps & { children: React.ReactElement<any, any> },
  ref: React.Ref<unknown>,
) {
  return <Zoom ref={ref} {...props} />;
});

// Modal Component
export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  content?: React.ReactNode;
  actions?: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'fullscreen';
  transition?: 'slide' | 'fade' | 'zoom';
  closeButton?: boolean;
  disableBackdropClick?: boolean;
  disableEscapeKeyDown?: boolean;
  fullWidth?: boolean;
  dividers?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  content,
  actions,
  size = 'sm',
  transition = 'slide',
  closeButton = true,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  fullWidth = true,
  dividers = false
}) => {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('sm')) && size === 'fullscreen';
  
  const TransitionComponent = {
    slide: SlideTransition,
    fade: FadeTransition,
    zoom: ZoomTransition
  }[transition];
  
  const handleClose = (_: {}, reason: 'backdropClick' | 'escapeKeyDown') => {
    if (reason === 'backdropClick' && disableBackdropClick) return;
    if (reason === 'escapeKeyDown' && disableEscapeKeyDown) return;
    onClose();
  };
  
  return (
    <Dialog
      open={open}
      onClose={handleClose}
      TransitionComponent={TransitionComponent}
      fullScreen={fullScreen}
      fullWidth={fullWidth}
      maxWidth={size === 'fullscreen' ? false : size}
    >
      {title && (
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">{title}</Typography>
            {closeButton && (
              <IconButton
                onClick={onClose}
                size="small"
                sx={{ ml: 2 }}
              >
                <Close />
              </IconButton>
            )}
          </Box>
        </DialogTitle>
      )}
      
      <DialogContent dividers={dividers}>
        {content}
      </DialogContent>
      
      {actions && (
        <DialogActions>
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
};

// Confirmation Dialog
export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  severity?: 'warning' | 'error' | 'info' | 'success';
  loading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  severity = 'warning',
  loading = false
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleConfirm = async () => {
    setIsProcessing(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error('Confirmation error:', error);
    } finally {
      setIsProcessing(false);
    }
  };
  
  const severityIcon = {
    warning: <Warning color="warning" />,
    error: <Error color="error" />,
    info: <Info color="info" />,
    success: <CheckCircle color="success" />
  }[severity];
  
  const severityColor = {
    warning: 'warning',
    error: 'error',
    info: 'info',
    success: 'success'
  }[severity] as any;
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      content={
        <Box display="flex" alignItems="flex-start" gap={2}>
          <Box mt={0.5}>{severityIcon}</Box>
          <DialogContentText>{message}</DialogContentText>
        </Box>
      }
      actions={
        <>
          <Button onClick={onClose} disabled={isProcessing || loading}>
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            color={severityColor}
            variant="contained"
            loading={isProcessing || loading}
          >
            {confirmText}
          </Button>
        </>
      }
      size="xs"
    />
  );
};

// Form Dialog
export interface FormDialogProps<T = any> {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: T) => void | Promise<void>;
  title: string;
  fields: any[];
  submitText?: string;
  cancelText?: string;
  schema?: any;
}

export function FormDialog<T = any>({
  open,
  onClose,
  onSubmit,
  title,
  fields,
  submitText = 'Submit',
  cancelText = 'Cancel',
  schema
}: FormDialogProps<T>) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async (data: T) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      onClose();
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      content={
        <Form schema={schema} onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {fields.map((field) => (
              <FormField key={field.name} {...field} />
            ))}
          </Stack>
        </Form>
      }
      actions={
        <>
          <Button onClick={onClose} disabled={isSubmitting}>
            {cancelText}
          </Button>
          <Button
            type="submit"
            variant="contained"
            loading={isSubmitting}
          >
            {submitText}
          </Button>
        </>
      }
      size="sm"
    />
  );
}

// Drawer Component
export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  anchor?: 'left' | 'right' | 'top' | 'bottom';
  width?: number | string;
  height?: number | string;
  title?: string;
  content?: React.ReactNode;
  actions?: React.ReactNode;
  persistent?: boolean;
}

export const Drawer: React.FC<DrawerProps> = ({
  open,
  onClose,
  anchor = 'right',
  width = 400,
  height = '100%',
  title,
  content,
  actions,
  persistent = false
}) => {
  const isHorizontal = anchor === 'left' || anchor === 'right';
  
  return (
    <MUIDrawer
      anchor={anchor}
      open={open}
      onClose={onClose}
      variant={persistent ? 'persistent' : 'temporary'}
      sx={{
        '& .MuiDrawer-paper': {
          width: isHorizontal ? width : '100%',
          height: !isHorizontal ? height : '100%',
          boxSizing: 'border-box'
        }
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%'
        }}
      >
        {title && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              borderBottom: 1,
              borderColor: 'divider'
            }}
          >
            <Typography variant="h6">{title}</Typography>
            <IconButton onClick={onClose}>
              <Close />
            </IconButton>
          </Box>
        )}
        
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {content}
        </Box>
        
        {actions && (
          <Box
            sx={{
              p: 2,
              borderTop: 1,
              borderColor: 'divider'
            }}
          >
            {actions}
          </Box>
        )}
      </Box>
    </MUIDrawer>
  );
};
```

**검증 기준**:
- [ ] 모달 트랜지션
- [ ] 확인 다이얼로그
- [ ] 폼 다이얼로그
- [ ] 드로어 컴포넌트

#### SubTask 7.13.4: 알림 및 토스트 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Notification/Notification.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Alert,
  AlertTitle,
  Snackbar,
  SnackbarContent,
  IconButton,
  Slide,
  Stack,
  Box,
  Typography,
  LinearProgress
} from '@mui/material';
import { Close, CheckCircle, Error, Warning, Info } from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';

// Toast types
export interface ToastOptions {
  id?: string;
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  duration?: number;
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  action?: React.ReactNode;
  persistent?: boolean;
  progress?: boolean;
  onClose?: () => void;
}

interface Toast extends ToastOptions {
  id: string;
}

// Toast Context
interface ToastContextValue {
  toasts: Toast[];
  showToast: (options: ToastOptions) => string;
  hideToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Toast Provider
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  
  const showToast = useCallback((options: ToastOptions): string => {
    const id = options.id || Date.now().toString();
    const toast: Toast = {
      ...options,
      id,
      duration: options.duration ?? 5000
    };
    
    setToasts(prev => [...prev, toast]);
    
    if (!options.persistent && toast.duration && toast.duration > 0) {
      setTimeout(() => {
        hideToast(id);
      }, toast.duration);
    }
    
    return id;
  }, []);
  
  const hideToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);
  
  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);
  
  return (
    <ToastContext.Provider value={{ toasts, showToast, hideToast, clearToasts }}>
      {children}
      <ToastContainer toasts={toasts} onClose={hideToast} />
    </ToastContext.Provider>
  );
};

// Toast Container
const ToastContainer: React.FC<{
  toasts: Toast[];
  onClose: (id: string) => void;
}> = ({ toasts, onClose }) => {
  // Group toasts by position
  const groupedToasts = toasts.reduce((acc, toast) => {
    const position = toast.position || 'bottom-center';
    if (!acc[position]) acc[position] = [];
    acc[position].push(toast);
    return acc;
  }, {} as Record<string, Toast[]>);
  
  const getPositionStyles = (position: string) => {
    const [vertical, horizontal] = position.split('-');
    return {
      position: 'fixed' as const,
      [vertical]: 24,
      [horizontal === 'center' ? 'left' : horizontal]: horizontal === 'center' ? '50%' : 24,
      transform: horizontal === 'center' ? 'translateX(-50%)' : undefined,
      zIndex: 9999
    };
  };
  
  return (
    <>
      {Object.entries(groupedToasts).map(([position, positionToasts]) => (
        <Box
          key={position}
          sx={getPositionStyles(position)}
        >
          <Stack spacing={1}>
            {positionToasts.map(toast => (
              <ToastItem
                key={toast.id}
                toast={toast}
                onClose={() => onClose(toast.id)}
              />
            ))}
          </Stack>
        </Box>
      ))}
    </>
  );
};

// Toast Item
const ToastItem: React.FC<{
  toast: Toast;
  onClose: () => void;
}> = ({ toast, onClose }) => {
  const [progress, setProgress] = useState(100);
  
  React.useEffect(() => {
    if (toast.progress && toast.duration && toast.duration > 0) {
      const interval = setInterval(() => {
        setProgress(prev => {
          const newValue = prev - (100 / (toast.duration! / 100));
          if (newValue <= 0) {
            clearInterval(interval);
            return 0;
          }
          return newValue;
        });
      }, 100);
      
      return () => clearInterval(interval);
    }
  }, [toast.progress, toast.duration]);
  
  const handleClose = () => {
    toast.onClose?.();
    onClose();
  };
  
  return (
    <Slide direction="left" in={true}>
      <Alert
        severity={toast.type || 'info'}
        onClose={handleClose}
        action={toast.action}
        sx={{
          minWidth: 300,
          boxShadow: 3
        }}
      >
        {toast.title && <AlertTitle>{toast.title}</AlertTitle>}
        {toast.message}
        {toast.progress && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 2
            }}
          />
        )}
      </Alert>
    </Slide>
  );
};

// Notification Component
export interface NotificationProps {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  closable?: boolean;
  onClose?: () => void;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  filled?: boolean;
}

export const Notification: React.FC<NotificationProps> = ({
  type = 'info',
  title,
  message,
  closable = true,
  onClose,
  action,
  icon,
  filled = false
}) => {
  return (
    <Alert
      severity={type}
      variant={filled ? 'filled' : 'standard'}
      onClose={closable ? onClose : undefined}
      action={action}
      icon={icon}
    >
      {title && <AlertTitle>{title}</AlertTitle>}
      {message}
    </Alert>
  );
};

// Banner Notification
export interface BannerProps {
  message: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  action?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  fixed?: boolean;
  position?: 'top' | 'bottom';
}

export const Banner: React.FC<BannerProps> = ({
  message,
  type = 'info',
  action,
  dismissible = true,
  onDismiss,
  fixed = false,
  position = 'top'
}) => {
  const [visible, setVisible] = useState(true);
  
  const handleDismiss = () => {
    setVisible(false);
    onDismiss?.();
  };
  
  if (!visible) return null;
  
  const bannerContent = (
    <Box
      sx={{
        backgroundColor: `${type}.main`,
        color: 'white',
        p: 1.5,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        ...(fixed && {
          position: 'fixed',
          [position]: 0,
          left: 0,
          right: 0,
          zIndex: 1300
        })
      }}
    >
      <Box display="flex" alignItems="center" gap={2}>
        <Typography variant="body2">{message}</Typography>
        {action}
      </Box>
      {dismissible && (
        <IconButton
          size="small"
          onClick={handleDismiss}
          sx={{ color: 'inherit' }}
        >
          <Close fontSize="small" />
        </IconButton>
      )}
    </Box>
  );
  
  return bannerContent;
};

// Hook for notifications
export const useNotification = () => {
  const toast = useToast();
  
  return {
    success: (message: string, options?: Partial<ToastOptions>) => 
      toast.showToast({ ...options, message, type: 'success' }),
    
    error: (message: string, options?: Partial<ToastOptions>) =>
      toast.showToast({ ...options, message, type: 'error' }),
    
    warning: (message: string, options?: Partial<ToastOptions>) =>
      toast.showToast({ ...options, message, type: 'warning' }),
    
    info: (message: string, options?: Partial<ToastOptions>) =>
      toast.showToast({ ...options, message, type: 'info' }),
    
    show: toast.showToast,
    hide: toast.hideToast,
    clear: toast.clearToasts
  };
};
```

**검증 기준**:
- [ ] 토스트 시스템
- [ ] 알림 컴포넌트
- [ ] 배너 알림
- [ ] 위치별 그룹핑

---

### Task 7.14: 유기체 컴포넌트 (Headers, Sidebars, etc.)

#### SubTask 7.14.1: 헤더 및 네비게이션 바 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/organisms/Header/Header.tsx
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  InputBase,
  Divider,
  ListItemIcon,
  ListItemText,
  useScrollTrigger,
  Slide
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { styled, alpha } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import useAppStore from '@/store';

// Hide on scroll
interface HideOnScrollProps {
  children: React.ReactElement;
}

function HideOnScroll({ children }: HideOnScrollProps) {
  const trigger = useScrollTrigger();
  
  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

// Search bar styles
const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
      '&:focus': {
        width: '30ch',
      },
    },
  },
}));

// Header Component
export interface HeaderProps {
  onMenuClick?: () => void;
  hideOnScroll?: boolean;
  elevation?: number;
  transparent?: boolean;
  showSearch?: boolean;
  showNotifications?: boolean;
  customActions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuClick,
  hideOnScroll = false,
  elevation = 1,
  transparent = false,
  showSearch = true,
  showNotifications = true,
  customActions
}) => {
  const navigate = useNavigate();
  const { user, theme, toggleTheme, notifications, logout } = useAppStore();
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notifAnchorEl, setNotifAnchorEl] = useState<null | HTMLElement>(null);
  const [searchValue, setSearchValue] = useState('');
  
  const unreadCount = notifications.filter(n => !n.read).length;
  
  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleNotificationMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotifAnchorEl(event.currentTarget);
  };
  
  const handleNotificationMenuClose = () => {
    setNotifAnchorEl(null);
  };
  
  const handleSearch = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && searchValue) {
      navigate(`/search?q=${encodeURIComponent(searchValue)}`);
      setSearchValue('');
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  const appBar = (
    <AppBar
      position="fixed"
      elevation={elevation}
      sx={{
        backgroundColor: transparent ? 'transparent' : undefined,
        backdropFilter: transparent ? 'blur(10px)' : undefined
      }}
    >
      <Toolbar>
        {onMenuClick && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 0 }}>
          T-Developer
        </Typography>
        
        {showSearch && (
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search…"
              inputProps={{ 'aria-label': 'search' }}
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onKeyPress={handleSearch}
            />
          </Search>
        )}
        
        <Box sx={{ flexGrow: 1 }} />
        
        {customActions}
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Toggle theme">
            <IconButton color="inherit" onClick={toggleTheme}>
              {theme === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
          
          {showNotifications && (
            <Tooltip title="Notifications">
              <IconButton color="inherit" onClick={handleNotificationMenuOpen}>
                <Badge badgeContent={unreadCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
          )}
          
          <Tooltip title="Profile">
            <IconButton onClick={handleProfileMenuOpen}>
              <Avatar
                alt={user?.name}
                src={user?.avatar}
                sx={{ width: 32, height: 32 }}
              >
                {user?.name?.charAt(0)}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleProfileMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <Box sx={{ px: 2, py: 1 }}>
            <Typography variant="subtitle1">{user?.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>
          <Divider />
          <MenuItem onClick={() => navigate('/profile')}>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Profile</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => navigate('/settings')}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Logout</ListItemText>
          </MenuItem>
        </Menu>
        
        {/* Notifications Menu */}
        <Menu
          anchorEl={notifAnchorEl}
          open={Boolean(notifAnchorEl)}
          onClose={handleNotificationMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          PaperProps={{
            sx: { width: 360, maxHeight: 400 }
          }}
        >
          <Box sx={{ p: 2 }}>
            <Typography variant="h6">Notifications</Typography>
          </Box>
          <Divider />
          {notifications.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No new notifications
              </Typography>
            </Box>
          ) : (
            notifications.map((notif) => (
              <MenuItem key={notif.id} onClick={handleNotificationMenuClose}>
                <Box>
                  <Typography variant="body2">{notif.title}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {notif.message}
                  </Typography>
                </Box>
              </MenuItem>
            ))
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
  
  return hideOnScroll ? <HideOnScroll>{appBar}</HideOnScroll> : appBar;
};
```

**검증 기준**:
- [ ] 헤더 레이아웃
- [ ] 검색 기능
- [ ] 사용자 메뉴
- [ ] 알림 시스템

---

# Phase 7: 프론트엔드 구현 - Tasks 7.13-7.14 SubTask 작업지시서 (계속)

### Task 7.13: 분자 컴포넌트 (Forms, Cards, etc.)

#### SubTask 7.13.1: 폼 컴포넌트 시스템
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 6시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Form/Form.tsx
import React, { useState, useCallback } from 'react';
import { useForm, Controller, FieldValues, UseFormReturn } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Grid,
  Stack,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import { TextInput, SelectInput, CheckboxInput, RadioGroupInput } from '@/components/atoms';

// Form Field Types
export interface FormField {
  name: string;
  label?: string;
  type: 'text' | 'password' | 'email' | 'number' | 'select' | 'checkbox' | 'radio' | 'date' | 'time' | 'file' | 'textarea' | 'custom';
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  defaultValue?: any;
  validation?: yup.AnySchema;
  options?: Array<{ value: string; label: string }>;
  grid?: { xs?: number; sm?: number; md?: number; lg?: number };
  condition?: (values: any) => boolean;
  component?: React.ComponentType<any>;
  props?: Record<string, any>;
}

export interface FormProps {
  fields: FormField[];
  onSubmit: (data: any) => void | Promise<void>;
  onCancel?: () => void;
  validationSchema?: yup.AnyObjectSchema;
  defaultValues?: Record<string, any>;
  submitText?: string;
  cancelText?: string;
  resetOnSubmit?: boolean;
  layout?: 'vertical' | 'horizontal' | 'inline';
  spacing?: number;
  showReset?: boolean;
  autoFocus?: boolean;
  debug?: boolean;
}

export const Form: React.FC<FormProps> = ({
  fields,
  onSubmit,
  onCancel,
  validationSchema,
  defaultValues = {},
  submitText = 'Submit',
  cancelText = 'Cancel',
  resetOnSubmit = false,
  layout = 'vertical',
  spacing = 2,
  showReset = false,
  autoFocus = false,
  debug = false
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Build validation schema from fields if not provided
  const schema = validationSchema || yup.object().shape(
    fields.reduce((acc, field) => {
      if (field.validation) {
        acc[field.name] = field.validation;
      } else if (field.required) {
        acc[field.name] = yup.string().required(`${field.label || field.name} is required`);
      }
      return acc;
    }, {} as Record<string, yup.AnySchema>)
  );
  
  const {
    control,
    handleSubmit,
    formState: { errors, isDirty, isValid },
    reset,
    watch,
    setValue,
    getValues
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      ...fields.reduce((acc, field) => {
        acc[field.name] = field.defaultValue || '';
        return acc;
      }, {} as Record<string, any>),
      ...defaultValues
    },
    mode: 'onChange'
  });
  
  const watchedValues = watch();
  
  const handleFormSubmit = async (data: any) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      if (resetOnSubmit) {
        reset();
      }
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const renderField = (field: FormField) => {
    // Check condition
    if (field.condition && !field.condition(watchedValues)) {
      return null;
    }
    
    // Custom component
    if (field.component) {
      return (
        <Controller
          name={field.name}
          control={control}
          render={({ field: controllerField, fieldState }) => (
            <field.component
              {...controllerField}
              {...field.props}
              error={!!fieldState.error}
              helperText={fieldState.error?.message || field.helperText}
            />
          )}
        />
      );
    }
    
    // Built-in field types
    return (
      <Controller
        name={field.name}
        control={control}
        render={({ field: controllerField, fieldState }) => {
          const commonProps = {
            ...controllerField,
            label: field.label,
            placeholder: field.placeholder,
            error: !!fieldState.error,
            helperText: fieldState.error?.message || field.helperText,
            disabled: field.disabled,
            fullWidth: true,
            ...field.props
          };
          
          switch (field.type) {
            case 'text':
            case 'email':
            case 'password':
            case 'number':
              return (
                <TextInput
                  {...commonProps}
                  type={field.type}
                  autoFocus={autoFocus && fields[0].name === field.name}
                />
              );
              
            case 'textarea':
              return (
                <TextInput
                  {...commonProps}
                  multiline
                  rows={4}
                />
              );
              
            case 'select':
              return (
                <SelectInput
                  {...commonProps}
                  options={field.options || []}
                />
              );
              
            case 'checkbox':
              return (
                <CheckboxInput
                  {...commonProps}
                  checked={controllerField.value}
                  onChange={(checked) => controllerField.onChange(checked)}
                />
              );
              
            case 'radio':
              return (
                <RadioGroupInput
                  {...commonProps}
                  options={field.options || []}
                />
              );
              
            case 'date':
              return (
                <TextInput
                  {...commonProps}
                  type="date"
                  InputLabelProps={{ shrink: true }}
                />
              );
              
            case 'time':
              return (
                <TextInput
                  {...commonProps}
                  type="time"
                  InputLabelProps={{ shrink: true }}
                />
              );
              
            case 'file':
              return (
                <Button
                  variant="outlined"
                  component="label"
                  fullWidth
                >
                  {field.label || 'Choose File'}
                  <input
                    type="file"
                    hidden
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        controllerField.onChange(file);
                      }
                    }}
                    {...field.props}
                  />
                </Button>
              );
              
            default:
              return null;
          }
        }}
      />
    );
  };
  
  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Grid container spacing={spacing}>
        {fields.map((field) => (
          <Grid
            key={field.name}
            item
            xs={field.grid?.xs || 12}
            sm={field.grid?.sm || field.grid?.xs || 12}
            md={field.grid?.md || field.grid?.sm || field.grid?.xs || 12}
            lg={field.grid?.lg || field.grid?.md || field.grid?.sm || field.grid?.xs || 12}
          >
            {renderField(field)}
          </Grid>
        ))}
      </Grid>
      
      <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
        <Button
          type="submit"
          variant="contained"
          disabled={!isValid || isSubmitting}
          fullWidth={layout === 'vertical'}
        >
          {isSubmitting ? 'Submitting...' : submitText}
        </Button>
        
        {showReset && (
          <Button
            type="button"
            variant="outlined"
            onClick={() => reset()}
            disabled={!isDirty || isSubmitting}
          >
            Reset
          </Button>
        )}
        
        {onCancel && (
          <Button
            type="button"
            variant="text"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            {cancelText}
          </Button>
        )}
      </Stack>
      
      {debug && (
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <pre>{JSON.stringify({ values: watchedValues, errors }, null, 2)}</pre>
        </Box>
      )}
    </Box>
  );
};

// Multi-Step Form Component
export interface FormStep {
  label: string;
  fields: FormField[];
  optional?: boolean;
  validation?: yup.AnyObjectSchema;
}

export interface MultiStepFormProps {
  steps: FormStep[];
  onSubmit: (data: any) => void | Promise<void>;
  onStepChange?: (step: number) => void;
  orientation?: 'horizontal' | 'vertical';
  showStepContent?: boolean;
  allowSkip?: boolean;
  persistData?: boolean;
}

export const MultiStepForm: React.FC<MultiStepFormProps> = ({
  steps,
  onSubmit,
  onStepChange,
  orientation = 'horizontal',
  showStepContent = true,
  allowSkip = false,
  persistData = true
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  
  const handleNext = (data: any) => {
    if (persistData) {
      setFormData({ ...formData, ...data });
    }
    
    setCompletedSteps(new Set([...completedSteps, activeStep]));
    
    if (activeStep === steps.length - 1) {
      onSubmit(persistData ? { ...formData, ...data } : data);
    } else {
      setActiveStep(activeStep + 1);
      onStepChange?.(activeStep + 1);
    }
  };
  
  const handleBack = () => {
    setActiveStep(activeStep - 1);
    onStepChange?.(activeStep - 1);
  };
  
  const handleSkip = () => {
    if (allowSkip && steps[activeStep].optional) {
      setActiveStep(activeStep + 1);
      onStepChange?.(activeStep + 1);
    }
  };
  
  const currentStep = steps[activeStep];
  
  return (
    <Box>
      <Stepper activeStep={activeStep} orientation={orientation}>
        {steps.map((step, index) => (
          <Step key={index} completed={completedSteps.has(index)}>
            <StepLabel optional={step.optional && <Typography variant="caption">Optional</Typography>}>
              {step.label}
            </StepLabel>
            {showStepContent && orientation === 'vertical' && (
              <StepContent>
                {index === activeStep && (
                  <Form
                    fields={currentStep.fields}
                    onSubmit={handleNext}
                    validationSchema={currentStep.validation}
                    defaultValues={persistData ? formData : {}}
                    submitText={activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                    showReset={false}
                  />
                )}
              </StepContent>
            )}
          </Step>
        ))}
      </Stepper>
      
      {orientation === 'horizontal' && (
        <Box sx={{ mt: 3 }}>
          <Form
            fields={currentStep.fields}
            onSubmit={handleNext}
            validationSchema={currentStep.validation}
            defaultValues={persistData ? formData : {}}
            submitText={activeStep === steps.length - 1 ? 'Finish' : 'Next'}
            showReset={false}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            
            {allowSkip && currentStep.optional && (
              <Button onClick={handleSkip}>
                Skip
              </Button>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

// Dynamic Form Builder
export interface DynamicFormProps {
  schema: any; // JSON Schema
  uiSchema?: any; // UI customization schema
  onSubmit: (data: any) => void;
  onChange?: (data: any) => void;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  schema,
  uiSchema = {},
  onSubmit,
  onChange
}) => {
  const generateFields = (schema: any): FormField[] => {
    const fields: FormField[] = [];
    
    Object.entries(schema.properties || {}).forEach(([key, value]: [string, any]) => {
      const uiConfig = uiSchema[key] || {};
      
      fields.push({
        name: key,
        label: value.title || key,
        type: mapSchemaTypeToFieldType(value.type, value.format),
        required: schema.required?.includes(key),
        helperText: value.description,
        options: value.enum?.map((v: string) => ({ value: v, label: v })),
        ...uiConfig
      });
    });
    
    return fields;
  };
  
  const mapSchemaTypeToFieldType = (type: string, format?: string): FormField['type'] => {
    if (format === 'date') return 'date';
    if (format === 'time') return 'time';
    if (format === 'email') return 'email';
    if (format === 'password') return 'password';
    
    switch (type) {
      case 'string': return 'text';
      case 'number': return 'number';
      case 'boolean': return 'checkbox';
      default: return 'text';
    }
  };
  
  return (
    <Form
      fields={generateFields(schema)}
      onSubmit={onSubmit}
    />
  );
};
```

**검증 기준**:
- [ ] 폼 필드 시스템
- [ ] 유효성 검사 통합
- [ ] 멀티스텝 폼
- [ ] 동적 폼 빌더

#### SubTask 7.13.2: 카드 및 리스트 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Card/Card.tsx
import React from 'react';
import {
  Card as MUICard,
  CardContent,
  CardHeader,
  CardActions,
  CardMedia,
  Collapse,
  IconButton,
  Typography,
  Box,
  Skeleton,
  Chip
} from '@mui/material';
import { MoreVert, Favorite, Share, ExpandMore } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

export interface CardProps {
  title?: string;
  subtitle?: string;
  content?: React.ReactNode;
  image?: string;
  imageHeight?: number;
  actions?: React.ReactNode;
  menu?: React.ReactNode;
  expandable?: boolean;
  expandContent?: React.ReactNode;
  loading?: boolean;
  onClick?: () => void;
  selected?: boolean;
  variant?: 'elevated' | 'outlined';
  badge?: string | number;
  badgeColor?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  tags?: string[];
  hoverable?: boolean;
}

const StyledCard = styled(MUICard, {
  shouldForwardProp: (prop) => !['selected', 'hoverable'].includes(prop as string)
})<{ selected?: boolean; hoverable?: boolean }>(({ theme, selected, hoverable }) => ({
  position: 'relative',
  transition: 'all 0.3s ease',
  cursor: hoverable ? 'pointer' : 'default',
  
  ...(selected && {
    borderColor: theme.palette.primary.main,
    borderWidth: 2,
    backgroundColor: theme.palette.action.selected
  }),
  
  ...(hoverable && {
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[8]
    }
  })
}));

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  content,
  image,
  imageHeight = 200,
  actions,
  menu,
  expandable = false,
  expandContent,
  loading = false,
  onClick,
  selected = false,
  variant = 'elevated',
  badge,
  badgeColor = 'primary',
  tags = [],
  hoverable = false
}) => {
  const [expanded, setExpanded] = React.useState(false);
  
  if (loading) {
    return (
      <StyledCard variant={variant}>
        <CardContent>
          <Skeleton variant="text" width="60%" height={32} />
          <Skeleton variant="text" width="40%" height={24} />
          <Skeleton variant="rectangular" height={100} sx={{ mt: 2 }} />
        </CardContent>
      </StyledCard>
    );
  }
  
  return (
    <StyledCard
      variant={variant}
      onClick={onClick}
      selected={selected}
      hoverable={hoverable}
    >
      {badge !== undefined && (
        <Chip
          label={badge}
          color={badgeColor}
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 1
          }}
        />
      )}
      
      {(title || subtitle || menu) && (
        <CardHeader
          title={title}
          subheader={subtitle}
          action={menu && (
            <IconButton>
              <MoreVert />
            </IconButton>
          )}
        />
      )}
      
      {image && (
        <CardMedia
          component="img"
          height={imageHeight}
          image={image}
          alt={title}
        />
      )}
      
      {content && (
        <CardContent>
          {content}
        </CardContent>
      )}
      
      {tags.length > 0 && (
        <Box sx={{ px: 2, pb: 1 }}>
          {tags.map((tag, index) => (
            <Chip
              key={index}
              label={tag}
              size="small"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          ))}
        </Box>
      )}
      
      {(actions || expandable) && (
        <CardActions disableSpacing>
          {actions}
          {expandable && (
            <IconButton
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              sx={{
                transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                marginLeft: 'auto',
                transition: 'transform 0.3s'
              }}
            >
              <ExpandMore />
            </IconButton>
          )}
        </CardActions>
      )}
      
      {expandable && expandContent && (
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent>
            {expandContent}
          </CardContent>
        </Collapse>
      )}
    </StyledCard>
  );
};

// List Component
export interface ListProps<T = any> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  loading?: boolean;
  loadingItems?: number;
  emptyMessage?: string;
  emptyIcon?: React.ReactNode;
  divider?: boolean;
  selectable?: boolean;
  selectedItems?: T[];
  onSelectItem?: (item: T) => void;
  sortable?: boolean;
  onSort?: (items: T[]) => void;
  virtualized?: boolean;
  itemHeight?: number;
  maxHeight?: number;
  grid?: boolean;
  gridColumns?: number | { xs?: number; sm?: number; md?: number; lg?: number };
  gap?: number;
}

export function List<T>({
  items,
  renderItem,
  loading = false,
  loadingItems = 3,
  emptyMessage = 'No items found',
  emptyIcon,
  divider = false,
  selectable = false,
  selectedItems = [],
  onSelectItem,
  sortable = false,
  onSort,
  virtualized = false,
  itemHeight = 72,
  maxHeight,
  grid = false,
  gridColumns = 1,
  gap = 2
}: ListProps<T>) {
  if (loading) {
    return (
      <Box>
        {Array.from({ length: loadingItems }).map((_, index) => (
          <Skeleton
            key={index}
            variant="rectangular"
            height={itemHeight}
            sx={{ mb: 1 }}
          />
        ))}
      </Box>
    );
  }
  
  if (items.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          py: 8,
          color: 'text.secondary'
        }}
      >
        {emptyIcon}
        <Typography variant="body1" sx={{ mt: 2 }}>
          {emptyMessage}
        </Typography>
      </Box>
    );
  }
  
  if (grid) {
    const getGridColumns = () => {
      if (typeof gridColumns === 'number') {
        return `repeat(${gridColumns}, 1fr)`;
      }
      return {
        xs: `repeat(${gridColumns.xs || 1}, 1fr)`,
        sm: `repeat(${gridColumns.sm || gridColumns.xs || 1}, 1fr)`,
        md: `repeat(${gridColumns.md || gridColumns.sm || gridColumns.xs || 1}, 1fr)`,
        lg: `repeat(${gridColumns.lg || gridColumns.md || gridColumns.sm || gridColumns.xs || 1}, 1fr)`
      };
    };
    
    return (
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: getGridColumns(),
          gap,
          maxHeight,
          overflow: maxHeight ? 'auto' : 'visible'
        }}
      >
        {items.map((item, index) => (
          <Box key={index}>
            {renderItem(item, index)}
          </Box>
        ))}
      </Box>
    );
  }
  
  return (
    <MUIList
      sx={{
        maxHeight,
        overflow: maxHeight ? 'auto' : 'visible'
      }}
    >
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ListItem
            button={selectable}
            selected={selectable && selectedItems.includes(item)}
            onClick={() => selectable && onSelectItem?.(item)}
          >
            {renderItem(item, index)}
          </ListItem>
          {divider && index < items.length - 1 && <Divider />}
        </React.Fragment>
      ))}
    </MUIList>
  );
}

// Data Card Component
export interface DataCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  loading?: boolean;
  onClick?: () => void;
  footer?: React.ReactNode;
}

export const DataCard: React.FC<DataCardProps> = ({
  title,
  value,
  change,
  changeType,
  icon,
  color = 'primary',
  loading = false,
  onClick,
  footer
}) => {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" width="50%" />
          <Skeleton variant="text" width="30%" height={40} />
          <Skeleton variant="text" width="40%" />
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card onClick={onClick} hoverable={!!onClick}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
            {change !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                <Typography
                  variant="body2"
                  color={changeType === 'increase' ? 'success.main' : 'error.main'}
                >
                  {changeType === 'increase' ? '↑' : '↓'} {Math.abs(change)}%
                </Typography>
                <Typography variant="body2" color="text.secondary" ml={1}>
                  vs last period
                </Typography>
              </Box>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                p: 1,
                borderRadius: 1,
                backgroundColor: `${color}.light`,
                color: `${color}.main`
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
        {footer && (
          <Box mt={2} pt={2} borderTop={1} borderColor="divider">
            {footer}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
```

**검증 기준**:
- [ ] 다양한 카드 변형
- [ ] 리스트 컴포넌트
- [ ] 데이터 카드
- [ ] 로딩 상태 처리

#### SubTask 7.13.3: 모달 및 다이얼로그 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Modal/Modal.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  IconButton,
  Typography,
  Box,
  Slide,
  Fade,
  Zoom,
  Grow,
  Backdrop,
  CircularProgress
} from '@mui/material';
import { TransitionProps } from '@mui/material/transitions';
import { Close, Warning, Info, CheckCircle, Error } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Transition components
const Transitions = {
  slide: React.forwardRef(function Transition(
    props: TransitionProps & { children: React.ReactElement<any, any> },
    ref: React.Ref<unknown>
  ) {
    return <Slide direction="up" ref={ref} {...props} />;
  }),
  fade: Fade,
  zoom: Zoom,
  grow: Grow
};

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  content?: React.ReactNode;
  actions?: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'fullscreen';
  transition?: 'slide' | 'fade' | 'zoom' | 'grow';
  closeButton?: boolean;
  disableBackdropClick?: boolean;
  disableEscapeKeyDown?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  dividers?: boolean;
  scroll?: 'paper' | 'body';
}

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    borderRadius: theme.shape.borderRadius * 2
  }
}));

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  content,
  actions,
  size = 'sm',
  transition = 'fade',
  closeButton = true,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  loading = false,
  fullWidth = false,
  dividers = false,
  scroll = 'paper'
}) => {
  const handleClose = (event: {}, reason: 'backdropClick' | 'escapeKeyDown') => {
    if (reason === 'backdropClick' && disableBackdropClick) return;
    if (reason === 'escapeKeyDown' && disableEscapeKeyDown) return;
    onClose();
  };
  
  return (
    <StyledDialog
      open={open}
      onClose={handleClose}
      maxWidth={size === 'fullscreen' ? false : size}
      fullWidth={fullWidth || size === 'fullscreen'}
      fullScreen={size === 'fullscreen'}
      TransitionComponent={Transitions[transition]}
      scroll={scroll}
    >
      {loading && (
        <Backdrop
          sx={{
            position: 'absolute',
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(255, 255, 255, 0.7)'
          }}
          open={loading}
        >
          <CircularProgress />
        </Backdrop>
      )}
      
      {title && (
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">{title}</Typography>
            {closeButton && (
              <IconButton
                onClick={onClose}
                size="small"
                sx={{ ml: 2 }}
              >
                <Close />
              </IconButton>
            )}
          </Box>
        </DialogTitle>
      )}
      
      {content && (
        <DialogContent dividers={dividers}>
          {content}
        </DialogContent>
      )}
      
      {actions && (
        <DialogActions>
          {actions}
        </DialogActions>
      )}
    </StyledDialog>
  );
};

// Confirmation Dialog
export interface ConfirmDialogProps {
  open: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  loading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onConfirm,
  onCancel,
  title = 'Confirm Action',
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'info',
  loading = false
}) => {
  const [isConfirming, setIsConfirming] = useState(false);
  
  const handleConfirm = async () => {
    setIsConfirming(true);
    try {
      await onConfirm();
      onCancel(); // Close dialog after confirmation
    } catch (error) {
      console.error('Confirmation error:', error);
    } finally {
      setIsConfirming(false);
    }
  };
  
  const icons = {
    info: <Info color="info" />,
    warning: <Warning color="warning" />,
    error: <Error color="error" />,
    success: <CheckCircle color="success" />
  };
  
  return (
    <Modal
      open={open}
      onClose={onCancel}
      title={title}
      size="xs"
      loading={loading || isConfirming}
      content={
        <Box display="flex" alignItems="flex-start" gap={2}>
          {icons[type]}
          <DialogContentText>{message}</DialogContentText>
        </Box>
      }
      actions={
        <>
          <Button onClick={onCancel} disabled={isConfirming}>
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            variant="contained"
            color={type === 'error' ? 'error' : 'primary'}
            disabled={isConfirming}
          >
            {isConfirming ? 'Processing...' : confirmText}
          </Button>
        </>
      }
    />
  );
};

// Drawer Component
export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  anchor?: 'left' | 'right' | 'top' | 'bottom';
  width?: number | string;
  content: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  persistent?: boolean;
  showCloseButton?: boolean;
}

export const Drawer: React.FC<DrawerProps> = ({
  open,
  onClose,
  anchor = 'right',
  width = 400,
  content,
  header,
  footer,
  persistent = false,
  showCloseButton = true
}) => {
  return (
    <MUIDrawer
      anchor={anchor}
      open={open}
      onClose={onClose}
      variant={persistent ? 'persistent' : 'temporary'}
      PaperProps={{
        sx: {
          width: ['top', 'bottom'].includes(anchor) ? '100%' : width,
          height: ['left', 'right'].includes(anchor) ? '100%' : 'auto'
        }
      }}
    >
      {header && (
        <Box
          sx={{
            p: 2,
            borderBottom: 1,
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          {header}
          {showCloseButton && (
            <IconButton onClick={onClose} size="small">
              <Close />
            </IconButton>
          )}
        </Box>
      )}
      
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {content}
      </Box>
      
      {footer && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          {footer}
        </Box>
      )}
    </MUIDrawer>
  );
};

// Popover Component
export interface PopoverProps {
  open: boolean;
  anchorEl: HTMLElement | null;
  onClose: () => void;
  content: React.ReactNode;
  anchorOrigin?: {
    vertical: 'top' | 'center' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  transformOrigin?: {
    vertical: 'top' | 'center' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  arrow?: boolean;
}

export const Popover: React.FC<PopoverProps> = ({
  open,
  anchorEl,
  onClose,
  content,
  anchorOrigin = { vertical: 'bottom', horizontal: 'left' },
  transformOrigin = { vertical: 'top', horizontal: 'left' },
  arrow = false
}) => {
  return (
    <MUIPopover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={anchorOrigin}
      transformOrigin={transformOrigin}
      PaperProps={{
        sx: {
          p: 2,
          maxWidth: 400,
          ...(arrow && {
            '&::before': {
              content: '""',
              position: 'absolute',
              top: -8,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 0,
              height: 0,
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderBottom: '8px solid white'
            }
          })
        }
      }}
    >
      {content}
    </MUIPopover>
  );
};
```

**검증 기준**:
- [ ] 모달 다이얼로그 시스템
- [ ] 확인 다이얼로그
- [ ] 드로어 컴포넌트
- [ ] 팝오버 컴포넌트

#### SubTask 7.13.4: 알림 및 토스트 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 4시간

**작업 내용**:

```typescript
// frontend/src/components/molecules/Notification/Notification.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Alert,
  AlertTitle,
  Snackbar,
  IconButton,
  Slide,
  SlideProps,
  Box,
  Typography,
  LinearProgress
} from '@mui/material';
import { Close, CheckCircle, Error, Warning, Info } from '@mui/icons-material';

// Toast types
export interface ToastOptions {
  id?: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  position?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  action?: React.ReactNode;
  closable?: boolean;
  progress?: boolean;
  onClose?: () => void;
}

// Toast Context
interface ToastContextValue {
  showToast: (options: ToastOptions) => void;
  hideToast: (id: string) => void;
  hideAllToasts: () => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Toast Provider
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastOptions[]>([]);
  
  const showToast = useCallback((options: ToastOptions) => {
    const id = options.id || Date.now().toString();
    const toast = {
      ...options,
      id,
      duration: options.duration ?? 5000
    };
    
    setToasts(prev => [...prev, toast]);
    
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => {
        hideToast(id);
      }, toast.duration);
    }
  }, []);
  
  const hideToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);
  
  const hideAllToasts = useCallback(() => {
    setToasts([]);
  }, []);
  
  return (
    <ToastContext.Provider value={{ showToast, hideToast, hideAllToasts }}>
      {children}
      <ToastContainer toasts={toasts} onClose={hideToast} />
    </ToastContext.Provider>
  );
};

// Toast Container
const ToastContainer: React.FC<{
  toasts: ToastOptions[];
  onClose: (id: string) => void;
}> = ({ toasts, onClose }) => {
  return (
    <>
      {toasts.map((toast, index) => (
        <Toast
          key={toast.id}
          {...toast}
          index={index}
          onClose={() => {
            toast.onClose?.();
            onClose(toast.id!);
          }}
        />
      ))}
    </>
  );
};

// Individual Toast Component
const Toast: React.FC<ToastOptions & { index: number }> = ({
  id,
  type = 'info',
  title,
  message,
  duration = 5000,
  position = { vertical: 'top', horizontal: 'right' },
  action,
  closable = true,
  progress = false,
  onClose,
  index
}) => {
  const [open, setOpen] = useState(true);
  const [progressValue, setProgressValue] = useState(100);
  
  React.useEffect(() => {
    if (progress && duration && duration > 0) {
      const interval = setInterval(() => {
        setProgressValue(prev => {
          const newValue = prev - (100 / (duration / 100));
          if (newValue <= 0) {
            clearInterval(interval);
            return 0;
          }
          return newValue;
        });
      }, 100);
      
      return () => clearInterval(interval);
    }
  }, [progress, duration]);
  
  const handleClose = () => {
    setOpen(false);
    setTimeout(() => {
      onClose?.();
    }, 300);
  };
  
  const icons = {
    success: <CheckCircle />,
    error: <Error />,
    warning: <Warning />,
    info: <Info />
  };
  
  return (
    <Snackbar
      open={open}
      anchorOrigin={position}
      onClose={handleClose}
      TransitionComponent={SlideTransition}
      sx={{
        top: position.vertical === 'top' ? 24 + index * 80 : undefined,
        bottom: position.vertical === 'bottom' ? 24 + index * 80 : undefined
      }}
    >
      <Alert
        severity={type}
        icon={icons[type]}
        action={
          <>
            {action}
            {closable && (
              <IconButton size="small" color="inherit" onClick={handleClose}>
                <Close fontSize="small" />
              </IconButton>
            )}
          </>
        }
        sx={{ minWidth: 300, maxWidth: 500 }}
      >
        {title && <AlertTitle>{title}</AlertTitle>}
        {message}
        {progress && duration && duration > 0 && (
          <LinearProgress
            variant="determinate"
            value={progressValue}
            sx={{
              mt: 1,
              height: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.3)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: 'currentColor'
              }
            }}
          />
        )}
      </Alert>
    </Snackbar>
  );
};

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="left" />;
}

// Alert Component
export interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  closable?: boolean;
  onClose?: () => void;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  variant?: 'standard' | 'filled' | 'outlined';
}

export const AlertComponent: React.FC<AlertProps> = ({
  type = 'info',
  title,
  message,
  closable = false,
  onClose,
  action,
  icon,
  variant = 'standard'
}) => {
  return (
    <Alert
      severity={type}
      onClose={closable ? onClose : undefined}
      action={action}
      icon={icon}
      variant={variant}
    >
      {title && <AlertTitle>{title}</AlertTitle>}
      {message}
    </Alert>
  );
};

// Notification Badge
export interface NotificationBadgeProps {
  count: number;
  max?: number;
  dot?: boolean;
  color?: 'primary' | 'secondary' | 'error';
  children: React.ReactNode;
  onClick?: () => void;
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({
  count,
  max = 99,
  dot = false,
  color = 'error',
  children,
  onClick
}) => {
  return (
    <Badge
      badgeContent={dot ? undefined : count > max ? `${max}+` : count}
      color={color}
      variant={dot ? 'dot' : 'standard'}
      invisible={count === 0}
      onClick={onClick}
      sx={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {children}
    </Badge>
  );
};

// System Notification Component
export interface SystemNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const SystemNotificationItem: React.FC<{
  notification: SystemNotification;
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
}> = ({ notification, onMarkAsRead, onDelete }) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'success': return <CheckCircle color="success" />;
      case 'error': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      default: return <Info color="info" />;
    }
  };
  
  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 1,
        backgroundColor: notification.read ? 'transparent' : 'action.hover',
        '&:hover': {
          backgroundColor: 'action.selected'
        }
      }}
    >
      <Box display="flex" alignItems="flex-start" gap={2}>
        {getIcon()}
        <Box flex={1}>
          <Typography variant="subtitle2" fontWeight={notification.read ? 400 : 600}>
            {notification.title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {notification.message}
          </Typography>
          <Typography variant="caption" color="text.disabled" sx={{ mt: 1, display: 'block' }}>
            {new Date(notification.timestamp).toLocaleString()}
          </Typography>
          {notification.action && (
            <Button
              size="small"
              onClick={notification.action.onClick}
              sx={{ mt: 1 }}
            >
              {notification.action.label}
            </Button>
          )}
        </Box>
        <Box>
          {!notification.read && (
            <IconButton size="small" onClick={() => onMarkAsRead(notification.id)}>
              <CheckCircle fontSize="small" />
            </IconButton>
          )}
          <IconButton size="small" onClick={() => onDelete(notification.id)}>
            <Close fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};
```

**검증 기준**:
- [ ] 토스트 시스템
- [ ] 알림 컴포넌트
- [ ] 시스템 알림
- [ ] 알림 배지

---

### Task 7.14: 유기체 컴포넌트 (Headers, Sidebars, etc.)

#### SubTask 7.14.1: 헤더 및 네비게이션 바 컴포넌트
**담당자**: 프론트엔드 개발자  
**예상 소요시간**: 5시간

**작업 내용**:

```typescript
// frontend/src/components/organisms/Header/Header.tsx
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Badge,
  InputBase,
  Divider,
  ListItemIcon,
  ListItemText,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { styled, alpha } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';

// Search Component
const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25)
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto'
  }
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch'
    }
  }
}));

export interface HeaderProps {
  onMenuToggle?: () => void;
  onThemeToggle?: () => void;
  isDarkMode?: boolean;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  notifications?: number;
  logo?: React.ReactNode;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  customActions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  onThemeToggle,
  isDarkMode = false,
  user,
  notifications = 0,
  logo,
  searchPlaceholder = 'Search...',
  onSearch,
  customActions
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleNotificationOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  };
  
  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };
  
  const handleSearch = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && onSearch) {
      onSearch(searchQuery);
    }
  };
  
  const handleLogout = () => {
    handleMenuClose();
    navigate('/logout');
  };
  
  const handleProfile = () => {
    handleMenuClose();
    navigate('/profile');
  };
  
  const handleSettings = () => {
    handleMenuClose();
    navigate('/settings');
  };
  
  return (
    <AppBar position="sticky" elevation={1}>
      <Toolbar>
        {/* Menu Toggle */}
        {onMenuToggle && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={onMenuToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        {/* Logo */}
        {logo ? (
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            {logo}
          </Box>
        ) : (
          <Typography variant="h6" noWrap sx={{ mr: 2 }}>
            T-Developer
          </Typography>
        )}
        
        {/* Search */}
        {!isMobile && onSearch && (
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleSearch}
            />
          </Search>
        )}
        
        <Box sx={{ flexGrow: 1 }} />
        
        {/* Custom Actions */}
        {customActions}
        
        {/* Theme Toggle */}
        {onThemeToggle && (
          <Tooltip title="Toggle theme">
            <IconButton color="inherit" onClick={onThemeToggle}>
              {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
        )}
        
        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton color="inherit" onClick={handleNotificationOpen}>
            <Badge badgeContent={notifications} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>
        
        {/* User Menu */}
        {user && (
          <Tooltip title="Account">
            <IconButton
              edge="end"
              color="inherit"
              onClick={handleProfileMenuOpen}
            >
              <Avatar
                src={user.avatar}
                alt={user.name}
                sx={{ width: 32, height: 32 }}
              >
                {user.name[0]}
              </Avatar>
            </IconButton>
          </Tooltip>
        )}
        
        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          PaperProps={{
            sx: { width: 250, mt: 1.5 }
          }}
        >
          {user && (
            <>
              <Box sx={{ px: 2, py: 1.5 }}>
                <Typography variant="subtitle1" fontWeight={600}>
                  {user.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {user.email}
                </Typography>
                {user.role && (
                  <Typography variant="caption" color="text.secondary">
                    {user.role}
                  </Typography>
                )}
              </Box>
              <Divider />
            </>
          )}
          
          <MenuItem onClick={handleProfile}>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Profile</ListItemText>
          </MenuItem>
          
          <MenuItem onClick={handleSettings}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Logout</ListItemText>
          </MenuItem>
        </Menu>
        
        {/* Notification Menu */}
        <Menu
          anchorEl={notificationAnchor}
          open={Boolean(notificationAnchor)}
          onClose={handleNotificationClose}
          PaperProps={{
            sx: { width: 360, maxHeight: 400 }
          }}
        >
          <Box sx={{ p: 2 }}>
            <Typography variant="h6">Notifications</Typography>
          </Box>
          <Divider />
          {notifications > 0 ? (
            <Box sx={{ p: 2 }}>
              {/* Notification items would go here */}
              <Typography variant="body2" color="text.secondary">
                You have {notifications} new notifications
              </Typography>
            </Box>
          ) : (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No new notifications
              </Typography>
            </Box>
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};
```

**검증 기준**:
- [ ] 헤더 레이아웃
- [ ] 검색 기능
- [ ] 사용자 메뉴
- [ ] 알림 시스템
