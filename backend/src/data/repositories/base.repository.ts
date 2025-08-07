/**
 * Base Repository Pattern Implementation
 * Provides standardized data access methods for all entities
 */

import { BaseEntity } from '../entities/base.entity';
import { BaseModel, QueryOptions, QueryResult, ModelHooks } from '../models/base.model';
import { EntityStatus } from '../schemas/table-schema';
import { SingleTableClient } from '../dynamodb/single-table';
import { ValidationError } from '../validation/validator';

export interface RepositoryOptions {
  enableCaching?: boolean;
  cacheExpiration?: number; // in seconds
  enableMetrics?: boolean;
  enableAuditLog?: boolean;
}

export interface RepositoryMetrics {
  totalQueries: number;
  totalWrites: number;
  cacheHits: number;
  cacheMisses: number;
  avgResponseTime: number;
  lastActivity: string;
}

export interface AuditLogEntry {
  operation: string;
  entityId: string;
  entityType: string;
  userId?: string;
  timestamp: string;
  details?: any;
}

export interface FilterOptions {
  status?: EntityStatus[];
  dateRange?: {
    from: string;
    to: string;
  };
  search?: string;
  customFilters?: Record<string, any>;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

export interface AdvancedQueryOptions extends QueryOptions {
  filters?: FilterOptions;
  sort?: SortOptions;
  includeDeleted?: boolean;
  includeArchived?: boolean;
}

/**
 * Abstract base repository providing standardized data access patterns
 */
export abstract class BaseRepository<T extends BaseEntity, TData = any> {
  protected model: BaseModel<T, TData>;
  protected client: SingleTableClient;
  protected options: RepositoryOptions;
  protected metrics: RepositoryMetrics;
  protected auditLog: AuditLogEntry[] = [];
  protected cache: Map<string, { data: T; expiry: number }> = new Map();

  constructor(
    model: BaseModel<T, TData>,
    options: RepositoryOptions = {}
  ) {
    this.model = model;
    this.client = (model as any).client;
    this.options = {
      enableCaching: false,
      cacheExpiration: 300, // 5 minutes
      enableMetrics: true,
      enableAuditLog: true,
      ...options
    };

    this.metrics = {
      totalQueries: 0,
      totalWrites: 0,
      cacheHits: 0,
      cacheMisses: 0,
      avgResponseTime: 0,
      lastActivity: new Date().toISOString()
    };
  }

  /**
   * Abstract method to get repository name for logging/metrics
   */
  protected abstract getRepositoryName(): string;

  /**
   * Track metrics for operations
   */
  protected trackMetrics(operation: 'query' | 'write', responseTime: number): void {
    if (!this.options.enableMetrics) return;

    this.metrics.lastActivity = new Date().toISOString();
    
    if (operation === 'query') {
      this.metrics.totalQueries++;
    } else {
      this.metrics.totalWrites++;
    }

    // Update average response time
    const totalOps = this.metrics.totalQueries + this.metrics.totalWrites;
    this.metrics.avgResponseTime = 
      ((this.metrics.avgResponseTime * (totalOps - 1)) + responseTime) / totalOps;
  }

  /**
   * Log audit entry
   */
  protected logAudit(
    operation: string,
    entityId: string,
    userId?: string,
    details?: any
  ): void {
    if (!this.options.enableAuditLog) return;

    const entry: AuditLogEntry = {
      operation,
      entityId,
      entityType: this.getRepositoryName(),
      userId,
      timestamp: new Date().toISOString(),
      details
    };

    this.auditLog.push(entry);

    // Keep only last 1000 entries to prevent memory issues
    if (this.auditLog.length > 1000) {
      this.auditLog.shift();
    }
  }

  /**
   * Cache management
   */
  protected getCacheKey(id: string): string {
    return `${this.getRepositoryName()}:${id}`;
  }

  protected getFromCache(id: string): T | null {
    if (!this.options.enableCaching) return null;

    const key = this.getCacheKey(id);
    const cached = this.cache.get(key);

    if (cached && cached.expiry > Date.now()) {
      this.metrics.cacheHits++;
      return cached.data;
    }

    if (cached) {
      this.cache.delete(key); // Remove expired entry
    }

    this.metrics.cacheMisses++;
    return null;
  }

  protected setToCache(id: string, entity: T): void {
    if (!this.options.enableCaching) return;

    const key = this.getCacheKey(id);
    const expiry = Date.now() + (this.options.cacheExpiration! * 1000);

    this.cache.set(key, { data: entity, expiry });
  }

  protected removeFromCache(id: string): void {
    if (!this.options.enableCaching) return;

    const key = this.getCacheKey(id);
    this.cache.delete(key);
  }

  protected clearCache(): void {
    this.cache.clear();
  }

  /**
   * Create new entity
   */
  public async create(data: TData, userId?: string): Promise<T> {
    const startTime = Date.now();

    try {
      const entity = await this.model.create(data, userId);
      
      this.setToCache(entity.EntityId, entity);
      this.logAudit('CREATE', entity.EntityId, userId, { data });
      
      return entity;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  /**
   * Find entity by ID with caching
   */
  public async findById(id: string): Promise<T | null> {
    const startTime = Date.now();

    try {
      // Check cache first
      const cached = this.getFromCache(id);
      if (cached) {
        return cached;
      }

      const entity = await this.model.findById(id);
      
      if (entity) {
        this.setToCache(id, entity);
        this.logAudit('READ', id);
      }

      return entity;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find multiple entities by IDs
   */
  public async findByIds(ids: string[]): Promise<T[]> {
    const startTime = Date.now();

    try {
      if (ids.length === 0) return [];

      // Check cache for each ID
      const results: T[] = [];
      const uncachedIds: string[] = [];

      if (this.options.enableCaching) {
        for (const id of ids) {
          const cached = this.getFromCache(id);
          if (cached) {
            results.push(cached);
          } else {
            uncachedIds.push(id);
          }
        }
      } else {
        uncachedIds.push(...ids);
      }

      // Fetch uncached entities
      if (uncachedIds.length > 0) {
        const entities = await this.model.findByIds(uncachedIds);
        
        // Cache the results
        entities.forEach(entity => {
          this.setToCache(entity.EntityId, entity);
        });
        
        results.push(...entities);
      }

      this.logAudit('BULK_READ', '', undefined, { count: results.length });
      return results;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
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
    const startTime = Date.now();

    try {
      const entity = await this.model.update(id, updates, userId);
      
      if (entity) {
        this.setToCache(id, entity);
        this.logAudit('UPDATE', id, userId, { updates });
      }

      return entity;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  /**
   * Delete entity
   */
  public async delete(id: string, userId?: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      const success = await this.model.delete(id);
      
      if (success) {
        this.removeFromCache(id);
        this.logAudit('DELETE', id, userId);
      }

      return success;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  /**
   * Soft delete (archive) entity
   */
  public async archive(id: string, userId?: string): Promise<T | null> {
    const startTime = Date.now();

    try {
      const entity = await this.model.archive(id, userId);
      
      if (entity) {
        this.setToCache(id, entity);
        this.logAudit('ARCHIVE', id, userId);
      }

      return entity;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  /**
   * Find all entities with advanced options
   */
  public async findAll(options: AdvancedQueryOptions = {}): Promise<QueryResult<T>> {
    const startTime = Date.now();

    try {
      let result = await this.model.findAll(options);

      // Apply additional filters
      if (options.filters) {
        result.items = this.applyFilters(result.items, options.filters);
        result.count = result.items.length;
      }

      // Apply sorting
      if (options.sort) {
        result.items = this.applySort(result.items, options.sort);
      }

      this.logAudit('LIST', '', undefined, { 
        count: result.count, 
        filters: options.filters 
      });

      return result;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find entities by status
   */
  public async findByStatus(
    status: EntityStatus,
    options: QueryOptions = {}
  ): Promise<QueryResult<T>> {
    const startTime = Date.now();

    try {
      const result = await this.model.findByStatus(status, options);
      
      this.logAudit('LIST_BY_STATUS', '', undefined, { 
        status, 
        count: result.count 
      });

      return result;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Find recent entities
   */
  public async findRecent(
    limit: number = 20,
    options: QueryOptions = {}
  ): Promise<QueryResult<T>> {
    const startTime = Date.now();

    try {
      const result = await this.model.findRecent(limit, options);
      
      this.logAudit('LIST_RECENT', '', undefined, { 
        limit,
        count: result.count 
      });

      return result;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Search entities
   */
  public async search(
    searchTerm: string,
    options: AdvancedQueryOptions = {}
  ): Promise<QueryResult<T>> {
    const startTime = Date.now();

    try {
      const result = await this.model.search(searchTerm, options);
      
      // Apply additional filters
      if (options.filters) {
        result.items = this.applyFilters(result.items, options.filters);
        result.count = result.items.length;
      }

      this.logAudit('SEARCH', '', undefined, { 
        searchTerm,
        count: result.count 
      });

      return result;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Count entities
   */
  public async count(status?: EntityStatus): Promise<number> {
    const startTime = Date.now();

    try {
      const count = await this.model.countByStatus(status);
      
      this.logAudit('COUNT', '', undefined, { status, count });
      return count;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Check if entity exists
   */
  public async exists(id: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      // Check cache first
      const cached = this.getFromCache(id);
      if (cached) {
        return true;
      }

      const exists = await this.model.exists(id);
      
      this.logAudit('EXISTS', id, undefined, { exists });
      return exists;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Batch operations
   */
  public async batchCreate(dataList: TData[], userId?: string): Promise<T[]> {
    const startTime = Date.now();

    try {
      const entities = await this.model.batchCreate(dataList, userId);
      
      // Cache the entities
      entities.forEach(entity => {
        this.setToCache(entity.EntityId, entity);
      });

      this.logAudit('BATCH_CREATE', '', userId, { count: entities.length });
      return entities;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  public async batchDelete(ids: string[], userId?: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      const success = await this.model.batchDelete(ids);
      
      if (success) {
        // Remove from cache
        ids.forEach(id => {
          this.removeFromCache(id);
        });
      }

      this.logAudit('BATCH_DELETE', '', userId, { count: ids.length });
      return success;
    } finally {
      this.trackMetrics('write', Date.now() - startTime);
    }
  }

  /**
   * Get repository statistics
   */
  public async getStatistics(): Promise<{
    total: number;
    active: number;
    inactive: number;
    archived: number;
    deleted: number;
  }> {
    const startTime = Date.now();

    try {
      const stats = await this.model.getStatistics();
      
      this.logAudit('STATS', '', undefined, stats);
      return stats;
    } finally {
      this.trackMetrics('query', Date.now() - startTime);
    }
  }

  /**
   * Get repository metrics
   */
  public getMetrics(): RepositoryMetrics {
    return { ...this.metrics };
  }

  /**
   * Get audit log
   */
  public getAuditLog(limit?: number): AuditLogEntry[] {
    if (limit) {
      return this.auditLog.slice(-limit);
    }
    return [...this.auditLog];
  }

  /**
   * Validate entity
   */
  public async validate(entity: T): Promise<ValidationError[]> {
    return await this.model.validate(entity);
  }

  /**
   * Refresh cache for entity
   */
  public async refreshCache(id: string): Promise<T | null> {
    this.removeFromCache(id);
    return await this.findById(id);
  }

  /**
   * Bulk refresh cache
   */
  public async refreshCacheForIds(ids: string[]): Promise<T[]> {
    // Remove from cache
    ids.forEach(id => this.removeFromCache(id));
    
    // Fetch fresh data
    return await this.findByIds(ids);
  }

  /**
   * Apply filters to results
   */
  protected applyFilters(items: T[], filters: FilterOptions): T[] {
    let filteredItems = [...items];

    // Status filter
    if (filters.status && filters.status.length > 0) {
      filteredItems = filteredItems.filter(item => 
        filters.status!.includes(item.Status)
      );
    }

    // Date range filter
    if (filters.dateRange) {
      const fromDate = new Date(filters.dateRange.from);
      const toDate = new Date(filters.dateRange.to);
      
      filteredItems = filteredItems.filter(item => {
        const createdAt = new Date(item.CreatedAt);
        return createdAt >= fromDate && createdAt <= toDate;
      });
    }

    // Text search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredItems = filteredItems.filter(item => {
        const data = JSON.stringify(item.Data).toLowerCase();
        return data.includes(searchTerm);
      });
    }

    return filteredItems;
  }

  /**
   * Apply sorting to results
   */
  protected applySort(items: T[], sort: SortOptions): T[] {
    return [...items].sort((a, b) => {
      const aValue = (a as any)[sort.field];
      const bValue = (b as any)[sort.field];

      let comparison = 0;
      if (aValue < bValue) comparison = -1;
      else if (aValue > bValue) comparison = 1;

      return sort.direction === 'desc' ? -comparison : comparison;
    });
  }

  /**
   * Health check for repository
   */
  public async healthCheck(): Promise<{
    healthy: boolean;
    responseTime: number;
    cacheHitRate: number;
    error?: string;
  }> {
    const startTime = Date.now();

    try {
      // Perform a simple query to test connectivity
      await this.count();
      
      const responseTime = Date.now() - startTime;
      const cacheHitRate = this.metrics.cacheHits / 
        (this.metrics.cacheHits + this.metrics.cacheMisses) * 100;

      return {
        healthy: true,
        responseTime,
        cacheHitRate: isNaN(cacheHitRate) ? 0 : cacheHitRate
      };
    } catch (error) {
      return {
        healthy: false,
        responseTime: Date.now() - startTime,
        cacheHitRate: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Reset metrics
   */
  public resetMetrics(): void {
    this.metrics = {
      totalQueries: 0,
      totalWrites: 0,
      cacheHits: 0,
      cacheMisses: 0,
      avgResponseTime: 0,
      lastActivity: new Date().toISOString()
    };
  }

  /**
   * Clear audit log
   */
  public clearAuditLog(): void {
    this.auditLog = [];
  }
}