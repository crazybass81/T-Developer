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