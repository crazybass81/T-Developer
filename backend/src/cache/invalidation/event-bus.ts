import { EventEmitter } from 'events';
import { InvalidationEngine, InvalidationEvent } from './invalidation-engine';

export interface CacheEvent {
  type: 'create' | 'update' | 'delete';
  entity: string;
  id: string;
  data?: any;
  userId?: string;
}

export class CacheEventBus extends EventEmitter {
  private invalidationEngine: InvalidationEngine;

  constructor(invalidationEngine: InvalidationEngine) {
    super();
    this.invalidationEngine = invalidationEngine;
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    // User events
    this.on('user:created', this.handleUserCreated.bind(this));
    this.on('user:updated', this.handleUserUpdated.bind(this));
    this.on('user:deleted', this.handleUserDeleted.bind(this));

    // Project events
    this.on('project:created', this.handleProjectCreated.bind(this));
    this.on('project:updated', this.handleProjectUpdated.bind(this));
    this.on('project:deleted', this.handleProjectDeleted.bind(this));

    // Agent events
    this.on('agent:created', this.handleAgentCreated.bind(this));
    this.on('agent:updated', this.handleAgentUpdated.bind(this));
    this.on('agent:executed', this.handleAgentExecuted.bind(this));

    // Session events
    this.on('session:created', this.handleSessionCreated.bind(this));
    this.on('session:expired', this.handleSessionExpired.bind(this));
  }

  async publishEvent(event: CacheEvent): Promise<void> {
    const eventName = `${event.entity}:${event.type}`;
    this.emit(eventName, event);
  }

  private async handleUserCreated(event: CacheEvent): Promise<void> {
    // No invalidation needed for creation
  }

  private async handleUserUpdated(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'user:update',
      entityId: event.id,
      data: event.data,
      timestamp: new Date()
    });
  }

  private async handleUserDeleted(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'user:delete',
      entityId: event.id,
      timestamp: new Date()
    });
  }

  private async handleProjectCreated(event: CacheEvent): Promise<void> {
    // Invalidate user's project list
    if (event.userId) {
      await this.invalidationEngine.invalidate({
        type: 'user:projects_changed',
        entityId: event.userId,
        timestamp: new Date()
      });
    }
  }

  private async handleProjectUpdated(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'project:update',
      entityId: event.id,
      data: event.data,
      timestamp: new Date()
    });

    // Cascade invalidation for related data
    await this.invalidationEngine.cascadeInvalidation('project', event.id, event.data);
  }

  private async handleProjectDeleted(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'project:delete',
      entityId: event.id,
      timestamp: new Date()
    });
  }

  private async handleAgentCreated(event: CacheEvent): Promise<void> {
    // Invalidate project's agent list
    if (event.data?.projectId) {
      await this.invalidationEngine.invalidate({
        type: 'project:agents_changed',
        entityId: event.data.projectId,
        timestamp: new Date()
      });
    }
  }

  private async handleAgentUpdated(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'agent:update',
      entityId: event.id,
      data: event.data,
      timestamp: new Date()
    });
  }

  private async handleAgentExecuted(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'agent:execute',
      entityId: event.id,
      data: event.data,
      timestamp: new Date()
    });
  }

  private async handleSessionCreated(event: CacheEvent): Promise<void> {
    // No invalidation needed for session creation
  }

  private async handleSessionExpired(event: CacheEvent): Promise<void> {
    await this.invalidationEngine.invalidate({
      type: 'session:expire',
      entityId: event.id,
      timestamp: new Date()
    });
  }
}