/**
 * T-Developer Index Management System
 * GSI/LSI 인덱스 관리 및 최적화
 */

import { singleTableClient } from '../dynamodb/single-table';
import { BaseEntity, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';

export interface IndexUsageMetrics {
  indexName: string;
  queryCount: number;
  avgResponseTime: number;
  lastUsed: Date;
  efficiency: number;
}

export class IndexManager {
  private indexMetrics: Map<string, IndexUsageMetrics> = new Map();
  
  /**
   * Query using optimal index
   */
  async queryWithOptimalIndex<T extends BaseEntity>(params: {
    entityType: string;
    filters: Record<string, any>;
    sortBy?: string;
    limit?: number;
  }): Promise<T[]> {
    const startTime = Date.now();
    let result: { items: T[] };
    let indexUsed = 'main';
    
    // Determine optimal index based on filters
    if (params.filters.userId && params.filters.projectId) {
      // Use GSI1 for user/project queries
      result = await singleTableClient.query<T>({
        indexName: 'GSI1',
        gsi1pk: CompositeKeyBuilder.buildPK('USER', params.filters.userId),
        gsi1sk: `PROJECT#${params.filters.projectId}`,
        limit: params.limit
      });
      indexUsed = 'GSI1';
    } else if (params.filters.agentId && params.filters.taskId) {
      // Use GSI2 for agent/task queries
      result = await singleTableClient.query<T>({
        indexName: 'GSI2',
        gsi2pk: CompositeKeyBuilder.buildPK('AGENT', params.filters.agentId),
        gsi2sk: `TASK#${params.filters.taskId}`,
        limit: params.limit
      });
      indexUsed = 'GSI2';
    } else if (params.sortBy === 'createdAt') {
      // Use GSI3 for time-based queries
      result = await singleTableClient.query<T>({
        indexName: 'GSI3',
        gsi3pk: `ENTITY#${params.entityType}`,
        scanIndexForward: false, // Most recent first
        limit: params.limit
      });
      indexUsed = 'GSI3';
    } else if (params.filters.status) {
      // Use GSI4 for status queries
      result = await singleTableClient.query<T>({
        indexName: 'GSI4',
        status: params.filters.status as EntityStatus,
        limit: params.limit
      });
      indexUsed = 'GSI4';
    } else if (params.entityType) {
      // Use GSI5 for entity type queries
      result = await singleTableClient.query<T>({
        indexName: 'GSI5',
        entityType: params.entityType,
        limit: params.limit
      });
      indexUsed = 'GSI5';
    } else {
      // Fallback to main table query
      result = await singleTableClient.query<T>({
        pk: CompositeKeyBuilder.buildPK(params.entityType, params.filters.id || ''),
        limit: params.limit
      });
    }
    
    // Update metrics
    this.updateIndexMetrics(indexUsed, Date.now() - startTime);
    
    return result.items;
  }
  
  /**
   * Analyze index usage patterns
   */
  analyzeIndexUsage(): Record<string, IndexUsageMetrics> {
    const analysis: Record<string, IndexUsageMetrics> = {};
    
    this.indexMetrics.forEach((metrics, indexName) => {
      analysis[indexName] = {
        ...metrics,
        efficiency: this.calculateEfficiency(metrics)
      };
    });
    
    return analysis;
  }
  
  /**
   * Recommend index optimizations
   */
  recommendOptimizations(): string[] {
    const recommendations: string[] = [];
    const usage = this.analyzeIndexUsage();
    
    Object.entries(usage).forEach(([indexName, metrics]) => {
      if (metrics.queryCount === 0) {
        recommendations.push(`Consider removing unused index: ${indexName}`);
      } else if (metrics.avgResponseTime > 1000) {
        recommendations.push(`Index ${indexName} has high latency. Consider optimizing.`);
      } else if (metrics.efficiency < 0.5) {
        recommendations.push(`Index ${indexName} has low efficiency. Review access patterns.`);
      }
    });
    
    return recommendations;
  }
  
  /**
   * Create composite keys for complex queries
   */
  createCompositeKey(attributes: string[]): string {
    return attributes.filter(Boolean).join('#');
  }
  
  /**
   * Validate index key structure
   */
  validateIndexKeys(item: BaseEntity): boolean {
    // Validate GSI1 keys if present
    if (item.GSI1PK && !item.GSI1SK) {
      return false;
    }
    
    // Validate GSI2 keys if present
    if (item.GSI2PK && !item.GSI2SK) {
      return false;
    }
    
    // Validate GSI3 keys if present
    if (item.GSI3PK && !item.CreatedAt) {
      return false;
    }
    
    return true;
  }
  
  /**
   * Update index metrics
   */
  private updateIndexMetrics(indexName: string, responseTime: number): void {
    const existing = this.indexMetrics.get(indexName) || {
      indexName,
      queryCount: 0,
      avgResponseTime: 0,
      lastUsed: new Date(),
      efficiency: 1
    };
    
    existing.queryCount++;
    existing.avgResponseTime = 
      (existing.avgResponseTime * (existing.queryCount - 1) + responseTime) / existing.queryCount;
    existing.lastUsed = new Date();
    
    this.indexMetrics.set(indexName, existing);
  }
  
  /**
   * Calculate index efficiency
   */
  private calculateEfficiency(metrics: IndexUsageMetrics): number {
    // Simple efficiency calculation based on response time and usage
    const responseScore = Math.max(0, 1 - (metrics.avgResponseTime / 1000));
    const usageScore = Math.min(1, metrics.queryCount / 100);
    
    return (responseScore + usageScore) / 2;
  }
  
  /**
   * Build index projection
   */
  buildProjection(attributes: string[]): string[] {
    // Always include base attributes
    const projection = [
      'PK', 'SK', 'EntityType', 'EntityId', 
      'Status', 'CreatedAt', 'UpdatedAt'
    ];
    
    // Add requested attributes
    attributes.forEach(attr => {
      if (!projection.includes(attr)) {
        projection.push(attr);
      }
    });
    
    return projection;
  }
  
  /**
   * Estimate index storage cost
   */
  estimateIndexStorage(itemCount: number, avgItemSize: number): {
    gsi: number;
    lsi: number;
    total: number;
  } {
    // Rough estimates based on AWS pricing
    const gsiCount = 5;
    const lsiCount = 2;
    
    const gsiStorage = itemCount * avgItemSize * gsiCount;
    const lsiStorage = itemCount * avgItemSize * lsiCount * 0.5; // LSIs share base table storage
    
    return {
      gsi: gsiStorage,
      lsi: lsiStorage,
      total: gsiStorage + lsiStorage
    };
  }
}

export const indexManager = new IndexManager();