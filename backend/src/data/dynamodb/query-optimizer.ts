import { QueryCommandInput } from '@aws-sdk/lib-dynamodb';

export interface QueryAnalysis {
  estimatedRCU: number;
  indexEfficiency: number;
  suggestions: string[];
}

export class DynamoDBQueryOptimizer {
  private queryCache: Map<string, any> = new Map();
  
  // Analyze query performance
  analyzeQuery(query: QueryCommandInput): QueryAnalysis {
    const analysis: QueryAnalysis = {
      estimatedRCU: this.estimateRCU(query),
      indexEfficiency: this.calculateIndexEfficiency(query),
      suggestions: []
    };
    
    // Generate optimization suggestions
    if (!query.ProjectionExpression) {
      analysis.suggestions.push('Add ProjectionExpression to reduce data transfer');
    }
    
    if (!query.Limit && !query.FilterExpression) {
      analysis.suggestions.push('Consider adding Limit to prevent large scans');
    }
    
    if (query.FilterExpression && !query.IndexName) {
      analysis.suggestions.push('Consider using GSI instead of FilterExpression');
    }
    
    return analysis;
  }
  
  private estimateRCU(query: QueryCommandInput): number {
    // Basic RCU estimation
    const baseRCU = 1;
    const limitMultiplier = query.Limit ? Math.min(query.Limit / 100, 10) : 10;
    
    return Math.ceil(baseRCU * limitMultiplier);
  }
  
  private calculateIndexEfficiency(query: QueryCommandInput): number {
    let efficiency = 0.5; // Base efficiency
    
    if (query.KeyConditionExpression) {
      efficiency += 0.3;
    }
    
    if (query.IndexName) {
      efficiency += 0.2;
    }
    
    if (query.FilterExpression) {
      efficiency -= 0.2; // Filter reduces efficiency
    }
    
    return Math.min(Math.max(efficiency, 0), 1);
  }
  
  // Optimize query
  optimizeQuery(query: QueryCommandInput): QueryCommandInput {
    const optimized = { ...query };
    
    // Add projection if missing
    if (!optimized.ProjectionExpression) {
      optimized.ProjectionExpression = 'PK, SK, #data';
      optimized.ExpressionAttributeNames = {
        ...optimized.ExpressionAttributeNames,
        '#data': 'data'
      };
    }
    
    // Add reasonable limit
    if (!optimized.Limit) {
      optimized.Limit = 100;
    }
    
    return optimized;
  }
  
  // Cache query results
  cacheResult(queryKey: string, result: any, ttl: number = 300000): void {
    this.queryCache.set(queryKey, {
      data: result,
      expires: Date.now() + ttl
    });
  }
  
  // Get cached result
  getCachedResult(queryKey: string): any | null {
    const cached = this.queryCache.get(queryKey);
    
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }
    
    if (cached) {
      this.queryCache.delete(queryKey);
    }
    
    return null;
  }
  
  // Generate query key for caching
  generateQueryKey(query: QueryCommandInput): string {
    return JSON.stringify({
      table: query.TableName,
      index: query.IndexName,
      key: query.KeyConditionExpression,
      filter: query.FilterExpression,
      projection: query.ProjectionExpression,
      limit: query.Limit
    });
  }
}