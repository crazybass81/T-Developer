import { DynamoDBDocumentClient, QueryCommand, PutCommand, GetCommand, UpdateCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { BaseModel } from '../models/base.model';

export interface QueryOptions {
  limit?: number;
  lastEvaluatedKey?: any;
  scanIndexForward?: boolean;
  filterExpression?: string;
  expressionAttributeValues?: Record<string, any>;
}

export interface QueryResult<T> {
  items: T[];
  lastEvaluatedKey?: any;
  count: number;
}

export abstract class BaseRepository<T extends BaseModel> {
  protected tableName = 'T-Developer-Main';

  constructor(
    protected docClient: DynamoDBDocumentClient,
    protected entityType: string
  ) {}

  abstract toDynamoItem(entity: T): Record<string, any>;
  abstract fromDynamoItem(item: Record<string, any>): T;
  abstract generateKeys(entity: T): { PK: string; SK: string };

  async create(entity: T): Promise<T> {
    const item = this.toDynamoItem(entity);
    
    await this.docClient.send(new PutCommand({
      TableName: this.tableName,
      Item: item,
      ConditionExpression: 'attribute_not_exists(PK)'
    }));

    return entity;
  }

  async findById(id: string): Promise<T | null> {
    const keys = this.generateKeysById(id);
    
    const result = await this.docClient.send(new GetCommand({
      TableName: this.tableName,
      Key: keys
    }));

    return result.Item ? this.fromDynamoItem(result.Item) : null;
  }

  async update(entity: T): Promise<T> {
    const keys = this.generateKeys(entity);
    const item = this.toDynamoItem(entity);
    
    // Remove keys from update item
    delete item.PK;
    delete item.SK;
    
    const updateExpression = this.buildUpdateExpression(item);
    
    await this.docClient.send(new UpdateCommand({
      TableName: this.tableName,
      Key: keys,
      UpdateExpression: updateExpression.expression,
      ExpressionAttributeNames: updateExpression.names,
      ExpressionAttributeValues: updateExpression.values,
      ConditionExpression: 'attribute_exists(PK)'
    }));

    return entity;
  }

  async delete(id: string): Promise<void> {
    const keys = this.generateKeysById(id);
    
    await this.docClient.send(new DeleteCommand({
      TableName: this.tableName,
      Key: keys,
      ConditionExpression: 'attribute_exists(PK)'
    }));
  }

  protected async query(
    keyCondition: string,
    options: QueryOptions = {},
    indexName?: string
  ): Promise<QueryResult<T>> {
    const result = await this.docClient.send(new QueryCommand({
      TableName: this.tableName,
      IndexName: indexName,
      KeyConditionExpression: keyCondition,
      FilterExpression: options.filterExpression,
      ExpressionAttributeValues: options.expressionAttributeValues,
      Limit: options.limit,
      ExclusiveStartKey: options.lastEvaluatedKey,
      ScanIndexForward: options.scanIndexForward
    }));

    return {
      items: (result.Items || []).map(item => this.fromDynamoItem(item)),
      lastEvaluatedKey: result.LastEvaluatedKey,
      count: result.Count || 0
    };
  }

  protected abstract generateKeysById(id: string): { PK: string; SK: string };

  private buildUpdateExpression(item: Record<string, any>) {
    const names: Record<string, string> = {};
    const values: Record<string, any> = {};
    const updates: string[] = [];

    Object.entries(item).forEach(([key, value], index) => {
      const nameKey = `#attr${index}`;
      const valueKey = `:val${index}`;
      
      names[nameKey] = key;
      values[valueKey] = value;
      updates.push(`${nameKey} = ${valueKey}`);
    });

    return {
      expression: `SET ${updates.join(', ')}, UpdatedAt = :updatedAt, Version = Version + :inc`,
      names: { ...names, '#updatedAt': 'UpdatedAt', '#version': 'Version' },
      values: { ...values, ':updatedAt': new Date().toISOString(), ':inc': 1 }
    };
  }
}