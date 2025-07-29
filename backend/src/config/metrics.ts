import promClient from 'prom-client';
import { Request, Response, NextFunction } from 'express';

const register = new promClient.Registry();

promClient.collectDefaultMetrics({ 
  register,
  prefix: 't_developer_'
});

export const metrics = {
  httpRequestDuration: new promClient.Histogram({
    name: 't_developer_http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
  }),
  
  httpRequestTotal: new promClient.Counter({
    name: 't_developer_http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
  }),
  
  agentExecutionDuration: new promClient.Histogram({
    name: 't_developer_agent_execution_duration_seconds',
    help: 'Duration of agent executions in seconds',
    labelNames: ['agent_name', 'status'],
    buckets: [1, 5, 10, 30, 60, 120, 300, 600]
  }),
  
  agentExecutionTotal: new promClient.Counter({
    name: 't_developer_agent_executions_total',
    help: 'Total number of agent executions',
    labelNames: ['agent_name', 'status']
  }),
  
  agentTokenUsage: new promClient.Counter({
    name: 't_developer_agent_token_usage_total',
    help: 'Total tokens used by agents',
    labelNames: ['agent_name', 'model']
  }),
  
  activeProjects: new promClient.Gauge({
    name: 't_developer_active_projects',
    help: 'Number of currently active projects',
    labelNames: ['status']
  }),
  
  cacheHitRate: new promClient.Gauge({
    name: 't_developer_cache_hit_rate',
    help: 'Cache hit rate percentage',
    labelNames: ['cache_type']
  })
};

register.registerMetric(metrics.httpRequestDuration);
register.registerMetric(metrics.httpRequestTotal);
register.registerMetric(metrics.agentExecutionDuration);
register.registerMetric(metrics.agentExecutionTotal);
register.registerMetric(metrics.agentTokenUsage);
register.registerMetric(metrics.activeProjects);
register.registerMetric(metrics.cacheHitRate);

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

export function metricsEndpoint() {
  return async (req: Request, res: Response) => {
    res.set('Content-Type', register.contentType);
    const metricsData = await register.metrics();
    res.end(metricsData);
  };
}

export class MetricsHelper {
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
  
  static updateCacheHitRate(cacheType: string, hitRate: number): void {
    metrics.cacheHitRate.set({ cache_type: cacheType }, hitRate);
  }
  
  static updateActiveProjects(status: string, count: number): void {
    metrics.activeProjects.set({ status }, count);
  }
}