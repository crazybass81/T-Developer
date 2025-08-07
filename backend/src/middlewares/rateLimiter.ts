import { Request, Response, NextFunction } from 'express';
import { redis } from '../services/database.service';
import { AppError } from './errorHandler';

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  message?: string;
}

const configs: Record<string, RateLimitConfig> = {
  default: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 100,
    message: 'Too many requests, please try again later',
  },
  login: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 5,
    message: 'Too many login attempts, please try again later',
  },
  register: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 3,
    message: 'Too many registration attempts, please try again later',
  },
};

export const rateLimiter = (configName: string = 'default') => {
  const config = configs[configName] || configs.default;

  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const key = `rate_limit:${configName}:${req.ip}`;
    
    try {
      const current = await redis.incr(key);
      
      if (current === 1) {
        await redis.expire(key, Math.floor(config.windowMs / 1000));
      }
      
      if (current > config.maxRequests) {
        res.status(429).json({
          status: 'error',
          message: config.message,
        });
        return;
      }
      
      res.setHeader('X-RateLimit-Limit', config.maxRequests.toString());
      res.setHeader('X-RateLimit-Remaining', 
        Math.max(0, config.maxRequests - current).toString()
      );
      
      next();
    } catch (error) {
      // If Redis is down, allow the request
      next();
    }
  };
};