/**
 * Hot Partition Manager
 * Manages hot partition detection and mitigation
 */

export interface HotPartitionMetrics {
  partitionKey: string;
  readThroughput: number;
  writeThroughput: number;
  throttleEvents: number;
  lastAccessed: string;
}

export class HotPartitionManager {
  private metrics: Map<string, HotPartitionMetrics> = new Map();
  private hotThreshold = 1000; // requests per second

  public recordAccess(partitionKey: string, isWrite: boolean = false): void {
    const existing = this.metrics.get(partitionKey);
    const now = new Date().toISOString();
    
    if (existing) {
      if (isWrite) {
        existing.writeThroughput++;
      } else {
        existing.readThroughput++;
      }
      existing.lastAccessed = now;
    } else {
      this.metrics.set(partitionKey, {
        partitionKey,
        readThroughput: isWrite ? 0 : 1,
        writeThroughput: isWrite ? 1 : 0,
        throttleEvents: 0,
        lastAccessed: now
      });
    }
  }

  public getHotPartitions(): HotPartitionMetrics[] {
    return Array.from(this.metrics.values())
      .filter(m => (m.readThroughput + m.writeThroughput) > this.hotThreshold)
      .sort((a, b) => (b.readThroughput + b.writeThroughput) - (a.readThroughput + a.writeThroughput));
  }

  public suggestMitigation(partitionKey: string): string[] {
    const suggestions: string[] = [];
    const metrics = this.metrics.get(partitionKey);
    
    if (metrics) {
      if (metrics.readThroughput > metrics.writeThroughput) {
        suggestions.push('Consider implementing read replicas or caching');
      }
      
      if (metrics.writeThroughput > 500) {
        suggestions.push('Consider sharding the partition key');
      }
    }
    
    return suggestions;
  }
}