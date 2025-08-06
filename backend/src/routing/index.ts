// 라우팅 모듈 통합 인덱스
export { IntelligentRouter } from './intelligent-router';
export { LoadBalancer, type AgentLoad, type BalancingStrategy, type LoadBalancingResult } from './load-balancer';

// 라우팅 관련 타입 정의
export interface Task {
  id: string;
  type: string;
  requirements: string[];
  complexity: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: Date;
  slaDeadline?: Date;
}

export interface Agent {
  id: string;
  type: string;
  capabilities: string[];
  status: 'idle' | 'busy' | 'offline';
  performance: {
    successRate: number;
    avgResponseTime: number;
    totalTasks: number;
  };
}

export interface RoutingDecision {
  selectedAgent: string;
  confidence: number;
  reasoning: string;
  alternatives: Array<{
    agentId: string;
    score: number;
    reason: string;
  }>;
}

export interface RoutingMetrics {
  totalRequests: number;
  successfulRoutes: number;
  averageLatency: number;
  agentUtilization: Record<string, number>;
  errorRate: number;
}

// 라우팅 전략 열거형
export enum RoutingStrategy {
  CAPABILITY_MATCH = 'capability-match',
  LOAD_BALANCED = 'load-balanced',
  PERFORMANCE_BASED = 'performance-based',
  HYBRID = 'hybrid'
}

// 라우팅 설정 인터페이스
export interface RoutingConfig {
  strategy: RoutingStrategy;
  loadBalancingStrategy: BalancingStrategy;
  enableMetrics: boolean;
  maxRetries: number;
  timeoutMs: number;
}