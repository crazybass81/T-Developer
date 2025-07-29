export interface AppConfig {
  server: {
    port: number;
  };
  app: {
    env: string;
    version: string;
  };
  aws: {
    region: string;
    dynamodbEndpoint?: string;
  };
  agents: {
    maxConcurrent: number;
    timeout: number;
  };
}

export const config: AppConfig = {
  server: {
    port: parseInt(process.env.PORT || '3000')
  },
  app: {
    env: process.env.NODE_ENV || 'development',
    version: process.env.APP_VERSION || '1.0.0'
  },
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    ...(process.env.DYNAMODB_ENDPOINT && { dynamodbEndpoint: process.env.DYNAMODB_ENDPOINT })
  },
  agents: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_AGENTS || '10'),
    timeout: parseInt(process.env.AGENT_TIMEOUT || '30000')
  }
};
