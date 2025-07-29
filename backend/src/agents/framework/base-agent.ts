import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

export interface AgentContext {
  projectId: string;
  userId: string;
  sessionId: string;
  parentAgent?: string;
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

export abstract class BaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected readonly version: string;
  protected context?: AgentContext;
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  
  constructor(name: string, version: string = '1.0.0') {
    super();
    this.id = `${name}-${uuidv4()}`;
    this.name = name;
    this.version = version;
    
    this.initialize();
  }
  
  protected abstract initialize(): void;
  protected abstract process(message: AgentMessage): Promise<any>;
  
  async start(context: AgentContext): Promise<void> {
    this.context = context;
    this.status = 'idle';
    
    console.log(`Agent ${this.name} started`, { agentId: this.id });
    this.emit('started', { agentId: this.id, context });
    
    await this.onStart();
  }
  
  async stop(): Promise<void> {
    this.status = 'idle';
    
    console.log(`Agent ${this.name} stopped`, { agentId: this.id });
    this.emit('stopped', { agentId: this.id });
    
    await this.onStop();
  }
  
  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    const startTime = Date.now();
    this.status = 'busy';
    
    try {
      console.log(`Agent ${this.name} processing message`, {
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
      
      this.status = 'idle';
      return response;
      
    } catch (error) {
      this.status = 'error';
      console.error(`Agent ${this.name} error`, {
        agentId: this.id,
        messageId: message.id,
        error
      });
      
      return {
        id: uuidv4(),
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: error instanceof Error ? error.message : 'Unknown error' },
        timestamp: new Date(),
        correlationId: message.id
      };
    }
  }
  
  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    console.log(`Capability registered: ${capability.name}`, { agentId: this.id });
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