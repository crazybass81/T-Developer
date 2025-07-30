import Redis from 'ioredis';

export interface CacheOptions {
  ttl?: number;
  prefix?: string;
}

export class RedisCache {
  private redis: Redis;
  private defaultTTL = 3600; // 1 hour
  
  constructor(config: { host: string; port: number; password?: string }) {
    this.redis = new Redis({
      host: config.host,
      port: config.port,
      password: config.password,
      maxRetriesPerRequest: 3,
      lazyConnect: true
    });
    
    this.redis.on('error', (err) => {
      console.error('Redis connection error:', err);
    });
  }
  
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    try {
      const prefixedKey = this.getPrefixedKey(key, options?.prefix);
      const value = await this.redis.get(prefixedKey);
      
      if (!value) return null;
      
      return JSON.parse(value);
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }
  
  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void> {
    try {
      const prefixedKey = this.getPrefixedKey(key, options?.prefix);
      const ttl = options?.ttl || this.defaultTTL;
      
      await this.redis.setex(prefixedKey, ttl, JSON.stringify(value));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }
  
  async del(key: string, options?: CacheOptions): Promise<void> {
    try {
      const prefixedKey = this.getPrefixedKey(key, options?.prefix);
      await this.redis.del(prefixedKey);
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }
  
  async invalidatePattern(pattern: string): Promise<number> {
    try {
      const keys = await this.redis.keys(pattern);
      if (keys.length === 0) return 0;
      
      return await this.redis.del(...keys);
    } catch (error) {
      console.error('Cache invalidate pattern error:', error);
      return 0;
    }
  }
  
  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    try {
      const prefixedKey = this.getPrefixedKey(key, options?.prefix);
      const result = await this.redis.exists(prefixedKey);
      return result === 1;
    } catch (error) {
      console.error('Cache exists error:', error);
      return false;
    }
  }
  
  private getPrefixedKey(key: string, prefix?: string): string {
    const defaultPrefix = 't-dev';
    const actualPrefix = prefix || defaultPrefix;
    return `${actualPrefix}:${key}`;
  }
  
  async disconnect(): Promise<void> {
    await this.redis.disconnect();
  }
}