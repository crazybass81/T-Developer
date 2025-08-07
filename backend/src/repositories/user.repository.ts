/**
 * User Repository
 * Phase 1: User CRUD operations
 */

import { prisma } from '../services/database.service';
import { User, UserRole, Prisma } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { AppError } from '../middlewares/errorHandler';
import { logger } from '../utils/logger';

export interface CreateUserData {
  email: string;
  password: string;
  name?: string;
  role?: UserRole;
}

export interface UpdateUserData {
  email?: string;
  name?: string;
  role?: UserRole;
}

export class UserRepository {
  async create(data: CreateUserData): Promise<User> {
    try {
      const hashedPassword = await bcrypt.hash(data.password, 12);
      
      const user = await prisma.user.create({
        data: {
          ...data,
          password: hashedPassword,
        },
      });

      logger.info(`User created: ${user.email} (${user.id})`);
      return user;
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2002') {
          throw new AppError('Email already exists', 409);
        }
      }
      logger.error('Error creating user:', error);
      throw error;
    }
  }

  async findById(id: string): Promise<User | null> {
    try {
      return await prisma.user.findUnique({
        where: { id },
        include: {
          projects: {
            take: 5,
            orderBy: { createdAt: 'desc' },
          },
          agents: {
            take: 5,
            orderBy: { createdAt: 'desc' },
          },
        },
      });
    } catch (error) {
      logger.error(`Error finding user by ID ${id}:`, error);
      throw error;
    }
  }

  async findByEmail(email: string): Promise<User | null> {
    try {
      return await prisma.user.findUnique({
        where: { email },
      });
    } catch (error) {
      logger.error(`Error finding user by email ${email}:`, error);
      throw error;
    }
  }

  async update(id: string, data: UpdateUserData): Promise<User> {
    try {
      const user = await prisma.user.update({
        where: { id },
        data,
      });

      logger.info(`User updated: ${user.email} (${user.id})`);
      return user;
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2025') {
          throw new AppError('User not found', 404);
        }
        if (error.code === 'P2002') {
          throw new AppError('Email already exists', 409);
        }
      }
      logger.error(`Error updating user ${id}:`, error);
      throw error;
    }
  }

  async delete(id: string): Promise<void> {
    try {
      await prisma.user.delete({
        where: { id },
      });

      logger.info(`User deleted: ${id}`);
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2025') {
          throw new AppError('User not found', 404);
        }
      }
      logger.error(`Error deleting user ${id}:`, error);
      throw error;
    }
  }

  async list(params: {
    skip?: number;
    take?: number;
    where?: Prisma.UserWhereInput;
    orderBy?: Prisma.UserOrderByWithRelationInput;
  }): Promise<{ users: User[]; total: number }> {
    try {
      const { skip = 0, take = 10, where, orderBy } = params;

      const [users, total] = await Promise.all([
        prisma.user.findMany({
          skip,
          take,
          where,
          orderBy,
          select: {
            id: true,
            email: true,
            name: true,
            role: true,
            createdAt: true,
            updatedAt: true,
            projects: {
              select: {
                id: true,
                name: true,
                status: true,
              },
              take: 3,
            },
          },
        }),
        prisma.user.count({ where }),
      ]);

      return { users: users as any[], total };
    } catch (error) {
      logger.error('Error listing users:', error);
      throw error;
    }
  }

  async validatePassword(email: string, password: string): Promise<User | null> {
    try {
      const user = await this.findByEmail(email);
      if (!user) return null;

      const isValid = await bcrypt.compare(password, user.password);
      return isValid ? user : null;
    } catch (error) {
      logger.error(`Error validating password for ${email}:`, error);
      return null;
    }
  }

  async updatePassword(id: string, newPassword: string): Promise<void> {
    try {
      const hashedPassword = await bcrypt.hash(newPassword, 12);
      
      await prisma.user.update({
        where: { id },
        data: { password: hashedPassword },
      });

      logger.info(`Password updated for user: ${id}`);
    } catch (error) {
      logger.error(`Error updating password for user ${id}:`, error);
      throw error;
    }
  }
}

export const userRepository = new UserRepository();