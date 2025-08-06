import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from 'winston';

export interface AgentMessage {
  id: string;
  type: 'request' | 'response' | 'error' | 'notification';
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

export abstract class BaseAgent extends EventEmitter {
  protected id: string;
  protected name: string;
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected logger: Logger;
  protected metrics: any;
  
  constructor(name: string, logger: Logger, metrics?: any) {
    super();
    this.id = uuidv4();
    this.name = name;
    this.logger = logger;
    this.metrics = metrics;
  }
  
  abstract process(message: AgentMessage): Promise<any>;
  
  async handleMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const startTime = Date.now();
    this.status = 'busy';
    
    try {
      this.logger.debug(`Agent ${this.name} processing message`, {
        agentId: this.id,
        messageId: message.id,
        type: message.type
      });
      
      const result = await this.process(message);
      
      const response: AgentMessage = {
        id: uuidv4(),
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date(),
        correlationId: message.id
      };
      
      if (this.metrics) {
        this.metrics.timing('agent.processing_time', Date.now() - startTime, [
          `agent:${this.name}`,
          `message_type:${message.type}`
        ]);
      }
      
      this.status = 'idle';
      return response;
      
    } catch (error) {
      this.status = 'error';
      this.logger.error(`Agent ${this.name} error`, {
        agentId: this.id,
        messageId: message.id,
        error
      });
      
      if (this.metrics) {
        this.metrics.increment('agent.errors', 1, [`agent:${this.name}`]);
      }
      
      return {
        id: uuidv4(),
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: (error as Error).message },
        timestamp: new Date(),
        correlationId: message.id
      };
    }
  }
  
  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    this.logger.info(`Capability registered: ${capability.name}`, {
      agentId: this.id,
      capability
    });
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
      status: this.status,
      capabilities: this.getCapabilities().length
    };
  }
  
  protected async onStart(): Promise<void> {}
  protected async onStop(): Promise<void> {}
}