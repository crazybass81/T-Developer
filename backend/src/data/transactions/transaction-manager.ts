// backend/src/data/transactions/transaction-manager.ts
import { DynamoDBDocumentClient, TransactWriteCommand, TransactGetCommand } from '@aws-sdk/lib-dynamodb';

export interface TransactionItem {
  operation: 'Put' | 'Update' | 'Delete' | 'ConditionCheck';
  tableName: string;
  key?: any;
  item?: any;
  updateExpression?: string;
  conditionExpression?: string;
  expressionAttributeNames?: Record<string, string>;
  expressionAttributeValues?: Record<string, any>;
}

export interface TransactionResult {
  success: boolean;
  transactionId: string;
  itemsProcessed: number;
  duration: number;
  error?: string;
}

export class TransactionManager {
  private activeTransactions = new Map<string, TransactionItem[]>();

  constructor(private docClient: DynamoDBDocumentClient) {}

  async executeTransaction(items: TransactionItem[]): Promise<TransactionResult> {
    const transactionId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      if (items.length > 25) {
        throw new Error('DynamoDB transaction limit is 25 items');
      }

      const transactItems = items.map(item => this.buildTransactItem(item));
      
      await this.docClient.send(new TransactWriteCommand({
        TransactItems: transactItems,
        ClientRequestToken: transactionId
      }));

      return {
        success: true,
        transactionId,
        itemsProcessed: items.length,
        duration: Date.now() - startTime
      };

    } catch (error) {
      return {
        success: false,
        transactionId,
        itemsProcessed: 0,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async readTransaction(keys: Array<{ tableName: string; key: any }>): Promise<any[]> {
    if (keys.length > 25) {
      throw new Error('DynamoDB transaction read limit is 25 items');
    }

    const transactItems = keys.map(({ tableName, key }) => ({
      Get: { TableName: tableName, Key: key }
    }));

    const result = await this.docClient.send(new TransactGetCommand({
      TransactItems: transactItems
    }));

    return result.Responses?.map(response => response.Item) || [];
  }

  private buildTransactItem(item: TransactionItem): any {
    const base = { TableName: item.tableName };

    switch (item.operation) {
      case 'Put':
        return {
          Put: {
            ...base,
            Item: item.item,
            ConditionExpression: item.conditionExpression,
            ExpressionAttributeNames: item.expressionAttributeNames,
            ExpressionAttributeValues: item.expressionAttributeValues
          }
        };

      case 'Update':
        return {
          Update: {
            ...base,
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
            ...base,
            Key: item.key,
            ConditionExpression: item.conditionExpression,
            ExpressionAttributeNames: item.expressionAttributeNames,
            ExpressionAttributeValues: item.expressionAttributeValues
          }
        };

      case 'ConditionCheck':
        return {
          ConditionCheck: {
            ...base,
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
}