import { RedisClient } from './redis/client';
import { CacheManager } from './cache-manager';
import { CacheMiddleware } from './cache-middleware';
import { CacheAsideStrategy, WriteThroughCache, DistributedCacheInvalidation } from './cache-strategies';

// Initialize caching system
export function initializeCaching() {
  const redisConfig = {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD,
    maxRetriesPerRequest: 3,
    retryDelayOnFailover: 100
  };
  
  const redisClient = new RedisClient(redisConfig);
  const cacheManager = new CacheManager(redisClient);
  const cacheMiddleware = new CacheMiddleware(cacheManager);
  const distributedInvalidation = new DistributedCacheInvalidation(cacheManager);
  
  // Connect to Redis
  redisClient.connect().catch(error => {
    console.error('Failed to connect to Redis:', error);
  });
  
  console.log('✅ Caching system initialized');
  
  return {
    redisClient,
    cacheManager,
    cacheMiddleware,
    distributedInvalidation
  };
}

export { RedisClient } from './redis/client';
export { CacheManager } from './cache-manager';
export { CacheMiddleware } from './cache-middleware';
export * from './cache-strategies';