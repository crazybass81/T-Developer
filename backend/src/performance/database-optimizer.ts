import { DynamoDBDocumentClient, GetCommand, PutCommand, QueryCommand, BatchGetCommand, BatchWriteCommand } from '@aws-sdk/lib-dynamodb';
import { PoolManager } from './connection-pool';

interface QueryMetrics {
  operation: string;
  table: string;
  duration: number;
  itemCount: number;
  consumedCapacity?: number;
}

export class DatabaseOptimizer {
  private poolManager = PoolManager.getInstance();
  private queryCache = new Map<string, { data: any; timestamp: number }>();
  private readonly CACHE_TTL = 300000; // 5 minutes
  private readonly MAX_BATCH_SIZE = 25;
  private readonly MAX_RETRY_ATTEMPTS = 3;

  async optimizedGet<T>(tableName: string, key: Record<string, any>): Promise<T | null> {
    const cacheKey = this.generateCacheKey(tableName, key);
    const cached = this.getFromCache(cacheKey);
    if (cached) return cached;

    const client = await this.poolManager.getDynamoPool().getClient();
    const startTime = Date.now();

    try {
      const result = await client.send(new GetCommand({
        TableName: tableName,
        Key: key
      }));

      const item = result.Item as T;
      if (item) {
        this.setCache(cacheKey, item);
      }

      this.recordQueryMetrics({
        operation: 'get',
        table: tableName,
        duration: Date.now() - startTime,
        itemCount: item ? 1 : 0,
        consumedCapacity: result.ConsumedCapacity?.CapacityUnits
      });

      return item || null;
    } finally {
      await this.poolManager.getDynamoPool().releaseClient(client);
    }
  }

  async optimizedPut(tableName: string, item: any): Promise<void> {
    const client = await this.poolManager.getDynamoPool().getClient();
    const startTime = Date.now();

    try {
      await client.send(new PutCommand({
        TableName: tableName,
        Item: item
      }));

      // Invalidate cache
      const key = this.extractKey(tableName, item);
      const cacheKey = this.generateCacheKey(tableName, key);
      this.invalidateCache(cacheKey);

      this.recordQueryMetrics({
        operation: 'put',
        table: tableName,
        duration: Date.now() - startTime,
        itemCount: 1
      });
    } finally {
      await this.poolManager.getDynamoPool().releaseClient(client);
    }
  }

  async optimizedQuery<T>(
    tableName: string,
    keyCondition: string,
    options: {
      filterExpression?: string;
      projectionExpression?: string;
      expressionAttributeValues?: Record<string, any>;
      expressionAttributeNames?: Record<string, string>;
      limit?: number;
      scanIndexForward?: boolean;
      exclusiveStartKey?: Record<string, any>;
    } = {}
  ): Promise<{ items: T[]; lastEvaluatedKey?: Record<string, any> }> {
    const client = await this.poolManager.getDynamoPool().getClient();
    const startTime = Date.now();

    try {
      const result = await client.send(new QueryCommand({
        TableName: tableName,
        KeyConditionExpression: keyCondition,
        FilterExpression: options.filterExpression,
        ProjectionExpression: options.projectionExpression,
        ExpressionAttributeValues: options.expressionAttributeValues,
        ExpressionAttributeNames: options.expressionAttributeNames,
        Limit: options.limit,
        ScanIndexForward: options.scanIndexForward,
        ExclusiveStartKey: options.exclusiveStartKey
      }));

      this.recordQueryMetrics({
        operation: 'query',
        table: tableName,
        duration: Date.now() - startTime,
        itemCount: result.Items?.length || 0,
        consumedCapacity: result.ConsumedCapacity?.CapacityUnits
      });

      return {
        items: (result.Items as T[]) || [],
        lastEvaluatedKey: result.LastEvaluatedKey
      };
    } finally {
      await this.poolManager.getDynamoPool().releaseClient(client);
    }
  }

  async batchGet<T>(tableName: string, keys: Array<Record<string, any>>): Promise<T[]> {
    if (keys.length === 0) return [];

    const client = await this.poolManager.getDynamoPool().getClient();
    const startTime = Date.now();
    const results: T[] = [];

    try {
      const chunks = this.chunkArray(keys, this.MAX_BATCH_SIZE);

      for (const chunk of chunks) {
        let retryCount = 0;
        let unprocessedKeys = chunk;

        while (unprocessedKeys.length > 0 && retryCount < this.MAX_RETRY_ATTEMPTS) {
          const result = await client.send(new BatchGetCommand({
            RequestItems: {
              [tableName]: {
                Keys: unprocessedKeys
              }
            }
          }));

          if (result.Responses?.[tableName]) {
            results.push(...(result.Responses[tableName] as T[]));
          }

          unprocessedKeys = result.UnprocessedKeys?.[tableName]?.Keys || [];
          
          if (unprocessedKeys.length > 0) {
            await this.exponentialBackoff(retryCount);
            retryCount++;
          }
        }
      }

      this.recordQueryMetrics({
        operation: 'batchGet',
        table: tableName,
        duration: Date.now() - startTime,
        itemCount: results.length
      });

      return results;
    } finally {
      await this.poolManager.getDynamoPool().releaseClient(client);
    }
  }

  async batchWrite(tableName: string, items: any[]): Promise<void> {
    if (items.length === 0) return;

    const client = await this.poolManager.getDynamoPool().getClient();
    const startTime = Date.now();

    try {
      const chunks = this.chunkArray(items, this.MAX_BATCH_SIZE);

      for (const chunk of chunks) {
        let retryCount = 0;
        let unprocessedItems = chunk.map(item => ({
          PutRequest: { Item: item }
        }));

        while (unprocessedItems.length > 0 && retryCount < this.MAX_RETRY_ATTEMPTS) {
          const result = await client.send(new BatchWriteCommand({
            RequestItems: {
              [tableName]: unprocessedItems
            }
          }));

          unprocessedItems = result.UnprocessedItems?.[tableName] || [];
          
          if (unprocessedItems.length > 0) {
            await this.exponentialBackoff(retryCount);
            retryCount++;
          }
        }
      }

      this.recordQueryMetrics({
        operation: 'batchWrite',
        table: tableName,
        duration: Date.now() - startTime,
        itemCount: items.length
      });
    } finally {
      await this.poolManager.getDynamoPool().releaseClient(client);
    }
  }

  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  private async exponentialBackoff(retryCount: number, baseDelay: number = 100): Promise<void> {
    const delay = baseDelay * Math.pow(2, retryCount) + Math.random() * 100;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  private generateCacheKey(tableName: string, key: Record<string, any>): string {
    return `${tableName}:${JSON.stringify(key)}`;
  }

  private getFromCache(key: string): any {
    const cached = this.queryCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }

  private setCache(key: string, data: any): void {
    this.queryCache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  private invalidateCache(key: string): void {
    this.queryCache.delete(key);
  }

  private extractKey(tableName: string, item: any): Record<string, any> {
    return { id: item.id };
  }

  private recordQueryMetrics(metrics: QueryMetrics): void {
    console.log('Query metrics:', metrics);
  }
}