/**
 * Base Model for T-Developer Data Layer
 * Provides ORM-like functionality and data mapping capabilities
 */

import { BaseEntity } from '../entities/base.entity';
import { EntityStatus } from '../schemas/table-schema';
import { SingleTableClient } from '../dynamodb/single-table';
import { ValidationError } from '../validation/validator';

export interface QueryOptions {
  limit?: number;
  lastEvaluatedKey?: any;
  scanIndexForward?: boolean;
  consistentRead?: boolean;
}

export interface QueryResult<T> {
  items: T[];
  lastEvaluatedKey?: any;
  count: number;
  scannedCount?: number;
}

export interface ModelHooks<T> {
  beforeCreate?(model: T): Promise<void> | void;
  afterCreate?(model: T): Promise<void> | void;
  beforeUpdate?(model: T, updates: Partial<T>): Promise<void> | void;
  afterUpdate?(model: T): Promise<void> | void;
  beforeDelete?(model: T): Promise<void> | void;
  afterDelete?(model: T): Promise<void> | void;
  beforeValidate?(model: T): Promise<void> | void;
  afterValidate?(model: T, errors: ValidationError[]): Promise<void> | void;
}

/**
 * Abstract base model providing ORM-like functionality
 */
export abstract class BaseModel<T extends BaseEntity, TData = any> {
  protected client: SingleTableClient;
  protected hooks: ModelHooks<T> = {};

  constructor(
    client?: SingleTableClient,
    hooks?: ModelHooks<T>
  ) {
    this.client = client || new SingleTableClient();
    if (hooks) {
      this.hooks = hooks;
    }
  }

  /**
   * Abstract method to create entity instance from data
   */
  protected abstract createEntity(data: TData): T;

  /**
   * Abstract method to get entity type
   */
  protected abstract getEntityType(): string;

  /**
   * Execute lifecycle hooks
   */
  protected async executeHook(
    hookName: keyof ModelHooks<T>,
    entity: T,
    ...args: any[]
  ): Promise<void> {
    const hook = this.hooks[hookName];
    if (hook) {
      await hook(entity, ...args);
    }
  }

  /**
   * Create a new entity
   */
  public async create(data: TData, userId?: string): Promise<T> {
    const entity = this.createEntity(data);
    
    if (userId) {
      entity.CreatedBy = userId;
      entity.UpdatedBy = userId;
    }

    // Execute before hooks
    await this.executeHook('beforeValidate', entity);
    
    // Initialize and validate entity
    entity.initialize();
    
    await this.executeHook('beforeCreate', entity);

    try {
      // Save to database
      await this.client.putItem(entity.toDynamoDBItem());
      
      await this.executeHook('afterCreate', entity);
      
      return entity;
    } catch (error) {
      throw new Error(`Failed to create ${this.getEntityType()}: ${error}`);
    }
  }

  /**
   * Find entity by ID
   */
  public async findById(id: string): Promise<T | null> {
    try {
      const pk = `${this.getEntityType().toUpperCase()}#${id}`;
      const sk = this.getDefaultSortKey();
      
      const item = await this.client.getItem(pk, sk);
      if (!item) return null;
      
      return BaseEntity.fromDynamoDBItem(item, this.getEntityClass());
    } catch (error) {
      throw new Error(`Failed to find ${this.getEntityType()} by ID: ${error}`);
    }
  }

  /**
   * Find multiple entities by IDs
   */
  public async findByIds(ids: string[]): Promise<T[]> {
    if (ids.length === 0) return [];

    try {
      const keys = ids.map(id => ({
        pk: `${this.getEntityType().toUpperCase()}#${id}`,
        sk: this.getDefaultSortKey()
      }));

      const items = await this.client.batchGet(keys);
      return items.map(item => BaseEntity.fromDynamoDBItem(item, this.getEntityClass()));
    } catch (error) {
      throw new Error(`Failed to find ${this.getEntityType()}s by IDs: ${error}`);
    }
  }

  /**
   * Update entity
   */
  public async update(
    id: string,
    updates: Partial<TData>,
    userId?: string
  ): Promise<T | null> {
    const entity = await this.findById(id);
    if (!entity) return null;

    await this.executeHook('beforeUpdate', entity, updates);

    try {
      // Update entity
      entity.update(updates as Partial<BaseEntity>, userId);
      
      // Save to database
      const pk = entity.PK;
      const sk = entity.SK;
      const updatedItem = await this.client.updateItem(pk, sk, updates);
      
      if (updatedItem) {
        const updatedEntity = BaseEntity.fromDynamoDBItem(updatedItem, this.getEntityClass());
        await this.executeHook('afterUpdate', updatedEntity);
        return updatedEntity;
      }
      
      return null;
    } catch (error) {
      throw new Error(`Failed to update ${this.getEntityType()}: ${error}`);
    }
  }

  /**
   * Delete entity
   */
  public async delete(id: string): Promise<boolean> {
    const entity = await this.findById(id);
    if (!entity) return false;

    await this.executeHook('beforeDelete', entity);

    try {
      const pk = entity.PK;
      const sk = entity.SK;
      const success = await this.client.deleteItem(pk, sk);
      
      if (success) {
        await this.executeHook('afterDelete', entity);
      }
      
      return success;
    } catch (error) {
      throw new Error(`Failed to delete ${this.getEntityType()}: ${error}`);
    }
  }

  /**
   * Soft delete (archive) entity
   */
  public async archive(id: string, userId?: string): Promise<T | null> {
    const entity = await this.findById(id);
    if (!entity) return null;

    entity.archive(userId);
    return await this.update(id, { Status: EntityStatus.ARCHIVED } as any, userId);
  }

  /**
   * Find all entities with pagination
   */
  public async findAll(options: QueryOptions = {}): Promise<QueryResult<T>> {
    try {
      const result = await this.client.query({
        indexName: 'GSI5',
        entityType: this.getEntityType().toUpperCase(),
        limit: options.limit,
        lastEvaluatedKey: options.lastEvaluatedKey,
        scanIndexForward: options.scanIndexForward
      });

      const entities = result.items.map(item => 
        BaseEntity.fromDynamoDBItem(item, this.getEntityClass())
      );

      return {
        items: entities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: entities.length
      };
    } catch (error) {
      throw new Error(`Failed to find all ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Find entities by status
   */
  public async findByStatus(
    status: EntityStatus,
    options: QueryOptions = {}
  ): Promise<QueryResult<T>> {
    try {
      const result = await this.client.query({
        indexName: 'GSI4',
        status: status,
        limit: options.limit,
        lastEvaluatedKey: options.lastEvaluatedKey,
        scanIndexForward: options.scanIndexForward
      });

      const entities = result.items.map(item => 
        BaseEntity.fromDynamoDBItem(item, this.getEntityClass())
      );

      return {
        items: entities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: entities.length
      };
    } catch (error) {
      throw new Error(`Failed to find ${this.getEntityType()}s by status: ${error}`);
    }
  }

  /**
   * Find recent entities
   */
  public async findRecent(
    limit: number = 20,
    options: QueryOptions = {}
  ): Promise<QueryResult<T>> {
    try {
      const result = await this.client.query({
        indexName: 'GSI3',
        gsi3pk: `ENTITY#${this.getEntityType().toUpperCase()}`,
        limit,
        lastEvaluatedKey: options.lastEvaluatedKey,
        scanIndexForward: false // Descending order (newest first)
      });

      const entities = result.items.map(item => 
        BaseEntity.fromDynamoDBItem(item, this.getEntityClass())
      );

      return {
        items: entities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: entities.length
      };
    } catch (error) {
      throw new Error(`Failed to find recent ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Count entities by status
   */
  public async countByStatus(status?: EntityStatus): Promise<number> {
    try {
      let result;
      
      if (status) {
        result = await this.client.query({
          indexName: 'GSI4',
          status: status,
          limit: 1000 // Adjust based on expected volume
        });
      } else {
        result = await this.client.query({
          indexName: 'GSI5',
          entityType: this.getEntityType().toUpperCase(),
          limit: 1000
        });
      }

      return result.items.length;
    } catch (error) {
      throw new Error(`Failed to count ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Check if entity exists
   */
  public async exists(id: string): Promise<boolean> {
    const entity = await this.findById(id);
    return entity !== null;
  }

  /**
   * Batch create entities
   */
  public async batchCreate(dataList: TData[], userId?: string): Promise<T[]> {
    const entities = dataList.map(data => {
      const entity = this.createEntity(data);
      if (userId) {
        entity.CreatedBy = userId;
        entity.UpdatedBy = userId;
      }
      entity.initialize();
      return entity;
    });

    try {
      const items = entities.map(entity => entity.toDynamoDBItem());
      await this.client.batchWrite(items, 'put');
      
      // Execute after hooks for each entity
      for (const entity of entities) {
        await this.executeHook('afterCreate', entity);
      }
      
      return entities;
    } catch (error) {
      throw new Error(`Failed to batch create ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Batch delete entities
   */
  public async batchDelete(ids: string[]): Promise<boolean> {
    if (ids.length === 0) return true;

    try {
      // Get entities first for hooks
      const entities = await this.findByIds(ids);
      
      // Execute before hooks
      for (const entity of entities) {
        await this.executeHook('beforeDelete', entity);
      }

      // Create delete items
      const deleteItems = entities.map(entity => ({
        PK: entity.PK,
        SK: entity.SK
      }));

      await this.client.batchWrite(deleteItems as any, 'delete');
      
      // Execute after hooks
      for (const entity of entities) {
        await this.executeHook('afterDelete', entity);
      }

      return true;
    } catch (error) {
      throw new Error(`Failed to batch delete ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Search entities (basic text search)
   */
  public async search(
    searchTerm: string,
    options: QueryOptions = {}
  ): Promise<QueryResult<T>> {
    try {
      // This is a simplified search - in production, you might use ElasticSearch
      const result = await this.client.scan({
        filter: 'contains(#data, :searchTerm)',
        expressionAttributeNames: {
          '#data': 'Data'
        },
        expressionAttributeValues: {
          ':searchTerm': searchTerm
        },
        limit: options.limit,
        lastEvaluatedKey: options.lastEvaluatedKey
      });

      const entities = result.items
        .filter(item => item.EntityType === this.getEntityType().toUpperCase())
        .map(item => BaseEntity.fromDynamoDBItem(item, this.getEntityClass()));

      return {
        items: entities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: entities.length
      };
    } catch (error) {
      throw new Error(`Failed to search ${this.getEntityType()}s: ${error}`);
    }
  }

  /**
   * Get entity statistics
   */
  public async getStatistics(): Promise<{
    total: number;
    active: number;
    inactive: number;
    archived: number;
    deleted: number;
  }> {
    const [total, active, inactive, archived, deleted] = await Promise.all([
      this.countByStatus(),
      this.countByStatus(EntityStatus.ACTIVE),
      this.countByStatus(EntityStatus.INACTIVE),
      this.countByStatus(EntityStatus.ARCHIVED),
      this.countByStatus(EntityStatus.DELETED)
    ]);

    return { total, active, inactive, archived, deleted };
  }

  /**
   * Validate entity data
   */
  public async validate(entity: T): Promise<ValidationError[]> {
    await this.executeHook('beforeValidate', entity);
    
    const errors = await entity['validate'](); // Access protected method
    
    await this.executeHook('afterValidate', entity, errors);
    
    return errors;
  }

  /**
   * Abstract method to get default sort key
   */
  protected abstract getDefaultSortKey(): string;

  /**
   * Abstract method to get entity class constructor
   */
  protected abstract getEntityClass(): new () => T;

  /**
   * Custom query method for complex queries
   */
  protected async customQuery(params: {
    pk?: string;
    skBeginsWith?: string;
    indexName?: string;
    gsi1pk?: string;
    gsi1sk?: string;
    gsi2pk?: string;
    gsi2sk?: string;
    gsi3pk?: string;
    status?: EntityStatus;
    entityType?: string;
    limit?: number;
    lastEvaluatedKey?: any;
    scanIndexForward?: boolean;
  }): Promise<QueryResult<T>> {
    try {
      const result = await this.client.query(params);
      const entities = result.items.map(item => 
        BaseEntity.fromDynamoDBItem(item, this.getEntityClass())
      );

      return {
        items: entities,
        lastEvaluatedKey: result.lastEvaluatedKey,
        count: entities.length
      };
    } catch (error) {
      throw new Error(`Custom query failed for ${this.getEntityType()}: ${error}`);
    }
  }

  /**
   * Transaction support
   */
  public async transaction(
    operations: Array<{
      type: 'create' | 'update' | 'delete';
      entity?: T;
      id?: string;
      data?: TData;
      userId?: string;
    }>
  ): Promise<void> {
    const transactItems = [];

    for (const op of operations) {
      if (op.type === 'create' && op.data) {
        const entity = this.createEntity(op.data);
        if (op.userId) {
          entity.CreatedBy = op.userId;
          entity.UpdatedBy = op.userId;
        }
        entity.initialize();
        
        transactItems.push({
          type: 'put',
          item: entity.toDynamoDBItem()
        });
      } else if (op.type === 'update' && op.id && op.data) {
        const entity = await this.findById(op.id);
        if (entity) {
          entity.update(op.data as any, op.userId);
          transactItems.push({
            type: 'update',
            key: { pk: entity.PK, sk: entity.SK },
            updates: op.data
          });
        }
      } else if (op.type === 'delete' && op.id) {
        const entity = await this.findById(op.id);
        if (entity) {
          transactItems.push({
            type: 'delete',
            key: { pk: entity.PK, sk: entity.SK }
          });
        }
      }
    }

    try {
      await this.client.transactWrite(transactItems);
    } catch (error) {
      throw new Error(`Transaction failed for ${this.getEntityType()}: ${error}`);
    }
  }
}