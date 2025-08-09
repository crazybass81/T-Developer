# T-Developer MVP 프론트엔드 페이지별 상세 기획서

## 시스템 아키텍처 개요

T-Developer MVP는 9개의 AI 에이전트가 협업하여 자연어 입력을 실제 동작하는 코드로 변환하는 차세대 개발 플랫폼입니다. AWS Bedrock, Agno, AWS Agent Squad를 통합한 멀티 에이전트 시스템으로, 실시간 WebSocket 통신을 통해 프론트엔드와 상호작용합니다.

### 핵심 에이전트 시스템
- **NL Input Agent**: 자연어 처리 및 요구사항 분석
- **UI Selection Agent**: UI 템플릿 선택 및 매칭
- **Parser Agent**: 코드 구조 분석 및 AST 처리
- **Component Decision Agent**: 컴포넌트 재사용/생성 결정
- **Match Rate Agent**: 유사도 계산 및 매칭 점수
- **Search/Call Agent**: 컴포넌트 라이브러리 검색
- **Generation Agent**: 코드 생성 및 최적화
- **Service Assembly Agent**: 서비스 조합 및 통합
- **Download/Package Agent**: 빌드 및 배포 패키징

## 페이지별 상세 기획

### 1. 랜딩/홈 페이지

#### 페이지 목적과 핵심 기능
- 플랫폼 소개 및 핵심 가치 전달
- 빠른 시작을 위한 진입점 제공
- 사용자 인증 및 온보딩

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Navigation Bar                         │
│  [Logo] [Features] [Docs] [Login/Start] │
├─────────────────────────────────────────┤
│                                         │
│        Hero Section                     │
│   "자연어로 앱을 만드는 가장 빠른 방법"    │
│                                         │
│   [시작하기] [데모 보기]                  │
│                                         │
├─────────────────────────────────────────┤
│   Interactive Demo                      │
│   ┌─────────┬──────────────────┐       │
│   │ Input   │ Live Preview     │       │
│   │         │                  │       │
│   └─────────┴──────────────────┘       │
├─────────────────────────────────────────┤
│   Feature Cards (3 columns)             │
│   [AI 에이전트] [실시간] [배포]          │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface LandingPageComponents {
  NavigationHeader: {
    logo: Logo;
    menu: MenuItem[];
    authButton: AuthButton;
  };
  HeroSection: {
    title: AnimatedText;
    subtitle: Text;
    ctaButtons: CTAButton[];
    backgroundAnimation: ParticleEffect;
  };
  InteractiveDemo: {
    codeInput: CodeMirror;
    livePreview: IframePreview;
    examplePrompts: PromptSuggestion[];
  };
  FeatureGrid: {
    featureCards: FeatureCard[];
    animations: ScrollAnimation;
  };
}
```

#### 사용자 인터랙션 플로우
1. 페이지 진입 → 자동 애니메이션 시작
2. Interactive Demo → 실시간 코드 생성 체험
3. "시작하기" 클릭 → 회원가입/로그인 모달
4. 인증 완료 → 프로젝트 생성 페이지로 이동

#### 백엔드 API 연동
```typescript
// 데모용 API 엔드포인트
POST /api/demo/generate
GET /api/showcase/projects
GET /api/statistics/usage
```

### 2. 프로젝트 생성 페이지 (자연어 입력)

#### 페이지 목적과 핵심 기능
- 자연어로 프로젝트 요구사항 입력
- AI 에이전트와의 대화형 인터페이스
- 요구사항 명확화 및 확인

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Project Creation Wizard                │
├─────────────────────────────────────────┤
│  Progress: [1.입력]━[2.분석]─[3.생성]    │
├─────────┬───────────────────────────────┤
│         │  Chat Interface               │
│ Context │  ┌─────────────────────┐     │
│ Panel   │  │ AI: 어떤 앱을 만들고  │     │
│         │  │     싶으신가요?       │     │
│ - 예제   │  └─────────────────────┘     │
│ - 템플릿 │  ┌─────────────────────┐     │
│ - 설정   │  │ User: 할일 관리 앱... │     │
│         │  └─────────────────────┘     │
│         │                               │
│         │  [입력 필드] [전송] [음성]     │
├─────────┴───────────────────────────────┤
│  Suggestions: [Todo앱] [캘린더] [노트]   │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface ProjectCreationComponents {
  WizardProgress: {
    steps: WizardStep[];
    currentStep: number;
  };
  ChatInterface: {
    messageHistory: Message[];
    inputField: PromptInput;
    voiceRecognition: VoiceInput;
    suggestions: SuggestionChips[];
  };
  ContextPanel: {
    templates: TemplateSelector;
    examples: ExampleProjects;
    settings: ProjectSettings;
    requirements: RequirementsList;
  };
  NLProcessingIndicator: {
    agentStatus: AgentStatusDisplay;
    processingSteps: StepIndicator[];
  };
}
```

#### 사용자 인터랙션 플로우
1. 자연어 입력 → NL Input Agent 처리
2. AI 응답 및 명확화 질문
3. 요구사항 확인 → UI Selection Agent 활성화
4. 템플릿 제안 → 사용자 선택
5. 프로젝트 생성 → 대시보드로 이동

#### 백엔드 API 연동
```typescript
// WebSocket 연결
ws.connect('/ws/project-creation');

// API 엔드포인트
POST /api/projects/create
POST /api/nl/process
GET /api/templates/suggestions
```

#### 실시간 업데이트 (WebSocket)
```typescript
interface WSMessages {
  nl_processing: {
    status: 'analyzing' | 'clarifying' | 'complete';
    confidence: number;
    suggestions: string[];
  };
  template_matching: {
    templates: Template[];
    matchScores: number[];
  };
}
```

### 3. 프로젝트 진행 대시보드 (에이전트 상태 모니터링)

#### 페이지 목적과 핵심 기능
- 9개 에이전트의 실시간 상태 모니터링
- 생성 과정 시각화
- 중간 결과물 미리보기

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Project: "할일 관리 앱"     [중단][설정] │
├─────────────────────────────────────────┤
│  Agent Pipeline Visualization           │
│                                         │
│  [NL]━━▶[UI]━━▶[Parser]━━▶[Component]  │
│   ✓     🔄      ⏸         ⏸           │
│     ↓                                   │
│  [Match]◀━━[Search]◀━━[Generation]     │
│    ⏸        ⏸          ⏸              │
│     ↓                                   │
│  [Assembly]━━▶[Package]                 │
│      ⏸           ⏸                     │
├─────────┬───────────────────────────────┤
│ Logs    │  Preview                      │
│         │  ┌──────────────────┐        │
│ 15:32   │  │                  │        │
│ NL완료   │  │  Generated UI    │        │
│         │  │                  │        │
│ 15:33   │  └──────────────────┘        │
│ UI선택   │                              │
│         │  Code Output:                 │
│ 15:34   │  ```jsx                      │
│ 파싱중   │  function TodoApp() {        │
│         │    ...                       │
└─────────┴───────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface DashboardComponents {
  AgentPipeline: {
    agents: AgentNode[];
    connections: PipelineConnection[];
    currentStatus: AgentStatus[];
  };
  MonitoringPanel: {
    performanceMetrics: Metrics;
    errorLogs: ErrorLog[];
    timeline: TimelineEvent[];
  };
  PreviewPanel: {
    uiPreview: LivePreview;
    codeViewer: CodeDisplay;
    fileTree: FileStructure;
  };
  ControlPanel: {
    pauseButton: ControlButton;
    settingsButton: ControlButton;
    exportButton: ControlButton;
  };
}
```

#### WebSocket 실시간 업데이트
```typescript
interface AgentStatusUpdate {
  type: 'agent_status';
  agentId: string;
  status: 'idle' | 'processing' | 'completed' | 'error';
  progress: number;
  output?: any;
  timestamp: string;
}

// 상태 업데이트 핸들러
const handleAgentUpdate = (update: AgentStatusUpdate) => {
  updateAgentVisualState(update.agentId, update.status);
  updateProgressBar(update.progress);
  if (update.output) {
    renderPreview(update.output);
  }
};
```

### 4. 컴포넌트 관리/검색 페이지

#### 페이지 목적과 핵심 기능
- 재사용 가능한 컴포넌트 라이브러리
- 검색 및 필터링
- 컴포넌트 커스터마이징

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Component Library          [새 컴포넌트] │
├──────────┬──────────────────────────────┤
│ Filters  │  Search: [___________] 🔍    │
│          │                              │
│ Category │  Grid View / List View       │
│ □ UI     │  ┌─────┐ ┌─────┐ ┌─────┐   │
│ □ Layout │  │Button│ │Input │ │Card  │   │
│ □ Forms  │  │ ⭐4.5│ │ ⭐4.2│ │ ⭐4.8│   │
│          │  └─────┘ └─────┘ └─────┘   │
│ Framework│  ┌─────┐ ┌─────┐ ┌─────┐   │
│ □ React  │  │Modal │ │Table │ │Nav   │   │
│ □ Vue    │  │ ⭐4.0│ │ ⭐4.6│ │ ⭐4.3│   │
│          │  └─────┘ └─────┘ └─────┘   │
├──────────┴──────────────────────────────┤
│ Component Detail (on hover/click)       │
│ Preview | Code | Props | Usage          │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface ComponentLibraryComponents {
  SearchBar: {
    input: SearchInput;
    filters: FilterDropdown[];
    sortOptions: SortSelector;
  };
  FilterPanel: {
    categoryFilters: CheckboxGroup;
    frameworkFilters: CheckboxGroup;
    complexityFilter: RangeSlider;
    ratingFilter: StarRating;
  };
  ComponentGrid: {
    componentCards: ComponentCard[];
    pagination: Pagination;
    viewToggle: ViewModeToggle;
  };
  ComponentModal: {
    preview: InteractivePreview;
    codeView: SyntaxHighlighter;
    propsEditor: PropsPanel;
    usageExamples: ExampleCode[];
  };
}
```

#### 백엔드 API 연동
```typescript
// 컴포넌트 검색 및 필터링
GET /api/components/search?q={query}&category={cat}&framework={fw}
GET /api/components/{id}
POST /api/components/customize
GET /api/components/recommendations
```

### 5. 코드 생성 결과 뷰어

#### 페이지 목적과 핵심 기능
- 생성된 코드 실시간 확인
- 코드 편집 및 수정
- 버전 관리 및 비교

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Generated Code        [Download] [Deploy]│
├────────┬────────────────────────────────┤
│ Files  │  Editor (Monaco)               │
│        │  ┌─────────────────────────┐   │
│ 📁 src │  │ import React from 'react'│   │
│  📄 App│  │ import './App.css'      │   │
│  📄 idx│  │                         │   │
│ 📁 comp│  │ function App() {        │   │
│  📄 Btn│  │   return (              │   │
│  📄 Crd│  │     <div>               │   │
│        │  │       ...               │   │
│        │  └─────────────────────────┘   │
├────────┴───────┬────────────────────────┤
│ Terminal       │ Preview               │
│ $ npm start    │ ┌─────────────────┐   │
│ Starting...    │ │                 │   │
│ ✓ Ready        │ │  Live Preview   │   │
│                │ │                 │   │
│                │ └─────────────────┘   │
└────────────────┴────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface CodeViewerComponents {
  FileExplorer: {
    fileTree: FileTreeNode[];
    fileActions: FileContextMenu;
  };
  CodeEditor: {
    monaco: MonacoEditor;
    syntaxHighlighting: LanguageSupport;
    autoComplete: IntelliSense;
    diffView: DiffEditor;
  };
  Terminal: {
    console: TerminalEmulator;
    commands: CommandInterface;
    output: OutputDisplay;
  };
  PreviewPane: {
    iframe: ResponsiveIframe;
    deviceSelector: DeviceFrame;
    refreshButton: RefreshControl;
  };
}
```

#### 실시간 업데이트 요구사항
```typescript
// WebSocket 코드 생성 스트리밍
ws.on('code_generation', (data: {
  file: string;
  content: string;
  action: 'create' | 'update' | 'delete';
}) => {
  updateFileInEditor(data);
  refreshPreview();
});
```

### 6. 다운로드/배포 페이지

#### 페이지 목적과 핵심 기능
- 프로젝트 빌드 및 패키징
- 다양한 배포 옵션 제공
- 배포 상태 모니터링

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Build & Deploy                         │
├─────────────────────────────────────────┤
│  Build Configuration                    │
│  ┌──────────────────────────────┐      │
│  │ Framework: React ▼            │      │
│  │ Build Tool: Vite ▼            │      │
│  │ ☑ Minification                │      │
│  │ ☑ Source Maps                 │      │
│  └──────────────────────────────┘      │
├─────────────────────────────────────────┤
│  Deployment Options                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Vercel  │ │   AWS   │ │ Netlify │  │
│  │   ⚡    │ │   ☁️    │ │   🚀   │  │
│  │ [Deploy]│ │ [Deploy]│ │ [Deploy]│  │
│  └─────────┘ └─────────┘ └─────────┘  │
│                                         │
│  Or Download: [ZIP] [TAR] [Git Repo]   │
├─────────────────────────────────────────┤
│  Build Progress                         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░ 75% Building...     │
│                                         │
│  ✓ Dependencies installed               │
│  ✓ Code optimized                      │
│  🔄 Creating production build...        │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface DeploymentComponents {
  BuildConfig: {
    frameworkSelector: Dropdown;
    buildOptions: CheckboxGroup;
    envVariables: EnvEditor;
  };
  DeploymentTargets: {
    vercelIntegration: VercelDeploy;
    awsIntegration: AWSDeploy;
    netlifyIntegration: NetlifyDeploy;
    customDeploy: CustomDeployConfig;
  };
  DownloadOptions: {
    formatSelector: RadioGroup;
    compressionOptions: CheckboxGroup;
    downloadButton: ActionButton;
  };
  BuildProgress: {
    progressBar: ProgressIndicator;
    logStream: BuildLogs;
    statusIndicators: StatusList;
  };
}
```

#### 백엔드 API 연동
```typescript
POST /api/build/start
GET /api/build/status/{buildId}
POST /api/deploy/{platform}
GET /api/deploy/status/{deploymentId}
GET /api/download/{projectId}/{format}
```

### 7. 프로젝트 목록/관리 페이지

#### 페이지 목적과 핵심 기능
- 모든 프로젝트 overview
- 프로젝트 관리 (수정, 삭제, 복제)
- 프로젝트 검색 및 필터링

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  My Projects (12)         [새 프로젝트]  │
├─────────────────────────────────────────┤
│  Filter: [All] [Active] [Archived]      │
│  Sort: [최신순 ▼]  Search: [______] 🔍  │
├─────────────────────────────────────────┤
│  ┌────────────┐ ┌────────────┐         │
│  │ Todo App   │ │ E-commerce │         │
│  │ 🟢 Active  │ │ 🟡 Building │         │
│  │ React      │ │ Vue        │         │
│  │ 2일 전     │ │ 5일 전     │         │
│  │[열기][수정]│ │[열기][수정]│         │
│  └────────────┘ └────────────┘         │
│  ┌────────────┐ ┌────────────┐         │
│  │ Blog       │ │ Dashboard  │         │
│  │ ✅ Complete│ │ 🔵 Draft   │         │
│  │ Next.js    │ │ React      │         │
│  │ 1주 전     │ │ 2주 전     │         │
│  │[열기][수정]│ │[열기][수정]│         │
│  └────────────┘ └────────────┘         │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface ProjectListComponents {
  ProjectHeader: {
    title: Title;
    projectCount: Counter;
    createButton: CTAButton;
  };
  FilterBar: {
    statusFilter: TabFilter;
    sortDropdown: SortSelector;
    searchInput: SearchBar;
  };
  ProjectGrid: {
    projectCards: ProjectCard[];
    emptyState: EmptyStateMessage;
    loadMore: InfiniteScroll;
  };
  ProjectCard: {
    thumbnail: ProjectPreview;
    status: StatusBadge;
    metadata: ProjectMeta;
    actions: ActionButtons;
  };
}
```

### 8. 분석/모니터링 대시보드

#### 페이지 목적과 핵심 기능
- 사용 통계 및 분석
- 에이전트 성능 모니터링
- 비용 및 리소스 사용량 추적

#### UI/UX 레이아웃 구조
```
┌─────────────────────────────────────────┐
│  Analytics Dashboard    Period: [7일 ▼] │
├─────────────────────────────────────────┤
│  Key Metrics                            │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐│
│  │ Projects │ │ Tokens   │ │ Success ││
│  │    42    │ │  125.3K  │ │  94.2%  ││
│  │   +12%   │ │   +8.5%  │ │  +2.1%  ││
│  └──────────┘ └──────────┘ └─────────┘│
├─────────────────────────────────────────┤
│  Agent Performance Chart                │
│  ┌────────────────────────────────┐    │
│  │     📊 Line Graph               │    │
│  │     각 에이전트별 처리 시간       │    │
│  └────────────────────────────────┘    │
├─────────────────────────────────────────┤
│  Usage Breakdown        Cost Analysis   │
│  ┌─────────────┐      ┌──────────────┐ │
│  │ 🍩 Pie Chart│      │ 📊 Bar Chart │ │
│  │ by Feature  │      │ Daily Cost   │ │
│  └─────────────┘      └──────────────┘ │
└─────────────────────────────────────────┘
```

#### 컴포넌트 구성
```typescript
interface AnalyticsComponents {
  MetricsCards: {
    projectMetric: MetricCard;
    tokenMetric: MetricCard;
    successRateMetric: MetricCard;
    customMetrics: MetricCard[];
  };
  Charts: {
    performanceChart: LineChart;
    usagePieChart: PieChart;
    costBarChart: BarChart;
    heatmap: ActivityHeatmap;
  };
  DataTables: {
    agentPerformance: DataTable;
    errorLogs: LogTable;
    apiUsage: UsageTable;
  };
  Controls: {
    dateRangePicker: DatePicker;
    exportButton: ExportControl;
    refreshButton: RefreshControl;
  };
}
```

## 기술 스택 구현 가이드

### 상태 관리 아키텍처 (Zustand)
```typescript
// stores/projectStore.ts
interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  agents: AgentStatus[];
  
  // Actions
  createProject: (data: ProjectData) => Promise<void>;
  updateAgentStatus: (agentId: string, status: AgentStatus) => void;
  loadProjects: () => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  agents: initialAgentStates,
  
  createProject: async (data) => {
    const response = await api.createProject(data);
    set(state => ({
      projects: [...state.projects, response],
      currentProject: response
    }));
  },
  
  updateAgentStatus: (agentId, status) => {
    set(state => ({
      agents: state.agents.map(agent =>
        agent.id === agentId ? { ...agent, ...status } : agent
      )
    }));
  }
}));
```

### WebSocket 서비스
```typescript
// services/websocket.ts
class WebSocketService {
  private ws: WebSocket | null = null;
  private subscribers = new Map<string, Set<Function>>();

  connect(projectId: string) {
    this.ws = new WebSocket(`${WS_URL}/project/${projectId}`);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.notifySubscribers(data.type, data);
    };
    
    this.ws.onerror = this.handleError;
    this.ws.onclose = this.handleReconnect;
  }

  subscribe(eventType: string, callback: Function) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set());
    }
    this.subscribers.get(eventType)!.add(callback);
    
    return () => {
      this.subscribers.get(eventType)?.delete(callback);
    };
  }

  private notifySubscribers(eventType: string, data: any) {
    this.subscribers.get(eventType)?.forEach(cb => cb(data));
  }
}

export const wsService = new WebSocketService();
```

### 컴포넌트 구조 예시
```typescript
// components/features/AgentPipeline/AgentPipeline.tsx
export const AgentPipeline: FC = () => {
  const { agents, updateAgentStatus } = useProjectStore();
  
  useEffect(() => {
    const unsubscribe = wsService.subscribe('agent_status', 
      (data: AgentStatusUpdate) => {
        updateAgentStatus(data.agentId, data);
      }
    );
    
    return unsubscribe;
  }, []);

  return (
    <div className="agent-pipeline">
      {agents.map(agent => (
        <AgentNode
          key={agent.id}
          agent={agent}
          onStatusChange={updateAgentStatus}
        />
      ))}
    </div>
  );
};
```

## 성능 최적화 전략

1. **코드 스플리팅**: 각 페이지별 lazy loading
2. **메모이제이션**: React.memo, useMemo 활용
3. **가상 스크롤링**: 대량 컴포넌트 목록 처리
4. **WebSocket 재연결**: 자동 재연결 로직
5. **상태 정규화**: 중복 데이터 최소화
6. **이미지 최적화**: Next.js Image 컴포넌트 활용

## 접근성 및 반응형 디자인

- **모바일 우선**: 모든 페이지 모바일 최적화
- **키보드 네비게이션**: 모든 인터랙티브 요소 접근 가능
- **ARIA 레이블**: 스크린 리더 완벽 지원
- **다크 모드**: 시스템 설정 연동 및 수동 전환
- **국제화(i18n)**: 다국어 지원 준비

이 상세 기획서는 T-Developer MVP의 프론트엔드 개발을 위한 완전한 가이드를 제공하며, 각 페이지의 목적, 구조, 컴포넌트, 그리고 기술적 구현 방법을 명확하게 정의합니다.