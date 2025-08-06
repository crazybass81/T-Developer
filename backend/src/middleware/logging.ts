import { Request, Response, NextFunction } from 'express';
import { logger, createRequestLogger } from '../config/logger';
import { v4 as uuidv4 } from 'uuid';

// Request 타입 확장
declare global {
  namespace Express {
    interface Request {
      id: string;
      logger: typeof logger;
      startTime: number;
    }
  }
}

export function loggingMiddleware(req: Request, res: Response, next: NextFunction): void {
  // 요청 ID 생성
  req.id = req.headers['x-request-id'] as string || uuidv4();
  req.startTime = Date.now();
  
  // 요청별 로거 생성
  req.logger = createRequestLogger(req.id);
  
  // 요청 시작 로그
  req.logger.info('Request started', {
    method: req.method,
    url: req.url,
    userAgent: req.headers['user-agent'],
    ip: req.ip
  });
  
  // 응답 완료 시 로그
  res.on('finish', () => {
    const duration = Date.now() - req.startTime;
    
    req.logger.info('Request completed', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration,
      contentLength: res.get('content-length')
    });
  });
  
  next();
}