import { Request, Response, NextFunction } from 'express';
import { CacheManager } from './cache-manager';
import crypto from 'crypto';

export interface CacheMiddlewareOptions {
  ttl?: number;
  keyGenerator?: (req: Request) => string;
  condition?: (req: Request) => boolean;
  vary?: string[];
}

export class CacheMiddleware {
  constructor(private cache: CacheManager) {}
  
  // HTTP response caching
  httpCache(options: CacheMiddlewareOptions = {}) {
    const cache = this.cache;
    return async (req: Request, res: Response, next: NextFunction) => {
      // Skip caching for non-GET requests
      if (req.method !== 'GET') {
        return next();
      }
      
      // Check condition
      if (options.condition && !options.condition(req)) {
        return next();
      }
      
      const cacheKey = this.generateCacheKey(req, options.keyGenerator);
      
      try {
        // Try to get from cache
        const cached = await this.cache.get<{
          statusCode: number;
          headers: Record<string, string>;
          body: any;
        }>(cacheKey);
        
        if (cached) {
          // Set headers
          Object.entries(cached.headers).forEach(([key, value]) => {
            res.setHeader(key, value);
          });
          
          res.setHeader('X-Cache', 'HIT');
          return res.status(cached.statusCode).json(cached.body);
        }
        
        // Cache miss - intercept response
        const originalJson = res.json;
        const originalStatus = res.status;
        let statusCode = 200;
        
        res.status = function(code: number) {
          statusCode = code;
          return originalStatus.call(this, code);
        };
        
        res.json = function(body: any) {
          // Only cache successful responses
          if (statusCode >= 200 && statusCode < 300) {
            const headers: Record<string, string> = {};
            
            // Copy relevant headers
            if (options.vary) {
              options.vary.forEach(header => {
                const value = res.getHeader(header);
                if (value) headers[header] = String(value);
              });
            }
            
            // Cache in background
            cache.set(cacheKey, {
              statusCode,
              headers,
              body
            }, { ttl: options.ttl }).catch(console.error);
          }
          
          res.setHeader('X-Cache', 'MISS');
          return originalJson.call(this, body);
        };
        
        next();
        
      } catch (error) {
        console.error('Cache middleware error:', error);
        next();
      }
    };
  }
  
  // API response caching
  apiCache(ttl: number = 300) {
    return this.httpCache({
      ttl,
      condition: (req) => req.method === 'GET',
      keyGenerator: (req) => `api:${req.path}:${JSON.stringify(req.query)}`
    });
  }
  
  // User-specific caching
  userCache(ttl: number = 600) {
    return this.httpCache({
      ttl,
      keyGenerator: (req) => {
        const userId = req.user?.userId || 'anonymous';
        return `user:${userId}:${req.path}:${JSON.stringify(req.query)}`;
      }
    });
  }
  
  // Cache invalidation middleware
  invalidateCache(patterns: string[]) {
    const cache = this.cache;
    return async (req: Request, res: Response, next: NextFunction) => {
      // Store original end function
      const originalEnd = res.end;
      
      res.end = function(...args: any[]) {
        // Only invalidate on successful mutations
        if (res.statusCode >= 200 && res.statusCode < 300) {
          for (const pattern of patterns) {
            const resolvedPattern = pattern
              .replace(':userId', req.user?.userId || '*')
              .replace(':projectId', req.params.projectId || '*');
            
            // Invalidate in background
            cache.deletePattern(resolvedPattern).catch(console.error);
          }
        }
        
        return originalEnd.apply(this, args as any);
      };
      
      next();
    };
  }
  
  private generateCacheKey(req: Request, keyGenerator?: (req: Request) => string): string {
    if (keyGenerator) {
      return keyGenerator(req);
    }
    
    // Default key generation
    const baseKey = `${req.method}:${req.path}`;
    const queryString = JSON.stringify(req.query);
    const userContext = req.user?.userId || 'anonymous';
    
    return crypto
      .createHash('md5')
      .update(`${baseKey}:${queryString}:${userContext}`)
      .digest('hex');
  }
}

// Cache warming middleware
export class CacheWarmingMiddleware {
  constructor(private cache: CacheManager) {}
  
  warmOnStartup(routes: Array<{ path: string; handler: () => Promise<any> }>) {
    return async () => {
      console.log('🔥 Warming cache...');
      
      const warmingPromises = routes.map(async (route) => {
        try {
          const data = await route.handler();
          await this.cache.set(`warm:${route.path}`, data, { ttl: 3600 });
        } catch (error) {
          console.error(`Failed to warm cache for ${route.path}:`, error);
        }
      });
      
      await Promise.all(warmingPromises);
      console.log('✅ Cache warming completed');
    };
  }
}