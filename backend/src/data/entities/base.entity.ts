/**
 * Base Entity for T-Developer Data Layer
 * Provides common functionality and validation for all entities
 */

import { BaseEntity as SchemaEntity, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';
import { ValidationError } from '../validation/validator';

export abstract class BaseEntity {
  public PK: string = '';
  public SK: string = '';
  public EntityType: string = '';
  public EntityId: string = '';
  public Status: EntityStatus = EntityStatus.ACTIVE;
  public CreatedAt: string = '';
  public UpdatedAt: string = '';
  public CreatedBy?: string;
  public UpdatedBy?: string;
  public Version?: number;
  public Priority?: number;
  public TTL?: number;
  public Data: string = '';
  public Metadata?: string;
  
  // GSI attributes
  public GSI1PK?: string;
  public GSI1SK?: string;
  public GSI2PK?: string;
  public GSI2SK?: string;
  public GSI3PK?: string;

  constructor(data?: Partial<BaseEntity>) {
    if (data) {
      Object.assign(this, data);
    }
    
    // Set timestamps if not provided
    const now = new Date().toISOString();
    if (!this.CreatedAt) {
      this.CreatedAt = now;
    }
    this.UpdatedAt = now;
    
    // Initialize version
    if (this.Version === undefined) {
      this.Version = 1;
    }
  }

  /**
   * Abstract method to build composite keys
   * Each entity must implement this to define its key structure
   */
  protected abstract buildKeys(): void;

  /**
   * Abstract method to validate entity data
   * Each entity must implement its own validation rules
   */
  protected abstract validate(): ValidationError[];

  /**
   * Abstract method to serialize entity-specific data
   * Each entity must implement how to serialize its data to JSON
   */
  protected abstract serializeData(): string;

  /**
   * Abstract method to deserialize entity-specific data
   * Each entity must implement how to deserialize its data from JSON
   */
  protected abstract deserializeData(data: string): void;

  /**
   * Initialize the entity with proper keys and validation
   */
  public initialize(): void {
    this.buildKeys();
    const errors = this.validate();
    
    if (errors.length > 0) {
      throw new ValidationError(`Entity validation failed: ${errors.map(e => e.message).join(', ')}`);
    }

    this.Data = this.serializeData();
    this.UpdatedAt = new Date().toISOString();
  }

  /**
   * Update entity data
   */
  public update(updates: Partial<BaseEntity>, userId?: string): void {
    Object.assign(this, updates);
    
    // Update metadata
    this.UpdatedAt = new Date().toISOString();
    if (userId) {
      this.UpdatedBy = userId;
    }
    
    // Increment version
    this.Version = (this.Version || 0) + 1;
    
    // Re-validate and serialize
    this.initialize();
  }

  /**
   * Set TTL for automatic deletion
   */
  public setTTL(daysFromNow: number): void {
    const ttlDate = new Date();
    ttlDate.setDate(ttlDate.getDate() + daysFromNow);
    this.TTL = Math.floor(ttlDate.getTime() / 1000);
  }

  /**
   * Archive the entity (soft delete)
   */
  public archive(userId?: string): void {
    this.Status = EntityStatus.ARCHIVED;
    this.UpdatedAt = new Date().toISOString();
    if (userId) {
      this.UpdatedBy = userId;
    }
    this.Version = (this.Version || 0) + 1;
  }

  /**
   * Activate the entity
   */
  public activate(userId?: string): void {
    this.Status = EntityStatus.ACTIVE;
    this.UpdatedAt = new Date().toISOString();
    if (userId) {
      this.UpdatedBy = userId;
    }
    this.Version = (this.Version || 0) + 1;
  }

  /**
   * Convert entity to DynamoDB item format
   */
  public toDynamoDBItem(): SchemaEntity {
    return {
      PK: this.PK,
      SK: this.SK,
      EntityType: this.EntityType,
      EntityId: this.EntityId,
      Status: this.Status,
      CreatedAt: this.CreatedAt,
      UpdatedAt: this.UpdatedAt,
      CreatedBy: this.CreatedBy,
      UpdatedBy: this.UpdatedBy,
      Version: this.Version,
      Priority: this.Priority,
      TTL: this.TTL,
      Data: this.Data,
      Metadata: this.Metadata,
      GSI1PK: this.GSI1PK,
      GSI1SK: this.GSI1SK,
      GSI2PK: this.GSI2PK,
      GSI2SK: this.GSI2SK,
      GSI3PK: this.GSI3PK
    };
  }

  /**
   * Create entity from DynamoDB item
   */
  public static fromDynamoDBItem<T extends BaseEntity>(
    item: SchemaEntity,
    entityClass: new () => T
  ): T {
    const entity = new entityClass();
    
    // Copy all properties from item
    Object.assign(entity, item);
    
    // Deserialize data if present
    if (item.Data) {
      entity.deserializeData(item.Data);
    }
    
    return entity;
  }

  /**
   * Clone the entity
   */
  public clone(): this {
    const Constructor = this.constructor as new () => this;
    const cloned = new Constructor();
    
    // Copy all properties
    Object.assign(cloned, this);
    
    // Reset keys and timestamps for new entity
    cloned.CreatedAt = new Date().toISOString();
    cloned.UpdatedAt = cloned.CreatedAt;
    cloned.Version = 1;
    
    return cloned;
  }

  /**
   * Get entity age in milliseconds
   */
  public getAge(): number {
    return new Date().getTime() - new Date(this.CreatedAt).getTime();
  }

  /**
   * Get time since last update in milliseconds
   */
  public getTimeSinceUpdate(): number {
    return new Date().getTime() - new Date(this.UpdatedAt).getTime();
  }

  /**
   * Check if entity is active
   */
  public isActive(): boolean {
    return this.Status === EntityStatus.ACTIVE;
  }

  /**
   * Check if entity is archived
   */
  public isArchived(): boolean {
    return this.Status === EntityStatus.ARCHIVED;
  }

  /**
   * Check if entity is expired (based on TTL)
   */
  public isExpired(): boolean {
    if (!this.TTL) return false;
    return Date.now() / 1000 > this.TTL;
  }

  /**
   * Get entity metadata as object
   */
  public getMetadata(): Record<string, any> {
    if (!this.Metadata) return {};
    try {
      return JSON.parse(this.Metadata);
    } catch {
      return {};
    }
  }

  /**
   * Set entity metadata
   */
  public setMetadata(metadata: Record<string, any>): void {
    this.Metadata = JSON.stringify(metadata);
    this.UpdatedAt = new Date().toISOString();
  }

  /**
   * Add metadata field
   */
  public addMetadata(key: string, value: any): void {
    const metadata = this.getMetadata();
    metadata[key] = value;
    this.setMetadata(metadata);
  }

  /**
   * Remove metadata field
   */
  public removeMetadata(key: string): void {
    const metadata = this.getMetadata();
    delete metadata[key];
    this.setMetadata(metadata);
  }
}

/**
 * Entity event types
 */
export enum EntityEventType {
  CREATED = 'CREATED',
  UPDATED = 'UPDATED',
  DELETED = 'DELETED',
  ARCHIVED = 'ARCHIVED',
  ACTIVATED = 'ACTIVATED',
  TTL_SET = 'TTL_SET',
  VALIDATED = 'VALIDATED'
}

/**
 * Entity event interface
 */
export interface EntityEvent {
  eventType: EntityEventType;
  entityId: string;
  entityType: string;
  timestamp: string;
  userId?: string;
  data?: any;
  metadata?: Record<string, any>;
}

/**
 * Entity lifecycle hooks
 */
export interface EntityHooks {
  beforeCreate?(entity: BaseEntity): Promise<void> | void;
  afterCreate?(entity: BaseEntity): Promise<void> | void;
  beforeUpdate?(entity: BaseEntity, updates: Partial<BaseEntity>): Promise<void> | void;
  afterUpdate?(entity: BaseEntity): Promise<void> | void;
  beforeDelete?(entity: BaseEntity): Promise<void> | void;
  afterDelete?(entity: BaseEntity): Promise<void> | void;
  beforeValidate?(entity: BaseEntity): Promise<void> | void;
  afterValidate?(entity: BaseEntity, errors: ValidationError[]): Promise<void> | void;
}

/**
 * Abstract entity factory
 */
export abstract class EntityFactory<T extends BaseEntity> {
  protected hooks: EntityHooks = {};

  constructor(hooks?: EntityHooks) {
    if (hooks) {
      this.hooks = hooks;
    }
  }

  /**
   * Create new entity instance
   */
  public abstract create(data: any): Promise<T>;

  /**
   * Create entity from DynamoDB item
   */
  public abstract fromItem(item: SchemaEntity): T;

  /**
   * Validate entity data
   */
  protected async executeHook(
    hookName: keyof EntityHooks,
    entity: BaseEntity,
    ...args: any[]
  ): Promise<void> {
    const hook = this.hooks[hookName];
    if (hook) {
      await hook(entity, ...args);
    }
  }
}