import { Request, Response, NextFunction } from 'express';
import Redis from 'ioredis';

export interface RateLimitOptions {
  windowMs: number;
  max: number;
  message?: string;
  keyGenerator?: (req: Request) => string;
}

export class RateLimiter {
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    });
  }
  
  middleware(options: RateLimitOptions) {
    const {
      windowMs = 60 * 1000,
      max = 100,
      message = 'Too many requests',
      keyGenerator = (req) => req.ip
    } = options;
    
    return async (req: Request, res: Response, next: NextFunction) => {
      const key = `rate-limit:${keyGenerator(req)}`;
      const now = Date.now();
      const window = now - windowMs;
      
      try {
        await this.redis.zremrangebyscore(key, '-inf', window);
        const count = await this.redis.zcard(key);
        
        if (count >= max) {
          return res.status(429).json({
            error: message,
            retryAfter: Math.ceil(windowMs / 1000)
          });
        }
        
        await this.redis.zadd(key, now, `${now}-${Math.random()}`);
        await this.redis.expire(key, Math.ceil(windowMs / 1000));
        
        res.setHeader('X-RateLimit-Limit', max);
        res.setHeader('X-RateLimit-Remaining', Math.max(0, max - count - 1));
        res.setHeader('X-RateLimit-Reset', new Date(now + windowMs).toISOString());
        
        next();
      } catch (error) {
        console.error('Rate limiter error:', error);
        next();
      }
    };
  }
}