import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { Request, Response, NextFunction } from 'express';

export interface User {
  id: string;
  email: string;
  role: 'user' | 'admin';
  permissions: string[];
}

export interface TokenPayload {
  id: string;
  userId: string;
  email: string;
  role: string;
  permissions: string[];
  scopes: string[];
  authMethod: 'api_key' | 'hmac' | 'jwt';
}

export class AuthManager {
  private readonly jwtSecret: string;
  private readonly jwtExpiry = '24h';
  private readonly refreshExpiry = '7d';
  
  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'dev-secret-key';
    
    if (process.env.NODE_ENV === 'production' && this.jwtSecret === 'dev-secret-key') {
      throw new Error('JWT_SECRET must be set in production');
    }
  }
  
  // Generate JWT tokens
  generateTokens(user: User): { accessToken: string; refreshToken: string } {
    const payload: TokenPayload = {
      id: user.id,
      userId: user.id,
      email: user.email,
      role: user.role,
      permissions: user.permissions,
      scopes: user.permissions,
      authMethod: 'jwt'
    };
    
    const accessToken = jwt.sign(payload, this.jwtSecret, {
      expiresIn: this.jwtExpiry,
      issuer: 't-developer'
    });
    
    const refreshToken = jwt.sign(
      { userId: user.id },
      this.jwtSecret,
      {
        expiresIn: this.refreshExpiry,
        issuer: 't-developer'
      }
    );
    
    return { accessToken, refreshToken };
  }
  
  // Verify JWT token
  verifyToken(token: string): TokenPayload {
    try {
      return jwt.verify(token, this.jwtSecret, {
        issuer: 't-developer'
      }) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }
  
  // Hash password
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
  }
  
  // Verify password
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
  
  // Authentication middleware
  authenticate() {
    return (req: Request, res: Response, next: NextFunction) => {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'No token provided' });
      }
      
      const token = authHeader.substring(7);
      
      try {
        const payload = this.verifyToken(token);
        req.user = {
          id: payload.userId,
          scopes: payload.permissions || [],
          authMethod: 'jwt',
          permissions: payload.permissions,
          role: payload.role
        };
        next();
      } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
      }
    };
  }
  
  // Authorization middleware
  authorize(requiredPermissions: string[]) {
    return (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
      }
      
      const userPermissions = req.user?.permissions || [];
      const hasPermission = requiredPermissions.every(permission =>
        userPermissions.includes(permission) || req.user?.role === 'admin'
      );
      
      if (!hasPermission) {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }
      
      next();
    };
  }
}

