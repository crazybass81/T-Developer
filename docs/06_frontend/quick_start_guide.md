# 🚀 T-Developer 프론트엔드 Quick Start Guide

## 📦 즉시 실행 가능한 MVP 셋업

### Step 1: 프로젝트 초기화 (2분)
```bash
cd /home/ec2-user/T-DeveloperMVP
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"
```

### Step 2: 필수 패키지 설치 (3분)
```bash
cd frontend
npm install \
  @tanstack/react-query \
  axios \
  socket.io-client \
  chart.js react-chartjs-2 \
  lucide-react \
  clsx tailwind-merge \
  @radix-ui/react-slot \
  class-variance-authority
```

### Step 3: shadcn/ui 설정 (1분)
```bash
npx shadcn-ui@latest init
# 선택 옵션:
# - Would you like to use TypeScript? → Yes
# - Which style? → Default
# - Which color? → Slate
# - CSS variables? → Yes
```

### Step 4: 기본 컴포넌트 설치 (2분)
```bash
npx shadcn-ui@latest add button card badge tabs alert
```

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── agents/
│   │   │   └── page.tsx
│   │   └── evolution/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   ├── dashboard/
│   │   │   ├── MetricCard.tsx
│   │   │   ├── EvolutionChart.tsx
│   │   │   └── AgentGrid.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── Sidebar.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── evolution.ts
│   │   │   └── agents.ts
│   │   └── utils.ts
│   └── hooks/
│       ├── useEvolution.ts
│       └── useAgents.ts
└── package.json
```

## 🔧 핵심 파일 구현

### 1. API Client (`src/lib/api/client.ts`)
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  error => Promise.reject(error)
);
```

### 2. Evolution Hook (`src/hooks/useEvolution.ts`)
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api/client';

export function useEvolutionStatus() {
  return useQuery({
    queryKey: ['evolution', 'status'],
    queryFn: async () => {
      const { data } = await api.get('/evolution/status');
      return data;
    },
    refetchInterval: 5000 // Poll every 5 seconds
  });
}

export function useEvolutionParams() {
  return useMutation({
    mutationFn: async (params: any) => {
      const { data } = await api.post('/evolution/params', params);
      return data;
    }
  });
}
```

### 3. Dashboard Page (`src/app/dashboard/page.tsx`)
```typescript
'use client';

import { useEvolutionStatus } from '@/hooks/useEvolution';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Brain, Zap, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading } = useEvolutionStatus();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="space-y-4 p-8">
      <h1 className="text-3xl font-bold">Evolution Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Generation</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.generation || 0}</div>
            <p className="text-xs text-muted-foreground">
              +{data?.improvement || 0}% from last
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.activeAgents || 0}</div>
            <p className="text-xs text-muted-foreground">
              {data?.totalAgents || 0} total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fitness Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.fitness || 0}%</div>
            <p className="text-xs text-muted-foreground">
              Target: 95%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.performance || 0}μs</div>
            <p className="text-xs text-muted-foreground">
              Constraint: 3μs
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### 4. WebSocket 연결 (`src/lib/socket.ts`)
```typescript
import { io, Socket } from 'socket.io-client';

class SocketManager {
  private socket: Socket | null = null;

  connect() {
    if (this.socket) return;
    
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    this.socket = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('evolution:update', (data) => {
      // Handle evolution updates
      console.log('Evolution update:', data);
    });

    this.socket.on('agent:status', (data) => {
      // Handle agent status updates
      console.log('Agent status:', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }
}

export const socketManager = new SocketManager();
```

## 🎨 테마 설정 (`src/app/globals.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --evolution: 142 76% 36%;
    --performance: 271 91% 65%;
    --danger: 0 84.2% 60.2%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --evolution: 142 76% 46%;
    --performance: 271 91% 75%;
  }
}

@layer utilities {
  .animate-pulse-slow {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  .gradient-evolution {
    background: linear-gradient(135deg, hsl(var(--evolution)), hsl(var(--performance)));
  }
}
```

## 🚀 실행 명령어

```bash
# 개발 서버 시작
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 실행
npm start

# 타입 체크
npm run type-check

# Lint
npm run lint
```

## 📊 현재 백엔드와 연동 가능한 엔드포인트

```typescript
// 즉시 사용 가능한 API 엔드포인트
const endpoints = {
  // Evolution Engine
  '/evolution/status': 'GET',
  '/evolution/generation/:id': 'GET',
  '/evolution/params': 'POST',
  '/evolution/start': 'POST',
  '/evolution/stop': 'POST',
  
  // Agent Registry
  '/agents': 'GET',
  '/agents/:id': 'GET',
  '/agents/:id/metrics': 'GET',
  '/agents/:id/deploy': 'POST',
  
  // Workflow Engine
  '/workflows': 'GET',
  '/workflows/create': 'POST',
  '/workflows/:id/execute': 'POST',
  '/workflows/:id/status': 'GET',
  
  // Analytics
  '/analytics/performance': 'GET',
  '/analytics/cost': 'GET',
  '/analytics/roi': 'GET'
};
```

## ⏱️ 예상 개발 시간

| 단계 | 작업 | 시간 |
|------|------|------|
| **Setup** | 프로젝트 초기화 + 패키지 | 10분 |
| **Day 1** | 기본 레이아웃 + 라우팅 | 4시간 |
| **Day 2** | Dashboard 구현 | 6시간 |
| **Day 3** | Agent Management | 6시간 |
| **Day 4** | Evolution Visualizer | 8시간 |
| **Day 5** | WebSocket + 실시간 업데이트 | 6시간 |
| **Total** | **MVP 완성** | **5일** |

## 🎯 체크리스트

- [ ] Next.js 프로젝트 생성
- [ ] 필수 패키지 설치
- [ ] API 클라이언트 구성
- [ ] 기본 레이아웃 구현
- [ ] Dashboard 페이지
- [ ] Agent 관리 페이지
- [ ] Evolution 시각화
- [ ] WebSocket 연동
- [ ] 에러 핸들링
- [ ] 로딩 상태
- [ ] 반응형 디자인
- [ ] 다크모드 지원
- [ ] 배포 준비

이 가이드를 따라 **즉시 시작**할 수 있습니다! 🚀
