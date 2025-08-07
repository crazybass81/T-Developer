/**
 * Transaction Manager for DynamoDB
 * Provides ACID transaction support for complex operations
 */

import { SingleTableClient } from '../dynamodb/single-table';
import { BaseEntity } from '../entities/base.entity';
import { v4 as uuidv4 } from 'uuid';

export interface TransactionItem {
  type: 'put' | 'update' | 'delete' | 'condition';
  entity?: BaseEntity;
  key?: { pk: string; sk: string };
  updates?: Record<string, any>;
  condition?: string;
  tableName?: string;
}

export interface TransactionOptions {
  maxRetries?: number;
  retryDelayMs?: number;
  timeoutMs?: number;
  enableLogging?: boolean;
}

export interface TransactionResult {
  success: boolean;
  transactionId: string;
  executionTime: number;
  itemCount: number;
  error?: string;
  retryCount: number;
}

export class TransactionError extends Error {
  public transactionId: string;
  public retryCount: number;
  public originalError: any;

  constructor(
    message: string,
    transactionId: string,
    retryCount: number = 0,
    originalError?: any
  ) {
    super(message);
    this.name = 'TransactionError';
    this.transactionId = transactionId;
    this.retryCount = retryCount;
    this.originalError = originalError;
  }
}

export class TransactionManager {
  private client: SingleTableClient;
  private options: Required<TransactionOptions>;

  constructor(client: SingleTableClient, options: TransactionOptions = {}) {
    this.client = client;
    this.options = {
      maxRetries: 3,
      retryDelayMs: 100,
      timeoutMs: 30000,
      enableLogging: true,
      ...options
    };
  }

  /**
   * Execute a transaction with retry logic
   */
  public async execute(
    items: TransactionItem[],
    options: Partial<TransactionOptions> = {}
  ): Promise<TransactionResult> {
    const transactionId = uuidv4();
    const mergedOptions = { ...this.options, ...options };
    const startTime = Date.now();
    
    let retryCount = 0;
    let lastError: any;

    if (items.length === 0) {
      throw new TransactionError('No transaction items provided', transactionId);
    }

    if (items.length > 100) {
      throw new TransactionError(
        'Too many transaction items (max 100)',
        transactionId
      );
    }

    while (retryCount <= mergedOptions.maxRetries) {
      try {
        if (mergedOptions.enableLogging) {
          console.log(`[Transaction ${transactionId}] Starting attempt ${retryCount + 1}`);
        }

        // Check for timeout
        if (Date.now() - startTime > mergedOptions.timeoutMs) {
          throw new TransactionError(
            'Transaction timeout',
            transactionId,
            retryCount
          );
        }

        // Prepare transaction items
        const transactItems = this.prepareTransactionItems(items);

        // Execute the transaction
        await this.client.transactWrite(transactItems);

        const executionTime = Date.now() - startTime;

        if (mergedOptions.enableLogging) {
          console.log(
            `[Transaction ${transactionId}] Completed successfully in ${executionTime}ms`
          );
        }

        return {
          success: true,
          transactionId,
          executionTime,
          itemCount: items.length,
          retryCount
        };

      } catch (error: any) {
        lastError = error;
        retryCount++;

        if (mergedOptions.enableLogging) {
          console.log(
            `[Transaction ${transactionId}] Attempt ${retryCount} failed: ${error.message}`
          );
        }

        // Check if we should retry
        if (this.shouldRetry(error) && retryCount <= mergedOptions.maxRetries) {
          await this.delay(mergedOptions.retryDelayMs * retryCount);
          continue;
        }

        break;
      }
    }

    // Transaction failed after all retries
    const executionTime = Date.now() - startTime;
    const errorMessage = lastError?.message || 'Unknown error';

    if (mergedOptions.enableLogging) {
      console.error(
        `[Transaction ${transactionId}] Failed after ${retryCount} attempts: ${errorMessage}`
      );
    }

    return {
      success: false,
      transactionId,
      executionTime,
      itemCount: items.length,
      error: errorMessage,
      retryCount: retryCount - 1
    };
  }

  /**
   * Execute multiple transactions in sequence
   */
  public async executeSequential(
    transactionGroups: TransactionItem[][],
    options: Partial<TransactionOptions> = {}
  ): Promise<TransactionResult[]> {
    const results: TransactionResult[] = [];

    for (const [index, items] of transactionGroups.entries()) {
      try {
        const result = await this.execute(items, options);
        results.push(result);

        // If any transaction fails, stop execution
        if (!result.success) {
          throw new TransactionError(
            `Sequential transaction ${index} failed: ${result.error}`,
            result.transactionId
          );
        }
      } catch (error) {
        // Add error result for failed transaction
        results.push({
          success: false,
          transactionId: uuidv4(),
          executionTime: 0,
          itemCount: items.length,
          error: error instanceof Error ? error.message : 'Unknown error',
          retryCount: 0
        });
        break;
      }
    }

    return results;
  }

  /**
   * Execute multiple transactions in parallel
   */
  public async executeParallel(
    transactionGroups: TransactionItem[][],
    options: Partial<TransactionOptions> = {}
  ): Promise<TransactionResult[]> {
    const promises = transactionGroups.map(items => 
      this.execute(items, options)
    );

    return await Promise.all(promises);
  }

  /**
   * Create a transaction builder for complex operations
   */
  public createBuilder(): TransactionBuilder {
    return new TransactionBuilder(this);
  }

  /**
   * Prepare transaction items for DynamoDB
   */
  private prepareTransactionItems(items: TransactionItem[]): any[] {
    return items.map(item => this.prepareTransactionItem(item));
  }

  /**
   * Prepare a single transaction item
   */
  private prepareTransactionItem(item: TransactionItem): any {
    switch (item.type) {
      case 'put':
        if (!item.entity) {
          throw new Error('Entity required for put operation');
        }
        return {
          Put: {
            TableName: item.tableName || this.client['tableName'],
            Item: item.entity.toDynamoDBItem(),
            ConditionExpression: 'attribute_not_exists(PK)'
          }
        };

      case 'update':
        if (!item.key || !item.updates) {
          throw new Error('Key and updates required for update operation');
        }

        const updateExpressions: string[] = [];
        const expressionAttributeNames: Record<string, string> = {};
        const expressionAttributeValues: Record<string, any> = {};

        Object.entries(item.updates).forEach(([key, value]) => {
          if (key === 'PK' || key === 'SK') return;
          
          const placeholder = `#${key}`;
          const valuePlaceholder = `:${key}`;
          
          updateExpressions.push(`${placeholder} = ${valuePlaceholder}`);
          expressionAttributeNames[placeholder] = key;
          expressionAttributeValues[valuePlaceholder] = value;
        });

        return {
          Update: {
            TableName: item.tableName || this.client['tableName'],
            Key: {
              PK: { S: item.key.pk },
              SK: { S: item.key.sk }
            },
            UpdateExpression: `SET ${updateExpressions.join(', ')}`,
            ExpressionAttributeNames: expressionAttributeNames,
            ExpressionAttributeValues: expressionAttributeValues,
            ConditionExpression: item.condition || 'attribute_exists(PK)'
          }
        };

      case 'delete':
        if (!item.key) {
          throw new Error('Key required for delete operation');
        }
        return {
          Delete: {
            TableName: item.tableName || this.client['tableName'],
            Key: {
              PK: { S: item.key.pk },
              SK: { S: item.key.sk }
            },
            ConditionExpression: item.condition || 'attribute_exists(PK)'
          }
        };

      case 'condition':
        if (!item.key || !item.condition) {
          throw new Error('Key and condition required for condition check');
        }
        return {
          ConditionCheck: {
            TableName: item.tableName || this.client['tableName'],
            Key: {
              PK: { S: item.key.pk },
              SK: { S: item.key.sk }
            },
            ConditionExpression: item.condition
          }
        };

      default:
        throw new Error(`Unknown transaction type: ${item.type}`);
    }
  }

  /**
   * Determine if error is retryable
   */
  private shouldRetry(error: any): boolean {
    const retryableErrors = [
      'ProvisionedThroughputExceededException',
      'ThrottlingException',
      'ServiceUnavailableException',
      'InternalServerError'
    ];

    return retryableErrors.some(errorType => 
      error.name === errorType || error.message?.includes(errorType)
    );
  }

  /**
   * Delay helper for retries
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Transaction Builder for fluent API
 */
export class TransactionBuilder {
  private items: TransactionItem[] = [];
  private manager: TransactionManager;

  constructor(manager: TransactionManager) {
    this.manager = manager;
  }

  /**
   * Add a put operation
   */
  public put(entity: BaseEntity): this {
    this.items.push({ type: 'put', entity });
    return this;
  }

  /**
   * Add an update operation
   */
  public update(
    key: { pk: string; sk: string },
    updates: Record<string, any>,
    condition?: string
  ): this {
    this.items.push({ type: 'update', key, updates, condition });
    return this;
  }

  /**
   * Add a delete operation
   */
  public delete(key: { pk: string; sk: string }, condition?: string): this {
    this.items.push({ type: 'delete', key, condition });
    return this;
  }

  /**
   * Add a condition check
   */
  public condition(key: { pk: string; sk: string }, condition: string): this {
    this.items.push({ type: 'condition', key, condition });
    return this;
  }

  /**
   * Execute the built transaction
   */
  public async execute(
    options: Partial<TransactionOptions> = {}
  ): Promise<TransactionResult> {
    if (this.items.length === 0) {
      throw new Error('No transaction items to execute');
    }

    return await this.manager.execute([...this.items], options);
  }

  /**
   * Get the current items (for inspection)
   */
  public getItems(): TransactionItem[] {
    return [...this.items];
  }

  /**
   * Clear all items
   */
  public clear(): this {
    this.items = [];
    return this;
  }

  /**
   * Get item count
   */
  public getItemCount(): number {
    return this.items.length;
  }
}