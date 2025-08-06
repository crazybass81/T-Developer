import promClient from 'prom-client';
import { Request, Response, NextFunction } from 'express';

// Prometheus 레지스트리
const register = new promClient.Registry();

// 기본 메트릭 수집
promClient.collectDefaultMetrics({ 
  register,
  prefix: 't_developer_'
});

// 커스텀 메트릭 정의
export const metrics = {
  // HTTP 요청 관련
  httpRequestDuration: new promClient.Histogram({
    name: 't_developer_http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10],
    registers: [register]
  }),
  
  httpRequestTotal: new promClient.Counter({
    name: 't_developer_http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code'],
    registers: [register]
  }),
  
  // 에이전트 실행 관련
  agentExecutionDuration: new promClient.Histogram({
    name: 't_developer_agent_execution_duration_seconds',
    help: 'Duration of agent executions in seconds',
    labelNames: ['agent_name', 'status'],
    buckets: [1, 5, 10, 30, 60, 120, 300, 600],
    registers: [register]
  }),
  
  agentExecutionTotal: new promClient.Counter({
    name: 't_developer_agent_executions_total',
    help: 'Total number of agent executions',
    labelNames: ['agent_name', 'status'],
    registers: [register]
  }),
  
  agentTokenUsage: new promClient.Counter({
    name: 't_developer_agent_token_usage_total',
    help: 'Total tokens used by agents',
    labelNames: ['agent_name', 'model'],
    registers: [register]
  }),
  
  // 프로젝트 관련
  projectCreationDuration: new promClient.Histogram({
    name: 't_developer_project_creation_duration_seconds',
    help: 'Duration of project creation in seconds',
    labelNames: ['project_type', 'status'],
    buckets: [10, 30, 60, 120, 300, 600, 1200],
    registers: [register]
  }),
  
  activeProjects: new promClient.Gauge({
    name: 't_developer_active_projects',
    help: 'Number of currently active projects',
    labelNames: ['status'],
    registers: [register]
  }),
  
  // 시스템 리소스
  cacheHitRate: new promClient.Gauge({
    name: 't_developer_cache_hit_rate',
    help: 'Cache hit rate percentage',
    labelNames: ['cache_type'],
    registers: [register]
  }),
  
  queueSize: new promClient.Gauge({
    name: 't_developer_queue_size',
    help: 'Current size of job queues',
    labelNames: ['queue_name'],
    registers: [register]
  }),
  
  // 비즈니스 메트릭
  componentUsage: new promClient.Counter({
    name: 't_developer_component_usage_total',
    help: 'Total usage of components',
    labelNames: ['component_name', 'version', 'language'],
    registers: [register]
  }),
  
  apiKeyUsage: new promClient.Counter({
    name: 't_developer_api_key_usage_total',
    help: 'API key usage by user',
    labelNames: ['user_id', 'endpoint'],
    registers: [register]
  })
};

// Express 미들웨어
export function metricsMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();
    
    res.on('finish', () => {
      const duration = (Date.now() - start) / 1000;
      const route = req.route?.path || req.path;
      const labels = {
        method: req.method,
        route,
        status_code: res.statusCode.toString()
      };
      
      metrics.httpRequestDuration.observe(labels, duration);
      metrics.httpRequestTotal.inc(labels);
    });
    
    next();
  };
}

// 메트릭 엔드포인트
export function metricsEndpoint() {
  return async (req: Request, res: Response) => {
    res.set('Content-Type', register.contentType);
    const metricsData = await register.metrics();
    res.end(metricsData);
  };
}

// 메트릭 헬퍼 클래스
export class MetricsHelper {
  // 에이전트 실행 메트릭 기록
  static recordAgentExecution(
    agentName: string, 
    duration: number, 
    status: 'success' | 'failure',
    tokensUsed?: number,
    model?: string
  ): void {
    metrics.agentExecutionDuration.observe({ agent_name: agentName, status }, duration);
    metrics.agentExecutionTotal.inc({ agent_name: agentName, status });
    
    if (tokensUsed && model) {
      metrics.agentTokenUsage.inc({ agent_name: agentName, model }, tokensUsed);
    }
  }
  
  // 프로젝트 생성 메트릭 기록
  static recordProjectCreation(
    projectType: string,
    duration: number,
    status: 'success' | 'failure'
  ): void {
    metrics.projectCreationDuration.observe({ project_type: projectType, status }, duration);
  }
  
  // 캐시 히트율 업데이트
  static updateCacheHitRate(cacheType: string, hitRate: number): void {
    metrics.cacheHitRate.set({ cache_type: cacheType }, hitRate);
  }
  
  // 큐 크기 업데이트
  static updateQueueSize(queueName: string, size: number): void {
    metrics.queueSize.set({ queue_name: queueName }, size);
  }
  
  // 활성 프로젝트 수 업데이트
  static updateActiveProjects(counts: Record<string, number>): void {
    Object.entries(counts).forEach(([status, count]) => {
      metrics.activeProjects.set({ status }, count);
    });
  }
}

export { register };