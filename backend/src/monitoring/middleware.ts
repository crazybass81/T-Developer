// Express middleware for monitoring
import { Request, Response, NextFunction } from 'express';
import { logger, metrics } from './index';

// Request logging middleware
export function requestLogger(req: Request, res: Response, next: NextFunction): void {
  const start = Date.now();
  const requestId = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  // Add request ID to request object
  (req as any).requestId = requestId;
  res.setHeader('X-Request-ID', requestId);

  // Log request start
  logger.info('Request started', {
    requestId,
    method: req.method,
    path: req.path,
    userAgent: req.headers['user-agent'],
    ip: req.ip
  });

  // Override res.end to capture response
  const originalEnd = res.end;
  res.end = function(chunk?: any, encoding?: any) {
    const duration = Date.now() - start;
    
    // Log request completion
    logger.info('Request completed', {
      requestId,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration
    });

    // Record metrics
    metrics.recordDuration('http.request.duration', duration, {
      method: req.method,
      status: res.statusCode.toString()
    });
    metrics.recordCount('http.request.total', 1, {
      method: req.method,
      status: res.statusCode.toString()
    });

    // Call original end
    originalEnd.call(this, chunk, encoding);
  };

  next();
}

// Error logging middleware
export function errorLogger(error: Error, req: Request, res: Response, next: NextFunction): void {
  const requestId = (req as any).requestId;
  
  logger.error('Request error', {
    requestId,
    error: error.message,
    stack: error.stack,
    method: req.method,
    path: req.path
  });

  metrics.recordCount('http.error.total', 1, {
    method: req.method,
    errorType: error.name
  });

  next(error);
}