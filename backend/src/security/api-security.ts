import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import { RateLimiter } from '../middleware/rate-limiter';

// API Key Manager
export class APIKeyManager {
  private static readonly KEY_PREFIX = 'sk_';
  private static readonly KEY_LENGTH = 32;
  
  static generateAPIKey(): string {
    const randomBytes = crypto.randomBytes(this.KEY_LENGTH);
    const key = randomBytes.toString('base64url');
    return `${this.KEY_PREFIX}${key}`;
  }
  
  static hashAPIKey(apiKey: string): string {
    return crypto.createHash('sha256').update(apiKey).digest('hex');
  }
  
  static validateKeyFormat(apiKey: string): boolean {
    const regex = new RegExp(`^${this.KEY_PREFIX}[A-Za-z0-9_-]{43}$`);
    return regex.test(apiKey);
  }
}

// HMAC Signature Validator
export class HMACValidator {
  private static readonly ALGORITHM = 'sha256';
  private static readonly TIMESTAMP_TOLERANCE = 300; // 5 minutes
  
  static generateSignature(secret: string, method: string, path: string, timestamp: number, body?: any): string {
    const payload = [method.toUpperCase(), path, timestamp, body ? JSON.stringify(body) : ''].join('\n');
    return crypto.createHmac(this.ALGORITHM, secret).update(payload).digest('hex');
  }
  
  static validateRequest(req: Request, secret: string): boolean {
    const signature = req.headers['x-signature'] as string;
    const timestamp = parseInt(req.headers['x-timestamp'] as string);
    
    if (!signature || !timestamp) return false;
    
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestamp) > this.TIMESTAMP_TOLERANCE) return false;
    
    const expectedSignature = this.generateSignature(secret, req.method, req.path, timestamp, req.body);
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
  }
}

// Scope Manager
export class ScopeManager {
  static readonly SCOPES = {
    'projects:read': 'Read project information',
    'projects:write': 'Create and modify projects',
    'projects:delete': 'Delete projects',
    'agents:execute': 'Execute agents',
    'agents:monitor': 'Monitor agent execution',
    'components:read': 'Read component library',
    'components:write': 'Add components to library',
    'admin:all': 'Full administrative access'
  };
  
  static validateScopes(requiredScopes: string[], userScopes: string[]): boolean {
    if (userScopes.includes('admin:all')) return true;
    return requiredScopes.every(scope => userScopes.includes(scope));
  }
}

// API Security Middleware
export class APISecurityMiddleware {
  static apiKeyAuth(requiredScopes: string[] = []) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const apiKey = req.headers['x-api-key'] as string;
      
      if (!apiKey) {
        return res.status(401).json({ error: 'API key required', code: 'MISSING_API_KEY' });
      }
      
      if (!APIKeyManager.validateKeyFormat(apiKey)) {
        return res.status(401).json({ error: 'Invalid API key format', code: 'INVALID_API_KEY_FORMAT' });
      }
      
      try {
        const hashedKey = APIKeyManager.hashAPIKey(apiKey);
        const keyInfo = await this.getAPIKeyInfo(hashedKey);
        
        if (!keyInfo?.active) {
          return res.status(401).json({ error: 'Invalid or inactive API key', code: 'INVALID_API_KEY' });
        }
        
        if (requiredScopes.length > 0 && !ScopeManager.validateScopes(requiredScopes, keyInfo.scopes)) {
          return res.status(403).json({
            error: 'Insufficient permissions',
            code: 'INSUFFICIENT_SCOPES',
            required: requiredScopes,
            provided: keyInfo.scopes
          });
        }
        
        req.user = { id: keyInfo.userId, scopes: keyInfo.scopes, authMethod: 'api_key' };
        await this.recordAPIKeyUsage(hashedKey, req.path);
        next();
      } catch (error) {
        return res.status(500).json({ error: 'Authentication error', code: 'AUTH_ERROR' });
      }
    };
  }
  
  static hmacAuth() {
    return async (req: Request, res: Response, next: NextFunction) => {
      const apiKey = req.headers['x-api-key'] as string;
      
      if (!apiKey) {
        return res.status(401).json({ error: 'API key required for HMAC authentication', code: 'MISSING_API_KEY' });
      }
      
      try {
        const hashedKey = APIKeyManager.hashAPIKey(apiKey);
        const keyInfo = await this.getAPIKeyInfo(hashedKey);
        
        if (!keyInfo?.secret) {
          return res.status(401).json({ error: 'Invalid API key', code: 'INVALID_API_KEY' });
        }
        
        if (!HMACValidator.validateRequest(req, keyInfo.secret)) {
          return res.status(401).json({ error: 'Invalid signature', code: 'INVALID_SIGNATURE' });
        }
        
        req.user = { id: keyInfo.userId, scopes: keyInfo.scopes, authMethod: 'hmac' };
        next();
      } catch (error) {
        return res.status(500).json({ error: 'Authentication error', code: 'AUTH_ERROR' });
      }
    };
  }
  
  static ipWhitelist(allowedIPs: string[] = []) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (process.env.NODE_ENV === 'development') return next();
      
      const clientIP = req.ip || req.socket.remoteAddress || '';
      const normalizedIP = clientIP === '::1' ? '127.0.0.1' : clientIP;
      
      if (!allowedIPs.includes(normalizedIP)) {
        return res.status(403).json({ error: 'Access denied from this IP address', code: 'IP_NOT_ALLOWED' });
      }
      
      next();
    };
  }
  
  static securityHeaders() {
    return (req: Request, res: Response, next: NextFunction) => {
      if (req.method === 'OPTIONS') {
        res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH');
        res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key, X-Signature, X-Timestamp');
        res.header('Access-Control-Max-Age', '86400');
        return res.sendStatus(204);
      }
      
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
      res.setHeader('Content-Security-Policy', "default-src 'self'");
      res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      res.setHeader('X-API-Version', process.env.API_VERSION || '1.0.0');
      
      next();
    };
  }
  
  private static async getAPIKeyInfo(hashedKey: string): Promise<any> {
    // Mock implementation - replace with DynamoDB query
    return {
      userId: 'user123',
      scopes: ['projects:read', 'projects:write'],
      active: true,
      secret: 'test-secret'
    };
  }
  
  private static async recordAPIKeyUsage(hashedKey: string, endpoint: string): Promise<void> {
    // Mock implementation - replace with CloudWatch metrics
  }
}

// Dynamic Rate Limiter
export class DynamicRateLimiter {
  private static limits = new Map([
    ['free', 100],
    ['basic', 1000],
    ['pro', 10000],
    ['enterprise', -1]
  ]);
  
  static middleware() {
    return async (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) return next();
      
      const userPlan = await this.getUserPlan(req.user.id);
      const limit = this.limits.get(userPlan) || 100;
      
      if (limit === -1) return next();
      
      const rateLimiter = new RateLimiter();
      const limitMiddleware = rateLimiter.middleware({
        windowMs: 60 * 60 * 1000,
        max: limit,
        keyGenerator: (req) => req.user!.id,
        message: `Rate limit exceeded. Your plan allows ${limit} requests per hour.`
      });
      
      limitMiddleware(req, res, next);
    };
  }
  
  private static async getUserPlan(userId: string): Promise<string> {
    return 'basic'; // Mock implementation
  }
}