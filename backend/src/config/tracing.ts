// Simple tracing implementation without OpenTelemetry dependencies
export class SimpleTracer {
  private spans: Map<string, any> = new Map();
  
  startSpan(name: string, attributes?: Record<string, any>) {
    const spanId = `${name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const span = {
      id: spanId,
      name,
      startTime: Date.now(),
      attributes: attributes || {},
      status: 'active'
    };
    
    this.spans.set(spanId, span);
    return span;
  }
  
  finishSpan(spanId: string, status: 'success' | 'error' = 'success', error?: any) {
    const span = this.spans.get(spanId);
    if (span) {
      span.endTime = Date.now();
      span.duration = span.endTime - span.startTime;
      span.status = status;
      if (error) {
        span.error = error.message;
      }
      console.log(`[TRACE] ${span.name}: ${span.duration}ms (${status})`);
    }
  }
  
  async startActiveSpan<T>(name: string, fn: (span: any) => Promise<T>): Promise<T> {
    const span = this.startSpan(name);
    try {
      const result = await fn(span);
      this.finishSpan(span.id, 'success');
      return result;
    } catch (error) {
      this.finishSpan(span.id, 'error', error);
      throw error;
    }
  }
}

const tracer = new SimpleTracer();

export class TracedAgent {
  constructor(private agentName: string) {}
  
  async execute(projectId: string, params: any): Promise<any> {
    return tracer.startActiveSpan(`agent.${this.agentName}.execute`, async (span: any) => {
      span.attributes = {
        'agent.name': this.agentName,
        'project.id': projectId,
        'params.count': Object.keys(params).length
      };
      
      // Simulate agent execution
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
      
      return {
        agentName: this.agentName,
        projectId,
        result: 'success',
        executionTime: Date.now(),
        params
      };
    });
  }
}

export class TracedExternalService {
  static async callBedrock(model: string, prompt: string): Promise<any> {
    return tracer.startActiveSpan(`external.bedrock`, async (span: any) => {
      span.attributes = {
        'bedrock.model': model,
        'prompt.length': prompt.length
      };
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, Math.random() * 200));
      
      return {
        model,
        prompt,
        response: `Mock response for: ${prompt.substring(0, 50)}...`,
        tokens: Math.floor(Math.random() * 1000)
      };
    });
  }
  
  static async queryDynamoDB(table: string, key: string): Promise<any> {
    return tracer.startActiveSpan(`db.query`, async (span: any) => {
      span.attributes = {
        'db.table': table,
        'db.key': key,
        'db.operation': 'query'
      };
      
      // Simulate DB query
      await new Promise(resolve => setTimeout(resolve, Math.random() * 50));
      
      return {
        table,
        key,
        data: {
          id: key,
          value: `Mock data for ${key}`,
          timestamp: new Date().toISOString()
        }
      };
    });
  }
}