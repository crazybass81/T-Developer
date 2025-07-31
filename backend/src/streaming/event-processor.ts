import { EventEmitter } from 'events';
import { StreamEvent } from './event-stream';

export interface ProcessorConfig {
  batchSize: number;
  maxConcurrency: number;
  retryAttempts: number;
  deadLetterQueue?: string;
}

export abstract class EventProcessor extends EventEmitter {
  protected config: ProcessorConfig;

  constructor(config: ProcessorConfig) {
    super();
    this.config = config;
  }

  abstract process(event: StreamEvent): Promise<void>;

  async processBatch(events: StreamEvent[]): Promise<void> {
    const chunks = this.chunk(events, this.config.maxConcurrency);
    
    for (const chunk of chunks) {
      await Promise.all(chunk.map(event => this.processWithRetry(event)));
    }
  }

  private async processWithRetry(event: StreamEvent): Promise<void> {
    let attempts = 0;
    
    while (attempts < this.config.retryAttempts) {
      try {
        await this.process(event);
        this.emit('processed', event);
        return;
      } catch (error) {
        attempts++;
        if (attempts >= this.config.retryAttempts) {
          this.emit('failed', event, error);
          if (this.config.deadLetterQueue) {
            await this.sendToDeadLetter(event, error);
          }
        } else {
          await this.delay(Math.pow(2, attempts) * 1000);
        }
      }
    }
  }

  private chunk<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async sendToDeadLetter(event: StreamEvent, error: any): Promise<void> {
    // Implementation would send to SQS DLQ
    console.error('Event failed processing:', event.id, error);
  }
}

export class ProjectEventProcessor extends EventProcessor {
  async process(event: StreamEvent): Promise<void> {
    switch (event.type) {
      case 'INSERT':
        await this.handleProjectCreated(event);
        break;
      case 'MODIFY':
        await this.handleProjectUpdated(event);
        break;
      case 'REMOVE':
        await this.handleProjectDeleted(event);
        break;
    }
  }

  private async handleProjectCreated(event: StreamEvent): Promise<void> {
    // Initialize project resources
    this.emit('project:created', event.data.newImage);
  }

  private async handleProjectUpdated(event: StreamEvent): Promise<void> {
    // Update related resources
    this.emit('project:updated', {
      old: event.data.oldImage,
      new: event.data.newImage
    });
  }

  private async handleProjectDeleted(event: StreamEvent): Promise<void> {
    // Cleanup project resources
    this.emit('project:deleted', event.data.oldImage);
  }
}

export class AgentEventProcessor extends EventProcessor {
  async process(event: StreamEvent): Promise<void> {
    switch (event.type) {
      case 'INSERT':
        await this.handleAgentCreated(event);
        break;
      case 'MODIFY':
        await this.handleAgentStatusChanged(event);
        break;
    }
  }

  private async handleAgentCreated(event: StreamEvent): Promise<void> {
    this.emit('agent:created', event.data.newImage);
  }

  private async handleAgentStatusChanged(event: StreamEvent): Promise<void> {
    const oldStatus = event.data.oldImage?.Status?.S;
    const newStatus = event.data.newImage?.Status?.S;
    
    if (oldStatus !== newStatus) {
      this.emit('agent:status-changed', {
        agentId: event.data.newImage.AgentId.S,
        oldStatus,
        newStatus
      });
    }
  }
}

export class EventProcessorManager {
  private processors: Map<string, EventProcessor> = new Map();

  register(name: string, processor: EventProcessor): void {
    this.processors.set(name, processor);
  }

  async processEvent(event: StreamEvent): Promise<void> {
    const processor = this.getProcessorForEvent(event);
    if (processor) {
      await processor.process(event);
    }
  }

  private getProcessorForEvent(event: StreamEvent): EventProcessor | undefined {
    if (event.metadata?.tableName?.includes('Project')) {
      return this.processors.get('project');
    }
    if (event.metadata?.tableName?.includes('Agent')) {
      return this.processors.get('agent');
    }
    return undefined;
  }
}