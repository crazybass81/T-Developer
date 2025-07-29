import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import cors from 'cors';

export const securityMiddleware = [
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "wss:", "https:"]
      }
    }
  }),
  
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
  }),
  
  (req: Request, res: Response, next: NextFunction) => {
    const id = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    (req as any).id = id;
    res.setHeader('X-Request-ID', id);
    next();
  }
];