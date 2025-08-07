/**
 * Unit of Work Pattern Implementation
 * Manages transactions and coordinates changes across multiple repositories
 */

import { BaseEntity } from '../entities/base.entity';
import { TransactionManager, TransactionItem, TransactionResult } from '../transactions/transaction-manager';
import { RepositoryFactory } from '../repositories/repository-factory';
import { SingleTableClient } from '../dynamodb/single-table';
import { v4 as uuidv4 } from 'uuid';

export enum ChangeType {
  INSERT = 'INSERT',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE'
}

export interface Change {
  id: string;
  type: ChangeType;
  entity: BaseEntity;
  originalEntity?: BaseEntity;
  repository: string;
  timestamp: number;
}

export interface UnitOfWorkOptions {
  enableLogging?: boolean;
  maxChanges?: number;
  autoCommit?: boolean;
  validateBeforeCommit?: boolean;
}

export interface UnitOfWorkResult {
  success: boolean;
  transactionId?: string;
  changeCount: number;
  executionTime: number;
  errors?: string[];
}

export class UnitOfWork {
  private changes: Map<string, Change> = new Map();
  private transactionManager: TransactionManager;
  private repositoryFactory: RepositoryFactory;
  private options: Required<UnitOfWorkOptions>;
  private isCommitted: boolean = false;
  private isRolledBack: boolean = false;
  private workId: string;

  constructor(
    repositoryFactory?: RepositoryFactory,
    options: UnitOfWorkOptions = {}
  ) {
    this.repositoryFactory = repositoryFactory || RepositoryFactory.getInstance();
    this.transactionManager = new TransactionManager(this.repositoryFactory.getClient());
    this.workId = uuidv4();
    
    this.options = {
      enableLogging: true,
      maxChanges: 100,
      autoCommit: false,
      validateBeforeCommit: true,
      ...options
    };

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Created`);
    }
  }

  /**
   * Register entity insertion
   */
  public registerNew(entity: BaseEntity, repository: string = 'default'): void {
    this.ensureNotFinished();
    this.ensureCapacity();

    const changeId = uuidv4();
    const change: Change = {
      id: changeId,
      type: ChangeType.INSERT,
      entity: entity.clone(),
      repository,
      timestamp: Date.now()
    };

    this.changes.set(changeId, change);

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Registered INSERT for ${entity.EntityType}#${entity.EntityId}`);
    }
  }

  /**
   * Register entity update
   */
  public registerDirty(
    entity: BaseEntity,
    originalEntity: BaseEntity,
    repository: string = 'default'
  ): void {
    this.ensureNotFinished();
    this.ensureCapacity();

    const changeId = uuidv4();
    const change: Change = {
      id: changeId,
      type: ChangeType.UPDATE,
      entity: entity.clone(),
      originalEntity: originalEntity.clone(),
      repository,
      timestamp: Date.now()
    };

    this.changes.set(changeId, change);

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Registered UPDATE for ${entity.EntityType}#${entity.EntityId}`);
    }
  }

  /**
   * Register entity deletion
   */
  public registerDeleted(entity: BaseEntity, repository: string = 'default'): void {
    this.ensureNotFinished();
    this.ensureCapacity();

    const changeId = uuidv4();
    const change: Change = {
      id: changeId,
      type: ChangeType.DELETE,
      entity: entity.clone(),
      repository,
      timestamp: Date.now()
    };

    this.changes.set(changeId, change);

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Registered DELETE for ${entity.EntityType}#${entity.EntityId}`);
    }
  }

  /**
   * Register entity clean (remove from tracking without persistence)
   */
  public registerClean(entityId: string): void {
    // Remove any pending changes for this entity
    const toRemove: string[] = [];
    for (const [changeId, change] of this.changes) {
      if (change.entity.EntityId === entityId) {
        toRemove.push(changeId);
      }
    }

    toRemove.forEach(id => this.changes.delete(id));

    if (this.options.enableLogging && toRemove.length > 0) {
      console.log(`[UnitOfWork ${this.workId}] Cleaned ${toRemove.length} changes for entity ${entityId}`);
    }
  }

  /**
   * Get all pending changes
   */
  public getChanges(): Change[] {
    return Array.from(this.changes.values()).sort((a, b) => a.timestamp - b.timestamp);
  }

  /**
   * Get changes by type
   */
  public getChangesByType(type: ChangeType): Change[] {
    return this.getChanges().filter(change => change.type === type);
  }

  /**
   * Get changes by entity type
   */
  public getChangesByEntityType(entityType: string): Change[] {
    return this.getChanges().filter(change => change.entity.EntityType === entityType);
  }

  /**
   * Check if entity is tracked
   */
  public isTracked(entityId: string): boolean {
    return this.getChanges().some(change => change.entity.EntityId === entityId);
  }

  /**
   * Get change count
   */
  public getChangeCount(): number {
    return this.changes.size;
  }

  /**
   * Validate all changes before commit
   */
  public async validate(): Promise<string[]> {
    const errors: string[] = [];

    for (const change of this.changes.values()) {
      try {
        // Validate entity
        const entityErrors = await change.entity['validate']();
        if (entityErrors.length > 0) {
          errors.push(
            ...entityErrors.map(e => 
              `${change.entity.EntityType}#${change.entity.EntityId}: ${e.message}`
            )
          );
        }

        // Check for conflicts (e.g., entity was modified since original read)
        if (change.type === ChangeType.UPDATE && change.originalEntity) {
          const conflicts = await this.detectConflicts(change);
          errors.push(...conflicts);
        }

      } catch (error) {
        errors.push(`Validation error for ${change.entity.EntityType}#${change.entity.EntityId}: ${error}`);
      }
    }

    return errors;
  }

  /**
   * Commit all changes as a single transaction
   */
  public async commit(): Promise<UnitOfWorkResult> {
    this.ensureNotFinished();
    const startTime = Date.now();
    const changeCount = this.changes.size;

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Committing ${changeCount} changes`);
    }

    try {
      if (changeCount === 0) {
        this.isCommitted = true;
        return {
          success: true,
          changeCount: 0,
          executionTime: Date.now() - startTime
        };
      }

      // Validate before commit
      if (this.options.validateBeforeCommit) {
        const validationErrors = await this.validate();
        if (validationErrors.length > 0) {
          return {
            success: false,
            changeCount,
            executionTime: Date.now() - startTime,
            errors: validationErrors
          };
        }
      }

      // Convert changes to transaction items
      const transactionItems = await this.convertChangesToTransactionItems();

      // Execute transaction
      const result = await this.transactionManager.execute(transactionItems);

      if (result.success) {
        this.isCommitted = true;
        this.changes.clear();

        if (this.options.enableLogging) {
          console.log(
            `[UnitOfWork ${this.workId}] Committed successfully in ${result.executionTime}ms`
          );
        }

        // Clear cache for affected entities
        await this.invalidateCache();

        return {
          success: true,
          transactionId: result.transactionId,
          changeCount,
          executionTime: Date.now() - startTime
        };
      } else {
        return {
          success: false,
          changeCount,
          executionTime: Date.now() - startTime,
          errors: [result.error || 'Transaction failed']
        };
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      if (this.options.enableLogging) {
        console.error(`[UnitOfWork ${this.workId}] Commit failed: ${errorMessage}`);
      }

      return {
        success: false,
        changeCount,
        executionTime: Date.now() - startTime,
        errors: [errorMessage]
      };
    }
  }

  /**
   * Rollback all changes
   */
  public async rollback(): Promise<void> {
    this.ensureNotFinished();

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Rolling back ${this.changes.size} changes`);
    }

    this.changes.clear();
    this.isRolledBack = true;
  }

  /**
   * Reset the unit of work
   */
  public reset(): void {
    this.changes.clear();
    this.isCommitted = false;
    this.isRolledBack = false;

    if (this.options.enableLogging) {
      console.log(`[UnitOfWork ${this.workId}] Reset`);
    }
  }

  /**
   * Check if work is finished
   */
  public isFinished(): boolean {
    return this.isCommitted || this.isRolledBack;
  }

  /**
   * Get work ID
   */
  public getId(): string {
    return this.workId;
  }

  /**
   * Clone the unit of work (for nested transactions)
   */
  public clone(): UnitOfWork {
    const cloned = new UnitOfWork(this.repositoryFactory, this.options);
    
    // Copy changes
    for (const [id, change] of this.changes) {
      cloned.changes.set(id, { ...change });
    }

    return cloned;
  }

  /**
   * Private helper methods
   */
  private ensureNotFinished(): void {
    if (this.isFinished()) {
      throw new Error(`UnitOfWork ${this.workId} is already finished`);
    }
  }

  private ensureCapacity(): void {
    if (this.changes.size >= this.options.maxChanges) {
      throw new Error(`UnitOfWork ${this.workId} has reached maximum capacity (${this.options.maxChanges})`);
    }
  }

  private async convertChangesToTransactionItems(): Promise<TransactionItem[]> {
    const items: TransactionItem[] = [];

    for (const change of this.changes.values()) {
      switch (change.type) {
        case ChangeType.INSERT:
          items.push({
            type: 'put',
            entity: change.entity
          });
          break;

        case ChangeType.UPDATE:
          // Convert entity updates to DynamoDB update format
          const updates = this.getEntityUpdates(change.entity, change.originalEntity);
          if (Object.keys(updates).length > 0) {
            items.push({
              type: 'update',
              key: {
                pk: change.entity.PK,
                sk: change.entity.SK
              },
              updates,
              condition: 'attribute_exists(PK)'
            });
          }
          break;

        case ChangeType.DELETE:
          items.push({
            type: 'delete',
            key: {
              pk: change.entity.PK,
              sk: change.entity.SK
            },
            condition: 'attribute_exists(PK)'
          });
          break;
      }
    }

    return items;
  }

  private getEntityUpdates(current: BaseEntity, original?: BaseEntity): Record<string, any> {
    const updates: Record<string, any> = {};

    if (!original) {
      // If no original, return all current properties (except keys)
      const currentData = current.toDynamoDBItem();
      for (const [key, value] of Object.entries(currentData)) {
        if (key !== 'PK' && key !== 'SK') {
          updates[key] = value;
        }
      }
      return updates;
    }

    // Compare current with original to find changes
    const currentData = current.toDynamoDBItem();
    const originalData = original.toDynamoDBItem();

    for (const [key, value] of Object.entries(currentData)) {
      if (key === 'PK' || key === 'SK') continue;
      
      if (JSON.stringify(value) !== JSON.stringify(originalData[key])) {
        updates[key] = value;
      }
    }

    return updates;
  }

  private async detectConflicts(change: Change): Promise<string[]> {
    const conflicts: string[] = [];

    try {
      // Check if entity was modified since we read it
      // This is a simplified conflict detection
      const current = await this.repositoryFactory
        .getClient()
        .getItem(change.entity.PK, change.entity.SK);

      if (current && change.originalEntity) {
        if (current.Version !== change.originalEntity.Version) {
          conflicts.push(
            `Concurrent modification detected for ${change.entity.EntityType}#${change.entity.EntityId}`
          );
        }
      }
    } catch (error) {
      // If we can't check for conflicts, log but don't fail
      console.warn(`Could not check for conflicts: ${error}`);
    }

    return conflicts;
  }

  private async invalidateCache(): Promise<void> {
    // Invalidate cache entries for all changed entities
    const cacheKeys = this.getChanges().map(change => 
      `${change.entity.EntityType}:${change.entity.EntityId}`
    );

    // This would integrate with your cache manager
    // For now, we'll just log the cache invalidation
    if (this.options.enableLogging && cacheKeys.length > 0) {
      console.log(`[UnitOfWork ${this.workId}] Invalidating cache for: ${cacheKeys.join(', ')}`);
    }
  }
}

/**
 * Unit of Work Factory for easy creation and management
 */
export class UnitOfWorkFactory {
  private static instances: Map<string, UnitOfWork> = new Map();

  /**
   * Create a new unit of work
   */
  public static create(
    options?: UnitOfWorkOptions,
    repositoryFactory?: RepositoryFactory
  ): UnitOfWork {
    const uow = new UnitOfWork(repositoryFactory, options);
    this.instances.set(uow.getId(), uow);
    return uow;
  }

  /**
   * Get unit of work by ID
   */
  public static get(id: string): UnitOfWork | undefined {
    return this.instances.get(id);
  }

  /**
   * Remove finished unit of work
   */
  public static cleanup(id: string): boolean {
    const uow = this.instances.get(id);
    if (uow && uow.isFinished()) {
      return this.instances.delete(id);
    }
    return false;
  }

  /**
   * Clean up all finished units of work
   */
  public static cleanupAll(): number {
    let cleaned = 0;
    for (const [id, uow] of this.instances) {
      if (uow.isFinished()) {
        this.instances.delete(id);
        cleaned++;
      }
    }
    return cleaned;
  }

  /**
   * Get all active units of work
   */
  public static getActive(): UnitOfWork[] {
    return Array.from(this.instances.values()).filter(uow => !uow.isFinished());
  }
}