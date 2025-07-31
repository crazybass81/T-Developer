import { CDCProcessor, ChangeEvent } from './change-capture';
import { ChangeLogger, ChangeAggregator } from './change-log';
import { DataReplicator, ReplicationTarget, ReplicationRule } from './replication';
import { EventEmitter } from 'events';

export interface CDCServiceConfig {
  batchSize: number;
  maxRetries: number;
  enableLogging: boolean;
  enableReplication: boolean;
  enableAggregation: boolean;
}

export class CDCService extends EventEmitter {
  private processor: CDCProcessor;
  private logger?: ChangeLogger;
  private replicator?: DataReplicator;
  private aggregator?: ChangeAggregator;

  constructor(private config: CDCServiceConfig) {
    super();
    
    this.processor = new CDCProcessor({
      batchSize: config.batchSize,
      maxRetries: config.maxRetries
    });

    if (config.enableLogging) {
      this.logger = new ChangeLogger();
    }

    if (config.enableReplication) {
      this.replicator = new DataReplicator();
      this.setupReplicationTargets();
    }

    if (config.enableAggregation) {
      this.aggregator = new ChangeAggregator();
    }

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.processor.registerHandler('INSERT', (event: ChangeEvent) => {
      this.handleInsert(event);
    });

    this.processor.registerHandler('MODIFY', (event: ChangeEvent) => {
      this.handleModify(event);
    });

    this.processor.registerHandler('REMOVE', (event: ChangeEvent) => {
      this.handleRemove(event);
    });
  }

  private async handleInsert(event: ChangeEvent): Promise<void> {
    await this.processChange(event);
    this.emit('entity:created', {
      tableName: event.tableName,
      entityId: this.extractEntityId(event.keys),
      data: event.newImage
    });
  }

  private async handleModify(event: ChangeEvent): Promise<void> {
    await this.processChange(event);
    this.emit('entity:updated', {
      tableName: event.tableName,
      entityId: this.extractEntityId(event.keys),
      oldData: event.oldImage,
      newData: event.newImage
    });
  }

  private async handleRemove(event: ChangeEvent): Promise<void> {
    await this.processChange(event);
    this.emit('entity:deleted', {
      tableName: event.tableName,
      entityId: this.extractEntityId(event.keys),
      data: event.oldImage
    });
  }

  private async processChange(event: ChangeEvent): Promise<void> {
    // Log change
    if (this.logger) {
      const logEntry = this.logger.logChange(event);
      
      if (this.aggregator) {
        this.aggregator.processChange(logEntry);
      }
    }

    // Replicate change
    if (this.replicator) {
      await this.replicator.replicate(event);
    }
  }

  private setupReplicationTargets(): void {
    if (!this.replicator) return;

    // Cache replication
    this.replicator.addTarget({
      id: 'redis-cache',
      type: 'cache',
      config: { host: process.env.REDIS_HOST },
      enabled: true
    });

    // Search replication
    this.replicator.addTarget({
      id: 'elasticsearch',
      type: 'search',
      config: { endpoint: process.env.ELASTICSEARCH_ENDPOINT },
      enabled: false
    });

    // Analytics replication
    this.replicator.addTarget({
      id: 'analytics',
      type: 'analytics',
      config: { stream: process.env.ANALYTICS_STREAM },
      enabled: true
    });

    // Setup replication rules
    this.setupReplicationRules();
  }

  private setupReplicationRules(): void {
    if (!this.replicator) return;

    // Replicate user changes to cache
    this.replicator.addRule({
      sourceTable: 'T-Developer-Main',
      targetId: 'redis-cache',
      filterFn: (event) => event.keys.PK?.S?.startsWith('USER#') || false
    });

    // Replicate project changes to analytics
    this.replicator.addRule({
      sourceTable: 'T-Developer-Main',
      targetId: 'analytics',
      filterFn: (event) => event.keys.PK?.S?.startsWith('PROJECT#') || false,
      transformFn: (data) => ({
        projectId: data.ProjectId?.S,
        status: data.Status?.S,
        timestamp: new Date().toISOString()
      })
    });
  }

  async processStreamEvent(streamEvent: any): Promise<void> {
    await this.processor.processStream(streamEvent);
  }

  getChangeHistory(entityId: string, limit = 100): any[] {
    return this.logger?.getChangesForEntity(entityId, limit) || [];
  }

  getAggregatedMetrics(): any {
    return this.aggregator?.getAggregates() || {};
  }

  addReplicationTarget(target: ReplicationTarget): void {
    this.replicator?.addTarget(target);
  }

  addReplicationRule(rule: ReplicationRule): void {
    this.replicator?.addRule(rule);
  }

  private extractEntityId(keys: Record<string, any>): string {
    return keys.PK?.S || keys.id?.S || 'unknown';
  }
}

export class CDCManager {
  private services: Map<string, CDCService> = new Map();

  createService(name: string, config: CDCServiceConfig): CDCService {
    const service = new CDCService(config);
    this.services.set(name, service);
    return service;
  }

  getService(name: string): CDCService | undefined {
    return this.services.get(name);
  }

  async processStreamEvent(serviceName: string, streamEvent: any): Promise<void> {
    const service = this.services.get(serviceName);
    if (service) {
      await service.processStreamEvent(streamEvent);
    }
  }

  getAllServices(): CDCService[] {
    return Array.from(this.services.values());
  }
}