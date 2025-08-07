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
  exp?: number;
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

    const { password: userPassword, ...userWithoutPassword } = user;
    
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