// backend/src/core/config/index.ts
export interface CoreConfig {
  app: {
    name: string;
    version: string;
    env: string;
  };
  server: {
    port: number;
    host: string;
  };
  database: {
    dynamodb: {
      region: string;
      endpoint?: string;
    };
  };
  cache: {
    redis: {
      host: string;
      port: number;
    };
  };
  agents: {
    maxConcurrent: number;
    timeout: number;
  };
}

export const config: CoreConfig = {
  app: {
    name: 'T-Developer',
    version: '1.0.0',
    env: process.env.NODE_ENV || 'development'
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
    host: process.env.HOST || 'localhost'
  },
  database: {
    dynamodb: {
      region: process.env.AWS_REGION || 'us-east-1',
      endpoint: process.env.DYNAMODB_ENDPOINT
    }
  },
  cache: {
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379')
    }
  },
  agents: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_AGENTS || '10'),
    timeout: parseInt(process.env.AGENT_TIMEOUT || '30000')
  }
};
