import Redis from 'ioredis';
import { LRUCache } from 'lru-cache';
import crypto from 'crypto';

// 캐시 키 네임스페이스
export enum CacheNamespace {
  PROJECT = 'project',
  USER = 'user',
  COMPONENT = 'component',
  AGENT_RESULT = 'agent_result',
  API_RESPONSE = 'api_response',
  SESSION = 'session'
}

// 캐시 TTL 설정 (초)
const CacheTTL = {
  [CacheNamespace.PROJECT]: 3600,        // 1시간
  [CacheNamespace.USER]: 1800,           // 30분
  [CacheNamespace.COMPONENT]: 86400,     // 24시간
  [CacheNamespace.AGENT_RESULT]: 7200,   // 2시간
  [CacheNamespace.API_RESPONSE]: 300,    // 5분
  [CacheNamespace.SESSION]: 3600         // 1시간
};

export class CacheManager {
  private redis: Redis;
  private memoryCache: LRUCache<string, any>;
  private stats = {
    hits: 0,
    misses: 0,
    errors: 0
  };
  
  constructor() {
    // Redis 연결
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || '0'),
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      enableOfflineQueue: true
    });
    
    // 인메모리 캐시 (L1 캐시)
    this.memoryCache = new LRUCache({
      max: 1000,
      ttl: 60000, // 1분
      updateAgeOnGet: true,
      updateAgeOnHas: true
    });
    
    // Redis 이벤트 핸들러
    this.redis.on('error', (err) => {
      console.error('Redis connection error:', err);
    });
    
    this.redis.on('connect', () => {
      console.log('Redis connected successfully');
    });
  }
  
  // 캐시 키 생성
  private generateKey(namespace: CacheNamespace, identifier: string, params?: any): string {
    if (!params) {
      return `${namespace}:${identifier}`;
    }
    
    // 파라미터 해시화
    const paramHash = crypto
      .createHash('md5')
      .update(JSON.stringify(params))
      .digest('hex');
    
    return `${namespace}:${identifier}:${paramHash}`;
  }
  
  // 캐시 가져오기 (L1 -> L2)
  async get<T>(
    namespace: CacheNamespace,
    identifier: string,
    params?: any
  ): Promise<T | null> {
    const key = this.generateKey(namespace, identifier, params);
    
    try {
      // L1 캐시 확인
      const memoryValue = this.memoryCache.get(key);
      if (memoryValue !== undefined) {
        this.stats.hits++;
        console.debug(`Cache hit (L1): ${key}`);
        return memoryValue;
      }
      
      // L2 캐시 (Redis) 확인
      const redisValue = await this.redis.get(key);
      if (redisValue) {
        this.stats.hits++;
        console.debug(`Cache hit (L2): ${key}`);
        
        const parsed = JSON.parse(redisValue);
        
        // L1 캐시에 저장
        this.memoryCache.set(key, parsed);
        
        return parsed;
      }
      
      this.stats.misses++;
      console.debug(`Cache miss: ${key}`);
      return null;
      
    } catch (error) {
      this.stats.errors++;
      console.error(`Cache get error for ${key}:`, error);
      return null;
    }
  }
  
  // 캐시 저장
  async set<T>(
    namespace: CacheNamespace,
    identifier: string,
    value: T,
    params?: any,
    ttl?: number
  ): Promise<void> {
    const key = this.generateKey(namespace, identifier, params);
    const finalTTL = ttl || CacheTTL[namespace] || 3600;
    
    try {
      const serialized = JSON.stringify(value);
      
      // L2 캐시 (Redis) 저장
      await this.redis.setex(key, finalTTL, serialized);
      
      // L1 캐시 (Memory) 저장
      this.memoryCache.set(key, value);
      
      console.debug(`Cache set: ${key} (TTL: ${finalTTL}s)`);
      
    } catch (error) {
      this.stats.errors++;
      console.error(`Cache set error for ${key}:`, error);
    }
  }
  
  // 캐시 무효화
  async invalidate(namespace: CacheNamespace, identifier: string, params?: any): Promise<void> {
    const key = this.generateKey(namespace, identifier, params);
    
    try {
      // L1 캐시 삭제
      this.memoryCache.delete(key);
      
      // L2 캐시 삭제
      await this.redis.del(key);
      
      console.debug(`Cache invalidated: ${key}`);
      
    } catch (error) {
      console.error(`Cache invalidation error for ${key}:`, error);
    }
  }
  
  // 패턴 기반 캐시 무효화
  async invalidatePattern(pattern: string): Promise<void> {
    try {
      // L1 캐시에서 패턴 매칭 삭제
      for (const key of this.memoryCache.keys()) {
        if (key.match(pattern)) {
          this.memoryCache.delete(key);
        }
      }
      
      // L2 캐시에서 패턴 매칭 삭제
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        console.debug(`Cache invalidated ${keys.length} keys matching pattern: ${pattern}`);
      }
      
    } catch (error) {
      console.error(`Pattern cache invalidation error:`, error);
    }
  }
  
  // 캐시 통계
  getStats() {
    const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses) || 0;
    
    return {
      ...this.stats,
      hitRate: (hitRate * 100).toFixed(2) + '%',
      memoryCacheSize: this.memoryCache.size,
      memoryCacheCapacity: this.memoryCache.max
    };
  }
  
  // 캐시 예열 (Cache Warming)
  async warmCache(namespace: CacheNamespace, items: Array<{ identifier: string; value: any; params?: any }>): Promise<void> {
    console.log(`Warming cache for namespace: ${namespace}`);
    
    const promises = items.map(item =>
      this.set(namespace, item.identifier, item.value, item.params)
    );
    
    await Promise.all(promises);
    
    console.log(`Cache warmed with ${items.length} items`);
  }
  
  // 캐시 태그 시스템
  async setWithTags<T>(
    namespace: CacheNamespace,
    identifier: string,
    value: T,
    tags: string[],
    params?: any,
    ttl?: number
  ): Promise<void> {
    await this.set(namespace, identifier, value, params, ttl);
    
    // 태그별로 키 저장
    const key = this.generateKey(namespace, identifier, params);
    for (const tag of tags) {
      await this.redis.sadd(`tag:${tag}`, key);
      await this.redis.expire(`tag:${tag}`, 86400); // 24시간
    }
  }
  
  // 태그 기반 캐시 무효화
  async invalidateByTag(tag: string): Promise<void> {
    const keys = await this.redis.smembers(`tag:${tag}`);
    
    if (keys.length > 0) {
      // 모든 관련 키 삭제
      await Promise.all(keys.map(key => {
        this.memoryCache.delete(key);
        return this.redis.del(key);
      }));
      
      // 태그 삭제
      await this.redis.del(`tag:${tag}`);
      
      console.debug(`Invalidated ${keys.length} cache entries with tag: ${tag}`);
    }
  }
}

// 캐싱 데코레이터
export function Cacheable(namespace: CacheNamespace, ttl?: number) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const cacheManager = (this as any).cacheManager || new CacheManager();
      
      // 캐시 키 생성을 위한 식별자
      const identifier = `${target.constructor.name}.${propertyName}`;
      const params = args.length > 0 ? args : undefined;
      
      // 캐시 확인
      const cached = await cacheManager.get(namespace, identifier, params);
      if (cached !== null) {
        return cached;
      }
      
      // 원본 메서드 실행
      const result = await originalMethod.apply(this, args);
      
      // 결과 캐싱
      await cacheManager.set(namespace, identifier, result, params, ttl);
      
      return result;
    };
    
    return descriptor;
  };
}

// HTTP 응답 캐싱 미들웨어
export function httpCacheMiddleware(options: {
  namespace?: CacheNamespace;
  ttl?: number;
  keyGenerator?: (req: any) => string;
}) {
  const cacheManager = new CacheManager();
  const {
    namespace = CacheNamespace.API_RESPONSE,
    ttl = 300,
    keyGenerator = (req) => `${req.method}:${req.path}:${JSON.stringify(req.query)}`
  } = options;
  
  return async (req: any, res: any, next: any) => {
    // POST, PUT, DELETE 요청은 캐싱하지 않음
    if (req.method !== 'GET') {
      return next();
    }
    
    const cacheKey = keyGenerator(req);
    
    // 캐시 확인
    const cached = await cacheManager.get(namespace, cacheKey);
    if (cached) {
      res.setHeader('X-Cache', 'HIT');
      res.setHeader('X-Cache-TTL', ttl.toString());
      return res.json(cached);
    }
    
    // 원본 응답 캐싱
    const originalJson = res.json;
    res.json = function (data: any) {
      res.setHeader('X-Cache', 'MISS');
      
      // 성공 응답만 캐싱
      if (res.statusCode >= 200 && res.statusCode < 300) {
        cacheManager.set(namespace, cacheKey, data, undefined, ttl)
          .catch((err: any) => console.error('Failed to cache response:', err));
      }
      
      return originalJson.call(this, data);
    };
    
    next();
  };
}