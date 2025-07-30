import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { AuthManager } from './auth-manager';
import { RBACManager } from './rbac-manager';

export class SecurityMiddleware {
  private authManager: AuthManager;
  private rbacManager: RBACManager;
  
  constructor() {
    this.authManager = new AuthManager();
    this.rbacManager = new RBACManager();
  }
  
  // Security headers
  securityHeaders() {
    return helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "wss:", "https:"]
        }
      },
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true
      }
    });
  }
  
  // Rate limiting
  rateLimiter(options?: { windowMs?: number; max?: number }) {
    return rateLimit({
      windowMs: options?.windowMs || 15 * 60 * 1000, // 15 minutes
      max: options?.max || 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP',
      standardHeaders: true,
      legacyHeaders: false
    });
  }
  
  // API rate limiting
  apiRateLimiter() {
    return rateLimit({
      windowMs: 60 * 1000, // 1 minute
      max: 60, // 60 requests per minute
      message: 'API rate limit exceeded',
      keyGenerator: (req) => {
        return req.user?.userId || req.ip || 'unknown';
      }
    });
  }
  
  // Authentication middleware
  authenticate() {
    return this.authManager.authenticate();
  }
  
  // Authorization middleware
  authorize(permissions: string[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
      }
      
      const hasPermission = permissions.some(permission =>
        this.rbacManager.hasPermission(req.user!.userId, permission)
      );
      
      if (!hasPermission) {
        return res.status(403).json({ 
          error: 'Insufficient permissions',
          required: permissions
        });
      }
      
      next();
    };
  }
  
  // Input validation
  validateInput() {
    return (req: Request, res: Response, next: NextFunction) => {
      // Basic input sanitization
      if (req.body) {
        req.body = this.sanitizeObject(req.body);
      }
      
      if (req.query) {
        req.query = this.sanitizeObject(req.query);
      }
      
      next();
    };
  }
  
  // Sanitize object
  private sanitizeObject(obj: any): any {
    if (typeof obj === 'string') {
      return obj.replace(/<script[^>]*>.*?<\/script>/gi, '')
                .replace(/javascript:/gi, '')
                .replace(/on\w+\s*=/gi, '');
    }
    
    if (Array.isArray(obj)) {
      return obj.map(item => this.sanitizeObject(item));
    }
    
    if (obj && typeof obj === 'object') {
      const sanitized: any = {};
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          sanitized[key] = this.sanitizeObject(obj[key]);
        }
      }
      return sanitized;
    }
    
    return obj;
  }
  
  // CORS configuration
  corsOptions() {
    return {
      origin: (origin: string | undefined, callback: Function) => {
        const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [
          'http://localhost:3000',
          'http://localhost:3001'
        ];
        
        if (!origin || allowedOrigins.includes(origin)) {
          callback(null, true);
        } else {
          callback(new Error('Not allowed by CORS'));
        }
      },
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID']
    };
  }
  
  // Request logging
  requestLogger() {
    return (req: Request, res: Response, next: NextFunction) => {
      const start = Date.now();
      
      res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
        
        // Log security events
        if (res.statusCode === 401 || res.statusCode === 403) {
          console.warn(`Security event: ${req.method} ${req.path} - ${res.statusCode} - IP: ${req.ip}`);
        }
      });
      
      next();
    };
  }
  
  // Error handler
  errorHandler() {
    return (error: Error, req: Request, res: Response, next: NextFunction) => {
      console.error('Security error:', error);
      
      // Don't expose internal errors in production
      if (process.env.NODE_ENV === 'production') {
        res.status(500).json({ error: 'Internal server error' });
      } else {
        res.status(500).json({ 
          error: error.message,
          stack: error.stack
        });
      }
    };
  }
}