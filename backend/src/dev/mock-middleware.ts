import { Request, Response, NextFunction } from 'express';
import { mockConfig } from './mock-system';

export function mockMiddleware(req: Request, res: Response, next: NextFunction) {
  if (!mockConfig.enabled) {
    return next();
  }

  // Override AWS SDK endpoints
  if (req.url.includes('/bedrock/')) {
    req.url = req.url.replace(/\/bedrock\//, mockConfig.endpoints.bedrock + '/');
  }

  // Add mock headers
  res.setHeader('X-Mock-Mode', 'enabled');
  res.setHeader('X-Mock-Timestamp', new Date().toISOString());

  next();
}

export function createMockResponse(data: any, delay: number = 0) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        data,
        mock: true,
        timestamp: new Date().toISOString()
      });
    }, delay);
  });
}