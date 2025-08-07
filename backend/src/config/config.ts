/**
 * Application Configuration
 * Phase 0: Basic configuration setup
 */

import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../../.env') });

export interface Config {
  env: string;
  port: number;
  cors: {
    origin: string | string[];
    credentials: boolean;
  };
  aws: {
    region: string;
    bedrock: {
      modelId: string;
    };
    dynamodb: {
      tablePrefix: string;
    };
  };
  jwt: {
    secret: string;
    refreshSecret?: string;
    expiresIn: string;
  };
  database: {
    url: string;
  };
  redis: {
    url: string;
  };
  logging: {
    level: string;
  };
}

export const config: Config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:5173',
    credentials: true
  },
  
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    bedrock: {
      modelId: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-sonnet-20240229-v1:0'
    },
    dynamodb: {
      tablePrefix: process.env.DYNAMODB_TABLE_PREFIX || 't-developer'
    }
  },
  
  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
    refreshSecret: process.env.JWT_REFRESH_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  },
  
  database: {
    url: process.env.DATABASE_URL || 'postgresql://tdeveloper:tdeveloper123@localhost:5432/tdeveloper'
  },
  
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379'
  },
  
  logging: {
    level: process.env.LOG_LEVEL || 'debug'
  }
};

// Validate required configuration
export const validateConfig = (): void => {
  const requiredEnvVars = [
    'AWS_REGION',
    'JWT_SECRET'
  ];
  
  const missingVars = requiredEnvVars.filter(
    varName => !process.env[varName]
  );
  
  if (missingVars.length > 0 && config.env === 'production') {
    throw new Error(
      `Missing required environment variables: ${missingVars.join(', ')}`
    );
  }
};