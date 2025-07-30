import { RedisClient } from './redis/client';

export interface CacheOptions {
  ttl?: number;
  prefix?: string;
  serialize?: boolean;
}

export class CacheManager {
  private redis: RedisClient;
  private defaultTTL: number = 3600; // 1 hour
  private keyPrefix: string = 't-dev:';
  
  constructor(redis: RedisClient) {
    this.redis = redis;
  }
  
  private buildKey(key: string, prefix?: string): string {
    const actualPrefix = prefix || this.keyPrefix;
    return `${actualPrefix}${key}`;
  }
  
  // Multi-level caching
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.buildKey(key, options?.prefix);
    return await this.redis.get<T>(fullKey);
  }
  
  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void> {
    const fullKey = this.buildKey(key, options?.prefix);
    const ttl = options?.ttl || this.defaultTTL;
    await this.redis.set(fullKey, value, ttl);
  }
  
  async del(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.buildKey(key, options?.prefix);
    await this.redis.del(fullKey);
  }
  
  // Cache-aside pattern
  async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    options?: CacheOptions
  ): Promise<T> {
    const cached = await this.get<T>(key, options);
    
    if (cached !== null) {
      return cached;
    }
    
    const value = await fetcher();
    await this.set(key, value, options);
    
    return value;
  }
  
  // Batch operations
  async mget<T>(keys: string[], options?: CacheOptions): Promise<(T | null)[]> {
    const fullKeys = keys.map(key => this.buildKey(key, options?.prefix));
    const client = this.redis.getClient();
    const values = await client.mget(...fullKeys);
    
    return values.map(value => value ? JSON.parse(value) : null);
  }
  
  async mset(items: Array<{ key: string; value: any }>, options?: CacheOptions): Promise<void> {
    const client = this.redis.getClient();
    const pipeline = client.pipeline();
    const ttl = options?.ttl || this.defaultTTL;
    
    for (const item of items) {
      const fullKey = this.buildKey(item.key, options?.prefix);
      pipeline.setex(fullKey, ttl, JSON.stringify(item.value));
    }
    
    await pipeline.exec();
  }
  
  // Pattern-based operations
  async deletePattern(pattern: string, options?: CacheOptions): Promise<number> {
    const fullPattern = this.buildKey(pattern, options?.prefix);
    const client = this.redis.getClient();
    
    const keys = await client.keys(fullPattern);
    if (keys.length === 0) return 0;
    
    await client.del(...keys);
    return keys.length;
  }
  
  // Cache warming
  async warmCache<T>(
    keys: string[],
    fetcher: (key: string) => Promise<T>,
    options?: CacheOptions
  ): Promise<void> {
    const items = await Promise.all(
      keys.map(async (key) => ({
        key,
        value: await fetcher(key)
      }))
    );
    
    await this.mset(items, options);
  }
  
  // Cache statistics
  async getStats(): Promise<{
    hitRate: number;
    missRate: number;
    totalKeys: number;
    memoryUsage: string;
  }> {
    const client = this.redis.getClient();
    const info = await client.info('stats');
    const keyspace = await client.info('keyspace');
    
    // Parse Redis info
    const stats = this.parseRedisInfo(info);
    const keys = this.parseKeyspace(keyspace);
    
    return {
      hitRate: stats.keyspace_hits / (stats.keyspace_hits + stats.keyspace_misses) || 0,
      missRate: stats.keyspace_misses / (stats.keyspace_hits + stats.keyspace_misses) || 0,
      totalKeys: keys.total || 0,
      memoryUsage: stats.used_memory_human || '0B'
    };
  }
  
  private parseRedisInfo(info: string): any {
    const stats: any = {};
    info.split('\r\n').forEach(line => {
      if (line.includes(':')) {
        const [key, value] = line.split(':');
        stats[key] = isNaN(Number(value)) ? value : Number(value);
      }
    });
    return stats;
  }
  
  private parseKeyspace(keyspace: string): any {
    const keys: any = {};
    keyspace.split('\r\n').forEach(line => {
      if (line.startsWith('db0:')) {
        const match = line.match(/keys=(\d+)/);
        if (match) keys.total = parseInt(match[1]);
      }
    });
    return keys;
  }
}