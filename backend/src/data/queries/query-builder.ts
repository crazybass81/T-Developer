/**
 * T-Developer Query Builder
 * 동적 쿼리 생성 및 실행
 */

import { BaseEntity, EntityStatus } from '../schemas/table-schema';
import { singleTableClient } from '../dynamodb/single-table';
import { CompositeKeyBuilder } from '../schemas/single-table-design';

export class QueryBuilder<T extends BaseEntity> {
  private conditions: Record<string, any> = {};
  private indexName?: string;
  private sortOrder: boolean = true;
  private limitValue?: number;
  private projectionAttributes?: string[];
  private filterExpressions: string[] = [];
  
  /**
   * Set partition key condition
   */
  where(field: string, value: any): this {
    this.conditions[field] = value;
    return this;
  }
  
  /**
   * Set multiple conditions
   */
  whereAll(conditions: Record<string, any>): this {
    Object.assign(this.conditions, conditions);
    return this;
  }
  
  /**
   * Use specific index
   */
  useIndex(indexName: string): this {
    this.indexName = indexName;
    return this;
  }
  
  /**
   * Set sort order
   */
  orderBy(ascending: boolean = true): this {
    this.sortOrder = ascending;
    return this;
  }
  
  /**
   * Limit results
   */
  limit(count: number): this {
    this.limitValue = count;
    return this;
  }
  
  /**
   * Select specific attributes
   */
  select(...attributes: string[]): this {
    this.projectionAttributes = attributes;
    return this;
  }
  
  /**
   * Add filter expression
   */
  filter(expression: string): this {
    this.filterExpressions.push(expression);
    return this;
  }
  
  /**
   * Filter by status
   */
  whereStatus(status: EntityStatus): this {
    this.conditions.status = status;
    return this;
  }
  
  /**
   * Filter by date range
   */
  whereBetween(field: string, start: Date, end: Date): this {
    this.filterExpressions.push(
      `#${field} BETWEEN :${field}_start AND :${field}_end`
    );
    this.conditions[`${field}_start`] = start.toISOString();
    this.conditions[`${field}_end`] = end.toISOString();
    return this;
  }
  
  /**
   * Execute query
   */
  async execute(): Promise<T[]> {
    const params = this.buildQueryParams();
    const result = await singleTableClient.query<T>(params);
    return result.items;
  }
  
  /**
   * Execute with pagination
   */
  async paginate(pageSize: number = 20): AsyncGenerator<T[], void, unknown> {
    let lastEvaluatedKey: any = undefined;
    
    while (true) {
      const params = this.buildQueryParams();
      params.limit = pageSize;
      params.lastEvaluatedKey = lastEvaluatedKey;
      
      const result = await singleTableClient.query<T>(params);
      
      if (result.items.length > 0) {
        yield result.items;
      }
      
      if (!result.lastEvaluatedKey) {
        break;
      }
      
      lastEvaluatedKey = result.lastEvaluatedKey;
    }
  }
  
  /**
   * Count matching items
   */
  async count(): Promise<number> {
    const params = this.buildQueryParams();
    let count = 0;
    let lastEvaluatedKey: any = undefined;
    
    do {
      params.lastEvaluatedKey = lastEvaluatedKey;
      const result = await singleTableClient.query<T>(params);
      count += result.items.length;
      lastEvaluatedKey = result.lastEvaluatedKey;
    } while (lastEvaluatedKey);
    
    return count;
  }
  
  /**
   * Get first matching item
   */
  async first(): Promise<T | null> {
    const params = this.buildQueryParams();
    params.limit = 1;
    const result = await singleTableClient.query<T>(params);
    return result.items[0] || null;
  }
  
  /**
   * Check if any items match
   */
  async exists(): Promise<boolean> {
    const first = await this.first();
    return first !== null;
  }
  
  /**
   * Build query parameters
   */
  private buildQueryParams(): any {
    const params: any = {
      scanIndexForward: this.sortOrder,
      limit: this.limitValue
    };
    
    // Determine query type based on conditions
    if (this.indexName) {
      params.indexName = this.indexName;
      
      switch (this.indexName) {
        case 'GSI1':
          if (this.conditions.userId) {
            params.gsi1pk = CompositeKeyBuilder.buildPK('USER', this.conditions.userId);
            if (this.conditions.projectId) {
              params.gsi1sk = `PROJECT#${this.conditions.projectId}`;
            }
          }
          break;
          
        case 'GSI2':
          if (this.conditions.agentId) {
            params.gsi2pk = CompositeKeyBuilder.buildPK('AGENT', this.conditions.agentId);
            if (this.conditions.taskId) {
              params.gsi2sk = `TASK#${this.conditions.taskId}`;
            }
          }
          break;
          
        case 'GSI3':
          if (this.conditions.entityType) {
            params.gsi3pk = `ENTITY#${this.conditions.entityType}`;
          }
          break;
          
        case 'GSI4':
          if (this.conditions.status) {
            params.status = this.conditions.status;
          }
          break;
          
        case 'GSI5':
          if (this.conditions.entityType) {
            params.entityType = this.conditions.entityType;
          }
          break;
      }
    } else {
      // Main table query
      if (this.conditions.pk) {
        params.pk = this.conditions.pk;
      } else if (this.conditions.entityType && this.conditions.entityId) {
        params.pk = CompositeKeyBuilder.buildPK(
          this.conditions.entityType,
          this.conditions.entityId
        );
      }
      
      if (this.conditions.sk) {
        params.skBeginsWith = this.conditions.sk;
      }
    }
    
    return params;
  }
}

/**
 * Factory function for query builder
 */
export function query<T extends BaseEntity>(): QueryBuilder<T> {
  return new QueryBuilder<T>();
}

/**
 * Pre-built query patterns
 */
export class QueryPatterns {
  /**
   * Get all items of a specific type
   */
  static byEntityType<T extends BaseEntity>(entityType: string): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI5')
      .where('entityType', entityType);
  }
  
  /**
   * Get items by status
   */
  static byStatus<T extends BaseEntity>(status: EntityStatus): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI4')
      .whereStatus(status)
      .orderBy(false); // Most recent first
  }
  
  /**
   * Get user's projects
   */
  static userProjects<T extends BaseEntity>(userId: string): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI1')
      .where('userId', userId);
  }
  
  /**
   * Get agent's tasks
   */
  static agentTasks<T extends BaseEntity>(agentId: string): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI2')
      .where('agentId', agentId);
  }
  
  /**
   * Get recent items
   */
  static recent<T extends BaseEntity>(entityType: string, limit: number = 10): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI3')
      .where('entityType', entityType)
      .orderBy(false)
      .limit(limit);
  }
  
  /**
   * Get items created in date range
   */
  static inDateRange<T extends BaseEntity>(
    entityType: string,
    start: Date,
    end: Date
  ): QueryBuilder<T> {
    return query<T>()
      .useIndex('GSI3')
      .where('entityType', entityType)
      .whereBetween('CreatedAt', start, end);
  }
}