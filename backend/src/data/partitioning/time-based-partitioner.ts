export type PartitionStrategy = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface PartitionMetrics {
  partitionKey: string;
  consumedRCU: number;
  consumedWCU: number;
  itemCount: number;
}

export interface HotPartition {
  partitionKey: string;
  consumedRCU: number;
  consumedWCU: number;
  itemCount: number;
  recommendation: string;
}

export interface ArchiveResult {
  totalPartitions: number;
  archived: string[];
  failed: string[];
  bytesArchived: number;
}

export class TimeBasedPartitioner {
  private partitionStrategy: PartitionStrategy;
  
  constructor(strategy: PartitionStrategy = 'monthly') {
    this.partitionStrategy = strategy;
  }
  
  generatePartitionKey(baseKey: string, timestamp: Date): string {
    const suffix = this.getPartitionSuffix(timestamp);
    return `${baseKey}#${suffix}`;
  }
  
  private getPartitionSuffix(date: Date): string {
    switch (this.partitionStrategy) {
      case 'daily':
        return date.toISOString().split('T')[0];
      case 'weekly':
        return this.getWeekIdentifier(date);
      case 'monthly':
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      case 'yearly':
        return String(date.getFullYear());
      default:
        throw new Error(`Unknown partition strategy: ${this.partitionStrategy}`);
    }
  }
  
  private getWeekIdentifier(date: Date): string {
    const year = date.getFullYear();
    const start = new Date(year, 0, 1);
    const days = Math.floor((date.getTime() - start.getTime()) / (24 * 60 * 60 * 1000));
    const week = Math.ceil((days + start.getDay() + 1) / 7);
    return `${year}-W${String(week).padStart(2, '0')}`;
  }
  
  getPartitionsForRange(startDate: Date, endDate: Date): string[] {
    const partitions: string[] = [];
    const current = new Date(startDate);
    
    while (current <= endDate) {
      partitions.push(this.getPartitionSuffix(current));
      this.incrementDate(current);
    }
    
    return [...new Set(partitions)];
  }
  
  private incrementDate(date: Date): void {
    switch (this.partitionStrategy) {
      case 'daily':
        date.setDate(date.getDate() + 1);
        break;
      case 'weekly':
        date.setDate(date.getDate() + 7);
        break;
      case 'monthly':
        date.setMonth(date.getMonth() + 1);
        break;
      case 'yearly':
        date.setFullYear(date.getFullYear() + 1);
        break;
    }
  }
  
  async detectHotPartitions(
    tableName: string,
    metrics: PartitionMetrics[]
  ): Promise<HotPartition[]> {
    const threshold = this.calculateDynamicThreshold(metrics);
    
    return metrics
      .filter(m => m.consumedRCU > threshold.rcu || m.consumedWCU > threshold.wcu)
      .map(m => ({
        partitionKey: m.partitionKey,
        consumedRCU: m.consumedRCU,
        consumedWCU: m.consumedWCU,
        itemCount: m.itemCount,
        recommendation: this.generateRebalancingRecommendation(m)
      }));
  }
  
  private calculateDynamicThreshold(metrics: PartitionMetrics[]): { rcu: number; wcu: number } {
    const avgRCU = metrics.reduce((sum, m) => sum + m.consumedRCU, 0) / metrics.length;
    const avgWCU = metrics.reduce((sum, m) => sum + m.consumedWCU, 0) / metrics.length;
    
    return {
      rcu: avgRCU * 2, // 2x average as threshold
      wcu: avgWCU * 2
    };
  }
  
  private generateRebalancingRecommendation(metrics: PartitionMetrics): string {
    if (metrics.consumedRCU > 1000) {
      return 'Consider splitting partition or adding read replicas';
    }
    if (metrics.consumedWCU > 1000) {
      return 'Consider write sharding or buffering';
    }
    return 'Monitor partition closely';
  }
  
  async archiveOldPartitions(
    tableName: string,
    retentionDays: number
  ): Promise<ArchiveResult> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
    
    const partitionsToArchive = await this.identifyArchivablePartitions(tableName, cutoffDate);
    
    const archived: string[] = [];
    const failed: string[] = [];
    
    for (const partition of partitionsToArchive) {
      try {
        await this.archivePartition(tableName, partition);
        archived.push(partition);
      } catch (error) {
        failed.push(partition);
        console.error(`Failed to archive partition ${partition}:`, error);
      }
    }
    
    return {
      totalPartitions: partitionsToArchive.length,
      archived,
      failed,
      bytesArchived: await this.calculateArchivedSize(archived)
    };
  }
  
  private async identifyArchivablePartitions(
    tableName: string,
    cutoffDate: Date
  ): Promise<string[]> {
    // Mock implementation - would scan table for old partitions
    const cutoffSuffix = this.getPartitionSuffix(cutoffDate);
    return [`old-partition-${cutoffSuffix}`];
  }
  
  private async archivePartition(tableName: string, partition: string): Promise<void> {
    // Mock implementation - would export to S3 and delete from DynamoDB
    console.log(`Archiving partition ${partition} from ${tableName}`);
  }
  
  private async calculateArchivedSize(partitions: string[]): Promise<number> {
    // Mock implementation - would calculate actual size
    return partitions.length * 1024 * 1024; // 1MB per partition
  }
}