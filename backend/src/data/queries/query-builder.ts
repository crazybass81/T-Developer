import { QueryCommand, QueryCommandInput } from '@aws-sdk/lib-dynamodb';

export class DynamoQueryBuilder {
  private params: QueryCommandInput = {
    TableName: '',
    KeyConditionExpression: '',
    ExpressionAttributeNames: {},
    ExpressionAttributeValues: {}
  };
  
  constructor(tableName: string) {
    this.params.TableName = tableName;
  }
  
  wherePartitionKey(key: string, value: string): this {
    this.params.KeyConditionExpression = '#pk = :pk';
    this.params.ExpressionAttributeNames!['#pk'] = key;
    this.params.ExpressionAttributeValues![':pk'] = value;
    return this;
  }
  
  andSortKey(key: string, operator: string, value: string | string[]): this {
    const skCondition = this.buildSortKeyCondition(key, operator, value);
    this.params.KeyConditionExpression += ` AND ${skCondition}`;
    return this;
  }
  
  private buildSortKeyCondition(key: string, operator: string, value: string | string[]): string {
    this.params.ExpressionAttributeNames!['#sk'] = key;
    
    switch (operator) {
      case '=':
        this.params.ExpressionAttributeValues![':sk'] = value;
        return '#sk = :sk';
      case 'begins_with':
        this.params.ExpressionAttributeValues![':sk'] = value;
        return 'begins_with(#sk, :sk)';
      case 'between':
        if (!Array.isArray(value) || value.length !== 2) {
          throw new Error('Between operator requires array of 2 values');
        }
        this.params.ExpressionAttributeValues![':sk1'] = value[0];
        this.params.ExpressionAttributeValues![':sk2'] = value[1];
        return '#sk BETWEEN :sk1 AND :sk2';
      default:
        throw new Error(`Unsupported operator: ${operator}`);
    }
  }
  
  filter(expression: string, values: Record<string, any>): this {
    this.params.FilterExpression = expression;
    Object.assign(this.params.ExpressionAttributeValues!, values);
    return this;
  }
  
  useIndex(indexName: string): this {
    this.params.IndexName = indexName;
    return this;
  }
  
  limit(count: number): this {
    this.params.Limit = count;
    return this;
  }
  
  startFrom(lastEvaluatedKey: any): this {
    if (lastEvaluatedKey) {
      this.params.ExclusiveStartKey = lastEvaluatedKey;
    }
    return this;
  }
  
  scanForward(forward: boolean = true): this {
    this.params.ScanIndexForward = forward;
    return this;
  }
  
  select(attributes: string[]): this {
    this.params.ProjectionExpression = attributes.join(', ');
    return this;
  }
  
  build(): QueryCommandInput {
    return this.params;
  }
}

export interface QueryResult<T> {
  items: T[];
  lastEvaluatedKey?: any;
  count: number;
  scannedCount: number;
}

export class QueryExecutor {
  constructor(private docClient: any) {}
  
  async query<T>(params: QueryCommandInput): Promise<QueryResult<T>> {
    const result = await this.docClient.send(new QueryCommand(params));
    
    return {
      items: (result.Items || []) as T[],
      lastEvaluatedKey: result.LastEvaluatedKey,
      count: result.Count || 0,
      scannedCount: result.ScannedCount || 0
    };
  }
  
  async queryAll<T>(params: QueryCommandInput): Promise<T[]> {
    const items: T[] = [];
    let lastEvaluatedKey: any;
    
    do {
      if (lastEvaluatedKey) {
        params.ExclusiveStartKey = lastEvaluatedKey;
      }
      
      const result = await this.query<T>(params);
      items.push(...result.items);
      lastEvaluatedKey = result.lastEvaluatedKey;
      
    } while (lastEvaluatedKey);
    
    return items;
  }
}