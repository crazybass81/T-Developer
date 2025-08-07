/**
 * Time-Based Partitioner for DynamoDB
 * Manages temporal data partitioning for efficient queries
 */

export interface PartitionConfig {
  strategy: 'daily' | 'weekly' | 'monthly' | 'yearly';
  retentionDays?: number;
  hotPartitionThreshold?: number;
}

export class TimeBasedPartitioner {
  private config: PartitionConfig;

  constructor(config: PartitionConfig) {
    this.config = config;
  }

  public getPartitionKey(date: Date = new Date()): string {
    switch (this.config.strategy) {
      case 'daily':
        return date.toISOString().split('T')[0]; // YYYY-MM-DD
      case 'weekly':
        const year = date.getFullYear();
        const week = this.getWeekNumber(date);
        return `${year}-W${week.toString().padStart(2, '0')}`;
      case 'monthly':
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
      case 'yearly':
        return date.getFullYear().toString();
      default:
        return date.toISOString().split('T')[0];
    }
  }

  public getPartitionedKey(entityType: string, entityId: string, date?: Date): {
    PK: string;
    SK: string;
    partitionKey: string;
  } {
    const partitionKey = this.getPartitionKey(date);
    return {
      PK: `${entityType}#${partitionKey}`,
      SK: `${entityId}#${Date.now()}`,
      partitionKey
    };
  }

  public shouldArchivePartition(partitionKey: string): boolean {
    if (!this.config.retentionDays) return false;
    
    const partitionDate = this.parsePartitionKey(partitionKey);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.config.retentionDays);
    
    return partitionDate < cutoffDate;
  }

  private getWeekNumber(date: Date): number {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear = (date.getTime() - firstDayOfYear.getTime()) / 86400000;
    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
  }

  private parsePartitionKey(partitionKey: string): Date {
    if (partitionKey.includes('-W')) {
      // Weekly format: YYYY-WNN
      const [year, week] = partitionKey.split('-W');
      const jan1 = new Date(parseInt(year), 0, 1);
      return new Date(jan1.getTime() + (parseInt(week) - 1) * 7 * 24 * 60 * 60 * 1000);
    } else if (partitionKey.match(/^\d{4}-\d{2}$/)) {
      // Monthly format: YYYY-MM
      const [year, month] = partitionKey.split('-');
      return new Date(parseInt(year), parseInt(month) - 1, 1);
    } else if (partitionKey.match(/^\d{4}$/)) {
      // Yearly format: YYYY
      return new Date(parseInt(partitionKey), 0, 1);
    } else {
      // Daily format: YYYY-MM-DD
      return new Date(partitionKey);
    }
  }
}