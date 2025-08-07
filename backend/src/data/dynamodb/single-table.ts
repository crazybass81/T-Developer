/**
 * T-Developer Single Table DynamoDB Operations
 * 단일 테이블 패턴 구현을 위한 DynamoDB 클라이언트 래퍼
 */

import {
  DynamoDBClient,
  PutItemCommand,
  GetItemCommand,
  QueryCommand,
  ScanCommand,
  UpdateItemCommand,
  DeleteItemCommand,
  BatchWriteItemCommand,
  BatchGetItemCommand,
  TransactWriteItemsCommand,
  TransactGetItemsCommand,
  PutItemCommandInput,
  GetItemCommandInput,
  QueryCommandInput,
  UpdateItemCommandInput,
  DeleteItemCommandInput,
  AttributeValue
} from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';
import { BaseEntity, EntityStatus } from '../schemas/table-schema';
import { CompositeKeyBuilder } from '../schemas/single-table-design';

export class SingleTableClient {
  private client: DynamoDBClient;
  private tableName: string;
  
  constructor(tableName: string = 'T-Developer-Main', region: string = 'us-east-1') {
    this.client = new DynamoDBClient({
      region: region,
      endpoint: process.env.DYNAMODB_ENDPOINT || undefined
    });
    this.tableName = tableName;
  }
  
  /**
   * Put item into table
   */
  async putItem<T extends BaseEntity>(item: T): Promise<T> {
    // Add timestamps
    const now = new Date().toISOString();
    if (!item.CreatedAt) {
      item.CreatedAt = now;
    }
    item.UpdatedAt = now;
    
    // Set default status if not provided
    if (!item.Status) {
      item.Status = EntityStatus.ACTIVE;
    }
    
    // Increment version
    if (item.Version === undefined) {
      item.Version = 1;
    } else {
      item.Version++;
    }
    
    const params: PutItemCommandInput = {
      TableName: this.tableName,
      Item: marshall(item, { removeUndefinedValues: true }),
      ConditionExpression: 'attribute_not_exists(PK)' // Prevent overwrites
    };
    
    try {
      await this.client.send(new PutItemCommand(params));
      return item;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        throw new Error(`Item already exists: ${item.PK}#${item.SK}`);
      }
      throw error;
    }
  }
  
  /**
   * Get item from table
   */
  async getItem<T extends BaseEntity>(pk: string, sk: string): Promise<T | null> {
    const params: GetItemCommandInput = {
      TableName: this.tableName,
      Key: marshall({ PK: pk, SK: sk })
    };
    
    const response = await this.client.send(new GetItemCommand(params));
    
    if (!response.Item) {
      return null;
    }
    
    return unmarshall(response.Item) as T;
  }
  
  /**
   * Query items by partition key
   */
  async query<T extends BaseEntity>(params: {
    pk?: string;
    skBeginsWith?: string;
    indexName?: string;
    gsi1pk?: string;
    gsi1sk?: string;
    gsi2pk?: string;
    gsi2sk?: string;
    gsi3pk?: string;
    status?: EntityStatus;
    entityType?: string;
    limit?: number;
    lastEvaluatedKey?: Record<string, AttributeValue>;
    scanIndexForward?: boolean;
  }): Promise<{
    items: T[];
    lastEvaluatedKey?: Record<string, AttributeValue>;
  }> {
    let queryParams: QueryCommandInput = {
      TableName: this.tableName,
      Limit: params.limit || 100,
      ScanIndexForward: params.scanIndexForward !== false,
      ExclusiveStartKey: params.lastEvaluatedKey
    };
    
    // Determine which index to use and build expression
    if (params.indexName === 'GSI1' && params.gsi1pk) {
      queryParams.IndexName = 'GSI1';
      queryParams.KeyConditionExpression = 'GSI1PK = :pk';
      queryParams.ExpressionAttributeValues = marshall({
        ':pk': params.gsi1pk
      });
      
      if (params.gsi1sk) {
        queryParams.KeyConditionExpression += ' AND begins_with(GSI1SK, :sk)';
        queryParams.ExpressionAttributeValues = marshall({
          ...unmarshall(queryParams.ExpressionAttributeValues!),
          ':sk': params.gsi1sk
        });
      }
    } else if (params.indexName === 'GSI2' && params.gsi2pk) {
      queryParams.IndexName = 'GSI2';
      queryParams.KeyConditionExpression = 'GSI2PK = :pk';
      queryParams.ExpressionAttributeValues = marshall({
        ':pk': params.gsi2pk
      });
      
      if (params.gsi2sk) {
        queryParams.KeyConditionExpression += ' AND begins_with(GSI2SK, :sk)';
        queryParams.ExpressionAttributeValues = marshall({
          ...unmarshall(queryParams.ExpressionAttributeValues!),
          ':sk': params.gsi2sk
        });
      }
    } else if (params.indexName === 'GSI3' && params.gsi3pk) {
      queryParams.IndexName = 'GSI3';
      queryParams.KeyConditionExpression = 'GSI3PK = :pk';
      queryParams.ExpressionAttributeValues = marshall({
        ':pk': params.gsi3pk
      });
    } else if (params.indexName === 'GSI4' && params.status) {
      queryParams.IndexName = 'GSI4';
      queryParams.KeyConditionExpression = '#status = :status';
      queryParams.ExpressionAttributeNames = { '#status': 'Status' };
      queryParams.ExpressionAttributeValues = marshall({
        ':status': params.status
      });
    } else if (params.indexName === 'GSI5' && params.entityType) {
      queryParams.IndexName = 'GSI5';
      queryParams.KeyConditionExpression = 'EntityType = :type';
      queryParams.ExpressionAttributeValues = marshall({
        ':type': params.entityType
      });
    } else if (params.pk) {
      queryParams.KeyConditionExpression = 'PK = :pk';
      queryParams.ExpressionAttributeValues = marshall({
        ':pk': params.pk
      });
      
      if (params.skBeginsWith) {
        queryParams.KeyConditionExpression += ' AND begins_with(SK, :sk)';
        queryParams.ExpressionAttributeValues = marshall({
          ...unmarshall(queryParams.ExpressionAttributeValues!),
          ':sk': params.skBeginsWith
        });
      }
    } else {
      throw new Error('Invalid query parameters: must specify PK or index-specific keys');
    }
    
    const response = await this.client.send(new QueryCommand(queryParams));
    
    return {
      items: (response.Items || []).map(item => unmarshall(item) as T),
      lastEvaluatedKey: response.LastEvaluatedKey
    };
  }
  
  /**
   * Update item
   */
  async updateItem<T extends BaseEntity>(
    pk: string,
    sk: string,
    updates: Partial<T>,
    condition?: string
  ): Promise<T | null> {
    const updateExpressions: string[] = [];
    const expressionAttributeNames: Record<string, string> = {};
    const expressionAttributeValues: Record<string, any> = {};
    
    // Always update UpdatedAt
    updates.UpdatedAt = new Date().toISOString();
    
    // Build update expression
    Object.entries(updates).forEach(([key, value]) => {
      if (key === 'PK' || key === 'SK') return; // Can't update keys
      
      const placeholder = `#${key}`;
      const valuePlaceholder = `:${key}`;
      
      updateExpressions.push(`${placeholder} = ${valuePlaceholder}`);
      expressionAttributeNames[placeholder] = key;
      expressionAttributeValues[valuePlaceholder] = value;
    });
    
    // Increment version
    updateExpressions.push('#version = if_not_exists(#version, :zero) + :one');
    expressionAttributeNames['#version'] = 'Version';
    expressionAttributeValues[':zero'] = 0;
    expressionAttributeValues[':one'] = 1;
    
    const params: UpdateItemCommandInput = {
      TableName: this.tableName,
      Key: marshall({ PK: pk, SK: sk }),
      UpdateExpression: `SET ${updateExpressions.join(', ')}`,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: marshall(expressionAttributeValues),
      ConditionExpression: condition || 'attribute_exists(PK)',
      ReturnValues: 'ALL_NEW'
    };
    
    try {
      const response = await this.client.send(new UpdateItemCommand(params));
      return response.Attributes ? unmarshall(response.Attributes) as T : null;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        return null;
      }
      throw error;
    }
  }
  
  /**
   * Delete item
   */
  async deleteItem(pk: string, sk: string): Promise<boolean> {
    const params: DeleteItemCommandInput = {
      TableName: this.tableName,
      Key: marshall({ PK: pk, SK: sk }),
      ConditionExpression: 'attribute_exists(PK)'
    };
    
    try {
      await this.client.send(new DeleteItemCommand(params));
      return true;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        return false;
      }
      throw error;
    }
  }
  
  /**
   * Batch write items
   */
  async batchWrite<T extends BaseEntity>(
    items: T[],
    operation: 'put' | 'delete' = 'put'
  ): Promise<void> {
    const chunks = this.chunkArray(items, 25); // DynamoDB limit
    
    for (const chunk of chunks) {
      const requests = chunk.map(item => {
        if (operation === 'put') {
          // Add timestamps for new items
          const now = new Date().toISOString();
          if (!item.CreatedAt) {
            item.CreatedAt = now;
          }
          item.UpdatedAt = now;
          
          return {
            PutRequest: {
              Item: marshall(item, { removeUndefinedValues: true })
            }
          };
        } else {
          return {
            DeleteRequest: {
              Key: marshall({ PK: item.PK, SK: item.SK })
            }
          };
        }
      });
      
      const params = {
        RequestItems: {
          [this.tableName]: requests
        }
      };
      
      await this.client.send(new BatchWriteItemCommand(params));
    }
  }
  
  /**
   * Batch get items
   */
  async batchGet<T extends BaseEntity>(
    keys: Array<{ pk: string; sk: string }>
  ): Promise<T[]> {
    const chunks = this.chunkArray(keys, 100); // DynamoDB limit
    const allItems: T[] = [];
    
    for (const chunk of chunks) {
      const params = {
        RequestItems: {
          [this.tableName]: {
            Keys: chunk.map(key => marshall({ PK: key.pk, SK: key.sk }))
          }
        }
      };
      
      const response = await this.client.send(new BatchGetItemCommand(params));
      const items = response.Responses?.[this.tableName] || [];
      allItems.push(...items.map(item => unmarshall(item) as T));
    }
    
    return allItems;
  }
  
  /**
   * Transaction write
   */
  async transactWrite(transactions: Array<{
    type: 'put' | 'update' | 'delete' | 'condition';
    item?: BaseEntity;
    key?: { pk: string; sk: string };
    updates?: Partial<BaseEntity>;
    condition?: string;
  }>): Promise<void> {
    const transactItems = transactions.map(tx => {
      if (tx.type === 'put' && tx.item) {
        // Add timestamps
        const now = new Date().toISOString();
        if (!tx.item.CreatedAt) {
          tx.item.CreatedAt = now;
        }
        tx.item.UpdatedAt = now;
        
        return {
          Put: {
            TableName: this.tableName,
            Item: marshall(tx.item, { removeUndefinedValues: true }),
            ConditionExpression: 'attribute_not_exists(PK)'
          }
        };
      } else if (tx.type === 'update' && tx.key && tx.updates) {
        const updateExpressions: string[] = [];
        const expressionAttributeNames: Record<string, string> = {};
        const expressionAttributeValues: Record<string, any> = {};
        
        // Always update UpdatedAt
        tx.updates.UpdatedAt = new Date().toISOString();
        
        Object.entries(tx.updates).forEach(([key, value]) => {
          if (key === 'PK' || key === 'SK') return;
          
          const placeholder = `#${key}`;
          const valuePlaceholder = `:${key}`;
          
          updateExpressions.push(`${placeholder} = ${valuePlaceholder}`);
          expressionAttributeNames[placeholder] = key;
          expressionAttributeValues[valuePlaceholder] = value;
        });
        
        return {
          Update: {
            TableName: this.tableName,
            Key: marshall({ PK: tx.key.pk, SK: tx.key.sk }),
            UpdateExpression: `SET ${updateExpressions.join(', ')}`,
            ExpressionAttributeNames: expressionAttributeNames,
            ExpressionAttributeValues: marshall(expressionAttributeValues),
            ConditionExpression: tx.condition || 'attribute_exists(PK)'
          }
        };
      } else if (tx.type === 'delete' && tx.key) {
        return {
          Delete: {
            TableName: this.tableName,
            Key: marshall({ PK: tx.key.pk, SK: tx.key.sk }),
            ConditionExpression: tx.condition || 'attribute_exists(PK)'
          }
        };
      } else if (tx.type === 'condition' && tx.key) {
        return {
          ConditionCheck: {
            TableName: this.tableName,
            Key: marshall({ PK: tx.key.pk, SK: tx.key.sk }),
            ConditionExpression: tx.condition || 'attribute_exists(PK)'
          }
        };
      }
      
      throw new Error(`Invalid transaction type: ${tx.type}`);
    });
    
    await this.client.send(new TransactWriteItemsCommand({
      TransactItems: transactItems
    }));
  }
  
  /**
   * Scan table (use sparingly)
   */
  async scan<T extends BaseEntity>(params: {
    filter?: string;
    expressionAttributeNames?: Record<string, string>;
    expressionAttributeValues?: Record<string, any>;
    limit?: number;
    lastEvaluatedKey?: Record<string, AttributeValue>;
  } = {}): Promise<{
    items: T[];
    lastEvaluatedKey?: Record<string, AttributeValue>;
  }> {
    const scanParams = {
      TableName: this.tableName,
      FilterExpression: params.filter,
      ExpressionAttributeNames: params.expressionAttributeNames,
      ExpressionAttributeValues: params.expressionAttributeValues 
        ? marshall(params.expressionAttributeValues) 
        : undefined,
      Limit: params.limit || 100,
      ExclusiveStartKey: params.lastEvaluatedKey
    };
    
    const response = await this.client.send(new ScanCommand(scanParams));
    
    return {
      items: (response.Items || []).map(item => unmarshall(item) as T),
      lastEvaluatedKey: response.LastEvaluatedKey
    };
  }
  
  /**
   * Helper to chunk arrays
   */
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}

// Export singleton instance
export const singleTableClient = new SingleTableClient();