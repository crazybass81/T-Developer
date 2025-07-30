// Task 1.14.3: 이벤트 버스 구현
import { EventBridgeClient, PutEventsCommand } from '@aws-sdk/client-eventbridge';

interface Event {
  source: string;
  type: string;
  data: any;
  timestamp?: Date;
}

export class EventBus {
  private eventBridge: EventBridgeClient;
  private eventBusName: string;

  constructor(region: string = 'us-east-1', eventBusName: string = 'default') {
    this.eventBridge = new EventBridgeClient({ region });
    this.eventBusName = eventBusName;
  }

  async publish(event: Event): Promise<void> {
    const eventEntry = {
      Source: event.source,
      DetailType: event.type,
      Detail: JSON.stringify(event.data),
      Time: event.timestamp || new Date(),
      EventBusName: this.eventBusName
    };

    await this.eventBridge.send(new PutEventsCommand({
      Entries: [eventEntry]
    }));
  }

  async publishBatch(events: Event[]): Promise<void> {
    const entries = events.map(event => ({
      Source: event.source,
      DetailType: event.type,
      Detail: JSON.stringify(event.data),
      Time: event.timestamp || new Date(),
      EventBusName: this.eventBusName
    }));

    // EventBridge supports max 10 events per batch
    for (let i = 0; i < entries.length; i += 10) {
      const batch = entries.slice(i, i + 10);
      await this.eventBridge.send(new PutEventsCommand({
        Entries: batch
      }));
    }
  }
}

// Agent-specific events
export class AgentEventBus extends EventBus {
  async publishAgentStart(agentId: string, agentType: string): Promise<void> {
    await this.publish({
      source: 't-developer.agents',
      type: 'AgentStarted',
      data: { agentId, agentType, timestamp: new Date() }
    });
  }

  async publishAgentComplete(agentId: string, result: any): Promise<void> {
    await this.publish({
      source: 't-developer.agents',
      type: 'AgentCompleted',
      data: { agentId, result, timestamp: new Date() }
    });
  }

  async publishAgentError(agentId: string, error: string): Promise<void> {
    await this.publish({
      source: 't-developer.agents',
      type: 'AgentError',
      data: { agentId, error, timestamp: new Date() }
    });
  }
}