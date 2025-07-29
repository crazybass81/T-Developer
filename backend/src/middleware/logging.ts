import { Request, Response, NextFunction } from 'express';
import { logger, createRequestLogger } from '../config/logger';
import { v4 as uuidv4 } from 'uuid';

export function loggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const requestId = req.headers['x-request-id'] as string || uuidv4();
  const requestLogger = createRequestLogger(requestId);
  
  req.requestId = requestId;
  req.logger = requestLogger;
  
  const start = Date.now();
  
  requestLogger.info('Request started', {
    method: req.method,
    url: req.url,
    userAgent: req.headers['user-agent'],
    ip: req.ip
  });
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    requestLogger.info('Request completed', {
      statusCode: res.statusCode,
      duration,
      contentLength: res.get('content-length')
    });
  });
  
  next();
}

declare global {
  namespace Express {
    interface Request {
      requestId: string;
      logger: any;
    }
  }
}