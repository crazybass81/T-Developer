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
}

export abstract class BaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected context?: AgentContext;

  constructor(name: string) {
    super();
    this.id = `${name}-${Date.now()}`;
    this.name = name;
  }

  abstract initialize(): Promise<void>;
  abstract process(message: AgentMessage): Promise<any>;

  async start(context: AgentContext): Promise<void> {
    this.context = context;
    await this.initialize();
    this.emit('started', { agentId: this.id, context });
  }

  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    try {
      const result = await this.process(message);
      return {
        id: `response-${Date.now()}`,
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        id: `error-${Date.now()}`,
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: error.message },
        timestamp: new Date()
      };
    }
  }
}
