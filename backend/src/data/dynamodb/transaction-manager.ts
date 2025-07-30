import { DynamoDBDocumentClient, TransactWriteCommand, TransactGetCommand } from '@aws-sdk/lib-dynamodb';
import crypto from 'crypto';

export interface TransactionItem {
  operation: 'Put' | 'Update' | 'Delete';
  tableName: string;
  key?: any;
  item?: any;
  updateExpression?: string;
  conditionExpression?: string;
  expressionAttributeNames?: Record<string, string>;
  expressionAttributeValues?: Record<string, any>;
}

export class TransactionManager {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  // Execute transaction
  async executeTransaction(items: TransactionItem[]): Promise<void> {
    const transactItems = items.map(item => this.buildTransactItem(item));
    
    await this.docClient.send(new TransactWriteCommand({
      TransactItems: transactItems,
      ClientRequestToken: crypto.randomUUID()
    }));
  }
  
  private buildTransactItem(item: TransactionItem): any {
    switch (item.operation) {
      case 'Put':
        return {
          Put: {
            TableName: item.tableName,
            Item: item.item,
            ConditionExpression: item.conditionExpression,
            ExpressionAttributeNames: item.expressionAttributeNames,
            ExpressionAttributeValues: item.expressionAttributeValues
          }
        };
        
      case 'Update':
        return {
          Update: {
            TableName: item.tableName,
            Key: item.key,
            UpdateExpression: item.updateExpression,
            ConditionExpression: item.conditionExpression,
            ExpressionAttributeNames: item.expressionAttributeNames,
            ExpressionAttributeValues: item.expressionAttributeValues
          }
        };
        
      case 'Delete':
        return {
          Delete: {
            TableName: item.tableName,
            Key: item.key,
            ConditionExpression: item.conditionExpression,
            ExpressionAttributeNames: item.expressionAttributeNames,
            ExpressionAttributeValues: item.expressionAttributeValues
          }
        };
        
      default:
        throw new Error(`Unsupported operation: ${item.operation}`);
    }
  }
  
  // Optimistic locking
  async optimisticUpdate(
    tableName: string,
    key: any,
    updateFn: (current: any) => any,
    maxRetries: number = 3
  ): Promise<any> {
    let attempts = 0;
    
    while (attempts < maxRetries) {
      try {
        // Get current item
        const current: any = await this.docClient.send({
          name: 'GetCommand',
          input: { TableName: tableName, Key: key }
        } as any);
        
        if (!current.Item) {
          throw new Error('Item not found');
        }
        
        const currentVersion = current.Item.version || 0;
        const updated = updateFn(current.Item);
        
        // Update with version check
        await this.docClient.send({
          name: 'UpdateCommand',
          input: {
            TableName: tableName,
            Key: key,
            UpdateExpression: 'SET #data = :data, #version = :newVersion',
            ConditionExpression: '#version = :currentVersion',
            ExpressionAttributeNames: {
              '#data': 'data',
              '#version': 'version'
            },
            ExpressionAttributeValues: {
              ':data': updated,
              ':newVersion': currentVersion + 1,
              ':currentVersion': currentVersion
            }
          }
        } as any);
        
        return updated;
        
      } catch (error: any) {
        if (error.name === 'ConditionalCheckFailedException') {
          attempts++;
          await this.delay(Math.pow(2, attempts) * 100); // Exponential backoff
          continue;
        }
        throw error;
      }
    }
    
    throw new Error('Optimistic lock failed after max retries');
  }
  
  // Distributed lock
  async acquireLock(
    lockId: string,
    ttl: number = 30000
  ): Promise<{ acquired: boolean; lockToken?: string }> {
    const lockToken = crypto.randomUUID();
    const expiresAt = Date.now() + ttl;
    
    try {
      await this.docClient.send({
        name: 'PutCommand',
        input: {
          TableName: 'T-Developer-Locks',
          Item: {
            PK: `LOCK#${lockId}`,
            SK: 'ACTIVE',
            lockToken,
            expiresAt,
            ttl: Math.floor(expiresAt / 1000)
          },
          ConditionExpression: 'attribute_not_exists(PK) OR expiresAt < :now',
          ExpressionAttributeValues: {
            ':now': Date.now()
          }
        }
      } as any);
      
      return { acquired: true, lockToken };
      
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        return { acquired: false };
      }
      throw error;
    }
  }
  
  // Release lock
  async releaseLock(lockId: string, lockToken: string): Promise<void> {
    await this.docClient.send({
      name: 'DeleteCommand',
      input: {
        TableName: 'T-Developer-Locks',
        Key: {
          PK: `LOCK#${lockId}`,
          SK: 'ACTIVE'
        },
        ConditionExpression: 'lockToken = :token',
        ExpressionAttributeValues: {
          ':token': lockToken
        }
      }
    } as any);
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}