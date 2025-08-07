/**
 * Database Service
 * Phase 1: PostgreSQL, DynamoDB, Redis 연결 관리
 */

import { PrismaClient } from '@prisma/client';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import Redis from 'ioredis';
import { logger } from '../utils/logger';
import { config } from '../config/config';

// PostgreSQL via Prisma
export const prisma = new PrismaClient({
  log: config.env === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// DynamoDB
const dynamodbClient = new DynamoDBClient({
  region: config.aws.region,
  ...(config.env === 'development' && {
    endpoint: 'http://localhost:8000',
    credentials: {
      accessKeyId: 'local',
      secretAccessKey: 'local',
    },
  }),
});

export const dynamodb = DynamoDBDocumentClient.from(dynamodbClient);

// Redis
export const redis = new Redis(config.redis.url, {
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  },
  maxRetriesPerRequest: 3,
});

// Database connection health check
export const checkDatabaseConnections = async (): Promise<{
  postgres: boolean;
  dynamodb: boolean;
  redis: boolean;
}> => {
  const status = {
    postgres: false,
    dynamodb: false,
    redis: false,
  };

  // PostgreSQL health check
  try {
    await prisma.$queryRaw`SELECT 1`;
    status.postgres = true;
    logger.info('✅ PostgreSQL connection successful');
  } catch (error) {
    logger.error('❌ PostgreSQL connection failed:', error);
  }

  // Redis health check
  try {
    await redis.ping();
    status.redis = true;
    logger.info('✅ Redis connection successful');
  } catch (error) {
    logger.error('❌ Redis connection failed:', error);
  }

  // DynamoDB health check
  try {
    const { ListTablesCommand } = await import('@aws-sdk/client-dynamodb');
    await dynamodbClient.send(new ListTablesCommand({ Limit: 1 }));
    status.dynamodb = true;
    logger.info('✅ DynamoDB connection successful');
  } catch (error) {
    logger.error('❌ DynamoDB connection failed:', error);
  }

  return status;
};

// Graceful shutdown
export const closeDatabaseConnections = async (): Promise<void> => {
  try {
    await prisma.$disconnect();
    redis.disconnect();
    logger.info('🔌 Database connections closed gracefully');
  } catch (error) {
    logger.error('❌ Error closing database connections:', error);
  }
};

// Initialize connections
export const initializeDatabases = async (): Promise<void> => {
  logger.info('🔄 Initializing database connections...');
  
  const health = await checkDatabaseConnections();
  
  if (!health.postgres) {
    throw new Error('PostgreSQL connection failed');
  }
  
  logger.info('✅ Database initialization complete', health);
};