import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// API 키 관리
export class APIKeyManager {
  private static readonly KEY_PREFIX = 'sk_';
  private static readonly KEY_LENGTH = 32;
  
  static generateAPIKey(): string {
    const randomBytes = crypto.randomBytes(this.KEY_LENGTH);
    return `${this.KEY_PREFIX}${randomBytes.toString('base64url')}`;
  }
  
  static hashAPIKey(apiKey: string): string {
    return crypto.createHash('sha256').update(apiKey).digest('hex');
  }
  
  static validateKeyFormat(apiKey: string): boolean {
    return apiKey.startsWith(this.KEY_PREFIX) && apiKey.length > this.KEY_PREFIX.length;
  }
}

// HMAC 서명 검증
export class HMACValidator {
  private static readonly TIMESTAMP_TOLERANCE = 300; // 5분
  
  static generateSignature(secret: string, method: string, path: string, timestamp: number, body?: any): string {
    const payload = [method.toUpperCase(), path, timestamp, body ? JSON.stringify(body) : ''].join('\n');
    return crypto.createHmac('sha256', secret).update(payload).digest('hex');
  }
  
  static validateRequest(req: Request, secret: string): boolean {
    const signature = req.headers['x-signature'] as string;
    const timestamp = parseInt(req.headers['x-timestamp'] as string);
    
    if (!signature || !timestamp) return false;
    
    // 타임스탬프 검증
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestamp) > this.TIMESTAMP_TOLERANCE) return false;
    
    // 서명 검증
    const expectedSignature = this.generateSignature(secret, req.method, req.path, timestamp, req.body);
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
  }
}

// API 보안 미들웨어
export class APISecurityMiddleware {
  // API 키 인증
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
          return res.status(401).json({ error: 'Invalid API key', code: 'INVALID_API_KEY' });
        }
        
        // 스코프 검증
        if (requiredScopes.length > 0 && !this.validateScopes(requiredScopes, keyInfo.scopes)) {
          return res.status(403).json({ 
            error: 'Insufficient permissions', 
            code: 'INSUFFICIENT_SCOPES',
            required: requiredScopes 
          });
        }
        
        req.user = { userId: keyInfo.userId, email: '', role: 'user', scopes: keyInfo.scopes, authMethod: 'api_key' };
        next();
      } catch (error) {
        return res.status(500).json({ error: 'Authentication error', code: 'AUTH_ERROR' });
      }
    };
  }
  
  // JWT 토큰 인증
  static jwtAuth(requiredScopes: string[] = []) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const authHeader = req.headers.authorization;
      
      if (!authHeader?.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Bearer token required', code: 'MISSING_TOKEN' });
      }
      
      const token = authHeader.substring(7);
      
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
        
        if (requiredScopes.length > 0 && !this.validateScopes(requiredScopes, decoded.scopes || [])) {
          return res.status(403).json({ 
            error: 'Insufficient permissions', 
            code: 'INSUFFICIENT_SCOPES' 
          });
        }
        
        req.user = { userId: decoded.userId, email: decoded.email || '', role: decoded.role || 'user', scopes: decoded.scopes || [], authMethod: 'jwt' };
        next();
      } catch (error) {
        return res.status(401).json({ error: 'Invalid token', code: 'INVALID_TOKEN' });
      }
    };
  }
  
  // IP 화이트리스트
  static ipWhitelist(allowedIPs: string[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (process.env.NODE_ENV === 'development') return next();
      
      const clientIP = (req.ip || req.socket.remoteAddress || '').replace('::1', '127.0.0.1');
      
      if (!allowedIPs.includes(clientIP)) {
        return res.status(403).json({ error: 'IP not allowed', code: 'IP_NOT_ALLOWED' });
      }
      
      next();
    };
  }
  
  // 의심스러운 User-Agent 탐지
  static validateUserAgent() {
    const suspiciousAgents = ['curl', 'wget', 'bot', 'crawler', 'spider'];
    
    return (req: Request, res: Response, next: NextFunction) => {
      const userAgent = (req.headers['user-agent'] || '').toLowerCase();
      
      if (!userAgent || suspiciousAgents.some(agent => userAgent.includes(agent))) {
        return res.status(403).json({ error: 'Invalid user agent', code: 'INVALID_USER_AGENT' });
      }
      
      next();
    };
  }
  
  // 보안 헤더 설정
  static securityHeaders() {
    return (req: Request, res: Response, next: NextFunction) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Strict-Transport-Security', 'max-age=31536000');
      res.setHeader('Content-Security-Policy', "default-src 'self'");
      next();
    };
  }
  
  // Helper 메서드
  private static async getAPIKeyInfo(hashedKey: string): Promise<any> {
    // 실제 구현에서는 DynamoDB 조회
    return {
      userId: 'user123',
      scopes: ['projects:read', 'projects:write'],
      active: true,
      secret: 'test-secret'
    };
  }
  
  private static validateScopes(required: string[], userScopes: string[]): boolean {
    return userScopes.includes('admin:all') || required.every(scope => userScopes.includes(scope));
  }
}