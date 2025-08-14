// Evolution Engine Types
export interface EvolutionGeneration {
  id: string;
  generation: number;
  fitness: number;
  diversity: number;
  convergence: number;
  agents: AgentGenome[];
  timestamp: string;
  parameters: EvolutionParameters;
}

export interface EvolutionParameters {
  populationSize: number;
  mutationRate: number;
  crossoverRate: number;
  eliteSize: number;
  maxGenerations: number;
  fitnessThreshold: number;
  diversityWeight: number;
}

export interface AgentGenome {
  id: string;
  generation: number;
  fitness: number;
  genes: Record<string, any>;
  parents: string[];
  mutations: number;
  performance: AgentPerformance;
}

export interface AgentPerformance {
  executionTime: number;
  memoryUsage: number;
  successRate: number;
  errorRate: number;
}

// Agent System Types
export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  version: string;
  size: number;
  performance: AgentMetrics;
  lastUpdated: string;
  dependencies: string[];
  capabilities: string[];
}

export type AgentType =
  | 'input'
  | 'processing'
  | 'analysis'
  | 'output'
  | 'meta'
  | 'service';

export type AgentStatus =
  | 'active'
  | 'idle'
  | 'processing'
  | 'error'
  | 'maintenance';

export interface AgentMetrics {
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  requestsPerSecond: number;
  errorRate: number;
  successRate: number;
}

// Workflow Types
export interface Workflow {
  id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  status: WorkflowStatus;
  createdAt: string;
  updatedAt: string;
  executionStats: ExecutionStats;
}

export interface WorkflowNode {
  id: string;
  type: 'agent' | 'decision' | 'parallel' | 'loop';
  position: { x: number; y: number };
  data: {
    label: string;
    agentId?: string;
    config?: Record<string, any>;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  label?: string;
}

export type WorkflowStatus =
  | 'draft'
  | 'ready'
  | 'running'
  | 'completed'
  | 'failed'
  | 'paused';

export interface ExecutionStats {
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  averageExecutionTime: number;
  lastExecutionTime?: string;
}

// Service Builder/Improver Types
export interface ServiceRequest {
  id: string;
  title: string;
  description: string;
  requirements: string[];
  status: ServiceStatus;
  createdAt: string;
  analysis?: ServiceAnalysis;
  implementation?: ServiceImplementation;
}

export type ServiceStatus =
  | 'pending'
  | 'analyzing'
  | 'building'
  | 'testing'
  | 'improving'
  | 'completed'
  | 'failed';

export interface ServiceAnalysis {
  feasibility: number;
  complexity: number;
  estimatedTime: number;
  suggestedAgents: string[];
  risks: string[];
  opportunities: string[];
}

export interface ServiceImplementation {
  agents: Agent[];
  workflow: Workflow;
  tests: TestResult[];
  metrics: ServiceMetrics;
  improvements: Improvement[];
}

export interface TestResult {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
}

export interface ServiceMetrics {
  codeQuality: number;
  performance: number;
  security: number;
  maintainability: number;
  testCoverage: number;
}

export interface Improvement {
  id: string;
  type: 'performance' | 'security' | 'quality' | 'feature';
  description: string;
  impact: number;
  applied: boolean;
  timestamp: string;
}

// Analytics Types
export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: {
    in: number;
    out: number;
  };
  activeAgents: number;
  runningWorkflows: number;
  queuedTasks: number;
}

export interface CostAnalytics {
  daily: CostBreakdown;
  weekly: CostBreakdown;
  monthly: CostBreakdown;
  projectedMonthly: number;
  savings: number;
  roi: number;
}

export interface CostBreakdown {
  ai: number;
  aws: number;
  total: number;
  breakdown: {
    compute: number;
    storage: number;
    network: number;
    aiApiCalls: number;
  };
}

// WebSocket Event Types
export interface WebSocketEvent {
  type: WebSocketEventType;
  payload: any;
  timestamp: string;
}

export type WebSocketEventType =
  | 'evolution:update'
  | 'agent:status'
  | 'workflow:progress'
  | 'metrics:update'
  | 'system:alert'
  | 'service:update';

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Filter and Query Types
export interface FilterOptions {
  search?: string;
  status?: string[];
  type?: string[];
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}
