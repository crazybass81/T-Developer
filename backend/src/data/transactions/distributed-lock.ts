/**
 * Distributed Lock Implementation for DynamoDB
 * Provides distributed locking mechanism for concurrent operations
 */

import { SingleTableClient } from '../dynamodb/single-table';
import { v4 as uuidv4 } from 'uuid';

export interface LockOptions {
  ttlMs?: number;
  retryDelayMs?: number;
  maxRetries?: number;
  enableLogging?: boolean;
}

export interface Lock {
  key: string;
  holder: string;
  acquiredAt: number;
  expiresAt: number;
  ttl: number;
}

export class DistributedLock {
  private client: SingleTableClient;
  private options: Required<LockOptions>;
  private instanceId: string;

  constructor(client: SingleTableClient, options: LockOptions = {}) {
    this.client = client;
    this.instanceId = uuidv4();
    this.options = {
      ttlMs: 30000, // 30 seconds
      retryDelayMs: 100,
      maxRetries: 10,
      enableLogging: false,
      ...options
    };
  }

  public async acquire(key: string, ttlMs?: number): Promise<boolean> {
    const actualTtl = ttlMs || this.options.ttlMs;
    const now = Date.now();
    const expiresAt = now + actualTtl;
    
    const lockItem = {
      PK: `LOCK#${key}`,
      SK: 'LOCK',
      EntityType: 'DISTRIBUTED_LOCK',
      EntityId: key,
      Status: 'ACTIVE',
      CreatedAt: new Date(now).toISOString(),
      UpdatedAt: new Date(now).toISOString(),
      TTL: Math.floor(expiresAt / 1000),
      Data: JSON.stringify({
        key,
        holder: this.instanceId,
        acquiredAt: now,
        expiresAt,
        ttl: actualTtl
      })
    };

    try {
      await this.client.putItem(lockItem);
      if (this.options.enableLogging) {
        console.log(`Lock acquired: ${key} by ${this.instanceId}`);
      }
      return true;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        return false; // Lock already exists
      }
      throw error;
    }
  }

  public async release(key: string): Promise<boolean> {
    try {
      const success = await this.client.deleteItem(`LOCK#${key}`, 'LOCK');
      if (this.options.enableLogging && success) {
        console.log(`Lock released: ${key} by ${this.instanceId}`);
      }
      return success;
    } catch (error) {
      console.error(`Failed to release lock ${key}:`, error);
      return false;
    }
  }

  public async withLock<T>(
    key: string,
    operation: () => Promise<T>,
    ttlMs?: number
  ): Promise<T> {
    let retryCount = 0;
    
    while (retryCount < this.options.maxRetries) {
      const acquired = await this.acquire(key, ttlMs);
      
      if (acquired) {
        try {
          return await operation();
        } finally {
          await this.release(key);
        }
      }
      
      retryCount++;
      if (retryCount < this.options.maxRetries) {
        await this.delay(this.options.retryDelayMs * retryCount);
      }
    }
    
    throw new Error(`Failed to acquire lock ${key} after ${this.options.maxRetries} attempts`);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}