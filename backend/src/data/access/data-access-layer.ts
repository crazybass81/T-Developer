// backend/src/data/access/data-access-layer.ts
import { IDataSource, QueryOptions, QueryResult, TransactionContext } from './data-source.interface';
import { CacheService } from '../../cache/cache.service';

export interface DataAccessConfig {
  caching?: {
    enabled: boolean;
    defaultTTL: number;
    cacheKeyPrefix: string;
  };
  metrics?: {
    enabled: boolean;
    slowQueryThreshold: number;
  };
  retries?: {
    maxAttempts: number;
    backoffMs: number;
  };
}

export class DataAccessLayer {
  private metrics = {
    queries: 0,
    slowQueries: 0,
    cacheHits: 0,
    cacheMisses: 0,
    errors: 0
  };

  constructor(
    private dataSource: IDataSource,
    private cacheService?: CacheService,
    private config: DataAccessConfig = {}
  ) {
    this.config = {
      caching: { enabled: false, defaultTTL: 300, cacheKeyPrefix: 'dal' },
      metrics: { enabled: true, slowQueryThreshold: 1000 },
      retries: { maxAttempts: 3, backoffMs: 100 },
      ...config
    };
  }

  async findById<T>(table: string, id: string, useCache = true): Promise<T | null> {
    const cacheKey = `${this.config.caching?.cacheKeyPrefix}:${table}:${id}`;
    const startTime = Date.now();

    try {
      // Try cache first
      if (useCache && this.config.caching?.enabled && this.cacheService) {
        const cached = await this.cacheService.get<T>(cacheKey);
        if (cached) {
          this.metrics.cacheHits++;
          return cached;
        }
        this.metrics.cacheMisses++;
      }

      // Query data source
      const result = await this.executeWithRetry(() => 
        this.dataSource.findById<T>(table, id)
      );

      // Cache result
      if (result && useCache && this.config.caching?.enabled && this.cacheService) {
        await this.cacheService.set(cacheKey, result, this.config.caching.defaultTTL);
      }

      this.recordMetrics(startTime);
      return result;

    } catch (error) {
      this.metrics.errors++;
      throw error;
    }
  }

  async findMany<T>(table: string, options?: QueryOptions): Promise<QueryResult<T>> {
    const startTime = Date.now();

    try {
      const result = await this.executeWithRetry(() =>
        this.dataSource.findMany<T>(table, options)
      );

      this.recordMetrics(startTime);
      return result;

    } catch (error) {
      this.metrics.errors++;
      throw error;
    }
  }

  async create<T>(table: string, data: T): Promise<T> {
    const startTime = Date.now();

    try {
      const result = await this.executeWithRetry(() =>
        this.dataSource.create<T>(table, data)
      );

      // Invalidate related cache
      if (this.config.caching?.enabled && this.cacheService) {
        await this.invalidateCache(table, (data as any).id);
      }

      this.recordMetrics(startTime);
      return result;

    } catch (error) {
      this.metrics.errors++;
      throw error;
    }
  }

  async update<T>(table: string, id: string, data: Partial<T>): Promise<T> {
    const startTime = Date.now();

    try {
      const result = await this.executeWithRetry(() =>
        this.dataSource.update<T>(table, id, data)
      );

      // Invalidate cache
      if (this.config.caching?.enabled && this.cacheService) {
        await this.invalidateCache(table, id);
      }

      this.recordMetrics(startTime);
      return result;

    } catch (error) {
      this.metrics.errors++;
      throw error;
    }
  }

  async delete(table: string, id: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      const result = await this.executeWithRetry(() =>
        this.dataSource.delete(table, id)
      );

      // Invalidate cache
      if (this.config.caching?.enabled && this.cacheService) {
        await this.invalidateCache(table, id);
      }

      this.recordMetrics(startTime);
      return result;

    } catch (error) {
      this.metrics.errors++;
      throw error;
    }
  }

  async transaction<T>(operations: (context: TransactionContext) => Promise<T>): Promise<T> {
    const context = await this.dataSource.beginTransaction();
    
    try {
      const result = await operations(context);
      await this.dataSource.commitTransaction(context);
      return result;
    } catch (error) {
      await this.dataSource.rollbackTransaction(context);
      throw error;
    }
  }

  query<T>(table: string) {
    return this.dataSource.query<T>(table);
  }

  async healthCheck(): Promise<{ healthy: boolean; metrics: any }> {
    const healthy = await this.dataSource.isHealthy();
    return { healthy, metrics: this.metrics };
  }

  private async executeWithRetry<T>(operation: () => Promise<T>): Promise<T> {
    const { maxAttempts, backoffMs } = this.config.retries!;
    let lastError: Error;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxAttempts || !this.isRetryableError(error)) {
          throw error;
        }

        await this.delay(backoffMs * Math.pow(2, attempt - 1));
      }
    }

    throw lastError!;
  }

  private isRetryableError(error: any): boolean {
    return error.name === 'ProvisionedThroughputExceededException' ||
           error.name === 'ThrottlingException' ||
           error.statusCode >= 500;
  }

  private async invalidateCache(table: string, id: string): Promise<void> {
    if (!this.cacheService) return;
    
    const cacheKey = `${this.config.caching?.cacheKeyPrefix}:${table}:${id}`;
    await this.cacheService.delete(cacheKey);
  }

  private recordMetrics(startTime: number): void {
    if (!this.config.metrics?.enabled) return;

    this.metrics.queries++;
    const duration = Date.now() - startTime;
    
    if (duration > this.config.metrics.slowQueryThreshold) {
      this.metrics.slowQueries++;
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}