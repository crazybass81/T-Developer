import { Response, NextFunction } from 'express';
import { AuthRequest } from './auth.middleware';
import { UserRole } from '@prisma/client';
import { AppError } from './errorHandler';

/**
 * Role-based authorization middleware
 */
export const authorize = (...roles: UserRole[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        status: 'error',
        message: 'Authentication required',
      });
      return;
    }

    if (!roles.includes(req.user.role)) {
      res.status(403).json({
        status: 'error',
        message: 'Insufficient permissions',
      });
      return;
    }

    next();
  };
};

/**
 * Check if user owns the resource
 */
export const authorizeOwner = (
  getUserId: (req: AuthRequest) => string | undefined
) => {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        status: 'error',
        message: 'Authentication required',
      });
      return;
    }

    const resourceUserId = getUserId(req);
    
    if (!resourceUserId) {
      res.status(404).json({
        status: 'error',
        message: 'Resource not found',
      });
      return;
    }

    if (req.user.id !== resourceUserId && req.user.role !== UserRole.ADMIN) {
      res.status(403).json({
        status: 'error',
        message: 'Access denied',
      });
      return;
    }

    next();
  };
};