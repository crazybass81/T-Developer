// backend/src/data/access/dynamodb-data-source.ts
import { DynamoDBDocumentClient, QueryCommand, ScanCommand, GetCommand, PutCommand, UpdateCommand, DeleteCommand, TransactWriteCommand } from '@aws-sdk/lib-dynamodb';
import { IDataSource, IQueryBuilder, QueryOptions, QueryResult, TransactionContext, TransactionOperation } from './data-source.interface';

export class DynamoDBDataSource implements IDataSource {
  constructor(
    private docClient: DynamoDBDocumentClient,
    private tableName: string
  ) {}

  async findById<T>(table: string, id: string): Promise<T | null> {
    const result = await this.docClient.send(new GetCommand({
      TableName: this.tableName,
      Key: { PK: `${table.toUpperCase()}#${id}`, SK: 'METADATA' }
    }));
    
    return result.Item as T || null;
  }

  async findMany<T>(table: string, options: QueryOptions = {}): Promise<QueryResult<T>> {
    const params: any = {
      TableName: this.tableName,
      FilterExpression: `EntityType = :entityType`,
      ExpressionAttributeValues: { ':entityType': table.toUpperCase() }
    };

    if (options.limit) params.Limit = options.limit;
    if (options.projection) params.ProjectionExpression = options.projection.join(', ');
    
    if (options.filters) {
      Object.entries(options.filters).forEach(([key, value], index) => {
        const attrName = `#attr${index}`;
        const attrValue = `:val${index}`;
        
        params.FilterExpression += ` AND ${attrName} = ${attrValue}`;
        params.ExpressionAttributeNames = { ...params.ExpressionAttributeNames, [attrName]: key };
        params.ExpressionAttributeValues[attrValue] = value;
      });
    }

    const result = await this.docClient.send(new ScanCommand(params));
    
    return {
      items: result.Items as T[] || [],
      totalCount: result.Count || 0,
      hasMore: !!result.LastEvaluatedKey,
      cursor: result.LastEvaluatedKey ? JSON.stringify(result.LastEvaluatedKey) : undefined
    };
  }

  async create<T>(table: string, data: T): Promise<T> {
    const item = {
      ...data,
      PK: `${table.toUpperCase()}#${(data as any).id}`,
      SK: 'METADATA',
      EntityType: table.toUpperCase(),
      CreatedAt: new Date().toISOString(),
      UpdatedAt: new Date().toISOString()
    };

    await this.docClient.send(new PutCommand({
      TableName: this.tableName,
      Item: item
    }));

    return data;
  }

  async update<T>(table: string, id: string, data: Partial<T>): Promise<T> {
    const updateExpression = this.buildUpdateExpression(data);
    
    const result = await this.docClient.send(new UpdateCommand({
      TableName: this.tableName,
      Key: { PK: `${table.toUpperCase()}#${id}`, SK: 'METADATA' },
      UpdateExpression: updateExpression.expression,
      ExpressionAttributeNames: updateExpression.names,
      ExpressionAttributeValues: updateExpression.values,
      ReturnValues: 'ALL_NEW'
    }));

    return result.Attributes as T;
  }

  async delete(table: string, id: string): Promise<boolean> {
    await this.docClient.send(new DeleteCommand({
      TableName: this.tableName,
      Key: { PK: `${table.toUpperCase()}#${id}`, SK: 'METADATA' }
    }));
    
    return true;
  }

  async batchCreate<T>(table: string, items: T[]): Promise<T[]> {
    const chunks = this.chunkArray(items, 25);
    
    for (const chunk of chunks) {
      const transactItems = chunk.map(item => ({
        Put: {
          TableName: this.tableName,
          Item: {
            ...item,
            PK: `${table.toUpperCase()}#${(item as any).id}`,
            SK: 'METADATA',
            EntityType: table.toUpperCase(),
            CreatedAt: new Date().toISOString(),
            UpdatedAt: new Date().toISOString()
          }
        }
      }));

      await this.docClient.send(new TransactWriteCommand({ TransactItems: transactItems }));
    }

    return items;
  }

  async batchUpdate<T>(table: string, updates: Array<{ id: string; data: Partial<T> }>): Promise<T[]> {
    const results: T[] = [];
    
    for (const update of updates) {
      const result = await this.update<T>(table, update.id, update.data);
      results.push(result);
    }
    
    return results;
  }

  async batchDelete(table: string, ids: string[]): Promise<number> {
    let deleted = 0;
    
    for (const id of ids) {
      const success = await this.delete(table, id);
      if (success) deleted++;
    }
    
    return deleted;
  }

  async beginTransaction(): Promise<TransactionContext> {
    return {
      id: crypto.randomUUID(),
      operations: []
    };
  }

  async commitTransaction(context: TransactionContext): Promise<void> {
    if (context.operations.length === 0) return;

    const transactItems = context.operations.map(op => {
      switch (op.type) {
        case 'create':
          return {
            Put: {
              TableName: this.tableName,
              Item: {
                ...op.data,
                PK: `${op.table.toUpperCase()}#${op.data.id}`,
                SK: 'METADATA',
                EntityType: op.table.toUpperCase()
              }
            }
          };
        case 'update':
          const updateExpr = this.buildUpdateExpression(op.data);
          return {
            Update: {
              TableName: this.tableName,
              Key: op.key,
              UpdateExpression: updateExpr.expression,
              ExpressionAttributeNames: updateExpr.names,
              ExpressionAttributeValues: updateExpr.values
            }
          };
        case 'delete':
          return {
            Delete: {
              TableName: this.tableName,
              Key: op.key
            }
          };
      }
    });

    await this.docClient.send(new TransactWriteCommand({ TransactItems: transactItems }));
  }

  async rollbackTransaction(context: TransactionContext): Promise<void> {
    // DynamoDB doesn't support rollback, operations are atomic
    context.operations = [];
  }

  query<T>(table: string): IQueryBuilder<T> {
    return new DynamoDBQueryBuilder<T>(this.docClient, this.tableName, table);
  }

  async isHealthy(): Promise<boolean> {
    try {
      await this.docClient.send(new GetCommand({
        TableName: this.tableName,
        Key: { PK: 'HEALTH_CHECK', SK: 'HEALTH_CHECK' }
      }));
      return true;
    } catch {
      return false;
    }
  }

  private buildUpdateExpression(data: any) {
    const expression: string[] = [];
    const names: Record<string, string> = {};
    const values: Record<string, any> = {};

    Object.entries(data).forEach(([key, value], index) => {
      const nameKey = `#attr${index}`;
      const valueKey = `:val${index}`;
      
      expression.push(`${nameKey} = ${valueKey}`);
      names[nameKey] = key;
      values[valueKey] = value;
    });

    values[':updatedAt'] = new Date().toISOString();
    names['#updatedAt'] = 'UpdatedAt';
    expression.push('#updatedAt = :updatedAt');

    return {
      expression: `SET ${expression.join(', ')}`,
      names,
      values
    };
  }

  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}

class DynamoDBQueryBuilder<T> implements IQueryBuilder<T> {
  private conditions: string[] = [];
  private attributeNames: Record<string, string> = {};
  private attributeValues: Record<string, any> = {};
  private sortField?: string;
  private sortDirection: 'asc' | 'desc' = 'asc';
  private limitCount?: number;
  private offsetCount?: number;
  private selectFields?: string[];

  constructor(
    private docClient: DynamoDBDocumentClient,
    private tableName: string,
    private entityType: string
  ) {
    this.conditions.push('EntityType = :entityType');
    this.attributeValues[':entityType'] = entityType.toUpperCase();
  }

  where(field: string, operator: string, value: any): IQueryBuilder<T> {
    const nameKey = `#${field}`;
    const valueKey = `:${field}`;
    
    this.attributeNames[nameKey] = field;
    this.attributeValues[valueKey] = value;
    
    const condition = operator === '=' ? `${nameKey} = ${valueKey}` : 
                     operator === '>' ? `${nameKey} > ${valueKey}` :
                     operator === '<' ? `${nameKey} < ${valueKey}` :
                     operator === 'contains' ? `contains(${nameKey}, ${valueKey})` :
                     `${nameKey} = ${valueKey}`;
    
    this.conditions.push(condition);
    return this;
  }

  whereIn(field: string, values: any[]): IQueryBuilder<T> {
    const nameKey = `#${field}`;
    this.attributeNames[nameKey] = field;
    
    const valueKeys = values.map((_, index) => {
      const key = `:${field}${index}`;
      this.attributeValues[key] = values[index];
      return key;
    });
    
    this.conditions.push(`${nameKey} IN (${valueKeys.join(', ')})`);
    return this;
  }

  whereBetween(field: string, start: any, end: any): IQueryBuilder<T> {
    const nameKey = `#${field}`;
    const startKey = `:${field}Start`;
    const endKey = `:${field}End`;
    
    this.attributeNames[nameKey] = field;
    this.attributeValues[startKey] = start;
    this.attributeValues[endKey] = end;
    
    this.conditions.push(`${nameKey} BETWEEN ${startKey} AND ${endKey}`);
    return this;
  }

  orderBy(field: string, direction: 'asc' | 'desc' = 'asc'): IQueryBuilder<T> {
    this.sortField = field;
    this.sortDirection = direction;
    return this;
  }

  limit(count: number): IQueryBuilder<T> {
    this.limitCount = count;
    return this;
  }

  offset(count: number): IQueryBuilder<T> {
    this.offsetCount = count;
    return this;
  }

  select(fields: string[]): IQueryBuilder<T> {
    this.selectFields = fields;
    return this;
  }

  async execute(): Promise<QueryResult<T>> {
    const params: any = {
      TableName: this.tableName,
      FilterExpression: this.conditions.join(' AND '),
      ExpressionAttributeNames: this.attributeNames,
      ExpressionAttributeValues: this.attributeValues
    };

    if (this.limitCount) params.Limit = this.limitCount;
    if (this.selectFields) params.ProjectionExpression = this.selectFields.join(', ');

    const result = await this.docClient.send(new ScanCommand(params));
    
    let items = result.Items as T[] || [];
    
    // Client-side sorting (DynamoDB limitation)
    if (this.sortField) {
      items.sort((a, b) => {
        const aVal = (a as any)[this.sortField!];
        const bVal = (b as any)[this.sortField!];
        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        return this.sortDirection === 'desc' ? -comparison : comparison;
      });
    }

    return {
      items,
      totalCount: result.Count || 0,
      hasMore: !!result.LastEvaluatedKey
    };
  }

  async first(): Promise<T | null> {
    const result = await this.limit(1).execute();
    return result.items[0] || null;
  }

  async count(): Promise<number> {
    const params = {
      TableName: this.tableName,
      FilterExpression: this.conditions.join(' AND '),
      ExpressionAttributeNames: this.attributeNames,
      ExpressionAttributeValues: this.attributeValues,
      Select: 'COUNT' as const
    };

    const result = await this.docClient.send(new ScanCommand(params));
    return result.Count || 0;
  }
}