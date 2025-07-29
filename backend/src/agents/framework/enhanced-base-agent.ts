import { EventEmitter } from 'events';

export interface AgentContext {
  projectId: string;
  userId: string;
  sessionId: string;
  metadata: Record<string, any>;
}

export interface AgentMessage {
  id: string;
  type: 'request' | 'response' | 'event' | 'error';
  source: string;
  target: string;
  payload: any;
  timestamp: Date;
  correlationId?: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  inputSchema: any;
  outputSchema: any;
  version: string;
}

export interface AgentConfig {
  name: string;
  version?: string;
  timeout?: number;
  retries?: number;
  capabilities?: AgentCapability[];
}

export abstract class EnhancedBaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected readonly version: string;
  protected readonly timeout: number;
  protected readonly retries: number;
  protected context?: AgentContext;
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected status: 'idle' | 'busy' | 'error' | 'stopped' = 'idle';
  protected metrics = {
    messagesProcessed: 0,
    errors: 0,
    averageProcessingTime: 0,
    lastActivity: new Date()
  };

  constructor(config: AgentConfig) {
    super();
    this.id = `${config.name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.name = config.name;
    this.version = config.version || '1.0.0';
    this.timeout = config.timeout || 30000;
    this.retries = config.retries || 3;
    
    if (config.capabilities) {
      config.capabilities.forEach(cap => this.registerCapability(cap));
    }
    
    this.initialize();
  }

  protected abstract initialize(): void;
  protected abstract process(message: AgentMessage): Promise<any>;

  async start(context: AgentContext): Promise<void> {
    this.context = context;
    this.status = 'idle';
    
    console.log(`Agent ${this.name} started`, { agentId: this.id, context });
    this.emit('started', { agentId: this.id, context });
    
    await this.onStart();
  }

  async stop(): Promise<void> {
    this.status = 'stopped';
    console.log(`Agent ${this.name} stopped`, { agentId: this.id });
    this.emit('stopped', { agentId: this.id });
    
    await this.onStop();
  }

  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    if (this.status === 'stopped') {
      throw new Error(`Agent ${this.name} is stopped`);
    }

    const startTime = Date.now();
    this.status = 'busy';
    this.metrics.lastActivity = new Date();

    try {
      console.log(`Agent ${this.name} processing message`, {
        agentId: this.id,
        messageId: message.id,
        type: message.type
      });

      const result = await this.processWithTimeout(message);

      const processingTime = Date.now() - startTime;
      this.updateMetrics(processingTime, false);

      const response: AgentMessage = {
        id: `response-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date(),
        correlationId: message.id
      };

      this.status = 'idle';
      this.emit('messageProcessed', { message, response, processingTime });
      return response;

    } catch (error) {
      this.status = 'error';
      this.updateMetrics(Date.now() - startTime, true);
      
      console.error(`Agent ${this.name} error`, {
        agentId: this.id,
        messageId: message.id,
        error
      });

      const errorResponse = {
        id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'error' as const,
        source: this.id,
        target: message.source,
        payload: { error: error instanceof Error ? error.message : String(error) },
        timestamp: new Date(),
        correlationId: message.id
      };

      this.emit('error', { message, error, response: errorResponse });
      return errorResponse;
    }
  }

  private async processWithTimeout(message: AgentMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Agent ${this.name} processing timeout after ${this.timeout}ms`));
      }, this.timeout);

      this.process(message)
        .then(result => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  private updateMetrics(processingTime: number, isError: boolean): void {
    this.metrics.messagesProcessed++;
    if (isError) {
      this.metrics.errors++;
    }
    
    const totalMessages = this.metrics.messagesProcessed;
    this.metrics.averageProcessingTime = 
      (this.metrics.averageProcessingTime * (totalMessages - 1) + processingTime) / totalMessages;
  }

  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    console.log(`Capability registered: ${capability.name}`, {
      agentId: this.id,
      capability
    });
    this.emit('capabilityRegistered', capability);
  }

  hasCapability(capabilityName: string): boolean {
    return this.capabilities.has(capabilityName);
  }

  getCapabilities(): AgentCapability[] {
    return Array.from(this.capabilities.values());
  }

  getStatus(): string {
    return this.status;
  }

  getMetrics(): any {
    return {
      agentId: this.id,
      name: this.name,
      version: this.version,
      status: this.status,
      capabilities: this.getCapabilities().length,
      ...this.metrics,
      uptime: this.context ? Date.now() - new Date(this.context.metadata.startTime || Date.now()).getTime() : 0
    };
  }

  protected async onStart(): Promise<void> {}
  protected async onStop(): Promise<void> {}

  protected log(level: 'info' | 'warn' | 'error', message: string, meta?: any): void {
    console[level](`[${this.name}:${this.id}] ${message}`, meta);
  }

  protected validateInput(input: any, schema: any): boolean {
    return input !== null && input !== undefined;
  }

  protected createResponse(data: any, metadata?: any): any {
    return {
      success: true,
      data,
      metadata: {
        agentId: this.id,
        agentName: this.name,
        timestamp: new Date().toISOString(),
        ...metadata
      }
    };
  }

  protected createError(message: string, code?: string, details?: any): any {
    return {
      success: false,
      error: {
        message,
        code,
        details,
        agentId: this.id,
        timestamp: new Date().toISOString()
      }
    };
  }
}