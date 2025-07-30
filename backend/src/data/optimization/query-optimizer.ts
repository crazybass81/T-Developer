import crypto from 'crypto';

export interface QueryAnalysis {
  estimatedRCU: number;
  indexEfficiency: number;
  projectionEfficiency: number;
  recommendations: QueryRecommendation[];
}

export interface QueryRecommendation {
  type: 'INDEX' | 'PROJECTION' | 'PAGINATION';
  message: string;
  impact: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface QueryMetrics {
  queryKey: string;
  executionCount: number;
  totalExecutionTime: number;
  averageExecutionTime: number;
  totalItemsReturned: number;
  totalRCUConsumed: number;
  lastExecuted: Date;
  frequency: number;
}

export class QueryOptimizer {
  private queryMetrics: Map<string, QueryMetrics> = new Map();
  
  async analyzeQuery(query: any): Promise<QueryAnalysis> {
    const analysis: QueryAnalysis = {
      estimatedRCU: this.estimateReadCapacityUnits(query),
      indexEfficiency: this.calculateIndexEfficiency(query),
      projectionEfficiency: this.calculateProjectionEfficiency(query),
      recommendations: []
    };
    
    if (analysis.indexEfficiency < 0.8) {
      analysis.recommendations.push({
        type: 'INDEX',
        message: 'Consider using a more selective index',
        impact: 'HIGH'
      });
    }
    
    if (!query.ProjectionExpression) {
      analysis.recommendations.push({
        type: 'PROJECTION',
        message: 'Add ProjectionExpression to reduce data transfer',
        impact: 'MEDIUM'
      });
    }
    
    return analysis;
  }
  
  async optimizeQuery(originalQuery: any, historicalMetrics?: QueryMetrics[]): Promise<any> {
    const optimized = { ...originalQuery };
    
    if (!optimized.ProjectionExpression && historicalMetrics) {
      const usedAttributes = this.analyzeAttributeUsage(historicalMetrics);
      if (usedAttributes.length > 0) {
        optimized.ProjectionExpression = usedAttributes.join(', ');
      }
    }
    
    if (!optimized.Limit) {
      optimized.Limit = this.calculateOptimalPageSize(historicalMetrics);
    }
    
    return optimized;
  }
  
  getCacheKey(query: any): string {
    const normalized = {
      table: query.TableName,
      index: query.IndexName || 'primary',
      pk: query.ExpressionAttributeValues?.[':pk'],
      sk: query.ExpressionAttributeValues?.[':sk'] || '',
      filter: query.FilterExpression || ''
    };
    
    return crypto
      .createHash('sha256')
      .update(JSON.stringify(normalized))
      .digest('hex');
  }
  
  shouldCache(query: any, result: any): boolean {
    const criteria = {
      minItems: 10,
      maxItems: 1000,
      minExecutionTime: 100,
      frequencyThreshold: 5
    };
    
    const metrics = this.queryMetrics.get(this.getCacheKey(query));
    
    return (
      result.items?.length >= criteria.minItems &&
      result.items?.length <= criteria.maxItems &&
      (metrics?.averageExecutionTime || 0) >= criteria.minExecutionTime &&
      (metrics?.frequency || 0) >= criteria.frequencyThreshold
    );
  }
  
  private estimateReadCapacityUnits(query: any): number {
    const baseRCU = 1;
    const itemSizeKB = 4;
    const estimatedItems = query.Limit || 100;
    
    return Math.ceil((estimatedItems * itemSizeKB) / 4) * baseRCU;
  }
  
  private calculateIndexEfficiency(query: any): number {
    if (!query.IndexName) return 1.0;
    
    const hasPartitionKey = query.KeyConditionExpression?.includes('#pk');
    const hasSortKey = query.KeyConditionExpression?.includes('#sk');
    
    if (hasPartitionKey && hasSortKey) return 1.0;
    if (hasPartitionKey) return 0.8;
    return 0.5;
  }
  
  private calculateProjectionEfficiency(query: any): number {
    return query.ProjectionExpression ? 1.0 : 0.5;
  }
  
  private analyzeAttributeUsage(metrics: QueryMetrics[]): string[] {
    return ['PK', 'SK', 'EntityType', 'CreatedAt'];
  }
  
  private calculateOptimalPageSize(metrics?: QueryMetrics[]): number {
    if (!metrics || metrics.length === 0) return 50;
    
    const avgItems = metrics.reduce((sum, m) => sum + m.totalItemsReturned, 0) / metrics.length;
    return Math.min(Math.max(Math.ceil(avgItems), 10), 100);
  }
}

export class QueryPerformanceMonitor {
  private metrics: Map<string, QueryMetrics> = new Map();
  
  async trackQuery(
    queryKey: string,
    executionTime: number,
    itemCount: number,
    consumedRCU?: number
  ): Promise<void> {
    const existing = this.metrics.get(queryKey) || {
      queryKey,
      executionCount: 0,
      totalExecutionTime: 0,
      averageExecutionTime: 0,
      totalItemsReturned: 0,
      totalRCUConsumed: 0,
      lastExecuted: new Date(),
      frequency: 0
    };
    
    existing.executionCount++;
    existing.totalExecutionTime += executionTime;
    existing.averageExecutionTime = existing.totalExecutionTime / existing.executionCount;
    existing.totalItemsReturned += itemCount;
    existing.totalRCUConsumed += consumedRCU || 0;
    existing.lastExecuted = new Date();
    existing.frequency = existing.executionCount;
    
    this.metrics.set(queryKey, existing);
    
    if (existing.averageExecutionTime > 1000) {
      await this.alertSlowQuery(queryKey, existing);
    }
  }
  
  private async alertSlowQuery(queryKey: string, metrics: QueryMetrics): Promise<void> {
    console.warn(`Slow query detected: ${queryKey}`, {
      averageTime: metrics.averageExecutionTime,
      frequency: metrics.frequency
    });
  }
  
  getMetrics(): Map<string, QueryMetrics> {
    return this.metrics;
  }
}