import { RedisClient, CacheConfig } from './redis-client';

export interface CacheStrategy {
  ttl: number;
  tags?: string[];
  invalidateOn?: string[];
}

export interface CacheMetrics {
  hits: number;
  misses: number;
  sets: number;
  deletes: number;
}

export class CacheManager {
  private redis: RedisClient;
  private strategies: Map<string, CacheStrategy> = new Map();
  private metrics: CacheMetrics = { hits: 0, misses: 0, sets: 0, deletes: 0 };

  constructor(config: CacheConfig) {
    this.redis = new RedisClient(config);
    this.initializeStrategies();
  }

  private initializeStrategies(): void {
    // User cache strategy
    this.strategies.set('user', {
      ttl: 3600, // 1 hour
      tags: ['user'],
      invalidateOn: ['user:update', 'user:delete']
    });

    // Project cache strategy
    this.strategies.set('project', {
      ttl: 1800, // 30 minutes
      tags: ['project'],
      invalidateOn: ['project:update', 'project:delete']
    });

    // Agent cache strategy
    this.strategies.set('agent', {
      ttl: 300, // 5 minutes (agents change frequently)
      tags: ['agent'],
      invalidateOn: ['agent:update', 'agent:execute']
    });

    // Query result cache
    this.strategies.set('query', {
      ttl: 600, // 10 minutes
      tags: ['query']
    });
  }

  async get<T>(key: string, loader?: () => Promise<T>): Promise<T | null> {
    try {
      const cached = await this.redis.get<T>(key);
      
      if (cached !== null) {
        this.metrics.hits++;
        return cached;
      }

      this.metrics.misses++;

      if (loader) {
        const value = await loader();
        await this.set(key, value);
        return value;
      }

      return null;
    } catch (error) {
      console.error('Cache get error:', error);
      return loader ? await loader() : null;
    }
  }

  async set<T>(key: string, value: T, strategyName?: string): Promise<void> {
    try {
      const strategy = strategyName ? this.strategies.get(strategyName) : null;
      const ttl = strategy?.ttl || 3600;
      
      await this.redis.set(key, value, ttl);
      this.metrics.sets++;

      // Add tags if strategy defines them
      if (strategy?.tags) {
        await this.addTags(key, strategy.tags);
      }
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  async del(key: string): Promise<void> {
    try {
      await this.redis.del(key);
      this.metrics.deletes++;
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }

  async invalidateByTag(tag: string): Promise<number> {
    try {
      const tagKey = `tag:${tag}`;
      const keys = await this.redis.get<string[]>(tagKey);
      
      if (!keys || keys.length === 0) return 0;

      // Delete all keys with this tag
      const pipeline = this.redis['client'].pipeline();
      keys.forEach(key => pipeline.del(key));
      pipeline.del(tagKey);
      
      await pipeline.exec();
      return keys.length;
    } catch (error) {
      console.error('Cache invalidate by tag error:', error);
      return 0;
    }
  }

  async invalidateByPattern(pattern: string): Promise<number> {
    try {
      return await this.redis.invalidatePattern(pattern);
    } catch (error) {
      console.error('Cache invalidate by pattern error:', error);
      return 0;
    }
  }

  private async addTags(key: string, tags: string[]): Promise<void> {
    for (const tag of tags) {
      const tagKey = `tag:${tag}`;
      const existingKeys = await this.redis.get<string[]>(tagKey) || [];
      
      if (!existingKeys.includes(key)) {
        existingKeys.push(key);
        await this.redis.set(tagKey, existingKeys, 86400); // 24 hours
      }
    }
  }

  // Cache warming for frequently accessed data
  async warmCache(warmupData: Array<{ key: string; loader: () => Promise<any>; strategy?: string }>): Promise<void> {
    const promises = warmupData.map(async ({ key, loader, strategy }) => {
      try {
        const exists = await this.redis.exists(key);
        if (!exists) {
          const value = await loader();
          await this.set(key, value, strategy);
        }
      } catch (error) {
        console.error(`Cache warm error for key ${key}:`, error);
      }
    });

    await Promise.all(promises);
  }

  getMetrics(): CacheMetrics & { hitRate: number } {
    const total = this.metrics.hits + this.metrics.misses;
    const hitRate = total > 0 ? this.metrics.hits / total : 0;
    
    return {
      ...this.metrics,
      hitRate
    };
  }

  async disconnect(): Promise<void> {
    await this.redis.disconnect();
  }
}