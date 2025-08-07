# Phase 2: 인증/보안 구현 - Q-Developer 작업지시서

## 📋 작업 개요
- **Phase**: 2 - 인증/보안 구현
- **목표**: JWT 기반 인증, 로그인/로그아웃, 역할 기반 접근 제어, 보안 강화
- **예상 소요시간**: 12시간
- **선행조건**: Phase 1 완료

---

## 🎯 Task 2.1: JWT 인증 시스템 구현

### 작업 지시사항

#### 1. JWT 토큰 서비스 구현

**backend/src/services/auth.service.ts**:
```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { User } from '@prisma/client';
import { config } from '../config/config';
import { userRepository } from '../repositories/user.repository';
import { sessionRepository } from '../repositories/session.repository';
import { AppError } from '../middlewares/errorHandler';
import { logger } from '../utils/logger';
import { redis } from './database.service';

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
  sessionId: string;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export class AuthService {
  private readonly ACCESS_TOKEN_EXPIRES = '15m';
  private readonly REFRESH_TOKEN_EXPIRES = '7d';
  private readonly TOKEN_BLACKLIST_PREFIX = 'blacklist:';

  /**
   * Generate JWT tokens
   */
  generateTokens(user: User, sessionId: string): AuthTokens {
    const payload: TokenPayload = {
      userId: user.id,
      email: user.email,
      role: user.role,
      sessionId,
    };

    const accessToken = jwt.sign(payload, config.jwt.secret, {
      expiresIn: this.ACCESS_TOKEN_EXPIRES,
    });

    const refreshToken = jwt.sign(
      { ...payload, type: 'refresh' },
      config.jwt.refreshSecret || config.jwt.secret,
      { expiresIn: this.REFRESH_TOKEN_EXPIRES }
    );

    return {
      accessToken,
      refreshToken,
      expiresIn: 900, // 15 minutes in seconds
    };
  }

  /**
   * Verify and decode JWT token
   */
  verifyToken(token: string): TokenPayload {
    try {
      const decoded = jwt.verify(token, config.jwt.secret) as TokenPayload;
      return decoded;
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new AppError('Token expired', 401);
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new AppError('Invalid token', 401);
      }
      throw error;
    }
  }

  /**
   * Login user
   */
  async login(email: string, password: string): Promise<{
    user: Omit<User, 'password'>;
    tokens: AuthTokens;
  }> {
    // Validate credentials
    const user = await userRepository.validatePassword(email, password);
    if (!user) {
      logger.warn(`Failed login attempt for email: ${email}`);
      throw new AppError('Invalid email or password', 401);
    }

    // Create session
    const session = await sessionRepository.create({
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    });

    // Generate tokens
    const tokens = this.generateTokens(user, session.id);

    // Store refresh token in Redis
    await redis.setex(
      `refresh:${session.id}`,
      7 * 24 * 60 * 60, // 7 days in seconds
      tokens.refreshToken
    );

    const { password, ...userWithoutPassword } = user;
    
    logger.info(`User logged in: ${email} (${user.id})`);
    
    return {
      user: userWithoutPassword,
      tokens,
    };
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    try {
      const decoded = jwt.verify(
        refreshToken,
        config.jwt.refreshSecret || config.jwt.secret
      ) as TokenPayload & { type: string };

      if (decoded.type !== 'refresh') {
        throw new AppError('Invalid token type', 401);
      }

      // Check if session exists
      const session = await sessionRepository.findById(decoded.sessionId);
      if (!session || session.expiresAt < new Date()) {
        throw new AppError('Session expired', 401);
      }

      // Check if refresh token matches stored token
      const storedToken = await redis.get(`refresh:${session.id}`);
      if (storedToken !== refreshToken) {
        throw new AppError('Invalid refresh token', 401);
      }

      // Get user
      const user = await userRepository.findById(decoded.userId);
      if (!user) {
        throw new AppError('User not found', 404);
      }

      // Generate new tokens
      const tokens = this.generateTokens(user, session.id);

      // Update refresh token in Redis
      await redis.setex(
        `refresh:${session.id}`,
        7 * 24 * 60 * 60,
        tokens.refreshToken
      );

      return tokens;
    } catch (error) {
      if (error instanceof AppError) throw error;
      throw new AppError('Invalid refresh token', 401);
    }
  }

  /**
   * Logout user
   */
  async logout(sessionId: string, token: string): Promise<void> {
    // Delete session
    await sessionRepository.delete(sessionId);

    // Delete refresh token from Redis
    await redis.del(`refresh:${sessionId}`);

    // Add access token to blacklist
    const decoded = this.verifyToken(token);
    const ttl = Math.floor((decoded.exp || 0) - Date.now() / 1000);
    if (ttl > 0) {
      await redis.setex(`${this.TOKEN_BLACKLIST_PREFIX}${token}`, ttl, '1');
    }

    logger.info(`User logged out: session ${sessionId}`);
  }

  /**
   * Check if token is blacklisted
   */
  async isTokenBlacklisted(token: string): Promise<boolean> {
    const result = await redis.get(`${this.TOKEN_BLACKLIST_PREFIX}${token}`);
    return result === '1';
  }

  /**
   * Validate session
   */
  async validateSession(sessionId: string): Promise<boolean> {
    const session = await sessionRepository.findById(sessionId);
    return session !== null && session.expiresAt > new Date();
  }
}

export const authService = new AuthService();
```

#### 2. Session Repository 구현

**backend/src/repositories/session.repository.ts**:
```typescript
import { prisma } from '../services/database.service';
import { Session, Prisma } from '@prisma/client';
import { logger } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export class SessionRepository {
  async create(data: {
    userId: string;
    expiresAt: Date;
  }): Promise<Session> {
    try {
      const session = await prisma.session.create({
        data: {
          ...data,
          token: uuidv4(),
        },
      });

      logger.info(`Session created for user: ${data.userId}`);
      return session;
    } catch (error) {
      logger.error('Error creating session:', error);
      throw error;
    }
  }

  async findById(id: string): Promise<Session | null> {
    try {
      return await prisma.session.findUnique({
        where: { id },
        include: { user: true },
      });
    } catch (error) {
      logger.error(`Error finding session ${id}:`, error);
      return null;
    }
  }

  async findByToken(token: string): Promise<Session | null> {
    try {
      return await prisma.session.findUnique({
        where: { token },
        include: { user: true },
      });
    } catch (error) {
      logger.error(`Error finding session by token:`, error);
      return null;
    }
  }

  async delete(id: string): Promise<void> {
    try {
      await prisma.session.delete({
        where: { id },
      });
      logger.info(`Session deleted: ${id}`);
    } catch (error) {
      logger.error(`Error deleting session ${id}:`, error);
    }
  }

  async deleteExpired(): Promise<number> {
    try {
      const result = await prisma.session.deleteMany({
        where: {
          expiresAt: {
            lt: new Date(),
          },
        },
      });
      
      if (result.count > 0) {
        logger.info(`Deleted ${result.count} expired sessions`);
      }
      
      return result.count;
    } catch (error) {
      logger.error('Error deleting expired sessions:', error);
      return 0;
    }
  }

  async deleteUserSessions(userId: string): Promise<void> {
    try {
      await prisma.session.deleteMany({
        where: { userId },
      });
      logger.info(`All sessions deleted for user: ${userId}`);
    } catch (error) {
      logger.error(`Error deleting user sessions:`, error);
    }
  }
}

export const sessionRepository = new SessionRepository();
```

---

## 🎯 Task 2.2: 인증 미들웨어 구현

### 작업 지시사항

#### 1. Authentication Middleware

**backend/src/middlewares/auth.middleware.ts**:
```typescript
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
```

#### 2. Authorization Middleware

**backend/src/middlewares/authorize.middleware.ts**:
```typescript
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
```

---

## 🎯 Task 2.3: Auth Controller 및 Routes

### 작업 지시사항

#### 1. Auth Controller

**backend/src/controllers/auth.controller.ts**:
```typescript
import { Request, Response } from 'express';
import { AuthRequest } from '../middlewares/auth.middleware';
import { authService } from '../services/auth.service';
import { userRepository } from '../repositories/user.repository';
import { asyncHandler } from '../middlewares/errorHandler';
import { validate } from '../utils/validator';
import Joi from 'joi';
import { logger } from '../utils/logger';

const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  name: Joi.string().min(1).max(100).required(),
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required(),
});

const refreshTokenSchema = Joi.object({
  refreshToken: Joi.string().required(),
});

export class AuthController {
  /**
   * Register new user
   */
  register = asyncHandler(async (req: Request, res: Response) => {
    const data = validate(req.body, registerSchema);

    // Create user
    const user = await userRepository.create({
      ...data,
      role: 'USER',
    });

    // Auto login after registration
    const result = await authService.login(data.email, data.password);

    logger.info(`New user registered: ${data.email}`);

    res.status(201).json({
      status: 'success',
      message: 'Registration successful',
      data: {
        user: result.user,
        tokens: result.tokens,
      },
    });
  });

  /**
   * Login user
   */
  login = asyncHandler(async (req: Request, res: Response) => {
    const { email, password } = validate(req.body, loginSchema);

    const result = await authService.login(email, password);

    res.json({
      status: 'success',
      message: 'Login successful',
      data: {
        user: result.user,
        tokens: result.tokens,
      },
    });
  });

  /**
   * Refresh access token
   */
  refreshToken = asyncHandler(async (req: Request, res: Response) => {
    const { refreshToken } = validate(req.body, refreshTokenSchema);

    const tokens = await authService.refreshToken(refreshToken);

    res.json({
      status: 'success',
      message: 'Token refreshed',
      data: { tokens },
    });
  });

  /**
   * Logout user
   */
  logout = asyncHandler(async (req: AuthRequest, res: Response) => {
    if (!req.sessionId || !req.token) {
      return res.status(401).json({
        status: 'error',
        message: 'Not authenticated',
      });
    }

    await authService.logout(req.sessionId, req.token);

    res.json({
      status: 'success',
      message: 'Logout successful',
    });
  });

  /**
   * Get current user
   */
  getCurrentUser = asyncHandler(async (req: AuthRequest, res: Response) => {
    if (!req.user) {
      return res.status(401).json({
        status: 'error',
        message: 'Not authenticated',
      });
    }

    const { password, ...userWithoutPassword } = req.user;

    res.json({
      status: 'success',
      data: { user: userWithoutPassword },
    });
  });

  /**
   * Update password
   */
  updatePassword = asyncHandler(async (req: AuthRequest, res: Response) => {
    const schema = Joi.object({
      currentPassword: Joi.string().required(),
      newPassword: Joi.string().min(8).required(),
    });

    const { currentPassword, newPassword } = validate(req.body, schema);

    if (!req.user) {
      return res.status(401).json({
        status: 'error',
        message: 'Not authenticated',
      });
    }

    // Validate current password
    const isValid = await userRepository.validatePassword(
      req.user.email,
      currentPassword
    );

    if (!isValid) {
      return res.status(400).json({
        status: 'error',
        message: 'Current password is incorrect',
      });
    }

    // Update password
    await userRepository.updatePassword(req.user.id, newPassword);

    // Logout all sessions
    await sessionRepository.deleteUserSessions(req.user.id);

    res.json({
      status: 'success',
      message: 'Password updated successfully. Please login again.',
    });
  });
}

export const authController = new AuthController();
```

#### 2. Auth Routes

**backend/src/api/routes/auth.routes.ts**:
```typescript
import { Router } from 'express';
import { authController } from '../../controllers/auth.controller';
import { authenticate } from '../../middlewares/auth.middleware';
import { rateLimiter } from '../../middlewares/rateLimiter';

const router = Router();

// Public routes
router.post('/register', rateLimiter('register'), authController.register);
router.post('/login', rateLimiter('login'), authController.login);
router.post('/refresh-token', authController.refreshToken);

// Protected routes
router.use(authenticate);
router.post('/logout', authController.logout);
router.get('/me', authController.getCurrentUser);
router.put('/password', authController.updatePassword);

export const authRoutes = router;
```

---

## 🎯 Task 2.4: 보안 강화

### 작업 지시사항

#### 1. Rate Limiting Middleware

**backend/src/middlewares/rateLimiter.ts**:
```typescript
import { Request, Response, NextFunction } from 'express';
import { redis } from '../services/database.service';
import { AppError } from './errorHandler';

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  message?: string;
}

const configs: Record<string, RateLimitConfig> = {
  default: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 100,
    message: 'Too many requests, please try again later',
  },
  login: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 5,
    message: 'Too many login attempts, please try again later',
  },
  register: {
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 3,
    message: 'Too many registration attempts, please try again later',
  },
};

export const rateLimiter = (configName: string = 'default') => {
  const config = configs[configName] || configs.default;

  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const key = `rate_limit:${configName}:${req.ip}`;
    
    try {
      const current = await redis.incr(key);
      
      if (current === 1) {
        await redis.expire(key, Math.floor(config.windowMs / 1000));
      }
      
      if (current > config.maxRequests) {
        res.status(429).json({
          status: 'error',
          message: config.message,
        });
        return;
      }
      
      res.setHeader('X-RateLimit-Limit', config.maxRequests.toString());
      res.setHeader('X-RateLimit-Remaining', 
        Math.max(0, config.maxRequests - current).toString()
      );
      
      next();
    } catch (error) {
      // If Redis is down, allow the request
      next();
    }
  };
};
```

#### 2. Update Config for JWT

**backend/src/config/config.ts** (수정):
```typescript
export interface Config {
  // ... existing config
  jwt: {
    secret: string;
    refreshSecret?: string;
    expiresIn: string;
  };
  // ... rest of config
}

export const config: Config = {
  // ... existing config
  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
    refreshSecret: process.env.JWT_REFRESH_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  },
  // ... rest of config
};
```

---

## 🎯 Task 2.5: 보안 헤더 및 CORS 설정

### 작업 지시사항

#### 1. Security Headers

**backend/src/middlewares/security.ts**:
```typescript
import helmet from 'helmet';
import cors from 'cors';
import { Express } from 'express';
import { config } from '../config/config';

export const setupSecurity = (app: Express): void => {
  // Helmet for security headers
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", 'data:', 'https:'],
      },
    },
    crossOriginEmbedderPolicy: false,
  }));

  // CORS configuration
  const corsOptions: cors.CorsOptions = {
    origin: (origin, callback) => {
      const allowedOrigins = Array.isArray(config.cors.origin) 
        ? config.cors.origin 
        : [config.cors.origin];
      
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining'],
  };

  app.use(cors(corsOptions));

  // Additional security
  app.disable('x-powered-by');
  app.set('trust proxy', 1);
};
```

---

## ✅ 검증 체크리스트

Phase 2 완료 후 다음 사항을 확인하세요:

- [ ] JWT 토큰 생성 및 검증 동작
- [ ] 로그인/로그아웃 API 동작
- [ ] Refresh Token 동작
- [ ] 인증 미들웨어 동작
- [ ] 역할 기반 접근 제어
- [ ] Rate Limiting 동작
- [ ] 보안 헤더 설정

---

## 🚀 테스트 명령어

```bash
# 1. 사용자 등록
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Password123","name":"John Doe"}'

# 2. 로그인
curl -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Password123"}'

# 3. 현재 사용자 조회 (토큰 필요)
curl http://localhost:3000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. 토큰 갱신
curl -X POST http://localhost:3000/api/v1/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"YOUR_REFRESH_TOKEN"}'

# 5. 로그아웃
curl -X POST http://localhost:3000/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📝 참고사항

- Access Token: 15분 유효
- Refresh Token: 7일 유효
- 로그아웃 시 토큰 블랙리스트 처리
- Rate Limiting: 로그인 15분당 5회, 회원가입 1시간당 3회
- 모든 민감한 정보는 환경 변수로 관리