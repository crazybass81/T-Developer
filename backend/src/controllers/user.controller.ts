/**
 * User Controller
 * Phase 1: User API endpoints
 */

import { Request, Response } from 'express';
import { userRepository } from '../repositories/user.repository';
import { asyncHandler } from '../middlewares/errorHandler';
import { validate, schemas } from '../utils/validator';
import Joi from 'joi';
import { logger } from '../utils/logger';

// Validation schemas
const createUserSchema = Joi.object({
  email: schemas.email.required(),
  password: schemas.password.required(),
  name: Joi.string().min(1).max(100).optional(),
  role: Joi.string().valid('ADMIN', 'USER', 'GUEST').optional(),
});

const updateUserSchema = Joi.object({
  email: schemas.email.optional(),
  name: Joi.string().min(1).max(100).optional(),
  role: Joi.string().valid('ADMIN', 'USER', 'GUEST').optional(),
});

const listUsersSchema = Joi.object({
  page: Joi.number().integer().min(1).default(1),
  limit: Joi.number().integer().min(1).max(100).default(10),
  role: Joi.string().valid('ADMIN', 'USER', 'GUEST').optional(),
  search: Joi.string().min(1).optional(),
});

export class UserController {
  createUser = asyncHandler(async (req: Request, res: Response) => {
    const data = validate(req.body, createUserSchema);
    
    const user = await userRepository.create(data);
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    logger.info(`User created via API: ${user.email}`);
    
    res.status(201).json({
      status: 'success',
      message: 'User created successfully',
      data: userWithoutPassword,
    });
  });

  getUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    if (!id) {
      return res.status(400).json({
        status: 'error',
        message: 'User ID is required',
      });
    }

    const user = await userRepository.findById(id);
    
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    res.json({
      status: 'success',
      data: userWithoutPassword,
    });
  });

  updateUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const data = validate(req.body, updateUserSchema);
    
    if (!id) {
      return res.status(400).json({
        status: 'error',
        message: 'User ID is required',
      });
    }

    const user = await userRepository.update(id, data);
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    res.json({
      status: 'success',
      message: 'User updated successfully',
      data: userWithoutPassword,
    });
  });

  deleteUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    if (!id) {
      return res.status(400).json({
        status: 'error',
        message: 'User ID is required',
      });
    }

    await userRepository.delete(id);
    
    res.status(200).json({
      status: 'success',
      message: 'User deleted successfully',
    });
  });

  listUsers = asyncHandler(async (req: Request, res: Response) => {
    const { page, limit, role, search } = validate(req.query, listUsersSchema);
    
    const skip = (page - 1) * limit;
    
    // Build where clause
    const where: any = {};
    if (role) {
      where.role = role;
    }
    if (search) {
      where.OR = [
        { name: { contains: search, mode: 'insensitive' } },
        { email: { contains: search, mode: 'insensitive' } },
      ];
    }
    
    const { users, total } = await userRepository.list({
      skip,
      take: limit,
      where: Object.keys(where).length > 0 ? where : undefined,
      orderBy: { createdAt: 'desc' },
    });
    
    res.json({
      status: 'success',
      data: users,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
        hasNext: page * limit < total,
        hasPrev: page > 1,
      },
    });
  });

  getUserProfile = asyncHandler(async (req: Request, res: Response) => {
    // Will be implemented in Phase 2 with proper auth middleware
    const userId = (req as any).user?.id;
    
    if (!userId) {
      return res.status(401).json({
        status: 'error',
        message: 'Authentication required',
      });
    }

    const user = await userRepository.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    res.json({
      status: 'success',
      data: userWithoutPassword,
    });
  });
}

export const userController = new UserController();