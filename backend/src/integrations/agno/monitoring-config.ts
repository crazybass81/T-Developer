import axios, { AxiosInstance } from 'axios';

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
  private metricBuffer: AgnoMetric[] = [];
  private eventBuffer: AgnoEvent[] = [];
  private traceBuffer: AgnoTrace[] = [];
  private flushTimer?: NodeJS.Timer;
  
  constructor(config: AgnoConfig) {
    this.config = {
      batchSize: 100,
      flushInterval: 10000, // 10 seconds
      ...config
    };
    
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
  
  async sendMetric(metric: AgnoMetric): Promise<void> {
    this.metricBuffer.push({
      ...metric,
      timestamp: metric.timestamp || new Date()
    });
    
    if (this.metricBuffer.length >= this.config.batchSize!) {
      await this.flushMetrics();
    }
  }
  
  async sendEvent(event: AgnoEvent): Promise<void> {
    this.eventBuffer.push({
      ...event,
      timestamp: event.timestamp || new Date()
    });
    
    if (this.eventBuffer.length >= this.config.batchSize!) {
      await this.flushEvents();
    }
  }
  
  async sendTrace(trace: AgnoTrace): Promise<void> {
    this.traceBuffer.push(trace);
    
    if (this.traceBuffer.length >= this.config.batchSize!) {
      await this.flushTraces();
    }
  }
  
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
  
  async monitorProjectProgress(
    projectId: string,
    phase: string,
    progress: number,
    metadata?: any
  ): Promise<void> {
    await this.sendEvent({
      type: 'project_progress',
      data: {
        projectId,
        phase,
        progress,
        ...metadata
      }
    });
    
    await this.sendMetric({
      name: 'project.progress',
      value: progress,
      tags: {
        project: projectId,
        phase
      }
    });
  }
  
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
  
  private async flushMetrics(): Promise<void> {
    if (this.metricBuffer.length === 0) return;
    
    const metrics = [...this.metricBuffer];
    this.metricBuffer = [];
    
    try {
      await this.client.post('/metrics', { metrics });
      console.log(`Flushed ${metrics.length} metrics to Agno`);
    } catch (error) {
      console.error('Failed to flush metrics to Agno', error);
      this.metricBuffer.unshift(...metrics);
    }
  }
  
  private async flushEvents(): Promise<void> {
    if (this.eventBuffer.length === 0) return;
    
    const events = [...this.eventBuffer];
    this.eventBuffer = [];
    
    try {
      await this.client.post('/events', { events });
      console.log(`Flushed ${events.length} events to Agno`);
    } catch (error) {
      console.error('Failed to flush events to Agno', error);
      this.eventBuffer.unshift(...events);
    }
  }
  
  private async flushTraces(): Promise<void> {
    if (this.traceBuffer.length === 0) return;
    
    const traces = [...this.traceBuffer];
    this.traceBuffer = [];
    
    try {
      await this.client.post('/traces', { traces });
      console.log(`Flushed ${traces.length} traces to Agno`);
    } catch (error) {
      console.error('Failed to flush traces to Agno', error);
      this.traceBuffer.unshift(...traces);
    }
  }
  
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

// Agno trace decorator
export function AgnoTrace(operationName?: string): MethodDecorator {
  return function (
    target: any,
    propertyKey: string | symbol,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const operation = operationName || String(propertyKey);
      const traceId = `trace-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const spanId = `span-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
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
            status: 'success' as const,
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
            status: 'error' as const,
            metadata: {
              class: target.constructor.name,
              method: String(propertyKey),
              error: error instanceof Error ? error.message : 'Unknown error'
            }
          });
        }
        
        throw error;
      }
    };
    
    return descriptor;
  };
}