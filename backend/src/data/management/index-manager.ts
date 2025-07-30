import { DynamoDBClient, DescribeTableCommand } from '@aws-sdk/client-dynamodb';
import { CloudWatchClient, GetMetricStatisticsCommand } from '@aws-sdk/client-cloudwatch';

export interface IndexUsageMetrics {
  indexName: string;
  readUtilization: number;
  writeUtilization: number;
  itemCount: number;
  sizeBytes: number;
  costEstimate: number;
}

export interface IndexUsageReport {
  tableName: string;
  period: number;
  indexes: IndexUsageMetrics[];
  recommendations: string[];
}

export interface UnusedIndex {
  indexName: string;
  lastUsed?: Date | null;
  estimatedMonthlyCost: number;
  recommendation: string;
}

export class IndexManager {
  constructor(
    private dynamoDB: DynamoDBClient,
    private cloudWatch: CloudWatchClient
  ) {}
  
  async analyzeIndexUsage(tableName: string, period: number = 7): Promise<IndexUsageReport> {
    const indexes = await this.listTableIndexes(tableName);
    const usage: IndexUsageMetrics[] = [];
    
    for (const index of indexes) {
      const metrics = await this.getIndexMetrics(tableName, index.IndexName!, period);
      
      usage.push({
        indexName: index.IndexName!,
        readUtilization: metrics.readUtilization,
        writeUtilization: metrics.writeUtilization,
        itemCount: metrics.itemCount,
        sizeBytes: metrics.sizeBytes,
        costEstimate: this.estimateIndexCost(metrics)
      });
    }
    
    return {
      tableName,
      period,
      indexes: usage,
      recommendations: this.generateIndexRecommendations(usage)
    };
  }
  
  async detectUnusedIndexes(tableName: string, threshold: number = 30): Promise<UnusedIndex[]> {
    const unusedIndexes: UnusedIndex[] = [];
    const indexes = await this.listTableIndexes(tableName);
    
    for (const index of indexes) {
      const lastUsed = await this.getLastIndexUsageTime(tableName, index.IndexName!);
      
      if (!lastUsed || (Date.now() - lastUsed.getTime()) > threshold * 24 * 60 * 60 * 1000) {
        unusedIndexes.push({
          indexName: index.IndexName!,
          lastUsed,
          estimatedMonthlyCost: await this.estimateIndexMonthlyCost(tableName, index.IndexName!),
          recommendation: 'Consider removing this unused index'
        });
      }
    }
    
    return unusedIndexes;
  }
  
  private async listTableIndexes(tableName: string): Promise<any[]> {
    const result = await this.dynamoDB.send(new DescribeTableCommand({
      TableName: tableName
    }));
    
    return result.Table?.GlobalSecondaryIndexes || [];
  }
  
  private async getIndexMetrics(tableName: string, indexName: string, period: number): Promise<any> {
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - period * 24 * 60 * 60 * 1000);
    
    const readMetrics = await this.cloudWatch.send(new GetMetricStatisticsCommand({
      Namespace: 'AWS/DynamoDB',
      MetricName: 'ConsumedReadCapacityUnits',
      Dimensions: [
        { Name: 'TableName', Value: tableName },
        { Name: 'GlobalSecondaryIndexName', Value: indexName }
      ],
      StartTime: startTime,
      EndTime: endTime,
      Period: 3600,
      Statistics: ['Sum', 'Average']
    }));
    
    const writeMetrics = await this.cloudWatch.send(new GetMetricStatisticsCommand({
      Namespace: 'AWS/DynamoDB',
      MetricName: 'ConsumedWriteCapacityUnits',
      Dimensions: [
        { Name: 'TableName', Value: tableName },
        { Name: 'GlobalSecondaryIndexName', Value: indexName }
      ],
      StartTime: startTime,
      EndTime: endTime,
      Period: 3600,
      Statistics: ['Sum', 'Average']
    }));
    
    return {
      readUtilization: this.calculateUtilization(readMetrics.Datapoints || []),
      writeUtilization: this.calculateUtilization(writeMetrics.Datapoints || []),
      itemCount: 1000,
      sizeBytes: 1024 * 1024
    };
  }
  
  private calculateUtilization(datapoints: any[]): number {
    if (datapoints.length === 0) return 0;
    
    const totalSum = datapoints.reduce((sum, dp) => sum + (dp.Sum || 0), 0);
    return totalSum / datapoints.length;
  }
  
  private estimateIndexCost(metrics: any): number {
    const readCost = metrics.readUtilization * 0.25;
    const writeCost = metrics.writeUtilization * 1.25;
    const storageCost = (metrics.sizeBytes / (1024 * 1024 * 1024)) * 0.25;
    
    return readCost + writeCost + storageCost;
  }
  
  private async getLastIndexUsageTime(tableName: string, indexName: string): Promise<Date | null> {
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    const metrics = await this.cloudWatch.send(new GetMetricStatisticsCommand({
      Namespace: 'AWS/DynamoDB',
      MetricName: 'ConsumedReadCapacityUnits',
      Dimensions: [
        { Name: 'TableName', Value: tableName },
        { Name: 'GlobalSecondaryIndexName', Value: indexName }
      ],
      StartTime: startTime,
      EndTime: endTime,
      Period: 3600,
      Statistics: ['Sum']
    }));
    
    const lastUsage = metrics.Datapoints?.find(dp => (dp.Sum || 0) > 0);
    return lastUsage ? lastUsage.Timestamp! : null;
  }
  
  private async estimateIndexMonthlyCost(tableName: string, indexName: string): Promise<number> {
    const metrics = await this.getIndexMetrics(tableName, indexName, 7);
    return this.estimateIndexCost(metrics) * 30;
  }
  
  private generateIndexRecommendations(usage: IndexUsageMetrics[]): string[] {
    const recommendations: string[] = [];
    
    const lowUsage = usage.filter(u => u.readUtilization < 10 && u.writeUtilization < 10);
    if (lowUsage.length > 0) {
      recommendations.push(`Consider removing low-usage indexes: ${lowUsage.map(u => u.indexName).join(', ')}`);
    }
    
    const highCost = usage.filter(u => u.costEstimate > 100);
    if (highCost.length > 0) {
      recommendations.push(`Review high-cost indexes: ${highCost.map(u => u.indexName).join(', ')}`);
    }
    
    return recommendations;
  }
}