// backend/src/data/transactions/optimistic-lock.ts
import { DynamoDBDocumentClient, GetCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';

export interface OptimisticLockConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

export class OptimisticLockManager {
  private config: OptimisticLockConfig = {
    maxRetries: 3,
    baseDelayMs: 100,
    maxDelayMs: 1000
  };

  constructor(
    private docClient: DynamoDBDocumentClient,
    config?: Partial<OptimisticLockConfig>
  ) {
    this.config = { ...this.config, ...config };
  }

  async updateWithOptimisticLock<T>(
    tableName: string,
    key: any,
    updateFn: (current: T) => Partial<T>,
    options?: { versionField?: string }
  ): Promise<T> {
    const versionField = options?.versionField || 'Version';
    let attempt = 0;

    while (attempt < this.config.maxRetries) {
      try {
        // Get current item
        const getResult = await this.docClient.send(new GetCommand({
          TableName: tableName,
          Key: key
        }));

        if (!getResult.Item) {
          throw new Error('Item not found');
        }

        const currentItem = getResult.Item as T;
        const currentVersion = (currentItem as any)[versionField] || 0;
        const newVersion = currentVersion + 1;

        // Apply updates
        const updates = updateFn(currentItem);
        const updatedItem = { ...currentItem, ...updates, [versionField]: newVersion };

        // Build update expression
        const updateExpression = this.buildUpdateExpression(updates, versionField);

        // Conditional update
        await this.docClient.send(new UpdateCommand({
          TableName: tableName,
          Key: key,
          UpdateExpression: updateExpression.expression,
          ConditionExpression: `${versionField} = :currentVersion`,
          ExpressionAttributeNames: updateExpression.names,
          ExpressionAttributeValues: {
            ...updateExpression.values,
            ':currentVersion': currentVersion,
            ':newVersion': newVersion
          }
        }));

        return updatedItem;

      } catch (error: any) {
        if (error.name === 'ConditionalCheckFailedException') {
          attempt++;
          if (attempt >= this.config.maxRetries) {
            throw new Error('Optimistic lock failed after maximum retries');
          }
          
          // Exponential backoff with jitter
          const delay = Math.min(
            this.config.baseDelayMs * Math.pow(2, attempt) + Math.random() * 100,
            this.config.maxDelayMs
          );
          await this.delay(delay);
          continue;
        }
        throw error;
      }
    }

    throw new Error('Optimistic lock failed');
  }

  private buildUpdateExpression(updates: any, versionField: string) {
    const expression: string[] = [];
    const names: Record<string, string> = {};
    const values: Record<string, any> = {};

    Object.entries(updates).forEach(([key, value], index) => {
      if (key === versionField) return; // Skip version field
      
      const nameKey = `#attr${index}`;
      const valueKey = `:val${index}`;
      
      expression.push(`${nameKey} = ${valueKey}`);
      names[nameKey] = key;
      values[valueKey] = value;
    });

    // Add version update
    names[`#${versionField}`] = versionField;
    expression.push(`#${versionField} = :newVersion`);

    return {
      expression: `SET ${expression.join(', ')}`,
      names,
      values
    };
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}