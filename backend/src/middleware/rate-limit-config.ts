import { RateLimiter } from './rate-limiter';

export class RateLimitConfig {
  private rateLimiter = new RateLimiter();

  // 사용자별 Rate Limiting
  userBasedLimiter = this.rateLimiter.middleware({
    windowMs: 60 * 1000, // 1분
    max: 100,
    message: 'Too many requests from this user',
    keyGenerator: (req: any) => req.user?.userId || req.ip
  });

  // IP 기반 Rate Limiting
  ipBasedLimiter = this.rateLimiter.middleware({
    windowMs: 60 * 1000, // 1분
    max: 200,
    message: 'Too many requests from this IP',
    keyGenerator: (req) => req.ip
  });

  // 엄격한 인증 제한
  strictAuthLimiter = this.rateLimiter.middleware({
    windowMs: 15 * 60 * 1000, // 15분
    max: 5,
    message: 'Too many authentication attempts',
    keyGenerator: (req) => `auth:${req.ip}`
  });

  // AI API 제한
  aiApiLimiter = this.rateLimiter.middleware({
    windowMs: 60 * 1000, // 1분
    max: 10,
    message: 'AI API rate limit exceeded',
    keyGenerator: (req: any) => `ai:${req.user?.userId || req.ip}`
  });

  // 프로젝트 생성 제한
  projectCreationLimiter = this.rateLimiter.middleware({
    windowMs: 60 * 60 * 1000, // 1시간
    max: 5,
    message: 'Project creation limit exceeded',
    keyGenerator: (req: any) => `project:${req.user?.userId || req.ip}`
  });
}