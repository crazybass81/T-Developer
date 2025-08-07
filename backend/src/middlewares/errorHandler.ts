/**
 * Error Handler Middleware
 * Phase 0: Basic error handling
 */

import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;
  
  constructor(message: string, statusCode: number = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  let error = err as AppError;
  
  // Default to 500 server error
  if (!error.statusCode) {
    error = new AppError(err.message || 'Internal Server Error', 500);
  }
  
  // Log error
  logger.error({
    message: error.message,
    statusCode: error.statusCode,
    stack: error.stack,
    path: req.path,
    method: req.method,
    ip: req.ip
  });
  
  // Send error response
  res.status(error.statusCode).json({
    status: 'error',
    statusCode: error.statusCode,
    message: error.message,
    ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
  });
};

// Async error wrapper
export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};