import { Request, Response, NextFunction } from 'express';
import { AuthManager, TokenPayload } from '../utils/auth';

declare global {
  namespace Express {
    interface Request {
      user?: TokenPayload;
    }
  }
}

export class AuthMiddleware {
  private authManager: AuthManager;

  constructor() {
    this.authManager = new AuthManager();
  }

  authenticate = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Access token required' });
      }

      const token = authHeader.substring(7);
      const payload = await this.authManager.verifyAccessToken(token);
      
      req.user = payload;
      next();
    } catch (error) {
      return res.status(401).json({ error: 'Invalid access token' });
    }
  };

  requireRole = (role: 'user' | 'admin') => {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
      }

      if (req.user.role !== role && req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }

      next();
    };
  };
}