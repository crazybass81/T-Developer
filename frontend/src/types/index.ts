// Base types
export interface BaseEntity {
  id: string
  createdAt: Date
  updatedAt: Date
}

// User types
export interface User extends BaseEntity {
  email: string
  name: string
  avatar?: string
  plan: 'free' | 'pro' | 'enterprise'
}

// Project types
export interface Project extends BaseEntity {
  name: string
  description: string
  status: 'draft' | 'building' | 'completed' | 'error' | 'archived'
  framework: 'react' | 'vue' | 'angular' | 'nextjs' | 'svelte'
  template?: string
  userId: string
  buildId?: string
  deployUrl?: string
  downloadId?: string
  downloadUrl?: string
  sourceCode?: string
  thumbnail?: string
  tags?: string[]
  settings: ProjectSettings
}

export interface ProjectSettings {
  theme: 'light' | 'dark' | 'auto'
  language: 'typescript' | 'javascript'
  cssFramework: 'tailwind' | 'css' | 'styled-components'
  buildTool: 'vite' | 'webpack' | 'parcel'
  packageManager: 'npm' | 'yarn' | 'pnpm'
  features: string[]
}

// Agent types
export type AgentStatus = 'idle' | 'processing' | 'completed' | 'error' | 'paused'

export interface AgentState {
  id: number
  name: string
  status: AgentStatus
  progress: number
  startTime?: Date
  endTime?: Date
  input?: any
  output?: any
  error?: string
  metrics?: {
    executionTime: number
    memoryUsage: number
    tokensUsed?: number
  }
}

export interface AgentPipeline {
  id: string
  projectId: string
  agents: AgentState[]
  currentAgent?: number
  status: 'idle' | 'running' | 'completed' | 'error' | 'paused'
  startTime?: Date
  endTime?: Date
  totalProgress: number
}

// WebSocket message types
export interface WSMessage {
  type: string
  data: any
  timestamp: Date
}

export interface AgentStatusUpdate extends WSMessage {
  type: 'agent_status'
  data: {
    agentId: number
    status: AgentStatus
    progress: number
    output?: any
    error?: string
  }
}

export interface CodeGenerationUpdate extends WSMessage {
  type: 'code_generation'
  data: {
    file: string
    content: string
    action: 'create' | 'update' | 'delete'
  }
}

export interface BuildProgressUpdate extends WSMessage {
  type: 'build_progress'
  data: {
    stage: string
    progress: number
    logs: string[]
  }
}

// Component types
export interface ComponentLibraryItem {
  id: string
  name: string
  description: string
  category: 'ui' | 'layout' | 'forms' | 'navigation' | 'feedback'
  framework: string[]
  tags: string[]
  rating: number
  downloads: number
  author: string
  version: string
  code: string
  preview: string
  props: ComponentProp[]
  examples: ComponentExample[]
}

export interface ComponentProp {
  name: string
  type: string
  required: boolean
  default?: any
  description: string
}

export interface ComponentExample {
  name: string
  code: string
  description: string
}

// Build and deployment types
export interface BuildConfig {
  framework: string
  buildTool: string
  outputDir: string
  publicDir: string
  envVars: Record<string, string>
  optimization: {
    minification: boolean
    sourceMaps: boolean
    treeshaking: boolean
    compression: boolean
  }
}

export interface DeploymentConfig {
  platform: 'vercel' | 'netlify' | 'aws' | 'github-pages'
  domain?: string
  environment: 'production' | 'staging' | 'preview'
  envVars: Record<string, string>
}

export interface BuildLog {
  timestamp: Date
  level: 'info' | 'warn' | 'error'
  message: string
  source?: string
}

// Chat and NL processing types
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: {
    tokens?: number
    model?: string
    confidence?: number
  }
}

export interface NLProcessingResult {
  intent: string
  entities: Record<string, any>
  confidence: number
  suggestions: string[]
  clarifyingQuestions?: string[]
}

// Template types
export interface Template {
  id: string
  name: string
  description: string
  category: string
  framework: string
  preview: string
  thumbnail: string
  features: string[]
  complexity: 'beginner' | 'intermediate' | 'advanced'
  estimatedTime: number
  tags: string[]
  rating: number
  downloads: number
}

// Analytics types
export interface UsageMetrics {
  projectsCreated: number
  tokensUsed: number
  buildTime: number
  successRate: number
  period: 'today' | 'week' | 'month' | 'year'
}

export interface AgentPerformanceMetric {
  agentId: number
  averageExecutionTime: number
  successRate: number
  errorRate: number
  totalExecutions: number
  memoryUsage: number
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: any
  }
  meta?: {
    page?: number
    limit?: number
    total?: number
  }
}

// Form types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'radio'
  placeholder?: string
  required?: boolean
  validation?: {
    min?: number
    max?: number
    pattern?: string
    custom?: (value: any) => string | null
  }
  options?: Array<{ label: string; value: string }>
}

// Theme types
export interface Theme {
  name: string
  colors: {
    primary: string
    secondary: string
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
    success: string
    warning: string
    error: string
  }
  fonts: {
    sans: string
    mono: string
    display: string
  }
  spacing: Record<string, string>
  borderRadius: Record<string, string>
  shadows: Record<string, string>
}

// Error types
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: Date
  severity: 'low' | 'medium' | 'high' | 'critical'
}

// Search and filter types
export interface SearchFilters {
  query?: string
  category?: string
  framework?: string
  status?: string
  dateRange?: {
    start: Date
    end: Date
  }
  tags?: string[]
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface PaginationInfo {
  page: number
  limit: number
  total: number
  hasNext: boolean
  hasPrev: boolean
}