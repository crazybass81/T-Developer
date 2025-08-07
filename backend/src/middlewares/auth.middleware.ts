import { Request, Response, NextFunction } from 'express';
import { authService } from '../services/auth.service';
import { userRepository } from '../repositories/user.repository';
import { AppError } from './errorHandler';
import { logger } from '../utils/logger';

export interface AuthRequest extends Request {
  user?: any;
  token?: string;
  sessionId?: string;
}

/**
 * Authentication middleware
 */
export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    // Get token from header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError('No token provided', 401);
    }

    const token = authHeader.substring(7);

    // Check if token is blacklisted
    const isBlacklisted = await authService.isTokenBlacklisted(token);
    if (isBlacklisted) {
      throw new AppError('Token has been revoked', 401);
    }

    // Verify token
    const decoded = authService.verifyToken(token);

    // Validate session
    const isValidSession = await authService.validateSession(decoded.sessionId);
    if (!isValidSession) {
      throw new AppError('Invalid or expired session', 401);
    }

    // Get user
    const user = await userRepository.findById(decoded.userId);
    if (!user) {
      throw new AppError('User not found', 404);
    }

    // Attach user to request
    req.user = user;
    req.token = token;
    req.sessionId = decoded.sessionId;

    next();
  } catch (error) {
    if (error instanceof AppError) {
      res.status(error.statusCode).json({
        status: 'error',
        message: error.message,
      });
    } else {
      logger.error('Authentication error:', error);
      res.status(401).json({
        status: 'error',
        message: 'Authentication failed',
      });
    }
  }
};

/**
 * Optional authentication middleware
 */
export const authenticateOptional = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      
      const isBlacklisted = await authService.isTokenBlacklisted(token);
      if (!isBlacklisted) {
        try {
          const decoded = authService.verifyToken(token);
          const user = await userRepository.findById(decoded.userId);
          if (user) {
            req.user = user;
            req.token = token;
            req.sessionId = decoded.sessionId;
          }
        } catch {
          // Invalid token, but continue without user
        }
      }
    }
    next();
  } catch (error) {
    next();
  }
};