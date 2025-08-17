// API Types
export enum ApiEndpoint {
  // Evolution endpoints
  EVOLUTION_START = '/api/evolution/start',
  EVOLUTION_STOP = '/api/evolution/stop',
  EVOLUTION_STATUS = '/api/evolution/status',
  EVOLUTION_CYCLES = '/api/evolution/cycles',
  EVOLUTION_CYCLE_BY_ID = '/api/evolution/cycles/:id',
  
  // Agent endpoints
  AGENTS = '/api/agents',
  AGENT_BY_ID = '/api/agents/:id',
  AGENT_START = '/api/agents/:id/start',
  AGENT_STOP = '/api/agents/:id/stop',
  AGENT_EXECUTE = '/api/agents/:id/execute',
  
  // Metrics endpoints
  METRICS = '/api/metrics',
  METRICS_REALTIME = '/api/metrics/realtime',
  
  // Workflow endpoints
  WORKFLOW_RUN = '/api/workflow/run',
  WORKFLOW_STATUS = '/api/workflow/:id/status',
  WORKFLOW_CANCEL = '/api/workflow/:id/cancel',
  
  // Logs endpoints
  LOGS = '/api/logs',
  LOGS_STREAM = '/api/logs/stream',
}

// Evolution types
export interface EvolutionConfig {
  target_path: string
  max_cycles: number
  focus_areas: string[]
  dry_run: boolean
  enable_code_modification?: boolean
  min_improvement?: number
  safety_checks?: boolean
}

export interface StartEvolutionRequest {
  config: EvolutionConfig
  context?: Record<string, any>
}

export interface StartEvolutionResponse {
  success: boolean
  message: string
  evolution_id?: string
  status?: EvolutionStatus
}

export enum EvolutionStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  SUCCESS = 'success',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface EvolutionCycle {
  id: string
  status: EvolutionStatus
  phase: string
  target_path: string
  focus_areas: string[]
  metrics_before?: Record<string, number>
  metrics_after?: Record<string, number>
  created_at: string
  updated_at?: string
  completed_at?: string
}

// Agent types
export enum AgentType {
  RESEARCH = 'research',
  CODE_ANALYSIS = 'code_analysis',
  PLANNER = 'planner',
  REFACTOR = 'refactor',
  EVALUATOR = 'evaluator',
}

export enum AgentStatus {
  IDLE = 'idle',
  READY = 'ready',
  BUSY = 'busy',
  ERROR = 'error',
  OFFLINE = 'offline',
}

export interface Agent {
  id: string
  name: string
  type: AgentType
  status: AgentStatus
  capabilities: string[]
  metrics: {
    tasksCompleted: number
    successRate: number
    avgExecutionTime: number
    lastActivity?: string
  }
  config?: Record<string, any>
}

export interface AgentTask {
  id: string
  agent_id: string
  type: string
  payload: Record<string, any>
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  started_at?: string
  completed_at?: string
  result?: any
  error?: string
}

// WebSocket types
export enum WebSocketMessageType {
  // Connection events
  CONNECTION = 'connection',
  DISCONNECT = 'disconnect',
  ERROR = 'error',
  
  // Evolution events
  EVOLUTION_STARTED = 'evolution:started',
  EVOLUTION_PHASE = 'evolution:phase',
  EVOLUTION_PROGRESS = 'evolution:progress',
  EVOLUTION_COMPLETED = 'evolution:completed',
  EVOLUTION_FAILED = 'evolution:failed',
  EVOLUTION_STOPPED = 'evolution:stopped',
  EVOLUTION_CYCLE_START = 'evolution:cycle_start',
  
  // Agent events
  AGENT_STATUS = 'agent:status',
  AGENT_TASK_START = 'agent:task:start',
  AGENT_TASK_COMPLETE = 'agent:task:complete',
  AGENT_TASK_FAILED = 'agent:task:failed',
  
  // Metrics events
  METRICS_UPDATE = 'metrics:update',
  
  // Log events
  LOG_MESSAGE = 'log:message',
}

export interface WebSocketMessage {
  id: string
  type: WebSocketMessageType
  payload: any
  timestamp: string
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

// Error types
export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  timestamp: string
}

// Metrics types
export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  active_tasks: number
  queue_size: number
  uptime: number
}

export interface EvolutionMetrics {
  cycles_completed: number
  total_improvements: number
  success_rate: number
  avg_cycle_time: number
  code_quality_score: number
}

// Workflow types
export interface WorkflowConfig {
  workflow: string
  target: string
  problem?: string
  parameters?: Record<string, any>
}

export interface WorkflowStatus {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_step?: string
  steps_completed: number
  total_steps: number
  started_at: string
  completed_at?: string
  error?: string
}

// Log types
export interface LogEntry {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  source: string
  message: string
  context?: Record<string, any>
}

export interface LogFilter {
  level?: string[]
  source?: string[]
  start_time?: string
  end_time?: string
  search?: string
  limit?: number
  offset?: number
}