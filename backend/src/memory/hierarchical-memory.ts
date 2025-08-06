import Redis from 'ioredis';

interface MemoryItem {
  key: string;
  value: any;
  importance: 'low' | 'normal' | 'high' | 'critical';
  accessCount: number;
  lastAccessed: Date;
  createdAt: Date;
}

abstract class MemoryLayer {
  abstract get(key: string): Promise<any>;
  abstract set(key: string, value: any, ttl?: number): Promise<void>;
  abstract delete(key: string): Promise<void>;
  abstract clear(): Promise<void>;
}

class WorkingMemory extends MemoryLayer {
  private memory = new Map<string, MemoryItem>();
  private maxSize: number;

  constructor(maxSize = 1000) {
    super();
    this.maxSize = maxSize;
  }

  async get(key: string): Promise<any> {
    const item = this.memory.get(key);
    if (item) {
      item.accessCount++;
      item.lastAccessed = new Date();
      return item.value;
    }
    return null;
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    if (this.memory.size >= this.maxSize) {
      await this.evictLRU();
    }

    this.memory.set(key, {
      key,
      value,
      importance: 'normal',
      accessCount: 1,
      lastAccessed: new Date(),
      createdAt: new Date(),
    });

    if (ttl) {
      setTimeout(() => this.delete(key), ttl * 1000);
    }
  }

  async delete(key: string): Promise<void> {
    this.memory.delete(key);
  }

  async clear(): Promise<void> {
    this.memory.clear();
  }

  private async evictLRU(): Promise<void> {
    let lruKey = '';
    let oldestAccess = new Date();

    for (const [key, item] of this.memory) {
      if (item.lastAccessed < oldestAccess) {
        oldestAccess = item.lastAccessed;
        lruKey = key;
      }
    }

    if (lruKey) {
      this.memory.delete(lruKey);
    }
  }
}

class ShortTermMemory extends MemoryLayer {
  private redis: Redis;

  constructor() {
    super();
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
    });
  }

  async get(key: string): Promise<any> {
    const value = await this.redis.get(key);
    return value ? JSON.parse(value) : null;
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    const serialized = JSON.stringify(value);
    if (ttl) {
      await this.redis.setex(key, ttl, serialized);
    } else {
      await this.redis.set(key, serialized);
    }
  }

  async delete(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async clear(): Promise<void> {
    await this.redis.flushdb();
  }
}

export class HierarchicalMemorySystem {
  private workingMemory: WorkingMemory;
  private shortTermMemory: ShortTermMemory;

  constructor() {
    this.workingMemory = new WorkingMemory();
    this.shortTermMemory = new ShortTermMemory();
  }

  async remember(key: string, value: any, importance: 'low' | 'normal' | 'high' | 'critical' = 'normal'): Promise<void> {
    switch (importance) {
      case 'critical':
        await this.workingMemory.set(key, value);
        await this.shortTermMemory.set(key, value, 86400); // 1일
        break;
      case 'high':
        await this.shortTermMemory.set(key, value, 3600); // 1시간
        break;
      default:
        await this.workingMemory.set(key, value);
        break;
    }
  }

  async recall(key: string): Promise<any> {
    // 계층적 검색
    let value = await this.workingMemory.get(key);
    if (value !== null) return value;

    value = await this.shortTermMemory.get(key);
    if (value !== null) {
      await this.workingMemory.set(key, value);
      return value;
    }

    return null;
  }

  async forget(key: string): Promise<void> {
    await Promise.all([
      this.workingMemory.delete(key),
      this.shortTermMemory.delete(key),
    ]);
  }

  async getStats(): Promise<any> {
    return {
      workingMemorySize: (this.workingMemory as any).memory.size,
      timestamp: new Date().toISOString(),
    };
  }
}