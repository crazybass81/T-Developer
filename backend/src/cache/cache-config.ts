import { CacheConfig } from './redis-client';
import { CacheManager } from './cache-manager';
import { CacheService } from './cache-service';
import { setCacheManager } from './cache-decorators';

export function createCacheSystem(): { cacheManager: CacheManager; cacheService: CacheService } {
  const config: CacheConfig = {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD,
    keyPrefix: 't-dev:',
    ttl: 3600, // 1 hour default
    cluster: process.env.REDIS_CLUSTER === 'true',
    nodes: process.env.REDIS_NODES ? 
      JSON.parse(process.env.REDIS_NODES) : undefined
  };

  const cacheManager = new CacheManager(config);
  const cacheService = new CacheService(cacheManager);

  // Set global cache manager for decorators
  setCacheManager(cacheManager);

  return { cacheManager, cacheService };
}

// Performance-optimized cache configuration for Agno Framework
export const AGNO_CACHE_CONFIG = {
  // Ultra-fast session caching for 3μs agent instantiation
  sessionTTL: 300, // 5 minutes
  
  // Agent state caching
  agentStateTTL: 60, // 1 minute
  
  // Component library caching
  componentTTL: 3600, // 1 hour
  
  // Query result caching
  queryTTL: 600, // 10 minutes
  
  // Batch size for bulk operations
  batchSize: 100
};