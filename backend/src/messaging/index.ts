// Task 1.14: 메시징 큐 시스템 - Main exports
export { QueueManager } from './queue-manager';
export { MessageProcessor } from './message-processor';
export { EventBus, AgentEventBus } from './event-bus';
export { MessageRouter, MessageFilter, AgentMessageRouter } from './message-routing';

// Integrated messaging system
import { QueueManager } from './queue-manager';
import { MessageProcessor } from './message-processor';
import { AgentEventBus } from './event-bus';
import { AgentMessageRouter } from './message-routing';

export class MessagingSystem {
  public queueManager: QueueManager;
  public processor: MessageProcessor;
  public eventBus: AgentEventBus;
  public router: AgentMessageRouter;

  constructor(region: string = 'us-east-1') {
    this.queueManager = new QueueManager(region);
    this.processor = new MessageProcessor();
    this.eventBus = new AgentEventBus(region);
    this.router = new AgentMessageRouter();
  }

  async initialize(): Promise<void> {
    // Setup default message handlers
    this.processor.registerHandler('agent-task', {
      handle: async (message) => {
        await this.eventBus.publishAgentStart(message.agentId, message.agentType);
      }
    });

    this.processor.registerHandler('notification', {
      handle: async (message) => {
        console.log('Notification:', message.content);
      }
    });
  }

  async sendMessage(type: string, data: any, priority: string = 'normal'): Promise<void> {
    const message = { type, data, priority, timestamp: new Date() };
    const destinations = this.router.route(message);
    
    for (const destination of destinations) {
      await this.queueManager.sendMessage(destination, message);
    }
  }

  async startProcessing(): Promise<void> {
    await this.processor.startProcessing(this.queueManager, 'agent-tasks');
  }

  stop(): void {
    this.processor.stop();
  }
}