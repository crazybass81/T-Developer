import Redis from 'ioredis';

export interface CacheService {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl?: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}

export class RedisCacheService implements CacheService {
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      maxRetriesPerRequest: 3
    });
  }
  
  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await this.redis.get(key);
      return value ? JSON.parse(value) : null;
    } catch {
      return null;
    }
  }
  
  async set<T>(key: string, value: T, ttl: number = 3600): Promise<void> {
    try {
      await this.redis.setex(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }
  
  async delete(key: string): Promise<void> {
    await this.redis.del(key);
  }
  
  async clear(): Promise<void> {
    await this.redis.flushall();
  }
}

export class MemoryCacheService implements CacheService {
  private cache = new Map<string, { value: any; expires: number }>();
  
  async get<T>(key: string): Promise<T | null> {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  async set<T>(key: string, value: T, ttl: number = 3600): Promise<void> {
    this.cache.set(key, {
      value,
      expires: Date.now() + (ttl * 1000)
    });
  }
  
  async delete(key: string): Promise<void> {
    this.cache.delete(key);
  }
  
  async clear(): Promise<void> {
    this.cache.clear();
  }
}