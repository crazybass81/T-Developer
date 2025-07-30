// Task 1.16.1: 중앙화된 에러 처리 시스템
import { Request, Response, NextFunction } from 'express';

export enum ErrorCode {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',
  AGENT_EXECUTION_ERROR = 'AGENT_EXECUTION_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
}

export class AppError extends Error {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly context?: any;

  constructor(
    message: string,
    code: ErrorCode,
    statusCode: number = 500,
    isOperational: boolean = true,
    context?: any
  ) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.context = context;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ErrorHandler {
  static handle(error: Error, req: Request, res: Response, next: NextFunction): void {
    if (error instanceof AppError) {
      this.handleOperationalError(error, req, res);
    } else {
      this.handleProgrammingError(error, req, res);
    }
  }

  private static handleOperationalError(error: AppError, req: Request, res: Response): void {
    console.error('Operational Error', {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      context: error.context,
      url: req.url,
      method: req.method
    });

    res.status(error.statusCode).json({
      success: false,
      error: {
        code: error.code,
        message: error.message,
        ...(process.env.NODE_ENV === 'development' && { context: error.context })
      }
    });
  }

  private static handleProgrammingError(error: Error, req: Request, res: Response): void {
    console.error('Programming Error', {
      message: error.message,
      stack: error.stack,
      url: req.url,
      method: req.method
    });

    res.status(500).json({
      success: false,
      error: {
        code: ErrorCode.INTERNAL_SERVER_ERROR,
        message: process.env.NODE_ENV === 'production' 
          ? 'Internal server error' 
          : error.message
      }
    });
  }

  static createError(code: ErrorCode, message: string, context?: any): AppError {
    const statusCodeMap: Record<ErrorCode, number> = {
      [ErrorCode.VALIDATION_ERROR]: 400,
      [ErrorCode.AUTHENTICATION_ERROR]: 401,
      [ErrorCode.AUTHORIZATION_ERROR]: 403,
      [ErrorCode.RESOURCE_NOT_FOUND]: 404,
      [ErrorCode.RATE_LIMIT_ERROR]: 429,
      [ErrorCode.AGENT_EXECUTION_ERROR]: 422,
      [ErrorCode.DATABASE_ERROR]: 500,
      [ErrorCode.EXTERNAL_SERVICE_ERROR]: 502,
      [ErrorCode.INTERNAL_SERVER_ERROR]: 500
    };

    return new AppError(message, code, statusCodeMap[code], true, context);
  }
}

export const asyncHandler = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};