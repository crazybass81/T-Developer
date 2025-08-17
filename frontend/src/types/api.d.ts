// API Type Definitions for T-Developer v2

// ============= Common Types =============
export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}

export interface Timestamped {
  timestamp: string
}

export interface PaginationParams {
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface ApiError {
  error: string
  message: string
  statusCode: number
  details?: any
}

// ============= Agent Types =============
export interface Agent extends BaseEntity {
  name: string
  type: AgentType
  status: AgentStatus
  capabilities: string[]
  config: AgentConfig
  metrics: AgentMetrics
  last_execution?: string
  error?: string
}

export enum AgentType {
  RESEARCH = 'research',
  CODE_ANALYSIS = 'code_analysis',
  PLANNER = 'planner',
  REFACTOR = 'refactor',
  EVALUATOR = 'evaluator',
  META = 'meta'
}

export enum AgentStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  STOPPED = 'stopped'
}

export interface AgentConfig {
  timeout?: number
  max_retries?: number
  enable_cache?: boolean
  [key: string]: any
}

export interface AgentMetrics {
  execution_count: number
  success_rate: number
  avg_execution_time: number
  last_error?: string
}

export interface AgentInput {
  task_id: string
  action: string
  payload: any
  context?: any
  priority?: number
}

export interface AgentOutput {
  task_id: string
  status: AgentStatus
  result?: any
  error?: string
  metrics?: any
  artifacts?: Artifact[]
}

export interface Artifact {
  kind: string
  ref: string
  content: any
}

// ============= Evolution Types =============
export interface EvolutionCycle extends BaseEntity {
  cycle_number: number
  phase: EvolutionPhase
  status: EvolutionStatus
  target_path: string
  focus_areas: string[]
  metrics_before: EvolutionMetrics
  metrics_after?: EvolutionMetrics
  improvements?: Improvement[]
  duration?: number
  error?: string
}

export enum EvolutionPhase {
  INITIALIZATION = 'initialization',
  RESEARCH = 'research',
  ANALYSIS = 'analysis',
  PLANNING = 'planning',
  IMPLEMENTATION = 'implementation',
  EVALUATION = 'evaluation',
  COMPLETED = 'completed'
}

export enum EvolutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  PARTIAL = 'partial',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface EvolutionMetrics {
  docstring_coverage: number
  test_coverage: number
  complexity_score: number
  security_score: number
  performance_score: number
  technical_debt: number
}

export interface Improvement {
  type: string
  description: string
  file_path: string
  line_start?: number
  line_end?: number
  impact: number
}

export interface EvolutionConfig {
  target_path: string
  max_cycles: number
  focus_areas: string[]
  dry_run: boolean
  max_files?: number
  enable_code_modification: boolean
  auto_commit?: boolean
  create_pr?: boolean
}

// ============= Context Types =============
export interface ProjectContext {
  project_root: string
  language: string
  framework?: string
  dependencies: Record<string, string>
  structure: Record<string, string[]>
  recent_changes: ChangeRecord[]
  active_tasks: string[]
  patterns: Record<string, any>
  metadata: Record<string, any>
}

export interface TaskContext {
  task_id: string
  task_type: string
  description: string
  target_files: string[]
  related_files: string[]
  requirements: string[]
  constraints: string[]
  history: HistoryEntry[]
  metrics: Record<string, number>
  created_at: string
}

export interface ChangeRecord {
  file: string
  type: 'added' | 'modified' | 'deleted'
  timestamp: string
  author?: string
  message?: string
}

export interface HistoryEntry {
  action: string
  timestamp: string
  result: 'success' | 'failure'
  details?: any
}

// ============= Memory Types =============
export interface Memory {
  memory_id: string
  type: MemoryType
  content: any
  timestamp: string
  importance: number
  access_count: number
  last_accessed?: string
  expires_at?: string
}

export enum MemoryType {
  SEMANTIC = 'semantic',
  EPISODIC = 'episodic',
  WORKING = 'working',
  PATTERN = 'pattern',
  EXPERIENCE = 'experience'
}

export interface Pattern {
  pattern_id: string
  pattern_type: string
  description: string
  context: any
  success_rate: number
  usage_count: number
  last_used?: string
}

// ============= Metrics Types =============
export interface MetricData {
  name: string
  value: number
  unit?: string
  timestamp: string
  tags?: Record<string, string>
}

export interface MetricSummary {
  total_evolutions: number
  success_rate: number
  avg_improvement: number
  total_files_modified: number
  total_lines_changed: number
  active_agents: number
  system_health: number
}

export interface TimeSeriesData {
  timestamps: string[]
  values: number[]
  label: string
}

// ============= Log Types =============
export interface LogEntry {
  id: string
  level: LogLevel
  message: string
  timestamp: string
  source: string
  context?: any
  stack_trace?: string
}

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export interface LogFilter {
  level?: LogLevel[]
  source?: string[]
  startTime?: string
  endTime?: string
  search?: string
  limit?: number
}

// ============= Workflow Types =============
export interface Workflow {
  id: string
  name: string
  description: string
  steps: WorkflowStep[]
  status: WorkflowStatus
  created_at: string
  started_at?: string
  completed_at?: string
  error?: string
}

export interface WorkflowStep {
  id: string
  name: string
  agent: AgentType
  input: any
  output?: any
  status: WorkflowStatus
  duration?: number
  error?: string
}

export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// ============= WebSocket Types =============
export interface WebSocketMessage {
  type: WebSocketMessageType
  payload: any
  timestamp: string
  id?: string
}

export enum WebSocketMessageType {
  // Evolution events
  EVOLUTION_STARTED = 'evolution:started',
  EVOLUTION_PHASE_CHANGED = 'evolution:phase_changed',
  EVOLUTION_PROGRESS = 'evolution:progress',
  EVOLUTION_COMPLETED = 'evolution:completed',
  EVOLUTION_FAILED = 'evolution:failed',

  // Agent events
  AGENT_STARTED = 'agent:started',
  AGENT_COMPLETED = 'agent:completed',
  AGENT_FAILED = 'agent:failed',
  AGENT_STATUS_CHANGED = 'agent:status_changed',

  // Metric events
  METRICS_UPDATE = 'metrics:update',

  // Log events
  LOG_ENTRY = 'log:entry',

  // System events
  SYSTEM_STATUS = 'system:status',
  SYSTEM_ERROR = 'system:error',
  SYSTEM_WARNING = 'system:warning',

  // Connection events
  CONNECTION_ESTABLISHED = 'connection:established',
  CONNECTION_LOST = 'connection:lost',
  CONNECTION_ERROR = 'connection:error'
}

// ============= API Endpoints =============
export enum ApiEndpoint {
  // Agent endpoints
  AGENTS = '/api/agents',
  AGENT_BY_ID = '/api/agents/:id',
  AGENT_START = '/api/agents/:id/start',
  AGENT_STOP = '/api/agents/:id/stop',
  AGENT_RESTART = '/api/agents/:id/restart',

  // Evolution endpoints
  EVOLUTION_START = '/api/evolution/start',
  EVOLUTION_STOP = '/api/evolution/stop',
  EVOLUTION_STATUS = '/api/evolution/status',
  EVOLUTION_CYCLES = '/api/evolution/cycles',
  EVOLUTION_CYCLE_BY_ID = '/api/evolution/cycles/:id',

  // Context endpoints
  CONTEXT_PROJECT = '/api/context/project',
  CONTEXT_TASK = '/api/context/task/:id',
  CONTEXT_EVOLUTION = '/api/context/evolution/:id',

  // Memory endpoints
  MEMORY_SEARCH = '/api/memory/search',
  MEMORY_STORE = '/api/memory/store',
  MEMORY_RECALL = '/api/memory/recall',

  // Metrics endpoints
  METRICS = '/api/metrics',
  METRICS_REALTIME = '/api/metrics/realtime',
  METRICS_SUMMARY = '/api/metrics/summary',
  METRICS_HISTORY = '/api/metrics/history',

  // Log endpoints
  LOGS = '/api/logs',
  LOGS_STREAM = '/api/logs/stream',
  LOGS_EXPORT = '/api/logs/export',

  // Workflow endpoints
  WORKFLOW_RUN = '/api/workflow/run',
  WORKFLOW_STATUS = '/api/workflow/:id/status',
  WORKFLOW_CANCEL = '/api/workflow/:id/cancel',
  WORKFLOWS = '/api/workflows',

  // System endpoints
  HEALTH = '/api/health',
  STATUS = '/api/status',
  CONFIG = '/api/config'
}

// ============= Request/Response Types =============
export interface StartEvolutionRequest {
  config: EvolutionConfig
  context?: any
}

export interface StartEvolutionResponse {
  evolution_id: string
  status: EvolutionStatus
  message: string
}

export interface RunWorkflowRequest {
  workflow: string
  target: string
  problem?: string
  config?: any
}

export interface RunWorkflowResponse {
  workflow_id: string
  status: WorkflowStatus
  message: string
}

export interface SearchMemoryRequest {
  query?: string
  type?: MemoryType
  importance_min?: number
  limit?: number
  offset?: number
}

export interface SearchMemoryResponse {
  memories: Memory[]
  total: number
  has_more: boolean
}
