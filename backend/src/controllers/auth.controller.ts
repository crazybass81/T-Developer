import { Request, Response } from 'express';
import { AuthRequest } from '../middlewares/auth.middleware';
import { authService } from '../services/auth.service';
import { userRepository } from '../repositories/user.repository';
import { sessionRepository } from '../repositories/session.repository';
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