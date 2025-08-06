import axios, { AxiosInstance } from 'axios';
import { Logger } from 'winston';

export interface AgnoConfig {
  apiKey: string;
  endpoint: string;
  projectId: string;
  environment: string;
  batchSize?: number;
  flushInterval?: number;
}

export interface AgnoMetric {
  name: string;
  value: number;
  tags?: Record<string, string>;
  timestamp?: Date;
}

export interface AgnoEvent {
  type: string;
  data: any;
  userId?: string;
  sessionId?: string;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

export interface AgnoTrace {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  operation: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  status: 'success' | 'error';
  metadata?: Record<string, any>;
}

export class AgnoMonitoringClient {
  private config: AgnoConfig;
  private client: AxiosInstance;
  private logger: Logger;
  private metricBuffer: AgnoMetric[] = [];
  private eventBuffer: AgnoEvent[] = [];
  private traceBuffer: AgnoTrace[] = [];
  private flushTimer?: NodeJS.Timer;
  
  constructor(config: AgnoConfig, logger: Logger) {
    this.config = {
      batchSize: 100,
      flushInterval: 10000, // 10초
      ...config
    };
    this.logger = logger;
    
    this.client = axios.create({
      baseURL: config.endpoint,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
        'X-Project-ID': config.projectId,
        'X-Environment': config.environment
      }
    });
    
    this.startFlushTimer();
  }
  
  // 메트릭 전송
  async sendMetric(metric: AgnoMetric): Promise<void> {
    this.metricBuffer.push({
      ...metric,
      timestamp: metric.timestamp || new Date()
    });
    
    if (this.metricBuffer.length >= this.config.batchSize!) {
      await this.flushMetrics();
    }
  }
  
  // 이벤트 전송
  async sendEvent(event: AgnoEvent): Promise<void> {
    this.eventBuffer.push({
      ...event,
      timestamp: event.timestamp || new Date()
    });
    
    if (this.eventBuffer.length >= this.config.batchSize!) {
      await this.flushEvents();
    }
  }
  
  // 트레이스 전송
  async sendTrace(trace: AgnoTrace): Promise<void> {
    this.traceBuffer.push(trace);
    
    if (this.traceBuffer.length >= this.config.batchSize!) {
      await this.flushTraces();
    }
  }
  
  // 에이전트 성능 모니터링
  async monitorAgentPerformance(
    agentName: string,
    operation: string,
    duration: number,
    success: boolean,
    metadata?: any
  ): Promise<void> {
    await this.sendMetric({
      name: `agent.${agentName}.duration`,
      value: duration,
      tags: {
        agent: agentName,
        operation,
        status: success ? 'success' : 'failure'
      }
    });
    
    await this.sendEvent({
      type: 'agent_operation',
      data: {
        agent: agentName,
        operation,
        duration,
        success,
        ...metadata
      }
    });
  }
  
  // 에러 추적
  async trackError(
    error: Error,
    context: {
      agent?: string;
      operation?: string;
      userId?: string;
      projectId?: string;
    }
  ): Promise<void> {
    await this.sendEvent({
      type: 'error',
      data: {
        message: error.message,
        stack: error.stack,
        name: error.name,
        ...context
      },
      userId: context.userId
    });
  }
  
  // 배치 전송 메서드들
  private async flushMetrics(): Promise<void> {
    if (this.metricBuffer.length === 0) return;
    
    const metrics = [...this.metricBuffer];
    this.metricBuffer = [];
    
    try {
      await this.client.post('/metrics', { metrics });
      this.logger.debug(`Flushed ${metrics.length} metrics to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush metrics to Agno', { error });
      this.metricBuffer.unshift(...metrics);
    }
  }
  
  private async flushEvents(): Promise<void> {
    if (this.eventBuffer.length === 0) return;
    
    const events = [...this.eventBuffer];
    this.eventBuffer = [];
    
    try {
      await this.client.post('/events', { events });
      this.logger.debug(`Flushed ${events.length} events to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush events to Agno', { error });
      this.eventBuffer.unshift(...events);
    }
  }
  
  private async flushTraces(): Promise<void> {
    if (this.traceBuffer.length === 0) return;
    
    const traces = [...this.traceBuffer];
    this.traceBuffer = [];
    
    try {
      await this.client.post('/traces', { traces });
      this.logger.debug(`Flushed ${traces.length} traces to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush traces to Agno', { error });
      this.traceBuffer.unshift(...traces);
    }
  }
  
  // 타이머 관리
  private startFlushTimer(): void {
    this.flushTimer = setInterval(async () => {
      await Promise.all([
        this.flushMetrics(),
        this.flushEvents(),
        this.flushTraces()
      ]);
    }, this.config.flushInterval!);
  }
  
  async shutdown(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    
    await Promise.all([
      this.flushMetrics(),
      this.flushEvents(),
      this.flushTraces()
    ]);
  }
}

// Agno 데코레이터 (메서드 자동 추적)
export function AgnoTrace(
  operationName?: string
): MethodDecorator {
  return function (
    target: any,
    propertyKey: string | symbol,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const operation = operationName || String(propertyKey);
      const traceId = `trace-${Date.now()}-${Math.random()}`;
      const spanId = `span-${Date.now()}-${Math.random()}`;
      const startTime = Date.now();
      
      const agnoClient = (this as any).agnoClient;
      
      try {
        const result = await originalMethod.apply(this, args);
        
        if (agnoClient) {
          await agnoClient.sendTrace({
            traceId,
            spanId,
            operation,
            startTime: new Date(startTime),
            endTime: new Date(),
            duration: Date.now() - startTime,
            status: 'success',
            metadata: {
              class: target.constructor.name,
              method: String(propertyKey)
            }
          });
        }
        
        return result;
        
      } catch (error) {
        if (agnoClient) {
          await agnoClient.sendTrace({
            traceId,
            spanId,
            operation,
            startTime: new Date(startTime),
            endTime: new Date(),
            duration: Date.now() - startTime,
            status: 'error',
            metadata: {
              class: target.constructor.name,
              method: String(propertyKey),
              error: error.message
            }
          });
        }
        
        throw error;
      }
    };
    
    return descriptor;
  };
}