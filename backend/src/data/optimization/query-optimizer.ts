/**
 * T-Developer Query Optimizer
 * 쿼리 최적화 및 성능 개선
 */

import { singleTableClient } from '../dynamodb/single-table';
import { BaseEntity } from '../schemas/table-schema';
import { indexManager } from '../management/index-manager';

export interface QueryPlan {
  indexName: string;
  estimatedCost: number;
  estimatedTime: number;
  scanRequired: boolean;
  filterExpression?: string;
}

export interface QueryStats {
  executionTime: number;
  itemsScanned: number;
  itemsReturned: number;
  consumedCapacity?: number;
}

export class QueryOptimizer {
  private queryCache: Map<string, any[]> = new Map();
  private queryStats: Map<string, QueryStats[]> = new Map();
  
  /**
   * Optimize and execute query
   */
  async executeOptimizedQuery<T extends BaseEntity>(params: {
    entityType: string;
    conditions: Record<string, any>;
    sort?: { field: string; order: 'asc' | 'desc' };
    limit?: number;
    useCache?: boolean;
  }): Promise<{
    items: T[];
    stats: QueryStats;
    plan: QueryPlan;
  }> {
    const startTime = Date.now();
    
    // Generate cache key
    const cacheKey = this.generateCacheKey(params);
    
    // Check cache if enabled
    if (params.useCache && this.queryCache.has(cacheKey)) {
      const cached = this.queryCache.get(cacheKey)!;
      return {
        items: cached as T[],
        stats: {
          executionTime: 0,
          itemsScanned: cached.length,
          itemsReturned: cached.length
        },
        plan: {
          indexName: 'cache',
          estimatedCost: 0,
          estimatedTime: 0,
          scanRequired: false
        }
      };
    }
    
    // Generate query plan
    const plan = this.generateQueryPlan(params);
    
    // Execute query based on plan
    const result = await this.executeQueryPlan<T>(plan, params);
    
    // Calculate stats
    const stats: QueryStats = {
      executionTime: Date.now() - startTime,
      itemsScanned: result.scanned,
      itemsReturned: result.items.length,
      consumedCapacity: result.consumedCapacity
    };
    
    // Update statistics
    this.updateQueryStats(cacheKey, stats);
    
    // Cache if appropriate
    if (params.useCache && stats.executionTime > 100) {
      this.queryCache.set(cacheKey, result.items);
      
      // Set cache expiration
      setTimeout(() => {
        this.queryCache.delete(cacheKey);
      }, 60000); // 1 minute cache
    }
    
    return {
      items: result.items,
      stats,
      plan
    };
  }
  
  /**
   * Generate optimal query plan
   */
  generateQueryPlan(params: {
    entityType: string;
    conditions: Record<string, any>;
    sort?: { field: string; order: 'asc' | 'desc' };
  }): QueryPlan {
    const conditions = params.conditions;
    const hasPartitionKey = !!conditions.id || !!conditions.pk;
    const hasSortKey = !!conditions.sk || !!conditions.timestamp;
    
    // Determine best index
    if (hasPartitionKey && hasSortKey) {
      return {
        indexName: 'main',
        estimatedCost: 1,
        estimatedTime: 10,
        scanRequired: false
      };
    }
    
    if (conditions.userId && conditions.projectId) {
      return {
        indexName: 'GSI1',
        estimatedCost: 2,
        estimatedTime: 20,
        scanRequired: false
      };
    }
    
    if (conditions.agentId && conditions.taskId) {
      return {
        indexName: 'GSI2',
        estimatedCost: 2,
        estimatedTime: 20,
        scanRequired: false
      };
    }
    
    if (params.sort?.field === 'createdAt') {
      return {
        indexName: 'GSI3',
        estimatedCost: 3,
        estimatedTime: 30,
        scanRequired: false
      };
    }
    
    if (conditions.status) {
      return {
        indexName: 'GSI4',
        estimatedCost: 3,
        estimatedTime: 30,
        scanRequired: false
      };
    }
    
    if (params.entityType) {
      return {
        indexName: 'GSI5',
        estimatedCost: 4,
        estimatedTime: 40,
        scanRequired: false
      };
    }
    
    // Fallback to scan
    return {
      indexName: 'scan',
      estimatedCost: 10,
      estimatedTime: 100,
      scanRequired: true,
      filterExpression: this.buildFilterExpression(conditions)
    };
  }
  
  /**
   * Execute query based on plan
   */
  private async executeQueryPlan<T extends BaseEntity>(
    plan: QueryPlan,
    params: any
  ): Promise<{
    items: T[];
    scanned: number;
    consumedCapacity?: number;
  }> {
    if (plan.scanRequired) {
      // Execute scan with filter
      const result = await singleTableClient.scan<T>({
        filter: plan.filterExpression,
        limit: params.limit
      });
      
      return {
        items: result.items,
        scanned: result.items.length * 2, // Estimate
        consumedCapacity: result.items.length * 0.5
      };
    }
    
    // Execute optimized query
    const result = await indexManager.queryWithOptimalIndex<T>({
      entityType: params.entityType,
      filters: params.conditions,
      sortBy: params.sort?.field,
      limit: params.limit
    });
    
    return {
      items: result,
      scanned: result.length,
      consumedCapacity: result.length * 0.25
    };
  }
  
  /**
   * Build filter expression for scan
   */
  private buildFilterExpression(conditions: Record<string, any>): string {
    const expressions: string[] = [];
    
    Object.entries(conditions).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        expressions.push(`#${key} = :${key}`);
      }
    });
    
    return expressions.join(' AND ');
  }
  
  /**
   * Generate cache key
   */
  private generateCacheKey(params: any): string {
    return JSON.stringify({
      entityType: params.entityType,
      conditions: params.conditions,
      sort: params.sort,
      limit: params.limit
    });
  }
  
  /**
   * Update query statistics
   */
  private updateQueryStats(key: string, stats: QueryStats): void {
    const existing = this.queryStats.get(key) || [];
    existing.push(stats);
    
    // Keep only last 100 stats
    if (existing.length > 100) {
      existing.shift();
    }
    
    this.queryStats.set(key, existing);
  }
  
  /**
   * Get query performance report
   */
  getPerformanceReport(): {
    totalQueries: number;
    avgExecutionTime: number;
    cacheHitRate: number;
    slowQueries: string[];
  } {
    let totalQueries = 0;
    let totalTime = 0;
    let cacheHits = 0;
    const slowQueries: string[] = [];
    
    this.queryStats.forEach((stats, key) => {
      stats.forEach(stat => {
        totalQueries++;
        totalTime += stat.executionTime;
        
        if (stat.executionTime === 0) {
          cacheHits++;
        }
        
        if (stat.executionTime > 500) {
          slowQueries.push(key);
        }
      });
    });
    
    return {
      totalQueries,
      avgExecutionTime: totalQueries > 0 ? totalTime / totalQueries : 0,
      cacheHitRate: totalQueries > 0 ? cacheHits / totalQueries : 0,
      slowQueries: [...new Set(slowQueries)]
    };
  }
  
  /**
   * Clear query cache
   */
  clearCache(): void {
    this.queryCache.clear();
  }
  
  /**
   * Suggest query improvements
   */
  suggestImprovements(query: string): string[] {
    const suggestions: string[] = [];
    
    // Analyze query pattern
    if (query.includes('scan')) {
      suggestions.push('Consider adding an index for this access pattern');
    }
    
    if (query.includes('multiple conditions')) {
      suggestions.push('Consider creating a composite key for these conditions');
    }
    
    if (!query.includes('limit')) {
      suggestions.push('Add a limit to reduce data transfer');
    }
    
    if (!query.includes('projection')) {
      suggestions.push('Use projection to return only needed attributes');
    }
    
    return suggestions;
  }
}

export const queryOptimizer = new QueryOptimizer();