// backend/src/data/transactions/distributed-lock.ts
import { DynamoDBDocumentClient, PutCommand, DeleteCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';

export interface LockOptions {
  ttl?: number; // seconds
  retryDelay?: number; // milliseconds
  maxRetries?: number;
}

export interface Lock {
  id: string;
  resource: string;
  owner: string;
  acquiredAt: Date;
  expiresAt: Date;
  release: () => Promise<void>;
  extend: (additionalTtl: number) => Promise<void>;
}

export class DistributedLockManager {
  private readonly lockTableName: string;
  private readonly instanceId: string;

  constructor(
    private docClient: DynamoDBDocumentClient,
    lockTableName: string = 'T-Developer-Locks'
  ) {
    this.lockTableName = lockTableName;
    this.instanceId = process.env.INSTANCE_ID || `instance-${Date.now()}`;
  }

  async acquireLock(resource: string, options: LockOptions = {}): Promise<Lock | null> {
    const {
      ttl = 30,
      retryDelay = 100,
      maxRetries = 10
    } = options;

    const lockId = crypto.randomUUID();
    const now = new Date();
    const expiresAt = new Date(now.getTime() + ttl * 1000);

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        await this.docClient.send(new PutCommand({
          TableName: this.lockTableName,
          Item: {
            PK: `LOCK#${resource}`,
            SK: 'ACTIVE',
            LockId: lockId,
            Owner: this.instanceId,
            AcquiredAt: now.toISOString(),
            ExpiresAt: expiresAt.toISOString(),
            TTL: Math.floor(expiresAt.getTime() / 1000)
          },
          ConditionExpression: 'attribute_not_exists(PK) OR ExpiresAt < :now',
          ExpressionAttributeValues: {
            ':now': now.toISOString()
          }
        }));

        return {
          id: lockId,
          resource,
          owner: this.instanceId,
          acquiredAt: now,
          expiresAt,
          release: () => this.releaseLock(resource, lockId),
          extend: (additionalTtl: number) => this.extendLock(resource, lockId, additionalTtl)
        };

      } catch (error: any) {
        if (error.name === 'ConditionalCheckFailedException') {
          // Lock is held by another process
          if (attempt < maxRetries - 1) {
            await this.delay(retryDelay * (attempt + 1));
            continue;
          }
          return null; // Failed to acquire lock
        }
        throw error;
      }
    }

    return null;
  }

  async releaseLock(resource: string, lockId: string): Promise<void> {
    try {
      await this.docClient.send(new DeleteCommand({
        TableName: this.lockTableName,
        Key: {
          PK: `LOCK#${resource}`,
          SK: 'ACTIVE'
        },
        ConditionExpression: 'LockId = :lockId AND Owner = :owner',
        ExpressionAttributeValues: {
          ':lockId': lockId,
          ':owner': this.instanceId
        }
      }));
    } catch (error: any) {
      if (error.name !== 'ConditionalCheckFailedException') {
        throw error;
      }
      // Lock was already released or expired
    }
  }

  async extendLock(resource: string, lockId: string, additionalTtl: number): Promise<void> {
    const newExpiresAt = new Date(Date.now() + additionalTtl * 1000);

    await this.docClient.send(new UpdateCommand({
      TableName: this.lockTableName,
      Key: {
        PK: `LOCK#${resource}`,
        SK: 'ACTIVE'
      },
      UpdateExpression: 'SET ExpiresAt = :expiresAt, TTL = :ttl',
      ConditionExpression: 'LockId = :lockId AND Owner = :owner',
      ExpressionAttributeValues: {
        ':lockId': lockId,
        ':owner': this.instanceId,
        ':expiresAt': newExpiresAt.toISOString(),
        ':ttl': Math.floor(newExpiresAt.getTime() / 1000)
      }
    }));
  }

  async withLock<T>(
    resource: string,
    operation: () => Promise<T>,
    options: LockOptions = {}
  ): Promise<T> {
    const lock = await this.acquireLock(resource, options);
    
    if (!lock) {
      throw new Error(`Failed to acquire lock for resource: ${resource}`);
    }

    try {
      return await operation();
    } finally {
      await lock.release();
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}