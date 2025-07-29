import { PoolManager } from './connection-pool';
import Redis from 'ioredis';

interface CacheOptions {
  ttl?: number;
  prefix?: string;
  serialize?: boolean;
}

interface CacheStats {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
  hitRate: number;
}

export class CacheManager {
  private poolManager = PoolManager.getInstance();
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0,
    hitRate: 0
  };
  private defaultTTL = 3600; // 1 hour
  private keyPrefix = 't-dev:';

  async get<T>(key: string, options: CacheOptions = {}): Promise<T | null> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      const value = await client.get(fullKey);
      
      if (value === null) {
        this.stats.misses++;
        this.updateHitRate();
        return null;
      }

      this.stats.hits++;
      this.updateHitRate();

      if (options.serialize !== false) {
        return JSON.parse(value);
      }
      return value as T;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      const ttl = options.ttl || this.defaultTTL;
      const serializedValue = options.serialize !== false ? JSON.stringify(value) : String(value);
      
      await client.setex(fullKey, ttl, serializedValue);
      this.stats.sets++;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async del(key: string, options: CacheOptions = {}): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      await client.del(fullKey);
      this.stats.deletes++;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async mget<T>(keys: string[], options: CacheOptions = {}): Promise<(T | null)[]> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKeys = keys.map(key => this.buildKey(key, options.prefix));
      const values = await client.mget(...fullKeys);
      
      return values.map(value => {
        if (value === null) {
          this.stats.misses++;
          return null;
        }
        this.stats.hits++;
        return options.serialize !== false ? JSON.parse(value) : value as T;
      });
    } finally {
      this.updateHitRate();
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async mset<T>(keyValuePairs: Array<[string, T]>, options: CacheOptions = {}): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const pipeline = client.pipeline();
      const ttl = options.ttl || this.defaultTTL;
      
      for (const [key, value] of keyValuePairs) {
        const fullKey = this.buildKey(key, options.prefix);
        const serializedValue = options.serialize !== false ? JSON.stringify(value) : String(value);
        pipeline.setex(fullKey, ttl, serializedValue);
      }
      
      await pipeline.exec();
      this.stats.sets += keyValuePairs.length;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async exists(key: string, options: CacheOptions = {}): Promise<boolean> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      const result = await client.exists(fullKey);
      return result === 1;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async expire(key: string, ttl: number, options: CacheOptions = {}): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      await client.expire(fullKey, ttl);
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async increment(key: string, by: number = 1, options: CacheOptions = {}): Promise<number> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullKey = this.buildKey(key, options.prefix);
      const result = await client.incrby(fullKey, by);
      
      if (options.ttl) {
        await client.expire(fullKey, options.ttl);
      }
      
      return result;
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<T> {
    const cached = await this.get<T>(key, options);
    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, options);
    return value;
  }

  async invalidatePattern(pattern: string, options: CacheOptions = {}): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      const fullPattern = this.buildKey(pattern, options.prefix);
      const keys = await client.keys(fullPattern);
      
      if (keys.length > 0) {
        await client.del(...keys);
        this.stats.deletes += keys.length;
      }
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  async flush(prefix?: string): Promise<void> {
    const client = await this.poolManager.getRedisPool().getClient();
    
    try {
      if (prefix) {
        const pattern = this.buildKey('*', prefix);
        const keys = await client.keys(pattern);
        if (keys.length > 0) {
          await client.del(...keys);
        }
      } else {
        await client.flushdb();
      }
    } finally {
      await this.poolManager.getRedisPool().releaseClient(client);
    }
  }

  getStats(): CacheStats {
    return { ...this.stats };
  }

  resetStats(): void {
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      hitRate: 0
    };
  }

  private buildKey(key: string, prefix?: string): string {
    const effectivePrefix = prefix || this.keyPrefix;
    return `${effectivePrefix}${key}`;
  }

  private updateHitRate(): void {
    const total = this.stats.hits + this.stats.misses;
    this.stats.hitRate = total > 0 ? this.stats.hits / total : 0;
  }
}

export class MultiLevelCache {
  private l1Cache = new Map<string, { value: any; expires: number }>();
  private l2Cache: CacheManager;
  private l1TTL = 60000; // 1 minute
  private maxL1Size = 1000;

  constructor() {
    this.l2Cache = new CacheManager();
    this.startCleanup();
  }

  async get<T>(key: string): Promise<T | null> {
    // L1 Cache check
    const l1Entry = this.l1Cache.get(key);
    if (l1Entry && l1Entry.expires > Date.now()) {
      return l1Entry.value;
    }

    // L2 Cache check
    const l2Value = await this.l2Cache.get<T>(key);
    if (l2Value !== null) {
      this.setL1(key, l2Value);
      return l2Value;
    }

    return null;
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    this.setL1(key, value);
    await this.l2Cache.set(key, value, { ttl });
  }

  async del(key: string): Promise<void> {
    this.l1Cache.delete(key);
    await this.l2Cache.del(key);
  }

  private setL1(key: string, value: any): void {
    if (this.l1Cache.size >= this.maxL1Size) {
      const firstKey = this.l1Cache.keys().next().value;
      this.l1Cache.delete(firstKey);
    }

    this.l1Cache.set(key, {
      value,
      expires: Date.now() + this.l1TTL
    });
  }

  private startCleanup(): void {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.l1Cache.entries()) {
        if (entry.expires <= now) {
          this.l1Cache.delete(key);
        }
      }
    }, 30000); // Clean every 30 seconds
  }
}