/**
 * Query Pattern Learner for ML-Based Optimization
 * Analyzes query patterns and suggests optimizations
 */

export interface QueryPattern {
  pattern: string;
  frequency: number;
  averageResponseTime: number;
  lastUsed: string;
  indexUsage: string[];
  filterUsage: string[];
}

export interface OptimizationSuggestion {
  type: 'index' | 'partition' | 'cache' | 'query_rewrite';
  description: string;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  estimatedImprovement: number; // percentage
}

export class QueryPatternLearner {
  private patterns: Map<string, QueryPattern> = new Map();
  private minFrequencyThreshold = 10;
  private slowQueryThreshold = 1000; // 1 second

  public recordQuery(
    queryString: string,
    responseTime: number,
    indexUsed?: string,
    filtersUsed?: string[]
  ): void {
    const pattern = this.normalizeQuery(queryString);
    const existing = this.patterns.get(pattern);

    if (existing) {
      existing.frequency++;
      existing.averageResponseTime = 
        (existing.averageResponseTime + responseTime) / 2;
      existing.lastUsed = new Date().toISOString();
      
      if (indexUsed && !existing.indexUsage.includes(indexUsed)) {
        existing.indexUsage.push(indexUsed);
      }
      
      if (filtersUsed) {
        existing.filterUsage.push(...filtersUsed.filter(f => !existing.filterUsage.includes(f)));
      }
    } else {
      this.patterns.set(pattern, {
        pattern,
        frequency: 1,
        averageResponseTime: responseTime,
        lastUsed: new Date().toISOString(),
        indexUsage: indexUsed ? [indexUsed] : [],
        filterUsage: filtersUsed || []
      });
    }
  }

  public getOptimizationSuggestions(): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];
    
    // Find frequent slow queries
    const frequentSlowQueries = Array.from(this.patterns.values())
      .filter(p => p.frequency >= this.minFrequencyThreshold && 
                   p.averageResponseTime > this.slowQueryThreshold);

    for (const query of frequentSlowQueries) {
      // Suggest index creation
      if (query.indexUsage.length === 0 || query.indexUsage.includes('scan')) {
        suggestions.push({
          type: 'index',
          description: `Create GSI for pattern: ${query.pattern}`,
          impact: 'high',
          effort: 'medium',
          estimatedImprovement: 60
        });
      }

      // Suggest caching for very frequent queries
      if (query.frequency > 100) {
        suggestions.push({
          type: 'cache',
          description: `Cache results for pattern: ${query.pattern}`,
          impact: 'medium',
          effort: 'low',
          estimatedImprovement: 40
        });
      }
    }

    return suggestions;
  }

  public getTopPatterns(limit: number = 10): QueryPattern[] {
    return Array.from(this.patterns.values())
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, limit);
  }

  private normalizeQuery(query: string): string {
    // Normalize the query by removing specific values and keeping structure
    return query
      .replace(/\b\d+\b/g, '?') // Replace numbers with ?
      .replace(/'[^']*'/g, '?') // Replace string literals with ?
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim()
      .toLowerCase();
  }
}